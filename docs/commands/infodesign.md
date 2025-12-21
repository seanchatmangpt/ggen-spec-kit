# Infodesign Command

## Description

Information design support and tools

## Usage

```bash
specify infodesign --help
```

## Examples

### Basic Usage

```bash
specify infodesign
```

## Architecture

### CLI Layer
`src/specify_cli/commands/infodesign.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/infodesign.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/infodesign.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_infodesign.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_infodesign.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_infodesign.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
