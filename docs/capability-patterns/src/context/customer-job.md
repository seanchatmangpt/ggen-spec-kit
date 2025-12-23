# 2. Customer Job

★★

*People don't want products or features. They "hire" solutions to make progress in their lives. Understanding the job they're trying to get done unlocks the insight needed to create truly valuable capabilities.*

---

Within every **[Living System](./living-system.md)**, people struggle to make progress. They have goals—sometimes explicit, often implicit. They face obstacles. They try various approaches. Sometimes they succeed; often they compromise.

We call this struggle a "job to be done."

A job is not a task on a to-do list. It's not a feature request. It's the underlying progress a person seeks. Consider:

- "I need to validate my RDF file" — This is a task
- "I need to feel confident my ontology is correct before committing" — This is the job

The task is mechanical. The job is human. The task describes *what*. The job reveals *why*.

**The problem: Building capabilities around tasks rather than jobs leads to solutions that address symptoms but miss the underlying need.**

---

**The forces at play:**

- *Customers articulate tasks, not jobs.* They say "I need a button that does X" not "I need to feel confident when Y."

- *Tasks are easier to implement.* A task has clear inputs and outputs. A job requires understanding context, emotion, and motivation.

- *Metrics favor tasks.* You can count button clicks. Measuring progress toward human goals is harder.

- *Jobs remain stable; tasks change.* The job "feel confident my code is correct" has existed for decades. The tasks (manual testing, unit tests, type checkers, AI review) keep evolving.

These forces tempt us to build around tasks. But tasks are symptoms. Jobs are causes. Treat the cause.

---

**Therefore:**

For every capability you consider, dig beneath the task to find the job. Use the Jobs to Be Done framework:

**1. The functional job** — What practical outcome are they trying to achieve?
- "Validate RDF syntax is correct"
- "Find all usages of a deprecated API"

**2. The emotional job** — How do they want to feel?
- "Confident that I won't break anything"
- "Relieved that I caught errors before anyone else"

**3. The social job** — How do they want to be perceived?
- "Seen as thorough and professional"
- "Known as someone who ships quality"

**4. The circumstance** — When and why does this job arise?
- "Before committing to version control"
- "After receiving a feature request from a customer"

Document the job in this structure:

```
When [circumstance]...
I want to [functional job]...
So I can [emotional/social job]...
```

Example:

```
When I've finished editing my RDF ontology,
I want to validate it against the schema,
So I can feel confident it's correct before committing.
```

This job statement becomes the north star for all design decisions. Every feature, every interaction, every error message should help the customer make progress on this job.

---

**Resulting context:**

After applying this pattern, you have:

- A job statement grounded in functional, emotional, and social dimensions
- Understanding of the circumstance that triggers the job
- Clarity about what "progress" means for this customer
- A foundation for evaluating design alternatives

This job understanding enables you to identify **[Outcome Desired](./outcome-desired.md)** and recognize **[Competing Solutions](./competing-solutions.md)**.

---

**Related patterns:**

- *Builds on:* **[1. Living System](./living-system.md)** — Jobs exist within systems
- *Leads to:* **[4. Circumstance of Struggle](./circumstance-of-struggle.md)** — When does this job arise?
- *Leads to:* **[5. Outcome Desired](./outcome-desired.md)** — How will progress be measured?
- *Reveals:* **[7. Anxieties and Habits](./anxieties-and-habits.md)** — What prevents progress?

---

> *"People don't want a quarter-inch drill. They want a quarter-inch hole."*
>
> — Theodore Levitt

Actually, they don't want the hole either. They want the shelf that will hold their books. And beneath that, they want a sense of order in their home. The job runs deep.

---

**Jobs to Be Done in spec-kit:**

In the spec-kit pattern language, customer jobs are encoded in RDF:

```turtle
jtbd:ValidateOntologyJob a jtbd:Job ;
    rdfs:label "Validate RDF Ontology"@en ;
    jtbd:persona jtbd:RDFOntologyDesigner ;
    jtbd:circumstance "Before committing to git"@en ;
    jtbd:functionalJob "Ensure valid RDF/Turtle syntax"@en ;
    jtbd:emotionalJob "Feel confident ontology is correct"@en ;
    jtbd:socialJob "Be seen as thorough designer"@en .
```

This formal encoding enables:
- Automatic generation of job-focused documentation
- SPARQL queries to find features that address a job
- Traceability from capabilities back to customer value

The job is not just a design artifact—it becomes part of the **[Single Source of Truth](../specification/single-source-of-truth.md)**.
