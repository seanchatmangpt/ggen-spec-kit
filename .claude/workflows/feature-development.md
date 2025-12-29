# Feature Development Workflow

## Process

### 1. Research & Plan
**Agent/Skill**: Code Reviewer, Debugger
**Tools**: Read, Glob, Grep
**Steps**:
- Explore similar features for patterns
- Map integration points
- Identify file locations to modify

**Success**: Clear understanding of scope and existing patterns

---

### 2. Define Specification (RDF-First)
**Agent/Skill**: Spec Writer
**Tools**: Edit (ontology/cli-commands.ttl)
**Steps**:
- Add RDF definition to ontology/cli-commands.ttl
- Define SHACL validation shapes if needed
- Create SPARQL query (if data extraction required)
- Create/update Tera template if needed

**Success**: Valid TTL file with complete specification

---

### 3. Generate Code
**Agent/Skill**: ggen Operator
**Tools**: Bash (ggen sync)
**Steps**:
1. Run `ggen sync`
2. Review generated files in src/specify_cli/commands/
3. Verify code structure matches specification

**Success**: Generated files appear correctly, no syntax errors

---

### 4. Implement Business Logic
**Agent/Skill**: Code Reviewer
**Tools**: Edit (ops/, runtime/)
**Steps**:
- Implement operations in `src/specify_cli/ops/` (pure logic)
- Implement runtime in `src/specify_cli/runtime/` (I/O, subprocesses)
- Respect three-tier architecture

**Success**: Code compiles, type hints pass, follows architecture

---

### 5. Write & Run Tests
**Agent/Skill**: Test Runner
**Tools**: Bash (pytest), Write
**Steps**:
1. Write tests in `tests/`
2. Run `uv run pytest tests/ -v`
3. Verify 80%+ coverage
4. Fix failures using Debugger skill if needed

**Success**: All tests pass, coverage meets threshold

---

### 6. Validate Quality
**Agent/Skill**: Code Reviewer, Architecture Validator
**Tools**: Bash
**Steps**:
1. Run `uv run ruff check src/`
2. Run `uv run mypy src/`
3. Run full test suite
4. Verify no architecture violations

**Success**: No lint errors, type-safe, all tests pass
