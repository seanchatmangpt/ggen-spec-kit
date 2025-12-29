---
paths:
  - "sparql/**/*.rq"
  - "sparql/**/*.sparql"
---

# SPARQL Query Rules

Extract data from RDF for μ transformation pipeline.

## Prefixes
```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX sk: <https://spec-kit.dev/ontology#>
```

## DO
- ✅ One clause per line
- ✅ Uppercase keywords (SELECT, WHERE)
- ✅ Meaningful var names (?command, not ?x)
- ✅ Use OPTIONAL for non-required fields
- ✅ Use BIND for computed values
- ✅ ORDER BY for consistent output

## DON'T
- ❌ Single-line clauses
- ❌ Generic variable names
- ❌ Unfiltered result sets
- ❌ Missing OPTIONAL for nullable data

## SELECT Pattern
```sparql
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
