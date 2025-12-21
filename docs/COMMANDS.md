# Uvmgr Commands

Complete reference for all 13 uvmgr commands in the RDF-first architecture.

## Commands

- [Build](commands/build.md) - Core command
- [Cache](commands/cache.md) - Core command
- [Deps](commands/deps.md) - Core command
- [Docs](commands/docs.md) - Core command
- [Dod](commands/dod.md) - Core command
- [Guides](commands/guides.md) - Core command
- [Infodesign](commands/infodesign.md) - Core command
- [Lint](commands/lint.md) - Core command
- [Mermaid](commands/mermaid.md) - Core command
- [Otel](commands/otel.md) - Core command
- [Terraform](commands/terraform.md) - Core command
- [Tests](commands/tests.md) - Core command
- [Worktree](commands/worktree.md) - Core command

## Three-Tier Architecture

Each command implements:

1. **CLI Layer** (`commands/{name}.py`)
   - User interface via Typer
   - Argument parsing and validation
   - Output formatting (text/JSON)

2. **Ops Layer** (`ops/{name}.py`)
   - Pure business logic
   - Input validation
   - Data transformation

3. **Runtime Layer** (`runtime/{name}.py`)
   - Subprocess execution
   - File I/O operations
   - External tool integration

## Constitutional Equation

Each command is generated from RDF specification:

```
code = μ(specification.ttl)
```

Where:
- **specification**: `ontology/cli-commands-uvmgr-full.ttl`
- **μ**: SPARQL extraction + template rendering
- **code**: CLI, ops, and runtime modules

## Testing

### Unit Tests (Ops Layer)
```bash
pytest tests/unit/test_ops_*.py
```

### Integration Tests (Runtime)
```bash
pytest tests/integration/test_runtime_*.py
```

### E2E Tests (CLI)
```bash
pytest tests/e2e/test_e2e_*.py
```

### Constitutional Equation Tests
```bash
pytest tests/integration/test_constitutional_equation_*.py
```

## Development

See `IMPLEMENTATION_GUIDE.md` for adding new commands.
