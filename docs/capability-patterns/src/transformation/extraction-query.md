# 23. Extraction Query

★★

*RDF is a graph. Templates need structured data. Extraction queries (μ₂) bridge this gap, using SPARQL to select and shape data for emission.*

---

After **[Normalization](./normalization-stage.md)**, you have validated RDF. But RDF is a graph of triples—flexible, interconnected, non-linear. Templates need structured data—lists, records, trees.

Extraction queries bridge this gap. They navigate the RDF graph, select relevant nodes and relationships, and shape the results into structures templates can consume.

Think of extraction as asking questions of the specification:
- "What commands exist and what are their arguments?"
- "What jobs have high-importance, low-satisfaction outcomes?"
- "What acceptance criteria apply to this feature?"

SPARQL answers these questions, producing structured results.

**The problem: RDF graphs don't directly map to template inputs. Extraction queries shape graph data into consumable structures.**

---

**The forces at play:**

- *Flexibility wants rich queries.* SPARQL can do almost anything.

- *Simplicity wants focused queries.* Complex queries are hard to maintain.

- *Reuse wants modular queries.* Same query for multiple templates.

- *Performance wants efficient queries.* Complex queries can be slow.

The tension: powerful enough to extract what's needed, simple enough to maintain.

---

**Therefore:**

Implement extraction (μ₂) using SPARQL queries that produce structured JSON for template consumption.

**Query structure:**

```sparql
# sparql/command-extract.rq
PREFIX cli: <http://github.com/spec-kit/cli#>
PREFIX sk: <http://github.com/spec-kit#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?description ?argName ?argType ?argRequired ?argHelp
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?name ;
         sk:description ?description .

    OPTIONAL {
        ?cmd cli:hasArgument ?arg .
        ?arg sk:name ?argName ;
             cli:type ?argType ;
             cli:required ?argRequired .
        OPTIONAL { ?arg cli:help ?argHelp }
    }
}
ORDER BY ?name ?argName
```

**Query result (JSON):**

```json
{
  "results": {
    "bindings": [
      {
        "name": {"value": "validate"},
        "description": {"value": "Validate RDF files against SHACL shapes"},
        "argName": {"value": "file"},
        "argType": {"value": "Path"},
        "argRequired": {"value": "true"},
        "argHelp": {"value": "File to validate"}
      }
    ]
  }
}
```

**Post-processing:**

Raw SPARQL results often need reshaping:

```python
# Group arguments by command
def reshape_commands(sparql_results):
    commands = {}
    for row in sparql_results:
        name = row['name']
        if name not in commands:
            commands[name] = {
                'name': name,
                'description': row['description'],
                'arguments': []
            }
        if row.get('argName'):
            commands[name]['arguments'].append({
                'name': row['argName'],
                'type': row['argType'],
                'required': row['argRequired'] == 'true',
                'help': row.get('argHelp', '')
            })
    return list(commands.values())
```

**Template-ready output:**

```json
[
  {
    "name": "validate",
    "description": "Validate RDF files against SHACL shapes",
    "arguments": [
      {
        "name": "file",
        "type": "Path",
        "required": true,
        "help": "File to validate"
      }
    ]
  }
]
```

**Query patterns:**

**Flat extraction:** Simple list of properties
```sparql
SELECT ?name ?description WHERE {
    ?cmd a cli:Command ; rdfs:label ?name ; sk:description ?description .
}
```

**Hierarchical extraction:** Parent with children
```sparql
SELECT ?cmdName ?argName ?argType WHERE {
    ?cmd a cli:Command ; rdfs:label ?cmdName ; cli:hasArgument ?arg .
    ?arg sk:name ?argName ; cli:type ?argType .
}
```

**Cross-domain extraction:** Spanning vocabularies
```sparql
SELECT ?cmdName ?jobLabel ?outcomeName WHERE {
    ?cmd a cli:Command ; rdfs:label ?cmdName ; cli:accomplishesJob ?job .
    ?job rdfs:label ?jobLabel ; jtbd:hasOutcome ?outcome .
    ?outcome rdfs:label ?outcomeName .
}
```

---

**Resulting context:**

After applying this pattern, you have:

- Structured data extracted from RDF graphs
- Template-ready input for emission
- Reusable queries for common extractions
- Separation of extraction logic from template logic

This feeds **[Template Emission](./template-emission.md)** and contributes to **[Receipt Generation](./receipt-generation.md)**.

---

**Related patterns:**

- *Part of:* **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₂
- *Follows:* **[22. Normalization Stage](./normalization-stage.md)** — Receives validated RDF
- *Uses:* **[14. Property Path](../specification/property-path.md)** — Navigation syntax
- *Feeds:* **[24. Template Emission](./template-emission.md)** — Data for templates

---

> *"The question is not how to get new ideas, but how to get rid of old ones."*
>
> — Dee Hock

Extraction queries don't add to the specification—they select and shape what's already there, revealing the structure templates need.
