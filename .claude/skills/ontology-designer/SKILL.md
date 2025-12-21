---
name: ontology-designer
description: Design and extend ontology schemas with classes, properties, and SHACL shapes. Use when creating new RDF classes, defining properties, or writing SHACL validation constraints.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Ontology Designer

Design and extend ontology schemas with classes, properties, and SHACL shapes.

## Instructions

1. Define new RDF classes
2. Create datatype and object properties
3. Write SHACL validation shapes
4. Document ontology elements
5. Test with instances

## Namespace

```turtle
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
```

## Class Definition

```turtle
sk:Feature a rdfs:Class ;
    rdfs:label "Feature" ;
    rdfs:comment "A software feature specification" ;
    rdfs:isDefinedBy sk: .
```

## Property Definition

```turtle
# Datatype property
sk:featureId a owl:DatatypeProperty ;
    rdfs:label "Feature ID" ;
    rdfs:domain sk:Feature ;
    rdfs:range xsd:string .

# Object property
sk:hasRequirement a owl:ObjectProperty ;
    rdfs:label "has requirement" ;
    rdfs:domain sk:Feature ;
    rdfs:range sk:Requirement .
```

## SHACL Shape

```turtle
sk:FeatureShape a sh:NodeShape ;
    sh:targetClass sk:Feature ;

    sh:property [
        sh:path sk:featureId ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z][a-z0-9-]*$" ;
    ] ;

    sh:property [
        sh:path sk:featureTitle ;
        sh:minCount 1 ;
        sh:minLength 3 ;
        sh:maxLength 100 ;
    ] .
```

## Naming Conventions

- **Classes**: PascalCase (`sk:Feature`, `sk:UserStory`)
- **Properties**: camelCase (`sk:featureId`, `sk:hasAuthor`)
- **Shapes**: ClassName + "Shape" (`sk:FeatureShape`)

## Validation

```bash
# Validate ontology syntax
uv run python -c "from rdflib import Graph; g = Graph(); g.parse('ontology/spec-kit-docs-extension.ttl'); print(len(g))"

# Test instance against shape
uv run pyshacl -s ontology/spec-kit-docs-extension.ttl -d tests/fixtures/instance.ttl
```

## Output Format

```markdown
## Ontology Design Summary

### New Classes
| Class | Superclass | Description |
|-------|------------|-------------|
| sk:X | sk:Y | Description |

### New Properties
| Property | Domain | Range | Type |
|----------|--------|-------|------|
| sk:prop | sk:X | xsd:string | Datatype |

### SHACL Shapes
| Shape | Target | Constraints |
|-------|--------|-------------|
| sk:XShape | sk:X | id required, pattern |

### Validation: ✅
```
