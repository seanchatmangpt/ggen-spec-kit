# 10. Single Source of Truth

★★

*When the same information exists in multiple places, it will eventually diverge. Establishing a single source of truth—one authoritative location for each piece of knowledge—prevents drift and enables automation.*

---

You've chosen a **[Semantic Foundation](./semantic-foundation.md)**. Now face a fundamental question: where does truth live?

In traditional development, truth is scattered:
- Requirements in documents
- Design in diagrams
- Behavior in code
- Documentation in wikis
- Tests in test files

Each location claims authority. Each evolves independently. Over time, they diverge. The document says one thing; the code does another. The tests validate something the documentation doesn't describe. Nobody knows which source to trust.

This scattered truth creates constant reconciliation work. Did you update the docs? Did you update the tests? Did you update the requirements? Every change requires manual synchronization across sources. And synchronization always fails eventually.

**The problem: When truth is scattered across multiple sources, divergence is inevitable. Reconciliation becomes a never-ending burden.**

---

**The forces at play:**

- *Convenience favors locality.* It's easier to update information where you're working than in a canonical location elsewhere.

- *Different stakeholders need different views.* Developers want code. Business wants requirements. Users want documentation. Each view has its home.

- *History creates scattering.* As projects evolve, different decisions about where to put things accumulate into a mess.

- *Tools assume their format is central.* Your IDE wants code to be authoritative. Your wiki wants documents. Each tool pulls toward itself.

The tension: a single source is simpler but feels restrictive. Multiple sources feel natural but create drift.

---

**Therefore:**

Designate one source of truth for each domain of knowledge. For capabilities, that source is RDF.

**The principle:** Any piece of knowledge that can be expressed in RDF, must be expressed in RDF. All other representations are generated.

```
RDF Source (truth)
      │
      ├──▶ Code (generated)
      ├──▶ Documentation (generated)
      ├──▶ Tests (generated)
      └──▶ Schemas (generated)
```

**What lives in RDF:**

- Command definitions (name, arguments, options)
- Feature specifications (behavior, constraints)
- Outcome definitions (metrics, targets)
- Job definitions (functional, emotional, social)
- Concept definitions (domain vocabulary)

**What is generated:**

- Python command implementations
- CLI argument parsing
- Documentation pages
- Test stubs
- API schemas

**Rules for the single source:**

1. **One write location:** Edit only the RDF source
2. **One read location:** Queries extract from RDF
3. **Generated artifacts are read-only:** Never edit generated files
4. **Regeneration is safe:** Running the transformation again produces identical output

**File organization:**

```
ontology/           # Source of truth for structure
  ├── schema.ttl    # Core concepts and relationships
  └── commands.ttl  # Command specifications

memory/             # Source of truth for content
  ├── jobs.ttl      # Customer jobs
  └── outcomes.ttl  # Desired outcomes

# GENERATED (do not edit)
src/commands/       # Generated from ontology/commands.ttl
docs/               # Generated from memory/*.ttl
tests/              # Generated from ontology/commands.ttl
```

---

**Resulting context:**

After applying this pattern, you have:

- One authoritative location for each piece of knowledge
- Clear separation between source and generated artifacts
- Ability to regenerate artifacts confidently
- Elimination of drift between code, docs, and tests

This enables **[Executable Specification](./executable-specification.md)** (specs can drive generation) and **[Drift Detection](../verification/drift-detection.md)** (compare generated with actual).

---

**Related patterns:**

- *Builds on:* **[9. Semantic Foundation](./semantic-foundation.md)** — RDF is the source format
- *Enables:* **[11. Executable Specification](./executable-specification.md)** — Source drives generation
- *Enables:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Artifacts are transformations
- *Verified by:* **[35. Drift Detection](../verification/drift-detection.md)** — Detect divergence

---

> *"There should be one—and preferably only one—obvious way to do it."*
>
> — The Zen of Python

Apply this principle not just to code, but to knowledge itself. One source. One truth. Everything else flows from it.

---

**The Discipline:**

Single source of truth requires discipline:

1. **Never edit generated files.** When you see something wrong in generated code, fix the RDF source and regenerate.

2. **Regenerate frequently.** Make regeneration part of your workflow. Commit both source and generated files together.

3. **Verify consistency.** Use **[Receipt Verification](../verification/receipt-verification.md)** to ensure generated files match their source.

4. **Document the boundary.** Make it clear which files are source and which are generated.

The discipline feels constraining at first. But it pays off in eliminated drift, automated consistency, and the ability to trust your artifacts.

---

**When Multiple Sources Seem Necessary:**

Sometimes you'll feel you need multiple sources:

- "The RDF is too verbose for this simple case"
- "The team knows how to edit YAML better"
- "The tool requires JSON"

Resist. Instead:
- Add a transformation that simplifies RDF for the common case
- Invest in team education on RDF
- Generate the required format from RDF

Every second source becomes a drift vector. Maintain the single source and build transformations.
