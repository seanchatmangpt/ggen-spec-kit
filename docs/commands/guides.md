# Guides Command

## Description

Development guides and documentation

## Usage

```bash
specify guides --help
```

## Examples

### Basic Usage

```bash
specify guides
```

## Architecture

### CLI Layer
`src/specify_cli/commands/guides.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/guides.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/guides.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_guides.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_guides.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_guides.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
