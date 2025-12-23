# 20. Traceability Thread

★★

*Every artifact should trace to its source. Every decision should trace to its rationale. Traceability threads connect the web of specifications, enabling impact analysis and provenance tracking. They are the memory that gives meaning to each piece.*

---

## The Web of Disconnected Artifacts

Your system now has many artifacts:
- Customer jobs and outcomes (from JTBD analysis)
- Formal specifications (RDF/Turtle files)
- Acceptance criteria (Given-When-Then)
- Generated code (Python, TypeScript, etc.)
- Documentation (Markdown, HTML)
- Tests (pytest, jest)
- Configuration (TOML, YAML)

These artifacts relate to each other. A test validates an acceptance criterion. The criterion addresses an outcome. The outcome belongs to a job. The job exists in a circumstance. But where are these relationships recorded?

Without explicit traceability:
- A test exists. Why? It validates something. What?
- A criterion specifies behavior. Which outcome does it address?
- A piece of code was generated. From what specification?
- A change is proposed. What else is affected?

The relationships are implicit—known to the person who created them, forgotten by everyone else. When something changes, impact is unclear. When something fails, root cause is obscure. When someone leaves, context evaporates.

---

## The Problem Statement

**Implicit relationships become lost knowledge. Changes have hidden impacts. Failures have unknown causes. The system becomes an archipelago of disconnected islands.**

The cost of missing traceability:
- **Change fear**: "What will break if I change this?"
- **Root cause mystery**: "Why is this test failing?"
- **Orphaned artifacts**: Tests without purpose, code without specs
- **Forgotten rationale**: "Why does this exist?"
- **Impact blindness**: Changes ripple unpredictably
- **Audit failure**: "Where is the requirement for this?"

---

## The Forces at Play

### Force 1: Completeness vs. Effort

**Completeness wants full traceability.** Every connection documented. Every relationship explicit. Total visibility.

**Effort wants efficiency.** Maintaining traceability has cost. Links must be created, updated, verified. Every link is a maintenance burden.

```
Completeness ←───────────────────────────→ Effort
(every connection)                         (minimal overhead)
```

### Force 2: Automation vs. Semantics

**Automation wants machine-readable links.** Tools can traverse, validate, and report on structured connections. Human-only traceability doesn't scale.

**Semantics wants meaningful relationships.** "Related to" isn't as useful as "validates" or "generated from." Rich semantics require human understanding.

```
Automation ←─────────────────────────────→ Semantics
(machine traversable)                      (meaningful connections)
```

### Force 3: Locality vs. Global View

**Locality wants links near content.** When reading a test, see what it tests. When reading a spec, see what traces to it.

**Global view wants overview.** See all connections at once. Understand the full dependency graph. Navigate the complete landscape.

```
Locality ←───────────────────────────────→ Global View
(links in context)                         (comprehensive map)
```

### Force 4: Stability vs. Evolution

**Stability wants fixed links.** Once established, relationships should persist. Changing links breaks traceability.

**Evolution wants adaptability.** As the system evolves, relationships change. Old links become stale. New links emerge.

```
Stability ←──────────────────────────────→ Evolution
(permanent connections)                    (living relationships)
```

---

## Therefore: Create Explicit Traceability Links in RDF

**Create explicit traceability links in RDF, forming threads that connect related artifacts across all levels—from customer need to deployed code.**

The key insight: Traceability is just more RDF. The same semantic web technologies that describe your specifications can describe the relationships between artifacts. Links are data. Links can be validated. Links can be queried.

### The Traceability Ontology

```turtle
@prefix tr: <https://spec-kit.io/ontology/trace#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# ═══════════════════════════════════════════════════════════════════
# CORE TRACEABILITY RELATIONSHIPS
# ═══════════════════════════════════════════════════════════════════

# Abstract base property
tr:tracesTo a rdf:Property ;
    rdfs:label "traces to" ;
    rdfs:comment "Base property for all traceability relationships" .

# Forward links (from implementation toward need)
tr:satisfies a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "satisfies" ;
    rdfs:comment "Test satisfies acceptance criterion" .

tr:addresses a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "addresses" ;
    rdfs:comment "Criterion addresses outcome" .

tr:accomplishes a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "accomplishes" ;
    rdfs:comment "Capability accomplishes job" .

tr:fulfills a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "fulfills" ;
    rdfs:comment "Job fulfills need" .

tr:validates a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "validates" ;
    rdfs:comment "Test validates specification" .

tr:implements a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "implements" ;
    rdfs:comment "Code implements specification" .

tr:generatedFrom a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "generated from" ;
    rdfs:comment "Artifact generated from specification" .

tr:documents a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "documents" ;
    rdfs:comment "Documentation describes specification" .

tr:configures a rdf:Property ;
    rdfs:subPropertyOf tr:tracesTo ;
    rdfs:label "configures" ;
    rdfs:comment "Configuration configures capability" .

# Inverse links (from need toward implementation)
tr:satisfiedBy a rdf:Property ;
    owl:inverseOf tr:satisfies ;
    rdfs:label "satisfied by" .

tr:addressedBy a rdf:Property ;
    owl:inverseOf tr:addresses ;
    rdfs:label "addressed by" .

tr:accomplishedBy a rdf:Property ;
    owl:inverseOf tr:accomplishes ;
    rdfs:label "accomplished by" .

tr:fulfilledBy a rdf:Property ;
    owl:inverseOf tr:fulfills ;
    rdfs:label "fulfilled by" .

tr:validatedBy a rdf:Property ;
    owl:inverseOf tr:validates ;
    rdfs:label "validated by" .

tr:implementedBy a rdf:Property ;
    owl:inverseOf tr:implements ;
    rdfs:label "implemented by" .

tr:generates a rdf:Property ;
    owl:inverseOf tr:generatedFrom ;
    rdfs:label "generates" .

tr:documentedBy a rdf:Property ;
    owl:inverseOf tr:documents ;
    rdfs:label "documented by" .

tr:configuredBy a rdf:Property ;
    owl:inverseOf tr:configures ;
    rdfs:label "configured by" .

# ═══════════════════════════════════════════════════════════════════
# PROVENANCE METADATA
# ═══════════════════════════════════════════════════════════════════

tr:TraceLink a rdfs:Class ;
    rdfs:label "Trace Link" ;
    rdfs:comment "Reified traceability relationship with metadata" .

tr:from a rdf:Property ;
    rdfs:domain tr:TraceLink ;
    rdfs:comment "Source of trace link" .

tr:to a rdf:Property ;
    rdfs:domain tr:TraceLink ;
    rdfs:comment "Target of trace link" .

tr:type a rdf:Property ;
    rdfs:domain tr:TraceLink ;
    rdfs:comment "Type of relationship (satisfies, addresses, etc.)" .

tr:createdAt a rdf:Property ;
    rdfs:domain tr:TraceLink ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "When the link was established" .

tr:createdBy a rdf:Property ;
    rdfs:domain tr:TraceLink ;
    rdfs:comment "Who/what created the link" .

tr:rationale a rdf:Property ;
    rdfs:domain tr:TraceLink ;
    rdfs:range xsd:string ;
    rdfs:comment "Why this link exists" .

tr:status a rdf:Property ;
    rdfs:domain tr:TraceLink ;
    rdfs:comment "Current status (active, deprecated, broken)" .

# Status values
tr:Active a tr:LinkStatus ;
    rdfs:label "Active" .

tr:Deprecated a tr:LinkStatus ;
    rdfs:label "Deprecated" .

tr:Broken a tr:LinkStatus ;
    rdfs:label "Broken" .

tr:Pending a tr:LinkStatus ;
    rdfs:label "Pending" .
```

---

## The Traceability Thread

A thread connects artifacts from need to implementation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    THE TRACEABILITY THREAD                       │
│                                                                  │
│  ┌─────────────┐                                                │
│  │ Customer    │ "I need to validate my files quickly"          │
│  │ Need        │                                                │
│  └──────┬──────┘                                                │
│         │ fulfills                                               │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Job To Be   │ Validate RDF files for correctness            │
│  │ Done        │                                                │
│  └──────┬──────┘                                                │
│         │ hasOutcome                                             │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Desired     │ Minimize time to validate                      │
│  │ Outcome     │ Minimize validation errors                      │
│  └──────┬──────┘                                                │
│         │ addressedBy                                            │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Acceptance  │ AC-VAL-001: Valid file → exit 0                │
│  │ Criterion   │ AC-VAL-010: < 1s for < 1MB                      │
│  └──────┬──────┘                                                │
│         │ satisfiedBy                                            │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Test Case   │ test_validate_valid_file()                      │
│  │             │ test_validate_performance()                     │
│  └──────┬──────┘                                                │
│         │ validates                                              │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Specification│ cli:ValidateCommand in cli-commands.ttl        │
│  │ (RDF)       │                                                │
│  └──────┬──────┘                                                │
│         │ generates                                              │
│         ▼                                                        │
│  ┌─────────────┐                                                │
│  │ Generated   │ src/commands/validate.py                        │
│  │ Code        │ docs/commands/validate.md                       │
│  └─────────────┘                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

Each arrow is an RDF relationship. Each box is an RDF resource. The entire thread is queryable.

---

## Example Thread in RDF

```turtle
@prefix tr: <https://spec-kit.io/ontology/trace#> .
@prefix jtbd: <https://spec-kit.io/ontology/jtbd#> .
@prefix ac: <https://spec-kit.io/ontology/acceptance#> .
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix test: <https://spec-kit.io/specs/tests#> .
@prefix docs: <https://spec-kit.io/specs/docs#> .
@prefix code: <https://spec-kit.io/artifacts/code#> .

# ═══════════════════════════════════════════════════════════════════
# LAYER 1: CUSTOMER CONTEXT
# ═══════════════════════════════════════════════════════════════════

jtbd:PreCommitValidation a jtbd:Circumstance ;
    sk:name "Pre-Commit Validation" ;
    sk:description """
        Developer has edited RDF files and is about to commit.
        Needs confidence that changes are valid before committing.
    """ ;
    jtbd:hasJob jtbd:ValidateOntologyJob .

jtbd:ValidateOntologyJob a jtbd:Job ;
    sk:name "Validate ontology before commit" ;
    sk:description "Ensure RDF files are syntactically and semantically valid" ;
    jtbd:hasOutcome jtbd:MinimizeValidationTime ;
    jtbd:hasOutcome jtbd:EnsureCorrectness ;
    jtbd:hasOutcome jtbd:ClearErrorMessages .

# ═══════════════════════════════════════════════════════════════════
# LAYER 2: DESIRED OUTCOMES
# ═══════════════════════════════════════════════════════════════════

jtbd:MinimizeValidationTime a jtbd:Outcome ;
    jtbd:direction "minimize" ;
    jtbd:metric "seconds" ;
    jtbd:object "time to validate file" ;
    sk:description "Fast validation enables integration into development flow" ;
    tr:addressedBy ac:AC-VAL-010 ;
    tr:addressedBy ac:AC-VAL-011 .

jtbd:EnsureCorrectness a jtbd:Outcome ;
    jtbd:direction "maximize" ;
    jtbd:metric "accuracy" ;
    jtbd:object "correctness of validation" ;
    sk:description "Validation must correctly identify all errors" ;
    tr:addressedBy ac:AC-VAL-001 ;
    tr:addressedBy ac:AC-VAL-002 ;
    tr:addressedBy ac:AC-VAL-003 .

jtbd:ClearErrorMessages a jtbd:Outcome ;
    jtbd:direction "maximize" ;
    jtbd:metric "clarity" ;
    jtbd:object "error message actionability" ;
    sk:description "When validation fails, user knows exactly what to fix" ;
    tr:addressedBy ac:AC-VAL-002 ;
    tr:addressedBy ac:AC-VAL-004 .

# ═══════════════════════════════════════════════════════════════════
# LAYER 3: ACCEPTANCE CRITERIA
# ═══════════════════════════════════════════════════════════════════

ac:AC-VAL-001 a ac:AcceptanceCriterion ;
    ac:identifier "AC-VAL-001" ;
    ac:given "A syntactically valid RDF/Turtle file exists" ;
    ac:when "User runs 'specify validate file.ttl'" ;
    ac:then "Command exits with code 0 and prints 'Valid ✓'" ;
    ac:priority ac:Must ;
    tr:addresses jtbd:EnsureCorrectness ;
    tr:satisfiedBy test:test_validate_valid_file .

ac:AC-VAL-002 a ac:AcceptanceCriterion ;
    ac:identifier "AC-VAL-002" ;
    ac:given "A file with RDF syntax errors exists" ;
    ac:when "User runs 'specify validate invalid.ttl'" ;
    ac:then "Command exits with non-zero code and prints error with line number" ;
    ac:priority ac:Must ;
    tr:addresses jtbd:EnsureCorrectness ;
    tr:addresses jtbd:ClearErrorMessages ;
    tr:satisfiedBy test:test_validate_invalid_file .

ac:AC-VAL-010 a ac:AcceptanceCriterion ;
    ac:identifier "AC-VAL-010" ;
    ac:given "A valid RDF file smaller than 1MB exists" ;
    ac:when "User runs validate on the file" ;
    ac:then "Command completes in less than 1 second" ;
    ac:priority ac:Should ;
    tr:addresses jtbd:MinimizeValidationTime ;
    tr:satisfiedBy test:test_validate_performance .

# ═══════════════════════════════════════════════════════════════════
# LAYER 4: TEST CASES
# ═══════════════════════════════════════════════════════════════════

test:test_validate_valid_file a test:TestCase ;
    sk:name "test_validate_valid_file" ;
    sk:description "Verify valid file produces exit code 0" ;
    test:file "tests/e2e/test_validate.py" ;
    test:line 42 ;
    tr:satisfies ac:AC-VAL-001 ;
    tr:validates cli:ValidateCommand .

test:test_validate_invalid_file a test:TestCase ;
    sk:name "test_validate_invalid_file" ;
    sk:description "Verify invalid file produces error with line number" ;
    test:file "tests/e2e/test_validate.py" ;
    test:line 67 ;
    tr:satisfies ac:AC-VAL-002 ;
    tr:validates cli:ValidateCommand .

test:test_validate_performance a test:TestCase ;
    sk:name "test_validate_performance" ;
    sk:description "Verify validation completes in < 1s for small files" ;
    test:file "tests/e2e/test_validate.py" ;
    test:line 89 ;
    tr:satisfies ac:AC-VAL-010 ;
    tr:validates cli:ValidateCommand .

# ═══════════════════════════════════════════════════════════════════
# LAYER 5: SPECIFICATION
# ═══════════════════════════════════════════════════════════════════

cli:ValidateCommand a cli:Command ;
    sk:name "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;
    cli:hasArgument [ sk:name "file" ; cli:type "Path" ; cli:required true ] ;
    cli:hasOption [ sk:name "--strict" ; cli:type "bool" ] ;
    tr:accomplishes jtbd:ValidateOntologyJob ;
    tr:generates code:validate_py ;
    tr:generates docs:validate_md .

# ═══════════════════════════════════════════════════════════════════
# LAYER 6: GENERATED ARTIFACTS
# ═══════════════════════════════════════════════════════════════════

code:validate_py a code:GeneratedFile ;
    code:path "src/specify_cli/commands/validate.py" ;
    tr:generatedFrom cli:ValidateCommand ;
    tr:generatedAt "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    tr:generatedBy <ggen:v5.0.2> ;
    tr:sourceHash "sha256:a1b2c3d4..." ;
    tr:artifactHash "sha256:e5f6g7h8..." .

docs:validate_md a docs:GeneratedFile ;
    docs:path "docs/commands/validate.md" ;
    tr:generatedFrom cli:ValidateCommand ;
    tr:generatedAt "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    tr:generatedBy <ggen:v5.0.2> .
```

---

## Traceability Queries

### Follow the Thread Upward (Implementation → Need)

```sparql
PREFIX tr: <https://spec-kit.io/ontology/trace#>
PREFIX jtbd: <https://spec-kit.io/ontology/jtbd#>
PREFIX ac: <https://spec-kit.io/ontology/acceptance#>
PREFIX test: <https://spec-kit.io/specs/tests#>

# Given a test, find the customer need it ultimately addresses
SELECT ?test ?criterion ?outcome ?job ?circumstance
WHERE {
    ?test a test:TestCase ;
          tr:satisfies ?criterion .

    ?criterion tr:addresses ?outcome .

    ?job jtbd:hasOutcome ?outcome .

    OPTIONAL { ?circumstance jtbd:hasJob ?job }
}
```

### Follow the Thread Downward (Need → Implementation)

```sparql
PREFIX tr: <https://spec-kit.io/ontology/trace#>
PREFIX jtbd: <https://spec-kit.io/ontology/jtbd#>

# Given a job, find all artifacts that implement it
SELECT ?job ?outcome ?criterion ?test ?code
WHERE {
    ?job a jtbd:Job ;
         jtbd:hasOutcome ?outcome .

    ?criterion tr:addresses ?outcome .

    ?test tr:satisfies ?criterion .

    OPTIONAL {
        ?test tr:validates ?spec .
        ?code tr:generatedFrom ?spec .
    }
}
```

### Impact Analysis: What is affected by this change?

```sparql
PREFIX tr: <https://spec-kit.io/ontology/trace#>
PREFIX cli: <https://spec-kit.io/ontology/cli#>

# If we change ValidateCommand, what else is affected?
SELECT DISTINCT ?affected ?type
WHERE {
    cli:ValidateCommand (
        tr:generates |
        ^tr:validates |
        ^tr:accomplishes |
        tr:accomplishes/jtbd:hasOutcome
    ) ?affected .

    ?affected a ?type .
}
```

### Coverage Analysis: What isn't traced?

```sparql
PREFIX tr: <https://spec-kit.io/ontology/trace#>
PREFIX ac: <https://spec-kit.io/ontology/acceptance#>

# Find criteria without tests
SELECT ?criterion ?id
WHERE {
    ?criterion a ac:AcceptanceCriterion ;
               ac:identifier ?id .

    FILTER NOT EXISTS {
        ?test tr:satisfies ?criterion .
    }
}
```

### Orphan Detection: What has no upstream trace?

```sparql
PREFIX tr: <https://spec-kit.io/ontology/trace#>
PREFIX test: <https://spec-kit.io/specs/tests#>

# Find tests that don't satisfy any criterion
SELECT ?test ?name
WHERE {
    ?test a test:TestCase ;
          sk:name ?name .

    FILTER NOT EXISTS {
        ?test tr:satisfies ?criterion .
    }
}
```

---

## Provenance Tracking

For generated artifacts, track complete provenance:

```turtle
code:validate_py a code:GeneratedFile ;
    code:path "src/specify_cli/commands/validate.py" ;

    # What it came from
    tr:generatedFrom cli:ValidateCommand ;

    # When it was generated
    tr:generatedAt "2025-01-15T10:30:00Z"^^xsd:dateTime ;

    # What generated it
    tr:generatedBy <ggen:v5.0.2> ;

    # Cryptographic verification
    tr:sourceHash "sha256:a1b2c3d4e5f6..." ;   # Hash of source .ttl
    tr:artifactHash "sha256:e5f6g7h8i9j0..." ; # Hash of output .py

    # Transformation details
    tr:templateUsed <templates/command.tera> ;
    tr:queryUsed <sparql/command-extract.rq> ;

    # Verification status
    tr:verified true ;
    tr:verifiedAt "2025-01-15T10:30:05Z"^^xsd:dateTime .
```

This enables:
- **Drift detection**: Compare current file hash to `artifactHash`
- **Reproducibility**: Re-run same transformation with same inputs
- **Audit**: Prove artifact came from specific specification
- **Debugging**: Know which template/query produced output

---

## Validating Traceability with SHACL

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix tr: <https://spec-kit.io/ontology/trace#> .
@prefix ac: <https://spec-kit.io/ontology/acceptance#> .
@prefix test: <https://spec-kit.io/specs/tests#> .
@prefix code: <https://spec-kit.io/artifacts/code#> .

# Every Must criterion should have a test
ac:MustCriterionTestShape a sh:NodeShape ;
    sh:target [
        a sh:SPARQLTarget ;
        sh:select """
            SELECT ?this WHERE {
                ?this a ac:AcceptanceCriterion ;
                      ac:priority ac:Must .
            }
        """
    ] ;
    sh:property [
        sh:path [ sh:inversePath tr:satisfies ] ;
        sh:minCount 1 ;
        sh:message "Must-priority criteria require at least one test"
    ] .

# Every test should trace to a criterion
test:TestTraceabilityShape a sh:NodeShape ;
    sh:targetClass test:TestCase ;
    sh:property [
        sh:path tr:satisfies ;
        sh:minCount 1 ;
        sh:message "Tests must trace to at least one acceptance criterion"
    ] .

# Generated files must have provenance
code:ProvenanceShape a sh:NodeShape ;
    sh:targetClass code:GeneratedFile ;
    sh:property [
        sh:path tr:generatedFrom ;
        sh:minCount 1 ;
        sh:message "Generated files must trace to source specification"
    ] ;
    sh:property [
        sh:path tr:generatedAt ;
        sh:minCount 1 ;
        sh:datatype xsd:dateTime ;
        sh:message "Generated files must have generation timestamp"
    ] ;
    sh:property [
        sh:path tr:artifactHash ;
        sh:minCount 1 ;
        sh:message "Generated files must have hash for verification"
    ] .

# Criteria must address outcomes
ac:CriterionOutcomeShape a sh:NodeShape ;
    sh:targetClass ac:AcceptanceCriterion ;
    sh:severity sh:Warning ;
    sh:property [
        sh:path tr:addresses ;
        sh:minCount 1 ;
        sh:message "Criteria should address at least one outcome for traceability"
    ] .
```

---

## Case Study: Impact Analysis in Practice

### The Scenario

A team needs to change how validation errors are reported. Currently:
```
Error: Line 45: Invalid predicate
```

New requirement:
```
Error: Line 45, Column 12: Invalid predicate 'foo:bar'
```

### Without Traceability

Team must manually search:
- Which code handles error formatting?
- Which tests verify error format?
- Which documentation describes error format?
- Which criteria define expected error format?
- Which outcomes depend on error clarity?

This takes hours and misses things.

### With Traceability

Query the impact:

```sparql
PREFIX tr: <https://spec-kit.io/ontology/trace#>
PREFIX jtbd: <https://spec-kit.io/ontology/jtbd#>

# Find everything connected to error message clarity
SELECT ?artifact ?type ?relationship
WHERE {
    jtbd:ClearErrorMessages (
        tr:addressedBy |
        tr:addressedBy/tr:satisfiedBy |
        ^tr:addresses/^tr:satisfies
    ) ?artifact .

    ?artifact a ?type .
    BIND("traces to ClearErrorMessages" AS ?relationship)
}
```

Results:
```
| artifact                      | type            | relationship             |
|-------------------------------|-----------------|--------------------------|
| ac:AC-VAL-002                 | AcceptanceCriterion | traces to ClearErrorMessages |
| ac:AC-VAL-004                 | AcceptanceCriterion | traces to ClearErrorMessages |
| test:test_validate_invalid_file | TestCase       | traces to ClearErrorMessages |
| test:test_validate_missing_file | TestCase       | traces to ClearErrorMessages |
```

Team instantly knows:
- Update criteria AC-VAL-002 and AC-VAL-004
- Update tests test_validate_invalid_file and test_validate_missing_file
- Update documentation for these criteria

Total time: 5 minutes.

---

## Visualizing Traceability

### Graph Visualization

```
                    ┌─────────────────┐
                    │ PreCommitValidation │
                    │    (Circumstance)   │
                    └─────────┬───────────┘
                              │ hasJob
                              ▼
                    ┌─────────────────┐
                    │ ValidateOntologyJob │
                    │      (Job)          │
                    └───────┬─┬─┬─────────┘
                            │ │ │ hasOutcome
            ┌───────────────┘ │ └───────────────┐
            ▼                 ▼                 ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ MinimizeTime  │ │ EnsureCorrect │ │ ClearMessages │
    │  (Outcome)    │ │   (Outcome)   │ │   (Outcome)   │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │addressedBy      │                 │
            ▼                 ▼                 ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ AC-VAL-010    │ │ AC-VAL-001    │ │ AC-VAL-002    │
    │  (Criterion)  │ │  (Criterion)  │ │  (Criterion)  │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │satisfiedBy      │                 │
            ▼                 ▼                 ▼
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ test_perf     │ │ test_valid    │ │ test_invalid  │
    │  (Test)       │ │   (Test)      │ │   (Test)      │
    └───────┬───────┘ └───────┬───────┘ └───────┬───────┘
            │validates        │                 │
            └────────────────┬┘─────────────────┘
                             ▼
                    ┌─────────────────┐
                    │ ValidateCommand │
                    │     (Spec)      │
                    └────────┬────────┘
                             │ generates
            ┌────────────────┴────────────────┐
            ▼                                 ▼
    ┌───────────────┐                 ┌───────────────┐
    │ validate.py   │                 │ validate.md   │
    │   (Code)      │                 │   (Docs)      │
    └───────────────┘                 └───────────────┘
```

### Traceability Matrix

| Outcome | Criterion | Test | Spec | Code | Docs |
|---------|-----------|------|------|------|------|
| MinimizeTime | AC-VAL-010 | test_perf | ValidateCommand | validate.py | validate.md |
| MinimizeTime | AC-VAL-011 | test_memory | ValidateCommand | validate.py | - |
| EnsureCorrect | AC-VAL-001 | test_valid | ValidateCommand | validate.py | validate.md |
| EnsureCorrect | AC-VAL-002 | test_invalid | ValidateCommand | validate.py | validate.md |
| ClearMessages | AC-VAL-002 | test_invalid | ValidateCommand | validate.py | validate.md |
| ClearMessages | AC-VAL-004 | test_missing | ValidateCommand | validate.py | validate.md |

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Manual Link Maintenance

```turtle
# BAD: Links maintained by hand, easily become stale
test:some_test rdfs:comment "Tests AC-001" .  # Not machine-readable!
```

**Problem:** Comments aren't queryable. Links rot.

### Anti-Pattern 2: Overly Granular Links

```turtle
# BAD: Every line of code traces to spec
code:line_42 tr:generatedFrom cli:ValidateCommand .
code:line_43 tr:generatedFrom cli:ValidateCommand .
code:line_44 tr:generatedFrom cli:ValidateCommand .
# ... 500 more lines
```

**Problem:** Noise obscures signal. Link at the right granularity.

### Anti-Pattern 3: Missing Inverse Links

```turtle
# BAD: Only forward links, no inverse
test:test_foo tr:satisfies ac:AC-001 .
# Can't easily query "what tests AC-001?"
```

**Solution:** Define inverse properties or use OWL inverse declarations.

### Anti-Pattern 4: Vague Relationship Types

```turtle
# BAD: Everything is just "relatedTo"
test:test_foo tr:relatedTo ac:AC-001 .
code:validate tr:relatedTo cli:ValidateCommand .
```

**Problem:** Can't distinguish satisfies from validates from documents.

### Anti-Pattern 5: No Provenance on Generated Artifacts

```turtle
# BAD: Generated file with no history
code:validate_py a code:GeneratedFile ;
    code:path "src/validate.py" .
# What generated this? When? From what?
```

**Problem:** Can't verify, can't reproduce, can't audit.

---

## Implementation Checklist

### Setting Up Traceability

- [ ] Define traceability ontology with typed relationships
- [ ] Establish link granularity conventions (file, function, line?)
- [ ] Create SHACL shapes to validate required links
- [ ] Set up queries for impact analysis and coverage

### Maintaining Traceability

- [ ] Automate link creation during generation
- [ ] Validate links in CI pipeline
- [ ] Generate traceability reports
- [ ] Detect and alert on broken links

### Using Traceability

- [ ] Query before making changes (impact analysis)
- [ ] Query for coverage gaps
- [ ] Query for orphaned artifacts
- [ ] Query for audit/compliance

---

## Resulting Context

After applying this pattern, you have:

- **Explicit links** connecting all artifacts from need to code
- **Impact analysis** capability before changes
- **Provenance tracking** for generated artifacts
- **Navigable threads** from any point in any direction
- **Coverage visibility**—see gaps in traceability
- **Audit trail**—prove relationships exist

This completes the Specification Patterns and prepares for **[Part III: Transformation Patterns](../transformation/constitutional-equation.md)**.

---

## Related Patterns

- *Links:* **[5. Outcome Desired](../context/outcome-desired.md)** ↔ **[19. Acceptance Criterion](./acceptance-criterion.md)**
- *Links:* **[19. Acceptance Criterion](./acceptance-criterion.md)** ↔ **[31. Test Before Code](../verification/test-before-code.md)**
- *Enables:* **[26. Receipt Generation](../transformation/receipt-generation.md)** — Receipts are traces
- *Supports:* **[35. Drift Detection](../verification/drift-detection.md)** — Detect broken traces

---

## Philosophical Coda

> *"You can't manage what you can't trace."*

Traceability threads make the implicit explicit. They transform a collection of files into a coherent system. They answer "why" questions at every level: Why does this code exist? Why does this test exist? Why does this requirement exist?

Without traceability, every artifact is an island. With it, every artifact is part of a continent of connected meaning.

---

## Transition to Part III

You've completed the Specification Patterns. You know how to:
- Establish a **[Semantic Foundation](./semantic-foundation.md)** with RDF
- Create a **[Single Source of Truth](./single-source-of-truth.md)**
- Make specifications **[Executable](./executable-specification.md)**
- Define **[Shape Constraints](./shape-constraint.md)** for validation
- Navigate with **[Property Paths](./property-path.md)**
- Derive knowledge with **[Inference Rules](./inference-rule.md)**
- Organize with **[Vocabulary Boundaries](./vocabulary-boundary.md)** and **[Layered Ontologies](./layered-ontology.md)**
- Simplify with **[Domain-Specific Languages](./domain-specific-language.md)**
- Add **[Narrative](./narrative-specification.md)** context
- Define **[Acceptance Criteria](./acceptance-criterion.md)**
- Create **[Traceability Threads](./traceability-thread.md)**

Now it's time to transform these specifications into artifacts. Turn to **[Part III: Transformation Patterns](../transformation/constitutional-equation.md)** to learn the art of faithful generation.

---

## Exercises

### Exercise 1: Thread Creation

Take a single feature in your system and create a complete traceability thread from customer need to implementation. How many artifacts are connected? How many links?

### Exercise 2: Impact Query

Write a SPARQL query that, given any artifact, finds all other artifacts that might be affected by changing it. Test it against your traceability data.

### Exercise 3: Coverage Report

Write a query that finds all acceptance criteria without tests, and all tests without criteria. Generate a coverage report.

### Exercise 4: Provenance Audit

For a generated artifact, verify its provenance:
1. Find the source specification
2. Regenerate the artifact
3. Compare hashes
4. Report whether the artifact is current or drifted

---

## Further Reading

- *Requirements Traceability* — Gotel & Finkelstein
- *Traceability in Model-Driven Engineering* — Various papers
- *Software Configuration Management* — IEEE Standards
- *PROV-O: The PROV Ontology* — W3C
- *Impact Analysis Techniques* — Various surveys

