# Docs Command

## Description

API documentation generation

## Usage

```bash
specify docs --help
```

## Examples

### Basic Usage

```bash
specify docs
```

## Architecture

### CLI Layer
`src/specify_cli/commands/docs.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/docs.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/docs.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_docs.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_docs.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_docs.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
