# Getting Started with JTBD in Spec-Kit

## Overview

This tutorial teaches you how to apply the Jobs To Be Done (JTBD) framework to spec-kit development. You'll learn to identify customer jobs, define desired outcomes, map features to outcomes, and measure success.

**What you'll learn:**
1. Define a customer job in RDF
2. List desired outcomes for that job
3. Map features to outcomes
4. Generate feature specifications
5. Measure outcome delivery with OTEL

**Time:** 30-45 minutes

**Prerequisites:**
- Basic understanding of RDF/Turtle syntax
- Familiarity with spec-kit CLI commands
- Python knowledge (for OTEL instrumentation)

---

## Table of Contents

1. [Step 1: Define Customer Job in RDF](#step-1-define-customer-job-in-rdf)
2. [Step 2: List Desired Outcomes](#step-2-list-desired-outcomes)
3. [Step 3: Map Features to Outcomes](#step-3-map-features-to-outcomes)
4. [Step 4: Generate Feature Specifications](#step-4-generate-feature-specifications)
5. [Step 5: Measure Outcome Delivery](#step-5-measure-outcome-delivery)
6. [Complete Example: End-to-End](#complete-example-end-to-end)
7. [Next Steps](#next-steps)

---

## Step 1: Define Customer Job in RDF

### The Job Statement

A job statement answers: **What progress is the customer trying to make?**

**Format:**
```
[Action verb] [Object] so I can [expected outcome] when [circumstance]
```

### Example Job

Let's define a job for the RDF Ontology Designer persona:

**Job Statement:**
> "Validate RDF ontology syntax and semantics so I can catch errors before committing to git when I've made changes to ontology files."

### RDF Encoding

Create a new file: `ontology/jtbd-jobs.ttl`

```turtle
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Define the job
jtbd:ValidateOntologyJob a jtbd:Job ;
    rdfs:label "Validate RDF Ontology Syntax and Semantics"@en ;
    jtbd:jobStatement "Validate RDF ontology syntax and semantics so I can catch errors before committing to git when I've made changes to ontology files."@en ;

    # Persona
    jtbd:persona jtbd:RDFOntologyDesigner ;

    # Circumstance
    jtbd:circumstance "Before committing ontology changes to version control"@en ;

    # Job dimensions
    jtbd:functionalJob "Ensure ontology files are valid RDF/Turtle and conform to SHACL shapes"@en ;
    jtbd:emotionalJob "Feel confident that ontology is correct before sharing with team"@en ;
    jtbd:socialJob "Be seen as thorough and rigorous in ontology design"@en ;

    # Importance
    jtbd:importance "high"^^xsd:string ;

    # When this job occurs
    jtbd:frequency "daily"^^xsd:string ;
    jtbd:urgency "high"^^xsd:string .
```

### Validate the Job Definition

Check that your job has:
- ✅ Clear job statement
- ✅ Identified persona
- ✅ Specific circumstance
- ✅ All three job dimensions (functional, emotional, social)
- ✅ Importance level
- ✅ Frequency and urgency

---

## Step 2: List Desired Outcomes

### Outcome Statement

An outcome answers: **How does the customer measure success?**

**Format:**
```
[Direction: Minimize/Maximize] [Metric] [Object of control] when [context]
```

### Example Outcomes

For the "Validate Ontology" job, list all outcomes the customer wants:

```turtle
# Outcome 1: Speed
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    rdfs:label "Minimize time to validate ontology"@en ;
    jtbd:outcomeStatement "Minimize the time it takes to validate all ontology files for syntax and semantic errors"@en ;

    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "time"^^xsd:string ;
    jtbd:metricUnit "seconds"^^xsd:string ;
    jtbd:objectOfControl "validation of all ontology files for syntax and semantic errors"@en ;

    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "medium"^^xsd:string ;  # Users moderately satisfied (3/5)

    # Measurement
    jtbd:baseline "300"^^xsd:integer ;  # 5 minutes (300 sec) manually
    jtbd:target "1"^^xsd:integer ;      # 1 second ideal
    jtbd:current "10"^^xsd:integer .    # 10 seconds currently

# Outcome 2: Error Detection
jtbd:MaximizeErrorDetection a jtbd:Outcome ;
    rdfs:label "Maximize error detection rate"@en ;
    jtbd:outcomeStatement "Maximize the likelihood of detecting syntax and semantic errors before they cause problems"@en ;

    jtbd:direction "maximize"^^xsd:string ;
    jtbd:metric "detection_rate"^^xsd:string ;
    jtbd:metricUnit "percent"^^xsd:string ;
    jtbd:objectOfControl "syntax and semantic errors in ontology"@en ;

    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string ;  # Users not satisfied (2/5)

    jtbd:baseline "50"^^xsd:integer ;   # 50% of errors caught manually
    jtbd:target "95"^^xsd:integer ;     # 95% ideal
    jtbd:current "70"^^xsd:integer .    # 70% currently

# Outcome 3: Effort
jtbd:MinimizeValidationSteps a jtbd:Outcome ;
    rdfs:label "Minimize validation steps"@en ;
    jtbd:outcomeStatement "Minimize the number of steps required to run a complete validation"@en ;

    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "steps"^^xsd:string ;
    jtbd:metricUnit "count"^^xsd:string ;
    jtbd:objectOfControl "required to run complete validation"@en ;

    jtbd:importance "medium"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string ;

    jtbd:baseline "5"^^xsd:integer ;    # 5 manual steps
    jtbd:target "1"^^xsd:integer ;      # 1 command ideal
    jtbd:current "1"^^xsd:integer .     # 1 command currently (good!)

# Link outcomes to job
jtbd:ValidateOntologyJob
    jtbd:hasOutcome jtbd:MinimizeValidationTime ;
    jtbd:hasOutcome jtbd:MaximizeErrorDetection ;
    jtbd:hasOutcome jtbd:MinimizeValidationSteps .
```

### Prioritize Outcomes

Use the **Importance-Satisfaction Gap** to prioritize:

| Outcome | Importance | Satisfaction | Gap | Priority |
|---------|------------|--------------|-----|----------|
| Maximize error detection | High | Low (2/5) | ⭐⭐⭐ | Critical |
| Minimize validation time | High | Medium (3/5) | ⭐⭐ | Important |
| Minimize validation steps | Medium | Low (2/5) | ⭐⭐ | Important |

**Focus first on:** Maximize error detection (high importance, low satisfaction)

---

## Step 3: Map Features to Outcomes

### Identify Features That Deliver Outcomes

For each outcome, list features that help achieve it:

```turtle
@prefix cli: <http://github.com/github/spec-kit/cli#> .

# Feature 1: specify check command
cli:CheckCommand a cli:Command ;
    rdfs:label "check"@en ;
    rdfs:comment "Check for required and optional tools"@en ;

    # Link to job
    jtbd:accomplishesJob jtbd:ValidateOntologyJob ;

    # Link to outcomes delivered
    jtbd:delivers jtbd:MinimizeValidationTime ;
    jtbd:delivers jtbd:MaximizeErrorDetection ;
    jtbd:delivers jtbd:MinimizeValidationSteps .

# Feature 2: RDF syntax validator (part of check)
cli:CheckRDFSyntax a cli:Validator ;
    rdfs:label "RDF Syntax Validator"@en ;
    rdfs:comment "Validates Turtle syntax in ontology files"@en ;

    jtbd:delivers jtbd:MinimizeValidationTime ;
    jtbd:delivers jtbd:MaximizeErrorDetection ;

    # Contribution to outcome
    jtbd:outcomeContribution [
        jtbd:outcome jtbd:MinimizeValidationTime ;
        jtbd:contributionLevel "high"^^xsd:string ;  # Significantly speeds up validation
        jtbd:currentPerformance "10"^^xsd:integer ;  # 10 seconds
        jtbd:targetPerformance "1"^^xsd:integer      # 1 second
    ] .

# Feature 3: SHACL validator (part of check)
cli:CheckSHACL a cli:Validator ;
    rdfs:label "SHACL Constraint Validator"@en ;
    rdfs:comment "Validates ontology against SHACL shape constraints"@en ;

    jtbd:delivers jtbd:MaximizeErrorDetection ;

    jtbd:outcomeContribution [
        jtbd:outcome jtbd:MaximizeErrorDetection ;
        jtbd:contributionLevel "high"^^xsd:string ;
        jtbd:currentPerformance "70"^^xsd:integer ;  # 70% detection rate
        jtbd:targetPerformance "95"^^xsd:integer     # 95% target
    ] .
```

### Outcome Gap Analysis

Calculate how well features deliver outcomes:

```sparql
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>

SELECT ?outcome ?current ?target ?gap ?satisfaction
WHERE {
  ?outcome a jtbd:Outcome ;
           jtbd:current ?current ;
           jtbd:target ?target ;
           jtbd:currentSatisfaction ?satisfaction .

  BIND(?target - ?current AS ?gap)
}
ORDER BY DESC(?gap)
```

**Results:**

| Outcome | Current | Target | Gap | Satisfaction |
|---------|---------|--------|-----|--------------|
| MaximizeErrorDetection | 70% | 95% | 25% | low |
| MinimizeValidationTime | 10s | 1s | 9s | medium |
| MinimizeValidationSteps | 1 | 1 | 0 | low (misleading!) |

**Insight:** Error detection has biggest gap, needs improvement!

---

## Step 4: Generate Feature Specifications

### Use RDF to Generate Specs

Now that we've defined jobs and outcomes in RDF, we can generate feature specs automatically.

**Create SPARQL query:** `sparql/feature-spec.rq`

```sparql
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>
PREFIX cli: <http://github.com/github/spec-kit/cli#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?feature ?job ?outcome ?importance ?satisfaction
WHERE {
  ?feature jtbd:accomplishesJob ?job ;
           jtbd:delivers ?outcome .

  ?outcome jtbd:importance ?importance ;
           jtbd:currentSatisfaction ?satisfaction .

  ?job rdfs:label ?jobLabel .
}
```

**Create Tera template:** `templates/feature-spec.md.tera`

```markdown
# Feature Specification: {{ feature.label }}

## Jobs To Be Done

{{ feature.description }}

**Accomplishes Job:**
{% for job in feature.jobs %}
- **{{ job.label }}**
  - Persona: {{ job.persona }}
  - Circumstance: {{ job.circumstance }}
  - Functional: {{ job.functionalJob }}
  - Emotional: {{ job.emotionalJob }}
  - Social: {{ job.socialJob }}
{% endfor %}

## Outcomes Delivered

{% for outcome in feature.outcomes %}
### {{ outcome.label }}

**Statement:** {{ outcome.outcomeStatement }}

**Measurement:**
- Direction: {{ outcome.direction }}
- Metric: {{ outcome.metric }}
- Baseline: {{ outcome.baseline }} {{ outcome.metricUnit }}
- Current: {{ outcome.current }} {{ outcome.metricUnit }}
- Target: {{ outcome.target }} {{ outcome.metricUnit }}

**Success:**
{% if outcome.direction == "minimize" %}
- Improvement: {{ outcome.baseline - outcome.current }} {{ outcome.metricUnit }} ({{ ((outcome.baseline - outcome.current) / outcome.baseline * 100) | round }}% faster)
- Progress to target: {{ ((outcome.baseline - outcome.current) / (outcome.baseline - outcome.target) * 100) | round }}%
{% else %}
- Improvement: {{ outcome.current - outcome.baseline }} {{ outcome.metricUnit }}
- Progress to target: {{ ((outcome.current - outcome.baseline) / (outcome.target - outcome.baseline) * 100) | round }}%
{% endif %}

**Priority:**
- Importance: {{ outcome.importance }}
- Satisfaction: {{ outcome.currentSatisfaction }}
- Gap: {% if outcome.importance == "high" and outcome.currentSatisfaction == "low" %}⭐⭐⭐ Critical{% elif outcome.importance == "high" %}⭐⭐ Important{% else %}⭐ Medium{% endif %}

{% endfor %}

## Implementation Requirements

To deliver the above outcomes, this feature must:

1. **For speed outcomes:**
   - Execute in < {{ target_time }}s
   - Provide progress feedback for long operations
   - Support parallel execution where possible

2. **For accuracy outcomes:**
   - Achieve {{ target_accuracy }}% detection rate
   - Minimize false positives (< 5%)
   - Provide clear, actionable error messages

3. **For effort outcomes:**
   - Single command execution
   - Sensible defaults (no required flags)
   - Integration with development workflow

## Success Metrics

Track these OTEL metrics:

```python
@timed
@span(
    "{{ feature.spanName }}",
    job="{{ job.id }}",
    outcome="{{ outcome.id }}",
    baseline={{ outcome.baseline }},
    target={{ outcome.target }}
)
def execute_feature():
    pass
```

**Target Metrics:**
{% for outcome in feature.outcomes %}
- {{ outcome.label }}: {{ outcome.target }} {{ outcome.metricUnit }}
{% endfor %}
```

**Generate specification:**

```bash
ggen sync --config docs/ggen.toml
```

This produces: `docs/features/check-command-spec.md` with complete JTBD justification!

---

## Step 5: Measure Outcome Delivery

### Instrument Feature with OTEL

Now implement the feature with measurement built-in:

```python
# src/specify_cli/commands/check.py
from specify_cli.core.telemetry import span, timed
from specify_cli.core.semconv import (
    ATTR_JOB_TYPE,
    ATTR_OUTCOME,
    ATTR_BASELINE,
    ATTR_TARGET
)

@app.command()
@timed
@span(
    "command.check",
    attributes={
        ATTR_JOB_TYPE: "validate_rdf_ontology",
        ATTR_OUTCOME: "minimize_validation_time",
        ATTR_BASELINE: 300_000,  # 5 min in ms
        ATTR_TARGET: 1_000       # 1 sec in ms
    }
)
def check(
    verbose: bool = False,
    json: bool = False,
    include_optional: bool = True
):
    """
    Check for required and optional tools.

    Jobs Accomplished:
    - Validate RDF Ontology (for RDF Ontology Designer persona)

    Outcomes Delivered:
    - Minimize time to validate: 10s (target: 1s)
    - Maximize error detection: 70% (target: 95%)
    - Minimize steps required: 1 (target: 1) ✓
    """
    with span("check.rdf_validation") as rdf_span:
        # Validate RDF syntax
        errors = validate_rdf_syntax(find_ontology_files())

        rdf_span.set_attribute("errors_detected", len(errors))
        rdf_span.set_attribute("outcome", "maximize_error_detection")

    with span("check.shacl_validation") as shacl_span:
        # Validate SHACL constraints
        violations = validate_shacl_constraints(find_ontology_files())

        shacl_span.set_attribute("violations_detected", len(violations))
        shacl_span.set_attribute("outcome", "maximize_error_detection")

    # Report results
    report_validation_results(errors, violations, json=json)
```

### Collect and Analyze Metrics

After users start using the feature, query OTEL data:

```sql
-- Average validation time (past 7 days)
SELECT
    AVG(duration_ms) as current_avg,
    PERCENTILE(duration_ms, 50) as p50,
    PERCENTILE(duration_ms, 95) as p95,
    300000 as baseline,
    1000 as target
FROM spans
WHERE span_name = 'command.check'
  AND attributes->>'job_type' = 'validate_rdf_ontology'
  AND timestamp > NOW() - INTERVAL 7 DAYS
```

**Results:**
- Current avg: 10,000ms (10 seconds)
- p50: 8,500ms
- p95: 15,000ms
- Baseline: 300,000ms (5 min)
- Target: 1,000ms (1 sec)

**Success Calculation:**
```
Improvement = (300000 - 10000) / 300000 = 97% faster than baseline
Progress to target = (300000 - 10000) / (300000 - 1000) = 97% of way to ideal
```

**Outcome:** Excellent speed improvement! 🎉

### Measure Error Detection Rate

```sql
-- Error detection rate
SELECT
    AVG(errors_detected + violations_detected) as avg_errors_found,
    COUNT(*) as validation_runs
FROM spans
WHERE span_name IN ('check.rdf_validation', 'check.shacl_validation')
  AND timestamp > NOW() - INTERVAL 7 DAYS
```

**Compare to baseline:**
- Baseline: Manual validation caught 50% of errors (from user studies)
- Current: Automated validation catches 70% (from OTEL)
- Target: 95% detection rate

**Gap:** Still 25% below target. Need to improve SHACL error detection!

### Survey User Satisfaction

Send outcome satisfaction survey to RDF Ontology Designers:

> **How satisfied are you with error detection during RDF validation?**
>
> When validating your RDF ontology, how satisfied are you with the likelihood of detecting syntax and semantic errors?
>
> 1 = Very Dissatisfied, 5 = Very Satisfied

**Results:**
- Average satisfaction: 2.8/5 (low)
- Comments: "Misses subtle semantic errors", "SHACL messages are cryptic"

**Insight:** Users want better error detection (confirms gap analysis!)

---

## Complete Example: End-to-End

Let's walk through a complete example from job identification to measurement.

### Scenario: New Feature Request

**User request:**
> "Can you add a way to visualize my RDF ontology as a graph?"

### Step 1: Identify the Job

**Question:** What job is the user trying to do?

**Answer (after job interview):**
> "Understand the structure and relationships in my RDF ontology so I can validate that it correctly models my domain when reviewing ontology design."

**RDF Encoding:**

```turtle
jtbd:UnderstandOntologyStructureJob a jtbd:Job ;
    rdfs:label "Understand Ontology Structure"@en ;
    jtbd:jobStatement "Understand the structure and relationships in my RDF ontology so I can validate design correctness during ontology review"@en ;
    jtbd:persona jtbd:RDFOntologyDesigner ;
    jtbd:circumstance "When reviewing ontology design or debugging relationships"@en ;
    jtbd:functionalJob "Visualize classes, properties, and relationships in ontology"@en ;
    jtbd:emotionalJob "Feel confident I understand the complete ontology structure"@en ;
    jtbd:socialJob "Communicate ontology design effectively to stakeholders"@en ;
    jtbd:importance "medium"^^xsd:string .
```

### Step 2: Define Outcomes

**User wants:**

```turtle
# Outcome 1: Minimize time to understand structure
jtbd:MinimizeStructureUnderstandingTime a jtbd:Outcome ;
    rdfs:label "Minimize time to understand ontology structure"@en ;
    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "time"^^xsd:string ;
    jtbd:baseline "60"^^xsd:integer ;   # 60 min reading RDF manually
    jtbd:target "5"^^xsd:integer ;      # 5 min with visualization
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .  # No visualization exists

# Outcome 2: Maximize clarity of relationships
jtbd:MaximizeRelationshipClarity a jtbd:Outcome ;
    rdfs:label "Maximize clarity of relationships"@en ;
    jtbd:direction "maximize"^^xsd:string ;
    jtbd:metric "clarity_score"^^xsd:string ;
    jtbd:baseline "2"^^xsd:integer ;    # 2/5 from reading RDF
    jtbd:target "5"^^xsd:integer ;      # 5/5 with clear visualization
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .
```

### Step 3: Design Feature

**Feature:** `specify visualize` command

```turtle
cli:VisualizeCommand a cli:Command ;
    rdfs:label "visualize"@en ;
    rdfs:comment "Visualize RDF ontology as interactive graph"@en ;
    jtbd:accomplishesJob jtbd:UnderstandOntologyStructureJob ;
    jtbd:delivers jtbd:MinimizeStructureUnderstandingTime ;
    jtbd:delivers jtbd:MaximizeRelationshipClarity .
```

### Step 4: Generate Spec

```bash
ggen sync
# Produces: docs/features/visualize-command-spec.md
```

### Step 5: Implement with Measurement

```python
@app.command()
@timed
@span(
    "command.visualize",
    job="understand_ontology_structure",
    outcome="minimize_understanding_time",
    baseline=3600000,  # 60 min in ms
    target=300000      # 5 min in ms
)
def visualize(
    ontology_file: Path,
    output: Optional[Path] = None,
    format: str = "html"
):
    """
    Visualize RDF ontology as interactive graph.

    Jobs: Understand Ontology Structure
    Outcomes:
    - Minimize understanding time: target 5 min (baseline 60 min)
    - Maximize relationship clarity: target 5/5 (baseline 2/5)
    """
    with span("visualize.load_ontology") as load_span:
        graph = load_rdf_graph(ontology_file)
        load_span.set_attribute("triple_count", len(graph))

    with span("visualize.generate_graph") as gen_span:
        visualization = generate_graphviz(graph)
        gen_span.set_attribute("node_count", len(visualization.nodes))
        gen_span.set_attribute("edge_count", len(visualization.edges))

    with span("visualize.render") as render_span:
        output_path = render_visualization(visualization, format, output)
        render_span.set_attribute("output_format", format)
        render_span.set_attribute("output_file", str(output_path))

    console.print(f"[green]✓[/green] Visualization saved to {output_path}")
```

### Step 6: Measure and Iterate

**After 30 days, analyze:**

```sql
SELECT
    AVG(duration_ms) / 1000 as avg_minutes,
    PERCENTILE(duration_ms, 50) / 1000 as p50_minutes
FROM spans
WHERE span_name = 'command.visualize'
  AND timestamp > NOW() - INTERVAL 30 DAYS
```

**Results:**
- Avg time: 8 minutes (user spends time examining visualization)
- Baseline: 60 minutes
- Target: 5 minutes

**Success:** 87% improvement, slightly above target (acceptable!)

**Survey results:**
- Clarity score: 4.5/5 (excellent!)
- Satisfaction: 4.3/5 (high)

**Outcome:** Feature successfully delivers desired outcomes! ✅

---

## Next Steps

### Apply JTBD to Your Feature

Now that you understand the process, apply it:

1. **Identify a feature** you want to add or improve
2. **Interview users** to understand the job
3. **Define outcomes** they want to achieve
4. **Encode in RDF** for traceability
5. **Generate specs** from RDF
6. **Implement with OTEL** instrumentation
7. **Measure and iterate** based on data

### Resources

- [JTBD Framework Guide](../guides/jtbd-framework.md) - Deep dive into JTBD theory
- [Personas](./personas.md) - Detailed customer segments
- [Jobs & Outcomes Catalog](./jobs-outcomes-catalog.md) - Complete outcome inventory
- [Measurement Strategy](./measurement-strategy.md) - How to track outcomes
- [Examples](./examples.md) - More worked examples

### JTBD in Practice

**Daily Workflow:**

1. **Before implementing features:** Define the job and outcomes
2. **During implementation:** Instrument with OTEL
3. **After deployment:** Measure outcome delivery
4. **Weekly:** Review outcome metrics and identify improvements
5. **Monthly:** Survey users on satisfaction, update priorities

**Team Collaboration:**

- **Product Managers:** Define jobs and outcomes
- **Designers:** Optimize for outcome delivery
- **Engineers:** Implement and instrument features
- **Analysts:** Measure and report on outcomes
- **All:** Iterate based on outcome data

---

## Summary

**The JTBD Process:**

```
1. Define Job (what progress?)
   ↓
2. List Outcomes (how measure success?)
   ↓
3. Map Features (what delivers outcomes?)
   ↓
4. Generate Specs (RDF → documentation)
   ↓
5. Measure (OTEL → data → insights)
   ↓
6. Iterate (improve outcome delivery)
```

**Key Takeaways:**

- **Jobs are stable**, solutions evolve
- **Measure outcomes**, not outputs
- **RDF encoding** enables traceability
- **OTEL instrumentation** enables measurement
- **Iterate** based on data, not opinions

You're now ready to apply JTBD to spec-kit development!

---

**Questions or feedback?** Open an issue on GitHub or join the discussion.
