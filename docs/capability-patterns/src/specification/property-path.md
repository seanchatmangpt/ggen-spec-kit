# 14. Property Path

★

*Complex queries require navigating relationships. Property paths provide a concise syntax for traversing the graph of specifications, finding data that spans multiple connections.*

---

Your specifications form a graph. Commands connect to arguments. Arguments connect to types. Jobs connect to outcomes. Outcomes connect to metrics. Navigating this graph efficiently is essential for extraction and analysis.

Simple queries retrieve direct properties:
```sparql
SELECT ?name WHERE { ?cmd rdfs:label ?name }
```

But real questions involve chains:
- "What are the argument types for all commands that accomplish a specific job?"
- "What outcomes are affected by commands in the 'validate' category?"
- "What metrics measure outcomes of jobs in the 'quality' category?"

These questions require traversing paths through the graph.

**The problem: Complex navigation queries become verbose and hard to maintain when expressed as multiple triple patterns.**

---

**The forces at play:**

- *Expressiveness wants deep traversal.* Real questions span many relationships.

- *Performance wants simplicity.* Complex paths can be slow to evaluate.

- *Readability wants compactness.* Multi-hop queries should be understandable.

- *Flexibility wants composition.* Paths should combine in useful ways.

The tension: express complex navigation without sacrificing readability or performance.

---

**Therefore:**

Use SPARQL property paths to express multi-hop navigation concisely.

**Basic path syntax:**

```sparql
# Direct property
?cmd cli:hasArgument ?arg .

# Sequence (A then B)
?cmd cli:hasArgument/cli:type ?type .  # cmd → arg → type

# Alternative (A or B)
?cmd (cli:hasArgument|cli:hasOption) ?param .  # arg or option

# Inverse (follow backwards)
?arg ^cli:hasArgument ?cmd .  # arg ← cmd

# Transitive closure (zero or more)
?concept rdfs:subClassOf* ?parent .  # any ancestor

# One or more
?concept rdfs:subClassOf+ ?parent .  # at least one step

# Optional step
?cmd cli:hasArgument? ?arg .  # cmd, or cmd → arg
```

**Common patterns:**

**1. Navigating type hierarchies:**
```sparql
# Find all instances of Command or its subclasses
SELECT ?instance WHERE {
    ?instance a/rdfs:subClassOf* cli:Command .
}
```

**2. Traversing composition:**
```sparql
# Find all argument types for validate commands
SELECT ?type WHERE {
    ?cmd a cli:Command ;
         rdfs:label "validate" ;
         cli:hasArgument/cli:type ?type .
}
```

**3. Cross-domain navigation:**
```sparql
# Find all outcomes affected by CLI commands
SELECT ?cmd ?outcome WHERE {
    ?cmd a cli:Command ;
         cli:accomplishesJob/jtbd:hasOutcome ?outcome .
}
```

**4. Finding paths of interest:**
```sparql
# Find commands and their documentation sections
SELECT ?cmd ?section WHERE {
    ?cmd a cli:Command ;
         docs:documentedIn/docs:hasSection ?section .
}
```

**Path in SHACL shapes:**

Property paths also work in SHACL for validation:

```turtle
sk:CommandShape a sh:NodeShape ;
    sh:property [
        # Every command's arguments must have types
        sh:path (cli:hasArgument cli:type) ;
        sh:minCount 1 ;
        sh:message "All command arguments must specify a type"
    ] .
```

---

**Resulting context:**

After applying this pattern, you have:

- Concise queries that traverse complex relationships
- Maintainable navigation expressions
- Ability to analyze cross-domain connections
- Foundation for sophisticated extraction queries

This enhances **[Extraction Query](../transformation/extraction-query.md)** and supports **[Traceability Thread](./traceability-thread.md)**.

---

**Related patterns:**

- *Enhances:* **[23. Extraction Query](../transformation/extraction-query.md)** — Paths make extraction powerful
- *Navigates:* **[13. Vocabulary Boundary](./vocabulary-boundary.md)** — Paths cross boundaries
- *Enables:* **[20. Traceability Thread](./traceability-thread.md)** — Trace links via paths

---

> *"The path is made by walking."*
>
> — Antonio Machado

In RDF, the path is made by defining relationships and navigating them. Well-designed paths make complex questions simple.

---

**Performance considerations:**

Property paths can be expensive. Mitigate with:

1. **Limit depth:** Use `+` over `*` when at least one step is required
2. **Add type constraints:** `?x a cli:Command` before path traversal
3. **Index key properties:** Ensure frequently traversed properties are indexed
4. **Cache common paths:** Materialize frequently queried paths

---

**Path design principles:**

1. **Prefer explicit to transitive:** Named relationships are clearer than `*` closure
2. **Document path semantics:** What does this path mean in domain terms?
3. **Test paths:** Verify paths return expected results
4. **Consider inverse:** Sometimes following backwards is more efficient
