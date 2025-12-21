# JTBD Quick Reference Card

## One-Page Cheat Sheet for Jobs To Be Done Ontology

### Core Principle

**Jobs are stable. Solutions come and go.**
Focus on the progress customers are trying to make, not the features they ask for.

---

## Job Statement Template

```
When [context/situation],
I want to [achieve outcome],
so I can [emotional/social benefit].
```

**Example:**
```turtle
jtbd:when "I receive a pull request for critical code" ;
jtbd:wantTo "quickly identify security vulnerabilities" ;
jtbd:soICan "confidently approve without fear of bugs" .
```

---

## Outcome Statement Template

```
Minimize/Maximize [metric] [object] [clarifier]
```

**Examples:**
- Minimize **time** to identify critical bugs **in pull requests**
- Maximize **confidence** that critical paths are reviewed **before approval**
- Minimize **likelihood** of approving code with defects **during review**

---

## Quick Class Reference

| What | Class | Example |
|------|-------|---------|
| Core task | `jtbd:FunctionalJob` | Ensure code quality |
| Desired feeling | `jtbd:EmotionalJob` | Feel confident |
| Social image | `jtbd:SocialJob` | Maintain reputation |
| Success measure | `jtbd:DesiredOutcome` | Minimize time to find bugs |
| Customer group | `jtbd:CustomerSegment` | Senior engineers |
| Representative | `jtbd:Persona` | Tech Lead Alex |
| Friction point | `jtbd:Painpoint` | Slow review process |
| Current problem | `jtbd:PushForce` | Manual review pain |
| New benefit | `jtbd:PullForce` | Automated insights |
| Old behavior | `jtbd:Habit` | Manual line-by-line review |
| Fear | `jtbd:Anxiety` | Missing critical bugs |

---

## Opportunity Scoring

```
Opportunity = Importance + (Importance - Satisfaction)
```

| Score | Type | Action |
|-------|------|--------|
| < 5 | Overserved | Avoid over-engineering |
| 5-10 | Appropriately Served | Maintain current |
| 10-15 | **Underserved** | **HIGH OPPORTUNITY** |
| > 15 | **Severely Underserved** | **CRITICAL NEED** |

---

## Minimal JTBD Specification

```turtle
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .

# 1. Define the job
:MyJob a jtbd:FunctionalJob ;
    jtbd:jobTitle "..." ;
    jtbd:jobDescription "..." ;
    jtbd:jobType "Functional" ;
    jtbd:hasJobStatement :Statement ;
    jtbd:hasDesiredOutcome :Outcome1, :Outcome2 ;
    jtbd:performedBy :Segment .

# 2. Job statement
:Statement a jtbd:JobStatement ;
    jtbd:when "..." ;
    jtbd:wantTo "..." ;
    jtbd:soICan "..." ;
    jtbd:fullStatement "When..., I want to..., so I can..." .

# 3. Desired outcomes
:Outcome1 a jtbd:DesiredOutcome ;
    jtbd:outcomeStatement "Minimize time..." ;
    jtbd:outcomeDirection "Minimize" ;
    jtbd:outcomeMetric "time" ;
    jtbd:outcomeObject "to complete task" ;
    jtbd:hasOutcomePriority :Priority1 .

:Priority1 a jtbd:OutcomePriority ;
    jtbd:importanceScore "9.2"^^xsd:decimal ;
    jtbd:satisfactionScore "4.1"^^xsd:decimal .

# 4. Customer segment
:Segment a jtbd:CustomerSegment ;
    jtbd:segmentName "..." ;
    jtbd:segmentDescription "..." ;
    jtbd:hasPersona :Persona1 .

:Persona1 a jtbd:Persona ;
    jtbd:personaName "..." ;
    jtbd:personaRole "..." ;
    jtbd:personaGoals "..." ;
    jtbd:personaChallenges "..." .
```

---

## Forces of Progress Diagram

```
CURRENT                                    NEW
SOLUTION                                   SOLUTION
   |                                          |
   |    ← PUSH (problems)                     |
   |    → HABIT (inertia)                     |
   |                                          |
   |    ← ANXIETY (fears)                     |
   |    → PULL (benefits)                     |
   |                                          |
```

**Progress happens when:** Push + Pull > Habit + Anxiety

---

## Integration with Spec-Kit

```turtle
# Link JTBD to Feature
:Feature a sk:Feature ;
    jtbd:targetsSegment :Segment ;
    jtbd:addressesPainpoint :Painpoint1 ;
    jtbd:enablesOutcome :Outcome1 .

# Link Job to Feature
:Job jtbd:informsFeature :Feature .
```

---

## Common Mistakes

| ❌ DON'T | ✅ DO |
|----------|-------|
| "Users want dark mode" | "Users want to reduce eye strain during extended sessions" |
| "Improve performance" | "Minimize time to load dashboard (< 2 sec)" |
| "Millennials aged 25-35" | "Developers reviewing 5+ PRs daily under time pressure" |
| Vague outcomes | Measurable outcomes with metrics |
| Ignore anxieties | Map all four forces |

---

## Validation Checklist

Before committing your JTBD spec:

- [ ] Job has title, description, type
- [ ] Job statement has when/wantTo/soICan
- [ ] At least 3 desired outcomes defined
- [ ] Each outcome has direction + metric + object
- [ ] Importance/satisfaction scores (1-10)
- [ ] Opportunity scores calculated
- [ ] Customer segment with persona
- [ ] At least 2 painpoints identified
- [ ] All four forces mapped (push/pull/habit/anxiety)
- [ ] SHACL validation passes: `ggen validate`

---

## File Locations

- **Ontology:** `/Users/sac/ggen-spec-kit/ontology/jtbd-schema.ttl`
- **Example:** `/Users/sac/ggen-spec-kit/docs/examples/jtbd-example-feature.ttl`
- **Guide:** `/Users/sac/ggen-spec-kit/docs/jtbd-ontology-guide.md`

---

## Key Metrics for Success

| Metric Type | Examples |
|-------------|----------|
| **Time** | Duration, frequency, wait time |
| **Quality** | Accuracy, completeness, defect rate |
| **Effort** | Steps, cognitive load, complexity |
| **Cost** | Money, resources, overhead |
| **Throughput** | Volume, capacity, bandwidth |

---

## 5-Minute JTBD Workflow

1. **Identify job** (5 min): What progress are customers trying to make?
2. **Write statement** (5 min): When/wantTo/soICan format
3. **List outcomes** (10 min): 8-12 Minimize/Maximize statements
4. **Survey customers** (external): Get importance/satisfaction scores
5. **Calculate opportunity** (5 min): Focus on scores > 10
6. **Map painpoints** (10 min): What prevents job completion?
7. **Map forces** (10 min): Push/pull/habit/anxiety
8. **Design solution** (∞): Feature addressing underserved outcomes

**Total:** ~45 min + customer research

---

## Property Severity/Strength Values

| Property | Valid Values |
|----------|--------------|
| `painpointSeverity` | Minor, Moderate, Critical |
| `forceStrength` | Weak, Moderate, Strong |
| `habitStrength` | Light, Moderate, Deep |
| `anxietyType` | Financial Risk, Learning Curve, Social Risk, Performance Risk, Privacy/Security Risk |
| `outcomeDirection` | Minimize, Maximize |
| `metricType` | Time, Quality, Effort, Cost, Throughput |

---

**Pro Tip:** Start with the functional job, then identify related emotional and social jobs. All three types inform feature design.
