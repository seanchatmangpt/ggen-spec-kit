# 23. Extraction Query

★★

*RDF is a graph. Templates need structured data. Extraction queries (μ₂) bridge this gap, using SPARQL to select and shape data for emission. This stage transforms the boundless flexibility of graphs into the focused structures templates require.*

---

## The Bridge

After **[Normalization](./normalization-stage.md)**, you have validated RDF. But RDF is a graph of triples—flexible, interconnected, non-linear. It's a web of relationships where any node can connect to any other node through any predicate.

Templates need something different. They need structured data—lists, records, trees. They need to iterate over commands, access arguments, render values. They need shape.

Extraction queries bridge this gap. They navigate the RDF graph with the precision of SPARQL, select the nodes and relationships relevant to the current transformation, and reshape the results into structures templates can consume directly.

Think of extraction as asking questions of the specification:
- "What commands exist and what are their arguments?"
- "What jobs have high-importance, low-satisfaction outcomes?"
- "What acceptance criteria apply to this feature?"
- "Which entities link to this capability and how?"

SPARQL answers these questions, producing structured results that templates transform into artifacts.

---

## The Shape Problem

**The fundamental challenge: RDF graphs don't directly map to template inputs. The graph is a web; templates need trees. The graph is interconnected; templates need focused slices. Extraction queries shape graph data into consumable structures.**

Let us understand why this matters:

### The Graph vs. Tree Tension

RDF represents knowledge as a graph:

```
           ┌─────────────────┐
           │ cli:validate    │
           └────────┬────────┘
                    │ a
                    ▼
           ┌─────────────────┐
           │ cli:Command     │◄────── cli:check
           └────────┬────────┘        (a cli:Command)
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
       rdfs:label  cli:desc  cli:hasArgument
          │         │         │
          ▼         ▼         ▼
       "validate"  "..."    ┌──────┐
                            │ _:b1 │
                            └──┬───┘
                               │
                    ┌──────────┼──────────┐
                    ▼          ▼          ▼
                cli:name   cli:type   cli:required
                    │          │          │
                    ▼          ▼          ▼
                  "file"     "Path"     true
```

Templates expect trees:

```json
{
  "commands": [
    {
      "name": "validate",
      "description": "...",
      "arguments": [
        {"name": "file", "type": "Path", "required": true}
      ]
    }
  ]
}
```

The extraction query transforms web to tree, graph to structure.

### The Vocabulary Spanning Challenge

Real specifications span multiple vocabularies:

```turtle
cli:validate
    a cli:Command ;
    jtbd:accomplishesJob :VerifyCorrectness ;
    acc:hasAcceptanceCriteria :AC001, :AC002 ;
    trace:derivesFrom :REQ-101 .
```

A single query might need to pull from CLI vocabulary, JTBD vocabulary, acceptance vocabulary, and traceability vocabulary. SPARQL handles this naturally through its graph pattern matching.

### The Optionality Problem

Not all specifications are complete. Some commands have arguments; some don't. Some have examples; some don't. Extraction must handle these variations gracefully.

```sparql
OPTIONAL {
    ?cmd cli:hasArgument ?arg .
    ?arg cli:name ?argName .
}
```

With OPTIONAL, missing data produces null results rather than failing the query.

---

## The Forces

Several tensions shape extraction design:

### Force: Flexibility vs. Focus

*SPARQL can express almost any query. But complex queries are hard to maintain.*

You could write a single massive query that extracts everything:

```sparql
SELECT ?cmd ?name ?desc ?arg ?argName ?argType ?option ?optName ?example ...
WHERE {
    ?cmd a cli:Command .
    ?cmd rdfs:label ?name .
    # ... hundreds of lines of graph patterns ...
}
```

This becomes unmaintainable. Each template addition requires modifying the monster query.

**Resolution:** Focused queries for focused purposes. Each template gets its own extraction query.

### Force: Reuse vs. Specificity

*Similar templates need similar data. But each template has unique needs.*

The Python command template needs arguments with types. The Markdown documentation template needs arguments with help text. Both need the command name and description.

**Resolution:** Query libraries and composition. Common patterns in shared queries, template-specific queries for unique needs.

### Force: Performance vs. Completeness

*Complex queries over large graphs can be slow. But incomplete queries require post-processing.*

```sparql
# Fast but requires post-processing
SELECT ?cmd ?argName WHERE { ... }

# Complete but potentially slow
SELECT ?cmd ?name ?desc ?arg ?argName ?argType ?argRequired ?argHelp ?argDefault
WHERE { ... }
```

**Resolution:** Profile and optimize. Use appropriate query complexity for the graph size. Consider caching for repeated queries.

### Force: Raw Results vs. Template-Ready

*SPARQL produces tabular results. Templates often need nested structures.*

```
| cmd      | argName | argType |
|----------|---------|---------|
| validate | file    | Path    |
| validate | output  | Path    |
| check    | input   | Path    |
```

Templates want:
```json
[
  {"name": "validate", "arguments": [{"name": "file"}, {"name": "output"}]},
  {"name": "check", "arguments": [{"name": "input"}]}
]
```

**Resolution:** Post-processing to reshape results. SPARQL provides the data; reshaping code provides the structure.

---

## Therefore

**Implement extraction (μ₂) using SPARQL queries that navigate the RDF graph, select relevant data, and produce structured results for template consumption. Include post-processing to reshape tabular results into template-ready structures.**

The extraction pipeline:

```
┌────────────────────────────────────────────────────────────────────┐
│  μ₂ EXTRACT                                                         │
│                                                                     │
│  1. LOAD validated RDF graph (from μ₁)                             │
│                                                                     │
│  2. LOAD SPARQL query for target                                   │
│     ├── Resolve query file path                                    │
│     ├── Parse query text                                           │
│     └── Validate query syntax                                      │
│                                                                     │
│  3. EXECUTE query against graph                                     │
│     ├── Bind any template-provided variables                       │
│     ├── Run query engine                                           │
│     └── Collect result bindings                                    │
│                                                                     │
│  4. RESHAPE results for template                                    │
│     ├── Group by primary entity                                    │
│     ├── Nest related entities                                      │
│     └── Convert to template-ready structure                        │
│                                                                     │
│  5. OUTPUT structured data                                          │
│     ├── As JSON for external templates                             │
│     └── As Python dict for internal templates                      │
│                                                                     │
│  Input: validated_feature.ttl + query.rq                           │
│  Output: structured_data.json (or dict)                            │
└────────────────────────────────────────────────────────────────────┘
```

---

## SPARQL Query Design

### Basic Query Structure

Every extraction query follows a similar pattern:

```sparql
# sparql/command-extract.rq
# Purpose: Extract CLI command data for Python code generation
# Used by: templates/command.py.tera

PREFIX cli: <http://spec-kit.dev/cli#>
PREFIX sk: <http://spec-kit.dev/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?cmdUri ?name ?description ?argName ?argType ?argRequired ?argHelp ?argDefault
WHERE {
    # Primary entity: commands
    ?cmdUri a cli:Command ;
            rdfs:label ?name ;
            sk:description ?description .

    # Optional related entities: arguments
    OPTIONAL {
        ?cmdUri cli:hasArgument ?arg .
        ?arg cli:name ?argName ;
             cli:type ?argType .
        OPTIONAL { ?arg cli:required ?argRequired }
        OPTIONAL { ?arg cli:help ?argHelp }
        OPTIONAL { ?arg cli:default ?argDefault }
    }
}
ORDER BY ?name ?argName
```

### Query Documentation

Every query should be documented:

```sparql
# ═══════════════════════════════════════════════════════════════════
# Query: command-docs-extract.rq
# ═══════════════════════════════════════════════════════════════════
#
# PURPOSE:
#   Extract CLI command data for documentation generation.
#   Includes examples, rationale, and cross-references.
#
# INPUTS:
#   - Validated cli-commands.ttl graph
#
# OUTPUTS:
#   - Command name, description, rationale
#   - Arguments with help text
#   - Usage examples
#   - Related commands
#
# USED BY:
#   - templates/command.md.tera
#   - templates/command-index.md.tera
#
# MAINTENANCE:
#   - Last updated: 2025-01-15
#   - Author: spec-kit team
# ═══════════════════════════════════════════════════════════════════
```

### Query Patterns

#### Pattern: Flat Extraction

Simple list of properties for a class:

```sparql
SELECT ?name ?description ?version
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?name ;
         sk:description ?description .
    OPTIONAL { ?cmd sk:version ?version }
}
ORDER BY ?name
```

**Result:**
```
| name     | description            | version |
|----------|------------------------|---------|
| check    | Quick validation check | 1.0     |
| validate | Full validation        | 2.1     |
```

#### Pattern: Hierarchical Extraction

Parent with children:

```sparql
SELECT ?cmdName ?argName ?argType ?argRequired
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         cli:hasArgument ?arg .
    ?arg cli:name ?argName ;
         cli:type ?argType .
    OPTIONAL { ?arg cli:required ?argRequired }
}
ORDER BY ?cmdName ?argName
```

**Result:**
```
| cmdName  | argName | argType | argRequired |
|----------|---------|---------|-------------|
| validate | file    | Path    | true        |
| validate | output  | Path    | false       |
| validate | strict  | bool    | false       |
```

#### Pattern: Cross-Vocabulary Extraction

Spanning multiple vocabularies:

```sparql
PREFIX cli: <http://spec-kit.dev/cli#>
PREFIX jtbd: <http://spec-kit.dev/jtbd#>
PREFIX acc: <http://spec-kit.dev/acceptance#>

SELECT ?cmdName ?jobLabel ?criterionText
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         jtbd:accomplishesJob ?job ;
         acc:hasAcceptanceCriteria ?criterion .
    ?job rdfs:label ?jobLabel .
    ?criterion acc:criterionText ?criterionText .
}
ORDER BY ?cmdName ?jobLabel
```

#### Pattern: Aggregation

Collecting multiple values:

```sparql
SELECT ?cmdName (GROUP_CONCAT(?tag; separator=", ") as ?tags)
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         sk:hasTag ?tag .
}
GROUP BY ?cmdName
```

**Result:**
```
| cmdName  | tags                    |
|----------|-------------------------|
| validate | rdf, validation, shacl  |
| check    | quick, lint             |
```

#### Pattern: Conditional Selection

Filtering based on conditions:

```sparql
SELECT ?cmdName ?description
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         sk:description ?description ;
         sk:stability ?stability .

    # Only stable commands
    FILTER (?stability = "stable")
}
```

#### Pattern: Property Paths

Traversing relationships:

```sparql
SELECT ?cmdName ?grandparentCategory
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?cmdName ;
         # Navigate: cmd -> category -> parent category
         cli:inCategory/sk:parentCategory ?grandparentCategory .
}
```

---

## Result Post-Processing

### From Tabular to Nested

SPARQL returns tabular data. Templates often need nested structures:

```python
def reshape_commands(sparql_results: list[dict]) -> list[dict]:
    """
    Transform tabular SPARQL results to nested command structure.

    Input (tabular):
        [
            {"cmdName": "validate", "argName": "file", "argType": "Path"},
            {"cmdName": "validate", "argName": "output", "argType": "Path"},
            {"cmdName": "check", "argName": "input", "argType": "Path"}
        ]

    Output (nested):
        [
            {
                "name": "validate",
                "arguments": [
                    {"name": "file", "type": "Path"},
                    {"name": "output", "type": "Path"}
                ]
            },
            {
                "name": "check",
                "arguments": [
                    {"name": "input", "type": "Path"}
                ]
            }
        ]
    """
    commands = {}

    for row in sparql_results:
        cmd_name = row['cmdName']

        # Initialize command if first encounter
        if cmd_name not in commands:
            commands[cmd_name] = {
                'name': cmd_name,
                'description': row.get('description', ''),
                'arguments': [],
                'options': []
            }

        # Add argument if present
        if row.get('argName'):
            commands[cmd_name]['arguments'].append({
                'name': row['argName'],
                'type': row.get('argType', 'str'),
                'required': row.get('argRequired', False),
                'help': row.get('argHelp', ''),
                'default': row.get('argDefault')
            })

    return list(commands.values())
```

### Type Conversion

SPARQL returns RDF types. Templates need language types:

```python
def convert_rdf_value(value, expected_type: str):
    """Convert RDF literal to Python type."""
    if value is None:
        return None

    if expected_type == 'boolean':
        if isinstance(value, bool):
            return value
        return str(value).lower() in ('true', '1', 'yes')

    elif expected_type == 'integer':
        return int(value)

    elif expected_type == 'float':
        return float(value)

    elif expected_type == 'date':
        from datetime import datetime
        return datetime.fromisoformat(str(value))

    else:
        return str(value)
```

### Deduplication

Joins can produce duplicates:

```python
def deduplicate_results(results: list[dict], key_fields: list[str]) -> list[dict]:
    """Remove duplicate rows based on key fields."""
    seen = set()
    unique = []

    for row in results:
        key = tuple(row.get(f) for f in key_fields)
        if key not in seen:
            seen.add(key)
            unique.append(row)

    return unique
```

### Sorting

Ensure consistent ordering:

```python
def sort_commands(commands: list[dict]) -> list[dict]:
    """Sort commands by name, arguments by position then name."""
    for cmd in commands:
        cmd['arguments'].sort(
            key=lambda a: (a.get('position', 999), a['name'])
        )
    return sorted(commands, key=lambda c: c['name'])
```

---

## Query Organization

### File Structure

```
sparql/
├── commands/
│   ├── command-extract.rq           # For Python code generation
│   ├── command-docs-extract.rq      # For Markdown documentation
│   ├── command-test-extract.rq      # For test generation
│   └── command-completions-extract.rq  # For shell completions
├── jobs/
│   ├── job-extract.rq               # JTBD extraction
│   └── outcome-extract.rq           # Outcome extraction
├── shared/
│   ├── prefixes.rq                  # Common prefix definitions
│   └── common-patterns.rq           # Reusable graph patterns
└── README.md                        # Query documentation
```

### Query Composition

Share common elements across queries:

```sparql
# shared/prefixes.rq
PREFIX cli: <http://spec-kit.dev/cli#>
PREFIX sk: <http://spec-kit.dev/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX jtbd: <http://spec-kit.dev/jtbd#>
PREFIX acc: <http://spec-kit.dev/acceptance#>
PREFIX trace: <http://spec-kit.dev/traceability#>
```

Include in queries:

```python
def load_query(query_path: Path) -> str:
    """Load query with prefix includes."""
    query_text = query_path.read_text()

    # Replace include directives
    while '#include' in query_text:
        query_text = resolve_includes(query_text)

    return query_text
```

---

## Configuration

```toml
# ggen.toml

[extraction]
query_dir = "sparql"
result_format = "json"  # json | dict

# Query execution settings
[extraction.engine]
timeout = 30  # seconds
memory_limit = "512MB"
inference = "rdfs"  # none | rdfs | owl

# Post-processing settings
[extraction.reshape]
deduplicate = true
sort_results = true
null_handling = "omit"  # omit | empty_string | explicit_null

# Per-target query configuration
[[targets]]
name = "python-commands"
query = "sparql/commands/command-extract.rq"
reshape = "reshape_commands"  # Python function for reshaping
```

---

## Case Study: The Query Optimization

*A team improves extraction performance for a large specification.*

### The Situation

The CloudOps team had 847 CLI commands specified in RDF. Generation worked, but extraction was slow—12 seconds per transformation run. This made iteration painful during development.

### The Analysis

Profiling revealed the problem:

```
Query execution breakdown:
  command-extract.rq:        2.1s   ████████░░
  command-docs-extract.rq:   3.4s   ██████████████░
  command-test-extract.rq:   4.2s   ████████████████░░
  command-index-extract.rq:  2.3s   █████████░
  Total:                    12.0s
```

The docs query was particularly slow due to a complex cross-vocabulary join:

```sparql
SELECT ?cmd ?name ?desc ?job ?outcome ?criterion ?relatedCmd
WHERE {
    ?cmd a cli:Command ; rdfs:label ?name ; sk:description ?desc .
    ?cmd jtbd:accomplishesJob ?job .
    ?job jtbd:hasOutcome ?outcome .
    ?cmd acc:hasAcceptanceCriteria ?criterion .
    OPTIONAL {
        ?cmd sk:relatedCommand ?relatedCmd .
    }
}
```

This created a massive cross-product for commands with many outcomes and criteria.

### The Solution

**Step 1: Query Decomposition**

Split the monolithic query into focused queries:

```sparql
# command-basic.rq - Core command data
SELECT ?cmd ?name ?desc WHERE { ?cmd a cli:Command ; rdfs:label ?name ; sk:description ?desc }

# command-jobs.rq - Job relationships
SELECT ?cmd ?job ?outcome WHERE { ?cmd jtbd:accomplishesJob ?job . ?job jtbd:hasOutcome ?outcome }

# command-criteria.rq - Acceptance criteria
SELECT ?cmd ?criterion WHERE { ?cmd acc:hasAcceptanceCriteria ?criterion }
```

**Step 2: Result Merging**

Merge results in post-processing:

```python
def merge_command_results(
    basic: list[dict],
    jobs: list[dict],
    criteria: list[dict]
) -> list[dict]:
    """Merge multiple query results into unified structure."""
    commands = {r['cmd']: {'name': r['name'], 'desc': r['desc']} for r in basic}

    # Add jobs
    for r in jobs:
        cmd = commands.get(r['cmd'])
        if cmd:
            cmd.setdefault('jobs', []).append(r['job'])

    # Add criteria
    for r in criteria:
        cmd = commands.get(r['cmd'])
        if cmd:
            cmd.setdefault('criteria', []).append(r['criterion'])

    return list(commands.values())
```

**Step 3: Caching**

Cache unchanged query results:

```python
@functools.lru_cache(maxsize=100)
def execute_cached_query(query_path: Path, graph_hash: str):
    """Execute query with caching based on graph hash."""
    return execute_query(query_path)
```

### The Results

After optimization:

```
Query execution breakdown:
  command-basic.rq:       0.3s   █░
  command-jobs.rq:        0.4s   ██░
  command-criteria.rq:    0.2s   █░
  command-test.rq:        0.5s   ██░
  command-index.rq:       0.3s   █░
  Merge operations:       0.1s   ░
  Total:                  1.8s   (85% improvement)
```

With caching enabled for unchanged specifications:

```
Cached query reuse:       0.05s  (99.6% improvement on cache hit)
```

---

## Anti-Patterns

### Anti-Pattern: The God Query

*"One query to rule them all—extract everything in a single massive SELECT."*

```sparql
SELECT ?cmd ?name ?desc ?arg ?argName ?opt ?optName ?example ?job ?outcome ...
WHERE {
    # Hundreds of lines of patterns
    # Massive cross-products
    # Unmaintainable mess
}
```

**Resolution:** Focused queries for focused purposes. Compose results in post-processing.

### Anti-Pattern: SELECT *

*"I'll just select everything and filter in Python."*

```sparql
SELECT * WHERE { ?s ?p ?o }  # Returns entire graph!
```

**Resolution:** Always specify exactly what you need.

### Anti-Pattern: Missing ORDER BY

*"Order doesn't matter—I'll sort later."*

Results without ORDER BY are non-deterministic. Different runs might produce different orders, breaking idempotence.

**Resolution:** Always include ORDER BY for consistent results.

### Anti-Pattern: Unoptimized OPTIONAL

*"I'll make everything OPTIONAL for flexibility."*

```sparql
SELECT ?name ?desc ?arg ?opt ?example ?job
WHERE {
    ?cmd a cli:Command .
    OPTIONAL { ?cmd rdfs:label ?name }      # Should be required!
    OPTIONAL { ?cmd sk:description ?desc }  # Should be required!
    OPTIONAL { ?cmd cli:hasArgument ?arg }  # Legitimately optional
    OPTIONAL { ?cmd cli:hasOption ?opt }    # Legitimately optional
}
```

**Resolution:** Only make genuinely optional things OPTIONAL. Required properties should be required.

### Anti-Pattern: Hardcoded URIs

*"I'll just hardcode the full URI in the query."*

```sparql
SELECT ?name WHERE {
    ?cmd <http://spec-kit.dev/cli#Command> ;  # Hardcoded!
         <http://www.w3.org/2000/01/rdf-schema#label> ?name .
}
```

**Resolution:** Use PREFIX declarations for maintainability.

---

## Implementation Checklist

### Query Development

- [ ] Document each query with purpose and usage
- [ ] Use meaningful variable names
- [ ] Include ORDER BY for deterministic results
- [ ] Test queries against sample data
- [ ] Profile query performance
- [ ] Use prefixes, not hardcoded URIs

### Post-Processing

- [ ] Implement reshaping for nested structures
- [ ] Handle type conversions
- [ ] Deduplicate where necessary
- [ ] Sort consistently
- [ ] Handle null/missing values

### Organization

- [ ] Organize queries by domain
- [ ] Share common prefixes
- [ ] Document dependencies between queries
- [ ] Version control query changes

### Performance

- [ ] Profile extraction time
- [ ] Decompose slow queries
- [ ] Implement caching where beneficial
- [ ] Monitor memory usage

---

## Exercises

### Exercise 1: First Extraction

Write your first extraction query:

1. Create a simple RDF specification with 3 commands
2. Write a SPARQL query to extract command names and descriptions
3. Execute the query using rdflib
4. Print the results

### Exercise 2: Hierarchical Extraction

Extract nested data:

1. Add arguments to your commands
2. Write a query extracting commands with their arguments
3. Implement reshaping to produce nested JSON
4. Verify the structure

### Exercise 3: Cross-Vocabulary Query

Span multiple vocabularies:

1. Add JTBD job relationships to commands
2. Write a query extracting commands with their jobs
3. Handle the vocabulary bridging
4. Produce unified output

### Exercise 4: Query Optimization

Optimize a slow query:

1. Create a large specification (100+ commands)
2. Write a complex multi-join query
3. Measure execution time
4. Decompose and optimize
5. Measure improvement

---

## Resulting Context

After implementing this pattern, you have:

- **Structured data** extracted from RDF graphs
- **Template-ready input** for the emission stage
- **Reusable queries** for common extraction patterns
- **Separation of concerns** between extraction logic and template logic
- **Optimizable pipeline** through query profiling and caching
- **Maintainable query library** organized by domain

The extraction stage transforms the graph-shaped specification into the tree-shaped data templates need. This transformation is the key bridge between the flexibility of RDF and the practicality of template rendering.

---

## Related Patterns

- **Part of:** **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₂
- **Follows:** **[22. Normalization Stage](./normalization-stage.md)** — Receives validated RDF
- **Uses:** **[14. Property Path](../specification/property-path.md)** — Navigation syntax
- **Feeds:** **[24. Template Emission](./template-emission.md)** — Data for templates

---

## Philosophical Note

> *"The question is not how to get new ideas, but how to get rid of old ones."*
> — Dee Hock

Extraction queries don't add to the specification—they select and shape what's already there. The specification contains everything; extraction reveals the structure templates need. The art is in asking the right questions, and SPARQL is the language of questions.

---

**Next:** The structured data flows to **[24. Template Emission](./template-emission.md)**, where templates transform data into human-readable artifacts.
