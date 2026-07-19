# defi-agent-skills

Agent Skills marketplace for **DeFi protocol interaction** — portable skills so AI agents (Claude Code, Codex, Grok, OpenCode, and others) can discover and use DeFi protocols correctly.

Built for agent-first onboarding: install the marketplace, load protocol skills, then interact with contracts and flows without reverse-engineering docs from scratch.

## Installation

### Claude Code

```bash
/plugin marketplace add cyotee/defi-agent-skills
/plugin
```

### Grok Build

```bash
grok plugin marketplace add cyotee/defi-agent-skills
```

### Local clone

```bash
git clone https://github.com/cyotee/defi-agent-skills.git
# then add the local path as a marketplace in your agent harness
```

## Structure

Follows the [Agent Skills](https://agentskills.io) / Claude plugin marketplace layout:

```text
.claude-plugin/
  marketplace.json          # Catalog (source of truth)
plugins/
  <protocol>/
    .claude-plugin/plugin.json
    README.md
    skills/
      <skill-name>/
        SKILL.md
```

## Protocols

Skills will be added per protocol. First target:

| Plugin | Protocol | Status |
|--------|----------|--------|
| `indexedex` | Indexedex (daosys) | Planned |

## Related

- Development monorepo submodule host: [projects-defi](https://github.com/cyotee/projects-defi) (if public)
- General workflow plugins: [cyotee-claude-plugins](https://github.com/cyotee/cyotee-claude-plugins)

## License

MIT (unless noted otherwise in individual plugins)
