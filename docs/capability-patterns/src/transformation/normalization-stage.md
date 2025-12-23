# 22. Normalization Stage

★★

*Before transformation, validation. The normalization stage (μ₁) ensures source specifications conform to their shapes, failing fast when they don't.*

---

The **[Constitutional Equation](./constitutional-equation.md)** begins its work with normalization. This first stage (μ₁) takes raw RDF input and validates it against SHACL shapes.

Why validate first? Because errors propagate. An invalid specification might produce output that looks correct but behaves wrong. By validating at the start, we catch problems before they contaminate the pipeline.

Normalization also provides a clean, canonical input for subsequent stages. The validated RDF is guaranteed to conform to expected structure.

**The problem: Invalid specifications can produce subtle errors that surface far from their source. Early validation catches problems when they're cheapest to fix.**

---

**The forces at play:**

- *Speed wants to skip validation.* Validation takes time.

- *Quality wants thoroughness.* Every constraint should be checked.

- *Feedback wants clarity.* Error messages should guide correction.

- *Development wants flexibility.* Draft specs might intentionally be incomplete.

The tension: validate thoroughly without blocking legitimate work.

---

**Therefore:**

Implement normalization (μ₁) as the first transformation stage, validating source RDF against SHACL shapes before any other processing.

**The normalization pipeline:**

```
┌───────────────────────────────────────────────────────────────┐
│  μ₁ NORMALIZE                                                 │
│                                                               │
│  1. Load RDF source file                                      │
│  2. Load SHACL shapes                                         │
│  3. Run SHACL validation                                      │
│  4. If violations:                                            │
│     - Format clear error messages                             │
│     - Report line numbers and context                         │
│     - Exit with failure status                                │
│  5. If valid:                                                 │
│     - Output normalized RDF for next stage                    │
│     - Record validation hash                                  │
│                                                               │
│  Input: feature.ttl                                           │
│  Output: normalized_feature.ttl (or error)                    │
└───────────────────────────────────────────────────────────────┘
```

**SHACL validation:**

```turtle
# shapes/command-shape.ttl
sk:CommandShape a sh:NodeShape ;
    sh:targetClass cli:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Command must have exactly one label (name)"
    ] ;
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 10 ;
        sh:message "Command must have a description of at least 10 characters"
    ] .
```

**Error reporting:**

When validation fails, provide actionable feedback:

```
Validation Failed: ontology/cli-commands.ttl

Error 1 of 2:
  Shape: sk:CommandShape
  Focus: cli:ValidateCommand
  Path: sk:description
  Message: Command must have a description of at least 10 characters
  Current value: "Validate"
  Line: 42

Error 2 of 2:
  Shape: sk:CommandShape
  Focus: cli:CheckCommand
  Path: rdfs:label
  Message: Command must have exactly one label (name)
  Missing property
  Line: 67

Fix these errors and run again.
```

**Validation modes:**

```toml
# ggen.toml
[validation]
mode = "strict"  # strict | warn | skip
shapes = ["shapes/command-shape.ttl", "shapes/argument-shape.ttl"]
```

- **strict:** Validation failures abort transformation (production)
- **warn:** Validation failures logged but transformation continues (development)
- **skip:** No validation (use carefully)

---

**Resulting context:**

After applying this pattern, you have:

- Early failure for invalid specifications
- Clear error messages guiding correction
- Confidence that downstream stages receive valid input
- Hash of validated content for receipt

This feeds into **[Extraction Query](./extraction-query.md)** and enables **[Receipt Generation](./receipt-generation.md)**.

---

**Related patterns:**

- *Part of:* **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₁
- *Uses:* **[12. Shape Constraint](../specification/shape-constraint.md)** — SHACL shapes
- *Precedes:* **[23. Extraction Query](./extraction-query.md)** — Next stage
- *Feeds:* **[26. Receipt Generation](./receipt-generation.md)** — Validation hash

---

> *"An ounce of prevention is worth a pound of cure."*

Normalization is the prevention. It catches errors before they propagate through extraction, emission, and deployment.
