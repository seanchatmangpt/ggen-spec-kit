# Pattern Index

★★

*A pattern language is not a dictionary to be read alphabetically—it's a territory to be explored. This index provides multiple entry points: by number, by confidence, by use case, by problem, by skill level. Use whatever map serves your journey.*

---

## How to Use This Index

This index serves multiple purposes:

1. **Quick Reference**: Find any pattern by number or name
2. **Navigation**: Discover which patterns address your current problem
3. **Learning Path**: Follow recommended sequences for different skill levels
4. **Assessment**: Understand confidence levels and maturity
5. **Planning**: Identify patterns needed for specific projects

### Reading Pattern Entries

Each pattern entry includes:

```
| # | Pattern | Confidence | Summary | Difficulty | Time |
```

- **#**: Sequential number in the language
- **Pattern**: Name linking to full pattern
- **Confidence**: ★★ (well-established) or ★ (promising)
- **Summary**: One-sentence description of the pattern's purpose
- **Difficulty**: Beginner / Intermediate / Advanced
- **Time**: Typical implementation effort (hours to weeks)

---

## Complete Pattern Catalog

### Part I: Context Patterns (1-8)

*Understanding the territory before building.*

Context patterns help you understand the world your capability will enter. Skip these at your peril—capabilities built without context understanding solve the wrong problems.

| # | Pattern | Confidence | Summary | Difficulty | Time |
|---|---------|------------|---------|------------|------|
| 1 | [Living System](../context/living-system.md) | ★★ | Understand the ecosystem your capability joins—people, tools, processes, culture, and their interconnections | Beginner | 2-4 hours |
| 2 | [Customer Job](../context/customer-job.md) | ★★ | Identify the progress customers seek, not just the features they request—functional, emotional, and social dimensions | Intermediate | 4-8 hours |
| 3 | [Forces in Tension](../context/forces-in-tension.md) | ★★ | Map the competing forces that make problems genuinely difficult—speed vs. thoroughness, flexibility vs. consistency | Intermediate | 2-4 hours |
| 4 | [Circumstance of Struggle](../context/circumstance-of-struggle.md) | ★★ | Discover when and why customers struggle—the triggers, emotional states, time budgets, and consequences that create demand | Intermediate | 4-8 hours |
| 5 | [Outcome Desired](../context/outcome-desired.md) | ★★ | Define measurable success criteria that capture what customers actually want to achieve, not proxy metrics | Intermediate | 2-4 hours |
| 6 | [Progress Maker](../context/progress-maker.md) | ★★ | Catalog how customers make progress today—the tools, workarounds, and manual processes that currently serve the job | Beginner | 2-4 hours |
| 7 | [Anxieties and Habits](../context/anxieties-and-habits.md) | ★★ | Understand what holds people back from switching—fears about new solutions, comfort with current approaches, switching costs | Intermediate | 4-8 hours |
| 8 | [Competing Solutions](../context/competing-solutions.md) | ★★ | Analyze all alternatives competing for the same job—including non-consumption and manual workarounds | Intermediate | 4-8 hours |

**Part I Total**: 8 patterns covering discovery and understanding

**Key Insight**: Most failed capabilities fail because of inadequate context understanding, not technical deficiencies. Invest here first.

---

### Part II: Specification Patterns (9-20)

*The grammar of capability definition.*

Specification patterns provide the formal language for capturing capability requirements. They ensure precision, enable automation, and maintain traceability.

| # | Pattern | Confidence | Summary | Difficulty | Time |
|---|---------|------------|---------|------------|------|
| 9 | [Semantic Foundation](../specification/semantic-foundation.md) | ★★ | Choose RDF as your knowledge representation—triples, URIs, and graphs as the universal substrate for specifications | Intermediate | 4-8 hours |
| 10 | [Single Source of Truth](../specification/single-source-of-truth.md) | ★★ | Establish one authoritative location for each piece of knowledge—eliminate duplication and drift at the root | Beginner | 1-2 hours |
| 11 | [Executable Specification](../specification/executable-specification.md) | ★★ | Write specifications precise enough to drive validation, extraction, and generation—not just documentation | Intermediate | 8-16 hours |
| 12 | [Shape Constraint](../specification/shape-constraint.md) | ★★ | Define valid specification structure using SHACL shapes—catch invalid specs before they propagate | Intermediate | 4-8 hours |
| 13 | [Vocabulary Boundary](../specification/vocabulary-boundary.md) | ★★ | Use namespaces to keep domain concepts distinct—prevent vocabulary collision and enable controlled evolution | Beginner | 2-4 hours |
| 14 | [Property Path](../specification/property-path.md) | ★ | Navigate multi-hop relationships using SPARQL property paths—traverse the graph efficiently | Advanced | 4-8 hours |
| 15 | [Inference Rule](../specification/inference-rule.md) | ★ | Derive facts from existing knowledge automatically—keep specifications DRY through logical entailment | Advanced | 8-16 hours |
| 16 | [Layered Ontology](../specification/layered-ontology.md) | ★★ | Organize concepts by abstraction level—universal, framework, domain, and instance layers with clear boundaries | Intermediate | 8-16 hours |
| 17 | [Domain-Specific Language](../specification/domain-specific-language.md) | ★ | Create simplified syntax for common specification tasks—patterns that expand to valid RDF | Advanced | 1-2 weeks |
| 18 | [Narrative Specification](../specification/narrative-specification.md) | ★ | Embed human context in formal specs—rationale, scenarios, alternatives, and examples alongside formal definitions | Intermediate | 4-8 hours |
| 19 | [Acceptance Criterion](../specification/acceptance-criterion.md) | ★★ | Define testable conditions for "done"—Given-When-Then scenarios that drive testing and verification | Intermediate | 4-8 hours |
| 20 | [Traceability Thread](../specification/traceability-thread.md) | ★★ | Link artifacts across all levels—from customer jobs to outcomes to criteria to tests to code | Intermediate | 8-16 hours |

**Part II Total**: 12 patterns covering formal specification

**Key Insight**: The quality of your specifications determines the quality of everything generated from them. Invest in precision.

---

### Part III: Transformation Patterns (21-30)

*The art of faithful generation.*

Transformation patterns define how specifications become artifacts. They ensure consistency, enable automation, and provide provenance.

| # | Pattern | Confidence | Summary | Difficulty | Time |
|---|---------|------------|---------|------------|------|
| 21 | [Constitutional Equation](../transformation/constitutional-equation.md) | ★★ | The fundamental principle: `spec.md = μ(feature.ttl)`—human-readable artifacts are always generated from formal specifications | Intermediate | 2-4 hours |
| 22 | [Normalization Stage](../transformation/normalization-stage.md) | ★★ | First pipeline stage (μ₁): Validate source against SHACL shapes before any transformation begins | Intermediate | 4-8 hours |
| 23 | [Extraction Query](../transformation/extraction-query.md) | ★★ | Second pipeline stage (μ₂): Use SPARQL to pull structured data from validated RDF for template rendering | Intermediate | 4-8 hours |
| 24 | [Template Emission](../transformation/template-emission.md) | ★★ | Third pipeline stage (μ₃): Render Tera templates with extracted data to produce output artifacts | Intermediate | 4-8 hours |
| 25 | [Canonicalization](../transformation/canonicalization.md) | ★★ | Fourth pipeline stage (μ₄): Normalize output format—line endings, whitespace, encoding—for consistent comparison | Intermediate | 2-4 hours |
| 26 | [Receipt Generation](../transformation/receipt-generation.md) | ★★ | Fifth pipeline stage (μ₅): Create cryptographic proof linking source to artifact through pipeline | Intermediate | 4-8 hours |
| 27 | [Idempotent Transform](../transformation/idempotent-transform.md) | ★★ | Ensure μ ∘ μ = μ—running the transformation twice produces identical results to running it once | Advanced | 8-16 hours |
| 28 | [Partial Regeneration](../transformation/partial-regeneration.md) | ★ | Regenerate only artifacts affected by a change—trade completeness for speed in large codebases | Advanced | 1-2 weeks |
| 29 | [Multi-Target Emission](../transformation/multi-target-emission.md) | ★ | Generate multiple output formats from a single specification—code, docs, tests, configs from one source | Intermediate | 4-8 hours |
| 30 | [Human-Readable Artifact](../transformation/human-readable-artifact.md) | ★★ | Design generated output for human consumption—clear structure, helpful comments, consistent formatting | Intermediate | 4-8 hours |

**Part III Total**: 10 patterns covering the transformation pipeline

**Key Insight**: The transformation pipeline is deterministic machinery. Every stage must be predictable, verifiable, and idempotent.

---

### Part IV: Verification Patterns (31-38)

*Ensuring the capability lives and breathes.*

Verification patterns ensure your capability does what it should. They catch problems early, maintain quality, and provide confidence.

| # | Pattern | Confidence | Summary | Difficulty | Time |
|---|---------|------------|---------|------------|------|
| 31 | [Test Before Code](../verification/test-before-code.md) | ★★ | Generate tests from specifications before implementing—let specs drive what gets tested | Intermediate | 4-8 hours |
| 32 | [Contract Test](../verification/contract-test.md) | ★★ | Verify interface promises without testing internal implementation—focus on the contract, not the machinery | Intermediate | 4-8 hours |
| 33 | [Integration Reality](../verification/integration-reality.md) | ★★ | Test with real dependencies, not just mocks—integration tests that reflect production reality | Advanced | 8-16 hours |
| 34 | [Shape Validation](../verification/shape-validation.md) | ★★ | Run SHACL validation continuously—catch invalid specifications before they corrupt downstream artifacts | Intermediate | 4-8 hours |
| 35 | [Drift Detection](../verification/drift-detection.md) | ★★ | Detect when generated files have been manually modified—catch constitutional violations automatically | Intermediate | 4-8 hours |
| 36 | [Receipt Verification](../verification/receipt-verification.md) | ★★ | Verify cryptographic proofs connecting sources to artifacts—trust but verify at scale | Intermediate | 4-8 hours |
| 37 | [Continuous Validation](../verification/continuous-validation.md) | ★★ | Run appropriate checks at every pipeline stage—fast checks often, thorough checks at gates | Intermediate | 8-16 hours |
| 38 | [Observable Execution](../verification/observable-execution.md) | ★★ | Instrument capabilities with telemetry—traces, metrics, and logs for understanding and debugging | Intermediate | 8-16 hours |

**Part IV Total**: 8 patterns covering verification and quality

**Key Insight**: Verification isn't a phase—it's continuous. Every commit, every push, every deployment should validate the constitutional equation.

---

### Part V: Evolution Patterns (39-45)

*The capability that learns and grows.*

Evolution patterns help your capability improve over time. They connect production reality back to specification evolution.

| # | Pattern | Confidence | Summary | Difficulty | Time |
|---|---------|------------|---------|------------|------|
| 39 | [Feedback Loop](../evolution/feedback-loop.md) | ★★ | Connect production telemetry to specification evolution—close the Build-Measure-Learn cycle | Intermediate | 8-16 hours |
| 40 | [Outcome Measurement](../evolution/outcome-measurement.md) | ★★ | Track whether customers achieve their desired outcomes—not just whether features work | Intermediate | 8-16 hours |
| 41 | [Gap Analysis](../evolution/gap-analysis.md) | ★★ | Identify where current performance falls short of targets—prioritize by importance and gap size | Intermediate | 4-8 hours |
| 42 | [Specification Refinement](../evolution/specification-refinement.md) | ★★ | Evolve specifications through a disciplined workflow—propose, review, validate, commit, regenerate | Intermediate | 4-8 hours |
| 43 | [Branching Exploration](../evolution/branching-exploration.md) | ★ | Generate multiple implementation variants from specification branches—compare approaches with data | Advanced | 1-2 weeks |
| 44 | [Deprecation Path](../evolution/deprecation-path.md) | ★★ | Retire capabilities gracefully—warnings, alternatives, timelines, and clean removal | Intermediate | 4-8 hours |
| 45 | [Living Documentation](../evolution/living-documentation.md) | ★★ | Generate documentation from specifications—docs that stay current because they're regenerated | Intermediate | 4-8 hours |

**Part V Total**: 7 patterns covering evolution and improvement

**Key Insight**: Capabilities that don't evolve die. Build feedback loops from day one, not as an afterthought.

---

## Patterns by Confidence Level

### ★★ Well-Established Patterns (35 total)

These patterns have substantial evidence of success across multiple contexts. They represent proven solutions that you can apply with confidence.

**Context (8/8):**
1. Living System
2. Customer Job
3. Forces in Tension
4. Circumstance of Struggle
5. Outcome Desired
6. Progress Maker
7. Anxieties and Habits
8. Competing Solutions

**Specification (9/12):**
9. Semantic Foundation
10. Single Source of Truth
11. Executable Specification
12. Shape Constraint
13. Vocabulary Boundary
16. Layered Ontology
19. Acceptance Criterion
20. Traceability Thread
(14, 15, 17, 18 are ★)

**Transformation (8/10):**
21. Constitutional Equation
22. Normalization Stage
23. Extraction Query
24. Template Emission
25. Canonicalization
26. Receipt Generation
27. Idempotent Transform
30. Human-Readable Artifact
(28, 29 are ★)

**Verification (8/8):**
31. Test Before Code
32. Contract Test
33. Integration Reality
34. Shape Validation
35. Drift Detection
36. Receipt Verification
37. Continuous Validation
38. Observable Execution

**Evolution (6/7):**
39. Feedback Loop
40. Outcome Measurement
41. Gap Analysis
42. Specification Refinement
44. Deprecation Path
45. Living Documentation
(43 is ★)

---

### ★ Promising Patterns (10 total)

These patterns represent best current thinking with less empirical validation. They're promising but may require adaptation to your context.

| # | Pattern | Why Promising | Risk Level |
|---|---------|---------------|------------|
| 14 | Property Path | Complex SPARQL feature, learning curve | Medium |
| 15 | Inference Rule | Powerful but can cause unexpected behavior | High |
| 17 | Domain-Specific Language | Significant investment, maintenance burden | Medium |
| 18 | Narrative Specification | Balance of formal/informal is subjective | Low |
| 28 | Partial Regeneration | Correctness vs. performance trade-off | Medium |
| 29 | Multi-Target Emission | Template proliferation risk | Low |
| 43 | Branching Exploration | Resource intensive, comparison complexity | High |

**Guidance for Promising Patterns:**
- Start small and validate in your context
- Have fallback plans if they don't work
- Consider them for optimization, not core infrastructure
- Document learnings to help mature these patterns

---

## Patterns by Difficulty Level

### Beginner Patterns (6 total)

Start here if you're new to specification-driven development. These patterns require minimal RDF/SHACL knowledge.

| # | Pattern | Time | Prerequisites |
|---|---------|------|---------------|
| 1 | Living System | 2-4h | Domain knowledge |
| 6 | Progress Maker | 2-4h | User access |
| 10 | Single Source of Truth | 1-2h | Basic version control |
| 13 | Vocabulary Boundary | 2-4h | Basic RDF concepts |

**Beginner Learning Path:**
```
1 → 6 → 10 → 13
Living System → Progress Maker → Single Source → Vocabulary Boundary
```

---

### Intermediate Patterns (31 total)

The bulk of the pattern language. Requires familiarity with RDF, SHACL, and SPARQL basics.

**Context:** 2, 3, 4, 5, 7, 8
**Specification:** 9, 11, 12, 16, 18, 19, 20
**Transformation:** 21, 22, 23, 24, 25, 26, 29, 30
**Verification:** 31, 32, 34, 35, 36, 37, 38
**Evolution:** 39, 40, 41, 42, 44, 45

**Intermediate Learning Path:**
```
2 → 5 → 9 → 11 → 12 → 21 → 31 → 37 → 39
Customer Job → Outcome → Semantic Foundation → Executable Spec →
Shape Constraint → Constitutional Equation → Test Before Code →
Continuous Validation → Feedback Loop
```

---

### Advanced Patterns (8 total)

These patterns require deep expertise and careful application. They offer power but also complexity.

| # | Pattern | Why Advanced | Prerequisites |
|---|---------|--------------|---------------|
| 14 | Property Path | Complex SPARQL navigation | SPARQL proficiency |
| 15 | Inference Rule | Reasoning systems, debugging | Logic programming |
| 17 | Domain-Specific Language | Parser/compiler design | Language design |
| 27 | Idempotent Transform | Subtle correctness issues | Pipeline mastery |
| 28 | Partial Regeneration | Dependency analysis | Build systems |
| 33 | Integration Reality | Test infrastructure | DevOps |
| 43 | Branching Exploration | Multi-variant management | CI/CD expertise |

**Advanced Learning Path:**
```
(Master intermediate first)
27 → 28 → 14 → 15 → 17 → 43
Idempotent → Partial → Property Path → Inference → DSL → Branching
```

---

## Patterns by Use Case

### Starting a New Capability

When building something entirely new, follow this sequence:

```
1 → 2 → 5 → 3 → 11 → 12 → 21 → 31 → 37 → 39

Living System:              Understand the ecosystem
       ↓
Customer Job:              Identify who needs what
       ↓
Outcome Desired:           Define success metrics
       ↓
Forces in Tension:         Map the trade-offs
       ↓
Executable Specification:  Write formal specs
       ↓
Shape Constraint:          Validate specs
       ↓
Constitutional Equation:   Generate artifacts
       ↓
Test Before Code:          Generate tests first
       ↓
Continuous Validation:     CI/CD pipeline
       ↓
Feedback Loop:             Close the loop
```

**Time estimate:** 2-4 weeks for foundation, ongoing for evolution

---

### Fixing a Broken Capability

When something isn't working, diagnose first:

```
35 → 36 → 38 → 41 → 42 → 21

Drift Detection:            Is the equation violated?
       ↓
Receipt Verification:       Are proofs valid?
       ↓
Observable Execution:       What does telemetry show?
       ↓
Gap Analysis:              Where are we falling short?
       ↓
Specification Refinement:   Update specs based on findings
       ↓
Constitutional Equation:    Regenerate artifacts
```

**Common causes of broken capabilities:**
- Manual edits to generated files (drift)
- Specification errors not caught by shapes
- Missing telemetry hiding problems
- Outcomes not matching customer needs

---

### Improving Performance

When optimization is needed:

```
38 → 40 → 41 → 43 → 42

Observable Execution:       Get baseline metrics
       ↓
Outcome Measurement:        Measure what matters
       ↓
Gap Analysis:              Identify bottlenecks
       ↓
Branching Exploration:      Try multiple approaches
       ↓
Specification Refinement:   Commit winning approach
```

**Performance improvement types:**
- **Latency**: Response time optimization
- **Throughput**: Volume handling
- **Resource usage**: Memory, CPU, storage
- **Reliability**: Error rates, availability

---

### Deprecating Old Capability

When retiring something:

```
44 → 45 → 42 → 7

Deprecation Path:           Plan the retirement
       ↓
Living Documentation:       Document the deprecation
       ↓
Specification Refinement:   Update specs with deprecation status
       ↓
Anxieties and Habits:       Address user concerns about transition
```

**Deprecation phases:**
1. **Soft deprecation**: Warnings, alternatives documented
2. **Hard deprecation**: Active warnings, migration tools
3. **Sunset**: No new usage allowed
4. **Removal**: Clean deletion

---

### Adding Documentation

When documentation needs improvement:

```
18 → 30 → 45 → 29

Narrative Specification:    Add human context to specs
       ↓
Human-Readable Artifact:    Design readable output
       ↓
Living Documentation:       Generate from specs
       ↓
Multi-Target Emission:      Multiple doc formats
```

**Documentation layers:**
- **Reference**: Generated API docs
- **Tutorial**: Hand-crafted learning paths
- **Conceptual**: Architecture and philosophy

---

### Migrating Legacy System

When converting existing systems:

```
1 → 6 → 10 → 9 → 11 → 35 → 37

Living System:              Map current state
       ↓
Progress Maker:             Document existing solutions
       ↓
Single Source of Truth:     Choose authoritative source
       ↓
Semantic Foundation:        Convert to RDF incrementally
       ↓
Executable Specification:   Make specs executable
       ↓
Drift Detection:            Verify consistency
       ↓
Continuous Validation:      Maintain quality
```

**Migration strategies:**
- **Big bang**: Convert everything at once (risky)
- **Strangler fig**: New capabilities use new approach
- **Incremental**: Convert piece by piece

---

## Pattern Quick Lookup by Need

| If you need to... | Use pattern(s) |
|-------------------|----------------|
| Understand users | 2, 4, 5, 7 |
| Map the ecosystem | 1, 6, 8 |
| Handle trade-offs | 3 |
| Write specifications | 9, 10, 11, 12 |
| Organize concepts | 13, 16 |
| Navigate relationships | 14, 20 |
| Derive facts | 15 |
| Simplify specs | 17, 18 |
| Define success | 5, 19 |
| Generate code | 21, 23, 24 |
| Generate docs | 29, 30, 45 |
| Ensure consistency | 25, 27 |
| Prove provenance | 26, 36 |
| Validate specs | 12, 22, 34 |
| Test implementation | 31, 32, 33 |
| Set up CI/CD | 35, 36, 37 |
| Monitor production | 38, 40 |
| Improve capability | 39, 41, 42 |
| Try alternatives | 43 |
| Retire capability | 44 |

---

## Pattern Dependency Summary

### Foundational Patterns (apply first)

```
9. Semantic Foundation    ← Everything builds on RDF
10. Single Source of Truth ← One source prevents drift
21. Constitutional Equation ← The governing principle
12. Shape Constraint       ← Validation prevents garbage-in
```

### Core Workflow Patterns (daily use)

```
11. Executable Specification ← What you write
22-26. Pipeline Stages       ← How it transforms
31. Test Before Code         ← How you verify
37. Continuous Validation    ← How you maintain
```

### Enhancement Patterns (add as needed)

```
14-15. Property Path, Inference ← Advanced querying
17-18. DSL, Narrative           ← Better ergonomics
28-29. Partial, Multi-Target    ← Scale optimizations
43. Branching Exploration       ← Experimentation
```

---

## Implementation Time Estimates

### Quick Wins (< 1 day each)

| Pattern | Time | Impact |
|---------|------|--------|
| 10. Single Source of Truth | 1-2h | Foundation |
| 1. Living System | 2-4h | Context |
| 13. Vocabulary Boundary | 2-4h | Organization |
| 21. Constitutional Equation | 2-4h | Principle |
| 25. Canonicalization | 2-4h | Consistency |

### Standard Effort (1-3 days each)

| Pattern | Time | Impact |
|---------|------|--------|
| 2. Customer Job | 4-8h | Understanding |
| 9. Semantic Foundation | 4-8h | Foundation |
| 12. Shape Constraint | 4-8h | Validation |
| 22-24. Pipeline Stages | 4-8h each | Transformation |
| 31-36. Verification | 4-8h each | Quality |

### Significant Investment (1+ weeks)

| Pattern | Time | Impact |
|---------|------|--------|
| 16. Layered Ontology | 8-16h | Architecture |
| 27. Idempotent Transform | 8-16h | Correctness |
| 17. Domain-Specific Language | 1-2w | Ergonomics |
| 28. Partial Regeneration | 1-2w | Performance |
| 43. Branching Exploration | 1-2w | Experimentation |

---

## Cross-Reference Matrix

### Which patterns are most connected?

| Pattern | Connections | Central To |
|---------|-------------|-----------|
| 21. Constitutional Equation | 15+ | Everything |
| 11. Executable Specification | 12+ | Specification |
| 37. Continuous Validation | 10+ | Verification |
| 5. Outcome Desired | 8+ | Context |
| 12. Shape Constraint | 8+ | Validation |

### Which patterns stand alone?

Some patterns can be applied with minimal dependencies:

| Pattern | Dependencies | Standalone Value |
|---------|--------------|------------------|
| 1. Living System | None | High |
| 6. Progress Maker | 1 | Medium |
| 18. Narrative Specification | 11 | Medium |
| 38. Observable Execution | 11 | High |

---

## Pattern Evolution Roadmap

### Currently ★, Targeting ★★

These patterns are being validated for promotion:

| Pattern | Blockers | Evidence Needed |
|---------|----------|-----------------|
| 14. Property Path | Adoption | More case studies |
| 18. Narrative Specification | Standardization | Best practices |
| 29. Multi-Target Emission | Complexity | Scaling evidence |

### Candidate New Patterns

Patterns under consideration for future versions:

| Candidate | Problem | Status |
|-----------|---------|--------|
| Schema Evolution | Versioning ontologies | Research |
| Federation | Distributed specifications | Experimental |
| Real-time Sync | Hot reloading | Prototype |

---

## Summary Statistics

| Category | Count | ★★ | ★ |
|----------|-------|-----|-----|
| Context | 8 | 8 | 0 |
| Specification | 12 | 9 | 3 |
| Transformation | 10 | 8 | 2 |
| Verification | 8 | 8 | 0 |
| Evolution | 7 | 6 | 1 |
| **Total** | **45** | **39** | **6** |

**Maturity**: 87% of patterns are well-established (★★)

---

## Final Notes

This index is itself a living document. As patterns mature, gain evidence, or reveal problems, this index evolves too. The goal isn't completeness—it's usefulness. Use whatever entry point serves your current need, then explore connections from there.

> *"A pattern language has the structure of a network... There is a tension between the wish to be complete, and the wish to be concise."*
> — Christopher Alexander, The Timeless Way of Building

The 45 patterns in this language represent a balanced vocabulary—enough to build complete capability systems, few enough to fit in a human head. Master the foundational patterns first, then expand your repertoire as needs arise.

---

**Next:** Explore **[Pattern Connections](./pattern-connections.md)** to understand how patterns relate to each other.
