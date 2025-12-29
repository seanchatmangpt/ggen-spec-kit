#!/bin/bash
# Session start hook for Claude Code
# Triggered by SessionStart event
#
# Sets up the development environment for both local CLI and web environments

set -e

# Detect execution context
IS_REMOTE="${CLAUDE_CODE_REMOTE:-false}"
PROJECT_ROOT="$(pwd)"

echo "🚀 Starting Claude Code session..." >&2

if [ "$IS_REMOTE" = "true" ]; then
    echo "📡 Running in Claude Code on the web" >&2
else
    echo "💻 Running in Claude Code CLI (local)" >&2
fi

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
    echo "❌ ERROR: Missing required tools: ${MISSING_TOOLS[*]}" >&2
    echo "Please install missing tools before continuing." >&2
    exit 1
fi

# Install dependencies with uv sync
if [ -f "pyproject.toml" ]; then
    echo "📦 Installing dependencies with uv sync..." >&2

    if [ ! -d ".venv" ]; then
        echo "Creating new virtual environment..." >&2
    fi

    # Install all dependency groups for development
    if ! uv sync --all-groups 2>&1 | tee /tmp/uv-sync.log >&2; then
        echo "⚠️  Warning: uv sync had issues, trying without all groups..." >&2
        uv sync 2>&1 | tee /tmp/uv-sync.log >&2 || {
            echo "❌ ERROR: Failed to install dependencies" >&2
            exit 1
        }
    fi

    echo "✅ Dependencies installed successfully" >&2
else
    echo "⚠️  Warning: No pyproject.toml found in current directory" >&2
fi

# Set up environment variables
if [ -n "$CLAUDE_ENV_FILE" ]; then
    echo "🔧 Configuring environment variables..." >&2

    # Set PYTHONPATH to include src directory
    echo "export PYTHONPATH=${PROJECT_ROOT}/src:${PROJECT_ROOT}:\${PYTHONPATH}" >> "$CLAUDE_ENV_FILE"

    # Set OpenTelemetry configuration for development
    echo "export OTEL_SDK_DISABLED=false" >> "$CLAUDE_ENV_FILE"
    echo "export OTEL_TRACES_EXPORTER=console" >> "$CLAUDE_ENV_FILE"
    echo "export OTEL_METRICS_EXPORTER=console" >> "$CLAUDE_ENV_FILE"
    echo "export OTEL_LOGS_EXPORTER=console" >> "$CLAUDE_ENV_FILE"
    echo "export OTEL_SERVICE_NAME=ggen-spec-kit" >> "$CLAUDE_ENV_FILE"

    # Set project root
    echo "export PROJECT_ROOT=${PROJECT_ROOT}" >> "$CLAUDE_ENV_FILE"

    echo "✅ Environment variables configured" >&2
else
    # Local execution - export directly
    export PYTHONPATH="${PROJECT_ROOT}/src:${PROJECT_ROOT}:${PYTHONPATH}"
    export OTEL_SDK_DISABLED=false
    export OTEL_TRACES_EXPORTER=console
    export OTEL_METRICS_EXPORTER=console
    export OTEL_LOGS_EXPORTER=console
    export OTEL_SERVICE_NAME=ggen-spec-kit
    export PROJECT_ROOT="${PROJECT_ROOT}"
fi

# Check for ggen availability and version
echo "🔍 Checking ggen availability..." >&2
if command -v ggen &> /dev/null; then
    GGEN_VERSION=$(ggen --version 2>&1 || echo "unknown")
    echo "✅ ggen found: $GGEN_VERSION" >&2

    # Verify ggen v5.0.2 (sync only)
    if echo "$GGEN_VERSION" | grep -q "5\.0\."; then
        echo "✅ ggen v5.0.x detected - sync command available" >&2
    else
        echo "⚠️  Warning: ggen version may not be v5.0.x - only 'ggen sync' is supported" >&2
    fi
else
    echo "⚠️  Warning: ggen not found - RDF transformations will not be available" >&2
    echo "Install ggen from: https://github.com/yourusername/ggen" >&2
fi

# Check for optional development tools
OPTIONAL_TOOLS=(
    "ruff"
    "mypy"
    "pytest"
)

MISSING_OPTIONAL=()

for tool in "${OPTIONAL_TOOLS[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        MISSING_OPTIONAL+=("$tool")
    fi
done

if [ ${#MISSING_OPTIONAL[@]} -gt 0 ]; then
    echo "ℹ️  Optional tools not found: ${MISSING_OPTIONAL[*]}" >&2
    echo "These should be available via 'uv run <tool>'" >&2
fi

# Check git status
if [ -d ".git" ]; then
    BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
    DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')

    echo "📂 Git branch: $BRANCH" >&2

    if [ "$DIRTY" != "0" ]; then
        echo "ℹ️  Working directory has $DIRTY uncommitted changes" >&2
    else
        echo "✅ Working directory is clean" >&2
    fi
fi

# Verify project structure
if [ -d "ontology" ] && [ -d "memory" ] && [ -d "sparql" ] && [ -d "templates" ]; then
    echo "✅ RDF-first project structure verified" >&2
else
    echo "⚠️  Warning: Expected RDF directories (ontology, memory, sparql, templates) not all found" >&2
fi

echo "🎉 Session initialization complete!" >&2
exit 0
