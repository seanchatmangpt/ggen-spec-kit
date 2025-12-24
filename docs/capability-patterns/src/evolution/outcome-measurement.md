# 40. Outcome Measurement

★★

*Features ship. Outcomes deliver. Outcome measurement tracks whether capabilities actually help customers make progress—not just whether they work. This is the difference between activity and impact.*

---

## Beyond Output Metrics

Software teams excel at measuring outputs:
- Lines of code written
- Features shipped
- Bugs fixed
- Tests passing
- Story points completed

These metrics feel productive. They're easy to count. They go up and to the right. Everyone feels good.

But outputs aren't outcomes.

An output is what you produce. An outcome is the change that results. You can ship a hundred features without moving the needle on what customers actually need.

```
OUTPUT                          OUTCOME
──────                          ───────
Feature released          →     Customer progress made
Tests passing             →     Errors prevented
Commands available        →     Time saved
Documentation written     →     Questions answered
Performance optimized     →     Frustration eliminated
```

Outcome measurement bridges this gap. It tracks whether your outputs create the outcomes you intended.

---

## The Measurement Problem

**The fundamental problem: Shipping features feels like progress. But features without outcomes are waste. Outcome measurement reveals whether you're actually helping.**

Consider two teams:

### Team A: Output-Focused
```
Q1 Report:
- Shipped 47 features
- Fixed 203 bugs
- Achieved 95% test coverage
- Maintained <500ms response time

Status: "Crushing it!"
```

### Team B: Outcome-Focused
```
Q1 Report:
- Shipped 12 features
- Customer time-to-value: reduced 40%
- Error recovery time: reduced 60%
- Customer satisfaction: increased from 72% to 89%
- Customer churn: reduced 25%

Status: "Making progress"
```

Team A shipped 4x more features. But which team delivered more value? Team B's customers are happier, more successful, and staying longer.

### The Attribution Challenge

Outcome measurement is harder than output measurement because:

1. **Outcomes are delayed.** You ship a feature today; the outcome manifests weeks later.

2. **Outcomes are influenced by many factors.** Did satisfaction improve because of your feature or because a competitor failed?

3. **Outcomes are subjective.** "Time saved" depends on how users work. "Satisfaction" depends on expectations.

4. **Outcomes require instrumentation.** You can count features without users. You can't measure outcomes without observing usage.

Despite these challenges, outcome measurement is essential. Without it, you're optimizing the wrong things.

---

## The Forces

### Force: Measurement Wants Precision

*Exact numbers feel rigorous. "P99 is 247ms" sounds scientific.*

Precise metrics are seductive. They feel objective, defensible, actionable. But precision without meaning is false rigor.

P99 latency of 247ms vs 251ms—does it matter? Does anyone notice? Does it change behavior?

**Resolution:** Pair precision with meaning. Measure precisely, but interpret relative to impact. A 2% improvement in latency that nobody notices isn't meaningful.

### Force: Outcomes Want Meaning

*Meaningful metrics are often fuzzy. "User satisfaction" is harder to pin down than "response time."*

The metrics that matter most—happiness, productivity, success—are inherently qualitative. They don't reduce to clean numbers.

**Resolution:** Accept meaningful fuzziness over meaningless precision. Satisfaction surveys aren't as precise as latency measurements, but they're more meaningful.

### Force: Attribution Wants Certainty

*Did our change cause the improvement? Or was it something else?*

In complex systems, many things change at once. Users are affected by your features, competitors' features, their own changing needs. Isolating your impact is difficult.

**Resolution:** Use multiple methods. Controlled experiments (A/B tests) for certainty. Correlation analysis for trends. Qualitative feedback for understanding.

### Force: Reality Wants Patience

*Outcomes take time to manifest. You can't ship today and measure tomorrow.*

Feature impact isn't instant. Users must discover features, learn them, incorporate them into workflows, and realize benefits. This takes weeks or months.

**Resolution:** Establish leading and lagging indicators. Leading indicators (feature adoption, engagement) predict lagging outcomes (satisfaction, retention). Track both.

---

## Therefore

**Implement outcome measurement that tracks the metrics defined in your outcome specifications. Connect every capability to measurable customer progress. Make outcomes visible alongside outputs.**

### The Outcome Measurement Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  OUTCOME MEASUREMENT ARCHITECTURE                                              │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ OUTCOME SPECIFICATION (from pattern 5)                                   │  │
│  │                                                                          │  │
│  │  jtbd:MinimizeValidationTime a jtbd:Outcome ;                           │  │
│  │      jtbd:direction "minimize" ;                                        │  │
│  │      jtbd:metric "time" ;                                               │  │
│  │      jtbd:object "discovering syntax errors" ;                          │  │
│  │      jtbd:target "PT5S"^^xsd:duration .                                 │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ MEASUREMENT SPECIFICATION                                                │  │
│  │                                                                          │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │  │
│  │  │   WHAT          │  │   HOW           │  │   WHERE         │          │  │
│  │  │                 │  │                 │  │                 │          │  │
│  │  │ • Metric name   │  │ • Histogram     │  │ • Telemetry     │          │  │
│  │  │ • Unit          │  │ • Counter       │  │ • Survey        │          │  │
│  │  │ • Direction     │  │ • Gauge         │  │ • Analytics     │          │  │
│  │  │ • Target        │  │ • Survey        │  │ • Support       │          │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘          │  │
│  │           │                    │                    │                   │  │
│  │           └────────────────────┼────────────────────┘                   │  │
│  │                                ↓                                         │  │
│  └────────────────────────────────┼────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ DATA COLLECTION                                                          │  │
│  │                                                                          │  │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │  │
│  │  │ TELEMETRY                                                          │  │  │
│  │  │                                                                    │  │  │
│  │  │ validate_duration.record(ms, {"file_size": size, "result": r})    │  │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                          │  │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │  │
│  │  │ SURVEYS                                                            │  │  │
│  │  │                                                                    │  │  │
│  │  │ "How satisfied are you with validation speed?" [1-5]              │  │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                          │  │
│  │  ┌───────────────────────────────────────────────────────────────────┐  │  │
│  │  │ ANALYTICS                                                          │  │  │
│  │  │                                                                    │  │  │
│  │  │ feature_used("validate", user_id, session_id)                     │  │  │
│  │  └───────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ OUTCOME TRACKING                                                         │  │
│  │                                                                          │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │  │                 DASHBOARD                                        │    │  │
│  │  │                                                                  │    │  │
│  │  │  Outcome: Minimize Validation Time                              │    │  │
│  │  │  Target: < 5 seconds                                            │    │  │
│  │  │                                                                  │    │  │
│  │  │  Current:                                                        │    │  │
│  │  │    P50:  1,200ms  ████████████░░░░░░░░  ✓                       │    │  │
│  │  │    P90:  3,500ms  ██████████████████░░  ✓                       │    │  │
│  │  │    P99: 12,000ms  ████████████████████  ✗ EXCEEDS               │    │  │
│  │  │                                                                  │    │  │
│  │  │  Trend: ↓ 15% improvement over 30 days                          │    │  │
│  │  │                                                                  │    │  │
│  │  └─────────────────────────────────────────────────────────────────┘    │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ GAP ANALYSIS & REFINEMENT                                                │  │
│  │                                                                          │  │
│  │  P99 exceeds target → Investigate large files → Stream validation       │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Outcome Specification in RDF

```turtle
# ontology/outcomes.ttl
@prefix jtbd: <http://github.com/spec-kit/jtbd#> .
@prefix sk: <http://github.com/spec-kit/schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# ============================================================================
# Outcome Schema
# ============================================================================

jtbd:Outcome a rdfs:Class ;
    rdfs:label "Outcome" ;
    rdfs:comment "A measurable result that helps customers make progress" .

jtbd:direction a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string ;
    rdfs:comment "Direction of optimization: minimize, maximize, or target" .

jtbd:metric a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string ;
    rdfs:comment "What is being measured: time, errors, effort, etc." .

jtbd:baseline a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:comment "Current/starting performance level" .

jtbd:target a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:comment "Goal performance level" .

jtbd:importance a rdf:Property ;
    rdfs:domain jtbd:Outcome ;
    rdfs:range xsd:string ;
    rdfs:comment "Relative importance: critical, high, medium, low" .

# ============================================================================
# Outcome Definitions
# ============================================================================

jtbd:MinimizeValidationTime a jtbd:Outcome ;
    rdfs:label "Minimize validation time" ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:object "discovering syntax errors" ;
    jtbd:baseline "PT5M"^^xsd:duration ;  # 5 minutes manual inspection
    jtbd:target "PT5S"^^xsd:duration ;    # 5 seconds automated
    jtbd:importance "high" ;
    jtbd:measurementMethod "histogram:validate.duration" ;
    sk:linkedCapability cli:ValidateCommand .

jtbd:MinimizeErrorComprehensionTime a jtbd:Outcome ;
    rdfs:label "Minimize error comprehension time" ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:object "understanding what went wrong" ;
    jtbd:baseline "PT2M"^^xsd:duration ;  # 2 minutes with old errors
    jtbd:target "PT10S"^^xsd:duration ;   # 10 seconds with clear errors
    jtbd:importance "high" ;
    jtbd:measurementMethod "survey:error_comprehension" ;
    sk:linkedCapability cli:ValidateCommand .

jtbd:MaximizeValidationCoverage a jtbd:Outcome ;
    rdfs:label "Maximize validation coverage" ;
    jtbd:direction "maximize" ;
    jtbd:metric "coverage" ;
    jtbd:object "RDF constructs validated" ;
    jtbd:baseline 0.70 ;  # 70% coverage
    jtbd:target 1.0 ;     # 100% coverage
    jtbd:importance "medium" ;
    jtbd:measurementMethod "counter:validation_coverage" ;
    sk:linkedCapability cli:ValidateCommand .

jtbd:MinimizeInitializationEffort a jtbd:Outcome ;
    rdfs:label "Minimize initialization effort" ;
    jtbd:direction "minimize" ;
    jtbd:metric "steps" ;
    jtbd:object "starting a new project" ;
    jtbd:baseline 12 ;  # 12 manual steps
    jtbd:target 1 ;     # 1 command
    jtbd:importance "high" ;
    jtbd:measurementMethod "analytics:init_completion_rate" ;
    sk:linkedCapability cli:InitCommand .

jtbd:MaximizeConfidenceBeforeCommit a jtbd:Outcome ;
    rdfs:label "Maximize confidence before commit" ;
    jtbd:direction "maximize" ;
    jtbd:metric "confidence" ;
    jtbd:object "code quality before committing" ;
    jtbd:baseline 0.6 ;  # 60% confident (survey)
    jtbd:target 0.95 ;   # 95% confident
    jtbd:importance "high" ;
    jtbd:measurementMethod "survey:commit_confidence" ;
    sk:linkedCapability cli:ValidateCommand .
```

### Measurement Implementation

```python
# src/specify_cli/ops/outcomes.py
"""Outcome measurement operations."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from enum import Enum
import statistics

from opentelemetry import metrics


class OutcomeDirection(Enum):
    """Direction of outcome optimization."""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    TARGET = "target"


class MetricType(Enum):
    """Types of metrics for outcome measurement."""
    TIME = "time"
    ERRORS = "errors"
    EFFORT = "effort"
    CONFIDENCE = "confidence"
    COVERAGE = "coverage"
    SUCCESS_RATE = "success_rate"


@dataclass
class OutcomeDefinition:
    """Definition of a measurable outcome."""
    id: str
    label: str
    direction: OutcomeDirection
    metric_type: MetricType
    object_description: str
    baseline: float
    target: float
    importance: str
    measurement_method: str
    linked_capability: str
    unit: Optional[str] = None


@dataclass
class OutcomeMeasurement:
    """A single measurement of an outcome."""
    outcome_id: str
    timestamp: datetime
    value: float
    percentile: Optional[str] = None  # p50, p90, p99
    segment: Optional[str] = None     # user segment
    sample_size: Optional[int] = None


@dataclass
class OutcomeReport:
    """Report on outcome achievement."""
    outcome: OutcomeDefinition
    measurements: List[OutcomeMeasurement]
    current_value: float
    target_achievement: float  # 0-1, how close to target
    trend: float              # positive = improving, negative = degrading
    status: str               # "meeting", "approaching", "missing"
    recommendation: Optional[str] = None


class OutcomeMeasurer:
    """Measure and track outcomes."""

    def __init__(self, telemetry_client, survey_client, analytics_client):
        self.telemetry = telemetry_client
        self.survey = survey_client
        self.analytics = analytics_client

        # Create OpenTelemetry instruments
        meter = metrics.get_meter(__name__)

        self.outcome_gauge = meter.create_gauge(
            name="outcome.current_value",
            description="Current value of outcome metric",
            unit="1"
        )

        self.outcome_target_gauge = meter.create_gauge(
            name="outcome.target_achievement",
            description="How close to target (0-1)",
            unit="1"
        )

    def measure_outcome(
        self,
        outcome: OutcomeDefinition,
        start_time: datetime,
        end_time: datetime
    ) -> OutcomeReport:
        """Measure an outcome over a time period."""

        # Collect measurements based on method
        measurements = self._collect_measurements(
            outcome, start_time, end_time
        )

        if not measurements:
            return OutcomeReport(
                outcome=outcome,
                measurements=[],
                current_value=outcome.baseline,
                target_achievement=0.0,
                trend=0.0,
                status="no_data",
                recommendation="No measurements available"
            )

        # Calculate current value (typically most recent or aggregate)
        current_value = self._calculate_current(measurements, outcome)

        # Calculate target achievement
        target_achievement = self._calculate_achievement(
            current_value, outcome
        )

        # Calculate trend
        trend = self._calculate_trend(measurements)

        # Determine status
        status = self._determine_status(target_achievement, trend)

        # Generate recommendation
        recommendation = self._generate_recommendation(
            outcome, current_value, target_achievement, trend
        )

        # Record to telemetry
        self.outcome_gauge.set(
            current_value,
            {"outcome_id": outcome.id}
        )
        self.outcome_target_gauge.set(
            target_achievement,
            {"outcome_id": outcome.id}
        )

        return OutcomeReport(
            outcome=outcome,
            measurements=measurements,
            current_value=current_value,
            target_achievement=target_achievement,
            trend=trend,
            status=status,
            recommendation=recommendation
        )

    def _collect_measurements(
        self,
        outcome: OutcomeDefinition,
        start: datetime,
        end: datetime
    ) -> List[OutcomeMeasurement]:
        """Collect measurements from appropriate source."""
        method = outcome.measurement_method

        if method.startswith("histogram:"):
            metric_name = method.split(":")[1]
            return self._collect_from_histogram(
                outcome.id, metric_name, start, end
            )
        elif method.startswith("counter:"):
            metric_name = method.split(":")[1]
            return self._collect_from_counter(
                outcome.id, metric_name, start, end
            )
        elif method.startswith("survey:"):
            survey_name = method.split(":")[1]
            return self._collect_from_survey(
                outcome.id, survey_name, start, end
            )
        elif method.startswith("analytics:"):
            event_name = method.split(":")[1]
            return self._collect_from_analytics(
                outcome.id, event_name, start, end
            )
        else:
            return []

    def _collect_from_histogram(
        self,
        outcome_id: str,
        metric_name: str,
        start: datetime,
        end: datetime
    ) -> List[OutcomeMeasurement]:
        """Collect from histogram metric (for latency)."""
        data = self.telemetry.query_histogram(
            metric_name, start, end,
            percentiles=[50, 90, 99]
        )

        measurements = []
        for point in data:
            for percentile, value in point['percentiles'].items():
                measurements.append(OutcomeMeasurement(
                    outcome_id=outcome_id,
                    timestamp=point['timestamp'],
                    value=value,
                    percentile=f"p{percentile}",
                    sample_size=point.get('count')
                ))

        return measurements

    def _collect_from_survey(
        self,
        outcome_id: str,
        survey_name: str,
        start: datetime,
        end: datetime
    ) -> List[OutcomeMeasurement]:
        """Collect from survey responses."""
        responses = self.survey.get_responses(
            survey_name, start, end
        )

        measurements = []
        for response in responses:
            measurements.append(OutcomeMeasurement(
                outcome_id=outcome_id,
                timestamp=response['submitted_at'],
                value=response['score'],
                segment=response.get('user_segment'),
                sample_size=1
            ))

        return measurements

    def _calculate_current(
        self,
        measurements: List[OutcomeMeasurement],
        outcome: OutcomeDefinition
    ) -> float:
        """Calculate current value from measurements."""
        # For histograms, use P99 or P50 depending on outcome
        if outcome.direction == OutcomeDirection.MINIMIZE:
            # For minimize, use worst case (P99)
            p99 = [m.value for m in measurements if m.percentile == "p99"]
            if p99:
                return statistics.mean(p99[-7:])  # Last 7 days

        # For surveys, use mean of recent responses
        recent = sorted(measurements, key=lambda m: m.timestamp)[-50:]
        if recent:
            return statistics.mean(m.value for m in recent)

        return outcome.baseline

    def _calculate_achievement(
        self,
        current: float,
        outcome: OutcomeDefinition
    ) -> float:
        """Calculate how close to target (0-1)."""
        baseline = outcome.baseline
        target = outcome.target

        if outcome.direction == OutcomeDirection.MINIMIZE:
            # For minimize: achievement when current <= target
            if current <= target:
                return 1.0
            elif current >= baseline:
                return 0.0
            else:
                return (baseline - current) / (baseline - target)

        elif outcome.direction == OutcomeDirection.MAXIMIZE:
            # For maximize: achievement when current >= target
            if current >= target:
                return 1.0
            elif current <= baseline:
                return 0.0
            else:
                return (current - baseline) / (target - baseline)

        else:  # TARGET
            # For target: achievement when current == target
            distance = abs(current - target)
            max_distance = abs(baseline - target)
            return 1.0 - min(distance / max_distance, 1.0)

    def _calculate_trend(
        self,
        measurements: List[OutcomeMeasurement]
    ) -> float:
        """Calculate trend (positive = improving)."""
        if len(measurements) < 2:
            return 0.0

        # Simple linear regression on recent measurements
        recent = sorted(measurements, key=lambda m: m.timestamp)[-30:]

        if len(recent) < 2:
            return 0.0

        # Calculate slope
        n = len(recent)
        x_sum = sum(range(n))
        y_sum = sum(m.value for m in recent)
        xy_sum = sum(i * m.value for i, m in enumerate(recent))
        x2_sum = sum(i**2 for i in range(n))

        slope = (n * xy_sum - x_sum * y_sum) / (n * x2_sum - x_sum**2)

        return slope

    def _determine_status(
        self,
        achievement: float,
        trend: float
    ) -> str:
        """Determine outcome status."""
        if achievement >= 0.95:
            return "meeting"
        elif achievement >= 0.7 or trend > 0:
            return "approaching"
        else:
            return "missing"

    def _generate_recommendation(
        self,
        outcome: OutcomeDefinition,
        current: float,
        achievement: float,
        trend: float
    ) -> Optional[str]:
        """Generate recommendation based on status."""
        if achievement >= 0.95:
            return None  # No action needed

        gap = abs(current - outcome.target)

        if outcome.direction == OutcomeDirection.MINIMIZE:
            if trend > 0:  # Getting worse
                return f"Degrading: {outcome.label} increased by {abs(trend):.1%}. Investigate root cause."
            elif achievement < 0.5:
                return f"Large gap: {outcome.label} is {gap:.1f}{outcome.unit or ''} from target. Prioritize improvement."
            else:
                return f"Approaching target for {outcome.label}. Continue current efforts."

        elif outcome.direction == OutcomeDirection.MAXIMIZE:
            if trend < 0:  # Getting worse
                return f"Degrading: {outcome.label} decreased by {abs(trend):.1%}. Investigate root cause."
            elif achievement < 0.5:
                return f"Large gap: {outcome.label} is {gap:.1f}{outcome.unit or ''} from target. Prioritize improvement."
            else:
                return f"Approaching target for {outcome.label}. Continue current efforts."

        return None


def create_outcome_dashboard(
    outcomes: List[OutcomeDefinition],
    measurer: OutcomeMeasurer,
    period_days: int = 30
) -> str:
    """Generate outcome dashboard report."""
    end_time = datetime.now()
    start_time = end_time - timedelta(days=period_days)

    lines = [
        "Outcome Dashboard",
        "═" * 70,
        "",
        f"Period: {start_time.date()} to {end_time.date()}",
        "",
    ]

    # Group by status
    meeting = []
    approaching = []
    missing = []

    for outcome in outcomes:
        report = measurer.measure_outcome(outcome, start_time, end_time)

        if report.status == "meeting":
            meeting.append(report)
        elif report.status == "approaching":
            approaching.append(report)
        else:
            missing.append(report)

    # Missing targets (highest priority)
    if missing:
        lines.append("❌ MISSING TARGET")
        lines.append("-" * 70)
        for report in missing:
            lines.extend(_format_outcome_report(report))
        lines.append("")

    # Approaching targets
    if approaching:
        lines.append("🔄 APPROACHING TARGET")
        lines.append("-" * 70)
        for report in approaching:
            lines.extend(_format_outcome_report(report))
        lines.append("")

    # Meeting targets
    if meeting:
        lines.append("✅ MEETING TARGET")
        lines.append("-" * 70)
        for report in meeting:
            lines.extend(_format_outcome_report(report))
        lines.append("")

    # Summary
    total = len(outcomes)
    lines.append("Summary")
    lines.append("-" * 70)
    lines.append(f"  Meeting target:    {len(meeting)}/{total} ({len(meeting)/total:.0%})")
    lines.append(f"  Approaching:       {len(approaching)}/{total}")
    lines.append(f"  Missing target:    {len(missing)}/{total}")

    return "\n".join(lines)


def _format_outcome_report(report: OutcomeReport) -> List[str]:
    """Format a single outcome report."""
    outcome = report.outcome

    # Progress bar
    achievement_pct = report.target_achievement * 100
    filled = int(achievement_pct / 5)
    bar = "█" * filled + "░" * (20 - filled)

    # Trend indicator
    if report.trend > 0.01:
        trend_str = "↑" if outcome.direction == OutcomeDirection.MAXIMIZE else "↓"
        trend_str += " improving"
    elif report.trend < -0.01:
        trend_str = "↓" if outcome.direction == OutcomeDirection.MAXIMIZE else "↑"
        trend_str += " degrading"
    else:
        trend_str = "→ stable"

    lines = [
        f"  {outcome.label}",
        f"    Target: {outcome.target} | Current: {report.current_value:.1f}",
        f"    Progress: [{bar}] {achievement_pct:.0f}%",
        f"    Trend: {trend_str}",
    ]

    if report.recommendation:
        lines.append(f"    → {report.recommendation}")

    lines.append("")

    return lines
```

### Outcome Measurement in Telemetry

```python
# src/specify_cli/core/outcome_telemetry.py
"""Telemetry instrumentation for outcome measurement."""

from opentelemetry import metrics
from functools import wraps
import time
from typing import Callable, Any


# Get the meter
meter = metrics.get_meter("specify_cli.outcomes")

# Create instruments for common outcomes
validate_duration = meter.create_histogram(
    name="validate.duration",
    description="Time to complete validation",
    unit="ms",
)

error_comprehension = meter.create_histogram(
    name="error.comprehension_time",
    description="Time user spends understanding errors",
    unit="s",
)

init_steps = meter.create_counter(
    name="init.steps_completed",
    description="Steps completed during initialization",
    unit="1",
)

commit_confidence = meter.create_gauge(
    name="commit.confidence_score",
    description="User confidence before commit (0-1)",
    unit="1",
)


def measure_duration(histogram, **attributes):
    """Decorator to measure function duration as outcome."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000

                # Add result status to attributes
                attrs = {**attributes}
                if hasattr(result, 'valid'):
                    attrs['result'] = 'success' if result.valid else 'failure'

                histogram.record(duration_ms, attrs)
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                histogram.record(duration_ms, {**attributes, 'result': 'error'})
                raise
        return wrapper
    return decorator


# Usage example
@measure_duration(validate_duration, capability="validate")
def validate(file_path):
    """Validate with automatic outcome measurement."""
    # ... validation logic ...
    pass
```

---

## Outcome Categories

Different outcomes require different measurement approaches:

### Time Outcomes

**What:** How long something takes
**Direction:** Usually minimize
**Measurement:** Histograms with percentiles

```turtle
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:measurementMethod "histogram:validate.duration" ;
    jtbd:target "PT5S"^^xsd:duration .
```

### Error Outcomes

**What:** Frequency of errors or failures
**Direction:** Minimize
**Measurement:** Error rate counters

```turtle
jtbd:MinimizeValidationErrors a jtbd:Outcome ;
    jtbd:direction "minimize" ;
    jtbd:metric "errors" ;
    jtbd:measurementMethod "counter:validate.errors / counter:validate.total" ;
    jtbd:target 0.01 .  # 1% error rate
```

### Effort Outcomes

**What:** Steps, clicks, or actions required
**Direction:** Minimize
**Measurement:** Step counters, analytics

```turtle
jtbd:MinimizeInitSteps a jtbd:Outcome ;
    jtbd:direction "minimize" ;
    jtbd:metric "steps" ;
    jtbd:measurementMethod "analytics:init_workflow_steps" ;
    jtbd:target 1 .
```

### Confidence Outcomes

**What:** User certainty about actions
**Direction:** Maximize
**Measurement:** Surveys

```turtle
jtbd:MaximizeCommitConfidence a jtbd:Outcome ;
    jtbd:direction "maximize" ;
    jtbd:metric "confidence" ;
    jtbd:measurementMethod "survey:commit_confidence" ;
    jtbd:target 0.95 .  # 95% confident
```

### Success Rate Outcomes

**What:** Completion or achievement rate
**Direction:** Maximize
**Measurement:** Conversion analytics

```turtle
jtbd:MaximizeTaskCompletion a jtbd:Outcome ;
    jtbd:direction "maximize" ;
    jtbd:metric "success_rate" ;
    jtbd:measurementMethod "analytics:task_completion_rate" ;
    jtbd:target 0.95 .
```

---

## Case Study: The Metric Transformation

*A team shifts from output metrics to outcome metrics and discovers the truth.*

### The Before: Output Paradise

The SpecGen team measured their success by outputs:

```
Monthly Dashboard:
- Features shipped: 12
- Bugs fixed: 47
- Test coverage: 91%
- CI pass rate: 98%
- Response time P50: 230ms

Conclusion: "We're crushing it!"
```

Everyone felt productive. Numbers went up. Celebrations happened.

### The Wake-Up Call

Then user feedback arrived:

```
NPS Survey Results:
- Score: 23 (poor)
- Top complaint: "It's confusing"
- Second complaint: "I don't know if it worked"
- Third complaint: "Takes forever for big projects"
```

How could NPS be 23 when all their metrics were green?

### The Investigation

They mapped their outputs to outcomes:

| Output | Assumed Outcome | Actual Outcome |
|--------|-----------------|----------------|
| 12 features | Users can do more | Users confused by options |
| 47 bugs fixed | Fewer errors | Same error rate (different bugs) |
| 91% test coverage | Confidence | Tests pass but users fail |
| 230ms P50 | Fast | P99 is 15 seconds (big projects) |

The outputs were real. The assumed outcomes were not.

### The Transformation

They implemented outcome measurement:

**Step 1: Define Outcomes**
```turtle
jtbd:MinimizeTimeToSuccess a jtbd:Outcome ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:object "completing first successful project" ;
    jtbd:baseline "PT4H"^^xsd:duration ;
    jtbd:target "PT30M"^^xsd:duration .

jtbd:MaximizeFirstAttemptSuccess a jtbd:Outcome ;
    jtbd:direction "maximize" ;
    jtbd:metric "success_rate" ;
    jtbd:object "projects succeeding on first attempt" ;
    jtbd:baseline 0.35 ;
    jtbd:target 0.85 .
```

**Step 2: Instrument**
```python
# Track time to success
project_duration = meter.create_histogram(
    "project.time_to_success", unit="s"
)

# Track first attempt success
first_attempt = meter.create_counter(
    "project.first_attempt_result"
)
```

**Step 3: Measure**
```
Week 1 Baseline:
- Time to success: 4.2 hours (median)
- First attempt success: 35%
- User comprehension: 2.1/5
```

**Step 4: Improve Based on Outcomes**

Instead of shipping more features, they:
- Simplified the interface (removed 3 features)
- Added progressive disclosure
- Improved error messages with examples
- Added a guided "first project" flow

### The Results

Three months later:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Features | 47 | 32 | -32% |
| Time to success | 4.2h | 35min | -86% |
| First attempt success | 35% | 78% | +123% |
| User comprehension | 2.1/5 | 4.2/5 | +100% |
| NPS | 23 | 61 | +165% |

Fewer features, better outcomes. Outputs down, impact up.

---

## Anti-Patterns

### Anti-Pattern: Vanity Metrics

*"We have 1 million downloads!"*

Downloads, page views, registered users—these feel impressive but don't indicate value delivered.

**Resolution:** Trace to outcomes. 1 million downloads is meaningless. 100,000 active users is better. 50,000 users achieving their goals is best.

### Anti-Pattern: Gaming Metrics

*"P50 latency is great! (P99 is terrible but we don't measure it)"*

When teams are measured on metrics, they optimize for those specific metrics—sometimes at the expense of actual outcomes.

**Resolution:** Measure what matters, not what's easy. Include percentiles that capture real user experience. Audit for gaming.

### Anti-Pattern: Measurement Theater

*"We measure everything! We have 10,000 dashboards!"*

Measuring everything means drowning in data. Important signals lost in noise.

**Resolution:** Curate ruthlessly. A few meaningful outcome metrics beat thousands of meaningless ones.

### Anti-Pattern: Trailing-Only Metrics

*"Churn increased this quarter. Better figure out why."*

Trailing metrics arrive too late for intervention. By the time you see churn, users have left.

**Resolution:** Pair trailing metrics with leading indicators. Feature adoption predicts retention. Engagement predicts satisfaction.

---

## Implementation Checklist

### Outcome Definition

- [ ] Identify key outcomes for each capability
- [ ] Define direction (minimize/maximize/target)
- [ ] Set baseline from current performance
- [ ] Set target from user research
- [ ] Assign importance rating
- [ ] Specify measurement method

### Instrumentation

- [ ] Create telemetry instruments for each outcome
- [ ] Implement measurement in code
- [ ] Add appropriate attributes for segmentation
- [ ] Test measurement accuracy

### Collection

- [ ] Configure data collection pipeline
- [ ] Set up survey mechanisms for subjective outcomes
- [ ] Integrate with analytics for behavioral outcomes
- [ ] Establish data retention policies

### Reporting

- [ ] Create outcome dashboard
- [ ] Configure alerting for degradation
- [ ] Set up regular reporting cadence
- [ ] Share with stakeholders

### Process

- [ ] Include outcome review in sprint ceremonies
- [ ] Link roadmap decisions to outcome impact
- [ ] Celebrate outcome improvements, not just shipping

---

## Exercises

### Exercise 1: Output to Outcome

For each output metric, identify the assumed outcome and design how to measure it:

| Output Metric | Assumed Outcome | How to Measure |
|--------------|-----------------|----------------|
| Tests passing | | |
| Response time | | |
| Features shipped | | |
| Documentation pages | | |

### Exercise 2: Define an Outcome

Create a complete outcome definition for a capability you maintain:

```turtle
jtbd:YOUR_OUTCOME a jtbd:Outcome ;
    rdfs:label "???" ;
    jtbd:direction "???" ;
    jtbd:metric "???" ;
    jtbd:object "???" ;
    jtbd:baseline ??? ;
    jtbd:target ??? ;
    jtbd:importance "???" ;
    jtbd:measurementMethod "???" .
```

### Exercise 3: Instrument a Function

Add outcome measurement to an existing function:

```python
def your_function(args):
    # TODO: Add start time capture

    # ... existing logic ...

    # TODO: Record outcome metric
    # TODO: Include relevant attributes

    return result
```

---

## Resulting Context

After implementing this pattern, you have:

- **Tracking of outcome metrics, not just output metrics** — measuring impact, not activity
- **Visibility into whether capabilities deliver value** — know if you're helping
- **Data for prioritization decisions** — invest in what moves outcomes
- **Foundation for continuous improvement** — feedback loop has meaningful input
- **Aligned incentives** — teams rewarded for impact, not output

Outcome measurement transforms development from feature factory to value delivery. You stop counting features and start measuring progress.

---

## Code References

The following spec-kit source files implement outcome measurement:

| Reference | Description |
|-----------|-------------|
| `ontology/jtbd-schema.ttl:51-108` | Outcome class with direction, metric, object properties |
| `ontology/jtbd-schema.ttl:110-112` | OutcomeMetric enumeration (time, count, rate, quality) |
| `ontology/jtbd-schema.ttl:889-920` | DesiredOutcomeShape for outcome validation |
| `src/specify_cli/core/jtbd_metrics.py:50-100` | Instrumentation tracking outcome metrics |

---

## Related Patterns

- **Measures:** **[5. Outcome Desired](../context/outcome-desired.md)** — Outcomes defined in context
- **Uses:** **[38. Observable Execution](../verification/observable-execution.md)** — Telemetry provides data
- **Feeds:** **[41. Gap Analysis](./gap-analysis.md)** — Reveals gaps between current and target
- **Informs:** **[42. Specification Refinement](./specification-refinement.md)** — Guides what to improve

---

## Philosophical Note

> *"You can't manage what you can't measure. But you can certainly measure the wrong things."*

This wisdom cuts both ways. Measurement is necessary—without it, you're guessing. But measuring the wrong things is worse than not measuring at all. It creates false confidence. It misdirects effort.

Output metrics are the wrong things. They measure your activity, not your impact. They make you feel productive while customers struggle.

Outcome metrics are the right things. They measure customer progress. They align your work with customer value. They tell the truth about whether you're helping.

Measure outcomes. The truth may be uncomfortable, but it's the only path to actual progress.

---

**Next:** Learn how **[41. Gap Analysis](./gap-analysis.md)** compares current performance against targets to reveal improvement opportunities.
