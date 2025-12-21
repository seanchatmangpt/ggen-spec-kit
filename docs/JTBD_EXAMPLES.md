# JTBD Examples - Practical Use Cases

**Version:** 1.0.0
**Last Updated:** 2025-12-21

## Overview

Practical examples demonstrating how to use the JTBD metrics framework in real-world scenarios.

## Table of Contents

1. [Complete CLI Command Flow](#complete-cli-command-flow)
2. [Multi-Step Job Journey](#multi-step-job-journey)
3. [Outcome Measurement](#outcome-measurement)
4. [Painpoint Tracking](#painpoint-tracking)
5. [User Feedback Collection](#user-feedback-collection)
6. [Analytics Dashboard](#analytics-dashboard)
7. [A/B Testing](#ab-testing)
8. [Feature Impact Analysis](#feature-impact-analysis)

---

## Complete CLI Command Flow

### Example: `specify deps add` Command

Track the complete customer journey from command invocation to outcome.

```python
from specify_cli.core.jtbd_metrics import (
    JobCompletion,
    OutcomeAchieved,
    PainpointResolved,
    PainpointCategory,
    TimeToOutcome,
    UserSatisfaction,
    SatisfactionLevel,
    track_job_completion,
    track_outcome_achieved,
    track_painpoint_resolved,
    track_time_to_outcome,
    track_user_satisfaction,
)
from specify_cli.core.telemetry import span
import time

@app.command()
def deps_add(package: str, dev: bool = False) -> None:
    """Add dependency to project."""

    # 1. Start job tracking
    job = JobCompletion(
        job_id="deps-add",
        persona="python-developer",
        feature_used="specify deps add",
        context={
            "package": package,
            "dev_dependency": dev
        }
    )

    # 2. Start time-to-outcome measurement
    tto = TimeToOutcome(
        outcome_id="dependency-added",
        persona="python-developer",
        feature="specify deps add",
        context={"package": package}
    )

    try:
        with span("deps.add", package=package):
            # Parse and validate
            tto.add_step("parse_arguments")
            validate_package_name(package)

            tto.add_step("check_pyproject_exists")
            pyproject_path = find_pyproject_toml()

            tto.add_step("validate_package_availability")
            start_uv = time.time()
            run_uv_add(package, dev=dev)
            uv_duration = time.time() - start_uv

            tto.add_step("update_lockfile")
            tto.add_step("install_package")

            # 3. Complete job
            job.complete()
            tto.complete()

            # 4. Track outcome (compare to baseline)
            baseline_time = 30.0  # Manual editing takes ~30s
            actual_time = tto.duration_seconds

            outcome = OutcomeAchieved(
                outcome_id="faster-dependency-management",
                metric="time_saved_seconds",
                expected_value=baseline_time,
                actual_value=baseline_time - actual_time,  # Time saved
                feature="specify deps add",
                persona="python-developer",
                context={
                    "package": package,
                    "baseline_method": "manual",
                    "uv_duration": uv_duration
                }
            )

            # 5. Track painpoint resolution
            painpoint = PainpointResolved(
                painpoint_id="manual-dependency-updates",
                category=PainpointCategory.MANUAL_EFFORT,
                description="Manually editing pyproject.toml and running uv add",
                feature="specify deps add",
                persona="python-developer",
                severity_before=8,  # High manual effort
                severity_after=2,   # Low effort with CLI
                context={
                    "frequency": "daily",
                    "steps_eliminated": 4
                }
            )

            # 6. Collect user satisfaction (simulated - normally via survey)
            satisfaction = UserSatisfaction(
                outcome_id="faster-dependency-management",
                feature="specify deps add",
                persona="python-developer",
                satisfaction_level=SatisfactionLevel.VERY_SATISFIED,
                met_expectations=True,
                would_recommend=True,
                effort_score=2,  # Very easy
                feedback_text="Much faster than manual editing!",
                context={"package": package}
            )

            # 7. Track all metrics
            track_job_completion(job)
            track_time_to_outcome(tto)
            track_outcome_achieved(outcome)
            track_painpoint_resolved(painpoint)
            track_user_satisfaction(satisfaction)

            # 8. Display success
            console.print(f"[green]✓[/green] Added {package} to dependencies")

    except Exception as e:
        # Track failure
        job.fail(reason=str(e))
        track_job_completion(job)
        console.print(f"[red]✗[/red] Failed to add {package}: {e}")
        raise
```

---

## Multi-Step Job Journey

### Example: Project Initialization

Track a complex job with multiple sub-jobs.

```python
from specify_cli.core.jtbd_metrics import JobCompletion, track_job_completion

@app.command()
def init(
    project_name: str,
    template: str = "basic",
    git_init: bool = True
) -> None:
    """Initialize a new project."""

    # Main job
    main_job = JobCompletion(
        job_id="init-project",
        persona="python-developer",
        feature_used="specify init",
        context={
            "project_name": project_name,
            "template": template,
            "git_init": git_init
        }
    )

    try:
        # Sub-job 1: Create directory structure
        sub_job_1 = JobCompletion(
            job_id="init-create-structure",
            persona="python-developer",
            feature_used="specify init",
            context={"project_name": project_name}
        )
        create_directory_structure(project_name)
        sub_job_1.complete()
        track_job_completion(sub_job_1)

        # Sub-job 2: Initialize git
        if git_init:
            sub_job_2 = JobCompletion(
                job_id="init-git-repo",
                persona="python-developer",
                feature_used="specify init",
                context={"project_name": project_name}
            )
            initialize_git(project_name)
            sub_job_2.complete()
            track_job_completion(sub_job_2)

        # Sub-job 3: Create pyproject.toml
        sub_job_3 = JobCompletion(
            job_id="init-create-pyproject",
            persona="python-developer",
            feature_used="specify init",
            context={
                "project_name": project_name,
                "template": template
            }
        )
        create_pyproject_toml(project_name, template)
        sub_job_3.complete()
        track_job_completion(sub_job_3)

        # Complete main job
        main_job.complete()
        track_job_completion(main_job)

        console.print(f"[green]✓[/green] Initialized project: {project_name}")

    except Exception as e:
        main_job.fail(reason=str(e))
        track_job_completion(main_job)
        raise
```

---

## Outcome Measurement

### Example: Build Performance Improvement

Measure and track performance improvements.

```python
from specify_cli.core.jtbd_metrics import OutcomeAchieved, track_outcome_achieved
import time

def measure_build_performance() -> None:
    """Measure build performance improvement."""

    # Baseline: old build system
    baseline_time = 120.0  # seconds

    # New: uv-based build
    start = time.time()
    run_uv_build()
    actual_time = time.time() - start

    # Track outcome
    outcome = OutcomeAchieved(
        outcome_id="faster-builds",
        metric="build_time_seconds",
        expected_value=baseline_time,
        actual_value=actual_time,
        feature="uv build",
        persona="python-developer",
        context={
            "baseline_tool": "pip + setuptools",
            "new_tool": "uv",
            "project_size_mb": 45,
            "num_dependencies": 23
        }
    )

    # Calculate improvement
    time_saved = baseline_time - actual_time
    improvement_pct = (time_saved / baseline_time) * 100

    track_outcome_achieved(outcome)

    console.print(f"Build time: {actual_time:.2f}s (saved {time_saved:.2f}s, {improvement_pct:.1f}% faster)")
```

### Example: Code Quality Improvement

Track quality metrics over time.

```python
from specify_cli.core.jtbd_metrics import OutcomeAchieved, track_outcome_achieved

def measure_code_quality() -> None:
    """Measure code quality improvement."""

    # Before: without mypy
    baseline_type_errors = 45

    # After: with mypy strict
    result = run_mypy_check()
    actual_type_errors = result.error_count

    # Calculate error reduction
    errors_eliminated = baseline_type_errors - actual_type_errors
    reduction_pct = (errors_eliminated / baseline_type_errors) * 100

    outcome = OutcomeAchieved(
        outcome_id="fewer-type-errors",
        metric="type_errors_eliminated",
        expected_value=baseline_type_errors * 0.8,  # Target: 80% reduction
        actual_value=errors_eliminated,
        feature="mypy strict mode",
        persona="python-developer",
        context={
            "baseline_errors": baseline_type_errors,
            "actual_errors": actual_type_errors,
            "reduction_percent": reduction_pct
        }
    )

    track_outcome_achieved(outcome)

    console.print(f"Type errors: {actual_type_errors} (eliminated {errors_eliminated}, {reduction_pct:.1f}% reduction)")
```

---

## Painpoint Tracking

### Example: Developer Experience Improvement

Track how features eliminate specific painpoints.

```python
from specify_cli.core.jtbd_metrics import (
    PainpointResolved,
    PainpointCategory,
    track_painpoint_resolved,
)

# Before: Manual testing
painpoint_before = {
    "id": "manual-test-execution",
    "description": "Manually running tests one by one",
    "severity": 9,  # Critical painpoint
    "time_cost_minutes": 15,
    "frequency": "hourly"
}

# After: Automated test runner
def track_test_automation_impact() -> None:
    """Track impact of automated test runner."""

    painpoint = PainpointResolved(
        painpoint_id="manual-test-execution",
        category=PainpointCategory.MANUAL_EFFORT,
        description="Manually running pytest for each test file",
        feature="pytest-watch auto-runner",
        persona="python-developer",
        severity_before=9,
        severity_after=2,  # Mostly eliminated
        context={
            "time_saved_per_run_minutes": 14,
            "frequency": "hourly",
            "daily_time_saved_hours": 3.5
        }
    )

    track_painpoint_resolved(painpoint)

    console.print(f"Painpoint resolution: {painpoint.resolution_effectiveness:.1f}% effective")
```

### Example: Integration Friction

Track painpoints around tool integration.

```python
from specify_cli.core.jtbd_metrics import (
    PainpointResolved,
    PainpointCategory,
    track_painpoint_resolved,
)

def track_integration_improvement() -> None:
    """Track improvement in tool integration."""

    # Painpoint: Different tools don't work together
    painpoint = PainpointResolved(
        painpoint_id="docker-otel-integration",
        category=PainpointCategory.INTEGRATION_FRICTION,
        description="Docker containers don't automatically send telemetry to OTEL",
        feature="specify docker run --otel",
        persona="devops-engineer",
        severity_before=8,
        severity_after=1,  # Fully automated
        context={
            "manual_steps_eliminated": 7,
            "configuration_files_eliminated": 2,
            "time_saved_minutes": 20
        }
    )

    track_painpoint_resolved(painpoint)
```

---

## User Feedback Collection

### Example: Post-Command Satisfaction Survey

Collect satisfaction feedback after key operations.

```python
from specify_cli.core.jtbd_metrics import (
    UserSatisfaction,
    SatisfactionLevel,
    track_user_satisfaction,
)
from readchar import readkey

def collect_satisfaction_feedback(outcome_id: str, feature: str, persona: str) -> None:
    """Collect user satisfaction after command completion."""

    # Ask for satisfaction (optional, non-blocking)
    console.print("\n[dim]How satisfied are you with this result? (1-5, or Enter to skip)[/dim]")

    try:
        response = readkey()
        if response == "\r":  # Enter key
            return

        rating = int(response)
        if not 1 <= rating <= 5:
            return

        # Map 1-5 to SatisfactionLevel
        levels = {
            1: SatisfactionLevel.VERY_DISSATISFIED,
            2: SatisfactionLevel.DISSATISFIED,
            3: SatisfactionLevel.NEUTRAL,
            4: SatisfactionLevel.SATISFIED,
            5: SatisfactionLevel.VERY_SATISFIED,
        }

        satisfaction = UserSatisfaction(
            outcome_id=outcome_id,
            feature=feature,
            persona=persona,
            satisfaction_level=levels[rating],
            met_expectations=(rating >= 4),
            would_recommend=(rating >= 4),
            effort_score=6 - rating,  # Invert: 1=hard, 5=easy
            context={"rating": rating}
        )

        track_user_satisfaction(satisfaction)
        console.print("[dim]Thank you for your feedback![/dim]")

    except (ValueError, KeyError):
        pass  # Invalid input, skip
```

### Example: Detailed Feedback with Text

```python
from specify_cli.core.jtbd_metrics import (
    UserSatisfaction,
    SatisfactionLevel,
    track_user_satisfaction,
)

def collect_detailed_feedback(outcome_id: str, feature: str, persona: str) -> None:
    """Collect detailed satisfaction feedback."""

    # Satisfaction rating
    console.print("How satisfied are you? (1-5):")
    rating = int(console.input("[dim]> [/dim]"))

    # Effort score
    console.print("How easy was it to use? (1=very hard, 7=very easy):")
    effort = int(console.input("[dim]> [/dim]"))

    # Would recommend?
    console.print("Would you recommend this feature? (y/n):")
    recommend = console.input("[dim]> [/dim]").lower() == "y"

    # Feedback text
    console.print("Any additional feedback? (optional):")
    feedback = console.input("[dim]> [/dim]")

    levels = {
        1: SatisfactionLevel.VERY_DISSATISFIED,
        2: SatisfactionLevel.DISSATISFIED,
        3: SatisfactionLevel.NEUTRAL,
        4: SatisfactionLevel.SATISFIED,
        5: SatisfactionLevel.VERY_SATISFIED,
    }

    satisfaction = UserSatisfaction(
        outcome_id=outcome_id,
        feature=feature,
        persona=persona,
        satisfaction_level=levels[rating],
        met_expectations=(rating >= 4),
        would_recommend=recommend,
        effort_score=effort,
        feedback_text=feedback if feedback else None
    )

    track_user_satisfaction(satisfaction)
```

---

## Analytics Dashboard

### Example: Generate JTBD Metrics Report

Analyze collected metrics and generate reports.

```python
from specify_cli.core.jtbd_metrics import (
    JobCompletion,
    OutcomeAchieved,
    PainpointResolved,
)
from collections import defaultdict

class JTBDAnalytics:
    """Analytics for JTBD metrics."""

    def __init__(self) -> None:
        self.jobs: list[JobCompletion] = []
        self.outcomes: list[OutcomeAchieved] = []
        self.painpoints: list[PainpointResolved] = []

    def add_job(self, job: JobCompletion) -> None:
        """Add job to analytics."""
        self.jobs.append(job)

    def add_outcome(self, outcome: OutcomeAchieved) -> None:
        """Add outcome to analytics."""
        self.outcomes.append(outcome)

    def add_painpoint(self, painpoint: PainpointResolved) -> None:
        """Add painpoint to analytics."""
        self.painpoints.append(painpoint)

    def job_completion_rate_by_persona(self) -> dict[str, float]:
        """Calculate job completion rate by persona."""
        persona_stats = defaultdict(lambda: {"completed": 0, "total": 0})

        for job in self.jobs:
            persona_stats[job.persona]["total"] += 1
            if job.status.value == "completed":
                persona_stats[job.persona]["completed"] += 1

        return {
            persona: (stats["completed"] / stats["total"]) * 100
            for persona, stats in persona_stats.items()
        }

    def average_outcome_achievement(self) -> float:
        """Calculate average outcome achievement rate."""
        if not self.outcomes:
            return 0.0

        total_rate = sum(o.achievement_rate for o in self.outcomes)
        return total_rate / len(self.outcomes)

    def average_painpoint_resolution(self) -> float:
        """Calculate average painpoint resolution effectiveness."""
        if not self.painpoints:
            return 0.0

        total_effectiveness = sum(
            p.resolution_effectiveness or 0.0
            for p in self.painpoints
        )
        return total_effectiveness / len(self.painpoints)

    def generate_report(self) -> str:
        """Generate analytics report."""
        report = ["# JTBD Metrics Report\n"]

        # Job completion rates
        report.append("## Job Completion Rates by Persona\n")
        completion_rates = self.job_completion_rate_by_persona()
        for persona, rate in completion_rates.items():
            report.append(f"- {persona}: {rate:.1f}%")

        # Outcome achievement
        report.append(f"\n## Average Outcome Achievement: {self.average_outcome_achievement():.1f}%\n")

        # Painpoint resolution
        report.append(f"\n## Average Painpoint Resolution: {self.average_painpoint_resolution():.1f}%\n")

        # Top performing features
        report.append("\n## Top Features by Outcome Achievement\n")
        feature_outcomes = defaultdict(list)
        for outcome in self.outcomes:
            feature_outcomes[outcome.feature].append(outcome.achievement_rate)

        for feature, rates in sorted(
            feature_outcomes.items(),
            key=lambda x: sum(x[1]) / len(x[1]),
            reverse=True
        ):
            avg_rate = sum(rates) / len(rates)
            report.append(f"- {feature}: {avg_rate:.1f}%")

        return "\n".join(report)

# Usage
analytics = JTBDAnalytics()

# Collect metrics
job = JobCompletion(job_id="deps-add", persona="python-developer", feature_used="specify deps add")
job.complete()
analytics.add_job(job)

outcome = OutcomeAchieved(
    outcome_id="faster-deps",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=25.0,
    feature="specify deps add"
)
analytics.add_outcome(outcome)

# Generate report
report = analytics.generate_report()
console.print(report)
```

---

## A/B Testing

### Example: Compare Two Implementations

Use JTBD metrics to compare feature variants.

```python
from specify_cli.core.jtbd_metrics import OutcomeAchieved, track_outcome_achieved
import random

def ab_test_feature(package: str) -> None:
    """A/B test two implementations."""

    # Randomly assign variant
    variant = "A" if random.random() < 0.5 else "B"

    import time
    start = time.time()

    if variant == "A":
        # Original implementation
        run_uv_add_v1(package)
    else:
        # New implementation
        run_uv_add_v2(package)

    duration = time.time() - start

    # Track outcome with variant
    outcome = OutcomeAchieved(
        outcome_id="faster-dependency-management",
        metric="time_seconds",
        expected_value=30.0,
        actual_value=duration,
        feature=f"specify deps add (variant {variant})",
        context={
            "variant": variant,
            "package": package
        }
    )

    track_outcome_achieved(outcome)
```

---

## Feature Impact Analysis

### Example: Before/After Feature Launch

Measure feature impact over time.

```python
from specify_cli.core.jtbd_metrics import (
    OutcomeAchieved,
    PainpointResolved,
    PainpointCategory,
    track_outcome_achieved,
    track_painpoint_resolved,
)
from datetime import datetime, timedelta

class FeatureImpactTracker:
    """Track feature impact before and after launch."""

    def __init__(self, feature_name: str, launch_date: datetime) -> None:
        self.feature_name = feature_name
        self.launch_date = launch_date
        self.before_metrics: list[OutcomeAchieved] = []
        self.after_metrics: list[OutcomeAchieved] = []

    def track_metric(self, outcome: OutcomeAchieved) -> None:
        """Track metric and categorize by launch date."""
        if datetime.now() < self.launch_date:
            self.before_metrics.append(outcome)
        else:
            self.after_metrics.append(outcome)

        track_outcome_achieved(outcome)

    def calculate_impact(self) -> dict[str, float]:
        """Calculate feature impact."""
        if not self.before_metrics or not self.after_metrics:
            return {}

        before_avg = sum(m.achievement_rate for m in self.before_metrics) / len(self.before_metrics)
        after_avg = sum(m.achievement_rate for m in self.after_metrics) / len(self.after_metrics)

        improvement = after_avg - before_avg
        improvement_pct = (improvement / before_avg) * 100

        return {
            "before_average": before_avg,
            "after_average": after_avg,
            "improvement": improvement,
            "improvement_percent": improvement_pct
        }

# Usage
tracker = FeatureImpactTracker(
    feature_name="specify deps add",
    launch_date=datetime(2025, 1, 15)
)

# Track metrics over time
outcome = OutcomeAchieved(
    outcome_id="faster-deps",
    metric="time_saved_seconds",
    expected_value=30.0,
    actual_value=8.5,
    feature="specify deps add"
)
tracker.track_metric(outcome)

# After enough data collected
impact = tracker.calculate_impact()
console.print(f"Feature impact: {impact['improvement_percent']:.1f}% improvement")
```

---

## See Also

- **[JTBD User Guide](JTBD_USER_GUIDE.md)** - Getting started and configuration
- **[JTBD API Reference](JTBD_API_REFERENCE.md)** - Complete API documentation
- **[RDF Schema](../ontology/jtbd-schema.ttl)** - JTBD ontology specification

---

**Version:** 1.0.0
**Framework:** Jobs-to-be-Done (Clayton Christensen)
**Integration:** OpenTelemetry distributed tracing
