# 19. Acceptance Criterion

★★

*How do you know when something is done? Acceptance criteria define the boundary between incomplete and complete, providing concrete, testable conditions for success.*

---

You've specified *what* to build. But when is it built? What conditions must be satisfied for the capability to be considered complete?

Vague acceptance leads to:
- "It works" (for whom? under what conditions?)
- "It's done" (says who? by what measure?)
- Endless scope creep (there's always one more thing)
- Arguments about completeness (we said X, they heard Y)

Acceptance criteria make completion concrete. They're the contract between specifier and implementer, the checklist that determines done.

**The problem: Without explicit acceptance criteria, "done" is undefined. Scope creeps, arguments arise, and capabilities linger in eternal incompleteness.**

---

**The forces at play:**

- *Completeness wants all cases covered.* Every edge case, every scenario.

- *Practicality wants focus.* Not everything matters equally.

- *Testability wants concreteness.* "Works well" is untestable. "Returns in < 100ms" is testable.

- *Flexibility wants room.* Over-specification constrains creative solutions.

The tension: specific enough to be testable, flexible enough to allow implementation choices.

---

**Therefore:**

For each capability, define explicit acceptance criteria using the Given-When-Then format, encoded in RDF for traceability.

**Given-When-Then structure:**

```
Given [precondition/context]
When [action/trigger]
Then [expected outcome/postcondition]
```

**Example acceptance criteria:**

```turtle
cli:ValidateCommand cli:hasAcceptanceCriterion [
    a sk:AcceptanceCriterion ;
    sk:id "AC-VAL-001" ;
    sk:given "A syntactically valid RDF/Turtle file exists" ;
    sk:when "User runs 'specify validate file.ttl'" ;
    sk:then "Command exits with code 0 and prints 'Valid ✓'" ;
    sk:priority "must"
] .

cli:ValidateCommand cli:hasAcceptanceCriterion [
    a sk:AcceptanceCriterion ;
    sk:id "AC-VAL-002" ;
    sk:given "A syntactically invalid RDF/Turtle file exists" ;
    sk:when "User runs 'specify validate file.ttl'" ;
    sk:then "Command exits with non-zero code and prints error with line number" ;
    sk:priority "must"
] .

cli:ValidateCommand cli:hasAcceptanceCriterion [
    a sk:AcceptanceCriterion ;
    sk:id "AC-VAL-003" ;
    sk:given "User runs validate on a 100MB file" ;
    sk:when "Validation completes" ;
    sk:then "Peak memory usage stays below 200MB" ;
    sk:priority "should"
] .
```

**Priority levels:**

- **must:** Required for acceptance. Capability is incomplete without this.
- **should:** Expected but negotiable. Missing this degrades quality.
- **could:** Nice to have. Missing this is acceptable.
- **won't:** Explicitly out of scope. Documents boundaries.

**Criteria categories:**

```turtle
# Functional: What it does
sk:FunctionalCriterion rdfs:subClassOf sk:AcceptanceCriterion .

# Performance: How fast/efficient
sk:PerformanceCriterion rdfs:subClassOf sk:AcceptanceCriterion .

# Usability: How easy to use
sk:UsabilityCriterion rdfs:subClassOf sk:AcceptanceCriterion .

# Security: How safe
sk:SecurityCriterion rdfs:subClassOf sk:AcceptanceCriterion .

# Compatibility: What it works with
sk:CompatibilityCriterion rdfs:subClassOf sk:AcceptanceCriterion .
```

**Linking to outcomes:**

```turtle
cli:ValidateCommand cli:hasAcceptanceCriterion [
    sk:id "AC-VAL-001" ;
    sk:addresses jtbd:MinimizeValidationTime ;  # Links to JTBD outcome
    sk:given "Valid RDF file" ;
    sk:when "User runs validate" ;
    sk:then "Completes in < 1 second for files < 1MB" ;
    sk:measurable true
] .
```

---

**Resulting context:**

After applying this pattern, you have:

- Concrete definition of "done" for each capability
- Testable conditions that can be automated
- Clear priority to guide implementation effort
- Traceable link from criteria to outcomes

This enables **[Test Before Code](../verification/test-before-code.md)** and supports **[Outcome Measurement](../evolution/outcome-measurement.md)**.

---

**Related patterns:**

- *Derives from:* **[5. Outcome Desired](../context/outcome-desired.md)** — Criteria address outcomes
- *Enables:* **[31. Test Before Code](../verification/test-before-code.md)** — Criteria become tests
- *Supports:* **[40. Outcome Measurement](../evolution/outcome-measurement.md)** — Criteria define metrics
- *Traced by:* **[20. Traceability Thread](./traceability-thread.md)** — Criteria linked to specs

---

> *"If you can't write a test for it, you don't understand it."*

Acceptance criteria force understanding. They make the implicit explicit, the vague concrete, the arguable testable.

---

**Writing good criteria:**

1. **One criterion, one condition:** Don't combine multiple checks
2. **Observable outcome:** Something you can see or measure
3. **No implementation details:** What, not how
4. **Edge cases matter:** Happy path + failure cases + boundaries
5. **Realistic scenarios:** Based on actual use cases

---

**Generating tests from criteria:**

```sparql
# Extract criteria for test generation
SELECT ?id ?given ?when ?then ?priority WHERE {
    ?cmd cli:hasAcceptanceCriterion ?criterion .
    ?criterion sk:id ?id ;
               sk:given ?given ;
               sk:when ?when ;
               sk:then ?then ;
               sk:priority ?priority .
    FILTER (?priority IN ("must", "should"))
}
```

```python
# Generated test stub
def test_AC_VAL_001():
    """
    Given: A syntactically valid RDF/Turtle file exists
    When: User runs 'specify validate file.ttl'
    Then: Command exits with code 0 and prints 'Valid ✓'
    """
    # Given
    valid_file = create_valid_ttl()

    # When
    result = runner.invoke(app, ["validate", valid_file])

    # Then
    assert result.exit_code == 0
    assert "Valid ✓" in result.output
```
