# 8. Competing Solutions

★★

*Your capability doesn't exist in isolation. It competes for adoption against every other way customers might get the job done—including doing nothing at all.*

---

You've mapped the **[Living System](./living-system.md)**, understood the **[Customer Job](./customer-job.md)**, and cataloged **[Progress Makers](./progress-maker.md)**. Now look at the landscape with competitive eyes.

Every progress maker is a competing solution. They compete for:
- The customer's attention
- The customer's time to learn
- The customer's willingness to change
- The customer's trust

Your capability enters this competition the moment you release it. Understanding the competitive landscape helps you design something that can actually win adoption.

**The problem: Capabilities built without considering competition often lose to existing solutions—not because they're worse, but because they're not different enough to overcome switching costs.**

---

**The forces at play:**

- *Good enough is the enemy of better.* If current solutions are "good enough," your "better" solution must be dramatically better to trigger change.

- *Integration beats isolation.* A solution that integrates with the existing ecosystem has an advantage over one that requires changing everything.

- *Trust takes time.* Established solutions have earned trust through use. New solutions must prove themselves.

- *Network effects compound.* Solutions others use become more valuable because knowledge, integrations, and support accumulate around them.

- *Switching costs are real.* Even free tools have adoption costs: learning, migration, integration, and workflow changes.

These forces mean that being "better" isn't enough. You must be better *enough* to overcome the total cost of switching.

---

**Therefore:**

Analyze the competitive landscape systematically:

**1. Direct Competitors**

Solutions explicitly designed for the same job:
- What do they do well?
- What do they do poorly?
- What is their positioning?
- What is their adoption level?

**2. Indirect Competitors**

Solutions used for the job but not designed for it:
- Workarounds and hacks
- General-purpose tools adapted to this job
- Manual processes and human labor

**3. Non-Consumption**

The choice to tolerate the problem:
- Why do some people not solve this job at all?
- What would make solving it worth their effort?

**4. Future Competitors**

Solutions that might emerge:
- What are technology trends?
- What are adjacent players who might enter this space?

For each competitor, assess:

| Competitor | Strengths | Weaknesses | Why Used |
|------------|-----------|------------|----------|
| Tool A | Fast, well-known | Poor error messages | Ecosystem default |
| Tool B | Great UX | Slow, limited scope | Easier to learn |
| Manual review | Catches nuance | Slow, inconsistent | No setup required |
| Nothing | Zero effort | Problems persist | Low perceived importance |

**5. Competitive Positioning**

Based on this analysis, choose your position:

- **Segment focus:** Serve a specific circumstance better than anyone
- **Outcome focus:** Deliver an outcome competitors neglect
- **Integration focus:** Work better with the ecosystem
- **Simplicity focus:** Radically easier to adopt and use
- **Performance focus:** Dramatically faster or more thorough

Your positioning should be defensible and meaningful to your target customers.

---

**Resulting context:**

After applying this pattern, you have:

- A clear view of the competitive landscape
- Understanding of why competitors succeed or fail
- Explicit positioning for your capability
- Realistic assessment of what's needed to win adoption

This completes the Context Patterns. You're ready to move to **[Part II: Specification Patterns](../specification/semantic-foundation.md)**, where you'll capture this understanding in executable form.

---

**Related patterns:**

- *Builds on:* **[6. Progress Maker](./progress-maker.md)** — Progress makers are competitors
- *Builds on:* **[7. Anxieties and Habits](./anxieties-and-habits.md)** — Competitors benefit from habits
- *Informs:* **[11. Executable Specification](../specification/executable-specification.md)** — Specs must address competitive position
- *Affects:* **[45. Living Documentation](../evolution/living-documentation.md)** — Docs must differentiate

---

> *"If you're not the one defining your competition, your competition will define you."*

Know what you're up against. Design accordingly.

---

**The Competitive Force Field:**

```
                    Direct Competitors
                          ▲
                          |
                          |
    Switching ◄───────────┼───────────► Future
    Costs                 |             Competitors
                          |
                          |
                          ▼
    ┌─────────────────────────────────────────┐
    │             Your Capability              │
    └─────────────────────────────────────────┘
                          |
                          |
                          ▼
    Non-Consumption ◄─────┴─────► Indirect Competitors
```

You're pulled by existing competitors and pushed by switching costs. Non-consumption and indirect competitors define the floor. Future competitors threaten your position.

---

**Example: Competitive Analysis for RDF Validation**

| Category | Competitor | Positioning |
|----------|-----------|-------------|
| Direct | `rapper` | Standard tool, cryptic UX |
| Direct | `riot` (Apache Jena) | Comprehensive, complex |
| Direct | `pyshacl` | Python-native, SHACL focus |
| Indirect | IDE linting | Real-time, limited depth |
| Indirect | CI pipeline | Thorough, slow feedback |
| Non-consumption | Manual review | Zero setup, unreliable |

**spec-kit positioning:** Fast CLI validation with clear error messages, integrated into developer workflow, serving the "pre-commit" circumstance better than any alternative.

This positioning acknowledges:
- Can't be more comprehensive than `riot` (don't try)
- Can't be more real-time than IDE (different circumstance)
- Can be faster and clearer than CI pipeline
- Can be more reliable than manual review

---

**Representing Competition in RDF:**

```turtle
jtbd:RapperTool a jtbd:CompetingSolution ;
    rdfs:label "rapper CLI tool" ;
    jtbd:category "direct" ;
    jtbd:strengths "Standard tool, widely available"@en ;
    jtbd:weaknesses "Cryptic error messages, no SHACL"@en ;
    jtbd:addressesJob jtbd:ValidateOntologyJob ;
    jtbd:positioning "Ecosystem default"@en .

jtbd:SpecKitCheck a jtbd:Capability ;
    rdfs:label "specify check" ;
    jtbd:competesAgainst jtbd:RapperTool, jtbd:CIPipeline, jtbd:ManualReview ;
    jtbd:positioning "Fast pre-commit validation with clear feedback"@en ;
    jtbd:differentiator "Speed + clarity + developer workflow integration"@en .
```

With competitive analysis in RDF:
- Feature planning can reference competitive gaps
- Documentation can emphasize differentiators
- Roadmap can track competitive evolution
- Market analysis becomes queryable

---

## Transition to Part II

You've completed the Context Patterns. You understand:
- The **[Living System](./living-system.md)** your capability will join
- The **[Customer Job](./customer-job.md)** to be done
- The **[Forces in Tension](./forces-in-tension.md)** to balance
- The **[Circumstance of Struggle](./circumstance-of-struggle.md)** that triggers need
- The **[Outcome Desired](./outcome-desired.md)** that defines success
- The **[Progress Makers](./progress-maker.md)** already in use
- The **[Anxieties and Habits](./anxieties-and-habits.md)** that resist change
- The **[Competing Solutions](./competing-solutions.md)** you face

Now it's time to capture this understanding in executable form. Turn to **[Part II: Specification Patterns](../specification/semantic-foundation.md)** to learn how.
