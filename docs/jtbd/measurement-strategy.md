# Measuring Outcome Success: JTBD Measurement Strategy

## Overview

Jobs To Be Done provides a customer-centric framework, but **measurement** is what makes it actionable. This document explains how to track whether we're delivering desired outcomes, improving customer satisfaction, and creating real value.

**Key Principle:** Measure outcomes, not outputs. Success isn't shipping features—it's helping customers make progress toward their goals.

---

## Table of Contents

1. [JTBD Measurement Philosophy](#jtbd-measurement-philosophy)
2. [Outcome Measurement Framework](#outcome-measurement-framework)
3. [OpenTelemetry Instrumentation Strategy](#opentelemetry-instrumentation-strategy)
4. [Metrics Collection and Analysis](#metrics-collection-and-analysis)
5. [Interpreting Results](#interpreting-results)
6. [Improving Outcome Delivery](#improving-outcome-delivery)
7. [Measurement Examples by Command](#measurement-examples-by-command)

---

## JTBD Measurement Philosophy

### Outcomes vs. Outputs

**Traditional (Output-Focused):**
- Metrics: Features shipped, lines of code, velocity
- Goal: Ship more features faster
- Problem: No guarantee of customer value

**JTBD (Outcome-Focused):**
- Metrics: Jobs completed successfully, satisfaction scores, outcome achievement
- Goal: Help customers make progress faster
- Benefit: Direct measure of value delivery

### The Outcome Success Equation

```
Outcome Success = (Current Performance - Baseline) / (Best Possible - Baseline)
```

Where:
- **Baseline**: Performance before feature exists (e.g., manual workflow)
- **Current Performance**: Performance with current feature
- **Best Possible**: Theoretical ideal (e.g., instant, zero errors)

Example: "Minimize time to validate RDF syntax"
- Baseline: 5 minutes (manual validation)
- Current: 10 seconds (automated `specify check`)
- Best Possible: 0 seconds (instant)
- Success: (300 - 10) / (300 - 0) = 97% of ideal achieved

### Leading vs. Lagging Indicators

**Leading Indicators** (predict future success):
- Feature adoption rate
- Usage frequency
- Time spent using feature
- Error rates during usage

**Lagging Indicators** (confirm success):
- Customer satisfaction scores
- Net Promoter Score (NPS)
- Outcome achievement rate
- Job success rate

Track both: leading indicators guide short-term improvements, lagging indicators validate long-term strategy.

---

## Outcome Measurement Framework

### Step 1: Define Measurable Outcomes

For each job, specify outcomes in measurable terms:

**Format:**
```
[Direction: Minimize/Maximize] [Metric] [Object of Control] [Context]
```

**Example:**
```
Minimize the time it takes to generate documentation from RDF when ontology files are updated
```

**Measurable Components:**
- **Direction**: Minimize
- **Metric**: Time (seconds)
- **Object**: Documentation generation process
- **Context**: After ontology updates
- **Baseline**: 30 minutes (manual)
- **Target**: < 5 seconds (automated)

### Step 2: Establish Baselines

Before implementing a feature, measure current state:

**Methods:**
- **User studies**: Time users performing task manually
- **Log analysis**: Parse historical logs for current metrics
- **Surveys**: Ask users to estimate current performance
- **Competitor analysis**: Benchmark against alternatives

**Example Baseline Measurement:**
```python
# Before `ggen sync` existed
def manual_documentation_generation(ontology: Path) -> Duration:
    """
    Measured manual documentation process:
    1. Read RDF ontology (5 min)
    2. Extract concepts manually (10 min)
    3. Write Markdown (15 min)
    Total: ~30 minutes average
    """
    return timedelta(minutes=30)
```

### Step 3: Instrument Features with OTEL

Add OpenTelemetry instrumentation to track outcome metrics:

```python
from specify_cli.core.telemetry import span, timed

@timed  # Automatically measures duration
@span("ggen.sync", outcome="documentation_generated")
def ggen_sync(config: Path) -> SyncResult:
    """
    OTEL Attributes tracked:
    - duration: Time to complete (ms)
    - ontology_file: Source ontology path
    - output_files: Count of files generated
    - success: Boolean success flag
    - error_type: If failed, what error
    """
    # Implementation
    pass
```

### Step 4: Define Success Criteria

Establish thresholds for outcome success:

**Success Levels:**

| Level | Performance | Example (Time to Generate Docs) |
|-------|-------------|----------------------------------|
| **Failing** | Worse than baseline | > 30 min (slower than manual!) |
| **Baseline** | Matches current state | ~30 min (same as manual) |
| **Good** | Better than baseline | < 10 min (3x faster) |
| **Excellent** | Near target | < 1 min (30x faster) |
| **Ideal** | At or beyond target | < 5 sec (360x faster) |

### Step 5: Measure Continuously

Track metrics in production with every usage:

**Measurement Cadence:**
- **Real-time**: OTEL spans for every execution
- **Daily**: Aggregate statistics (p50, p95, p99)
- **Weekly**: Trend analysis and anomaly detection
- **Monthly**: Satisfaction surveys and outcome reviews

---

## OpenTelemetry Instrumentation Strategy

### Standard Span Attributes

All spans should include these attributes for JTBD analysis:

```python
@span(
    "command.execution",
    # Job context
    job_type="validate_rdf_ontology",          # Which job
    persona="rdf_ontology_designer",           # Which persona
    circumstance="pre_commit_validation",      # When/why

    # Outcome tracking
    outcome="syntax_validated",                # What outcome
    outcome_importance="high",                 # How critical
    outcome_satisfaction="medium",             # Current satisfaction

    # Performance metrics
    duration_ms=duration,                      # How long
    success=success,                           # Did it work
    error_type=error_type if not success else None,

    # Context
    user_id=user_id,                           # Who (hashed for privacy)
    project_id=project_id,                     # What project
    tool_version=VERSION                       # Which version
)
def execute_command():
    pass
```

### Span Naming Convention

Use hierarchical naming for aggregation:

```
<domain>.<job>.<outcome>

Examples:
- ontology.validation.syntax_checked
- code_generation.ggen_sync.documentation_generated
- process_mining.discovery.model_extracted
- workflow.validation.deployment_verified
```

### Metrics to Collect

**Duration Metrics** (time-based outcomes):
```python
@timed
def minimize_time_outcome():
    # Automatically tracked:
    # - start_time
    # - end_time
    # - duration_ms
    pass
```

**Count Metrics** (quantity-based outcomes):
```python
@span("validation.errors_detected", error_count=len(errors))
def maximize_error_detection():
    # Track: Number of errors found
    pass
```

**Boolean Metrics** (success/failure outcomes):
```python
@span("deployment.validation", success=all_checks_passed)
def validate_deployment():
    # Track: Pass/fail status
    pass
```

**Distribution Metrics** (quality-based outcomes):
```python
@span(
    "documentation.generation",
    accuracy_score=accuracy,      # 0.0 - 1.0
    completeness_score=completeness,
    confidence_score=confidence
)
def generate_documentation():
    # Track: Quality dimensions
    pass
```

### Event Tracking

Track significant events for job lifecycle:

```python
from specify_cli.core.telemetry import event

# Job started
event("job.started", job_type="validate_ontology", persona="rdf_designer")

# Job progressing
event("job.progress", step="syntax_validation", progress=0.33)

# Job completed
event("job.completed", job_type="validate_ontology", outcome="syntax_validated", success=True)

# Job abandoned
event("job.abandoned", job_type="validate_ontology", reason="missing_dependency")
```

### Context Propagation

Propagate job context through call chains:

```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def high_level_job():
    with tracer.start_as_current_span("job.validate_ontology") as span:
        span.set_attribute("job.type", "validate_ontology")
        span.set_attribute("persona", "rdf_designer")

        # Child spans inherit context
        validate_syntax()    # Child span knows it's part of validation job
        validate_shacl()     # Can aggregate metrics by parent job
```

---

## Metrics Collection and Analysis

### Data Pipeline

```
User Action → OTEL Span → Collector → Storage → Analysis → Insights
```

**Components:**

1. **OTEL SDK**: Instrument code
2. **OTEL Collector**: Aggregate and export spans
3. **Storage**: Time-series database (Prometheus, InfluxDB) or OTEL backend (Jaeger, Zipkin)
4. **Analysis**: Query and aggregate metrics
5. **Visualization**: Dashboards (Grafana, custom)

### Key Queries

**Outcome Performance:**
```sql
-- Average time to validate RDF syntax (past 7 days)
SELECT
    AVG(duration_ms) as avg_duration,
    PERCENTILE(duration_ms, 50) as p50,
    PERCENTILE(duration_ms, 95) as p95,
    PERCENTILE(duration_ms, 99) as p99
FROM spans
WHERE span_name = 'ontology.validation.syntax_checked'
  AND timestamp > NOW() - INTERVAL 7 DAYS
```

**Job Success Rate:**
```sql
-- Success rate for "validate ontology" job (past 30 days)
SELECT
    COUNT(*) as total_attempts,
    SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as successful,
    SUM(CASE WHEN success = true THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as success_rate
FROM spans
WHERE job_type = 'validate_rdf_ontology'
  AND timestamp > NOW() - INTERVAL 30 DAYS
```

**Outcome Achievement by Persona:**
```sql
-- How well are we serving each persona?
SELECT
    persona,
    outcome,
    AVG(outcome_satisfaction) as avg_satisfaction,
    COUNT(*) as usage_count
FROM spans
WHERE timestamp > NOW() - INTERVAL 30 DAYS
GROUP BY persona, outcome
ORDER BY avg_satisfaction ASC  -- Lowest satisfaction first (needs attention)
```

**Baseline Comparison:**
```sql
-- Improvement vs. baseline
WITH baseline AS (
    SELECT 'validate_rdf_ontology' as job, 300000 as baseline_ms  -- 5 min manual
)
SELECT
    s.job_type,
    AVG(s.duration_ms) as current_avg_ms,
    b.baseline_ms,
    (b.baseline_ms - AVG(s.duration_ms))::FLOAT / b.baseline_ms * 100 as improvement_pct
FROM spans s
JOIN baseline b ON s.job_type = b.job
WHERE s.timestamp > NOW() - INTERVAL 7 DAYS
GROUP BY s.job_type, b.baseline_ms
```

### Dashboards

**Outcome Dashboard** (per persona):
- Current performance vs. baseline vs. target
- Trend over time (improving/degrading)
- Success rate
- Usage frequency

**Job Health Dashboard**:
- Jobs by success rate (lowest first)
- Jobs by satisfaction (lowest first)
- Jobs by usage frequency (most used)
- Error distribution by job type

**Feature Impact Dashboard**:
- Before/after feature deployment comparison
- Outcome improvement attribution
- Feature adoption rate
- ROI calculation (time saved × usage count)

---

## Interpreting Results

### Outcome Success Scoring

For each outcome, calculate success score:

```python
def calculate_outcome_success(
    current: float,
    baseline: float,
    target: float,
    direction: str  # "minimize" or "maximize"
) -> float:
    """
    Calculate outcome success score (0.0 to 1.0).

    Returns:
        0.0: No improvement vs. baseline
        0.5: Halfway to target
        1.0: Target achieved
        > 1.0: Exceeded target
    """
    if direction == "minimize":
        # Lower is better (e.g., time)
        if current >= baseline:
            return 0.0  # No improvement
        improvement = baseline - current
        total_possible = baseline - target
        return improvement / total_possible if total_possible > 0 else 1.0

    else:  # "maximize"
        # Higher is better (e.g., accuracy)
        if current <= baseline:
            return 0.0  # No improvement
        improvement = current - baseline
        total_possible = target - baseline
        return improvement / total_possible if total_possible > 0 else 1.0

# Example: "Minimize time to validate RDF"
score = calculate_outcome_success(
    current=10,       # 10 seconds current
    baseline=300,     # 5 minutes baseline
    target=1,         # 1 second target
    direction="minimize"
)
# Result: (300 - 10) / (300 - 1) = 0.97 (97% of ideal achieved)
```

### Satisfaction Scoring

Survey users on outcome satisfaction:

**Outcome Satisfaction Survey** (1-5 scale):

> **How satisfied are you with [outcome]?**
>
> When [performing job], how satisfied are you with the [metric] to [object of control]?
>
> Example: "When validating RDF ontology, how satisfied are you with the time it takes to detect syntax errors?"
>
> 1 = Very Dissatisfied
> 2 = Dissatisfied
> 3 = Neutral
> 4 = Satisfied
> 5 = Very Satisfied

**Importance vs. Satisfaction Matrix:**

| Importance | Satisfaction | Priority | Action |
|------------|-------------|----------|--------|
| High | Low | ⭐⭐⭐ Critical | Fix immediately |
| High | Medium | ⭐⭐ Important | Improve continuously |
| High | High | ⭐ Maintain | Keep quality high |
| Medium | Low | ⭐⭐ Address | Fix when feasible |
| Medium | Medium | Acceptable | Monitor |
| Medium | High | Excellent | Showcase |
| Low | Low | Low Priority | Deprioritize |
| Low | Medium | Low Priority | Consider removing |
| Low | High | Overserved | Simplify |

### Red Flags

**Performance Degradation:**
- Metric getting worse over time (regression)
- High variance (unpredictable performance)
- Success rate declining

**Low Adoption:**
- Feature exists but rarely used
- Competing manual workflows persist
- High abandonment rate

**Dissatisfaction:**
- Low satisfaction scores (< 3/5)
- High error rates
- Support tickets increasing

---

## Improving Outcome Delivery

### Improvement Process

**1. Identify Underperforming Outcomes**

Query for high-importance, low-satisfaction outcomes:

```sql
SELECT outcome, importance, satisfaction, usage_count
FROM outcome_metrics
WHERE importance = 'high' AND satisfaction < 3.0
ORDER BY usage_count DESC  -- High usage, low satisfaction = top priority
```

**2. Diagnose Root Causes**

Use OTEL traces to understand why outcome isn't being delivered:

```python
# Analyze failed job attempts
failed_attempts = query_spans(
    job_type="validate_rdf_ontology",
    success=False,
    limit=100
)

# Group by error type
error_distribution = Counter(span.error_type for span in failed_attempts)
# Result: {"missing_dependency": 45, "syntax_error": 30, "timeout": 25}

# Most common failure: missing dependencies
# Root cause: Users don't have tools installed
# Solution: Improve `specify check` guidance
```

**3. Design Improvement Hypotheses**

**Hypothesis Format:**
```
If we [change], then [outcome] will improve by [amount] because [reason].
```

**Example:**
```
If we add plain-English SHACL error explanations,
then "likelihood of detecting semantic errors" will improve by 20%
because users will understand errors and fix them correctly.
```

**4. Implement and Measure**

Deploy improvement with A/B testing where possible:

```python
@span("shacl.validation", variant="plain_english_errors")
def validate_shacl_with_improved_errors():
    # Track variant in OTEL
    # Compare outcome metrics between variants
    pass
```

**5. Validate Improvement**

Compare before/after metrics:

```sql
-- Before improvement (cohort: 2024-01-01 to 2024-01-31)
SELECT AVG(outcome_satisfaction)
FROM spans
WHERE job_type = 'validate_rdf_ontology'
  AND timestamp BETWEEN '2024-01-01' AND '2024-01-31'
-- Result: 2.8 (low satisfaction)

-- After improvement (cohort: 2024-02-01 to 2024-02-28)
SELECT AVG(outcome_satisfaction)
FROM spans
WHERE job_type = 'validate_rdf_ontology'
  AND timestamp BETWEEN '2024-02-01' AND '2024-02-28'
-- Result: 3.9 (improved by 39%)
```

**6. Iterate or Pivot**

- **Success**: Outcome improved significantly → Keep change, monitor
- **Partial Success**: Some improvement → Iterate on design
- **No Effect**: No change → Investigate assumptions, try different approach
- **Regression**: Worse → Roll back, diagnose

---

## Measurement Examples by Command

### Example 1: `ggen sync`

**Job:** Generate documentation from RDF
**Outcome:** Minimize time to generate documentation

**Baseline Measurement:**
```python
# Manual documentation writing (before ggen)
baseline_duration = timedelta(minutes=30)  # From user studies
```

**Current Measurement:**
```python
@timed
@span(
    "ggen.sync",
    job="generate_documentation",
    outcome="minimize_generation_time",
    baseline_ms=1_800_000,  # 30 min
    target_ms=5_000         # 5 sec
)
def ggen_sync(config: Path) -> SyncResult:
    # OTEL automatically tracks duration
    pass
```

**Analysis Query:**
```sql
-- Current performance vs. baseline
SELECT
    AVG(duration_ms) as current_avg,
    1800000 as baseline,
    5000 as target,
    (1800000 - AVG(duration_ms))::FLOAT / (1800000 - 5000) * 100 as success_pct
FROM spans
WHERE span_name = 'ggen.sync'
  AND timestamp > NOW() - INTERVAL 7 DAYS
```

**Result Interpretation:**
- Current avg: 4,200ms (4.2 seconds)
- Success score: 99.7% (nearly ideal)
- **Action**: Maintain performance, monitor for regressions

---

### Example 2: `specify check`

**Job:** Verify tool ecosystem health
**Outcome:** Minimize time to diagnose missing dependencies

**Baseline Measurement:**
```python
# Manual checking before `specify check`
baseline_duration = timedelta(minutes=15)  # Trial-and-error
```

**Current Measurement:**
```python
@timed
@span(
    "dependency.check",
    job="verify_tool_health",
    outcome="minimize_diagnosis_time",
    tools_checked=len(tools),
    tools_missing=len(missing),
    baseline_ms=900_000,  # 15 min
    target_ms=10_000      # 10 sec
)
def check_dependencies() -> CheckResult:
    pass
```

**Analysis Query:**
```sql
-- How well are we detecting issues?
SELECT
    AVG(duration_ms) as avg_check_time,
    AVG(tools_missing) as avg_missing_tools,
    SUM(CASE WHEN tools_missing > 0 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as issue_detection_rate
FROM spans
WHERE span_name = 'dependency.check'
  AND timestamp > NOW() - INTERVAL 30 DAYS
```

**Result Interpretation:**
- Avg check time: 8,500ms (8.5 sec)
- Avg missing tools: 1.2
- Issue detection rate: 35% (35% of runs find issues)
- **Action**: Excellent performance, high value (catching issues early)

---

### Example 3: `pm discover`

**Job:** Discover process patterns from logs
**Outcome:** Minimize time to extract process model

**Baseline Measurement:**
```python
# Manual process modeling before pm4py
baseline_duration = timedelta(hours=2)  # From analyst interviews
```

**Current Measurement:**
```python
@timed
@span(
    "pm.discover",
    job="discover_process_patterns",
    outcome="minimize_discovery_time",
    event_count=len(events),
    algorithm=algorithm,
    baseline_ms=7_200_000,  # 2 hours
    target_ms=60_000        # 1 min
)
def discover_process(log_file: Path, algorithm: str) -> ProcessModel:
    pass
```

**Analysis Query:**
```sql
-- Performance by algorithm
SELECT
    algorithm,
    AVG(duration_ms) as avg_time,
    AVG(event_count) as avg_events,
    AVG(duration_ms) / AVG(event_count) as ms_per_event
FROM spans
WHERE span_name = 'pm.discover'
  AND timestamp > NOW() - INTERVAL 30 DAYS
GROUP BY algorithm
ORDER BY avg_time ASC
```

**Result Interpretation:**
| Algorithm | Avg Time | Avg Events | ms/event |
|-----------|----------|------------|----------|
| Inductive | 45,000ms | 50,000 | 0.9 |
| Heuristic | 52,000ms | 50,000 | 1.04 |
| Alpha | 38,000ms | 50,000 | 0.76 |

- **Action**: Inductive is good default (balances speed and quality)
- All algorithms meet target (< 1 min for typical logs)
- Success score: ~99% of ideal achieved

---

### Example 4: `wf validate`

**Job:** Validate deployment readiness
**Outcome:** Maximize confidence in production health

**Baseline Measurement:**
```python
# Manual validation checklist
baseline_confidence = 2.5  # Survey: 1-5 scale, avg 2.5 before automation
```

**Current Measurement:**
```python
@span(
    "workflow.validation",
    job="validate_deployment",
    outcome="maximize_deployment_confidence",
    checks_passed=passed,
    checks_failed=failed,
    baseline_confidence=2.5,
    target_confidence=4.5
)
def validate_deployment() -> ValidationReport:
    # Also survey users: "How confident are you in deployment after validation?"
    pass
```

**Analysis Query:**
```sql
-- Validation success rates
SELECT
    AVG(checks_passed) as avg_passed,
    AVG(checks_failed) as avg_failed,
    AVG(checks_passed)::FLOAT / (AVG(checks_passed) + AVG(checks_failed)) as pass_rate
FROM spans
WHERE span_name = 'workflow.validation'
  AND timestamp > NOW() - INTERVAL 30 DAYS
```

**Survey Results:**
- Current confidence: 4.2/5
- Baseline: 2.5/5
- Target: 4.5/5
- Success score: (4.2 - 2.5) / (4.5 - 2.5) = 85%

**Action**: Good progress, identify why not yet at 4.5 (investigate failures)

---

## Summary

### Measurement Best Practices

1. **Define measurable outcomes** before implementing features
2. **Establish baselines** to measure improvement against
3. **Instrument with OTEL** for automatic, continuous measurement
4. **Track both performance and satisfaction** (objective + subjective)
5. **Analyze trends** not just point-in-time metrics
6. **Use importance-satisfaction matrix** to prioritize improvements
7. **A/B test** improvements when possible
8. **Close the loop** from measurement → insight → action → measurement

### Key Metrics by Outcome Type

| Outcome Type | Metrics | Example |
|--------------|---------|---------|
| **Time-based** | Duration (p50, p95, p99), trend | Time to validate RDF |
| **Accuracy-based** | Precision, recall, F1 score | Error detection rate |
| **Confidence-based** | Survey score (1-5), NPS | Deployment confidence |
| **Effort-based** | Steps, clicks, commands | Validation steps required |
| **Quality-based** | Completeness, consistency scores | Documentation quality |

### The Measurement Loop

```
1. Identify outcome
2. Measure baseline
3. Set target
4. Instrument feature
5. Deploy and measure
6. Analyze results
7. Identify improvements
8. Implement and measure again
```

This loop runs continuously, ensuring we're always improving outcome delivery.

---

**Next Steps:**
- [Getting Started with JTBD](./getting-started.md) - Tutorial for applying JTBD
- [Examples](./examples.md) - Complete worked examples
- [Jobs & Outcomes Catalog](./jobs-outcomes-catalog.md) - Full outcome inventory
