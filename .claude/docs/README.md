# Claude Code Reference Documentation

This directory contains comprehensive reference documentation for Claude Code features, compiled from official documentation and research.

## Documentation Index

| Document | Description |
|----------|-------------|
| [AGENTS-REFERENCE.md](./AGENTS-REFERENCE.md) | Subagent definitions, schemas, collaboration patterns |
| [SKILLS-REFERENCE.md](./SKILLS-REFERENCE.md) | SKILL.md format, automatic activation, allowed-tools |
| [HOOKS-REFERENCE.md](./HOOKS-REFERENCE.md) | Hook events, configuration, security examples |
| [COMMANDS-REFERENCE.md](./COMMANDS-REFERENCE.md) | Slash command creation, arguments, permissions |
| [MCP-REFERENCE.md](./MCP-REFERENCE.md) | Model Context Protocol servers, configuration |
| [SETTINGS-REFERENCE.md](./SETTINGS-REFERENCE.md) | Complete settings.json schema, permissions |
| [AGENT-SDK-REFERENCE.md](./AGENT-SDK-REFERENCE.md) | Claude Agent SDK architecture, APIs |
| [ORCHESTRATION-REFERENCE.md](./ORCHESTRATION-REFERENCE.md) | Multi-agent patterns, parallel execution |
| [TOOLS-REFERENCE.md](./TOOLS-REFERENCE.md) | Built-in tools, parameters, permissions |
| [MEMORY-REFERENCE.md](./MEMORY-REFERENCE.md) | CLAUDE.md format, context management |

## Quick Reference

### Key Concepts

- **Agents**: Specialized workers with isolated context (`Task` tool)
- **Skills**: Auto-activated expertise packages (semantic matching)
- **Hooks**: Deterministic shell commands on events
- **Commands**: User-defined `/slash-commands`
- **MCP**: External tool integration protocol

### Configuration Files

```
.claude/
├── settings.json          # Team configuration
├── settings.local.json    # Personal overrides (gitignored)
├── agents/                # Custom agents
├── skills/                # Custom skills
├── commands/              # Slash commands
├── rules/                 # Topic-specific rules
└── docs/                  # This documentation
```

### Core Principles

1. **Maximum Parallelism**: 1 message = all parallel operations
2. **Single Responsibility**: One agent/skill = one job
3. **Least Privilege**: Only allow needed tools
4. **Context Efficiency**: Keep CLAUDE.md < 300 lines
5. **Deterministic Hooks**: Use hooks for validation, not prompts

## Research Sources

This documentation was compiled from:

- [Claude Code Official Documentation](https://code.claude.com/docs)
- [Claude Agent SDK Reference](https://platform.claude.com/docs/en/agent-sdk)
- [Anthropic Engineering Blog](https://www.anthropic.com/engineering)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)

---

*Generated: 2025-12-28*
