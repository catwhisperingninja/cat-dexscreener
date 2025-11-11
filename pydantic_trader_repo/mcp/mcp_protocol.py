"""
MCP Protocol Client Module
Reliable MCP client for connecting to locally running servers.
No mock data fallbacks - real connections only.
"""

import asyncio
import json
import subprocess
import time
import os
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
import logging

# Try to use app logger if available, otherwise use standard logger
try:
    from ..utils.logging import app_logger
    logger = app_logger
except ImportError:
    logger = logging.getLogger(__name__)

@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: str
    args: List[str]
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    timeout: int = 30

class MCPProtocolError(Exception):
    """MCP protocol communication error."""
    pass

class MCPConnectionError(Exception):
    """MCP connection error."""
    pass

class MCPClient:
    """
    MCP Protocol Client
    Connects to MCP servers via stdio transport.
    """
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process = None
        self.message_id = 1
        self.initialized = False
        self.capabilities = {}
        self.tools = []
        self.resources = []
        
    async def connect(self) -> bool:
        """Connect to MCP server and initialize."""
        try:
            # Start server process
            env = dict(os.environ)
            if self.config.env:
                env.update(self.config.env)
            
            logger.info(f"Starting MCP server: {self.config.name}")
            logger.debug(f"Command: {self.config.command} {' '.join(self.config.args)}")
            
            # Use command directly
            command = self.config.command
            
            self.process = subprocess.Popen(
                [command] + self.config.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.config.cwd,
                env=env,
                text=True,
                bufsize=0
            )
            
            # Wait for process to start
            await asyncio.sleep(0.5)
            
            # Check if process is still running
            if self.process.poll() is not None:
                raise MCPConnectionError(f"External MCP server '{self.config.name}' failed to start")
            
            # Initialize MCP session
            await self._initialize()
            await self._load_capabilities()
            
            logger.info(f"✅ MCP Connected: {self.config.name} ({len(self.tools)} tools, {len(self.resources)} resources)")
            return True
            
        except Exception as e:
            logger.error(f"❌ External MCP Server Connection Failed: {self.config.name} - {e}")
            await self.disconnect()
            raise MCPConnectionError(f"External MCP server connection failed: {e}")
    
    async def disconnect(self):
        """Disconnect from MCP server."""
        if self.process:
            try:
                self.process.terminate()
                await asyncio.sleep(0.1)
                if self.process.poll() is None:
                    self.process.kill()
            except:
                pass
            finally:
                self.process = None
        
        self.initialized = False
        logger.info(f"🔌 MCP Disconnected: {self.config.name}")
    
    async def _send_message(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send JSON-RPC message to server."""
        if not self.process or self.process.poll() is not None:
            raise MCPConnectionError("Server process not running")
        
        message = {
            "jsonrpc": "2.0",
            "id": self.message_id,
            "method": method,
            "params": params or {}
        }
        self.message_id += 1
        
        # Send message
        message_json = json.dumps(message) + "\n"
        logger.debug(f"📤 Sending to {self.config.name}: {message_json.strip()}")
        try:
            self.process.stdin.write(message_json)
            self.process.stdin.flush()
        except BrokenPipeError:
            raise MCPConnectionError("Broken pipe - server disconnected")
        
        # Read response
        try:
            response_line = await asyncio.wait_for(
                asyncio.to_thread(self.process.stdout.readline),
                timeout=self.config.timeout
            )
            
            if not response_line:
                raise MCPConnectionError("No response from server")
            
            logger.debug(f"📥 Raw response from {self.config.name}: {response_line.strip()}")
            response = json.loads(response_line.strip())
            
            if "error" in response:
                error = response["error"]
                raise MCPProtocolError(f"Server error: {error.get('message', error)}")
            
            return response
            
        except asyncio.TimeoutError:
            raise MCPConnectionError("Response timeout")
        except json.JSONDecodeError as e:
            raise MCPProtocolError(f"Invalid JSON response: {e}")
    
    async def _initialize(self):
        """Initialize MCP connection."""
        response = await self._send_message("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"listChanged": True}
            },
            "clientInfo": {
                "name": "mcp-client",
                "version": "1.0.0"
            }
        })
        
        result = response.get("result", {})
        self.capabilities = result.get("capabilities", {})
        self.initialized = True
        
        # Send initialized notification
        await self._send_notification("notifications/initialized")
    
    async def _send_notification(self, method: str, params: Dict[str, Any] = None):
        """Send notification (no response expected)."""
        if not self.process or self.process.poll() is not None:
            raise MCPConnectionError("Server process not running")
        
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        message_json = json.dumps(message) + "\n"
        self.process.stdin.write(message_json)
        self.process.stdin.flush()
    
    async def _load_capabilities(self):
        """Load tools and resources from server."""
        # Load tools
        if "tools" in self.capabilities:
            try:
                response = await self._send_message("tools/list")
                self.tools = response.get("result", {}).get("tools", [])
            except Exception as e:
                logger.warning(f"Failed to load tools: {e}")
        
        # Load resources  
        if "resources" in self.capabilities:
            try:
                response = await self._send_message("resources/list")
                self.resources = response.get("result", {}).get("resources", [])
            except Exception as e:
                logger.warning(f"Failed to load resources: {e}")
    
    async def call_tool(self, name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call a tool on the MCP server."""
        if not self.initialized:
            raise MCPProtocolError("Client not initialized")
        
        # Check if tool exists
        tool_names = [tool.get("name") for tool in self.tools]
        if name not in tool_names:
            raise MCPProtocolError(f"Tool '{name}' not found. Available: {tool_names}")
        
        logger.debug(f"🔧 MCP Tool Call: {self.config.name}.{name}")
        
        response = await self._send_message("tools/call", {
            "name": name,
            "arguments": arguments or {}
        })
        
        result = response.get("result", {})
        logger.debug(f"🔧 MCP Tool Response for {name}: {type(result)} - {str(result)[:200]}")
        return result
    
    async def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server."""
        if not self.initialized:
            raise MCPProtocolError("Client not initialized")
        
        response = await self._send_message("resources/read", {
            "uri": uri
        })
        
        return response.get("result", {})
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools."""
        if not self.initialized:
            raise MCPProtocolError("Client not initialized")
        
        response = await self._send_message("tools/list")
        return response.get("result", {}).get("tools", [])
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources."""
        if not self.initialized:
            raise MCPProtocolError("Client not initialized")
        
        response = await self._send_message("resources/list")
        return response.get("result", {}).get("resources", [])
    
    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific tool."""
        for tool in self.tools:
            if tool.get("name") == name:
                return tool.get("inputSchema", {})
        return None
    
    async def health_check(self) -> bool:
        """Check if server is healthy."""
        try:
            if not self.process or self.process.poll() is not None:
                return False
            
            # Try to list tools as a health check
            await self.list_tools()
            return True
        except:
            return False

class MCPManager:
    """Manages multiple MCP server connections."""
    
    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
    
    def add_server(self, config: MCPServerConfig):
        """Add an MCP server configuration."""
        self.clients[config.name] = MCPClient(config)
    
    async def connect_all(self):
        """Connect to all configured servers."""
        results = {}
        for name, client in self.clients.items():
            try:
                success = await client.connect()
                results[name] = success
                logger.info(f"Connected to {name}: {success}")
            except Exception as e:
                results[name] = False
                logger.error(f"External MCP server '{name}' connection failed: {e}")
        return results
    
    async def disconnect_all(self):
        """Disconnect from all servers."""
        for client in self.clients.values():
            await client.disconnect()
    
    def get_client(self, name: str) -> Optional[MCPClient]:
        """Get client by server name."""
        return self.clients.get(name)
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call a tool on a specific server."""
        client = self.get_client(server_name)
        if not client:
            raise MCPProtocolError(f"Server '{server_name}' not found")
        
        return await client.call_tool(tool_name, arguments)
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all servers."""
        results = {}
        for name, client in self.clients.items():
            results[name] = await client.health_check()
        return results

# Example usage
async def example_usage():
    """Example of how to use the MCP client."""
    
    # Configure your servers
    market_data_config = MCPServerConfig(
        name="market-data",
        command="python",
        args=["-m", "market_data_server"],
        cwd="/path/to/market-data-server"
    )
    
    execution_config = MCPServerConfig(
        name="execution",
        command="python", 
        args=["-m", "execution_server"],
        cwd="/path/to/execution-server"
    )
    
    # Create manager and add servers
    manager = MCPManager()
    manager.add_server(market_data_config)
    manager.add_server(execution_config)
    
    try:
        # Connect to all servers
        results = await manager.connect_all()
        print(f"Connection results: {results}")
        
        # Use the market data server
        market_client = manager.get_client("market-data")
        if market_client:
            tools = await market_client.list_tools()
            print(f"Market data tools: {[t['name'] for t in tools]}")
            
            # Call a tool
            if tools:
                result = await market_client.call_tool(tools[0]['name'], {"symbol": "BTC"})
                print(f"Tool result: {result}")
        
        # Health check
        health = await manager.health_check_all()
        print(f"Health status: {health}")
        
    finally:
        # Always disconnect
        await manager.disconnect_all()

if __name__ == "__main__":
    asyncio.run(example_usage())