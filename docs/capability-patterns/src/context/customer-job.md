# 2. Customer Job

★★

*People don't want products or features. They "hire" solutions to make progress in their lives. Understanding the job they're trying to get done unlocks the insight needed to create truly valuable capabilities.*

---

## The Fundamental Insight

Within every **[Living System](./living-system.md)**, people struggle to make progress. They have goals—sometimes explicit, often implicit. They face obstacles. They try various approaches. Sometimes they succeed; often they compromise.

We call this struggle a "job to be done."

This phrase comes from Clayton Christensen's Jobs to Be Done (JTBD) framework, one of the most powerful tools for understanding why people adopt solutions. The core insight is simple but profound:

**People don't buy products. They hire them to get a job done.**

When someone buys a drill, they don't want a drill—they want a hole. But even that's not quite right. They don't want a hole—they want to hang a shelf. They don't want a shelf—they want their books organized. They don't want organized books—they want a sense of order and control in their living space.

The job runs deep. And understanding it at the right level unlocks the ability to create solutions that truly matter.

---

## What is a Job?

A job is not a task on a to-do list. It's not a feature request. It's not a requirement in a specification document.

**A job is the underlying progress a person seeks to make in a particular circumstance.**

Consider these contrasts:

| Task | Job |
|------|-----|
| "Validate my RDF file" | "Feel confident my ontology is correct before committing" |
| "Run the test suite" | "Know whether my changes broke anything" |
| "Generate documentation" | "Help future developers understand my code" |
| "Deploy to production" | "Deliver value to users without breaking things" |

The task is mechanical. The job is human. The task describes *what*. The job reveals *why*.

A task can be completed. A job is never fully done—it recurs, evolves, and deepens.

---

## The Problem

**Building capabilities around tasks rather than jobs leads to solutions that address symptoms but miss the underlying need.**

This manifests in many ways:

- The feature that works perfectly but nobody uses
- The tool that solves the stated problem but not the real one
- The automation that saves time on the wrong thing
- The optimization that improves a metric nobody cares about
- The enhancement that adds complexity without adding value

Behind each of these failures lies the same mistake: building for tasks rather than jobs.

When we build for tasks, we get feature creep—endless additions that check boxes without creating progress. When we build for jobs, we get focus—capabilities that help people achieve what they actually care about.

---

## The Three Dimensions of a Job

Every job has three dimensions. Miss any one and you've missed the job.

### 1. The Functional Dimension

What practical outcome is the person trying to achieve?

This is the surface level—what we usually call "requirements." But it's only the beginning.

**Examples of functional jobs:**
- "Validate that my RDF syntax is correct"
- "Find all usages of a deprecated API"
- "Generate test cases from specifications"
- "Track changes across file versions"

The functional job is necessary but not sufficient. Two solutions might solve the same functional job but feel completely different to use—because the emotional and social dimensions differ.

### 2. The Emotional Dimension

How does the person want to feel?

Every job carries emotional weight. People don't just want outcomes—they want to feel certain ways about those outcomes.

**Examples of emotional jobs:**
- "Feel confident that I won't break anything"
- "Feel relieved that I caught errors before anyone else did"
- "Feel proud of the quality of my work"
- "Feel calm knowing the system is watching for problems"

The emotional dimension explains why people sometimes reject technically superior solutions. If a solution makes them feel stupid, anxious, or out of control, they won't use it—even if it works.

### 3. The Social Dimension

How does the person want to be perceived?

We are social creatures. Our jobs often involve our reputation, relationships, and standing in communities.

**Examples of social jobs:**
- "Be seen as thorough and professional"
- "Be known as someone who ships quality"
- "Avoid being blamed when things go wrong"
- "Be recognized as an expert in my domain"

The social dimension explains why people sometimes do things that seem irrational individually. They're optimizing for social outcomes, not just functional ones.

---

## The Circumstance Factor

A job doesn't exist in the abstract. It arises in a specific circumstance—a moment when progress becomes urgent.

**The same underlying job feels different in different circumstances:**

| Job: "Validate my code is correct" | Circumstance Changes Everything |
|------------------------------------|---------------------------------|
| Before committing | Speed matters, brief feedback okay |
| After customer bug report | Thoroughness matters, speed secondary |
| During code review | Clarity matters, must explain to others |
| Before major release | Completeness matters, no shortcuts |

A capability that serves one circumstance may fail another. Understanding circumstance is so important that it has its own pattern: **[4. Circumstance of Struggle](./circumstance-of-struggle.md)**.

---

## The Forces at Play

Several forces make jobs difficult to discover:

### Customers Articulate Tasks, Not Jobs

When you ask someone what they need, they'll describe a task: "I need a button that validates my file." They won't say "I need to feel confident when I commit."

This isn't deception—it's how human minds work. We're conscious of tasks but often unconscious of the deeper jobs they serve. The job is like water to a fish: invisible because it's everywhere.

**Implication**: Don't just listen to what people say. Watch what they do. Dig beneath the surface. Ask "why" repeatedly.

### Tasks Are Easier to Implement

A task has clear inputs and outputs. "Given a file, return valid or invalid." Done.

A job is fuzzy. "Help me feel confident"—what does that even mean technically? How do you measure it? How do you test it?

The temptation is strong to reduce the job to something measurable and implementable. But this reduction often loses the essence.

**Implication**: Resist premature reduction. Stay with the fuzziness long enough to understand its shape.

### Metrics Favor Tasks

Organizations measure what's easy to measure. Button clicks. Response times. Error counts. Feature completion percentages.

These are task metrics. Job metrics—confidence, clarity, relief, trust—are harder to quantify. They get squeezed out of dashboards and OKRs.

**Implication**: Create proxies for job metrics. "Did the user continue to the next step?" can approximate "Did they feel confident?" "Did they undo/retry?" can approximate "Were they confused?"

### Jobs Remain Stable; Tasks Change

This is perhaps the most important insight for long-term capability thinking.

The job "feel confident my code is correct" has existed for as long as there has been code. The tasks serving this job have evolved continuously:
- Manual inspection (1960s)
- Test suites (1970s)
- Type checkers (1980s)
- Static analysis (1990s)
- CI/CD pipelines (2000s)
- AI code review (2020s)

Each new task obsoletes the previous one—but the job remains.

**Implication**: Build capabilities that serve jobs, and they'll remain valuable as technology evolves. Build capabilities that complete tasks, and they'll be replaced when tasks change.

---

## Therefore

**For every capability you consider, dig beneath the task to find the job.**

### The Job Discovery Process

#### Step 1: Start with the Stated Request

Someone says "I need X." This is your raw material. Don't accept or reject it yet—just record it.

*Example: "I need a command that validates my RDF file."*

#### Step 2: Ask "Why?" Multiple Times

The first answer will be superficial. Keep asking.

- "I need to validate my RDF file."
- "Why?" → "To catch syntax errors."
- "Why do you want to catch syntax errors?" → "So they don't break the pipeline."
- "Why does it matter if the pipeline breaks?" → "Because then my changes get rejected."
- "Why does rejection matter?" → "Because I have to fix them and resubmit."
- "What's wrong with that?" → "It's embarrassing and wastes time."

Now we're getting somewhere. The job isn't "validate syntax"—it's "feel confident my work is ready before I submit it."

#### Step 3: Identify the Three Dimensions

Once you've dug deep, explicitly articulate each dimension:

**Functional job**: Ensure my RDF file is syntactically and semantically correct before it enters the shared pipeline.

**Emotional job**: Feel confident that my work is complete and correct. Feel relieved that I caught problems early. Avoid the anxiety of waiting for pipeline results.

**Social job**: Be seen as someone who submits quality work. Avoid the embarrassment of having my changes rejected. Maintain my reputation for thoroughness.

#### Step 4: Map the Circumstances

When does this job arise? Document each circumstance:

**Circumstance 1: Pre-commit**
- Trigger: Finished editing, about to commit
- Emotional state: Eager to close the task, slight anxiety
- Time budget: Seconds
- Consequences of not doing: Risk of pipeline failure, wasted round-trip

**Circumstance 2: Post-error**
- Trigger: Got an error from somewhere, need to diagnose
- Emotional state: Frustrated, problem-solving mode
- Time budget: Minutes
- Consequences of not doing: Problem remains unsolved

**Circumstance 3: Learning mode**
- Trigger: Working with unfamiliar RDF vocabulary
- Emotional state: Curious but uncertain
- Time budget: Flexible
- Consequences of not doing: Incorrect mental model forms

Each circumstance may need different capability support.

#### Step 5: Write the Job Statement

Combine everything into a single statement:

```
When [circumstance]...
I want to [functional job]...
So I can [emotional/social job]...
```

*Example:*

```
When I've finished editing my RDF ontology,
I want to validate it against the schema,
So I can feel confident it's correct before committing.
```

This job statement becomes the north star for all design decisions. Every feature, every interaction, every error message should help the customer make progress on this job.

---

## The Job Map

For complex domains, you may discover multiple related jobs. Map them to understand their relationships.

### The Main Job

The primary progress the customer seeks. This is your focus.

### Related Jobs

Jobs that arise alongside the main job:

**Preparation jobs**: What must happen before the main job?
- "Understand what files to validate"
- "Configure validation rules for my context"

**Execution jobs**: What happens during the main job?
- "Run validation quickly"
- "Get clear feedback on issues"

**Completion jobs**: What happens after the main job?
- "Fix identified issues"
- "Record that validation passed"
- "Share results with team"

**Ancillary jobs**: What related needs exist?
- "Learn the validation tool"
- "Customize validation rules"
- "Integrate validation into workflows"

Each related job might be served by different features of your capability—or might be served better by other tools.

---

## Common Job Discovery Mistakes

### Mistake 1: Accepting the First Answer

Someone says "I need X" and you build X. But X was just the first thing that came to mind—a symptom, not the disease.

**Fix**: Always ask why. Multiple times. Silence is okay—people need time to think.

### Mistake 2: Inferring Jobs from Features

"They use feature X, so they must want Y." But people use features for unexpected reasons. The feature's intended purpose may not match its actual job.

**Fix**: Observe actual usage. Ask about specific instances. "Tell me about the last time you used this."

### Mistake 3: Projecting Your Own Jobs

"I would want X in this situation." But you're not the customer. Your expertise, preferences, and circumstances differ.

**Fix**: Practice beginner's mind. Assume you know nothing. Let the evidence lead.

### Mistake 4: Stopping at Functional Jobs

"They need to validate RDF." Functional jobs are important but incomplete. The emotional and social dimensions determine whether a solution will be adopted and loved.

**Fix**: Always explicitly articulate all three dimensions.

### Mistake 5: Ignoring Circumstance

A job without circumstance is too abstract to design for. "Feel confident" means different things at 9 AM with fresh coffee versus 5 PM on Friday with a deadline.

**Fix**: Document specific circumstances. Design for the moments, not the abstraction.

---

## Jobs to Be Done in RDF Specification

In the spec-kit pattern language, customer jobs are encoded formally in RDF. This enables:

- Machine-readable job documentation
- SPARQL queries to find features serving jobs
- Traceability from capabilities back to customer value
- Automated generation of job-focused documentation

### RDF Representation

```turtle
@prefix jtbd: <http://example.org/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# The persona who has this job
jtbd:RDFOntologyDesigner a jtbd:Persona ;
    rdfs:label "RDF Ontology Designer"@en ;
    jtbd:description "A developer who creates and maintains RDF vocabularies and ontologies"@en ;
    jtbd:skills "RDF, SPARQL, ontology design"@en ;
    jtbd:frustrations "Syntax errors caught late, unclear error messages"@en .

# The job itself
jtbd:ValidateOntologyJob a jtbd:Job ;
    rdfs:label "Validate RDF Ontology"@en ;
    jtbd:persona jtbd:RDFOntologyDesigner ;
    jtbd:functionalJob "Ensure valid RDF/Turtle syntax and SHACL compliance"@en ;
    jtbd:emotionalJob "Feel confident ontology is correct before sharing"@en ;
    jtbd:socialJob "Be seen as a thorough, professional designer"@en ;
    jtbd:hasCircumstance jtbd:PreCommitCircumstance, jtbd:DebugCircumstance ;
    jtbd:hasOutcome jtbd:MinimizeValidationTime, jtbd:MinimizeErrors .

# A circumstance when this job arises
jtbd:PreCommitCircumstance a jtbd:Circumstance ;
    rdfs:label "Pre-commit validation"@en ;
    jtbd:trigger "Developer finishes changes, initiates commit"@en ;
    jtbd:emotionalState "Eager to close task, slightly anxious"@en ;
    jtbd:timeBudget "PT2S"^^xsd:duration ;
    jtbd:concernsJob jtbd:ValidateOntologyJob .

# An outcome that measures progress on this job
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    rdfs:label "Minimize validation time"@en ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:object "discovering syntax errors" ;
    jtbd:baseline "PT5M"^^xsd:duration ;
    jtbd:target "PT5S"^^xsd:duration ;
    jtbd:concernsJob jtbd:ValidateOntologyJob .
```

### SPARQL Queries Against Jobs

With jobs in RDF, you can query them:

```sparql
# Find all outcomes for a specific job
SELECT ?outcome ?label ?direction ?metric
WHERE {
    ?outcome jtbd:concernsJob jtbd:ValidateOntologyJob ;
             rdfs:label ?label ;
             jtbd:direction ?direction ;
             jtbd:metric ?metric .
}

# Find jobs with high importance but low satisfaction (opportunities)
SELECT ?job ?label
WHERE {
    ?job a jtbd:Job ;
         rdfs:label ?label .
    ?outcome jtbd:concernsJob ?job ;
             jtbd:importance "high" ;
             jtbd:currentSatisfaction "low" .
}
```

### Generated Documentation

From the RDF specification, templates can generate documentation:

```markdown
## Job: Validate RDF Ontology

**Persona**: RDF Ontology Designer

### What they're trying to do (functional)
Ensure valid RDF/Turtle syntax and SHACL compliance

### How they want to feel (emotional)
Feel confident ontology is correct before sharing

### How they want to be seen (social)
Be seen as a thorough, professional designer

### When this job arises
- Pre-commit validation: When developer finishes changes and initiates commit
- Debugging session: When a problem is discovered and must be diagnosed

### Success metrics
- Minimize time to discover errors: from 5 minutes to 5 seconds
- Minimize number of undetected errors: from ~3/file to 0
```

The job is not just a design artifact—it becomes part of the **[Single Source of Truth](../specification/single-source-of-truth.md)**.

---

## Case Study: The Drill That Wasn't

A team was asked to build "faster validation." They optimized the hell out of their validation logic. Execution time dropped from 5 seconds to 0.5 seconds.

Usage didn't increase.

Why? Because the job wasn't "validate faster." The job was "feel confident before committing." And the existing tool, despite being slower, gave clear, actionable feedback. The new tool was fast but cryptic.

When they discovered the real job, they:
1. Added clear error messages explaining *what* was wrong and *how* to fix it
2. Added a confidence indicator: "3 issues found (2 warnings, 1 error)"
3. Integrated with the editor to show problems in context

Validation time was still 0.5 seconds—but now usage soared. Because now it served the job.

---

## Case Study: The Milkshake Story

Clayton Christensen's famous milkshake study illustrates job discovery perfectly:

A fast-food chain wanted to sell more milkshakes. Traditional market research (demographics, preferences, flavors) yielded only incremental improvements.

Then researchers watched *when* and *why* people bought milkshakes. They discovered two completely different jobs:

**Morning commuters** bought thick milkshakes to:
- Keep themselves occupied during a boring drive (functional)
- Feel satisfied until lunch (functional)
- Enjoy a small indulgence to start the day (emotional)

The "competitors" weren't other milkshakes—they were bagels, bananas, and coffee.

**Evening parents** bought milkshakes to:
- Treat their children after dinner (functional)
- Feel like a good parent (emotional)
- Connect with their kids through a shared experience (social)

The "competitors" were ice cream, desserts, and trips to the toy store.

Same product. Completely different jobs. Completely different design implications.

**Morning optimization**: Thicker consistency (lasts the drive), faster pickup, unique flavors (variety for daily commuters).

**Evening optimization**: Smaller sizes (parents felt guilty about big ones), kid-friendly flavors, easy-to-share packaging.

One milkshake couldn't serve both jobs well. Understanding the jobs revealed why, and what to do about it.

---

## From Job to Capability

Once you understand the job, capability design becomes clearer:

### Every Feature Should Trace to Job Progress

Ask of every proposed feature: "How does this help the customer make progress on their job?"

If you can't answer clearly, reconsider the feature.

### Trade-offs Are Job Trade-offs

When facing design trade-offs, evaluate them through job lenses:
- "Fast but cryptic" fails the emotional job (confidence requires understanding)
- "Thorough but slow" may fail certain circumstances (pre-commit needs speed)
- "Powerful but complex" may fail the social job (looking foolish while learning)

### Error Messages Are Job Moments

When something goes wrong, the customer's job isn't to "read an error"—it's to "understand what happened and how to fix it." Design error messages as progress enablers.

### Documentation Is Job Onboarding

Documentation doesn't exist to describe features. It exists to help customers make progress on their jobs. Organize docs around jobs, not features.

---

## Resulting Context

After applying this pattern, you have:

- A job statement grounded in functional, emotional, and social dimensions
- Understanding of the circumstances that trigger the job
- Clarity about what "progress" means for your customer
- A foundation for evaluating design alternatives
- A north star for feature decisions

This job understanding enables you to identify:
- **[5. Outcome Desired](./outcome-desired.md)** — How will progress be measured?
- **[8. Competing Solutions](./competing-solutions.md)** — What else "competes" for this job?
- **[7. Anxieties and Habits](./anxieties-and-habits.md)** — What prevents progress?

---

## Related Patterns

### Builds on:

**[1. Living System](./living-system.md)** — Jobs exist within systems. Understanding the system reveals the jobs.

### Leads to:

**[4. Circumstance of Struggle](./circumstance-of-struggle.md)** — When does this job arise?

**[5. Outcome Desired](./outcome-desired.md)** — How will progress be measured?

### Reveals:

**[7. Anxieties and Habits](./anxieties-and-habits.md)** — What prevents progress on this job?

---

## Philosophical Foundations

> *"People don't want a quarter-inch drill. They want a quarter-inch hole."*
>
> — Theodore Levitt

Actually, they don't want the hole either. They want the shelf that will hold their books. And beneath that, they want a sense of order in their home. And beneath that, they want to feel in control of their life.

The job runs deep. The art is knowing when to stop digging—when you've reached the level that's actionable for your capability.

> *"If I had asked people what they wanted, they would have said faster horses."*
>
> — (Attributed to) Henry Ford

People can articulate tasks but rarely jobs. The automobile didn't serve the job "faster horse." It served the job "get from here to there faster, more reliably, with less maintenance." That job was invisible to horse users—until a solution appeared that served it better.

Your job as a capability creator is to see the invisible. To understand what people are really trying to achieve, even when they can't articulate it. And then to build something that helps them achieve it—something they didn't know to ask for but immediately recognize as exactly what they needed.

---

## Exercise: Discover a Job

Before designing your next capability, complete this exercise:

1. **Identify a stated request**: What are people asking for?

2. **Ask "why" five times**: Dig beneath the surface.

3. **Articulate the three dimensions**:
   - Functional job: What practical outcome?
   - Emotional job: How do they want to feel?
   - Social job: How do they want to be perceived?

4. **Document the circumstances**: When does this job arise?

5. **Write the job statement**:
   ```
   When [circumstance]...
   I want to [functional job]...
   So I can [emotional/social job]...
   ```

6. **Validate with real people**: Share your job statement. Does it resonate?

Only after completing this exercise should you proceed to design features.

---

## Further Reading

- Christensen, Clayton. *Competing Against Luck* (2016) — The definitive JTBD book from the framework's creator.
- Kalbach, Jim. *The Jobs To Be Done Playbook* (2019) — Practical techniques for applying JTBD.
- Moesta, Bob. *Demand-Side Sales 101* (2020) — JTBD applied to understanding demand.
- Ulwick, Tony. *Jobs to Be Done: Theory to Practice* (2016) — The Outcome-Driven Innovation methodology.

---

People don't want your capability. They want progress. Understand the progress they seek, and you'll build something that matters.
