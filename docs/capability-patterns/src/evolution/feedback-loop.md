# 39. Feedback Loop

★★

*Build, measure, learn. The feedback loop closes the circuit between what you build and what customers experience, enabling continuous improvement based on real-world data. This is how capabilities learn from their own existence.*

---

## The Circuit of Learning

In electrical engineering, a circuit must be complete for current to flow. An open circuit is inert—electrons have nowhere to go. Close the circuit, and energy flows.

Software development faces the same principle. Building is one direction of flow—from specification through transformation to artifact. But without a return path, you're building into a void. You ship features without knowing if they help. You optimize metrics without knowing if they matter.

The feedback loop closes the circuit:

```
Specification → Transformation → Artifact → Usage → Feedback → Specification
       ↑                                                            │
       └────────────────────────────────────────────────────────────┘
```

This isn't just monitoring. Monitoring observes without acting. The feedback loop observes *and* responds—channeling observations back into specification refinement. The capability learns. It evolves based on evidence, not assumption.

---

## The Blind Building Problem

**The fundamental problem: Without feedback, capabilities stagnate. Assumptions remain unchallenged. Opportunities for improvement go unnoticed. You build what you think is right rather than what is actually needed.**

Consider what happens without feedback:

### The Assumption Trap

```
Day 1:
"Users need fast validation"
    ↓
Optimize for speed
    ↓
Ship fast validator

Day 100:
Users: "It's fast, but the error messages are confusing"
Developer: (doesn't know—no feedback loop)

Day 200:
Users: (still confused, stopped using the tool)
Developer: (still optimizing speed)
```

The assumption was partially correct—users do want fast validation. But the *priority* was wrong. Comprehensible errors mattered more than speed. Without feedback, this insight never reaches the team.

### The Metrics Mirage

Teams measure what's easy to measure:
- Lines of code written
- Features shipped
- Test coverage achieved
- Performance benchmarks met

These are *output metrics*. They measure what you produced. They don't measure whether it mattered.

*Outcome metrics* are harder to measure but more meaningful:
- Time users save
- Errors users avoid
- Questions users don't need to ask
- Progress users make on their jobs

Without feedback loops, teams optimize outputs while outcomes languish.

### The Opportunity Blindness

Every capability has hidden potential:
- Features users would love but haven't requested
- Use cases you haven't imagined
- Integrations that would multiply value
- Simplifications that would remove friction

Users discover these opportunities through usage. Without feedback, their discoveries die in isolation.

---

## The Forces

### Force: Building Wants Forward Motion

*Shipping features feels productive. Pausing to learn feels slow.*

Development culture celebrates shipping. "Move fast and break things." "Ship early, ship often." The bias is toward action, toward progress, toward the next feature.

Learning requires pausing. Analyzing data takes time. Synthesizing insights requires thought. This feels like slowing down.

**Resolution:** Make learning continuous, not separate. Build feedback into the flow rather than treating it as a phase.

### Force: Learning Wants Reflection

*Understanding usage takes time. Insights don't emerge from raw data.*

Data is not insight. You can have terabytes of telemetry and zero understanding. Insight requires:
- Asking the right questions
- Looking at the right data
- Recognizing patterns
- Synthesizing meaning

This takes dedicated attention.

**Resolution:** Establish structured reflection rhythms. Weekly reviews, monthly deep dives, quarterly retrospectives. Make reflection routine, not exceptional.

### Force: Data Wants Analysis

*Raw metrics aren't insights. Numbers need interpretation.*

P99 latency increased by 15%. Is that good or bad? It depends:
- What's the baseline?
- What's the target?
- What's causing the increase?
- Who's affected?
- Does it matter?

Data without context is noise.

**Resolution:** Always pair metrics with context. Establish baselines, targets, and thresholds. Make data meaningful through comparison.

### Force: Action Wants Clarity

*What should we do differently? Feedback must be actionable.*

"Users are unhappy" isn't actionable. "Users spend 2 minutes understanding error messages that should take 10 seconds" is actionable. It tells you what to fix.

**Resolution:** Push feedback toward specificity. From sentiment to behavior. From behavior to cause. From cause to action.

---

## Therefore

**Establish explicit feedback loops that connect operational data back to specification evolution. Make learning systematic, not accidental. Close the circuit between building and understanding.**

### The Feedback Loop Architecture

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  THE COMPLETE FEEDBACK LOOP                                                    │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 1: OBSERVE                                                         │  │
│  │                                                                          │  │
│  │ Data Sources:                                                            │  │
│  │                                                                          │  │
│  │ ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐           │  │
│  │ │   TELEMETRY     │  │ USER FEEDBACK   │  │    ANALYTICS    │           │  │
│  │ │                 │  │                 │  │                 │           │  │
│  │ │ • Traces        │  │ • Surveys       │  │ • Feature usage │           │  │
│  │ │ • Metrics       │  │ • Support tix   │  │ • Flows         │           │  │
│  │ │ • Logs          │  │ • Interviews    │  │ • Retention     │           │  │
│  │ │ • Events        │  │ • Feedback btn  │  │ • Churn         │           │  │
│  │ └────────┬────────┘  └────────┬────────┘  └────────┬────────┘           │  │
│  │          │                    │                    │                    │  │
│  │          └──────────────────┬─┴────────────────────┘                    │  │
│  │                             ↓                                           │  │
│  └─────────────────────────────┼───────────────────────────────────────────┘  │
│                                │                                               │
│  ┌─────────────────────────────┼───────────────────────────────────────────┐  │
│  │ PHASE 2: ANALYZE            │                                            │  │
│  │                             ↓                                            │  │
│  │ ┌─────────────────────────────────────────────────────────────────────┐ │  │
│  │ │                      DATA AGGREGATION                                │ │  │
│  │ │                                                                      │ │  │
│  │ │  Combine telemetry + feedback + analytics into unified view         │ │  │
│  │ └────────────────────────────┬────────────────────────────────────────┘ │  │
│  │                              ↓                                          │  │
│  │ ┌─────────────────────────────────────────────────────────────────────┐ │  │
│  │ │                     PATTERN EXTRACTION                               │ │  │
│  │ │                                                                      │ │  │
│  │ │  • Performance bottlenecks (where is latency?)                      │ │  │
│  │ │  • Error patterns (what fails, when, for whom?)                     │ │  │
│  │ │  • Usage patterns (what's used, what's ignored?)                    │ │  │
│  │ │  • Outcome achievement (are targets met?)                           │ │  │
│  │ └────────────────────────────┬────────────────────────────────────────┘ │  │
│  │                              ↓                                          │  │
│  └──────────────────────────────┼──────────────────────────────────────────┘  │
│                                 │                                              │
│  ┌──────────────────────────────┼──────────────────────────────────────────┐  │
│  │ PHASE 3: HYPOTHESIZE         │                                           │  │
│  │                              ↓                                           │  │
│  │  "Users struggle with X because..."                                      │  │
│  │  "Outcome Y isn't achieved because..."                                   │  │
│  │  "Performance degrades when..."                                          │  │
│  │  "Feature Z is underused because..."                                     │  │
│  │                              │                                           │  │
│  │  Hypotheses must be:         │                                           │  │
│  │  • Specific and testable     │                                           │  │
│  │  • Tied to data              │                                           │  │
│  │  • Actionable                │                                           │  │
│  │                              ↓                                           │  │
│  └──────────────────────────────┼──────────────────────────────────────────┘  │
│                                 │                                              │
│  ┌──────────────────────────────┼──────────────────────────────────────────┐  │
│  │ PHASE 4: SPECIFY             │                                           │  │
│  │                              ↓                                           │  │
│  │  Update specifications based on hypotheses:                              │  │
│  │                                                                          │  │
│  │  • New acceptance criteria                                               │  │
│  │  • Refined outcomes                                                      │  │
│  │  • Additional constraints                                                │  │
│  │  • New capabilities                                                      │  │
│  │  • Deprecation of unused features                                        │  │
│  │                              │                                           │  │
│  │  Changes flow through RDF specification                                  │  │
│  │                              ↓                                           │  │
│  └──────────────────────────────┼──────────────────────────────────────────┘  │
│                                 │                                              │
│  ┌──────────────────────────────┼──────────────────────────────────────────┐  │
│  │ PHASE 5: TRANSFORM           │                                           │  │
│  │                              ↓                                           │  │
│  │  Regenerate artifacts using μ transformation                             │  │
│  │                                                                          │  │
│  │  spec.md = μ(feature.ttl)                                                │  │
│  │                              │                                           │  │
│  │  Changes propagate from specification to all artifacts                   │  │
│  │                              ↓                                           │  │
│  └──────────────────────────────┼──────────────────────────────────────────┘  │
│                                 │                                              │
│  ┌──────────────────────────────┼──────────────────────────────────────────┐  │
│  │ PHASE 6: VERIFY              │                                           │  │
│  │                              ↓                                           │  │
│  │  Ensure changes work:                                                    │  │
│  │                                                                          │  │
│  │  • Run all verification patterns                                         │  │
│  │  • Check constitutional equation holds                                   │  │
│  │  • Validate against SHACL shapes                                         │  │
│  │  • Execute contract tests                                                │  │
│  │  • Run integration tests                                                 │  │
│  │                              │                                           │  │
│  │                              ↓                                           │  │
│  └──────────────────────────────┼──────────────────────────────────────────┘  │
│                                 │                                              │
│  ┌──────────────────────────────┼──────────────────────────────────────────┐  │
│  │ PHASE 7: DEPLOY              │                                           │  │
│  │                              ↓                                           │  │
│  │  Release changes to production                                           │  │
│  │                                                                          │  │
│  │  Then return to OBSERVE to close the loop                                │  │
│  │                              │                                           │  │
│  │                              └─────────────────────────────────────────┐ │  │
│  │                                                                         │ │  │
│  └─────────────────────────────────────────────────────────────────────────┘ │  │
│                                                                               │  │
└───────────────────────────────────────────────────────────────────────────────┘
                              │
                              ↓
                    [Back to OBSERVE]
```

---

## Implementation

### Data Collection Infrastructure

```python
# src/specify_cli/ops/feedback.py
"""Feedback loop data collection and analysis."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum


class FeedbackSource(Enum):
    """Sources of feedback data."""
    TELEMETRY = "telemetry"
    USER_SURVEY = "user_survey"
    SUPPORT_TICKET = "support_ticket"
    USAGE_ANALYTICS = "usage_analytics"
    ERROR_REPORT = "error_report"
    AB_TEST = "ab_test"
    INTERVIEW = "interview"


@dataclass
class FeedbackItem:
    """A single piece of feedback."""
    id: str
    source: FeedbackSource
    timestamp: datetime
    capability: str
    observation: str
    impact: Optional[str] = None
    proposed_action: Optional[str] = None
    linked_outcome: Optional[str] = None
    user_segment: Optional[str] = None
    severity: Optional[str] = None

    def to_rdf(self) -> str:
        """Convert to RDF/Turtle format."""
        return f'''
feedback:{self.id} a sk:Feedback ;
    sk:source "{self.source.value}" ;
    sk:timestamp "{self.timestamp.isoformat()}"^^xsd:dateTime ;
    sk:concernsCapability cli:{self.capability} ;
    sk:observation """{self.observation}""" ;
    {f'sk:impact """{self.impact}""" ;' if self.impact else ''}
    {f'sk:proposedAction """{self.proposed_action}""" ;' if self.proposed_action else ''}
    {f'sk:linkedOutcome jtbd:{self.linked_outcome} ;' if self.linked_outcome else ''}
    {f'sk:userSegment "{self.user_segment}" ;' if self.user_segment else ''}
    {f'sk:severity "{self.severity}" ;' if self.severity else ''}
    .
'''


class FeedbackCollector:
    """Collect feedback from multiple sources."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.items: List[FeedbackItem] = []

    def collect_from_telemetry(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[FeedbackItem]:
        """Extract feedback insights from telemetry data."""
        items = []

        # Query for performance anomalies
        anomalies = self._query_performance_anomalies(start_time, end_time)
        for anomaly in anomalies:
            items.append(FeedbackItem(
                id=f"TELEM-{anomaly['id']}",
                source=FeedbackSource.TELEMETRY,
                timestamp=anomaly['timestamp'],
                capability=anomaly['capability'],
                observation=f"P99 latency {anomaly['value']}ms exceeds threshold {anomaly['threshold']}ms",
                impact=f"Affects {anomaly['affected_users']} users",
                linked_outcome=anomaly.get('outcome'),
                severity="high" if anomaly['value'] > anomaly['threshold'] * 2 else "medium"
            ))

        # Query for error spikes
        errors = self._query_error_spikes(start_time, end_time)
        for error in errors:
            items.append(FeedbackItem(
                id=f"ERROR-{error['id']}",
                source=FeedbackSource.ERROR_REPORT,
                timestamp=error['timestamp'],
                capability=error['capability'],
                observation=f"Error rate {error['rate']}% for {error['error_type']}",
                impact=f"{error['occurrences']} occurrences in period",
                proposed_action=f"Investigate: {error['error_message'][:100]}",
                severity="critical" if error['rate'] > 5 else "high"
            ))

        return items

    def collect_from_surveys(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[FeedbackItem]:
        """Extract feedback from user surveys."""
        items = []

        # Query survey responses
        responses = self._query_survey_responses(start_time, end_time)
        for response in responses:
            # Convert satisfaction score to observation
            score = response['satisfaction']
            if score <= 2:
                severity = "high"
                observation = f"Low satisfaction ({score}/5): {response['comment']}"
            elif score == 3:
                severity = "medium"
                observation = f"Neutral satisfaction ({score}/5): {response['comment']}"
            else:
                severity = "low"
                observation = f"Positive feedback ({score}/5): {response['comment']}"

            items.append(FeedbackItem(
                id=f"SURVEY-{response['id']}",
                source=FeedbackSource.USER_SURVEY,
                timestamp=response['timestamp'],
                capability=response.get('capability', 'general'),
                observation=observation,
                user_segment=response.get('segment'),
                severity=severity
            ))

        return items

    def collect_from_support(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[FeedbackItem]:
        """Extract feedback from support tickets."""
        items = []

        tickets = self._query_support_tickets(start_time, end_time)
        for ticket in tickets:
            items.append(FeedbackItem(
                id=f"TICKET-{ticket['id']}",
                source=FeedbackSource.SUPPORT_TICKET,
                timestamp=ticket['created_at'],
                capability=ticket.get('capability', 'unknown'),
                observation=ticket['summary'],
                impact=f"Resolution time: {ticket['resolution_time']}",
                user_segment=ticket.get('customer_tier'),
                severity=ticket['priority']
            ))

        return items

    def _query_performance_anomalies(self, start: datetime, end: datetime) -> List[Dict]:
        """Query telemetry for performance anomalies."""
        # Implementation would query actual telemetry backend
        # This is a placeholder showing the interface
        pass

    def _query_error_spikes(self, start: datetime, end: datetime) -> List[Dict]:
        """Query telemetry for error spikes."""
        pass

    def _query_survey_responses(self, start: datetime, end: datetime) -> List[Dict]:
        """Query survey system for responses."""
        pass

    def _query_support_tickets(self, start: datetime, end: datetime) -> List[Dict]:
        """Query support system for tickets."""
        pass


@dataclass
class FeedbackAnalysis:
    """Analysis results from feedback data."""
    period_start: datetime
    period_end: datetime
    total_items: int
    by_source: Dict[str, int]
    by_severity: Dict[str, int]
    by_capability: Dict[str, int]
    patterns: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]


class FeedbackAnalyzer:
    """Analyze collected feedback to extract insights."""

    def analyze(self, items: List[FeedbackItem]) -> FeedbackAnalysis:
        """Analyze feedback items and extract patterns."""
        if not items:
            return FeedbackAnalysis(
                period_start=datetime.now(),
                period_end=datetime.now(),
                total_items=0,
                by_source={},
                by_severity={},
                by_capability={},
                patterns=[],
                recommendations=[]
            )

        # Aggregate by dimensions
        by_source = self._count_by(items, lambda x: x.source.value)
        by_severity = self._count_by(items, lambda x: x.severity or 'unknown')
        by_capability = self._count_by(items, lambda x: x.capability)

        # Extract patterns
        patterns = self._extract_patterns(items)

        # Generate recommendations
        recommendations = self._generate_recommendations(patterns)

        timestamps = [item.timestamp for item in items]

        return FeedbackAnalysis(
            period_start=min(timestamps),
            period_end=max(timestamps),
            total_items=len(items),
            by_source=by_source,
            by_severity=by_severity,
            by_capability=by_capability,
            patterns=patterns,
            recommendations=recommendations
        )

    def _count_by(self, items: List[FeedbackItem], key_fn) -> Dict[str, int]:
        """Count items by a key function."""
        counts = {}
        for item in items:
            key = key_fn(item)
            counts[key] = counts.get(key, 0) + 1
        return counts

    def _extract_patterns(self, items: List[FeedbackItem]) -> List[Dict[str, Any]]:
        """Extract patterns from feedback items."""
        patterns = []

        # Pattern: High-severity cluster
        high_severity = [i for i in items if i.severity in ['critical', 'high']]
        if len(high_severity) > 5:
            by_cap = self._count_by(high_severity, lambda x: x.capability)
            worst_cap = max(by_cap, key=by_cap.get)
            patterns.append({
                'type': 'severity_cluster',
                'capability': worst_cap,
                'count': by_cap[worst_cap],
                'description': f"High severity feedback concentrated in {worst_cap}"
            })

        # Pattern: Recurring theme
        # Simple keyword extraction (production would use NLP)
        observations = [item.observation.lower() for item in items]
        common_words = self._find_common_words(observations)
        for word, count in common_words[:3]:
            if count > len(items) * 0.2:  # Appears in >20% of feedback
                patterns.append({
                    'type': 'recurring_theme',
                    'theme': word,
                    'frequency': count / len(items),
                    'description': f"'{word}' mentioned in {count} feedback items"
                })

        return patterns

    def _find_common_words(self, texts: List[str]) -> List[tuple]:
        """Find commonly occurring significant words."""
        # Simplified implementation
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'to', 'for', 'in', 'on', 'of'}
        word_counts = {}
        for text in texts:
            words = set(text.split())
            for word in words - stopwords:
                if len(word) > 3:
                    word_counts[word] = word_counts.get(word, 0) + 1
        return sorted(word_counts.items(), key=lambda x: x[1], reverse=True)

    def _generate_recommendations(
        self,
        patterns: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations from patterns."""
        recommendations = []

        for pattern in patterns:
            if pattern['type'] == 'severity_cluster':
                recommendations.append({
                    'priority': 'high',
                    'capability': pattern['capability'],
                    'action': f"Investigate and address issues in {pattern['capability']}",
                    'rationale': pattern['description']
                })
            elif pattern['type'] == 'recurring_theme':
                recommendations.append({
                    'priority': 'medium',
                    'theme': pattern['theme'],
                    'action': f"Address user concerns about '{pattern['theme']}'",
                    'rationale': pattern['description']
                })

        return recommendations
```

### Feedback in RDF Specification

```turtle
# memory/feedback.ttl
@prefix feedback: <http://github.com/spec-kit/feedback#> .
@prefix sk: <http://github.com/spec-kit/schema#> .
@prefix jtbd: <http://github.com/spec-kit/jtbd#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# ============================================================================
# Feedback Schema
# ============================================================================

sk:Feedback a rdfs:Class ;
    rdfs:label "Feedback" ;
    rdfs:comment "A piece of feedback from any source" .

sk:FeedbackSource a rdfs:Class ;
    rdfs:label "Feedback Source" ;
    rdfs:comment "The origin of feedback data" .

# Feedback sources
sk:TelemetrySource a sk:FeedbackSource ;
    rdfs:label "Telemetry" ;
    sk:description "Automated data from OpenTelemetry instrumentation" .

sk:SurveySource a sk:FeedbackSource ;
    rdfs:label "User Survey" ;
    sk:description "Direct user feedback through surveys" .

sk:SupportSource a sk:FeedbackSource ;
    rdfs:label "Support Ticket" ;
    sk:description "Issues raised through support channels" .

sk:AnalyticsSource a sk:FeedbackSource ;
    rdfs:label "Usage Analytics" ;
    sk:description "Behavioral data from product analytics" .

# ============================================================================
# Sample Feedback Items
# ============================================================================

feedback:FB-2025-01-15-001 a sk:Feedback ;
    sk:source sk:TelemetrySource ;
    sk:timestamp "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    sk:concernsCapability cli:ValidateCommand ;
    sk:observation "P95 latency exceeds 500ms for files > 1MB" ;
    sk:impact "Users report slow validation frustrating" ;
    sk:proposedAction "Add streaming validation for large files" ;
    sk:linkedOutcome jtbd:MinimizeValidationTime ;
    sk:severity "high" .

feedback:FB-2025-01-16-001 a sk:Feedback ;
    sk:source sk:SurveySource ;
    sk:timestamp "2025-01-16T14:22:00Z"^^xsd:dateTime ;
    sk:concernsCapability cli:ValidateCommand ;
    sk:observation "Error messages difficult to understand" ;
    sk:impact "Users struggle to fix validation failures" ;
    sk:proposedAction "Add plain-language error explanations" ;
    sk:linkedOutcome jtbd:MinimizeErrorComprehensionTime ;
    sk:severity "high" ;
    sk:userSegment "new_users" .

feedback:FB-2025-01-17-001 a sk:Feedback ;
    sk:source sk:SupportSource ;
    sk:timestamp "2025-01-17T09:15:00Z"^^xsd:dateTime ;
    sk:concernsCapability cli:InitCommand ;
    sk:observation "Init command fails on Windows with path separator issues" ;
    sk:impact "Windows users cannot start projects" ;
    sk:proposedAction "Normalize path separators in init command" ;
    sk:severity "critical" ;
    sk:userSegment "windows_users" .

# ============================================================================
# Feedback Analysis Results
# ============================================================================

feedback:Analysis-2025-W03 a sk:FeedbackAnalysis ;
    sk:period "2025-W03" ;
    sk:totalItems 47 ;
    sk:pattern [
        a sk:SeverityCluster ;
        sk:capability cli:ValidateCommand ;
        sk:count 12 ;
        sk:description "High severity feedback concentrated in validation"
    ] ;
    sk:pattern [
        a sk:RecurringTheme ;
        sk:theme "slow" ;
        sk:frequency 0.34 ;
        sk:description "Performance concerns mentioned in 34% of feedback"
    ] ;
    sk:recommendation [
        sk:priority "high" ;
        sk:capability cli:ValidateCommand ;
        sk:action "Implement streaming validation for large files" ;
        sk:rationale "Performance is top concern for validation"
    ] .
```

### Feedback Cadence Configuration

```yaml
# .ggen/feedback-config.yaml
feedback_loop:
  # Data collection schedule
  collection:
    telemetry:
      frequency: continuous
      aggregation: 1h
      retention: 90d

    surveys:
      frequency: weekly
      sample_size: 100
      questions:
        - "How satisfied are you with {capability}?"
        - "What would make {capability} better?"

    support:
      frequency: continuous
      auto_tag: true
      escalation_threshold: 5  # same issue reported 5+ times

    analytics:
      frequency: daily
      metrics:
        - feature_usage
        - conversion_funnel
        - retention_cohorts

  # Analysis schedule
  analysis:
    daily:
      focus:
        - error_rates
        - critical_metrics
        - anomaly_detection
      alert_threshold: 2x baseline

    weekly:
      focus:
        - performance_trends
        - usage_patterns
        - survey_synthesis
      report_to: team_channel

    monthly:
      focus:
        - outcome_achievement
        - satisfaction_scores
        - gap_analysis
      report_to: stakeholders

    quarterly:
      focus:
        - strategic_alignment
        - roadmap_impact
        - capability_health
      report_to: leadership

  # Action triggers
  actions:
    automatic:
      - condition: "error_rate > 5%"
        action: "page_on_call"
      - condition: "p99_latency > 2x target"
        action: "create_investigation_ticket"

    manual_review:
      - condition: "survey_score < 3"
        action: "schedule_user_interview"
      - condition: "support_tickets > 10/week for capability"
        action: "prioritize_improvement"
```

### Feedback Dashboard Queries

```sparql
# sparql/feedback-dashboard.rq
# Dashboard queries for feedback analysis

PREFIX feedback: <http://github.com/spec-kit/feedback#>
PREFIX sk: <http://github.com/spec-kit/schema#>
PREFIX jtbd: <http://github.com/spec-kit/jtbd#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# Query 1: High-severity feedback by capability
SELECT ?capability (COUNT(?feedback) AS ?count)
WHERE {
    ?feedback a sk:Feedback ;
              sk:concernsCapability ?capability ;
              sk:severity ?severity .
    FILTER(?severity IN ("critical", "high"))
}
GROUP BY ?capability
ORDER BY DESC(?count)

# Query 2: Feedback trends over time
SELECT ?week (COUNT(?feedback) AS ?total)
       (SUM(IF(?severity = "critical", 1, 0)) AS ?critical)
       (SUM(IF(?severity = "high", 1, 0)) AS ?high)
WHERE {
    ?feedback a sk:Feedback ;
              sk:timestamp ?ts ;
              sk:severity ?severity .
    BIND(CONCAT(STR(YEAR(?ts)), "-W", STR(WEEK(?ts))) AS ?week)
}
GROUP BY ?week
ORDER BY ?week

# Query 3: Outcome-linked feedback
SELECT ?outcome ?outcomeLabel (COUNT(?feedback) AS ?feedbackCount)
WHERE {
    ?feedback a sk:Feedback ;
              sk:linkedOutcome ?outcome .
    ?outcome rdfs:label ?outcomeLabel .
}
GROUP BY ?outcome ?outcomeLabel
ORDER BY DESC(?feedbackCount)

# Query 4: User segment analysis
SELECT ?segment (COUNT(?feedback) AS ?count)
       (AVG(IF(?severity = "critical", 4,
            IF(?severity = "high", 3,
            IF(?severity = "medium", 2, 1)))) AS ?avgSeverity)
WHERE {
    ?feedback a sk:Feedback ;
              sk:userSegment ?segment ;
              sk:severity ?severity .
}
GROUP BY ?segment
ORDER BY DESC(?avgSeverity)
```

---

## The Build-Measure-Learn Cycle

The feedback loop implements the Build-Measure-Learn cycle from Lean Startup, adapted for specification-driven development:

```
┌───────────────────────────────────────────────────────────────────────────┐
│  BUILD-MEASURE-LEARN FOR SPECIFICATIONS                                    │
│                                                                            │
│                         ┌─────────────┐                                    │
│                         │   IDEAS     │                                    │
│                         │             │                                    │
│                         │ Hypotheses  │                                    │
│                         │ about what  │                                    │
│                         │ will help   │                                    │
│                         └──────┬──────┘                                    │
│                                │                                           │
│                                ↓                                           │
│              ┌─────────────────────────────────────┐                       │
│              │              BUILD                   │                       │
│              │                                      │                       │
│              │  1. Encode idea in RDF spec          │                       │
│              │  2. Define acceptance criteria       │                       │
│              │  3. Transform to artifacts           │                       │
│              │  4. Verify correctness               │                       │
│              │  5. Deploy to production             │                       │
│              └─────────────────┬───────────────────┘                       │
│                                │                                           │
│                                ↓                                           │
│                         ┌─────────────┐                                    │
│                         │   PRODUCT   │                                    │
│                         │             │                                    │
│                         │ Generated   │                                    │
│                         │ capability  │                                    │
│                         │ in prod     │                                    │
│                         └──────┬──────┘                                    │
│                                │                                           │
│                                ↓                                           │
│              ┌─────────────────────────────────────┐                       │
│              │            MEASURE                   │                       │
│              │                                      │                       │
│              │  1. Collect telemetry                │                       │
│              │  2. Gather user feedback             │                       │
│              │  3. Track outcome metrics            │                       │
│              │  4. Monitor error rates              │                       │
│              │  5. Aggregate into unified view      │                       │
│              └─────────────────┬───────────────────┘                       │
│                                │                                           │
│                                ↓                                           │
│                         ┌─────────────┐                                    │
│                         │    DATA     │                                    │
│                         │             │                                    │
│                         │ Performance │                                    │
│                         │ Usage       │                                    │
│                         │ Feedback    │                                    │
│                         └──────┬──────┘                                    │
│                                │                                           │
│                                ↓                                           │
│              ┌─────────────────────────────────────┐                       │
│              │              LEARN                   │                       │
│              │                                      │                       │
│              │  1. Analyze patterns                 │                       │
│              │  2. Compare to hypotheses            │                       │
│              │  3. Identify gaps                    │                       │
│              │  4. Generate new hypotheses          │                       │
│              │  5. Feed back to IDEAS               │                       │
│              └─────────────────┬───────────────────┘                       │
│                                │                                           │
│                                ↓                                           │
│                         ┌─────────────┐                                    │
│                         │  LEARNING   │                                    │
│                         │             │                                    │
│                         │ Validated/  │                                    │
│                         │ Invalidated │                                    │
│                         │ hypotheses  │──────────────→ [IDEAS]             │
│                         └─────────────┘                                    │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
```

### Key Differences from Traditional BML

| Aspect | Traditional | Specification-Driven |
|--------|-------------|---------------------|
| Build input | User stories, requirements | RDF specifications |
| Build output | Code changes | Generated artifacts |
| Measure focus | Feature metrics | Outcome metrics |
| Learn output | Backlog items | Specification refinements |
| Iteration | Ad-hoc changes | Constitutional equation |

---

## Case Study: The Learning Validation Team

*A team transforms their validation capability through systematic feedback.*

### The Before

The ValidationCo team shipped a validation capability:
- 500ms typical latency
- 85% user satisfaction
- 3 support tickets per week

They thought they were done. The capability worked, tests passed, users seemed happy.

### The Feedback Loop Implementation

They implemented a complete feedback loop:

**Week 1: Instrument**
```python
# Added telemetry to validation
@timed
def validate(file: Path) -> ValidationResult:
    with span("validate", {"file_size": file.stat().st_size}):
        # ...
```

**Week 2: Collect**
- Telemetry: 10,000 validation events/day
- Survey: 50 responses (sent to recent users)
- Support: Tagged existing tickets with capability

**Week 3: Analyze**
```
Discovery 1: P99 latency is 8 seconds, not 500ms
  - 500ms was P50
  - Large files (>1MB) took dramatically longer
  - 5% of validations were large files

Discovery 2: Survey revealed hidden pain
  - "It's fast for small files but I have to wait forever for big ones"
  - "The error messages are technical. I don't know what to fix."
  - "Sometimes it just says 'invalid' with no details"

Discovery 3: Support tickets clustered
  - 70% were about error message comprehension
  - 20% were about large file performance
  - 10% were actual bugs
```

**Week 4: Hypothesize**
```
H1: Adding streaming validation will reduce large file P99 by 80%
H2: Adding plain-language error explanations will reduce comprehension support tickets by 50%
H3: Adding specific error locations will reduce debugging time by 70%
```

**Week 5: Specify**
```turtle
# Updated specification with new acceptance criteria
cli:ValidateCommand
    sk:acceptanceCriteria [
        sk:id "AC-VAL-P99" ;
        sk:criterion "P99 latency < 2 seconds for files up to 10MB" ;
        sk:previousCriterion "P50 latency < 1 second" ;
        sk:rationale "Feedback showed P99 is what users experience"
    ] ;
    sk:acceptanceCriteria [
        sk:id "AC-VAL-ERROR" ;
        sk:criterion "Error messages include plain-language explanation" ;
        sk:rationale "Support tickets show technical messages confuse users"
    ] .
```

**Week 6: Transform & Verify**
- Regenerated artifacts from updated spec
- Implemented streaming validation
- Added error explanations
- All tests passing

**Week 7: Deploy & Observe**

### The Results

After one complete feedback cycle:

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| P50 latency | 500ms | 400ms | -20% |
| P99 latency | 8,000ms | 1,200ms | -85% |
| Large file P99 | 25,000ms | 2,000ms | -92% |
| Support tickets | 3/week | 1/week | -67% |
| User satisfaction | 85% | 94% | +9% |
| Error comprehension time | 2min | 20sec | -83% |

### The Continuous Loop

The team established ongoing cadence:

- **Daily**: Check error rates, P99 latency, alert on anomalies
- **Weekly**: Review feedback items, update hypotheses
- **Monthly**: Full feedback analysis, specification refinement
- **Quarterly**: Strategic review, major improvements

Each cycle generated new insights:
- Cycle 2: Discovered users wanted batch validation
- Cycle 3: Found specific file types caused issues
- Cycle 4: Identified power user needs vs. casual users

---

## Anti-Patterns

### Anti-Pattern: Data Hoarding

*"We collect everything! We have 2 years of telemetry data!"*

Data without analysis is digital hoarding. Petabytes of logs mean nothing if no one looks at them.

**Resolution:** Collect with intent. For every metric, know why you're collecting it and what you'll do with it.

### Anti-Pattern: Analysis Paralysis

*"We need more data before we can decide anything."*

Perfect data doesn't exist. Waiting for certainty means waiting forever.

**Resolution:** Set decision thresholds. "If X > Y for 2 weeks, we act." Make decisions with available data.

### Anti-Pattern: Vanity Metrics

*"Downloads are up 50%!"*

Downloads, page views, sign-ups—these are vanity metrics. They feel good but don't indicate value delivery.

**Resolution:** Focus on outcome metrics. Did users make progress? Did they achieve their goals?

### Anti-Pattern: Feedback Firewall

*"The support team handles user feedback. Engineering doesn't need to see it."*

Separating feedback from engineering creates a firewall. Engineers don't feel user pain. Support can't explain technical context.

**Resolution:** Make feedback visible to all. Engineers should see support tickets. Support should understand technical constraints.

### Anti-Pattern: One-Time Learning

*"We did a feedback analysis last quarter."*

One analysis creates a snapshot. The world moves on. New issues emerge. Old insights become stale.

**Resolution:** Make feedback continuous. Establish rhythms. Never stop learning.

---

## Implementation Checklist

### Infrastructure Setup

- [ ] Configure telemetry collection (OpenTelemetry)
- [ ] Set up user feedback mechanisms (surveys, in-app)
- [ ] Integrate support ticket system
- [ ] Establish analytics pipeline
- [ ] Create feedback data store (RDF/graph database)

### Collection Configuration

- [ ] Define metrics to collect
- [ ] Set collection frequencies
- [ ] Configure aggregation windows
- [ ] Establish retention policies
- [ ] Set up alerting thresholds

### Analysis Process

- [ ] Define analysis cadences (daily/weekly/monthly)
- [ ] Create analysis queries and dashboards
- [ ] Establish pattern recognition criteria
- [ ] Define recommendation templates
- [ ] Assign analysis responsibilities

### Feedback-to-Spec Pipeline

- [ ] Define feedback item schema
- [ ] Create feedback → hypothesis process
- [ ] Establish specification update workflow
- [ ] Link feedback to outcomes
- [ ] Track hypothesis validation

### Continuous Improvement

- [ ] Schedule regular retrospectives
- [ ] Review feedback loop effectiveness
- [ ] Refine collection and analysis
- [ ] Update documentation
- [ ] Share learnings across team

---

## Exercises

### Exercise 1: Map Your Feedback Sources

Identify all potential feedback sources for a capability you maintain:

| Source | What It Tells You | Collection Method | Current State |
|--------|-------------------|-------------------|---------------|
| Telemetry | | | |
| Surveys | | | |
| Support | | | |
| Analytics | | | |
| Interviews | | | |

### Exercise 2: Design a Feedback Item

Create an RDF feedback item for a recent user complaint or telemetry anomaly:

```turtle
feedback:YOUR-ID a sk:Feedback ;
    sk:source ??? ;
    sk:timestamp ???^^xsd:dateTime ;
    sk:concernsCapability ??? ;
    sk:observation """???""" ;
    sk:impact """???""" ;
    sk:proposedAction """???""" ;
    sk:linkedOutcome ??? .
```

### Exercise 3: Hypothesis from Feedback

Given these feedback items, form a testable hypothesis:

```
- 5 support tickets about "confusing error messages"
- Telemetry shows 30% of users retry validation 3+ times
- Survey comment: "I don't know what went wrong"
```

Hypothesis: _______________________

How would you test it? _______________________

What specification change would address it? _______________________

---

## Resulting Context

After implementing this pattern, you have:

- **Closed circuit between building and learning** — every deployment feeds back insights
- **Data-driven improvement process** — decisions based on evidence, not assumption
- **Structured approach to learning** — regular cadences, clear processes
- **Living capabilities that evolve** — continuous refinement from feedback
- **Reduced waste** — stop building features that don't help

The feedback loop transforms capabilities from static artifacts into learning systems. They improve themselves based on their own usage.

---

## Related Patterns

- **Collects data from:** **[38. Observable Execution](../verification/observable-execution.md)** — Telemetry foundation
- **Enables:** **[40. Outcome Measurement](./outcome-measurement.md)** — Measure outcomes
- **Drives:** **[42. Specification Refinement](./specification-refinement.md)** — Improve specs
- **Guided by:** **[41. Gap Analysis](./gap-analysis.md)** — Find gaps

---

## Philosophical Note

> *"If you're not measuring it, you're just practicing."*

Practice without feedback is repetition. Repetition reinforces whatever you're doing—good or bad. Feedback enables learning. Learning enables improvement.

The feedback loop isn't overhead. It's the mechanism by which capabilities grow. Without it, you ship features into the void, hoping they help. With it, you know.

Close the circuit. Let the current flow. Watch your capabilities learn.

---

**Next:** Learn how **[40. Outcome Measurement](./outcome-measurement.md)** tracks whether capabilities actually help customers make progress.
