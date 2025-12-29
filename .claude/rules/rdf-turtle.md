---
paths:
  - "ontology/**/*.ttl"
  - "memory/**/*.ttl"
  - "**/*.turtle"
---

# RDF/Turtle Rules

SOURCE OF TRUTH. Edit RDF first, generate code/docs via `ggen sync`.

## Prefixes
```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sk: <https://spec-kit.dev/ontology#> .
```

## Formatting
- ✅ One triple per line
- ✅ Blank line between subjects
- ✅ Use `;` for multiple predicates
- ✅ Use `,` for multiple objects
- ✅ 4-space indent on continuation
- ❌ Multiple triples on one line
- ❌ Inconsistent indentation

## Pattern
```turtle
sk:MyCommand
    a sk:Command ;
    rdfs:label "my-command" ;
    sk:description "Command description" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "input" ;
        sk:type "Path" ;
        sk:required true
    ] .
```

## Validation
- ✅ All resources have `rdfs:label`
- ✅ Commands have `sk:description`
- ✅ Args specify `sk:type` and `sk:required`
- ✅ Run `ggen sync` after editing
- ❌ Missing labels or descriptions
- ❌ Inconsistent property naming
