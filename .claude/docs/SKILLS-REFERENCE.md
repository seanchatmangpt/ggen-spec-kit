# Claude Code Skills Reference

## Overview

Skills are modular expertise packages that Claude automatically discovers and activates based on semantic relevance to user requests. Unlike agents, skills integrate directly into the conversation context.

## Skill Definition Schema

Skills are defined in `.claude/skills/*/SKILL.md` files:

```yaml
---
# REQUIRED FIELDS
name: skill-identifier              # Lowercase, hyphens only, max 64 chars
description: |
  What this skill does AND when to use it.
  This is the PRIMARY trigger for automatic activation.

# OPTIONAL FIELDS
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, LSP
model: claude-opus-4-5-20251101    # Or "inherit"
---

# Skill Display Name

## Instructions
Step-by-step guidance for Claude to follow.

## Patterns
Examples of correct usage.

## Output Format
```markdown
Expected output structure
```
```

## Directory Structure

```
.claude/skills/my-skill/
├── SKILL.md                    # REQUIRED - Main instructions
├── reference.md                # OPTIONAL - Detailed docs
├── templates/
│   └── template.md
└── scripts/
    └── helper.py               # Executes without loading context
```

## Skill Locations & Precedence

```
Enterprise (highest) → Personal → Project → Plugin (lowest)
```

| Scope | Location |
|-------|----------|
| Personal | `~/.claude/skills/` |
| Project | `.claude/skills/` |

## Allowed-Tools Syntax

```yaml
# Restrict tools without permission prompts
allowed-tools: Read, Grep, Glob, Bash

# Common patterns:
# Read-only: Read, Grep, Glob
# Analysis: Read, Grep, Glob, Bash, LSP
# Full access: Read, Write, Edit, Bash, Grep, Glob, LSP
```

**Note**: `allowed-tools` only works in Claude Code CLI, not Agent SDK.

## Skill vs Agent Comparison

| Aspect | Skill | Agent |
|--------|-------|-------|
| **Activation** | Automatic (semantic) | Manual (Task tool) |
| **Context** | Integrated | Isolated |
| **Size Limit** | <500 lines recommended | Can be larger |
| **Permission** | Asks on first use | Explicit invocation |

## Description Writing Best Practices

The description is the **primary trigger mechanism**:

```yaml
# ✅ GOOD - Clear purpose and triggers
description: Review code for quality, patterns, and three-tier architecture compliance. Use when reviewing PRs, checking code quality, or validating architecture boundaries.

# ❌ BAD - Too vague
description: This skill does code review.
```

## SKILL.md Body Best Practices

```markdown
---
name: code-reviewer
description: [Clear triggers]
allowed-tools: Read, Glob, Grep, LSP, Bash
---

# Code Reviewer

## Instructions
1. Clear step-by-step guidance
2. Reference files/examples
3. Explain methodology

## Checklists
- ✅ Item to check
- ✅ Another verification

## Good Pattern Example
[Show CORRECT way]

## Anti-Pattern Example
[Show WRONG way]

## Common Issues
- Problem 1: How to diagnose
- Problem 2: How to fix

## Output Format
```markdown
## Summary
[Structured output template]
```
```

## Example: Complete Skill

```yaml
---
name: test-runner
description: Run tests, analyze failures, and fix issues systematically. Use when running pytest, diagnosing test failures, checking coverage, or fixing broken tests.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, LSP
---

# Test Runner

## Instructions
1. Run tests with appropriate pytest options
2. Analyze output to identify root causes
3. Implement fixes for failing tests
4. Verify 80%+ code coverage

## Test Commands
```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=src/ --cov-report=term-missing
```

## Output Format
```markdown
## Test Run Summary
- Total: X, Passed: X, Failed: X
- Coverage: XX%
```
```

## Best Practices

1. **Under 500 Lines**: Keep SKILL.md lean
2. **Clear Description**: Include all trigger keywords
3. **Progressive Disclosure**: Link detailed docs
4. **Specific Examples**: Domain-specific patterns
5. **Structured Output**: Consistent templates
6. **Least Privilege**: Only allow needed tools
