# 43. Branching Exploration

★

*One specification, many possibilities. Branching exploration generates multiple implementation variants from the same specification, enabling experimentation and comparison.*

---

**[Gap Analysis](./gap-analysis.md)** reveals a problem. But how should you solve it? Sometimes the answer isn't clear. Multiple approaches seem viable.

Traditional development picks one approach and commits. If it's wrong, you backtrack expensively.

Specification-driven development enables branching exploration. From the same specification, generate different implementations:
- One optimized for performance
- One optimized for simplicity
- One using a different algorithm

Compare them. Measure them. Choose the best.

**The problem: Committing to one implementation approach before validating it is risky. Branching exploration lets you try multiple approaches cheaply.**

---

**The forces at play:**

- *Time wants quick decisions.* Exploration takes time.

- *Quality wants the best solution.* Quick decisions may not be optimal.

- *Resources want efficiency.* Multiple implementations are wasteful if one would suffice.

- *Learning wants experimentation.* You learn by trying.

The tension: explore enough to make good decisions, not so much that you never decide.

---

**Therefore:**

Use specification variants and conditional generation to explore multiple implementation approaches.

**Approach 1: Specification variants**

Create specification branches for different approaches:

```turtle
# variant-a.ttl - Performance-optimized
cli:ValidateCommand_VariantA a cli:Command ;
    rdfs:label "validate" ;
    sk:variant "performance" ;
    cli:implementation "streaming" ;
    sk:description "Streaming validation for speed" .

# variant-b.ttl - Simplicity-optimized
cli:ValidateCommand_VariantB a cli:Command ;
    rdfs:label "validate" ;
    sk:variant "simplicity" ;
    cli:implementation "batch" ;
    sk:description "Batch validation for simplicity" .
```

**Approach 2: Conditional templates**

Single spec with variant selection:

```turtle
cli:ValidateCommand a cli:Command ;
    cli:hasVariant [
        sk:name "streaming" ;
        sk:condition "file_size > 1MB" ;
        cli:template "command-streaming.py.tera"
    ] ;
    cli:hasVariant [
        sk:name "batch" ;
        sk:condition "file_size <= 1MB" ;
        cli:template "command-batch.py.tera"
    ] .
```

**Exploration workflow:**

```bash
# Generate variant A
ggen sync --variant performance
mv src/commands/validate.py src/commands/validate_perf.py

# Generate variant B
ggen sync --variant simplicity
mv src/commands/validate.py src/commands/validate_simple.py

# Benchmark both
python benchmark.py --implementations validate_perf,validate_simple

# Results:
#   validate_perf:  P50=200ms, P99=800ms, complexity=high
#   validate_simple: P50=400ms, P99=1200ms, complexity=low
```

**A/B testing integration:**

```turtle
cli:ValidateCommand cli:experiment [
    sk:name "validation-approach" ;
    sk:variantA "streaming" ;
    sk:variantB "batch" ;
    sk:metric jtbd:MinimizeValidationTime ;
    sk:status "running" ;
    sk:startDate "2025-02-01"^^xsd:date ;
    sk:trafficSplit 0.5
] .
```

**Decision framework:**

| Factor | Streaming | Batch |
|--------|-----------|-------|
| P50 latency | 200ms | 400ms |
| P99 latency | 800ms | 1200ms |
| Memory usage | Low | High |
| Code complexity | High | Low |
| Maintenance cost | High | Low |

Decision: Use streaming for files > 1MB, batch for smaller files (hybrid approach).

---

**Resulting context:**

After applying this pattern, you have:

- Ability to explore multiple approaches
- Data-driven comparison of alternatives
- Reduced risk of committing to wrong approach
- Learning from experimentation

This supports **[42. Specification Refinement](./specification-refinement.md)** with validated approaches.

---

**Related patterns:**

- *Supports:* **[42. Specification Refinement](./specification-refinement.md)** — Validated approaches
- *Uses:* **[40. Outcome Measurement](./outcome-measurement.md)** — Compare variants
- *Leverages:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Generation enables exploration
- *Guided by:* **[3. Forces in Tension](../context/forces-in-tension.md)** — Trade-offs to balance

---

> *"The best way to have a good idea is to have lots of ideas."*
>
> — Linus Pauling

Branching exploration lets you have lots of ideas—and test them.
