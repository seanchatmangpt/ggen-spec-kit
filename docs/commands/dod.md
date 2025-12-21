# Dod Command

## Description

Definition of Done automation and checklists

## Usage

```bash
specify dod --help
```

## Examples

### Basic Usage

```bash
specify dod
```

## Architecture

### CLI Layer
`src/specify_cli/commands/dod.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/dod.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/dod.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_dod.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_dod.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_dod.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
