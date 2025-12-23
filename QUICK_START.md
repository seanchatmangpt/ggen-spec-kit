# Quick Start Guide

Welcome to ggen Spec Kit! Get started in 5 minutes.

## 1. Install Specify CLI

```bash
uv tool install specify-cli --from git+https://github.com/seanchatmangpt/ggen-spec-kit.git
```

## 2. Create Your First Project

```bash
specify init my-first-app
cd my-first-app
```

## 3. Verify Installation

```bash
specify check
```

## 4. Start Learning

Choose your path:

### 👨‍🎓 New to Spec Kit?
→ **[Start with Tutorial 1: Getting Started](./docs/tutorials/01-getting-started.md)** (10 min)

### 🚀 Ready to Build?
→ **[Browse How-to Guides](./docs/guides/)** for task-oriented instructions

### 💻 Need Technical Details?
→ **[Check Reference Docs](./docs/reference/)** for specifications

### 🧠 Want to Understand Concepts?
→ **[Read Explanations](./docs/explanation/)** for deep dives

---

## Documentation Portal

All documentation is organized using the **Diataxis framework**:

### 📚 [Tutorials](./docs/tutorials/)
Step-by-step hands-on learning (100 minutes to complete all)

### 🎯 [How-to Guides](./docs/guides/)
Goal-oriented task instructions

### 📋 [Reference](./docs/reference/)
Technical specifications and facts

### 💡 [Explanations](./docs/explanation/)
Conceptual understanding and design rationale

→ **[Full Documentation Portal](./docs/)**

---

## What is Spec-Driven Development?

ggen Spec Kit enables **specification-driven development** where:

1. **You write RDF specifications** - Define your domain in machine-readable format
2. **ggen transforms them** - Into Python code, tests, and documentation
3. **Your code stays in sync** - Specs are the source of truth
4. **Type-safe across languages** - Generate code in Python, TypeScript, Rust, Java, C#, Go

**The Constitutional Equation:**
```
spec.md = μ(feature.ttl)
```

This means: *Markdown documentation is generated from RDF specifications.*

---

## Quick Tour

### Create a CLI Command in 3 Steps

**1. Write RDF specification** (`ontology/cli-commands.ttl`):
```turtle
sk:hello
    a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet the user" .
```

**2. Transform with ggen:**
```bash
ggen sync
```

**3. Implement the business logic** (`src/specify_cli/ops/hello.py`):
```python
def hello_operation() -> str:
    return "Hello, World!"
```

Done! Your command is ready.

---

## Key Concepts

### Three-Tier Architecture

Spec Kit organizes code into three clean layers:

```
Commands       ← CLI interface (user-facing)
    ↓
Operations     ← Pure business logic (no side effects)
    ↓
Runtime        ← I/O, subprocess, HTTP (all side effects)
```

### Specification-Driven Workflow

```
Edit RDF → ggen sync → Implement → Test → Deploy
```

### RDF-First Philosophy

**Unlike traditional development:**
```
Design → Code → Test → Document → Deploy
```

**Spec-Driven development:**
```
RDF Spec → Generate Code/Tests/Docs → Deploy
```

---

## Next Steps

1. **Complete Tutorial 1-3** (50 minutes) - Get the fundamentals
2. **Try the How-to Guides** (10-30 minutes) - Do something real
3. **Explore Reference Docs** - Look up details as needed
4. **Read Explanations** - Understand the "why"

---

## Getting Help

- **Questions?** Start with [Documentation](./docs/)
- **Found a bug?** [Open an issue](https://github.com/seanchatmangpt/ggen-spec-kit/issues)
- **Want to discuss?** [Start a discussion](https://github.com/seanchatmangpt/ggen-spec-kit/discussions)
- **Want to contribute?** See [CONTRIBUTING.md](./CONTRIBUTING.md)

---

## Key Files

| File | Purpose |
|------|---------|
| **[README.md](./README.md)** | Project overview |
| **[CLAUDE.md](./CLAUDE.md)** | Developer guide for AI agents |
| **[docs/](./docs/)** | Complete documentation |
| **[src/](./src/)** | Source code |
| **[tests/](./tests/)** | Test suite |
| **[ontology/](./ontology/)** | RDF schemas |
| **[memory/](./memory/)** | RDF specifications |

---

## Resources

- **GitHub:** https://github.com/seanchatmangpt/ggen-spec-kit
- **Documentation:** [docs/](./docs/)
- **Contributing:** [CONTRIBUTING.md](./CONTRIBUTING.md)
- **License:** [LICENSE](./LICENSE)

---

**Ready to start?** → [Tutorial 1: Getting Started](./docs/tutorials/01-getting-started.md) 🚀
