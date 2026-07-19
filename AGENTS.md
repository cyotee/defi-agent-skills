# AGENTS.md — defi-agent-skills

Guidance for AI agents using this marketplace.

## What this is

A **curated agent marketplace** for **interacting with DeFi on-chain**. Skills teach discovery, quoting, approvals, execution, and verification — not protocol architecture dumps or contract test frameworks.

For building/testing smart contracts, use [cyotee-claude-plugins](https://github.com/cyotee/cyotee-claude-plugins) instead.

## Install

```bash
# Claude Code
/plugin marketplace add cyotee/defi-agent-skills
/plugin install foundry-agent@defi-agent-skills

# Grok Build
grok plugin marketplace add cyotee/defi-agent-skills

# Codex (after clone with submodules)
codex plugin marketplace add cyotee/defi-agent-skills
# or: codex plugin marketplace add .
```

Install only the plugins you need. Prefer a single **execution backend**.

## Execution backends (pick one)

| Plugin | Use when |
|--------|----------|
| `foundry-agent` | You will call RPCs with `cast` / multi-step `forge script` |
| `bankr-ops` | You will execute via Bankr wallet/API (optional; install only if needed) |

Do **not** load both unless you truly need both tools.

## Global safety

1. Confirm chain id matches the intended network before any write.
2. Resolve addresses from skill address tables or on-chain registries — never invent.
3. Prefer read-only (`cast call`) and dry-run before `cast send`.
4. Require explicit user confirmation for any value transfer, approval, or state change (all networks).
5. Never print private keys or dump keystores into chat.
6. Prefer small amounts and testnets/forks first.

## Catalog policy

- Plugins are **git submodules** of independent repos (single source of truth across marketplaces).
- Architecture / forge-test / UI E2E skills are **not** listed here.
- Protocol packages use the `*-ops` naming pattern (`aave-v3-ops`, `indexedex-ops`, …).

See [docs/PLUGIN_CATALOG.md](docs/PLUGIN_CATALOG.md) and [docs/SKILL_AUTHORING.md](docs/SKILL_AUTHORING.md).
