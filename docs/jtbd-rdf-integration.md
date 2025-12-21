# Jobs-To-Be-Done (JTBD) Integration for RDF-First Development

**Version:** 1.0
**Status:** Design Specification
**Last Updated:** 2025-12-21
**Authors:** Spec-Kit Design Team

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Constitutional Equation Extension](#constitutional-equation-extension)
3. [JTBD Ontology Design](#jtbd-ontology-design)
4. [RDF Schema Extension](#rdf-schema-extension)
5. [SPARQL Query Patterns](#sparql-query-patterns)
6. [Tera Template Extensions](#tera-template-extensions)
7. [ggen.toml Configuration](#ggentoml-configuration)
8. [Measurement Framework](#measurement-framework)
9. [Concrete Examples: uvmgr Commands](#concrete-examples-uvmgr-commands)
10. [Integration Workflow](#integration-workflow)
11. [Implementation Roadmap](#implementation-roadmap)
12. [Validation & Testing](#validation--testing)

---

## Executive Summary

This document specifies how Jobs-To-Be-Done (JTBD) framework integrates into spec-kit's RDF-first development methodology. JTBD shifts focus from features to customer outcomes, ensuring every generated feature addresses a real job customers are trying to accomplish.

### Key Principles

1. **Outcome-Driven Specifications**: Features defined by the jobs they accomplish, not just technical capabilities
2. **Measurable Progress**: Track whether features deliver promised outcomes through concrete metrics
3. **Bidirectional Traceability**: Map features → jobs → outcomes and back
4. **Automated Documentation**: Generate "Why This Exists" sections automatically from RDF
5. **Continuous Validation**: Verify feature-job alignment before and after implementation

### Constitutional Equation Extension

**Current:**
```
code = μ(feature.ttl)
spec.md = μ(documentation.ttl)
```

**Proposed:**
```
outcome-driven-features = μ(jtbd.ttl + customer-jobs.ttl + feature.ttl)
why-documentation = μ(jobs-mapping.ttl)
metrics-dashboard = μ(outcome-measurements.ttl)
```

Where:
- **jtbd.ttl**: Customer jobs, desired outcomes, painpoints, and progress makers
- **customer-jobs.ttl**: Specific job instances with context and success criteria
- **feature.ttl**: Feature specifications (existing)
- **jobs-mapping.ttl**: Bidirectional links between features and jobs
- **outcome-measurements.ttl**: Metrics and measurements of job success

---

## Constitutional Equation Extension

### Extended Transformation Pipeline

The JTBD integration extends the five-stage μ transformation:

```
μ₁ Normalize:   Validate JTBD SHACL shapes + feature shapes
μ₂ Extract:     Execute SPARQL to join features ↔ jobs ↔ outcomes
μ₃ Emit:        Render templates with job-outcome context
μ₄ Canonicalize: Format output (code, docs, metrics dashboards)
μ₅ Receipt:     SHA256 proof: output = μ(jtbd.ttl + feature.ttl)
```

### Three-Level Constitutional Equation

#### Level 1: Feature-Job Mapping
```turtle
outcome-driven-feature = μ(feature.ttl ⊗ jtbd.ttl)
```

Where `⊗` represents semantic joining via `:addressesJob` relationships.

**Example:**
```turtle
# Input: feature.ttl
:DepsAddCommand a :Feature ;
    :addressesJob :RDFDesignersJob ;
    :addressesJob :PythonDevelopersJob .

# Input: jtbd.ttl
:RDFDesignersJob a :Job ;
    :title "Manage project dependencies without breaking RDF workflow" .

# Output (after μ transformation):
# Generated code includes docstring:
"""
Why This Feature Exists:
    Addresses: Manage project dependencies without breaking RDF workflow
    Addresses: Add Python packages with minimal cognitive overhead
"""
```

#### Level 2: Outcome Documentation
```turtle
why-documentation = μ(jobs-mapping.ttl)
```

Generates documentation explaining WHY features exist, not just WHAT they do.

**Example output (generated Markdown):**
```markdown
## Why `specify deps add` Exists

### Customer Jobs Addressed
1. **RDF Designers** need to add dependencies without leaving RDF-first workflow
2. **Python Developers** need to add packages with minimal cognitive overhead

### Outcomes Delivered
- **Faster Development**: Reduce dependency addition time from 5 minutes to 30 seconds
- **Zero Context Switching**: Stay in spec-kit CLI, no manual pyproject.toml editing
- **Guaranteed Consistency**: Automatic validation against project requirements
```

#### Level 3: Metrics Dashboard
```turtle
metrics-dashboard = μ(outcome-measurements.ttl)
```

Generates dashboards tracking whether features deliver promised outcomes.

**Example output (generated metrics):**
```json
{
  "feature": "deps-add",
  "outcomes": [
    {
      "outcome_id": "faster-dev",
      "target": "< 30 seconds",
      "current": "18 seconds (avg)",
      "status": "exceeds-target",
      "measurement_date": "2025-12-21"
    }
  ]
}
```

---

## JTBD Ontology Design

### Core JTBD Classes

```turtle
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix sk: <http://github.com/github/spec-kit#> .

# ============================================================================
# JTBD Class Hierarchy
# ============================================================================

jtbd:Job a owl:Class ;
    rdfs:label "Customer Job" ;
    rdfs:comment "A job customers are trying to accomplish (functional, emotional, social)" .

jtbd:FunctionalJob rdfs:subClassOf jtbd:Job ;
    rdfs:label "Functional Job" ;
    rdfs:comment "Practical task customer needs to complete" .

jtbd:EmotionalJob rdfs:subClassOf jtbd:Job ;
    rdfs:label "Emotional Job" ;
    rdfs:comment "How customer wants to feel while accomplishing task" .

jtbd:SocialJob rdfs:subClassOf jtbd:Job ;
    rdfs:label "Social Job" ;
    rdfs:comment "How customer wants to be perceived by others" .

jtbd:Outcome a owl:Class ;
    rdfs:label "Desired Outcome" ;
    rdfs:comment "Measurable result customer wants to achieve when doing job" .

jtbd:Painpoint a owl:Class ;
    rdfs:label "Painpoint" ;
    rdfs:comment "Obstacle or frustration preventing job success" .

jtbd:ProgressMaker a owl:Class ;
    rdfs:label "Progress Maker" ;
    rdfs:comment "Capability that enables job progress" .

jtbd:JobContext a owl:Class ;
    rdfs:label "Job Context" ;
    rdfs:comment "Circumstances under which job is performed" .

jtbd:CustomerSegment a owl:Class ;
    rdfs:label "Customer Segment" ;
    rdfs:comment "Group of customers with similar jobs" .

jtbd:Measurement a owl:Class ;
    rdfs:label "Outcome Measurement" ;
    rdfs:comment "Actual measured delivery of an outcome" .
```

### JTBD Properties

```turtle
# ============================================================================
# JTBD Object Properties (Relationships)
# ============================================================================

jtbd:addressesJob a owl:ObjectProperty ;
    rdfs:label "addresses job" ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:Job ;
    rdfs:comment "Feature addresses customer job" .

jtbd:deliversOutcome a owl:ObjectProperty ;
    rdfs:label "delivers outcome" ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:Outcome ;
    rdfs:comment "Feature delivers desired outcome" .

jtbd:reducesPainpoint a owl:ObjectProperty ;
    rdfs:label "reduces painpoint" ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:Painpoint ;
    rdfs:comment "Feature reduces or eliminates painpoint" .

jtbd:enablesProgressMaker a owl:ObjectProperty ;
    rdfs:label "enables progress maker" ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:ProgressMaker ;
    rdfs:comment "Feature enables progress maker capability" .

jtbd:hasOutcome a owl:ObjectProperty ;
    rdfs:label "has outcome" ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:Outcome ;
    rdfs:comment "Job defines desired outcome" .

jtbd:hasPainpoint a owl:ObjectProperty ;
    rdfs:label "has painpoint" ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:Painpoint ;
    rdfs:comment "Job encounters painpoint" .

jtbd:hasContext a owl:ObjectProperty ;
    rdfs:label "has context" ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:JobContext ;
    rdfs:comment "Job performed in context" .

jtbd:performedBy a owl:ObjectProperty ;
    rdfs:label "performed by" ;
    rdfs:domain jtbd:Job ;
    rdfs:range jtbd:CustomerSegment ;
    rdfs:comment "Job performed by customer segment" .

jtbd:hasMeasurement a owl:ObjectProperty ;
    rdfs:label "has measurement" ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range jtbd:Measurement ;
    rdfs:comment "Outcome has measurement data" .

# ============================================================================
# JTBD Datatype Properties (Attributes)
# ============================================================================

jtbd:jobTitle a owl:DatatypeProperty ;
    rdfs:label "job title" ;
    rdfs:domain jtbd:Job ;
    rdfs:range xsd:string ;
    rdfs:comment "Human-readable job title (verb-noun format)" .

jtbd:jobDescription a owl:DatatypeProperty ;
    rdfs:label "job description" ;
    rdfs:domain jtbd:Job ;
    rdfs:range xsd:string ;
    rdfs:comment "Detailed job description" .

jtbd:outcomeDescription a owl:DatatypeProperty ;
    rdfs:label "outcome description" ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string ;
    rdfs:comment "Desired outcome description" .

jtbd:priority a owl:DatatypeProperty ;
    rdfs:label "priority" ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:integer ;
    rdfs:comment "Outcome priority (1-10 scale)" .

jtbd:frequency a owl:DatatypeProperty ;
    rdfs:label "frequency" ;
    rdfs:domain jtbd:Job ;
    rdfs:range xsd:string ;
    rdfs:comment "How often job is performed (Daily, Weekly, Monthly, Rarely)" .

jtbd:painpointDescription a owl:DatatypeProperty ;
    rdfs:label "painpoint description" ;
    rdfs:domain jtbd:Painpoint ;
    rdfs:range xsd:string ;
    rdfs:comment "Painpoint description" .

jtbd:severity a owl:DatatypeProperty ;
    rdfs:label "severity" ;
    rdfs:domain jtbd:Painpoint ;
    rdfs:range xsd:integer ;
    rdfs:comment "Painpoint severity (1-10 scale)" .

jtbd:progressMakerDescription a owl:DatatypeProperty ;
    rdfs:label "progress maker description" ;
    rdfs:domain jtbd:ProgressMaker ;
    rdfs:range xsd:string ;
    rdfs:comment "Progress maker description" .

jtbd:metricName a owl:DatatypeProperty ;
    rdfs:label "metric name" ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string ;
    rdfs:comment "Name of metric measuring outcome" .

jtbd:targetValue a owl:DatatypeProperty ;
    rdfs:label "target value" ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string ;
    rdfs:comment "Target value for outcome (e.g., '< 30 seconds')" .

jtbd:currentValue a owl:DatatypeProperty ;
    rdfs:label "current value" ;
    rdfs:domain jtbd:Measurement ;
    rdfs:range xsd:string ;
    rdfs:comment "Currently measured value" .

jtbd:measurementDate a owl:DatatypeProperty ;
    rdfs:label "measurement date" ;
    rdfs:domain jtbd:Measurement ;
    rdfs:range xsd:dateTime ;
    rdfs:comment "Date measurement was taken" .

jtbd:status a owl:DatatypeProperty ;
    rdfs:label "status" ;
    rdfs:domain jtbd:Measurement ;
    rdfs:range xsd:string ;
    rdfs:comment "Status (exceeds-target, meets-target, below-target)" .
```

---

## RDF Schema Extension

### Complete JTBD Schema (jtbd-schema.ttl)

```turtle
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix shacl: <http://www.w3.org/ns/shacl#> .

# ============================================================================
# JTBD Ontology Schema v1.0
# ============================================================================
# Purpose: Extend Spec-Kit with Jobs-To-Be-Done framework for outcome-driven development
# Integration: Works with existing sk:Feature, sk:UserStory, sk:SuccessCriterion
# ============================================================================

# [Class definitions from previous section...]

# ============================================================================
# SHACL Validation Shapes
# ============================================================================

jtbd:JobShape a shacl:NodeShape ;
    shacl:targetClass jtbd:Job ;
    shacl:property [
        shacl:path jtbd:jobTitle ;
        shacl:datatype xsd:string ;
        shacl:minCount 1 ;
        shacl:maxCount 1 ;
        shacl:minLength 10 ;
        shacl:description "Job title required (at least 10 characters, verb-noun format)" ;
    ] ;
    shacl:property [
        shacl:path jtbd:frequency ;
        shacl:datatype xsd:string ;
        shacl:in ("Daily" "Weekly" "Monthly" "Rarely") ;
        shacl:description "Frequency must be Daily, Weekly, Monthly, or Rarely" ;
    ] ;
    shacl:property [
        shacl:path jtbd:hasOutcome ;
        shacl:class jtbd:Outcome ;
        shacl:minCount 1 ;
        shacl:description "Job must have at least one desired outcome" ;
    ] ;
    shacl:property [
        shacl:path jtbd:performedBy ;
        shacl:class jtbd:CustomerSegment ;
        shacl:minCount 1 ;
        shacl:description "Job must have at least one customer segment" ;
    ] .

jtbd:OutcomeShape a shacl:NodeShape ;
    shacl:targetClass jtbd:Outcome ;
    shacl:property [
        shacl:path jtbd:outcomeDescription ;
        shacl:datatype xsd:string ;
        shacl:minCount 1 ;
        shacl:maxCount 1 ;
        shacl:minLength 15 ;
        shacl:description "Outcome description required (at least 15 characters)" ;
    ] ;
    shacl:property [
        shacl:path jtbd:priority ;
        shacl:datatype xsd:integer ;
        shacl:minCount 1 ;
        shacl:maxCount 1 ;
        shacl:minInclusive 1 ;
        shacl:maxInclusive 10 ;
        shacl:description "Priority required (1-10 scale)" ;
    ] ;
    shacl:property [
        shacl:path jtbd:metricName ;
        shacl:datatype xsd:string ;
        shacl:minCount 1 ;
        shacl:description "Measurable outcome must have metric name" ;
    ] ;
    shacl:property [
        shacl:path jtbd:targetValue ;
        shacl:datatype xsd:string ;
        shacl:minCount 1 ;
        shacl:description "Measurable outcome must have target value" ;
    ] .

jtbd:PainpointShape a shacl:NodeShape ;
    shacl:targetClass jtbd:Painpoint ;
    shacl:property [
        shacl:path jtbd:painpointDescription ;
        shacl:datatype xsd:string ;
        shacl:minCount 1 ;
        shacl:minLength 15 ;
    ] ;
    shacl:property [
        shacl:path jtbd:severity ;
        shacl:datatype xsd:integer ;
        shacl:minInclusive 1 ;
        shacl:maxInclusive 10 ;
    ] .

jtbd:FeatureJobMappingShape a shacl:NodeShape ;
    shacl:targetClass sk:Feature ;
    shacl:property [
        shacl:path jtbd:addressesJob ;
        shacl:class jtbd:Job ;
        shacl:minCount 1 ;
        shacl:message "Feature must address at least one customer job" ;
    ] ;
    shacl:property [
        shacl:path jtbd:deliversOutcome ;
        shacl:class jtbd:Outcome ;
        shacl:minCount 1 ;
        shacl:message "Feature must deliver at least one measurable outcome" ;
    ] .
```

### Feature Extension Example

Here's how existing `sk:Feature` integrates with JTBD:

```turtle
@prefix : <http://uvmgr.io/cli#> .
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix sk: <http://github.com/github/spec-kit#> .

# ============================================================================
# Feature with JTBD Integration
# ============================================================================

:DepsAddCommand a sk:Feature ;
    # Existing feature properties
    sk:featureName "deps add" ;
    sk:featureBranch "001-deps-add" ;
    sk:status "In Progress" ;

    # JTBD Integration (NEW)
    jtbd:addressesJob :ManageDependenciesJob ;
    jtbd:addressesJob :AddPythonPackageJob ;

    jtbd:deliversOutcome :FasterDevelopmentOutcome ;
    jtbd:deliversOutcome :ZeroContextSwitchingOutcome ;
    jtbd:deliversOutcome :GuaranteedConsistencyOutcome ;

    jtbd:reducesPainpoint :ManualPyprojectEditingPainpoint ;
    jtbd:reducesPainpoint :DependencyConflictsPainpoint ;

    jtbd:enablesProgressMaker :CLIWorkflowProgressMaker ;
    jtbd:enablesProgressMaker :AutomatedValidationProgressMaker ;
    .

# ============================================================================
# Jobs (Customer Jobs to Accomplish)
# ============================================================================

:ManageDependenciesJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Manage project dependencies without breaking RDF-first workflow" ;
    jtbd:jobDescription "As an RDF designer working on specification-driven projects, I need to add, update, and remove Python dependencies without leaving my RDF-first workflow or manually editing configuration files." ;
    jtbd:frequency "Daily" ;
    jtbd:performedBy :RDFDesignerSegment ;
    jtbd:hasOutcome :FasterDevelopmentOutcome ;
    jtbd:hasOutcome :ZeroContextSwitchingOutcome ;
    jtbd:hasPainpoint :ManualPyprojectEditingPainpoint ;
    jtbd:hasContext :RDFFirstDevelopmentContext ;
    .

:AddPythonPackageJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Add Python packages with minimal cognitive overhead" ;
    jtbd:jobDescription "As a Python developer, I need to add packages to my project quickly without remembering complex uv syntax or worrying about version conflicts." ;
    jtbd:frequency "Daily" ;
    jtbd:performedBy :PythonDeveloperSegment ;
    jtbd:hasOutcome :FasterDevelopmentOutcome ;
    jtbd:hasOutcome :GuaranteedConsistencyOutcome ;
    jtbd:hasPainpoint :DependencyConflictsPainpoint ;
    .

# ============================================================================
# Outcomes (Measurable Results)
# ============================================================================

:FasterDevelopmentOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Reduce time to add dependency from 5 minutes to 30 seconds" ;
    jtbd:priority 9 ;
    jtbd:metricName "time-to-add-dependency" ;
    jtbd:targetValue "< 30 seconds" ;
    jtbd:hasMeasurement :FasterDevelopmentMeasurement_20251221 ;
    .

:ZeroContextSwitchingOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Stay in spec-kit CLI without switching to editor or terminal" ;
    jtbd:priority 8 ;
    jtbd:metricName "context-switches-per-dependency-add" ;
    jtbd:targetValue "0" ;
    .

:GuaranteedConsistencyOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "100% dependency additions validated against project requirements" ;
    jtbd:priority 10 ;
    jtbd:metricName "validation-success-rate" ;
    jtbd:targetValue "100%" ;
    .

# ============================================================================
# Painpoints (Obstacles to Job Success)
# ============================================================================

:ManualPyprojectEditingPainpoint a jtbd:Painpoint ;
    jtbd:painpointDescription "Manually editing pyproject.toml is error-prone, requires context switching, and breaks RDF-first workflow" ;
    jtbd:severity 8 ;
    .

:DependencyConflictsPainpoint a jtbd:Painpoint ;
    jtbd:painpointDescription "Dependency version conflicts discovered late, after manual editing, requiring rework" ;
    jtbd:severity 9 ;
    .

# ============================================================================
# Progress Makers (Capabilities Enabling Success)
# ============================================================================

:CLIWorkflowProgressMaker a jtbd:ProgressMaker ;
    jtbd:progressMakerDescription "Command-line interface keeps developer in terminal, no editor context switch required" ;
    .

:AutomatedValidationProgressMaker a jtbd:ProgressMaker ;
    jtbd:progressMakerDescription "Automated validation ensures dependency compatibility before modification" ;
    .

# ============================================================================
# Customer Segments
# ============================================================================

:RDFDesignerSegment a jtbd:CustomerSegment ;
    rdfs:label "RDF Designers" ;
    rdfs:comment "Developers working primarily with RDF specifications and semantic data" ;
    .

:PythonDeveloperSegment a jtbd:CustomerSegment ;
    rdfs:label "Python Developers" ;
    rdfs:comment "Software engineers building Python applications" ;
    .

# ============================================================================
# Job Contexts
# ============================================================================

:RDFFirstDevelopmentContext a jtbd:JobContext ;
    rdfs:label "RDF-First Development" ;
    rdfs:comment "Development workflow where RDF specifications are primary artifacts" ;
    .

# ============================================================================
# Measurements (Actual Outcome Data)
# ============================================================================

:FasterDevelopmentMeasurement_20251221 a jtbd:Measurement ;
    jtbd:currentValue "18 seconds (average over 50 operations)" ;
    jtbd:measurementDate "2025-12-21T12:00:00Z"^^xsd:dateTime ;
    jtbd:status "exceeds-target" ;
    rdfs:comment "Measured via OpenTelemetry spans on deps-add command execution" ;
    .
```

---

## SPARQL Query Patterns

### Query 1: Extract Feature-Job Mappings

**File:** `sparql/extract-feature-jobs.rq`

```sparql
PREFIX sk: <http://github.com/github/spec-kit#>
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Extract all features with their addressed jobs and delivered outcomes
# Used for generating "Why This Feature Exists" documentation

SELECT DISTINCT
  ?featureName
  ?jobTitle
  ?jobDescription
  ?jobFrequency
  ?customerSegment
  ?outcomeDescription
  ?priority
  ?targetValue
WHERE {
  ?feature a sk:Feature .
  ?feature sk:featureName ?featureName .

  # Jobs addressed
  ?feature jtbd:addressesJob ?job .
  ?job jtbd:jobTitle ?jobTitle .
  ?job jtbd:jobDescription ?jobDescription .
  OPTIONAL { ?job jtbd:frequency ?jobFrequency }

  # Customer segments
  ?job jtbd:performedBy ?segment .
  ?segment rdfs:label ?customerSegment .

  # Outcomes delivered
  ?feature jtbd:deliversOutcome ?outcome .
  ?outcome jtbd:outcomeDescription ?outcomeDescription .
  ?outcome jtbd:priority ?priority .
  OPTIONAL { ?outcome jtbd:targetValue ?targetValue }
}
ORDER BY DESC(?priority) ?featureName
```

### Query 2: Extract Painpoints and Progress Makers

**File:** `sparql/extract-painpoints-progress.rq`

```sparql
PREFIX sk: <http://github.com/github/spec-kit#>
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Extract painpoints reduced and progress makers enabled by features
# Used for generating problem-solution documentation

SELECT DISTINCT
  ?featureName
  ?painpointDescription
  ?severity
  ?progressMakerDescription
WHERE {
  ?feature a sk:Feature .
  ?feature sk:featureName ?featureName .

  # Painpoints reduced (optional - some features may not reduce painpoints)
  OPTIONAL {
    ?feature jtbd:reducesPainpoint ?painpoint .
    ?painpoint jtbd:painpointDescription ?painpointDescription .
    ?painpoint jtbd:severity ?severity .
  }

  # Progress makers enabled
  OPTIONAL {
    ?feature jtbd:enablesProgressMaker ?progressMaker .
    ?progressMaker jtbd:progressMakerDescription ?progressMakerDescription .
  }
}
ORDER BY DESC(?severity) ?featureName
```

### Query 3: Extract Outcome Measurements

**File:** `sparql/extract-outcome-measurements.rq`

```sparql
PREFIX sk: <http://github.com/github/spec-kit#>
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Extract outcome measurements for metrics dashboard
# Shows whether features are delivering promised outcomes

SELECT DISTINCT
  ?featureName
  ?outcomeDescription
  ?metricName
  ?targetValue
  ?currentValue
  ?measurementDate
  ?status
WHERE {
  ?feature a sk:Feature .
  ?feature sk:featureName ?featureName .

  # Outcomes delivered
  ?feature jtbd:deliversOutcome ?outcome .
  ?outcome jtbd:outcomeDescription ?outcomeDescription .
  ?outcome jtbd:metricName ?metricName .
  ?outcome jtbd:targetValue ?targetValue .

  # Measurements (optional - may not have measurements yet)
  OPTIONAL {
    ?outcome jtbd:hasMeasurement ?measurement .
    ?measurement jtbd:currentValue ?currentValue .
    ?measurement jtbd:measurementDate ?measurementDate .
    ?measurement jtbd:status ?status .
  }
}
ORDER BY ?measurementDate DESC ?featureName
```

### Query 4: Job-Feature Coverage Analysis

**File:** `sparql/analyze-job-coverage.rq`

```sparql
PREFIX sk: <http://github.com/github/spec-kit#>
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Identify jobs without features addressing them (gaps)
# Used for product planning and roadmap prioritization

SELECT DISTINCT
  ?jobTitle
  ?jobDescription
  ?jobFrequency
  ?customerSegment
  (COUNT(?feature) AS ?featureCount)
WHERE {
  ?job a jtbd:Job .
  ?job jtbd:jobTitle ?jobTitle .
  ?job jtbd:jobDescription ?jobDescription .
  ?job jtbd:frequency ?jobFrequency .
  ?job jtbd:performedBy ?segment .
  ?segment rdfs:label ?customerSegment .

  # Left join to find jobs without features
  OPTIONAL {
    ?feature jtbd:addressesJob ?job .
  }
}
GROUP BY ?jobTitle ?jobDescription ?jobFrequency ?customerSegment
HAVING (COUNT(?feature) = 0)
ORDER BY ?jobFrequency
```

---

## Tera Template Extensions

### Template 1: Feature Documentation with JTBD

**File:** `templates/feature-with-jtbd.tera`

```jinja2
# {{ results[0].featureName }}

## Why This Feature Exists

### Customer Jobs Addressed

{% for job in results | group_by(attribute="jobTitle") | unique %}
**{{ loop.index }}. {{ job.jobTitle }}** ({{ job.customerSegment }}, {{ job.jobFrequency }})

{{ job.jobDescription }}

{% endfor %}

### Outcomes Delivered

{% for outcome in results | sort(attribute="priority") | reverse %}
- **{{ outcome.outcomeDescription }}**
  - Priority: {{ outcome.priority }}/10
  {% if outcome.targetValue %}
  - Target: {{ outcome.targetValue }}
  {% endif %}
  {% if outcome.currentValue %}
  - Current Performance: {{ outcome.currentValue }} ({{ outcome.status | replace(from="-", to=" ") | title }})
  {% endif %}
{% endfor %}

### Problems Solved

{% for painpoint in results | filter(attribute="painpointDescription") | unique %}
- **{{ painpoint.painpointDescription }}** (Severity: {{ painpoint.severity }}/10)
{% endfor %}

### Capabilities Enabled

{% for progressMaker in results | filter(attribute="progressMakerDescription") | unique %}
- {{ progressMaker.progressMakerDescription }}
{% endfor %}

---

## Feature Specification

[Standard feature specification content follows...]
```

### Template 2: Metrics Dashboard

**File:** `templates/metrics-dashboard.tera`

```jinja2
# Outcome Metrics Dashboard

**Generated:** {{ now() | date(format="%Y-%m-%d %H:%M:%S UTC") }}
**Total Features Tracked:** {{ results | group_by(attribute="featureName") | length }}

---

{% for feature in results | group_by(attribute="featureName") %}
## {{ feature.featureName }}

| Outcome | Metric | Target | Current | Status |
|---------|--------|--------|---------|--------|
{% for outcome in results | filter(attribute="featureName", value=feature.featureName) %}
| {{ outcome.outcomeDescription }} | {{ outcome.metricName }} | {{ outcome.targetValue }} | {{ outcome.currentValue | default(value="Not measured") }} | {{ outcome.status | default(value="pending") | replace(from="-", to=" ") | title }} |
{% endfor %}

{% if feature.measurementDate %}
*Last measured: {{ feature.measurementDate | date(format="%Y-%m-%d") }}*
{% else %}
*No measurements yet*
{% endif %}

---

{% endfor %}

## Summary

{% set total_outcomes = results | length %}
{% set measured_outcomes = results | filter(attribute="currentValue") | length %}
{% set exceeds_target = results | filter(attribute="status", value="exceeds-target") | length %}
{% set meets_target = results | filter(attribute="status", value="meets-target") | length %}
{% set below_target = results | filter(attribute="status", value="below-target") | length %}

- **Total Outcomes:** {{ total_outcomes }}
- **Measured:** {{ measured_outcomes }} ({{ measured_outcomes * 100 / total_outcomes }}%)
- **Exceeding Target:** {{ exceeds_target }}
- **Meeting Target:** {{ meets_target }}
- **Below Target:** {{ below_target }}

{% if below_target > 0 %}
⚠️ **Attention Required:** {{ below_target }} outcome(s) below target
{% endif %}
```

### Template 3: Job Coverage Report

**File:** `templates/job-coverage-report.tera`

```jinja2
# Job Coverage Analysis

**Generated:** {{ now() | date(format="%Y-%m-%d") }}

---

## Unaddressed Customer Jobs

These jobs have **zero** features addressing them and represent potential opportunities:

{% if results | length > 0 %}
{% for job in results %}
### {{ loop.index }}. {{ job.jobTitle }}

- **Customer Segment:** {{ job.customerSegment }}
- **Frequency:** {{ job.jobFrequency }}
- **Current Feature Count:** {{ job.featureCount }}

**Description:**
{{ job.jobDescription }}

**Recommendation:** Consider prioritizing features to address this {% if job.jobFrequency == "Daily" %}high-frequency{% elif job.jobFrequency == "Weekly" %}medium-frequency{% else %}low-frequency{% endif %} job.

---

{% endfor %}
{% else %}
✅ **All identified customer jobs are addressed by at least one feature.**
{% endif %}

## Next Steps

1. Review unaddressed jobs with product team
2. Create feature specifications for high-priority gaps
3. Validate job descriptions with customer research
4. Schedule outcome measurement for existing features
```

### Template 4: Code Docstring with JTBD

**File:** `templates/command-with-jtbd-docstring.tera`

```jinja2
"""{{ results[0].featureName }} - {{ results[0].description }}

Why This Command Exists
------------------------
{% for job in results | group_by(attribute="jobTitle") | unique %}
- Addresses: {{ job.jobTitle }}
  ({{ job.customerSegment }}, {{ job.jobFrequency }})
{% endfor %}

Outcomes Delivered
------------------
{% for outcome in results | sort(attribute="priority") | reverse | slice(end=3) %}
- {{ outcome.outcomeDescription }}
  Target: {{ outcome.targetValue }}
{% endfor %}

Problems Solved
---------------
{% for painpoint in results | filter(attribute="painpointDescription") | unique | slice(end=3) %}
- {{ painpoint.painpointDescription }}
{% endfor %}

Usage
-----
{{ results[0].usageExample }}

OpenTelemetry
-------------
Span: {{ results[0].telemetryName }}
Attributes: feature.name, job.title, outcome.metric
"""
```

---

## ggen.toml Configuration

### Extended Configuration with JTBD Transformations

```toml
# ============================================================================
# JTBD TRANSFORMATIONS - Outcome-Driven Documentation
# ============================================================================

[[transformations.jtbd]]
name = "feature-job-mappings"
description = "Generate feature documentation with JTBD context"
input_files = [
  "ontology/cli-commands-uvmgr.ttl",
  "ontology/jtbd-schema.ttl",
  "memory/customer-jobs.ttl",
  "memory/jobs-mapping.ttl"
]
schema_files = [
  "ontology/spec-kit-schema.ttl",
  "ontology/jtbd-schema.ttl"
]
sparql_query = "sparql/extract-feature-jobs.rq"
template = "templates/feature-with-jtbd.tera"
output_file = "docs/features/FEATURE_JOBS_MAPPING.md"
deterministic = true

[[transformations.jtbd]]
name = "outcome-metrics-dashboard"
description = "Generate outcome metrics dashboard from measurements"
input_files = [
  "memory/outcome-measurements.ttl",
  "memory/jobs-mapping.ttl"
]
schema_files = [
  "ontology/spec-kit-schema.ttl",
  "ontology/jtbd-schema.ttl"
]
sparql_query = "sparql/extract-outcome-measurements.rq"
template = "templates/metrics-dashboard.tera"
output_file = "docs/metrics/OUTCOME_METRICS.md"
deterministic = true

[[transformations.jtbd]]
name = "job-coverage-analysis"
description = "Identify customer jobs without features (product gaps)"
input_files = [
  "memory/customer-jobs.ttl",
  "memory/jobs-mapping.ttl",
  "ontology/cli-commands-uvmgr.ttl"
]
schema_files = [
  "ontology/spec-kit-schema.ttl",
  "ontology/jtbd-schema.ttl"
]
sparql_query = "sparql/analyze-job-coverage.rq"
template = "templates/job-coverage-report.tera"
output_file = "docs/planning/JOB_COVERAGE_GAPS.md"
deterministic = true

[[transformations.jtbd]]
name = "painpoints-progress-report"
description = "Document painpoints and progress makers"
input_files = [
  "memory/jobs-mapping.ttl"
]
schema_files = [
  "ontology/spec-kit-schema.ttl",
  "ontology/jtbd-schema.ttl"
]
sparql_query = "sparql/extract-painpoints-progress.rq"
template = "templates/painpoints-progress-report.tera"
output_file = "docs/features/PAINPOINTS_PROGRESS.md"
deterministic = true

# ============================================================================
# CODE GENERATION WITH JTBD DOCSTRINGS
# ============================================================================

[[transformations.code]]
name = "uvmgr-deps-command-with-jtbd"
description = "Generate deps command with JTBD-enriched docstrings"
input_files = [
  "ontology/cli-commands-uvmgr.ttl",
  "memory/jobs-mapping.ttl"
]
schema_files = [
  "ontology/spec-kit-schema.ttl",
  "ontology/jtbd-schema.ttl"
]
sparql_query = "sparql/extract-commands-with-jobs.rq"
sparql_params = { command_name = "deps" }
template = "templates/cli-command-with-jtbd.tera"
output_file = "src/specify_cli/commands/deps.py"
deterministic = true

# [Additional commands follow same pattern...]

# ============================================================================
# PIPELINE CONFIGURATION
# ============================================================================

[pipeline]
stages = ["normalize", "extract", "emit", "canonicalize", "receipt"]

# μ₁ Normalization: Validate JTBD SHACL shapes
[pipeline.normalize]
enabled = true
fail_on_validation_error = true
shacl_shapes = [
  "ontology/jtbd-schema.ttl"
]

# μ₂ Extraction: Execute SPARQL to join features ↔ jobs ↔ outcomes
[pipeline.extract]
enabled = true
timeout_seconds = 30

# μ₃ Emission: Render Tera templates with JTBD context
[pipeline.emit]
enabled = true
template_engine = "tera"

# μ₄ Canonicalization: Format output
[pipeline.canonicalize]
enabled = true
line_ending = "lf"
trim_trailing_whitespace = true
ensure_final_newline = true

# μ₅ Receipt: SHA256 proof of transformation
[pipeline.receipt]
enabled = true
hash_algorithm = "sha256"
write_manifest = true
```

---

## Measurement Framework

### 1. Outcome Measurement Types

| Metric Category | Example Metrics | Measurement Method |
|-----------------|-----------------|-------------------|
| **Performance** | Time to complete job, Throughput, Latency | OpenTelemetry spans, system metrics |
| **Quality** | Error rate, Success rate, Validation pass rate | Application logs, test results |
| **User Experience** | Context switches, Cognitive load, Learning time | User surveys, observability data |
| **Business Value** | Adoption rate, Feature usage, Customer satisfaction | Analytics, customer feedback |

### 2. Automated Measurement via OpenTelemetry

**Integration Pattern:**

```python
from opentelemetry import trace
from specify_cli.core.telemetry import span

@span("deps.add", attributes={
    "feature.name": "deps-add",
    "job.title": "manage-dependencies",
    "outcome.metric": "time-to-add-dependency"
})
def deps_add(package: str) -> None:
    """Add dependency with JTBD outcome tracking."""
    start_time = time.time()

    # Implementation
    result = add_package_to_pyproject(package)

    # Record outcome measurement
    duration = time.time() - start_time
    trace.get_current_span().set_attribute("outcome.current_value", f"{duration:.2f}s")
    trace.get_current_span().set_attribute("outcome.target_value", "< 30s")

    if duration < 30:
        trace.get_current_span().set_attribute("outcome.status", "exceeds-target")
    else:
        trace.get_current_span().set_attribute("outcome.status", "below-target")

    return result
```

### 3. Measurement Pipeline

```
1. Feature Execution
   ↓
2. OTEL Span with Outcome Attributes
   ↓
3. Export to OTLP Collector
   ↓
4. Transform to RDF Measurement
   ↓
5. Update outcome-measurements.ttl
   ↓
6. Run ggen sync
   ↓
7. Generate Updated Metrics Dashboard
```

### 4. Feedback Loop Implementation

**File:** `scripts/measure-outcomes.py`

```python
#!/usr/bin/env python3
"""
Extract outcome measurements from OpenTelemetry spans and update RDF.

Constitutional equation: outcome-measurements.ttl ⊆ μ⁻¹(otel-spans)
(Inverse transformation: derive RDF from observed behavior)
"""

import json
from datetime import datetime
from pathlib import Path
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, XSD

JTBD = Namespace("http://github.com/github/spec-kit/jtbd#")

def extract_measurements_from_otel(spans_file: Path) -> list[dict]:
    """Extract outcome measurements from OTEL spans JSON."""
    with open(spans_file) as f:
        spans = json.load(f)

    measurements = []
    for span in spans:
        attrs = span.get("attributes", {})
        if "outcome.metric" in attrs:
            measurements.append({
                "feature": attrs.get("feature.name"),
                "job": attrs.get("job.title"),
                "metric": attrs["outcome.metric"],
                "current_value": attrs.get("outcome.current_value"),
                "target_value": attrs.get("outcome.target_value"),
                "status": attrs.get("outcome.status"),
                "timestamp": span["timestamp"]
            })

    return measurements

def update_rdf_measurements(measurements: list[dict], output_file: Path) -> None:
    """Update outcome-measurements.ttl with new measurements."""
    g = Graph()
    g.bind("jtbd", JTBD)

    for m in measurements:
        measurement_uri = URIRef(f"http://example.org/measurement/{m['feature']}/{m['timestamp']}")

        g.add((measurement_uri, RDF.type, JTBD.Measurement))
        g.add((measurement_uri, JTBD.currentValue, Literal(m["current_value"])))
        g.add((measurement_uri, JTBD.measurementDate, Literal(m["timestamp"], datatype=XSD.dateTime)))
        g.add((measurement_uri, JTBD.status, Literal(m["status"])))

    # Serialize to Turtle
    g.serialize(destination=output_file, format="turtle")
    print(f"Updated {output_file} with {len(measurements)} measurements")

if __name__ == "__main__":
    spans_file = Path("traces/otel-spans.json")
    output_file = Path("memory/outcome-measurements.ttl")

    measurements = extract_measurements_from_otel(spans_file)
    update_rdf_measurements(measurements, output_file)
```

### 5. Continuous Validation

**Pre-commit Hook Integration:**

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate that all features address at least one job
echo "Validating feature-job mappings..."
ggen validate --shacl ontology/jtbd-schema.ttl memory/jobs-mapping.ttl

if [ $? -ne 0 ]; then
    echo "❌ JTBD validation failed: All features must address at least one customer job"
    exit 1
fi

# Check for unaddressed high-priority jobs
echo "Checking job coverage gaps..."
ggen sync --transformation job-coverage-analysis

if grep -q "Daily" docs/planning/JOB_COVERAGE_GAPS.md; then
    echo "⚠️  Warning: Daily jobs exist without features"
fi

echo "✅ JTBD validation passed"
```

---

## Concrete Examples: uvmgr Commands

### Example 1: `deps add` Command

**Full RDF Specification with JTBD**

```turtle
@prefix : <http://uvmgr.io/cli#> .
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix sk: <http://github.com/github/spec-kit#> .

# ============================================================================
# deps add - Complete JTBD Integration Example
# ============================================================================

:DepsAddCommand a sk:Feature ;
    sk:featureName "deps add" ;
    sk:featureBranch "001-deps-add" ;
    sk:status "In Progress" ;
    sk:created "2025-12-21"^^xsd:date ;

    # Traditional specification
    sk:hasUserStory :DepsAddUserStory1 ;
    sk:hasFunctionalRequirement :DepsAddFR001 ;
    sk:hasSuccessCriterion :DepsAddSC001 ;

    # JTBD Integration
    jtbd:addressesJob :ManageDependenciesJob ;
    jtbd:addressesJob :AddPythonPackageJob ;
    jtbd:addressesJob :ValidateDependencyCompatibilityJob ;

    jtbd:deliversOutcome :FasterDevelopmentOutcome ;
    jtbd:deliversOutcome :ZeroContextSwitchingOutcome ;
    jtbd:deliversOutcome :GuaranteedConsistencyOutcome ;
    jtbd:deliversOutcome :AutomatedValidationOutcome ;

    jtbd:reducesPainpoint :ManualPyprojectEditingPainpoint ;
    jtbd:reducesPainpoint :DependencyConflictsPainpoint ;
    jtbd:reducesPainpoint :UnclearVersionSyntaxPainpoint ;

    jtbd:enablesProgressMaker :CLIWorkflowProgressMaker ;
    jtbd:enablesProgressMaker :AutomatedValidationProgressMaker ;
    jtbd:enablesProgressMaker :InstantFeedbackProgressMaker ;
    .

# Jobs
:ManageDependenciesJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Manage project dependencies without breaking RDF-first workflow" ;
    jtbd:jobDescription "As an RDF designer, I need to add, update, and remove dependencies while staying in my RDF-first workflow." ;
    jtbd:frequency "Daily" ;
    jtbd:performedBy :RDFDesignerSegment ;
    jtbd:hasOutcome :FasterDevelopmentOutcome ;
    jtbd:hasOutcome :ZeroContextSwitchingOutcome ;
    jtbd:hasPainpoint :ManualPyprojectEditingPainpoint ;
    jtbd:hasContext :RDFFirstDevelopmentContext ;
    .

:AddPythonPackageJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Add Python packages with minimal cognitive overhead" ;
    jtbd:jobDescription "As a Python developer, I need to add packages quickly without remembering uv syntax." ;
    jtbd:frequency "Daily" ;
    jtbd:performedBy :PythonDeveloperSegment ;
    jtbd:hasOutcome :FasterDevelopmentOutcome ;
    jtbd:hasPainpoint :UnclearVersionSyntaxPainpoint ;
    .

:ValidateDependencyCompatibilityJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Ensure dependency compatibility before installation" ;
    jtbd:jobDescription "As a DevOps engineer, I need to validate dependencies won't break the build before adding them." ;
    jtbd:frequency "Weekly" ;
    jtbd:performedBy :DevOpsEngineerSegment ;
    jtbd:hasOutcome :GuaranteedConsistencyOutcome ;
    jtbd:hasOutcome :AutomatedValidationOutcome ;
    jtbd:hasPainpoint :DependencyConflictsPainpoint ;
    .

# Outcomes
:FasterDevelopmentOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Reduce time to add dependency from 5 minutes to 30 seconds" ;
    jtbd:priority 9 ;
    jtbd:metricName "time-to-add-dependency" ;
    jtbd:targetValue "< 30 seconds" ;
    jtbd:hasMeasurement :FasterDevelopmentMeasurement_20251221 ;
    .

:ZeroContextSwitchingOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Stay in CLI without switching to editor" ;
    jtbd:priority 8 ;
    jtbd:metricName "context-switches-per-operation" ;
    jtbd:targetValue "0" ;
    .

:GuaranteedConsistencyOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "100% of dependency additions validated" ;
    jtbd:priority 10 ;
    jtbd:metricName "validation-success-rate" ;
    jtbd:targetValue "100%" ;
    .

:AutomatedValidationOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Dependency conflicts detected before installation" ;
    jtbd:priority 9 ;
    jtbd:metricName "conflict-detection-rate" ;
    jtbd:targetValue "100%" ;
    .

# Painpoints
:ManualPyprojectEditingPainpoint a jtbd:Painpoint ;
    jtbd:painpointDescription "Manually editing pyproject.toml is error-prone and breaks RDF workflow" ;
    jtbd:severity 8 ;
    .

:DependencyConflictsPainpoint a jtbd:Painpoint ;
    jtbd:painpointDescription "Version conflicts discovered late, after editing, requiring rework" ;
    jtbd:severity 9 ;
    .

:UnclearVersionSyntaxPainpoint a jtbd:Painpoint ;
    jtbd:painpointDescription "Remembering uv version syntax (>=, ^, ~) is cognitive overhead" ;
    jtbd:severity 6 ;
    .

# Progress Makers
:CLIWorkflowProgressMaker a jtbd:ProgressMaker ;
    jtbd:progressMakerDescription "CLI keeps developer in terminal without editor context switch" ;
    .

:AutomatedValidationProgressMaker a jtbd:ProgressMaker ;
    jtbd:progressMakerDescription "Validation ensures compatibility before modification" ;
    .

:InstantFeedbackProgressMaker a jtbd:ProgressMaker ;
    jtbd:progressMakerDescription "Immediate feedback on success or conflicts" ;
    .

# Measurements
:FasterDevelopmentMeasurement_20251221 a jtbd:Measurement ;
    jtbd:currentValue "18 seconds (avg over 50 ops)" ;
    jtbd:measurementDate "2025-12-21T12:00:00Z"^^xsd:dateTime ;
    jtbd:status "exceeds-target" ;
    rdfs:comment "Measured via OTEL spans on deps-add executions" ;
    .
```

**Generated Documentation (from μ transformation):**

````markdown
# deps add - Add Python Dependency to Project

## Why This Feature Exists

### Customer Jobs Addressed

**1. Manage project dependencies without breaking RDF-first workflow** (RDF Designers, Daily)

As an RDF designer, I need to add, update, and remove dependencies while staying in my RDF-first workflow.

**2. Add Python packages with minimal cognitive overhead** (Python Developers, Daily)

As a Python developer, I need to add packages quickly without remembering uv syntax.

**3. Ensure dependency compatibility before installation** (DevOps Engineers, Weekly)

As a DevOps engineer, I need to validate dependencies won't break the build before adding them.

### Outcomes Delivered

- **100% of dependency additions validated**
  - Priority: 10/10
  - Target: 100%
  - Current Performance: Not yet measured

- **Reduce time to add dependency from 5 minutes to 30 seconds**
  - Priority: 9/10
  - Target: < 30 seconds
  - Current Performance: 18 seconds (avg over 50 ops) (Exceeds Target)

- **Dependency conflicts detected before installation**
  - Priority: 9/10
  - Target: 100%

- **Stay in CLI without switching to editor**
  - Priority: 8/10
  - Target: 0

### Problems Solved

- **Version conflicts discovered late, after editing, requiring rework** (Severity: 9/10)
- **Manually editing pyproject.toml is error-prone and breaks RDF workflow** (Severity: 8/10)
- **Remembering uv version syntax (>=, ^, ~) is cognitive overhead** (Severity: 6/10)

### Capabilities Enabled

- CLI keeps developer in terminal without editor context switch
- Validation ensures compatibility before modification
- Immediate feedback on success or conflicts

---

## Feature Specification

[Traditional spec-kit feature content follows...]
````

### Example 2: `tests run` Command

**RDF Specification:**

```turtle
:TestsRunCommand a sk:Feature ;
    sk:featureName "tests run" ;

    jtbd:addressesJob :ExecuteTestSuiteJob ;
    jtbd:addressesJob :VerifyCodeQualityJob ;

    jtbd:deliversOutcome :FastFeedbackOutcome ;
    jtbd:deliversOutcome :ComprehensiveCoverageOutcome ;
    jtbd:deliversOutcome :CICompatibilityOutcome ;

    jtbd:reducesPainpoint :SlowTestExecutionPainpoint ;
    jtbd:reducesPainpoint :UnclearFailureMessagesPainpoint ;

    jtbd:enablesProgressMaker :ParallelExecutionProgressMaker ;
    jtbd:enablesProgressMaker :RichOutputProgressMaker ;
    .

:ExecuteTestSuiteJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Run test suite with fast feedback" ;
    jtbd:jobDescription "As a Python developer, I need to run tests quickly to validate changes before commit." ;
    jtbd:frequency "Daily" ;
    jtbd:performedBy :PythonDeveloperSegment ;
    jtbd:hasOutcome :FastFeedbackOutcome ;
    jtbd:hasPainpoint :SlowTestExecutionPainpoint ;
    .

:FastFeedbackOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Test suite completes in under 10 seconds" ;
    jtbd:priority 9 ;
    jtbd:metricName "test-suite-duration" ;
    jtbd:targetValue "< 10 seconds" ;
    .
```

### Example 3: `otel validate` Command

**RDF Specification:**

```turtle
:OtelValidateCommand a sk:Feature ;
    sk:featureName "otel validate" ;

    jtbd:addressesJob :EnsureObservabilityJob ;
    jtbd:addressesJob :DebugProductionIssuesJob ;

    jtbd:deliversOutcome :CompleteTelemetryOutcome ;
    jtbd:deliversOutcome :EarlyDetectionOutcome ;

    jtbd:reducesPainpoint :MissingTelemetryPainpoint ;
    jtbd:reducesPainpoint :LateProblemDiscoveryPainpoint ;

    jtbd:enablesProgressMaker :AutomatedValidationProgressMaker ;
    .

:EnsureObservabilityJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Ensure all code paths have telemetry before deployment" ;
    jtbd:jobDescription "As an SRE, I need to verify telemetry coverage so I can debug production issues." ;
    jtbd:frequency "Weekly" ;
    jtbd:performedBy :SRESegment ;
    jtbd:hasOutcome :CompleteTelemetryOutcome ;
    jtbd:hasPainpoint :MissingTelemetryPainpoint ;
    .

:CompleteTelemetryOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "100% of command executions instrumented with OTEL" ;
    jtbd:priority 10 ;
    jtbd:metricName "telemetry-coverage" ;
    jtbd:targetValue "100%" ;
    .
```

### Example 4: `docs generate` Command

**RDF Specification:**

```turtle
:DocsGenerateCommand a sk:Feature ;
    sk:featureName "docs generate" ;

    jtbd:addressesJob :MaintainUpToDateDocsJob ;
    jtbd:addressesJob :OnboardNewDevelopersJob ;

    jtbd:deliversOutcome :AlwaysCurrentDocsOutcome ;
    jtbd:deliversOutcome :ZeroStalenessOutcome ;

    jtbd:reducesPainpoint :StaleDocumentationPainpoint ;
    jtbd:reducesPainpoint :ManualDocSyncPainpoint ;

    jtbd:enablesProgressMaker :AutomatedRegenerationProgressMaker ;
    .

:MaintainUpToDateDocsJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "Keep documentation synchronized with code changes" ;
    jtbd:jobDescription "As a technical writer, I need docs to auto-update when code changes so they're never stale." ;
    jtbd:frequency "Daily" ;
    jtbd:performedBy :TechnicalWriterSegment ;
    jtbd:hasOutcome :AlwaysCurrentDocsOutcome ;
    jtbd:hasPainpoint :StaleDocumentationPainpoint ;
    .

:AlwaysCurrentDocsOutcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Documentation regenerated within 5 seconds of code change" ;
    jtbd:priority 8 ;
    jtbd:metricName "doc-sync-delay" ;
    jtbd:targetValue "< 5 seconds" ;
    .
```

---

## Integration Workflow

### Development Workflow with JTBD

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. Identify Customer Job                                       │
│    "As [segment], I need to [job] so I can [outcome]"          │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. Define Job in RDF (customer-jobs.ttl)                       │
│    - Job title, description, frequency                         │
│    - Desired outcomes with metrics                             │
│    - Painpoints and severity                                   │
│    - Customer segment                                          │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Design Feature in RDF (feature.ttl)                         │
│    - Link feature to job via jtbd:addressesJob                │
│    - Link to outcomes via jtbd:deliversOutcome                │
│    - Link to painpoints via jtbd:reducesPainpoint             │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Validate RDF (μ₁ Normalization)                             │
│    ggen validate --shacl jtbd-schema.ttl jobs-mapping.ttl      │
│    - Ensures feature addresses ≥1 job                          │
│    - Ensures job has ≥1 outcome                                │
│    - Validates metric definitions                              │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Generate Code (μ₂-μ₅ Transformation)                        │
│    ggen sync --transformation uvmgr-deps-command-with-jtbd      │
│    - Generates code with JTBD docstrings                       │
│    - Includes "Why This Exists" comments                       │
│    - Instruments OTEL with outcome attributes                  │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Implement & Test (TDD)                                      │
│    - Feature execution generates OTEL spans                    │
│    - Spans include outcome.metric attributes                   │
│    - Tests verify outcome delivery                             │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. Measure Outcomes (Continuous)                               │
│    scripts/measure-outcomes.py                                 │
│    - Extract measurements from OTEL spans                      │
│    - Update outcome-measurements.ttl                           │
│    - Regenerate metrics dashboard                              │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Review & Iterate                                            │
│    - Check metrics dashboard                                   │
│    - Identify outcomes below target                            │
│    - Refine feature or update job definition                   │
│    - Loop back to step 3                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Pre-Commit Validation

```bash
#!/bin/bash
# .git/hooks/pre-commit - JTBD Validation

echo "🔍 Validating JTBD integration..."

# 1. Validate SHACL shapes
echo "  ✓ Validating SHACL shapes..."
ggen validate \
  --shacl ontology/jtbd-schema.ttl \
  memory/jobs-mapping.ttl

# 2. Check for features without jobs
echo "  ✓ Checking feature-job mappings..."
missing_jobs=$(ggen query \
  --query sparql/find-features-without-jobs.rq \
  --input ontology/cli-commands-uvmgr.ttl \
  --input memory/jobs-mapping.ttl \
  | wc -l)

if [ "$missing_jobs" -gt 0 ]; then
    echo "  ❌ Found $missing_jobs features without jobs"
    exit 1
fi

# 3. Check for high-priority unaddressed jobs
echo "  ✓ Checking job coverage..."
ggen sync --transformation job-coverage-analysis

if grep -q "Daily" docs/planning/JOB_COVERAGE_GAPS.md; then
    echo "  ⚠️  Warning: Daily jobs exist without features"
fi

echo "✅ JTBD validation passed"
```

---

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)

**Deliverables:**
- [ ] Create `ontology/jtbd-schema.ttl` with complete JTBD ontology
- [ ] Add SHACL shapes for JTBD validation
- [ ] Create example RDF files:
  - [ ] `memory/customer-jobs-example.ttl`
  - [ ] `memory/jobs-mapping-example.ttl`
- [ ] Validate schemas with `ggen validate`

**Validation:**
```bash
ggen validate --shacl ontology/jtbd-schema.ttl memory/customer-jobs-example.ttl
```

### Phase 2: SPARQL Queries (Week 3)

**Deliverables:**
- [ ] `sparql/extract-feature-jobs.rq`
- [ ] `sparql/extract-painpoints-progress.rq`
- [ ] `sparql/extract-outcome-measurements.rq`
- [ ] `sparql/analyze-job-coverage.rq`
- [ ] Test queries against example data

**Validation:**
```bash
ggen query --query sparql/extract-feature-jobs.rq \
  --input memory/jobs-mapping-example.ttl
```

### Phase 3: Tera Templates (Week 4)

**Deliverables:**
- [ ] `templates/feature-with-jtbd.tera`
- [ ] `templates/metrics-dashboard.tera`
- [ ] `templates/job-coverage-report.tera`
- [ ] `templates/cli-command-with-jtbd.tera`
- [ ] Test templates with example data

**Validation:**
```bash
ggen sync --transformation feature-job-mappings --dry-run
```

### Phase 4: ggen.toml Integration (Week 5)

**Deliverables:**
- [ ] Add JTBD transformations to `docs/ggen.toml`
- [ ] Configure pipeline stages
- [ ] Test end-to-end transformation
- [ ] Verify deterministic output

**Validation:**
```bash
ggen sync --config docs/ggen.toml --transformation feature-job-mappings
diff docs/features/FEATURE_JOBS_MAPPING.md <expected-output>
```

### Phase 5: Real uvmgr Command Integration (Week 6)

**Deliverables:**
- [ ] Create jobs for `deps add` command
- [ ] Create jobs for `tests run` command
- [ ] Create jobs for `otel validate` command
- [ ] Link features to jobs in RDF
- [ ] Generate code with JTBD docstrings

**Validation:**
```bash
ggen sync --transformation uvmgr-deps-command-with-jtbd
python -c "import specify_cli.commands.deps; help(deps)"
# Verify JTBD docstring present
```

### Phase 6: Measurement Framework (Week 7-8)

**Deliverables:**
- [ ] Create `scripts/measure-outcomes.py`
- [ ] Integrate OTEL span attributes for outcomes
- [ ] Test measurement extraction pipeline
- [ ] Generate initial metrics dashboard
- [ ] Set up continuous measurement

**Validation:**
```bash
# Run command with OTEL
specify deps add httpx

# Extract measurements
scripts/measure-outcomes.py

# Verify RDF update
ggen query --query sparql/extract-outcome-measurements.rq \
  --input memory/outcome-measurements.ttl
```

### Phase 7: Documentation & Training (Week 9)

**Deliverables:**
- [ ] Complete this design document
- [ ] Create tutorial: "Adding JTBD to Features"
- [ ] Create cookbook: "Measuring Outcomes"
- [ ] Create video walkthrough
- [ ] Team training session

### Phase 8: Continuous Validation (Week 10)

**Deliverables:**
- [ ] Pre-commit hook for JTBD validation
- [ ] CI/CD pipeline integration
- [ ] Metrics dashboard auto-update
- [ ] Alerts for outcomes below target

---

## Validation & Testing

### Test Suite Structure

```
tests/
├── jtbd/
│   ├── test_jtbd_schema_validation.py
│   ├── test_feature_job_mapping.py
│   ├── test_outcome_measurement.py
│   ├── test_sparql_queries.py
│   ├── test_template_rendering.py
│   └── test_end_to_end_transformation.py
└── fixtures/
    ├── jtbd-valid.ttl
    ├── jtbd-invalid-missing-job.ttl
    ├── jtbd-invalid-missing-outcome.ttl
    └── measurement-data.json
```

### Test 1: SHACL Validation

```python
# tests/jtbd/test_jtbd_schema_validation.py

def test_valid_job_passes_shacl():
    """Test that valid job RDF passes SHACL validation."""
    result = run_ggen_validate(
        shacl="ontology/jtbd-schema.ttl",
        data="tests/fixtures/jtbd-valid.ttl"
    )
    assert result.returncode == 0

def test_feature_without_job_fails_shacl():
    """Test that feature without job fails SHACL validation."""
    result = run_ggen_validate(
        shacl="ontology/jtbd-schema.ttl",
        data="tests/fixtures/jtbd-invalid-missing-job.ttl"
    )
    assert result.returncode != 0
    assert "must address at least one customer job" in result.stderr
```

### Test 2: SPARQL Query Correctness

```python
# tests/jtbd/test_sparql_queries.py

def test_extract_feature_jobs_query():
    """Test that SPARQL query extracts all feature-job mappings."""
    results = run_ggen_query(
        query="sparql/extract-feature-jobs.rq",
        input_files=["tests/fixtures/jtbd-valid.ttl"]
    )

    assert len(results) == 3  # Expected: 3 job mappings
    assert "Manage project dependencies" in results[0]["jobTitle"]
    assert results[0]["priority"] == 9
```

### Test 3: Template Rendering

```python
# tests/jtbd/test_template_rendering.py

def test_feature_with_jtbd_template():
    """Test that template renders correctly with JTBD data."""
    output = run_ggen_sync(
        transformation="feature-job-mappings",
        config="docs/ggen.toml"
    )

    assert "## Why This Feature Exists" in output
    assert "Customer Jobs Addressed" in output
    assert "Outcomes Delivered" in output
    assert "Priority: 9/10" in output
```

### Test 4: End-to-End Transformation

```python
# tests/jtbd/test_end_to_end_transformation.py

def test_full_transformation_pipeline():
    """Test complete μ transformation with JTBD."""
    # 1. Create test RDF
    create_test_feature_with_jobs("tests/fixtures/test-feature.ttl")

    # 2. Run transformation
    result = run_ggen_sync(
        transformation="uvmgr-deps-command-with-jtbd",
        config="docs/ggen.toml"
    )

    # 3. Verify output
    generated_code = read_file("src/specify_cli/commands/deps.py")

    assert "Why This Command Exists" in generated_code
    assert "Addresses: Manage project dependencies" in generated_code
    assert 'span("deps.add", attributes={"outcome.metric":' in generated_code

    # 4. Verify receipt (μ₅)
    receipt = read_json("src/specify_cli/commands/deps.py.receipt.json")
    assert receipt["hash_algorithm"] == "sha256"
    assert receipt["source_files"] == ["tests/fixtures/test-feature.ttl"]
```

### Test 5: Measurement Extraction

```python
# tests/jtbd/test_outcome_measurement.py

def test_extract_measurements_from_otel():
    """Test extraction of outcome measurements from OTEL spans."""
    # 1. Run command with OTEL
    with otel_collector():
        run_command("specify deps add httpx")

    # 2. Extract spans
    spans = read_otel_spans("traces/otel-spans.json")

    # 3. Extract measurements
    measurements = extract_measurements(spans)

    assert len(measurements) > 0
    assert measurements[0]["metric"] == "time-to-add-dependency"
    assert "current_value" in measurements[0]

    # 4. Update RDF
    update_rdf_measurements(measurements, "memory/outcome-measurements.ttl")

    # 5. Verify RDF
    graph = load_rdf("memory/outcome-measurements.ttl")
    assert graph.query("SELECT ?m WHERE { ?m a jtbd:Measurement }") is not None
```

---

## Conclusion

This JTBD-RDF integration design provides:

1. **Constitutional Foundation**: Clear extension of the constitutional equation to include outcome-driven development
2. **Complete Ontology**: Full RDF schema with SHACL validation for JTBD concepts
3. **Automated Transformations**: SPARQL queries and Tera templates for generating JTBD documentation and code
4. **Measurement Framework**: Continuous outcome tracking via OpenTelemetry and automated RDF updates
5. **Concrete Examples**: Real uvmgr command mappings to customer jobs and outcomes
6. **Implementation Roadmap**: 10-week phased rollout with clear deliverables and validation

### Key Benefits

- **Traceability**: Every feature traceable to customer jobs and measurable outcomes
- **Justification**: Automatic "Why This Exists" documentation
- **Validation**: Pre-commit checks ensure features address jobs
- **Metrics**: Continuous measurement of outcome delivery
- **Feedback Loops**: Production reality feeds back into job definitions

### Next Steps

1. Review and approve this design
2. Begin Phase 1 implementation (JTBD schema creation)
3. Create pilot integration with `deps add` command
4. Validate end-to-end transformation
5. Roll out to remaining uvmgr commands
6. Establish continuous measurement pipeline

---

**Version History:**
- v1.0 (2025-12-21): Initial design specification

**References:**
- Jobs-To-Be-Done Framework: Clayton Christensen
- Spec-Kit Constitutional Equation: `spec.md = μ(feature.ttl)`
- ggen v5.0.2 API: https://github.com/ggen-project/ggen

---

*This design document was generated as part of the spec-kit JTBD integration initiative.*
