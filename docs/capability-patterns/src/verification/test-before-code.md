# 31. Test Before Code

★★

*Write tests before implementation. When tests are generated from specifications, they define expected behavior before code exists—making implementation the act of making tests pass. This is the discipline that ensures what you build is what you intended.*

---

## The Inversion of Development

Traditional development follows a seemingly logical sequence: understand the requirement, write the code, test that it works. The code comes first; the test verifies what was built.

But this sequence has a hidden flaw. Tests written after code test what *was* built, not what *should* have been built. If the implementation contains an error—a misunderstood requirement, a subtle bug, an edge case overlooked—the test may encode that error. The test passes because it matches the code, not because the code is correct.

Test Before Code inverts this sequence:

```
Traditional:
  Requirement → Code → Test (verify code)

  Risk: Test encodes implementation errors

Test Before Code:
  Requirement → Test → Code (satisfy test)

  Benefit: Test encodes requirement, code must satisfy it
```

In specification-driven development, this inversion is natural. Specifications define what should happen. Tests are transformations of specifications—they express the same requirements in executable form. Implementation is simply the process of making those executable requirements pass.

---

## The Specification-Test Connection

**The fundamental problem: Tests written after code test what was built, not what was intended. Implementation errors become encoded in tests, making bugs invisible.**

Let us trace how this happens:

### The Error Encoding Problem

```python
# Specification says: "Exit code 0 for valid files"
# Developer implements incorrectly:

def validate(file):
    # Bug: always returns 0, even for invalid files
    try:
        parse(file)
    except:
        pass  # Swallows errors!
    return 0

# Test written after implementation:
def test_validate():
    result = validate("any_file.ttl")
    assert result == 0  # Passes! But is wrong.
```

The test passes because it matches the implementation. The bug is invisible—both code and test agree on the wrong behavior.

### The Test-First Solution

```python
# Test generated from specification BEFORE implementation:
def test_valid_file_returns_zero(tmp_path):
    """
    Specification: Exit code 0 for valid files
    """
    valid = tmp_path / "valid.ttl"
    valid.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

    result = validate(str(valid))
    assert result == 0

def test_invalid_file_returns_nonzero(tmp_path):
    """
    Specification: Exit code non-zero for invalid files
    """
    invalid = tmp_path / "invalid.ttl"
    invalid.write_text("not valid turtle")

    result = validate(str(invalid))
    assert result != 0  # This will FAIL with buggy implementation!
```

Now the second test fails, revealing the bug. The test was generated from the specification, not from the implementation, so it tests what *should* happen.

---

## The Forces

Several tensions shape test-before-code practices:

### Force: Speed vs. Safety

*Writing tests first feels slower. Coding first feels productive.*

The urge to "just write the code" is strong. Tests feel like overhead, delay before the "real work." But code without tests often needs debugging, rework, and late-stage fixes that cost more than upfront testing.

**Resolution:** View tests as the first draft of implementation. Writing `assert result == 0` is faster than debugging why the wrong value appears in production.

### Force: Flexibility vs. Discipline

*Strict test-first can feel constraining during exploration.*

When you're exploring a problem—prototyping, experimenting, learning—rigid test-first discipline can slow you down. You don't know what you're building yet.

**Resolution:** Distinguish exploration from implementation. Explore freely, but once you know what to build, write the tests first. The specification crystallizes exploration into requirements; tests crystallize requirements into executable form.

### Force: Coverage vs. Burden

*Complete coverage requires many tests. Many tests require maintenance.*

Testing every acceptance criterion, every edge case, every error path creates a large test suite. Large test suites take time to run, effort to maintain, and can become fragile.

**Resolution:** Generate tests from specifications. Generated tests are automatically maintained when specifications change. Focus manual testing on aspects that resist specification (exploratory testing, usability testing).

### Force: Specification vs. Implementation

*Tests should test specification, not implementation.*

Tests coupled to implementation details break when refactoring, even when behavior is unchanged. This creates false negatives and erodes test trust.

**Resolution:** Generate tests from acceptance criteria, not from implementation knowledge. Test what the system should do (behavior), not how it does it (implementation).

---

## Therefore

**Generate test stubs from acceptance criteria before writing implementation code. Tests define the contract; implementation fulfills it. The sequence is: specify → generate tests → fail tests → implement → pass tests.**

The test-before-code flow:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TEST BEFORE CODE WORKFLOW                                               │
│                                                                          │
│  1. SPECIFY acceptance criteria                                          │
│     │                                                                    │
│     │  cli:validate sk:hasAcceptanceCriterion [                         │
│     │      sk:given "valid RDF file" ;                                  │
│     │      sk:when "user runs validate" ;                               │
│     │      sk:then "exit 0, print success" ] .                          │
│     │                                                                    │
│     ▼                                                                    │
│  2. GENERATE tests from criteria                                         │
│     │                                                                    │
│     │  ggen sync → test_validate.py                                     │
│     │                                                                    │
│     ▼                                                                    │
│  3. RUN tests (expect failure)                                           │
│     │                                                                    │
│     │  pytest → FAILED (no implementation yet)                          │
│     │                                                                    │
│     ▼                                                                    │
│  4. IMPLEMENT to make tests pass                                         │
│     │                                                                    │
│     │  def validate(): ...                                              │
│     │                                                                    │
│     ▼                                                                    │
│  5. RUN tests (expect success)                                           │
│     │                                                                    │
│     │  pytest → PASSED                                                  │
│     │                                                                    │
│     ▼                                                                    │
│  6. COMMIT specification + tests + implementation together               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria in RDF

### The Gherkin-RDF Mapping

Acceptance criteria follow the Gherkin pattern: Given-When-Then. This structure maps naturally to RDF:

```turtle
@prefix sk: <https://spec-kit.org/ontology#> .
@prefix cli: <https://spec-kit.org/cli#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Command definition with acceptance criteria
cli:ValidateCommand a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;

    # Criterion 1: Valid file succeeds
    sk:hasAcceptanceCriterion [
        a sk:AcceptanceCriterion ;
        sk:id "AC-VAL-001" ;
        sk:title "Valid file validation succeeds" ;
        sk:given "A syntactically valid RDF/Turtle file exists at the specified path" ;
        sk:when "User runs 'specify validate <path>'" ;
        sk:then "Command exits with code 0 and prints 'Valid ✓'" ;
        sk:priority "must" ;
        sk:category "success-path"
    ] ;

    # Criterion 2: Invalid file fails
    sk:hasAcceptanceCriterion [
        a sk:AcceptanceCriterion ;
        sk:id "AC-VAL-002" ;
        sk:title "Invalid file validation fails" ;
        sk:given "A syntactically invalid RDF/Turtle file exists at the specified path" ;
        sk:when "User runs 'specify validate <path>'" ;
        sk:then "Command exits with code 1 and prints error with line number" ;
        sk:priority "must" ;
        sk:category "error-path"
    ] ;

    # Criterion 3: Missing file fails gracefully
    sk:hasAcceptanceCriterion [
        a sk:AcceptanceCriterion ;
        sk:id "AC-VAL-003" ;
        sk:title "Missing file handled gracefully" ;
        sk:given "No file exists at the specified path" ;
        sk:when "User runs 'specify validate <path>'" ;
        sk:then "Command exits with code 2 and prints 'File not found: <path>'" ;
        sk:priority "must" ;
        sk:category "error-path"
    ] ;

    # Criterion 4: SHACL validation with custom shapes
    sk:hasAcceptanceCriterion [
        a sk:AcceptanceCriterion ;
        sk:id "AC-VAL-004" ;
        sk:title "Custom shapes validation" ;
        sk:given """
            A valid RDF file exists AND
            A custom SHACL shapes file exists AND
            The RDF file violates constraints in the shapes file
        """ ;
        sk:when "User runs 'specify validate <file> --shapes <shapes>'" ;
        sk:then """
            Command exits with code 1 AND
            Output includes shape constraint violation details
        """ ;
        sk:priority "should" ;
        sk:category "feature"
    ] .
```

### Priority Levels

```turtle
# MoSCoW prioritization in specifications
sk:must     rdfs:label "Must have" ;
            sk:description "Requirement is essential; system unusable without it" .

sk:should   rdfs:label "Should have" ;
            sk:description "Important but not essential; workarounds exist" .

sk:could    rdfs:label "Could have" ;
            sk:description "Desirable but not necessary; nice to have" .

sk:wont     rdfs:label "Won't have" ;
            sk:description "Explicitly excluded from current scope" .
```

---

## Test Generation

### SPARQL Extraction for Tests

```sparql
# sparql/acceptance-tests.rq
PREFIX sk: <https://spec-kit.org/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?command ?commandLabel ?criterionId ?title ?given ?when ?then ?priority ?category
WHERE {
    ?command a sk:Command ;
             rdfs:label ?commandLabel ;
             sk:hasAcceptanceCriterion ?criterion .

    ?criterion sk:id ?criterionId ;
               sk:given ?given ;
               sk:when ?when ;
               sk:then ?then .

    OPTIONAL { ?criterion sk:title ?title }
    OPTIONAL { ?criterion sk:priority ?priority }
    OPTIONAL { ?criterion sk:category ?category }
}
ORDER BY ?command ?criterionId
```

### Test Template

```jinja2
{# templates/acceptance-test.py.tera #}
"""Acceptance tests for {{ command_label }} command.

⚠️  AUTO-GENERATED FROM ACCEPTANCE CRITERIA  ⚠️

Source: ontology/cli-commands.ttl
Template: templates/acceptance-test.py.tera
Generated: {{ timestamp }}

These tests verify that the {{ command_label }} command meets its
acceptance criteria as defined in the specification. Do not edit
manually—update the specification and regenerate.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from specify_cli.app import app

runner = CliRunner()


class Test{{ command_label | pascal_case }}Command:
    """Acceptance tests for the {{ command_label }} command.

    Generated from acceptance criteria in cli-commands.ttl.
    Each test method corresponds to one acceptance criterion.
    """

{% for criterion in criteria %}
    def test_{{ criterion.id | snake_case }}(self, tmp_path):
        """
        {{ criterion.id }}: {{ criterion.title | default(criterion.id) }}

        Given: {{ criterion.given | wordwrap(70) | indent(15) }}
        When:  {{ criterion.when | wordwrap(70) | indent(15) }}
        Then:  {{ criterion.then | wordwrap(70) | indent(15) }}

        Priority: {{ criterion.priority | default("unspecified") }}
        Category: {{ criterion.category | default("general") }}
        """
        # ─────────────────────────────────────────────────────────────
        # Given
        # ─────────────────────────────────────────────────────────────
        {{ criterion | generate_given_section }}

        # ─────────────────────────────────────────────────────────────
        # When
        # ─────────────────────────────────────────────────────────────
        {{ criterion | generate_when_section }}

        # ─────────────────────────────────────────────────────────────
        # Then
        # ─────────────────────────────────────────────────────────────
        {{ criterion | generate_then_section }}

{% endfor %}
```

### Generated Test Example

```python
# tests/acceptance/test_validate_acceptance.py
"""Acceptance tests for validate command.

⚠️  AUTO-GENERATED FROM ACCEPTANCE CRITERIA  ⚠️

Source: ontology/cli-commands.ttl
Template: templates/acceptance-test.py.tera
Generated: 2025-01-15T10:30:00Z

These tests verify that the validate command meets its
acceptance criteria as defined in the specification.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from specify_cli.app import app

runner = CliRunner()


class TestValidateCommand:
    """Acceptance tests for the validate command.

    Generated from acceptance criteria in cli-commands.ttl.
    """

    def test_ac_val_001_valid_file_validation_succeeds(self, tmp_path):
        """
        AC-VAL-001: Valid file validation succeeds

        Given: A syntactically valid RDF/Turtle file exists at the
               specified path
        When:  User runs 'specify validate <path>'
        Then:  Command exits with code 0 and prints 'Valid ✓'

        Priority: must
        Category: success-path
        """
        # ─────────────────────────────────────────────────────────────
        # Given: A syntactically valid RDF/Turtle file exists
        # ─────────────────────────────────────────────────────────────
        valid_file = tmp_path / "valid.ttl"
        valid_file.write_text("""
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix ex: <http://example.org/> .

            ex:Person a rdfs:Class ;
                rdfs:label "Person" ;
                rdfs:comment "A human being" .
        """)

        # ─────────────────────────────────────────────────────────────
        # When: User runs 'specify validate <path>'
        # ─────────────────────────────────────────────────────────────
        result = runner.invoke(app, ["validate", str(valid_file)])

        # ─────────────────────────────────────────────────────────────
        # Then: Command exits with code 0 and prints 'Valid ✓'
        # ─────────────────────────────────────────────────────────────
        assert result.exit_code == 0, (
            f"Expected exit code 0, got {result.exit_code}. "
            f"Output: {result.output}"
        )
        assert "Valid" in result.output or "✓" in result.output, (
            f"Expected success indicator in output. Got: {result.output}"
        )

    def test_ac_val_002_invalid_file_validation_fails(self, tmp_path):
        """
        AC-VAL-002: Invalid file validation fails

        Given: A syntactically invalid RDF/Turtle file exists at the
               specified path
        When:  User runs 'specify validate <path>'
        Then:  Command exits with code 1 and prints error with line number

        Priority: must
        Category: error-path
        """
        # ─────────────────────────────────────────────────────────────
        # Given: A syntactically invalid RDF/Turtle file exists
        # ─────────────────────────────────────────────────────────────
        invalid_file = tmp_path / "invalid.ttl"
        invalid_file.write_text("""
            this is not valid turtle syntax
            @prefix missing closing bracket
            ex:incomplete ex:triple
        """)

        # ─────────────────────────────────────────────────────────────
        # When: User runs 'specify validate <path>'
        # ─────────────────────────────────────────────────────────────
        result = runner.invoke(app, ["validate", str(invalid_file)])

        # ─────────────────────────────────────────────────────────────
        # Then: Command exits with code 1 and prints error with line number
        # ─────────────────────────────────────────────────────────────
        assert result.exit_code == 1, (
            f"Expected exit code 1 for invalid file, got {result.exit_code}. "
            f"Output: {result.output}"
        )
        assert "line" in result.output.lower() or "error" in result.output.lower(), (
            f"Expected error message with line number. Got: {result.output}"
        )

    def test_ac_val_003_missing_file_handled_gracefully(self):
        """
        AC-VAL-003: Missing file handled gracefully

        Given: No file exists at the specified path
        When:  User runs 'specify validate <path>'
        Then:  Command exits with code 2 and prints 'File not found: <path>'

        Priority: must
        Category: error-path
        """
        # ─────────────────────────────────────────────────────────────
        # Given: No file exists at the specified path
        # ─────────────────────────────────────────────────────────────
        nonexistent_path = "/nonexistent/path/to/file.ttl"

        # ─────────────────────────────────────────────────────────────
        # When: User runs 'specify validate <path>'
        # ─────────────────────────────────────────────────────────────
        result = runner.invoke(app, ["validate", nonexistent_path])

        # ─────────────────────────────────────────────────────────────
        # Then: Command exits with code 2 and prints 'File not found'
        # ─────────────────────────────────────────────────────────────
        assert result.exit_code == 2, (
            f"Expected exit code 2 for missing file, got {result.exit_code}. "
            f"Output: {result.output}"
        )
        assert "not found" in result.output.lower() or "does not exist" in result.output.lower(), (
            f"Expected 'not found' message. Got: {result.output}"
        )
```

---

## The Discipline

### The Red-Green-Refactor Cycle

```
┌─────────────────────────────────────────────────────────────────────────┐
│  RED-GREEN-REFACTOR                                                      │
│                                                                          │
│                    ┌──────────────┐                                      │
│         ┌─────────▶│     RED      │◀─────────┐                          │
│         │          │  Tests fail  │          │                          │
│         │          └──────┬───────┘          │                          │
│         │                 │                  │                          │
│         │                 ▼                  │                          │
│         │          ┌──────────────┐          │                          │
│  Refactor          │    GREEN     │     Write/Update                    │
│         │          │  Tests pass  │       Test                          │
│         │          └──────┬───────┘          │                          │
│         │                 │                  │                          │
│         │                 ▼                  │                          │
│         │          ┌──────────────┐          │                          │
│         └──────────│   REFACTOR   │──────────┘                          │
│                    │ Clean up code│                                      │
│                    └──────────────┘                                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

**RED Phase:**
1. Generate test from acceptance criterion
2. Run test—it should fail (no implementation yet)
3. Verify it fails for the right reason (not syntax error)

**GREEN Phase:**
1. Write minimal code to make test pass
2. Run test—it should pass
3. Don't optimize yet—just make it work

**REFACTOR Phase:**
1. Clean up implementation
2. Remove duplication
3. Improve naming
4. Run tests—they should still pass

### The Workflow

```bash
# 1. Write specification (acceptance criteria)
vim ontology/cli-commands.ttl

# 2. Generate tests
ggen sync

# 3. Verify tests exist and fail (RED)
uv run pytest tests/acceptance/test_validate_acceptance.py -v
# Expected: FAILED (NotImplementedError or similar)

# 4. Implement (GREEN)
vim src/specify_cli/commands/validate.py
vim src/specify_cli/ops/validate.py

# 5. Run tests, iterate until passing
uv run pytest tests/acceptance/test_validate_acceptance.py -v
# Expected: PASSED

# 6. Refactor if needed
vim src/specify_cli/ops/validate.py

# 7. Final test run
uv run pytest tests/ -v

# 8. Commit together
git add ontology/ tests/ src/
git commit -m "feat(validate): implement validation per AC-VAL-001..003"
```

---

## Case Study: The Email Validator

*A team adopts test-before-code and discovers hidden requirements.*

### The Situation

The NotifyAPI team needed to add email validation to their user registration service. The initial requirement seemed simple:

> "Validate that email addresses are valid"

### The Traditional Approach (Before)

Without test-before-code, they would have written:

```python
def validate_email(email: str) -> bool:
    return "@" in email
```

Then written a test:

```python
def test_validate_email():
    assert validate_email("test@example.com") == True
    assert validate_email("invalid") == False
```

Ship it. Done.

### The Test-Before-Code Approach

They first wrote acceptance criteria:

```turtle
:email_validation sk:hasAcceptanceCriterion [
    sk:id "AC-EMAIL-001" ;
    sk:given "A string containing '@' with local and domain parts" ;
    sk:when "validate_email is called" ;
    sk:then "Returns True"
] .

:email_validation sk:hasAcceptanceCriterion [
    sk:id "AC-EMAIL-002" ;
    sk:given "A string without '@'" ;
    sk:when "validate_email is called" ;
    sk:then "Returns False"
] .
```

When writing these criteria, they asked: "What else makes an email valid?"

This led to more criteria:

```turtle
# What about empty strings?
:email_validation sk:hasAcceptanceCriterion [
    sk:id "AC-EMAIL-003" ;
    sk:given "An empty string" ;
    sk:when "validate_email is called" ;
    sk:then "Returns False"
] .

# What about multiple @?
:email_validation sk:hasAcceptanceCriterion [
    sk:id "AC-EMAIL-004" ;
    sk:given "A string with multiple '@' characters" ;
    sk:when "validate_email is called" ;
    sk:then "Returns False"
] .

# What about special characters?
:email_validation sk:hasAcceptanceCriterion [
    sk:id "AC-EMAIL-005" ;
    sk:given "A string with valid special characters (+, -, .)" ;
    sk:when "validate_email is called with 'user+tag@example.com'" ;
    sk:then "Returns True"
] .

# What about case sensitivity?
:email_validation sk:hasAcceptanceCriterion [
    sk:id "AC-EMAIL-006" ;
    sk:given "An email in mixed case" ;
    sk:when "validate_email is called with 'User@Example.COM'" ;
    sk:then "Returns True (email local part is case-sensitive, domain is not)"
] .

# What about internationalized emails?
:email_validation sk:hasAcceptanceCriterion [
    sk:id "AC-EMAIL-007" ;
    sk:given "An internationalized email address" ;
    sk:when "validate_email is called with 'пользователь@пример.рф'" ;
    sk:then "Returns True (IDN support)"
] .
```

### The Discovery

By writing acceptance criteria first, they discovered:
- **7 edge cases** they hadn't considered
- **Internationalization requirements** nobody mentioned
- **RFC 5321 compliance** questions
- **Business rules** about what emails to accept

The tests were generated:

```python
def test_ac_email_001_valid_email_with_at(self):
    assert validate_email("test@example.com") == True

def test_ac_email_002_invalid_without_at(self):
    assert validate_email("invalid") == False

def test_ac_email_003_empty_string_rejected(self):
    assert validate_email("") == False

def test_ac_email_004_multiple_at_rejected(self):
    assert validate_email("a@b@c.com") == False

def test_ac_email_005_special_chars_accepted(self):
    assert validate_email("user+tag@example.com") == True

def test_ac_email_006_mixed_case_accepted(self):
    assert validate_email("User@Example.COM") == True

def test_ac_email_007_international_accepted(self):
    assert validate_email("пользователь@пример.рф") == True
```

### The Implementation

Now they knew what to build. The implementation was more thorough:

```python
import re
import idna

def validate_email(email: str) -> bool:
    """Validate email per RFC 5321 with IDN support."""
    if not email:
        return False

    if email.count("@") != 1:
        return False

    local, domain = email.split("@")

    if not local or not domain:
        return False

    # Try to encode domain (handles IDN)
    try:
        idna.encode(domain)
    except idna.IDNAError:
        return False

    return True
```

### The Results

| Metric | Without Test-First | With Test-First |
|--------|-------------------|-----------------|
| Edge cases caught before release | 2 | 7 |
| Bugs found in production | 5 | 0 |
| Requirements clarified | After release | Before coding |
| Time to stable implementation | 3 weeks | 1 week |

Test-before-code forced them to think through requirements before coding. The time "lost" writing tests was recovered many times over in reduced debugging and rework.

---

## Anti-Patterns

### Anti-Pattern: Test-After Encoding

*"We write tests after the code to make sure it works."*

Tests written after implementation often test what was built, not what should have been built. They encode implementation decisions rather than requirements.

**Resolution:** Generate tests from specifications before implementation. Tests should express requirements, not echo implementation.

### Anti-Pattern: Testing Implementation

*"Our tests verify each method behaves correctly."*

Unit tests for internal methods couple tests to implementation. Refactoring breaks tests even when behavior is unchanged.

**Resolution:** Test behavior (acceptance criteria), not implementation. Test the public interface, not internal methods.

### Anti-Pattern: Manual Test Writing

*"We hand-write each test case."*

Manual test writing is slow, inconsistent, and easily incomplete. Tests may not cover all acceptance criteria.

**Resolution:** Generate tests from specifications. Every criterion gets a test. Templates ensure consistency.

### Anti-Pattern: Skipping Red

*"The test passes immediately—great!"*

If a new test passes immediately, either the feature already exists (which is fine) or the test doesn't test what you think (which is bad).

**Resolution:** Always verify new tests fail before implementation. The RED phase confirms the test tests the right thing.

### Anti-Pattern: Gold-Plating

*"Let me add extra test coverage while I'm here."*

Adding tests beyond acceptance criteria conflates requirement verification with exploratory testing. Extra tests may test implementation details.

**Resolution:** Keep acceptance tests focused on criteria. Add exploratory tests in a separate test suite with different maintenance expectations.

---

## Configuration

### Test Generation Configuration

```toml
# ggen.toml

[[targets]]
source = "ontology/cli-commands.ttl"
query = "sparql/acceptance-tests.rq"
template = "templates/acceptance-test.py.tera"
output = "tests/acceptance/test_{{ command | snake_case }}_acceptance.py"

[targets.options]
# Generate test class per command
group_by = "command"

# Skip criteria marked as "wont"
filter = "priority != 'wont'"

# Include setup/teardown helpers
include_fixtures = true
```

### pytest Configuration

```toml
# pyproject.toml

[tool.pytest.ini_options]
markers = [
    "acceptance: Acceptance tests from specifications",
    "must: Must-have requirements",
    "should: Should-have requirements",
    "could: Could-have requirements",
]

testpaths = ["tests"]

# Run acceptance tests by priority
addopts = "-m 'acceptance and must' --tb=short"
```

---

## Implementation Checklist

### Specification

- [ ] Define acceptance criteria in RDF
- [ ] Use Given-When-Then format
- [ ] Assign IDs to criteria
- [ ] Set priorities (must/should/could)
- [ ] Categorize criteria (success/error/feature)

### Test Generation

- [ ] Create SPARQL query for criteria extraction
- [ ] Create test template
- [ ] Configure ggen.toml target
- [ ] Generate tests with `ggen sync`
- [ ] Verify test file structure

### Discipline

- [ ] Run tests before implementation (RED)
- [ ] Verify tests fail for the right reason
- [ ] Implement minimum to pass (GREEN)
- [ ] Run tests after implementation
- [ ] Refactor if needed
- [ ] Commit specification + tests + code together

### Coverage

- [ ] Every "must" criterion has a test
- [ ] Every "should" criterion has a test
- [ ] Tests run in CI
- [ ] Failed tests block merge

---

## Exercises

### Exercise 1: Write Acceptance Criteria

Given this requirement: "The `check` command verifies that required tools are installed"

Write acceptance criteria in RDF covering:
- All tools installed → success
- Some tools missing → list missing tools
- No tools installed → helpful error message

### Exercise 2: Generate Tests

Using your criteria from Exercise 1:
1. Write a SPARQL query to extract criteria
2. Create a test template
3. Generate test file
4. Verify tests fail (no implementation)

### Exercise 3: Implement

1. Take the failing tests from Exercise 2
2. Implement the `check` command
3. Make tests pass
4. Refactor for clarity
5. Verify tests still pass

### Exercise 4: Discover Requirements

Choose a feature in your project. Write acceptance criteria for it.

Questions to ask:
- What happens with valid input?
- What happens with invalid input?
- What happens with missing input?
- What are the edge cases?
- What error messages should appear?

Count how many requirements you discover through this process.

---

## Resulting Context

After implementing this pattern, you have:

- **Tests that define expected behavior** before implementation exists
- **Implementation that provably meets acceptance criteria** by making tests pass
- **Traceability from tests to criteria** through IDs and documentation
- **Confidence that what was built matches what was specified** because tests come from specifications
- **Forced requirement clarity** because unclear requirements can't become tests

Test Before Code transforms implementation from "writing code" to "making tests pass." The tests become the executable specification—the authoritative definition of what the system should do.

---

## Code References

The following spec-kit source files implement test-before-code concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/spec-kit-schema.ttl:40-60` | AcceptanceScenario class that generates tests |
| `ontology/spec-kit-schema.ttl:584-617` | AcceptanceScenarioShape validating Given/When/Then |
| `templates/command.tera` | Template that could generate test scaffolding |

---

## Related Patterns

- **Implements:** **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria become tests
- **Part of:** **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Tests are generated artifacts
- **Enables:** **[37. Continuous Validation](./continuous-validation.md)** — Tests run in CI
- **Supports:** **[32. Contract Test](./contract-test.md)** — Interface contracts verified

---

## Philosophical Note

> *"If you can't write a test for it, you don't understand it well enough to build it."*

Test Before Code forces understanding before implementation. Writing a test requires knowing:
- What inputs the system accepts
- What outputs it produces
- What errors it reports
- What edge cases exist

This knowledge must exist before coding begins. If you can't express the requirement as a test, you don't understand the requirement well enough to implement it correctly.

The discipline feels constraining at first. "Just let me write the code!" But the constraint is valuable—it prevents building the wrong thing. A few minutes spent writing acceptance criteria and generating tests saves hours of debugging and rework.

In specification-driven development, the discipline becomes natural. Specifications *are* requirements. Tests *are* executable specifications. Implementation *is* making tests pass. The sequence isn't artificial—it's the logical flow from intent to verification to realization.

---

**Next:** Learn how **[32. Contract Test](./contract-test.md)** verifies that implementations honor their interface contracts.
