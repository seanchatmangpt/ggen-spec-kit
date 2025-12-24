# 41. Gap Analysis

★★

*Where are we falling short? Gap analysis compares current performance against targets and expectations, revealing opportunities for improvement. This is how you discover what matters most to fix.*

---

## The Space Between

Every capability exists in two states: where it is and where it should be. The distance between these states is the gap.

**[Outcome Measurement](./outcome-measurement.md)** shows current performance. But performance in isolation isn't actionable. You need context:

- How does current compare to target?
- Which outcomes have the largest gaps?
- Which gaps matter most to customers?
- What's causing the gaps?

Gap analysis provides this context. It transforms raw metrics into prioritized improvement opportunities. Without it, you might optimize the wrong things—closing small gaps while ignoring large ones, improving unimportant metrics while critical ones languish.

---

## The Prioritization Problem

**The fundamental problem: Knowing current performance isn't enough. Gap analysis reveals where improvement efforts will have the most impact. Without it, you optimize blindly.**

Consider a capability with these outcome metrics:

```
Outcome A: Target 100ms, Current 150ms   (50% gap)
Outcome B: Target 5 steps, Current 7 steps   (40% gap)
Outcome C: Target 99% success, Current 92%   (7% gap)
Outcome D: Target 10s, Current 12s   (20% gap)
```

Which should you fix first? Raw percentages don't tell you. You need to weight by importance:

```
Outcome A: 50% gap × Medium importance = Priority 2.0
Outcome B: 40% gap × Low importance = Priority 0.8
Outcome C: 7% gap × Critical importance = Priority 3.5  ← FIX THIS FIRST
Outcome D: 20% gap × High importance = Priority 1.6
```

Outcome C has the smallest percentage gap but the highest priority because importance dominates. Gap analysis reveals this.

### The Invisible Gaps

Some gaps are invisible without analysis:

1. **Segment gaps**: Overall metrics are fine, but a specific user segment is struggling.
2. **Edge case gaps**: P50 is great, but P99 is terrible.
3. **Trend gaps**: Current is acceptable, but trajectory leads to problems.
4. **Relative gaps**: You meet your target, but competitors do better.

Gap analysis surfaces these hidden issues.

### The Root Cause Connection

Gaps without causes are frustrating. "Latency is too high" isn't actionable. "Latency is too high because we're loading all records instead of paginating" is actionable.

Gap analysis connects gaps to root causes, turning complaints into fixes.

---

## The Forces

### Force: Resources Are Limited

*You can't improve everything at once. Some gaps must wait.*

Every team has finite time, energy, and budget. Trying to close all gaps simultaneously means closing none effectively.

**Resolution:** Prioritize ruthlessly. Close high-priority gaps first. Let low-priority gaps wait.

### Force: Importance Varies

*Not all gaps matter equally. Some outcomes are critical; others are nice-to-have.*

A 10% gap in critical functionality matters more than a 50% gap in minor features.

**Resolution:** Weight gaps by importance. Use customer research to determine which outcomes matter most.

### Force: Causes Differ

*Different gaps need different solutions. Some are quick fixes; others are architectural.*

A configuration change can fix one gap. Another requires redesigning the system.

**Resolution:** Estimate effort alongside impact. A small gap that's easy to close might be worth fixing before a large gap that's expensive.

### Force: Priorities Compete

*Everyone thinks their area is most important. Stakeholders advocate for their concerns.*

Without objective analysis, the loudest voice wins—not the most important gap.

**Resolution:** Use data. Gap analysis provides objective prioritization that stakeholders can align around.

---

## Therefore

**Perform structured gap analysis that combines outcome measurement with importance ratings to identify high-priority improvement opportunities. Prioritize by impact, not by who complains loudest.**

### The Gap Analysis Formula

```
Priority = Importance × Gap / Effort
```

Where:
- **Importance**: How much customers care (1-5 scale)
- **Gap**: Distance from target as percentage
- **Effort**: Estimated work to close gap (optional refinement)

High importance + large gap + low effort = highest priority.

### Gap Analysis Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  GAP ANALYSIS ARCHITECTURE                                                     │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ INPUT: OUTCOME MEASUREMENTS                                              │  │
│  │                                                                          │  │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐          │  │
│  │  │ Outcome A       │  │ Outcome B       │  │ Outcome C       │          │  │
│  │  │                 │  │                 │  │                 │          │  │
│  │  │ Target: 100ms   │  │ Target: 5 steps │  │ Target: 99%     │          │  │
│  │  │ Current: 150ms  │  │ Current: 7      │  │ Current: 92%    │          │  │
│  │  │ Importance: 3   │  │ Importance: 2   │  │ Importance: 5   │          │  │
│  │  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘          │  │
│  │           │                    │                    │                   │  │
│  │           └────────────────────┼────────────────────┘                   │  │
│  │                                ↓                                         │  │
│  └────────────────────────────────┼────────────────────────────────────────┘  │
│                                   │                                            │
│  ┌────────────────────────────────┼────────────────────────────────────────┐  │
│  │ PROCESS: GAP CALCULATION       │                                         │  │
│  │                                ↓                                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │  │ For each outcome:                                                │    │  │
│  │  │                                                                  │    │  │
│  │  │   Gap = (Target - Current) / Target                             │    │  │
│  │  │   Priority = Importance × Gap                                    │    │  │
│  │  │                                                                  │    │  │
│  │  │ ┌─────────────────────────────────────────────────────────────┐ │    │  │
│  │  │ │ Outcome A: Gap = 33%, Priority = 3 × 0.33 = 1.0             │ │    │  │
│  │  │ │ Outcome B: Gap = 40%, Priority = 2 × 0.40 = 0.8             │ │    │  │
│  │  │ │ Outcome C: Gap = 7%,  Priority = 5 × 0.07 = 0.35            │ │    │  │
│  │  │ └─────────────────────────────────────────────────────────────┘ │    │  │
│  │  │                                                                  │    │  │
│  │  │ Wait... that doesn't match intuition!                           │    │  │
│  │  │                                                                  │    │  │
│  │  │ Use weighted formula:                                            │    │  │
│  │  │   Priority = Importance² × Gap                                   │    │  │
│  │  │                                                                  │    │  │
│  │  │ ┌─────────────────────────────────────────────────────────────┐ │    │  │
│  │  │ │ Outcome A: Priority = 9 × 0.33 = 3.0                        │ │    │  │
│  │  │ │ Outcome B: Priority = 4 × 0.40 = 1.6                        │ │    │  │
│  │  │ │ Outcome C: Priority = 25 × 0.07 = 1.75                      │ │    │  │
│  │  │ └─────────────────────────────────────────────────────────────┘ │    │  │
│  │  │                                                                  │    │  │
│  │  │ Now critical importance weighs more heavily                     │    │  │
│  │  └─────────────────────────────────────────────────────────────────┘    │  │
│  │                                │                                         │  │
│  │                                ↓                                         │  │
│  └────────────────────────────────┼────────────────────────────────────────┘  │
│                                   │                                            │
│  ┌────────────────────────────────┼────────────────────────────────────────┐  │
│  │ OUTPUT: PRIORITIZED GAP REPORT │                                         │  │
│  │                                ↓                                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │  │
│  │  │ HIGH PRIORITY (Priority > 2.0)                                   │    │  │
│  │  │ ─────────────────────────────────────────────────────────────── │    │  │
│  │  │ 1. Outcome A: Latency exceeds target                            │    │  │
│  │  │    Gap: 33% | Importance: HIGH | Priority: 3.0                  │    │  │
│  │  │    Root cause: Sequential processing                            │    │  │
│  │  │    Recommendation: Implement streaming                          │    │  │
│  │  │                                                                  │    │  │
│  │  │ MEDIUM PRIORITY (Priority 1.0-2.0)                               │    │  │
│  │  │ ─────────────────────────────────────────────────────────────── │    │  │
│  │  │ 2. Outcome C: Success rate below target                         │    │  │
│  │  │    Gap: 7% | Importance: CRITICAL | Priority: 1.75              │    │  │
│  │  │    Root cause: Edge case failures                               │    │  │
│  │  │    Recommendation: Add edge case handling                       │    │  │
│  │  │                                                                  │    │  │
│  │  │ 3. Outcome B: Too many steps                                    │    │  │
│  │  │    Gap: 40% | Importance: LOW | Priority: 1.6                   │    │  │
│  │  │    Root cause: Manual steps in workflow                         │    │  │
│  │  │    Recommendation: Automate steps 3-5                           │    │  │
│  │  └─────────────────────────────────────────────────────────────────┘    │  │
│  │                                                                          │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Gap Analysis Query in SPARQL

```sparql
# sparql/gap-analysis.rq
# Find outcomes with significant gaps, prioritized by importance

PREFIX jtbd: <http://github.com/spec-kit/jtbd#>
PREFIX sk: <http://github.com/spec-kit/schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?outcome ?label ?importance ?target ?current ?gap ?priority
WHERE {
    ?outcome a jtbd:Outcome ;
             rdfs:label ?label ;
             jtbd:importance ?importanceStr ;
             jtbd:target ?target ;
             jtbd:currentPerformance ?current .

    # Convert importance to numeric
    BIND(
        IF(?importanceStr = "critical", 5,
        IF(?importanceStr = "high", 4,
        IF(?importanceStr = "medium", 3,
        IF(?importanceStr = "low", 2, 1))))
        AS ?importance
    )

    # Calculate gap (as positive value regardless of direction)
    BIND(ABS(?target - ?current) / ?target AS ?gap)

    # Calculate priority (importance squared × gap)
    BIND(?importance * ?importance * ?gap AS ?priority)
}
ORDER BY DESC(?priority)
```

### Gap Analysis in Python

```python
# src/specify_cli/ops/gap_analysis.py
"""Gap analysis operations for outcome prioritization."""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import math


class Importance(Enum):
    """Outcome importance levels."""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    MINIMAL = 1


class GapStatus(Enum):
    """Status of gap relative to target."""
    EXCEEDS = "exceeds"      # Beyond target (good for maximize, bad for minimize)
    MEETS = "meets"          # At or near target
    APPROACHING = "approaching"  # Making progress
    MISSING = "missing"      # Significant gap
    REGRESSING = "regressing"    # Getting worse


@dataclass
class OutcomeGap:
    """Analysis of gap for a single outcome."""
    outcome_id: str
    label: str
    importance: Importance
    target: float
    current: float
    baseline: float
    gap_percentage: float
    priority_score: float
    status: GapStatus
    trend: float  # positive = improving
    root_cause: Optional[str] = None
    recommendation: Optional[str] = None
    effort_estimate: Optional[str] = None


@dataclass
class GapAnalysisReport:
    """Complete gap analysis report."""
    period: str
    total_outcomes: int
    outcomes_meeting_target: int
    outcomes_approaching: int
    outcomes_missing: int
    high_priority_gaps: List[OutcomeGap]
    medium_priority_gaps: List[OutcomeGap]
    low_priority_gaps: List[OutcomeGap]
    summary_recommendations: List[str]


class GapAnalyzer:
    """Analyze gaps between current performance and targets."""

    def __init__(
        self,
        priority_threshold_high: float = 2.0,
        priority_threshold_medium: float = 0.5
    ):
        self.priority_threshold_high = priority_threshold_high
        self.priority_threshold_medium = priority_threshold_medium

    def analyze_outcome(
        self,
        outcome_id: str,
        label: str,
        importance: Importance,
        target: float,
        current: float,
        baseline: float,
        direction: str = "minimize",
        trend: float = 0.0,
        root_cause: Optional[str] = None
    ) -> OutcomeGap:
        """Analyze gap for a single outcome."""

        # Calculate gap percentage
        if direction == "minimize":
            # For minimize: gap is how much current exceeds target
            if current <= target:
                gap_percentage = 0.0
            else:
                gap_percentage = (current - target) / target
        else:  # maximize
            # For maximize: gap is how much current falls short of target
            if current >= target:
                gap_percentage = 0.0
            else:
                gap_percentage = (target - current) / target

        # Calculate priority score (importance² × gap)
        priority_score = (importance.value ** 2) * gap_percentage

        # Determine status
        status = self._determine_status(gap_percentage, trend)

        # Generate recommendation if not provided
        recommendation = self._generate_recommendation(
            label, gap_percentage, importance, direction
        ) if not root_cause else f"Address: {root_cause}"

        return OutcomeGap(
            outcome_id=outcome_id,
            label=label,
            importance=importance,
            target=target,
            current=current,
            baseline=baseline,
            gap_percentage=gap_percentage,
            priority_score=priority_score,
            status=status,
            trend=trend,
            root_cause=root_cause,
            recommendation=recommendation
        )

    def analyze_all(
        self,
        outcomes: List[Dict[str, Any]]
    ) -> GapAnalysisReport:
        """Analyze gaps for all outcomes."""

        gaps = []
        for outcome in outcomes:
            gap = self.analyze_outcome(
                outcome_id=outcome['id'],
                label=outcome['label'],
                importance=Importance[outcome['importance'].upper()],
                target=outcome['target'],
                current=outcome['current'],
                baseline=outcome['baseline'],
                direction=outcome.get('direction', 'minimize'),
                trend=outcome.get('trend', 0.0),
                root_cause=outcome.get('root_cause')
            )
            gaps.append(gap)

        # Sort by priority
        gaps.sort(key=lambda g: g.priority_score, reverse=True)

        # Categorize by priority
        high = [g for g in gaps if g.priority_score >= self.priority_threshold_high]
        medium = [g for g in gaps if self.priority_threshold_medium <= g.priority_score < self.priority_threshold_high]
        low = [g for g in gaps if g.priority_score < self.priority_threshold_medium]

        # Count by status
        meeting = sum(1 for g in gaps if g.status == GapStatus.MEETS)
        approaching = sum(1 for g in gaps if g.status == GapStatus.APPROACHING)
        missing = sum(1 for g in gaps if g.status in [GapStatus.MISSING, GapStatus.REGRESSING])

        # Generate summary recommendations
        summary = self._generate_summary_recommendations(high, medium)

        return GapAnalysisReport(
            period="current",
            total_outcomes=len(gaps),
            outcomes_meeting_target=meeting,
            outcomes_approaching=approaching,
            outcomes_missing=missing,
            high_priority_gaps=high,
            medium_priority_gaps=medium,
            low_priority_gaps=low,
            summary_recommendations=summary
        )

    def _determine_status(self, gap: float, trend: float) -> GapStatus:
        """Determine gap status from gap percentage and trend."""
        if gap <= 0.05:  # Within 5% of target
            return GapStatus.MEETS
        elif gap <= 0.2 and trend < 0:  # Within 20% and improving
            return GapStatus.APPROACHING
        elif trend > 0.1:  # Getting significantly worse
            return GapStatus.REGRESSING
        else:
            return GapStatus.MISSING

    def _generate_recommendation(
        self,
        label: str,
        gap: float,
        importance: Importance,
        direction: str
    ) -> str:
        """Generate recommendation based on gap analysis."""
        if gap <= 0.05:
            return f"Maintain current performance for {label}"

        severity = "urgent" if importance.value >= 4 else "recommended"
        gap_str = f"{gap:.0%}"

        if direction == "minimize":
            return f"{severity.capitalize()}: Reduce {label} by {gap_str} to meet target"
        else:
            return f"{severity.capitalize()}: Increase {label} by {gap_str} to meet target"

    def _generate_summary_recommendations(
        self,
        high: List[OutcomeGap],
        medium: List[OutcomeGap]
    ) -> List[str]:
        """Generate summary recommendations from gap analysis."""
        recommendations = []

        if high:
            recommendations.append(
                f"IMMEDIATE: Address {len(high)} high-priority gaps"
            )
            # Top 3 specific recommendations
            for gap in high[:3]:
                if gap.recommendation:
                    recommendations.append(f"  → {gap.recommendation}")

        if medium:
            recommendations.append(
                f"PLANNED: Schedule {len(medium)} medium-priority improvements"
            )

        return recommendations


def generate_gap_report(
    analyzer: GapAnalyzer,
    report: GapAnalysisReport
) -> str:
    """Generate formatted gap analysis report."""
    lines = [
        "Outcome Gap Analysis",
        "═" * 70,
        "",
        f"Period: {report.period}",
        f"Total outcomes: {report.total_outcomes}",
        f"  Meeting target: {report.outcomes_meeting_target}",
        f"  Approaching: {report.outcomes_approaching}",
        f"  Missing: {report.outcomes_missing}",
        "",
    ]

    if report.high_priority_gaps:
        lines.append("HIGH PRIORITY (Gap Score > 2.0)")
        lines.append("-" * 70)
        for i, gap in enumerate(report.high_priority_gaps, 1):
            lines.extend(_format_gap(i, gap))
        lines.append("")

    if report.medium_priority_gaps:
        lines.append("MEDIUM PRIORITY (Gap Score 0.5-2.0)")
        lines.append("-" * 70)
        for i, gap in enumerate(report.medium_priority_gaps, 1):
            lines.extend(_format_gap(i, gap))
        lines.append("")

    if report.low_priority_gaps:
        lines.append("LOW PRIORITY (Gap Score < 0.5)")
        lines.append("-" * 70)
        for i, gap in enumerate(report.low_priority_gaps, 1):
            lines.extend(_format_gap(i, gap))
        lines.append("")

    if report.summary_recommendations:
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 70)
        for rec in report.summary_recommendations:
            lines.append(rec)

    return "\n".join(lines)


def _format_gap(index: int, gap: OutcomeGap) -> List[str]:
    """Format a single gap for report."""
    status_symbols = {
        GapStatus.MEETS: "✓",
        GapStatus.APPROACHING: "→",
        GapStatus.MISSING: "✗",
        GapStatus.REGRESSING: "↓",
        GapStatus.EXCEEDS: "★"
    }

    trend_str = ""
    if gap.trend > 0.01:
        trend_str = " ↑ improving"
    elif gap.trend < -0.01:
        trend_str = " ↓ degrading"

    return [
        f"{index}. {gap.label}",
        f"   Importance: {gap.importance.name}",
        f"   Target: {gap.target} | Current: {gap.current}",
        f"   Gap: {gap.gap_percentage:.0%} | Priority: {gap.priority_score:.2f}{trend_str}",
        f"   {status_symbols[gap.status]} Status: {gap.status.value}",
        f"",
        f"   {gap.root_cause or 'Root cause: Unknown'}",
        f"   → {gap.recommendation}",
        "",
    ]
```

### Gap Tracking Over Time in RDF

```turtle
# memory/gap-history.ttl
@prefix jtbd: <http://github.com/spec-kit/jtbd#> .
@prefix sk: <http://github.com/spec-kit/schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Track gap evolution over time
jtbd:MinimizeValidationTime
    jtbd:gapHistory [
        jtbd:date "2025-01-01"^^xsd:date ;
        jtbd:target "PT5S"^^xsd:duration ;
        jtbd:current "PT12S"^^xsd:duration ;
        jtbd:gap 1.4 ;  # 140% over target
        jtbd:priority 5.6 ;
        jtbd:status "missing"
    ] ;
    jtbd:gapHistory [
        jtbd:date "2025-02-01"^^xsd:date ;
        jtbd:target "PT5S"^^xsd:duration ;
        jtbd:current "PT8S"^^xsd:duration ;
        jtbd:gap 0.6 ;  # 60% over target
        jtbd:priority 2.4 ;
        jtbd:status "approaching" ;
        jtbd:improvement "Implemented streaming for large files"
    ] ;
    jtbd:gapHistory [
        jtbd:date "2025-03-01"^^xsd:date ;
        jtbd:target "PT5S"^^xsd:duration ;
        jtbd:current "PT5.5S"^^xsd:duration ;
        jtbd:gap 0.1 ;  # 10% over target
        jtbd:priority 0.4 ;
        jtbd:status "approaching" ;
        jtbd:improvement "Optimized template rendering"
    ] ;
    jtbd:gapHistory [
        jtbd:date "2025-04-01"^^xsd:date ;
        jtbd:target "PT5S"^^xsd:duration ;
        jtbd:current "PT4.8S"^^xsd:duration ;
        jtbd:gap 0.0 ;  # At target
        jtbd:priority 0.0 ;
        jtbd:status "meets" ;
        jtbd:note "Target achieved!"
    ] .
```

---

## The Importance-Satisfaction Matrix

Gap analysis can be visualized using an importance-satisfaction matrix:

```
                        SATISFACTION
                        Low         High
                  ┌──────────┬──────────┐
              High│ PRIORITY │ MAINTAIN │
   IMPORTANCE     │          │          │
                  │  Fix     │  Protect │
                  │  First!  │  Success │
                  ├──────────┼──────────┤
              Low │ IGNORE   │ REDUCE   │
                  │          │          │
                  │  Later   │ Potential│
                  │  (maybe) │ Overkill │
                  └──────────┴──────────┘
```

**PRIORITY (High Importance, Low Satisfaction)**: Fix these first. Customers care deeply but aren't satisfied.

**MAINTAIN (High Importance, High Satisfaction)**: Protect these. Customers care and are happy—don't break them.

**IGNORE (Low Importance, Low Satisfaction)**: Address later or never. Customers don't care much and aren't satisfied—probably not worth fixing.

**REDUCE (Low Importance, High Satisfaction)**: Potential over-investment. Customers don't care much but are very satisfied—might be spending too much effort here.

---

## Case Study: The Priority Revelation

*A team uses gap analysis to discover their priorities were backwards.*

### The Before

The PriorityBlind team had these improvement initiatives:

1. **Project Alpha**: Speed up initialization (5 engineers, 3 months)
2. **Project Beta**: Add batch mode (3 engineers, 2 months)
3. **Project Gamma**: Improve error messages (1 engineer, 2 weeks)

Priority was assigned by engineering effort and technical interest.

### The Gap Analysis

They conducted gap analysis on their outcomes:

```
OUTCOME GAP ANALYSIS
═══════════════════════════════════════════════════════════════════

HIGH PRIORITY
─────────────────────────────────────────────────────────────────

1. Minimize error comprehension time
   Importance: CRITICAL (5)
   Target: 10 seconds
   Current: 120 seconds
   Gap: 1100% | Priority: 27.5

   Root cause: Technical error messages without context
   Recommendation: Add plain-language explanations

2. Maximize first-attempt success rate
   Importance: HIGH (4)
   Target: 90%
   Current: 45%
   Gap: 50% | Priority: 8.0

   Root cause: Confusing options and unclear defaults
   Recommendation: Simplify common path

MEDIUM PRIORITY
─────────────────────────────────────────────────────────────────

3. Minimize initialization time
   Importance: MEDIUM (3)
   Target: 30 seconds
   Current: 45 seconds
   Gap: 50% | Priority: 4.5

   Root cause: Sequential dependency loading
   Recommendation: Parallelize dependency resolution

LOW PRIORITY
─────────────────────────────────────────────────────────────────

4. Support batch operations
   Importance: LOW (2)
   Target: 100 files
   Current: 1 file
   Gap: 99% | Priority: 3.96

   Root cause: Single-file architecture
   Recommendation: Defer unless demand increases
```

### The Revelation

Their original prioritization was exactly backwards:

| Project | Original Priority | Gap Priority | Investment |
|---------|------------------|--------------|------------|
| Alpha (init speed) | 1 | 3 (Medium) | 15 eng-months |
| Beta (batch mode) | 2 | 4 (Low) | 6 eng-months |
| Gamma (errors) | 3 | 1 (Critical) | 0.5 eng-months |

Project Gamma—the smallest, lowest-priority initiative—addressed their highest-priority gap. They were about to spend 21 engineer-months on low-priority work while ignoring critical issues.

### The Reprioritization

After gap analysis:

1. **Project Gamma (errors)**: Immediate start, 1 engineer, 2 weeks
2. **Project Delta (first-attempt success)**: New initiative, 2 engineers, 1 month
3. **Project Alpha (init speed)**: Reduced scope, 2 engineers, 1 month
4. **Project Beta (batch mode)**: Deferred pending customer demand

### The Results

| Metric | Before | After 3 Months |
|--------|--------|----------------|
| Error comprehension time | 120s | 15s |
| First-attempt success | 45% | 78% |
| Initialization time | 45s | 40s |
| Customer satisfaction | 62% | 87% |
| Support tickets | 47/week | 12/week |

Same engineering time, dramatically better outcomes.

---

## Anti-Patterns

### Anti-Pattern: Priority by Volume

*"We got 50 feature requests for batch mode and only 5 about errors. Batch mode must be more important."*

Volume indicates noise, not importance. A critical issue affecting everyone might generate few complaints because users give up instead of complaining.

**Resolution:** Weight by importance, not volume. Survey to determine importance independently of request count.

### Anti-Pattern: Priority by Squeaky Wheel

*"The enterprise client keeps complaining about performance. That's our top priority."*

The loudest customer isn't necessarily the most important issue. Enterprise clients have more leverage to complain, not necessarily more important problems.

**Resolution:** Analyze gaps across all segments. Enterprise concerns might be real but lower priority than issues affecting everyone.

### Anti-Pattern: Priority by Recency

*"Users just complained about slow exports. Let's fix that first."*

Recent complaints feel urgent. But urgency isn't importance. The slow export might be a minor annoyance while older, ignored issues cause real pain.

**Resolution:** Systematic gap analysis on regular cadence. Don't let recency bias distort priorities.

### Anti-Pattern: Ignoring Easy Wins

*"The big gaps are the important ones. We'll fix small gaps later."*

Sometimes small gaps are easy to close, providing quick wins that build momentum.

**Resolution:** Include effort in prioritization. A small gap that takes an hour to close might be worth doing before a large gap that takes months.

---

## Implementation Checklist

### Data Collection

- [ ] Define all outcomes with targets
- [ ] Implement outcome measurement for each
- [ ] Assign importance ratings (validated with customers)
- [ ] Track current performance continuously
- [ ] Record trend data over time

### Gap Calculation

- [ ] Calculate gap percentage for each outcome
- [ ] Compute priority scores (importance × gap)
- [ ] Sort outcomes by priority
- [ ] Categorize into high/medium/low priority
- [ ] Identify segment-specific gaps

### Root Cause Analysis

- [ ] Investigate top priority gaps
- [ ] Document root causes
- [ ] Estimate effort to close each gap
- [ ] Identify dependencies between gaps

### Reporting

- [ ] Generate gap analysis report
- [ ] Create importance-satisfaction matrix
- [ ] Track gap trends over time
- [ ] Share with stakeholders

### Action

- [ ] Reprioritize roadmap based on gaps
- [ ] Create improvement initiatives for top gaps
- [ ] Set gap closure targets
- [ ] Measure improvement after changes

---

## Exercises

### Exercise 1: Calculate Gap Priority

Given these outcomes, calculate priority scores and rank:

| Outcome | Importance | Target | Current |
|---------|------------|--------|---------|
| Latency | High (4) | 100ms | 250ms |
| Success rate | Critical (5) | 99% | 95% |
| Steps | Medium (3) | 3 | 7 |
| Coverage | Low (2) | 100% | 80% |

### Exercise 2: Importance-Satisfaction Matrix

Place your product's top 10 features on the importance-satisfaction matrix. What does the distribution reveal?

### Exercise 3: Root Cause Investigation

For your highest-priority gap, conduct a "5 Whys" analysis:

```
Gap: _______________

Why 1: _______________
Why 2: _______________
Why 3: _______________
Why 4: _______________
Why 5: _______________ ← Root cause
```

---

## Resulting Context

After implementing this pattern, you have:

- **Prioritized list of improvement opportunities** — know what to fix first
- **Data-driven basis for resource allocation** — invest where impact is highest
- **Tracking of gap closure over time** — see progress
- **Clear connection between gaps and root causes** — know what to change
- **Objective prioritization** — reduce politics in roadmap decisions

Gap analysis transforms vague "we should improve" into specific "we should fix X because it has priority score Y and root cause Z."

---

## Code References

The following spec-kit source files support gap analysis:

| Reference | Description |
|-----------|-------------|
| `ontology/jtbd-schema.ttl:51-108` | Outcome class for defining target metrics |
| `ontology/jtbd-schema.ttl:889-920` | DesiredOutcomeShape validating outcome targets |
| `src/specify_cli/core/jtbd_metrics.py:50-100` | Metrics collection for current vs. target comparison |

---

## Related Patterns

- **Uses:** **[40. Outcome Measurement](./outcome-measurement.md)** — Provides current performance data
- **Drives:** **[42. Specification Refinement](./specification-refinement.md)** — Informs what to improve
- **Informs:** **[43. Branching Exploration](./branching-exploration.md)** — Helps choose which solutions to explore
- **Guided by:** **[5. Outcome Desired](../context/outcome-desired.md)** — Targets defined in context

---

## Philosophical Note

> *"The first step toward solving a problem is recognizing that it exists."*

Gap analysis doesn't just recognize problems—it quantifies them, prioritizes them, and points toward solutions. It transforms intuition into analysis and opinion into data.

Without gap analysis, priorities are set by politics, recency, or whoever complains loudest. With gap analysis, priorities are set by impact. The highest-priority gaps get attention. The lowest-priority gaps wait their turn.

This isn't about ignoring customer feedback. It's about organizing it. Every complaint represents a gap. Gap analysis helps you understand which complaints represent the most important gaps—and therefore where to invest your limited resources.

Find the gaps. Close the important ones. Let the rest wait.

---

**Next:** Learn how **[42. Specification Refinement](./specification-refinement.md)** channels improvement insights into disciplined specification evolution.
