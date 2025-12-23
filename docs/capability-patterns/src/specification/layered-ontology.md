# 16. Layered Ontology

★★

*Not all concepts are created equal. Some are foundational and stable. Others are domain-specific and evolving. Layered ontologies separate levels of abstraction, enabling reuse while allowing specialization.*

---

Your ontology grows. You add classes for commands, jobs, outcomes, metrics. Each concept connects to others. Before long, you have a web of definitions that's hard to navigate, change, or reuse.

The problem is mixing levels:
- Universal concepts (name, description, timestamp) mixed with
- Framework concepts (Job, Outcome, Command) mixed with
- Domain concepts (ValidateCommand, SyntaxCheckJob) mixed with
- Instance data (the actual command definitions)

When everything lives at one level, changes ripple unpredictably. Reusing parts becomes impossible. Understanding the whole becomes overwhelming.

**The problem: Flat ontologies mix universal, framework, domain, and instance levels, creating tangled dependencies and preventing reuse.**

---

**The forces at play:**

- *Simplicity wants one layer.* Fewer files, fewer imports, less ceremony.

- *Reuse wants abstraction.* Generic concepts should be reusable across domains.

- *Evolution wants isolation.* Domain changes shouldn't affect framework. Framework changes shouldn't affect universal.

- *Integration wants connection.* Layers must work together seamlessly.

The tension: separate concerns cleanly while maintaining coherent integration.

---

**Therefore:**

Organize your ontology into distinct layers, each building on the ones below.

**Layer 0: External Standards**
```turtle
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
```
Universal standards. Never modified. Always imported.

**Layer 1: Framework Core**
```turtle
# core/framework.ttl
@prefix sk: <http://github.com/spec-kit#> .

sk:Entity a rdfs:Class ;
    rdfs:label "Entity" ;
    rdfs:comment "Base class for all spec-kit entities" .

sk:name a rdf:Property ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:string .

sk:description a rdf:Property ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:string .
```
Fundamental concepts shared across all spec-kit domains.

**Layer 2: Domain Schemas**
```turtle
# cli/schema.ttl
@prefix cli: <http://github.com/spec-kit/cli#> .
@prefix sk: <http://github.com/spec-kit#> .

cli:Command a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:comment "A CLI command" .

cli:Argument a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:comment "A command argument" .

cli:hasArgument a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range cli:Argument .
```
Domain-specific concepts that use framework core.

```turtle
# jtbd/schema.ttl
@prefix jtbd: <http://github.com/spec-kit/jtbd#> .
@prefix sk: <http://github.com/spec-kit#> .

jtbd:Job a rdfs:Class ;
    rdfs:subClassOf sk:Entity .

jtbd:Outcome a rdfs:Class ;
    rdfs:subClassOf sk:Entity .
```
Another domain schema, parallel to CLI.

**Layer 3: Domain Instances**
```turtle
# cli/commands.ttl
@prefix cli: <http://github.com/spec-kit/cli#> .

cli:ValidateCommand a cli:Command ;
    sk:name "validate" ;
    sk:description "Validate RDF files" ;
    cli:hasArgument cli:FileArgument .

cli:FileArgument a cli:Argument ;
    sk:name "file" ;
    cli:type "Path" ;
    cli:required true .
```
Actual specification instances.

**Layer structure:**

```
Layer 0: External Standards (rdfs, xsd, sh, owl)
    │
    ▼
Layer 1: Framework Core (sk:)
    │
    ├───────┬───────┬───────┐
    ▼       ▼       ▼       ▼
Layer 2: CLI     JTBD    Docs   (domain schemas)
         (cli:)  (jtbd:) (docs:)
    │       │       │
    ▼       ▼       ▼
Layer 3: Commands Jobs  Sections (domain instances)
```

**Import discipline:**

Each layer imports only from layers below:
```turtle
# cli/schema.ttl
@prefix cli: <http://github.com/spec-kit/cli#> .

# Imports from Layer 1 (below)
<> owl:imports <../core/framework.ttl> .

# Never imports from peer domains (JTBD, Docs)
# Those connections happen through explicit bridges
```

**Cross-domain bridges:**

When domains need to connect, create explicit bridge vocabularies:
```turtle
# bridges/cli-jtbd.ttl
@prefix bridge: <http://github.com/spec-kit/bridge#> .

bridge:accomplishesJob a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range jtbd:Job ;
    rdfs:comment "Links CLI commands to JTBD jobs" .
```

---

**Resulting context:**

After applying this pattern, you have:

- Clear separation of universal, framework, domain, and instance layers
- Ability to reuse framework across domains
- Isolated change impact—domain changes don't affect framework
- Coherent integration through explicit imports

This supports **[Vocabulary Boundary](./vocabulary-boundary.md)** and enables **[Partial Regeneration](../transformation/partial-regeneration.md)**.

---

**Related patterns:**

- *Refines:* **[13. Vocabulary Boundary](./vocabulary-boundary.md)** — Layers have vocabularies
- *Supports:* **[12. Shape Constraint](./shape-constraint.md)** — Shapes per layer
- *Enables:* **[28. Partial Regeneration](../transformation/partial-regeneration.md)** — Change in one layer

---

> *"High cohesion within layers, loose coupling between layers."*

Layered ontologies apply this principle to knowledge organization. Each layer is internally coherent; connections between layers are explicit and controlled.
