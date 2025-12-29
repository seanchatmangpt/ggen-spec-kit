# Multi-Agent Orchestration Reference

## Overview

Claude Code supports multi-agent orchestration through the Task tool, enabling parallel task execution, specialized subagents, and hierarchical workflows. Full support on web and desktop; context isolation applies equally.

## Core Concept: Task Tool Parallelism

The Task tool spawns subagents with isolated context windows. Multiple tasks in a single message execute in parallel.

### Parallel Execution Pattern

```
Single Message:
├─ Task 1 (Component creation)
├─ Task 2 (Styling files)
├─ Task 3 (Test files)
├─ Task 4 (Type definitions)
└─ Task 5 (Documentation)

All tasks execute simultaneously.
```

### Decision Tree

```
Is Task B dependent on Task A's output?
├─ NO → Run in PARALLEL (same message)
└─ YES → Run SEQUENTIALLY (separate messages)
```

## Hierarchical Architecture

### Three-Tier Pattern

```
Tier 1: Orchestrator (Main Agent)
├─ Maintains global state
├─ Delegates to specialists
└─ Aggregates results

Tier 2: Specialized Subagents
├─ Single responsibility
├─ Restricted tool access
└─ Returns focused results

Tier 3: Execution Tasks (Optional)
├─ Micro-tasks within subagent
└─ Parallel exploration
```

## Orchestration Patterns

### Pattern 1: Pipeline

```
analyst → architect → implementer → tester → reviewer
   ↓         ↓           ↓           ↓           ↓
extract   design       write      verify      check
   ↓         ↓           ↓           ↓           ↓
   └─────────┴───────────┴───────────┴───────────┘
              Orchestrator aggregates
```

### Pattern 2: Parallel Specialization

```
┌─ Frontend-Agent → Build UI
├─ Backend-Agent → Create APIs
├─ Database-Agent → Design schema
├─ Test-Agent → Write tests
└─ Docs-Agent → Generate docs
        ↓
    Orchestrator integrates
```

### Pattern 3: Verification Loop

```
Orchestrator writes code
    ↓
┌─ Quality-Reviewer
├─ Security-Reviewer
├─ Performance-Reviewer
└─ Test-Runner
    ↓
If all pass → Deploy
If failures → Fix → Loop
```

## Context Sharing & Isolation

### Isolation by Design

- Each subagent has its own context window
- Subagents do NOT see full conversation history
- Prevents "context pollution"
- Enables focused specialization

### Shared Knowledge via CLAUDE.md

All agents inherit CLAUDE.md content:

```markdown
# CLAUDE.md (Shared across agents)

## Architecture
- Three-tier: commands, ops, runtime

## Coding Standards
- 100% type hints
- 80%+ coverage
```

## Agent Communication

### Parent → Child
- Context passed through task descriptions
- Only relevant information shared

### Child → Parent
- Structured summaries returned
- Important findings highlighted
- Artifacts (files) reported

### Context Bridge Workarounds

```markdown
# Problem: Subagent creates file, parent unaware

Solutions:
1. Request explicit summaries
2. Use CLAUDE.md as shared memory
3. Write findings to shared state file
4. Report critical state changes
```

## Concurrency Limits

### Practical Recommendations

| Environment | Safe Parallel Agents |
|-------------|---------------------|
| Home development | 3-5 |
| Workstation | 5-10 |
| CI/CD | 10-20 |
| Cloud | 20-100+ |

### Token Consumption

```
Single agent task: 5,000 tokens
With 5 parallel agents: 25,000 tokens
With 10 parallel agents: 50,000 tokens

Parallelism trades tokens for speed.
```

## Model Selection Strategy

```
Critical path: Opus 4 (max quality)
Standard work: Sonnet 4 (balanced)
Simple tasks: Haiku 3.5 (fast, cheap)
```

## Error Handling

### Error Types

1. **Subagent Errors**: Tool failures, validation issues
2. **Coordination Errors**: Timeouts, resource exhaustion
3. **State Errors**: Inconsistent state, lost context

### Recovery Pattern

```
Subagent Error
    ↓
Recoverable? → Auto-retry → Continue
    ↓
Fatal? → Escalate to Orchestrator
    ↓
Log error, stop workflow, alert human
```

## When to Use Agents vs Direct Work

### Use Agents When:
- Parallelization benefits exist
- Specialization needed
- Context management required
- Long-running workflows

### Use Direct Work When:
- Simple, linear tasks
- High interdependency
- Small scope (< 5 minutes)
- Privacy concerns

## Example: Full-Stack Development

```
Time 0:00 - Parallel Phase:
├─ Backend-Agent (15 min, Sonnet)
├─ Frontend-Agent (15 min, Sonnet)
└─ Security-Agent (10 min, Opus)

Time 10:00 - Sequential Phase:
├─ Integration-Test-Agent
└─ Performance-Agent

Time 20:00 - Complete
├─ Aggregated results
├─ Issues identified
└─ Ready for deployment
```

## Example: Codebase Exploration

```
4 Parallel Exploration Agents:
├─ Frontend (src/ui/, components/)
├─ Backend (src/api/, services/)
├─ Database (src/db/, migrations/)
└─ Config (src/config/, env files)

Time: 5 min (vs 25 min sequential)
Result: 4x parallelism, better understanding
```

## Best Practices

1. **Single Responsibility**: One agent, one job
2. **Explicit Delegation**: Clear task descriptions
3. **Minimize Dependencies**: Independent tasks when possible
4. **Define Boundaries**: Clear inputs/outputs/criteria
5. **Model Selection**: Right model for task complexity
6. **Error Recovery**: Plan for failures
7. **Token Awareness**: Monitor consumption
8. **Context Efficiency**: Lean CLAUDE.md, focused summaries
9. **Web Optimization**: Use parallel tasks to reduce latency
