# Lint Command

## Description

Code quality checks (ruff, black, mypy)

## Usage

```bash
specify lint --help
```

## Examples

### Basic Usage

```bash
specify lint
```

## Architecture

### CLI Layer
`src/specify_cli/commands/lint.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/lint.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/lint.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_lint.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_lint.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_lint.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
