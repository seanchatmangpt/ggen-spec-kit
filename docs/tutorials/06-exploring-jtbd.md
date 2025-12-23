# Tutorial 6: Exploring the JTBD Framework

**Time to complete:** 15-20 minutes
**Prerequisites:** Complete [Tutorial 2: Create Your First Project](./02-first-project.md)
**What you'll learn:** Introduction to Jobs-to-be-Done framework for feature prioritization

---

## Overview

Jobs-to-be-Done (JTBD) is a framework for understanding what users actually want to accomplish. Rather than building features, we build solutions to user "jobs."

---

## Key Concept: Jobs vs. Features

### Feature-Focused Thinking ❌

```
"Build a photo editing app"
"Add dark mode"
"Create a user profile page"
```

Problem: You might build the wrong things!

### Job-Focused Thinking ✅

```
"Help users organize memories into albums"
"Help users work at night without eye strain"
"Help users manage their presence online"
```

Benefit: You build what users actually need!

---

## Step 1: Understand the JTBD Components

Every job has three parts:

```
Situation → Task → Desired Outcome
```

### Example Job

```
When: I'm reviewing family photos
I want to: Organize them into chronological albums
So that: I can quickly find specific memories
```

Broken down:
- **Situation** (When): Context where the job happens
- **Task** (I want to): The action the user wants to do
- **Outcome** (So that): The result the user desires

---

## Step 2: Define a Job for Your Project

Let's define a job for your project:

Create a file: `docs/JTBD_EXAMPLE.md`

```markdown
# Example Job-to-be-Done

## Job Definition

**Situation:**
When I'm starting a new development project

**Task:**
I want to set up a structured RDF-based specification system

**Desired Outcome:**
So that my code, documentation, and specifications never drift out of sync

---

## Success Criteria

How do we know if this job is done well?

- [ ] Setup takes less than 10 minutes
- [ ] All necessary files are generated automatically
- [ ] Documentation is immediately available
- [ ] First test passes without manual edits
- [ ] Developer understands the structure intuitively

---

## User Story

As a **software developer**
I want to **initialize a project with a complete spec-driven structure**
So that **I can start building with confidence**

---

## Acceptance Criteria

- [ ] `specify init my-project` creates complete directory structure
- [ ] README explains the structure
- [ ] CLAUDE.md provides developer guidance
- [ ] Example specifications are present
- [ ] Example tests pass
```

---

## Step 3: Jobs vs. User Stories vs. Features

Understand the differences:

| Concept | Focuses On | Example |
|---------|-----------|---------|
| **Job** | Outcome user wants | "Organize photos chronologically" |
| **User Story** | User perspective | "As a user, I want to..." |
| **Feature** | How to build it | "Add folder sorting option" |

In JTBD, we start with jobs, then derive user stories and features.

---

## Step 4: Identify Your Project's Jobs

What jobs does your project solve?

For Spec Kit:

1. **Job 1: Start New Project**
   - Situation: Developer starting new project
   - Task: Set up spec-driven development structure
   - Outcome: Complete, ready-to-code environment

2. **Job 2: Document Features**
   - Situation: Developer building new features
   - Task: Specify features in RDF
   - Outcome: Documentation generated automatically

3. **Job 3: Verify Code**
   - Situation: Developer before deployment
   - Task: Run comprehensive tests
   - Outcome: Confidence that code matches specs

---

## Step 5: Measure Job Success with Outcomes

Define measurable outcomes:

```markdown
## Job: Specify Features

### Desired Outcomes

- [ ] Outcome 1: Specification is clear enough for code generation
  - Measure: Code generated with < 5% manual edits

- [ ] Outcome 2: Documentation is automatically generated
  - Measure: No manual documentation writing needed

- [ ] Outcome 3: Tests validate specification compliance
  - Measure: All tests pass with generated code
```

---

## Step 6: Map Features to Jobs

For each feature in your project, ask: "What job does this solve?"

```markdown
## Feature → Job Mapping

### Feature: `ggen sync` command
- **Job:** Transform specifications into code
- **Outcome:** Code matches specifications automatically
- **Success Metric:** 100% test passing rate on generated code

### Feature: SHACL validation
- **Job:** Validate specification correctness
- **Outcome:** Errors caught before code generation
- **Success Metric:** All validation errors caught < 100ms

### Feature: Tera template rendering
- **Job:** Generate code from templates
- **Outcome:** Type-safe code across languages
- **Success Metric:** Generated code has zero runtime errors
```

---

## Step 7: Prioritize Using JTBD

Use JTBD to prioritize what to build:

```markdown
## Priority Matrix

### High Impact, High Effort
- Implement process mining
- Build hyperdimensional computing integration
→ Do these first, they enable future jobs

### High Impact, Low Effort
- Improve error messages
- Add command documentation
→ Do these immediately

### Low Impact, High Effort
- Fancy UI for ontology editor
- Support legacy RDF formats
→ Deprioritize these

### Low Impact, Low Effort
- Minor documentation fixes
- Code style improvements
→ Do these when there's time
```

---

## Step 8: Use JTBD for Feature Decisions

When deciding whether to build a feature, ask:

1. **What job does it help with?**
2. **Does it solve a real user need?**
3. **Can we measure success?**
4. **What's the priority vs. other jobs?**

Example decision:

```
Proposed Feature: "Dark mode for documentation"

Q: What job does it solve?
A: "Help developers work at night without eye strain"

Q: Real user need?
A: Yes, developers work at all hours

Q: How to measure success?
A: Track usage metrics, survey developer satisfaction

Q: Priority?
A: Medium - improves experience but doesn't enable new capabilities
```

---

## Step 9: Document Jobs in Your Project

Create a JTBD documentation file:

```bash
touch docs/JTBD_DECISIONS.md
```

This file should document:
- Jobs your project solves
- Features mapped to jobs
- Success metrics for each job
- Prioritization decisions

---

## Step 10: Continue Learning

Now that you understand JTBD basics, explore:

- **[How-to: Apply JTBD Framework](../guides/jtbd/apply-framework.md)** - Practical implementation
- **[How-to: Measure Outcomes](../guides/jtbd/measure-outcomes.md)** - Define success metrics
- **[Reference: JTBD Framework](../reference/jtbd-framework.md)** - Complete reference
- **[Explanation: Why JTBD](../explanation/why-jtbd-framework.md)** - Deep conceptual understanding

---

## Next Steps

You've learned:
- ✅ What Jobs-to-be-Done means
- ✅ How to define jobs
- ✅ Difference between jobs, stories, and features
- ✅ How to measure success
- ✅ How to prioritize using JTBD

**Continue with:**
- **[Tutorial 7: OpenTelemetry Basics](./07-observability-basics.md)** - Add observability
- **[How-to: Apply JTBD](../guides/jtbd/apply-framework.md)** - Practical application

---

## Summary

Jobs-to-be-Done helps you:
- Understand user needs deeply
- Prioritize the right features
- Measure success objectively
- Build products users actually want

The principle: **Build to accomplish user jobs, not to add features.**

In Spec Kit, you use JTBD to define what specifications to write - focusing on what users need, not implementation details!
