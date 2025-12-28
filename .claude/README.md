# Claude Code Configuration

This directory contains comprehensive Claude Code configuration for the ggen-spec-kit project.

## Directory Structure

```
.claude/
├── agents/           # Specialized AI agents
├── skills/           # Domain-specific skills
├── commands/         # Custom slash commands
├── rules/            # Path-specific coding rules
├── hooks/            # Lifecycle event scripts
├── workflows/        # Multi-step workflow definitions
├── personas/         # Communication style configurations
├── prompts/          # Reusable prompt templates
├── context/          # Context injection files
├── guardrails/       # Security and protection rules
├── memory/           # Persistent memory and decisions
├── integrations/     # IDE and CI/CD integration guides
├── docs/             # Reference documentation
├── settings.json     # Permission and hook configuration
└── README.md         # This file
```

## Quick Reference

### Agents (11)
| Agent | Purpose |
|-------|---------|
| `architect` | System design and architecture |
| `coder` | Implementation and coding |
| `debugger` | Error diagnosis and fixing |
| `devops` | CI/CD and infrastructure |
| `documentation-writer` | Technical documentation |
| `orchestrator` | Multi-agent coordination |
| `performance-optimizer` | Performance analysis |
| `researcher` | Code exploration |
| `reviewer` | Code review |
| `security-auditor` | Security analysis |
| `tester` | Test creation and running |

### Skills (13)
Architecture, changelog, code review, debugging, doc generation, ggen operation, ontology design, OTEL analysis, performance profiling, RDF validation, SPARQL, spec writing, testing.

### Commands (10)
`/analyze-otel`, `/changelog`, `/create-feature`, `/debug`, `/explore`, `/lint`, `/review-pr`, `/run-tests`, `/sync-rdf`, `/validate-architecture`

### Workflows
- `feature-development.md` - RDF-first feature workflow
- `bug-fix.md` - Systematic debugging workflow
- `code-review.md` - Comprehensive review checklist

### Personas
- `concise.md` - Direct, minimal responses
- `mentor.md` - Educational approach
- `rdf-expert.md` - Semantic web expertise

## Usage

### Slash Commands
Type `/command-name` in Claude Code:
```
/run-tests tests/unit/
/lint src/
/review-pr 123
```

### Agent Invocation
Agents are used via the Task tool:
```
Task("description", "agent-name", "prompt")
```

### Skills
Skills auto-activate based on context and task type.

## Configuration

### Settings (`settings.json`)
- Permissions: allow/ask/deny rules
- Hooks: event → script mappings
- Environment variables

### Rules
Path-specific rules with YAML frontmatter:
```yaml
---
paths: ["src/**/*.py"]
---
# Rules for Python files
```

## Plugin

This project is also packaged as a Claude Code plugin.
See `.claude-plugin/plugin.json` for manifest.

## Related Files

- `CLAUDE.md` - Main project instructions
- `.mcp.json` - MCP server configuration
- `.gitignore` - Excludes `settings.local.json`
