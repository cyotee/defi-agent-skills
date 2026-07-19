# Multi-harness distribution

Claude `.claude-plugin/marketplace.json` is the **source of truth**.

| Artifact | Role |
|----------|------|
| `.claude-plugin/marketplace.json` | Claude / Grok-compatible catalog |
| `.agents/plugins/marketplace.json` | Codex catalog (**generated**) |
| `plugins/*/.codex-plugin/plugin.json` | Codex per-plugin (**generated**) |
| `install-opencode.sh` | Copy skills into OpenCode skills dir |

```bash
python3 scripts/generate-codex-marketplace.py
python3 scripts/generate-codex-marketplace.py --check
./install-opencode.sh foundry-agent
```
