---
paths:
  - "ontology/**/*.ttl"
  - "memory/**/*.ttl"
  - "**/*.turtle"
---

# RDF/Turtle Rules

## Purpose
RDF files are the SOURCE OF TRUTH per the constitutional equation.

## Prefixes
Always declare standard prefixes:
```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sk: <https://spec-kit.dev/ontology#> .
```

## Formatting
- One triple per line for readability
- Blank line between subjects
- Use `;` for multiple predicates on same subject
- Use `,` for multiple objects on same predicate
- Indent continuation lines with 4 spaces

## Pattern
```turtle
sk:MyCommand
    a sk:Command ;
    rdfs:label "my-command" ;
    sk:description "Description of the command" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "input" ;
        sk:type "Path" ;
        sk:required true ;
        sk:description "Input file path"
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:name "verbose" ;
        sk:short "-v" ;
        sk:type "bool" ;
        sk:default "false"
    ] .
```

## Validation
- All resources should have `rdfs:label`
- Commands should have `sk:description`
- Arguments should specify `sk:type` and `sk:required`
- Use SHACL shapes for validation

## After Editing
Always run `ggen sync` after editing TTL files to regenerate code.
