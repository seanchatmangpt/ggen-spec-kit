# JTBD (Jobs To Be Done) - Complete Index

## Overview

The spec-kit JTBD framework integrates Clayton Christensen's Jobs To Be Done methodology with RDF-first specification development, enabling customer-centric feature design validated through semantic constraints.

**Total JTBD Assets:** 30+ files across ontology, examples, documentation, SPARQL queries, templates, and Python implementation.

---

## Core Ontology

### Primary Schema
- **Location:** `/Users/sac/ggen-spec-kit/ontology/jtbd-schema.ttl`
- **Size:** 1,064 lines (40KB)
- **Content:**
  - 25 classes (Job, Outcome, Customer, Force, Solution)
  - 78 properties (52 datatype + 26 object)
  - 12 comprehensive SHACL validation shapes
  - Integration with spec-kit Feature class

### Extension Schema
- **Location:** `/Users/sac/ggen-spec-kit/ontology/spec-kit-jtbd-extension.ttl`
- **Purpose:** Additional spec-kit integration properties

---

## Documentation (5 files, ~100KB total)

### 1. Ontology Guide (Primary Reference)
**File:** `/Users/sac/ggen-spec-kit/docs/jtbd-ontology-guide.md` (14KB)

**Contents:**
- Core concepts (Jobs, Outcomes, Forces, Painpoints)
- Job statement structure
- Outcome measurement framework
- Customer segmentation
- Forces of Progress model
- Integration with spec-kit
- SHACL validation
- Best practices and anti-patterns

**Audience:** Developers creating JTBD specifications

### 2. Quick Reference Card
**File:** `/Users/sac/ggen-spec-kit/docs/jtbd-quick-reference.md` (6.5KB)

**Contents:**
- One-page cheat sheet
- Job statement template
- Outcome statement template
- Opportunity scoring formula
- Minimal JTBD specification example
- Common mistakes checklist
- Property value reference

**Audience:** Quick lookups during JTBD authoring

### 3. RDF Integration Guide
**File:** `/Users/sac/ggen-spec-kit/docs/jtbd-rdf-integration.md` (65KB)

**Contents:**
- Deep RDF integration patterns
- SPARQL query examples
- Tera template integration
- ggen transformation workflows
- Advanced use cases

**Audience:** Advanced users doing RDF transformations

### 4. Measurement Guide
**File:** `/Users/sac/ggen-spec-kit/docs/jtbd-measurement-guide.md` (21KB)

**Contents:**
- Opportunity scoring methodology
- Importance/satisfaction surveys
- Outcome prioritization
- Success metric design
- Customer research techniques

**Audience:** Product managers and researchers

### 5. Framework Overview
**File:** `/Users/sac/ggen-spec-kit/docs/guides/jtbd-framework.md`

**Contents:**
- High-level JTBD theory
- Christensen, Ulwick, Moesta approaches
- When to use JTBD
- Integration with product development

**Audience:** Teams new to JTBD

---

## Examples (3 RDF files)

### 1. Comprehensive Example: GitHub Code Review
**File:** `/Users/sac/ggen-spec-kit/docs/examples/jtbd-example-feature.ttl` (17KB, 330 lines)

**Demonstrates:**
- Functional, emotional, and social jobs
- 4 desired outcomes with opportunity scores
- Success metrics (time, quality, coverage)
- Customer segment with persona
- 3 painpoints with severity
- All 4 forces (push/pull/habit/anxiety)
- Current and proposed solutions
- Integration with sk:Feature

**Use Case:** GitHub AI-powered code review assistant

### 2. Customer Jobs Collection
**File:** `/Users/sac/ggen-spec-kit/memory/jtbd-customer-jobs.ttl`

**Contents:** Library of common customer jobs across domains

### 3. Forces Analysis Template
**File:** `/Users/sac/ggen-spec-kit/memory/jtbd-forces-analysis.ttl`

**Contents:** Template for Forces of Progress analysis

---

## SPARQL Queries (6 files)

### 1. Extract Jobs
**File:** `/Users/sac/ggen-spec-kit/sparql/jtbd-extract-jobs.rq`
**Purpose:** Query all jobs with their outcomes and painpoints

### 2. Feature Impact Analysis
**File:** `/Users/sac/ggen-spec-kit/sparql/jtbd-feature-impact.rq`
**Purpose:** Analyze which features address which jobs

### 3. Job-Feature Mapping
**File:** `/Users/sac/ggen-spec-kit/sparql/jtbd-job-feature-mapping.rq`
**Purpose:** Map jobs to features and outcomes

### 4. Outcome Metrics
**File:** `/Users/sac/ggen-spec-kit/sparql/jtbd-outcome-metrics.rq`
**Purpose:** Extract outcome priorities and opportunity scores

### 5. Painpoint Coverage
**File:** `/Users/sac/ggen-spec-kit/sparql/jtbd-painpoint-coverage.rq`
**Purpose:** Analyze painpoint coverage across features

### 6. Persona Analysis
**File:** `/Users/sac/ggen-spec-kit/sparql/jtbd-persona-analysis.rq`
**Purpose:** Extract persona insights and segments

---

## Tera Templates (3 files)

### 1. Metrics Dashboard
**File:** `/Users/sac/ggen-spec-kit/templates/jtbd-metrics-dashboard.tera`
**Purpose:** Generate opportunity score dashboard from RDF

### 2. Product Roadmap
**File:** `/Users/sac/ggen-spec-kit/templates/jtbd-roadmap.tera`
**Purpose:** Generate JTBD-driven roadmap from features

### 3. User Story Generator
**File:** `/Users/sac/ggen-spec-kit/templates/jtbd-user-story.tera`
**Purpose:** Convert JTBD to user stories for agile teams

---

## Python Implementation (2 modules)

### 1. JTBD Measurement Module
**File:** `/Users/sac/ggen-spec-kit/src/specify_cli/core/jtbd_measurement.py`
**Test:** `/Users/sac/ggen-spec-kit/tests/unit/test_jtbd_measurement.py`

**Functions:**
- `calculate_opportunity_score(importance, satisfaction)` - ODI formula
- `classify_opportunity(score)` - Overserved/Underserved classification
- `prioritize_outcomes(outcome_list)` - Sort by opportunity

### 2. JTBD Metrics Module
**File:** `/Users/sac/ggen-spec-kit/src/specify_cli/core/jtbd_metrics.py`
**Test:** `/Users/sac/ggen-spec-kit/tests/unit/test_jtbd_metrics.py`

**Functions:**
- `extract_job_metrics(rdf_graph)` - Parse JTBD RDF
- `generate_opportunity_matrix(jobs)` - Create visualization
- `analyze_forces(job_uri)` - Forces diagram data

---

## Template Examples (2 files)

### 1. Example Feature JTBD
**File:** `/Users/sac/ggen-spec-kit/templates/jtbd/example-feature-jtbd.ttl`
**Purpose:** Blank template for new features

### 2. Example Roadmap JTBD
**File:** `/Users/sac/ggen-spec-kit/templates/jtbd/example-roadmap-jtbd.ttl`
**Purpose:** Template for roadmap planning

---

## Test Coverage (4 files)

### Unit Tests
1. **test_jtbd_measurement.py** - Opportunity scoring tests
2. **test_jtbd_metrics.py** - RDF parsing and metrics tests
3. **test_jtbd_import_validation.py** - SHACL validation tests
4. **test_jtbd_permutations.py** - Edge case coverage

**Coverage:** See `/Users/sac/ggen-spec-kit/reports/coverage/`

---

## Quick Start Guide

### 1. Create New JTBD Specification

```bash
# Copy example template
cp docs/examples/jtbd-example-feature.ttl memory/jtbd/my-feature.ttl

# Edit in your preferred editor
vim memory/jtbd/my-feature.ttl

# Validate SHACL constraints
ggen validate --config docs/ggen.toml memory/jtbd/my-feature.ttl
```

### 2. Calculate Opportunity Scores

```python
from specify_cli.core.jtbd_measurement import calculate_opportunity_score, classify_opportunity

# Survey results
importance = 9.2
satisfaction = 4.1

# Calculate
score = calculate_opportunity_score(importance, satisfaction)
classification = classify_opportunity(score)

print(f"Opportunity: {score} ({classification})")
# Output: Opportunity: 14.3 (Underserved)
```

### 3. Generate Documentation

```bash
# Run ggen transformation
ggen sync --config docs/ggen.toml

# Generates:
# - docs/jtbd-metrics-dashboard.md
# - docs/jtbd-roadmap.md
# - docs/jtbd-user-stories.md
```

### 4. Query JTBD Data

```bash
# Extract all jobs with high opportunity scores
sparql --data=memory/jtbd/*.ttl --query=sparql/jtbd-outcome-metrics.rq

# Analyze feature-job mapping
sparql --data=memory/jtbd/*.ttl --query=sparql/jtbd-feature-impact.rq
```

---

## JTBD Workflow

```
1. Research Phase
   ├─ Conduct customer interviews
   ├─ Identify jobs (functional, emotional, social)
   ├─ Extract desired outcomes (8-12 per job)
   └─ Document painpoints and forces

2. Measurement Phase
   ├─ Survey customers (importance/satisfaction)
   ├─ Calculate opportunity scores
   ├─ Prioritize outcomes (focus on score > 10)
   └─ Validate with segment data

3. Specification Phase
   ├─ Create jtbd:Job RDF instances
   ├─ Define jtbd:DesiredOutcome with scores
   ├─ Map jtbd:Painpoint to sk:Feature
   └─ Validate with SHACL shapes

4. Design Phase
   ├─ Create sk:Feature addressing underserved outcomes
   ├─ Link feature to customer segments
   ├─ Design solutions overcoming anxieties
   └─ Generate user stories from templates

5. Validation Phase
   ├─ Run ggen validate
   ├─ Generate metrics dashboard
   ├─ Review opportunity matrix
   └─ Iterate based on feedback
```

---

## Key Formulas

### Opportunity Score (Ulwick ODI)
```
Opportunity = Importance + (Importance - Satisfaction)

Where:
  Importance: 1-10 (how important outcome is)
  Satisfaction: 1-10 (how satisfied with current solutions)

Interpretation:
  < 5: Overserved (don't over-engineer)
  5-10: Appropriately served (maintain)
  10-15: Underserved (HIGH OPPORTUNITY)
  > 15: Severely underserved (CRITICAL)
```

### Job Statement
```
When [context/situation],
I want to [achieve outcome],
so I can [emotional/social benefit].
```

### Outcome Statement
```
Minimize/Maximize [metric] [object] [clarifier]

Examples:
- Minimize time to identify bugs in pull requests
- Maximize confidence that code is reviewed before approval
```

---

## Integration with Spec-Kit

```turtle
# JTBD informs Feature
:CodeQualityJob jtbd:informsFeature :AIReviewFeature .

# Feature targets Segment
:AIReviewFeature jtbd:targetsSegment :SeniorEngineerSegment .

# Feature addresses Painpoint
:AIReviewFeature jtbd:addressesPainpoint :SlowReviewProcess .

# Feature enables Outcome
:AIReviewFeature jtbd:enablesOutcome :MinimizeTimeToFindIssues .

# Feature has User Story (spec-kit)
:AIReviewFeature sk:hasUserStory :AutomatedSecurityScan .
```

---

## Resources

### Learning JTBD Theory
- **Clayton Christensen:** "Competing Against Luck" (original theory)
- **Tony Ulwick:** "Jobs to be Done: Theory to Practice" (ODI methodology)
- **Bob Moesta:** "Demand-Side Sales 101" (Forces of Progress)
- **Alan Klement:** "When Coffee and Kale Compete" (product development)

### RDF/SPARQL Resources
- **W3C RDF Primer:** https://www.w3.org/TR/rdf11-primer/
- **SHACL Spec:** https://www.w3.org/TR/shacl/
- **SPARQL Tutorial:** https://www.w3.org/TR/sparql11-query/

### Spec-Kit Resources
- **Philosophy:** `memory/philosophy.ttl`
- **Spec-Kit Schema:** `ontology/spec-kit-schema.ttl`
- **ggen Documentation:** https://github.com/gritGmbH/ggen

---

## File Structure Summary

```
ggen-spec-kit/
├── ontology/
│   ├── jtbd-schema.ttl (1,064 lines, PRIMARY SCHEMA)
│   └── spec-kit-jtbd-extension.ttl
├── docs/
│   ├── JTBD-INDEX.md (this file)
│   ├── jtbd-ontology-guide.md (14KB, MAIN GUIDE)
│   ├── jtbd-quick-reference.md (6.5KB, CHEAT SHEET)
│   ├── jtbd-rdf-integration.md (65KB)
│   ├── jtbd-measurement-guide.md (21KB)
│   ├── guides/jtbd-framework.md
│   └── examples/
│       └── jtbd-example-feature.ttl (330 lines, GITHUB EXAMPLE)
├── memory/
│   ├── jtbd-customer-jobs.ttl
│   ├── jtbd-example.ttl
│   └── jtbd-forces-analysis.ttl
├── sparql/
│   ├── jtbd-extract-jobs.rq
│   ├── jtbd-feature-impact.rq
│   ├── jtbd-job-feature-mapping.rq
│   ├── jtbd-outcome-metrics.rq
│   ├── jtbd-painpoint-coverage.rq
│   └── jtbd-persona-analysis.rq
├── templates/
│   ├── jtbd-metrics-dashboard.tera
│   ├── jtbd-roadmap.tera
│   ├── jtbd-user-story.tera
│   └── jtbd/
│       ├── example-feature-jtbd.ttl
│       └── example-roadmap-jtbd.ttl
├── src/specify_cli/core/
│   ├── jtbd_measurement.py
│   └── jtbd_metrics.py
└── tests/unit/
    ├── test_jtbd_measurement.py
    └── test_jtbd_metrics.py
```

**Total Files:** 30+ across 7 categories
**Total Lines:** ~2,500 lines of RDF + docs
**Total Size:** ~150KB

---

## Common Tasks

### Create JTBD for New Feature
```bash
# 1. Start with template
cp templates/jtbd/example-feature-jtbd.ttl memory/jtbd/my-feature.ttl

# 2. Fill in job details
vim memory/jtbd/my-feature.ttl

# 3. Validate
ggen validate --config docs/ggen.toml memory/jtbd/my-feature.ttl

# 4. Generate docs
ggen sync --config docs/ggen.toml
```

### Calculate Opportunity Scores
```bash
# Use Python module
python -c "
from specify_cli.core.jtbd_measurement import calculate_opportunity_score
print(calculate_opportunity_score(9.2, 4.1))  # 14.3
"
```

### Query High-Opportunity Outcomes
```bash
# Use SPARQL
sparql --data=memory/jtbd/*.ttl \
       --query=sparql/jtbd-outcome-metrics.rq \
       --results=CSV > high-opportunity.csv
```

### Generate Roadmap from JTBD
```bash
# Use Tera template
ggen sync --config docs/ggen.toml \
          --template templates/jtbd-roadmap.tera \
          --output docs/product-roadmap.md
```

---

## Next Steps

1. **Read:** Start with `docs/jtbd-quick-reference.md` for overview
2. **Study:** Review `docs/examples/jtbd-example-feature.ttl` for complete example
3. **Learn:** Deep dive into `docs/jtbd-ontology-guide.md` for concepts
4. **Practice:** Create your first JTBD spec using templates
5. **Validate:** Run `ggen validate` to ensure correctness
6. **Generate:** Use SPARQL + Tera to create documentation

---

## Support & Contribution

- **Issues:** Open GitHub issue with `[JTBD]` prefix
- **Questions:** Tag `@jtbd-experts` in discussions
- **Examples:** Add new examples to `docs/examples/`
- **SPARQL Queries:** Contribute to `sparql/` directory
- **Templates:** Share Tera templates in `templates/`

---

**Last Updated:** 2025-12-21
**Ontology Version:** 1.0.0
**Spec-Kit Version:** 0.0.22+
