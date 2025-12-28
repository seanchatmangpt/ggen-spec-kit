#!/bin/bash
# Post-edit formatting hook for Claude Code
# Triggered by PostToolUse on Edit/Write operations
#
# This hook runs formatters after file edits

set -e

# Read tool input from stdin
INPUT=$(cat)

# Extract file path
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // empty')

if [ -z "$FILE_PATH" ] || [ ! -f "$FILE_PATH" ]; then
    exit 0
fi

# Get file extension
EXT="${FILE_PATH##*.}"

# Format based on file type
case "$EXT" in
    py)
        # Format Python with ruff (if available)
        if command -v ruff &> /dev/null; then
            ruff format "$FILE_PATH" --quiet 2>/dev/null || true
            ruff check "$FILE_PATH" --fix --quiet 2>/dev/null || true
        fi
        ;;
    json)
        # Validate JSON (but don't reformat to preserve style)
        python3 -m json.tool "$FILE_PATH" > /dev/null 2>&1 || {
            echo "WARNING: Invalid JSON in $FILE_PATH" >&2
        }
        ;;
    ttl|turtle)
        # Validate Turtle syntax (if rapper available)
        if command -v rapper &> /dev/null; then
            rapper -q -i turtle "$FILE_PATH" > /dev/null 2>&1 || {
                echo "WARNING: Invalid Turtle syntax in $FILE_PATH" >&2
            }
        fi
        ;;
esac

exit 0
