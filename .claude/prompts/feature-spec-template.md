# Feature Specification Prompt Template

## Variables
- `{{feature_name}}` - Name of the feature
- `{{description}}` - Feature description
- `{{requirements}}` - Specific requirements

## Template

Create an RDF specification for the following feature:

### Feature Name
{{feature_name}}

### Description
{{description}}

### Requirements
{{requirements}}

## Output Format

Generate the following files:

### 1. RDF Specification (`ontology/cli-commands.ttl`)

```turtle
@prefix sk: <https://spec-kit.dev/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

sk:{{feature_name}}
    a sk:Command ;
    rdfs:label "{{feature_name}}" ;
    sk:description "{{description}}" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "arg_name" ;
        sk:type "type" ;
        sk:required true/false ;
        sk:description "Argument description"
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:name "option_name" ;
        sk:short "-o" ;
        sk:type "type" ;
        sk:default "default_value" ;
        sk:description "Option description"
    ] .
```

### 2. SPARQL Query (if needed)

```sparql
PREFIX sk: <https://spec-kit.dev/ontology#>

SELECT ?feature ?name ?description
WHERE {
    ?feature a sk:Command ;
             rdfs:label ?name ;
             sk:description ?description .
}
```

### 3. Tera Template (if needed)

```jinja
# Generated from RDF specification
# DO NOT EDIT MANUALLY

{{ description }}
```

## Verification Checklist

- [ ] RDF follows Turtle syntax correctly
- [ ] All required prefixes declared
- [ ] Arguments have types and descriptions
- [ ] Options have defaults and short forms
- [ ] SHACL shape validates the specification
