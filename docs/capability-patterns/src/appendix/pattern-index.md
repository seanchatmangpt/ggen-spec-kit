# Pattern Index

Quick reference for all 45 patterns in this pattern language.

---

## Part I: Context Patterns

Understanding the territory before building.

| # | Pattern | Confidence | Summary |
|---|---------|------------|---------|
| 1 | [Living System](../context/living-system.md) | ★★ | Understand the system your capability will join |
| 2 | [Customer Job](../context/customer-job.md) | ★★ | Identify what progress customers seek |
| 3 | [Forces in Tension](../context/forces-in-tension.md) | ★★ | Map the tensions that make problems difficult |
| 4 | [Circumstance of Struggle](../context/circumstance-of-struggle.md) | ★★ | Identify when and why struggle occurs |
| 5 | [Outcome Desired](../context/outcome-desired.md) | ★★ | Define measurable success criteria |
| 6 | [Progress Maker](../context/progress-maker.md) | ★★ | Catalog existing solutions |
| 7 | [Anxieties and Habits](../context/anxieties-and-habits.md) | ★★ | Understand resistance to change |
| 8 | [Competing Solutions](../context/competing-solutions.md) | ★★ | Analyze the competitive landscape |

---

## Part II: Specification Patterns

The grammar of capability definition.

| # | Pattern | Confidence | Summary |
|---|---------|------------|---------|
| 9 | [Semantic Foundation](../specification/semantic-foundation.md) | ★★ | Choose RDF as your representation |
| 10 | [Single Source of Truth](../specification/single-source-of-truth.md) | ★★ | One authoritative location for knowledge |
| 11 | [Executable Specification](../specification/executable-specification.md) | ★★ | Specs that validate, extract, and generate |
| 12 | [Shape Constraint](../specification/shape-constraint.md) | ★★ | SHACL shapes for validation |
| 13 | [Vocabulary Boundary](../specification/vocabulary-boundary.md) | ★★ | Namespaces for domain separation |
| 14 | [Property Path](../specification/property-path.md) | ★ | SPARQL paths for graph navigation |
| 15 | [Inference Rule](../specification/inference-rule.md) | ★ | Derive facts from existing knowledge |
| 16 | [Layered Ontology](../specification/layered-ontology.md) | ★★ | Organize concepts by abstraction level |
| 17 | [Domain-Specific Language](../specification/domain-specific-language.md) | ★ | Simplify common specification tasks |
| 18 | [Narrative Specification](../specification/narrative-specification.md) | ★ | Embed human context in formal specs |
| 19 | [Acceptance Criterion](../specification/acceptance-criterion.md) | ★★ | Define testable conditions for done |
| 20 | [Traceability Thread](../specification/traceability-thread.md) | ★★ | Link artifacts across levels |

---

## Part III: Transformation Patterns

The art of faithful generation.

| # | Pattern | Confidence | Summary |
|---|---------|------------|---------|
| 21 | [Constitutional Equation](../transformation/constitutional-equation.md) | ★★ | spec.md = μ(feature.ttl) |
| 22 | [Normalization Stage](../transformation/normalization-stage.md) | ★★ | μ₁: Validate before transforming |
| 23 | [Extraction Query](../transformation/extraction-query.md) | ★★ | μ₂: SPARQL for data extraction |
| 24 | [Template Emission](../transformation/template-emission.md) | ★★ | μ₃: Tera templates for generation |
| 25 | [Canonicalization](../transformation/canonicalization.md) | ★★ | μ₄: Normalize output format |
| 26 | [Receipt Generation](../transformation/receipt-generation.md) | ★★ | μ₅: Cryptographic proof |
| 27 | [Idempotent Transform](../transformation/idempotent-transform.md) | ★★ | μ ∘ μ = μ |
| 28 | [Partial Regeneration](../transformation/partial-regeneration.md) | ★ | Regenerate only affected artifacts |
| 29 | [Multi-Target Emission](../transformation/multi-target-emission.md) | ★ | One spec, many output formats |
| 30 | [Human-Readable Artifact](../transformation/human-readable-artifact.md) | ★★ | Generated output for human consumption |

---

## Part IV: Verification Patterns

Ensuring the capability lives and breathes.

| # | Pattern | Confidence | Summary |
|---|---------|------------|---------|
| 31 | [Test Before Code](../verification/test-before-code.md) | ★★ | Tests from specs before implementation |
| 32 | [Contract Test](../verification/contract-test.md) | ★★ | Verify interface contracts |
| 33 | [Integration Reality](../verification/integration-reality.md) | ★★ | Test with real dependencies |
| 34 | [Shape Validation](../verification/shape-validation.md) | ★★ | SHACL validation in practice |
| 35 | [Drift Detection](../verification/drift-detection.md) | ★★ | Catch modified generated files |
| 36 | [Receipt Verification](../verification/receipt-verification.md) | ★★ | Verify cryptographic proofs |
| 37 | [Continuous Validation](../verification/continuous-validation.md) | ★★ | Validation at every stage |
| 38 | [Observable Execution](../verification/observable-execution.md) | ★★ | Telemetry for understanding |

---

## Part V: Evolution Patterns

The capability that learns and grows.

| # | Pattern | Confidence | Summary |
|---|---------|------------|---------|
| 39 | [Feedback Loop](../evolution/feedback-loop.md) | ★★ | Connect production to specification |
| 40 | [Outcome Measurement](../evolution/outcome-measurement.md) | ★★ | Track customer progress metrics |
| 41 | [Gap Analysis](../evolution/gap-analysis.md) | ★★ | Identify improvement opportunities |
| 42 | [Specification Refinement](../evolution/specification-refinement.md) | ★★ | Disciplined spec evolution |
| 43 | [Branching Exploration](../evolution/branching-exploration.md) | ★ | Try multiple implementation approaches |
| 44 | [Deprecation Path](../evolution/deprecation-path.md) | ★★ | Graceful capability retirement |
| 45 | [Living Documentation](../evolution/living-documentation.md) | ★★ | Docs generated from specs |

---

## Patterns by Confidence

### ★★ Well-Established (35 patterns)

These patterns have substantial evidence of success across multiple contexts.

1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44, 45

### ★ Promising (10 patterns)

These patterns represent best current thinking with less empirical validation.

14, 15, 17, 18, 28, 29, 43

---

## Patterns by Use Case

### Starting a New Capability

1 → 2 → 5 → 11 → 21 → 31 → 39

### Fixing a Broken Capability

35 → 36 → 41 → 42 → 21

### Improving Performance

38 → 40 → 41 → 43 → 42

### Deprecating Old Capability

44 → 45 → 42

### Adding Documentation

18 → 30 → 45

---

## Pattern Quick Lookup

| Need | Pattern(s) |
|------|------------|
| Understanding users | 2, 4, 5, 7 |
| Writing specifications | 9, 10, 11, 12 |
| Generating code | 21, 23, 24 |
| Generating docs | 29, 30, 45 |
| Validating specs | 12, 22, 34 |
| Testing | 31, 32, 33 |
| CI/CD | 35, 36, 37 |
| Observability | 38 |
| Improvement | 39, 40, 41 |
| Changes | 42, 44 |
