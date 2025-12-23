# Tutorials - Learn Spec Kit Step by Step

Welcome to the Spec Kit tutorials! These are **learning-oriented** guides designed to teach you the fundamentals through hands-on practice.

---

## 📚 Tutorial Sequence

Follow these tutorials **in order** for a complete learning experience:

### 1. [Getting Started](./01-getting-started.md)
**Time:** 10-15 minutes | **Level:** Beginner

Learn what Spec Kit is and install the tools you need.

**What you'll learn:**
- What is RDF-first specification-driven development?
- How to install Specify CLI
- The three core concepts (RDF-first, three-tier, transformation)
- How to verify your system is ready

**Prerequisites:** None - start here!

---

### 2. [Create Your First Project](./02-first-project.md)
**Time:** 15-20 minutes | **Level:** Beginner

Initialize your first Spec Kit project and understand its structure.

**What you'll learn:**
- How to initialize a new project with `specify init`
- The directory structure and what each folder means
- Where to write RDF specifications
- How the RDF-first workflow works

**Prerequisites:** Tutorial 1

---

### 3. [Write Your First RDF Specification](./03-first-rdf-spec.md)
**Time:** 20-25 minutes | **Level:** Beginner

Write your first RDF specification and see it transform into code.

**What you'll learn:**
- Turtle syntax basics for RDF
- How to define a CLI command in RDF
- How `ggen sync` transforms RDF into Python code
- How to implement the generated skeleton
- The constitutional equation in action: `spec.md = μ(feature.ttl)`

**Prerequisites:** Tutorial 2

---

### 4. [Your First Test](./04-first-test.md)
**Time:** 15-20 minutes | **Level:** Beginner

Write unit tests and end-to-end tests for your code.

**What you'll learn:**
- How to write unit tests with pytest
- How to write end-to-end tests for CLI commands
- How to run tests and check coverage
- Test-driven development practices

**Prerequisites:** Tutorial 3

---

### 5. [Running ggen Sync](./05-ggen-sync-first-time.md)
**Time:** 10-15 minutes | **Level:** Beginner

Understand how the ggen transformation pipeline works.

**What you'll learn:**
- What `ggen sync` does and how to run it
- The five transformation stages (μ₁ through μ₅)
- How to verify transformations with SHA256 receipts
- The Edit RDF → ggen sync → Implement cycle

**Prerequisites:** Tutorial 3

---

### 6. [Exploring JTBD Framework](./06-exploring-jtbd.md)
**Time:** 15-20 minutes | **Level:** Intermediate

Learn how to prioritize features using Jobs-to-be-Done framework.

**What you'll learn:**
- What is Jobs-to-be-Done (JTBD)?
- Jobs vs. features vs. user stories
- How to define measurable outcomes
- How to prioritize using JTBD

**Prerequisites:** Tutorial 2

---

### 7. [OpenTelemetry Basics](./07-observability-basics.md)
**Time:** 15-20 minutes | **Level:** Intermediate

Add observability to your code with OpenTelemetry.

**What you'll learn:**
- What observability means (traces, metrics, logs)
- How to instrument your code with `@timed` and `span()`
- How to export traces to Jaeger
- How to add metrics and custom logging

**Prerequisites:** Tutorial 3

---

## 🎯 Learning Paths

### Path 1: Complete Beginner
Follow tutorials **1 → 2 → 3 → 4 → 5** for a complete introduction to Spec Kit fundamentals.

**Time:** ~75 minutes

**Outcome:** You can create a project, write RDF specifications, and test your code.

### Path 2: Intermediate Developer
Start at tutorial **2**, then follow **3 → 4 → 5**, then explore **6** and **7**.

**Time:** ~80 minutes

**Outcome:** You understand the complete workflow and can apply advanced concepts.

### Path 3: Operations/DevOps Focus
Start at tutorial **5**, then explore:
- [How-to: Run ggen Sync](../guides/operations/run-ggen-sync.md)
- [How-to: Setup CI/CD](../guides/deployment/setup-ci-cd.md)
- [How-to: Setup OpenTelemetry](../guides/observability/setup-otel.md)

**Time:** ~40 minutes

**Outcome:** You can automate Spec Kit workflows in CI/CD pipelines.

---

## 🔍 What Makes These Tutorials Special

### ✅ Hands-On
Every tutorial includes **practical exercises** you can do immediately.

### ✅ Cumulative
Each tutorial builds on the previous one, so you learn progressively.

### ✅ Self-Contained
Each tutorial is complete and can be skipped (though earlier ones are recommended).

### ✅ No Prerequisites
Start with zero knowledge - we explain everything!

---

## ⚡ Quick Navigation

| I want to... | Start here |
|-----------|-----------|
| Learn Spec Kit from scratch | [Tutorial 1: Getting Started](./01-getting-started.md) |
| Create my first project | [Tutorial 2: Create Your First Project](./02-first-project.md) |
| Write specifications | [Tutorial 3: Write RDF Specifications](./03-first-rdf-spec.md) |
| Test my code | [Tutorial 4: Your First Test](./04-first-test.md) |
| Understand code generation | [Tutorial 5: Running ggen Sync](./05-ggen-sync-first-time.md) |
| Prioritize features | [Tutorial 6: Exploring JTBD](./06-exploring-jtbd.md) |
| Monitor my application | [Tutorial 7: OpenTelemetry Basics](./07-observability-basics.md) |

---

## 📖 After the Tutorials

Once you've completed these tutorials, explore:

### [How-to Guides](../guides/)
Goal-oriented guides for specific tasks:
- Adding CLI commands
- Writing complete specifications
- Running tests
- Troubleshooting issues
- And more...

### [Reference Documentation](../reference/)
Authoritative technical information for lookup:
- CLI command reference
- RDF ontology specification
- Configuration options
- API documentation

### [Explanations](../explanation/)
Understanding-oriented content about concepts:
- Why RDF-first development?
- How does the three-tier architecture work?
- What's the constitutional equation?
- Why Jobs-to-be-Done?

---

## 🆘 Troubleshooting

### I'm stuck on a tutorial
- Reread the step carefully
- Check the "Troubleshooting" section at the end of each tutorial
- See if a [How-to Guide](../guides/) covers your issue
- Look at [Reference Documentation](../reference/) for more details

### I want to skip ahead
- You can skip to Tutorial 5-7 if you're an experienced developer
- But we recommend going through all tutorials for completeness
- Even experienced developers often learn new things!

### I want more practice
- Modify the examples to practice
- Create your own small project
- Experiment with the code
- Try to break things and fix them!

---

## ✅ Learning Checklist

Use this checklist to track your progress:

- [ ] Tutorial 1: Getting Started - Completed ✓
- [ ] Tutorial 2: Create Your First Project - Completed ✓
- [ ] Tutorial 3: Write Your First RDF Specification - Completed ✓
- [ ] Tutorial 4: Your First Test - Completed ✓
- [ ] Tutorial 5: Running ggen Sync - Completed ✓
- [ ] Tutorial 6: Exploring JTBD - Completed ✓
- [ ] Tutorial 7: OpenTelemetry Basics - Completed ✓
- [ ] Ready for [How-to Guides](../guides/) - ✓

---

## 💡 Learning Tips

1. **Type out the examples** - Don't copy-paste! Typing helps learning.
2. **Modify examples** - Change values and observe what happens.
3. **Ask questions** - If something doesn't make sense, dig deeper.
4. **Take breaks** - Learning complex concepts takes time.
5. **Practice** - Repetition is key to understanding.
6. **Explain to others** - Teaching helps solidify knowledge.

---

## 🚀 Next Steps

Ready to go deeper? Choose your path:

### Want to build real projects?
→ Start with [How-to Guides](../guides/)

### Want to understand the concepts?
→ Explore [Explanations](../explanation/)

### Want detailed technical information?
→ Check [Reference Documentation](../reference/)

---

## Feedback

Have feedback on these tutorials? Found an error? Have a suggestion?

- Open an issue: https://github.com/seanchatmangpt/ggen-spec-kit/issues
- Suggest improvements in discussions
- Share your learning experience!

Happy learning! 🎓
