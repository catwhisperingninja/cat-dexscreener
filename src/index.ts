import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import axios from 'axios';

const DEXSCREENER_API = 'https://api.dexscreener.com/latest';

// For Smithery deployment
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

  return server.server;
}

// For local testing with stdio
if (import.meta.url === `file://${process.argv[1]}`) {
  const server = new McpServer({
    name: 'dexscreener-mcp',
    version: '0.1.0'
  });

  server.tool('search_pairs', 'Search for trading pairs', 
    { query: { type: 'string' } },
    async ({ query }) => {
      const response = await axios.get(`${DEXSCREENER_API}/dex/search?q=${encodeURIComponent(query)}`);
      return { content: [{ type: 'text', text: JSON.stringify(response.data, null, 2) }] };
    }
  );

  const transport = new StdioServerTransport();
  server.connect(transport).then(() => {
    console.error('DexScreener MCP server running');
  });
}
