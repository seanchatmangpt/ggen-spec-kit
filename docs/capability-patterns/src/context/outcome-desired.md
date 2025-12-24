# 5. Outcome Desired

★★

*Progress isn't abstract. It's measurable. The outcomes people desire—specific, concrete improvements in their situation—define what success looks like for a capability.*

---

## The Measure of Progress

You know the **[Customer Job](./customer-job.md)**. You've identified the **[Circumstance of Struggle](./circumstance-of-struggle.md)**. Now ask: what does progress actually look like? How will the customer know they've made progress?

This is the outcome desired.

Outcomes are not features. Features are what we build. Outcomes are what customers experience. Consider:

- Feature: "Validation command checks RDF syntax"
- Outcome: "Reduce time to discover syntax errors from 5 minutes to 5 seconds"

The feature describes the mechanism. The outcome describes the *change in the customer's world*.

Features are inputs. Outcomes are outputs. Features are means. Outcomes are ends.

Designing for features produces tools. Designing for outcomes produces progress.

---

## The Problem

**Building features without defined outcomes leads to capabilities that are technically complete but experientially hollow.**

This manifests in predictable ways:

- The feature that works perfectly but doesn't improve the customer's situation
- The optimization that improves internal metrics but not customer experience
- The enhancement that adds complexity without adding value
- The refactoring that satisfies engineers but not users
- The product that is feature-complete but outcome-incomplete

Behind each failure lies the same mistake: measuring success by what we built rather than by how the customer's world improved.

---

## What is an Outcome?

An outcome is a specific, measurable improvement in the customer's situation when trying to get a job done.

### The Outcome Formula

Every outcome has three components:

```
[Direction] + [Metric] + [Object]
```

**Direction**: Is the customer trying to minimize or maximize something?
- **Minimize**: Less is better (time, errors, effort, friction, risk, cost)
- **Maximize**: More is better (speed, confidence, coverage, clarity, accuracy)

**Metric**: What specific measure captures this?
- **Time**: Seconds, minutes, hours, days
- **Count**: Number of items, errors, steps, attempts
- **Rate**: Percentage, ratio, frequency
- **Quality**: Accuracy, clarity, completeness
- **Effort**: Clicks, keystrokes, cognitive load

**Object**: What exactly is being measured?
- Time to [do what specific thing]?
- Number of [what specific things]?
- Rate of [what happening]?

### Outcome Statement Examples

**Well-formed outcome statements:**

| Direction | Metric | Object |
|-----------|--------|--------|
| Minimize | the time | to discover syntax errors |
| Minimize | the number | of undetected errors reaching CI |
| Maximize | the clarity | of error messages |
| Minimize | the effort | required to fix identified errors |
| Maximize | the confidence | that code is correct before committing |
| Minimize | the likelihood | of false positive errors |

**Poorly-formed outcome statements:**

| Statement | Problem |
|-----------|---------|
| "Better validation" | Not measurable |
| "Users like it" | Not specific |
| "Faster" | Missing object and metric |
| "More features" | Describes means, not ends |
| "High quality" | Undefined and subjective |

---

## The Forces at Play

Several forces make outcomes difficult to define and measure:

### Features Are Controllable; Outcomes Depend on Context

You can guarantee a feature works. You can write tests that verify it. You can ship it with confidence.

You cannot guarantee an outcome unless the context cooperates. "Reduce time to discover errors" depends on users actually using the feature, using it correctly, and in circumstances where time matters.

**Implication**: Design for adoption, not just functionality. An unused feature delivers no outcomes.

### Outcomes Require Baselines

You can't measure improvement without knowing the starting point.

"Reduce validation time to 5 seconds" means nothing if you don't know the current validation time. Is 5 seconds an improvement from 30 seconds? A regression from 2 seconds?

**Implication**: Measure before building. Establish baselines for the outcomes you intend to improve.

### Some Outcomes Are Hard to Measure

"Feel more confident" is a real outcome that matters. But how do you quantify confidence? How do you measure a feeling?

Not all outcomes map cleanly to numbers. Emotional and social outcomes especially resist quantification.

**Implication**: Create proxies. Indirect measures can approximate direct outcomes:
- "Time to abandon" approximates frustration
- "Completion rate" approximates confidence
- "Retry rate" approximates confusion
- "Recommendation rate" approximates satisfaction

### Outcomes Compound

Primary outcomes enable secondary outcomes. Faster validation enables more frequent validation, which enables catching errors earlier, which enables higher quality, which enables greater confidence, which enables faster shipping, which enables more learning, which enables better products.

Outcomes form chains. Improving one can cascade through many.

**Implication**: Understand the outcome hierarchy. Sometimes the most valuable improvement is upstream.

---

## Therefore

**For each job and circumstance, define the specific outcomes that represent progress.**

### The Outcome Definition Process

#### Step 1: Brainstorm Potential Outcomes

For the job and circumstance you've identified, list all ways the customer's situation could improve:

```
Job: Validate RDF ontology before committing
Circumstance: Pre-commit check

Potential outcomes:
- Faster detection of syntax errors
- Fewer errors reaching CI
- Less cognitive load during validation
- More confidence in code correctness
- Less embarrassment from caught errors
- Clearer understanding of what's wrong
- Easier fixes for identified problems
- Less anxiety about pushing code
- More consistent code quality
- Less rework after commit
```

Don't filter yet. Capture the full range of possible improvements.

#### Step 2: Structure as Outcome Statements

Transform each potential outcome into the formula:

| Direction | Metric | Object |
|-----------|--------|--------|
| Minimize | the time | to detect syntax errors |
| Minimize | the number | of errors reaching CI |
| Minimize | the cognitive load | during validation |
| Maximize | the confidence | in code correctness before commit |
| Minimize | the embarrassment | from errors caught by others |
| Maximize | the clarity | of error messages |
| Minimize | the effort | to fix identified problems |
| Minimize | the anxiety | about pushing code |
| Maximize | the consistency | of code quality across commits |
| Minimize | the rework | needed after commit |

#### Step 3: Establish Baselines and Targets

For each outcome, document current state and desired state:

| Outcome | Current (Baseline) | Target | Improvement |
|---------|-------------------|--------|-------------|
| Time to detect errors | 5 min (manual review) | 5 sec (automated) | 60x faster |
| Errors reaching CI | ~3 per commit | 0 | 100% reduction |
| Error message clarity | Low (cryptic) | High (actionable) | Qualitative |
| Effort to fix | 2 min per error | 30 sec per error | 4x easier |
| Confidence pre-commit | Low | High | Qualitative |

Baselines ground you in reality. Targets give you something to aim for.

#### Step 4: Assess Importance vs. Satisfaction

For each outcome, evaluate:

**Importance**: How much does this outcome matter to the customer?
- Critical (job fails without it)
- High (significant impact on success)
- Medium (noticeable impact)
- Low (nice to have)

**Current Satisfaction**: How well do existing solutions address this outcome?
- Not at all (completely unmet)
- Poorly (significant gaps)
- Somewhat (adequate but improvable)
- Well (competitive)
- Fully (no improvement possible)

The gap between importance and satisfaction reveals opportunity:

```
                     SATISFACTION
                Low ──────────────────▶ High
          ┌────────────────────────────────────┐
    High  │  ★★★★★ OPPORTUNITY      ★★☆☆☆    │
          │  Critical to address     Maintain │
          │                                    │
    I     │                                    │
    M     │  ★★★★☆                   ★☆☆☆☆    │
    P     │  High opportunity        Low      │
    O     │                          priority │
    R     │                                    │
    T     │  ★★★☆☆                   ★☆☆☆☆    │
    A     │  Worth addressing        Nice to  │
    N     │                          have     │
    C     │                                    │
    E     │  ★★☆☆☆                   ★☆☆☆☆    │
          │  Low priority            Skip     │
    Low   │                                    │
          └────────────────────────────────────┘
```

Focus on high importance + low satisfaction = high opportunity.

#### Step 5: Prioritize Outcomes

Based on importance, satisfaction gap, and feasibility, rank outcomes:

| Priority | Outcome | Importance | Satisfaction | Gap | Feasibility |
|----------|---------|------------|--------------|-----|-------------|
| 1 | Minimize time to detect errors | Critical | Low | High | High |
| 2 | Maximize clarity of error messages | High | Low | High | High |
| 3 | Minimize errors reaching CI | High | Low | High | Medium |
| 4 | Minimize effort to fix issues | Medium | Low | Medium | High |
| 5 | Maximize confidence | High | Medium | Medium | Medium |

The highest-priority outcomes become your design drivers.

---

## The Outcome Hierarchy

Outcomes form hierarchies. Understanding this hierarchy helps you prioritize wisely.

### Enabling Outcomes

Some outcomes enable others:

```
Minimize time to detect syntax errors
    └── Enables: Minimize time to fix errors
        └── Enables: Minimize time to commit clean code
            └── Enables: Maximize confidence in commits
                └── Enables: Minimize anxiety when pushing
                    └── Enables: Maximize willingness to ship frequently
```

Improving upstream outcomes creates cascading benefits downstream.

### Competing Outcomes

Some outcomes compete:

```
Maximize thoroughness of validation
    ↔ Conflicts with: Minimize time to complete validation
```

This is the **[Forces in Tension](./forces-in-tension.md)** pattern manifesting at the outcome level. You must design for trade-offs.

### Orthogonal Outcomes

Some outcomes are independent:

```
Minimize errors in syntax
    ⊥ Independent of: Minimize errors in semantics
```

Independent outcomes can be addressed separately.

---

## Outcome Measurement

### Direct Measurement

When possible, measure the outcome directly:

| Outcome | Direct Measure | How to Capture |
|---------|---------------|----------------|
| Time to detect errors | Elapsed time | Instrumentation |
| Errors reaching CI | Count of CI failures | CI logs |
| Error message clarity | Comprehension score | User testing |

### Proxy Measurement

When direct measurement is difficult, use proxies:

| Outcome | Proxy Measure | Rationale |
|---------|---------------|-----------|
| Confidence | Completion rate without retry | Confident users don't second-guess |
| Clarity | Time to understand error | Clear messages are understood quickly |
| Anxiety | Pre-commit hesitation time | Anxious users hesitate before committing |

### Qualitative Measurement

Some outcomes resist quantification. Use qualitative methods:

- **User interviews**: "How confident do you feel when using this?"
- **Observation**: Watch body language, hear sighs of frustration or relief
- **Diary studies**: Have users journal their experience over time
- **Support analysis**: What complaints and questions emerge?

---

## Representing Outcomes in RDF

Outcomes can be formally captured in specifications:

```turtle
@prefix jtbd: <http://example.org/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Outcome definition
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    rdfs:label "Minimize validation time"@en ;
    rdfs:comment "Reduce the time from initiating validation to receiving results"@en ;

    # Formula components
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:object "discovering syntax errors" ;

    # Baselines and targets
    jtbd:baseline "PT5M"^^xsd:duration ;
    jtbd:baselineContext "Manual review of ontology file"@en ;
    jtbd:target "PT5S"^^xsd:duration ;
    jtbd:targetRationale "Fast enough to maintain developer flow state"@en ;

    # Importance assessment
    jtbd:importance "critical" ;
    jtbd:importanceRationale "Slow validation breaks flow and reduces adoption"@en ;
    jtbd:currentSatisfaction "low" ;
    jtbd:satisfactionRationale "Current tools take 5+ minutes"@en ;

    # Relationships
    jtbd:concernsJob jtbd:ValidateOntologyJob ;
    jtbd:relevantToCircumstance jtbd:PreCommitCircumstance ;
    jtbd:enablesOutcome jtbd:MinimizeErrorFixTime ;
    jtbd:conflictsWith jtbd:MaximizeThoroughness .

jtbd:MaximizeErrorClarity a jtbd:Outcome ;
    rdfs:label "Maximize error message clarity"@en ;

    jtbd:direction "maximize" ;
    jtbd:metric "clarity" ;
    jtbd:object "error messages" ;

    jtbd:importance "high" ;
    jtbd:currentSatisfaction "low" ;

    jtbd:concernsJob jtbd:ValidateOntologyJob ;
    jtbd:enablesOutcome jtbd:MinimizeEffortToFix .

# Outcome hierarchies
jtbd:MinimizeValidationTime jtbd:enablesOutcome jtbd:MinimizeErrorFixTime .
jtbd:MinimizeErrorFixTime jtbd:enablesOutcome jtbd:MinimizeTimeToCommit .
jtbd:MinimizeTimeToCommit jtbd:enablesOutcome jtbd:MaximizeConfidence .
jtbd:MaximizeConfidence jtbd:enablesOutcome jtbd:MinimizeCommitAnxiety .
```

### Querying Outcomes

With outcomes in RDF, you can query them:

```sparql
# Find high-importance, low-satisfaction outcomes (opportunities)
SELECT ?outcome ?label ?direction ?metric ?object
WHERE {
    ?outcome a jtbd:Outcome ;
             rdfs:label ?label ;
             jtbd:direction ?direction ;
             jtbd:metric ?metric ;
             jtbd:object ?object ;
             jtbd:importance "critical" ;
             jtbd:currentSatisfaction "low" .
}

# Find outcome hierarchies
SELECT ?upstream ?downstream
WHERE {
    ?upstream jtbd:enablesOutcome ?downstream .
}

# Find outcomes relevant to a specific circumstance
SELECT ?outcome ?label
WHERE {
    ?outcome a jtbd:Outcome ;
             rdfs:label ?label ;
             jtbd:relevantToCircumstance jtbd:PreCommitCircumstance .
}

# Find conflicting outcomes
SELECT ?outcome1 ?outcome2
WHERE {
    ?outcome1 jtbd:conflictsWith ?outcome2 .
}
```

### Generated Documentation

From outcome specifications, generate documentation:

```markdown
## Outcomes: RDF Validation

### Priority Outcomes

#### 1. Minimize validation time
- **Current**: 5 minutes (manual review)
- **Target**: 5 seconds (automated)
- **Improvement**: 60x faster
- **Importance**: Critical - slow validation breaks flow
- **Enables**: Faster error fixes → Faster commits → Greater confidence

#### 2. Maximize error message clarity
- **Current**: Low (cryptic messages)
- **Target**: High (actionable with fix suggestions)
- **Importance**: High - unclear messages waste time
- **Enables**: Faster error fixes

### Outcome Hierarchy

```
Minimize validation time
└── Minimize error fix time
    └── Minimize time to commit
        └── Maximize confidence
            └── Minimize commit anxiety
```

### Trade-offs

- "Minimize validation time" conflicts with "Maximize thoroughness"
  - Resolution: Provide multiple modes (quick/full)
```

---

## Case Study: The Feature That Wasn't

A team built a feature: "Show SHACL shape violations with line numbers."

They shipped it. Users said "nice." Usage was mediocre.

The feature worked. But what outcome did it serve?

When they investigated, they found:
- The underlying job was "feel confident before committing"
- The relevant outcome was "minimize time to understand what's wrong"
- Line numbers helped—but users still couldn't understand the SHACL vocabulary

The feature addressed a symptom, not the outcome.

**The fix:**

They redefined success around the outcome:

**Outcome**: Minimize time to understand what's wrong

| Before | After |
|--------|-------|
| "Shape violation at line 47: sh:minCount constraint failed" | "Line 47: The 'author' property is required but missing. Add: `dcterms:author <person>.`" |

The new version:
- Translated SHACL vocabulary to plain English
- Explained what was expected
- Suggested how to fix

Time to understand dropped from minutes to seconds. The outcome was achieved.

---

## Case Study: Measuring the Unmeasurable

A team wanted to improve "developer confidence." But how do you measure confidence?

They tried direct measurement:
- Survey after each commit: "How confident do you feel?"
- Response rate: 2%. Unhelpful.

They switched to proxies:

| Proxy | Rationale | Finding |
|-------|-----------|---------|
| Pre-commit hesitation time | Confident users commit quickly | Reduced from 45s to 12s |
| Post-commit check rate | Confident users don't double-check | Reduced from 80% to 25% |
| Revert rate | Confident users make fewer mistakes | Reduced from 5% to 1% |

The proxies told the story. Confidence improved, even though it was never directly measured.

---

## Checklist: Have You Defined Outcomes?

Before proceeding to design, verify:

### Outcome Identification
- [ ] I have listed specific outcomes for this job and circumstance
- [ ] Each outcome follows the formula: Direction + Metric + Object
- [ ] I have covered functional, emotional, and social outcomes

### Baselines and Targets
- [ ] I have established baselines for each outcome
- [ ] I have set targets that represent meaningful improvement
- [ ] Targets are specific and measurable (or have defined proxies)

### Prioritization
- [ ] I have assessed importance for each outcome
- [ ] I have assessed current satisfaction for each outcome
- [ ] I have identified the high-opportunity outcomes

### Hierarchies and Trade-offs
- [ ] I understand how outcomes enable or conflict with each other
- [ ] I have identified upstream outcomes that create cascading benefits
- [ ] I have strategies for managing conflicting outcomes

### Measurement
- [ ] I have defined how each outcome will be measured
- [ ] I have proxies for hard-to-measure outcomes
- [ ] I have plans for both quantitative and qualitative assessment

If any of these remain unclear, invest more time in understanding before building.

---

## Resulting Context

After applying this pattern, you have:

- Specific, measurable outcome statements
- Baselines and targets for each outcome
- Understanding of importance and satisfaction gaps
- Criteria for evaluating whether a capability succeeds
- A hierarchy showing how outcomes connect

These outcomes feed directly into:
- **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria derive from outcomes
- **[40. Outcome Measurement](../evolution/outcome-measurement.md)** — Track outcome delivery over time

---

## Code References

The following spec-kit source files implement outcome concepts discussed in this pattern:

| Reference | Description |
|-----------|-------------|
| `ontology/jtbd-schema.ttl:51-108` | Outcome class with direction, metric, object properties |
| `ontology/jtbd-schema.ttl:889-920` | DesiredOutcomeShape SHACL validation for outcome specifications |
| `ontology/jtbd-schema.ttl:110-112` | OutcomeMetric enumeration (time, count, rate, quality, effort) |
| `src/specify_cli/core/jtbd_metrics.py:50-100` | Instrumentation tracking outcome achievement |
| `ontology/spec-kit-schema.ttl:584-617` | AcceptanceScenarioShape linking scenarios to outcomes |
| `ontology/spec-kit-schema.ttl:652-676` | SuccessCriterionShape defining outcome measurement |

---

## Related Patterns

### Builds on:

**[2. Customer Job](./customer-job.md)** — Outcomes express progress on jobs.

**[4. Circumstance of Struggle](./circumstance-of-struggle.md)** — Circumstances contextualize outcomes.

### Enables:

**[6. Progress Maker](./progress-maker.md)** — What makes progress possible.

### Shapes:

**[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria derive from outcomes.

### Measured by:

**[40. Outcome Measurement](../evolution/outcome-measurement.md)** — Track outcome delivery.

---

## Philosophical Foundations

> *"If you can't measure it, you can't improve it."*
>
> — Peter Drucker

But also: if you measure the wrong thing, you'll improve the wrong thing.

Features are easy to measure. Did we ship the feature? Yes or no. Is it bug-free? Mostly.

Outcomes are harder to measure. Did the customer's life improve? By how much? The measurement is difficult, but it's what matters.

Organizations optimize for what they measure. If you measure features, you'll ship features. If you measure outcomes, you'll create progress.

> *"We have a strategic plan. It's called doing things."*
>
> — Herb Kelleher

Doing things is necessary but not sufficient. Doing things that create outcomes—that's the goal.

---

## Exercise: Define Your Outcomes

Before designing your next capability, complete this exercise:

1. **List potential outcomes**: What could improve for the customer?

2. **Structure as statements**: Direction + Metric + Object for each.

3. **Establish baselines**: What's the current state?

4. **Set targets**: What's the desired state?

5. **Assess importance and satisfaction**: Where are the gaps?

6. **Prioritize**: Which outcomes matter most?

7. **Define measurement**: How will you know if outcomes improve?

Only after completing this exercise should you proceed to identify **[Progress Makers](./progress-maker.md)**.

---

## Further Reading

- Ulwick, Tony. *Jobs to Be Done: Theory to Practice* (2016) — The Outcome-Driven Innovation methodology.
- Osterwalder, Alex. *Value Proposition Design* (2014) — Connecting features to customer outcomes.
- Croll, Alistair & Yoskovitz, Benjamin. *Lean Analytics* (2013) — Measuring what matters.
- Hubbard, Douglas. *How to Measure Anything* (2014) — Making the intangible tangible.

---

Features are means. Outcomes are ends. Build for outcomes, and you build for progress.
