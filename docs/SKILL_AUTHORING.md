# Skill authoring guide (agent-ops)

## Frontmatter template

```yaml
---
name: example-ops-action
description: >
  Use when the agent must <action> on <protocol>. Covers cast call/send
  recipes, address resolution, and post-tx verification.
---
```

## Required sections

1. **Goal** — one sentence
2. **Prerequisites** — binaries, env (`ETH_RPC_URL`), chain, address source
3. **Safety** — read vs write; confirmation; no secrets in output
4. **Inspect** — `cast call` / backend reads
5. **Dry-run** — estimate, quote, or call simulation
6. **Execute** — `cast send` / `forge script` / delegate to backend plugin
7. **Verify** — receipt + state re-read
8. **Common failures**
9. **References** — addresses, selectors; link architecture `*-skill` if needed

## Rules

- Prefer signatures like `"balanceOf(address)(uint256)"` in cast strings.
- Human amounts + `cast to-wei` where helpful.
- Addresses only from versioned tables; fail closed if missing.
- Default recipes use **Foundry**. Do not require Bankr in the same skill body as mandatory reading — point to `bankr-ops` for that backend.
- Keep `SKILL.md` focused; put large tables in `references/`.

## Anti-patterns

- Pasting entire pool/core contract sources
- Architecture-only skills in this marketplace
- Invented mainnet addresses
- Logging `$PRIVATE_KEY`
