# RDF Development Context

## Active When
Working with files in `ontology/`, `memory/`, `sparql/`, or `templates/`.

## Key Principles

### Source of Truth
RDF files are the source of truth. Never edit generated files.

### The Equation
```
spec.md = μ(feature.ttl)
```

### File Relationships
```
ontology/*.ttl  →  SPARQL query  →  Tera template  →  Generated file
     ↓                  ↓                 ↓                 ↓
   Schema           Extraction         Rendering          Output
```

## Common Patterns

### Adding a New Command
1. Edit `ontology/cli-commands.ttl`
2. Define command with arguments/options
3. Run `ggen sync`
4. Implement ops/runtime logic

### Updating Documentation
1. Edit `memory/*.ttl`
2. Run `ggen sync`
3. Verify generated docs

### Changing a Template
1. Edit `templates/*.tera`
2. Run `ggen sync`
3. Verify output format

## Validation

Before committing RDF changes:
```bash
# Validate Turtle syntax
rapper -q -i turtle ontology/file.ttl

# Run transformation
ggen sync

# Run tests
uv run pytest tests/
```

## Prefixes Reference

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <https://spec-kit.dev/ontology#> .
```
