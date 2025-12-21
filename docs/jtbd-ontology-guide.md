# JTBD Ontology Guide - Jobs To Be Done for Spec-Kit

## Overview

The JTBD (Jobs To Be Done) ontology extends spec-kit with customer-centric feature development based on Clayton Christensen's Jobs To Be Done theory. It enables you to specify features based on deep customer understanding rather than just technical requirements.

**Location:** `/Users/sac/ggen-spec-kit/ontology/jtbd-schema.ttl`

**Constitutional Equation:**
```
jtbd-spec.md = μ(jtbd-feature.ttl)
```

## Core Concepts

### 1. Jobs - What Customers Try to Accomplish

**Jobs are stable over time and solution-agnostic.** They represent the fundamental progress customers are trying to make in their lives.

#### Job Types

```turtle
# Functional Job - The practical task
:EnsureCodeQuality a jtbd:FunctionalJob ;
    jtbd:jobTitle "Ensure Code Quality Before Merging" ;
    jtbd:jobDescription "Verify new code meets standards..." ;
    jtbd:jobType "Functional" .

# Emotional Job - How they want to feel
:FeelConfident a jtbd:EmotionalJob ;
    jtbd:jobTitle "Feel Confident About Merge Decisions" ;
    jtbd:jobType "Emotional" .

# Social Job - How they want to be perceived
:MaintainReputation a jtbd:SocialJob ;
    jtbd:jobTitle "Maintain Reputation as Thorough Reviewer" ;
    jtbd:jobType "Social" .
```

#### Job Statement Structure

The canonical format: **"When [context], I want to [achieve outcome] so I can [benefit]"**

```turtle
:JobStatement a jtbd:JobStatement ;
    jtbd:when "I receive a pull request for critical code" ;
    jtbd:wantTo "quickly identify security vulnerabilities" ;
    jtbd:soICan "confidently approve without fear of bugs" ;
    jtbd:fullStatement "When I receive a pull request for critical code, I want to quickly identify security vulnerabilities, so I can confidently approve without fear of bugs." .
```

### 2. Desired Outcomes - How Customers Measure Success

Outcomes are measurable, stable criteria that customers use to judge whether a job is done well.

#### Outcome Statement Format

**"Minimize/Maximize [metric] [object] [clarifier]"**

```turtle
:MinimizeTimeToFindIssues a jtbd:DesiredOutcome ;
    jtbd:outcomeStatement "Minimize the time it takes to identify critical bugs in pull requests" ;
    jtbd:outcomeDirection "Minimize" ;
    jtbd:outcomeMetric "time" ;
    jtbd:outcomeObject "to identify critical bugs" ;
    jtbd:outcomeClarifier "in pull requests" .
```

#### Outcome Prioritization

Use importance and satisfaction scores to calculate opportunity:

```turtle
:OutcomePriority a jtbd:OutcomePriority ;
    jtbd:importanceScore "9.2"^^xsd:decimal ;    # How important (1-10)
    jtbd:satisfactionScore "4.1"^^xsd:decimal .  # How satisfied (1-10)

:OpportunityScore a jtbd:OpportunityScore ;
    jtbd:opportunityScoreValue "14.3"^^xsd:decimal ;  # Importance + (Importance - Satisfaction)
    jtbd:opportunityType "Underserved" .              # > 10 = innovation opportunity
```

**Opportunity Score Interpretation:**
- **< 5:** Overserved (customers don't care, avoid over-engineering)
- **5-10:** Appropriately served (maintain current solution)
- **10-15:** Underserved (high innovation opportunity)
- **> 15:** Severely underserved (critical unmet need)

### 3. Customer Segments - Who Has the Job

Segments are defined by **job circumstances**, not demographics.

```turtle
:SeniorEngineerSegment a jtbd:CustomerSegment ;
    jtbd:segmentName "Senior Engineers with Review Responsibilities" ;
    jtbd:segmentDescription "Engineers (5+ years) who review PRs regularly..." ;
    jtbd:segmentSize "12000"^^xsd:integer ;
    jtbd:marketShare "35.5"^^xsd:decimal ;
    jtbd:hasPersona :TechLeadAlex .

:TechLeadAlex a jtbd:Persona ;
    jtbd:personaName "Tech Lead Alex" ;
    jtbd:personaRole "Senior Software Engineer & Tech Lead" ;
    jtbd:personaGoals "Maintain quality while helping team grow" ;
    jtbd:personaChallenges "Limited time (5-10 PRs/day), fear of missing critical issues" .
```

### 4. Forces - What Pushes/Pulls Decision-Making

The **Forces of Progress** model explains why customers switch solutions (or don't).

```
Progress Makers (toward new solution):
├─ Push Forces: Problems with current state
└─ Pull Forces: Benefits of new solution

Progress Brakers (against new solution):
├─ Habits: Inertia of current behavior
└─ Anxieties: Fears about switching
```

#### Example Forces

```turtle
# PUSH - Problem with current solution
:ManualReviewPain a jtbd:PushForce ;
    jtbd:pushReason "Manual review is time-consuming and error-prone" ;
    jtbd:forceStrength "Strong" .

# PULL - Attraction to new solution
:AutomatedInsights a jtbd:PullForce ;
    jtbd:pullBenefit "AI analysis flags issues automatically" ;
    jtbd:forceStrength "Strong" .

# HABIT - Current behavior creating inertia
:ManualLineByLineReview a jtbd:Habit ;
    jtbd:habitDescription "Reviewers read every line manually" ;
    jtbd:habitStrength "Moderate" .

# ANXIETY - Fear preventing adoption
:MissingCriticalBugs a jtbd:Anxiety ;
    jtbd:anxietyDescription "Fear automated tools will miss subtle bugs" ;
    jtbd:anxietyType "Performance Risk" ;
    jtbd:forceStrength "Moderate" .
```

### 5. Painpoints - Specific Friction

Painpoints are concrete obstacles preventing job completion.

```turtle
:SlowReviewProcess a jtbd:Painpoint ;
    jtbd:painpointDescription "Manual review takes 30+ minutes per PR" ;
    jtbd:painpointSeverity "Critical" ;
    jtbd:workaround "Reviewers skim large PRs, missing issues" .
```

**Severity Levels:**
- **Minor:** Annoyance (doesn't block progress)
- **Moderate:** Significant friction (slows progress)
- **Critical:** Blocking (prevents job completion)

### 6. Context Clues - When Jobs Arise

Context clues signal **when** a job needs to be done.

```turtle
:PullRequestNotification a jtbd:ContextClue ;
    jtbd:contextDescription "Developer receives PR ready for review notification" ;
    jtbd:triggerType "Event-based" ;
    jtbd:triggerFrequency "Daily" .
```

### 7. Success Metrics - Measuring Completion

Define concrete, measurable criteria for job success.

```turtle
:TimeToReviewMetric a jtbd:SuccessMetric ;
    jtbd:metricName "Time to Complete Review" ;
    jtbd:metricType "Time" ;
    jtbd:targetValue "< 15 minutes for PRs under 500 lines" ;
    jtbd:currentValue "~35 minutes average" .
```

**Metric Types:**
- **Time:** Duration, frequency
- **Quality:** Accuracy, completeness, defect rate
- **Effort:** Steps, cognitive load, complexity
- **Cost:** Money, resources
- **Throughput:** Volume, capacity

## Integration with Spec-Kit Features

Connect JTBD research to spec-kit feature specifications:

```turtle
# 1. Start with JTBD research
:EnsureCodeQualityJob a jtbd:FunctionalJob ;
    jtbd:hasDesiredOutcome :MinimizeTimeToFindIssues ;
    jtbd:hasPainpoint :SlowReviewProcess .

# 2. Create feature addressing painpoint
:AICodeReviewFeature a sk:Feature ;
    sk:featureBranch "001-ai-code-review" ;
    jtbd:targetsSegment :SeniorEngineerSegment ;
    jtbd:addressesPainpoint :SlowReviewProcess ;
    jtbd:enablesOutcome :MinimizeTimeToFindIssues .

# 3. Link job to feature
:EnsureCodeQualityJob jtbd:informsFeature :AICodeReviewFeature .
```

## JTBD Development Workflow

### Step 1: Identify the Job

**Bad (solution-centric):**
> "Users want a better code review UI"

**Good (job-centric):**
> "Developers need to ensure code quality before merging to prevent production bugs"

### Step 2: Write Job Statement

Template: **"When [context], I want to [outcome], so I can [benefit]"**

```turtle
:JobStatement a jtbd:JobStatement ;
    jtbd:when "I receive a pull request notification for critical code" ;
    jtbd:wantTo "quickly identify security vulnerabilities and bugs" ;
    jtbd:soICan "confidently approve without fear of production incidents" .
```

### Step 3: Define Desired Outcomes

List 8-12 outcomes using **"Minimize/Maximize [metric] [object]"** format:

```turtle
:Job
    jtbd:hasDesiredOutcome
        :MinimizeTimeToFindIssues,
        :MinimizeLikelihoodOfMissedDefects,
        :MaximizeConfidenceInApproval,
        :MinimizeContextSwitches .
```

### Step 4: Prioritize Outcomes

Survey customers to get importance and satisfaction scores:

```turtle
:OutcomePriority
    jtbd:importanceScore "9.2"^^xsd:decimal ;
    jtbd:satisfactionScore "4.1"^^xsd:decimal .

:OpportunityScore
    jtbd:opportunityScoreValue "14.3"^^xsd:decimal ;  # 9.2 + (9.2 - 4.1)
    jtbd:opportunityType "Underserved" .              # Focus here!
```

### Step 5: Identify Painpoints

What specifically prevents job completion?

```turtle
:Painpoint
    jtbd:painpointDescription "Manual review takes 30+ minutes per PR" ;
    jtbd:painpointSeverity "Critical" ;
    jtbd:workaround "Skip thorough review, trust tests" .
```

### Step 6: Map Forces

Understand what drives/prevents adoption:

```turtle
:Job
    jtbd:hasPushForce :ManualReviewPain ;      # Why leave current solution
    jtbd:hasPullForce :AutomatedInsights ;     # Why adopt new solution
    jtbd:hasHabit :ManualReview ;              # Why stay with current
    jtbd:hasAnxiety :MissingBugs .             # Why fear new solution
```

### Step 7: Design Solution

Create feature that:
1. **Reduces painpoints** (addresses friction)
2. **Enables high-opportunity outcomes** (focuses on underserved needs)
3. **Overcomes anxieties** (builds trust)
4. **Disrupts habits** (makes switching easy)

```turtle
:Feature
    jtbd:addressesPainpoint :SlowReviewProcess ;
    jtbd:enablesOutcome :MinimizeTimeToFindIssues ;
    jtbd:targetsSegment :SeniorEngineerSegment .
```

## SHACL Validation

The ontology includes comprehensive SHACL shapes to validate your JTBD specifications:

```bash
# Validate JTBD specification
ggen validate --config docs/ggen.toml docs/examples/jtbd-example-feature.ttl
```

**Common Validation Rules:**
- Job must have title, description, type, job statement, and desired outcomes
- Job statement must have when/wantTo/soICan components
- Desired outcomes must have direction (Minimize/Maximize), metric, and object
- Importance/satisfaction scores must be 1-10
- Opportunity scores must be 0-30
- Painpoint severity must be Minor/Moderate/Critical
- Force strength must be Weak/Moderate/Strong

## Best Practices

### ✅ DO

1. **Focus on the job, not the solution**
   - ❌ "Users want a dark mode toggle"
   - ✅ "Users want to reduce eye strain during extended work sessions"

2. **Make outcomes measurable**
   - ❌ "Make review better"
   - ✅ "Minimize time to identify critical bugs (< 15 minutes)"

3. **Segment by circumstances, not demographics**
   - ❌ "Developers aged 25-35"
   - ✅ "Senior engineers reviewing 5+ PRs daily under time pressure"

4. **Use customer language**
   - ❌ "Optimize algorithmic complexity analysis"
   - ✅ "Quickly spot performance problems"

5. **Connect to real painpoints**
   - Include workarounds customers currently use
   - Measure severity objectively

### ❌ DON'T

1. **Don't assume solutions**
   - Jobs should be solution-agnostic
   - Focus on progress customers want to make

2. **Don't use vague outcomes**
   - Every outcome needs a concrete metric
   - Must be measurable and observable

3. **Don't ignore forces**
   - Understanding why customers resist change is critical
   - Habits and anxieties are as important as painpoints

4. **Don't skip opportunity scoring**
   - Importance without satisfaction is incomplete
   - Focus innovation on underserved outcomes (score > 10)

## Example: Complete JTBD Specification

See `/Users/sac/ggen-spec-kit/docs/examples/jtbd-example-feature.ttl` for a comprehensive example showing:

- **Primary functional job** (ensure code quality)
- **Related emotional/social jobs** (feel confident, maintain reputation)
- **8+ desired outcomes** with importance/satisfaction/opportunity scores
- **Success metrics** (time, quality, coverage)
- **Customer segment** with persona
- **Painpoints** (slow review, missed security issues)
- **Forces** (push/pull/habit/anxiety)
- **Current and proposed solutions**
- **Integration with spec-kit Feature**

## RDF Properties Reference

### Job Classes

| Class | Purpose | Required Properties |
|-------|---------|---------------------|
| `jtbd:Job` | Base job class | `jobTitle`, `jobDescription`, `jobType` |
| `jtbd:FunctionalJob` | Core practical task | Same as Job |
| `jtbd:EmotionalJob` | Desired feeling | Same as Job |
| `jtbd:SocialJob` | Desired perception | Same as Job |

### Outcome Classes

| Class | Purpose | Required Properties |
|-------|---------|---------------------|
| `jtbd:DesiredOutcome` | Measurable success criterion | `outcomeStatement`, `outcomeDirection`, `outcomeMetric`, `outcomeObject` |
| `jtbd:OutcomePriority` | Importance/satisfaction scores | `importanceScore`, `satisfactionScore` |
| `jtbd:OpportunityScore` | Innovation potential | `opportunityScoreValue`, `opportunityType` |

### Customer Classes

| Class | Purpose | Required Properties |
|-------|---------|---------------------|
| `jtbd:CustomerSegment` | Job-based customer group | `segmentName`, `segmentDescription` |
| `jtbd:Persona` | Representative archetype | `personaName`, `personaRole`, `personaGoals`, `personaChallenges` |

### Force Classes

| Class | Purpose | Required Properties |
|-------|---------|---------------------|
| `jtbd:PushForce` | Problem with current state | `pushReason`, `forceStrength` |
| `jtbd:PullForce` | Attraction to new solution | `pullBenefit`, `forceStrength` |
| `jtbd:Habit` | Inertia of current behavior | `habitDescription`, `habitStrength` |
| `jtbd:Anxiety` | Fear preventing adoption | `anxietyDescription`, `anxietyType` |

## ggen Transformation

Use SPARQL queries and Tera templates to generate JTBD documentation from RDF:

```toml
# docs/ggen.toml
[[transformations]]
name = "jtbd-feature-spec"
input = "memory/jtbd/*.ttl"
queries = "sparql/jtbd-queries.rq"
templates = "templates/jtbd-spec.md.tera"
output = "docs/jtbd/{feature-name}.md"
```

## Further Reading

- **Clayton Christensen:** "Competing Against Luck" (original JTBD theory)
- **Tony Ulwick:** "Jobs to be Done: Theory to Practice" (Outcome-Driven Innovation)
- **Alan Klement:** "When Coffee and Kale Compete" (JTBD for product development)
- **Bob Moesta:** "Demand-Side Sales 101" (Forces of Progress)

## Support

For questions or contributions to the JTBD ontology:
- Open an issue in the spec-kit repository
- Review `/Users/sac/ggen-spec-kit/docs/examples/jtbd-example-feature.ttl`
- Validate with `ggen validate` before committing
