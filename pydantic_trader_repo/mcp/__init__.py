"""MCP (Model Context Protocol) client implementations"""

# Use HTTP client instead of stdio
from .mcp_http_client import (
    MCPHTTPClient as MCPClient,
    AAVEHTTPClient as AAVEMCPClient, 
    UniswapHTTPClient as UniswapMCPClient,
    get_aave_client,
    get_uniswap_client
)

__all__ = ["MCPClient", "AAVEMCPClient", "UniswapMCPClient", "get_aave_client", "get_uniswap_client"]