#!/usr/bin/env node
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';
import { DexScreenerService } from './services/dexscreener.js';

// Optional: Define configuration schema
export const configSchema = z.object({
  apiKey: z.string().optional().describe("DexScreener API key"),
});

// For Smithery: Export default function that returns server
export default function({ config }: { config: z.infer<typeof configSchema> }) {
  const server = new McpServer({
    name: 'dexscreener-mcp-server',
    version: '0.1.0'
  });

  // Initialize service
  const dexService = new DexScreenerService();
  
  // Use config.apiKey if provided
  if (config?.apiKey) {
    process.env.DEXSCREENER_API_KEY = config.apiKey;
  }

  // Register tools
  server.tool(
    'get_latest_token_profiles',
    'Get the latest token profiles',
    {},
    async () => {
      const result = await dexService.getLatestTokenProfiles();
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }
  );

  server.tool(
    'get_latest_boosted_tokens', 
    'Get the latest boosted tokens',
    {},
    async () => {
      const result = await dexService.getLatestBoostedTokens();
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }
  );

  server.tool(
    'get_top_boosted_tokens',
    'Get tokens with most active boosts',
    {},
    async () => {
      const result = await dexService.getTopBoostedTokens();
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }
  );

  server.tool(
    'get_token_orders',
    'Check orders paid for a specific token',
    {
      chainId: z.string().describe('Chain ID (e.g., "solana")'),
      tokenAddress: z.string().describe('Token address')
    },
    async ({ chainId, tokenAddress }) => {
      const result = await dexService.getTokenOrders({ chainId, tokenAddress });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }
  );

  server.tool(
    'get_pairs_by_chain_and_address',
    'Get one or multiple pairs by chain and pair address',
    {
      chainId: z.string().describe('Chain ID (e.g., "solana")'),
      pairId: z.string().describe('Pair address')
    },
    async ({ chainId, pairId }) => {
      const result = await dexService.getPairsByChainAndAddress({ chainId, pairId });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }
  );

  server.tool(
    'get_pairs_by_token_addresses',
    'Get one or multiple pairs by token address (max 30)',
    {
      tokenAddresses: z.string().describe('Comma-separated token addresses')
    },
    async ({ tokenAddresses }) => {
      const result = await dexService.getPairsByTokenAddresses({ tokenAddresses });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }
  );

  server.tool(
    'search_pairs',
    'Search for pairs matching query',
    {
      query: z.string().describe('Search query')
    },
    async ({ query }) => {
      const result = await dexService.searchPairs({ query });
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }]
      };
    }
  );

  // Add resources
  server.resource(
    'api-docs',
    'dexscreener://docs/api',
    { mimeType: 'text/markdown', description: 'DexScreener API Documentation' },
    async () => {
      return { 
        contents: [{
          uri: 'dexscreener://docs/api',
          mimeType: 'text/markdown',
          text: `# DexScreener API Documentation

## Overview
DexScreener provides real-time data for decentralized exchanges across multiple blockchains. The API allows you to:
- Get real-time pair data and price information
- Search for trading pairs
- Monitor token profiles and boosted tokens
- Track token orders and market activity

## Best Practices
1. Rate Limiting: Respect the API rate limits to ensure stable service
2. Caching: Cache responses when possible to reduce API load
3. Error Handling: Implement proper error handling for API responses
4. Pagination: Use pagination parameters when available to manage large datasets

## Chain IDs
Common chain IDs include:
- solana: Solana blockchain
- ethereum: Ethereum mainnet
- bsc: Binance Smart Chain
- polygon: Polygon/Matic
- arbitrum: Arbitrum One
- avalanche: Avalanche C-Chain`
        }]
      };
    }
  );

  server.resource(
    'memecoin-best-practices',
    'dexscreener://docs/memecoin-best-practices',
    { mimeType: 'text/markdown', description: 'Memecoin Trading Best Practices' },
    async () => {
      return {
        contents: [{
          uri: 'dexscreener://docs/memecoin-best-practices',
          mimeType: 'text/markdown',
          text: `# Memecoin Trading Best Practices

## Analysis Guidelines
1. Liquidity Analysis
   - Check liquidity pool size
   - Monitor liquidity distribution
   - Track liquidity lock status and duration

2. Trading Volume
   - Analyze 24h volume trends
   - Compare volume across different pairs
   - Look for unusual volume spikes

3. Market Cap Considerations
   - Calculate fully diluted valuation
   - Compare with similar tokens
   - Check token distribution

4. Risk Management
   - Set strict stop losses
   - Don't invest more than you can afford to lose
   - Be aware of potential scams and rugpulls

5. Technical Analysis
   - Use multiple timeframes
   - Watch for pattern breakouts
   - Monitor momentum indicators

## Common Red Flags
- Extremely low liquidity
- Unlocked liquidity
- Anonymous team
- No clear utility or roadmap
- Suspicious contract code
- Unusual buying/selling patterns`
        }]
      };
    }
  );

  // Return the server for Smithery
  return server.server;
}

// For local/stdio mode when run directly
async function main() {
  const server = new McpServer({
    name: 'dexscreener-mcp-server',
    version: '0.1.0'
  });

  const dexService = new DexScreenerService();

  // Register all the same tools for local mode
  server.tool('get_latest_token_profiles', 'Get the latest token profiles', {}, async () => {
    const result = await dexService.getLatestTokenProfiles();
    return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
  });

  server.tool('get_latest_boosted_tokens', 'Get the latest boosted tokens', {}, async () => {
    const result = await dexService.getLatestBoostedTokens();
    return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
  });

  server.tool('get_top_boosted_tokens', 'Get tokens with most active boosts', {}, async () => {
    const result = await dexService.getTopBoostedTokens();
    return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
  });

  server.tool('get_token_orders', 'Check orders paid for a specific token',
    { chainId: z.string().describe('Chain ID'), tokenAddress: z.string().describe('Token address') },
    async ({ chainId, tokenAddress }) => {
      const result = await dexService.getTokenOrders({ chainId, tokenAddress });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool('get_pairs_by_chain_and_address', 'Get pairs by chain and address',
    { chainId: z.string().describe('Chain ID'), pairId: z.string().describe('Pair address') },
    async ({ chainId, pairId }) => {
      const result = await dexService.getPairsByChainAndAddress({ chainId, pairId });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool('get_pairs_by_token_addresses', 'Get pairs by token addresses',
    { tokenAddresses: z.string().describe('Comma-separated addresses') },
    async ({ tokenAddresses }) => {
      const result = await dexService.getPairsByTokenAddresses({ tokenAddresses });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  server.tool('search_pairs', 'Search for pairs',
    { query: z.string().describe('Search query') },
    async ({ query }) => {
      const result = await dexService.searchPairs({ query });
      return { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] };
    }
  );

  // Add resources for local mode
  server.resource(
    'api-docs',
    'dexscreener://docs/api',
    { mimeType: 'text/markdown', description: 'DexScreener API Documentation' },
    async () => {
      return { 
        contents: [{
          uri: 'dexscreener://docs/api',
          mimeType: 'text/markdown',
          text: `# DexScreener API Documentation - Full documentation available`
        }]
      };
    }
  );

  server.resource(
    'memecoin-best-practices',
    'dexscreener://docs/memecoin-best-practices',
    { mimeType: 'text/markdown', description: 'Memecoin Trading Best Practices' },
    async () => {
      return {
        contents: [{
          uri: 'dexscreener://docs/memecoin-best-practices',
          mimeType: 'text/markdown',
          text: `# Memecoin Trading Best Practices - Full guide available`
        }]
      };
    }
  );

  // Connect stdio transport for local mode
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('DexScreener MCP server running on stdio');
}

// Run main if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}
