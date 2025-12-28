#!/bin/bash
# Session start hook for Claude Code
# Triggered by SessionStart event
#
# Sets up the development environment

set -e

# Check for required tools
REQUIRED_TOOLS=(
    "uv"
    "git"
    "python3"
)

MISSING_TOOLS=()

for tool in "${REQUIRED_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_TOOLS+=("$tool")
    fi
done

if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    echo "WARNING: Missing required tools: ${MISSING_TOOLS[*]}" >&2
fi

# Check for optional tools
OPTIONAL_TOOLS=(
    "ggen"
    "ruff"
    "mypy"
)

MISSING_OPTIONAL=()

for tool in "${OPTIONAL_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_OPTIONAL+=("$tool")
    fi
done

if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
    echo "INFO: Optional tools not found: ${MISSING_OPTIONAL[*]}" >&2
fi

# Check if uv environment is set up
if [ -f "pyproject.toml" ]; then
    if [ ! -d ".venv" ]; then
        echo "INFO: Virtual environment not found. Run 'uv sync' to set up." >&2
    fi
fi

# Check git status
if [ -d ".git" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

    if [ "$DIRTY" != "0" ]; then
        echo "INFO: Git working directory has $DIRTY uncommitted changes on branch $BRANCH" >&2
    fi
fi

exit 0
