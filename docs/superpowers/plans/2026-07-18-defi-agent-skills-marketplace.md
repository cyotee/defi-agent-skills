# DeFi Agent Skills Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `cyotee/defi-agent-skills` as a **curated AI-agent marketplace**: only skills needed to **interact with DeFi on-chain**, composed primarily as **git submodules** of shared plugin repos so all marketplaces share one source of truth (with intentional drift allowed later).

**Architecture:** Catalog-of-submodules. Plugins live in independent GitHub repos; marketplaces only pin versions via `.gitmodules` + `.claude-plugin/marketplace.json`. This marketplace **must not** install architecture/dev/test skills that force agents to filter noise. If a plugin mixes **development** knowledge with **interaction** knowledge, **split it** into separate repos and update **both** `cyotee-claude-plugins` and `defi-agent-skills`.

**Tech Stack:** Agent Skills (`SKILL.md`), Claude plugin marketplace + Codex dual-ship + OpenCode bridge (full multi-harness), git submodules, Foundry (`cast`/`forge`/`anvil`) and other **execution backends as separate plugins**, deployment address JSON from IndexedEx.

## Locked decisions (from requirements review)

| Topic | Decision |
|-------|----------|
| **foundry-agent placement** | List in **both** `cyotee-claude-plugins` and `defi-agent-skills`. Slim `foundry-skills` to pure test/deploy/project. |
| **Repo / plugin naming** | **`{protocol}-ops`** pattern: `aave-v3-ops`, `permit2-ops`, `balancer-v3-ops`, `indexedex-ops`, etc. Architecture stays `*-skill`. |
| **Chains / writes** | Include **mainnet / Base mainnet** recipes **when addresses exist**; still require explicit confirmation on every write. Testnet tables required for rehearsal. |
| **Multi-harness** | **Claude, Grok, OpenCode, and Codex** all supported at launch (marketplace.json SoT + Codex generator + OpenCode install/bridge, following `cyotee-claude-plugins`). |
| **Execution backends** | **Split by tool** so agents only load the backend they use for RPCs/txs. e.g. `foundry-agent` (cast/forge) vs `bankr-ops` (Bankr wallet/API) as **separate plugins** — not one skill that teaches both. Protocol `*-ops` skills should be backend-agnostic where possible (function selectors, params, safety) and **delegate execution** to the installed backend plugin; or provide backend-specific sections only when necessary, without requiring Bankr if using Foundry. |

## Global Constraints

- **Agent-only catalog:** `defi-agent-skills` lists only plugins whose skills help an agent **discover, read, quote, approve, execute, and verify** DeFi actions. No Crane style guides, no forge-fuzz suites, no architecture-only dumps, no Playwright/Synpress, no boardgame, etc.
- **Submodule SoT:** Prefer `git submodule add https://github.com/cyotee/<plugin-repo>.git plugins/<name>`. Do **not** copy-paste skill trees into this repo. Local `plugins/*` only for marketplace-native glue that has no shared repo yet (then extract when stable).
- **Drift is allowed later:** Submodule pins are intentional versions. A marketplace may later fork or pin a divergent commit; document why in the marketplace README if so.
- **Split on mingle:** If one repo serves both “how to implement/test this” and “how to call this on-chain,” split into `*-skill` (dev/architecture) vs `*-ops` (interaction). Update `.gitmodules` + marketplace.json in **every** marketplace that consumed the old combined repo.
- **Operational skill bar:** Runbooks with exact CLI/API, addresses from tables, safety gates — not full protocol source dumps.
- **Execution backends are separate plugins:** Agents install `foundry-agent` **or** `bankr-ops` (etc.), not a combined mega-runtime. Protocol ops must not force loading unused backends.
- **Default recipes use Foundry** when illustrating `*-ops` (widely available CLI); Bankr variants live under `bankr-ops` or thin “execute via Bankr submit” references, not mixed into every skill body as required reading.
- **No address hallucination:** Refuse if address book / registry cannot resolve. Prefer live deployment artifacts; document mainnet only when real addresses are known.
- **Write safety:** Every state-changing path requires explicit user confirmation (all networks, including mainnet).
- **Cross-link, don’t rehost architecture:** Point to architecture `*-skill` repos for internals; this marketplace stays thin and actionable.
- **Naming:** interaction plugins use **`{name}-ops`**; architecture/dev keep existing `*-skill` names. Foundry agent package: plugin id `foundry-agent`, repo `foundry-agent-skills` (or `foundry-ops` — prefer `foundry-agent` to avoid confusion with forge-the-binary).
- **Multi-harness at launch:** Claude catalog SoT; generate Codex dual-ship; OpenCode bridge/install path (reuse patterns from `cyotee-claude-plugins`).

---

## Marketplace review

### How `cyotee-claude-plugins` is already structured

Most plugins are **already separate GitHub repos**, linked as submodules:

| Plugin path | Remote (submodule) | Role today |
|-------------|-------------------|------------|
| `plugins/foundry` | `cyotee/foundry-skills` | **Mingled** — cast + anvil + forge test/deploy/fuzz |
| `plugins/aave-v3` | `cyotee/aave-v3-skill` | Architecture only (no cast playbooks) |
| `plugins/aave-v4` | `cyotee/aave-V4-skill` | Architecture only |
| `plugins/uniswap-v3` | `cyotee/uniswap-V3-skill` | Architecture only |
| `plugins/uniswap-v4` | `cyotee/uniswap-V4-skill` | Architecture only |
| `plugins/balancer-v3` | `cyotee/balancer-v3-skill` | Architecture only |
| `plugins/aerodrome` | `cyotee/aerodrome-skill` | Architecture only |
| `plugins/aerodrome-slipstream` | `cyotee/aerodrome-V2-slipstream-skill` | Architecture only |
| `plugins/compound-v3-comet` | `cyotee/compound-V3-comet-skill` | Architecture only |
| `plugins/euler-lending` | `cyotee/euler-lending-skill` | Architecture only |
| `plugins/resupply` | `cyotee/resupply-skill` | Architecture only |
| `plugins/crane` | `cyotee/cyotee-claude-plugin-crane` | **Dev** (architecture, testing, style) |
| `plugins/playwright` / `synpress` / `metamask` / `defi-ui-testing` | respective repos | **Dev/UI test** — not agent DeFi ops |
| `plugins/permit2` | **local only** (`./plugins/permit2`) | Integrator TS/Solidity — not agent cast |
| `plugins/tevm`, `wagmi`, `chainlink`, `reliquary` | **local only** | Dev/integration |

`marketplace.json` often points `source` at the GitHub repo (install-from-GitHub) while the monorepo still vendors the same tree as a submodule for editing.

### Classification signal (measured)

Sampled protocol skills under aave/uniswap/balancer/aerodrome: **~0 `cast` references**, heavy ````solidity` blocks → **architecture/education**, not agent interaction.

Foundry plugin: **`cast-commands` / `anvil-node` / parts of `forge-deployment`** are agent-relevant; **`forge-testing` / `forge-fuzz-testing` / `forge-signing` (test-oriented)** are developer-relevant → **MINGLE → SPLIT**.

Permit2 plugin: SDK, wagmi, Solidity contract patterns → **integration/dev**, not agent CLI → **do not submodule whole package into agent marketplace**; create **`permit2-ops`** for cast runbooks (may reuse `permit2-addresses` content by extracting or subpath later).

### Two-marketplace product split

```text
┌──────────────────────────────────────────────────────────────┐
│ cyotee-claude-plugins  (developer + architecture + tooling)  │
│  crane, forge-testing, aave-v3-skill (internals), UI E2E…    │
└───────────────────────────────▲──────────────────────────────┘
                                │ same submodule remotes
                                │ (pins may differ)
┌───────────────────────────────┴──────────────────────────────┐
│ defi-agent-skills  (AI agents interacting with DeFi)         │
│  foundry-agent / bankr-ops (backends), *-ops, indexedex-ops  │
│  NO architecture dumps, NO test frameworks as product skills │
└──────────────────────────────────────────────────────────────┘
```

Agents installing `defi-agent-skills` should never have to open 8 Uniswap architecture skills to find one swap recipe.

---

## Submodule composition model

### Layout of `defi-agent-skills`

```text
defi-agent-skills/
  .gitmodules
  .claude-plugin/marketplace.json    # only agent-facing plugins
  README.md
  AGENTS.md
  docs/
    superpowers/plans/…
    SKILL_AUTHORING.md
    PLUGIN_CATALOG.md                # which remotes, audience, pin notes
  plugins/                           # almost all git submodules
    foundry-agent/                   # NEW repo (split from foundry-skills)
    defi-primitives/                 # NEW repo (or local→extract)
    permit2-ops/                     # NEW repo
    aave-v3-ops/                     # NEW repo
    uniswap-v3-ops/                  # NEW repo
    balancer-v3-ops/                 # NEW repo
    aerodrome-ops/                   # NEW repo
    indexedex/                       # NEW repo (flagship product ops)
  scripts/
    check-skills.sh
    check-submodules.sh
    bump-plugin.sh                   # helper: update one submodule pin
```

### Rules for adding a plugin

1. Plugin content lives in `https://github.com/cyotee/<repo>`.
2. `git submodule add <url> plugins/<name>` in **each** marketplace that should ship it.
3. Register in that marketplace’s `.claude-plugin/marketplace.json` with:
   - `source: { "source": "github", "repo": "cyotee/<repo>" }` for remote install, **or**
   - `source: "./plugins/<name>"` for monorepo/path install (Codex local clone path).
4. Prefer the same path name across marketplaces (`plugins/aave-v3-ops`) when both ship it.
5. **Never** add an architecture-only submodule to `defi-agent-skills` “just in case.”

### Audience tags (for PLUGIN_CATALOG.md)

| Tag | Meaning | Belongs in |
|-----|---------|------------|
| `agent-ops` | Call protocols on-chain | `defi-agent-skills` (required) |
| `architecture` | How protocol works internally | `cyotee-claude-plugins` only |
| `dev-tooling` | Write/test/deploy contracts | `cyotee-claude-plugins` only |
| `mingled` | Both → **must split** | neither until split complete |

---

## Split & new-repo matrix

### Already pure architecture (do **not** submodule into agent marketplace)

Keep as-is in `cyotee-claude-plugins` only:

- `aave-v3-skill`, `aave-V4-skill`, `uniswap-V3-skill`, `uniswap-V4-skill`, `balancer-v3-skill`, `aerodrome-skill`, `aerodrome-V2-slipstream-skill`, `compound-V3-comet-skill`, `euler-lending-skill`, `resupply-skill`, crane, UI testing plugins, etc.

**Action for agent needs:** create **new** `cyotee/<protocol>-ops` (or `*-agent-skills`) repos with cast runbooks. Optionally each ops skill’s README links to the architecture repo for deep dives.

### Must split: `cyotee/foundry-skills` (MINGLED)

| Stay in foundry-skills (dev marketplace) | Move / new foundry-agent repo |
|------------------------------------------|-------------------------------|
| `forge-testing` | `cast-commands` (SoT remains shared or move) |
| `forge-fuzz-testing` | `anvil-node` (agent local/fork rehearsal) |
| `forge-signing` (test sigs) | NEW: `foundry-agent-safety` |
| `foundry-project` | NEW: `foundry-script-ops` (multi-step broadcast) |
| `forge-deployment` (mostly deploy) | slim “cast RPC runtime” skill if needed |
| `supersim` (dev multi-L2) | optional later if agents need Superchain ops |

**Preferred split design:**

1. Create **`cyotee/foundry-agent-skills`** (name flexible) containing agent-facing skills only.
2. **Move** `cast-commands` (+ `patterns.md`) and `anvil-node` into the new repo (git history filter optional; file move + commit is fine).
3. Leave test/deploy skills in `cyotee/foundry-skills`.
4. Update **`cyotee-claude-plugins`**:
   - Keep submodule `plugins/foundry` → `foundry-skills` (dev).
   - **Add** submodule `plugins/foundry-agent` → `foundry-agent-skills` **if** developers should also install cast agent skills from the big marketplace — **OR** only list foundry-agent in `defi-agent-skills` and leave a README link from foundry-skills (“for agent cast runtime see …”).
5. **Locked:** Ship `foundry-agent` in **both** marketplaces. **Remove** cast/anvil from fat `foundry-skills` so it is pure dev. Single SoT repo submodule’d in both — **no** duplicate `cast-commands`.

### Not split, not agent: local `permit2` package

- Leave integrator package in `cyotee-claude-plugins` (extract to `cyotee/permit2-skill` submodule when convenient — orthogonal cleanup).
- Create **`cyotee/permit2-ops`** for agent cast: addresses, `approve`→Permit2, AllowanceTransfer via cast, signature path notes.

### New product: IndexedEx agent plugin

- Create **`cyotee/indexedex-ops`** as independent repo.
- Submodule only into `defi-agent-skills` for launch; optionally also into `cyotee-claude-plugins` later if desired (not required for uncluttered agent UX).
- Do **not** publish IndexedEx testing/crane skills into the agent marketplace.

### New primitives repo

- Create **`cyotee/defi-primitives-ops`**: ERC20, WETH, approvals, units, agent confirmation patterns for token ops.
- Submodule into `defi-agent-skills` (primary); optional in developer marketplace.

---

## Skill quality bar (agent-ops only)

Each interaction `SKILL.md` must include:

1. Frontmatter: `name`, trigger-rich `description`.
2. Goal (one sentence).
3. Prerequisites (binaries, env, chain, address source).
4. Safety (read vs write; confirmation; no secret logging).
5. Inspect (`cast call` …).
6. Dry-run / quote / estimate.
7. Execute (`cast send` / `forge script`).
8. Verify (receipt + re-read state).
9. Common failures.
10. Link to architecture plugin repo if deep internals needed.

---

## Target catalog for `defi-agent-skills` v1

| Plugin (path) | Remote repo | Origin |
|---------------|-------------|--------|
| `foundry-agent` | `cyotee/foundry-agent-skills` | **Split** from `foundry-skills` (both marketplaces) |
| `bankr-ops` | `cyotee/bankr-ops` (or extract from Bankr pack) | **New/thin** — Bankr wallet/API execution backend only; optional install |
| `defi-primitives` | `cyotee/defi-primitives-ops` | **New** |
| `permit2-ops` | `cyotee/permit2-ops` | **New** |
| `aave-v3-ops` | `cyotee/aave-v3-ops` | **New** (architecture stays `aave-v3-skill`) |
| `uniswap-v3-ops` | `cyotee/uniswap-v3-ops` | **New** |
| `balancer-v3-ops` | `cyotee/balancer-v3-ops` | **New** |
| `aerodrome-ops` | `cyotee/aerodrome-ops` | **New** |
| `indexedex-ops` | `cyotee/indexedex-ops` | **New** flagship |

**Explicitly excluded from this marketplace:** architecture protocol skills, crane, forge-testing/fuzz, playwright/synpress/metamask/defi-ui-testing, boardgame, homunculus, qmd, voltaire (unless a pure agent-ops subset is split later), wagmi/tevm, full Bankr skill pack (games/trading bloat).

---

### Task 0: Document catalog policy (this repo)

**Files:**
- Create: `docs/PLUGIN_CATALOG.md`
- Modify: `README.md` (submodule + audience policy)
- Create: `AGENTS.md` (agent install + “this catalog is ops-only”)
- Create: `docs/SKILL_AUTHORING.md`
- Create: `scripts/check-skills.sh`, `scripts/check-submodules.sh`

- [ ] **Step 1: Write `docs/PLUGIN_CATALOG.md`**

Include: audience tags; table of planned remotes; rule “architecture plugins never listed here”; how to pin/bump; how to intentionally drift.

- [ ] **Step 2: Write AGENTS.md + SKILL_AUTHORING.md + README audience section**

State clearly: agents should install **this** marketplace for DeFi interaction; developers use `cyotee-claude-plugins` for building/testing.

- [ ] **Step 3: Checker scripts**

`check-submodules.sh`: every `plugins/*` with a `.git` must appear in `.gitmodules`; every marketplace.json plugin `source` must resolve.

- [ ] **Step 4: Commit on `defi-agent-skills`**

```bash
git add docs README.md AGENTS.md scripts
git commit -m "docs: agent-only catalog and submodule policy"
```

---

### Task 1: Split Foundry — create `foundry-agent-skills`, update both marketplaces

**Repos:**
- Create: GitHub `cyotee/foundry-agent-skills`
- Modify: `cyotee/foundry-skills` (remove moved skills; README pointers)
- Modify: `cyotee-claude-plugins` `.gitmodules` + marketplace.json
- Modify: `defi-agent-skills` `.gitmodules` + marketplace.json

**Produces:** Single SoT for cast/anvil/agent safety; dev marketplace no longer mixes fuzz testing with cast RPC for agent install paths.

- [ ] **Step 1: Create `foundry-agent-skills` repo**

```bash
gh repo create cyotee/foundry-agent-skills --public \
  --description "Foundry cast/anvil skills for AI agents operating on EVM chains" \
  --clone
```

Initial skills to include (move content from `foundry-skills`):

- `skills/cast-commands/` (full existing skill + patterns.md)
- `skills/anvil-node/` (fork rehearsal for agents)
- **New** `skills/foundry-agent-safety/SKILL.md`
- **New** `skills/foundry-script-ops/SKILL.md` (multi-step `forge script` broadcasts)

Plugin manifest `.claude-plugin/plugin.json` name: `foundry-agent`.

- [ ] **Step 2: Clean `foundry-skills`**

- Delete moved skill directories (after move lands on agent repo `main`).
- README: “Agent cast/anvil skills live in foundry-agent-skills; this package is forge test/deploy/project setup.”
- Bump version; push.

- [ ] **Step 3: Update `cyotee-claude-plugins`**

```bash
cd cyotee-claude-plugins
# refresh foundry submodule to cleaned commit
git submodule update --remote plugins/foundry   # or pin specific SHA
git submodule add https://github.com/cyotee/foundry-agent-skills.git plugins/foundry-agent
```

Marketplace.json:

- Keep `foundry` → `cyotee/foundry-skills` (dev).
- Add `foundry-agent` → `cyotee/foundry-agent-skills`.
- Regenerate Codex catalog if used: `python3 scripts/generate-codex-marketplace.py`.

- [ ] **Step 4: Update `defi-agent-skills`**

```bash
cd defi-agent-skills
git submodule add https://github.com/cyotee/foundry-agent-skills.git plugins/foundry-agent
```

Marketplace.json: **only** `foundry-agent` (do **not** add full `foundry-skills`).

- [ ] **Step 5: Verify no duplicate cast-commands**

```bash
# should be empty / only one tree
find cyotee-claude-plugins/plugins -path '*cast-commands/SKILL.md'
find defi-agent-skills/plugins -path '*cast-commands/SKILL.md'
```

- [ ] **Step 6: Commits**

Separate commits per repo: foundry-agent-skills, foundry-skills, cyotee-claude-plugins, defi-agent-skills.

---

### Task 2: New shared ops repos as submodules (primitives + permit2 + protocols)

For each new repo, same recipe:

1. `gh repo create cyotee/<name> --public --description "…"`.
2. Scaffold `.claude-plugin/plugin.json`, `README.md`, `skills/*/SKILL.md` meeting agent quality bar.
3. `git submodule add` into **`defi-agent-skills` only** (architecture siblings stay only in developer marketplace).
4. Register marketplace.json entry with GitHub source.
5. Push and pin submodule SHA.

**Order (IndexedEx dependencies first):**

| Order | Repo | Why |
|-------|------|-----|
| 2a | `defi-primitives-ops` | ERC20 / approve / WETH / units |
| 2b | `permit2-ops` | IndexedEx / Balancer routers |
| 2c | `balancer-v3-ops` | IndexedEx SE + DETF reserve |
| 2d | `aave-v3-ops` | Canonical agent demo |
| 2e | `uniswap-v3-ops` | Canonical swap demo |
| 2f | `aerodrome-ops` | Base + IndexedEx SE |

Each ops README must link architecture counterpart, e.g.:

```markdown
Deep protocol internals: install `aave-v3` from cyotee/cyotee-claude-plugins
(`cyotee/aave-v3-skill`). This package is cast runbooks only.
```

**Do not** add `aave-v3-skill` as a submodule of `defi-agent-skills`.

Skill content requirements remain as in prior plan (inspect → dry-run → execute → verify) with exact cast recipes and address tables.

- [ ] **Step (per repo): create, author MVP skills, submodule into defi-agent-skills, commit both**

Example for primitives:

```bash
cd defi-agent-skills
git submodule add https://github.com/cyotee/defi-primitives-ops.git plugins/defi-primitives
# edit marketplace.json
git add .gitmodules plugins/defi-primitives .claude-plugin/marketplace.json
git commit -m "feat: add defi-primitives-ops as submodule"
```

---

### Task 2g: `bankr-ops` execution backend (optional install)

**Repo:** `cyotee/bankr-ops` — **not** the full BankrBot skills dump.

- Skills: auth/key setup, portfolio/read, sign/submit, swap/transfer **only as backend primitives**.
- No Polymarket/games/token-launch clutter.
- Protocol `*-ops` may say: “If using Bankr backend, submit calldata via `bankr-ops`; if using Foundry, use `cast send` above.”
- Agents install **either** `foundry-agent` **or** `bankr-ops` (or both only if they truly need both).

### Task 2h: Multi-harness packaging for `defi-agent-skills`

- Port/adapt `scripts/generate-codex-marketplace.py` (or submodule shared tooling) for Codex dual-ship.
- OpenCode: install script or document bridge (mirror `cyotee-claude-plugins`).
- README install sections for Claude, Grok, Codex, OpenCode.
- CI check: `--check` on generated Codex artifacts when present.

### Task 3: IndexedEx ops plugin repo + submodule

**Repo:** `cyotee/indexedex-ops` (plugin name `indexedex-ops`).

**Skills (v1):**

| Skill | Purpose |
|-------|---------|
| `indexedex-overview` | Product mental model for agents (SE, DETF, registry) — short, no diamond internals dump |
| `indexedex-networks-addresses` | Vendored deployment snapshots + chain ids |
| `indexedex-registry-discovery` | `cast call` registry queries |
| `indexedex-standard-exchange` | SE exchange routes via cast |
| `indexedex-balancer-se-router` | Balancer SE router + Permit2 |
| `indexedex-detf-user-flows` | bond / mint-burn / claim paths agents may use |
| `indexedex-agent-checklist` | Pre-flight safety checklist |

**Sources of truth (read-only for authors):**  
`daosys/lib/indexedex/contracts/interfaces/*`, `deployments/*`, `AGENTS.md` user-route rules.

**Addresses:** Vendor testnet **and** mainnet/Base mainnet tables **only when real deployment artifacts exist**. Skills must fail closed if a chain table is missing.

**Exclude from this plugin:** `indexedex-testing`, adversarial testing, script orchestration for deploy engineers, crane.

- [ ] **Step 1: Create `cyotee/indexedex-ops` + MVP skills**
- [ ] **Step 2: Submodule into `defi-agent-skills` only**
- [ ] **Step 3: Optional later** — submodule into developer marketplace if maintainers want one install path (not required for campaign)

---

### Task 4: Extract local developer plugins (optional cleanup, parallel)

When touching permit2 for ops:

- Optionally extract `cyotee-claude-plugins/plugins/permit2` → `cyotee/permit2-skill` submodule in **developer** marketplace only (keeps integrator SoT clean).
- Same pattern later for tevm/wagmi/chainlink/reliquary.

Not blocking for agent marketplace launch.

---

### Task 5: QA and publish

- [ ] **Step 1: Catalog lint**

```bash
# defi-agent-skills: zero architecture protocol names
jq -r '.plugins[].name' .claude-plugin/marketplace.json
# expect only: foundry-agent, bankr-ops (optional), defi-primitives, *-ops, indexedex-ops
```

- [ ] **Step 2: Submodule status clean**

```bash
git submodule status
./scripts/check-skills.sh
```

- [ ] **Step 3: Smoke read-only cast** on testnet for registry + one ERC20 path; multi-harness install dry-run (Claude catalog + Codex check + OpenCode path).

- [ ] **Step 4: Push all new remotes + both marketplaces; bump `projects-defi` submodule pointers**

```bash
# defi-agent-skills
git push origin main
# cyotee-claude-plugins after foundry split
git push origin main
# projects-defi parent
git add defi-agent-skills cyotee-claude-plugins
git commit -m "chore: pin marketplaces after foundry split and agent catalog"
```

---

## Phases (revised)

| Phase | Work | Outcome |
|-------|------|---------|
| **P0** | Task 0 policy + Task 1 foundry **split** + both marketplaces + Task 2h multi-harness skeleton | Shared cast SoT; clean agent catalog; Claude/Grok/Codex/OpenCode install paths |
| **P1** | Task 2a–2c primitives, permit2-ops, balancer-v3-ops; Task 2g bankr-ops thin backend | Dependencies for IndexedEx; backends split |
| **P2** | Task 3 `indexedex-ops` submodule | Launch catalog |
| **P3** | Task 2d–2f remaining protocol ops | Full agent DeFi surface |
| **P4** | Task 5 QA/publish + optional Task 4 extracts | Production pins |

**Campaign MVP:** P0 + P1 + P2.

---

## What not to do

- ❌ Copy architecture skill trees into `defi-agent-skills/plugins` as regular files
- ❌ Submodule entire `aave-v3-skill` (etc.) into the agent marketplace “for context”
- ❌ Keep `cast-commands` in both `foundry-skills` and `foundry-agent-skills` as divergent copies
- ❌ Put crane / forge-fuzz / UI E2E into the agent marketplace
- ❌ One mega-repo of all skills with marketplace.json filters only (filters fail; agents still index noise if plugins are installed broadly — **curate by not listing**)

---

## Relationship diagram (submodules)

```text
                    cyotee/foundry-agent-skills  ◄── submodule (both marketplaces)
                    cyotee/bankr-ops             ◄── submodule (agent mkt; optional)
                    cyotee/defi-primitives-ops   ◄── submodule ──┐
                    cyotee/permit2-ops           ◄── submodule ──┤
                    cyotee/aave-v3-ops           ◄── submodule ──┼── defi-agent-skills
                    cyotee/uniswap-v3-ops        ◄── submodule ──┤
                    cyotee/balancer-v3-ops       ◄── submodule ──┤
                    cyotee/aerodrome-ops         ◄── submodule ──┤
                    cyotee/indexedex-ops         ◄── submodule ──┘

cyotee/foundry-skills ── submodule ──► cyotee-claude-plugins only (dev test/deploy)
cyotee/aave-v3-skill  ── submodule ──► cyotee-claude-plugins only (architecture)
…other architecture plugins…
```

---

## Self-review

| Intent | Plan coverage |
|--------|----------------|
| Existing skills as submodules / single SoT | Submodule composition model; Task 1–3 |
| Agent marketplace uncluttered | Audience tags; exclusion list; no architecture submodules |
| Mingled skills → split + update existing marketplace | Foundry split Task 1; mingle rule in Global Constraints |
| Interaction via Foundry RPC | foundry-agent + *-ops cast runbooks |
| Backend split (Foundry vs Bankr) | foundry-agent vs bankr-ops; locked decisions |
| Multi-harness Claude/Grok/Codex/OpenCode | Task 2h |
| IndexedEx for campaign | Task 3 (`indexedex-ops`) |
| Drift later allowed | Global Constraints + PLUGIN_CATALOG pin notes |

---

## Execution handoff

Requirements locked. Plan covers submodule composition, split-on-mingle, multi-harness, and split execution backends.

**Suggested first execution block:** Task 0 (policy) → Task 1 (foundry split) → Task 2h (multi-harness skeleton).

**Two execution options:**

1. **Subagent-Driven (recommended)** — one repo/marketplace change per subagent with review  
2. **Inline Execution** — P0 then P1–P2 in this session  


**Which approach?**
