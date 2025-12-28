#!/bin/bash
# Bash command safety hook for Claude Code
# Triggered by PreToolUse on Bash operations
#
# Exit codes:
#   0 - Allow the operation
#   1 - Block the operation (shows stderr to user)
#   2 - Block silently

set -e

# Read tool input from stdin
INPUT=$(cat)

# Extract command from tool input
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if [ -z "$COMMAND" ]; then
    exit 0
fi

# Dangerous command patterns to block
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \$HOME"
    ":(){:|:&};:"
    "mkfs"
    "dd if="
    "> /dev/sd"
    "chmod -R 777 /"
    "curl.*|.*sh"
    "wget.*|.*sh"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if [[ "$COMMAND" == *"$pattern"* ]]; then
        echo "BLOCKED: Dangerous command pattern detected: $pattern" >&2
        exit 1
    fi
done

# Warn about shell=True equivalent patterns
if [[ "$COMMAND" == *"eval"* ]] || [[ "$COMMAND" == *"\$("* ]]; then
    echo "WARNING: Command contains shell expansion" >&2
    # Allow but warn
fi

# Block force push to main/master
if [[ "$COMMAND" == *"git push"*"--force"* ]] || [[ "$COMMAND" == *"git push"*"-f"* ]]; then
    if [[ "$COMMAND" == *"main"* ]] || [[ "$COMMAND" == *"master"* ]]; then
        echo "BLOCKED: Force push to main/master is not allowed" >&2
        exit 1
    fi
fi

exit 0
