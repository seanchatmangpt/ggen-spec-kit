# Claude Code Slash Commands Reference

## Overview

Slash commands are user-defined prompts stored as Markdown files that execute with `/command-name` syntax. They support argument interpolation, file references, and tool permissions. Fully supported on web and desktop.

## Command File Format

Commands are defined in `.claude/commands/*.md`:

```markdown
---
description: Brief command overview (30-100 chars)
allowed-tools: Read, Write, Grep, Bash(git diff:*)
argument-hint: [filename] [priority]
model: claude-opus-4-5-20251101
---

# Command Title

## Instructions
Detailed guidance with $ARGUMENTS or $1, $2 for parameters.
```

## Frontmatter Fields

| Field | Type | Purpose | Required |
|-------|------|---------|----------|
| `description` | String | Brief overview | Yes (for SlashCommand tool) |
| `allowed-tools` | String | Tool permissions | No |
| `argument-hint` | String | Parameter autocomplete | No |
| `model` | String | Claude model override | No |

## Argument Passing

### Global Arguments
```markdown
Fix issue #$ARGUMENTS

# Usage: /fix-issue 456
# Result: "Fix issue #456"
```

### Positional Parameters
```markdown
Review PR #$1 with priority: $2
Reviewer: $3

# Usage: /review-pr 123 high alice
# $1 = "123", $2 = "high", $3 = "alice"
```

### File References (@ prefix)
```markdown
Compare these files:
@ src/old-version.py
@ src/new-version.py
```

### Bash Execution (! prefix)
```markdown
!`git diff HEAD~1 HEAD`

Review the changes above.
```

## Built-in Commands

| Command | Purpose |
|---------|---------|
| `/clear` | Clear conversation history |
| `/compact` | Compress conversation |
| `/export` | Export conversation |
| `/rewind` | Undo recent responses |
| `/config` | View/modify settings |
| `/model` | Change AI model |
| `/status` | Show session status |
| `/help` | List available commands |
| `/cost` | Show token usage |

## Directory Structure

```
.claude/commands/
├── review.md
├── deploy.md
├── analysis/
│   ├── performance.md
│   └── security.md
└── testing/
    ├── run-tests.md
    └── coverage.md
```

**Note**: Subdirectories organize commands but don't affect command names.

## Project vs User Commands

| Scope | Location | Shared |
|-------|----------|--------|
| Project | `.claude/commands/` | Yes (git) |
| User | `~/.claude/commands/` | No |

Project commands override user commands with same name.

## Tool Permission Syntax

```yaml
# Simple (all capabilities)
allowed-tools: Read, Write, Grep, Bash

# Constrained (specific operations)
allowed-tools: Bash(git diff:*, git add:*)
             Bash(npm run:test)
```

## Example: Code Review Command

```markdown
---
description: Comprehensive security code review
allowed-tools: Read, Grep, Bash(git:*)
---

Perform security review:

!`git diff HEAD~1 HEAD`

Check for:
1. Hardcoded secrets
2. SQL injection
3. Path traversal
4. Unsafe subprocess
```

## Example: Test Command

```markdown
---
description: Run tests and generate coverage report
allowed-tools: Bash(pytest:*, coverage:*)
argument-hint: [test-pattern]
---

Run tests matching: $1 (or all if no pattern)

Steps:
1. Execute: pytest tests/ -k "$ARGUMENTS" --cov=src/
2. Generate markdown report
3. Highlight any coverage regressions
```

## Example: Architecture Validation

```markdown
---
description: Validate three-tier architecture
allowed-tools: Grep, Glob
---

Check architecture compliance:

Commands Layer:
!`grep -r "import.*runtime" src/commands/ || echo "✅ No violations"`

Operations Layer:
!`grep -r "subprocess\|open" src/ops/ || echo "✅ No violations"`

Report findings with recommendations.
```

## Best Practices

1. **Clear Description**: 30-100 chars, action-focused
2. **Minimal Permissions**: Only allow needed tools
3. **Document Arguments**: Use `argument-hint`
4. **Organize by Category**: Use subdirectories
5. **Version Control**: Commit project commands
6. **Security Review**: Check bash operations
7. **Web Ready**: Commands work equally on web and desktop

## Naming Conventions

```
✅ GOOD:
- /code-review (verb-noun)
- /validate-schema
- /test-coverage

❌ AVOID:
- /x (cryptic)
- /very-long-command-name
- /DO_EVERYTHING
```
