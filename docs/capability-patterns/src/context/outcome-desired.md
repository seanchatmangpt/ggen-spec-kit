# 5. Outcome Desired

★★

*Progress isn't abstract. It's measurable. The outcomes people desire—specific, concrete improvements in their situation—define what success looks like for a capability.*

---

You know the **[Customer Job](./customer-job.md)**. You've identified the **[Circumstance of Struggle](./circumstance-of-struggle.md)**. Now ask: what does progress actually look like? How will the customer know they've made progress?

This is the outcome desired.

Outcomes are not features. Features are what we build. Outcomes are what customers experience. Consider:

- Feature: "Validation command checks RDF syntax"
- Outcome: "Reduce time to discover syntax errors from 5 minutes to 5 seconds"

The feature describes the mechanism. The outcome describes the *change in the customer's world*.

**The problem: Building features without defined outcomes leads to capabilities that are technically complete but experientially hollow.**

---

**The forces at play:**

- *Features are controllable; outcomes depend on context.* You can guarantee a feature works. You cannot guarantee the outcome unless the context cooperates.

- *Outcomes require baselines.* You can't measure improvement without knowing the starting point.

- *Some outcomes are hard to measure.* "Feel more confident" is real but elusive. "Reduce errors by 50%" is precise but may miss what matters.

- *Outcomes compound.* Primary outcomes enable secondary outcomes. Faster validation enables more frequent validation, which enables catching errors earlier, which enables higher quality.

The tension: outcomes are what matter, but they're harder to define and measure than features.

---

**Therefore:**

For each job and circumstance, define the specific outcomes that represent progress. Use the Outcome-Driven Innovation framework:

**1. Direction** — Is the customer trying to minimize or maximize something?
- Minimize: time, errors, effort, friction, risk
- Maximize: speed, confidence, coverage, clarity

**2. Metric** — What specific measure captures this?
- Time: seconds, minutes, hours
- Count: errors found, steps required, clicks needed
- Rate: success rate, completion rate

**3. Object** — What exactly is being measured?
- Time to [do what]?
- Number of [what]?
- Rate of [what happening]?

Combine into outcome statements:

```
Minimize the [metric] of [object]

Maximize the [metric] of [object]
```

Example outcomes for RDF validation:

| Outcome Statement | Baseline | Target |
|-------------------|----------|--------|
| Minimize the time to discover syntax errors | 5 min (manual) | 5 sec |
| Minimize the number of undetected errors | ~3 per file | 0 |
| Maximize the clarity of error messages | Low (cryptic) | High (actionable) |
| Minimize the effort to fix identified errors | ~2 min/error | ~30 sec/error |

**4. Importance vs. Satisfaction**

For each outcome, assess:
- **Importance:** How much does this outcome matter to the customer?
- **Satisfaction:** How well does the current solution address it?

The gap between importance and satisfaction reveals opportunity:

- High importance + Low satisfaction = **Critical opportunity**
- High importance + High satisfaction = **Maintain quality**
- Low importance + Any satisfaction = **Deprioritize**

This analysis guides where to invest effort.

---

**Resulting context:**

After applying this pattern, you have:

- Specific, measurable outcome statements
- Baselines and targets for each outcome
- Understanding of importance and satisfaction gaps
- Criteria for evaluating whether a capability succeeds

These outcomes feed directly into **[Acceptance Criterion](../specification/acceptance-criterion.md)** and provide the basis for **[Outcome Measurement](../evolution/outcome-measurement.md)**.

---

**Related patterns:**

- *Builds on:* **[2. Customer Job](./customer-job.md)** — Outcomes express progress on jobs
- *Builds on:* **[4. Circumstance of Struggle](./circumstance-of-struggle.md)** — Circumstances contextualize outcomes
- *Enables:* **[6. Progress Maker](./progress-maker.md)** — What makes progress possible
- *Shapes:* **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria derive from outcomes
- *Measured by:* **[40. Outcome Measurement](../evolution/outcome-measurement.md)** — Track outcome delivery

---

> *"If you can't measure it, you can't improve it."*
>
> — Peter Drucker

But also: if you measure the wrong thing, you'll improve the wrong thing. Outcomes keep measurement focused on what customers actually experience.

---

**Representing Outcomes in RDF:**

```turtle
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    rdfs:label "Minimize validation time" ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:object "discovering syntax errors" ;
    jtbd:baseline "PT5M"^^xsd:duration ;
    jtbd:target "PT5S"^^xsd:duration ;
    jtbd:importance "high" ;
    jtbd:currentSatisfaction "low" ;
    jtbd:concernsJob jtbd:ValidateOntologyJob .

jtbd:MaximizeErrorClarity a jtbd:Outcome ;
    rdfs:label "Maximize error message clarity" ;
    jtbd:direction "maximize" ;
    jtbd:metric "clarity" ;
    jtbd:object "error messages" ;
    jtbd:importance "high" ;
    jtbd:currentSatisfaction "medium" ;
    jtbd:concernsJob jtbd:ValidateOntologyJob .
```

With outcomes in RDF:
- SPARQL queries can find high-importance, low-satisfaction gaps
- Features can declare which outcomes they address
- Documentation can auto-generate outcome tracking sections
- Telemetry can be linked to outcome measurement

---

**The Outcome Hierarchy:**

Outcomes often form hierarchies:

```
Minimize time to discover syntax errors
    └── Enables: Minimize time to fix errors
        └── Enables: Minimize time to commit clean code
            └── Enables: Maximize confidence in commits
                └── Enables: Minimize anxiety when pushing to main
```

Understanding this hierarchy helps prioritize: addressing upstream outcomes creates cascading benefits downstream.
