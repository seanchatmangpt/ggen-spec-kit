# 9. Semantic Foundation

★★

*Before you can specify what to build, you must choose how to represent meaning. The semantic foundation—the formal language of concepts and relationships—determines what can be expressed, validated, and transformed.*

---

You understand the context. You know the **[Customer Job](../context/customer-job.md)**, the **[Forces in Tension](../context/forces-in-tension.md)**, the **[Outcome Desired](../context/outcome-desired.md)**. Now you must capture this understanding in a form that can be processed, validated, and transformed into artifacts.

This is the moment of representation choice.

You could write natural language documents. They're easy to create but impossible to validate automatically. Ambiguity creeps in. Different readers interpret differently. The document and the implementation inevitably drift.

You could write code directly. It's precise and executable. But it conflates *what* with *how*. The implementation obscures the intent. Changes require understanding the full codebase.

Or you could choose a semantic foundation—a formal language designed to represent meaning itself. Concepts, relationships, constraints, rules. Precise enough for machines. Rich enough for humans.

**The problem: Without a semantic foundation, specifications remain ambiguous documents that drift from implementation, or they become code that buries intent in mechanism.**

---

**The forces at play:**

- *Expressiveness vs. Formality.* Rich expression allows nuance. Formal structure enables validation. These pull in different directions.

- *Human readability vs. Machine processability.* Humans need to understand. Machines need to process. Serving one can harm the other.

- *Established ecosystems vs. Optimal fit.* Existing standards have tooling. Custom formats might fit better but lack ecosystem.

- *Learning curve vs. Long-term productivity.* Powerful formalisms require investment. Simple formats hit ceilings.

The tension: you need representation that's formal enough to validate and transform, expressive enough to capture intent, and practical enough for your team to adopt.

---

**Therefore:**

Choose RDF (Resource Description Framework) as your semantic foundation.

RDF provides:

**1. Universal identifiers (URIs)**

Every concept, relationship, and entity has a globally unique identifier:
```turtle
<http://github.com/spec-kit#ValidateCommand>
```

No collisions. No ambiguity. References can span documents, systems, organizations.

**2. Subject-predicate-object triples**

All knowledge expressed as simple statements:
```turtle
sk:ValidateCommand sk:hasArgument sk:FileArgument .
sk:FileArgument sk:type xsd:string .
sk:FileArgument sk:required true .
```

Simple primitives, unlimited expressiveness.

**3. Schema languages (RDFS, OWL)**

Define concepts, hierarchies, and relationships:
```turtle
sk:Command rdfs:subClassOf sk:CLIElement .
sk:Argument rdfs:domain sk:Command .
```

Formal ontologies enable inference and validation.

**4. Constraint languages (SHACL)**

Define validation rules:
```turtle
sk:CommandShape a sh:NodeShape ;
    sh:targetClass sk:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:datatype xsd:string
    ] .
```

Constraints are data, not code. They can be queried, transformed, documented.

**5. Query languages (SPARQL)**

Extract data with precision:
```sparql
SELECT ?command ?description WHERE {
    ?command a sk:Command ;
             sk:description ?description .
}
```

Queries can drive code generation, documentation, analysis.

**6. Human-readable serialization (Turtle)**

```turtle
@prefix sk: <http://github.com/spec-kit#> .

sk:ValidateCommand a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" .
```

Readable, writable, diffable.

---

**Resulting context:**

After applying this pattern, you have:

- A formal foundation for expressing specifications
- Global identifiers that prevent naming conflicts
- Schema and constraint languages for validation
- Query languages for extraction and transformation
- Human-readable serialization for editing and review

This foundation enables all subsequent specification patterns, starting with **[Single Source of Truth](./single-source-of-truth.md)**.

---

**Related patterns:**

- *Enables:* **[10. Single Source of Truth](./single-source-of-truth.md)** — RDF files become the source
- *Enables:* **[12. Shape Constraint](./shape-constraint.md)** — SHACL validates specifications
- *Enables:* **[23. Extraction Query](../transformation/extraction-query.md)** — SPARQL extracts data
- *Supports:* **[16. Layered Ontology](./layered-ontology.md)** — RDFS/OWL organize concepts

---

> *"The limits of my language mean the limits of my world."*
>
> — Ludwig Wittgenstein

Choose a language that expands your world. RDF provides the vocabulary for specifications that are precise, validatable, and transformable.

---

**Why Not Alternatives?**

| Alternative | Limitation |
|-------------|------------|
| JSON Schema | Limited expressiveness, no inference, no global identifiers |
| XML Schema | Verbose, structural focus, weak semantics |
| Protobuf | Wire format focus, no query language |
| Custom DSL | No ecosystem, maintenance burden |
| Markdown | Unstructured, no validation |

RDF isn't the only choice. But for specification-driven development, it offers the best balance of expressiveness, tooling, and standards support.

---

**Getting Started:**

1. Learn Turtle syntax (1-2 hours)
2. Define your core prefixes and namespaces
3. Model your first entity (a command, a feature, a concept)
4. Write your first SHACL shape
5. Write your first SPARQL query

The investment pays off when you see specifications flow through validation, extraction, and transformation into consistent artifacts.
