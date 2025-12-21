# Terraform Command

## Description

Terraform support and infrastructure as code

## Usage

```bash
specify terraform --help
```

## Examples

### Basic Usage

```bash
specify terraform
```

## Architecture

### CLI Layer
`src/specify_cli/commands/terraform.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/terraform.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/terraform.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_terraform.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_terraform.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_terraform.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
