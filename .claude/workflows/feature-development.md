# Feature Development Workflow

## Overview
Complete workflow for implementing new features following RDF-first principles.

## Phases

### Phase 1: Research (Read-Only)
```yaml
mode: plan-mode
tools: [Read, Glob, Grep]
output: Understanding of existing patterns
```

Steps:
1. Explore existing similar features
2. Understand current architecture
3. Identify integration points
4. Document findings

### Phase 2: Specification
```yaml
mode: implementation
tools: [Write, Edit]
output: RDF specification in ontology/
```

Steps:
1. Create RDF specification in `ontology/cli-commands.ttl`
2. Define SHACL shapes for validation
3. Create SPARQL query if needed
4. Create Tera template if needed

### Phase 3: Generation
```yaml
mode: implementation
tools: [Bash]
output: Generated code
```

Steps:
1. Run `ggen sync`
2. Verify generated files
3. Review output for correctness

### Phase 4: Implementation
```yaml
mode: implementation
tools: [Write, Edit]
output: Business logic in ops/runtime
```

Steps:
1. Implement operations in `src/specify_cli/ops/`
2. Implement runtime in `src/specify_cli/runtime/`
3. Follow three-tier architecture rules

### Phase 5: Testing
```yaml
mode: implementation
tools: [Bash, Write]
output: Passing tests
```

Steps:
1. Write tests in `tests/`
2. Run `uv run pytest tests/ -v`
3. Ensure 80%+ coverage
4. Fix any failures

### Phase 6: Validation
```yaml
mode: verification
tools: [Bash]
output: Clean checks
```

Steps:
1. Run `uv run ruff check src/`
2. Run `uv run mypy src/`
3. Run full test suite
4. Verify architecture compliance

## Parallel Opportunities

These can run in parallel:
- Research different aspects simultaneously
- Run lint + type check + tests in parallel
- Multiple test files can be written in parallel

## Error Recovery

If tests fail:
1. Analyze failure output
2. Identify root cause
3. Fix in appropriate layer
4. Re-run tests

If architecture violation:
1. Identify the violation
2. Move code to correct layer
3. Update imports
4. Re-verify
