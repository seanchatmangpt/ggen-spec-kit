# How to Use This Pattern Language

## Reading Patterns

A pattern language is not a cookbook. It is a generative grammar—a way of thinking about problems that produces appropriate solutions.

When reading a pattern, do not look for step-by-step instructions. Instead, look for:

1. **The problem as you experience it** — Does this pattern address something you face?
2. **The forces as you feel them** — Do these tensions resonate with your situation?
3. **The solution as a principle** — Not "do this" but "consider this approach"
4. **The connections to other patterns** — What comes before? What comes after?

---

## Navigating the Patterns

The patterns are numbered 1-45, but you need not read them in order. Instead, navigate by need:

### Starting from Scratch

If you're beginning a new capability, start with the Context Patterns:

1. **[Living System](./context/living-system.md)** — Understand what you're part of
2. **[Customer Job](./context/customer-job.md)** — Understand what customers need
3. **[Outcome Desired](./context/outcome-desired.md)** — Define what success looks like

Then move to Specification Patterns:

9. **[Semantic Foundation](./specification/semantic-foundation.md)** — Choose your representation
10. **[Single Source of Truth](./specification/single-source-of-truth.md)** — Establish authority
11. **[Executable Specification](./specification/executable-specification.md)** — Make it precise

### Implementing a Capability

If you have specifications and need implementation, focus on Transformation Patterns:

21. **[Constitutional Equation](./transformation/constitutional-equation.md)** — The fundamental principle
22. **[Normalization Stage](./transformation/normalization-stage.md)** — Validate first
23. **[Extraction Query](./transformation/extraction-query.md)** — Pull data out
24. **[Template Emission](./transformation/template-emission.md)** — Generate artifacts

### Ensuring Quality

If you need confidence in your capability, explore Verification Patterns:

31. **[Test Before Code](./verification/test-before-code.md)** — Define expectations first
34. **[Shape Validation](./verification/shape-validation.md)** — Enforce constraints
35. **[Drift Detection](./verification/drift-detection.md)** — Catch divergence

### Evolving Capabilities

If you have a working capability that needs to grow, study Evolution Patterns:

39. **[Feedback Loop](./evolution/feedback-loop.md)** — Learn from reality
40. **[Outcome Measurement](./evolution/outcome-measurement.md)** — Track progress
42. **[Specification Refinement](./evolution/specification-refinement.md)** — Improve over time

---

## Applying Patterns

When applying a pattern, follow this process:

### 1. Recognize the Problem

The pattern describes a problem that occurs over and over. First, confirm you're facing this problem. Not every pattern applies to every situation.

**Ask yourself:**
- Is this the problem I'm facing?
- Do I feel the forces described?
- Is the context similar to mine?

### 2. Understand the Forces

Forces are the tensions that make the problem difficult. They often pull in opposite directions:

- **Precision vs. Accessibility** — Precise specifications are hard to read
- **Flexibility vs. Constraint** — Too flexible becomes chaotic; too constrained becomes brittle
- **Automation vs. Control** — Automation saves time but reduces oversight

Understanding the forces helps you find the right balance for your situation.

### 3. Apply the Solution Principle

The solution in a pattern is a principle, not a prescription. It tells you *what* to achieve, not *how* to achieve it.

**"Therefore:"** introduces the core solution. Apply it in a way that fits your context.

For example, the Constitutional Equation pattern says:

> *Therefore: Treat all human-readable specifications as generated artifacts from formal semantic definitions.*

This doesn't tell you which tools to use or what file format. It tells you the principle: source of truth is formal; human-readable is generated.

### 4. Complete with Related Patterns

No pattern stands alone. After applying one pattern, you'll discover needs that other patterns address.

The "Related Patterns" section points you toward:
- **Larger patterns** that set context for this one
- **Smaller patterns** that complete this one

---

## Pattern Confidence Ratings

Each pattern has a confidence rating:

### ★★ (Two Stars)

Well-established patterns with substantial evidence of success. These patterns have been applied in multiple contexts with consistent positive results. Use them with confidence.

### ★ (One Star)

Promising patterns with less empirical validation. These patterns represent our best current thinking but have less track record. Apply them thoughtfully and observe results carefully.

---

## Creating Your Own Patterns

As you work with capabilities, you'll discover patterns not in this book. Document them:

### Pattern Template

```markdown
# [Number]. [Pattern Name]

★ or ★★

[Introductory paragraph setting context]

---

**The problem:**

[Bold statement of the recurring problem]

---

**The forces:**

- [Force 1]
- [Force 2]
- [Force 3]

These forces pull in different directions, creating tension.

---

**Therefore:**

[Solution principle that resolves the forces]

[Detailed explanation]

---

**Resulting context:**

After applying this pattern, you will have:
- [Result 1]
- [Result 2]

---

**Related patterns:**

- Larger: [Pattern names that set context]
- Smaller: [Pattern names that complete this one]
```

---

## Common Mistakes

### Mistake 1: Treating Patterns as Rules

Patterns are principles, not rules. The same problem in different contexts may require different solutions inspired by the same pattern.

### Mistake 2: Skipping Context Patterns

Eager teams jump straight to implementation patterns. Without the Context Patterns, you may build the wrong capability—efficiently solving the wrong problem.

### Mistake 3: Applying Patterns in Isolation

Patterns form a language. Applying one pattern without its related patterns creates incomplete solutions. Follow the connections.

### Mistake 4: Over-Patterning

Not every problem needs a pattern. Simple problems deserve simple solutions. Use patterns for recurring, difficult problems with inherent tension.

---

## The Quality Without a Name

Alexander spoke of "the quality without a name"—a quality present in living buildings but absent in dead ones. You know it when you see it: a space that feels right, that invites you in, that works with human nature rather than against it.

Capabilities can have this quality too. A capability with the quality without a name:

- **Feels natural** to use
- **Guides you** toward correct usage
- **Helps you** when things go wrong
- **Grows** gracefully as needs change
- **Maintains** its integrity over time

The patterns in this book won't guarantee this quality. But they create conditions where it can emerge. They help you understand the forces at play, resolve tensions thoughtfully, and create space for living capabilities.

---

## Next Steps

- Review the **[Pattern Map](./pattern-map.md)** to see how patterns connect
- Start with **[Pattern 1: Living System](./context/living-system.md)** for a foundation
- Or jump to the pattern area most relevant to your current need

The journey of a thousand capabilities begins with understanding a single customer job.
