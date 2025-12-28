#!/bin/bash
# Pre-commit validation hook for Claude Code
# Triggered by PreToolUse on Edit/Write operations
#
# Exit codes:
#   0 - Allow the operation
#   1 - Block the operation (shows stderr to user)
#   2 - Block silently

set -e

# Read tool input from stdin
INPUT=$(cat)

# Extract file path from tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')

if [ -z "$FILE_PATH" ]; then
    exit 0  # No file path, allow
fi

# Block editing generated files
GENERATED_PATTERNS=(
    "src/specify_cli/commands/*.py"
    "docs/*.md"
    "CHANGELOG.md"
)

for pattern in "${GENERATED_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == $pattern ]]; then
        echo "BLOCKED: Cannot edit generated file: $FILE_PATH" >&2
        echo "Edit the RDF source instead, then run 'ggen sync'" >&2
        exit 1
    fi
done

# Block editing secrets
SECRET_PATTERNS=(
    ".env"
    ".env.*"
    "*credentials*"
    "*secret*"
    "*.pem"
    "*.key"
)

for pattern in "${SECRET_PATTERNS[@]}"; do
    if [[ "$FILE_PATH" == $pattern ]]; then
        echo "BLOCKED: Cannot edit secret file: $FILE_PATH" >&2
        exit 1
    fi
done

exit 0
