# 8. Competing Solutions

★★

*Your capability doesn't exist in isolation. It competes for adoption against every other way customers might get the job done—including doing nothing at all.*

---

## The Competitive Reality

You've mapped the **[Living System](./living-system.md)**, understood the **[Customer Job](./customer-job.md)**, and cataloged **[Progress Makers](./progress-maker.md)**. Now look at the landscape with competitive eyes.

Every progress maker is a competing solution. They compete for:
- The customer's attention
- The customer's time to learn
- The customer's willingness to change
- The customer's trust
- A place in the customer's workflow

Your capability enters this competition the moment you release it. Understanding the competitive landscape helps you design something that can actually win adoption—not just work technically.

---

## The Problem

**Capabilities built without considering competition often lose to existing solutions—not because they're worse, but because they're not different enough to overcome switching costs.**

This manifests in predictable ways:

- The better tool that never displaces the incumbent
- The faster solution ignored because "what we have works"
- The innovation that seems obvious but never catches on
- The superior technology that remains a niche curiosity
- The feature that solves a problem nobody will pay attention to

Behind each failure lies the same competitive blindness: building without understanding what you're competing against.

---

## Understanding Competitive Categories

Competition comes in many forms. Understanding these categories reveals who and what you're actually up against.

### Direct Competitors

Solutions explicitly designed for the same job:

These are the obvious competitors—tools, products, and services that position themselves for the same use case.

**Questions to ask:**
- What tools are marketed for this job?
- What do users search for when looking for a solution?
- What appears in "alternatives to X" lists?
- What do blog posts compare?

**Analysis points:**
- What do they do well?
- What do they do poorly?
- What is their positioning?
- What is their adoption level?
- What is their trajectory (growing, stable, declining)?

### Indirect Competitors

Solutions used for the job but not designed for it:

These are the less obvious competitors—tools people have adapted, workarounds they've developed, general-purpose solutions they've applied.

**Examples:**
- Spreadsheets used as databases
- Shell scripts used as automation
- Email used as task management
- Manual processes substituting for automation
- General-purpose tools (grep, awk) doing specialized jobs

**Analysis points:**
- Why are people using these instead of purpose-built tools?
- What do they provide that purpose-built tools don't?
- What are the limitations that create opportunity?

### Non-Consumption

The choice to tolerate the problem rather than solve it:

This is the most underestimated competitor. Many people don't use any solution—they just live with the problem.

**Why it matters:**
- Non-consumption represents untapped market
- But it also signals that the problem may not be painful enough
- Or that all solutions are too expensive (in time, money, or effort)

**Analysis points:**
- Why do some people not solve this job at all?
- What would make solving it worth their effort?
- What barriers prevent adoption of existing solutions?

### Future Competitors

Solutions that might emerge:

Technology evolves. New approaches appear. Adjacent players enter the space.

**Questions to ask:**
- What technology trends could enable new solutions?
- Who are adjacent players who might expand into this job?
- What startups are emerging in this space?
- What research might become productized?

**Analysis points:**
- What's your defensive moat against future competitors?
- How can you evolve to stay ahead?
- What positioning is durable vs. vulnerable?

---

## The Forces at Play

Several forces shape competitive dynamics:

### Good Enough Is the Enemy of Better

If current solutions are "good enough," your "better" solution must be dramatically better to trigger change.

**The 10x rule**: For many users, a new solution needs to be ~10x better on some dimension to overcome switching costs. Marginal improvements don't motivate change.

**Implication**: Don't just be better. Be remarkably better on dimensions that matter.

### Integration Beats Isolation

A solution that integrates with the existing ecosystem has an advantage over one that requires changing everything.

**Network effects**: Tools that connect to other tools become more valuable. Tools that require replacing the ecosystem face resistance.

**Implication**: Design for the ecosystem, not against it.

### Trust Takes Time

Established solutions have earned trust through use. New solutions must prove themselves.

**Risk asymmetry**: Switching to something new carries risk. Staying with something known doesn't. Even if the new is better, the risk feels higher.

**Implication**: Build trust through transparency, proof, and incremental adoption paths.

### Network Effects Compound

Solutions others use become more valuable because:
- Knowledge accumulates (tutorials, Stack Overflow answers)
- Integrations multiply (plugins, extensions)
- Support strengthens (communities, consultants)
- Hiring becomes easier (people know it)

**Implication**: Consider community building, not just product building.

### Switching Costs Are Real

Even free tools have adoption costs:
- Learning: Time to understand
- Migration: Effort to transition
- Integration: Work to connect to other tools
- Workflow: Changes to established patterns
- Risk: Possibility of problems

**Implication**: Account for total cost of adoption, not just tool cost.

---

## Therefore

**Analyze the competitive landscape systematically before designing.**

### The Competitive Analysis Process

#### Step 1: Enumerate All Competitors

Create a comprehensive list:

| Competitor | Category | Brief Description |
|------------|----------|-------------------|
| `rapper` CLI | Direct | Standard RDF syntax validator |
| `riot` (Jena) | Direct | Comprehensive RDF toolkit |
| `pyshacl` | Direct | Python SHACL validator |
| IDE linting | Indirect | Real-time syntax feedback |
| CI pipeline | Indirect | Automated validation in flow |
| Manual review | Indirect | Human visual inspection |
| Nothing | Non-consumption | Tolerating occasional errors |

#### Step 2: Profile Each Competitor

For each competitor, understand:

```
┌─────────────────────────────────────────────────────────────────────┐
│                   COMPETITOR PROFILE                                │
├─────────────────────────────────────────────────────────────────────┤
│ Name: rapper (Raptor RDF Parser)                                    │
│ Category: Direct competitor                                         │
│                                                                     │
│ STRENGTHS                                                           │
│ - Standard tool in RDF ecosystem                                    │
│ - Widely installed and available                                    │
│ - Fast for basic syntax checking                                    │
│ - Well-documented, stable                                           │
│                                                                     │
│ WEAKNESSES                                                          │
│ - Cryptic error messages                                            │
│ - No SHACL support                                                  │
│ - No semantic validation                                            │
│ - Output format dated                                               │
│                                                                     │
│ POSITIONING                                                         │
│ "The standard RDF parser and serializer"                            │
│ De facto baseline tool for basic validation                         │
│                                                                     │
│ ADOPTION                                                            │
│ Very high in RDF community. Often pre-installed.                    │
│ Default choice when validation is needed.                           │
│                                                                     │
│ TRAJECTORY                                                          │
│ Stable. Mature product with infrequent updates.                     │
│ Not actively evolving but not declining.                            │
│                                                                     │
│ WHY PEOPLE USE IT                                                   │
│ - "It's what everyone uses"                                         │
│ - "It came with my setup"                                           │
│ - "Good enough for basic checks"                                    │
│                                                                     │
│ WHY PEOPLE DON'T USE IT                                             │
│ - "Error messages are useless"                                      │
│ - "Need SHACL validation"                                           │
│ - "Doesn't fit my workflow"                                         │
└─────────────────────────────────────────────────────────────────────┘
```

#### Step 3: Create a Competitive Map

Visualize the landscape on relevant dimensions:

```
                    COMPREHENSIVE
                         ↑
                         |
                         |  ┌─────────┐
                         |  │  riot   │ (high capability, complex)
                         |  └─────────┘
                         |
                         |         ┌─────────┐
                         |         │ pyshacl │
                         |         └─────────┘
                         |
         ┌─────────┐     |
         │ Manual  │     |
         │ Review  │     |
         └─────────┘     |
                         |
    SLOW ────────────────┼────────────────── FAST
                         |
                         |  ┌─────────┐
                         |  │ rapper  │
                         |  └─────────┘
                         |
          ┌─────────┐    |     ┌─────────┐
          │ Nothing │    |     │ IDE     │
          └─────────┘    |     │ Linting │
                         |     └─────────┘
                         |
                         ↓
                      SIMPLE
```

This reveals positioning opportunities:
- Fast + Comprehensive = open space
- Fast + Simple = crowded (IDE, rapper)
- Slow + Comprehensive = served (riot, pyshacl)

#### Step 4: Identify Competitive Position

Based on analysis, choose your position:

**Segment Focus**: Serve a specific circumstance better than anyone.
- "Best pre-commit experience"
- "Most developer-friendly error messages"
- "Fastest local validation"

**Outcome Focus**: Deliver an outcome competitors neglect.
- "Zero errors reach CI"
- "Understand what's wrong in 5 seconds"
- "Confidence before you push"

**Integration Focus**: Work better with the ecosystem.
- "Works with every IDE"
- "Drops into any CI pipeline"
- "Complements your existing tools"

**Simplicity Focus**: Radically easier to adopt and use.
- "One command to install"
- "Zero configuration needed"
- "Works in 5 seconds"

**Performance Focus**: Dramatically faster or more thorough.
- "10x faster than anything else"
- "Catches errors others miss"
- "Combines syntax + SHACL + semantics"

Your positioning should be:
- **Defensible**: Hard for competitors to copy
- **Meaningful**: Matters to your target customers
- **Clear**: Easy to communicate
- **Aligned**: Fits your capabilities and resources

#### Step 5: Articulate Differentiation

Write the positioning statement:

```
For [target customer]
Who [job to be done]
The [capability name] is a [category]
That [key benefit]
Unlike [competitors]
Our solution [differentiation]
```

Example:

```
For RDF developers
Who need to validate ontologies before committing
spec-kit validate is a CLI validator
That catches errors before they reach CI with clear, actionable messages
Unlike rapper (cryptic) or CI pipelines (slow feedback)
Our solution gives fast, friendly feedback in the developer workflow
```

---

## Case Study: Entering a Crowded Space

A team wanted to build a validation tool for RDF. The space seemed crowded:
- rapper: Standard, everywhere
- riot: Comprehensive, powerful
- pyshacl: SHACL-focused, Python
- IDE plugins: Real-time, in-context

Why build another?

**Competitive analysis revealed:**

| Competitor | Speed | Clarity | SHACL | Workflow Fit |
|------------|-------|---------|-------|--------------|
| rapper | Fast | Poor | No | Medium |
| riot | Slow | Medium | Yes | Poor |
| pyshacl | Medium | Medium | Yes | Medium |
| IDE | Fast | Medium | No | Excellent |
| CI | Slow | Poor | Yes | Excellent |

**The gap**: No solution was fast + clear + SHACL + workflow-integrated.

**The position**: "Fast pre-commit validation with clear messages and SHACL support."

**The differentiation**:
- Faster than riot (seconds, not minutes)
- Clearer than rapper (actionable messages)
- More complete than IDE (SHACL included)
- Earlier than CI (pre-commit, not post-push)

This wasn't about being better at everything. It was about being notably better at a specific combination that no one else offered.

---

## Case Study: Competing Against Non-Consumption

Another team found that most developers in their target market didn't use any validation tool. "We just eyeball it."

Competitive analysis against non-consumption:

**Why non-consumption wins:**
- "Validation tools are slow and annoying"
- "Setup takes too long"
- "Errors are rare enough to ignore"
- "I'll catch it in review"

**What would make consumption worthwhile:**
- Instant feedback (no waiting)
- Zero setup (works immediately)
- Clear value (catches things humans miss)
- Low friction (doesn't interrupt workflow)

**The positioning**: Not "better than other tools" but "better than nothing—barely more effort than doing nothing."

**The strategy**:
- One-line install that works immediately
- Automatic activation (pre-commit hook installed automatically)
- Silent when passing (no noise)
- Only interrupts for real problems

This wasn't competing with other tools. It was competing with the inertia of doing nothing.

---

## Representing Competition in RDF

Competitive analysis can be formally captured:

```turtle
@prefix jtbd: <http://example.org/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Competitor definitions
jtbd:RapperTool a jtbd:CompetingSolution ;
    rdfs:label "rapper CLI"@en ;
    jtbd:category jtbd:DirectCompetitor ;
    jtbd:description "Standard RDF syntax validator"@en ;

    jtbd:strength "Standard tool, widely available"@en ;
    jtbd:weakness "Cryptic error messages"@en ;
    jtbd:weakness "No SHACL support"@en ;
    jtbd:positioning "Ecosystem default"@en ;
    jtbd:adoptionLevel "high" ;
    jtbd:trajectory "stable" ;

    jtbd:addressesJob jtbd:ValidateOntologyJob .

jtbd:NonConsumption a jtbd:CompetingSolution ;
    rdfs:label "Non-consumption"@en ;
    jtbd:category jtbd:NonConsumption ;
    jtbd:description "Choosing to live with occasional errors"@en ;

    jtbd:strength "Zero effort"@en ;
    jtbd:weakness "Errors escape and cause problems"@en ;
    jtbd:adoptionReason "Insufficient pain, all solutions too costly"@en ;

    jtbd:addressesJob jtbd:ValidateOntologyJob .

# Our positioning
jtbd:SpecKitValidate a jtbd:Capability ;
    rdfs:label "spec-kit validate"@en ;
    jtbd:positioningType jtbd:SegmentFocus ;
    jtbd:targetCircumstance jtbd:PreCommitCircumstance ;
    jtbd:keyBenefit "Fast, clear feedback before commit"@en ;

    jtbd:competesAgainst jtbd:RapperTool, jtbd:NonConsumption, jtbd:CIPipeline ;
    jtbd:differentiation "Speed + clarity + SHACL in developer workflow"@en ;

    jtbd:advantageOver jtbd:RapperTool, "Clear error messages" ;
    jtbd:advantageOver jtbd:CIPipeline, "Faster feedback loop" ;
    jtbd:advantageOver jtbd:NonConsumption, "Catches errors with minimal effort" .
```

### Querying Competition

With competitive analysis in RDF, you can query:

```sparql
# Find all direct competitors
SELECT ?competitor ?strength ?weakness
WHERE {
    ?competitor a jtbd:CompetingSolution ;
                jtbd:category jtbd:DirectCompetitor ;
                jtbd:addressesJob jtbd:ValidateOntologyJob ;
                jtbd:strength ?strength ;
                jtbd:weakness ?weakness .
}

# Find our advantages over each competitor
SELECT ?competitor ?advantage
WHERE {
    jtbd:SpecKitValidate jtbd:advantageOver ?competitor, ?advantage .
}

# Find high-adoption competitors (biggest threats)
SELECT ?competitor ?adoptionLevel
WHERE {
    ?competitor a jtbd:CompetingSolution ;
                jtbd:adoptionLevel "high" .
}
```

---

## The Competitive Force Field

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

**Direct competitors**: Existing tools for the same job
**Indirect competitors**: Adapted solutions and workarounds
**Non-consumption**: The choice to do nothing
**Switching costs**: Barriers to choosing you
**Future competitors**: Emerging threats

You're pulled in all directions. Your positioning determines which battles to fight and which to avoid.

---

## Checklist: Have You Analyzed Competition?

Before finalizing design, verify:

### Competitor Enumeration
- [ ] I have listed all direct competitors
- [ ] I have identified indirect competitors
- [ ] I have analyzed non-consumption
- [ ] I have considered future competitors

### Competitor Profiling
- [ ] I have documented each competitor's strengths and weaknesses
- [ ] I understand why people choose each competitor
- [ ] I know each competitor's positioning and trajectory
- [ ] I've used the tools myself

### Competitive Mapping
- [ ] I have visualized the landscape on relevant dimensions
- [ ] I have identified gaps and opportunities
- [ ] I understand where the space is crowded vs. open

### Positioning
- [ ] I have chosen a clear positioning
- [ ] My positioning is defensible and meaningful
- [ ] I can articulate differentiation concisely
- [ ] I know which competitors I'm taking on vs. avoiding

If any of these remain unclear, invest more time before building.

---

## Resulting Context

After applying this pattern, you have:

- A clear view of the competitive landscape
- Understanding of why competitors succeed or fail
- Explicit positioning for your capability
- Realistic assessment of what's needed to win adoption

This completes the Context Patterns. You're ready to move to **[Part II: Specification Patterns](../specification/semantic-foundation.md)**, where you'll capture this understanding in executable form.

---

## Related Patterns

### Builds on:

**[6. Progress Maker](./progress-maker.md)** — Progress makers are competitors.

**[7. Anxieties and Habits](./anxieties-and-habits.md)** — Competitors benefit from existing habits.

### Informs:

**[11. Executable Specification](../specification/executable-specification.md)** — Specs must address competitive position.

### Affects:

**[45. Living Documentation](../evolution/living-documentation.md)** — Docs must differentiate.

---

## Philosophical Foundations

> *"If you're not the one defining your competition, your competition will define you."*

Know what you're up against. Design accordingly.

Competition isn't just about winning market share. It's about understanding the forces that shape adoption. Even if you're building for internal use, with no commercial competitors, you still compete:
- Against existing tools and processes
- Against habits and inertia
- Against the choice to do nothing
- For attention, time, and trust

A capability that understands its competitive context can position itself effectively. A capability that ignores competition will be surprised when technically excellent solutions fail to achieve adoption.

> *"The purpose of a company is to create a customer."*
>
> — Peter Drucker

But customers have choices. Understanding those choices—and positioning to win them—is how you actually create customers.

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

This is the context. You understand the territory.

Now it's time to capture this understanding in executable form. Turn to **[Part II: Specification Patterns](../specification/semantic-foundation.md)** to learn how to transform this context understanding into formal, machine-readable specifications that can drive generation, validation, and evolution.

---

## Exercise: Map Your Competition

Before designing your next capability, complete this exercise:

1. **Enumerate**: List all competitors (direct, indirect, non-consumption, future)
2. **Profile**: Understand each competitor's strengths, weaknesses, positioning
3. **Map**: Visualize the landscape on relevant dimensions
4. **Position**: Choose your positioning and differentiation
5. **Validate**: Test your positioning with target customers

Only after completing this exercise should you proceed to **[Part II: Specification Patterns](../specification/semantic-foundation.md)**.

---

## Further Reading

- Moore, Geoffrey. *Crossing the Chasm* (2014) — Competitive positioning for technology adoption.
- Porter, Michael. *Competitive Strategy* (1980) — The classic framework for competitive analysis.
- Kim, W. Chan & Mauborgne, Renée. *Blue Ocean Strategy* (2015) — Creating uncontested market space.
- Christensen, Clayton. *The Innovator's Dilemma* (1997) — How disruption works in competitive markets.

---

You don't build in a vacuum. You build in a world of alternatives, habits, and choices. Understand that world, and you'll build something that can actually win.
