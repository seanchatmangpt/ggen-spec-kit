# 7. Anxieties and Habits

★★

*Progress isn't just about moving forward. It's about overcoming the forces that hold people back. Anxieties create resistance. Habits create inertia. A capability that ignores these forces will struggle to be adopted.*

---

You've mapped **[Progress Makers](./progress-maker.md)** and defined **[Outcomes Desired](./outcome-desired.md)**. You know what success looks like. But something keeps people from achieving it. Two forces conspire against progress:

**Anxieties** — The fears that make people hesitate
**Habits** — The patterns that make change uncomfortable

A capability might be technically superior to current solutions, yet fail to be adopted. The technical advantages don't overcome the human resistance. Understanding anxieties and habits reveals why good solutions go unused—and how to design ones that actually get adopted.

**The problem: Capabilities that ignore anxieties and habits face invisible resistance. They work but aren't used.**

---

**The forces at play:**

- *Loss aversion dominates.* The pain of losing something familiar outweighs the pleasure of gaining something new.

- *Habits are efficient.* Current workflows are optimized through repetition. New tools disrupt this efficiency—at least initially.

- *Anxiety seeks safety.* When uncertain, people stick with what they know, even if it's suboptimal.

- *Change requires energy.* Every new tool has a learning curve. People must perceive the investment as worthwhile.

- *Social proof matters.* People look to peers. If nobody else is using your capability, why should they?

These forces create a gravitational pull toward the status quo. Your capability must be compelling enough to overcome this gravity.

---

**Therefore:**

For the job and circumstance you're addressing, explicitly identify the anxieties and habits at play:

**Anxieties (Four Categories):**

1. **Anxiety of the new solution**
   - "Will this tool break my workflow?"
   - "Will I look foolish if I can't use it?"
   - "What if it gives wrong results?"
   - "Is my data safe?"

2. **Anxiety of switching**
   - "How much time will migration take?"
   - "What if I lose work during the transition?"
   - "Who will help me if I get stuck?"

3. **Anxiety of missing out (on the old)**
   - "What if the old tool had features I'll miss?"
   - "What if I need to go back?"

4. **Anxiety about others' perception**
   - "Will my team think I'm wasting time?"
   - "Will I be blamed if this doesn't work?"

**Habits to Break:**

- Existing muscle memory (keystrokes, commands, workflows)
- Mental models of how things work
- Integration with other tools in the ecosystem
- Rhythms and rituals (daily/weekly patterns)

**Design Responses:**

For each anxiety, design a response:

| Anxiety | Design Response |
|---------|----------------|
| "Will this break my workflow?" | Non-invasive integration, opt-in features |
| "Will I look foolish?" | Progressive disclosure, helpful errors |
| "What if results are wrong?" | Verification modes, transparency |
| "Is my data safe?" | Local processing, no data sent |
| "How long will migration take?" | Zero-config defaults, migration guides |
| "What if I need the old tool?" | Complement rather than replace |

For each habit, design a bridge:

| Habit | Bridge |
|-------|--------|
| Existing commands | Alias support, familiar syntax |
| Mental models | Consistent metaphors, gentle corrections |
| Tool integrations | Plugin architecture, standard formats |
| Workflows | Fit into existing rhythms |

---

**Resulting context:**

After applying this pattern, you have:

- A list of anxieties that create resistance
- A map of habits that create inertia
- Design responses that lower adoption barriers
- Understanding of why technically superior solutions might fail

This directly shapes **[Acceptance Criterion](../specification/acceptance-criterion.md)** (criteria must include adoption factors) and influences **[Human-Readable Artifact](../transformation/human-readable-artifact.md)** (documentation must address anxieties).

---

**Related patterns:**

- *Builds on:* **[6. Progress Maker](./progress-maker.md)** — Current progress makers create habits
- *Informs:* **[8. Competing Solutions](./competing-solutions.md)** — Anxieties are competitive barriers
- *Shapes:* **[18. Narrative Specification](../specification/narrative-specification.md)** — Stories can address anxieties
- *Affects:* **[45. Living Documentation](../evolution/living-documentation.md)** — Docs must ease anxiety

---

> *"People don't resist change. They resist being changed."*
>
> — Peter Senge

The key insight: a capability that feels imposed creates resistance. A capability that feels like a natural extension creates adoption.

---

**The Forces Diagram:**

```
                     PROGRESS
                        ↑
                        |
    Push of Current ────┼──── Pull of New
    Situation           |     Solution
    (pain of status quo)|     (attraction of benefit)
                        |
                        |
    Anxiety of New ─────┼───── Habit of Old
    Solution            |      Behavior
    (fear of change)    |      (inertia)
                        ↓
                    STATUS QUO
```

For adoption to occur:
**(Push + Pull) > (Anxiety + Habit)**

Your capability increases "Pull" through valuable outcomes. But don't forget to reduce "Anxiety" and ease the transition from "Habit."

---

**Example: Adopting a New Validation Tool**

| Factor | Force | Mitigation |
|--------|-------|------------|
| Push (status quo pain) | Manual validation is slow | None needed—this helps |
| Pull (new benefit) | Fast automated checking | Highlight speed in docs |
| Anxiety | "What if it misses errors?" | Show test coverage, comparison |
| Anxiety | "Will it slow my workflow?" | Design for < 1 second |
| Habit | Always run `make check` | Integrate with existing make targets |
| Habit | Read error output in terminal | Match familiar output format |

---

**Representing Anxieties in RDF:**

```turtle
jtbd:WorkflowDisruptionAnxiety a jtbd:Anxiety ;
    rdfs:label "Fear of workflow disruption" ;
    jtbd:question "Will this tool break my existing workflow?"@en ;
    jtbd:affectsJob jtbd:ValidateOntologyJob ;
    jtbd:mitigatedBy jtbd:NonInvasiveIntegration ;
    jtbd:severity "high" .

jtbd:NonInvasiveIntegration a jtbd:AnxietyMitigation ;
    rdfs:label "Non-invasive integration" ;
    rdfs:comment "Tool integrates with existing workflows without requiring changes"@en .

jtbd:MakeCheckHabit a jtbd:Habit ;
    rdfs:label "Running make check" ;
    jtbd:description "Users habitually run 'make check' before commits"@en ;
    jtbd:bridgedBy jtbd:MakeIntegration ;
    jtbd:affectsJob jtbd:ValidateOntologyJob .

jtbd:MakeIntegration a jtbd:HabitBridge ;
    rdfs:label "Make integration" ;
    rdfs:comment "Provide Makefile targets that invoke the new tool"@en .
```

With anxieties and habits formally captured:
- Documentation can auto-generate FAQ sections addressing anxieties
- Onboarding guides can identify habits to bridge
- Feature design can be evaluated against anxiety mitigation
- Adoption tracking can correlate with anxiety/habit factors
