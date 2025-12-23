# 9. Semantic Foundation

★★

*Before you can specify what to build, you must choose how to represent meaning. The semantic foundation—the formal language of concepts and relationships—determines what can be expressed, validated, and transformed.*

---

## The Moment of Representation

You've completed the **[Context Patterns](../context/living-system.md)**. You understand the **[Living System](../context/living-system.md)**, the **[Customer Job](../context/customer-job.md)**, the **[Forces in Tension](../context/forces-in-tension.md)**, the **[Outcome Desired](../context/outcome-desired.md)**. You know what you need to build and why.

Now you face a critical choice: How will you represent this understanding?

This is not a minor technical decision. The representation you choose determines:
- What can be expressed (expressiveness)
- What can be validated (formality)
- What can be transformed (machine-processability)
- What can be understood by humans (readability)
- What can be maintained over time (evolvability)

Choose poorly, and your specifications become either:
- Ambiguous documents that drift from implementation
- Rigid code that buries intent in mechanism
- Custom formats that lack tooling and require constant maintenance

Choose well, and your specifications become the foundation for a living system of generation, validation, and evolution.

---

## The Problem

**Without a semantic foundation, specifications remain ambiguous documents that drift from implementation, or they become code that buries intent in mechanism.**

This manifests in predictable ways:

- **Documentation drift**: The spec says one thing; the code does another. No one knows which is right.
- **Validation gaps**: Requirements can't be automatically verified. Manual review is the only check.
- **Generation limits**: Each output format requires custom code. There's no shared model to transform.
- **Communication failures**: Different stakeholders interpret specs differently. Conflicts emerge late.
- **Maintenance burden**: Every change requires updating multiple inconsistent artifacts.

Behind each failure lies the same root cause: the absence of a formal, semantic foundation that captures meaning in a way that both humans and machines can reliably process.

---

## Understanding Representation Choices

Before choosing RDF, understand the alternatives and why they fall short.

### Natural Language Documents

**What it is**: Specifications written in English (or other natural languages) in documents like Word, Google Docs, or Markdown.

**Strengths**:
- Easy to write
- Universally readable
- Flexible and expressive
- No special tools required

**Limitations**:
- Inherently ambiguous
- Cannot be validated automatically
- Cannot be transformed programmatically
- Drift is inevitable
- Different readers interpret differently

**Verdict**: Good for communication, inadequate for formal specification.

### Code as Specification

**What it is**: Writing the implementation itself, treating code as the specification.

**Strengths**:
- Precise and executable
- Always matches implementation (by definition)
- Single source of truth

**Limitations**:
- Conflates *what* with *how*
- Intent buried in mechanism
- Technology-specific
- Hard for non-developers to understand
- Changes require understanding full codebase

**Verdict**: Good for execution, poor for specification of intent.

### JSON/YAML Configuration

**What it is**: Using structured data formats like JSON or YAML for configuration.

**Strengths**:
- Easy to read and write
- Good tooling support
- Hierarchical structure
- Language-agnostic

**Limitations**:
- No inherent semantics (keys mean whatever you decide)
- Limited schema validation
- No query language
- No inference capability
- No global identifiers

**Verdict**: Good for configuration, insufficient for knowledge representation.

### XML/XSD

**What it is**: XML for data, XSD for schema validation.

**Strengths**:
- Strong validation (XSD)
- Mature ecosystem
- Standard transformations (XSLT, XPath)

**Limitations**:
- Verbose syntax
- Structural, not semantic focus
- No inference capability
- No global identifier standard
- Complex to author

**Verdict**: Powerful but heavyweight; focuses on structure over meaning.

### Custom Domain-Specific Languages

**What it is**: Creating your own language tailored to your domain.

**Strengths**:
- Perfect fit for your needs
- Optimal expressiveness for your domain
- Full control over syntax and semantics

**Limitations**:
- No existing ecosystem
- Maintenance burden forever
- Training cost for every new team member
- No interoperability
- Reinventing the wheel

**Verdict**: Tempting but rarely justified; ecosystem trumps fit.

### RDF (Resource Description Framework)

**What it is**: A semantic web standard for representing knowledge as subject-predicate-object triples with global identifiers.

**Strengths**:
- Global identifiers (URIs)
- Rich schema languages (RDFS, OWL)
- Powerful constraint language (SHACL)
- Expressive query language (SPARQL)
- Human-readable serialization (Turtle)
- Inference capability
- Mature ecosystem and tooling
- W3C standard

**Limitations**:
- Learning curve
- Can be verbose
- Tooling less mainstream than JSON
- Overkill for simple configuration

**Verdict**: The best balance of expressiveness, formality, and tooling for specification-driven development.

---

## The Forces at Play

Several forces pull in different directions when choosing a semantic foundation:

### Expressiveness vs. Formality

**Expressiveness**: The ability to capture nuance, context, and complexity.

**Formality**: The precision that enables machine processing and validation.

Natural language is maximally expressive but minimally formal. Programming languages are formal but often inexpressive about intent.

RDF hits the sweet spot: formal enough for validation and transformation, expressive enough for complex knowledge representation.

### Human Readability vs. Machine Processability

**Human readability**: Specifications that people can understand, review, and maintain.

**Machine processability**: Specifications that tools can validate, query, and transform.

Many formal systems sacrifice readability for processability. RDF's Turtle serialization maintains both—it's designed to be human-readable while remaining fully machine-processable.

### Established Ecosystem vs. Optimal Fit

**Established ecosystem**: Standards with mature tools, documentation, community, and integration.

**Optimal fit**: Custom solutions tailored to your exact needs.

The temptation is always to build something custom. But ecosystem benefits compound over time: bug fixes from the community, integrations with other tools, training resources, experienced hires.

RDF represents decades of standardization work. Building custom is rarely worth abandoning this investment.

### Learning Curve vs. Long-Term Productivity

**Learning curve**: The upfront investment to master a representation.

**Long-term productivity**: The ongoing efficiency once mastery is achieved.

Simple formats are easy to start with but hit ceilings quickly. Powerful formalisms require investment but enable capabilities that simpler approaches cannot match.

RDF has a learning curve, but the investment pays off through:
- Automatic validation (SHACL)
- Powerful querying (SPARQL)
- Inference capabilities (RDFS/OWL)
- Transformation pipelines
- Living documentation generation

---

## Therefore

**Choose RDF (Resource Description Framework) as your semantic foundation.**

RDF provides the core capabilities needed for specification-driven development:

### 1. Universal Identifiers (URIs)

Every concept, relationship, and entity has a globally unique identifier:

```turtle
<http://github.com/spec-kit#ValidateCommand>
```

This means:
- **No collisions**: Different teams, different organizations, different systems can define concepts without conflicting.
- **No ambiguity**: A reference to `sk:ValidateCommand` means exactly one thing everywhere.
- **Linkability**: Concepts can reference each other across documents, systems, and organizations.
- **Stability**: Once defined, identifiers remain stable even as implementations change.

#### The Power of URIs

Consider the difference:

**Without URIs**:
```yaml
command:
  name: validate
  # Is this the same as the "validate" in another file?
  # Which one is authoritative?
```

**With URIs**:
```turtle
<http://github.com/spec-kit#ValidateCommand>
    # Globally unique. Unambiguous. Referenceable.
```

URIs solve the naming problem that plagues every large-scale specification effort.

### 2. Subject-Predicate-Object Triples

All knowledge expressed as simple statements:

```turtle
sk:ValidateCommand sk:hasArgument sk:FileArgument .
sk:FileArgument sk:type xsd:string .
sk:FileArgument sk:required true .
```

Each triple is a fact:
- **Subject**: The thing being described (`sk:ValidateCommand`)
- **Predicate**: The property or relationship (`sk:hasArgument`)
- **Object**: The value or related thing (`sk:FileArgument`)

#### The Power of Triples

Simple primitives, unlimited expressiveness. Any knowledge that can be expressed can be expressed as triples:

```turtle
# A command
sk:ValidateCommand a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" .

# An argument
sk:FileArgument a sk:Argument ;
    rdfs:label "file" ;
    sk:type xsd:string ;
    sk:required true ;
    sk:position 0 .

# A relationship
sk:ValidateCommand sk:hasArgument sk:FileArgument .

# A constraint
sk:FileArgument sk:mustExist true .

# A circumstance reference
sk:ValidateCommand sk:primaryCircumstance jtbd:PreCommitCircumstance .
```

Triples can express anything: entities, relationships, properties, constraints, metadata.

### 3. Schema Languages (RDFS, OWL)

Define concepts, hierarchies, and relationships:

```turtle
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Class hierarchy
sk:Command a rdfs:Class ;
    rdfs:subClassOf sk:CLIElement ;
    rdfs:label "Command"@en ;
    rdfs:comment "A CLI command that can be invoked"@en .

sk:Argument a rdfs:Class ;
    rdfs:label "Argument"@en ;
    rdfs:comment "A parameter to a command"@en .

# Property definitions
sk:hasArgument a rdf:Property ;
    rdfs:domain sk:Command ;
    rdfs:range sk:Argument ;
    rdfs:label "has argument"@en .

sk:required a owl:DatatypeProperty ;
    rdfs:domain sk:Argument ;
    rdfs:range xsd:boolean ;
    rdfs:label "required"@en .
```

Schema languages enable:
- **Type checking**: Ensure values are of expected types
- **Hierarchy traversal**: Query for all `sk:CLIElement` instances includes all `sk:Command` instances
- **Inference**: Derive new facts from existing ones
- **Documentation**: Schema is self-documenting

### 4. Constraint Languages (SHACL)

Define validation rules:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .

sk:CommandShape a sh:NodeShape ;
    sh:targetClass sk:Command ;

    # Every command must have a label
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Every command must have exactly one label"
    ] ;

    # Description is recommended
    sh:property [
        sh:path sk:description ;
        sh:minCount 0 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:severity sh:Warning ;
        sh:message "Commands should have descriptions"
    ] ;

    # Arguments must be valid
    sh:property [
        sh:path sk:hasArgument ;
        sh:node sk:ArgumentShape
    ] .

sk:ArgumentShape a sh:NodeShape ;
    sh:targetClass sk:Argument ;

    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:pattern "^[a-z][a-z0-9_-]*$" ;
        sh:message "Argument names must be lowercase with hyphens/underscores"
    ] ;

    sh:property [
        sh:path sk:required ;
        sh:minCount 1 ;
        sh:datatype xsd:boolean
    ] .
```

SHACL constraints are **data, not code**:
- They can be queried, transformed, documented
- They can generate validation reports
- They can be versioned and evolved
- They are the specification of valid structure

### 5. Query Languages (SPARQL)

Extract data with precision:

```sparql
PREFIX sk: <http://github.com/spec-kit#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Find all commands with their descriptions
SELECT ?command ?label ?description
WHERE {
    ?command a sk:Command ;
             rdfs:label ?label .
    OPTIONAL { ?command sk:description ?description }
}
ORDER BY ?label

# Find all required arguments for a specific command
SELECT ?arg ?name ?type
WHERE {
    sk:ValidateCommand sk:hasArgument ?arg .
    ?arg rdfs:label ?name ;
         sk:required true .
    OPTIONAL { ?arg sk:type ?type }
}

# Find commands without descriptions (documentation gaps)
SELECT ?command ?label
WHERE {
    ?command a sk:Command ;
             rdfs:label ?label .
    FILTER NOT EXISTS { ?command sk:description ?desc }
}
```

SPARQL enables:
- **Code generation**: Extract data to render templates
- **Documentation**: Query for all commands, arguments, descriptions
- **Analysis**: Find patterns, gaps, relationships
- **Validation**: Check invariants beyond SHACL

### 6. Human-Readable Serialization (Turtle)

```turtle
@prefix sk: <http://github.com/spec-kit#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# A complete command specification
sk:ValidateCommand a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;
    sk:hasArgument sk:FileArgument, sk:StrictArgument ;
    sk:primaryCircumstance jtbd:PreCommitCircumstance .

sk:FileArgument a sk:Argument ;
    rdfs:label "file" ;
    sk:description "Path to the RDF file to validate" ;
    sk:type xsd:string ;
    sk:required true ;
    sk:position 0 .

sk:StrictArgument a sk:Argument ;
    rdfs:label "--strict" ;
    sk:description "Treat warnings as errors" ;
    sk:type xsd:boolean ;
    sk:required false ;
    sk:default false .
```

Turtle is:
- **Readable**: Humans can understand it at a glance
- **Writable**: Humans can author it without special tools
- **Diffable**: Version control works naturally
- **Parseable**: Machines can process it without ambiguity

---

## The RDF Ecosystem

Choosing RDF gives you access to a mature ecosystem:

### Serialization Formats

| Format | Use Case | Human Readable |
|--------|----------|----------------|
| Turtle | Primary authoring | ★★★★★ |
| JSON-LD | Web/API integration | ★★★★☆ |
| N-Triples | Streaming/processing | ★★☆☆☆ |
| RDF/XML | Legacy integration | ★☆☆☆☆ |

### Tools and Libraries

| Category | Examples |
|----------|----------|
| Validation | pyshacl, TopBraid SHACL |
| Query engines | Apache Jena, RDFLib, Oxigraph |
| Editors | Protégé, TopBraid Composer, VS Code plugins |
| Triple stores | Fuseki, GraphDB, Stardog |
| Transformation | ggen, custom SPARQL-based pipelines |

### Standards

| Standard | Purpose |
|----------|---------|
| RDF 1.1 | Core data model |
| RDFS | Basic schema vocabulary |
| OWL 2 | Advanced ontology language |
| SHACL | Constraints and validation |
| SPARQL 1.1 | Query and update |
| Turtle | Human-readable syntax |
| JSON-LD | JSON-based RDF |

---

## Case Study: The Documentation Drift

A team maintained command-line tool documentation in Markdown. The code implemented commands in Python. Over time, they diverged:

- New commands were added to code but not docs
- Argument names changed in code but not docs
- Descriptions in docs didn't match `--help` output
- Users complained about inconsistent information

**The fix**:

They moved to RDF as the source of truth:

```turtle
# Source of truth: commands.ttl
sk:ValidateCommand a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;
    sk:hasArgument sk:FileArgument .
```

From this, they generated:
- Python CLI code
- Markdown documentation
- `--help` output
- Man pages

Drift became impossible. The equation held:

```
docs.md = μ(commands.ttl)
code.py = μ(commands.ttl)
```

---

## Case Study: The Multi-Language Challenge

Another team needed to generate code in Python, TypeScript, and Go from the same specification. Each language had different patterns:

- Python: Typer for CLI
- TypeScript: Commander.js
- Go: Cobra

Without a semantic foundation, they would need three separate specification documents that would inevitably diverge.

**The solution**:

RDF specification + language-specific templates:

```turtle
# Language-agnostic specification
sk:ValidateCommand a sk:Command ;
    rdfs:label "validate" ;
    sk:hasArgument [
        a sk:Argument ;
        rdfs:label "file" ;
        sk:type sk:Path ;
        sk:required true
    ] .
```

Templates for each language:

```
# python.tera
@app.command()
def {{ command.label }}({{ arguments | python_signature }}):
    ...

# typescript.tera
program.command('{{ command.label }}')
       .argument({{ arguments | ts_arguments }})
       ...

# go.tera
var {{ command.label | go_name }}Cmd = &cobra.Command{
    Use: "{{ command.label }}",
    ...
}
```

One specification, three outputs. Changes propagate automatically.

---

## Getting Started with RDF

### Step 1: Learn Turtle Syntax (1-2 hours)

The basics:

```turtle
# Prefixes (shorthand for URIs)
@prefix sk: <http://github.com/spec-kit#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Subject-predicate-object triple
sk:MyCommand rdfs:label "my-command" .

# Multiple properties, same subject (use semicolons)
sk:MyCommand a sk:Command ;
    rdfs:label "my-command" ;
    sk:description "Does something useful" .

# Multiple values, same property (use commas)
sk:MyCommand sk:hasArgument sk:Arg1, sk:Arg2, sk:Arg3 .

# Blank nodes (anonymous resources)
sk:MyCommand sk:hasArgument [
    a sk:Argument ;
    rdfs:label "file" ;
    sk:required true
] .
```

### Step 2: Define Your Core Prefixes

```turtle
@prefix : <http://your-project.example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix jtbd: <http://your-project.example.org/jtbd#> .
```

### Step 3: Model Your First Entity

Start simple:

```turtle
:MyFirstFeature a :Feature ;
    rdfs:label "My First Feature" ;
    :description "This feature does something valuable" ;
    :concernsJob jtbd:SomeCustomerJob ;
    :priority "high" .
```

### Step 4: Write Your First SHACL Shape

```turtle
:FeatureShape a sh:NodeShape ;
    sh:targetClass :Feature ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Every feature must have a label"
    ] ;
    sh:property [
        sh:path :priority ;
        sh:in ("low" "medium" "high" "critical") ;
        sh:message "Priority must be low, medium, high, or critical"
    ] .
```

### Step 5: Write Your First SPARQL Query

```sparql
PREFIX : <http://your-project.example.org/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?feature ?label ?priority
WHERE {
    ?feature a :Feature ;
             rdfs:label ?label ;
             :priority ?priority .
}
ORDER BY ?priority
```

---

## Checklist: Have You Established a Semantic Foundation?

Before proceeding, verify:

### Foundation Choice
- [ ] I have evaluated representation alternatives
- [ ] I have chosen RDF as my semantic foundation
- [ ] I understand the trade-offs involved

### Core Infrastructure
- [ ] I have defined my base prefixes and namespaces
- [ ] I have created my first ontology file
- [ ] I have SHACL shapes for validation
- [ ] I have SPARQL queries for extraction

### Team Readiness
- [ ] Team members have learned Turtle basics
- [ ] Tooling is installed (editors, validators)
- [ ] Workflow is established (edit, validate, commit)

### First Specification
- [ ] At least one entity is fully specified in RDF
- [ ] The specification is validated by SHACL
- [ ] A SPARQL query can extract useful data

If any of these remain unclear, invest more time before proceeding.

---

## Why Not Alternatives?

| Alternative | Primary Limitation |
|-------------|-------------------|
| JSON Schema | No inference, no global identifiers, limited expressiveness |
| XML/XSD | Verbose, structural focus, weak semantics, complex |
| Protobuf | Wire format focus, no query language, no constraints |
| Custom DSL | No ecosystem, permanent maintenance burden |
| Plain Markdown | Unstructured, no validation, inevitable drift |
| YAML configs | No semantics, no query, no inference |

RDF isn't perfect. It has a learning curve. It can be verbose for simple things. Tooling is less mainstream than JSON.

But for specification-driven development—where you need validation, transformation, and evolution—RDF offers the best balance of expressiveness, tooling, and standards support.

---

## Resulting Context

After applying this pattern, you have:

- A formal foundation for expressing specifications
- Global identifiers that prevent naming conflicts
- Schema and constraint languages for validation
- Query languages for extraction and transformation
- Human-readable serialization for editing and review

This foundation enables all subsequent specification patterns:

- **[10. Single Source of Truth](./single-source-of-truth.md)** — RDF files become the authoritative source
- **[12. Shape Constraint](./shape-constraint.md)** — SHACL validates specifications
- **[13. Vocabulary Boundary](./vocabulary-boundary.md)** — Namespaces organize concepts
- **[23. Extraction Query](../transformation/extraction-query.md)** — SPARQL extracts data for transformation

---

## Related Patterns

### Enables:

**[10. Single Source of Truth](./single-source-of-truth.md)** — RDF files become the source.

**[12. Shape Constraint](./shape-constraint.md)** — SHACL validates specifications.

**[13. Vocabulary Boundary](./vocabulary-boundary.md)** — Namespaces organize concepts.

### Supports:

**[16. Layered Ontology](./layered-ontology.md)** — RDFS/OWL organize concepts by abstraction.

**[17. Domain-Specific Language](./domain-specific-language.md)** — DSLs can be built on RDF.

---

## Philosophical Foundations

> *"The limits of my language mean the limits of my world."*
>
> — Ludwig Wittgenstein

The representation you choose determines what you can express. A language without formal semantics cannot express formal constraints. A language without global identifiers cannot express unambiguous references. A language without query capability cannot express extractable knowledge.

Choose a language that expands your world. RDF provides the vocabulary for specifications that are precise, validatable, and transformable.

> *"There are only two hard things in Computer Science: cache invalidation and naming things."*
>
> — Phil Karlton

RDF's URI-based identifiers solve the naming problem once and for all. Every concept has a globally unique, unambiguous identifier. No collisions. No confusion. No drift.

---

## The Investment Perspective

Learning RDF requires investment. Is it worth it?

**Short-term costs**:
- Learning curve for Turtle, SPARQL, SHACL
- New tooling to install and configure
- New patterns to learn

**Long-term benefits**:
- Specifications that are precise and unambiguous
- Automatic validation catches errors early
- Generation eliminates drift
- Documentation stays current
- Transformation enables multi-target output
- Evolution is traceable

The return on investment is multiplicative. Every specification you write benefits from the foundation. Every artifact you generate is consistent. Every validation run catches errors before they escape.

The question isn't whether to invest in a semantic foundation. It's whether you can afford not to.

---

## Exercise: Establish Your Foundation

Before proceeding to the next pattern, complete this exercise:

1. **Install tooling**: Set up an RDF editor and SHACL validator

2. **Learn Turtle**: Complete a Turtle syntax tutorial (see Further Reading)

3. **Define your namespace**: Choose your base URI and core prefixes

4. **Model one entity**: Create your first RDF specification

5. **Validate it**: Write a SHACL shape and validate your specification

6. **Query it**: Write a SPARQL query that extracts useful data

Only after completing this exercise should you proceed to **[Single Source of Truth](./single-source-of-truth.md)**.

---

## Further Reading

- W3C. *RDF 1.1 Primer* — Introduction to RDF concepts: [https://www.w3.org/TR/rdf11-primer/](https://www.w3.org/TR/rdf11-primer/)
- W3C. *Turtle Syntax* — The human-readable serialization: [https://www.w3.org/TR/turtle/](https://www.w3.org/TR/turtle/)
- W3C. *SHACL Specification* — Constraints and validation: [https://www.w3.org/TR/shacl/](https://www.w3.org/TR/shacl/)
- W3C. *SPARQL 1.1* — Query language: [https://www.w3.org/TR/sparql11-query/](https://www.w3.org/TR/sparql11-query/)
- Allemang, Dean & Hendler, James. *Semantic Web for the Working Ontologist* (2011) — Practical guide to semantic technologies.

---

The semantic foundation determines everything that follows. Choose wisely, invest in learning, and the patterns that follow will flow naturally from a solid base.
