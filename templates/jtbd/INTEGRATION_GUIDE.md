# JTBD Templates Integration Guide

Complete guide for integrating Jobs-to-be-Done (JTBD) templates into your spec-kit workflow.

## Quick Start

### 1. Add JTBD Schema to Your Project

Create `ontology/jtbd-schema.ttl`:

```turtle
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .

# Core JTBD Classes
jtbd:Job a owl:Class ;
    rdfs:label "Job to be Done" ;
    rdfs:comment "A goal or task a customer is trying to accomplish" .

jtbd:Outcome a owl:Class ;
    rdfs:label "Desired Outcome" ;
    rdfs:comment "A measurable result a customer wants to achieve" .

jtbd:Persona a owl:Class ;
    rdfs:label "Customer Persona" ;
    rdfs:comment "A customer segment with specific jobs and needs" .

jtbd:Painpoint a owl:Class ;
    rdfs:label "Pain Point" ;
    rdfs:comment "A current frustration or obstacle" .

# Core JTBD Properties
jtbd:accomplishesJob a owl:ObjectProperty ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:Job .

jtbd:deliversOutcome a owl:ObjectProperty ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:Outcome .

jtbd:targetPersona a owl:ObjectProperty ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:Persona .

jtbd:resolvesPainpoint a owl:ObjectProperty ;
    rdfs:domain sk:Feature ;
    rdfs:range jtbd:Painpoint .

# Job Properties
jtbd:jobTitle a owl:DatatypeProperty ;
    rdfs:domain jtbd:Job ;
    rdfs:range rdfs:Literal .

jtbd:jobContext a owl:DatatypeProperty ;
    rdfs:domain jtbd:Job ;
    rdfs:range rdfs:Literal .

jtbd:jobFrequency a owl:DatatypeProperty ;
    rdfs:domain jtbd:Job ;
    rdfs:range rdfs:Literal .

jtbd:jobImportance a owl:DatatypeProperty ;
    rdfs:domain jtbd:Job ;
    rdfs:range rdfs:Literal .

# Outcome Properties
jtbd:outcomeDescription a owl:DatatypeProperty ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range rdfs:Literal .

jtbd:outcomeMetric a owl:DatatypeProperty ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range rdfs:Literal .

jtbd:successCriteria a owl:DatatypeProperty ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range rdfs:Literal .

jtbd:targetValue a owl:DatatypeProperty ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range rdfs:Literal .

jtbd:currentValue a owl:DatatypeProperty ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range rdfs:Literal .

# Persona Properties
jtbd:personaName a owl:DatatypeProperty ;
    rdfs:domain jtbd:Persona ;
    rdfs:range rdfs:Literal .

# Painpoint Properties
jtbd:painpointDescription a owl:DatatypeProperty ;
    rdfs:domain jtbd:Painpoint ;
    rdfs:range rdfs:Literal .
```

### 2. Create Feature Specifications with JTBD

Create `memory/features-jtbd.ttl` (see `example-feature-jtbd.ttl` for full example):

```turtle
@prefix : <http://github.com/your-org/your-project#> .
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .

:my-feature a sk:Feature ;
    sk:featureName "my-feature" ;
    sk:featureDescription "Feature description" ;
    jtbd:accomplishesJob :my-job ;
    jtbd:deliversOutcome :my-outcome ;
    jtbd:targetPersona :my-persona ;
    jtbd:resolvesPainpoint :my-painpoint ;
    jtbd:emotionalBenefit "Feel confident" ;
    sk:featureStatus "Planned" .

:my-job a jtbd:Job ;
    jtbd:jobTitle "Accomplish something important" ;
    jtbd:jobFrequency "High" ;
    jtbd:jobImportance "Critical" .

:my-outcome a jtbd:Outcome ;
    jtbd:outcomeDescription "Complete task 50% faster" ;
    jtbd:outcomeMetric "Task completion time" ;
    jtbd:successCriteria "Time to complete" ;
    jtbd:targetValue "< 5 seconds" .

:my-persona a jtbd:Persona ;
    jtbd:personaName "Product Manager" .

:my-painpoint a jtbd:Painpoint ;
    jtbd:painpointDescription "Manual process is tedious" .
```

### 3. Create SPARQL Queries

Copy from `example-sparql-queries.rq` to `sparql/jtbd-*.rq`:

```bash
# Extract relevant queries
cp templates/jtbd/example-sparql-queries.rq sparql/jtbd-feature-cards.rq
# Edit to extract just the feature card query
```

Or create custom queries for your needs.

### 4. Configure ggen Transformations

Add to `docs/ggen.toml`:

```toml
# Feature Outcome Cards
[[transformations.docs]]
name = "feature-outcome-cards"
description = "Generate outcome-driven feature cards"
input_files = ["memory/features-jtbd.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl", "ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-feature-cards.rq"
template = "templates/feature-outcome-card.tera"
output_file = "docs/features/outcome-cards.md"
deterministic = true

# JTBD User Stories
[[transformations.docs]]
name = "jtbd-user-stories"
description = "Generate JTBD-formatted user stories"
input_files = ["memory/user-stories-jtbd.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl", "ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-user-stories.rq"
template = "templates/jtbd-user-story.tera"
output_file = "docs/user-stories.md"
deterministic = true

# Outcome-Focused Documentation
[[transformations.docs]]
name = "outcome-docs"
description = "Generate job-focused feature documentation"
input_files = ["memory/features-jtbd.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl", "ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-feature-docs.rq"
template = "templates/outcome-focused-docs.tera"
output_file = "docs/features/README.md"
deterministic = true

# JTBD Metrics Dashboard
[[transformations.docs]]
name = "jtbd-dashboard"
description = "Generate outcome metrics dashboard"
input_files = ["memory/features-jtbd.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl", "ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-metrics.rq"
template = "templates/jtbd-metrics-dashboard.tera"
output_file = "docs/metrics/jtbd-dashboard.md"
deterministic = true

# JTBD Feature Roadmap
[[transformations.docs]]
name = "jtbd-roadmap"
description = "Generate JTBD-prioritized roadmap"
input_files = ["memory/roadmap-jtbd.ttl"]
schema_files = ["ontology/spec-kit-schema.ttl", "ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-roadmap.rq"
template = "templates/jtbd-roadmap.tera"
output_file = "docs/ROADMAP.md"
deterministic = true
```

### 5. Generate Documentation

```bash
# Generate all JTBD documentation
ggen sync --config docs/ggen.toml

# Or generate specific transformations
ggen sync --config docs/ggen.toml --transformation feature-outcome-cards
ggen sync --config docs/ggen.toml --transformation jtbd-roadmap
```

---

## Complete Workflow Example

### Scenario: Building a CLI Tool with JTBD Approach

#### Step 1: Customer Research

Interview customers to identify:
- What jobs they're trying to accomplish
- What outcomes they want
- What pain points they experience

Document findings in notes or spreadsheets.

#### Step 2: Translate to RDF

Create `memory/cli-features-jtbd.ttl`:

```turtle
@prefix : <http://github.com/my-org/my-cli#> .
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .

# Research Finding #1: Developers waste time on dependency management
:deps-add a sk:Feature ;
    sk:featureName "deps add" ;
    sk:featureDescription "Add project dependencies with validation" ;
    jtbd:accomplishesJob :manage-deps-job ;
    jtbd:deliversOutcome :faster-deps ;
    jtbd:targetPersona :cli-developer ;
    jtbd:resolvesPainpoint :manual-dep-mgmt ;
    jtbd:emotionalBenefit "Feel productive and avoid dependency hell" ;
    jtbd:usageExample "cli deps add lodash ^4.17.21" ;
    sk:featureStatus "Planned" .

:manage-deps-job a jtbd:Job ;
    jtbd:jobTitle "Manage project dependencies" ;
    jtbd:jobContext "When starting a new project or adding functionality" ;
    jtbd:jobFrequency "High" ;
    jtbd:jobImportance "Critical" .

:faster-deps a jtbd:Outcome ;
    jtbd:outcomeDescription "Add dependencies 3x faster" ;
    jtbd:outcomeMetric "Time from decision to added dependency" ;
    jtbd:successCriteria "Total time including validation" ;
    jtbd:targetValue "< 30 seconds" ;
    jtbd:priority "High" .

:cli-developer a jtbd:Persona ;
    jtbd:personaName "CLI Developer" ;
    jtbd:personaDescription "Software engineer building command-line tools" .

:manual-dep-mgmt a jtbd:Painpoint ;
    jtbd:painpointDescription "Manual dependency management causes errors and wastes time" ;
    jtbd:painpointFrequency "Daily" ;
    jtbd:painpointSeverity "High" .
```

#### Step 3: Generate Feature Card

```bash
ggen sync --config docs/ggen.toml --transformation feature-outcome-cards
```

Output in `docs/features/outcome-cards.md`:

```markdown
# deps add Feature

## Jobs & Outcomes

**CLI Developer Job**: Manage project dependencies

**Delivered Outcome**: Add dependencies 3x faster

**Success Metric**: Total time including validation < 30 seconds

**Pain Point Resolved**: Manual dependency management causes errors and wastes time

**Emotional Benefit**: Feel productive and avoid dependency hell
```

#### Step 4: Create Roadmap

Create `memory/roadmap-2025.ttl`:

```turtle
:q1-2025 a jtbd:Release ;
    jtbd:quarter "Q1 2025" ;
    jtbd:releaseName "Dependency Management MVP" ;
    jtbd:hasFeature :deps-add-roadmap .

:deps-add-roadmap a jtbd:PlannedFeature ;
    sk:featureName "deps add" ;
    jtbd:accomplishesJob :manage-deps-job ;
    jtbd:deliversOutcome :faster-deps ;
    jtbd:targetPersona :cli-developer ;
    jtbd:jobFrequency "High" ;
    jtbd:jobImportance "Critical" ;
    jtbd:estimatedEffort "Small" ;
    jtbd:riskLevel "Low" .
```

Generate roadmap:

```bash
ggen sync --config docs/ggen.toml --transformation jtbd-roadmap
```

#### Step 5: Track Outcomes

After release, measure actual performance:

```turtle
:faster-deps a jtbd:Outcome ;
    jtbd:outcomeDescription "Add dependencies 3x faster" ;
    jtbd:targetValue "< 30 seconds" ;
    jtbd:currentValue "22 seconds" .  # Actual measurement
```

Generate dashboard:

```bash
ggen sync --config docs/ggen.toml --transformation jtbd-dashboard
```

Review dashboard to see which features meet their outcome targets.

---

## Advanced Usage

### Multi-Persona Features

Some features serve multiple personas:

```turtle
:deps-visualize a sk:Feature ;
    jtbd:targetPersona :cli-developer, :tech-lead, :architect .
```

### Feature Dependencies

Link features that depend on each other:

```turtle
:advanced-feature a sk:Feature ;
    jtbd:dependencies "basic-feature|another-feature" .
```

### Outcome Tracking Over Time

Create snapshots:

```turtle
:outcome-2025-01 a jtbd:OutcomeMeasurement ;
    jtbd:measuredOutcome :faster-deps ;
    jtbd:currentValue "25 seconds" ;
    jtbd:measurementDate "2025-01-15"^^xsd:date .

:outcome-2025-02 a jtbd:OutcomeMeasurement ;
    jtbd:measuredOutcome :faster-deps ;
    jtbd:currentValue "22 seconds" ;
    jtbd:measurementDate "2025-02-15"^^xsd:date .
```

---

## Best Practices

### 1. Start with Customer Interviews

Don't guess at jobs and outcomes. Interview actual customers.

### 2. Focus on Outcomes, Not Features

Describe what customers want to achieve, not what buttons to press.

### 3. Measure Everything

Add `jtbd:currentValue` for all released features. Track over time.

### 4. Prioritize by Job Frequency × Importance

High-frequency, high-importance jobs first. Not "cool features."

### 5. Link Features to Jobs

Every feature must accomplish a job. If it doesn't, question why it exists.

### 6. Update RDF as You Learn

As you interview more customers, update job descriptions and priorities.

### 7. Review Dashboard Weekly

Use metrics dashboard to identify coverage gaps and underperforming features.

---

## Troubleshooting

### Query Returns No Results

**Problem**: SPARQL query doesn't match your RDF structure.

**Solution**: Verify your RDF uses the correct properties (`jtbd:accomplishesJob`, etc.). Check example files.

### Template Variables Are Empty

**Problem**: SPARQL query doesn't select the variables the template expects.

**Solution**: Compare SPARQL SELECT clause with template variable references. Add `OPTIONAL` clauses for optional fields.

### Generated Markdown Has Formatting Issues

**Problem**: Data contains special characters or newlines.

**Solution**: Sanitize data in RDF or add filters in template (e.g., `| escape`).

---

## Examples

All example files are in `templates/jtbd/`:

- `README.md` - This guide
- `example-feature-jtbd.ttl` - Feature with JTBD mapping
- `example-roadmap-jtbd.ttl` - Roadmap with job prioritization
- `example-sparql-queries.rq` - SPARQL queries for all templates
- `example-outputs.md` - Expected template outputs
- `INTEGRATION_GUIDE.md` - This file

---

## References

- [Jobs to be Done Framework](https://jtbd.info/)
- [Outcome-Driven Innovation](https://jobs-to-be-done.com/)
- [When Coffee and Kale Compete](https://www.amazon.com/When-Coffee-Kale-Compete-products/dp/1983204137) - Book on JTBD
- [Competing Against Luck](https://www.amazon.com/Competing-Against-Luck-Innovation-Customer/dp/0062435612) - Clayton Christensen on JTBD

---

*Last updated: 2025-12-21 | For questions, see [SUPPORT.md](../../SUPPORT.md)*
