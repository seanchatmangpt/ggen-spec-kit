# 11. Executable Specification

★★

*A specification that cannot be executed is a wish. An executable specification is precise enough to drive validation, generation, and testing—eliminating the gap between what we intend and what we build.*

---

You have a **[Single Source of Truth](./single-source-of-truth.md)**. But truth that sits inert is just documentation. The power of a specification emerges when it *executes*—when it actively participates in validation, generation, and verification.

Traditional specifications are passive. They describe what should be built. A human reads them, interprets them, implements something based on their understanding. Interpretation introduces drift. Each reader understands differently.

Executable specifications are active. They don't just describe—they *do*:
- Validation: Does this instance conform?
- Generation: Produce code from this definition
- Testing: Verify behavior matches this contract

When a specification executes, there's no interpretation gap. The specification *is* the behavior definition.

**The problem: Passive specifications allow interpretation. Interpretation causes drift. Drift causes bugs, inconsistency, and wasted reconciliation effort.**

---

**The forces at play:**

- *Precision is hard.* Executable specifications require unambiguous definition. Ambiguity is easier to write.

- *Edge cases are tedious.* Real execution requires handling every case. Documentation can wave at edge cases.

- *Maintenance burden.* Executable specifications must stay updated. Documentation can quietly rot.

- *Tooling required.* Execution requires infrastructure. Documentation needs only a text editor.

The tension: executable specifications are more valuable but more demanding. The investment must be worthwhile.

---

**Therefore:**

Make your RDF specifications executable through three mechanisms:

**1. SHACL Validation**

Every specification includes SHACL shapes that validate instances:

```turtle
# Specification: Commands must have a name, description, and at least one argument
sk:CommandShape a sh:NodeShape ;
    sh:targetClass sk:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z][a-z0-9-]*$"
    ] ;
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:datatype xsd:string
    ] .
```

This shape *executes* by validating every command definition. Invalid commands are rejected before generation.

**2. SPARQL Extraction**

Every specification can be queried to extract structured data:

```sparql
# Extract command definitions for code generation
SELECT ?name ?description ?argName ?argType ?argRequired WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?name ;
         sk:description ?description ;
         sk:hasArgument ?arg .
    ?arg sk:name ?argName ;
         sk:type ?argType ;
         sk:required ?argRequired .
}
```

This query *executes* by extracting data that drives template rendering.

**3. Template Emission**

Specifications drive code generation through templates:

```jinja
# Generated from ontology/commands.ttl
@app.command("{{ name }}")
def {{ name|replace("-", "_") }}_command(
    {% for arg in arguments %}
    {{ arg.name }}: {{ arg.type }}{% if not arg.required %} = None{% endif %},
    {% endfor %}
) -> None:
    """{{ description }}"""
    pass
```

The template *executes* by producing code files from extracted data.

**The execution pipeline:**

```
Specification (RDF)
      │
      ├──[SHACL]──▶ Validation (pass/fail)
      │
      ├──[SPARQL]──▶ Extraction (JSON)
      │                 │
      │                 └──[Template]──▶ Code/Docs
      │
      └──[Inference]──▶ Derived facts
```

Every specification participates in this pipeline. If it can't be validated, extracted, or transformed, it's not executable—it's just documentation.

---

**Resulting context:**

After applying this pattern, you have:

- Specifications that actively validate their instances
- Specifications that drive code and documentation generation
- No gap between specification and implementation
- Automatic detection when specifications are violated

This enables the full **[Constitutional Equation](../transformation/constitutional-equation.md)** pipeline and supports **[Test Before Code](../verification/test-before-code.md)**.

---

**Related patterns:**

- *Builds on:* **[10. Single Source of Truth](./single-source-of-truth.md)** — Source must be executable
- *Uses:* **[12. Shape Constraint](./shape-constraint.md)** — SHACL makes specs executable
- *Enables:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Transformation of specs
- *Supports:* **[31. Test Before Code](../verification/test-before-code.md)** — Specs define tests

---

> *"An ounce of specification is worth a pound of debugging."*

And an executable specification is worth a ton of passive documentation.

---

**Levels of Executability:**

Not all specifications need full executability. Consider levels:

| Level | Execution | Example |
|-------|-----------|---------|
| 0 | None (documentation) | Prose description |
| 1 | Validation only | SHACL shape without generation |
| 2 | Validation + Extraction | Data extracted but not generated |
| 3 | Full pipeline | Validation → Extraction → Generation |

Aim for Level 3 for core specifications. Accept lower levels for supplementary information.

---

**Making Existing Specs Executable:**

If you have existing prose specifications:

1. **Identify the formal content:** What parts can be precisely defined?
2. **Model in RDF:** Express formal content as triples
3. **Add SHACL shapes:** Define validation rules
4. **Write SPARQL queries:** Extract data for generation
5. **Create templates:** Generate artifacts
6. **Link prose to formal:** Keep narrative as annotations on formal specs

The goal isn't to eliminate prose—it's to separate executable content from narrative context.
