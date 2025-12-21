---
name: spec-writer
description: Create and maintain RDF/Turtle specifications following the constitutional equation spec.md = μ(feature.ttl). Use when writing feature specs, requirements, user stories, or any RDF specification.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Specification Writer

Create RDF/Turtle specifications that drive code generation through the constitutional equation.

## Instructions

1. Write Turtle RDF for features, requirements, or stories
2. Validate syntax with rdflib
3. Ensure SHACL compliance
4. Align with Tera templates
5. Generate documentation with ggen sync

## Constitutional Equation

```
specification.md = μ(feature.ttl)
```

## Specification Types

### Feature
```turtle
@prefix sk: <http://github.com/github/spec-kit#> .

sk:FeatureName a sk:Feature ;
    sk:featureId "feature-id" ;
    sk:featureTitle "Feature Title" ;
    sk:featureDescription "Description" ;
    sk:featureStatus "planned" ;
    sk:hasRequirement sk:Req1 ;
    .
```

### Requirement
```turtle
sk:Req1 a sk:Requirement ;
    sk:requirementId "REQ-001" ;
    sk:requirementTitle "Title" ;
    sk:requirementDescription "Description" ;
    sk:requirementPriority "must-have" ;
    .
```

### User Story
```turtle
sk:Story1 a sk:UserStory ;
    sk:storyId "US-001" ;
    sk:asA "developer" ;
    sk:iWant "to initialize a project" ;
    sk:soThat "I can start developing" ;
    .
```

## Locations

```
ontology/spec-kit-schema.ttl          # Core ontology
ontology/spec-kit-docs-extension.ttl  # Documentation extension
memory/*.ttl                          # Specifications
docs/*.ttl                            # Guide specs
```

## Validation

```bash
# Validate RDF syntax
uv run python -c "from rdflib import Graph; g = Graph(); g.parse('path/to/spec.ttl'); print(f'Valid: {len(g)} triples')"

# Generate with ggen (reads ggen.toml from CWD)
cd docs/ && ggen sync
```

## Output Format

```markdown
## Specification Created

### File: `specs/features/feature-name.ttl`

### RDF Summary
- Triples: X
- Classes: Feature, Requirement
- Valid: ✅

### Generation
```bash
# Run ggen sync from the directory containing ggen.toml
cd docs/ && ggen sync
```
```
