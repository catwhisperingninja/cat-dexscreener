# DexScreener MCP Server Fix Plan

## Problem Analysis

### Current State

- **Working deployed version (75111d3):** 3 basic tools, Smithery deployment
  works
- **Broken enhanced version (6030711):** 7 tools + resources but deployment
  fails

### Root Cause

Smithery cannot resolve these imports during build:

```typescript
import { DexScreenerService } from "./services/dexscreener.js"; // ❌ Module resolution fails
import { z } from "zod"; // ❌ Added unnecessary dependency
```

### What's Missing from Working Version

1. **4 Additional Tools:**

   - `get_latest_token_profiles`
   - `get_latest_boosted_tokens`
   - `get_top_boosted_tokens`
   - `get_token_orders` (with chainId, tokenAddress params)

2. **Enhanced Existing Tools:**

   - `get_pairs_by_chain_and_address` (currently missing)
   - `get_pairs_by_token_addresses` (currently missing)

3. **Resources:**

   - API documentation resource
   - Memecoin best practices resource

4. **Rate Limiting:**
   - Proper request throttling

## Solution: Inline All Functionality

### Strategy

Keep what works (McpServer + axios), inline everything else into single
`src/index.ts` file.

### Implementation Steps

#### Step 1: Foundation (Keep Working)

```typescript
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import axios from "axios";

export default function () {
	// Streamable HTTP handled by Smithery
}
```

#### Step 2: Add Simple Rate Limiting (Inline)

```typescript
let lastRequest = 0;
const minInterval = 200; // 200ms between requests

async function makeRequest(url: string) {
	const now = Date.now();
	const timeSinceLastRequest = now - lastRequest;
	if (timeSinceLastRequest < minInterval) {
		await new Promise((resolve) =>
			setTimeout(resolve, minInterval - timeSinceLastRequest)
		);
	}
	lastRequest = Date.now();

	const response = await axios.get(url);
	return response.data;
}
```

#### Step 3: Add Missing Tools (Direct API Calls)

**Token Profile Tools:**

- `get_latest_token_profiles` →
  `GET https://api.dexscreener.com/token-profiles/latest/v1`
- `get_latest_boosted_tokens` →
  `GET https://api.dexscreener.com/token-boosts/latest/v1`
- `get_top_boosted_tokens` →
  `GET https://api.dexscreener.com/token-boosts/top/v1`

**Order Tool:**

- `get_token_orders` →
  `GET https://api.dexscreener.com/orders/v1/{chainId}/{tokenAddress}`

**Enhanced Pair Tools:**

- Update existing `get_pair` to use proper parameter names (`chainId`, `pairId`)
- Add `get_pairs_by_token_addresses` →
  `GET https://api.dexscreener.com/latest/dex/tokens/{tokenAddresses}`

#### Step 4: Add Resources (Inline)

```typescript
server.resource(
	"api-docs",
	"dexscreener://docs/api",
	{ mimeType: "text/markdown", description: "DexScreener API Documentation" },
	async () => ({
		contents: [
			{
				uri: "dexscreener://docs/api",
				mimeType: "text/markdown",
				text: `# DexScreener API Documentation...`,
			},
		],
	})
);
```

#### Step 5: Error Handling

Wrap all API calls in try-catch blocks:

```typescript
async ({ params }) => {
	try {
		const result = await makeRequest(url);
		return {
			content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
		};
	} catch (error: any) {
		return { content: [{ type: "text", text: `Error: ${error.message}` }] };
	}
};
```

## Expected Result

### Tools (7 total)

1. `search_pairs` - Search for trading pairs ✅ (already working)
2. `get_pair` - Get pair by chain and address ✅ (already working, rename
   params)
3. `get_token_pairs` - Get pairs for token address ✅ (already working)
4. `get_latest_token_profiles` - Latest token profiles ➕ (add)
5. `get_latest_boosted_tokens` - Latest boosted tokens ➕ (add)
6. `get_top_boosted_tokens` - Top boosted tokens ➕ (add)
7. `get_token_orders` - Token orders by chain/address ➕ (add)

### Resources (2 total)

1. API documentation resource ➕ (add)
2. Memecoin best practices resource ➕ (add)

### Technical Requirements

- ✅ Streamable HTTP transport (handled by Smithery)
- ✅ No external imports (everything inlined)
- ✅ No additional dependencies
- ✅ Rate limiting (simple but effective)
- ✅ Error handling for all endpoints

## Validation Plan

1. **Build Test:** `npm run build` succeeds
2. **Local Test:** Server starts and lists all 7 tools
3. **API Test:** At least one API call works (test search_pairs)
4. **Deploy Test:** Push and verify Smithery deployment succeeds
5. **Integration Test:** Test from Claude Code with deployed server

## Success Criteria

- [ ] All 7 tools available
- [ ] 2 resources available
- [ ] Smithery deployment successful
- [ ] No import/dependency errors
- [ ] Rate limiting prevents API abuse
- [ ] Maintains streamable HTTP compatibility
