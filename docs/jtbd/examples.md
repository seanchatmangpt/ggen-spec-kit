# JTBD Integration Examples

## Overview

This document provides complete, worked examples of using Jobs To Be Done (JTBD) in spec-kit development. Each example shows the full lifecycle:

1. Job identification
2. Outcome definition
3. RDF specification
4. Feature implementation
5. Outcome measurement
6. Iteration based on data

---

## Table of Contents

1. [Example 1: Creating the `deps` Command with JTBD](#example-1-creating-the-deps-command-with-jtbd)
2. [Example 2: Improving SHACL Validation](#example-2-improving-shacl-validation)
3. [Example 3: Before/After Comparison (Traditional vs. JTBD)](#example-3-beforeafter-comparison-traditional-vs-jtbd)

---

## Example 1: Creating the `deps` Command with JTBD

### Background

**User request:**
> "We need a command to manage Python dependencies better."

**Traditional approach:** Build a feature that manages dependencies.

**JTBD approach:** First, understand the job.

---

### Step 1: Job Discovery Interview

**Questions:**
- What are you trying to accomplish?
- When do you need to manage dependencies?
- What's frustrating about the current approach?
- How do you measure success?

**User responses:**

**CLI Developer persona:**
> "I'm trying to ensure my CLI project has correct dependencies so I can avoid import errors and version conflicts during development. This happens whenever I add a new feature or update dependencies. Currently, I manually edit `pyproject.toml` and it's error-prone. Success means my project builds correctly and CI doesn't fail."

**Operations Engineer persona:**
> "I need to audit dependencies across multiple projects to identify security vulnerabilities and license compliance issues. This happens monthly for compliance reports. Manually inspecting each project's dependencies takes hours. Success means complete, accurate dependency inventory in minutes."

### Step 2: Define Jobs in RDF

From interviews, we identified **two jobs** for different personas:

```turtle
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Job 1: Manage Project Dependencies (CLI Developer)
jtbd:ManageProjectDependenciesJob a jtbd:Job ;
    rdfs:label "Manage Project Dependencies"@en ;
    jtbd:jobStatement "Ensure my CLI project has correct dependencies so I can avoid import errors and version conflicts during development"@en ;
    jtbd:persona jtbd:CLIDeveloper ;
    jtbd:circumstance "When adding features or updating dependencies"@en ;
    jtbd:functionalJob "Add, update, and remove Python dependencies correctly"@en ;
    jtbd:emotionalJob "Feel confident that dependencies are correct and complete"@en ;
    jtbd:socialJob "Be seen as maintaining a well-structured, reliable project"@en ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:frequency "weekly"^^xsd:string .

# Job 2: Audit Dependency Portfolio (Operations Engineer)
jtbd:AuditDependencyPortfolioJob a jtbd:Job ;
    rdfs:label "Audit Dependency Portfolio"@en ;
    jtbd:jobStatement "Audit dependencies across multiple projects to identify security and compliance issues for monthly reports"@en ;
    jtbd:persona jtbd:OperationsEngineer ;
    jtbd:circumstance "Monthly compliance reporting, security audits"@en ;
    jtbd:functionalJob "Extract complete dependency inventory from all projects"@en ;
    jtbd:emotionalJob "Feel assured no vulnerabilities are missed"@en ;
    jtbd:socialJob "Be recognized for thorough security and compliance practices"@en ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:frequency "monthly"^^xsd:string .
```

### Step 3: Define Desired Outcomes

For each job, list outcomes:

```turtle
# Outcomes for Job 1: Manage Dependencies (CLI Developer)

jtbd:MinimizeTimeToAddDependency a jtbd:Outcome ;
    rdfs:label "Minimize time to add dependency"@en ;
    jtbd:outcomeStatement "Minimize the time it takes to add a new dependency to project configuration"@en ;
    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "time"^^xsd:string ;
    jtbd:metricUnit "seconds"^^xsd:string ;
    jtbd:baseline "180"^^xsd:integer ;   # 3 min manual editing
    jtbd:target "10"^^xsd:integer ;      # 10 sec with CLI
    jtbd:current "180"^^xsd:integer ;    # No automation yet
    jtbd:importance "medium"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .

jtbd:MaximizeDependencyAccuracy a jtbd:Outcome ;
    rdfs:label "Maximize dependency accuracy"@en ;
    jtbd:outcomeStatement "Maximize the likelihood that dependencies are correct (no version conflicts or missing packages)"@en ;
    jtbd:direction "maximize"^^xsd:string ;
    jtbd:metric "accuracy"^^xsd:string ;
    jtbd:metricUnit "percent"^^xsd:string ;
    jtbd:baseline "70"^^xsd:integer ;    # 70% correct manually
    jtbd:target "100"^^xsd:integer ;     # 100% with validation
    jtbd:current "70"^^xsd:integer ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .

jtbd:MinimizeDependencyConflicts a jtbd:Outcome ;
    rdfs:label "Minimize version conflicts"@en ;
    jtbd:outcomeStatement "Minimize the number of version conflicts that occur when adding dependencies"@en ;
    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "conflict_count"^^xsd:string ;
    jtbd:metricUnit "count"^^xsd:string ;
    jtbd:baseline "3"^^xsd:integer ;     # 3 conflicts per 10 dep changes
    jtbd:target "0"^^xsd:integer ;       # Zero conflicts
    jtbd:current "3"^^xsd:integer ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .

# Outcomes for Job 2: Audit Dependencies (Operations Engineer)

jtbd:MinimizeAuditTime a jtbd:Outcome ;
    rdfs:label "Minimize audit time"@en ;
    jtbd:outcomeStatement "Minimize the time required to audit dependencies across all organization projects"@en ;
    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "time"^^xsd:string ;
    jtbd:metricUnit "minutes"^^xsd:string ;
    jtbd:baseline "240"^^xsd:integer ;   # 4 hours manual
    jtbd:target "10"^^xsd:integer ;      # 10 min automated
    jtbd:current "240"^^xsd:integer ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .

jtbd:MaximizeVulnerabilityDetection a jtbd:Outcome ;
    rdfs:label "Maximize vulnerability detection"@en ;
    jtbd:outcomeStatement "Maximize the likelihood of detecting security vulnerabilities in dependencies"@en ;
    jtbd:direction "maximize"^^xsd:string ;
    jtbd:metric "detection_rate"^^xsd:string ;
    jtbd:metricUnit "percent"^^xsd:string ;
    jtbd:baseline "60"^^xsd:integer ;    # 60% manual scanning
    jtbd:target "95"^^xsd:integer ;      # 95% automated
    jtbd:current "60"^^xsd:integer ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .

# Link outcomes to jobs
jtbd:ManageProjectDependenciesJob
    jtbd:hasOutcome jtbd:MinimizeTimeToAddDependency ;
    jtbd:hasOutcome jtbd:MaximizeDependencyAccuracy ;
    jtbd:hasOutcome jtbd:MinimizeDependencyConflicts .

jtbd:AuditDependencyPortfolioJob
    jtbd:hasOutcome jtbd:MinimizeAuditTime ;
    jtbd:hasOutcome jtbd:MaximizeVulnerabilityDetection .
```

### Step 4: Design Features to Deliver Outcomes

Based on outcomes, design the `deps` command with subcommands:

```turtle
@prefix cli: <http://github.com/github/spec-kit/cli#> .

# Main command group
cli:DepsCommand a cli:Command ;
    rdfs:label "deps"@en ;
    rdfs:comment "Dependency management command group"@en ;
    jtbd:accomplishesJob jtbd:ManageProjectDependenciesJob ;
    jtbd:accomplishesJob jtbd:AuditDependencyPortfolioJob .

# Subcommand 1: Add dependency
cli:DepsAddCommand a cli:Command ;
    rdfs:subCommandOf cli:DepsCommand ;
    rdfs:label "add"@en ;
    rdfs:comment "Add a dependency to the project"@en ;
    jtbd:delivers jtbd:MinimizeTimeToAddDependency ;
    jtbd:delivers jtbd:MaximizeDependencyAccuracy ;
    jtbd:delivers jtbd:MinimizeDependencyConflicts .

# Subcommand 2: Audit dependencies
cli:DepsAuditCommand a cli:Command ;
    rdfs:subCommandOf cli:DepsCommand ;
    rdfs:label "audit"@en ;
    rdfs:comment "Audit dependencies for security and compliance"@en ;
    jtbd:delivers jtbd:MinimizeAuditTime ;
    jtbd:delivers jtbd:MaximizeVulnerabilityDetection .

# Subcommand 3: List dependencies
cli:DepsListCommand a cli:Command ;
    rdfs:subCommandOf cli:DepsCommand ;
    rdfs:label "list"@en ;
    rdfs:comment "List all project dependencies"@en ;
    jtbd:delivers jtbd:MinimizeAuditTime .
```

### Step 5: Generate Specification

Use ggen to generate specification from RDF:

**SPARQL query:** `sparql/deps-spec.rq`

```sparql
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>
PREFIX cli: <http://github.com/github/spec-kit/cli#>

CONSTRUCT {
  ?command a cli:Command ;
           rdfs:label ?label ;
           rdfs:comment ?comment ;
           jtbd:accomplishesJob ?job ;
           jtbd:delivers ?outcome .

  ?job rdfs:label ?jobLabel ;
       jtbd:persona ?persona ;
       jtbd:jobStatement ?jobStmt .

  ?outcome rdfs:label ?outcomeLabel ;
           jtbd:importance ?importance ;
           jtbd:baseline ?baseline ;
           jtbd:target ?target .
}
WHERE {
  ?command a cli:Command ;
           rdfs:label "deps"@en .

  OPTIONAL {
    ?command jtbd:accomplishesJob ?job .
    ?job rdfs:label ?jobLabel ;
         jtbd:persona ?persona ;
         jtbd:jobStatement ?jobStmt .
  }

  OPTIONAL {
    ?command jtbd:delivers ?outcome .
    ?outcome rdfs:label ?outcomeLabel ;
             jtbd:importance ?importance ;
             jtbd:baseline ?baseline ;
             jtbd:target ?target .
  }
}
```

**Tera template:** `templates/deps-spec.md.tera`

```markdown
# Specification: deps Command

## Jobs To Be Done

This command accomplishes the following customer jobs:

{% for job in jobs %}
### {{ job.label }}

**Persona:** {{ job.persona }}

**Job Statement:**
{{ job.jobStatement }}

**When:** {{ job.circumstance }}
{% endfor %}

## Outcomes Delivered

{% for outcome in outcomes %}
### {{ outcome.label }}

**Outcome Statement:** {{ outcome.outcomeStatement }}

**Measurement:**
- Baseline: {{ outcome.baseline }} {{ outcome.metricUnit }}
- Target: {{ outcome.target }} {{ outcome.metricUnit }}
- Importance: {{ outcome.importance }}

**Success Criteria:**
The feature must achieve at least 80% of the improvement from baseline to target.
{% endfor %}

## Command Design

### deps add <package>

Add a dependency to the project.

**Arguments:**
- `package`: Package name (e.g., "requests", "pytest")

**Options:**
- `--dev`: Add as development dependency
- `--version`: Specific version constraint

**Outcome Delivery:**
- Minimize time to add: < 10 sec (vs. 3 min baseline)
- Maximize accuracy: Validate version compatibility
- Minimize conflicts: Check for conflicts before adding

### deps audit

Audit dependencies for security and compliance.

**Options:**
- `--json`: Export results as JSON
- `--severity`: Minimum severity (low, medium, high, critical)

**Outcome Delivery:**
- Minimize audit time: < 10 min for portfolio (vs. 4 hours)
- Maximize detection: 95%+ vulnerability detection rate

### deps list

List all project dependencies.

**Options:**
- `--tree`: Show dependency tree
- `--outdated`: Show outdated packages

## Implementation Requirements

To deliver the specified outcomes, the implementation must:

1. **Speed:**
   - Execute `deps add` in < 10 seconds
   - Execute `deps audit` in < 10 minutes for 50 projects

2. **Accuracy:**
   - Validate version compatibility before adding
   - Check for conflicts with existing dependencies
   - Detect 95%+ of known vulnerabilities

3. **Usability:**
   - Single command execution
   - Clear error messages
   - Progress feedback for long operations

## Success Metrics (OTEL)

Track these metrics in OpenTelemetry:

```python
@span("deps.add", outcome="minimize_add_time", baseline=180, target=10)
def deps_add(package: str):
    # Measure duration

@span("deps.audit", outcome="minimize_audit_time", baseline=14400, target=600)
def deps_audit():
    # Measure duration and vulnerabilities detected
```
```

**Generate:**

```bash
ggen sync --config docs/ggen.toml
```

**Output:** `docs/features/deps-command-spec.md`

### Step 6: Implement with OTEL Instrumentation

```python
# src/specify_cli/commands/deps.py
from pathlib import Path
from typing import Optional
import typer
from specify_cli.core.telemetry import span, timed
from specify_cli.ops.dependency import add_dependency, audit_dependencies

app = typer.Typer(help="Dependency management commands")

@app.command()
@timed
@span(
    "deps.add",
    job="manage_project_dependencies",
    outcome="minimize_add_time",
    baseline=180_000,  # 3 min in ms
    target=10_000      # 10 sec in ms
)
def add(
    package: str,
    dev: bool = False,
    version: Optional[str] = None
):
    """
    Add a dependency to the project.

    Jobs: Manage Project Dependencies (CLI Developer)
    Outcomes:
    - Minimize time to add: target 10s (baseline 3min)
    - Maximize accuracy: validate compatibility
    - Minimize conflicts: check before adding
    """
    with span("deps.validate_compatibility") as validate_span:
        conflicts = check_version_conflicts(package, version)
        validate_span.set_attribute("conflicts_detected", len(conflicts))
        validate_span.set_attribute("outcome", "minimize_conflicts")

        if conflicts:
            console.print(f"[red]✗[/red] Version conflicts detected:")
            for conflict in conflicts:
                console.print(f"  - {conflict}")
            raise typer.Exit(1)

    with span("deps.add_to_config") as add_span:
        success = add_dependency(package, version, dev=dev)
        add_span.set_attribute("success", success)
        add_span.set_attribute("package", package)
        add_span.set_attribute("outcome", "maximize_accuracy")

    console.print(f"[green]✓[/green] Added {package} to dependencies")


@app.command()
@timed
@span(
    "deps.audit",
    job="audit_dependency_portfolio",
    outcome="minimize_audit_time",
    baseline=14_400_000,  # 4 hours in ms
    target=600_000        # 10 min in ms
)
def audit(
    json: bool = False,
    severity: str = "medium"
):
    """
    Audit dependencies for security and compliance.

    Jobs: Audit Dependency Portfolio (Operations Engineer)
    Outcomes:
    - Minimize audit time: target 10min (baseline 4hr)
    - Maximize detection: 95%+ vulnerability detection
    """
    with span("deps.collect_dependencies") as collect_span:
        all_deps = collect_all_dependencies()
        collect_span.set_attribute("dependency_count", len(all_deps))

    with span("deps.scan_vulnerabilities") as scan_span:
        vulnerabilities = scan_for_vulnerabilities(all_deps, severity)
        scan_span.set_attribute("vulnerabilities_found", len(vulnerabilities))
        scan_span.set_attribute("outcome", "maximize_vulnerability_detection")

    if json:
        typer.echo(json.dumps(vulnerabilities, indent=2))
    else:
        report_vulnerabilities(vulnerabilities)
```

### Step 7: Measure Outcome Delivery

**After 30 days of usage, query OTEL:**

```sql
-- Outcome 1: Minimize time to add dependency
SELECT
    AVG(duration_ms) as current_avg,
    PERCENTILE(duration_ms, 50) as p50,
    180000 as baseline,
    10000 as target,
    (180000 - AVG(duration_ms))::FLOAT / (180000 - 10000) * 100 as success_pct
FROM spans
WHERE span_name = 'deps.add'
  AND timestamp > NOW() - INTERVAL 30 DAYS
```

**Results:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Current avg | 12,000ms (12s) | Slightly above target |
| p50 | 9,500ms | Median meets target! |
| p95 | 18,000ms | Slow cases need investigation |
| Success % | 99% | Excellent vs. baseline |

**Outcome 2: Maximize dependency accuracy**

```sql
SELECT
    AVG(conflicts_detected) as avg_conflicts,
    SUM(CASE WHEN conflicts_detected > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) * 100 as conflict_rate
FROM spans
WHERE span_name = 'deps.validate_compatibility'
  AND timestamp > NOW() - INTERVAL 30 DAYS
```

**Results:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Avg conflicts detected | 0.3 | Catching conflicts early! |
| Conflict rate | 15% | 15% of adds would have caused conflicts |
| Accuracy improvement | 30% → 100% | Prevented all conflicts |

**User Satisfaction Survey:**

> How satisfied are you with the `deps` command for managing dependencies?

**Results:**
- CLI Developer satisfaction: 4.3/5 (high)
- Operations Engineer satisfaction: 4.5/5 (high)
- Comments: "Saves so much time!", "Catches issues I would have missed"

**Outcome:** Feature successfully delivers desired outcomes! ✅

### Step 8: Iterate Based on Insights

**Identified issue:** p95 is 18 seconds (slow cases)

**Investigation:**

```sql
-- What causes slow adds?
SELECT
    package,
    duration_ms
FROM spans
WHERE span_name = 'deps.add'
  AND duration_ms > 15000
ORDER BY duration_ms DESC
LIMIT 10
```

**Finding:** Large packages with many dependencies (e.g., pandas, pytorch) take longer due to dependency tree analysis.

**Improvement:** Add caching for dependency trees.

**Result after caching:**
- p95 improved from 18s to 11s
- User satisfaction increased from 4.3 to 4.6

---

## Example 2: Improving SHACL Validation

### Background

From the [Jobs & Outcomes Catalog](./jobs-outcomes-catalog.md), we identified a high-priority outcome:

**Outcome O1.2.2:** Maximize likelihood of detecting SHACL violations
- Importance: High
- Current Satisfaction: Low (2/5)
- Gap: ⭐⭐⭐ Critical

**Problem:** SHACL error messages are cryptic, users don't understand them.

### Step 1: Understand the Painpoint

**User interview (RDF Ontology Designer):**

> "When SHACL validation fails, I get messages like 'sh:MinCountConstraintComponent violated.' I don't know what that means or how to fix it. I end up Googling SHACL specs or asking colleagues. It takes 15-30 minutes to understand and fix each error."

**Current state:**
```
SHACL Validation Failed:
  - sh:MinCountConstraintComponent violated on :Person
  - sh:MaxLengthConstraintComponent violated on :name
  - sh:DatatypeConstraintComponent violated on :age
```

**User wants:**
```
SHACL Validation Failed:

  ✗ Missing required property
    Class: :Person
    Property: :name
    Constraint: Must have at least 1 value
    Fix: Add at least one :name property to :Person

  ✗ Value too long
    Class: :Person
    Property: :name
    Current: 150 characters
    Maximum: 100 characters
    Fix: Shorten the :name value to 100 characters or less

  ✗ Wrong data type
    Class: :Person
    Property: :age
    Expected: xsd:integer
    Got: xsd:string
    Fix: Change :age value to an integer (e.g., 25 instead of "25")
```

### Step 2: Define Improvement Outcome

```turtle
jtbd:MaximizeSHACLErrorClarity a jtbd:Outcome ;
    rdfs:label "Maximize SHACL error clarity"@en ;
    jtbd:outcomeStatement "Maximize the clarity of SHACL validation error messages so errors can be understood and fixed quickly"@en ;
    jtbd:direction "maximize"^^xsd:string ;
    jtbd:metric "clarity_score"^^xsd:string ;
    jtbd:metricUnit "score"^^xsd:string ;  # 1-5 scale
    jtbd:baseline "2"^^xsd:integer ;    # Current: cryptic
    jtbd:target "5"^^xsd:integer ;      # Goal: crystal clear
    jtbd:current "2"^^xsd:integer ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .

jtbd:MinimizeErrorResolutionTime a jtbd:Outcome ;
    rdfs:label "Minimize error resolution time"@en ;
    jtbd:outcomeStatement "Minimize the time required to understand and fix SHACL validation errors"@en ;
    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "time"^^xsd:string ;
    jtbd:metricUnit "minutes"^^xsd:string ;
    jtbd:baseline "20"^^xsd:integer ;   # Current: 15-30 min avg
    jtbd:target "2"^^xsd:integer ;      # Goal: < 2 min
    jtbd:current "20"^^xsd:integer ;
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .
```

### Step 3: Design Improvement

**Feature enhancement:** Plain-English SHACL error explanations

```python
# src/specify_cli/ops/shacl_validation.py

ERROR_TEMPLATES = {
    "sh:MinCountConstraintComponent": {
        "title": "Missing required property",
        "explanation": "This class requires at least {min_count} value(s) for this property",
        "fix": "Add at least {min_count} {property} value(s) to {focus_node}"
    },
    "sh:MaxLengthConstraintComponent": {
        "title": "Value too long",
        "explanation": "The property value exceeds the maximum allowed length",
        "fix": "Shorten the {property} value to {max_length} characters or less"
    },
    "sh:DatatypeConstraintComponent": {
        "title": "Wrong data type",
        "explanation": "The property value has an incorrect data type",
        "fix": "Change {property} value to type {expected_type}"
    }
}

def format_shacl_error(violation: SHACLViolation) -> str:
    """Convert cryptic SHACL violation to plain English."""
    template = ERROR_TEMPLATES.get(violation.component_type, {
        "title": "Validation error",
        "explanation": str(violation),
        "fix": "Review the SHACL constraint and adjust your data"
    })

    return f"""
  ✗ {template['title']}
    Class: {violation.focus_node}
    Property: {violation.property}
    Constraint: {template['explanation'].format(**violation.parameters)}
    Fix: {template['fix'].format(**violation.parameters)}
    """.strip()
```

### Step 4: Implement with A/B Testing

Track which version users see:

```python
@span(
    "shacl.validation",
    error_format="plain_english",  # or "raw" for control group
    outcome="maximize_error_clarity"
)
def validate_shacl(ontology: Path, use_plain_english: bool = True):
    violations = run_shacl_validation(ontology)

    if use_plain_english:
        formatted_errors = [format_shacl_error(v) for v in violations]
    else:
        formatted_errors = [str(v) for v in violations]  # Raw SHACL output

    return ValidationResult(
        success=len(violations) == 0,
        violations=violations,
        formatted_errors=formatted_errors
    )
```

### Step 5: Measure Impact

**After 60 days, compare cohorts:**

```sql
-- Clarity score by error format
SELECT
    attributes->>'error_format' as format,
    AVG(user_satisfaction_clarity) as avg_clarity
FROM spans
WHERE span_name = 'shacl.validation'
  AND timestamp > NOW() - INTERVAL 60 DAYS
GROUP BY format
```

**Results:**

| Format | Clarity Score | Improvement |
|--------|---------------|-------------|
| raw (baseline) | 2.1/5 | - |
| plain_english | 4.3/5 | +105% |

**Resolution time:**

```sql
-- Time from error to fix (tracked by subsequent validation)
SELECT
    attributes->>'error_format' as format,
    AVG(time_to_resolution_min) as avg_resolution_time
FROM error_resolution_events
WHERE error_type = 'shacl_violation'
  AND timestamp > NOW() - INTERVAL 60 DAYS
GROUP BY format
```

**Results:**

| Format | Avg Resolution Time | Improvement |
|--------|---------------------|-------------|
| raw (baseline) | 18 min | - |
| plain_english | 4 min | -78% (14 min saved) |

**User feedback:**

> "HUGE improvement! I can actually understand what's wrong now." - RDF Designer

> "Error messages are clear and actionable. Love it!" - Ontology Engineer

**Outcome:** Plain-English errors significantly improved clarity and resolution time! ✅

**Decision:** Roll out plain-English errors to 100% of users.

---

## Example 3: Before/After Comparison (Traditional vs. JTBD)

### Scenario: Feature Request

**Request:**
> "Add a `--watch` flag to `ggen sync` so it re-runs when files change."

---

### Traditional Approach (Feature-Driven)

**Process:**

1. **Receive request** → Add to backlog
2. **Prioritize** based on intuition/loudest voice
3. **Implement** `--watch` flag
4. **Ship** and move to next feature

**Implementation:**

```python
@app.command()
def sync(
    watch: bool = False  # Added based on request
):
    if watch:
        # Implement file watching
        observer = Observer()
        observer.schedule(event_handler, path=".")
        observer.start()
    else:
        # Normal sync
        run_ggen_sync()
```

**Outcome:**
- Feature exists ✓
- Some users use it ✓
- Don't know if it actually helps ✗
- Can't measure value delivered ✗
- Don't know if there are better solutions ✗

---

### JTBD Approach (Outcome-Driven)

**Process:**

1. **Understand the job** → Why do users want `--watch`?
2. **Define outcomes** → What are they trying to achieve?
3. **Evaluate solutions** → Is `--watch` the best way?
4. **Implement & measure** → Track outcome delivery
5. **Iterate** → Improve based on data

**Step 1: Job Interview**

**Questions:**
- Why do you want a `--watch` flag?
- When would you use it?
- What problem does it solve?
- How would you measure success?

**User response:**

> "I'm iterating on documentation templates and it's annoying to manually run `ggen sync` after every template change. I want the documentation to update automatically so I can preview changes in real-time while I'm working. Success means I can see updated output within seconds of saving a template file."

**Job identified:**
> "Keep generated documentation synchronized with evolving templates so I can preview changes in real-time during iterative template development."

**Step 2: Define Outcomes**

```turtle
jtbd:MinimizeIterationCycleTime a jtbd:Outcome ;
    rdfs:label "Minimize iteration cycle time"@en ;
    jtbd:outcomeStatement "Minimize the time from template edit to seeing updated documentation during iterative development"@en ;
    jtbd:direction "minimize"^^xsd:string ;
    jtbd:metric "time"^^xsd:string ;
    jtbd:metricUnit "seconds"^^xsd:string ;
    jtbd:baseline "30"^^xsd:integer ;   # Switch to terminal, run command, switch back
    jtbd:target "2"^^xsd:integer ;      # Automatic, nearly instant
    jtbd:importance "medium"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .

jtbd:MaximizeDevelopmentFlow a jtbd:Outcome ;
    rdfs:label "Maximize development flow state"@en ;
    jtbd:outcomeStatement "Maximize the ability to stay in flow state during template development by minimizing context switches"@en ;
    jtbd:direction "maximize"^^xsd:string ;
    jtbd:metric "flow_score"^^xsd:string ;
    jtbd:metricUnit "score"^^xsd:string ;  # 1-5 subjective
    jtbd:baseline "2"^^xsd:integer ;    # Constant interruptions
    jtbd:target "5"^^xsd:integer ;      # Seamless iteration
    jtbd:importance "high"^^xsd:string ;
    jtbd:currentSatisfaction "low"^^xsd:string .
```

**Step 3: Evaluate Solutions**

**Possible solutions beyond `--watch`:**

1. **Watch mode** (`--watch` flag)
2. **IDE integration** (VS Code extension with live preview)
3. **Hot reload** (embedded server with WebSocket updates)
4. **Git hooks** (automatic sync on file save/commit)

**Evaluate each against outcomes:**

| Solution | Cycle Time | Flow State | Complexity | Decision |
|----------|------------|------------|------------|----------|
| Watch mode | 2-5s | Good | Low | ✓ Quick win |
| IDE integration | 1s | Excellent | High | Future enhancement |
| Hot reload | <1s | Excellent | High | Overkill for now |
| Git hooks | 5-10s | Poor | Medium | Doesn't help iteration |

**Decision:** Start with `--watch` (delivers outcomes with low complexity), plan IDE integration for future.

**Step 4: Implement with Measurement**

```python
@app.command()
@timed
@span(
    "ggen.sync",
    watch_mode=watch,
    outcome="minimize_iteration_cycle_time",
    baseline=30_000,  # 30s manual
    target=2_000      # 2s automatic
)
def sync(
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch for file changes and auto-regenerate")
):
    """
    Transform RDF specifications to code/markdown.

    Jobs: Keep Documentation Synchronized with Templates
    Outcomes:
    - Minimize iteration cycle time: target 2s (baseline 30s)
    - Maximize flow state: reduce context switches
    """
    if watch:
        with span("ggen.watch_mode") as watch_span:
            file_watcher = FileWatcher(
                paths=["templates/", "ontology/"],
                on_change=lambda: run_ggen_sync()
            )

            console.print("[cyan]Watching for changes...[/cyan]")
            file_watcher.start()

            watch_span.set_attribute("files_watched", len(file_watcher.paths))
    else:
        run_ggen_sync()
```

**Step 5: Measure Outcomes**

```sql
-- Cycle time with vs. without watch mode
SELECT
    CASE WHEN watch_mode THEN 'watch' ELSE 'manual' END as mode,
    AVG(duration_ms) as avg_cycle_time,
    COUNT(*) as usage_count
FROM spans
WHERE span_name = 'ggen.sync'
  AND timestamp > NOW() - INTERVAL 30 DAYS
GROUP BY watch_mode
```

**Results:**

| Mode | Avg Cycle Time | Usage Count | Notes |
|------|----------------|-------------|-------|
| manual | 28s | 450 | Baseline |
| watch | 3.2s | 850 | 89% faster, 2x more iterations |

**Observation:** Watch mode users iterate 2x more (850 vs 450 syncs) → enabling more experimentation!

**Survey:**

> How does watch mode affect your template development workflow?

**Results:**
- Flow state score: 4.2/5 (vs. 2.1 baseline) → +100% improvement
- Comments: "Game changer for template development", "Never going back to manual sync"

**Step 6: Discover Additional Insights**

**Unexpected finding from OTEL:**

```sql
-- What files trigger regeneration most often?
SELECT
    file_path,
    COUNT(*) as change_count
FROM file_change_events
WHERE watcher_active = true
  AND timestamp > NOW() - INTERVAL 30 DAYS
GROUP BY file_path
ORDER BY change_count DESC
LIMIT 10
```

**Results:**

| File | Changes | Insight |
|------|---------|---------|
| templates/main.md.tera | 450 | Most-edited template |
| ontology/schema.ttl | 320 | Schema evolving frequently |
| sparql/extract.rq | 180 | SPARQL queries iterated often |
| .gitignore | 150 | Why is this triggering sync? Bug! |

**Improvement:** Exclude `.gitignore` and other non-source files from watch.

**Step 7: Plan Next Iteration**

Based on outcome data and user feedback:

**High priority (next sprint):**
- IDE integration (VS Code extension) → Further reduce cycle time, eliminate terminal switching
- Better progress indication → Show which files being processed

**Medium priority (backlog):**
- Smart incremental regeneration → Only regenerate changed files
- Template syntax validation → Catch errors before regeneration

**Low priority:**
- Hot reload web preview → Nice-to-have, high complexity

---

### Comparison: Traditional vs. JTBD Results

| Aspect | Traditional Approach | JTBD Approach |
|--------|---------------------|---------------|
| **Feature shipped** | Yes | Yes |
| **User satisfaction** | Unknown | 4.2/5 (measured) |
| **Outcome delivered** | Unknown | 89% faster iteration |
| **Usage adoption** | Unknown | 65% of doc writers use it |
| **Innovation** | Implemented request as-is | Identified IDE integration opportunity |
| **Measurement** | No metrics | Full OTEL instrumentation |
| **Next steps** | Wait for next request | Data-driven roadmap (IDE integration) |
| **Value proof** | Anecdotal | Quantitative (850 uses/month, 14min saved per session) |

**JTBD advantage:**
- **Objective prioritization** (high importance + low satisfaction = top priority)
- **Measurable impact** (89% cycle time reduction, 2x more iterations)
- **Continuous improvement** (data identifies next enhancements)
- **Innovation discovery** (found better solution: IDE integration)
- **Alignment** (team agrees on outcome-driven roadmap)

---

## Summary: JTBD in Practice

### Key Takeaways

1. **Start with the job, not the feature**
   - Feature requests are solutions; discover the underlying job first

2. **Define measurable outcomes**
   - Vague goals → "improve error messages"
   - JTBD → "Maximize clarity score from 2/5 to 5/5, minimize resolution time from 20min to 2min"

3. **Evaluate alternative solutions**
   - Don't implement first idea; consider all ways to deliver outcomes

4. **Instrument and measure**
   - OTEL tracks outcome delivery in production
   - Data drives iteration and proves value

5. **Iterate based on data, not opinions**
   - Metrics reveal what works and what doesn't
   - Discover unexpected usage patterns and opportunities

### JTBD Workflow

```
User Request
    ↓
Job Interview (understand progress desired)
    ↓
Outcome Definition (measurable success criteria)
    ↓
Solution Evaluation (what delivers outcomes best?)
    ↓
RDF Specification (encode jobs, outcomes, features)
    ↓
Implementation + OTEL (build with measurement)
    ↓
Outcome Measurement (did we deliver?)
    ↓
Iteration (improve outcome delivery continuously)
```

### When to Use JTBD

**Always:**
- New features
- Prioritization decisions
- User research
- Roadmap planning

**Especially:**
- High-stakes features (complex, costly, risky)
- Conflicting feature requests
- Low user satisfaction areas
- Innovation opportunities

**Skip (maybe):**
- Trivial fixes (typos, obvious bugs)
- Compliance requirements (no choice)
- Internal tech debt (developers are the "users")

---

**More Resources:**
- [JTBD Framework Guide](../guides/jtbd-framework.md)
- [Personas](./personas.md)
- [Jobs & Outcomes Catalog](./jobs-outcomes-catalog.md)
- [Measurement Strategy](./measurement-strategy.md)
- [Getting Started Guide](./getting-started.md)
