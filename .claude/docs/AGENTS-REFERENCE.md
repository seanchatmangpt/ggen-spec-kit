# Claude Code Agents Reference

## Overview

Claude Code agents (subagents) are specialized AI workers that operate in isolated context windows, enabling parallel task execution and focused expertise. They are invoked via the `Task` tool with a `subagent_type` parameter.

## Agent Definition Schema

Agents are defined in `.claude/agents/*.md` files with YAML frontmatter:

```yaml
---
# REQUIRED FIELDS
name: agent-name                    # Unique identifier, lowercase with hyphens
description: |
  Brief description of agent purpose and capabilities.
  This text appears in agent selection UI.

role: Agent Role Name               # Human-readable role title
version: 1.0.0                      # Semantic version

# TOOL CONFIGURATION
tools:                              # Whitelist - only listed tools available
  - Read                            # File reading
  - Write                           # File creation
  - Edit                            # File modification
  - Bash                            # Shell execution
  - Glob                            # Pattern-based file search
  - Grep                            # Content search with regex
  - LSP                             # Language Server Protocol
  - WebSearch                       # Web searching
  - WebFetch                        # URL content fetching
  # DO NOT include Task - agents cannot spawn agents

# MODEL SELECTION
model: "sonnet"                     # Options: sonnet, opus, haiku, inherit

# AGENT SPECIALIZATION
capabilities:
  - Specific capability 1
  - Specific capability 2

expertise_areas:
  - Domain expertise 1
  - Domain expertise 2

constraints:
  - Must validate against X
  - Cannot do Y

# PERSONALITY & STYLE
personality:
  traits:
    - Trait 1
    - Trait 2
  communication_style:
    - Style descriptor 1
    - Style descriptor 2

# WORKFLOW & PROCESS
workflow:
  phase_name:
    - Step 1
    - Step 2

example_prompts:
  category_name:
    - "Example invocation 1"
    - "Example invocation 2"

# QUALITY STANDARDS
quality_gates:
  - Gate 1
  - Gate 2

# COLLABORATION
collaboration:
  works_well_with:
    - agent-name: Purpose
  handoff_points:
    - "Condition → next agent"

# BEST PRACTICES
best_practices:
  - Practice 1
  - Practice 2

anti_patterns_to_avoid:
  - Anti-pattern 1
  - Anti-pattern 2
---

# Agent Display Name

Markdown content with detailed instructions follows...
```

## Built-in Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| `general-purpose` | Complex multi-step tasks | Inherits |
| `Explore` | Fast codebase searching | Haiku |
| `Plan` | Implementation planning | Inherits |

## Agent vs Skill Comparison

| Aspect | Agent | Skill |
|--------|-------|-------|
| **Invocation** | Manual (Task tool) | Automatic (semantic) |
| **Context** | Isolated window | Integrated |
| **File Location** | `.claude/agents/` | `.claude/skills/` |
| **Use Case** | Complex workflows | Quick expertise |

## Tool Access Control

```yaml
# Whitelist approach - only listed tools available
tools:
  - Read
  - Glob
  - Grep

# If omitted, inherits ALL tools from session
```

**Important**: Never include `Task` in agent tools - only the main Claude instance can spawn agents.

## Collaboration Patterns

### Pipeline Pattern
```
analyst → architect → implementer → tester → reviewer
```

### Parallel Pattern
```
┌─ Frontend-Agent
├─ Backend-Agent
├─ Database-Agent
└─ Test-Agent
    ↓
 Orchestrator aggregates
```

## Best Practices

1. **Single Responsibility**: One agent, one job
2. **Clear Capabilities**: List specific abilities
3. **Explicit Constraints**: Define boundaries
4. **Example Prompts**: Show how to invoke
5. **Quality Gates**: Define success criteria
6. **Collaboration Points**: Document handoffs

## Example: Minimal Agent

```yaml
---
name: code-reviewer
role: Code Review Specialist
description: Reviews code for quality and security
tools:
  - Read
  - Glob
  - Grep
  - Bash
---

# Code Reviewer

Review code following project standards...
```
