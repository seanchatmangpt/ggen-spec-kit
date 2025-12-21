# Build Command

## Description

Build wheels, sdists, and executables using PyInstaller

## Usage

```bash
specify build --help
```

## Examples

### Basic Usage

```bash
specify build
```

## Architecture

### CLI Layer
`src/specify_cli/commands/build.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/build.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/build.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_build.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_build.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_build.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
