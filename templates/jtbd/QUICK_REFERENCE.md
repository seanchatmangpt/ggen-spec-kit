# JTBD Templates Quick Reference

One-page reference for using JTBD-focused Tera templates in spec-kit.

---

## Template Cheat Sheet

| Template | Purpose | Input | Output | Lines |
|----------|---------|-------|--------|-------|
| `feature-outcome-card.tera` | Feature cards | Features + JTBD | Markdown card | 63 |
| `jtbd-user-story.tera` | User stories | Stories + jobs | JTBD stories | 74 |
| `outcome-focused-docs.tera` | Feature docs | Features + context | Job-focused docs | 105 |
| `jtbd-metrics-dashboard.tera` | Metrics | Features + outcomes | Analytics dashboard | 139 |
| `jtbd-roadmap.tera` | Roadmap | Planned features | Prioritized roadmap | 185 |

---

## Minimal RDF Example

```turtle
@prefix : <http://example.org#> .
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .

:my-feature a sk:Feature ;
    sk:featureName "my-feature" ;
    sk:featureDescription "What it does" ;
    jtbd:accomplishesJob :my-job ;
    jtbd:deliversOutcome :my-outcome ;
    jtbd:targetPersona :my-persona ;
    sk:featureStatus "Released" .

:my-job a jtbd:Job ;
    jtbd:jobTitle "Do something important" ;
    jtbd:jobFrequency "High" ;
    jtbd:jobImportance "Critical" .

:my-outcome a jtbd:Outcome ;
    jtbd:outcomeDescription "50% faster" ;
    jtbd:successCriteria "Time to complete" ;
    jtbd:targetValue "< 10s" .

:my-persona a jtbd:Persona ;
    jtbd:personaName "Developer" .
```

---

## Minimal SPARQL Query

```sparql
PREFIX sk: <http://github.com/github/spec-kit#>
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>

SELECT ?featureName ?jobTitle ?outcome ?personaName ?targetValue
WHERE {
  ?feature a sk:Feature ;
    sk:featureName ?featureName ;
    jtbd:accomplishesJob ?job ;
    jtbd:deliversOutcome ?outcomeNode ;
    jtbd:targetPersona ?persona .

  ?job jtbd:jobTitle ?jobTitle .
  ?outcomeNode jtbd:outcomeDescription ?outcome ;
    jtbd:targetValue ?targetValue .
  ?persona jtbd:personaName ?personaName .
}
```

---

## ggen.toml Configuration

```toml
[[transformations.docs]]
name = "feature-cards"
input_files = ["memory/features-jtbd.ttl"]
schema_files = ["ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-features.rq"
template = "templates/feature-outcome-card.tera"
output_file = "docs/features.md"
deterministic = true
```

---

## Command Line Usage

```bash
# Generate all JTBD docs
ggen sync --config docs/ggen.toml

# Generate specific transformation
ggen sync --config docs/ggen.toml --transformation feature-cards

# Validate RDF before generation
ggen validate --config docs/ggen.toml
```

---

## Required RDF Properties

### Feature
- `sk:featureName` - Feature name (required)
- `sk:featureDescription` - Description (required)
- `jtbd:accomplishesJob` - Link to job (required)
- `jtbd:deliversOutcome` - Link to outcome (required)
- `jtbd:targetPersona` - Link to persona (required)
- `sk:featureStatus` - Status (optional)

### Job
- `jtbd:jobTitle` - Job name (required)
- `jtbd:jobFrequency` - High/Medium/Low (optional)
- `jtbd:jobImportance` - Critical/High/Medium/Low (optional)

### Outcome
- `jtbd:outcomeDescription` - What improves (required)
- `jtbd:successCriteria` - How to measure (required)
- `jtbd:targetValue` - Performance target (required)
- `jtbd:currentValue` - Actual performance (optional)

### Persona
- `jtbd:personaName` - Persona name (required)

---

## Template Variable Reference

### feature-outcome-card.tera
```
featureName, featureDescription, jobTitle, personaName
outcome, outcomeMetric, successCriteria, targetValue
painpoint, emotionalBenefit, relatedFeatures
```

### jtbd-user-story.tera
```
storyId, personaName, jobContext, desiredOutcome
featureName, emotionalBenefit, painpoint
acceptanceCriteria, priority, estimatedValue
```

### outcome-focused-docs.tera
```
featureName, featureDescription, jobTitle, personaName
outcome, outcomeMetric, successCriteria, targetValue
painpoint, usageExample, relatedFeatures, prerequisites
```

### jtbd-metrics-dashboard.tera
```
outcome, outcomeDescription, featureName, personaName
successCriteria, targetValue, currentValue
featureStatus, priority
```

### jtbd-roadmap.tera
```
quarter, releaseName, featureName, jobTitle
jobFrequency, jobImportance, outcome, personaName
riskLevel, mitigation, dependencies, estimatedEffort
```

---

## Directory Structure

```
project/
├── ontology/
│   └── jtbd-schema.ttl          # JTBD ontology
├── memory/
│   ├── features-jtbd.ttl        # Feature specs
│   └── roadmap-jtbd.ttl         # Roadmap plans
├── sparql/
│   ├── jtbd-features.rq         # Feature queries
│   └── jtbd-roadmap.rq          # Roadmap queries
├── templates/
│   ├── feature-outcome-card.tera
│   ├── jtbd-user-story.tera
│   ├── outcome-focused-docs.tera
│   ├── jtbd-metrics-dashboard.tera
│   └── jtbd-roadmap.tera
└── docs/
    ├── ggen.toml                # Configuration
    ├── features.md              # Generated
    └── ROADMAP.md               # Generated
```

---

## Common Patterns

### Multiple Personas
```turtle
:feature jtbd:targetPersona :persona1, :persona2 .
```

### Related Features
```turtle
:feature jtbd:relatedFeatures "feature1|feature2|feature3" .
```

### Dependencies
```turtle
:feature jtbd:dependencies "prerequisite1|prerequisite2" .
```

### Acceptance Criteria
```turtle
:story jtbd:acceptanceCriteria "criterion1|criterion2|criterion3" .
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Empty output | Check SPARQL variable names match template |
| No results | Verify RDF properties (use `jtbd:` prefix) |
| Missing data | Add `OPTIONAL` clauses in SPARQL |
| Format issues | Escape special chars or use filters |

---

## Examples

Full examples in `templates/jtbd/`:
- `example-feature-jtbd.ttl` - Complete feature spec
- `example-roadmap-jtbd.ttl` - Roadmap with priorities
- `example-sparql-queries.rq` - All SPARQL queries
- `example-outputs.md` - Expected outputs

---

## Resources

- **README.md** - Template overview and usage
- **INTEGRATION_GUIDE.md** - Complete integration workflow
- **QUICK_REFERENCE.md** - This file

---

**Quick Start**: Copy `example-feature-jtbd.ttl`, modify for your feature, run `ggen sync`.

*Updated: 2025-12-21*
