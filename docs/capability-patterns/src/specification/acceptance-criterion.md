# 19. Acceptance Criterion

★★

*How do you know when something is done? Acceptance criteria define the boundary between incomplete and complete, providing concrete, testable conditions for success. They are the contract that eliminates ambiguity and makes "done" unambiguous.*

---

## The Problem of "Done"

You've specified *what* to build. The formal specification describes the structure, the narrative explains the intent. But when is it built? What conditions must be satisfied for the capability to be considered complete?

Without explicit acceptance criteria, "done" becomes a matter of opinion:

**The Developer says:** "It works!"
**The Tester asks:** "For whom? Under what conditions?"
**The Product Manager wonders:** "Does it actually solve the customer's problem?"
**The Customer complains:** "This isn't what I asked for."

Everyone has a different mental model of "done." The specification says what to build, but not how to verify it's built correctly. This gap leads to:

- **Scope creep**: "Just one more thing" because boundaries aren't clear
- **Arguments**: "We said X" / "No, you said Y"
- **Rework**: Building the wrong thing, then rebuilding
- **Lingering incompleteness**: Features that are "almost done" forever
- **Customer disappointment**: Meeting spec but missing intent

---

## The Problem Statement

**Without explicit acceptance criteria, "done" is undefined. Scope creeps, arguments arise, and capabilities linger in eternal incompleteness or are declared done prematurely.**

The symptoms of missing acceptance criteria:
- **Ambiguous completion**: Nobody agrees when something is finished
- **Moving targets**: Requirements change mid-implementation
- **Untestable features**: No way to verify correctness
- **Customer surprises**: Delivered functionality doesn't match expectations
- **Technical debt**: "Good enough" becomes permanent

---

## The Forces at Play

### Force 1: Completeness vs. Practicality

**Completeness wants all cases covered.** Every edge case, every scenario, every combination. If it could happen, test for it.

**Practicality wants focus.** Not everything matters equally. Some scenarios are rare. Some edge cases are theoretical. Testing everything takes forever.

```
Completeness ←───────────────────────────→ Practicality
(test everything)                          (test what matters)
```

### Force 2: Specificity vs. Flexibility

**Specificity wants precision.** "Returns in < 100ms" is testable. "Works well" is not. Specific criteria leave no room for interpretation.

**Flexibility wants room.** Over-specification constrains creative solutions. Sometimes the path to a goal matters less than reaching it.

```
Specificity ←────────────────────────────→ Flexibility
(exact requirements)                       (solution freedom)
```

### Force 3: Stability vs. Discovery

**Stability wants upfront definition.** Know what done looks like before starting. No surprises. Clear contract.

**Discovery wants evolution.** Understanding deepens during implementation. Early criteria may be wrong. Allow learning.

```
Stability ←──────────────────────────────→ Discovery
(define before build)                      (learn while building)
```

### Force 4: Customer vs. Technical

**Customer perspective wants outcomes.** "I can validate my files quickly" matters. Internal implementation doesn't.

**Technical perspective wants behavior.** "Returns exit code 0" is testable. "User feels confident" isn't.

```
Customer View ←──────────────────────────→ Technical View
(outcome-focused)                          (behavior-focused)
```

---

## Therefore: Define Explicit Acceptance Criteria

**For each capability, define explicit acceptance criteria using the Given-When-Then format, encoded in RDF for traceability and automated test generation.**

Acceptance criteria bridge the gap between specification and verification. They translate abstract requirements into concrete, testable conditions.

### The Given-When-Then Structure

The Gherkin syntax provides a clear pattern for expressing criteria:

```
Given [precondition/context]
  - What state must exist before the action?
  - What assumptions are we making?

When [action/trigger]
  - What action does the user take?
  - What event triggers the behavior?

Then [expected outcome/postcondition]
  - What should happen?
  - What state should result?
```

This structure forces clarity:
- **Given** makes context explicit
- **When** specifies the exact trigger
- **Then** defines observable outcomes

---

## Acceptance Criteria in RDF

### The Acceptance Criterion Ontology

```turtle
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix ac: <https://spec-kit.io/ontology/acceptance#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Core class
ac:AcceptanceCriterion a rdfs:Class ;
    rdfs:label "Acceptance Criterion" ;
    rdfs:comment """
        A testable condition that must be satisfied for a
        capability to be considered complete.
    """ .

# Criterion components
ac:given a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range xsd:string ;
    rdfs:comment "Precondition that must be true before testing" .

ac:when a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range xsd:string ;
    rdfs:comment "Action or trigger being tested" .

ac:then a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range xsd:string ;
    rdfs:comment "Expected outcome after action" .

# Metadata
ac:identifier a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range xsd:string ;
    rdfs:comment "Unique identifier (e.g., AC-VAL-001)" .

ac:priority a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range ac:Priority ;
    rdfs:comment "Importance of this criterion" .

# Priority enumeration (MoSCoW)
ac:Priority a rdfs:Class ;
    rdfs:comment "Priority levels for acceptance criteria" .

ac:Must a ac:Priority ;
    rdfs:label "Must" ;
    rdfs:comment "Required for acceptance. Without this, capability is incomplete." .

ac:Should a ac:Priority ;
    rdfs:label "Should" ;
    rdfs:comment "Expected but negotiable. Missing degrades quality." .

ac:Could a ac:Priority ;
    rdfs:label "Could" ;
    rdfs:comment "Nice to have. Missing is acceptable." .

ac:Wont a ac:Priority ;
    rdfs:label "Won't" ;
    rdfs:comment "Explicitly out of scope. Documents boundaries." .

# Categories
ac:Category a rdfs:Class .

ac:Functional a ac:Category ;
    rdfs:label "Functional" ;
    rdfs:comment "What the capability does" .

ac:Performance a ac:Category ;
    rdfs:label "Performance" ;
    rdfs:comment "How fast/efficient it is" .

ac:Usability a ac:Category ;
    rdfs:label "Usability" ;
    rdfs:comment "How easy to use" .

ac:Security a ac:Category ;
    rdfs:label "Security" ;
    rdfs:comment "How safe it is" .

ac:Compatibility a ac:Category ;
    rdfs:label "Compatibility" ;
    rdfs:comment "What it works with" .

ac:Reliability a ac:Category ;
    rdfs:label "Reliability" ;
    rdfs:comment "How consistently it works" .

ac:category a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range ac:Category .

# Traceability
ac:addresses a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range jtbd:Outcome ;
    rdfs:comment "Links criterion to the outcome it verifies" .

ac:measurable a rdf:Property ;
    rdfs:domain ac:AcceptanceCriterion ;
    rdfs:range xsd:boolean ;
    rdfs:comment "Whether the outcome can be objectively measured" .
```

### Comprehensive Example

```turtle
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix ac: <https://spec-kit.io/ontology/acceptance#> .
@prefix jtbd: <https://spec-kit.io/ontology/jtbd#> .
@prefix sk: <https://spec-kit.io/ontology#> .

# The command being specified
cli:ValidateCommand a cli:Command ;
    sk:name "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;

    # ═══════════════════════════════════════════════════════════════
    # FUNCTIONAL CRITERIA (Must Have)
    # ═══════════════════════════════════════════════════════════════

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-001" ;
        ac:category ac:Functional ;
        ac:priority ac:Must ;
        ac:given "A syntactically valid RDF/Turtle file exists" ;
        ac:when "User runs 'specify validate file.ttl'" ;
        ac:then "Command exits with code 0 and prints 'Valid ✓'" ;
        ac:addresses jtbd:EnsureCorrectRDF ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-002" ;
        ac:category ac:Functional ;
        ac:priority ac:Must ;
        ac:given "A file with RDF syntax errors exists" ;
        ac:when "User runs 'specify validate invalid.ttl'" ;
        ac:then """
            Command exits with non-zero code and prints error
            message including line number and description
        """ ;
        ac:addresses jtbd:IdentifyErrors ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-003" ;
        ac:category ac:Functional ;
        ac:priority ac:Must ;
        ac:given "Valid RDF file and SHACL shapes file exist" ;
        ac:when "User runs 'specify validate data.ttl --shapes shapes.ttl'" ;
        ac:then """
            Command validates RDF against shapes and reports
            any shape violations with affected node and property
        """ ;
        ac:addresses jtbd:ValidateAgainstShapes ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-004" ;
        ac:category ac:Functional ;
        ac:priority ac:Must ;
        ac:given "File path does not exist" ;
        ac:when "User runs 'specify validate nonexistent.ttl'" ;
        ac:then """
            Command exits with code 2 and prints
            'Error: File not found: nonexistent.ttl'
        """ ;
        ac:addresses jtbd:ClearErrorHandling ;
        ac:measurable true
    ] ;

    # ═══════════════════════════════════════════════════════════════
    # PERFORMANCE CRITERIA (Should Have)
    # ═══════════════════════════════════════════════════════════════

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-010" ;
        ac:category ac:Performance ;
        ac:priority ac:Should ;
        ac:given "A valid RDF file smaller than 1MB exists" ;
        ac:when "User runs validate on the file" ;
        ac:then "Command completes in less than 1 second" ;
        ac:addresses jtbd:MinimizeValidationTime ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-011" ;
        ac:category ac:Performance ;
        ac:priority ac:Should ;
        ac:given "A valid RDF file of 100MB exists" ;
        ac:when "User runs validate on the file" ;
        ac:then "Peak memory usage stays below 200MB" ;
        ac:addresses jtbd:HandleLargeFiles ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-012" ;
        ac:category ac:Performance ;
        ac:priority ac:Should ;
        ac:given "100 RDF files totaling 10MB exist" ;
        ac:when "User runs 'specify validate *.ttl'" ;
        ac:then "All files are validated in under 10 seconds" ;
        ac:addresses jtbd:BatchValidation ;
        ac:measurable true
    ] ;

    # ═══════════════════════════════════════════════════════════════
    # USABILITY CRITERIA (Should Have)
    # ═══════════════════════════════════════════════════════════════

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-020" ;
        ac:category ac:Usability ;
        ac:priority ac:Should ;
        ac:given "User is new to the tool" ;
        ac:when "User runs 'specify validate --help'" ;
        ac:then """
            Help text displays:
            - Command description
            - All arguments with types
            - All options with defaults
            - At least one example
        """ ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-021" ;
        ac:category ac:Usability ;
        ac:priority ac:Should ;
        ac:given "Terminal supports colors" ;
        ac:when "Validation succeeds" ;
        ac:then "Success message is displayed in green" ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-022" ;
        ac:category ac:Usability ;
        ac:priority ac:Should ;
        ac:given "Terminal supports colors" ;
        ac:when "Validation fails" ;
        ac:then "Error messages are displayed in red" ;
        ac:measurable true
    ] ;

    # ═══════════════════════════════════════════════════════════════
    # COMPATIBILITY CRITERIA (Could Have)
    # ═══════════════════════════════════════════════════════════════

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-030" ;
        ac:category ac:Compatibility ;
        ac:priority ac:Could ;
        ac:given "User is on Windows, macOS, or Linux" ;
        ac:when "User runs the validate command" ;
        ac:then "Command functions identically on all platforms" ;
        ac:measurable true
    ] ;

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-031" ;
        ac:category ac:Compatibility ;
        ac:priority ac:Could ;
        ac:given "RDF file uses N-Triples format" ;
        ac:when "User runs 'specify validate file.nt'" ;
        ac:then "Command auto-detects format and validates successfully" ;
        ac:measurable true
    ] ;

    # ═══════════════════════════════════════════════════════════════
    # EXPLICITLY OUT OF SCOPE (Won't Have)
    # ═══════════════════════════════════════════════════════════════

    cli:hasAcceptanceCriterion [
        a ac:AcceptanceCriterion ;
        ac:identifier "AC-VAL-099" ;
        ac:category ac:Functional ;
        ac:priority ac:Wont ;
        ac:given "User wants to validate remote URL" ;
        ac:when "User runs 'specify validate http://example.org/file.ttl'" ;
        ac:then """
            Not supported in this version. Error message explains
            that remote URLs are not supported and suggests using
            curl/wget first.
        """ ;
        rdfs:comment """
            Remote validation deferred due to security concerns
            (SSRF) and performance unpredictability. May revisit
            in future version with proper safeguards.
        """
    ] .
```

---

## Linking Criteria to Outcomes

Acceptance criteria should trace back to customer outcomes:

```turtle
# Job outcome
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    jtbd:direction "minimize" ;
    jtbd:metric "seconds" ;
    jtbd:object "time to validate RDF file" ;
    sk:description "Validate files quickly so it can be part of development flow" .

# Criterion addresses outcome
ac:AC-VAL-010
    ac:addresses jtbd:MinimizeValidationTime ;
    ac:measurable true ;
    ac:threshold "1 second" ;
    ac:baseline "5 seconds (previous tool)" .
```

This creates a **[Traceability Thread](./traceability-thread.md)**:

```
Customer Need: "I need fast validation"
    │
    ▼
Job: Validate RDF syntax and shapes
    │
    ▼
Outcome: Minimize time to validate
    │
    ▼
Criterion: AC-VAL-010 (< 1 second for < 1MB)
    │
    ▼
Test: test_validate_performance_small_file()
    │
    ▼
Implementation: validate command with streaming
```

---

## Generating Tests from Criteria

### SPARQL Query for Test Generation

```sparql
PREFIX cli: <https://spec-kit.io/ontology/cli#>
PREFIX ac: <https://spec-kit.io/ontology/acceptance#>

SELECT ?id ?given ?when ?then ?priority ?category
WHERE {
    ?cmd a cli:Command ;
         cli:hasAcceptanceCriterion ?criterion .

    ?criterion ac:identifier ?id ;
               ac:given ?given ;
               ac:when ?when ;
               ac:then ?then ;
               ac:priority ?priority .

    OPTIONAL { ?criterion ac:category ?category }

    # Only Must and Should for automated tests
    FILTER (?priority IN (ac:Must, ac:Should))
}
ORDER BY ?id
```

### Test Template

```jinja
{# templates/acceptance-test.tera #}
"""
Acceptance tests generated from specifications.
DO NOT EDIT - regenerate from RDF source.
"""
import pytest
from click.testing import CliRunner
from specify_cli import app

{% for criterion in criteria %}

class Test{{ criterion.id | replace("-", "_") }}:
    """
    {{ criterion.id }}: {{ criterion.category }}

    Given: {{ criterion.given }}
    When: {{ criterion.when }}
    Then: {{ criterion.then }}

    Priority: {{ criterion.priority }}
    {% if criterion.addresses %}
    Addresses: {{ criterion.addresses }}
    {% endif %}
    """

    def test_acceptance(self, {% if criterion.fixtures %}{{ criterion.fixtures }}{% endif %}):
        # Given
        {{ criterion.given_code | default("pass  # TODO: Set up precondition") }}

        # When
        {{ criterion.when_code | default("result = None  # TODO: Execute action") }}

        # Then
        {{ criterion.then_code | default("assert True  # TODO: Verify outcome") }}

{% endfor %}
```

### Generated Test

```python
"""
Acceptance tests generated from specifications.
DO NOT EDIT - regenerate from RDF source.
"""
import pytest
from click.testing import CliRunner
from specify_cli import app


class Test_AC_VAL_001:
    """
    AC-VAL-001: Functional

    Given: A syntactically valid RDF/Turtle file exists
    When: User runs 'specify validate file.ttl'
    Then: Command exits with code 0 and prints 'Valid ✓'

    Priority: Must
    Addresses: EnsureCorrectRDF
    """

    def test_acceptance(self, valid_ttl_file):
        # Given
        # (provided by valid_ttl_file fixture)

        # When
        runner = CliRunner()
        result = runner.invoke(app, ["validate", str(valid_ttl_file)])

        # Then
        assert result.exit_code == 0
        assert "Valid ✓" in result.output


class Test_AC_VAL_002:
    """
    AC-VAL-002: Functional

    Given: A file with RDF syntax errors exists
    When: User runs 'specify validate invalid.ttl'
    Then: Command exits with non-zero code and prints error
          message including line number and description

    Priority: Must
    Addresses: IdentifyErrors
    """

    def test_acceptance(self, invalid_ttl_file):
        # Given
        # (provided by invalid_ttl_file fixture)

        # When
        runner = CliRunner()
        result = runner.invoke(app, ["validate", str(invalid_ttl_file)])

        # Then
        assert result.exit_code != 0
        assert "line" in result.output.lower()
        assert "error" in result.output.lower()


class Test_AC_VAL_010:
    """
    AC-VAL-010: Performance

    Given: A valid RDF file smaller than 1MB exists
    When: User runs validate on the file
    Then: Command completes in less than 1 second

    Priority: Should
    Addresses: MinimizeValidationTime
    """

    def test_acceptance(self, small_valid_ttl_file):
        import time

        # Given
        # (provided by small_valid_ttl_file fixture - < 1MB)

        # When
        runner = CliRunner()
        start = time.perf_counter()
        result = runner.invoke(app, ["validate", str(small_valid_ttl_file)])
        elapsed = time.perf_counter() - start

        # Then
        assert result.exit_code == 0
        assert elapsed < 1.0, f"Validation took {elapsed:.2f}s, expected < 1s"
```

---

## Writing Good Acceptance Criteria

### Principle 1: One Criterion, One Condition

Each criterion should test one specific thing:

```turtle
# BAD: Multiple conditions in one criterion
ac:given "Valid file exists" ;
ac:when "User validates" ;
ac:then """
    Exits 0, prints Valid, completes in < 1s,
    uses < 100MB memory, writes no temp files
""" .

# GOOD: Separate criteria for each condition
# AC-VAL-001: Functional - exit code
ac:then "Exits with code 0" .

# AC-VAL-002: Functional - output
ac:then "Prints 'Valid ✓'" .

# AC-VAL-010: Performance - time
ac:then "Completes in < 1 second" .

# AC-VAL-011: Performance - memory
ac:then "Uses < 100MB memory" .
```

### Principle 2: Observable Outcomes

Criteria must describe something you can see or measure:

```turtle
# BAD: Internal state (not observable)
ac:then "Internal validation flag is set to true" .

# BAD: Subjective (not measurable)
ac:then "User feels confident about their file" .

# GOOD: Observable behavior
ac:then "Command prints 'Valid ✓' to stdout" .

# GOOD: Measurable outcome
ac:then "Command completes in < 1 second" .
```

### Principle 3: No Implementation Details

Criteria should specify *what*, not *how*:

```turtle
# BAD: Implementation detail
ac:then "Command uses RDF4J library to parse Turtle" .

# BAD: Internal structure
ac:then "Validation result stored in ValidationResult object" .

# GOOD: External behavior
ac:then "Command correctly identifies all syntax errors" .
```

### Principle 4: Edge Cases Matter

Include failure modes and boundaries:

```turtle
# Happy path
ac:AC-VAL-001
    ac:given "Valid file" ;
    ac:when "Validate" ;
    ac:then "Success" .

# Error case: Missing file
ac:AC-VAL-004
    ac:given "File does not exist" ;
    ac:when "Validate" ;
    ac:then "Clear error message" .

# Error case: Permission denied
ac:AC-VAL-005
    ac:given "File exists but is not readable" ;
    ac:when "Validate" ;
    ac:then "Permission error message" .

# Boundary: Empty file
ac:AC-VAL-006
    ac:given "File exists but is empty" ;
    ac:when "Validate" ;
    ac:then "Valid (empty graph is valid RDF)" .

# Boundary: Very large file
ac:AC-VAL-011
    ac:given "100MB file" ;
    ac:when "Validate" ;
    ac:then "Completes without memory error" .
```

### Principle 5: Realistic Scenarios

Base criteria on actual use cases:

```turtle
# BAD: Contrived scenario
ac:given "User has exactly 17 files with prime-number line counts" .

# GOOD: Real-world scenario
ac:given "User has modified ontology.ttl and wants to validate before commit" .
```

---

## Priority Levels (MoSCoW)

### Must

**Required for acceptance.** Without this, the capability is incomplete and should not ship.

```turtle
ac:AC-VAL-001 ac:priority ac:Must ;
    ac:given "Valid file" ;
    ac:when "Validate" ;
    ac:then "Reports valid" .

ac:AC-VAL-002 ac:priority ac:Must ;
    ac:given "Invalid file" ;
    ac:when "Validate" ;
    ac:then "Reports errors with line numbers" .
```

Use Must for:
- Core functionality
- Safety requirements
- Contractual obligations
- Legal/regulatory requirements

### Should

**Expected but negotiable.** Missing this degrades quality but doesn't block release.

```turtle
ac:AC-VAL-010 ac:priority ac:Should ;
    ac:given "Small file" ;
    ac:when "Validate" ;
    ac:then "Completes in < 1s" .
```

Use Should for:
- Performance targets
- Quality-of-life features
- Expected behaviors

### Could

**Nice to have.** Missing this is acceptable.

```turtle
ac:AC-VAL-030 ac:priority ac:Could ;
    ac:given "N-Triples format file" ;
    ac:when "Validate" ;
    ac:then "Auto-detects format" .
```

Use Could for:
- Convenience features
- Minor enhancements
- "Cherry on top" items

### Won't

**Explicitly out of scope.** Documents boundaries.

```turtle
ac:AC-VAL-099 ac:priority ac:Wont ;
    ac:given "Remote URL" ;
    ac:when "Validate" ;
    ac:then "Not supported (explains why)" .
```

Use Won't for:
- Deferred features
- Out-of-scope requests
- Things explicitly not supported

---

## Validating Criteria with SHACL

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ac: <https://spec-kit.io/ontology/acceptance#> .
@prefix cli: <https://spec-kit.io/ontology/cli#> .

# Commands must have acceptance criteria
cli:CommandAcceptanceShape a sh:NodeShape ;
    sh:targetClass cli:Command ;

    sh:property [
        sh:path cli:hasAcceptanceCriterion ;
        sh:minCount 1 ;
        sh:message "Commands must have at least one acceptance criterion"
    ] .

# Criteria must have required fields
ac:AcceptanceCriterionShape a sh:NodeShape ;
    sh:targetClass ac:AcceptanceCriterion ;

    sh:property [
        sh:path ac:identifier ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:pattern "^AC-[A-Z]+-[0-9]+$" ;
        sh:message "Criterion must have identifier matching AC-XXX-NNN"
    ] ;

    sh:property [
        sh:path ac:given ;
        sh:minCount 1 ;
        sh:minLength 10 ;
        sh:message "Criterion must have Given clause (min 10 chars)"
    ] ;

    sh:property [
        sh:path ac:when ;
        sh:minCount 1 ;
        sh:minLength 10 ;
        sh:message "Criterion must have When clause (min 10 chars)"
    ] ;

    sh:property [
        sh:path ac:then ;
        sh:minCount 1 ;
        sh:minLength 10 ;
        sh:message "Criterion must have Then clause (min 10 chars)"
    ] ;

    sh:property [
        sh:path ac:priority ;
        sh:minCount 1 ;
        sh:in (ac:Must ac:Should ac:Could ac:Wont) ;
        sh:message "Criterion must have priority (Must/Should/Could/Wont)"
    ] .

# Must-priority criteria should link to outcomes
ac:MustCriterionTraceabilityShape a sh:NodeShape ;
    sh:target [
        a sh:SPARQLTarget ;
        sh:select """
            SELECT ?this WHERE {
                ?this a ac:AcceptanceCriterion ;
                      ac:priority ac:Must .
            }
        """
    ] ;
    sh:severity sh:Warning ;
    sh:property [
        sh:path ac:addresses ;
        sh:minCount 1 ;
        sh:message "Must-priority criteria should link to outcomes for traceability"
    ] .
```

---

## Case Study: The Unclear Done

### The Problem

A team builds a "search" feature. The specification says:

```turtle
cli:SearchCommand a cli:Command ;
    sk:name "search" ;
    sk:description "Search for entities in specifications" .
```

After 3 weeks of development, stakeholders review:

- **Developer**: "Search is done! It finds entities."
- **Tester**: "I found cases where it misses results."
- **Product Manager**: "It's too slow for large datasets."
- **Customer**: "I wanted fuzzy search, not exact match."

Everyone is frustrated. The spec was met, but nobody is happy.

### The Solution

The team writes explicit acceptance criteria:

```turtle
cli:SearchCommand cli:hasAcceptanceCriterion [
    ac:identifier "AC-SEARCH-001" ;
    ac:priority ac:Must ;
    ac:given "Ontology contains entity with name 'Validate'" ;
    ac:when "User runs 'specify search validate'" ;
    ac:then "Results include the Validate entity"
] ;

cli:hasAcceptanceCriterion [
    ac:identifier "AC-SEARCH-002" ;
    ac:priority ac:Must ;
    ac:given "Ontology contains 'validate' and 'Validator'" ;
    ac:when "User runs 'specify search valid'" ;
    ac:then "Results include both (prefix matching)"
] ;

cli:hasAcceptanceCriterion [
    ac:identifier "AC-SEARCH-003" ;
    ac:priority ac:Should ;
    ac:given "User misspells search term" ;
    ac:when "User runs 'specify search valiate'" ;
    ac:then "Results suggest 'validate' (fuzzy matching)"
] ;

cli:hasAcceptanceCriterion [
    ac:identifier "AC-SEARCH-010" ;
    ac:priority ac:Should ;
    ac:given "Ontology has 100,000 entities" ;
    ac:when "User runs search" ;
    ac:then "Results return in < 500ms"
] .
```

### The Outcome

With explicit criteria:
- Developer knows exactly what to build
- Tester has clear test cases
- Product Manager can prioritize (fuzzy = Should, not Must)
- Customer expectations are aligned before development

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Vague Criteria

```turtle
# BAD: Not testable
ac:then "Works correctly" .
ac:then "Performs well" .
ac:then "Is user-friendly" .
```

### Anti-Pattern 2: Implementation-Focused

```turtle
# BAD: Specifies how, not what
ac:then "Uses binary search algorithm for performance" .
ac:then "Caches results in Redis" .
```

### Anti-Pattern 3: Untestable Criteria

```turtle
# BAD: Can't be automatically tested
ac:then "User is delighted" .
ac:then "Code is maintainable" .
ac:then "System is scalable" .
```

### Anti-Pattern 4: Missing Edge Cases

```turtle
# BAD: Only happy path
ac:AC-001 ac:then "Valid file validates" .
# What about invalid files? Missing files? Large files? Empty files?
```

### Anti-Pattern 5: Unstable Criteria

```turtle
# BAD: Changes during development
Week 1: ac:then "Completes in < 1s"
Week 2: ac:then "Completes in < 5s"  # Team couldn't hit target
Week 3: ac:then "Completes in reasonable time"  # Gave up
```

---

## Implementation Checklist

### Writing Criteria

- [ ] One condition per criterion
- [ ] All criteria have unique identifiers
- [ ] Given-When-Then format for all criteria
- [ ] Priority assigned (Must/Should/Could/Won't)
- [ ] Observable, measurable outcomes
- [ ] Edge cases and error paths included

### Validating Criteria

- [ ] SHACL shapes enforce structure
- [ ] Must criteria link to outcomes
- [ ] All criteria are testable
- [ ] No implementation details in criteria

### Using Criteria

- [ ] Generate tests from criteria
- [ ] Review criteria before implementation
- [ ] Update criteria when requirements change
- [ ] Track completion by priority

---

## Resulting Context

After applying this pattern, you have:

- **Concrete definition of "done"** for each capability
- **Testable conditions** that can be automated
- **Clear priority** to guide implementation effort
- **Traceable links** from criteria to outcomes
- **Shared understanding** between stakeholders
- **Reduced arguments** about completeness

This enables **[Test Before Code](../verification/test-before-code.md)** and supports **[Outcome Measurement](../evolution/outcome-measurement.md)**.

---

## Code References

The following spec-kit source files implement acceptance criterion concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/spec-kit-schema.ttl:40-60` | AcceptanceScenario class with Given/When/Then structure |
| `ontology/spec-kit-schema.ttl:584-617` | AcceptanceScenarioShape SHACL validation |
| `ontology/spec-kit-schema.ttl:652-676` | SuccessCriterionShape with measurable conditions |
| `ontology/jtbd-schema.ttl:889-920` | DesiredOutcomeShape linking criteria to outcomes |

---

## Related Patterns

- *Derives from:* **[5. Outcome Desired](../context/outcome-desired.md)** — Criteria address outcomes
- *Enables:* **[31. Test Before Code](../verification/test-before-code.md)** — Criteria become tests
- *Supports:* **[40. Outcome Measurement](../evolution/outcome-measurement.md)** — Criteria define metrics
- *Traced by:* **[20. Traceability Thread](./traceability-thread.md)** — Criteria link in threads

---

## Philosophical Coda

> *"If you can't write a test for it, you don't understand it."*

Acceptance criteria force understanding. They make the implicit explicit, the vague concrete, the arguable testable. They are the bridge between intention and verification.

A specification without acceptance criteria is like a destination without directions. You know where you want to go, but not how to know when you've arrived. Criteria are the signpost that says: "You are here. Journey complete."

---

## Exercises

### Exercise 1: Criteria Audit

Review a feature in your codebase. Does it have explicit acceptance criteria? If not, write them retroactively. Did the exercise reveal gaps in understanding?

### Exercise 2: Edge Case Discovery

For a single criterion, brainstorm all possible edge cases:
- What if the input is empty?
- What if the input is very large?
- What if permissions are wrong?
- What if the system is under load?

### Exercise 3: Priority Assignment

Take a list of 20 potential criteria for a feature. Assign MoSCoW priorities. How many Must vs. Should vs. Could? Is the Must list achievable in one iteration?

### Exercise 4: Test Generation

Write a simple template that generates test stubs from acceptance criteria. How much of the test can be generated vs. requires manual implementation?

---

## Further Reading

- *Specification by Example* — Gojko Adzic
- *Writing Effective Use Cases* — Alistair Cockburn
- *User Stories Applied* — Mike Cohn
- *The Cucumber Book* — Matt Wynne & Aslak Hellesoy
- *Acceptance Test-Driven Development* — Ken Pugh

