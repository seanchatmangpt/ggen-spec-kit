# Otel Command

## Description

OpenTelemetry validation and management

## Usage

```bash
specify otel --help
```

## Examples

### Basic Usage

```bash
specify otel
```

## Architecture

### CLI Layer
`src/specify_cli/commands/otel.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/otel.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/otel.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_otel.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_otel.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_otel.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
