#!/bin/bash
# Notification hook for Claude Code
# Triggered by Stop event
#
# Sends desktop notification when Claude completes (local only)
# Skips notifications in web environment

set -e

# Detect execution context
IS_REMOTE="${CLAUDE_CODE_REMOTE:-false}"

# Skip notifications in remote/web environment
if [ "$IS_REMOTE" = "true" ]; then
    # Web environment - desktop notifications not applicable
    exit 0
fi

# Read input
INPUT=$(cat)

# Extract stop reason
STOP_REASON=$(echo "$INPUT" | jq -r '.stop_hook_reason // "unknown"')

# Message based on stop reason
case "$STOP_REASON" in
    "endTurn")
        MESSAGE="Claude completed the task"
        ;;
    "error")
        MESSAGE="Claude encountered an error"
        ;;
    "interrupt")
        MESSAGE="Claude was interrupted"
        ;;
    *)
        MESSAGE="Claude session ended: $STOP_REASON"
        ;;
esac

# Send notification (platform-specific, local only)
if command -v notify-send &> /dev/null; then
    # Linux
    notify-send "Claude Code" "$MESSAGE" 2>/dev/null || true
elif command -v osascript &> /dev/null; then
    # macOS
    osascript -e "display notification \"$MESSAGE\" with title \"Claude Code\"" 2>/dev/null || true
elif command -v powershell.exe &> /dev/null; then
    # WSL/Windows
    powershell.exe -Command "[System.Windows.Forms.MessageBox]::Show('$MESSAGE', 'Claude Code')" 2>/dev/null || true
fi

exit 0
