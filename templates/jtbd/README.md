# JTBD-Focused Tera Templates

This directory contains Tera templates for generating outcome-driven documentation from Jobs-to-be-Done (JTBD) specifications stored in RDF.

## Template Overview

### 1. Feature Outcome Card (`feature-outcome-card.tera`)

**Purpose**: Generate concise feature cards explaining what job each feature accomplishes, for which persona, and which outcomes it delivers.

**Input Data**: Feature specifications with JTBD mappings

**Expected SPARQL Variables**:
```sparql
?featureName ?featureDescription ?jobTitle ?personaName
?outcome ?outcomeMetric ?successCriteria ?targetValue
?painpoint ?emotionalBenefit ?relatedFeatures
```

**Output**: Markdown feature card

**Example Output**:
```markdown
# deps-add Feature

## Jobs & Outcomes

**RDF Designer Job**: Specify dependency management

**Delivered Outcome**: Add dependencies 50% faster

**Success Metric**: < 10 seconds per add operation
```

---

### 2. JTBD User Story (`jtbd-user-story.tera`)

**Purpose**: Generate user stories in JTBD format explaining customer needs through jobs, outcomes, and pain points.

**Input Data**: Customer segments, jobs, outcomes, and pain points

**Expected SPARQL Variables**:
```sparql
?storyId ?personaName ?jobContext ?desiredOutcome
?featureName ?emotionalBenefit ?painpoint
?acceptanceCriteria ?priority ?estimatedValue
```

**Output**: JTBD-formatted user stories with acceptance criteria

**Example Output**:
```markdown
## User Story: DEPS-001

**As a** RDF Designer trying to add semantic dependencies,
**I need** deps-add command
**So I can** work confidently and stop experiencing manual SPARQL editing
```

---

### 3. Outcome-Focused Documentation (`outcome-focused-docs.tera`)

**Purpose**: Generate user-centric documentation explaining features through the lens of jobs they accomplish and outcomes they deliver.

**Input Data**: Feature specs with complete JTBD context

**Expected SPARQL Variables**:
```sparql
?featureName ?featureDescription ?jobTitle ?personaName
?outcome ?outcomeMetric ?successCriteria ?targetValue
?painpoint ?usageExample ?relatedFeatures ?prerequisites
```

**Output**: Job-focused feature documentation

**Example Sections**:
- Why This Feature Exists
- The Job / The Problem / The Solution
- How It Improves Your Outcomes
- Success Metrics to Track

---

### 4. JTBD Metrics Dashboard (`jtbd-metrics-dashboard.tera`)

**Purpose**: Generate analytics dashboard showing which features deliver which outcomes, with coverage analysis and impact metrics.

**Input Data**: All features with outcome mappings and performance data

**Expected SPARQL Variables**:
```sparql
?outcome ?outcomeDescription ?featureName ?personaName
?successCriteria ?targetValue ?currentValue
?featureStatus ?priority
```

**Output**: HTML/Markdown dashboard with:
- Executive summary
- Outcomes by category
- Coverage analysis
- Impact metrics
- ROI visualization

---

### 5. JTBD Feature Roadmap (`jtbd-roadmap.tera`)

**Purpose**: Generate product roadmap prioritized by job frequency and importance rather than feature complexity.

**Input Data**: Planned features with job analysis data

**Expected SPARQL Variables**:
```sparql
?quarter ?releaseName ?featureName ?jobTitle
?jobFrequency ?jobImportance ?outcome ?personaName
?riskLevel ?mitigation ?dependencies ?estimatedEffort
```

**Output**: Quarterly roadmap showing:
- Features grouped by release
- Priority matrix (frequency × importance)
- Risk assessment
- Dependency timeline
- Persona coverage

---

## Usage Pattern

### 1. Define JTBD Data in RDF

```turtle
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .

# Feature with JTBD mapping
:deps-add-feature a sk:Feature ;
    sk:featureName "deps-add" ;
    sk:featureDescription "Add dependencies to RDF project" ;
    jtbd:accomplishesJob :specify-dependency-job ;
    jtbd:deliversOutcome :faster-dependency-addition ;
    jtbd:targetPersona :rdf-designer ;
    jtbd:resolvesPainpoint "Manual SPARQL editing is error-prone" .

# Job definition
:specify-dependency-job a jtbd:Job ;
    jtbd:jobTitle "Specify dependency management" ;
    jtbd:jobContext "When adding external ontologies to project" ;
    jtbd:jobFrequency "High" ;
    jtbd:jobImportance "Critical" .

# Outcome definition
:faster-dependency-addition a jtbd:Outcome ;
    jtbd:outcomeDescription "Add dependencies 50% faster" ;
    jtbd:outcomeMetric "Time per dependency addition" ;
    jtbd:successCriteria "< 10 seconds" ;
    jtbd:targetValue "10s" .
```

### 2. Create SPARQL Query

```sparql
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>
PREFIX sk: <http://github.com/github/spec-kit#>

SELECT ?featureName ?jobTitle ?outcome ?personaName ?targetValue
WHERE {
    ?feature a sk:Feature ;
        sk:featureName ?featureName ;
        jtbd:accomplishesJob ?job ;
        jtbd:deliversOutcome ?outcome_node ;
        jtbd:targetPersona ?persona .

    ?job jtbd:jobTitle ?jobTitle .
    ?outcome_node jtbd:outcomeDescription ?outcome ;
        jtbd:targetValue ?targetValue .
    ?persona jtbd:personaName ?personaName .
}
```

### 3. Configure Transformation in ggen.toml

```toml
[[transformations.docs]]
name = "feature-outcome-cards"
description = "Generate outcome-driven feature cards"
input_files = ["ontology/features-jtbd.ttl"]
schema_files = ["ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-features.rq"
template = "templates/feature-outcome-card.tera"
output_file = "docs/features/outcome-cards.md"
deterministic = true
```

### 4. Run Transformation

```bash
ggen sync --config docs/ggen.toml
```

---

## JTBD Schema Requirements

To use these templates, your RDF schema should include:

**Core Classes**:
- `jtbd:Job` - A job to be done
- `jtbd:Outcome` - A desired outcome
- `jtbd:Persona` - A customer segment
- `jtbd:Painpoint` - A current frustration
- `jtbd:Feature` - A solution

**Core Properties**:
- `jtbd:accomplishesJob` - Links feature to job
- `jtbd:deliversOutcome` - Links feature to outcome
- `jtbd:targetPersona` - Links feature to persona
- `jtbd:resolvesPainpoint` - Links feature to pain point
- `jtbd:jobFrequency` - How often job occurs
- `jtbd:jobImportance` - How critical job is
- `jtbd:successCriteria` - How to measure success
- `jtbd:targetValue` - Performance target

---

## Example Workflow

1. **Research Phase**: Conduct customer interviews to identify jobs, outcomes, and pain points
2. **Specification Phase**: Document findings in RDF using JTBD ontology
3. **Generation Phase**: Run `ggen sync` to generate documentation
4. **Review Phase**: Validate that generated docs accurately reflect customer needs
5. **Iteration Phase**: Update RDF as you learn more about customer jobs

---

## Benefits

- **Customer-Centric**: Documentation explains features through customer jobs
- **Outcome-Driven**: Focus on measurable outcomes, not feature lists
- **Traceable**: Link features → jobs → outcomes → personas in RDF
- **Maintainable**: Update RDF, regenerate all docs consistently
- **Analytical**: Dashboard and roadmap provide strategic insights

---

## References

- [Jobs to be Done Framework](https://jtbd.info/)
- [Outcome-Driven Innovation](https://jobs-to-be-done.com/)
- [Spec-Kit JTBD Schema](../../ontology/jtbd-schema.ttl)
- [Example JTBD Specifications](../../examples/jtbd/)

---

*Last updated: 2025-12-21*
