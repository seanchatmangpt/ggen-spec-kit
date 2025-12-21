# Worktree Command

## Description

Git worktree management

## Usage

```bash
specify worktree --help
```

## Examples

### Basic Usage

```bash
specify worktree
```

## Architecture

### CLI Layer
`src/specify_cli/commands/worktree.py`
- Parses arguments
- Handles user output formatting
- Delegates to ops layer

### Ops Layer
`src/specify_cli/ops/worktree.py`
- Pure business logic
- Input validation
- No side effects

### Runtime Layer
`src/specify_cli/runtime/worktree.py`
- Subprocess execution
- File I/O operations
- External tool integration

## Testing

### Unit Tests
```bash
pytest tests/unit/test_ops_worktree.py
```

### Runtime Tests
```bash
pytest tests/integration/test_runtime_worktree.py
```

### E2E Tests
```bash
pytest tests/e2e/test_e2e_worktree.py
```

## RDF Specification

Defined in `ontology/cli-commands-uvmgr-full.ttl`

## Related Commands

See `docs/COMMANDS.md` for complete command index.
