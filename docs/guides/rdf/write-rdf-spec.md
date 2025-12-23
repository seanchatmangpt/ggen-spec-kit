# How-to: Write Complete RDF Specifications

**Goal:** Write comprehensive RDF specifications for all feature types
**Time:** 30-40 minutes | **Level:** Intermediate

## Getting Started

RDF uses Turtle syntax. Basic command:

```turtle
@prefix sk: <http://ggen-spec-kit.org/spec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

sk:myfeature
    a sk:Command ;
    rdfs:label "myfeature" ;
    sk:description "Description" .
```

## CLI Command Specification

**Simple command:**
```turtle
sk:hello
    a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet the user" ;
    sk:hasModule "specify_cli.commands.hello" .
```

**With arguments:**
```turtle
sk:greet
    a sk:Command ;
    rdfs:label "greet" ;
    sk:description "Greet a person" ;
    sk:hasModule "specify_cli.commands.greet" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "name" ;
        sk:description "Name to greet" ;
        sk:required true ;
        sk:type "str"
    ] ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "greeting" ;
        sk:description "Greeting word" ;
        sk:required false ;
        sk:default "Hello" ;
        sk:type "str"
    ] .
```

**With options:**
```turtle
sk:process
    a sk:Command ;
    rdfs:label "process" ;
    sk:description "Process data" ;
    sk:hasModule "specify_cli.commands.process" ;
    sk:hasOption [
        a sk:Option ;
        sk:name "verbose" ;
        sk:description "Verbose output" ;
        sk:flag true
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:name "format" ;
        sk:description "Output format" ;
        sk:flag false ;
        sk:default "json"
    ] .
```

## Feature Specification

Describe what feature accomplishes:

```turtle
spec:UserGreeting
    a spec:Feature ;
    rdfs:label "User Greeting" ;
    spec:job "Greet users personally" ;
    spec:outcome "Users feel welcomed" ;
    spec:priority "high" ;
    spec:implementedBy sk:greet .
```

## Architecture Specification

Specify system components:

```turtle
arch:GreetingModule
    a arch:Component ;
    rdfs:label "Greeting Module" ;
    arch:implements spec:UserGreeting ;
    arch:layer "operations" ;
    arch:contains [
        a arch:Module ;
        arch:path "specify_cli/ops/greet.py"
    ] .
```

## Validation

```bash
# Check syntax
ggen validate ontology/cli-commands.ttl

# Full validation
ggen validate --shapes ontology/spec-kit-schema.ttl ontology/cli-commands.ttl
```

## Best Practices

✅ Use prefixes consistently
✅ Include descriptions
✅ Define all required properties
✅ Validate before running ggen
✅ Comment complex specs

## Patterns

Common patterns:

```turtle
# Pattern 1: Simple command (no args)
sk:hello a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Say hello" .

# Pattern 2: Command with arguments
sk:greet a sk:Command ;
    sk:hasArgument [ sk:name "name" ; ... ] .

# Pattern 3: Command with options
sk:process a sk:Command ;
    sk:hasOption [ sk:name "verbose" ; ... ] .

# Pattern 4: Command with sub-commands
sk:admin
    sk:hasSubcommand sk:admin-add ;
    sk:hasSubcommand sk:admin-remove .
```

See: `ontology/cli-commands.ttl` for more examples
