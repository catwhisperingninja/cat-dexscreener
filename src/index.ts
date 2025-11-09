import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import type { CallToolResult } from '@modelcontextprotocol/sdk/types.js';
import axios from 'axios';

const BASE_URL = 'https://api.dexscreener.com';

type RateLimiterConfig = {
  limit: number;
  intervalMs?: number;
};

class RateLimiter {
  private timestamps: number[] = [];
  private readonly limit: number;
  private readonly interval: number;

  constructor({ limit, intervalMs = 60_000 }: RateLimiterConfig) {
    this.limit = limit;
    this.interval = intervalMs;
  }

  async waitForSlot(): Promise<void> {
    const now = Date.now();
    this.timestamps = this.timestamps.filter((ts) => now - ts < this.interval);

    if (this.timestamps.length >= this.limit) {
      const oldest = this.timestamps[0];
      const delay = this.interval - (now - oldest);
      await new Promise((resolve) => setTimeout(resolve, delay));
    }

    this.timestamps.push(Date.now());
  }
}

const tokenRateLimiter = new RateLimiter({ limit: 60 });
const dexRateLimiter = new RateLimiter({ limit: 300 });

async function fetchWithRateLimit<T>(
  endpoint: string,
  limiter: RateLimiter,
  params?: Record<string, string>
): Promise<T> {
  await limiter.waitForSlot();

  const url = new URL(endpoint, BASE_URL);
  if (params) {
    Object.entries(params)
      .filter(([, value]) => value !== undefined && value !== null)
      .forEach(([key, value]) => {
        url.searchParams.set(key, value);
      });
  }

  const response = await axios.get<T>(url.toString(), { timeout: 10_000 });
  return response.data;
}

function successResponse(data: unknown): CallToolResult {
  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(data, null, 2)
      }
    ]
  };
}

function errorResponse(error: unknown): CallToolResult {
  let message = 'Unknown error';
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const apiMessage = error.response?.data?.message;
    message = status
      ? `API error (${status}): ${apiMessage ?? error.message}`
      : `Network error: ${error.message}`;
  } else if (error instanceof Error) {
    message = error.message;
  }

  return {
    isError: true,
    content: [
      {
        type: 'text',
        text: `Error: ${message}`
      }
    ]
  };
}

function ensureString(value: unknown, field: string): string {
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new Error(`Missing or invalid "${field}" parameter`);
  }
  return value.trim();
}

const API_DOCS_RESOURCE = `# DexScreener MCP API

## Token Profile Endpoints
- GET /token-profiles/latest/v1
- GET /token-boosts/latest/v1
- GET /token-boosts/top/v1

## Orders
- GET /orders/v1/{chainId}/{tokenAddress}

## DEX Data
- GET /latest/dex/pairs/{chainId}/{pairId}
- GET /latest/dex/tokens/{tokenAddresses}
- GET /latest/dex/search?q={query}

All responses follow DexScreener's public schema with \`schemaVersion\`, \`pairs\`, token metadata, liquidity, FDV, and boosts.`;

const MEMECOIN_BEST_PRACTICES = `# Memecoin Best Practices

1. Verify contract safety: locked liquidity, renounced ownership, audited bytecode.
2. Track liquidity depth across chains before executing large orders.
3. Monitor boosts and ads to understand artificial volume.
4. Use stop-loss logic because slippage can spike when boosts expire.
5. Cross-reference social channels to avoid impersonators.`;

// For Smithery deployment - default export
export default function() {
  const server = new McpServer({
    name: 'dexscreener-mcp',
    version: '0.1.0'
  });

  const registerTool = (
    name: string,
    description: string,
    parameters: Record<string, any>,
    handler: (args: Record<string, any>) => Promise<unknown>
  ) => {
    server.tool(name, description, parameters, async (args) => {
      try {
        const data = await handler(args);
        return successResponse(data);
      } catch (error) {
        return errorResponse(error);
      }
    });
  };

  registerTool(
    'get_latest_token_profiles',
    'Get the latest token profiles',
    {},
    () => fetchWithRateLimit('/token-profiles/latest/v1', tokenRateLimiter)
  );

  registerTool(
    'get_latest_boosted_tokens',
    'Get the latest boosted tokens',
    {},
    () => fetchWithRateLimit('/token-boosts/latest/v1', tokenRateLimiter)
  );

  registerTool(
    'get_top_boosted_tokens',
    'Get tokens with the most active boosts',
    {},
    () => fetchWithRateLimit('/token-boosts/top/v1', tokenRateLimiter)
  );

  registerTool(
    'get_token_orders',
    'Get paid orders for a specific token',
    {
      chainId: { type: 'string', description: 'Chain ID (e.g., solana, ethereum)' },
      tokenAddress: { type: 'string', description: 'Token address' }
    },
    ({ chainId, tokenAddress }) => {
      const safeChain = ensureString(chainId, 'chainId');
      const safeToken = ensureString(tokenAddress, 'tokenAddress');
      return fetchWithRateLimit(
        `/orders/v1/${encodeURIComponent(safeChain)}/${encodeURIComponent(safeToken)}`,
        tokenRateLimiter
      );
    }
  );

  registerTool(
    'get_pairs_by_chain_and_address',
    'Get pair data by chain and pair address',
    {
      chainId: { type: 'string', description: 'Chain ID (e.g., solana, ethereum)' },
      pairId: { type: 'string', description: 'Pair address/identifier' }
    },
    ({ chainId, pairId }) => {
      const safeChain = ensureString(chainId, 'chainId');
      const safePair = ensureString(pairId, 'pairId');
      return fetchWithRateLimit(
        `/latest/dex/pairs/${encodeURIComponent(safeChain)}/${encodeURIComponent(safePair)}`,
        dexRateLimiter
      );
    }
  );

  registerTool(
    'get_pairs_by_token_addresses',
    'Get pairs for one or multiple token addresses',
    {
      tokenAddresses: {
        type: 'string',
        description: 'Comma-separated list of addresses (max 30)'
      }
    },
    ({ tokenAddresses }) => {
      const addresses = ensureString(tokenAddresses, 'tokenAddresses')
        .split(',')
        .map((addr) => addr.trim())
        .filter(Boolean)
        .map((addr) => encodeURIComponent(addr))
        .join(',');

      if (!addresses) {
        throw new Error('Provide at least one token address');
      }

      return fetchWithRateLimit(`/latest/dex/tokens/${addresses}`, dexRateLimiter);
    }
  );

  // Backwards compatibility with earlier builds
  registerTool(
    'get_token_pairs',
    'Deprecated alias for get_pairs_by_token_addresses (single token)',
    {
      tokenAddress: { type: 'string', description: 'Token address' }
    },
    ({ tokenAddress }) => {
      const address = encodeURIComponent(ensureString(tokenAddress, 'tokenAddress'));
      return fetchWithRateLimit(`/latest/dex/tokens/${address}`, dexRateLimiter);
    }
  );

  registerTool(
    'search_pairs',
    'Search for trading pairs on DexScreener',
    {
      query: { type: 'string', description: 'Search query (token name or symbol)' }
    },
    ({ query }) => {
      const q = ensureString(query, 'query');
      return fetchWithRateLimit(
        '/latest/dex/search',
        dexRateLimiter,
        { q }
      );
    }
  );

  server.resource(
    'dexscreener_api_docs',
    'dexscreener://docs/api',
    { mimeType: 'text/markdown', description: 'DexScreener API overview' },
    async () => ({
      contents: [
        {
          uri: 'dexscreener://docs/api',
          mimeType: 'text/markdown',
          text: API_DOCS_RESOURCE
        }
      ]
    })
  );

  server.resource(
    'memecoin_best_practices',
    'dexscreener://docs/memecoin',
    { mimeType: 'text/markdown', description: 'Operational safety tips for memecoin trading' },
    async () => ({
      contents: [
        {
          uri: 'dexscreener://docs/memecoin',
          mimeType: 'text/markdown',
          text: MEMECOIN_BEST_PRACTICES
        }
      ]
    })
  );

  return server.server;
}
