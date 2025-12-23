# 43. Branching Exploration

★

*One specification, many possibilities. Branching exploration generates multiple implementation variants from the same specification, enabling experimentation and comparison before committing. This is how you find the best approach without gambling.*

---

## The Exploration Imperative

**[Gap Analysis](./gap-analysis.md)** reveals a problem. But how should you solve it? Sometimes the answer isn't obvious. Multiple approaches seem viable:

- Optimize for performance or simplicity?
- Use algorithm A or algorithm B?
- Add a flag or change default behavior?
- Streaming or batch processing?

Traditional development picks one approach and commits. If it's wrong, you backtrack expensively—code rewritten, tests updated, users frustrated.

Specification-driven development enables a different approach: branching exploration. From the same specification, generate different implementations. Compare them. Measure them. Choose the best.

This isn't theoretical. The transformation pipeline makes it practical. Specifications can have variants. Templates can have conditions. Generation can produce alternatives.

---

## The Commitment Problem

**The fundamental problem: Committing to one implementation approach before validating it is risky. Branching exploration lets you try multiple approaches cheaply, then commit to the winner.**

Consider the decision:

```
Gap: Large file validation takes 12 seconds (target: 2 seconds)

Approach A: Streaming validation
  - Process file in chunks
  - Lower memory usage
  - More complex implementation

Approach B: Parallel validation
  - Process sections concurrently
  - Faster for multi-core systems
  - Higher memory usage

Approach C: Lazy validation
  - Validate on-demand
  - Only checks what's accessed
  - Different API semantics
```

Which is best? Theory doesn't tell you. Only measurement can.

### The Cost of Wrong Commitment

Choosing wrong is expensive:

```
Week 1-4: Implement Approach A (streaming)
Week 5: Discover streaming doesn't help because bottleneck is parsing
Week 6-9: Rewrite to Approach B (parallel)
Week 10: Discover parallel has race conditions
Week 11-14: Rewrite to Approach C (lazy)
Week 15: Finally solving the problem

Total: 15 weeks
Effective: 4 weeks
Waste: 11 weeks
```

### The Exploration Alternative

With branching exploration:

```
Week 1: Generate all three variants from specification
Week 2: Benchmark all three in real conditions
Week 3: Discover Approach B is fastest but has race conditions
Week 4: Refine Approach B to fix race conditions
Week 5: Commit to refined Approach B

Total: 5 weeks
Waste: 0 weeks
```

---

## The Forces

### Force: Time Wants Quick Decisions

*Exploration takes time. Stakeholders want decisions.*

Analysis paralysis is real. You can explore forever without deciding.

**Resolution:** Timebox exploration. "We'll spend 2 weeks exploring, then commit." Make exploration efficient, not endless.

### Force: Quality Wants the Best Solution

*Quick decisions may not be optimal. The best solution requires investigation.*

Rushing to commit often means committing to suboptimal solutions.

**Resolution:** Invest in exploration for high-stakes decisions. The bigger the gap, the more exploration is warranted.

### Force: Resources Want Efficiency

*Multiple implementations are wasteful if one would suffice.*

Generating three variants when you'll only keep one feels inefficient.

**Resolution:** Make exploration cheap. Generate variants automatically from specifications. Don't hand-code each alternative.

### Force: Learning Wants Experimentation

*You learn by trying. Theoretical analysis only goes so far.*

Real performance, real complexity, real edge cases—these emerge only from actual implementation.

**Resolution:** Embrace experimentation. Specification-driven development makes it practical.

---

## Therefore

**Use specification variants and conditional generation to explore multiple implementation approaches before committing. Make exploration cheap through automation, then commit to the validated winner.**

### Exploration Approaches

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  BRANCHING EXPLORATION APPROACHES                                              │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ APPROACH 1: SPECIFICATION VARIANTS                                       │  │
│  │                                                                          │  │
│  │  Create separate specification files for each approach                   │  │
│  │                                                                          │  │
│  │  variant-streaming.ttl  ──────┐                                          │  │
│  │                                ├──→ Generate → Compare → Choose         │  │
│  │  variant-parallel.ttl   ──────┤                                          │  │
│  │                                │                                          │  │
│  │  variant-lazy.ttl       ──────┘                                          │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ APPROACH 2: CONDITIONAL TEMPLATES                                        │  │
│  │                                                                          │  │
│  │  Single spec with variant selection in template                          │  │
│  │                                                                          │  │
│  │  command.ttl  ─────────→  command.py.tera                               │  │
│  │                            │                                             │  │
│  │                            ├─ {% if variant == "streaming" %}            │  │
│  │                            │    ... streaming implementation ...         │  │
│  │                            ├─ {% elif variant == "parallel" %}           │  │
│  │                            │    ... parallel implementation ...          │  │
│  │                            └─ {% else %}                                 │  │
│  │                                 ... default implementation ...           │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ APPROACH 3: SPEC-LEVEL VARIANTS                                          │  │
│  │                                                                          │  │
│  │  Single spec with multiple variant definitions                           │  │
│  │                                                                          │  │
│  │  cli:ValidateCommand                                                     │  │
│  │      cli:hasVariant [                                                    │  │
│  │          sk:name "streaming" ;                                           │  │
│  │          sk:implementation "stream_validate" ;                           │  │
│  │      ] ;                                                                 │  │
│  │      cli:hasVariant [                                                    │  │
│  │          sk:name "parallel" ;                                            │  │
│  │          sk:implementation "parallel_validate" ;                         │  │
│  │      ] .                                                                 │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ APPROACH 4: A/B TESTING INTEGRATION                                      │  │
│  │                                                                          │  │
│  │  Deploy multiple variants to production, measure real usage              │  │
│  │                                                                          │  │
│  │  cli:ValidateCommand cli:experiment [                                    │  │
│  │      sk:name "validation-approach" ;                                     │  │
│  │      sk:variantA "streaming" ;                                           │  │
│  │      sk:variantB "parallel" ;                                            │  │
│  │      sk:trafficSplit 0.5 ;                                               │  │
│  │      sk:metric jtbd:MinimizeValidationTime ;                             │  │
│  │  ] .                                                                     │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Specification Variants

```turtle
# variants/validate-streaming.ttl
@prefix cli: <http://github.com/spec-kit/cli#> .
@prefix sk: <http://github.com/spec-kit/schema#> .

cli:ValidateCommand_Streaming a cli:Command ;
    rdfs:label "validate" ;
    sk:variant "streaming" ;
    sk:description "Streaming validation for large files" ;

    cli:implementation [
        sk:approach "streaming" ;
        sk:processingModel "chunk-based" ;
        sk:memoryUsage "low" ;
        sk:complexity "high" ;
        sk:bestFor "files > 1MB"
    ] ;

    sk:hasOption [
        sk:name "--chunk-size" ;
        sk:type "int" ;
        sk:default "65536" ;
        sk:help "Chunk size in bytes for streaming"
    ] .


# variants/validate-parallel.ttl
cli:ValidateCommand_Parallel a cli:Command ;
    rdfs:label "validate" ;
    sk:variant "parallel" ;
    sk:description "Parallel validation using multiple cores" ;

    cli:implementation [
        sk:approach "parallel" ;
        sk:processingModel "concurrent" ;
        sk:memoryUsage "high" ;
        sk:complexity "medium" ;
        sk:bestFor "multi-core systems"
    ] ;

    sk:hasOption [
        sk:name "--workers" ;
        sk:type "int" ;
        sk:default "4" ;
        sk:help "Number of parallel workers"
    ] .


# variants/validate-lazy.ttl
cli:ValidateCommand_Lazy a cli:Command ;
    rdfs:label "validate" ;
    sk:variant "lazy" ;
    sk:description "Lazy validation - validate on access" ;

    cli:implementation [
        sk:approach "lazy" ;
        sk:processingModel "on-demand" ;
        sk:memoryUsage "minimal" ;
        sk:complexity "low" ;
        sk:bestFor "partial validation scenarios"
    ] ;

    sk:hasOption [
        sk:name "--eager" ;
        sk:type "bool" ;
        sk:default "false" ;
        sk:help "Force eager validation of all elements"
    ] .
```

### Generating Variants

```bash
# Generate all variants
$ ggen sync --variant streaming --output-dir variants/streaming/
$ ggen sync --variant parallel --output-dir variants/parallel/
$ ggen sync --variant lazy --output-dir variants/lazy/

# Each outputs:
#   variants/{variant}/src/commands/validate.py
#   variants/{variant}/tests/test_validate.py
#   variants/{variant}/docs/validate.md
```

### Benchmarking Variants

```python
# scripts/benchmark_variants.py
"""Benchmark validation variants to compare performance."""

import subprocess
import time
import statistics
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class BenchmarkResult:
    """Result from benchmarking a variant."""
    variant: str
    file_size: str
    iterations: int
    p50_ms: float
    p90_ms: float
    p99_ms: float
    memory_mb: float
    errors: int


def benchmark_variant(
    variant: str,
    test_file: Path,
    iterations: int = 100
) -> BenchmarkResult:
    """Benchmark a single variant."""
    times = []
    memory_samples = []
    errors = 0

    variant_script = Path(f"variants/{variant}/src/commands/validate.py")

    for _ in range(iterations):
        start = time.perf_counter()
        try:
            result = subprocess.run(
                ["python", str(variant_script), str(test_file)],
                capture_output=True,
                timeout=60
            )
            if result.returncode != 0:
                errors += 1
        except subprocess.TimeoutExpired:
            errors += 1
            continue

        elapsed = (time.perf_counter() - start) * 1000
        times.append(elapsed)

        # Sample memory (simplified)
        # In reality, use memory_profiler or similar
        memory_samples.append(100)  # Placeholder

    if not times:
        return BenchmarkResult(
            variant=variant,
            file_size=_categorize_size(test_file),
            iterations=iterations,
            p50_ms=float('inf'),
            p90_ms=float('inf'),
            p99_ms=float('inf'),
            memory_mb=0,
            errors=errors
        )

    times.sort()
    return BenchmarkResult(
        variant=variant,
        file_size=_categorize_size(test_file),
        iterations=iterations,
        p50_ms=times[len(times) // 2],
        p90_ms=times[int(len(times) * 0.9)],
        p99_ms=times[int(len(times) * 0.99)],
        memory_mb=statistics.mean(memory_samples),
        errors=errors
    )


def _categorize_size(path: Path) -> str:
    """Categorize file by size."""
    size = path.stat().st_size
    if size < 100 * 1024:
        return "small (<100KB)"
    elif size < 1024 * 1024:
        return "medium (100KB-1MB)"
    else:
        return "large (>1MB)"


def compare_variants(
    variants: List[str],
    test_files: List[Path]
) -> Dict[str, List[BenchmarkResult]]:
    """Compare all variants across test files."""
    results = {variant: [] for variant in variants}

    for variant in variants:
        for test_file in test_files:
            result = benchmark_variant(variant, test_file)
            results[variant].append(result)
            print(f"  {variant} / {test_file.name}: P50={result.p50_ms:.0f}ms")

    return results


def generate_comparison_report(
    results: Dict[str, List[BenchmarkResult]]
) -> str:
    """Generate comparison report."""
    lines = [
        "Variant Comparison Report",
        "═" * 70,
        "",
    ]

    # Summary table
    lines.append("Summary (P50 latency in ms)")
    lines.append("-" * 70)
    lines.append(f"{'Variant':<15} {'Small':<12} {'Medium':<12} {'Large':<12} {'Memory':<12}")
    lines.append("-" * 70)

    for variant, variant_results in results.items():
        small = [r for r in variant_results if "small" in r.file_size]
        medium = [r for r in variant_results if "medium" in r.file_size]
        large = [r for r in variant_results if "large" in r.file_size]

        small_p50 = statistics.mean(r.p50_ms for r in small) if small else 0
        medium_p50 = statistics.mean(r.p50_ms for r in medium) if medium else 0
        large_p50 = statistics.mean(r.p50_ms for r in large) if large else 0
        memory = statistics.mean(r.memory_mb for r in variant_results)

        lines.append(
            f"{variant:<15} {small_p50:<12.0f} {medium_p50:<12.0f} "
            f"{large_p50:<12.0f} {memory:<12.0f}"
        )

    lines.append("")

    # Winner analysis
    lines.append("Analysis")
    lines.append("-" * 70)

    # Find best for each category
    for category in ["small", "medium", "large"]:
        best_variant = None
        best_p50 = float('inf')

        for variant, variant_results in results.items():
            cat_results = [r for r in variant_results if category in r.file_size]
            if cat_results:
                avg_p50 = statistics.mean(r.p50_ms for r in cat_results)
                if avg_p50 < best_p50:
                    best_p50 = avg_p50
                    best_variant = variant

        lines.append(f"  Best for {category} files: {best_variant} ({best_p50:.0f}ms)")

    return "\n".join(lines)


if __name__ == "__main__":
    variants = ["streaming", "parallel", "lazy"]
    test_files = list(Path("test_data").glob("*.ttl"))

    print("Benchmarking variants...")
    results = compare_variants(variants, test_files)

    report = generate_comparison_report(results)
    print(report)

    # Write report
    Path("benchmark_report.txt").write_text(report)
```

### Example Benchmark Output

```
Variant Comparison Report
═══════════════════════════════════════════════════════════════════════

Summary (P50 latency in ms)
───────────────────────────────────────────────────────────────────────
Variant         Small        Medium       Large        Memory
───────────────────────────────────────────────────────────────────────
streaming       180          250          800          50
parallel        150          200          1200         200
lazy            120          180          400          30

Analysis
───────────────────────────────────────────────────────────────────────
  Best for small files: lazy (120ms)
  Best for medium files: lazy (180ms)
  Best for large files: lazy (400ms)

Recommendation:
  - Lazy approach wins across all file sizes
  - Consider lazy as default with streaming fallback for memory-constrained environments
  - Parallel approach not recommended (high memory, race condition risks)
```

### Decision Framework

```turtle
# Record exploration decision
sk:Exploration-2025-02-15 a sk:Exploration ;
    sk:date "2025-02-15"^^xsd:date ;
    sk:gap jtbd:MinimizeValidationTime ;
    sk:variantsExplored (
        cli:ValidateCommand_Streaming
        cli:ValidateCommand_Parallel
        cli:ValidateCommand_Lazy
    ) ;
    sk:decision [
        sk:chosenVariant cli:ValidateCommand_Lazy ;
        sk:rationale """
            Lazy validation showed best performance across all file sizes.
            P50 latency 40% better than streaming, 50% better than parallel.
            Memory usage minimal (30MB vs 200MB for parallel).
            Implementation complexity is lowest.
        """ ;
        sk:tradeoffs """
            Lazy validation changes API semantics slightly.
            Full validation requires --eager flag.
            Decision validated with user research showing partial
            validation acceptable for 95% of use cases.
        """
    ] ;
    sk:resultingRefinement sk:REFINE-2025-02-20 .
```

---

## A/B Testing Integration

For production validation of variants:

```turtle
# Spec-level A/B test configuration
cli:ValidateCommand cli:experiment [
    a sk:Experiment ;
    sk:name "validation-approach-test" ;
    sk:hypothesis "Lazy validation will reduce P99 latency by 50%" ;
    sk:variantA [
        sk:name "control" ;
        sk:implementation "current_validate"
    ] ;
    sk:variantB [
        sk:name "treatment" ;
        sk:implementation "lazy_validate"
    ] ;
    sk:trafficSplit 0.5 ;  # 50/50 split
    sk:primaryMetric jtbd:MinimizeValidationTime ;
    sk:secondaryMetrics (
        jtbd:MaximizeValidationCoverage
        jtbd:MaximizeUserSatisfaction
    ) ;
    sk:minimumSampleSize 10000 ;
    sk:duration "P14D"^^xsd:duration ;
    sk:status "running" ;
    sk:startDate "2025-02-01"^^xsd:date ;
    sk:endDate "2025-02-15"^^xsd:date
] .
```

### A/B Test Results

```
A/B Test Results: validation-approach-test
═══════════════════════════════════════════════════════════════════════

Duration: 2025-02-01 to 2025-02-15
Sample size: 15,234 validations (7,612 control, 7,622 treatment)

Primary Metric: Minimize Validation Time
───────────────────────────────────────────────────────────────────────
                    Control (current)    Treatment (lazy)    Difference
P50 latency         450ms               280ms               -38%
P90 latency         1,200ms             520ms               -57%
P99 latency         5,400ms             890ms               -84%

Statistical significance: p < 0.001 ✓

Secondary Metrics
───────────────────────────────────────────────────────────────────────
Validation coverage: 100% vs 100% (no change)
User satisfaction: 3.8/5 vs 4.2/5 (+10%)
Error rate: 0.3% vs 0.2% (-33%)

Recommendation: ADOPT treatment (lazy validation)

Confidence: HIGH
- All metrics improved or unchanged
- Large sample size
- Strong statistical significance
- User satisfaction increased
```

---

## Case Study: The Parallel vs Streaming Decision

*A team uses branching exploration to avoid an expensive mistake.*

### The Setup

Gap analysis showed validation was slow for large files. Engineering proposed two solutions:

**Team A's proposal: Parallel validation**
- "Multi-core is the future"
- "Just parallelize the validators"
- Estimated: 3 weeks

**Team B's proposal: Streaming validation**
- "Memory is the bottleneck"
- "Process incrementally"
- Estimated: 4 weeks

Management wanted to pick one and commit.

### The Exploration

Instead, they ran branching exploration:

```bash
# Week 1: Generate both variants
ggen sync --variant parallel --output-dir variants/parallel/
ggen sync --variant streaming --output-dir variants/streaming/

# Week 1: Benchmark
python scripts/benchmark_variants.py

# Results shocked everyone:
#   Parallel: P50=200ms (small), P50=1200ms (large)
#   Streaming: P50=180ms (small), P50=800ms (large)
#   Current: P50=450ms (small), P50=12000ms (large)
```

### The Discovery

Both variants were faster than current, but neither met the target (2 seconds for large files).

Root cause investigation during benchmarking revealed:
- Bottleneck wasn't CPU or memory
- Bottleneck was SHACL shape compilation
- Shapes were recompiled for each file

### The Real Solution

```turtle
# New variant: cached validation
cli:ValidateCommand_Cached a cli:Command ;
    sk:variant "cached" ;
    cli:implementation [
        sk:approach "cached" ;
        sk:insight "Compile shapes once, reuse across files" ;
        sk:expectedImprovement "90% for repeated validations"
    ] .
```

Benchmark with caching:
```
Cached: P50=50ms (small), P50=200ms (large)

Target met!
```

### The Lesson

Without exploration, they would have spent 3-4 weeks building parallel or streaming, only to discover neither solved the real problem. Exploration took 1 week and found the actual solution.

---

## Anti-Patterns

### Anti-Pattern: Exploration Theater

*"We explored three options for 5 minutes and picked the first one."*

Shallow exploration isn't exploration. It's justifying a predetermined decision.

**Resolution:** Set minimum exploration standards. Require benchmarks, data, and documented trade-offs.

### Anti-Pattern: Endless Exploration

*"We've been exploring for 6 months. We still can't decide."*

Exploration without decision is analysis paralysis.

**Resolution:** Timebox exploration. Set a decision date. "Good enough and chosen" beats "perfect and never decided."

### Anti-Pattern: Ignoring Results

*"The data says lazy is best, but I prefer parallel. Let's do parallel."*

If you ignore exploration results, why explore?

**Resolution:** Commit to data-driven decisions. Document why if you override data.

---

## Implementation Checklist

### Setup

- [ ] Define variant schema in RDF
- [ ] Create variant specification templates
- [ ] Set up variant generation pipeline
- [ ] Create benchmarking framework

### Exploration

- [ ] Identify approaches to explore
- [ ] Create specification variants
- [ ] Generate implementation variants
- [ ] Build benchmark test suite

### Comparison

- [ ] Run benchmarks across variants
- [ ] Measure key metrics (latency, memory, complexity)
- [ ] Document trade-offs for each variant
- [ ] Create comparison report

### Decision

- [ ] Review data with stakeholders
- [ ] Document chosen variant and rationale
- [ ] Create refinement proposal for winner
- [ ] Archive exploration artifacts

---

## Exercises

### Exercise 1: Define Variants

For a performance problem, define three variant specifications:

```turtle
# Variant A
cli:Command_VariantA a cli:Command ;
    sk:variant "???" ;
    cli:implementation [
        sk:approach "???" ;
        sk:tradeoff "???"
    ] .

# Variant B ...
# Variant C ...
```

### Exercise 2: Create Benchmark

Design a benchmark to compare your variants:

```python
def benchmark(variant: str, test_cases: List[Path]) -> BenchmarkResult:
    # What metrics would you measure?
    # What test cases would you use?
    # How would you ensure fairness?
    pass
```

### Exercise 3: Make a Decision

Given these benchmark results, which variant would you choose?

| Variant | Small Files | Large Files | Memory | Complexity |
|---------|-------------|-------------|--------|------------|
| A | 100ms | 5000ms | 50MB | Low |
| B | 150ms | 500ms | 200MB | Medium |
| C | 80ms | 800ms | 100MB | High |

Document your decision and rationale.

---

## Resulting Context

After implementing this pattern, you have:

- **Ability to explore multiple approaches** before committing
- **Data-driven comparison of alternatives** — not gut feelings
- **Reduced risk of committing to wrong approach** — explore first
- **Learning from experimentation** — even "losing" variants teach lessons
- **Validated refinements** — commit to proven winners

Branching exploration transforms risky bets into informed decisions. You try before you commit.

---

## Related Patterns

- **Supports:** **[42. Specification Refinement](./specification-refinement.md)** — Provides validated approaches
- **Uses:** **[40. Outcome Measurement](./outcome-measurement.md)** — Compare variant outcomes
- **Leverages:** **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Generation enables exploration
- **Guided by:** **[3. Forces in Tension](../context/forces-in-tension.md)** — Trade-offs to balance

---

## Philosophical Note

> *"The best way to have a good idea is to have lots of ideas."*
>
> — Linus Pauling

Innovation isn't about picking the right answer on the first try. It's about generating possibilities, testing them, and selecting the best. Branching exploration systematizes this process.

Specification-driven development makes exploration practical. The transformation pipeline can generate variants cheaply. Benchmarks can compare them objectively. You can have lots of ideas—and test them all.

Don't commit to your first idea. Explore. Compare. Then commit to the validated winner.

---

**Next:** Learn how **[44. Deprecation Path](./deprecation-path.md)** provides graceful retirement for capabilities that exploration has superseded.
