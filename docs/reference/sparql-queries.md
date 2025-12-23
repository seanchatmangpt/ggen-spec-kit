# Reference: SPARQL Queries

Available SPARQL query templates for extracting specification data.

## command-extract.rq

Extract CLI command metadata from RDF.

**Returns:**
- Command name (label)
- Description
- Module path
- Arguments
- Options

**Usage:**
```bash
ggen sync --sparql sparql/command-extract.rq
```

**Example Result:**
```json
{
  "commands": [
    {
      "label": "hello",
      "description": "Greet the user",
      "module": "specify_cli.commands.hello"
    }
  ]
}
```

## docs-extract.rq

Extract documentation specifications.

**Returns:**
- Document titles
- Content
- Relationships
- Prerequisites

## changelog-extract.rq

Extract changelog entries.

**Returns:**
- Version
- Date
- Changes
- Categories

## Writing Custom Queries

Template:
```sparql
PREFIX sk: <http://ggen-spec-kit.org/spec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?label ?description WHERE {
    ?subject rdfs:label ?label ;
             sk:description ?description .
}
```

See: `sparql/` directory for more examples.
