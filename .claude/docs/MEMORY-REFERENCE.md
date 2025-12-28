# Claude Code Memory & Context Reference

## Overview

Claude Code uses CLAUDE.md files as persistent instruction files, loaded automatically at session start to provide project context, coding standards, and architectural guidance.

## Memory Hierarchy (Highest to Lowest)

```
1. Enterprise Policy (unchangeable)
2. Command-line Arguments
3. Local Settings (.claude/settings.local.json)
4. Project Memory (CLAUDE.md, .claude/settings.json)
5. User Memory (~/.claude/CLAUDE.md, ~/.claude/settings.json)
```

## CLAUDE.md Locations

| Type | Location | Shared | Git |
|------|----------|--------|-----|
| Project | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Yes | Yes |
| Local | `./CLAUDE.local.md` | No | No (gitignored) |
| User | `~/.claude/CLAUDE.md` | No | No |

## CLAUDE.md Structure

```markdown
# Project Name - Developer Guide

## Quick Overview
[2-3 line description]

## Critical Rules
### RULE 1: [High-priority constraint]
[Explanation]

## Architecture
[ASCII diagram or description]

## Key Commands
```bash
command-1
command-2
```

## Code Patterns
[Examples]

## Quality Standards
[Requirements]

## File Organization
[Directory structure]

## When to Use Agents/Skills
[List with triggers]
```

## Size Guidelines

- **Target**: < 300 lines
- **Ideal**: Shorter is better
- **Why**: Loaded on EVERY session, consumes token budget

## File Import System

```markdown
# CLAUDE.md

@docs/architecture.md
@docs/patterns.md
@specs/conventions.md

[Rest of content]
```

**Rules**:
- Relative to importing file
- Max depth: 5 levels
- Handles circular imports
- Contributes to context size

## Context Management Commands

```
/context         # Visualize context as colored grid
/cost            # Show token usage
/memory          # View/edit loaded memory files
/compact         # Summarize conversation
/clear           # Reset conversation history
/rewind          # Go back to earlier checkpoint
```

## Token Budget Management

```
At Regular Intervals (30-45 min):
├─ Run /cost
├─ If tokens > 50k:
│  ├─ Use /compact
│  ├─ Or /clear
│  └─ Or /rewind
└─ Continue work
```

## Extended Context Window

```bash
# Enable 1M token context
claude --model claude-opus-4-5-20251101[1m]
```

## Session Management

```bash
# Resume most recent
claude --continue

# Interactive picker
claude --resume

# Resume by name
claude --resume my-session

# In session
/resume          # Switch conversations
/rename          # Name session
```

## Checkpoint System

```
Checkpoint includes:
├─ Code state (file modifications)
├─ Conversation state
├─ Timestamp
├─ Tool execution results
└─ Optional checkpoint name
```

Commands:
```
/rewind                  # View checkpoints
/rewind checkpoint-name  # Jump to checkpoint
/name-checkpoint X       # Name current checkpoint
```

## Rules Organization

```
.claude/rules/
├── python.md           # Rules for .py files
├── tests.md            # Rules for test files
└── markdown.md         # Rules for .md files
```

With YAML frontmatter:
```yaml
---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Python Code Rules
...
```

## Writing Effective Instructions

### ✅ Good (Specific)
```markdown
### Code Style
- 2-space indentation
- Max line length: 88 characters
- 100% type hint coverage
- NumPy-style docstrings
```

### ❌ Bad (Vague)
```markdown
### Code Style
Follow good coding practices.
```

## System Reminders

Claude Code injects system reminders automatically:
- CLAUDE.md content
- Git status information
- Project configuration
- Tool availability

```
<system-reminder>
Context information...
</system-reminder>
```

## Context Optimization

### Token Distribution (200k example)

```
System prompt & CLAUDE.md: 10-15k (5-7%)
Conversation history: 50-100k (25-50%)
Current request: 20-40k (10-20%)
Model processing: 20-30k (10-15%)
Output buffer: 20-40k (10-20%)
```

### Optimization Strategies

1. **Lean CLAUDE.md**: Only universal rules
2. **Use imports**: Large sections in separate files
3. **Regular cleanup**: Remove outdated patterns
4. **Focused sessions**: One feature per session
5. **Use /compact**: When tokens grow

## Directory Structure Best Practice

```
├─ CLAUDE.md                    # Main guide (< 100 lines)
├─ .claude/
│  ├─ CLAUDE.md                # Alternative location
│  ├─ settings.json            # Configuration
│  ├─ settings.local.json      # Local overrides
│  ├─ agents/                  # Custom agents
│  ├─ skills/                  # Custom skills
│  ├─ commands/                # Slash commands
│  ├─ rules/                   # Rule files
│  └─ docs/                    # Supporting docs
└─ CLAUDE.local.md             # Personal notes
```

## Troubleshooting

### Memory Not Loading
1. Check file location: `./CLAUDE.md` or `./.claude/CLAUDE.md`
2. Verify readable by user
3. Run `/memory` command
4. Start fresh session

### Context Exhausted
1. Run `/compact` to summarize
2. Run `/clear` to reset
3. Use `/rewind` to go back
4. Reduce CLAUDE.md size
5. Use extended context `[1m]`

### Conflicting Instructions
Higher tier wins:
```
Enterprise > CLI > Local > Project > User
```

## Best Practices Checklist

**Content**:
- [ ] Clear project overview (< 3 lines)
- [ ] Critical rule explicitly stated
- [ ] Architecture explained
- [ ] Code patterns with examples
- [ ] Quality standards specified
- [ ] Common commands listed
- [ ] Agent usage guidance

**Format**:
- [ ] Valid Markdown
- [ ] < 300 lines
- [ ] Logical section ordering
- [ ] Consistent headings
- [ ] Links to detailed docs

**Maintenance**:
- [ ] Up-to-date with patterns
- [ ] Reviewed quarterly
- [ ] Uses imports for large sections
