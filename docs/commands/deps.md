# Deps Command

## Description

Dependency management with uv (add/remove/upgrade/list/lock)

## Usage

```bash
specify deps --help
```

## Examples

### Basic Usage

```bash
specify deps
```

## Architecture

### CLI Layer
`src/specify_cli/commands/deps.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/deps.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/deps.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_deps.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_deps.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_deps.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
