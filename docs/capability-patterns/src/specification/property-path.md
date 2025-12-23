# 14. Property Path

★

*Complex queries require navigating relationships. Property paths provide a concise syntax for traversing the graph of specifications, finding data that spans multiple connections. They are the highways of your knowledge graph.*

---

## The Graph Navigation Challenge

Your specifications form a graph. Commands connect to arguments. Arguments connect to types. Jobs connect to outcomes. Outcomes connect to metrics. This web of relationships holds the full richness of your domain—but accessing that richness requires navigation.

Simple queries retrieve direct properties:

```sparql
SELECT ?name WHERE { ?cmd rdfs:label ?name }
```

But real questions involve chains:
- "What are the argument types for all commands that accomplish a specific job?"
- "What outcomes are affected by commands in the 'validate' category?"
- "What metrics measure outcomes of jobs in the 'quality' category?"
- "What documentation sections cover commands with deprecated arguments?"

These questions require traversing paths through the graph—following the links that connect concepts.

Without property paths, such queries become verbose:

```sparql
# Without paths: verbose, repetitive, hard to read
SELECT ?type WHERE {
    ?cmd a cli:Command ;
         rdfs:label "validate" .
    ?cmd cli:hasArgument ?arg .
    ?arg cli:type ?type .
}
```

With property paths, the same query is concise:

```sparql
# With paths: concise, clear intent
SELECT ?type WHERE {
    ?cmd a cli:Command ;
         rdfs:label "validate" ;
         cli:hasArgument/cli:type ?type .
}
```

---

## The Problem Statement

**Complex navigation queries become verbose and hard to maintain when expressed as multiple triple patterns. The structure of the graph becomes obscured by syntactic noise.**

The cost of verbosity:
- **Readability**: Long queries hide intent
- **Maintainability**: More lines mean more bugs
- **Performance**: Some path expressions optimize better than explicit joins
- **Expressiveness**: Some patterns (like transitive closure) are awkward without paths

---

## The Forces at Play

### Force 1: Expressiveness vs. Performance

**Expressiveness wants deep traversal.** Real questions span many relationships. "Find all outcomes affected by any command that directly or indirectly generates documentation" requires multi-hop navigation.

**Performance wants simplicity.** Complex paths can be slow to evaluate, especially with transitive closure (`*`) over large graphs.

```
Expressiveness ←────────────────────────→ Performance
(deep traversal)                          (simple queries)
```

### Force 2: Readability vs. Flexibility

**Readability wants compactness.** Multi-hop queries should be understandable at a glance. The structure should be obvious.

**Flexibility wants composition.** Paths should combine in useful ways—alternatives, optionals, sequences. But more operators mean more complexity.

```
Readability ←────────────────────────────→ Flexibility
(simple, obvious)                          (powerful, complex)
```

### Force 3: Abstraction vs. Transparency

**Abstraction wants navigation hidden.** "Get all related items" without caring about the exact path.

**Transparency wants visible structure.** Understanding the exact path helps debugging and optimization.

```
Abstraction ←────────────────────────────→ Transparency
(hide navigation)                          (show structure)
```

---

## Therefore: Use SPARQL Property Paths

Use SPARQL property paths to express multi-hop navigation concisely. Property paths are part of the SPARQL 1.1 specification and are widely supported.

### Basic Path Operators

#### Sequence: A then B

Navigate through a chain of properties:

```sparql
# Direct property
?cmd cli:hasArgument ?arg .

# Sequence: command → argument → type
?cmd cli:hasArgument/cli:type ?type .

# Longer sequence: command → argument → type → constraints
?cmd cli:hasArgument/cli:type/sk:hasConstraint ?constraint .

# Cross-domain: command → job → outcome
?cmd cli:accomplishesJob/jtbd:hasOutcome ?outcome .
```

#### Alternative: A or B

Match either of multiple properties:

```sparql
# Either arguments or options
?cmd (cli:hasArgument|cli:hasOption) ?param .

# Any kind of relationship to job
?cmd (cli:accomplishesJob|cli:supportsJob) ?job .

# Name in any language
?entity (rdfs:label|skos:prefLabel|skos:altLabel) ?name .
```

#### Inverse: Follow Backwards

Navigate relationships in reverse:

```sparql
# Normal: command → argument
?cmd cli:hasArgument ?arg .

# Inverse: argument ← command
?arg ^cli:hasArgument ?cmd .

# Useful for finding parents
?entity ^sk:contains ?parent .
```

#### Transitive Closure: Zero or More Steps

Navigate chains of any length:

```sparql
# Any ancestor (zero or more steps)
?concept rdfs:subClassOf* ?parent .
# Matches: concept itself, direct parent, grandparent, etc.

# Any descendant
?parent ^rdfs:subClassOf* ?descendant .

# Useful for type hierarchies
?instance a/rdfs:subClassOf* sk:Entity .
```

#### One or More Steps

Like transitive closure, but at least one step:

```sparql
# At least one ancestor (not self)
?concept rdfs:subClassOf+ ?parent .

# At least one level of nesting
?root sk:contains+ ?nested .
```

#### Optional: Zero or One Step

Match with or without a step:

```sparql
# Command, or command's argument if it exists
?cmd cli:hasArgument? ?maybeArg .
```

#### Negation: Not Through Path

Exclude certain paths (limited support):

```sparql
# Find nodes not connected via deprecated
?entity !(sk:deprecated) ?other .
```

### Path Composition

Combine operators for powerful expressions:

```sparql
# All arguments and options, with their types
?cmd (cli:hasArgument|cli:hasOption)/cli:type ?type .

# All outcomes at any depth in job hierarchy
?job jtbd:hasOutcome+/jtbd:subOutcome* ?outcome .

# Find documentation for any ancestor command
?cmd (^cli:subCommandOf)*/cli:documentedIn ?docs .
```

---

## Common Navigation Patterns

### Pattern 1: Type Hierarchy Navigation

Find all instances of a class or its subclasses:

```sparql
# Find all instances of Command or any subclass
SELECT ?instance WHERE {
    ?instance a/rdfs:subClassOf* cli:Command .
}

# Equivalent to the union:
# ?instance a cli:Command .
# ?instance a cli:ValidationCommand .  (subclass of Command)
# ?instance a cli:GenerationCommand .  (subclass of Command)
```

### Pattern 2: Composition Traversal

Navigate through compositional relationships:

```sparql
# Find all argument types for validate commands
SELECT ?type WHERE {
    ?cmd a cli:Command ;
         rdfs:label "validate" ;
         cli:hasArgument/cli:type ?type .
}

# Find all constraint violations in any argument
SELECT ?cmd ?violation WHERE {
    ?cmd cli:hasArgument/sh:violation ?violation .
}
```

### Pattern 3: Cross-Domain Navigation

Navigate across vocabulary boundaries:

```sparql
# Find all outcomes affected by CLI commands
SELECT ?cmd ?outcome WHERE {
    ?cmd a cli:Command ;
         cli:accomplishesJob/jtbd:hasOutcome ?outcome .
}

# Find documentation coverage for jobs
SELECT ?job ?section WHERE {
    ?job a jtbd:Job ;
         ^cli:accomplishesJob/cli:documentedIn ?section .
}
```

### Pattern 4: Containment Hierarchies

Navigate nested structures:

```sparql
# Find all deeply nested elements
SELECT ?root ?nested WHERE {
    ?root a docs:Document ;
          docs:contains+ ?nested .
}

# Find the root of any element
SELECT ?element ?root WHERE {
    ?element ^docs:contains* ?root .
    FILTER NOT EXISTS { ?root ^docs:contains ?parent }
}
```

### Pattern 5: Finding Paths

Discover what connects two nodes:

```sparql
# What path connects this command to this outcome?
SELECT ?intermediate WHERE {
    cli:ValidateCommand (!<>)+ ?intermediate .
    ?intermediate (!<>)* jtbd:FastValidation .
}
```

---

## Paths in SHACL

Property paths also work in SHACL shapes for validation:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .

sk:CommandShape a sh:NodeShape ;
    sh:targetClass cli:Command ;

    # Every command's arguments must have types
    sh:property [
        sh:path (cli:hasArgument cli:type) ;
        sh:minCount 1 ;
        sh:message "All command arguments must specify a type"
    ] ;

    # Commands must trace to at least one job
    sh:property [
        sh:path cli:accomplishesJob ;
        sh:minCount 1 ;
        sh:message "Commands must accomplish at least one job"
    ] ;

    # No deprecated arguments in non-deprecated commands
    sh:sparql [
        sh:message "Non-deprecated commands cannot have deprecated arguments" ;
        sh:select """
            SELECT $this WHERE {
                $this cli:hasArgument/sk:deprecated true .
                FILTER NOT EXISTS { $this sk:deprecated true }
            }
        """
    ] .
```

---

## Path Performance

Property paths can be expensive. Mitigate with these strategies:

### Strategy 1: Limit Depth

Use `+` (one or more) instead of `*` (zero or more) when at least one step is required. This avoids matching the node to itself.

```sparql
# Better: At least one step required
?concept rdfs:subClassOf+ ?ancestor .

# Worse: May match concept to itself
?concept rdfs:subClassOf* ?ancestor .
```

### Strategy 2: Add Type Constraints First

Constrain the starting nodes before path traversal:

```sparql
# Better: Filter first, then traverse
SELECT ?outcome WHERE {
    ?cmd a cli:Command ;
         rdfs:label "validate" ;
         cli:accomplishesJob/jtbd:hasOutcome ?outcome .
}

# Worse: Traverse all paths, then filter
SELECT ?outcome WHERE {
    ?cmd cli:accomplishesJob/jtbd:hasOutcome ?outcome .
    ?cmd a cli:Command ;
         rdfs:label "validate" .
}
```

### Strategy 3: Bound Variables

Start from known nodes when possible:

```sparql
# Better: Start from specific command
SELECT ?outcome WHERE {
    cli:ValidateCommand cli:accomplishesJob/jtbd:hasOutcome ?outcome .
}

# Worse: Find all commands, then their outcomes
SELECT ?outcome WHERE {
    ?cmd a cli:Command ;
         cli:accomplishesJob/jtbd:hasOutcome ?outcome .
}
```

### Strategy 4: Index Key Properties

Ensure frequently traversed properties are indexed in your triplestore:

```
# Common indexes for path queries
cli:hasArgument
cli:accomplishesJob
jtbd:hasOutcome
rdfs:subClassOf
sk:contains
```

### Strategy 5: Materialize Common Paths

For frequently queried paths, consider materializing them:

```sparql
# Pre-compute: Commands and their outcomes (transitive)
INSERT {
    ?cmd sk:affectsOutcome ?outcome .
}
WHERE {
    ?cmd cli:accomplishesJob+/jtbd:hasOutcome+ ?outcome .
}
```

Then query the materialized relationship:

```sparql
# Fast query against materialized path
SELECT ?outcome WHERE {
    cli:ValidateCommand sk:affectsOutcome ?outcome .
}
```

---

## Case Study: Traceability Navigation

### The Challenge

A team needs to answer traceability questions:
- "What tests cover this outcome?"
- "What requirements are affected by this code change?"
- "What is the full provenance chain for this artifact?"

These questions require navigating complex paths across multiple domains.

### Without Paths: Verbose Queries

```sparql
# What tests cover this outcome? (verbose version)
SELECT ?test WHERE {
    jtbd:MinimizeValidationTime sk:addressedBy ?criterion .
    ?criterion sk:satisfiedBy ?test .
}

# Equivalent path version
SELECT ?test WHERE {
    jtbd:MinimizeValidationTime sk:addressedBy/sk:satisfiedBy ?test .
}
```

### Full Traceability Query

```sparql
# Complete traceability thread using paths
PREFIX cli: <https://spec-kit.io/ontology/cli#>
PREFIX jtbd: <https://spec-kit.io/ontology/jtbd#>
PREFIX sk: <https://spec-kit.io/ontology#>

SELECT ?need ?job ?outcome ?criterion ?test ?code ?spec WHERE {
    # Start from a need
    ?need jtbd:hasJob ?job .

    # Follow to outcomes
    ?job jtbd:hasOutcome+ ?outcome .

    # Through criteria to tests
    ?outcome sk:addressedBy ?criterion .
    ?criterion sk:satisfiedBy ?test .

    # Tests validate code
    ?test sk:validates ?code .

    # Code generated from spec
    ?code sk:generatedFrom ?spec .
}
```

### Impact Analysis

```sparql
# What is impacted if we change this job?
SELECT ?impacted ?type WHERE {
    jtbd:ValidateOntologyJob (
        jtbd:hasOutcome |
        jtbd:hasOutcome/sk:addressedBy |
        jtbd:hasOutcome/sk:addressedBy/sk:satisfiedBy |
        ^cli:accomplishesJob
    ) ?impacted .
    ?impacted a ?type .
}
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Unbounded Transitive Closure

Using `*` without bounds on large graphs:

```sparql
# Dangerous: Could traverse entire graph
SELECT ?related WHERE {
    ?start (!<>)* ?related .
}
```

**Problem:** Exponential expansion. Use bounded depth or add type constraints.

### Anti-Pattern 2: Path Instead of Join

Using paths where explicit joins would be clearer:

```sparql
# Overly compressed
SELECT ?name WHERE {
    ?x cli:hasArgument/rdfs:label ?name .
}

# Clearer when you need the intermediate
SELECT ?arg ?name WHERE {
    ?x cli:hasArgument ?arg .
    ?arg rdfs:label ?name .
}
```

**When to use paths vs joins:** Paths when you don't need intermediates. Joins when you do.

### Anti-Pattern 3: Complex Path Without Testing

Building complex paths without verifying they return expected results:

```sparql
# Complex path - does it do what you think?
SELECT ?x WHERE {
    ?start (a/rdfs:subClassOf*/^a)+ ?x .
}
```

**Always test paths** against known data before using in production.

---

## Path Design Principles

### Principle 1: Prefer Explicit to Transitive

Named relationships are clearer than `*` closure:

```sparql
# Clear: Explicit relationship
?cmd cli:hasRequiredArgument ?arg .

# Less clear: Inferred from path
?cmd cli:hasArgument ?arg .
?arg cli:required true .
```

When a path pattern is common, consider defining a property for it.

### Principle 2: Document Path Semantics

What does this path mean in domain terms?

```sparql
# Document the meaning
# "All customer outcomes that this command helps achieve"
?cmd cli:accomplishesJob/jtbd:hasOutcome ?outcome .
```

### Principle 3: Test Paths

Verify paths return expected results:

```sparql
# Test: This path should return exactly these values
SELECT ?outcome WHERE {
    cli:ValidateCommand cli:accomplishesJob/jtbd:hasOutcome ?outcome .
}
# Expected: jtbd:FastValidation, jtbd:AccurateValidation
```

### Principle 4: Consider Inverse

Sometimes following backwards is more efficient:

```sparql
# Forward: From jobs to commands
SELECT ?cmd WHERE {
    ?job jtbd:hasOutcome jtbd:FastValidation .
    ?cmd cli:accomplishesJob ?job .
}

# Inverse: From outcome to commands (sometimes faster)
SELECT ?cmd WHERE {
    jtbd:FastValidation ^jtbd:hasOutcome/^cli:accomplishesJob ?cmd .
}
```

---

## Resulting Context

After applying this pattern, you have:

- **Concise queries** that traverse complex relationships
- **Maintainable navigation expressions** that capture intent
- **Cross-domain analysis** capabilities
- **Foundation for sophisticated extraction queries**
- **Pattern library** for common navigation needs

This enhances **[Extraction Query](../transformation/extraction-query.md)** and supports **[Traceability Thread](./traceability-thread.md)**.

---

## Related Patterns

- *Enhances:* **[23. Extraction Query](../transformation/extraction-query.md)** — Paths make extraction powerful
- *Navigates:* **[13. Vocabulary Boundary](./vocabulary-boundary.md)** — Paths cross boundaries
- *Enables:* **[20. Traceability Thread](./traceability-thread.md)** — Trace links via paths
- *Works with:* **[15. Inference Rule](./inference-rule.md)** — Paths query inferred facts

---

## Philosophical Coda

> *"The path is made by walking."*
>
> — Antonio Machado

In RDF, the path is made by defining relationships and navigating them. Well-designed paths make complex questions simple. Poorly-designed paths make simple questions complex.

The relationships you define are the roads. Property paths are how you travel them. Build good roads, and navigation becomes natural.

---

## Exercises

### Exercise 1: Path Conversion

Convert these verbose queries to use property paths:

```sparql
# Query 1
SELECT ?type WHERE {
    ?cmd cli:hasArgument ?arg .
    ?arg cli:type ?type .
}

# Query 2
SELECT ?doc WHERE {
    ?cmd cli:accomplishesJob ?job .
    ?job jtbd:hasOutcome ?outcome .
    ?outcome sk:documentedIn ?doc .
}
```

### Exercise 2: Path Design

Design paths for these questions:
1. "All commands that have deprecated arguments"
2. "All jobs whose outcomes are not measured"
3. "The documentation section for any command's argument's type"

### Exercise 3: Performance Analysis

For a graph with 10,000 nodes:
1. Measure query time with `rdfs:subClassOf*` vs `rdfs:subClassOf+`
2. Compare bounded vs unbounded traversal
3. Test the effect of type constraints on performance

---

## Further Reading

- *SPARQL 1.1 Property Paths* — W3C Specification
- *SPARQL Query Optimization* — Various papers
- *Graph Database Patterns* — O'Reilly
- *RDF Graph Navigation* — Semantic Web best practices

