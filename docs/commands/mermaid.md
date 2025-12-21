# Mermaid Command

## Description

Mermaid diagram generation from code/specs

## Usage

```bash
specify mermaid --help
```

## Examples

### Basic Usage

```bash
specify mermaid
```

## Architecture

### CLI Layer
`src/specify_cli/commands/mermaid.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/mermaid.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/mermaid.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_mermaid.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_mermaid.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_mermaid.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
