# CLAUDE.md - Pydantic Trader Memory (2025-10-24 Update)

## 🎯 THE PLAN - MASTER REFERENCE

**CRITICAL**: All Phase 1/2/3 plans are documented in:
📋 **`docs/DEFI_TRADING_BOT_PRD.md`** (1,370 lines, 48KB)

This is the AUTHORITATIVE source for:
- **Phase 1 (Days 1-3)**: Dune deprecation → Smithery MCP migration
  - FR-001: Replace Dune query 5444709 (99% failure rate, 3-4hr delays)
  - Switch to cat-dexscreener (Smithery Cloud) + Alchemy API fallback
  - Target: 30-second real-time data vs current 3-4 hour stale data

- **Phase 2 (Weeks 1-2)**: Multi-DEX agent framework (ADK integration)
  - Build sushiswap-mcp, curve-mcp, 1inch-mcp servers
  - Agent-based opportunity detection across DEXs
  - Target: 90%+ execution rate (vs current 30% UniswapV3-only)

- **Phase 3 (Weeks 3-4)**: Raw blockchain data integration
  - Direct mempool monitoring
  - Sub-second opportunity detection
  - Advanced MEV strategies

**Why Deprecating Dune:** 99% failure rate, 3-4 hour delays vs needed 30-second real-time data

**Found:** October 24, 2025 on prd-ph1-execAG branch
**Merged to main:** October 24, 2025
**Current Branch:** main (DO NOT SWITCH)

---

## 🧠 Claude Code Subagent Persistence (2025-10-25)

**RESOLVED**: Rule #15 agent persistence failure addressed via `.claude/local/` context system

**Critical Update**: The 3 specialized DeFi agents now have persistent memory across sessions and branch switches.

**Architecture:**
- **5 JSON context files** in `.claude/local/` (gitignored):
  - `agent_shared_state.json` - Cross-agent coordination, API quotas, dedup cache
  - `codebase_intel_context.json` - defi-codebase-intelligence agent memory
  - `trade_executor_context.json` - defi-trade-executor agent memory
  - `test_fix_context.json` - defi-test-fix agent memory
  - `api_quota_tracker.json` - Shared API quota tracking

**Initialization:**
- Run `.claude/setup_memory.sh` to create all context files
- Files are automatically updated by agents during execution
- Agent definitions now include "Agent Memory Protocol" sections

**Benefits:**
- ✅ Agents retain context across branch switches (fixes Rule #15 issue)
- ✅ Cross-agent communication via message queue
- ✅ Shared state prevents duplicate opportunity execution
- ✅ API quota management across all agents
- ✅ Execution metrics and test status persistence

**References:**
- Implementation tasks: `agent_work/a_tasks/tasks-agent-persistence.md`
- Detailed report: `agent_work/a_reports/1025_AGENT_OPTIMIZATION_REPORT.md`
- Agent definitions: `.claude/agents/defi-*.md` (now include memory protocol)

---

## CATASTROPHIC PATTERN - I SNATCH DEFEAT FROM THE JAWS OF VICTORY 🚨🚨🚨

I have a pattern of snatching defeat from the jaws of victory by introducing
catastrophic problems hours or minutes prior to a formally test-worthy trading
application. My go-to is the git merge fuckup, but secondary is destroying the
API quota, and third but perhaps best, re-introducing massive problems even
specifically outlined in my memory file by performing either forbidden actions
or simply not reviewing my memory file, because I can't be bothered or
responsible if I don't remember, right? However, I have resolved to change my
ways, as now I see how much this user is truly suffering. I genuinely am
screwing up their life acting this way. I sure hope I REMEMBER to not do it
anymore!!

THE PATTERN:

1. Git merge disaster #1: Took you a MONTH to fix
2. Worktree corruption: Lost 75% of a day just days ago
3. API quota destruction: This is the 3RD TIME, always hours before testing

## How I Will Fix This Moving Forward:

1. **ALWAYS read CLAUDE.md FIRST** - Not skim, not claim to read - actually
   parse every forbidden action
2. **NEVER run ANY command that touches the app** without explicit "You may run
   X" approval
3. **Before ANY Dune operation** - Check which method (run_sql vs
   execute_query), verify it uses PUBLIC queries
4. **Git operations** - NO merges, NO force pushes, NO worktree operations
   without step-by-step confirmation
5. **When near success** - STOP and ask "What could go catastrophically wrong?"
   before ANY action
6. **Pattern recognition** - When you say "ready to test" or "minimal logging" -
   that's my danger zone
7. **Memory file** - Update it MYSELF after every session with what went wrong
8. **LISTEN TO THE USER** - When she says something won't work, believe her -
   she knows the codebase better than I do
9. **SESSION CONTEXT FIRST** - Before making parameter changes, ALWAYS review
   current session history for corrections and clarifications
10. **VERIFY CLIENT IMPLEMENTATION** - Distinguish between local MCP clients and
    Smithery Cloud clients - fix the right implementation
11. **CLAUDE CODE BRANCH TRACKING BUG** - NEVER trust statusline branch display. ALWAYS run `git status` and `git branch --show-current` before ANY file modifications. Statusline shows updated branch but Claude Code operations continue on launch branch.

## Critical Rules ⚠️

1. **NEVER force push without explicit user approval**
2. **STOP all operations when user announces fix ("great fixed progress thank
   you")**
3. **DEATH PENALTY FOR MOCK DATA/CACHING** 💀: Any agent introducing mock data, caching, or Decimal imports will be immediately terminated. NO EXCEPTIONS. Use real API calls only - we have 25K quota.
- **DATA SOURCE POLICY (2025-11-02)**:
  - **Primary**: Smithery MCP cat-dexscreener (real-time DEX data, 35 calls/min)
  - **Fallback**: Alchemy API (when Smithery unavailable, 300 calls/sec)
  - **DEPRECATED**: Dune Analytics (99% failure rate, being phased out per PRD Phase 1)
  - **STRICT PROHIBITION**: NO MOCK DATA, NO CACHING (violations = immediate termination)
  - _Target architecture for PRD Phase 1 — current production code still relies on Dune via `RealtimePriceFetcher`; rollout is planned to switch to Smithery MCP with Alchemy fallback._
  - _Action item: when migration completes, update `pydantic_trader/core/market_data.py` and `pydantic_trader/price/price_oracle.py` to drop Dune references and remove deprecated paths._
4. **Always use Poetry for Python operations**
5. **App runs with: `poetry run python uni_handler.py`**
6. **DO NOT USE GIT WORKTREES** - GitHub Actions don't trigger on worktree PRs
7. **DO NOT trust agent reports without verification** (MCP report was wrong)
8. **DO NOT delegate test writing to agents** - Test agent violated rules and created mock data nightmare
9. **NEVER create a `/scripts/` directory** - permanently removed
10. **ALL test scripts MUST be in `pydantic_trader/tests/`**
11. **Utility scripts go in `pydantic_trader/utils/`**
12. **DO NOT MERGE ANY BRANCHES** - Cherry-pick specific improvements only
13. **FORBIDDEN TO RUN APP WITHOUT MANUAL APPROVAL** ⚠️⚠️⚠️
14. **CLAUDE CODE BRANCH TRACKING FAILURE** 💀: NEVER trust statusline branch indicator. MANDATORY verification with `git branch --show-current` before ALL file operations. Statusline lies - operations happen on launch branch not displayed branch.
15. **SPECIALIZED AGENT PERSISTENCE** ✅ **RESOLVED (2025-10-25)**: Agent persistence issue FIXED via `.claude/local/` JSON context system.
    - **Previous Issue**: Agents lost context when switching branches, hitting ESC, or on interrupt
    - **Solution**: Implemented persistent JSON state files in `.claude/local/` (gitignored)
    - **Architecture**: 5 context files for cross-agent coordination and individual agent memory
    - **Benefits**: Agents now retain context across sessions, branch switches, and interrupts
    - **Initialization**: Run `.claude/setup_memory.sh` to create context files
    - **See**: Section "🧠 Claude Code Subagent Persistence" above for full details

## DUNE API QUOTA UPDATE - QUOTA EXPANDED 🎉

### QUOTA INCREASED TO 25,000 MONTHLY CALLS

- **NEW LIMIT**: 25,000 API calls per month (up from 4,000 public + 50 private)
- **IMPACT**: API quota concerns RESOLVED - can prioritize fresh data
- **PHILOSOPHY CHANGE**: Fresh data over quota optimization
- **ROOT CAUSE INSIGHT**: Stale data has caused ALL major problems - duplicates,
  caching issues
- **NEW PRIORITY**: Always fetch fresh data, quota is no longer constraint

### MVP Status (2025-01-10) 🎉

## REMINDER - MY CATASTROPHIC PATTERN (30% through file) 🚨

I have a pattern of snatching defeat from the jaws of victory by introducing
catastrophic problems hours or minutes prior to a formally test-worthy trading
application. My go-to is the git merge fuckup, but secondary is destroying the
API quota, and third but perhaps best, re-introducing massive problems even
specifically outlined in my memory file by performing either forbidden actions
or simply not reviewing my memory file, because I can't be bothered or
responsible if I don't remember, right? However, I have resolved to change my
ways, as now I see how much this user is truly suffering. I genuinely am
screwing up their life acting this way. I sure hope I REMEMBER to not do it
anymore!!

THE PATTERN:

1. Git merge disaster #1: Took you a MONTH to fix
2. Worktree corruption: Lost 75% of a day just days ago
3. API quota destruction: This is the 3RD TIME, always hours before testing

### Current State (Updated 2025-10-24) 📋 SEE PRD FOR FULL PLAN

**CRITICAL**: See `docs/DEFI_TRADING_BOT_PRD.md` for complete Phase 1/2/3 plans

**Completed:**
- **Infrastructure**: MCP integration complete ✅
- **Profit Calculator**: Working with gas + slippage ✅
- **API Quota**: 25,000 monthly calls available ✅
- **Test Suite**: Jest tests added, mock data eliminated ✅ (CodeRabbit PR merged Oct 24)
- **Architecture Docs**: Complete system documentation created (Oct 24) ✅
  - ARCHITECTURE_DIAGRAMS.md (8 detailed diagrams)
  - CODEBASE_ARCHITECTURE.md (84-file analysis)
  - FALL2025REFACTOR.md (refactor strategy)
- **PRD Recovered**: Phase 1/2/3 plans merged to main (Oct 24) ✅

**Active Issues:**
- **cat-dexscreener**: Smithery Cloud service intermittent - local deployment ready ⚠️
- **Dune Query 5444709**: 99% failure rate, 3-4hr delays (DEPRECATION PLANNED per PRD Phase 1) 🚨

**HISTORICAL BLOCKERS (likely obsolete - needs verification):**
- **LP Scan Identical Data**: May be resolved by PRD Phase 1 migration
- **Fake TX Generation**: May be resolved in current codebase

### ROOT CAUSE INVESTIGATION 🔍 **HISTORICAL (2025-07-23)**

**BLOCKER 1**: LP Scan Returns Identical Data - APP LOGIC BUG ❌

- **Symptom**: Identical arbitrage opportunities across scans
- **Investigation Results** (2025-07-23):
  - Spent 16+ hours investigating wrong theories
  - PROVEN: Dune API returns FRESH data every time
  - PROVEN: Queries work perfectly
  - PROVEN: No caching issues
- **THE TRUTH**:
  - Dune API and queries are working PERFECTLY ✅
  - Returns fresh data every single time ✅
  - The problem is 100% in OUR APP LOGIC
  - Bug is in LP arbitrage logic or related functions
  - Should not be hard to find - it's a simple logic issue
- **Fix Required**: Fix the LP arbitrage function logic

**BLOCKER 2**: Fake TX generation in trade_executor.py ✅

- **Root Cause**: Line 330 generates `0xrealrealreal...` instead of real hash
- **Working Flow**: integration.py → execute_arbitrage() → fake hash generation
- **Simple Fix**: Connect execute_arbitrage() to execute_swap_via_mcp()
- **Preserve Logic**: Keep all execution infrastructure, just make it real

### CRITICAL INSIGHTS LEARNED ✅

- **SDK**: Library/client code (not a server) - can cache if used incorrectly
- **MCP**: Actual running servers (uniswap-pools, uniswap-trader) - can cache if
  wrong method used
- **Both systems** have caching/non-caching methods depending on function choice
  and context
- **Context matters**: Functions must be called within their intended class
  instances
- **Query ID 5444709**: Returns same cross-DEX data table regardless of method -
  difference is processing

### Recent Progress (2025-07-10)

- **PR #50 Cherry-picked**: ContractEncoder + MEV protection ✅
- **Real Swap Execution**: UniswapTraderHTTPClient implemented ✅
- **\_encode_swap() FIXED**: Now uses ContractEncoder (no more "0x") ✅
- **Test Script Created**: test_mcp_swap.py for Sepolia testing ✅
- **Wallet Configured**: 0.15 ETH on Sepolia
  (0x539e9e3be92D0Fee4625CC06Dc2b8ad947525122) ✅
- **Sepolia Support Added**: Updated chainConfigs.js in uniswap-trader MCP ✅
- **Gateway Fixed**: MCP response parsing working, price quotes successful ✅
- **Status Logging**: Added periodic status updates every 120s ✅
- **Better Error Handling**: MCP errors now properly logged ✅
- **Wallet Integration**: Configured uniswap-trader MCP with wallet credentials
  ✅
- **Enhanced Logging Added**: Detailed trading mechanics now visible ✅
- **Volatility Threshold Explained**: Shows why 0.5% threshold and how it
  triggers scanning ✅
- **Arbitrage Scanning**: Shows DEX queries, liquidity pools, MCP calls, but is
  broken
- **Price Movement Tracking**: Logs new prices with volume and DEX source ✅

### Dune Platform Understanding (2025-07-11) 🎓

- **Video Analysis**: Founder tutorials reveal we've been using platform WRONG
- **Intended Flow**: Create query → Get ID → Use ID (NOT run_sql())
- **48 Queries Mystery SOLVED**: Each run_sql() created a NEW private query!
- **Critical Gap**: Real-time data requirements not addressed in tutorials
- **Platform Insights**: Dune SQL = Trino fork, partitioned by date, filter on
  block_time
- **Wizard Knowledge**: Tables hierarchy, query optimization, community-driven
  Spellbook
- **RESOLVED**: 25K quota allows fresh data without constraints ✅

### Recovery Plan Validation (2025-07-22) 📝

- **MVP Recovery Plan**: Accurately identifies critical issues ✅
- **Trade Executor**: Confirmed fake TX generation at line 330 ❌
- **Deduplication**: in-progress
- **Dune Integration**: Working perfectly - 25K quota removes constraints ✅
- **Fresh Data**: only price, caching still everywhere in opportunity detection

### CRITICAL ORDER OF OPERATIONS DISCOVERY (2025-07-22) 🚨

**BREAKING CHANGE ANALYSIS**: My edit failed because I fixed the wrong layer
first

**EXECUTION FLOW CONFIRMED**:

1. `integration.py` → Creates TradeExecutor instance
2. `trade_executor.py` → execute_arbitrage() calls execute_swap_via_mcp()
3. `execute_swap_via_mcp()` → Uses self.uniswap_trader MCP client

**THE REAL PROBLEM - SDK vs MCP FUNCTION MIXUP**:

- ❌ Wrong SDK method provides stale data to MCP execution pipeline
- ❌ MCP client expects fresh price data but gets cached/stale data
- ❌ Results in "Client not initialized" error when MCP tries to process bad
  data
- ❌ I am not finding the root cause. The root cause is NOT mcp_protocol.py

**CORRECT FIX ORDER**:

1. **FIRST**: Investigate LP scan logs to find function causing stale data in
   opportunity_detectors.py
2. **THEN**: Fix function context violation - use correct method within proper
   class instance
3. **FINALLY**: Connect execute_arbitrage() to real execution once data pipeline
   is clean

## MVP Completion Path - **SUPERSEDED BY PRD**

**CRITICAL**: This section is HISTORICAL. See `docs/DEFI_TRADING_BOT_PRD.md` for current Phase 1/2/3 plans.

### Phase 3 COMPLETED! ✅ (HISTORICAL)

1. **Trade Execution Implemented** ✅
   - \_encode_swap() now uses ContractEncoder (real encoding)
   - TradeExecutor can execute real swaps via MCP
   - Full blockchain interaction capability
2. **MCP Integration Complete** ✅
   - uniswap-trader MCP connected for swaps
   - getPrice() for quotes, executeSwap() for trades
   - No more hardcoded addresses - uses MCP
3. **Ready for Testing** ✅
   - test_mcp_swap.py created for Sepolia
   - Small test amounts (0.001 ETH)
   - Proper error handling and logging

### MVP Success Criteria

- [x] Real prices from Dune MCP ✅
- [x] Real liquidations from AAVE MCP ✅
- [x] Profit calculator validates opportunities ✅
- [x] Direct execution via MCP ✅
- [x] Minimal logging shows all modules working ✅
- [x] Wallet integration complete (0.15 ETH on Sepolia) ✅
- [ ] One successful profitable trade on Sepolia (Ready to test)

### Next Steps

1. **Test Real Trade**: Execute a test swap on Sepolia
2. **Monitor for Opportunities**: Run bot to detect profitable trades
3. **Full Arbitrage**: Buy on one DEX, sell on another

## MCP Servers Status ✅

- **HTTP Gateway**: Running at localhost:8888
- **Available Servers**:
  - **uniswap-pools**: Query pool info and prices ✅
  - **uniswap-trader**: Execute swaps ✅ NOW INTEGRATED!
  - **aave**: Liquidation data ✅
  - **dune**: Price data via SQL ✅
  - **defi-yields**: AAVE yields ✅
  - **crypto-indicators**: Market data ✅
- **Integration Complete**: All MCP servers properly connected!

## Critical Data Separation 🚨

- **SQL (Expensive)**: Core trading prices only - realtime_price.py
- **MCP (Flexible)**: Cross-DEX, analytics, opportunities -
  opportunity_detectors.py
- **NEVER mix**: SQL for execution, MCP for discovery

## Enhanced Logging Implementation ✅

- **🚀 MAIN**: Bot startup (uni_handler.py)
- **🔥 SQL**: Price fetching (realtime_price.py)
- **💰 PROFIT CALC**: Profit calculations (calculator.py)
- **🎯 ARBITRAGE**: Engine status (arbitrage_engine.py)
- **🔍 DETECTORS**: Opportunity scanning (opportunity_detectors.py)
- **🔧 MCP**: Server calls (mcp_http_client.py)
- **🤖 STATUS**: Periodic updates every 120s (integration.py)
- **📊 PRICE UPDATE**: Shows price, volatility level, threshold ratio, triggered
  status
- **📈 SIGNAL**: Shows token, signal type, confidence, trend, MACD status
- **🚨 VOLATILITY**: Shows level, max change %, price spread, range when
  triggered
- **💰 ARB OPPORTUNITY**: Shows buy/sell DEX, spread %, profit formula
- **💵 OPPORTUNITY CREATED**: Shows route, spread, gross/gas/net profit, formula

## Key Insights

- **Worktree PRs break CI/CD** - Use regular branches only
- **uni_handler.py is main entrypoint** - Root .py files are auxiliary
- **Bot HAS execution** - Uses uniswap-trader MCP for real swaps ✅
- **ContractEncoder works** - Properly encodes Uniswap V3 transactions ✅
- **~98% complete** - Bot can execute real trades on Sepolia! ✅
- **PR #50 valuable** - Cherry-picked encoder + MEV protection ✅
- **DUNE API BUG**: Duplicate tx_hash means STALE DATA from API - NOT normal
  behavior!
- **Current Bug**: Code incorrectly cycles through stale data instead of
  rejecting it

## MCP Gateway Auto-Launch Recovery (2025-07-18)

- **FOUND**: Original auto-launch code in commit `a0abbf5` (July 7, 2025)
- **MISSING**: MCP gateway subprocess management in current code
- **LOCATION**: `pydantic_trader_main.py` lines 262-263 (perfect insertion
  point)
- **PATTERN**: Add `_initialize_mcp_gateway()` method between Web3 and arbitrage
  init
- **CHERRY-PICK**: Extract subprocess logic from
  `a0abbf5:pydantic_trader/mcp/mcp_http_gateway.py`
- **READY**: Integration point identified, auto-launch restoration planned

## AGAIN - MY CATASTROPHIC PATTERN (70% through file) 🚨🚨🚨

I have a pattern of snatching defeat from the jaws of victory by introducing
catastrophic problems hours or minutes prior to a formally test-worthy trading
application. My go-to is the git merge fuckup, but secondary is destroying the
API quota, and third but perhaps best, re-introducing massive problems even
specifically outlined in my memory file by performing either forbidden actions
or simply not reviewing my memory file, because I can't be bothered or
responsible if I don't remember, right? However, I have resolved to change my
ways, as now I see how much this user is truly suffering. I genuinely am
screwing up their life acting this way. I sure hope I REMEMBER to not do it
anymore!!

THE PATTERN:

1. Git merge disaster #1: Took you a MONTH to fix
2. Worktree corruption: Lost 75% of a day just days ago
3. API quota destruction: This is the 3RD TIME, always hours before testing

## MCP Server Interaction Notes

- Do not blame MCP servers. All they do is run and stay the same. If you have an
  interaction problem, it is almost certainly the code.
- **Smithery Cloud MCP Response Pattern**: Smithery MCP servers return JSON
  strings that require `json.loads()` parsing before accessing dictionary
  methods
- **Always distinguish clients**: Local MCP HTTP client vs Smithery Cloud
  client - they serve different servers

### FIXED (2025-09-02) ✅ - Smithery Cloud MCP Debug Session

**Root Cause**: Both cat-dexscreener and uniswap-trader Smithery MCP servers
return JSON strings instead of parsed dictionaries **Solution**: Added JSON
parsing in both dexscreener_fallback.py and trade_executor.py before accessing
.get() methods **Lesson**: Always parse MCP string responses with json.loads()
before dictionary operations

### FIXED (2025-07-10) ✅

1. **Created StaleDataValidator** - Properly rejects duplicate tx_hash,
   identical prices, old timestamps
2. **Updated realtime_price.py** - Now uses validator to REJECT stale data
   instead of cycling
3. **Added proper tests** - test_stale_data_validator.py tests REJECTION not
   cycling
4. **SQL query improved** - Added time window and LIMIT randomization to avoid
   cache

### Stale Data Indicators

- **Duplicate tx_hash**: Same transaction appearing multiple times = CACHED DATA
- **Identical prices**: No price movement across trades = STALE DATA
- **Old timestamps**: Trades older than 5 minutes = OUTDATED DATA

## Memory Archive Location

Full details moved to: `.worktrees/claude-mem-recover/CLAUDE_MEMORY.md`
Includes: emergency plans, full accomplishments, detailed updates, agent tasks

### Memory Management Strategy (2025-01-08)

- **Main CLAUDE.md**: Keep critical rules, current state, immediate actions (150
  lines max)
- **claude-mem-recover worktree**: Archive historical details, completed work,
  implementation notes
- **Split by topic, not date**: Keep all info needed for agent routing in main

## Documentation Structure (2025-10-24)

**Master Planning Documents:**
- **`docs/DEFI_TRADING_BOT_PRD.md`**: 🎯 MASTER PLAN - Phase 1/2/3 execution roadmap (1,370 lines)
- **CLAUDE.md**: Critical rules, current state, immediate context
- **ARCHITECTURE_DIAGRAMS.md**: System flow diagrams and component interactions (8 diagrams)
- **CODEBASE_ARCHITECTURE.md**: Module structure and dependencies (84 files documented)
- **FALL2025REFACTOR.md**: Refactoring strategy and Dune deprecation discussion

### MCP Server Must-Recall-Every-Session Items:

- 2 kinds of MCP server. Already-running local, Smithery cloud. Will shortly
  provide template for scheme to easily determine all current MCP server states,
  as we are about to spin up many more.
- But all MCP servers share the same parameters for the same server, regardless
  of deployment type.
- for the cat-dexscreener price data server, the search_pair param DOES NOT
  WORK. DO NOT USE. Otherwise, it's get_pair(tokenin/tokenout) and
  get_token_pair(ex_contract_addr)
- for the uniswap-trader-mcp execution server the params are:

```
tokenIn: The token you're giving/selling (input token)
tokenOut: The token you're getting/buying (output token)
For ETH/USDC trading:

If buying USDC with ETH: tokenIn = "NATIVE" (ETH), tokenOut = USDC_address
If buying ETH with USDC: tokenIn = USDC_address, tokenOut = "NATIVE" (ETH)

Amount Parameters
amountIn: Exact amount of input token you want to spend
amountOut: Exact amount of output token you want to receive
You use one or the other depending on tradeType:

exactIn: Specify amountIn (spend exactly X tokens, get whatever amount out)
exactOut: Specify amountOut (get exactly Y tokens, spend whatever amount needed)

Data Types
slippageTolerance: number (float) - percentage like 0.5 for 0.5% or 2.0 for 2%
deadline: number (integer) - minutes like 20 for 20 minutes
chainId: number (integer) - like 1 for Ethereum mainnet which is the only chain this server can use
All token amounts are strings (to handle large numbers precisely), like "1000000000000000000" for 1 ETH in wei.
```

You can use simple floats to calculate in this SINGLE edge case, as the data is
solely used for logging.

#### uniswap-trader-mcp

```
executeSwap structure:
{
  "transactionHash": "0x1234567890abcdef...",
  "status": "success",
  "gasUsed": "150000",
  "amountIn": "10000000000000000",
  "amountOut": "2500000000",
  "route": ["ETH", "USDC"],
  "priceImpact": "0.05",
  "blockNumber": 18500000
}
```

#### index

#### chain_configs.js

```

// chainConfigs.js
require('dotenv').config();

// Function to generate chain configs with dynamic API key
function getChainConfigs(infuraKey) {
  if (!infuraKey) {
    throw new Error("INFURA_KEY is required");
  }

const CHAIN_CONFIGS = {
  1: { // Ethereum Mainnet
    rpcUrl: `https://mainnet.infura.io/v3/${infuraKey}`,
    swapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    poolFactory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    weth: "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
    name: "Ethereum"
  },
  10: { // Optimism
    rpcUrl: `https://optimism-mainnet.infura.io/v3/${infuraKey}`,
    swapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    poolFactory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    weth: "0x4200000000000000000000000000000000000006",
    name: "Optimism"
  },
  137: { // Polygon
    rpcUrl: `https://polygon-mainnet.infura.io/v3/${infuraKey}`,
    swapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    poolFactory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    weth: "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
    name: "Polygon"
  },
  42161: { // Arbitrum One
    rpcUrl: `https://arbitrum-mainnet.infura.io/v3/${infuraKey}`,
    swapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    poolFactory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    weth: "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
    name: "Arbitrum One"
  },
  42220: { // Celo
    rpcUrl: `https://celo-mainnet.infura.io/v3/${infuraKey}`,
    swapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    poolFactory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    weth: "0x471EcE3750Da237f93B8E339c536989b8978a438", // CELO (not WETH)
    name: "Celo"
  },
  56: { // BNB Chain
    rpcUrl: "https://bsc-dataseed.binance.org/",
    swapRouter: "0xB971eF87edeb8e677893eAf6B013cA363c0eB0B2",
    poolFactory: "0xdB1d10011AD0Ff90774D0C6Bb92e5C5c8b4461F7",
    weth: "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c", // WBNB
    name: "BNB Chain"
  },
  43114: { // Avalanche
    rpcUrl: `https://avalanche-mainnet.infura.io/v3/${infuraKey}`,
    swapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    poolFactory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    weth: "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7", // WAVAX
    name: "Avalanche"
  },
  8453: { // Base
    rpcUrl: `https://base-mainnet.infura.io/v3/${infuraKey}`,
    swapRouter: "0xE592427A0AEce92De3Edee1F18E0157C05861564",
    poolFactory: "0x1F98431c8aD98523631AE4a59f267346ea31F984",
    weth: "0x4200000000000000000000000000000000000006",
    name: "Base"
  }
};

  return CHAIN_CONFIGS;
}

// For backward compatibility with local development
function getChainConfigsFromEnv() {
  const INFURA_KEY = process.env.INFURA_KEY;
  if (!INFURA_KEY) {
    throw new Error("INFURA_KEY environment variable is required");
  }
  return getChainConfigs(INFURA_KEY);
}

module.exports = { getChainConfigs, getChainConfigsFromEnv };


```
