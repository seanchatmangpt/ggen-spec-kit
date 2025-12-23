# 4. Circumstance of Struggle

★★

*A job alone doesn't tell you when to act. The circumstance—the specific moment when struggle becomes acute—reveals when capability matters most.*

---

You understand the **[Customer Job](./customer-job.md)**. You've mapped the **[Forces in Tension](./forces-in-tension.md)**. But when does this job actually arise? When do people feel the need acutely enough to seek a solution?

This is the circumstance of struggle.

A job might exist abstractly for years. "I should validate my code" is a perpetual background thought. But the *circumstance* creates urgency:

- "I just made a significant change and I'm about to push to main"
- "A customer reported a bug and I need to find the cause"
- "I'm reviewing a colleague's pull request"
- "It's 5 PM on Friday and I want to go home confident"

Each circumstance carries different emotional weight, different time pressure, different willingness to invest effort. The capability that serves "5 PM Friday" differs from the one that serves "deep debugging session."

**The problem: Capabilities designed for abstract jobs rather than concrete circumstances miss the moment when they're needed most.**

---

**The forces at play:**

- *Jobs are continuous; circumstances are discrete.* The job exists always. The circumstance punctuates time with moments of need.

- *Urgency varies dramatically.* The same job under different circumstances may be critical or ignorable.

- *Context shapes tolerance.* In a crisis, people accept friction. In routine, friction drives them away.

- *Multiple circumstances, one job.* The same job arises in many circumstances. Each might need different support.

These forces mean that a capability must understand not just the job but the *when* and *why now* of the job.

---

**Therefore:**

For each job, identify the key circumstances when it arises. Ask:

**1. What triggers the need?**
- External events (customer report, deadline, meeting)
- Internal events (finishing a task, making a decision, feeling uncertain)
- Periodic events (daily standup, weekly review, release cycle)

**2. What's the emotional state?**
- Confident or anxious?
- Rushed or reflective?
- Focused or distracted?

**3. What resources are available?**
- How much time can they invest?
- What tools are at hand?
- Who can help?

**4. What happens if the job isn't done?**
- Immediate consequences?
- Delayed consequences?
- Social consequences?

Document circumstances as scenarios:

```
Circumstance: Pre-commit validation

Trigger: Developer finishes a set of changes, types `git commit`
Emotional state: Eager to close the task, slight anxiety about correctness
Time budget: Seconds to minutes (not more)
Consequences of skipping: Possible CI failure, embarrassment, delay

Implication for capability: Must be FAST. Must give clear pass/fail.
Must not block workflow. Detailed feedback can wait.
```

```
Circumstance: Debugging session

Trigger: Test failure or customer bug report
Emotional state: Frustrated, determined, investigative
Time budget: Minutes to hours
Consequences of skipping: Bug persists, customer unhappy

Implication for capability: Depth matters more than speed.
Detailed diagnostics. Interactive exploration.
```

These circumstance profiles reveal that the same job may need multiple capability "modes" or even separate capabilities.

---

**Resulting context:**

After applying this pattern, you have:

- Concrete scenarios when the job arises
- Understanding of emotional state and time pressure
- Insight into what matters most in each circumstance
- Guidance for capability design trade-offs

This informs **[Outcome Desired](./outcome-desired.md)** (outcomes are circumstance-dependent) and shapes **[Acceptance Criterion](../specification/acceptance-criterion.md)** (criteria must address specific circumstances).

---

**Related patterns:**

- *Builds on:* **[2. Customer Job](./customer-job.md)** — Circumstances instantiate jobs
- *Builds on:* **[3. Forces in Tension](./forces-in-tension.md)** — Circumstances shift force balance
- *Leads to:* **[5. Outcome Desired](./outcome-desired.md)** — Outcomes are circumstance-specific
- *Shapes:* **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria must be circumstance-aware

---

> *"A job without a circumstance is a fantasy. A circumstance without a job is just a moment. Together, they create the opportunity for progress."*

---

**Example: The CLI Validation Capability**

Consider the `specify check` command. The job is "validate RDF correctness." But examine the circumstances:

| Circumstance | Time Budget | Key Need | Capability Mode |
|-------------|-------------|----------|-----------------|
| Pre-commit hook | < 2 sec | Pass/fail | `--quick` flag |
| Manual check | < 30 sec | Summary + top errors | Default mode |
| Debug session | Minutes | Full diagnostics | `--verbose` flag |
| CI pipeline | < 5 min | Machine-readable output | `--json` flag |

Each circumstance demands different behavior from the same underlying capability. Understanding circumstances prevents the mistake of building one mode that serves no circumstance well.

---

**Representing Circumstances in RDF:**

```turtle
jtbd:PreCommitCircumstance a jtbd:Circumstance ;
    rdfs:label "Pre-commit validation" ;
    jtbd:trigger "Developer finishes changes, initiates commit"@en ;
    jtbd:emotionalState "Eager, slightly anxious"@en ;
    jtbd:timeBudget "PT2S"^^xsd:duration ;
    jtbd:concernsJob jtbd:ValidateOntologyJob ;
    jtbd:impliesRequirement "Fast feedback, clear pass/fail"@en .

jtbd:DebugSessionCircumstance a jtbd:Circumstance ;
    rdfs:label "Debugging session" ;
    jtbd:trigger "Test failure or customer bug report"@en ;
    jtbd:emotionalState "Frustrated, investigative"@en ;
    jtbd:timeBudget "PT30M"^^xsd:duration ;
    jtbd:concernsJob jtbd:ValidateOntologyJob ;
    jtbd:impliesRequirement "Detailed diagnostics, exploration"@en .
```

Circumstances become queryable design constraints, traceable from capability features back to the human moments they serve.
