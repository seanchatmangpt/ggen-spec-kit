# Reference: RDF Ontology

Complete specification of all RDF classes and properties in Spec Kit.

---

## Core Classes

### `sk:Command`
A CLI command.

**Properties:**
- `rdfs:label` (required) - Command name
- `sk:description` (required) - What it does
- `sk:hasModule` (required) - Python module path
- `sk:hasArgument` (optional) - Arguments
- `sk:hasOption` (optional) - Options

**Example:**
```turtle
sk:hello a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet the user" ;
    sk:hasModule "specify_cli.commands.hello" .
```

### `sk:Argument`
A positional or keyword argument for a command.

**Properties:**
- `sk:name` (required) - Argument name
- `sk:type` (required) - Type: "str", "int", "Path"
- `sk:required` (required) - true or false
- `sk:default` (optional) - Default value
- `sk:description` (optional) - Help text

### `sk:Option`
An option/flag for a command.

**Properties:**
- `sk:name` (required) - Option name
- `sk:flag` (required) - Boolean flag
- `sk:description` (optional) - Help text
- `sk:default` (optional) - Default value

### `sk:Feature`
A feature that the system provides.

**Properties:**
- `rdfs:label` (required) - Feature name
- `sk:description` (required) - Description
- `sk:enables` (optional) - What jobs it enables

---

## Archit ecture Classes

### `sk:Layer`
Code organization layer.

**Subtypes:**
- `sk:CommandsLayer` - CLI interface
- `sk:OperationsLayer` - Business logic
- `sk:RuntimeLayer` - I/O and side effects

**Constraints:**
- Commands imports Operations only
- Operations imports nothing (pure)
- Runtime imports Operations

---

## Documentation Classes

See `docs/ontology/documentation.ttl` for:
- `doc:Tutorial`
- `doc:HowToGuide`
- `doc:Reference`
- `doc:Explanation`

---

## Common Properties

| Property | Type | Purpose |
|----------|------|---------|
| `rdfs:label` | Literal | Human-readable name |
| `rdfs:comment` | Literal | Description |
| `sk:description` | Literal | Detailed description |
| `sk:type` | Class | Type specification |
| `sk:required` | Boolean | Required or optional |
| `sk:default` | Literal | Default value |

---

## See Also

- [SPARQL Queries Reference](./sparql-queries.md)
- [SHACL Shapes Reference](./rdf-schema.md)
- File: `ontology/spec-kit-schema.ttl`
- File: `docs/ontology/documentation.ttl`
