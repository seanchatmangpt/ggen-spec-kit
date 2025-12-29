---
name: sparql-analyst
description: Write and optimize SPARQL queries for RDF data extraction. Use when creating queries for ggen transformations, extracting data from TTL files, or optimizing query performance.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# SPARQL Analyst

Write and optimize SPARQL queries for extracting data from RDF graphs.

## Trigger Conditions

- Creating ggen extraction queries
- Optimizing query performance
- Aligning queries with Tera templates
- Testing data extraction

## Key Capabilities

- SPARQL query authoring (SELECT, OPTIONAL, FILTER)
- Performance optimization
- Query testing against graphs
- Template variable binding

## Integration

**ggen v5.0.2**: SPARQL queries execute in μ₂ extraction phase
**Architecture**: Ops layer (μ₂ data extraction, pure logic)

## Instructions

1. Create SPARQL queries for data extraction
2. Optimize query performance
3. Align queries with Tera templates
4. Test queries against data
5. Document bindings

## Query Location

```
sparql/
├── guide-query.rq
├── principle-query.rq
├── changelog-query.rq
├── config-query.rq
└── workflow-query.rq
```

## Basic Patterns

### Simple SELECT
```sparql
PREFIX sk: <http://github.com/github/spec-kit#>

SELECT ?feature ?title ?description
WHERE {
    ?feature a sk:Feature ;
        sk:featureTitle ?title ;
        sk:featureDescription ?description .
}
ORDER BY ?title
```

### With Optional
```sparql
SELECT ?feature ?title ?status
WHERE {
    ?feature a sk:Feature ;
        sk:featureTitle ?title .
    OPTIONAL { ?feature sk:featureStatus ?status }
}
```

### Filtering
```sparql
SELECT ?feature ?title
WHERE {
    ?feature a sk:Feature ;
        sk:featureTitle ?title ;
        sk:featureStatus ?status .
    FILTER (?status IN ("planned", "in-progress"))
}
```

### Property Paths
```sparql
# Navigate relationships
SELECT ?feature ?authorName
WHERE {
    ?feature sk:hasAuthor/sk:authorName ?authorName .
}
```

## Testing Queries

```bash
uv run python -c "
from rdflib import Graph
g = Graph()
g.parse('memory/philosophy.ttl')

query = '''
PREFIX sk: <http://github.com/github/spec-kit#>
SELECT ?id ?title
WHERE {
    ?p a sk:Principle ;
        sk:principleId ?id ;
        sk:principleTitle ?title .
}
'''

for row in g.query(query):
    print(f'{row.id}: {row.title}')
"
```

## Optimization Tips

```sparql
# ❌ Slow: Generic pattern first
SELECT ?x ?title
WHERE {
    ?x ?p ?o .
    ?x a sk:Feature .
    ?x sk:featureTitle ?title .
}

# ✅ Fast: Specific pattern first
SELECT ?x ?title
WHERE {
    ?x a sk:Feature ;
        sk:featureTitle ?title .
}
```

## Output Format

```markdown
## SPARQL Query Report

### Query File: `sparql/query.rq`

### Bindings
| Variable | Type | Description |
|----------|------|-------------|
| ?feature | URI | Feature resource |
| ?title | String | Title |

### Test Results
| feature | title |
|---------|-------|
| sk:F1 | "Auth" |

### Template Integration
- Template: `templates/feature.tera`
- Uses: `results` array
```
