"""
FastAPI HTTP Gateway for MCP Servers

This provides a simple HTTP interface to execute code on MCP servers
instead of dealing with complex stdio protocol connections.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from typing import Dict, Any, List, Optional
import os
import json
from pathlib import Path
from contextlib import asynccontextmanager

from .mcp_protocol import MCPManager, MCPServerConfig

# Add logger
import logging
logger = logging.getLogger(__name__)

# Global MCP manager instance
manager = MCPManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage MCP connections lifecycle"""
    # Load server configurations
    config_path = Path(__file__).parent / "mcp_server_config.json"
    
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            
        # Add servers from config
        for server_id, server_config in config['servers'].items():
            cmd_parts = server_config['command']
            command = cmd_parts[0]
            args = cmd_parts[1:] if len(cmd_parts) > 1 else []
            
            # Build environment variables
            env = {}
            for key, value in server_config.get('env', {}).items():
                if value.startswith('${') and value.endswith('}'):
                    # Extract environment variable name and default
                    var_expr = value[2:-1]
                    if ':-' in var_expr:
                        var_name, default = var_expr.split(':-', 1)
                        env[key] = os.getenv(var_name, default)
                    else:
                        env[key] = os.getenv(var_expr, '')
                else:
                    env[key] = value
            
            # Check if server is optional
            is_optional = server_config.get('optional', False)
            fallback_message = server_config.get('fallback_message', f"External server '{server_id}' unavailable")
            
            # No special handling needed
                
            manager.add_server(MCPServerConfig(
                name=server_id,
                command=command,
                args=args,
                env=env,
                cwd=server_config.get('path')
            ))
    
    # Gateway starts immediately - MCP servers are external services that must be already running
    print("🚀 MCP Gateway: Starting HTTP gateway (external MCP servers must be running)")
    print("📡 MCP Gateway: This gateway provides HTTP interface to external MCP servers")
    print("⚠️  MCP Gateway: If servers are not running, they will show as unavailable")
    
    yield
    
    # Disconnect from all servers on shutdown
    await manager.disconnect_all()
    print("🔌 MCP Gateway: Disconnected from all servers")


app = FastAPI(title="MCP Trading Servers Gateway", lifespan=lifespan)


class ToolCallRequest(BaseModel):
    """Request to call a tool on an MCP server"""
    tool_name: str
    arguments: Dict[str, Any] = {}


class ToolCallResponse(BaseModel):
    """Response from tool call"""
    result: Any
    error: Optional[str] = None


class ServerInfo(BaseModel):
    """Information about an MCP server"""
    name: str
    connected: bool
    tools: List[Dict[str, Any]] = []


@app.get("/health")
async def health_check():
    """Check gateway and server health"""
    health_status = await manager.health_check_all()
    
    return {
        "status": "healthy",
        "servers": health_status
    }


@app.get("/servers")
async def list_servers() -> List[ServerInfo]:
    """List all configured servers and their status"""
    servers = []
    
    for name, client in manager.clients.items():
        info = ServerInfo(
            name=name,
            connected=client.initialized,
            tools=client.tools if client.initialized else []
        )
        servers.append(info)
    
    return servers


@app.get("/servers/{server_name}/tools")
async def get_server_tools(server_name: str):
    """Get available tools for a specific server"""
    client = manager.get_client(server_name)
    if not client:
        raise HTTPException(status_code=404, detail=f"Server {server_name} not found")
    
    if not client.initialized:
        raise HTTPException(status_code=503, detail=f"Server {server_name} not connected")
    
    return {
        "server": server_name,
        "tools": client.tools
    }


@app.post("/servers/{server_name}/tools/{tool_name}", response_model=ToolCallResponse)
async def call_tool(server_name: str, tool_name: str, request: ToolCallRequest = None):
    """Call a tool on a specific server"""
    try:
        # Use arguments from request body if provided, otherwise empty dict
        arguments = request.arguments if request else {}
        
        result = await manager.call_tool(server_name, tool_name, arguments)
        return ToolCallResponse(result=result)
        
    except Exception as e:
        return ToolCallResponse(result=None, error=str(e))


@app.post("/servers/{server_name}/reconnect")
async def reconnect_server(server_name: str):
    """Reconnect to a specific server"""
    client = manager.get_client(server_name)
    if not client:
        raise HTTPException(status_code=404, detail=f"Server {server_name} not found")
    
    # Disconnect first if connected
    if client.initialized:
        await client.disconnect()
    
    # Try to reconnect
    try:
        success = await client.connect()
        return {"server": server_name, "connected": success}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Failed to reconnect: {str(e)}")


@app.post("/servers/add")
async def add_new_server(config: Dict[str, Any]):
    """Add a new MCP server dynamically"""
    try:
        # Validate required fields
        required = ["name", "command", "path"]
        for field in required:
            if field not in config:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Parse command
        cmd_parts = config['command'] if isinstance(config['command'], list) else [config['command']]
        command = cmd_parts[0]
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []
        
        # No special handling needed
        
        # Create server config
        server_config = MCPServerConfig(
            name=config['name'],
            command=command,
            args=args,
            env=config.get('env', {}),
            cwd=config.get('path')
        )
        
        # Add and connect
        manager.add_server(server_config)
        client = manager.get_client(config['name'])
        success = await client.connect()
        
        return {
            "server": config['name'],
            "connected": success,
            "tools": client.tools if success else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Simplified legacy endpoint for compatibility
@app.post("/execute/{server_name}")
async def execute_on_server(server_name: str, request: Dict[str, Any]):
    """Legacy endpoint - redirects to tool call"""
    tool_name = request.get('method', request.get('tool_name'))
    if not tool_name:
        raise HTTPException(status_code=400, detail="Missing tool_name or method")
    
    arguments = request.get('params', request.get('arguments', {}))
    
    try:
        result = await manager.call_tool(server_name, tool_name, arguments)
        # Log what we're returning
        logger.info(f"Tool {tool_name} returned: {type(result)} - {str(result)[:300]}")
        
        # The result is already processed by mcp_protocol.py, just return it
        return {"result": result, "error": ""}
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
        return {"result": None, "error": str(e)}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8888)