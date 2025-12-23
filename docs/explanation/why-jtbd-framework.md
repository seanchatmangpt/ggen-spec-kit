# Explanation: Why Jobs-to-be-Done Framework?

**Time to understand:** 15-20 minutes

## The Problem with Features

### Feature-Focused Thinking

```
What should we build?
→ "Add dark mode"
→ "Create mobile app"
→ "Build GraphQL API"

Problem: You might build the wrong thing!
```

### Job-Focused Thinking

```
What do users need to accomplish?
→ "Work at night without eye strain"
→ "Access system from anywhere"
→ "Query data efficiently"

Benefit: You build what users actually need!
```

## What is a Job?

A **job** is something a user needs to accomplish.

Not a feature. Not a product. **A goal or outcome.**

### Examples

❌ **Feature:** "Add calendar sync"
✅ **Job:** "Stay coordinated with my team's schedule"

❌ **Feature:** "Mobile app"
✅ **Job:** "Access work from anywhere"

❌ **Feature:** "Notifications"
✅ **Job:** "Know immediately when something needs my attention"

## Jobs Have Three Parts

```
Situation + Task + Outcome = Job
```

### Example: Spec Kit Job

```
Situation: When I'm building software
Task: I want to define features in RDF
Outcome: So my code, tests, and docs are always in sync
```

Breaking it down:
- **Situation:** Starting a project
- **Task:** Define specs formally
- **Outcome:** Perfect synchronization

## Why JTBD is Better

### Traditional Feature Prioritization

```
Feature A: High effort, unclear value
Feature B: Low effort, unclear value
Feature C: Medium effort, unknown impact

How to prioritize? 🤷
```

### JTBD Prioritization

```
Job 1: Help users start quickly
  - Impact: HIGH (99% of users)
  - Effort: MEDIUM
  - Priority: DO FIRST ✓

Job 2: Help users add features
  - Impact: HIGH (80% of users)
  - Effort: MEDIUM
  - Priority: DO SECOND ✓

Job 3: Support exotic languages
  - Impact: LOW (5% of users)
  - Effort: HIGH
  - Priority: DO LATER
```

**Clear prioritization based on actual user value!**

## JTBD Benefits

### 1. Focus on User Value
- Avoid building features nobody needs
- Measure actual impact
- Understand what matters

### 2. Better Prioritization
- Clear criteria (impact vs. effort)
- Data-driven decisions
- Alignment with user needs

### 3. Better Communication
- Developers understand purpose
- Teams align on goals
- Stakeholders see value

### 4. Measurable Success
- Define outcomes
- Track metrics
- Improve continuously

## From Jobs to Features

```
Job: "Help users start projects quickly"
  ↓ (What features enable this?)
Features:
  - Project templates
  - Setup wizard
  - Example code
  - Quick start guide
  - One-command init
```

**Jobs drive features, not the other way around.**

## Example: Spec Kit

### Jobs Spec Kit Solves

**Job 1:** Prevent documentation drift
```
Situation: Building features
Task: Keep specs, code, and docs in sync
Outcome: No drift, perfect alignment

Solutions:
- Generate code from specs
- Generate docs from specs
- Tests validate specs
```

**Job 2:** Enable safe refactoring
```
Situation: Changing existing code
Task: Know code still matches specification
Outcome: Confident refactoring

Solutions:
- Tests verify specs
- SHACL validation catches errors
- Receipts prove alignment
```

**Job 3:** Understand design decisions
```
Situation: Joining team or reviewing code
Task: Know why code is structured this way
Outcome: Rapid understanding

Solutions:
- RDF makes intentions explicit
- Specs document decisions
- Architecture patterns are clear
```

## Measurement

For each job, define outcomes:

```
Job: Help users start quickly

Outcome 1: Setup completes in < 15 minutes
  - Measure: Time to run first command
  - Target: < 15 min
  - Current: 20 min → Improve!

Outcome 2: User understands structure
  - Measure: Can explain three-tier arch
  - Target: 80% can explain
  - Current: 60% → Need better docs

Outcome 3: First project works without errors
  - Measure: Zero manual fixes needed
  - Target: 99%
  - Current: 95% → Improve error messages
```

## See Also
- [How-to: Apply JTBD Framework](../guides/jtbd/apply-framework.md)
- [Tutorial 6: Exploring JTBD](../tutorials/06-exploring-jtbd.md)
- [Reference: JTBD Framework](../reference/jtbd-framework.md)
