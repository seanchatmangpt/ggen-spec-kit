# How-to: Write Custom SPARQL Queries

**Goal:** Create SPARQL queries to extract specification data
**Time:** 25-30 minutes | **Level:** Advanced

## SPARQL Basics

```sparql
PREFIX sk: <http://ggen-spec-kit.org/spec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?label ?description
WHERE {
    ?command a sk:Command ;
             rdfs:label ?label ;
             sk:description ?description .
}
```

## Query Patterns

### Pattern 1: Find All Commands
```sparql
SELECT ?label WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?label .
}
```

### Pattern 2: Commands with Arguments
```sparql
SELECT ?cmdLabel ?argName WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?cmdLabel ;
         sk:hasArgument ?arg .
    ?arg sk:name ?argName .
}
```

### Pattern 3: Nested Properties
```sparql
SELECT ?module ?argType WHERE {
    ?cmd sk:hasModule ?module ;
         sk:hasArgument [
             sk:type ?argType
         ] .
}
```

## Advanced Features

### FILTER

```sparql
SELECT ?label WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?label .
    FILTER(STRLEN(?label) > 5)
}
```

### OPTIONAL

```sparql
SELECT ?label ?description WHERE {
    ?cmd rdfs:label ?label .
    OPTIONAL {
        ?cmd sk:description ?description .
    }
}
```

### ORDER BY and LIMIT

```sparql
SELECT ?label
WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?label .
}
ORDER BY ?label
LIMIT 10
```

## Integration with ggen

Save query:
```bash
# File: sparql/my-custom-query.rq
# [query content above]
```

Update `docs/ggen.toml`:
```toml
[[transformation]]
sparql = "sparql/my-custom-query.rq"
template = "templates/my-output.tera"
```

Run:
```bash
ggen sync
```

## Tools

**Test queries online:**
- SPARQL Query Editor
- Use local Jena or similar

**Query local RDF:**
```bash
# Install SPARQL endpoint
docker run -d -p 8080:8080 stain/jena-fuseki

# Query
curl http://localhost:8080/ds/query?query=SELECT%20*%20WHERE%20%7B%7D
```

## Best Practices

✅ Use prefixes consistently
✅ Filter early
✅ Limit results
✅ Test before using
✅ Document queries

See: `sparql/` directory for examples
