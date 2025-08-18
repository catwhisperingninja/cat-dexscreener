# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DexScreener MCP (Model Context Protocol) server that provides real-time access to DEX pair data, token information, and market statistics across multiple blockchains. It's implemented as a TypeScript Node.js application using the MCP SDK.

## Common Development Commands

### Building and Development
- `npm run build` - Compile TypeScript to JavaScript
- `npm run dev` - Watch mode with auto-rebuild and restart
- `npm run watch` - Watch TypeScript files for changes

### Testing
- `npm test` - Run integration tests
- `npm run test:watch` - Run tests in watch mode

### Setup and Installation
- `npm install` - Install dependencies
- `npm run setup` - Configure Claude Desktop to use this MCP server

### Running the Server
- `npm start` - Run the compiled server
- `npm run inspector` - Run with MCP inspector for debugging

## Architecture Overview

### Core Components

1. **MCP Server Implementation** (`src/index.ts`)
   - Main server class `DexScreenerMcpServer` that handles MCP protocol
   - Tool handlers for each DexScreener API endpoint
   - Resource handlers for documentation access
   - Rate limiting integration for API compliance

2. **DexScreener Service** (`src/services/dexscreener.ts`)
   - API client with rate limiting (60 req/min for token endpoints, 300 req/min for DEX endpoints)
   - Error handling and response processing
   - Methods for all DexScreener API endpoints

3. **Type Definitions** (`src/types/`)
   - TypeScript interfaces for API responses and parameters
   - MCP protocol type definitions

### Key Design Patterns

- **Rate Limiting**: Two separate rate limiters for different endpoint groups to respect API limits
- **Error Handling**: Custom `DexScreenerError` class with proper MCP error propagation
- **Modular Service Layer**: Separation between MCP server logic and API service implementation

## Available MCP Tools

The server exposes these tools through the MCP protocol:
- `get_latest_token_profiles` - Latest token profiles
- `get_latest_boosted_tokens` - Latest boosted tokens  
- `get_top_boosted_tokens` - Most actively boosted tokens
- `get_token_orders` - Orders for specific token (requires chainId, tokenAddress)
- `get_pairs_by_chain_and_address` - Pair data by chain and address (requires chainId, pairId)
- `get_pairs_by_token_addresses` - Pairs by token addresses (max 30)
- `search_pairs` - Search for trading pairs

## Testing Approach

Integration tests are located in `src/tests/dexscreener.test.ts` and test actual API endpoints with rate limiting compliance.