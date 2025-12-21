# JTBD SPARQL Queries - Usage Guide

## Overview

This directory contains comprehensive SPARQL queries for extracting and analyzing Jobs-to-be-Done (JTBD) data from RDF specifications. These queries enable customer-centric feature planning, outcome-driven innovation, and data-driven roadmap prioritization.

## JTBD Ontology

The queries operate on the JTBD extension ontology defined in `/ontology/spec-kit-jtbd-extension.ttl`, which includes:

- **CustomerSegment**: Groups of customers with similar characteristics
- **Persona**: Archetypal users representing customer segments
- **Job**: High-level jobs customers are trying to get done
- **Outcome**: Measurable outcomes customers want to achieve
- **Painpoint**: Obstacles preventing outcome achievement
- **ProgressMaker**: Forces that help customers make progress
- **JobContext**: Situations when jobs arise

## Query Files

### 1. `jtbd-extract-jobs.rq` - Extract All Jobs and Outcomes

**Purpose**: Extract complete view of customer segments, jobs, outcomes, painpoints, and progress makers.

**Output Columns**:
- Segment and persona information
- Job details (name, frequency, importance, satisfaction)
- Outcome metrics (name, priority, target, opportunity score)
- Painpoints (description, severity)
- Progress makers (description, type)

**Use Cases**:
- Feature planning workshops
- Customer journey mapping
- Opportunity analysis (importance - satisfaction gaps)
- Export to CSV for spreadsheet analysis

**Example Usage**:
```bash
# Using Apache Jena ARQ
arq --data=memory/jtbd-spec.ttl \
    --data=ontology/spec-kit-jtbd-extension.ttl \
    --query=sparql/jtbd-extract-jobs.rq \
    --results=CSV > jobs-report.csv
```

**Key Metrics**:
- `jobOpportunity`: Gap between importance and current satisfaction
- `outcomeOpportunityScore`: Calculated opportunity score for prioritization

---

### 2. `jtbd-job-feature-mapping.rq` - Job-to-Feature Mapping

**Purpose**: Show which features address which jobs and deliver which outcomes. Identify gaps where jobs/outcomes lack features.

**Output Columns**:
- Job and outcome names
- Features addressing them
- Feature status (Draft, In Progress, Complete)
- Gap indicator (YES/NO)
- Feature count per outcome

**Use Cases**:
- Feature coverage analysis
- Roadmap gap identification
- Impact assessment (which features deliver most value)
- Justifying feature development

**Example Result**:
```
Job: "Manage dependencies"
Outcome: "Fast dependency resolution"
Feature: "deps-add" (Complete)
Gap: No

Job: "Configure OTEL"
Outcome: "Complete observability"
Feature: NULL
Gap: YES - NO FEATURE  ← Needs attention!
```

**How to Use**:
1. Run query to identify gaps
2. Filter for `hasGap = "YES - NO FEATURE"`
3. Prioritize creating features for high-importance outcomes
4. Track feature count per outcome (aim for 1-3 features per outcome)

---

### 3. `jtbd-painpoint-coverage.rq` - Painpoint Coverage Analysis

**Purpose**: For each painpoint, calculate how many features address it. Identify unaddressed painpoints by severity.

**Output Columns**:
- Painpoint description and severity
- Related job/outcome context
- Features solving the painpoint
- Feature count and coverage status
- Priority score (Critical=100, High=75, Medium=50, Low=25)

**Coverage Status**:
- `UNADDRESSED`: Zero features address this painpoint
- `Partial`: One feature addresses this painpoint
- `Covered`: Multiple features address this painpoint

**Use Cases**:
- Pain-driven development prioritization
- Critical painpoint resolution
- Customer satisfaction improvement
- Support ticket reduction planning

**Example Workflow**:
```bash
# 1. Extract painpoint coverage
arq --query=sparql/jtbd-painpoint-coverage.rq ... > painpoints.csv

# 2. Filter for UNADDRESSED + Critical/High severity
grep "UNADDRESSED.*Critical" painpoints.csv
grep "UNADDRESSED.*High" painpoints.csv

# 3. Create features to address top 3 unaddressed painpoints
```

---

### 4. `jtbd-outcome-metrics.rq` - Outcome Metrics Dashboard

**Purpose**: Extract all success criteria and outcome metrics. Identify measurement gaps where outcomes lack defined metrics.

**Output Columns**:
- Persona and job context
- Outcome name and description
- Metric definition (time, accuracy, count, percent, etc.)
- Target value (e.g., "< 5 minutes", "> 80%", "0 vulnerabilities")
- Definition status (Yes / NO - NEEDS METRIC)
- Gap severity (HIGH PRIORITY GAP / OK)

**Use Cases**:
- Success criteria definition
- OKR and KPI setting
- Metric dashboard creation
- Outcome measurement planning

**Example Output**:
```
Persona: Dev Lead
Job: Manage dependencies
Outcome: Fast resolution
Metric: time
Target: < 5 min
Has Definition: Yes
Gap Severity: OK

Persona: Backend Dev
Job: Configure OTEL
Outcome: Complete observability
Metric: NULL
Target: NULL
Has Definition: NO - NEEDS METRIC
Gap Severity: HIGH PRIORITY GAP  ← Define metric!
```

**Action Items from Query**:
1. Filter for `hasDefinition = "NO - NEEDS METRIC"`
2. Prioritize by `gapSeverity = "HIGH PRIORITY GAP"`
3. Define metrics for high-importance outcomes
4. Set concrete, measurable targets

---

### 5. `jtbd-feature-impact.rq` - Feature-to-Job Impact Analysis

**Purpose**: Calculate weighted impact score for each feature based on outcome priority, importance, and job count. Rank features by ROI.

**Output Columns**:
- Feature name and status
- Jobs addressed count
- Outcomes delivered count
- Average outcome priority
- Average outcome importance
- Impact score (calculated)
- Recommendation (High/Medium/Low ROI)

**Impact Score Formula**:
```
impactScore = (10 - avgPriority) × avgImportance × (1 + jobCount × 0.2)
```

**Recommendation Thresholds**:
- **High ROI - Ship Now**: Impact score ≥ 80
- **Medium ROI - Next Sprint**: Impact score ≥ 60
- **Low ROI - Backlog**: Impact score ≥ 40
- **Consider Deprioritizing**: Impact score < 40

**Use Cases**:
- Roadmap prioritization
- Resource allocation decisions
- Feature justification to stakeholders
- MVP scope definition

**Example Workflow**:
```bash
# 1. Extract feature impact analysis
arq --query=sparql/jtbd-feature-impact.rq ... > feature-impact.csv

# 2. Filter for high ROI features
grep "High ROI" feature-impact.csv | sort -t',' -k8 -rn

# 3. Build roadmap from top impact score features
```

---

### 6. `jtbd-persona-analysis.rq` - Persona Segmentation Report

**Purpose**: Analyze jobs and outcomes per persona. Identify overlapping needs across personas and unique persona-specific jobs. Calculate feature coverage percentage.

**Output Columns**:
- Persona name, role, goals, frustrations
- Total jobs, outcomes, painpoints, progress makers
- Features targeting this persona
- Outcome coverage percentage
- Coverage assessment (Excellent/Good/Needs Improvement/Poor)

**Coverage Assessment**:
- **Excellent**: ≥75% of outcomes have features
- **Good**: ≥50% of outcomes have features
- **Needs Improvement**: ≥25% of outcomes have features
- **Poor Coverage - Priority**: <25% of outcomes have features

**Use Cases**:
- Persona-driven roadmap planning
- Market segmentation analysis
- Multi-persona feature identification
- Underserved persona detection

**Example Output**:
```
Persona: Dev Lead
Jobs: 5
Outcomes: 12
Features: 8
Coverage: 67% → "Good Coverage"

Persona: Ops Engineer
Jobs: 4
Outcomes: 9
Features: 4
Coverage: 44% → "Needs Improvement"
```

**Action Items**:
1. Filter for `coverageAssessment = "Poor Coverage - Priority"`
2. Identify underserved personas
3. Create features targeting their top jobs/outcomes
4. Aim for balanced coverage across all personas

---

## Query Execution Methods

### Method 1: Apache Jena ARQ (Recommended)

```bash
# Install ARQ
# macOS: brew install jena
# Linux: apt-get install jena

# Execute query
arq --data=memory/jtbd-spec.ttl \
    --data=ontology/spec-kit-schema.ttl \
    --data=ontology/spec-kit-jtbd-extension.ttl \
    --query=sparql/jtbd-extract-jobs.rq \
    --results=CSV > output.csv
```

### Method 2: RDFLib (Python)

```python
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

# Load ontology and data
g = Graph()
g.parse("ontology/spec-kit-jtbd-extension.ttl", format="turtle")
g.parse("memory/jtbd-spec.ttl", format="turtle")

# Execute query
with open("sparql/jtbd-extract-jobs.rq") as f:
    query = prepareQuery(f.read())

results = g.query(query)
for row in results:
    print(row)
```

### Method 3: SPARQL Endpoint (Fuseki)

```bash
# Start Fuseki server
fuseki-server --loc=data /jtbd

# Upload data via Fuseki UI or curl
curl -X POST \
  -H "Content-Type: text/turtle" \
  --data-binary @memory/jtbd-spec.ttl \
  http://localhost:3030/jtbd/data

# Execute query
curl -X POST \
  -H "Accept: text/csv" \
  --data-urlencode query@sparql/jtbd-extract-jobs.rq \
  http://localhost:3030/jtbd/sparql > results.csv
```

---

## Creating JTBD Data

### Example RDF Specification

```turtle
@prefix sk: <http://github.com/github/spec-kit#> .

# Define persona
:DevLead a sk:Persona ;
  sk:personaName "Dev Lead Dana" ;
  sk:personaRole "Development Team Lead" ;
  sk:personaGoals "Ship features fast with high quality" .

# Define job
:ManageDependencies a sk:Job ;
  sk:jobName "Manage project dependencies" ;
  sk:jobFrequency "Daily" ;
  sk:jobImportance 9 ;
  sk:jobSatisfaction 4 .

:DevLead sk:hasJob :ManageDependencies .

# Define outcome
:FastResolution a sk:Outcome ;
  sk:outcomeName "Fast dependency resolution" ;
  sk:outcomeMetric "time" ;
  sk:outcomeTarget "< 5 minutes" ;
  sk:outcomePriority 1 ;
  sk:outcomeImportance 9 ;
  sk:outcomeSatisfaction 5 ;
  sk:outcomeOpportunityScore 13.0 .

:ManageDependencies sk:hasOutcome :FastResolution .

# Define painpoint
:SlowResolution a sk:Painpoint ;
  sk:painpointDescription "Dependency resolution takes 15+ minutes" ;
  sk:painpointSeverity "High" .

:FastResolution sk:hasPainpoint :SlowResolution .

# Link feature to job/outcome
:DepsAddFeature a sk:Feature ;
  sk:featureName "deps-add" ;
  sk:status "Complete" ;
  sk:addressesJob :ManageDependencies ;
  sk:deliversOutcome :FastResolution ;
  sk:solvesPainpoint :SlowResolution .
```

---

## Query Optimization Tips

1. **Use OPTIONAL carefully**: Too many OPTIONALs can slow queries
2. **Filter early**: Use FILTER clauses before complex joins
3. **Limit results**: Add LIMIT when testing queries
4. **Index properties**: Ensure important properties are indexed (Fuseki)
5. **Batch queries**: Run multiple queries in parallel for dashboards

---

## Integration with ggen

These queries are designed to work with ggen's transformation pipeline:

1. **Store JTBD data in Turtle files** (`memory/jtbd-*.ttl`)
2. **Extract insights with SPARQL queries** (these files)
3. **Transform results to Markdown** (ggen templates)
4. **Generate reports** (`docs/jtbd-analysis.md`)

Example ggen workflow:
```bash
# 1. Run SPARQL query
arq --query=sparql/jtbd-feature-impact.rq ... --results=JSON > /tmp/impact.json

# 2. Use ggen to transform to Markdown
ggen compile --input=/tmp/impact.json --template=templates/jtbd-report.md.tera
```

---

## Recommended Workflow

### 1. Initial Setup
- Create JTBD ontology instances in `memory/jtbd-*.ttl`
- Define personas, jobs, outcomes, painpoints

### 2. Ongoing Analysis
- **Weekly**: Run `jtbd-painpoint-coverage.rq` to track pain resolution
- **Sprint Planning**: Run `jtbd-feature-impact.rq` to prioritize features
- **Monthly**: Run `jtbd-persona-analysis.rq` to check persona balance
- **Quarterly**: Run `jtbd-extract-jobs.rq` for full opportunity analysis

### 3. Decision Making
- Use impact scores to rank features
- Use painpoint coverage to address critical issues
- Use outcome metrics to define success
- Use persona analysis to ensure balanced roadmap

---

## Further Reading

- [Jobs-to-be-Done Framework](https://jobs-to-be-done.com/)
- [Outcome-Driven Innovation](https://strategyn.com/outcome-driven-innovation/)
- [SPARQL Query Language](https://www.w3.org/TR/sparql11-query/)
- [RDF 1.1 Turtle](https://www.w3.org/TR/turtle/)

---

**Generated**: 2025-12-21
**Version**: 1.0.0
**License**: MIT
