# Plugin catalog policy

## Audience tags

| Tag | Meaning | This marketplace |
|-----|---------|------------------|
| `agent-ops` | Call protocols / backends on-chain | **Listed** |
| `architecture` | How a protocol works internally | **Never listed** |
| `dev-tooling` | Write, test, deploy contracts | **Never listed** |

## Composition model

1. Plugin content lives in `https://github.com/cyotee/<repo>`.
2. This marketplace pins it with `git submodule` under `plugins/<name>/`.
3. `.claude-plugin/marketplace.json` registers install metadata.
4. Pins may differ from other marketplaces (intentional drift is allowed; document why).

## Planned / current remotes

| Plugin path | Remote | Status |
|-------------|--------|--------|
| `foundry-agent` | `cyotee/foundry-agent-skills` | **Shipping** |
| `bankr-ops` | `cyotee/bankr-ops` | Planned (optional backend) |
| `defi-primitives` | `cyotee/defi-primitives-ops` | Planned |
| `permit2-ops` | `cyotee/permit2-ops` | Planned |
| `balancer-v3-ops` | `cyotee/balancer-v3-ops` | Planned |
| `aave-v3-ops` | `cyotee/aave-v3-ops` | Planned |
| `uniswap-v3-ops` | `cyotee/uniswap-v3-ops` | Planned |
| `aerodrome-ops` | `cyotee/aerodrome-ops` | Planned |
| `indexedex-ops` | `cyotee/indexedex-ops` | Planned (flagship) |

Architecture counterparts (`aave-v3-skill`, etc.) stay only in [cyotee-claude-plugins](https://github.com/cyotee/cyotee-claude-plugins).

## Adding a plugin

```bash
git submodule add https://github.com/cyotee/<repo>.git plugins/<name>
# edit .claude-plugin/marketplace.json
python3 scripts/generate-codex-marketplace.py   # if Codex dual-ship enabled
./scripts/check-skills.sh
./scripts/check-submodules.sh
```

## Bumping a pin

```bash
./scripts/bump-plugin.sh plugins/<name>   # or: cd plugins/<name> && git pull && cd ../..
git add plugins/<name> .gitmodules
git commit -m "chore: bump <name> submodule"
```
