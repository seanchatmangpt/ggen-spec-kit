# Definition of Done

Acceptance criteria and quality standards for work in ggen spec-kit.

## Overview

The **Definition of Done** (DoD) specifies what "done" means for different work items. All work must meet these criteria before being merged to main.

---

## Code Changes

### Code Quality

- [ ] **Type hints** - All function parameters and returns have type annotations
- [ ] **Docstrings** - Public functions have docstrings (NumPy style)
- [ ] **Linting** - `ruff check src/` passes with no violations
- [ ] **Formatting** - `black src/` passes (code is formatted)
- [ ] **Type checking** - `mypy src/` passes with no errors
- [ ] **Complexity** - Cyclomatic complexity < 10 per function
- [ ] **Line length** - No lines > 100 characters (except URLs)
- [ ] **Naming** - Clear, descriptive names (no abbreviations)

### Architecture Compliance

- [ ] **Layer separation** - No imports across command ↔ ops ↔ runtime boundaries
- [ ] **Pure ops** - Operations layer has no side effects (no file I/O, subprocess, HTTP)
- [ ] **Side effects in runtime** - All I/O is in runtime layer via `run_logged()`
- [ ] **No hardcoded paths** - Uses `platformdirs` or configuration
- [ ] **Configuration driven** - Uses `pyproject.toml` or environment variables
- [ ] **Error handling** - Appropriate try-catch with meaningful error messages

### Security

- [ ] **No shell=True** - All subprocess calls use list syntax (never `shell=True`)
- [ ] **Path validation** - File operations validate paths (no traversal attacks)
- [ ] **Secrets safe** - No credentials in code, uses environment/config
- [ ] **Dependency review** - No untrusted/unmaintained dependencies
- [ ] **Input validation** - User input validated before processing

### Testing

- [ ] **Test coverage** - New code has corresponding tests
- [ ] **Coverage > 80%** - Overall project maintains >80% coverage
- [ ] **Unit tests** - Business logic has isolated unit tests
- [ ] **Integration tests** - Inter-layer interactions tested
- [ ] **Edge cases** - Tests cover happy path, errors, edge cases
- [ ] **Tests pass** - `uv run pytest tests/` passes
- [ ] **No test skips** - No `@skip` or `@pytest.mark.skip` without justification

### Documentation

- [ ] **README updated** - Changes documented in README
- [ ] **Docstrings added** - New public APIs have docstrings
- [ ] **Changelog entry** - Change documented in CHANGELOG.md
- [ ] **Example added** - If new feature, example included in docs/
- [ ] **API reference updated** - If public API changed, reference updated

---

## RDF Specifications

### Semantic Correctness

- [ ] **Valid Turtle** - Syntax is correct, parses without errors
- [ ] **SHACL validation** - Passes `ggen sync` validation (μ₁)
- [ ] **Proper namespaces** - Uses correct prefixes and URIs
- [ ] **Ontology aligned** - Uses existing classes/properties from spec-kit-schema.ttl
- [ ] **Unique IRIs** - All resource IRIs are unique within spec

### Specification Quality

- [ ] **Descriptive** - Labels and comments are clear and complete
- [ ] **Complete** - All required properties present
- [ ] **Linked** - Related resources linked via properties
- [ ] **Consistent** - Naming and structure consistent with existing specs
- [ ] **Examples** - Complex specs have example instances

### Generation

- [ ] **Idempotent** - `ggen sync` run twice produces identical output
- [ ] **No conflicts** - Generated code doesn't conflict with hand-written code
- [ ] **Tests pass** - Generated tests pass (`uv run pytest tests/`)
- [ ] **Code quality** - Generated code meets code quality standards above

---

## Documentation

### Content Quality

- [ ] **Clear purpose** - First paragraph explains what document covers
- [ ] **Well organized** - Logical sections with clear headings
- [ ] **Examples included** - Practical examples for key concepts
- [ ] **Links working** - All cross-references are valid links
- [ ] **Typos checked** - No obvious spelling/grammar errors
- [ ] **Current info** - Reflects actual behavior (not aspirational)

### Diataxis Compliance

**Tutorials (Learning):**
- [ ] Teaches concepts progressively
- [ ] Hands-on, learner-focused
- [ ] 10-25 minute duration
- [ ] No prerequisite knowledge assumed

**How-To Guides (Task-oriented):**
- [ ] Solves specific practical problem
- [ ] Assumes some knowledge
- [ ] Step-by-step instructions
- [ ] Can be referenced mid-task

**Reference (Information):**
- [ ] Complete and accurate
- [ ] Organized for quick lookup
- [ ] All options/parameters documented
- [ ] Examples for each major section

**Explanation (Understanding):**
- [ ] Explores why/how behind concepts
- [ ] Discusses alternatives and tradeoffs
- [ ] Non-linear reading OK
- [ ] Philosophical/conceptual

### Coverage

- [ ] **Visible in navigation** - Indexed in README files
- [ ] **Discoverable** - Linked from related docs
- [ ] **Cross-referenced** - "See Also" sections point to related content
- [ ] **Not orphaned** - Not unreferenced dead documentation

---

## Testing

### Unit Tests

- [ ] **Test per module** - Each module has `tests/unit/test_*.py`
- [ ] **Coverage > 80%** - Lines and branches covered
- [ ] **Isolation** - Mocks external dependencies
- [ ] **Named clearly** - Test names describe what they test
- [ ] **Fast** - Unit tests complete in <100ms
- [ ] **Deterministic** - Always pass/fail consistently

### Integration Tests

- [ ] **Test interactions** - Tests between layers (ops ↔ runtime)
- [ ] **Real file I/O** - Uses temp directories, not mocks
- [ ] **Setup/teardown** - Proper test fixtures
- [ ] **Error cases** - Tests error handling paths

### E2E Tests

- [ ] **Command execution** - Tests actual CLI commands
- [ ] **Example workflow** - Common workflows tested
- [ ] **Realistic data** - Uses representative test data
- [ ] **Performance acceptable** - E2E tests complete in <30s per test

### Test Infrastructure

- [ ] **pytest configured** - `pyproject.toml` has pytest config
- [ ] **Fixtures available** - Common fixtures in `conftest.py`
- [ ] **CI/CD runs tests** - GitHub Actions or equivalent
- [ ] **Coverage tracked** - Coverage reports in CI

---

## Pull Request

### Process

- [ ] **Branch created** - Work on feature branch (not main)
- [ ] **Commits logical** - Each commit is logical unit
- [ ] **Messages clear** - Commit messages describe "why"
- [ ] **PR description complete** - Explains changes and testing
- [ ] **Self-reviewed** - Author reviewed own changes first
- [ ] **Code review** - Peer review completed and approved
- [ ] **CI passes** - All checks green before merge

### Pre-merge

- [ ] **Conflicts resolved** - No merge conflicts
- [ ] **Branch up-to-date** - Rebased on latest main (if needed)
- [ ] **All tests pass** - Including new tests
- [ ] **Coverage maintained** - Doesn't decrease overall coverage
- [ ] **No regressions** - Existing tests still pass

---

## Release

### Release Candidate Checklist

- [ ] **Version updated** - `pyproject.toml` version bumped correctly
- [ ] **Changelog updated** - `CHANGELOG.md` has new entry
- [ ] **GitHub release notes** - Release notes written
- [ ] **All tests pass** - Full test suite clean
- [ ] **Build succeeds** - `uv build` produces wheel/sdist
- [ ] **Documentation published** - Docs regenerated and deployed
- [ ] **No known issues** - All known bugs tracked (can be Future)

### Post-release

- [ ] **Tag created** - Git tag matches version
- [ ] **Package published** - Wheel available on package registry
- [ ] **Release notes published** - GitHub release page updated
- [ ] **Documentation live** - Latest docs online
- [ ] **Announcement made** - Users informed of release

---

## Critical Requirements

Items marked **CRITICAL** must be met or PR is blocked:

### Always Required
- ✓ **Type hints** - All functions MUST have type hints
- ✓ **Tests** - New code MUST have tests
- ✓ **Linting passes** - `ruff check` MUST pass
- ✓ **CI passes** - All GitHub Actions MUST be green
- ✓ **No hardcoded paths** - Code MUST use configuration
- ✓ **No shell=True** - Subprocess MUST use list syntax

### For RDF Changes
- ✓ **SHACL passes** - RDF MUST validate against shapes
- ✓ **Idempotent** - `ggen sync` run twice MUST produce identical output
- ✓ **Tests generated code** - Generated code MUST have tests

### For Documentation
- ✓ **Complete reference** - All parameters MUST be documented
- ✓ **Examples included** - Complex features MUST have examples
- ✓ **Linked** - New docs MUST be linked from index

---

## Gradual Adoption

Some DoD criteria are enforced immediately, others have adoption timelines:

### Enforced Now
- Type hints (mypy strict mode)
- Linting (ruff)
- Code formatting (black)
- Testing (pytest)
- SHACL validation (for RDF)

### Enforced in 90 Days
- >80% test coverage
- All public APIs documented
- No hardcoded paths/secrets

### Best Effort (Not Enforced)
- Documentation examples
- Cross-references completeness
- README updates (encouraged but optional)

---

## Checklist Template

Use this for pull requests:

```markdown
## Definition of Done Checklist

### Code Quality
- [ ] Type hints on all functions
- [ ] Linting passes (`ruff check`)
- [ ] Formatting passes (`black`)
- [ ] Type checking passes (`mypy`)

### Testing
- [ ] New code has tests
- [ ] All tests pass (`pytest`)
- [ ] Coverage maintained or improved

### Architecture
- [ ] Layer separation correct
- [ ] No circular imports
- [ ] Configuration used (no hardcodes)

### Security
- [ ] No shell=True
- [ ] No secrets in code
- [ ] Input validated

### Documentation
- [ ] README updated
- [ ] Docstrings added
- [ ] CHANGELOG entry created

### RDF (if applicable)
- [ ] Valid Turtle syntax
- [ ] Passes SHACL validation
- [ ] `ggen sync` idempotent
- [ ] Generated code works

### CI/CD
- [ ] All checks green
- [ ] No regressions
- [ ] Peer review approved
```

---

## Quality Metrics

Track these metrics to ensure DoD is maintained:

| Metric | Target | Measure |
|--------|--------|---------|
| Test coverage | > 80% | `pytest --cov` |
| Type hints | 100% | `mypy` strict mode |
| Linting | 0 violations | `ruff check` |
| Doc coverage | > 90% | API reference completeness |
| PR review time | < 24 hours | GitHub analytics |
| Build time | < 2 minutes | CI/CD duration |
| Test runtime | < 30 seconds | `pytest -v` |

---

## Exceptions

In rare cases, items can be exempted from DoD with explicit approval:

- **Security team** can approve skipping security checks
- **Tech lead** can approve skipping tests (with comment)
- **Architect** can approve skipping layer separation (with design doc)

Exceptions must be tracked and revisited.

---

## See Also

- `/docs/guides/testing/run-tests.md` - How to run tests
- `/docs/guides/testing/setup-tests.md` - Test setup
- `/docs/guides/testing/debug-tests.md` - Debugging tests
- `/docs/reference/quality-metrics.md` - Quality standards
- `CONTRIBUTING.md` - Contribution guidelines
