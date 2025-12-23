# 3. Forces in Tension

★★

*Every interesting problem involves forces that pull in different directions. Understanding these forces—not avoiding them—is the key to solutions that feel alive.*

---

You've identified a **[Customer Job](./customer-job.md)**. You're eager to design a solution. But wait—the job exists precisely because there are forces in tension. If there were no tension, the job would already be done.

Consider the job: "Validate my RDF ontology before committing."

Why isn't this trivially solved? Because forces pull in different directions:

- The person wants *speed* (finish the task quickly)
- But also wants *thoroughness* (catch every error)
- They want *detailed feedback* (understand what's wrong)
- But also want *simplicity* (don't overwhelm with information)
- They want *automation* (not think about validation)
- But also want *control* (override when they know better)

These forces don't resolve to a single optimal solution. They create tension. Different people in different circumstances will want different balances.

**The problem: Solutions that ignore forces in tension become rigid. They serve one pole perfectly while frustrating everyone who needs a different balance.**

---

**The forces at play (meta-level):**

- *Simplicity obscures complexity.* It's tempting to say "just be fast" or "just be thorough." But real needs involve trade-offs.

- *Analysis can paralyze.* You could enumerate forces forever. At some point, you must act.

- *Forces are contextual.* What matters to a novice differs from what matters to an expert. What matters in development differs from production.

- *Forces evolve.* Today's critical concern becomes tomorrow's baseline assumption. Forces shift as the living system evolves.

The tension at this meta-level: understand forces deeply enough to design well, but not so exhaustively that you never build anything.

---

**Therefore:**

For the job you've identified, enumerate the key forces in tension. Look for:

**1. Speed vs. Thoroughness**
- How quickly must the job complete?
- How comprehensive must the result be?

**2. Simplicity vs. Power**
- How easy should it be for beginners?
- How much control should experts have?

**3. Automation vs. Control**
- What should happen automatically?
- What should require explicit human decision?

**4. Safety vs. Freedom**
- What constraints protect against mistakes?
- What constraints become annoying limitations?

**5. Consistency vs. Flexibility**
- What should always work the same way?
- What should adapt to context?

For each force pair, document:
- What the tension is
- Why both poles have value
- Who cares more about which pole
- When the balance shifts

Example analysis for RDF validation:

| Force | Tension | Contextual Balance |
|-------|---------|-------------------|
| Speed vs. Thoroughness | Quick feedback vs. deep checking | Development favors speed; CI favors thoroughness |
| Simplicity vs. Power | "Is it valid?" vs. detailed diagnostics | Beginners need simple; experts need detail |
| Automation vs. Control | Auto-validate on save vs. manual trigger | Depends on file size and user preference |

This analysis doesn't resolve the tensions—it illuminates them. The resolution comes through design choices that honor multiple forces simultaneously.

---

**Resulting context:**

After applying this pattern, you have:

- A map of the key forces affecting this job
- Understanding of why no single solution serves everyone perfectly
- Insight into how balance points shift by context
- Raw material for design decisions

This understanding shapes **[Outcome Desired](./outcome-desired.md)** (outcomes must honor forces) and informs **[Acceptance Criterion](../specification/acceptance-criterion.md)** (criteria must acknowledge trade-offs).

---

**Related patterns:**

- *Builds on:* **[2. Customer Job](./customer-job.md)** — Forces arise from jobs
- *Informs:* **[5. Outcome Desired](./outcome-desired.md)** — Outcomes balance forces
- *Informs:* **[6. Progress Maker](./progress-maker.md)** — Progress means resolving tensions
- *Shapes:* **[11. Executable Specification](../specification/executable-specification.md)** — Specs must accommodate forces

---

> *"In complex systems, there are no solutions—only trade-offs."*
>
> — Thomas Sowell

The art of capability creation lies not in eliminating trade-offs but in finding resolutions that honor multiple forces. A truly alive capability doesn't ignore forces—it dances with them.

---

**Representing Forces in RDF:**

Forces can be formally captured:

```turtle
jtbd:SpeedVsThoroughness a jtbd:ForceTension ;
    rdfs:label "Speed vs Thoroughness" ;
    jtbd:force1 jtbd:Speed ;
    jtbd:force2 jtbd:Thoroughness ;
    jtbd:affectsJob jtbd:ValidateOntologyJob ;
    jtbd:balanceDescription "Development favors speed; CI favors thoroughness"@en .

jtbd:Speed a jtbd:Force ;
    rdfs:label "Speed" ;
    jtbd:valueProposition "Complete tasks quickly, maintain flow state"@en .

jtbd:Thoroughness a jtbd:Force ;
    rdfs:label "Thoroughness" ;
    jtbd:valueProposition "Catch all errors, ensure correctness"@en .
```

This formal representation enables queries like "What forces affect this job?" and "Which features address the speed pole?" The forces become part of the traceable specification.
