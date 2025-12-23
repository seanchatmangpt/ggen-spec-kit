# 41. Gap Analysis

★★

*Where are we falling short? Gap analysis compares current performance against targets and expectations, revealing opportunities for improvement.*

---

**[Outcome Measurement](./outcome-measurement.md)** shows current performance. But performance in isolation isn't actionable. You need context:

- How does current compare to target?
- Which outcomes have the largest gaps?
- Which gaps matter most to customers?
- What's causing the gaps?

Gap analysis provides this context. It identifies where attention is needed most and provides the data to prioritize effectively.

**The problem: Knowing current performance isn't enough. Gap analysis reveals where improvement efforts will have the most impact.**

---

**The forces at play:**

- *Resources are limited.* You can't improve everything at once.

- *Importance varies.* Not all gaps matter equally.

- *Causes differ.* Different gaps need different solutions.

- *Priorities compete.* Everyone thinks their area is most important.

The tension: focus limited resources on gaps that matter most.

---

**Therefore:**

Perform structured gap analysis that combines outcome measurement with importance ratings to identify high-priority improvement opportunities.

**Gap calculation:**

```
Gap = Importance × (Target - Current) / Target
```

High importance + large gap = high priority.

**Gap analysis query:**

```sparql
# Find outcomes with significant gaps
PREFIX jtbd: <http://github.com/spec-kit/jtbd#>

SELECT ?outcome ?importance ?target ?current ?gap ?priority
WHERE {
    ?outcome a jtbd:Outcome ;
             jtbd:importance ?importance ;
             jtbd:target ?target ;
             jtbd:currentPerformance ?current .

    BIND((?target - ?current) / ?target AS ?gap)
    BIND(?importance * ?gap AS ?priority)
}
ORDER BY DESC(?priority)
```

**Gap analysis report:**

```
Outcome Gap Analysis
═══════════════════════════════════════════════════════════

HIGH PRIORITY (Gap Score > 0.7)
───────────────────────────────────────────────────────────

1. Minimize large file validation time
   Importance: HIGH (5/5)
   Target: 5 seconds
   Current: 12 seconds (P99)
   Gap: 140% over target
   Priority Score: 0.92

   Root Cause: Sequential file processing
   Recommendation: Implement streaming validation

2. Minimize error message comprehension time
   Importance: HIGH (5/5)
   Target: 30 seconds to understand
   Current: 2 minutes (survey)
   Gap: 300% over target
   Priority Score: 0.88

   Root Cause: Technical error messages
   Recommendation: Add plain-language explanations

MEDIUM PRIORITY (Gap Score 0.4-0.7)
───────────────────────────────────────────────────────────

3. Maximize validation coverage
   Importance: MEDIUM (3/5)
   Target: 100% of RDF constructs
   Current: 85%
   Gap: 15% under target
   Priority Score: 0.45

   Root Cause: Missing SPARQL validation
   Recommendation: Add SPARQL pattern checking

LOW PRIORITY (Gap Score < 0.4)
───────────────────────────────────────────────────────────

4. Minimize command startup time
   Importance: LOW (2/5)
   Target: 100ms
   Current: 150ms
   Gap: 50% over target
   Priority Score: 0.25

   Root Cause: Import overhead
   Recommendation: Defer unless user complaints
```

**Importance-satisfaction matrix:**

```
                    SATISFACTION
                    Low         High
              ┌──────────┬──────────┐
          High│ PRIORITY │ MAINTAIN │
IMPORTANCE    │  (fix!)  │ (keep)   │
              ├──────────┼──────────┤
          Low │ IGNORE   │ REDUCE   │
              │ (later)  │ (overkill)│
              └──────────┴──────────┘
```

**Gap tracking over time:**

```turtle
# Track gap evolution
jtbd:MinimizeValidationTime
    jtbd:gapHistory [
        jtbd:date "2025-01-01"^^xsd:date ;
        jtbd:gap 0.85 ;  # 85% gap
    ] ;
    jtbd:gapHistory [
        jtbd:date "2025-02-01"^^xsd:date ;
        jtbd:gap 0.60 ;  # Improving!
    ] ;
    jtbd:gapHistory [
        jtbd:date "2025-03-01"^^xsd:date ;
        jtbd:gap 0.40 ;  # Further progress
    ] .
```

---

**Resulting context:**

After applying this pattern, you have:

- Prioritized list of improvement opportunities
- Data-driven basis for resource allocation
- Tracking of gap closure over time
- Clear connection between gaps and root causes

This drives **[42. Specification Refinement](./specification-refinement.md)** and informs **[43. Branching Exploration](./branching-exploration.md)**.

---

**Related patterns:**

- *Uses:* **[40. Outcome Measurement](./outcome-measurement.md)** — Current performance
- *Drives:* **[42. Specification Refinement](./specification-refinement.md)** — Fix gaps
- *Informs:* **[43. Branching Exploration](./branching-exploration.md)** — Explore solutions
- *Guided by:* **[5. Outcome Desired](../context/outcome-desired.md)** — Targets defined

---

> *"The first step toward solving a problem is recognizing that it exists."*

Gap analysis doesn't just recognize problems—it quantifies them, prioritizes them, and points toward solutions.
