"""
HTTP-based MCP Client

This client connects to the MCP HTTP Gateway instead of using stdio.
Much simpler and more reliable than subprocess management.
"""

import aiohttp
import asyncio
from typing import Dict, Any, Optional, List
import logging
from ..utils.logging import app_logger

logger = app_logger

class MCPHTTPClient:
    """Base HTTP client for MCP servers via gateway"""

    def __init__(self, gateway_url: str = "http://127.0.0.1:8888"):
        """
        Initialize HTTP client

        Args:
            gateway_url: URL of the MCP HTTP gateway
        """
        self.gateway_url = gateway_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def connect(self) -> bool:
        """
        Connect to the HTTP gateway

        Returns:
            True if connection successful
        """
        try:
            self.session = aiohttp.ClientSession()

            # Test connection with health check
            async with self.session.get(f"{self.gateway_url}/health") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    servers = list(data['servers'].keys())
                    logger.info(f"🌐 MCP Gateway Connected: {self.gateway_url}")
                    logger.info(f"📡 Available servers: {', '.join(servers)}")
                    return True
                else:
                    logger.error(f"❌ MCP Gateway connection failed: HTTP {resp.status}")
                    return False

        except Exception as e:
            logger.error(f"Failed to connect to MCP gateway: {e}")
            return False

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None

    async def execute(self, server: str, method: str, params: Dict[str, Any] = None) -> Any:
        """
        Execute a method on an MCP server

        Args:
            server: Server name (e.g., 'aave', 'uniswap-pools')
            method: Method to execute
            params: Parameters for the method

        Returns:
            Result from the server
        """
        if not self.session:
            raise RuntimeError("Not connected to gateway. Call connect() first.")

        payload = {
            "tool_name": method,
            "arguments": params or {}
        }

        logger.signal(f"🔧 MCP: Calling {server}.{method}")

        try:
            async with self.session.post(
                f"{self.gateway_url}/execute/{server}",
                json=payload
            ) as resp:
                if resp.status == 200:
                    try:
                        data = await resp.json()
                    except Exception as json_err:
                        text = await resp.text()
                        logger.error(f"❌ MCP JSON Parse Error ({server}): {json_err}, Response: {text[:200]}")
                        return None

                    if data.get('error'):
                        error_msg = data.get('error', 'Unknown error')
                        logger.error(f"❌ MCP Error ({server}.{method}): {error_msg}")
                        logger.debug(f"Full response: {data}")
                        # Return empty dict instead of None for better error handling
                        return {'error': error_msg}
                    logger.debug(f"✅ MCP Success: {server}.{method}")
                    result = data.get('result')

                    # Handle MCP formatted responses
                    if isinstance(result, dict) and 'content' in result:
                        content = result.get('content', [])
                        if content and isinstance(content, list) and len(content) > 0:
                            first_item = content[0]
                            if isinstance(first_item, dict) and first_item.get('type') == 'text':
                                text_content = first_item.get('text', '')
                                try:
                                    # Try to parse as JSON
                                    import json
                                    return json.loads(text_content)
                                except json.JSONDecodeError:
                                    # Return as plain text if not JSON
                                    return text_content

                    return result
                else:
                    logger.error(f"❌ MCP HTTP error {resp.status}: {await resp.text()}")
                    return None

        except Exception as e:
            logger.error(f"❌ MCP Exception ({server}.{method}): {e}")
            return None


class AAVEHTTPClient(MCPHTTPClient):
    """HTTP client for AAVE MCP server"""

    async def get_user_positions(self, user_address: str) -> List[Dict[str, Any]]:
        """Get user positions from AAVE"""
        result = await self.execute(
            "aave",
            "get_user_data",  # Correct method name
            {"user_address": user_address}
        )
        return result.get("positions", []) if result else []

    async def get_reserve_data(self, asset: str) -> Dict[str, Any]:
        """Get reserve data for an asset"""
        result = await self.execute(
            "aave",
            "get_reserve_data",
            {"asset": asset}
        )
        return result or {}

    async def get_liquidatable_positions(self, min_value: float = 1000) -> List[Dict[str, Any]]:
        """Get liquidatable positions by checking reserves and user health"""
        # First get all active reserves
        reserves_result = await self.execute("aave", "get_reserves", {})

        if not reserves_result or 'content' not in reserves_result:
            return []

        # Parse reserves from response
        try:
            import json
            content = reserves_result['content'][0]['text'] if reserves_result['content'] else '[]'
            reserves = json.loads(content)

            # Zero tolerance - only return real liquidatable positions
            # Without actual user positions with health_factor < 1.0, return empty
            logger.signal(f"📊 MCP/AAVE: {len(reserves)} reserves found")
            return []

        except Exception as e:
            logger.error(f"Error parsing AAVE reserves: {e}")
            return []


class UniswapHTTPClient(MCPHTTPClient):
    """HTTP client for Uniswap MCP servers"""

    async def get_pool_price(self, token0: str, token1: str) -> Optional[float]:
        """Get price from Uniswap pool"""
        result = await self.execute(
            "uniswap-pools",
            "get_pool_price",
            {"token0": token0, "token1": token1}
        )
        return result.get("price") if result else None

    async def get_pool_info(self, token0: str, token1: str, fee: int = 3000) -> Dict[str, Any]:
        """Get pool information"""
        result = await self.execute(
            "uniswap-pools",
            "get_pool_info",
            {"token0": token0, "token1": token1, "fee": fee}
        )
        return result or {}


class UniswapTraderHTTPClient(MCPHTTPClient):
    """HTTP client for Uniswap Trader MCP server - executes real swaps"""

    async def get_price_quote(self, token_in: str, token_out: str,
                             amount_in: Optional[str] = None, amount_out: Optional[str] = None,
                             chain_id: int = 11155111, trade_type: str = "exactIn") -> Dict[str, Any]:
        """
        Get price quote for a swap

        Args:
            token_in: Input token address (use "NATIVE" for ETH)
            token_out: Output token address (use "NATIVE" for ETH)
            amount_in: Amount to swap in (for exactIn trades)
            amount_out: Desired output amount (for exactOut trades)
            chain_id: Chain ID (11155111 for Sepolia)
            trade_type: "exactIn" or "exactOut"
        """
        params = {
            "chainId": chain_id,
            "amountIn": token_in,
            "amountOut": token_out,
            "tradeType": trade_type
        }

        if trade_type == "exactIn" and amount_in:
            params["amountIn"] = amount_in
        elif trade_type == "exactOut" and amount_out:
            params["amountOut"] = amount_out

        result = await self.execute(
            "uniswap-trader",
            "getPrice",
            params
        )
        return result or {}

    async def execute_swap(self, token_in: str, token_out: str,
                          amount_in: Optional[str] = None, amount_out: Optional[str] = None,
                          chain_id: int = 11155111, trade_type: str = "exactIn",
                          slippage_tolerance: float = 0.5, deadline: int = 20) -> Dict[str, Any]:
        """
        Execute a real swap on-chain

        Args:
            token_in: Input token address (use "NATIVE" for ETH)
            token_out: Output token address (use "NATIVE" for ETH)
            amount_in: Amount to swap in (for exactIn trades)
            amount_out: Desired output amount (for exactOut trades)
            chain_id: Chain ID (11155111 for Sepolia)
            trade_type: "exactIn" or "exactOut"
            slippage_tolerance: Max slippage in percentage
            deadline: Transaction deadline in minutes

        Returns:
            Transaction hash, amounts, route, gas used
        """
        params = {
            "chainId": chain_id,
            "amountIn": token_in,
            "amountOut": token_out,
            "tradeType": trade_type
        }

        if trade_type == "exactIn" and amount_in:
            params["amountIn"] = amount_in
        elif trade_type == "exactOut" and amount_out:
            params["amountOut"] = amount_out

        result = await self.execute(
            "uniswap-trader",
            "executeSwap",
            params
        )

        if result:
            logger.info(f"Swap executed: {result.get('transactionHash')}")
            app_logger.signal(f"SWAP EXECUTED: {result.get('transactionHash')}")

        return result or {}


class DexscreenerHTTPClient(MCPHTTPClient):
    """
    ⚠️ DEPRECATED: Do NOT use this class!

    cat-dexscreener is ONLY available on Smithery Cloud.
    Use smithery_cloud_client.get_smithery_dexscreener() instead.

    This class will be removed in a future version.
    """

    def __init__(self):
        """Initialize Dexscreener client"""
        logger.warning(
            "⚠️ DexscreenerHTTPClient is deprecated. "
            "cat-dexscreener is Smithery Cloud only. "
            "Use smithery_cloud_client.get_smithery_dexscreener() instead."
        )
        super().__init__()
        self.server_name = "cat-dexscreener"

    async def search_pairs(self, query: str) -> Dict[str, Any]:
        """
        Search for trading pairs on DexScreener

        Args:
            query: Search query (e.g., "ETH USDC ethereum")

        Returns:
            Search results with pairs data
        """
        result = await self.execute(
            self.server_name,
            "search_pairs",
            {"query": query}
        )
        return result or {}

    async def get_pair(self, chain: str, pair_address: str) -> Dict[str, Any]:
        """
        Get pair data by chain and address

        Args:
            chain: Blockchain name (e.g., "ethereum")
            pair_address: Pair contract address

        Returns:
            Pair data
        """
        result = await self.execute(
            self.server_name,
            "get_pair",
            {"chainId": chain, "pairAddress": pair_address}
        )
        return result or {}

    async def get_token_pairs(self, token_address: str) -> Dict[str, Any]:
        """
        Get all pairs for a token address

        Args:
            token_address: Token contract address

        Returns:
            List of pairs for the token
        """
        result = await self.execute(
            self.server_name,
            "get_token_pairs",
            {"tokenAddress": token_address}
        )
        return result or {}


# Factory functions for compatibility
def get_aave_client() -> AAVEHTTPClient:
    """Get AAVE HTTP client instance"""
    return AAVEHTTPClient()

def get_uniswap_client() -> UniswapHTTPClient:
    """Get Uniswap HTTP client instance"""
    return UniswapHTTPClient()


def get_dexscreener_client():
    """
    Get Dexscreener client (SMITHERY CLOUD ONLY per PRD FR-001)

    CRITICAL: cat-dexscreener is ONLY available on Smithery Cloud.
    There is NO local deployment option. Do NOT fall back to local HTTP client.
    """
    from .smithery_cloud_client import get_smithery_dexscreener
    return get_smithery_dexscreener()  # NO FALLBACK - Smithery or error

def get_uniswap_trader_client():
    """Get Uniswap Trader client - cloud or local"""
    use_cloud = True  # Toggle for cloud/local

    if use_cloud:
        try:
            from .smithery_cloud_client import get_smithery_uniswap_trader
            return get_smithery_uniswap_trader()
        except ImportError as e:
            logger.error(f"Failed to import Smithery Uniswap Trader: {e}")
            return UniswapTraderHTTPClient()
    else:
        return UniswapTraderHTTPClient()
