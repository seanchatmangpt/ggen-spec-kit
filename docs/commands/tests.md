# Tests Command

## Description

Run tests with pytest, coverage, and CI verification

## Usage

```bash
specify tests --help
```

## Examples

### Basic Usage

```bash
specify tests
```

## Architecture

### CLI Layer
`src/specify_cli/commands/tests.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/tests.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/tests.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_tests.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_tests.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_tests.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
