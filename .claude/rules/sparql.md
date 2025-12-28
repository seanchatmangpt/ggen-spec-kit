---
paths:
  - "sparql/**/*.rq"
  - "sparql/**/*.sparql"
---

# SPARQL Query Rules

## Purpose
SPARQL queries extract data from RDF for the μ transformation pipeline.

## Standard Prefixes
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX sk: <https://spec-kit.dev/ontology#>
```

## Formatting
- One clause per line
- Uppercase keywords (SELECT, WHERE, FILTER)
- Indent nested patterns
- Use meaningful variable names (?command, ?name, not ?x, ?y)

## SELECT Pattern
```sparql
PREFIX sk: <https://spec-kit.dev/ontology#>

SELECT ?command ?name ?description
WHERE {
    ?command a sk:Command ;
             rdfs:label ?name ;
             sk:description ?description .

    OPTIONAL {
        ?command sk:hasArgument ?arg .
        ?arg sk:name ?argName .
    }
}
ORDER BY ?name
```

## CONSTRUCT Pattern
```sparql
PREFIX sk: <https://spec-kit.dev/ontology#>

CONSTRUCT {
    ?command sk:fullSpec ?spec .
}
WHERE {
    ?command a sk:Command ;
             rdfs:label ?name ;
             sk:description ?desc .
    BIND(CONCAT(?name, ": ", ?desc) AS ?spec)
}
```

## Best Practices
- Use OPTIONAL for non-required fields
- Use BIND for computed values
- Use FILTER for conditions
- Use ORDER BY for consistent output
- Test queries with sample data first
