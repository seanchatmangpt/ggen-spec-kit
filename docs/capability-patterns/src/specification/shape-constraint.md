# 12. Shape Constraint

★★

*Freedom without constraint leads to chaos. Constraints without purpose lead to bureaucracy. Shape constraints define the structure of valid specifications—strict enough to prevent errors, flexible enough to allow expression.*

---

You've committed to **[Executable Specifications](./executable-specification.md)**. Execution requires validation. Validation requires constraints. Without constraints, any RDF is valid—including nonsensical or incomplete specifications.

Shape constraints define what a well-formed specification looks like:
- What properties must be present?
- What values are allowed?
- What relationships must exist?
- What patterns must be followed?

These constraints are not bureaucracy. They are the grammar of your specification language. Just as natural language has grammar that enables communication, shape constraints enable shared understanding and automated processing.

**The problem: Without explicit constraints, specifications can be syntactically valid but semantically meaningless. Errors propagate through the pipeline until they surface as bugs or crashes.**

---

**The forces at play:**

- *Strict constraints catch errors early.* The more constrained, the more validation catches.

- *Strict constraints limit expression.* Over-constrained specifications become rigid forms, not living documents.

- *Different contexts need different constraints.* Draft specifications need flexibility; production specifications need strictness.

- *Constraints have maintenance cost.* Every constraint must be kept consistent with evolving needs.

The tension: find the constraint sweet spot—strict enough to catch real errors, loose enough to allow legitimate variation.

---

**Therefore:**

Use SHACL (Shapes Constraint Language) to define shape constraints for your specifications.

**Basic structure:**

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <http://github.com/spec-kit#> .

# Every command must have a name and description
sk:CommandShape a sh:NodeShape ;
    sh:targetClass sk:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:name "name" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 1 ;
        sh:pattern "^[a-z][a-z0-9-]*$" ;
        sh:message "Command name must be lowercase with hyphens"
    ] ;
    sh:property [
        sh:path sk:description ;
        sh:name "description" ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 10 ;
        sh:message "Description required, at least 10 characters"
    ] .
```

**Constraint categories:**

**1. Cardinality** — How many values?
```turtle
sh:minCount 1 ;  # Required
sh:maxCount 1 ;  # At most one
sh:minCount 0 ; sh:maxCount 5 ;  # Up to 5
```

**2. Type** — What kind of value?
```turtle
sh:datatype xsd:string ;   # Must be string
sh:datatype xsd:integer ;  # Must be integer
sh:class sk:Argument ;     # Must be an Argument
sh:nodeKind sh:IRI ;       # Must be a URI
```

**3. Pattern** — What form?
```turtle
sh:pattern "^[a-z][a-z0-9-]*$" ;  # Matches regex
sh:minLength 3 ;                   # At least 3 chars
sh:maxLength 100 ;                 # At most 100 chars
sh:in ("draft" "review" "final") ; # One of these values
```

**4. Relationship** — How connected?
```turtle
sh:property [
    sh:path sk:hasArgument ;
    sh:minCount 0 ;
    sh:node sk:ArgumentShape ;  # Each argument must match ArgumentShape
] ;
```

**5. Conditional** — Context-dependent rules
```turtle
# If type is "file", path is required
sh:property [
    sh:path sk:hasArgument ;
    sh:node [
        sh:if [
            sh:path sk:type ;
            sh:hasValue "file"
        ] ;
        sh:then [
            sh:property [
                sh:path sk:pathPattern ;
                sh:minCount 1
            ]
        ]
    ]
] ;
```

**Constraint layering:**

Define constraints at multiple levels:

```turtle
# Core shape (all commands)
sk:CommandCoreShape a sh:NodeShape ;
    sh:property [ sh:path rdfs:label ; sh:minCount 1 ] .

# Extended shape (production commands)
sk:CommandProductionShape a sh:NodeShape ;
    sh:node sk:CommandCoreShape ;  # Include core
    sh:property [ sh:path sk:hasTest ; sh:minCount 1 ] ;
    sh:property [ sh:path sk:hasDocumentation ; sh:minCount 1 ] .
```

---

**Resulting context:**

After applying this pattern, you have:

- Explicit definition of valid specification structure
- Early validation catches errors before processing
- Clear error messages guide specification authors
- Shared understanding of what specifications must contain

This supports **[Shape Validation](../verification/shape-validation.md)** and enables **[Normalization Stage](../transformation/normalization-stage.md)**.

---

**Related patterns:**

- *Enables:* **[11. Executable Specification](./executable-specification.md)** — Shapes make specs validatable
- *Part of:* **[22. Normalization Stage](../transformation/normalization-stage.md)** — Validation as first transformation step
- *Verified by:* **[34. Shape Validation](../verification/shape-validation.md)** — Checking shapes in CI
- *Supports:* **[16. Layered Ontology](./layered-ontology.md)** — Shapes at different layers

---

> *"Constraints are not the opposite of freedom. They are the precondition for meaningful choice."*

Shape constraints don't limit what you can express—they ensure what you express is coherent.

---

**Error messages matter:**

Good constraint messages guide correction:

```turtle
sh:property [
    sh:path sk:description ;
    sh:minCount 1 ;
    sh:message "Every command needs a description. Add 'sk:description \"Your description here\"' to your command definition."
] ;
```

Bad: "Validation failed"
Good: "Command 'validate' is missing a description. Add sk:description with at least 10 characters explaining what this command does."

---

**Evolving constraints:**

Constraints evolve as understanding deepens:

1. **Start loose:** Allow flexibility while learning the domain
2. **Tighten gradually:** Add constraints as patterns emerge
3. **Document rationale:** Record why each constraint exists
4. **Version shapes:** Use versioned shapes for backwards compatibility

```turtle
sk:CommandShapeV1 a sh:NodeShape ; ... .
sk:CommandShapeV2 a sh:NodeShape ; ... .

# In ggen.toml, specify which version to use
shape_version = "v2"
```
