# 6. Progress Maker

★★

*Customers don't want features. They want progress. A progress maker is anything that helps move from struggle to satisfaction on a job to be done.*

---

You've defined the **[Customer Job](./customer-job.md)**, identified the **[Circumstance of Struggle](./circumstance-of-struggle.md)**, and specified the **[Outcome Desired](./outcome-desired.md)**. Now ask: what actually helps customers make progress?

A progress maker is any solution—complete or partial, manual or automated, simple or complex—that moves customers toward their desired outcome. Progress makers exist before you build anything. Your capability, if you build it well, becomes one more progress maker in the customer's toolkit.

Understanding existing progress makers is essential. You're not building in a vacuum; you're entering a world where people have already found ways to cope.

**The problem: Building capabilities without understanding existing progress makers leads to solutions that ignore what already works, compete poorly, or duplicate effort.**

---

**The forces at play:**

- *Something is always better than nothing.* Even a terrible workaround represents progress over pure struggle.

- *Familiarity breeds tolerance.* People accept friction in tools they know. Your "better" solution must overcome inertia.

- *Partial solutions accumulate.* Customers often combine multiple partial progress makers. Your capability enters this ecosystem.

- *Different progress makers serve different circumstances.* The quick workaround serves one circumstance; the thorough tool serves another.

The implication: your capability must acknowledge, complement, or decisively surpass existing progress makers.

---

**Therefore:**

Before designing your capability, catalog the progress makers customers currently use. For each one, understand:

**1. What is it?**
- A tool, script, service, process, habit, or workaround
- Formal or informal
- Individual or shared

**2. What progress does it enable?**
- Which outcomes does it address?
- How well does it address them?
- What circumstances does it serve?

**3. What are its limitations?**
- Which outcomes does it fail to address?
- What friction does it introduce?
- When does it break down?

**4. Why do people use it?**
- Familiarity, convenience, mandate?
- Is it the best option or just the known option?

Create a progress maker landscape:

| Progress Maker | Outcomes Addressed | Limitations | Circumstance Fit |
|---------------|-------------------|-------------|------------------|
| Manual inspection | Error detection | Slow, incomplete | Low-risk changes |
| CI validation | Automated checking | Slow feedback | Pre-merge |
| IDE plugins | Real-time feedback | Limited scope | During editing |
| Peer review | Error detection + knowledge sharing | Time-consuming | All commits |

From this landscape, identify your capability's position:

- **Gap filler:** Address outcomes no current progress maker serves well
- **Consolidator:** Replace multiple partial solutions with one complete one
- **Complementer:** Work alongside existing progress makers
- **Disruptor:** Decisively surpass all existing options

---

**Resulting context:**

After applying this pattern, you have:

- A map of existing progress makers
- Understanding of what's working and what's not
- Clear positioning for your capability
- Realistic expectations for adoption

This understanding shapes **[Competing Solutions](./competing-solutions.md)** (what you're up against) and informs **[Acceptance Criterion](../specification/acceptance-criterion.md)** (you must outperform the status quo).

---

**Related patterns:**

- *Builds on:* **[5. Outcome Desired](./outcome-desired.md)** — Progress makers address outcomes
- *Informs:* **[8. Competing Solutions](./competing-solutions.md)** — Progress makers are competing solutions
- *Shapes:* **[17. Domain-Specific Language](../specification/domain-specific-language.md)** — DSL must fit existing progress makers
- *Affects:* **[7. Anxieties and Habits](./anxieties-and-habits.md)** — Progress makers shape habits

---

> *"People hire products and services to get jobs done. If you can understand the job, you can get it done better than anyone else."*
>
> — Clayton Christensen

But first, understand how they're currently getting it done. Even imperfectly.

---

**The Non-Consumption Alternative:**

Sometimes the most important progress maker is "nothing." People tolerate the struggle rather than seeking any solution. This is *non-consumption*—and it represents both an opportunity and a warning.

Opportunity: If people aren't using any progress maker, your capability faces no direct competition.

Warning: If people aren't seeking progress, your capability may solve a problem they don't care enough about.

When you encounter non-consumption, investigate:
- Is the struggle genuinely tolerable?
- Are barriers to adopting solutions too high?
- Is the job not important enough to invest in?

---

**Example: Progress Makers for RDF Validation**

| Progress Maker | Type | Outcomes | Limitations |
|---------------|------|----------|-------------|
| Manual inspection | Habit | Error detection | Slow, unreliable |
| `rapper` CLI tool | External tool | Syntax validation | Cryptic errors |
| VS Code extension | IDE plugin | Real-time feedback | Limited to VS Code |
| CI SHACL check | Pipeline | Schema validation | Slow feedback loop |
| Peer review | Process | Error + knowledge | Human time expensive |
| Non-consumption | Nothing | None | Errors escape |

A new `specify check` capability must position itself:
- Faster than CI pipeline
- More comprehensive than IDE plugins
- Clearer than `rapper`
- Less expensive than peer review

Or it must serve a circumstance none of these serve well.

---

**Representing Progress Makers in RDF:**

```turtle
jtbd:ManualInspection a jtbd:ProgressMaker ;
    rdfs:label "Manual inspection" ;
    jtbd:addressesOutcome jtbd:ErrorDetection ;
    jtbd:limitation "Slow, incomplete, unreliable"@en ;
    jtbd:circumstanceFit jtbd:LowRiskChanges ;
    jtbd:adoptionReason "Always available, no setup"@en .

jtbd:RapperTool a jtbd:ProgressMaker ;
    rdfs:label "rapper CLI tool" ;
    jtbd:addressesOutcome jtbd:SyntaxValidation ;
    jtbd:limitation "Cryptic error messages"@en ;
    jtbd:circumstanceFit jtbd:CLIUsers ;
    jtbd:adoptionReason "Standard tool in RDF ecosystem"@en .
```

This formal representation enables queries like:
- "What outcomes are poorly served by current progress makers?"
- "What progress makers compete with our proposed capability?"
- "What circumstances have no good progress maker?"
