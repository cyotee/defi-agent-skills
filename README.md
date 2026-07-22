# defi-agent-skills

**AI-agent marketplace** for **DeFi protocol interaction** — curated so agents only load skills needed to operate on-chain, not architecture or test-framework noise.

**Status:** testnet-first / public preview. IndexedEx and many runbooks target **Base Sepolia** (or documented networks) until mainnet artifacts are published. Prefer dry-run / read paths before any value-bearing `cast send`.

Plugins are **git submodules** of independent repos (shared SoT with other marketplaces; pins may drift intentionally).

## Who should use this

| Audience | Marketplace |
|----------|-------------|
| Agents calling DeFi / RPCs | **This repo** |
| Developers writing/testing contracts (incl. Crane) | [cyotee-claude-plugins](https://github.com/cyotee/cyotee-claude-plugins) |
| Crane framework source & docs | [cyotee/crane](https://github.com/cyotee/crane) · [docs](https://cyotee.github.io/crane/) |

> **Disclaimer:** Ops skills describe third-party protocols for agent automation. They are **not** official products of Aave, Uniswap, Balancer, or other protocol teams.

## Installation

### Claude Code

```bash
/plugin marketplace add cyotee/defi-agent-skills
/plugin install foundry-agent@defi-agent-skills
```

### Grok Build

```bash
grok plugin marketplace add cyotee/defi-agent-skills
```

### Codex CLI

```bash
git clone --recurse-submodules https://github.com/cyotee/defi-agent-skills.git
cd defi-agent-skills
codex plugin marketplace add .
# or: codex plugin marketplace add cyotee/defi-agent-skills
```

Regenerate Codex artifacts after catalog edits:

```bash
python3 scripts/generate-codex-marketplace.py
python3 scripts/generate-codex-marketplace.py --check
```

### OpenCode

```bash
git clone --recurse-submodules https://github.com/cyotee/defi-agent-skills.git
cd defi-agent-skills
./install-opencode.sh   # when present; or install skills via OpenCode plugin bridge
```

## Execution backends

Install **one** primary backend:

| Plugin | Tool |
|--------|------|
| `foundry-agent` | `cast` / `forge script` / Anvil forks |
| `bankr-ops` | Bankr wallet API (optional, separate plugin) |

## Plugins

| Plugin | Purpose | Status |
|--------|---------|--------|
| `foundry-agent` | Cast/Anvil agent runtime + safety | **Shipping** |
| `bankr-ops` | Optional Bankr wallet execution backend | **Shipping** |
| `defi-primitives` | ERC20, approvals, WETH, units | **Shipping** |
| `permit2-ops` | Permit2 allowance cast runbooks | **Shipping** |
| `balancer-v3-ops` | Balancer V3 vault/router cast | **Shipping** |
| `indexedex-ops` | IndexedEx flagship agent flows | **Shipping** |


## Structure

```text
.claude-plugin/marketplace.json   # Claude catalog (SoT)
.agents/plugins/marketplace.json  # Codex catalog (generated)
plugins/                          # git submodules
docs/PLUGIN_CATALOG.md
AGENTS.md
```

## Related

| Resource | Link |
|----------|------|
| Developer marketplace | [cyotee-claude-plugins](https://github.com/cyotee/cyotee-claude-plugins) |
| Crane (Diamond framework) | [github.com/cyotee/crane](https://github.com/cyotee/crane) · [docs](https://cyotee.github.io/crane/) |
| Plugin catalog policy | [docs/PLUGIN_CATALOG.md](docs/PLUGIN_CATALOG.md) |

## License

MIT — see [LICENSE](LICENSE). Individual plugins may note additional terms in their manifests.
