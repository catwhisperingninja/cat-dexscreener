"""
Smithery Cloud MCP Client - FIXED
"""

import os
import asyncio
from typing import Dict, Any, Optional
from urllib.parse import urlencode

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from ..utils.logging import app_logger

logger = app_logger


def _mask_secret(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep * 2:
        return value[:keep] + "..."
    return f"{value[:keep]}...{value[-keep:]}"


def _decode_config_b64(b64_string: str) -> Optional[Dict[str, Any]]:
    try:
        import base64
        import json

        # Support URL-safe and standard base64
        padding = '=' * (-len(b64_string) % 4)
        normalized = b64_string + padding
        decoded = base64.urlsafe_b64decode(normalized.encode()).decode()
        return json.loads(decoded)
    except Exception:
        return None

# Smithery server configurations
SMITHERY_SERVERS = {
    "cat-dexscreener": {
        "url": "https://server.smithery.ai/@catwhisperingninja/cat-dexscreener/mcp"
    },
    "uniswap-trader": {
        "url": "https://server.smithery.ai/@catwhisperingninja/uniswap-trader-mcp/mcp"
    }
}


class SmitheryMCPClient:
    """Manage authenticated MCP sessions against Smithery-hosted tools.

    This client wraps the streamed HTTP transport provided by the Smithery
    platform and exposes a minimal interface for connecting to a named MCP
    server (see `SMITHERY_SERVERS`), invoking remote tools, and closing the
    session cleanly. Callers instantiate the client with a supported
    `server_name`, ensure the `SMITHERY_API_KEY` environment variable is
    populated (``.env`` loading occurs during ``connect``), and then use the
    async ``connect``/``call_tool``/``close`` methods to interact with the
    service. Tool calls forward arbitrary argument dictionaries and return the
    parsed MCP response (JSON payloads are deserialized automatically when
    possible) or an error dictionary if the request fails. ``connect`` raises a
    ``ValueError`` when configuration is missing and logs connection/tool
    failures via ``app_logger`` so downstream services can react appropriately.
    """

    def __init__(self, server_name: str):
        """Initialize for a specific server"""
        if server_name not in SMITHERY_SERVERS:
            raise ValueError(f"Unknown server: {server_name}")

        self.server_name = server_name
        self.base_url = SMITHERY_SERVERS[server_name]["url"]
        self.api_key = os.getenv("SMITHERY_API_KEY")

        if not self.api_key:
            raise ValueError("SMITHERY_API_KEY not found in environment")

        self.session = None
        self.read = None
        self.write = None
        self.connected = False
        self._http_client = None

    async def connect(self) -> bool:
        """Connect to Smithery server using MCP client"""
        try:
            # Load API key from environment
            if not self.api_key:
                # Try loading from .env if not already in environment
                from dotenv import load_dotenv
                load_dotenv()
                self.api_key = os.getenv("SMITHERY_API_KEY")

                if not self.api_key:
                    raise ValueError("SMITHERY_API_KEY not found in environment or .env file")

            # Build URL with API key
            params = {"api_key": self.api_key}
            url = f"{self.base_url}?{urlencode(params)}"

            logger.info(f"Connecting to Smithery {self.server_name}...")

            # Create the HTTP client
            self._transport = streamablehttp_client(url)

            # Get the read/write streams
            self.read, self.write, _ = await self._transport.__aenter__()

            # Create session with the streams
            self.session = ClientSession(self.read, self.write)
            await self.session.__aenter__()

            # Initialize the connection
            await self.session.initialize()

            # List tools to verify connection
            tools = await self.session.list_tools()
            tool_names = [t.name for t in tools.tools]

            self.connected = True
            logger.info(f"✅ Connected to Smithery {self.server_name}: {', '.join(tool_names)}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Smithery {self.server_name}: {e}")
            self.connected = False
            return False

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Any:
        """Call a tool on the server"""
        if not self.connected or not self.session:
            # Try to connect
            if not await self.connect():
                return {"error": "Failed to connect to Smithery"}

        try:
            result = await self.session.call_tool(tool_name, arguments or {})

            # Parse result based on type
            if hasattr(result, 'content'):
                if isinstance(result.content, list) and len(result.content) > 0:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        # Try to parse as JSON
                        import json
                        try:
                            return json.loads(content.text)
                        except json.JSONDecodeError:
                            return content.text
                    return content
                return result.content

            return result

        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close the connection"""
        try:
            if self.session:
                await self.session.__aexit__(None, None, None)
            if self._transport:
                await self._transport.__aexit__(None, None, None)
            self.connected = False
            logger.info(f"Disconnected from Smithery {self.server_name}")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")


class SmitheryHTTPAdapter:
    """
    Adapter that makes Smithery MCP client look like MCPHTTPClient
    This allows it to be a drop-in replacement
    """

    def __init__(self, server_name: str):
        self.client = SmitheryMCPClient(server_name)
        self.gateway_url = "http://127.0.0.1:8888"  # For compatibility
        self.session = None  # For compatibility
        self.server_name = server_name

    async def connect(self) -> bool:
        """Connect to Smithery"""
        return await self.client.connect()

    async def close(self):
        """Close connection"""
        await self.client.close()

    async def execute(self, server: str, method: str, params: Dict[str, Any] = None) -> Any:
        """Execute method - compatible with MCPHTTPClient interface"""
        result = await self.client.call_tool(method, params)
        return result

    # Dexscreener-specific methods
    async def search_pairs(self, query: str) -> Dict[str, Any]:
        """Search for trading pairs on DexScreener"""
        result = await self.client.call_tool("search_pairs", {"query": query})
        return result or {}

    async def get_pair(self, chain: str, pair_address: str) -> Dict[str, Any]:
        """Get pair data by chain and address"""
        result = await self.client.call_tool(
            "get_pair",
            {"chain": chain, "pairAddress": pair_address}
        )
        # Don't mask empty responses - let the caller handle them
        logger.info(f"🔍 get_pair result type: {type(result)}, value: {result}")
        return result

    async def get_token_pairs(self, token_address: str) -> Dict[str, Any]:
        """Get all pairs for a token address"""
        result = await self.client.call_tool(
            "get_token_pairs",
            {"tokenAddress": token_address}
        )
        # Don't mask empty responses - let the caller handle them
        logger.debug(f"get_token_pairs result type: {type(result)}, value: {result}")
        return result


# Factory functions for each server
def get_smithery_dexscreener():
    """Get Smithery Dexscreener client"""
    return SmitheryHTTPAdapter("cat-dexscreener")

def get_smithery_uniswap_trader():
    """Get Smithery Uniswap Trader client"""
    return SmitheryHTTPAdapter("uniswap-trader")
