# Plugin catalog policy

## Audience tags

| Tag | Meaning | This marketplace |
|-----|---------|------------------|
| `agent-ops` | Call protocols / backends on-chain | **Listed** |
| `architecture` | Internals | **Never listed** |
| `dev-tooling` | Test/deploy | **Never listed** |

## Remotes (v1.0 campaign MVP)

| Plugin path | Remote | Status |
|-------------|--------|--------|
| `foundry-agent` | `cyotee/foundry-agent-skills` | **Shipping** |
| `bankr-ops` | `cyotee/bankr-ops` | **Shipping** |
| `defi-primitives` | `cyotee/defi-primitives-ops` | **Shipping** |
| `permit2-ops` | `cyotee/permit2-ops` | **Shipping** |
| `balancer-v3-ops` | `cyotee/balancer-v3-ops` | **Shipping** |
| `indexedex-ops` | `cyotee/indexedex-ops` | **Shipping** |

## Adding a plugin

```bash
git submodule add https://github.com/cyotee/<repo>.git plugins/<name>
python3 scripts/generate-codex-marketplace.py
./scripts/check-skills.sh && ./scripts/check-submodules.sh
python3 tests/test_marketplace_catalog.py
```
