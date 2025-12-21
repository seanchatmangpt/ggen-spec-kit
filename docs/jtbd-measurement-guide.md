# JTBD Measurement Guide

**Jobs-to-be-Done (JTBD) Metrics Collection and Analysis Framework for spec-kit**

This guide explains how to use the JTBD measurement framework to track outcome delivery, measure feature effectiveness, and drive outcome-driven product development.

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Metrics Collection](#metrics-collection)
4. [Data Analysis](#data-analysis)
5. [Reporting](#reporting)
6. [Integration with OpenTelemetry](#integration-with-opentelemetry)
7. [Best Practices](#best-practices)
8. [Examples](#examples)

---

## Overview

The JTBD measurement framework enables you to:

- **Track job completions** by user persona
- **Measure outcome achievement** against success criteria
- **Monitor painpoint resolution** across features
- **Calculate time-to-outcome** for customer journeys
- **Collect user satisfaction** scores and feedback

All metrics integrate seamlessly with OpenTelemetry for distributed tracing and analysis.

### Why JTBD Metrics Matter

Traditional feature-based metrics ("How many users clicked X?") don't tell you if users achieved their goals. JTBD metrics focus on **outcomes**:

- ✅ "Did the user achieve faster dependency management?"
- ✅ "Did we eliminate the manual effort painpoint?"
- ✅ "How long did it take to complete the job?"

This shifts focus from **outputs** (features shipped) to **outcomes** (customer value delivered).

---

## Core Concepts

### Jobs

A **job** is a high-level task the user wants to accomplish.

Examples:
- "Add a Python dependency to my project"
- "Generate documentation from RDF specs"
- "Validate my workflow definition"

### Outcomes

An **outcome** is a measurable result the user wants to achieve.

Examples:
- "Save 30+ seconds on dependency management"
- "Achieve 80%+ test coverage"
- "Reduce manual errors to zero"

### Painpoints

A **painpoint** is a specific problem/frustration users experience.

Categories:
- `TIME_WASTED` - Inefficient processes
- `COGNITIVE_LOAD` - Mental complexity
- `MANUAL_EFFORT` - Repetitive tasks
- `ERROR_PRONE` - Quality/reliability issues
- `LACK_OF_CONTROL` - Limited flexibility
- `LACK_OF_VISIBILITY` - Poor observability
- `INTEGRATION_FRICTION` - Tool compatibility
- `LEARNING_CURVE` - Difficulty to learn

### Personas

A **persona** is a user archetype with specific needs.

Examples:
- `python-developer` - Building Python applications
- `devops-engineer` - Managing infrastructure
- `data-scientist` - Analyzing data workflows
- `technical-writer` - Creating documentation

---

## Metrics Collection

### 1. Job Completion Tracking

Track which jobs users complete with your features.

```python
from specify_cli.core.jtbd_metrics import (
    JobCompletion,
    JobStatus,
    track_job_completion,
)

# Start a job
job = JobCompletion(
    job_id="deps-add",
    persona="python-developer",
    feature_used="specify deps add",
    context={"package": "httpx", "group": "main"}
)

# ... perform the job ...

# Complete the job
job.complete()
track_job_completion(job)
```

**Tracked Attributes:**
- `jtbd.job.id` - Job identifier
- `jtbd.job.persona` - User persona
- `jtbd.job.feature` - Feature used
- `jtbd.job.status` - Completion status
- `jtbd.job.duration_seconds` - Time to complete

### 2. Outcome Achievement Tracking

Measure whether features deliver promised outcomes.

```python
from specify_cli.core.jtbd_metrics import (
    OutcomeAchieved,
    track_outcome_achieved,
)

outcome = OutcomeAchieved(
    outcome_id="faster-dependency-management",
    metric="time_saved_seconds",
    expected_value=30.0,   # Expected to save 30+ seconds
    actual_value=8.5,      # Actually saved 8.5 seconds
    feature="specify deps add",
    persona="python-developer"
)

track_outcome_achieved(outcome)

# Check achievement
print(f"Achievement rate: {outcome.achievement_rate}%")
print(f"Exceeds expectations: {outcome.exceeds_expectations}")
```

**Tracked Attributes:**
- `jtbd.outcome.id` - Outcome identifier
- `jtbd.outcome.metric` - Metric being measured
- `jtbd.outcome.expected` - Expected value
- `jtbd.outcome.actual` - Actual value achieved
- `jtbd.outcome.achievement_rate` - Percentage achieved
- `jtbd.outcome.exceeds_expectations` - Boolean flag

### 3. Painpoint Resolution Tracking

Track which painpoints your features resolve.

```python
from specify_cli.core.jtbd_metrics import (
    PainpointCategory,
    PainpointResolved,
    track_painpoint_resolved,
)

painpoint = PainpointResolved(
    painpoint_id="manual-dependency-updates",
    category=PainpointCategory.MANUAL_EFFORT,
    description="Manually updating pyproject.toml",
    feature="specify deps add",
    persona="python-developer",
    severity_before=8,  # 1-10 scale
    severity_after=2,   # 1-10 scale
)

track_painpoint_resolved(painpoint)

# Check effectiveness
print(f"Resolution effectiveness: {painpoint.resolution_effectiveness}%")
```

**Tracked Attributes:**
- `jtbd.painpoint.id` - Painpoint identifier
- `jtbd.painpoint.category` - Painpoint category
- `jtbd.painpoint.severity_before` - Severity before (1-10)
- `jtbd.painpoint.severity_after` - Severity after (1-10)
- `jtbd.painpoint.resolution_effectiveness` - Effectiveness %

### 4. Time-to-Outcome Measurement

Measure how long it takes users to achieve outcomes.

```python
from specify_cli.core.jtbd_metrics import (
    TimeToOutcome,
    track_time_to_outcome,
)

# Start measuring
tto = TimeToOutcome(
    outcome_id="dependency-added",
    persona="python-developer",
    feature="specify deps add"
)

# Track steps
tto.add_step("parse_args")
tto.add_step("validate_package")
tto.add_step("update_pyproject")
tto.add_step("install_package")

# Complete measurement
tto.complete()
track_time_to_outcome(tto)

print(f"Time to outcome: {tto.duration_seconds}s")
print(f"Steps: {len(tto.steps)}")
```

**Tracked Attributes:**
- `jtbd.tto.outcome_id` - Outcome identifier
- `jtbd.tto.duration_seconds` - Total time
- `jtbd.tto.steps_count` - Number of steps
- `jtbd.tto.step_N` - Individual step names

### 5. User Satisfaction Tracking

Collect user satisfaction with outcome delivery.

```python
from specify_cli.core.jtbd_metrics import (
    SatisfactionLevel,
    UserSatisfaction,
    track_user_satisfaction,
)

satisfaction = UserSatisfaction(
    outcome_id="faster-dependency-management",
    feature="specify deps add",
    persona="python-developer",
    satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
    met_expectations=True,
    would_recommend=True,
    effort_score=2,  # 1-7, lower is better
    feedback_text="So much faster than pip!"
)

track_user_satisfaction(satisfaction)
```

**Tracked Attributes:**
- `jtbd.satisfaction.level` - Satisfaction level (1-5 scale)
- `jtbd.satisfaction.met_expectations` - Boolean
- `jtbd.satisfaction.would_recommend` - Boolean (NPS)
- `jtbd.satisfaction.effort_score` - Customer Effort Score (1-7)

---

## Data Analysis

### Extracting Metrics from Traces

Extract JTBD metrics from OpenTelemetry trace data:

```python
from specify_cli.core.jtbd_measurement import extract_jtbd_metrics

# Load trace data (e.g., from OTEL collector)
trace_data = load_traces_from_otel()

# Extract metrics
metrics = extract_jtbd_metrics(trace_data)

print(f"Jobs completed: {len(metrics.job_completions)}")
print(f"Outcomes achieved: {len(metrics.outcome_achievements)}")
print(f"Painpoints resolved: {len(metrics.painpoint_resolutions)}")
```

### Analyzing Outcome Delivery

Analyze how well features deliver promised outcomes:

```python
from specify_cli.core.jtbd_measurement import analyze_outcome_delivery

# Analyze all outcomes
analysis = analyze_outcome_delivery(metrics)

for outcome_id, result in analysis.items():
    print(f"\n{outcome_id}:")
    print(f"  Delivery Rate: {result.delivery_rate}%")
    print(f"  Avg Achievement: {result.avg_achievement_rate}%")
    print(f"  Avg Time: {result.avg_time_to_outcome}s")
    print(f"  Exceeds Expectations: {result.exceeds_expectations_count} times")

# Filter by persona
python_dev_analysis = analyze_outcome_delivery(
    metrics,
    persona="python-developer"
)

# Filter by specific outcome
fast_deps_analysis = analyze_outcome_delivery(
    metrics,
    outcome_id="faster-dependency-management"
)
```

### Analyzing Feature Effectiveness

Calculate ROI and effectiveness scores for features:

```python
from specify_cli.core.jtbd_measurement import analyze_feature_effectiveness

effectiveness = analyze_feature_effectiveness(metrics)

# Sort by effectiveness score
ranked_features = sorted(
    effectiveness.items(),
    key=lambda x: x[1].effectiveness_score,
    reverse=True
)

for feature, eff in ranked_features:
    print(f"\n{feature}:")
    print(f"  Effectiveness Score: {eff.effectiveness_score:.1f}/100")
    print(f"  Outcomes Delivered: {eff.outcomes_delivered}")
    print(f"  Painpoints Resolved: {eff.painpoints_resolved}")
    print(f"  Avg Satisfaction: {eff.avg_satisfaction:.2f}/5.0")
    print(f"  Recommendation Rate: {eff.recommendation_rate}%")
```

**Effectiveness Score Formula:**
```
Score = (Outcome Delivery × 0.4) +
        (User Satisfaction × 0.3) +
        (Painpoint Resolution × 0.2) +
        (Low Effort × 0.1)
```

### Querying Specific Metrics

Query specific metric types with filters:

```python
from specify_cli.core.jtbd_measurement import (
    query_job_completions,
    query_outcome_achievements,
    query_painpoint_resolutions,
)

# Query job completions
jobs = query_job_completions(
    trace_data,
    persona="python-developer",
    status=JobStatus.COMPLETED
)

# Query outcomes with high achievement rates
high_performers = query_outcome_achievements(
    trace_data,
    min_achievement_rate=80.0
)

# Query painpoint resolutions by category
manual_effort_fixes = query_painpoint_resolutions(
    trace_data,
    category=PainpointCategory.MANUAL_EFFORT,
    min_effectiveness=70.0
)
```

---

## Reporting

### Exporting Metrics

Export metrics to JSON or CSV for analysis:

```python
from specify_cli.core.jtbd_measurement import export_metrics

# Export to JSON
export_metrics(metrics, "jtbd_metrics.json", format="json")

# Export to CSV (creates multiple files)
export_metrics(metrics, "jtbd_metrics.csv", format="csv")
# Creates:
# - jtbd_metrics_job_completions.csv
# - jtbd_metrics_outcomes.csv
# - jtbd_metrics_painpoints.csv
```

### Generating Reports

Generate comprehensive JTBD reports:

```python
from specify_cli.core.jtbd_measurement import generate_jtbd_report

generate_jtbd_report(metrics, "jtbd_report.md")
```

**Report Includes:**
- Summary statistics
- Outcome delivery analysis per outcome
- Feature effectiveness rankings
- Top performing features
- Personas served

---

## Integration with OpenTelemetry

### Automatic Instrumentation

All JTBD tracking functions automatically integrate with OpenTelemetry:

```python
from specify_cli.core.telemetry import span
from specify_cli.core.jtbd_metrics import (
    JobCompletion,
    track_job_completion,
)

# Your code already creates spans
with span("deps.add", feature="specify deps add"):
    # Track JTBD metrics within the span
    job = JobCompletion(
        job_id="deps-add",
        persona="python-developer",
        feature_used="specify deps add"
    )

    # ... do the work ...

    job.complete()
    track_job_completion(job)

    # JTBD attributes are added to the current span
```

### Custom Attributes

JTBD metrics add semantic attributes to spans:

```yaml
Span: cli.command.deps_add
Attributes:
  # Standard CLI attributes
  cli.command: "deps add"
  cli.args.count: 2

  # JTBD attributes (automatically added)
  jtbd.job.id: "deps-add"
  jtbd.job.persona: "python-developer"
  jtbd.job.feature: "specify deps add"
  jtbd.job.status: "completed"
  jtbd.job.duration_seconds: 8.5

  jtbd.outcome.id: "faster-dependency-management"
  jtbd.outcome.achievement_rate: 28.3
  jtbd.outcome.exceeds_expectations: false
```

### Span Events

JTBD tracking creates structured events:

```yaml
Events:
  - name: "job_completed"
    timestamp: "2024-01-15T10:30:00Z"
    attributes:
      jtbd.job.id: "deps-add"
      jtbd.job.status: "completed"

  - name: "outcome_achieved"
    timestamp: "2024-01-15T10:30:00Z"
    attributes:
      jtbd.outcome.id: "faster-dependency-management"
      jtbd.outcome.achievement_rate: 28.3

  - name: "painpoint_resolved"
    timestamp: "2024-01-15T10:30:00Z"
    attributes:
      jtbd.painpoint.category: "manual_effort"
      jtbd.painpoint.resolution_effectiveness: 75.0
```

### Metrics

JTBD tracking creates OpenTelemetry metrics:

**Counters:**
- `jtbd.job.{job_id}.completions` - Job completion count
- `jtbd.outcome.{outcome_id}.achievements` - Outcome achievement count
- `jtbd.painpoint.resolutions` - Painpoint resolution count
- `jtbd.satisfaction.{outcome_id}.responses` - Satisfaction response count

**Histograms:**
- `jtbd.job.{job_id}.duration` - Job completion time distribution
- `jtbd.outcome.{outcome_id}.achievement_rate` - Achievement rate distribution
- `jtbd.painpoint.effectiveness` - Resolution effectiveness distribution
- `jtbd.tto.{outcome_id}.duration` - Time-to-outcome distribution
- `jtbd.satisfaction.effort_score` - Customer effort score distribution

---

## Best Practices

### 1. Define Clear Outcomes

❌ **Vague:** "Better user experience"
✅ **Clear:** "Reduce dependency setup time by 30+ seconds"

❌ **Vague:** "Improved quality"
✅ **Clear:** "Achieve 80%+ test coverage with zero manual steps"

### 2. Measure from User Perspective

Track what users **achieve**, not what features **do**:

```python
# ❌ Feature-centric
track_feature_usage("deps add", clicks=1)

# ✅ Outcome-centric
outcome = OutcomeAchieved(
    outcome_id="faster-dependency-management",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=8.5,
    feature="specify deps add"
)
track_outcome_achieved(outcome)
```

### 3. Track Complete Journeys

Measure the **entire** customer journey, not just individual steps:

```python
# Track the full time-to-outcome
tto = TimeToOutcome(
    outcome_id="dependency-added",
    persona="python-developer",
    feature="specify deps add"
)

# Track each step in the journey
tto.add_step("discover_package")
tto.add_step("decide_to_add")
tto.add_step("run_command")
tto.add_step("verify_installation")

tto.complete()
track_time_to_outcome(tto)
```

### 4. Collect Qualitative Feedback

Combine quantitative metrics with qualitative insights:

```python
satisfaction = UserSatisfaction(
    outcome_id="faster-dependency-management",
    feature="specify deps add",
    persona="python-developer",
    satisfaction_level=SatisfactionLevel.SATISFIED,
    met_expectations=True,
    would_recommend=True,
    effort_score=3,
    # ✅ Capture the "why"
    feedback_text="Fast but confusing error messages"
)
```

### 5. Segment by Persona

Different personas have different needs and outcomes:

```python
# Track outcomes separately for each persona
python_dev_outcome = OutcomeAchieved(
    outcome_id="faster-dependency-management",
    persona="python-developer",  # ✅ Segment by persona
    ...
)

devops_outcome = OutcomeAchieved(
    outcome_id="automated-deployment",
    persona="devops-engineer",  # ✅ Different persona, different outcome
    ...
)
```

### 6. Set Realistic Expectations

Base expected values on user research and benchmarks:

```python
# ❌ Arbitrary target
OutcomeAchieved(
    expected_value=100.0,  # Based on nothing
    actual_value=8.5
)

# ✅ Research-based target
OutcomeAchieved(
    # Based on: "Manual process takes 30-45s on average"
    expected_value=30.0,
    actual_value=8.5
)
```

### 7. Analyze Trends Over Time

Track how outcome delivery improves:

```python
# Query outcomes for a specific time period
recent_outcomes = query_outcome_achievements(
    trace_data,
    outcome_id="faster-dependency-management"
)

# Calculate trends
weekly_achievement_rates = calculate_weekly_trends(recent_outcomes)

# Identify improvements or regressions
if this_week_rate < last_week_rate:
    print("⚠️  Outcome delivery regressed!")
```

---

## Examples

### Example 1: Complete JTBD Flow

```python
from specify_cli.core.jtbd_metrics import *
from specify_cli.core.telemetry import span

def add_dependency(package: str, persona: str = "python-developer"):
    """Add a dependency with complete JTBD tracking."""

    # 1. Start job tracking
    job = JobCompletion(
        job_id="deps-add",
        persona=persona,
        feature_used="specify deps add",
        context={"package": package}
    )

    # 2. Start time-to-outcome tracking
    tto = TimeToOutcome(
        outcome_id="dependency-added",
        persona=persona,
        feature="specify deps add"
    )

    with span("deps.add", package=package):
        try:
            # 3. Perform the job
            tto.add_step("validate_package")
            validate_package(package)

            tto.add_step("update_pyproject")
            update_pyproject_toml(package)

            tto.add_step("install_package")
            install_package(package)

            # 4. Complete job
            job.complete()
            track_job_completion(job)

            # 5. Track outcome achievement
            outcome = OutcomeAchieved(
                outcome_id="faster-dependency-management",
                metric="time_saved_seconds",
                expected_value=30.0,
                actual_value=job.duration_seconds or 0.0,
                feature="specify deps add",
                persona=persona
            )
            track_outcome_achieved(outcome)

            # 6. Track painpoint resolution
            painpoint = PainpointResolved(
                painpoint_id="manual-dependency-updates",
                category=PainpointCategory.MANUAL_EFFORT,
                description="Manually updating pyproject.toml",
                feature="specify deps add",
                persona=persona,
                severity_before=8,
                severity_after=2
            )
            track_painpoint_resolved(painpoint)

            # 7. Complete time-to-outcome
            tto.complete()
            track_time_to_outcome(tto)

            # 8. Collect satisfaction (optional - via feedback prompt)
            satisfaction = UserSatisfaction(
                outcome_id="faster-dependency-management",
                feature="specify deps add",
                persona=persona,
                satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
                met_expectations=True,
                would_recommend=True,
                effort_score=2
            )
            track_user_satisfaction(satisfaction)

        except Exception as e:
            job.fail(reason=str(e))
            track_job_completion(job)
            raise
```

### Example 2: Analyzing Feature ROI

```python
from specify_cli.core.jtbd_measurement import (
    extract_jtbd_metrics,
    analyze_feature_effectiveness,
)

# Load traces from OTEL
trace_data = load_traces()

# Extract metrics
metrics = extract_jtbd_metrics(trace_data)

# Analyze feature effectiveness
effectiveness = analyze_feature_effectiveness(metrics)

# Identify top performers
top_features = sorted(
    effectiveness.items(),
    key=lambda x: x[1].effectiveness_score,
    reverse=True
)[:5]

print("🏆 Top 5 Features by Effectiveness:\n")
for rank, (feature, eff) in enumerate(top_features, 1):
    print(f"{rank}. {feature}")
    print(f"   Score: {eff.effectiveness_score:.1f}/100")
    print(f"   Outcomes: {eff.outcomes_delivered}")
    print(f"   Satisfaction: {eff.avg_satisfaction:.2f}/5.0")
    print(f"   NPS: {eff.recommendation_rate}%")
    print()

# Identify underperformers
underperformers = [
    (feature, eff)
    for feature, eff in effectiveness.items()
    if eff.effectiveness_score < 50.0
]

if underperformers:
    print("⚠️  Features Needing Improvement:\n")
    for feature, eff in underperformers:
        print(f"- {feature}: {eff.effectiveness_score:.1f}/100")
```

### Example 3: Dashboard Queries

Use these queries to build dashboards in Grafana, Datadog, etc.

**Outcome Delivery Rate (Last 7 Days):**
```sql
SELECT
    outcome_id,
    COUNT(*) as total_attempts,
    SUM(CASE WHEN status = 'achieved' THEN 1 ELSE 0 END) as successes,
    (SUM(CASE WHEN status = 'achieved' THEN 1 ELSE 0 END) / COUNT(*)) * 100 as delivery_rate
FROM jtbd_outcomes
WHERE timestamp > NOW() - INTERVAL '7 days'
GROUP BY outcome_id
ORDER BY delivery_rate DESC;
```

**Average Time-to-Outcome by Persona:**
```sql
SELECT
    persona,
    outcome_id,
    AVG(duration_seconds) as avg_duration,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_seconds) as median_duration
FROM jtbd_time_to_outcome
GROUP BY persona, outcome_id
ORDER BY avg_duration ASC;
```

**Top Painpoints Resolved:**
```sql
SELECT
    painpoint_category,
    COUNT(*) as resolution_count,
    AVG(resolution_effectiveness) as avg_effectiveness
FROM jtbd_painpoints
WHERE resolution_effectiveness > 70
GROUP BY painpoint_category
ORDER BY resolution_count DESC;
```

---

## Summary

The JTBD measurement framework helps you:

✅ **Shift from outputs to outcomes** - Focus on customer value, not feature counts
✅ **Measure what matters** - Track job completion, outcome delivery, and satisfaction
✅ **Drive product decisions** - Use data to prioritize high-impact features
✅ **Validate feature ROI** - Calculate effectiveness scores and identify winners
✅ **Close the feedback loop** - Continuously improve based on actual outcomes

**Next Steps:**

1. Define jobs, outcomes, and painpoints for your features
2. Instrument your code with JTBD tracking calls
3. Collect metrics via OpenTelemetry
4. Analyze data to identify high-impact improvements
5. Iterate based on outcome delivery rates

For questions or support, see the [main spec-kit documentation](../README.md).
