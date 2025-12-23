# 4. Circumstance of Struggle

★★

*A job alone doesn't tell you when to act. The circumstance—the specific moment when struggle becomes acute—reveals when capability matters most.*

---

## The Moment of Truth

You understand the **[Customer Job](./customer-job.md)**. You've mapped the **[Forces in Tension](./forces-in-tension.md)**. But when does this job actually arise? When do people feel the need acutely enough to seek a solution?

This is the circumstance of struggle.

A job might exist abstractly for years. "I should validate my code" is a perpetual background thought. But the *circumstance* creates urgency—the specific moment when the abstract becomes concrete, when "I should" becomes "I must."

Understanding circumstances transforms vague requirements into actionable design.

---

## The Problem

**Capabilities designed for abstract jobs rather than concrete circumstances miss the moment when they're needed most.**

This manifests in predictable ways:

- The tool that works great in tutorials but fails in the heat of battle
- The feature that's technically correct but never invoked at the right time
- The automation that triggers when nobody needs it and stays silent when everyone does
- The interface that assumes calm and focus when users are stressed and distracted
- The workflow that ignores the emotional reality of the moment

Behind each failure lies the same mistake: designing for the job in the abstract rather than the circumstance in the concrete.

---

## What is a Circumstance?

A circumstance is the specific situation in which a job arises. It includes:

### The Trigger

What event or realization initiates the need?

- An external event (customer bug report, approaching deadline, colleague question)
- An internal event (finishing a task, making a decision, noticing something wrong)
- A periodic event (daily standup, weekly review, release cycle milestone)

The trigger transforms potential need into actual need.

### The Emotional State

How is the person feeling when the need arises?

- Confident or anxious?
- Rushed or reflective?
- Focused or distracted?
- Calm or stressed?
- Optimistic or frustrated?

The emotional state determines what kind of help is welcome. An anxious person needs reassurance. A rushed person needs speed. A frustrated person needs empathy.

### The Time Budget

How much time can they invest?

- Seconds (pre-commit check, quick validation)
- Minutes (debugging session, code review)
- Hours (deep investigation, learning mode)

The time budget constrains what's possible. A 30-second task can't use a 5-minute tool.

### The Attention Context

What else is competing for their attention?

- Deep work (single-tasking, minimal interruption tolerance)
- Shallow work (multi-tasking, frequent context switches)
- Social context (meeting, pair programming, demo)

The attention context determines how much cognitive load is acceptable.

### The Consequences

What happens if the job isn't done?

- Immediate consequences (broken pipeline, blocked colleagues)
- Delayed consequences (bug discovered later, technical debt)
- Social consequences (embarrassment, blame, lost credibility)

The consequences determine how much effort is justified.

---

## The Forces at Play

Several forces make circumstances difficult to design for:

### Jobs Are Continuous; Circumstances Are Discrete

The job exists always. The circumstance punctuates time with moments of need.

You can't design for "always"—it's too abstract. You can design for "when"—specific moments with specific characteristics.

### Urgency Varies Dramatically

The same job under different circumstances may be critical or ignorable.

"Validate my code" at 2 PM on Tuesday = nice to have
"Validate my code" at 5:55 PM on release day = critical path

### Context Shapes Tolerance

In a crisis, people accept friction. In routine, friction drives them away.

A tool that's acceptable during debugging may be unacceptable during flow state. A workflow that's fine once a week may be intolerable if it's needed every commit.

### Multiple Circumstances, One Job

The same job arises in many circumstances. Each might need different support.

This is perhaps the most important insight: a single capability often needs multiple "modes" or even separate interfaces to serve different circumstances.

---

## Therefore

**For each job, identify the key circumstances when it arises.**

### The Circumstance Mapping Process

#### Step 1: Enumerate Circumstances

List all the situations where this job becomes relevant:

| # | Circumstance | Description |
|---|--------------|-------------|
| 1 | Pre-commit | Developer finishes changes, about to commit |
| 2 | CI failure | Build broke, need to diagnose |
| 3 | Code review | Reviewing someone else's changes |
| 4 | Learning mode | Exploring unfamiliar codebase |
| 5 | Pre-release | Final checks before production |
| 6 | Customer escalation | Bug reported, pressure to fix |

Don't try to be exhaustive. Focus on the most common or most important.

#### Step 2: Profile Each Circumstance

For each circumstance, document its characteristics:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CIRCUMSTANCE PROFILE                             │
├─────────────────────────────────────────────────────────────────────┤
│ Name: Pre-commit validation                                         │
│                                                                     │
│ TRIGGER                                                             │
│ What: Developer finishes a set of changes, types `git commit`       │
│ Type: Internal event (task completion decision)                     │
│                                                                     │
│ EMOTIONAL STATE                                                     │
│ Primary: Eager to close the task                                    │
│ Secondary: Slight anxiety about correctness                         │
│ Energy level: Medium (end of a work session)                        │
│                                                                     │
│ TIME BUDGET                                                         │
│ Ideal: < 2 seconds                                                  │
│ Acceptable: < 5 seconds                                             │
│ Unacceptable: > 10 seconds                                          │
│                                                                     │
│ ATTENTION CONTEXT                                                   │
│ Mode: Transitioning from deep work to shallow work                  │
│ Interruption tolerance: Low (want to finish and context-switch)     │
│                                                                     │
│ CONSEQUENCES OF NOT DOING                                           │
│ Immediate: None                                                     │
│ Delayed: Possible CI failure, wasted round-trip                     │
│ Social: Embarrassment if errors found by others                     │
│                                                                     │
│ DESIGN IMPLICATIONS                                                 │
│ 1. Speed is paramount—must complete in seconds                      │
│ 2. Clear pass/fail—no ambiguity                                     │
│ 3. Brief output—don't overwhelm, just summarize                     │
│ 4. Non-blocking option—let user override if needed                  │
│ 5. Minimal cognitive load—user is ready to move on                  │
└─────────────────────────────────────────────────────────────────────┘
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CIRCUMSTANCE PROFILE                             │
├─────────────────────────────────────────────────────────────────────┤
│ Name: Debugging session                                             │
│                                                                     │
│ TRIGGER                                                             │
│ What: Test failure or customer bug report                           │
│ Type: External event (something went wrong)                         │
│                                                                     │
│ EMOTIONAL STATE                                                     │
│ Primary: Frustrated                                                 │
│ Secondary: Determined, investigative                                │
│ Energy level: Variable (depends on pressure)                        │
│                                                                     │
│ TIME BUDGET                                                         │
│ Ideal: As fast as possible                                          │
│ Acceptable: Minutes to hours                                        │
│ Unacceptable: N/A (will wait for thorough results)                  │
│                                                                     │
│ ATTENTION CONTEXT                                                   │
│ Mode: Deep work, problem-solving                                    │
│ Interruption tolerance: Medium (focused but welcomes help)          │
│                                                                     │
│ CONSEQUENCES OF NOT DOING                                           │
│ Immediate: Bug persists                                             │
│ Delayed: Customer unhappy, escalation                               │
│ Social: Pressure, blame if not resolved                             │
│                                                                     │
│ DESIGN IMPLICATIONS                                                 │
│ 1. Depth matters more than speed                                    │
│ 2. Detailed diagnostics—help understand root cause                  │
│ 3. Interactive exploration—let user dig deeper                      │
│ 4. Context preservation—connect to related information              │
│ 5. Progress indication—show that something is happening             │
└─────────────────────────────────────────────────────────────────────┘
```

#### Step 3: Compare Across Circumstances

Create a comparison matrix to see how requirements differ:

| Dimension | Pre-commit | Debug | Code Review | Pre-release |
|-----------|------------|-------|-------------|-------------|
| Speed priority | ★★★★★ | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ |
| Detail priority | ★★☆☆☆ | ★★★★★ | ★★★★☆ | ★★★★★ |
| Pass/fail clarity | ★★★★★ | ★★☆☆☆ | ★★★☆☆ | ★★★★★ |
| Override needed | ★★★★☆ | ★☆☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| Interactive mode | ★☆☆☆☆ | ★★★★★ | ★★★☆☆ | ★★★☆☆ |

This matrix reveals that a single interface cannot serve all circumstances equally.

#### Step 4: Design for Each Circumstance

For each circumstance, articulate the capability mode that serves it:

**Pre-commit mode (`--quick`):**
- Maximum 2 seconds
- Syntax check only
- Single-line output: "OK" or "1 error"
- Easy override for urgent commits

**Debug mode (`--verbose`):**
- No time limit
- Full validation suite
- Detailed output with line numbers, suggestions
- Interactive "why" explanations

**Review mode (`--diff`):**
- Focus on changes, not entire file
- Comparison with baseline
- Summary suitable for sharing

**Release mode (`--strict`):**
- Zero-tolerance for warnings
- Comprehensive checks
- Machine-readable output for CI

---

## The Circumstance-First Design Principle

Traditional design asks: "What features does this capability need?"

Circumstance-first design asks: "What circumstances does this capability serve, and what does each circumstance demand?"

### The Shift in Perspective

**Feature-first thinking:**
1. List possible features
2. Prioritize by difficulty/value
3. Build the features
4. Hope users find them useful

**Circumstance-first thinking:**
1. Identify key circumstances
2. Profile each circumstance
3. Design for each circumstance
4. Validate with users in context

The difference is profound. Feature-first produces capability lists. Circumstance-first produces capability *experiences*.

### The Entry Point Problem

Every capability has entry points—the moments when users invoke it. Entry points must match circumstances.

**Bad entry point design:**
- Single command with many flags
- Requires user to know which flags for which situation
- Mental overhead at the moment of need

**Good entry point design:**
- Multiple commands/modes named for circumstances
- Sensible defaults for each circumstance
- Progressive disclosure when needed

Example:

```bash
# Bad: User must remember flags
$ validate --quick --no-shacl --first-error-only ontology.ttl

# Good: Circumstance is the command
$ validate pre-commit ontology.ttl    # Quick, summary only
$ validate debug ontology.ttl         # Thorough, interactive
$ validate release ontology.ttl       # Strict, complete
```

---

## Case Study: The One-Size-Fits-None Validator

A team built a comprehensive RDF validator. It was thorough—50 different checks. It was detailed—verbose error messages. It was correct—caught everything.

It was also slow (8 seconds) and overwhelming (output averaged 47 lines).

Users fell into two camps:

**Camp A (Pre-commit users):** "Too slow, too noisy. I disabled it."

**Camp B (Debug users):** "Great detail! But I wish I could explore interactively."

Neither camp was happy because the tool was designed for no circumstance in particular. It was designed for the abstract job "validate RDF."

**The fix:**

The team profiled their users' circumstances:

1. **Pre-commit** (60% of invocations): Needed < 2 seconds, pass/fail only
2. **Debug** (25% of invocations): Needed detail, exploration, no time limit
3. **CI pipeline** (15% of invocations): Needed machine-readable output, full checks

They restructured:

```bash
# Pre-commit (default for git hooks)
$ validate --quick ontology.ttl
✓ OK (0.3s)

# Debug (explicit invocation)
$ validate --full ontology.ttl
[Details follow...]
$ validate --why 3    # Interactive: "Why is error 3 an error?"

# CI (detected automatically, or --ci flag)
$ validate --ci ontology.ttl
{"status": "fail", "errors": [...], "warnings": [...]}
```

Usage increased across all camps. The capability now served circumstances, not abstractions.

---

## Case Study: The Debugging Journey

Consider a more detailed example of circumstance-aware design:

A developer discovers a failing test. They enter the "debugging" circumstance. But this circumstance has sub-phases:

**Phase 1: Orientation (seconds)**
- "What broke?"
- Needs: Quick summary of failure, location, immediate context
- Design: Show failing test name, assertion message, stack trace summary

**Phase 2: Investigation (minutes)**
- "Why did it break?"
- Needs: Detailed information, ability to explore, hypothesis testing
- Design: Verbose output, interactive mode, ability to re-run subset

**Phase 3: Isolation (minutes to hours)**
- "What exactly causes it?"
- Needs: Reproducibility, minimization, bisection
- Design: Record/replay, test case generators, git bisect integration

**Phase 4: Resolution (minutes)**
- "How do I fix it?"
- Needs: Suggestions, documentation links, similar past fixes
- Design: Fix suggestions, "did you mean?", related commit search

**Phase 5: Verification (seconds)**
- "Did my fix work?"
- Needs: Fast feedback, confidence that all issues resolved
- Design: Quick re-run, delta display, all-clear signal

A truly circumstance-aware debugging tool provides different interfaces for each phase, understanding that "debugging" is not one circumstance but a journey through several.

---

## Representing Circumstances in RDF

Circumstances can be formally captured in specifications:

```turtle
@prefix jtbd: <http://example.org/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Circumstance definition
jtbd:PreCommitCircumstance a jtbd:Circumstance ;
    rdfs:label "Pre-commit validation"@en ;
    rdfs:comment "Developer finishes changes, initiates commit"@en ;

    # Trigger
    jtbd:trigger "Developer types git commit or pushes save"@en ;
    jtbd:triggerType jtbd:InternalEvent ;

    # Emotional state
    jtbd:emotionalState "Eager to finish, slightly anxious"@en ;
    jtbd:emotionalPrimary "Eagerness"@en ;
    jtbd:emotionalSecondary "Anxiety"@en ;
    jtbd:energyLevel "Medium"@en ;

    # Time budget
    jtbd:timeBudget "PT2S"^^xsd:duration ;
    jtbd:timeBudgetIdeal "PT1S"^^xsd:duration ;
    jtbd:timeBudgetUnacceptable "PT10S"^^xsd:duration ;

    # Attention context
    jtbd:attentionMode "Transitioning from deep to shallow work"@en ;
    jtbd:interruptionTolerance "Low"@en ;

    # Consequences
    jtbd:consequenceImmediate "None"@en ;
    jtbd:consequenceDelayed "Possible CI failure"@en ;
    jtbd:consequenceSocial "Embarrassment if errors found by others"@en ;

    # Design implications
    jtbd:impliesRequirement [
        a jtbd:DesignRequirement ;
        rdfs:label "Speed paramount"@en ;
        jtbd:priority "critical" ;
        jtbd:specification "Complete in under 2 seconds"@en
    ] ;
    jtbd:impliesRequirement [
        a jtbd:DesignRequirement ;
        rdfs:label "Clear pass/fail"@en ;
        jtbd:priority "high" ;
        jtbd:specification "Single-line output with unambiguous result"@en
    ] ;

    # Relationship to job
    jtbd:concernsJob jtbd:ValidateOntologyJob .

jtbd:DebugSessionCircumstance a jtbd:Circumstance ;
    rdfs:label "Debugging session"@en ;
    rdfs:comment "Investigating a failure or unexpected behavior"@en ;

    jtbd:trigger "Test failure, customer bug report, or unexpected behavior"@en ;
    jtbd:triggerType jtbd:ExternalEvent ;

    jtbd:emotionalState "Frustrated but determined"@en ;
    jtbd:emotionalPrimary "Frustration"@en ;
    jtbd:emotionalSecondary "Determination"@en ;
    jtbd:energyLevel "Variable"@en ;

    jtbd:timeBudget "PT30M"^^xsd:duration ;
    jtbd:timeBudgetIdeal "PT5M"^^xsd:duration ;
    jtbd:timeBudgetUnacceptable "N/A"@en ;

    jtbd:attentionMode "Deep work, problem-solving"@en ;
    jtbd:interruptionTolerance "Medium"@en ;

    jtbd:consequenceImmediate "Bug persists"@en ;
    jtbd:consequenceDelayed "Customer escalation"@en ;
    jtbd:consequenceSocial "Pressure, possible blame"@en ;

    jtbd:impliesRequirement [
        a jtbd:DesignRequirement ;
        rdfs:label "Depth over speed"@en ;
        jtbd:priority "critical" ;
        jtbd:specification "Comprehensive diagnostics, even if slow"@en
    ] ;
    jtbd:impliesRequirement [
        a jtbd:DesignRequirement ;
        rdfs:label "Interactive exploration"@en ;
        jtbd:priority "high" ;
        jtbd:specification "Allow user to drill down and explore"@en
    ] ;

    jtbd:concernsJob jtbd:ValidateOntologyJob .
```

### Querying Circumstances

With circumstances in RDF, you can query them:

```sparql
# Find all circumstances for a job
SELECT ?circumstance ?label ?timeBudget ?trigger
WHERE {
    ?circumstance a jtbd:Circumstance ;
                  jtbd:concernsJob jtbd:ValidateOntologyJob ;
                  rdfs:label ?label ;
                  jtbd:timeBudget ?timeBudget ;
                  jtbd:trigger ?trigger .
}

# Find design requirements by priority
SELECT ?circumstance ?requirement ?spec
WHERE {
    ?circumstance a jtbd:Circumstance ;
                  jtbd:impliesRequirement ?req .
    ?req rdfs:label ?requirement ;
         jtbd:priority "critical" ;
         jtbd:specification ?spec .
}

# Find circumstances with sub-second time budgets (speed-critical)
SELECT ?circumstance ?label
WHERE {
    ?circumstance a jtbd:Circumstance ;
                  rdfs:label ?label ;
                  jtbd:timeBudget ?budget .
    FILTER (xsd:duration(?budget) <= "PT2S"^^xsd:duration)
}
```

---

## The Circumstance Journey Map

For complex jobs, circumstances often connect in journeys. A user doesn't experience isolated circumstances—they move through sequences.

### Example: The Development Cycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CIRCUMSTANCE JOURNEY MAP                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐             │
│  │ Writing │──▶│ Testing │──▶│ Commit  │──▶│   CI    │             │
│  │  Code   │   │ Locally │   │  Check  │   │ Pipeline│             │
│  └────┬────┘   └────┬────┘   └────┬────┘   └────┬────┘             │
│       │             │             │             │                   │
│       ▼             ▼             ▼             ▼                   │
│  ┌─────────────────────────────────────────────────────┐           │
│  │ If error at any stage:                              │           │
│  │  ┌─────────┐   ┌─────────┐   ┌─────────┐            │           │
│  │  │ Diagnose│──▶│  Fix    │──▶│ Verify  │──▶ (back to │           │
│  │  │  Error  │   │  Issue  │   │   Fix   │   Testing) │           │
│  │  └─────────┘   └─────────┘   └─────────┘            │           │
│  └─────────────────────────────────────────────────────┘           │
│                                                                     │
│  ┌─────────┐   ┌─────────┐                                         │
│  │ Review  │──▶│ Merge   │──▶ (new cycle)                          │
│  │   PR    │   │         │                                         │
│  └─────────┘   └─────────┘                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

Each box is a circumstance. The arrows show transitions. A capability that understands this journey can:

- Provide smooth transitions between modes
- Preserve context across circumstances
- Anticipate what's needed next
- Guide the user along the happy path

---

## Checklist: Have You Understood the Circumstances?

Before proceeding to design, verify:

### Circumstance Identification
- [ ] I have listed all key circumstances when this job arises
- [ ] I have prioritized by frequency and importance
- [ ] I have not assumed "one circumstance fits all"

### Circumstance Profiling
- [ ] I have documented trigger, emotional state, time budget for each
- [ ] I have documented attention context and consequences
- [ ] I have articulated design implications

### Cross-Circumstance Comparison
- [ ] I have compared requirements across circumstances
- [ ] I have identified where requirements conflict
- [ ] I have designed modes/interfaces for each circumstance

### Journey Mapping
- [ ] I understand how circumstances connect in user journeys
- [ ] I have designed for transitions between circumstances
- [ ] I have considered what context carries across

If any of these remain unclear, invest more time in understanding before building.

---

## Resulting Context

After applying this pattern, you have:

- Concrete scenarios when the job arises
- Understanding of emotional state and time pressure
- Insight into what matters most in each circumstance
- Guidance for capability design trade-offs
- A journey map showing how circumstances connect

This informs:
- **[5. Outcome Desired](./outcome-desired.md)** — Outcomes are circumstance-dependent
- **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria must address specific circumstances
- **[7. Anxieties and Habits](./anxieties-and-habits.md)** — Different circumstances trigger different anxieties

---

## Related Patterns

### Builds on:

**[2. Customer Job](./customer-job.md)** — Circumstances instantiate jobs. The job is the "what"; the circumstance is the "when."

**[3. Forces in Tension](./forces-in-tension.md)** — Circumstances shift force balance. What matters in one circumstance differs from another.

### Leads to:

**[5. Outcome Desired](./outcome-desired.md)** — Outcomes are circumstance-specific. Success in one circumstance may differ from another.

### Shapes:

**[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria must be circumstance-aware. Tests should cover multiple circumstances.

---

## Philosophical Foundations

> *"A job without a circumstance is a fantasy. A circumstance without a job is just a moment. Together, they create the opportunity for progress."*

The circumstance is where the abstract becomes concrete. It's where human reality intersects with capability possibility. It's where design meets the mess of actual life.

When you design for circumstances, you're not just designing for users—you're designing for users at specific moments in their lives, with specific pressures, specific emotions, specific needs.

This is the difference between software that works and software that feels right. Software that works is correct. Software that feels right is circumstance-aware.

> *"The quality of a thing is related to how well it answers the question: For whom was it made, and for what occasion?"*
>
> — (Adapted from Christopher Alexander)

A capability that answers this question well will thrive. A capability that ignores circumstances will struggle to find adoption, no matter how technically correct it is.

---

## Exercise: Profile Your Circumstances

Before designing your next capability, complete this exercise:

1. **List circumstances**: When does this job arise? List at least 3-5 circumstances.

2. **Profile each**: For each circumstance, document:
   - Trigger
   - Emotional state
   - Time budget
   - Attention context
   - Consequences

3. **Compare across**: Create a comparison matrix showing how requirements differ.

4. **Design modes**: For each circumstance, sketch the interface/behavior that would serve it.

5. **Map the journey**: How do circumstances connect? What transitions occur?

Only after completing this exercise should you proceed to define **[Outcomes Desired](./outcome-desired.md)**.

---

## Further Reading

- Cooper, Alan. *About Face: The Essentials of Interaction Design* (2014) — Designing for user context and scenarios.
- Christensen, Clayton. *Competing Against Luck* (2016) — The role of circumstance in Jobs to Be Done.
- Kalbach, Jim. *Mapping Experiences* (2016) — Journey mapping techniques.
- Kim, W. Chan & Mauborgne, Renée. *Blue Ocean Strategy* (2015) — Understanding moments of decision.

---

A job without a circumstance is too abstract to design for. A capability without circumstance awareness is too generic to excel. Design for the moment, and you design for reality.
