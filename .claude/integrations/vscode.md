# VS Code Integration

## Extension Setup

1. Open VS Code
2. Press `Cmd+Shift+X` (Mac) or `Ctrl+Shift+X` (Windows/Linux)
3. Search for "Claude Code"
4. Click Install
5. Restart VS Code

## Quick Launch

- **Spark Icon**: Click in top-right toolbar when file is open
- **Command Palette**: `Cmd+Shift+P` → "Claude Code"
- **Status Bar**: Click "✱ Claude Code" in bottom-right

## Recommended Settings

```json
// .vscode/settings.json
{
  "claude-code.diffTool": "auto",
  "claude-code.autoFormat": true,
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "python.linting.ruffEnabled": true,
  "python.linting.mypyEnabled": true
}
```

## Keyboard Shortcuts

| Action | Mac | Windows/Linux |
|--------|-----|---------------|
| Open Claude Code | `Cmd+Shift+P` → Claude | `Ctrl+Shift+P` → Claude |
| Accept diff | Click "Accept" | Click "Accept" |
| Reject diff | Click "Reject" | Click "Reject" |

## Features

### Real-Time Diffs
- See changes before applying
- Accept/reject individual changes
- Undo with checkpoints

### Selection Context
- Select code and ask Claude about it
- Current file automatically shared
- Lint errors shared for context

### Slash Commands
All commands in `.claude/commands/` available:
- `/run-tests`
- `/lint`
- `/review-pr`
- etc.

## Tips

1. Use integrated terminal for Claude CLI
2. Resume conversations with `claude --resume`
3. Configure MCP servers via CLI first
4. Set diff tool to "auto" for best experience
