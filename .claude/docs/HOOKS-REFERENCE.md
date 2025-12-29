# Claude Code Hooks Reference

## Overview

Hooks are shell commands that execute in response to Claude Code events, enabling deterministic control over tool execution, validation, logging, and notifications. Desktop only; not available in web browser.

## Hook Events

| Event | Timing | Can Block | Use Cases |
|-------|--------|-----------|-----------|
| `PreToolUse` | Before tool execution | Yes (exit 2) | Validation, blocking |
| `PostToolUse` | After successful execution | No | Formatting, logging |
| `PostToolUseFailure` | After failed execution | No | Error handling |
| `PermissionRequest` | Permission dialog shown | Yes (exit 2) | Custom permission logic |
| `UserPromptSubmit` | Before prompt processing | No | Input validation |
| `SessionStart` | Session begins | No | Environment setup |
| `SessionEnd` | Session terminates | No | Cleanup |
| `Stop` | Claude finishes responding | No | Continuation control |
| `SubagentStart` | Subagent task begins | No | Monitoring |
| `SubagentStop` | Subagent task ends | No | Result handling |
| `PreCompact` | Before context compaction | No | Pre-compact ops |
| `Notification` | Alert triggered | No | Custom notifications |

## Configuration Schema

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolPattern|*",
        "hooks": [
          {
            "type": "command",
            "command": "/path/to/script.sh",
            "timeout": 60000
          }
        ]
      }
    ]
  }
}
```

## Matcher Patterns

```json
"matcher": "Bash"           // Exact tool match
"matcher": "Bash|Edit"      // Multiple tools
"matcher": "*"              // All tools
"matcher": ""               // All tools (empty)
```

## Hook Input (JSON via stdin)

```json
{
  "session_id": "uuid-string",
  "transcript_path": "/path/to/transcript.txt",
  "cwd": "/current/working/directory",
  "permission_mode": "ask|allow|deny",
  "hook_event_name": "PreToolUse|PostToolUse|...",
  "tool_name": "Read|Write|Edit|Bash|...",
  "tool_input": {
    "file_path": "/path/to/file",
    "command": "..."
  }
}
```

## Exit Code Semantics

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success (decision applied) |
| `2` | Blocking error (blocks tool, stderr to Claude) |
| `1, 3+` | Non-blocking error (shown to user only) |

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `CLAUDE_PROJECT_DIR` | Project root path |
| `CLAUDE_ENV_FILE` | Environment file path (SessionStart only) |
| `CLAUDE_CODE_REMOTE` | `"true"` or `"false"` |

## Example: PreToolUse Permission Control

```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Block sensitive files
if [[ "$file_path" =~ \.env|\.git|secrets ]]; then
  echo "Error: Protected file" >&2
  exit 2
fi

exit 0
```

## Example: PostToolUse Auto-Format

```bash
#!/bin/bash
input=$(cat)
file=$(echo "$input" | jq -r '.tool_input.file_path // ""')

# Format TypeScript files
if [[ "$file" == *.ts ]]; then
  npx prettier --write "$file"
fi

exit 0
```

## Example: SessionStart Environment

```bash
#!/bin/bash
# Set persistent environment variables
cat > "$CLAUDE_ENV_FILE" <<'EOF'
export NODE_ENV=development
export CUSTOM_VAR=value
EOF

exit 0
```

## Example: Command Logging

```bash
#!/bin/bash
input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')
echo "[$(date)] BASH: $command" >> ~/.claude/command-audit.log
exit 0
```

## PreToolUse Decision Output

```json
// Allow
{ "decision": "allow" }

// Deny
{ "decision": "deny", "reason": "Explanation" }

// Ask user
{ "decision": "ask" }

// Allow with modified input
{
  "decision": "allow",
  "updatedInput": {
    "command": "modified_command"
  }
}
```

## Best Practices

1. **Keep hooks fast** - Long-running hooks slow execution
2. **Use timeout parameter** - Prevent hanging
3. **Exit code 2 blocks** - Only use in PreToolUse/PermissionRequest
4. **Log to stderr** - stdout goes to transcript
5. **Use absolute paths** - For script locations
6. **Quote variables** - Prevent injection
7. **Validate inputs** - Never trust directly
8. **Desktop only** - Hooks not available in web sessions

## Security Considerations

```bash
# ✅ CORRECT: Validate paths
if [[ "$FILE" =~ \.\. ]]; then
  echo "Path traversal detected" >&2
  exit 2
fi

# ✅ CORRECT: Quote variables
FILE="$CLAUDE_PROJECT_DIR/data.txt"

# ❌ WRONG: Unquoted variables
FILE=$CLAUDE_PROJECT_DIR/data.txt
```

## Configuration Locations

| Scope | Location | Priority |
|-------|----------|----------|
| Enterprise | Managed settings | Highest |
| User | `~/.claude/settings.json` | Lower |
| Project | `.claude/settings.json` | Higher than user |
