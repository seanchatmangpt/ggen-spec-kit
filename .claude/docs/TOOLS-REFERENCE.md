# Claude Code Tools Reference

## Built-in Tools (10)

| Tool | Function | Permission | Read-Only | Web Support |
|------|----------|------------|-----------|-------------|
| **Read** | Read file contents | No | Yes | Yes |
| **Bash** | Execute shell commands | Yes | No | Limited* |
| **Edit** | Targeted file edits | Yes | No | Yes |
| **Write** | Create/overwrite files | Yes | No | Yes |
| **Glob** | Pattern-based file discovery | No | Yes | Yes |
| **Grep** | Content pattern searching | No | Yes | Yes |
| **WebFetch** | Fetch URL content | Yes | No | Yes |
| **WebSearch** | Web search (US only) | Yes | No | Yes |
| **Task** | Spawn subagents | No | N/A | Yes |
| **NotebookEdit** | Modify Jupyter cells | Yes | No | Yes |

*Bash: Web sessions cannot execute arbitrary system commands; limited to safe operations.

## Tool Parameters

### Bash
```json
{
  "command": "string",
  "description": "string (optional)"
}
```

### Read
```json
{
  "file_path": "string",
  "offset": "number (optional)",
  "limit": "number (optional)"
}
```

### Write
```json
{
  "file_path": "string",
  "file_text": "string"
}
```

### Edit
```json
{
  "file_path": "string",
  "original_text": "string",
  "new_text": "string"
}
```

### Glob
```json
{
  "pattern": "string",
  "path": "string (optional)"
}
```

### Grep
```json
{
  "pattern": "string",
  "path": "string (optional)",
  "type": "string (optional)",
  "glob": "string (optional)",
  "multiline": "boolean (optional)",
  "-i": "boolean (optional)",
  "-n": "boolean (optional)",
  "-A": "number (optional)",
  "-B": "number (optional)",
  "-C": "number (optional)",
  "output_mode": "content|files_with_matches|count",
  "head_limit": "number (optional)"
}
```

### WebFetch
```json
{
  "url": "string",
  "prompt": "string"
}
```

### WebSearch
```json
{
  "query": "string",
  "allowed_domains": ["array (optional)"],
  "blocked_domains": ["array (optional)"]
}
```

### Task
```json
{
  "prompt": "string",
  "agent": "string (optional)",
  "context": "string (optional)"
}
```

## Permission Configuration

### Permission Precedence
```
DENY > ASK > ALLOW
```

### settings.json Configuration
```json
{
  "permissions": {
    "allow": [
      "Bash(npm run:*)",
      "Read(**/*.py)"
    ],
    "ask": [
      "Bash(git push:*)"
    ],
    "deny": [
      "Read(.env**)",
      "Bash(rm:*)"
    ]
  }
}
```

### Permission Rule Syntax

**Bash (Prefix Matching)**:
```json
"Bash(npm run test:*)"  // npm run test, npm run test:unit
"Bash(git:*)"           // All git commands
```

**File Paths (Glob Patterns)**:
```json
"Read(**/*.py)"         // All Python files
"Read(//etc/hosts)"     // Absolute path
"Read(~/Documents/**)"  // Home directory
"Edit(src/**/*.ts)"     // TypeScript in src/
```

**WebFetch (Domain)**:
```json
"WebFetch(domain:github.com)"
```

**MCP Tools**:
```json
"mcp__github__*"
"mcp__postgres__read_*"
```

## Tool Execution Lifecycle

```
User Request
    ↓
Claude creates tool parameters
    ↓
[PreToolUse Hook] ← Can block/modify
    ↓
Permission Check (Deny → Allow → Ask)
    ↓
Tool Executes
    ↓
[PostToolUse Hook] ← Can process/log
    ↓
Response to User
```

## Tool Batching & Parallelism

### Golden Rule
**1 MESSAGE = ALL PARALLEL OPERATIONS**

### ✅ Correct: Parallel
```
[Single Message]:
  Read("file1.py")
  Read("file2.py")
  Glob("**/*.ts")
  Grep("pattern", "src/")
```

### ❌ Wrong: Sequential
```
Message 1: Read("file1.py")
Message 2: Read("file2.py")  // Should be parallel!
```

### When to Use Each

**PARALLEL (same message)**:
- Multiple file reads
- Multiple grep/glob searches
- Multiple agent spawns
- Independent bash commands

**SEQUENTIAL (separate messages)**:
- Read → Edit based on contents
- Git add → commit → push
- Create directory → write files
- Output of A needed for B

## Security Safeguards

### Blocklisted by Default
- `curl` / `wget` (arbitrary content)
- Network-unsafe operations

### Filesystem Restrictions
- Write limited to working directory
- Read extended for libraries
- Parent writes require `additionalDirectories`

### Domain Filtering
```json
"allow": ["WebFetch(domain:github.com)"]
```

## Performance Targets

| Operation | Target |
|-----------|--------|
| Command startup | < 500ms |
| Simple operations | < 100ms |
| Complex transforms | < 5s |
| Parallel tools | ~same as single |

## Custom Tools via MCP

```
Tool naming: mcp__<server>__<tool>

Examples:
mcp__github__search_repositories
mcp__postgres__execute_query
```

## Tool Selection Guide

| Need | Use |
|------|-----|
| File discovery | Glob |
| Content search | Grep |
| File reading | Read |
| Scripting/side effects | Bash |
| External data | WebFetch/WebSearch |
| Custom tools | MCP servers |

## Best Practices

1. **Batch operations**: Maximize parallelism
2. **Minimal permissions**: Only allow needed tools
3. **Use specialized tools**: Glob over `find`, Grep over `grep`
4. **Hook validation**: Deterministic checks via hooks
5. **Security first**: Deny sensitive file access explicitly
6. **Web Compatibility**: Avoid Bash for system-specific operations on web
7. **Tool Selection**: Choose tools suitable for your platform
