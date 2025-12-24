# 16. Layered Ontology

★★

*Not all concepts are created equal. Some are foundational and stable. Others are domain-specific and evolving. Layered ontologies separate levels of abstraction, enabling reuse while allowing specialization. They are the geological strata of your knowledge architecture—each layer building on those below, each serving a distinct purpose.*

---

## The Complexity of Growing Knowledge

Your ontology grows. You add classes for commands, jobs, outcomes, metrics. Each concept connects to others. Before long, you have a web of definitions that's hard to navigate, change, or reuse.

The problem is mixing levels. Consider what happens in a typical ontology:

```turtle
# The tangled mess of a flat ontology
@prefix ex: <http://example.org/> .

# Universal concept mixed in
ex:name a rdf:Property .
ex:description a rdf:Property .

# Framework concept
ex:Command a rdfs:Class .

# Domain-specific concept
ex:ValidateCommand a rdfs:Class ;
    rdfs:subClassOf ex:Command .

# Instance data
ex:validate a ex:ValidateCommand ;
    ex:name "validate" .

# Another domain's concept
ex:Job a rdfs:Class .

# Cross-domain relationship (where does it belong?)
ex:accomplishesJob a rdf:Property ;
    rdfs:domain ex:Command ;
    rdfs:range ex:Job .
```

What's wrong with this? Several things:

1. **Universal concepts** (name, description) mixed with **domain concepts** (Command, Job)
2. **Class definitions** mixed with **instance data**
3. **No clear reuse boundaries**—you can't take just the framework without dragging in domains
4. **Change ripples unpredictably**—modifying a framework concept might break domain code
5. **No import hygiene**—everything sees everything

This flat structure becomes untenable as the ontology grows beyond a few hundred triples.

---

## The Problem Statement

**Flat ontologies mix universal, framework, domain, and instance levels, creating tangled dependencies that prevent reuse, obscure structure, and make evolution hazardous.**

The symptoms of flat ontology:
- **Difficult reuse**: Can't extract just the parts you need
- **Scary changes**: Any modification might break something
- **Learning curve**: New team members can't find entry points
- **Namespace confusion**: What belongs where is unclear
- **Testing complexity**: Can't test layers in isolation
- **Version conflicts**: Upgrading one thing upgrades everything

---

## The Forces at Play

### Force 1: Simplicity vs. Structure

**Simplicity wants one layer.** Fewer files, fewer imports, less ceremony. Just put everything in one place and be done with it.

**Structure wants separation.** Clear organization helps understanding, maintenance, and reuse. The complexity of multiple files pays off at scale.

```
Simplicity ←────────────────────────────→ Structure
(one file, no imports)                     (many files, clear layers)
```

### Force 2: Reuse vs. Specificity

**Reuse wants abstraction.** Generic concepts should be reusable across domains. A framework for CLI commands should work for any CLI, not just yours.

**Specificity wants customization.** Your domain has unique needs. Generic frameworks never quite fit. You need room for domain-specific concepts.

```
Reuse ←──────────────────────────────────→ Specificity
(abstract, generic)                        (concrete, specialized)
```

### Force 3: Stability vs. Evolution

**Stability wants immutability.** Universal standards shouldn't change. Framework concepts should be stable. Changes ripple too far.

**Evolution wants freedom.** Domains grow and adapt. New requirements emerge. The ontology must evolve with the business.

```
Stability ←──────────────────────────────→ Evolution
(change is dangerous)                      (change is necessary)
```

### Force 4: Integration vs. Isolation

**Integration wants connection.** Domains need to reference each other. Commands accomplish Jobs. Documents describe Commands. Everything connects.

**Isolation wants boundaries.** Changes in one domain shouldn't break others. Teams should work independently. Modules should be replaceable.

```
Integration ←────────────────────────────→ Isolation
(everything connected)                     (boundaries maintained)
```

---

## Therefore: Organize Concepts in Distinct Layers

**Create a layered architecture for your ontology, where each layer builds on those below, has clear responsibilities, and maintains explicit import relationships.**

### The Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Domain Instances                                   │
│  ─────────────────────────────────────────────────────────  │
│  Actual data: specific commands, jobs, outcomes, tests      │
│  Changes: Frequently (daily/weekly)                         │
│  Team: Domain experts, specification authors                │
│  Files: memory/*.ttl, specs/*.ttl                          │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ imports
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Domain Schemas                                     │
│  ─────────────────────────────────────────────────────────  │
│  Domain classes: Command, Job, Outcome, Document            │
│  Changes: Occasionally (monthly/quarterly)                  │
│  Team: Domain architects                                    │
│  Files: ontology/cli-schema.ttl, ontology/jtbd-schema.ttl  │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ imports
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Framework Core                                     │
│  ─────────────────────────────────────────────────────────  │
│  Base classes: Entity, Specification, Artifact              │
│  Common properties: name, description, version              │
│  Changes: Rarely (annually/never)                           │
│  Team: Framework maintainers                                │
│  Files: ontology/core/framework.ttl                        │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │ imports
┌─────────────────────────────────────────────────────────────┐
│  Layer 0: External Standards                                 │
│  ─────────────────────────────────────────────────────────  │
│  W3C standards: RDF, RDFS, OWL, SHACL, XSD                  │
│  Changes: Never (externally controlled)                     │
│  Team: W3C                                                  │
│  Files: (standard URIs, not local files)                   │
└─────────────────────────────────────────────────────────────┘
```

### Layer 0: External Standards

These are the bedrock—universal standards you build upon but never modify:

```turtle
# You don't create these—you just reference them
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
```

**Characteristics:**
- Externally maintained by standards bodies
- Universally understood semantics
- Maximum interoperability
- Never modify, only use

### Layer 1: Framework Core

Your universal building blocks—concepts that apply across all your domains:

```turtle
# ontology/core/framework.ttl
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Ontology metadata
<https://spec-kit.io/ontology> a owl:Ontology ;
    rdfs:label "Spec-Kit Framework Core" ;
    owl:versionInfo "2.0.0" ;
    rdfs:comment """
        The foundational layer of the Spec-Kit ontology.
        Contains universal concepts used across all domains.
    """ .

# Base entity class
sk:Entity a rdfs:Class ;
    rdfs:label "Entity" ;
    rdfs:comment """
        Base class for all Spec-Kit entities.
        Provides common properties and behaviors.
    """ .

# Universal properties
sk:name a rdf:Property ;
    rdfs:label "name" ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable name" .

sk:description a rdf:Property ;
    rdfs:label "description" ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable description" .

sk:identifier a rdf:Property ;
    rdfs:label "identifier" ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:string ;
    rdfs:comment "Machine-readable identifier" .

sk:version a rdf:Property ;
    rdfs:label "version" ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:string ;
    rdfs:comment "Semantic version string" .

sk:createdAt a rdf:Property ;
    rdfs:label "created at" ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "Creation timestamp" .

sk:modifiedAt a rdf:Property ;
    rdfs:label "modified at" ;
    rdfs:domain sk:Entity ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "Last modification timestamp" .

# Lifecycle states
sk:Status a rdfs:Class ;
    rdfs:label "Status" ;
    rdfs:comment "Lifecycle status of an entity" .

sk:Draft a sk:Status ;
    rdfs:label "Draft" .

sk:Active a sk:Status ;
    rdfs:label "Active" .

sk:Deprecated a sk:Status ;
    rdfs:label "Deprecated" .

sk:Archived a sk:Status ;
    rdfs:label "Archived" .

sk:status a rdf:Property ;
    rdfs:domain sk:Entity ;
    rdfs:range sk:Status .

# Relationship primitives
sk:dependsOn a rdf:Property ;
    rdfs:label "depends on" ;
    rdfs:domain sk:Entity ;
    rdfs:range sk:Entity ;
    rdfs:comment "Generic dependency relationship" .

sk:relatedTo a rdf:Property ;
    rdfs:label "related to" ;
    rdfs:domain sk:Entity ;
    rdfs:range sk:Entity ;
    a owl:SymmetricProperty ;
    rdfs:comment "Generic bidirectional relationship" .
```

**Characteristics:**
- Your stable foundation
- Reused by all domain schemas
- Changes require careful versioning
- Maximum internal reuse

### Layer 2: Domain Schemas

Domain-specific classes that use the framework core:

```turtle
# ontology/cli/schema.ttl
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Ontology metadata with import
<https://spec-kit.io/ontology/cli> a owl:Ontology ;
    rdfs:label "CLI Domain Schema" ;
    owl:imports <https://spec-kit.io/ontology> ;
    owl:versionInfo "1.5.0" ;
    rdfs:comment "Domain schema for CLI command specifications" .

# Domain classes
cli:Command a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Command" ;
    rdfs:comment "A CLI command that users can invoke" .

cli:Argument a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Argument" ;
    rdfs:comment "A positional argument to a command" .

cli:Option a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Option" ;
    rdfs:comment "A flag or option for a command" .

cli:SubCommand a rdfs:Class ;
    rdfs:subClassOf cli:Command ;
    rdfs:label "Sub-Command" ;
    rdfs:comment "A command that is part of another command" .

# Command specializations
cli:ValidationCommand a rdfs:Class ;
    rdfs:subClassOf cli:Command ;
    rdfs:label "Validation Command" ;
    rdfs:comment "A command that validates something" .

cli:GenerationCommand a rdfs:Class ;
    rdfs:subClassOf cli:Command ;
    rdfs:label "Generation Command" ;
    rdfs:comment "A command that generates artifacts" .

cli:QueryCommand a rdfs:Class ;
    rdfs:subClassOf cli:Command ;
    rdfs:label "Query Command" ;
    rdfs:comment "A command that queries for information" .

# Domain properties
cli:hasArgument a rdf:Property ;
    rdfs:label "has argument" ;
    rdfs:domain cli:Command ;
    rdfs:range cli:Argument .

cli:hasOption a rdf:Property ;
    rdfs:label "has option" ;
    rdfs:domain cli:Command ;
    rdfs:range cli:Option .

cli:hasSubCommand a rdf:Property ;
    rdfs:label "has sub-command" ;
    rdfs:domain cli:Command ;
    rdfs:range cli:SubCommand .

cli:type a rdf:Property ;
    rdfs:label "type" ;
    rdfs:comment "Data type of argument or option" ;
    rdfs:range xsd:string .

cli:required a rdf:Property ;
    rdfs:label "required" ;
    rdfs:range xsd:boolean .

cli:default a rdf:Property ;
    rdfs:label "default value" ;
    rdfs:range xsd:string .

cli:help a rdf:Property ;
    rdfs:label "help text" ;
    rdfs:range xsd:string .

cli:exitCode a rdf:Property ;
    rdfs:label "exit code" ;
    rdfs:domain cli:Command ;
    rdfs:range xsd:integer .
```

```turtle
# ontology/jtbd/schema.ttl
@prefix jtbd: <https://spec-kit.io/ontology/jtbd#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<https://spec-kit.io/ontology/jtbd> a owl:Ontology ;
    rdfs:label "JTBD Domain Schema" ;
    owl:imports <https://spec-kit.io/ontology> ;
    owl:versionInfo "1.2.0" .

# Core JTBD classes
jtbd:Job a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Job" ;
    rdfs:comment "A job that customers are trying to accomplish" .

jtbd:Outcome a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Outcome" ;
    rdfs:comment "A desired outcome of accomplishing a job" .

jtbd:Circumstance a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Circumstance" ;
    rdfs:comment "The situation in which a job arises" .

jtbd:ProgressMaker a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Progress Maker" ;
    rdfs:comment "Something that helps make progress on a job" .

# JTBD properties
jtbd:hasOutcome a rdf:Property ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:Outcome .

jtbd:inCircumstance a rdf:Property ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:Circumstance .

jtbd:direction a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range [ owl:oneOf ("minimize" "maximize") ] .

jtbd:metric a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string .
```

**Characteristics:**
- Each domain has its own namespace
- Imports only from Layer 1 (and Layer 0)
- Peer domains don't import each other directly
- Domain architects own these schemas

### Layer 3: Domain Instances

Actual specification data—the content that changes frequently:

```turtle
# memory/cli-commands.ttl
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix : <https://spec-kit.io/specs/commands#> .

# Actual command instances
:validate a cli:ValidationCommand ;
    sk:name "validate" ;
    sk:description "Validate RDF/Turtle files against SHACL shapes" ;
    sk:identifier "validate" ;
    sk:version "1.0.0" ;
    sk:status sk:Active ;
    cli:hasArgument :validate_file_arg ;
    cli:hasOption :validate_strict_opt .

:validate_file_arg a cli:Argument ;
    sk:name "file" ;
    cli:type "Path" ;
    cli:required true ;
    cli:help "The file to validate" .

:validate_strict_opt a cli:Option ;
    sk:name "--strict" ;
    cli:type "bool" ;
    cli:default "false" ;
    cli:help "Enable strict validation mode" .

# Another command instance
:generate a cli:GenerationCommand ;
    sk:name "generate" ;
    sk:description "Generate artifacts from specifications" ;
    sk:version "2.0.0" ;
    sk:status sk:Active ;
    cli:hasArgument :generate_spec_arg ;
    cli:hasOption :generate_output_opt .
```

**Characteristics:**
- The bulk of your content lives here
- Changes frequently as specs evolve
- Domain experts author this layer
- Validated against Layer 2 schemas

---

## Cross-Domain Integration

Domains need to connect, but direct imports create coupling. Use explicit bridge vocabularies:

### Bridge Vocabularies

```turtle
# ontology/bridges/cli-jtbd.ttl
@prefix bridge: <https://spec-kit.io/ontology/bridge#> .
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix jtbd: <https://spec-kit.io/ontology/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

<https://spec-kit.io/ontology/bridge/cli-jtbd> a owl:Ontology ;
    rdfs:label "CLI-JTBD Bridge" ;
    owl:imports <https://spec-kit.io/ontology/cli> ;
    owl:imports <https://spec-kit.io/ontology/jtbd> .

# Cross-domain properties
bridge:accomplishesJob a rdf:Property ;
    rdfs:label "accomplishes job" ;
    rdfs:domain cli:Command ;
    rdfs:range jtbd:Job ;
    rdfs:comment "Links CLI commands to the jobs they accomplish" .

bridge:deliversOutcome a rdf:Property ;
    rdfs:label "delivers outcome" ;
    rdfs:domain cli:Command ;
    rdfs:range jtbd:Outcome ;
    rdfs:comment "Links CLI commands to outcomes they deliver" .
```

### Using the Bridge

```turtle
# memory/cli-jtbd-mappings.ttl
@prefix bridge: <https://spec-kit.io/ontology/bridge#> .
@prefix cmd: <https://spec-kit.io/specs/commands#> .
@prefix job: <https://spec-kit.io/specs/jobs#> .

cmd:validate
    bridge:accomplishesJob job:ValidateOntology ;
    bridge:deliversOutcome job:MinimizeValidationTime ;
    bridge:deliversOutcome job:EnsureCorrectness .
```

---

## Import Discipline

Each layer imports only from layers below—never from peers or above:

```
Layer 3 (Instances)
   │
   │ imports Layer 2 schemas
   │ imports Layer 1 core
   │ imports Layer 0 standards
   │
   ▼
Layer 2 (Domain Schemas)
   │
   │ imports Layer 1 core
   │ imports Layer 0 standards
   │ NEVER imports peer domains
   │
   ▼
Layer 1 (Framework Core)
   │
   │ imports Layer 0 standards only
   │
   ▼
Layer 0 (External Standards)
   │
   │ (nothing to import)
```

### Enforcing Import Discipline with SHACL

```turtle
# shapes/import-rules.ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

sk:ImportDisciplineShape a sh:NodeShape ;
    sh:targetClass owl:Ontology ;
    sh:message "Ontology import discipline violation" ;

    # Layer 2 schemas cannot import peer domains
    sh:sparql [
        sh:select """
            SELECT $this ?import WHERE {
                $this owl:imports ?import .
                # Check if both are Layer 2 and peers
                FILTER(
                    CONTAINS(STR($this), '/ontology/') &&
                    CONTAINS(STR(?import), '/ontology/') &&
                    !CONTAINS(STR(?import), '/core/') &&
                    !CONTAINS(STR(?import), '/bridge/')
                )
            }
        """ ;
        sh:message "Layer 2 schemas cannot import peer domain schemas directly. Use a bridge vocabulary."
    ] .
```

---

## Layer Structure Visualization

```
┌───────────────────────────────────────────────────────────────────────┐
│                        LAYER 0: EXTERNAL STANDARDS                     │
│                                                                         │
│   ┌─────┐  ┌─────┐  ┌─────┐  ┌──────┐  ┌─────┐                        │
│   │ RDF │  │RDFS │  │ OWL │  │SHACL │  │ XSD │                        │
│   └─────┘  └─────┘  └─────┘  └──────┘  └─────┘                        │
│         ▲        ▲        ▲         ▲        ▲                         │
└─────────┼────────┼────────┼─────────┼────────┼─────────────────────────┘
          │        │        │         │        │
┌─────────┴────────┴────────┴─────────┴────────┴─────────────────────────┐
│                        LAYER 1: FRAMEWORK CORE                          │
│                                                                         │
│   ┌─────────────────────────────────────────────────────────┐          │
│   │                    sk: (spec-kit core)                   │          │
│   │  Entity, name, description, version, Status, ...        │          │
│   └─────────────────────────────────────────────────────────┘          │
│                              ▲                                          │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────────────┐
│                        LAYER 2: DOMAIN SCHEMAS                          │
│                                                                         │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐                │
│  │  cli:        │   │  jtbd:       │   │  docs:       │                │
│  │  Command     │   │  Job         │   │  Document    │                │
│  │  Argument    │   │  Outcome     │   │  Section     │                │
│  │  Option      │   │  Circumstance│   │  Topic       │                │
│  └──────────────┘   └──────────────┘   └──────────────┘                │
│         │                  │                  │                         │
│         └────────┬─────────┴──────────┬──────┘                         │
│                  │                    │                                 │
│         ┌────────┴────────┐   ┌───────┴───────┐                        │
│         │ bridge:cli-jtbd │   │bridge:jtbd-docs│                        │
│         └─────────────────┘   └───────────────┘                        │
│                              ▲                                          │
└──────────────────────────────┼──────────────────────────────────────────┘
                               │
┌──────────────────────────────┴──────────────────────────────────────────┐
│                        LAYER 3: DOMAIN INSTANCES                        │
│                                                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ cli-commands.ttl│  │  jobs.ttl       │  │  docs.ttl       │         │
│  │ :validate       │  │  :ValidateJob   │  │  :UserGuide     │         │
│  │ :generate       │  │  :GenerateJob   │  │  :Reference     │         │
│  │ :query          │  │  :QueryJob      │  │  :Tutorial      │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Case Study: Evolution Without Breakage

### The Challenge

A team using Spec-Kit needs to add a new concept: "Command Groups" for organizing related commands. How do they add this without breaking existing specifications?

### Without Layers: Risky Change

In a flat ontology, adding CommandGroup means:
- Modifying the single ontology file
- Risk of breaking all existing commands
- No way to test the change in isolation
- All specs must be updated simultaneously

### With Layers: Safe Evolution

**Step 1: Add to Layer 2 (Domain Schema)**

```turtle
# ontology/cli/schema.ttl - ADD these lines
cli:CommandGroup a rdfs:Class ;
    rdfs:subClassOf sk:Entity ;
    rdfs:label "Command Group" ;
    rdfs:comment "A logical grouping of related commands" .

cli:inGroup a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range cli:CommandGroup ;
    rdfs:comment "The group this command belongs to" .

cli:groupOrder a rdf:Property ;
    rdfs:domain cli:Command ;
    rdfs:range xsd:integer ;
    rdfs:comment "Order of command within its group" .
```

**Step 2: Validate Schema Changes**

```bash
# Test schema alone, without instances
riot --validate ontology/cli/schema.ttl
shacl validate -d ontology/cli/schema.ttl -s shapes/schema-shapes.ttl
```

**Step 3: Update Layer 3 Instances Incrementally**

```turtle
# memory/cli-commands.ttl - ADD groups, UPDATE commands

# Define groups
:validation_group a cli:CommandGroup ;
    sk:name "Validation" ;
    sk:description "Commands for validating specifications" .

:generation_group a cli:CommandGroup ;
    sk:name "Generation" ;
    sk:description "Commands for generating artifacts" .

# Update existing commands (OPTIONAL - old commands still work!)
:validate cli:inGroup :validation_group ;
          cli:groupOrder 1 .

:generate cli:inGroup :generation_group ;
          cli:groupOrder 1 .
```

**Step 4: Backward Compatibility**

The key insight: `cli:inGroup` is optional. Existing commands without a group still validate and work. Migration can be gradual:

```sparql
# Find commands not yet assigned to groups
SELECT ?cmd ?name WHERE {
    ?cmd a cli:Command ;
         sk:name ?name .
    FILTER NOT EXISTS { ?cmd cli:inGroup ?group }
}
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Skipping Layers

Importing directly from Layer 3 to Layer 0:

```turtle
# WRONG: Instance importing external standard directly
:myCommand a cli:Command ;
    xsd:integer "123" .  # Direct use of XSD in instance data
```

**Problem:** Bypasses framework abstractions. Changes to typing require touching instances.

### Anti-Pattern 2: Circular Imports

```turtle
# cli/schema.ttl imports jtbd/schema.ttl
# jtbd/schema.ttl imports cli/schema.ttl
# CIRCULAR DEPENDENCY
```

**Problem:** Neither can load without the other. Use bridge vocabularies instead.

### Anti-Pattern 3: Fat Bridges

Bridges that contain business logic:

```turtle
# WRONG: Bridge with complex rules
bridge:validateJobCompletion a sh:NodeShape ;
    # Complex validation logic belongs in domain, not bridge
```

**Problem:** Bridges should only define relationships, not behavior. Keep them thin.

### Anti-Pattern 4: Instance Data in Schemas

```turtle
# WRONG: Schema containing instances
cli:Command a rdfs:Class .
cli:validate a cli:Command .  # Instance in schema file!
```

**Problem:** Schema changes force instance regeneration. Keep layers separate.

---

## Implementation Checklist

### Setting Up Layers

- [ ] Create directory structure matching layers:
  ```
  ontology/
  ├── core/           # Layer 1
  │   └── framework.ttl
  ├── cli/            # Layer 2
  │   └── schema.ttl
  ├── jtbd/           # Layer 2
  │   └── schema.ttl
  └── bridges/        # Layer 2 (cross-domain)
      └── cli-jtbd.ttl
  memory/             # Layer 3
  ├── cli-commands.ttl
  └── jobs.ttl
  ```

- [ ] Define namespaces for each layer
- [ ] Create explicit owl:imports declarations
- [ ] Document the layer each file belongs to

### Validating Layer Discipline

- [ ] SHACL shapes to enforce import rules
- [ ] CI checks for circular dependencies
- [ ] Code review checklist for layer compliance
- [ ] Automated dependency graph generation

### Evolving Layers

- [ ] Semantic versioning for each layer
- [ ] Changelog per layer
- [ ] Migration guides for breaking changes
- [ ] Deprecation warnings before removal

---

## Philosophical Foundation

> *"High cohesion within layers, loose coupling between layers."*

This principle from software architecture applies directly to knowledge organization:

- **Cohesion within**: All concepts in a layer serve the same purpose at the same abstraction level
- **Coupling between**: Layers connect through narrow, explicit interfaces (imports)

The result is an ontology that can grow without chaos, evolve without breakage, and be understood without overwhelming complexity.

Consider the alternative: a "big ball of mud" ontology where everything connects to everything. Such systems become:
- Impossible to understand in pieces
- Dangerous to change at all
- Unnavigable for newcomers
- Un-testable in isolation

Layers prevent this descent into chaos.

---

## Resulting Context

After applying this pattern, you have:

- **Clear separation** of universal, framework, domain, and instance layers
- **Ability to reuse** framework across domains without modification
- **Isolated change impact**—domain changes don't affect framework
- **Coherent integration** through explicit imports and bridges
- **Testable modules** that can be validated independently
- **Safe evolution** with backward-compatible additions

This supports **[Vocabulary Boundary](./vocabulary-boundary.md)** and enables **[Partial Regeneration](../transformation/partial-regeneration.md)**.

---

## Code References

The following spec-kit source files implement layered ontology concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/spec-kit-schema.ttl:1-18` | Layer 1 (Framework): Core spec-kit vocabulary imports |
| `ontology/jtbd-schema.ttl:1-20` | Layer 2 (Domain): JTBD domain vocabulary |
| `ontology/cli-commands.ttl:1-5` | Layer 2 (Domain): CLI domain vocabulary |
| `ontology/spec-kit-schema.ttl:20-83` | Layer 1 classes used across domains |
| `memory/*.ttl` | Layer 3 (Instance): Specific feature/spec instances |

---

## Related Patterns

- *Refines:* **[13. Vocabulary Boundary](./vocabulary-boundary.md)** — Layers organize vocabularies
- *Supports:* **[12. Shape Constraint](./shape-constraint.md)** — Shapes per layer
- *Enables:* **[28. Partial Regeneration](../transformation/partial-regeneration.md)** — Change one layer, regenerate its artifacts
- *Integrates with:* **[15. Inference Rule](./inference-rule.md)** — Rules can cross layers

---

## Exercises

### Exercise 1: Layer Classification

Given these concepts, assign each to the correct layer:
1. `xsd:string`
2. `sk:Entity`
3. `cli:Command`
4. `:validate` (a specific command)
5. `sh:NodeShape`
6. `jtbd:Job`
7. `:ValidateOntologyJob` (a specific job)

### Exercise 2: Bridge Design

Design a bridge vocabulary connecting a new "testing" domain to the CLI domain. The testing domain has concepts: `TestSuite`, `TestCase`, `TestResult`. How do tests relate to commands?

### Exercise 3: Import Validation

Write a SPARQL query that finds all import violations in an ontology—cases where a Layer 2 file imports from a peer Layer 2 domain.

### Exercise 4: Evolution Planning

Your team needs to add a "CommandAlias" concept (alternative names for commands). Plan the change:
1. Which layer(s) need modification?
2. Is this backward compatible?
3. What's the migration path for existing specs?

---

## Further Reading

- *Ontology Development 101* — Noy & McGuinness
- *Modular Ontology Engineering* — Various papers
- *Software Architecture Patterns* — O'Reilly
- *Building Maintainable Software* — On modularity
- *The Pragmatic Programmer* — On orthogonality

