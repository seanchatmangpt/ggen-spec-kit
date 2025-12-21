# JTBD API Reference

**Version:** 1.0.0
**Module:** `specify_cli.core.jtbd_metrics`
**Last Updated:** 2025-12-21

## Overview

Complete API reference for the Jobs-to-be-Done (JTBD) metrics framework.

## Table of Contents

1. [Enumerations](#enumerations)
2. [Data Classes](#data-classes)
3. [Tracking Functions](#tracking-functions)
4. [Type Signatures](#type-signatures)
5. [Error Handling](#error-handling)

---

## Enumerations

### JobStatus

```python
class JobStatus(str, Enum):
    """Job completion status."""
```

**Values:**

| Value | Type | Description |
|-------|------|-------------|
| `STARTED` | `str` | Job has been initiated |
| `IN_PROGRESS` | `str` | Job is actively being worked on |
| `COMPLETED` | `str` | Job completed successfully |
| `FAILED` | `str` | Job failed to complete |
| `ABANDONED` | `str` | Job was abandoned by user |

**Example:**

```python
from specify_cli.core.jtbd_metrics import JobStatus

status = JobStatus.COMPLETED
print(status.value)  # "completed"
```

---

### OutcomeStatus

```python
class OutcomeStatus(str, Enum):
    """Outcome achievement status."""
```

**Values:**

| Value | Type | Description |
|-------|------|-------------|
| `NOT_STARTED` | `str` | Outcome measurement not yet started |
| `IN_PROGRESS` | `str` | Outcome partially achieved (1-74%) |
| `ACHIEVED` | `str` | Outcome fully achieved (≥100%) |
| `PARTIALLY_ACHIEVED` | `str` | Outcome nearly achieved (75-99%) |
| `NOT_ACHIEVED` | `str` | Outcome not achieved (0%) |

**Example:**

```python
from specify_cli.core.jtbd_metrics import OutcomeStatus

status = OutcomeStatus.ACHIEVED
print(status.value)  # "achieved"
```

---

### PainpointCategory

```python
class PainpointCategory(str, Enum):
    """Categories of painpoints that features resolve."""
```

**Values:**

| Value | Type | Description |
|-------|------|-------------|
| `TIME_WASTED` | `str` | Inefficient processes waste time |
| `COGNITIVE_LOAD` | `str` | Mental complexity is high |
| `MANUAL_EFFORT` | `str` | Repetitive manual tasks |
| `ERROR_PRONE` | `str` | Quality/reliability issues |
| `LACK_OF_CONTROL` | `str` | Limited flexibility/customization |
| `LACK_OF_VISIBILITY` | `str` | Poor observability/feedback |
| `INTEGRATION_FRICTION` | `str` | Tool compatibility problems |
| `LEARNING_CURVE` | `str` | Difficult to learn or use |

**Example:**

```python
from specify_cli.core.jtbd_metrics import PainpointCategory

category = PainpointCategory.MANUAL_EFFORT
print(category.value)  # "manual_effort"
```

---

### SatisfactionLevel

```python
class SatisfactionLevel(str, Enum):
    """User satisfaction with outcome delivery."""
```

**Values:**

| Value | Type | Description |
|-------|------|-------------|
| `VERY_DISSATISFIED` | `str` | User extremely unhappy |
| `DISSATISFIED` | `str` | User unhappy |
| `NEUTRAL` | `str` | User neither happy nor unhappy |
| `SATISFIED` | `str` | User happy |
| `VERY_SATISFIED` | `str` | User extremely happy |

**Example:**

```python
from specify_cli.core.jtbd_metrics import SatisfactionLevel

level = SatisfactionLevel.VERY_SATISFIED
print(level.value)  # "very_satisfied"
```

---

## Data Classes

### JobCompletion

```python
@dataclass
class JobCompletion:
    """Track which job was completed by a user."""
```

**Attributes:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `job_id` | `str` | - | Unique identifier for the job type |
| `persona` | `str` | - | User persona completing the job |
| `feature_used` | `str` | - | Feature/command used to complete job |
| `status` | `JobStatus` | `STARTED` | Current status of the job |
| `context` | `dict[str, Any]` | `{}` | Additional context about job execution |
| `started_at` | `datetime` | `now(UTC)` | When the job started |
| `completed_at` | `datetime \| None` | `None` | When the job completed |
| `duration_seconds` | `float \| None` | `None` | Time taken to complete the job |

**Methods:**

#### `complete() -> None`

Mark the job as completed and calculate duration.

```python
job = JobCompletion(job_id="deps-add", persona="python-developer", feature_used="specify deps add")
job.complete()  # Sets status=COMPLETED, completed_at=now(), duration_seconds=elapsed
```

**Side Effects:**
- Sets `status` to `JobStatus.COMPLETED`
- Sets `completed_at` to current UTC time
- Calculates `duration_seconds` as `completed_at - started_at`

---

#### `fail(reason: str | None = None) -> None`

Mark the job as failed.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `reason` | `str \| None` | `None` | Reason for failure (stored in context) |

```python
job = JobCompletion(job_id="deps-add", persona="python-developer", feature_used="specify deps add")
job.fail(reason="Package not found")
# status=FAILED, context["failure_reason"]="Package not found"
```

**Side Effects:**
- Sets `status` to `JobStatus.FAILED`
- Adds `failure_reason` to `context` if reason provided

---

### OutcomeAchieved

```python
@dataclass
class OutcomeAchieved:
    """Track outcome achievement and measure against success criteria."""
```

**Attributes:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `outcome_id` | `str` | - | Unique identifier for the outcome type |
| `metric` | `str` | - | Metric being measured (e.g., "time_saved_seconds") |
| `expected_value` | `float` | - | Expected/target value for the outcome |
| `actual_value` | `float` | - | Actual value achieved |
| `feature` | `str` | - | Feature that delivered the outcome |
| `persona` | `str \| None` | `None` | User persona achieving the outcome |
| `status` | `OutcomeStatus` | `ACHIEVED` | Status of outcome achievement |
| `context` | `dict[str, Any]` | `{}` | Additional context about outcome delivery |
| `measured_at` | `datetime` | `now(UTC)` | When the outcome was measured |

**Properties:**

#### `achievement_rate: float`

Calculate achievement rate as a percentage.

**Returns:** `float` - Percentage of expected outcome achieved.

```python
outcome = OutcomeAchieved(
    outcome_id="faster-deps",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=8.5,
    feature="specify deps add"
)
print(outcome.achievement_rate)  # 28.33
```

**Calculation:**
```python
if expected_value == 0:
    return 100.0 if actual_value >= 0 else 0.0
return (actual_value / expected_value) * 100.0
```

---

#### `exceeds_expectations: bool`

Check if outcome exceeded expectations.

**Returns:** `bool` - `True` if actual > expected.

```python
outcome = OutcomeAchieved(
    outcome_id="faster-deps",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=45.0,
    feature="specify deps add"
)
print(outcome.exceeds_expectations)  # True
```

---

**Methods:**

#### `determine_status() -> OutcomeStatus`

Determine outcome status based on achievement rate.

**Returns:** `OutcomeStatus` - Status based on achievement percentage.

```python
outcome = OutcomeAchieved(
    outcome_id="faster-deps",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=22.5,
    feature="specify deps add"
)
status = outcome.determine_status()
print(status)  # OutcomeStatus.PARTIALLY_ACHIEVED (75%)
```

**Status Mapping:**

| Achievement Rate | Status |
|------------------|--------|
| ≥ 100% | `ACHIEVED` |
| 75-99% | `PARTIALLY_ACHIEVED` |
| 1-74% | `IN_PROGRESS` |
| 0% | `NOT_ACHIEVED` |

---

### PainpointResolved

```python
@dataclass
class PainpointResolved:
    """Track which painpoints were resolved by a feature."""
```

**Attributes:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `painpoint_id` | `str` | - | Unique identifier for the painpoint |
| `category` | `PainpointCategory` | - | Category of painpoint |
| `description` | `str` | - | Human-readable description of the painpoint |
| `feature` | `str` | - | Feature that resolved the painpoint |
| `persona` | `str` | - | User persona experiencing the painpoint |
| `severity_before` | `int` | - | Severity rating before resolution (1-10) |
| `severity_after` | `int` | - | Severity rating after resolution (1-10) |
| `resolution_effectiveness` | `float \| None` | `None` | Calculated effectiveness of resolution (%) |
| `context` | `dict[str, Any]` | `{}` | Additional context about painpoint resolution |
| `resolved_at` | `datetime` | `now(UTC)` | When the painpoint was resolved |

**Post-Init:**

`resolution_effectiveness` is automatically calculated:

```python
if severity_before > 0:
    reduction = severity_before - severity_after
    resolution_effectiveness = (reduction / severity_before) * 100.0
else:
    resolution_effectiveness = 0.0
```

**Example:**

```python
painpoint = PainpointResolved(
    painpoint_id="manual-editing",
    category=PainpointCategory.MANUAL_EFFORT,
    description="Manual pyproject.toml editing",
    feature="specify deps add",
    persona="python-developer",
    severity_before=8,
    severity_after=2
)
# resolution_effectiveness = ((8-2)/8)*100 = 75.0%
```

---

### TimeToOutcome

```python
@dataclass
class TimeToOutcome:
    """Measure time required to achieve an outcome."""
```

**Attributes:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `outcome_id` | `str` | - | Identifier for the outcome being measured |
| `persona` | `str` | - | User persona achieving the outcome |
| `feature` | `str` | - | Feature used to achieve the outcome |
| `start_time` | `float` | `time.time()` | Start timestamp (Unix time) |
| `end_time` | `float \| None` | `None` | End timestamp (Unix time) |
| `duration_seconds` | `float \| None` | `None` | Total time to achieve outcome |
| `steps` | `list[str]` | `[]` | Steps taken to achieve the outcome |
| `context` | `dict[str, Any]` | `{}` | Additional context about the journey |

**Methods:**

#### `add_step(step: str) -> None`

Add a step to the journey.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `step` | `str` | Name of the step |

```python
tto = TimeToOutcome(outcome_id="deps-added", persona="python-developer", feature="specify deps add")
tto.add_step("parse_args")
tto.add_step("validate_package")
tto.add_step("update_pyproject")
```

---

#### `complete() -> None`

Mark the outcome as achieved and calculate duration.

```python
tto = TimeToOutcome(outcome_id="deps-added", persona="python-developer", feature="specify deps add")
tto.add_step("parse_args")
tto.add_step("validate_package")
tto.complete()  # Sets end_time=time.time(), duration_seconds=end_time-start_time
```

**Side Effects:**
- Sets `end_time` to current time
- Calculates `duration_seconds` as `end_time - start_time`

---

### UserSatisfaction

```python
@dataclass
class UserSatisfaction:
    """Track user satisfaction with outcome achievement."""
```

**Attributes:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `outcome_id` | `str` | - | Identifier for the outcome |
| `feature` | `str` | - | Feature that delivered the outcome |
| `persona` | `str` | - | User persona providing feedback |
| `satisfaction_level` | `SatisfactionLevel` | - | Overall satisfaction rating |
| `met_expectations` | `bool` | - | Whether outcome met expectations |
| `would_recommend` | `bool` | - | Whether user would recommend the feature |
| `effort_score` | `int \| None` | `None` | Customer Effort Score (1-7, lower is better) |
| `feedback_text` | `str \| None` | `None` | Qualitative feedback from user |
| `context` | `dict[str, Any]` | `{}` | Additional context about satisfaction |
| `recorded_at` | `datetime` | `now(UTC)` | When satisfaction was recorded |

**Example:**

```python
satisfaction = UserSatisfaction(
    outcome_id="faster-deps",
    feature="specify deps add",
    persona="python-developer",
    satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
    met_expectations=True,
    would_recommend=True,
    effort_score=2,
    feedback_text="Super fast and easy!"
)
```

---

## Tracking Functions

### track_job_completion

```python
def track_job_completion(job: JobCompletion) -> None:
    """Track job completion with OpenTelemetry."""
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `job` | `JobCompletion` | Job completion data to track |

**Returns:** `None`

**Side Effects:**
- Creates OTEL span event "job_completed"
- Sets span attributes with job metadata
- Updates metrics counter `jtbd.job.{job_id}.completions`
- Updates metrics histogram `jtbd.job.{job_id}.duration` (if duration available)

**Example:**

```python
from specify_cli.core.jtbd_metrics import JobCompletion, track_job_completion

job = JobCompletion(
    job_id="deps-add",
    persona="python-developer",
    feature_used="specify deps add"
)
job.complete()
track_job_completion(job)
```

**OTEL Attributes:**

| Attribute | Type | Example |
|-----------|------|---------|
| `jtbd.job.id` | `str` | `"deps-add"` |
| `jtbd.job.persona` | `str` | `"python-developer"` |
| `jtbd.job.feature` | `str` | `"specify deps add"` |
| `jtbd.job.status` | `str` | `"completed"` |
| `jtbd.job.duration_seconds` | `float` | `2.34` |
| `jtbd.job.context.*` | `str` | `jtbd.job.context.package="httpx"` |

---

### track_outcome_achieved

```python
def track_outcome_achieved(outcome: OutcomeAchieved) -> None:
    """Track outcome achievement with OpenTelemetry."""
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `outcome` | `OutcomeAchieved` | Outcome achievement data to track |

**Returns:** `None`

**Side Effects:**
- Creates OTEL span event "outcome_achieved"
- Sets span attributes with outcome metadata
- Updates metrics counter `jtbd.outcome.{outcome_id}.achievements`
- Updates metrics histogram `jtbd.outcome.{outcome_id}.achievement_rate`

**Example:**

```python
from specify_cli.core.jtbd_metrics import OutcomeAchieved, track_outcome_achieved

outcome = OutcomeAchieved(
    outcome_id="faster-deps",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=8.5,
    feature="specify deps add"
)
track_outcome_achieved(outcome)
```

**OTEL Attributes:**

| Attribute | Type | Example |
|-----------|------|---------|
| `jtbd.outcome.id` | `str` | `"faster-deps"` |
| `jtbd.outcome.metric` | `str` | `"time_saved_seconds"` |
| `jtbd.outcome.expected` | `float` | `30.0` |
| `jtbd.outcome.actual` | `float` | `8.5` |
| `jtbd.outcome.achievement_rate` | `float` | `28.33` |
| `jtbd.outcome.feature` | `str` | `"specify deps add"` |
| `jtbd.outcome.status` | `str` | `"in_progress"` |
| `jtbd.outcome.exceeds_expectations` | `bool` | `False` |

---

### track_painpoint_resolved

```python
def track_painpoint_resolved(painpoint: PainpointResolved) -> None:
    """Track painpoint resolution with OpenTelemetry."""
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `painpoint` | `PainpointResolved` | Painpoint resolution data to track |

**Returns:** `None`

**Side Effects:**
- Creates OTEL span event "painpoint_resolved"
- Sets span attributes with painpoint metadata
- Updates metrics counter `jtbd.painpoint.resolutions`
- Updates metrics histogram `jtbd.painpoint.effectiveness`

**Example:**

```python
from specify_cli.core.jtbd_metrics import (
    PainpointResolved,
    PainpointCategory,
    track_painpoint_resolved,
)

painpoint = PainpointResolved(
    painpoint_id="manual-editing",
    category=PainpointCategory.MANUAL_EFFORT,
    description="Manual pyproject.toml editing",
    feature="specify deps add",
    persona="python-developer",
    severity_before=8,
    severity_after=2
)
track_painpoint_resolved(painpoint)
```

**OTEL Attributes:**

| Attribute | Type | Example |
|-----------|------|---------|
| `jtbd.painpoint.id` | `str` | `"manual-editing"` |
| `jtbd.painpoint.category` | `str` | `"manual_effort"` |
| `jtbd.painpoint.description` | `str` | `"Manual pyproject.toml editing"` |
| `jtbd.painpoint.feature` | `str` | `"specify deps add"` |
| `jtbd.painpoint.persona` | `str` | `"python-developer"` |
| `jtbd.painpoint.severity_before` | `int` | `8` |
| `jtbd.painpoint.severity_after` | `int` | `2` |
| `jtbd.painpoint.resolution_effectiveness` | `float` | `75.0` |

---

### track_time_to_outcome

```python
def track_time_to_outcome(time_to_outcome: TimeToOutcome) -> None:
    """Track time-to-outcome measurement with OpenTelemetry."""
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `time_to_outcome` | `TimeToOutcome` | Time-to-outcome data to track |

**Returns:** `None`

**Side Effects:**
- Creates OTEL span event "time_to_outcome" (if duration calculated)
- Sets span attributes with time-to-outcome metadata
- Updates metrics histogram `jtbd.tto.{outcome_id}.duration`

**Example:**

```python
from specify_cli.core.jtbd_metrics import TimeToOutcome, track_time_to_outcome

tto = TimeToOutcome(
    outcome_id="deps-added",
    persona="python-developer",
    feature="specify deps add"
)
tto.add_step("parse_args")
tto.add_step("validate_package")
tto.complete()
track_time_to_outcome(tto)
```

**OTEL Attributes:**

| Attribute | Type | Example |
|-----------|------|---------|
| `jtbd.tto.outcome_id` | `str` | `"deps-added"` |
| `jtbd.tto.persona` | `str` | `"python-developer"` |
| `jtbd.tto.feature` | `str` | `"specify deps add"` |
| `jtbd.tto.duration_seconds` | `float` | `2.34` |
| `jtbd.tto.steps_count` | `int` | `2` |
| `jtbd.tto.step_1` | `str` | `"parse_args"` |
| `jtbd.tto.step_2` | `str` | `"validate_package"` |

---

### track_user_satisfaction

```python
def track_user_satisfaction(satisfaction: UserSatisfaction) -> None:
    """Track user satisfaction with OpenTelemetry."""
```

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `satisfaction` | `UserSatisfaction` | User satisfaction data to track |

**Returns:** `None`

**Side Effects:**
- Creates OTEL span event "user_satisfaction"
- Sets span attributes with satisfaction metadata
- Updates metrics counter `jtbd.satisfaction.{outcome_id}.responses`
- Updates metrics histogram `jtbd.satisfaction.effort_score` (if provided)

**Example:**

```python
from specify_cli.core.jtbd_metrics import (
    UserSatisfaction,
    SatisfactionLevel,
    track_user_satisfaction,
)

satisfaction = UserSatisfaction(
    outcome_id="faster-deps",
    feature="specify deps add",
    persona="python-developer",
    satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
    met_expectations=True,
    would_recommend=True,
    effort_score=2
)
track_user_satisfaction(satisfaction)
```

**OTEL Attributes:**

| Attribute | Type | Example |
|-----------|------|---------|
| `jtbd.satisfaction.outcome_id` | `str` | `"faster-deps"` |
| `jtbd.satisfaction.feature` | `str` | `"specify deps add"` |
| `jtbd.satisfaction.persona` | `str` | `"python-developer"` |
| `jtbd.satisfaction.level` | `str` | `"very_satisfied"` |
| `jtbd.satisfaction.met_expectations` | `bool` | `True` |
| `jtbd.satisfaction.would_recommend` | `bool` | `True` |
| `jtbd.satisfaction.effort_score` | `int` | `2` |
| `jtbd.satisfaction.feedback` | `str` | `"Super fast!"` |

---

## Type Signatures

### Complete Type Signatures

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

# Enums
class JobStatus(str, Enum): ...
class OutcomeStatus(str, Enum): ...
class PainpointCategory(str, Enum): ...
class SatisfactionLevel(str, Enum): ...

# Data Classes
@dataclass
class JobCompletion:
    job_id: str
    persona: str
    feature_used: str
    status: JobStatus = JobStatus.STARTED
    context: dict[str, Any] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_seconds: float | None = None

    def complete(self) -> None: ...
    def fail(self, reason: str | None = None) -> None: ...

@dataclass
class OutcomeAchieved:
    outcome_id: str
    metric: str
    expected_value: float
    actual_value: float
    feature: str
    persona: str | None = None
    status: OutcomeStatus = OutcomeStatus.ACHIEVED
    context: dict[str, Any] = field(default_factory=dict)
    measured_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def achievement_rate(self) -> float: ...

    @property
    def exceeds_expectations(self) -> bool: ...

    def determine_status(self) -> OutcomeStatus: ...

@dataclass
class PainpointResolved:
    painpoint_id: str
    category: PainpointCategory
    description: str
    feature: str
    persona: str
    severity_before: int
    severity_after: int
    resolution_effectiveness: float | None = None
    context: dict[str, Any] = field(default_factory=dict)
    resolved_at: datetime = field(default_factory=lambda: datetime.now(UTC))

@dataclass
class TimeToOutcome:
    outcome_id: str
    persona: str
    feature: str
    start_time: float = field(default_factory=time.time)
    end_time: float | None = None
    duration_seconds: float | None = None
    steps: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)

    def add_step(self, step: str) -> None: ...
    def complete(self) -> None: ...

@dataclass
class UserSatisfaction:
    outcome_id: str
    feature: str
    persona: str
    satisfaction_level: SatisfactionLevel
    met_expectations: bool
    would_recommend: bool
    effort_score: int | None = None
    feedback_text: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    recorded_at: datetime = field(default_factory=lambda: datetime.now(UTC))

# Tracking Functions
def track_job_completion(job: JobCompletion) -> None: ...
def track_outcome_achieved(outcome: OutcomeAchieved) -> None: ...
def track_painpoint_resolved(painpoint: PainpointResolved) -> None: ...
def track_time_to_outcome(time_to_outcome: TimeToOutcome) -> None: ...
def track_user_satisfaction(satisfaction: UserSatisfaction) -> None: ...
```

---

## Error Handling

### Graceful Degradation

All tracking functions gracefully degrade when OpenTelemetry is unavailable:

```python
# If OTEL unavailable, metrics are logged locally
# No exceptions are raised
track_job_completion(job)  # Works with or without OTEL
```

### Common Errors

#### AttributeError: 'NoneType' has no attribute 'total_seconds'

**Cause:** Calling `track_job_completion()` before `job.complete()`.

**Solution:**

```python
# ✅ CORRECT
job.complete()  # Calculates duration
track_job_completion(job)

# ❌ WRONG
track_job_completion(job)  # duration_seconds is None
```

---

#### ZeroDivisionError in achievement_rate

**Cause:** `expected_value = 0` and special case not handled.

**Solution:** Framework handles this automatically:

```python
if expected_value == 0:
    return 100.0 if actual_value >= 0 else 0.0
# No ZeroDivisionError raised
```

---

#### ValueError: severity_before/after not in range 1-10

**Cause:** Severity scores outside valid range.

**Solution:**

```python
# ✅ CORRECT
painpoint = PainpointResolved(
    severity_before=8,  # 1-10
    severity_after=2    # 1-10
)

# ❌ WRONG
painpoint = PainpointResolved(
    severity_before=15,  # Invalid: > 10
    severity_after=0     # Invalid: < 1
)
```

**Recommendation:** Add validation:

```python
assert 1 <= severity_before <= 10, "Severity must be 1-10"
assert 1 <= severity_after <= 10, "Severity must be 1-10"
```

---

## See Also

- **[JTBD User Guide](JTBD_USER_GUIDE.md)** - Getting started and usage
- **[JTBD Examples](JTBD_EXAMPLES.md)** - Practical code examples
- **[RDF Schema](../ontology/jtbd-schema.ttl)** - JTBD ontology specification
- **[JTBD Framework](https://jobs-to-be-done.com/)** - Original framework

---

**Version:** 1.0.0
**Module:** `specify_cli.core.jtbd_metrics`
**Type Coverage:** 100% (all functions fully typed)
