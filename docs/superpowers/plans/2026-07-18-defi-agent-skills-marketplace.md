# DeFi Agent Skills Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `cyotee/defi-agent-skills` into an agent-facing marketplace that teaches AI agents how to **operate** DeFi protocols on-chain using the **Foundry stack** (`cast` for RPC reads/writes, `forge script` for multi-step sequences), culminating in IndexedEx interaction skills for the launch campaign.

**Architecture:** Layered plugins: (0) Foundry agent runtime + safety, (1) universal token/approval primitives, (2) protocol operation playbooks (Aave, Uniswap, Balancer, Aerodrome, Permit2), (3) IndexedEx product skills (registry discovery, Standard Exchange, DETF, bonds). Skills are **runbooks with exact CLI commands**, not protocol source dumps. Claude `marketplace.json` is source of truth; portable unit is `skills/*/SKILL.md`.

**Tech Stack:** Agent Skills (`SKILL.md`), Claude plugin marketplace format, Foundry (`cast`, `forge`, `anvil`), optional `forge script` Solidity helpers, deployment address JSON from IndexedEx `deployments/`.

## Global Constraints

- **Operational, not educational-internals:** Prefer user-entry interfaces, selectors, params, and `cast`/`forge script` recipes over full Solidity source of core contracts.
- **Foundry-first RPC:** Default tools are `cast call` / `cast send` / `cast estimate` / `cast receipt`. Use `forge script --rpc-url …` when a flow needs multi-step approve→deposit→mint with one broadcast. Do **not** require Bankr/viem/wagmi for core paths (optional later adapters).
- **Safety defaults:** Read-only first; writes require explicit user confirmation; never print private keys; use `$ETH_RPC_URL`, `$PRIVATE_KEY` or keystore; prefer testnets / Anvil forks in examples.
- **No address hallucination:** Every skill that uses addresses must load them from a versioned address table (`references/addresses.md` or `deployments/<network>.json`). If unknown, instruct agent to query registry / refuse.
- **Progressive disclosure:** `SKILL.md` ≤ ~200–300 lines of essential runbook; deep tables go in `references/`.
- **Do not fork-copy** full `cyotee-claude-plugins` architecture skills into this repo. Cross-link them for “how it works”; this marketplace owns “how to call it.”
- **Naming:** plugin `name` kebab-case; skill `name` matches directory; marketplace name stays `defi-agent-skills`.
- **Harness portability:** Skills first; slash commands optional; no hooks required for v1.

---

## Marketplace review (context for implementers)

### What already exists

| Asset | Location | Strength | Gap vs agent operations |
|-------|----------|----------|-------------------------|
| `cyotee-claude-plugins` | `projects-defi/cyotee-claude-plugins` | Deep protocol architecture skills (Aave, Uni V3/V4, Balancer V3, Aerodrome, Euler, etc.), Foundry developer skills, multi-harness install | Skills teach **internals** (Solidity dumps). Agents still cannot “supply USDC on Aave” or “deposit into IndexedEx vault” without inventing CLI. |
| Foundry plugin | `plugins/foundry` (+ GitHub `cyotee/foundry-skills`) | `cast-commands`, `forge-testing`, `forge-deployment`, `anvil-node` | Cast is generic CLI reference, not protocol playbooks. No agent safety loop, no address catalogs, no IndexedEx flows. |
| Permit2 plugin | `plugins/permit2` | Allowance / signature transfer patterns | Oriented to integrators writing Solidity/TS, not agent CLI execution. |
| IndexedEx repo skills | `daosys/lib/indexedex/.claude/skills` | `indexedex-testing`, script orchestration, crane testing | **Dev/test** focused, not external agent product usage. |
| Bankr skill pack | `daosys/lib/indexedex/lib/bankr-skills` | Excellent **agent-operational** skill style (triggers, CLI recipes, safety, confirmations) | Execution via Bankr API, not Foundry. Different product surface. |
| `defi-agent-skills` | this repo (submodule) | Empty marketplace skeleton | Needs full plugin tree. |

### Design lesson from Bankr (adopt) vs Bankr (do not copy)

**Adopt:** imperative runbooks, prerequisite checks, “read then write,” explicit confirmation, chain-scoped examples, failure recovery, trigger-rich frontmatter.

**Do not copy:** Bankr-specific wallet API, natural-language trade prompts as the only interface, x402 marketplace bloat. This marketplace’s differentiator is **sovereign Foundry CLI control** of protocol contracts.

### Tooling clarification (Forge vs Cast)

User-facing messaging may say “Foundry/Forge.” Implementation truth:

| Goal | Tool |
|------|------|
| Read chain state | `cast call`, `cast balance`, `cast storage`, `cast logs` |
| Send single tx | `cast send` |
| Encode/decode | `cast calldata`, `cast abi-encode`, `cast 4byte` |
| Gas / simulation | `cast estimate`, `cast call` (state override), `forge script --slow` dry paths |
| Multi-step atomic-ish flows | `forge script` with `vm.startBroadcast` |
| Local / fork rehearsal | `anvil --fork-url` + same cast recipes |

Every protocol skill MUST show **cast-first** recipes. Add `forge script` only when multi-tx choreography is error-prone as separate cast sends.

---

## Target marketplace layout

```text
defi-agent-skills/
  .claude-plugin/marketplace.json
  README.md
  AGENTS.md                          # how agents should use this marketplace
  docs/
    superpowers/plans/…              # this plan
    SKILL_AUTHORING.md               # skill template + QA checklist
  plugins/
    foundry-agent-runtime/           # Layer 0
    defi-primitives/                 # Layer 1
    aave-v3-ops/                     # Layer 2 examples
    uniswap-v3-ops/
    balancer-v3-ops/
    aerodrome-ops/
    permit2-ops/
    indexedex/                       # Layer 3 product (launch focus)
  scripts/
    check-skills.sh                  # frontmatter + path checks
    smoke-cast-recipes.sh            # optional live/fork smokes (gated)
```

---

## Skill quality bar (every skill)

Each `SKILL.md` must include:

1. YAML frontmatter: `name`, `description` (trigger-rich, “use when…”).
2. **Goal** in one sentence (what the agent accomplishes).
3. **Prerequisites:** binaries (`cast`, `forge`), env (`ETH_RPC_URL`), chain id, addresses source.
4. **Safety:** read-only vs write; confirmation gate; never log secrets.
5. **Discovery / inspect** (cast calls only).
6. **Dry-run** (`cast call` / `cast estimate` / quote).
7. **Execute** (`cast send` or `forge script`) with exact signatures.
8. **Verify** (post-tx `cast receipt`, balance/share re-reads).
9. **Common failures** (allowance, slippage, paused, wrong chain).
10. **References** link for addresses and full ABI tables.

---

## File map (create)

| Path | Responsibility |
|------|----------------|
| `AGENTS.md` | Top-level agent onboarding for the marketplace |
| `docs/SKILL_AUTHORING.md` | Template + review checklist |
| `plugins/foundry-agent-runtime/**` | Cast/forge RPC runtime for agents |
| `plugins/defi-primitives/**` | ERC20, WETH, approvals, units, safety |
| `plugins/*-ops/**` | Protocol operation playbooks |
| `plugins/indexedex/**` | IndexedEx agent product skills |
| `.claude-plugin/marketplace.json` | Catalog of all plugins |
| `scripts/check-skills.sh` | Structural validation |

---

### Task 1: Marketplace conventions + authoring guide

**Files:**
- Create: `AGENTS.md`
- Create: `docs/SKILL_AUTHORING.md`
- Modify: `README.md`
- Create: `scripts/check-skills.sh`

**Produces:** Conventions later tasks must follow; empty marketplace still valid.

- [ ] **Step 1: Write `AGENTS.md`**

Content requirements (implement fully):

- Purpose: agent-operable DeFi via Foundry.
- Install: `/plugin marketplace add cyotee/defi-agent-skills` then install plugins.
- Tool preference table (cast vs forge script).
- Global safety rules.
- How to resolve addresses (never invent).
- Relationship to `cyotee-claude-plugins` (architecture) vs this repo (operations).
- IndexedEx as flagship plugin.

- [ ] **Step 2: Write `docs/SKILL_AUTHORING.md`**

Include:

- Frontmatter template.
- Required sections checklist (from “Skill quality bar”).
- Signature style: always show Solidity-style signatures in cast strings, e.g. `"balanceOf(address)(uint256)"`.
- Units: prefer human amounts + `cast to-wei` examples.
- Address table format (markdown table: network, name, address, notes).
- Anti-patterns: pasting entire pool contracts; Bankr-only paths; mainnet PK in docs.

- [ ] **Step 3: Update root `README.md`**

- Positioning for AI-agent marketing.
- Layer diagram (0–3).
- Install for Claude / Grok / local.
- Plugin table (initially “scaffolded / planned” then update as plugins land).
- Link to `AGENTS.md` and this plan.

- [ ] **Step 4: Add `scripts/check-skills.sh`**

```bash
#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0
while IFS= read -r -d '' f; do
  if ! head -n 1 "$f" | grep -q '^---$'; then
    echo "FAIL: missing frontmatter: $f"; fail=1
  fi
  if ! grep -q '^name:' "$f"; then
    echo "FAIL: missing name: $f"; fail=1
  fi
  if ! grep -q '^description:' "$f"; then
    echo "FAIL: missing description: $f"; fail=1
  fi
done < <(find "$ROOT/plugins" -name SKILL.md -print0 2>/dev/null || true)
if [[ "$fail" -ne 0 ]]; then exit 1; fi
echo "OK: skill frontmatter checks passed"
```

- [ ] **Step 5: Commit**

```bash
cd /Users/cyotee/Development/projects-defi/defi-agent-skills
chmod +x scripts/check-skills.sh
git add AGENTS.md docs/SKILL_AUTHORING.md README.md scripts/check-skills.sh
git commit -m "docs: marketplace conventions and skill authoring guide"
```

---

### Task 2: Layer 0 — `foundry-agent-runtime` plugin

**Files:**
- Create: `plugins/foundry-agent-runtime/.claude-plugin/plugin.json`
- Create: `plugins/foundry-agent-runtime/README.md`
- Create: `plugins/foundry-agent-runtime/skills/foundry-rpc-runtime/SKILL.md`
- Create: `plugins/foundry-agent-runtime/skills/foundry-rpc-runtime/references/rpc-and-wallets.md`
- Create: `plugins/foundry-agent-runtime/skills/foundry-agent-safety/SKILL.md`
- Create: `plugins/foundry-agent-runtime/skills/foundry-script-ops/SKILL.md`
- Modify: `.claude-plugin/marketplace.json` — register plugin

**Produces:** Agents can configure RPC, read/write with cast, and know when to use forge script.

- [ ] **Step 1: Create plugin manifest**

```json
{
  "name": "foundry-agent-runtime",
  "description": "Foundry cast/forge runtime for AI agents: RPC config, reads, sends, simulation, and multi-step forge scripts",
  "version": "0.1.0",
  "author": { "name": "cyotee" }
}
```

- [ ] **Step 2: Author `foundry-rpc-runtime` skill**

Must cover:

```bash
# env
export ETH_RPC_URL=...
export CHAIN_ID=$(cast chain-id)
cast chain-id
cast block-number
cast balance $ADDR -e

# read
cast call $CONTRACT "fn(type)(ret)" args...

# write
cast send $CONTRACT "fn(type)" args... --private-key $PRIVATE_KEY
# prefer: --account / keystore when available

# decode
cast receipt $TX
cast 4byte 0x...
```

Include named RPC via `foundry.toml` `[rpc_endpoints]` pattern.

- [ ] **Step 3: Author `foundry-agent-safety` skill**

Mandatory agent policy:

1. Confirm chain id matches intended network.
2. For any value transfer or approval: print human-readable summary; wait for user OK.
3. Cap first live tx to small amounts.
4. Prefer Anvil fork rehearsal: `anvil --fork-url $ETH_RPC_URL` then point `ETH_RPC_URL=http://127.0.0.1:8545`.
5. Never echo `$PRIVATE_KEY`.
6. On revert: `cast receipt`, decode selector, do not blind-retry with higher gas blindly.

- [ ] **Step 4: Author `foundry-script-ops` skill**

When multi-step:

```solidity
// script/AgentOp.s.sol pattern
contract AgentOp is Script {
    function run() external {
        uint256 pk = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(pk);
        // approve + deposit + ...
        vm.stopBroadcast();
    }
}
```

```bash
forge script script/AgentOp.s.sol:AgentOp --rpc-url $ETH_RPC_URL --broadcast -vvvv
# dry: omit --broadcast
```

- [ ] **Step 5: Register in marketplace.json**

```json
{
  "name": "foundry-agent-runtime",
  "source": "./plugins/foundry-agent-runtime",
  "description": "Foundry cast/forge runtime for AI agents calling blockchain RPCs",
  "version": "0.1.0",
  "author": { "name": "cyotee" },
  "category": "development",
  "tags": ["foundry", "cast", "forge", "rpc", "agent"]
}
```

- [ ] **Step 6: Run checker + commit**

```bash
./scripts/check-skills.sh
git add plugins/foundry-agent-runtime .claude-plugin/marketplace.json
git commit -m "feat(foundry-agent-runtime): cast/forge RPC runtime and safety skills"
```

---

### Task 3: Layer 1 — `defi-primitives` plugin

**Files:**
- Create: `plugins/defi-primitives/.claude-plugin/plugin.json`
- Create: `plugins/defi-primitives/README.md`
- Create: `plugins/defi-primitives/skills/erc20-ops/SKILL.md`
- Create: `plugins/defi-primitives/skills/approval-ops/SKILL.md`
- Create: `plugins/defi-primitives/skills/weth-ops/SKILL.md`
- Create: `plugins/defi-primitives/skills/units-and-amounts/SKILL.md`
- Create: `plugins/defi-primitives/skills/erc20-ops/references/common-tokens.md`
- Modify: `.claude-plugin/marketplace.json`

**Produces:** Every later protocol skill can assume agents know approve/balance/units.

- [ ] **Step 1: `erc20-ops` skill — required cast recipes**

```bash
cast call $TOKEN "name()(string)"
cast call $TOKEN "symbol()(string)"
cast call $TOKEN "decimals()(uint8)"
cast call $TOKEN "balanceOf(address)(uint256)" $USER
cast call $TOKEN "allowance(address,address)(uint256)" $OWNER $SPENDER
cast send $TOKEN "transfer(address,uint256)" $TO $AMOUNT --private-key $PRIVATE_KEY
```

- [ ] **Step 2: `approval-ops` skill**

Patterns:

- Exact approve amount (preferred for agents).
- Infinite approve risk warning.
- USDT-style reset-to-zero then set.
- Verify allowance before spender call.

```bash
cast send $TOKEN "approve(address,uint256)" $SPENDER $AMOUNT --private-key $PRIVATE_KEY
cast call $TOKEN "allowance(address,address)(uint256)" $USER $SPENDER
```

- [ ] **Step 3: `weth-ops` skill**

```bash
cast send $WETH "deposit()" --value 0.01ether --private-key $PRIVATE_KEY
cast send $WETH "withdraw(uint256)" $(cast to-wei 0.01 ether) --private-key $PRIVATE_KEY
```

Addresses only via `references/common-tokens.md` (Base, Ethereum, Sepolia, Arbitrum — fill from known canonicals; document sources).

- [ ] **Step 4: `units-and-amounts` skill**

```bash
cast to-wei 1.5 ether
cast from-wei 1500000000000000000
# 6-decimal tokens
cast to-unit 1000000 6   # if available patterns; else manual 1e6
```

- [ ] **Step 5: Register + commit**

```bash
./scripts/check-skills.sh
git add plugins/defi-primitives .claude-plugin/marketplace.json
git commit -m "feat(defi-primitives): ERC20, approvals, WETH, units for agents"
```

---

### Task 4: Layer 2 — Protocol ops plugins (cast playbooks)

Ship **ops** plugins that thin-wrap entrypoints. Do **not** copy architecture skills wholesale. Each skill links “Deep internals: see cyotee-claude-plugins / plugin X.”

**Priority order (launch value + IndexedEx dependencies):**

| Plugin | Why |
|--------|-----|
| `permit2-ops` | IndexedEx + Balancer routers use Permit2 |
| `balancer-v3-ops` | IndexedEx DETF reserve + SE router path |
| `aave-v3-ops` | Canonical DeFi agent demo (supply/borrow) |
| `uniswap-v3-ops` | Canonical swap demo |
| `aerodrome-ops` | Base ecosystem + IndexedEx SE integration |

**Files (repeat pattern per plugin):**
- `plugins/<name>/.claude-plugin/plugin.json`
- `plugins/<name>/README.md`
- `plugins/<name>/skills/<skill>/SKILL.md`
- `plugins/<name>/skills/<skill>/references/addresses.md`
- marketplace entry

**Produces:** Agents can perform standard DeFi actions via cast on major protocols.

#### Task 4a: `permit2-ops`

Skills:

1. `permit2-allowance-cast` — `approve` token → Permit2; `Permit2.approve(token, spender, amount, expiration)`.
2. `permit2-signature-cast` — outline EIP-712 signing with `cast wallet sign` / forge for witness flows; when signature path is too heavy, document AllowanceTransfer cast path as default agent path.

Canonical Permit2: `0x000000000022D473030F116dDEE9F6B43aC78BA3` (document chain coverage).

#### Task 4b: `aave-v3-ops`

Skills:

1. `aave-v3-inspect` — PoolAddressesProvider → Pool; `getUserAccountData`, reserve data via cast.
2. `aave-v3-supply-withdraw` — approve + `supply` / `withdraw` cast recipes.
3. `aave-v3-borrow-repay` — health factor check before borrow; repay max pattern.

Source addresses from Aave address books (link official docs); put Base/Ethereum/Sepolia tables in references.

Example shape:

```bash
# inspect HF
cast call $POOL "getUserAccountData(address)(uint256,uint256,uint256,uint256,uint256,uint256)" $USER

# supply
cast send $ASSET "approve(address,uint256)" $POOL $AMOUNT --private-key $PK
cast send $POOL "supply(address,uint256,address,uint16)" $ASSET $AMOUNT $USER 0 --private-key $PK
```

#### Task 4c: `uniswap-v3-ops`

Skills:

1. `uniswap-v3-quote` — QuoterV2 cast (note: quoter often uses revert-data; document `cast call --trace` / known quoter patterns).
2. `uniswap-v3-swap-exact-in` — SwapRouter02 `exactInputSingle` with deadline + minOut.
3. `uniswap-v3-pool-read` — `slot0`, liquidity, token0/token1.

#### Task 4d: `balancer-v3-ops`

Skills:

1. `balancer-v3-vault-read` — pool tokens, balances via Vault query surfaces used by IndexedEx.
2. `balancer-v3-router-swap` — Router exact-in single token cast recipes.
3. `balancer-v3-add-remove-liquidity` — proportional join/exit high-level cast.

Keep lighter than architecture plugin; enough for agents to move tokens.

#### Task 4e: `aerodrome-ops`

Skills:

1. `aerodrome-pool-read`
2. `aerodrome-router-swap`
3. `aerodrome-liquidity` (optional v1.1)

- [ ] **Step (per plugin): scaffold, author SKILL.md with addresses, marketplace entry, `./scripts/check-skills.sh`, commit**

Suggested commits:

```bash
git commit -m "feat(permit2-ops): agent cast playbooks for Permit2 allowances"
git commit -m "feat(aave-v3-ops): supply/borrow/repay cast runbooks"
git commit -m "feat(uniswap-v3-ops): quote and swap cast runbooks"
git commit -m "feat(balancer-v3-ops): vault/router cast runbooks"
git commit -m "feat(aerodrome-ops): swap cast runbooks for Base"
```

---

### Task 5: Layer 3 — IndexedEx flagship plugin (launch campaign)

**Source of truth for product behavior:**  
`daosys/lib/indexedex/` — `AGENTS.md`, `contracts/interfaces/*`, `deployments/*`, component docs under `docs/components/`.

**Files:**
- Create: `plugins/indexedex/.claude-plugin/plugin.json`
- Create: `plugins/indexedex/README.md`
- Create: skills listed below
- Create: `plugins/indexedex/skills/*/references/` address + selector tables
- Create: `plugins/indexedex/scripts/` optional forge helper scripts later
- Modify: marketplace.json

**Skill set (v1 MVP for agents):**

| Skill | Agent capability |
|-------|------------------|
| `indexedex-overview` | What IndexedEx is; user roles; DETF vs Standard Exchange vs registry; when to use which surface |
| `indexedex-networks-addresses` | Load addresses from deployment artifacts; chain ids; env vars |
| `indexedex-registry-discovery` | `vaults()`, `isVault`, `vaultsOfToken`, package queries via cast |
| `indexedex-standard-exchange` | SE vault inspect + exchange-in/out routes via cast (from `IStandardExchange*` / proxy interfaces) |
| `indexedex-balancer-se-router` | Balancer V3 SE router exact-in/out + Permit2 variants |
| `indexedex-detf-user-flows` | Live vs inert; mint/burn gates; bond; claim redeem high-level cast sequences |
| `indexedex-agent-checklist` | Pre-trade checklist: chain, registry, allowances, previews, slippage, verify |

**Deferred (v1.1+):** Protocol DETF family-specific skills, fee oracle admin, NFT vault operator flows, cross-chain supersim.

#### Task 5a: Overview + addresses

- [ ] **Step 1: `indexedex-overview`**

Explain in agent language (from IndexedEx AGENTS.md / PRD):

- Modular Diamond vault infrastructure.
- **Standard Exchange (SE):** unified swap/liquidity vault abstraction over DEXes.
- **DETF:** diamond-as-share ERC20; seigniorage vs reserve; bond NFT + rebasing claim.
- **Vault Registry:** discovery.
- **Manager:** deployment/registry hub (`IIndexedexManagerProxy`).

User routes (defaults from AGENTS.md):

- Prefer vault shares ↔ DETF on DETF surface.
- RateAsset as mint input usually requires deposit into SE first.
- No inventing approximate solvers.

- [ ] **Step 2: `indexedex-networks-addresses`**

- Document how agents should read deployment JSON from IndexedEx repo when present, or vendored copies under `plugins/indexedex/references/deployments/`.
- For public marketing marketplace: **vendor** a minimal `public_sepolia` / `base_sepolia` address file (copied from `daosys/lib/indexedex/deployments/`) so agents do not need the monorepo.
- Include chain ids and RPC env names.

Copy policy: commit a **snapshot** JSON + `SOURCE` note with commit SHA of IndexedEx; refresh script optional later.

#### Task 5b: Registry discovery

- [ ] **Step 3: `indexedex-registry-discovery`**

From `IVaultRegistryVaultQuery`:

```bash
cast call $VAULT_REGISTRY "vaults()(address[])"
cast call $VAULT_REGISTRY "isVault(address)(bool)" $VAULT
cast call $VAULT_REGISTRY "vaultsOfToken(address)(address[])" $TOKEN
cast call $VAULT_REGISTRY "isContainedToken(address)(bool)" $TOKEN
```

Also document package query interfaces if needed for “find SE of type X.”

Agent rule: **discover then act** — never hardcode vault addresses in conversation without registry or address book confirmation.

#### Task 5c: Standard Exchange + router

- [ ] **Step 4: Pull exact function signatures from interfaces**

Implementer must open and quote signatures from:

- `contracts/interfaces/IStandardExchange.sol` (+ In/Out via Crane re-exports if needed)
- `IBalancerV3StandardExchangeRouterExactInSwap.sol`
- `IBalancerV3StandardExchangeRouterExactOutSwap.sol`
- Permit2 witness interfaces as applicable

For each user action, SKILL.md must show:

1. Inspect vault tokens / config.
2. Preview/query if available (`*Query` interfaces).
3. Approve (ERC20 or Permit2).
4. Execute swap/deposit route.
5. Verify balances.

Example pattern (signatures must match source at implement time):

```bash
cast call $ROUTER "..." # query
cast send $TOKEN "approve(address,uint256)" $ROUTER $AMOUNT --private-key $PK
cast send $ROUTER "swapSingleTokenExactIn(...)" ... --private-key $PK
```

#### Task 5d: DETF user flows

- [ ] **Step 5: `indexedex-detf-user-flows`**

Cover agent-visible flows from interfaces (`IProtocolDETF`, `IComposedStableCommonDetfBonding`, `ISeigniorageDETF` as relevant):

1. **Inspect:** `mintThreshold`, `burnThreshold`, live/reserve status, accepted bond tokens.
2. **Exchange / mint-burn** when live (exact-in closed form only).
3. **Bond:** `bond(tokenIn, amountIn, lockDuration, recipient, deadline)`.
4. **Claim / redeem** high-level path (point to claim token + redeem entrypoints; warn about burnShares discipline).
5. **Inert vs live:** refuse seigniorage mint instructions if not live; guide first bond only when docs support agent-initiated bootstrap (often operator-only — state that clearly).

Safety: DETF economics are subtle; skill must say **preview + small size + confirm thresholds**.

#### Task 5e: Agent checklist + README marketing

- [ ] **Step 6: `indexedex-agent-checklist`**

Numbered pre-flight:

1. Plugin install + Foundry available.
2. Correct network / RPC.
3. Address book loaded.
4. Registry validates vault.
5. Token decimals/balances.
6. Allowance path chosen.
7. Preview/query.
8. User confirmation.
9. Broadcast.
10. Receipt + state re-read.
11. Report tx hash + explorer link.

- [ ] **Step 7: Plugin README for campaign**

Marketing-ready install blurb:

```bash
/plugin marketplace add cyotee/defi-agent-skills
/plugin install foundry-agent-runtime@defi-agent-skills
/plugin install defi-primitives@defi-agent-skills
/plugin install indexedex@defi-agent-skills
```

“What agents can do” bullet list (discover vaults, exchange, bond, inspect DETF).

- [ ] **Step 8: Commit**

```bash
./scripts/check-skills.sh
git add plugins/indexedex .claude-plugin/marketplace.json
git commit -m "feat(indexedex): agent cast runbooks for registry, SE, DETF"
```

---

### Task 6: Optional forge script pack for IndexedEx multi-step ops

**Files:**
- Create: `plugins/indexedex/scripts/foundry/` minimal package or document scripts living in skill references
- Create: `plugins/indexedex/skills/indexedex-forge-scripts/SKILL.md`

**Produces:** One-command multi-step flows for agents that struggle with sequential cast.

- [ ] **Step 1: Add script templates**

Examples:

- `ApproveAndSwapExactIn.s.sol`
- `ApproveAndBond.s.sol`

Use env-configured addresses; no hardcoded mainnet keys.

- [ ] **Step 2: Document run commands**

```bash
forge script ... --rpc-url $ETH_RPC_URL --broadcast -vvvv
```

- [ ] **Step 3: Commit**

```bash
git commit -m "feat(indexedex): forge script templates for multi-step agent ops"
```

---

### Task 7: QA, smoke tests, and dual-harness notes

**Files:**
- Create: `docs/QA.md`
- Create: `scripts/smoke-cast-recipes.sh` (manual/gated)
- Modify: `README.md` (QA section)
- Optional: copy `generate-codex-marketplace.py` pattern from `cyotee-claude-plugins` only if Codex install is a launch requirement

- [ ] **Step 1: Manual QA matrix**

For each skill: agent (or human) runs read-only path on public Sepolia/Base Sepolia with real addresses.

| Skill | Read smoke | Write smoke (testnet) |
|-------|------------|------------------------|
| foundry-rpc-runtime | chain-id, balance | N/A |
| erc20-ops | USDC decimals/balance | tiny transfer to self |
| aave-v3-ops | getUserAccountData | tiny supply if faucet |
| indexedex-registry | vaults() | N/A |
| indexedex-se | query | tiny swap if liquidity |

- [ ] **Step 2: `scripts/smoke-cast-recipes.sh`**

Gated by `SMOKE_RPC_URL` and `SMOKE_NETWORK`; skip if unset. Only **read** calls in CI.

- [ ] **Step 3: Commit**

```bash
git commit -m "test: skill QA matrix and optional cast smoke script"
```

---

### Task 8: Publish + monorepo submodule bump

**Files:**
- Push `defi-agent-skills` `main`
- Update submodule pointer in `projects-defi`
- Optional: announce install line in IndexedEx `README` / launch docs (separate PR in daosys/indexedex)

- [ ] **Step 1: Push marketplace**

```bash
cd /Users/cyotee/Development/projects-defi/defi-agent-skills
git push origin main
```

- [ ] **Step 2: Bump parent submodule**

```bash
cd /Users/cyotee/Development/projects-defi
git add defi-agent-skills
git commit -m "chore: bump defi-agent-skills submodule"
# push parent only if user wants
```

- [ ] **Step 3: Verify install from GitHub**

```text
/plugin marketplace add cyotee/defi-agent-skills
/plugin install indexedex@defi-agent-skills
```

---

## Implementation phases (summary)

| Phase | Tasks | Outcome |
|-------|-------|---------|
| **P0 — Scaffold** | 1–3 | Agents have Foundry runtime + token primitives |
| **P1 — Protocol ops** | 4a–4e | Agents can do Aave/Uni/Balancer/Aero/Permit2 via cast |
| **P2 — IndexedEx launch** | 5–6 | Agents can discover and use IndexedEx on testnets |
| **P3 — Harden** | 7–8 | Smokes, publish, marketing install path |

**Recommended first ship for campaign:** P0 + P2 (with Permit2 + Balancer ops as dependencies of IndexedEx), then fill remaining Layer 2 for credibility.

---

## What not to build in v1

- Full architecture mirrors of Uniswap/Aave skills from `cyotee-claude-plugins`
- Bankr/x402 skill rehosting
- Frontend/wagmi skills (already covered elsewhere)
- Admin diamondCut / fee oracle governance for agents
- Mainnet “set-and-forget” autonomous trading bots without human confirmation
- Hallucinated mainnet IndexedEx addresses before deployment artifacts exist

---

## Relationship diagram

```text
┌─────────────────────────────────────────────────────────────┐
│ cyotee-claude-plugins                                       │
│  "How does the protocol work?" (architecture, Solidity)     │
└──────────────────────────▲──────────────────────────────────┘
                           │ cross-link only
┌──────────────────────────┴──────────────────────────────────┐
│ defi-agent-skills (this repo)                               │
│  "How do I call it on-chain with Foundry?"                  │
│                                                             │
│  L0 foundry-agent-runtime → L1 defi-primitives              │
│       → L2 *-ops → L3 indexedex                             │
└──────────────────────────▲──────────────────────────────────┘
                           │ addresses / interfaces
┌──────────────────────────┴──────────────────────────────────┐
│ daosys/lib/indexedex                                        │
│  contracts, deployments/, product truth                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Self-review

| Spec intent | Task coverage |
|-------------|----------------|
| Review existing marketplace | “Marketplace review” section |
| Skills for agents to interact with DeFi | Tasks 3–4 |
| Use Forge/Foundry for RPCs | Tasks 2, 6; cast/forge clarification |
| IndexedEx product skills | Task 5–6 |
| Marketplace repo readiness | Tasks 1, 7–8 |

Placeholder scan: no TBD-only steps; signatures that depend on live interfaces are explicitly “read from interface file at implement time” with paths given.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-07-18-defi-agent-skills-marketplace.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task (or phase), review between tasks  
2. **Inline Execution** — implement P0→P2 in this session with checkpoints  

**Which approach?**
