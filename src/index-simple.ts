#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import axios from 'axios';

const DEXSCREENER_API = 'https://api.dexscreener.com/latest';

// For Smithery deployment - default export
export default function() {
  const server = new McpServer({
    name: 'dexscreener-mcp',
    version: '0.1.0'
  });

  // Simple tool to search pairs
  server.tool(
    'search_pairs',
    'Search for trading pairs on DexScreener',
    {
      query: { type: 'string', description: 'Search query (token name or symbol)' }
    },
    async ({ query }) => {
      try {
        const response = await axios.get(`${DEXSCREENER_API}/dex/search?q=${encodeURIComponent(query)}`);
        return {
          content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }]
        };
      } catch (error: any) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }]
        };
      }
    }
  );

  // Get pair by address
  server.tool(
    'get_pair',
    'Get pair data by chain and address',
    {
      chainId: { type: 'string', description: 'Chain ID (e.g., solana, ethereum)' },
      pairAddress: { type: 'string', description: 'Pair contract address' }
    },
    async ({ chainId, pairAddress }) => {
      try {
        const response = await axios.get(`${DEXSCREENER_API}/dex/pairs/${chainId}/${pairAddress}`);
        return {
          content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }]
        };
      } catch (error: any) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }]
        };
      }
    }
  );

  // Get token pairs
  server.tool(
    'get_token_pairs',
    'Get all pairs for a token address',
    {
      tokenAddress: { type: 'string', description: 'Token contract address' }
    },
    async ({ tokenAddress }) => {
      try {
        const response = await axios.get(`${DEXSCREENER_API}/dex/tokens/${tokenAddress}`);
        return {
          content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }]
        };
      } catch (error: any) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }]
        };
      }
    }
  );

  // Get latest token profiles
  server.tool(
    'get_latest_token_profiles',
    'Get the latest token profiles',
    {},
    async () => {
      try {
        const response = await axios.get(`${DEXSCREENER_API}/token-profiles/latest/v1`);
        return {
          content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }]
        };
      } catch (error: any) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }]
        };
      }
    }
  );

  // Get latest boosted tokens
  server.tool(
    'get_latest_boosted_tokens',
    'Get the latest boosted tokens',
    {},
    async () => {
      try {
        const response = await axios.get(`${DEXSCREENER_API}/token-boosts/latest/v1`);
        return {
          content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }]
        };
      } catch (error: any) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }]
        };
      }
    }
  );

  // Get top boosted tokens
  server.tool(
    'get_top_boosted_tokens',
    'Get tokens with most active boosts',
    {},
    async () => {
      try {
        const response = await axios.get(`${DEXSCREENER_API}/token-boosts/top/v1`);
        return {
          content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }]
        };
      } catch (error: any) {
        return {
          content: [{ type: 'text', text: `Error: ${error.message}` }]
        };
      }
    }
  );

  return server.server;
}