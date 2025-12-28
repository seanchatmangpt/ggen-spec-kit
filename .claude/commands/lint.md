# Lint and Type Check

Run linting and type checking on the codebase.

## Usage
```
/lint [PATH]
```

## Arguments
- `$1` - Path to lint (optional, default: src/)

## Instructions

Run code quality checks:

```bash
# Linting with ruff
uv run ruff check $1

# Type checking with mypy
uv run mypy $1
```

If no path provided, check the entire source directory:
```bash
uv run ruff check src/
uv run mypy src/
```

After running:
1. Report any linting errors with file:line references
2. Report any type errors
3. For fixable issues, offer to auto-fix with `ruff check --fix`
4. Explain complex type errors if present
