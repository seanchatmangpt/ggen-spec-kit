# Run Tests

Run the test suite with optional filtering and coverage.

## Usage
```
/run-tests [OPTIONS]
```

## Arguments
- `$1` - Test path or pattern (optional, default: all tests)
- `$2` - Additional pytest options (optional)

## Instructions

Run the test suite using:

```bash
uv run pytest $1 $2 -v
```

If no arguments provided, run the full test suite:
```bash
uv run pytest tests/ -v
```

After running tests:
1. Report the pass/fail summary
2. If failures occur, analyze and explain each failure
3. Suggest fixes for failing tests
4. If all pass, report coverage summary

Common options:
- `tests/unit/` - Unit tests only
- `tests/e2e/` - End-to-end tests only
- `-x` - Stop on first failure
- `--cov=src/specify_cli` - With coverage
- `-k "test_name"` - Filter by name
