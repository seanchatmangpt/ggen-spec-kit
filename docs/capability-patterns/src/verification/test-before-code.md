# 31. Test Before Code

★★

*Write tests before implementation. When tests are generated from specifications, they define expected behavior before code exists—making implementation the act of making tests pass.*

---

Traditional development writes code, then tests to verify it. This approach has tests follow implementation, checking what was built rather than what should be built.

Test Before Code inverts this. Tests are generated from **[Acceptance Criteria](../specification/acceptance-criterion.md)** before implementation exists. The tests define expected behavior. Implementation is the process of making tests pass.

In specification-driven development, this inversion is natural. Specifications define what should happen. Tests are transformations of specifications. Code is what makes those tests pass.

**The problem: Tests written after code test what was built, not what was intended. Implementation errors become encoded in tests.**

---

**The forces at play:**

- *Speed wants to code first.* Writing tests feels like delay.

- *Correctness wants to test first.* Tests define the contract.

- *Iteration wants flexibility.* Strict test-first can feel constraining.

- *Confidence wants coverage.* Tests must cover all acceptance criteria.

The tension: thorough test coverage without slowing down productive work.

---

**Therefore:**

Generate test stubs from acceptance criteria before writing implementation code. Tests define the contract; implementation fulfills it.

**The flow:**

```
Acceptance Criteria (in RDF)
         │
         ▼
    ggen sync
         │
         ▼
Test Stubs (failing tests)
         │
         ▼
Implementation (make tests pass)
         │
         ▼
Verified Capability (tests green)
```

**Acceptance criterion in RDF:**

```turtle
cli:ValidateCommand cli:hasAcceptanceCriterion [
    a sk:AcceptanceCriterion ;
    sk:id "AC-VAL-001" ;
    sk:given "A syntactically valid RDF/Turtle file exists" ;
    sk:when "User runs 'specify validate file.ttl'" ;
    sk:then "Command exits with code 0 and prints 'Valid ✓'" ;
    sk:priority "must"
] .
```

**Generated test stub:**

```python
# tests/e2e/test_validate.py
# AUTO-GENERATED from ontology/cli-commands.ttl
# Run: ggen sync to regenerate

import pytest
from typer.testing import CliRunner
from specify_cli.app import app

runner = CliRunner()


class TestValidateCommand:
    """Tests for the validate command.

    Generated from acceptance criteria in cli-commands.ttl.
    """

    def test_AC_VAL_001_valid_file_succeeds(self, tmp_path):
        """
        AC-VAL-001: Valid file validation

        Given: A syntactically valid RDF/Turtle file exists
        When: User runs 'specify validate file.ttl'
        Then: Command exits with code 0 and prints 'Valid ✓'
        """
        # Given
        valid_file = tmp_path / "valid.ttl"
        valid_file.write_text("""
            @prefix ex: <http://example.org/> .
            ex:subject ex:predicate ex:object .
        """)

        # When
        result = runner.invoke(app, ["validate", str(valid_file)])

        # Then
        assert result.exit_code == 0
        assert "Valid ✓" in result.output

    def test_AC_VAL_002_invalid_file_fails(self, tmp_path):
        """
        AC-VAL-002: Invalid file detection

        Given: A syntactically invalid RDF/Turtle file exists
        When: User runs 'specify validate file.ttl'
        Then: Command exits with non-zero code and prints error with line number
        """
        # Given
        invalid_file = tmp_path / "invalid.ttl"
        invalid_file.write_text("this is not valid turtle")

        # When
        result = runner.invoke(app, ["validate", str(invalid_file)])

        # Then
        assert result.exit_code != 0
        assert "line" in result.output.lower()
```

**The discipline:**

1. **Write specification first:** Define acceptance criteria in RDF
2. **Generate tests:** Run `ggen sync` to produce test stubs
3. **Verify tests fail:** Run pytest, confirm tests fail (no implementation yet)
4. **Implement:** Write code to make tests pass
5. **Verify tests pass:** Run pytest, confirm all tests green
6. **Commit together:** Specification, generated tests, and implementation

---

**Resulting context:**

After applying this pattern, you have:

- Tests that define expected behavior before implementation
- Implementation that provably meets acceptance criteria
- Traceability from tests to criteria to outcomes
- Confidence that what was built matches what was specified

This implements **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** and enables **[37. Continuous Validation](./continuous-validation.md)**.

---

**Related patterns:**

- *Implements:* **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria become tests
- *Part of:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Tests are artifacts
- *Enables:* **[37. Continuous Validation](./continuous-validation.md)** — Tests run in CI
- *Supports:* **[32. Contract Test](./contract-test.md)** — Interface contracts

---

> *"If you can't write a test for it, you don't understand it well enough to build it."*

Test Before Code forces understanding before implementation. It makes the implicit explicit and the assumed verified.
