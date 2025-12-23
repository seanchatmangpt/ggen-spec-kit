# 39. Feedback Loop

★★

*Build, measure, learn. The feedback loop closes the circuit between what you build and what customers experience, enabling continuous improvement based on real-world data.*

---

You've built a capability. You've verified it works. But does it serve its purpose? Does it help customers make progress on their jobs? Does it deliver the outcomes you intended?

Without feedback, these questions remain unanswered. You're flying blind, hoping your assumptions were correct.

The feedback loop changes this. It connects production reality back to specification evolution:

```
Specification → Transformation → Artifact → Usage → Feedback → Specification
```

Production metrics, user behavior, error rates, performance data—all feed back into specification refinement. The capability learns from its own use.

**The problem: Without feedback, capabilities stagnate. Assumptions remain unchallenged. Opportunities for improvement go unnoticed.**

---

**The forces at play:**

- *Building wants forward motion.* Shipping features feels productive.

- *Learning wants reflection.* Understanding usage takes time.

- *Data wants analysis.* Raw metrics aren't insights.

- *Action wants clarity.* What should we do differently?

The tension: keep building while creating space for learning.

---

**Therefore:**

Establish explicit feedback loops that connect operational data back to specification evolution.

**Feedback loop structure:**

```
┌─────────────────────────────────────────────────────────────┐
│                      FEEDBACK LOOP                          │
│                                                             │
│  1. OBSERVE                                                 │
│     Collect data from:                                      │
│     • Telemetry (traces, metrics, logs)                     │
│     • User feedback (surveys, support tickets)              │
│     • Usage analytics (feature adoption, flows)             │
│     • Error reports (crashes, failures)                     │
│                                                             │
│  2. ANALYZE                                                 │
│     Extract insights:                                       │
│     • Performance bottlenecks                               │
│     • Error patterns                                        │
│     • Usage patterns                                        │
│     • Outcome achievement                                   │
│                                                             │
│  3. HYPOTHESIZE                                             │
│     Form hypotheses:                                        │
│     • "Users struggle with X because..."                    │
│     • "Outcome Y isn't achieved because..."                 │
│     • "Performance degrades when..."                        │
│                                                             │
│  4. SPECIFY                                                 │
│     Update specifications:                                  │
│     • New acceptance criteria                               │
│     • Refined outcomes                                      │
│     • Additional constraints                                │
│                                                             │
│  5. TRANSFORM                                               │
│     Regenerate artifacts with μ                             │
│                                                             │
│  6. VERIFY                                                  │
│     Ensure changes work                                     │
│                                                             │
│  7. DEPLOY                                                  │
│     Release and return to OBSERVE                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Feedback sources:**

| Source | Data Type | Feeds Into |
|--------|-----------|------------|
| OpenTelemetry | Performance metrics | Performance requirements |
| Error tracking | Failure patterns | Robustness criteria |
| User surveys | Satisfaction scores | Outcome refinement |
| Support tickets | Pain points | New requirements |
| Usage analytics | Feature adoption | Priority decisions |
| A/B tests | Comparative effectiveness | Design choices |

**Feedback in RDF:**

```turtle
# Record feedback as linked data
feedback:FB-2025-01-15-001 a sk:Feedback ;
    sk:source "telemetry" ;
    sk:timestamp "2025-01-15T10:30:00Z"^^xsd:dateTime ;
    sk:concernsCapability cli:ValidateCommand ;
    sk:observation "P95 latency exceeds 500ms for files > 1MB" ;
    sk:impact "Users report slow validation frustrating" ;
    sk:proposedAction "Add streaming validation for large files" ;
    sk:linkedOutcome jtbd:MinimizeValidationTime .
```

**Feedback cadence:**

| Cadence | Focus |
|---------|-------|
| Daily | Error rates, critical metrics |
| Weekly | Performance trends, usage patterns |
| Monthly | Outcome achievement, satisfaction |
| Quarterly | Strategic alignment, roadmap impact |

---

**Resulting context:**

After applying this pattern, you have:

- Connection between production and specification
- Data-driven improvement process
- Structured approach to learning
- Living capabilities that evolve

This enables **[40. Outcome Measurement](./outcome-measurement.md)** and drives **[42. Specification Refinement](./specification-refinement.md)**.

---

**Related patterns:**

- *Collects data from:* **[38. Observable Execution](../verification/observable-execution.md)** — Telemetry
- *Enables:* **[40. Outcome Measurement](./outcome-measurement.md)** — Measure outcomes
- *Drives:* **[42. Specification Refinement](./specification-refinement.md)** — Improve specs
- *Guided by:* **[41. Gap Analysis](./gap-analysis.md)** — Find gaps

---

> *"If you're not measuring it, you're just practicing."*

The feedback loop transforms practice into progress. It closes the circuit between building and learning.
