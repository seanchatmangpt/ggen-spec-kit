# JTBD User Guide - Jobs-to-be-Done Metrics Framework

**Version:** 1.0.0
**Last Updated:** 2025-12-21
**Framework:** Jobs-to-be-Done (Clayton Christensen)

## Overview

The JTBD (Jobs-to-be-Done) metrics framework provides comprehensive tracking of customer outcomes, measuring:

- Job completion rates by persona
- Outcome achievement metrics
- Painpoint resolution tracking
- Time-to-outcome measurements
- User satisfaction scores

All metrics integrate with OpenTelemetry for distributed tracing across the customer journey.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core Concepts](#core-concepts)
3. [Tracking Jobs](#tracking-jobs)
4. [Measuring Outcomes](#measuring-outcomes)
5. [Analyzing Painpoints](#analyzing-painpoints)
6. [Time-to-Outcome](#time-to-outcome)
7. [User Satisfaction](#user-satisfaction)
8. [Configuration](#configuration)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

The JTBD framework is included in spec-kit. No additional installation required.

```bash
# Install spec-kit
uv sync

# Verify JTBD module is available
python -c "from specify_cli.core.jtbd_metrics import JobCompletion; print('JTBD Ready')"
```

### Quick Start Example

```python
from specify_cli.core.jtbd_metrics import (
    JobCompletion,
    OutcomeAchieved,
    track_job_completion,
    track_outcome_achieved,
)

# Track a job completion
job = JobCompletion(
    job_id="deps-add",
    persona="python-developer",
    feature_used="specify deps add",
    context={"package": "httpx"}
)
job.complete()
track_job_completion(job)

# Track outcome achievement
outcome = OutcomeAchieved(
    outcome_id="faster-dependency-management",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=8.5,
    feature="specify deps add"
)
track_outcome_achieved(outcome)
```

### Enable OpenTelemetry (Optional)

```bash
# Set OTEL endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

# Run with OTEL enabled
specify deps add httpx

# View traces in your OTEL backend (Jaeger, Zipkin, etc.)
```

---

## Core Concepts

### Jobs-to-be-Done Framework

**Job**: A high-level task the user wants to accomplish (e.g., "add dependency", "validate RDF specs").

**Outcome**: A measurable result the user wants (e.g., "faster dependency management", "higher code quality").

**Painpoint**: A specific problem/frustration preventing job completion (e.g., "manual pyproject.toml editing").

**Persona**: Representative user archetype based on job circumstances, not demographics.

### The JTBD Metric Categories

| Category | What It Measures | Example |
|----------|------------------|---------|
| **Job Completion** | Which jobs are completed | "deps-add" completed by "python-developer" |
| **Outcome Achievement** | Desired results achieved | "30s time saved" vs "8.5s actual" |
| **Painpoint Resolution** | Problems eliminated | "Manual editing" reduced from 8/10 to 2/10 severity |
| **Time-to-Outcome** | Speed to achieve outcome | "2.3 seconds from command to success" |
| **User Satisfaction** | Expectation fulfillment | "Very Satisfied" + "Would Recommend" |

---

## Tracking Jobs

### Job Completion Lifecycle

```python
from specify_cli.core.jtbd_metrics import JobCompletion, JobStatus, track_job_completion

# 1. Start a job
job = JobCompletion(
    job_id="validate-rdf",
    persona="backend-developer",
    feature_used="specify ggen validate-rdf",
    context={
        "file": "ontology/schema.ttl",
        "format": "turtle"
    }
)
# Status: STARTED

# 2. Job in progress (optional)
job.status = JobStatus.IN_PROGRESS

# 3. Complete successfully
job.complete()  # Sets status=COMPLETED, calculates duration
track_job_completion(job)

# OR fail
job.fail(reason="Invalid RDF syntax")
track_job_completion(job)
```

### Job Statuses

| Status | Meaning | When to Use |
|--------|---------|-------------|
| `STARTED` | Job initiated | Default on creation |
| `IN_PROGRESS` | Actively working | Optional interim state |
| `COMPLETED` | Successful completion | Call `job.complete()` |
| `FAILED` | Job failed | Call `job.fail(reason)` |
| `ABANDONED` | User quit early | User canceled with Ctrl+C |

### Tracking Multiple Jobs

```python
from specify_cli.core.jtbd_metrics import JobCompletion, track_job_completion

# Track concurrent jobs
jobs = [
    JobCompletion(
        job_id="init-project",
        persona="python-developer",
        feature_used="specify init",
        context={"project_name": "my-app"}
    ),
    JobCompletion(
        job_id="add-dependencies",
        persona="python-developer",
        feature_used="specify deps add",
        context={"packages": ["httpx", "pydantic"]}
    ),
]

for job in jobs:
    job.complete()
    track_job_completion(job)
```

### Job Context (Additional Data)

```python
# Rich context for analytics
job = JobCompletion(
    job_id="generate-docs",
    persona="technical-writer",
    feature_used="specify ggen sync",
    context={
        "template": "philosophy.tera",
        "input_file": "memory/philosophy.ttl",
        "output_file": "docs/spec-driven.md",
        "file_size_kb": 45,
        "num_transformations": 1
    }
)
```

---

## Measuring Outcomes

### Outcome Achievement

```python
from specify_cli.core.jtbd_metrics import OutcomeAchieved, OutcomeStatus, track_outcome_achieved

outcome = OutcomeAchieved(
    outcome_id="faster-dependency-management",
    metric="time_saved_seconds",
    expected_value=30.0,      # Expected to save 30s
    actual_value=8.5,         # Actually saved 8.5s
    feature="specify deps add",
    persona="python-developer",
    context={"package": "httpx", "method": "uv"}
)

# Calculate achievement rate
print(f"Achievement: {outcome.achievement_rate}%")  # 28.3%

# Check if exceeded expectations
print(f"Exceeded: {outcome.exceeds_expectations}")  # False

# Determine status
status = outcome.determine_status()
print(f"Status: {status}")  # IN_PROGRESS (achieved 28%, need 100%)

track_outcome_achieved(outcome)
```

### Outcome Status Thresholds

| Status | Achievement Rate | Meaning |
|--------|------------------|---------|
| `ACHIEVED` | ≥ 100% | Fully met expectations |
| `PARTIALLY_ACHIEVED` | 75-99% | Nearly met expectations |
| `IN_PROGRESS` | 1-74% | Making progress |
| `NOT_ACHIEVED` | 0% | No progress |
| `NOT_STARTED` | N/A | Not yet measured |

### Outcome Metrics (Common)

```python
# Time savings
OutcomeAchieved(
    outcome_id="faster-builds",
    metric="time_saved_seconds",
    expected_value=120.0,
    actual_value=95.0,
    feature="uv build"
)

# Error reduction
OutcomeAchieved(
    outcome_id="fewer-type-errors",
    metric="error_reduction_percent",
    expected_value=90.0,
    actual_value=85.0,
    feature="mypy strict mode"
)

# Quality improvement
OutcomeAchieved(
    outcome_id="higher-coverage",
    metric="coverage_increase_percent",
    expected_value=10.0,
    actual_value=15.0,  # Exceeded!
    feature="pytest --cov"
)

# Throughput improvement
OutcomeAchieved(
    outcome_id="faster-tests",
    metric="tests_per_second",
    expected_value=5.0,
    actual_value=8.2,
    feature="pytest-xdist"
)
```

---

## Analyzing Painpoints

### Painpoint Resolution Tracking

```python
from specify_cli.core.jtbd_metrics import (
    PainpointResolved,
    PainpointCategory,
    track_painpoint_resolved,
)

painpoint = PainpointResolved(
    painpoint_id="manual-dependency-updates",
    category=PainpointCategory.MANUAL_EFFORT,
    description="Manually editing pyproject.toml for each dependency",
    feature="specify deps add",
    persona="python-developer",
    severity_before=8,  # High pain (1-10 scale)
    severity_after=2,   # Low pain after feature
    context={
        "frequency": "daily",
        "time_cost_minutes": 5
    }
)

# Resolution effectiveness calculated automatically
print(f"Effectiveness: {painpoint.resolution_effectiveness}%")  # 75%

track_painpoint_resolved(painpoint)
```

### Painpoint Categories

| Category | Description | Example |
|----------|-------------|---------|
| `TIME_WASTED` | Inefficient processes | Manual copy-paste workflows |
| `COGNITIVE_LOAD` | Mental complexity | Remembering complex commands |
| `MANUAL_EFFORT` | Repetitive tasks | Editing config files by hand |
| `ERROR_PRONE` | Quality/reliability issues | Typos in dependency names |
| `LACK_OF_CONTROL` | Limited flexibility | Can't customize output format |
| `LACK_OF_VISIBILITY` | Poor observability | No progress indicators |
| `INTEGRATION_FRICTION` | Tool compatibility | Different tools don't work together |
| `LEARNING_CURVE` | Difficulty to learn | Steep syntax learning |

### Severity Scoring (1-10)

| Score | Severity | Impact | Example |
|-------|----------|--------|---------|
| 1-3 | **Minor** | Annoyance, workaround exists | Slightly verbose output |
| 4-7 | **Moderate** | Significant friction, slows work | Need to look up syntax each time |
| 8-10 | **Critical** | Blocking, prevents job completion | Cannot complete task without tool |

### Measuring Resolution Effectiveness

```python
# High effectiveness (75% reduction)
painpoint1 = PainpointResolved(
    painpoint_id="slow-builds",
    category=PainpointCategory.TIME_WASTED,
    description="Slow build times",
    feature="uv build",
    persona="python-developer",
    severity_before=8,
    severity_after=2  # 75% reduction
)

# Low effectiveness (25% reduction)
painpoint2 = PainpointResolved(
    painpoint_id="complex-config",
    category=PainpointCategory.COGNITIVE_LOAD,
    description="Complex configuration",
    feature="specify init",
    persona="python-developer",
    severity_before=8,
    severity_after=6  # Only 25% reduction
)
```

---

## Time-to-Outcome

### Measuring Customer Journey

```python
from specify_cli.core.jtbd_metrics import TimeToOutcome, track_time_to_outcome

# 1. Start measuring
tto = TimeToOutcome(
    outcome_id="dependency-added",
    persona="python-developer",
    feature="specify deps add",
    context={"package": "httpx"}
)

# 2. Track steps in the journey
tto.add_step("parse_args")
tto.add_step("validate_package_name")
tto.add_step("check_pyproject_exists")
tto.add_step("update_dependencies")
tto.add_step("run_uv_add")

# 3. Complete measurement
tto.complete()  # Calculates duration

# 4. Track the outcome
track_time_to_outcome(tto)

print(f"Time: {tto.duration_seconds}s")  # 2.34s
print(f"Steps: {len(tto.steps)}")  # 5
```

### Journey Steps (Best Practices)

```python
# Detailed step tracking
tto = TimeToOutcome(
    outcome_id="rdf-validated",
    persona="backend-developer",
    feature="specify ggen validate-rdf"
)

# Capture all significant operations
tto.add_step("load_rdf_file")
tto.add_step("parse_turtle_syntax")
tto.add_step("load_shacl_shapes")
tto.add_step("validate_against_shapes")
tto.add_step("generate_validation_report")

tto.complete()
track_time_to_outcome(tto)
```

### Context for Analysis

```python
tto = TimeToOutcome(
    outcome_id="project-initialized",
    persona="python-developer",
    feature="specify init",
    context={
        "template_used": "fastapi",
        "num_files_created": 12,
        "total_file_size_kb": 45
    }
)
```

---

## User Satisfaction

### Tracking Satisfaction

```python
from specify_cli.core.jtbd_metrics import (
    UserSatisfaction,
    SatisfactionLevel,
    track_user_satisfaction,
)

satisfaction = UserSatisfaction(
    outcome_id="faster-dependency-management",
    feature="specify deps add",
    persona="python-developer",
    satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
    met_expectations=True,
    would_recommend=True,
    effort_score=2,  # Customer Effort Score (1-7, lower is better)
    feedback_text="Super fast and easy to use!",
    context={"previous_tool": "pip"}
)

track_user_satisfaction(satisfaction)
```

### Satisfaction Levels

| Level | Meaning | When to Use |
|-------|---------|-------------|
| `VERY_DISSATISFIED` | Extremely unhappy | Feature actively harmful |
| `DISSATISFIED` | Unhappy | Feature didn't help |
| `NEUTRAL` | Neither happy nor unhappy | Feature worked but not impressive |
| `SATISFIED` | Happy | Feature met expectations |
| `VERY_SATISFIED` | Extremely happy | Feature exceeded expectations |

### Customer Effort Score (CES)

Scale: 1 (very easy) to 7 (very difficult)

| Score | Effort Level | Meaning |
|-------|--------------|---------|
| 1-2 | Very Low | Effortless, intuitive |
| 3-4 | Moderate | Some effort required |
| 5-6 | High | Difficult, frustrating |
| 7 | Very High | Extremely difficult |

**Target:** CES ≤ 3 (low effort)

```python
# Example: Low effort (good)
UserSatisfaction(
    outcome_id="deps-added",
    feature="specify deps add",
    persona="python-developer",
    satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
    met_expectations=True,
    would_recommend=True,
    effort_score=1  # Effortless
)

# Example: High effort (bad)
UserSatisfaction(
    outcome_id="complex-setup",
    feature="manual-config",
    persona="python-developer",
    satisfaction_level=SatisfactionLevel.DISSATISFIED,
    met_expectations=False,
    would_recommend=False,
    effort_score=6  # Very difficult
)
```

---

## Configuration

### OpenTelemetry Setup

**Option 1: Environment Variables**

```bash
# OTLP endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318

# Service name
export OTEL_SERVICE_NAME=specify-cli

# Run CLI with OTEL
specify deps add httpx
```

**Option 2: Configuration File**

```python
# src/specify_cli/core/config.py
from specify_cli.core.telemetry import configure_otel

configure_otel(
    service_name="specify-cli",
    endpoint="http://localhost:4318",
    insecure=True
)
```

### Graceful Degradation

JTBD metrics work with or without OpenTelemetry:

- **With OTEL**: Spans, events, and metrics sent to backend
- **Without OTEL**: Metrics logged locally (no external dependency)

```python
# Works without OTEL
track_job_completion(job)  # Logs locally if OTEL unavailable
```

---

## Best Practices

### 1. Track Jobs at Command Entry Points

```python
# ✅ CORRECT: Track at command level
@app.command()
def deps_add(package: str) -> None:
    """Add dependency to project."""
    job = JobCompletion(
        job_id="deps-add",
        persona="python-developer",
        feature_used="specify deps add",
        context={"package": package}
    )

    try:
        # Do work
        add_dependency(package)
        job.complete()
    except Exception as e:
        job.fail(reason=str(e))
    finally:
        track_job_completion(job)
```

### 2. Measure Outcomes Against Baselines

```python
# ✅ CORRECT: Compare to baseline
import time

start = time.time()
# Do work
duration = time.time() - start

outcome = OutcomeAchieved(
    outcome_id="faster-builds",
    metric="time_saved_seconds",
    expected_value=120.0,  # Baseline: old method took 120s
    actual_value=duration,  # New method measured
    feature="uv build"
)
```

### 3. Link Jobs to Outcomes

```python
# ✅ CORRECT: Same context across job and outcome
context = {"package": "httpx", "method": "uv"}

job = JobCompletion(
    job_id="deps-add",
    persona="python-developer",
    feature_used="specify deps add",
    context=context
)

outcome = OutcomeAchieved(
    outcome_id="faster-dependency-management",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=8.5,
    feature="specify deps add",
    context=context  # Same context
)
```

### 4. Track Painpoints Before and After

```python
# ✅ CORRECT: Measure before and after feature
before_severity = measure_current_pain()  # 8/10

# Implement feature
release_new_feature()

after_severity = measure_current_pain()  # 2/10

painpoint = PainpointResolved(
    painpoint_id="manual-editing",
    category=PainpointCategory.MANUAL_EFFORT,
    description="Manual config editing",
    feature="specify deps add",
    persona="python-developer",
    severity_before=before_severity,
    severity_after=after_severity
)
```

### 5. Use Personas Consistently

```python
# ✅ CORRECT: Consistent persona naming
PERSONAS = {
    "python-developer": "Python developers building applications",
    "backend-developer": "Backend engineers working with APIs",
    "devops-engineer": "DevOps managing infrastructure",
}

# Use same persona across all metrics
persona = "python-developer"
job = JobCompletion(job_id="deps-add", persona=persona, ...)
outcome = OutcomeAchieved(outcome_id="faster-deps", persona=persona, ...)
painpoint = PainpointResolved(painpoint_id="manual-edit", persona=persona, ...)
```

---

## Troubleshooting

### OTEL Spans Not Appearing

**Problem:** Metrics tracked but not visible in OTEL backend.

**Solution:**

```bash
# 1. Check OTEL endpoint
echo $OTEL_EXPORTER_OTLP_ENDPOINT
# Should be: http://localhost:4318

# 2. Check OTEL backend is running
curl http://localhost:4318/health

# 3. Enable debug logging
export OTEL_LOG_LEVEL=debug
specify deps add httpx

# 4. Check for errors in logs
tail -f /tmp/specify-otel.log
```

### Metrics Not Recorded

**Problem:** `track_*()` functions called but no data.

**Solution:**

```python
# Check current span is recording
from specify_cli.core.telemetry import get_current_span

span = get_current_span()
print(f"Recording: {span.is_recording()}")

# If False, create a span first
from specify_cli.core.telemetry import span

with span("my_operation"):
    track_job_completion(job)  # Now it works
```

### Duration Always Zero

**Problem:** `job.duration_seconds` is always 0.

**Solution:**

```python
# ❌ WRONG: Forgot to call complete()
job = JobCompletion(...)
track_job_completion(job)  # duration_seconds = None

# ✅ CORRECT: Call complete() first
job = JobCompletion(...)
job.complete()  # Calculates duration
track_job_completion(job)  # duration_seconds = 2.34
```

### Achievement Rate Incorrect

**Problem:** `outcome.achievement_rate` shows unexpected value.

**Solution:**

```python
# Check expected vs actual values
print(f"Expected: {outcome.expected_value}")
print(f"Actual: {outcome.actual_value}")
print(f"Rate: {outcome.achievement_rate}%")

# For "minimize" outcomes, invert the logic
# Example: Minimize time (lower is better)
expected_time = 30.0  # Want under 30s
actual_time = 8.5     # Achieved 8.5s

# ❌ WRONG: Direct comparison (28% achievement)
outcome = OutcomeAchieved(
    metric="time_saved_seconds",
    expected_value=expected_time,
    actual_value=actual_time  # Lower is better, but calc shows 28%
)

# ✅ CORRECT: Invert for "minimize" metrics
time_saved = expected_time - actual_time  # 21.5s saved
outcome = OutcomeAchieved(
    metric="time_saved_seconds",
    expected_value=expected_time,
    actual_value=expected_time  # 100% if under target
)
```

---

## Next Steps

- **[JTBD API Reference](JTBD_API_REFERENCE.md)** - Detailed API documentation
- **[JTBD Examples](JTBD_EXAMPLES.md)** - Practical code examples
- **[RDF Schema](../ontology/jtbd-schema.ttl)** - JTBD ontology specification
- **[JTBD Framework](https://jobs-to-be-done.com/)** - Original framework

---

**Framework:** Jobs-to-be-Done (Clayton Christensen)
**Integration:** OpenTelemetry distributed tracing
**Status:** Production-ready (v1.0.0)
