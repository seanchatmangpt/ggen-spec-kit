# 6. Progress Maker

★★

*Customers don't want features. They want progress. A progress maker is anything that helps move from struggle to satisfaction on a job to be done.*

---

## The Progress Landscape

You've defined the **[Customer Job](./customer-job.md)**, identified the **[Circumstance of Struggle](./circumstance-of-struggle.md)**, and specified the **[Outcome Desired](./outcome-desired.md)**. Now ask: what actually helps customers make progress?

A progress maker is any solution—complete or partial, manual or automated, simple or complex—that moves customers toward their desired outcome.

Progress makers exist before you build anything. Your capability, if you build it well, becomes one more progress maker in the customer's toolkit. But you're not entering a vacuum; you're joining a world where people have already found ways to cope.

Understanding existing progress makers is essential. They reveal:
- What's already working (so you don't reinvent it poorly)
- What's failing (opportunities to do better)
- What's expected (the baseline you must exceed)
- How people think about the problem (the mental models they bring)

---

## The Problem

**Building capabilities without understanding existing progress makers leads to solutions that ignore what already works, compete poorly, or duplicate effort.**

This manifests in predictable ways:

- The new tool that's objectively better but feels unfamiliar (users stay with the old)
- The feature that solves a problem users already solved with a workaround (they don't switch)
- The capability that requires abandoning existing integrations (too expensive to adopt)
- The innovation that doesn't improve on the cobbled-together solution (insufficient motivation to change)
- The product that enters a saturated space without understanding it (fails to differentiate)

Behind each failure lies the same mistake: building without understanding what already makes progress possible.

---

## What is a Progress Maker?

A progress maker is anything that helps customers make progress on a job. It includes:

### Formal Tools

Software, hardware, services explicitly designed for the job:
- Commercial products
- Open source tools
- Internal applications
- Platforms and services

### Shadow Tools

Unofficial solutions people create for themselves:
- Spreadsheets repurposed for tracking
- Scripts cobbled together for automation
- Browser bookmarklets for quick actions
- Command aliases and shell functions
- Shared templates and checklists

Shadow tools reveal the true jobs. If people invest effort creating them, the job matters.

### Manual Processes

Human labor without automation:
- Peer review (visual inspection)
- Checklists (mental verification)
- Pair programming (real-time validation)
- Manual testing (exploratory verification)

Manual processes are often invisible in tools-focused thinking but represent significant investment.

### Workarounds

Hacks that address limitations of existing solutions:
- "Just ignore that error, it's a known issue"
- "Copy-paste from the template and edit"
- "Run the command twice because it fails the first time"
- "Export to CSV, fix in Excel, import back"

Workarounds reveal gaps in existing progress makers—and opportunities for improvement.

### Non-Consumption

The choice to tolerate the problem rather than solve it:
- "We just live with it"
- "It's not worth the hassle"
- "We'll deal with it later"
- "It's a nice-to-have, not a must-have"

Non-consumption is the most important progress maker to understand. It reveals when the job isn't painful enough—or when all solutions are too costly.

---

## The Forces at Play

Several forces make progress makers difficult to understand:

### Something Is Always Better Than Nothing

Even a terrible workaround represents progress over pure struggle. People adapt to what they have. The clunky tool becomes "how we do things."

**Implication**: Your capability competes against established (even suboptimal) solutions, not against nothing.

### Familiarity Breeds Tolerance

People accept friction in tools they know. Learning curves are sunk costs. Integration is already done. Mental models are established.

Your "better" solution must overcome this accumulated investment.

**Implication**: Being marginally better isn't enough. You need significant improvement to justify switching.

### Partial Solutions Accumulate

Customers often combine multiple partial progress makers:
- IDE plugin for quick syntax check
- CI pipeline for comprehensive validation
- Peer review for semantic understanding
- Manual testing for edge cases

Your capability enters this ecosystem, not replacing it but fitting into it.

**Implication**: Consider complementing existing progress makers, not just replacing them.

### Different Progress Makers Serve Different Circumstances

The quick workaround serves one circumstance; the thorough tool serves another. The same job may have different progress makers for different moments.

**Implication**: Understand which progress makers serve which circumstances.

---

## Therefore

**Before designing your capability, catalog the progress makers customers currently use.**

### The Progress Maker Mapping Process

#### Step 1: Enumerate Progress Makers

List all ways customers currently make progress on this job:

| # | Progress Maker | Type | Brief Description |
|---|----------------|------|-------------------|
| 1 | Manual inspection | Manual | Visual review of code before commit |
| 2 | IDE linting | Formal tool | Real-time syntax highlighting |
| 3 | `rapper` CLI | Formal tool | RDF syntax validation |
| 4 | CI SHACL check | Formal tool | Automated schema validation |
| 5 | Custom script | Shadow tool | Team-built validation wrapper |
| 6 | Peer review | Manual | Colleague reviews changes |
| 7 | "Ignore it" | Non-consumption | Tolerate occasional errors |

Don't filter yet. Capture the full landscape.

#### Step 2: Profile Each Progress Maker

For each progress maker, understand its characteristics:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PROGRESS MAKER PROFILE                           │
├─────────────────────────────────────────────────────────────────────┤
│ Name: IDE Linting (VS Code RDF Extension)                           │
│ Type: Formal Tool                                                   │
│                                                                     │
│ WHAT IT DOES                                                        │
│ - Highlights syntax errors in real-time                             │
│ - Shows squiggly underlines at error locations                      │
│ - Provides quick-fix suggestions for common issues                  │
│                                                                     │
│ OUTCOMES ADDRESSED                                                  │
│ ✓ Minimize time to detect syntax errors: High                       │
│ ✓ Maximize clarity of error messages: Medium                        │
│ ✗ Minimize semantic errors: Not addressed                           │
│ ✗ Full SHACL validation: Not addressed                              │
│                                                                     │
│ STRENGTHS                                                           │
│ - Instant feedback (no command invocation)                          │
│ - Visible in context (where you're editing)                         │
│ - Low cognitive load (automatic)                                    │
│ - Already integrated in workflow                                    │
│                                                                     │
│ LIMITATIONS                                                         │
│ - Syntax only (no schema validation)                                │
│ - Limited error explanations                                        │
│ - VS Code only (not portable)                                       │
│ - Misses some edge cases                                            │
│                                                                     │
│ CIRCUMSTANCE FIT                                                    │
│ ✓ During editing: Excellent                                         │
│ ✗ Pre-commit: Not designed for this                                 │
│ ✗ Debug session: Insufficient depth                                 │
│ ✗ CI pipeline: Not applicable                                       │
│                                                                     │
│ ADOPTION REASON                                                     │
│ - Pre-installed with popular extension                              │
│ - Zero configuration                                                │
│ - Familiar from other languages                                     │
│                                                                     │
│ SWITCHING COST                                                      │
│ Low for this specific tool, but high for IDE in general.            │
│ Users won't change IDEs for better RDF validation.                  │
└─────────────────────────────────────────────────────────────────────┘
```

#### Step 3: Map Outcomes to Progress Makers

Create a matrix showing which progress makers address which outcomes:

| Outcome | IDE Lint | rapper | CI SHACL | Peer Review | Script |
|---------|----------|--------|----------|-------------|--------|
| Fast error detection | ★★★★★ | ★★★☆☆ | ★☆☆☆☆ | ★☆☆☆☆ | ★★★☆☆ |
| Error message clarity | ★★★☆☆ | ★☆☆☆☆ | ★★☆☆☆ | ★★★★★ | ★★☆☆☆ |
| Semantic validation | ☆☆☆☆☆ | ☆☆☆☆☆ | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Pre-commit blocking | ☆☆☆☆☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★★☆ |
| Confidence boost | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ |

This reveals:
- **Gaps**: Outcomes no progress maker addresses well
- **Saturated areas**: Outcomes well-served by multiple progress makers
- **Opportunities**: High-importance outcomes with low coverage

#### Step 4: Identify Your Positioning

Based on the landscape, determine how your capability should position:

**Gap Filler**: Address outcomes no current progress maker serves well.
- Example: "Clear error messages that explain how to fix" (currently weak everywhere)

**Consolidator**: Replace multiple partial solutions with one complete one.
- Example: "One tool that combines syntax, SHACL, and CI-ready output"

**Complementer**: Work alongside existing progress makers.
- Example: "Pre-commit hook that uses existing IDE and feeds CI"

**Disruptor**: Decisively surpass all existing options.
- Example: "10x faster than anything else, with AI-powered fix suggestions"

**Segment Focus**: Serve a specific circumstance better than anyone.
- Example: "Best-in-class pre-commit experience, leave CI to others"

Choose a position and commit to it. Trying to be everything to everyone results in mediocrity.

---

## The Non-Consumption Challenge

Non-consumption deserves special attention. When customers choose to tolerate the problem, it signals:

### The Struggle Isn't Painful Enough

If people live with occasional errors without seeking solutions, either:
- The job isn't important enough
- The consequences aren't severe enough
- The pain hasn't crossed the action threshold

**Implication**: You may need to increase awareness of the problem, not just offer a solution.

### All Solutions Are Too Costly

If people would love to solve the problem but don't:
- Learning curves are too steep
- Integration effort is too high
- Monetary cost is prohibitive
- Time investment isn't worthwhile

**Implication**: Your differentiator might be accessibility, not capability.

### The Workaround Is Good Enough

If people's informal solutions work acceptably:
- You need to be significantly better, not just different
- Or you need to reduce friction even further

**Implication**: Measure against the workaround, not against nothing.

### Investigating Non-Consumption

Ask:
- "Why aren't you using any validation tool?"
- "What would have to be true for you to use one?"
- "What's the worst thing that happens when errors slip through?"
- "If I gave you a perfect tool for free right now, would you use it?"

The answers reveal whether to build, and what would make the difference.

---

## Case Study: The Ignored Solution

A team built a comprehensive RDF validation library. Technically superior: faster than alternatives, more comprehensive checks, better error messages.

Adoption: near zero.

Why? They hadn't studied progress makers.

**What they discovered (too late):**

1. **IDE linting was "good enough"**: Developers caught most syntax errors while editing. The remaining errors were rare.

2. **CI pipeline was the safety net**: For the rare errors that slipped through, CI caught them. Yes, it was slow feedback, but it was automatic.

3. **The "tool gap" didn't hurt**: Between IDE and CI, most errors were caught. The gap—errors that passed IDE but failed CI—wasn't painful enough.

4. **The adoption cost was high**: Using the new library required installing dependencies, configuring it, learning the API, integrating with workflows.

The library was better, but not *enough* better to justify switching.

**The pivot:**

They stopped positioning as a replacement and started positioning as a complement:

- **Pre-commit hook**: "Catch CI errors before you wait for CI"
- **Zero-config default**: Works out of the box with sensible settings
- **Familiar output**: Same format as their linter
- **Escape hatch**: `--skip-validation` for when you need it

Now the pitch was: "Keep your IDE linting. Keep your CI. Add this one hook to avoid the 5-minute CI round-trip when you have a typo."

Adoption increased dramatically.

---

## Case Study: Learning from Workarounds

Another team noticed developers doing something strange: before committing, they'd open a separate terminal and run a cryptic one-liner that piped the output to `head -1`.

Investigation revealed:
- They were running the official validation tool
- But the output was 50+ lines of verbose diagnostics
- They only cared about pass/fail
- The one-liner extracted just the summary line

The workaround revealed the real job: "Tell me quickly if it's okay."

The official tool was designed for the debug circumstance (detailed output). But most usage was the pre-commit circumstance (fast yes/no).

**The fix:**

Added a `--quiet` mode that gave one-line output. Made it the default for the pre-commit hook.

Usage of the workaround dropped to zero. The official tool now served both circumstances.

The workaround was a gift—it revealed what users actually needed.

---

## Representing Progress Makers in RDF

Progress makers can be formally captured in specifications:

```turtle
@prefix jtbd: <http://example.org/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Progress maker definitions
jtbd:IDELinting a jtbd:ProgressMaker ;
    rdfs:label "IDE Linting (VS Code)"@en ;
    jtbd:type jtbd:FormalTool ;
    jtbd:description "Real-time syntax error highlighting in editor"@en ;

    # Outcomes addressed
    jtbd:addressesOutcome jtbd:MinimizeDetectionTime ;
    jtbd:addressesOutcome jtbd:MaximizeErrorClarity ;
    jtbd:outcomeStrength jtbd:MinimizeDetectionTime, "high" ;
    jtbd:outcomeStrength jtbd:MaximizeErrorClarity, "medium" ;

    # Characteristics
    jtbd:strength "Instant feedback, in-context, low cognitive load"@en ;
    jtbd:limitation "Syntax only, VS Code only, misses edge cases"@en ;
    jtbd:circumstanceFit jtbd:DuringEditingCircumstance ;
    jtbd:adoptionReason "Pre-installed, zero config, familiar"@en ;
    jtbd:switchingCost "low" ;

    jtbd:concernsJob jtbd:ValidateOntologyJob .

jtbd:ManualInspection a jtbd:ProgressMaker ;
    rdfs:label "Manual inspection"@en ;
    jtbd:type jtbd:ManualProcess ;
    jtbd:description "Visual review of code before commit"@en ;

    jtbd:addressesOutcome jtbd:MinimizeDetectionTime ;
    jtbd:outcomeStrength jtbd:MinimizeDetectionTime, "low" ;

    jtbd:strength "Always available, catches nuance humans see"@en ;
    jtbd:limitation "Slow, unreliable, fatiguing"@en ;
    jtbd:circumstanceFit jtbd:LowVolumeCircumstance ;
    jtbd:adoptionReason "No setup required"@en ;
    jtbd:switchingCost "none" ;

    jtbd:concernsJob jtbd:ValidateOntologyJob .

jtbd:NonConsumption a jtbd:ProgressMaker ;
    rdfs:label "Non-consumption (tolerating errors)"@en ;
    jtbd:type jtbd:NonConsumption ;
    jtbd:description "Choosing to live with occasional validation failures"@en ;

    jtbd:strength "Zero effort, no adoption cost"@en ;
    jtbd:limitation "Errors escape, accumulate, cause problems later"@en ;
    jtbd:adoptionReason "Insufficient pain, all solutions too costly"@en ;

    jtbd:concernsJob jtbd:ValidateOntologyJob .

# Your capability's positioning
jtbd:SpecKitValidate a jtbd:Capability ;
    rdfs:label "spec-kit validate"@en ;
    jtbd:positioning jtbd:GapFiller ;
    jtbd:differentiator "Fast pre-commit validation with clear, actionable error messages"@en ;

    jtbd:complementsProgressMaker jtbd:IDELinting ;
    jtbd:complementsProgressMaker jtbd:CIPipeline ;
    jtbd:replacesProgressMaker jtbd:ManualInspection ;
    jtbd:replacesProgressMaker jtbd:CustomScript ;

    jtbd:targetCircumstance jtbd:PreCommitCircumstance ;

    jtbd:addressesOutcome jtbd:MinimizeDetectionTime ;
    jtbd:addressesOutcome jtbd:MaximizeErrorClarity ;
    jtbd:addressesOutcome jtbd:MinimizeErrorsReachingCI .
```

### Querying Progress Makers

With progress makers in RDF, you can query them:

```sparql
# Find all progress makers for a job
SELECT ?maker ?label ?type
WHERE {
    ?maker a jtbd:ProgressMaker ;
           rdfs:label ?label ;
           jtbd:type ?type ;
           jtbd:concernsJob jtbd:ValidateOntologyJob .
}

# Find outcomes not well addressed by any progress maker (gaps)
SELECT ?outcome ?label
WHERE {
    ?outcome a jtbd:Outcome ;
             rdfs:label ?label ;
             jtbd:concernsJob jtbd:ValidateOntologyJob .

    FILTER NOT EXISTS {
        ?maker jtbd:addressesOutcome ?outcome ;
               jtbd:outcomeStrength ?outcome, ?strength .
        FILTER (?strength IN ("high", "excellent"))
    }
}

# Find what a new capability would complement vs replace
SELECT ?complemented ?replaced
WHERE {
    jtbd:SpecKitValidate jtbd:complementsProgressMaker ?complemented .
    OPTIONAL { jtbd:SpecKitValidate jtbd:replacesProgressMaker ?replaced . }
}
```

---

## The Progress Maker Landscape Canvas

Use this framework to visualize the landscape:

```
┌─────────────────────────────────────────────────────────────────────┐
│                   PROGRESS MAKER LANDSCAPE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  JOB: Validate RDF before committing                                │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ HIGH SATISFACTION                                              │ │
│  │                                                                │ │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │ │
│  │   │ IDE Linting │  │ CI Pipeline │  │ Peer Review │          │ │
│  │   │ (editing)   │  │ (pre-merge) │  │ (shared)    │          │ │
│  │   └─────────────┘  └─────────────┘  └─────────────┘          │ │
│  │                                                                │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │                                                                │ │
│  │   ┌─────────────┐  ┌─────────────┐                            │ │
│  │   │ rapper CLI  │  │ Custom      │  GAP: Pre-commit          │ │
│  │   │ (manual)    │  │ Script      │  with clear feedback       │ │
│  │   └─────────────┘  └─────────────┘                            │ │
│  │                                                                │ │
│  ├────────────────────────────────────────────────────────────────┤ │
│  │ LOW SATISFACTION                                               │ │
│  │                                                                │ │
│  │   ┌─────────────┐  ┌─────────────┐                            │ │
│  │   │ Manual      │  │ Non-        │                            │ │
│  │   │ Inspection  │  │ Consumption │                            │ │
│  │   └─────────────┘  └─────────────┘                            │ │
│  │                                                                │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                                                                     │
│  OPPORTUNITY: Fill the pre-commit gap between IDE and CI           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Checklist: Have You Understood Progress Makers?

Before proceeding to design, verify:

### Enumeration
- [ ] I have listed all formal tools used for this job
- [ ] I have identified shadow tools and scripts
- [ ] I have understood manual processes
- [ ] I have discovered workarounds
- [ ] I have investigated non-consumption

### Profiling
- [ ] I have profiled each progress maker's strengths and limitations
- [ ] I have understood which outcomes each addresses
- [ ] I have mapped circumstance fit for each
- [ ] I have assessed adoption reasons and switching costs

### Analysis
- [ ] I have created an outcome-to-progress-maker matrix
- [ ] I have identified gaps (outcomes not well-served)
- [ ] I have identified saturation (outcomes over-served)
- [ ] I have understood the adoption barriers

### Positioning
- [ ] I have chosen a positioning (gap filler, consolidator, complementer, disruptor, segment focus)
- [ ] I know which progress makers I complement vs. replace
- [ ] I have realistic expectations for adoption

If any of these remain unclear, invest more time in understanding before building.

---

## Resulting Context

After applying this pattern, you have:

- A map of existing progress makers
- Understanding of what's working and what's not
- Clear positioning for your capability
- Realistic expectations for adoption
- Insight into adoption barriers

This understanding shapes:
- **[8. Competing Solutions](./competing-solutions.md)** — What you're up against
- **[7. Anxieties and Habits](./anxieties-and-habits.md)** — Current solutions create habits
- **[19. Acceptance Criterion](../specification/acceptance-criterion.md)** — You must outperform the status quo

---

## Related Patterns

### Builds on:

**[5. Outcome Desired](./outcome-desired.md)** — Progress makers address outcomes.

### Informs:

**[8. Competing Solutions](./competing-solutions.md)** — Progress makers are competing solutions.

### Shapes:

**[17. Domain-Specific Language](../specification/domain-specific-language.md)** — DSL must fit existing progress makers.

### Affects:

**[7. Anxieties and Habits](./anxieties-and-habits.md)** — Progress makers shape habits.

---

## Philosophical Foundations

> *"People hire products and services to get jobs done. If you can understand the job, you can get it done better than anyone else."*
>
> — Clayton Christensen

But first, understand how they're currently getting it done. Even imperfectly. Even with workarounds. Even by tolerating the problem.

Progress makers represent human ingenuity. People don't wait passively for solutions—they create them. Spreadsheets become databases. Scripts become tools. Workarounds become workflows.

Respect these solutions. Learn from them. Your capability doesn't replace human ingenuity—it channels it more effectively.

> *"The best way to predict the future is to invent it."*
>
> — Alan Kay

But the best way to invent the right future is to understand the present first.

---

## Exercise: Map Your Progress Makers

Before designing your next capability, complete this exercise:

1. **Enumerate**: List all progress makers for your job
2. **Profile**: Document each one's characteristics
3. **Map**: Create an outcome-to-progress-maker matrix
4. **Analyze**: Identify gaps and saturation
5. **Position**: Choose your positioning strategy

Only after completing this exercise should you proceed to understand **[Anxieties and Habits](./anxieties-and-habits.md)**.

---

## Further Reading

- Christensen, Clayton. *Competing Against Luck* (2016) — The role of hiring and firing products.
- Moesta, Bob. *Demand-Side Sales 101* (2020) — Understanding how customers make progress.
- Moore, Geoffrey. *Crossing the Chasm* (2014) — Positioning in competitive landscapes.
- Ulwick, Tony. *Jobs to Be Done: Theory to Practice* (2016) — Systematic job and solution analysis.

---

Your capability enters a world that already has solutions. Understand those solutions, and you'll understand how to offer something better.
