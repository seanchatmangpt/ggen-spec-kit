# 3. Forces in Tension

★★

*Every interesting problem involves forces that pull in different directions. Understanding these forces—not avoiding them—is the key to solutions that feel alive.*

---

## The Nature of Tension

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

The tension is not a bug—it's a feature. It's what makes problems interesting and solutions valuable.

---

## The Problem

**Solutions that ignore forces in tension become rigid. They serve one pole perfectly while frustrating everyone who needs a different balance.**

This manifests in predictable ways:

- The "fast" solution that catches 60% of errors (users lose trust)
- The "thorough" solution that takes 10 minutes (users skip it)
- The "detailed" solution with 50-line error messages (users can't parse them)
- The "simple" solution with "Error: validation failed" (users can't fix anything)
- The "automated" solution that runs on every save (users disable it)
- The "manual" solution requiring explicit invocation (users forget it)

Each failure comes from optimizing for one force while ignoring its counterweight.

---

## Understanding Force Pairs

Forces rarely exist alone. They come in pairs that pull against each other. Understanding these pairs is essential to understanding the problem space.

### Speed vs. Thoroughness

**Speed**: Complete the task quickly. Don't interrupt flow. Return to other work.

**Thoroughness**: Check everything. Leave nothing unverified. Be comprehensive.

These forces interact:
- Faster usually means less thorough
- More thorough usually means slower
- The optimal balance depends on circumstance

**Pre-commit**: Speed dominates. Developers want feedback in seconds. A 90% check in 1 second beats a 100% check in 10 seconds.

**CI pipeline**: Thoroughness dominates. No one is watching. Better to catch everything even if it takes minutes.

**Production deployment**: Both matter equally. Can't be slow, can't miss critical issues.

### Simplicity vs. Power

**Simplicity**: Easy to understand. Few options. Quick to learn. Low cognitive load.

**Power**: Many capabilities. Fine-grained control. Handles edge cases. Highly configurable.

These forces interact:
- Simpler usually means less powerful
- More powerful usually means more complex
- The optimal balance depends on expertise level

**Novices**: Simplicity dominates. They need to succeed with minimal learning. Confusion kills adoption.

**Experts**: Power dominates. They've mastered the basics. They need capabilities that match their needs.

**Teams with mixed skill levels**: Must support both simultaneously.

### Automation vs. Control

**Automation**: Happens without thinking. Reduces cognitive load. Consistent behavior.

**Control**: Human decides when and how. Override when appropriate. Maintain agency.

These forces interact:
- More automated means less control
- More control means more decisions to make
- The optimal balance depends on trust and predictability

**Well-understood domains**: Automation dominates. If behavior is predictable, why require manual intervention?

**Novel situations**: Control dominates. Can't automate what isn't understood.

**Critical operations**: Control dominates even when automation is possible. Humans want final say on important decisions.

### Safety vs. Freedom

**Safety**: Prevent mistakes. Constrain actions. Protect from errors.

**Freedom**: Allow anything. Trust the user. Don't patronize.

These forces interact:
- Safer usually means more restricted
- Freer usually means more risk of mistakes
- The optimal balance depends on reversibility of errors

**Irreversible operations** (production deployment, data deletion): Safety dominates. Better to prevent mistakes than recover from them.

**Reversible operations** (code editing, local changes): Freedom dominates. Mistakes are learning opportunities.

**Mixed operations**: Need to distinguish what's reversible from what's not.

### Consistency vs. Flexibility

**Consistency**: Same behavior everywhere. Predictable. Easy to document.

**Flexibility**: Adapts to context. Handles special cases. Respects local needs.

These forces interact:
- More consistent means less adaptable
- More flexible means harder to predict
- The optimal balance depends on diversity of contexts

**Standardized environments**: Consistency dominates. Everyone benefits from predictability.

**Diverse environments**: Flexibility dominates. One size doesn't fit all.

**Platform evolution**: Flexibility enables experimentation; consistency enables stability.

---

## The Forces Meta-Level

Analyzing forces creates its own tensions:

### Analysis Can Paralyze

You could enumerate forces forever. Every force has sub-forces. Every pair has contextual variations. At some point, you must act.

**The danger**: Spending so long analyzing that you never build anything.

**The antidote**: "Good enough" understanding. Iterate. Learn from building.

### Forces Are Contextual

What matters to a novice differs from what matters to an expert. What matters in development differs from production. What matters at 9 AM differs from 5 PM Friday.

**The danger**: Treating forces as fixed when they're dynamic.

**The antidote**: Understand circumstances. Design for variation.

### Forces Evolve

Today's critical concern becomes tomorrow's baseline assumption. Yesterday's edge case becomes today's normal. Forces shift as the living system evolves.

**The danger**: Optimizing for yesterday's balance.

**The antidote**: Build for change. Create feedback loops.

---

## Therefore

**For the job you've identified, enumerate the key forces in tension.**

### The Force Mapping Process

#### Step 1: Identify the Primary Force Pairs

Start with the common pairs and assess their relevance to your job:

| Force Pair | Relevance to This Job |
|------------|----------------------|
| Speed vs. Thoroughness | High / Medium / Low |
| Simplicity vs. Power | High / Medium / Low |
| Automation vs. Control | High / Medium / Low |
| Safety vs. Freedom | High / Medium / Low |
| Consistency vs. Flexibility | High / Medium / Low |

Focus on high-relevance pairs. Don't waste energy on forces that don't matter.

#### Step 2: Articulate What Each Force Means

For each relevant pair, describe concretely what each pole means in your context:

**Speed vs. Thoroughness for RDF validation:**

| Speed Pole | Thoroughness Pole |
|------------|-------------------|
| Sub-second response | Full SHACL validation |
| Check syntax only | Check semantics, cardinality, types |
| Report first error | Report all errors |
| Skip optional checks | Run every check |
| Optimize for developer flow | Optimize for correctness |

#### Step 3: Map Forces to Circumstances

Different circumstances favor different balances:

| Circumstance | Speed Favored | Thoroughness Favored |
|--------------|---------------|---------------------|
| Pre-commit hook | ★★★★★ | ★★☆☆☆ |
| Manual check | ★★★☆☆ | ★★★★☆ |
| Debug session | ★☆☆☆☆ | ★★★★★ |
| CI pipeline | ★★☆☆☆ | ★★★★★ |
| Pre-release | ★★★☆☆ | ★★★★★ |

#### Step 4: Identify Who Cares About Which Pole

Different stakeholders weight forces differently:

| Stakeholder | Speed Priority | Thoroughness Priority |
|-------------|----------------|----------------------|
| Individual developer | High | Medium |
| Code reviewer | Medium | High |
| CI/CD system | Low | High |
| End user (indirectly) | Medium | High |
| Team lead | Medium | High |

#### Step 5: Document the Balance Points

For each circumstance and stakeholder combination, articulate the preferred balance:

```
Circumstance: Pre-commit validation
Stakeholder: Individual developer

Speed-Thoroughness Balance: 70% Speed, 30% Thoroughness

Rationale: The developer wants to maintain flow state. They've been
editing for hours and want to commit before context-switching.
A slow validation breaks their rhythm. They're willing to catch
some errors later in CI if it means staying fast now.

Design Implications:
- Sub-second response time is mandatory
- Syntax checking only (semantic checking in CI)
- Show first error, not all errors
- Provide quick-fix suggestions where possible
```

---

## The Force Resolution Principle

Forces are not resolved by choosing one pole. They're resolved by finding solutions that honor multiple forces simultaneously.

### Resolution Through Modes

Provide different modes for different circumstances:

```bash
# Speed-optimized: pre-commit
$ validate --quick ontology.ttl
OK (0.3s)

# Thoroughness-optimized: debug
$ validate --full --verbose ontology.ttl
[Details of all checks...]
(12.4s, 47 checks passed, 3 warnings)

# Balanced default: manual check
$ validate ontology.ttl
✓ Syntax valid
✓ SHACL shapes pass
2 warnings (use --verbose to see)
(1.2s)
```

### Resolution Through Layers

Build layers that serve different force balances:

**Layer 1: Core** (thoroughness focus)
- Complete validation logic
- All checks available
- Detailed diagnostics

**Layer 2: CLI** (balance speed and usability)
- Sensible defaults
- Progress indicators
- Formatted output

**Layer 3: IDE Integration** (speed focus)
- Real-time checking
- Incremental validation
- Inline error display

### Resolution Through Configuration

Allow users to set their own balance:

```yaml
# .validate.yaml
defaults:
  speed_level: fast  # fast | balanced | thorough
  error_display: summary  # first | summary | all

profiles:
  development:
    speed_level: fast
    on_error: continue

  production:
    speed_level: thorough
    on_error: fail
```

### Resolution Through Progressive Disclosure

Start simple, reveal power on demand:

**First use**: Just works with sensible defaults
**Repeated use**: Discover command-line options
**Advanced use**: Learn configuration files
**Expert use**: Extend with custom validation rules

---

## Anti-Patterns: How NOT to Handle Forces

### The "Pick a Side" Anti-Pattern

**What it looks like**: "We're building for speed. Thoroughness will come later."

**Why it fails**: "Later" never comes. The fast version ships. Users adapt to it. Adding thoroughness later breaks their workflow.

**Alternative**: Design for the tension from the start. Build modes, not migrations.

### The "Split the Difference" Anti-Pattern

**What it looks like**: "Let's aim for medium speed and medium thoroughness."

**Why it fails**: Medium-medium often means "not fast enough for speed-sensitive circumstances, not thorough enough for thoroughness-sensitive circumstances." You satisfy no one.

**Alternative**: Provide distinct balance points optimized for distinct circumstances.

### The "More Options" Anti-Pattern

**What it looks like**: "Let's add a flag for that. And that. And that."

**Why it fails**: Too many options means no one understands what to use when. Cognitive load defeats the purpose of simplicity.

**Alternative**: Sensible defaults, named profiles, progressive disclosure.

### The "One User Type" Anti-Pattern

**What it looks like**: "Our users are experts. They want power."

**Why it fails**: No user base is homogeneous. Even experts have moments when they want simplicity. New users need on-ramps.

**Alternative**: Design for the spectrum. Welcome newcomers. Enable experts.

### The "Forces Are Fixed" Anti-Pattern

**What it looks like**: Design once, ship forever.

**Why it fails**: Forces shift as the living system evolves. Yesterday's balance becomes today's mismatch.

**Alternative**: Build feedback loops. Measure usage. Evolve the balance.

---

## Case Study: The Speed Trap

A team built a validation tool optimized for thoroughness. It ran 47 different checks. Every edge case was covered. It was beautiful engineering.

Problem: It took 15 seconds.

Developers stopped using it. "Too slow for my workflow." They reverted to manual inspection.

The team's response: "But it's more accurate!"

Yes, but 0% usage of a thorough tool catches fewer errors than 100% usage of a quick tool.

**The fix**:

They analyzed circumstances and discovered:
- 80% of usage was pre-commit (speed critical)
- 15% was debugging (thoroughness critical)
- 5% was CI (thoroughness critical, speed less important)

They restructured:
- Quick mode (2 seconds): Syntax + critical SHACL shapes only. Default for pre-commit.
- Full mode (15 seconds): All 47 checks. Explicit invocation for debug.
- CI mode (15 seconds + detailed output): Same checks, machine-readable format.

Usage soared. Errors caught increased. The forces were honored.

---

## Case Study: The Configurability Explosion

Another team overcorrected. They made everything configurable. Users could:
- Choose which checks to run
- Set severity for each check
- Configure error formats
- Tune performance parameters
- Define custom checks
- ...and 47 more options

The result: analysis paralysis. Users didn't know what to configure. Documentation sprawled. Support tickets multiplied. "What settings should I use?"

**The fix**:

They collapsed to three modes:
1. **Quick** — Speed optimized, 5 critical checks
2. **Standard** — Balanced, 20 common checks
3. **Thorough** — Comprehensive, all 47 checks

Power users could still override, but 95% of users just picked a mode.

Adoption increased. Support decreased. The forces were honored through simplicity.

---

## Representing Forces in RDF

Forces can be formally captured in the specification:

```turtle
@prefix jtbd: <http://example.org/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Define a force tension
jtbd:SpeedVsThoroughness a jtbd:ForceTension ;
    rdfs:label "Speed vs Thoroughness"@en ;
    rdfs:comment "The tension between fast feedback and comprehensive checking"@en ;
    jtbd:force1 jtbd:Speed ;
    jtbd:force2 jtbd:Thoroughness ;
    jtbd:affectsJob jtbd:ValidateOntologyJob ;
    jtbd:relevance "high" .

# Define individual forces
jtbd:Speed a jtbd:Force ;
    rdfs:label "Speed"@en ;
    jtbd:valueProposition "Complete tasks quickly, maintain flow state"@en ;
    jtbd:indicators "response time, perceived responsiveness, workflow interruption"@en .

jtbd:Thoroughness a jtbd:Force ;
    rdfs:label "Thoroughness"@en ;
    jtbd:valueProposition "Catch all errors, ensure correctness"@en ;
    jtbd:indicators "error detection rate, false negative rate, coverage"@en .

# Define balance points for circumstances
jtbd:PreCommitSpeedBalance a jtbd:ForceBalance ;
    jtbd:forTension jtbd:SpeedVsThoroughness ;
    jtbd:forCircumstance jtbd:PreCommitCircumstance ;
    jtbd:balance1Weight "70"^^xsd:integer ;  # Speed
    jtbd:balance2Weight "30"^^xsd:integer ;  # Thoroughness
    jtbd:rationale "Developer flow state is critical; some errors can be caught in CI"@en ;
    jtbd:designImplication "Sub-second response required; syntax-only checking acceptable"@en .

jtbd:DebugSessionBalance a jtbd:ForceBalance ;
    jtbd:forTension jtbd:SpeedVsThoroughness ;
    jtbd:forCircumstance jtbd:DebugSessionCircumstance ;
    jtbd:balance1Weight "20"^^xsd:integer ;  # Speed
    jtbd:balance2Weight "80"^^xsd:integer ;  # Thoroughness
    jtbd:rationale "Finding the root cause matters more than speed"@en ;
    jtbd:designImplication "Full validation acceptable; detailed diagnostics essential"@en .

# Features can declare which force they serve
jtbd:QuickValidationMode a jtbd:Feature ;
    rdfs:label "Quick validation mode"@en ;
    jtbd:servesForce jtbd:Speed ;
    jtbd:sacrificesForce jtbd:Thoroughness ;
    jtbd:appropriateFor jtbd:PreCommitCircumstance .

jtbd:FullValidationMode a jtbd:Feature ;
    rdfs:label "Full validation mode"@en ;
    jtbd:servesForce jtbd:Thoroughness ;
    jtbd:sacrificesForce jtbd:Speed ;
    jtbd:appropriateFor jtbd:DebugSessionCircumstance, jtbd:CIPipelineCircumstance .
```

### Querying Force Relationships

With forces in RDF, you can query them:

```sparql
# Find all force tensions affecting a job
SELECT ?tension ?force1 ?force2
WHERE {
    ?tension a jtbd:ForceTension ;
             jtbd:affectsJob jtbd:ValidateOntologyJob ;
             jtbd:force1 ?force1 ;
             jtbd:force2 ?force2 .
}

# Find appropriate features for a circumstance
SELECT ?feature ?label ?serves ?sacrifices
WHERE {
    ?feature a jtbd:Feature ;
             rdfs:label ?label ;
             jtbd:appropriateFor jtbd:PreCommitCircumstance ;
             jtbd:servesForce ?serves ;
             jtbd:sacrificesForce ?sacrifices .
}

# Find balance points for a tension
SELECT ?circumstance ?label ?weight1 ?weight2 ?rationale
WHERE {
    ?balance jtbd:forTension jtbd:SpeedVsThoroughness ;
             jtbd:forCircumstance ?circumstance ;
             jtbd:balance1Weight ?weight1 ;
             jtbd:balance2Weight ?weight2 ;
             jtbd:rationale ?rationale .
    ?circumstance rdfs:label ?label .
}
```

---

## The Force Balance Canvas

Use this framework to structure your force analysis:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FORCE BALANCE CANVAS                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  JOB: _____________________________________                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      FORCE PAIR 1                            │   │
│  │  Force A: ____________    ←──────────→    Force B: _________ │   │
│  │                                                              │   │
│  │  Circumstance 1: ________   Balance: A [===|    ] B          │   │
│  │  Circumstance 2: ________   Balance: A [  |=====] B          │   │
│  │  Circumstance 3: ________   Balance: A [=== |===] B          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                      FORCE PAIR 2                            │   │
│  │  Force C: ____________    ←──────────→    Force D: _________ │   │
│  │                                                              │   │
│  │  Circumstance 1: ________   Balance: C [===|    ] D          │   │
│  │  Circumstance 2: ________   Balance: C [  |=====] D          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  DESIGN IMPLICATIONS:                                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. _______________________________________________________  │   │
│  │ 2. _______________________________________________________  │   │
│  │ 3. _______________________________________________________  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Checklist: Have You Understood the Forces?

Before proceeding to design, verify:

### Force Identification
- [ ] I have identified the key force pairs affecting this job
- [ ] I have articulated what each force means in this context
- [ ] I understand why each force has value (not just why one pole is better)

### Circumstance Mapping
- [ ] I have mapped how force balance shifts across circumstances
- [ ] I have documented which stakeholders care about which forces
- [ ] I understand when each balance point is appropriate

### Resolution Strategy
- [ ] I have a strategy for honoring multiple forces (modes, layers, configuration)
- [ ] I have sensible defaults for common circumstances
- [ ] I have progressive disclosure for advanced needs

### Anti-Pattern Avoidance
- [ ] I am not "picking a side" and ignoring the other pole
- [ ] I am not "splitting the difference" with a compromise that satisfies no one
- [ ] I am not creating a "configurability explosion" that overwhelms users
- [ ] I am not assuming "one user type" when my users are diverse

If any of these remain unclear, invest more time in understanding before building.

---

## Resulting Context

After applying this pattern, you have:

- A map of the key forces affecting this job
- Understanding of why no single solution serves everyone perfectly
- Insight into how balance points shift by context
- Raw material for design decisions

This understanding shapes:
- **[5. Outcome Desired](./outcome-desired.md)** — Outcomes must honor forces
- **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — Criteria must acknowledge trade-offs
- **[11. Executable Specification](../specification/executable-specification.md)** — Specs must accommodate forces

---

## Code References

The following spec-kit source files implement force concepts discussed in this pattern:

| Reference | Description |
|-----------|-------------|
| `ontology/jtbd-schema.ttl:138-176` | Force classes (Force, PushForce, PullForce, Habit, Anxiety) modeling tensions |
| `ontology/jtbd-schema.ttl:178-220` | ForceTension class linking opposing forces |
| `ontology/jtbd-schema.ttl:950-990` | ForceShape SHACL validation for force specifications |
| `ontology/spec-kit-schema.ttl:466-516` | FeatureShape showing how features balance forces |
| `src/specify_cli/runtime/receipt.py:188-209` | verify_idempotence showing tension between speed and thoroughness |

---

## Related Patterns

### Builds on:

**[2. Customer Job](./customer-job.md)** — Forces arise from jobs. The job creates the context where forces become relevant.

**[1. Living System](./living-system.md)** — Forces emerge from the living system. The system's complexity generates the tensions.

### Informs:

**[5. Outcome Desired](./outcome-desired.md)** — Outcomes balance forces. Different outcomes prioritize different force poles.

**[6. Progress Maker](./progress-maker.md)** — Progress means resolving tensions. Existing progress makers embody particular force balances.

### Shapes:

**[11. Executable Specification](../specification/executable-specification.md)** — Specifications must accommodate forces. The spec should capture force balance requirements.

---

## Philosophical Foundations

> *"In complex systems, there are no solutions—only trade-offs."*
>
> — Thomas Sowell

The art of capability creation lies not in eliminating trade-offs but in finding resolutions that honor multiple forces. A truly alive capability doesn't ignore forces—it dances with them.

Every force pair represents a fundamental truth about the problem domain. Speed and thoroughness are both valuable—that's why they're in tension. The tension is not a defect of reality; it's a feature.

A capability that pretends one pole doesn't exist will frustrate users who need that pole. A capability that tries to "solve" the tension by forcing one answer will feel rigid and dead.

A capability that acknowledges the tension, provides graceful ways to navigate it, and respects different users' different needs—that capability feels alive. It has the "quality without a name."

> *"There is a central quality which is the root criterion of life and spirit in a man, a town, a building, or a wilderness. This quality is objective and precise, but it cannot be named."*
>
> — Christopher Alexander

That quality emerges when forces are honored, not suppressed.

---

## Exercise: Map Your Forces

Before designing your next capability, complete this exercise:

1. **Identify your job**: What progress is the customer seeking?

2. **List force pairs**: Which of the common pairs (speed/thoroughness, simplicity/power, etc.) are relevant?

3. **Articulate each pole**: What does each force mean in your specific context?

4. **Map to circumstances**: How does the balance shift across the circumstances you've identified?

5. **Design for resolution**: How will you honor multiple forces? Modes? Layers? Configuration? Progressive disclosure?

6. **Test your design**: For each circumstance, verify that your design provides an appropriate balance.

Only after completing this exercise should you proceed to define **[Outcomes Desired](./outcome-desired.md)**.

---

## Further Reading

- Alexander, Christopher. *Notes on the Synthesis of Form* (1964) — The foundational work on handling forces in design.
- Norman, Don. *The Design of Everyday Things* (2013) — Practical treatment of trade-offs in user-facing design.
- Meadows, Donella. *Thinking in Systems* (2008) — Understanding forces from a systems perspective.
- Brand, Stewart. *How Buildings Learn* (1994) — How designs evolve as forces shift over time.

---

Forces are not problems to be solved. They are tensions to be understood, honored, and navigated. The capability that dances with its forces will thrive. The capability that ignores them will struggle.
