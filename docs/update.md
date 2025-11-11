Previous work: Test pass. Smith rebuild fails. Agent is referring to Defi
contract that Smithery server calls, not Smithery "contract." Got the Smithery
contract back on spec by wiring up rate-limited HTTP helpers, all seven required
tools (plus the legacy alias), and both documentation resources directly inside
the server entry point, then added the missing operational scripts so the
documented install/test flow actually works.

src/index.ts (lines 1-287) now hosts a reusable rate limiter +
fetchWithRateLimit, consistent success/error helpers typed as CallToolResult,
and the full tool suite (get_latest_token_profiles, get_latest_boosted_tokens,
get_top_boosted_tokens, get_token_orders, get_pairs_by_chain_and_address,
get_pairs_by_token_addresses, search_pairs, plus the deprecated get_token_pairs
alias). Each handler validates inputs, encodes path segments safely, and shares
the same error formatting so Claude/Smithery get predictable results. Added the
dexscreener_api_docs and memecoin_best_practices resources inline so Claude can
fall back to documentation/context as required by Smithery. package.json (lines
6-13) adds the previously missing setup script (node scripts/setup-claude.js) so
npm run setup in README/install.sh finally works, and makes npm test build first
so the compiled tests actually exist. package-lock.json updated automatically
when installing dependencies so TypeScript/Smithery tooling can compile the new
entry point. Validation:

npm run build ✅ npm test ❌ – fails immediately with DexScreenerError: Network
error: fetch failed while the integration suite tries to reach
https://api.dexscreener.com. Re-run once your environment allows outbound
fetches. Next steps:

Re-run npm test in an environment with outbound network access to verify the
live DexScreener calls and rate limiting. Deploy through Smithery (npx
@smithery/cli deploy) once tests pass so Claude picks up the expanded
tool/resource surface. prev plan: Findings

src/index.ts (lines 13-75) only registers three tools (search_pairs, get_pair,
get_token_pairs), while both the README and CLAUDE guidance promise seven tools
plus resources (README.md (lines 95-180), CLAUDE.md (lines 34-78)).
Smithery/Claude deployments that try to call get_latest_token_profiles,
get_pairs_by_chain_and_address, etc. receive “tool not found”, which is exactly
why GET/SEARCH workflows fail. Even the pair tools that do exist are
incompatible with the published contract: external clients are coded to call
get_pairs_by_chain_and_address with a pairId, but the server exposes get_pair
with pairAddress (src/index.ts (lines 35-44) vs README.md (lines 144-156)). That
mismatch guarantees runtime failures for GET pair requests even though the
underlying DexScreener endpoint works. The documented rate limiting, typed
responses, and richer error handling live in src/services/dexscreener.ts (lines
15-137), but nothing imports that service. The live server makes raw axios calls
without throttling or typed validation, so any burst of search_pairs calls
quickly hits DexScreener’s 300 rpm cap and returns opaque 500/429 errors—hence
the “sometimes GET succeeds, SEARCH doesn’t” behaviour you’re seeing.
Smithery-specific resources mentioned in FIX.md (API docs + memecoin best
practices) were never wired up. No server.resource(...) calls exist in
src/index.ts, so Claude cannot “use the other remaining two tool calls to
recreate the third” via documentation/context the way Smithery expects.
Operational scripts don’t match the published setup flow. Both README.md (lines
24-30) and install.sh (lines 8-19) instruct npm run setup, but there is no setup
entry in package.json (lines 6-12), so the one-line install always stops with
“missing script: setup” before it ever registers the server with Claude Desktop.
The test pipeline in package.json (lines 6-11) runs node
build/tests/dexscreener.test.js with no preceding build, so npm test fails on a
clean checkout because build/… doesn’t exist. Combined with the lack of CI
wiring, none of the integration tests that verify pairs/search/tools are
actually exercised. Next Steps

Decide whether to finish the inline plan from FIX.md or to reinstating
DexScreenerService; either way, expose the seven documented tools (with matching
names/params), add the two resources, and reuse the rate-limited service layer
so Smithery/Claude gets the contract it expects. Wire up the operational
workflow ("setup": "node scripts/setup-claude.js", make npm test run npm run
build && node …, etc.) so README/install instructions work verbatim and
Smithery’s cloud build has a reproducible entrypoint. Plan was not successful.
It's impossible to tell if server function is designed. Please review Context7
docs for Smithery info.
## 2025-11-09
- Reviewed the Smithery "TypeScript with Smithery CLI" migration guide and confirmed that Step 4/5 require the `module` hint plus separate `build:http`, `build:stdio`, `start:http`, and `start:stdio` scripts so the CLI can orchestrate HTTP transport while custom containers keep STDIO fallbacks.
- Updated `package.json` scripts accordingly, added the `prepublishOnly` safeguard, and moved `@smithery/cli` into `devDependencies` while promoting `@smithery/sdk` to a runtime dependency so the generated `.smithery/index.cjs` has everything it needs in cloud builds.
- Regenerated `package-lock.json` via `npm install` and re-ran the full integration suite (`npm test`) plus the Smithery build (`npm run build:http`), both of which now succeed locally; note the tests require outbound HTTPS to DexScreener.
- New workflow:
    - Local HTTP playground: `npm run dev`
    - Smithery artifact: `npm run build:http`
    - STDIO fallback: `npm run start:stdio`
    - Container/cloud deploy: build the Docker image (uses `.smithery/index.cjs`) and push/run it with your SMITHERY_API_KEY.
- Next unblockers: hook `npm run build:http` into CI so artifacts stay fresh, and keep runtime images (Dockerfile, Kubernetes, etc.) pinned to the same CLI version (>=1.6.3) so the artifact you test locally matches production.
## 2025-11-10 (2)
- Clarified deployment workflow: the Smithery CLI (v1.6.3) does not expose a `deploy` command, so our scripts now point builders at `npm run build:http` (HTTP artifact) or `npm run start:http` (runtime). Removed the broken `npm run deploy` alias from `package.json` to avoid future confusion.
- To ship the server, either (a) run `smithery dev` for local testing or `npm run start:http` with `SMITHERY_API_KEY` in your environment, or (b) build/push the Docker image—which now runs `.smithery/index.cjs` directly—into your own infrastructure.
## 2025-11-10 (3)
- Tool handlers now accept common alias parameter names (`token_address`, `contractAddress`, `pairAddress`, etc.) via a shared `getStringArg` helper, preventing Smithery clients from tripping the "Missing tokenAddress" guard when they use snake_case fields.
- Error payloads are JSON encoded (`{"error": "..."}`) instead of plain strings, so downstream automations like pydantic_trader can continue to `json.loads` even when a request fails.
- `npm test` (STDIO build + integration suite) still passes after the normalization changes.
