# Cache Command

## Description

Cache management and operations

## Usage

```bash
specify cache --help
```

## Examples

### Basic Usage

```bash
specify cache
```

## Architecture

### CLI Layer
`src/specify_cli/commands/cache.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/cache.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/cache.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_cache.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_cache.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_cache.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
