# Pattern Connections

★★

*Patterns don't stand alone. They form a network of relationships—some patterns set context for others, some complete others, some are alternatives to each other. Understanding these connections is as important as understanding individual patterns.*

---

## The Network Nature of Pattern Languages

Christopher Alexander emphasized that a pattern language is not a collection of isolated solutions—it's a generative network. Patterns reference other patterns, build upon each other, and create something greater than their sum.

> *"Each pattern depends on other patterns to form a language—a web of interconnected solutions that together create a whole."*
> — Christopher Alexander

This section maps the connections between all 45 patterns in this language.

---

## Connection Types

Four types of relationships connect patterns:

### → Sets Context For (Arrow)

Pattern A → Pattern B means applying A creates the conditions that make B possible or necessary. A provides foundation; B builds on it.

*Example:* Pattern 9 (Semantic Foundation) → Pattern 12 (Shape Constraint)
: You need RDF as your foundation before you can define SHACL shapes that constrain it.

---

### ↔ Completed By (Double Arrow)

Pattern A ↔ Pattern B means these patterns work together—one is incomplete without the other. They're complementary pairs.

*Example:* Pattern 11 (Executable Specification) ↔ Pattern 12 (Shape Constraint)
: Executable specifications need shape constraints to validate them; shape constraints need specifications to constrain.

---

### ⟷ Alternative To (Long Double Arrow)

Pattern A ⟷ Pattern B means these patterns address similar problems with different approaches. Choose based on your context.

*Example:* Pattern 35 (Drift Detection) ⟷ Pattern 36 (Receipt Verification)
: Both detect violations of the constitutional equation, but through different mechanisms (regeneration comparison vs. cryptographic verification).

---

### ⊢ Verified By (Turnstile)

Pattern A ⊢ Pattern B means B checks, validates, or verifies A. B is the guardian of A's correctness.

*Example:* Pattern 21 (Constitutional Equation) ⊢ Pattern 36 (Receipt Verification)
: Receipt verification checks that the constitutional equation hasn't been violated.

---

## Part I: Context Pattern Connections

Context patterns form a discovery sequence, with each pattern revealing more about the problem space.

### Visual Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CONTEXT PATTERN CONNECTIONS                           │
│                                                                              │
│    ┌─────────────────┐                                                       │
│    │  1. Living      │                                                       │
│    │     System      │                                                       │
│    └────────┬────────┘                                                       │
│             │                                                                │
│             ├──────────────────────┬──────────────────────┐                  │
│             ▼                      ▼                      ▼                  │
│    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│    │  2. Customer    │    │  3. Forces      │    │  6. Progress    │        │
│    │     Job         │    │     in Tension  │    │     Maker       │        │
│    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘        │
│             │                      │                      │                  │
│             ├──────────────────────┼──────────────────────┤                  │
│             ▼                      │                      ▼                  │
│    ┌─────────────────┐             │             ┌─────────────────┐        │
│    │  4. Circumstance│             │             │  7. Anxieties   │        │
│    │     of Struggle │             │             │     and Habits  │        │
│    └────────┬────────┘             │             └────────┬────────┘        │
│             │                      │                      │                  │
│             └──────────────────────┼──────────────────────┘                  │
│                                    ▼                                         │
│                           ┌─────────────────┐                                │
│                           │  5. Outcome     │                                │
│                           │     Desired     │                                │
│                           └────────┬────────┘                                │
│                                    │                                         │
│                                    ▼                                         │
│                           ┌─────────────────┐                                │
│                           │  8. Competing   │                                │
│                           │     Solutions   │                                │
│                           └─────────────────┘                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Connections

**Pattern 1: Living System**

```
1. Living System
   │
   ├──→ 2. Customer Job
   │    (understand system to find jobs within it)
   │
   ├──→ 3. Forces in Tension
   │    (system reveals forces at play)
   │
   └──→ 6. Progress Maker
        (system contains existing solutions)
```

*Rationale:* You can't understand customer jobs without knowing the system they operate within. Forces emerge from system dynamics. Progress makers already exist in the system.

---

**Pattern 2: Customer Job**

```
2. Customer Job
   │
   ├──← 1. Living System (context)
   │
   ├──→ 4. Circumstance of Struggle
   │    (when and why job arises)
   │
   ├──→ 5. Outcome Desired
   │    (what success looks like)
   │
   └──↔ 6. Progress Maker
        (what helps with job today)
```

*Rationale:* Jobs exist in circumstances. Jobs have outcomes. Current progress makers address current jobs.

---

**Pattern 3: Forces in Tension**

```
3. Forces in Tension
   │
   ├──← 1. Living System (context)
   ├──← 2. Customer Job (job reveals forces)
   │
   ├──→ 5. Outcome Desired
   │    (outcomes balance forces)
   │
   └──→ 11. Executable Specification (Part II)
        (specs must accommodate forces)
```

*Rationale:* Forces create the tensions that make problems hard. Good outcomes resolve forces. Specifications must explicitly address force trade-offs.

---

**Pattern 4: Circumstance of Struggle**

```
4. Circumstance of Struggle
   │
   ├──← 2. Customer Job (instantiates job)
   │
   ├──→ 5. Outcome Desired
   │    (outcomes are circumstance-specific)
   │
   └──→ 19. Acceptance Criterion (Part II)
        (criteria address circumstances)
```

*Rationale:* Jobs arise in specific circumstances. What counts as success depends on circumstance. Acceptance criteria must reflect real circumstances.

---

**Pattern 5: Outcome Desired**

```
5. Outcome Desired
   │
   ├──← 2. Customer Job (outcomes express job progress)
   ├──← 3. Forces in Tension (outcomes balance forces)
   ├──← 4. Circumstance of Struggle (context)
   │
   ├──→ 6. Progress Maker
   │    (what makes progress possible)
   │
   ├──→ 19. Acceptance Criterion (Part II)
   │    (criteria derive from outcomes)
   │
   └──⊢ 40. Outcome Measurement (Part V)
        (track whether outcomes are achieved)
```

*Rationale:* Outcomes emerge from jobs, forces, and circumstances. Progress makers enable outcomes. Acceptance criteria operationalize outcomes. Measurement verifies achievement.

---

**Pattern 6: Progress Maker**

```
6. Progress Maker
   │
   ├──← 5. Outcome Desired (progress makers address outcomes)
   │
   ├──→ 7. Anxieties and Habits
   │    (current solutions shape habits)
   │
   └──→ 8. Competing Solutions
        (progress makers are competitors)
```

*Rationale:* Progress makers create habits and anxieties. Every progress maker competes with others.

---

**Pattern 7: Anxieties and Habits**

```
7. Anxieties and Habits
   │
   ├──← 6. Progress Maker (current solutions create habits)
   │
   ├──→ 8. Competing Solutions
   │    (anxieties are competitive barriers)
   │
   └──→ 30. Human-Readable Artifact (Part III)
        (address anxieties in output design)
```

*Rationale:* Habits favor existing solutions. Anxieties block new adoption. Generated artifacts should address user anxieties.

---

**Pattern 8: Competing Solutions**

```
8. Competing Solutions
   │
   ├──← 6. Progress Maker (progress makers are competitors)
   ├──← 7. Anxieties and Habits (habits favor incumbents)
   │
   └──→ 11. Executable Specification (Part II)
        (specs address competitive position)
```

*Rationale:* New capabilities compete with existing solutions. Specifications must define competitive advantage.

---

## Part II: Specification Pattern Connections

Specification patterns form the formal language layer, with vocabulary and constraints enabling executable specifications.

### Visual Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SPECIFICATION PATTERN CONNECTIONS                        │
│                                                                              │
│    ┌─────────────────┐                                                       │
│    │  9. Semantic    │                                                       │
│    │     Foundation  │                                                       │
│    └────────┬────────┘                                                       │
│             │                                                                │
│             ├──────────────────────┬──────────────────────┐                  │
│             ▼                      ▼                      ▼                  │
│    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│    │ 10. Single      │    │ 12. Shape       │    │ 13. Vocabulary  │        │
│    │     Source      │    │     Constraint  │    │     Boundary    │        │
│    └────────┬────────┘    └────────┬────────┘    └────────┬────────┘        │
│             │                      │                      │                  │
│             │                      │                      │                  │
│             └──────────────────────┼──────────────────────┘                  │
│                                    ▼                                         │
│                           ┌─────────────────┐                                │
│                           │ 11. Executable  │                                │
│                           │     Specification│                               │
│                           └────────┬────────┘                                │
│                                    │                                         │
│             ┌──────────────────────┼──────────────────────┐                  │
│             ▼                      ▼                      ▼                  │
│    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│    │ 14. Property    │    │ 16. Layered     │    │ 17. Domain-     │        │
│    │     Path        │    │     Ontology    │    │     Specific    │        │
│    └────────┬────────┘    └─────────────────┘    │     Language    │        │
│             │                                    └────────┬────────┘        │
│             │                                             │                  │
│             └──────────────────────┬──────────────────────┘                  │
│                                    ▼                                         │
│    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│    │ 15. Inference   │    │ 18. Narrative   │    │ 19. Acceptance  │        │
│    │     Rule        │◄───│     Specification│───►│     Criterion   │        │
│    └─────────────────┘    └─────────────────┘    └────────┬────────┘        │
│                                                           │                  │
│                                                           ▼                  │
│                                                  ┌─────────────────┐        │
│                                                  │ 20. Traceability│        │
│                                                  │     Thread      │        │
│                                                  └─────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Connections

**Pattern 9: Semantic Foundation**

```
9. Semantic Foundation
   │
   ├──→ 10. Single Source of Truth
   │    (RDF files become source)
   │
   ├──→ 12. Shape Constraint
   │    (SHACL validates RDF)
   │
   └──→ 13. Vocabulary Boundary
        (namespaces organize RDF)
```

*Rationale:* RDF enables single source, shape validation, and namespace organization.

---

**Pattern 10: Single Source of Truth**

```
10. Single Source of Truth
    │
    ├──← 9. Semantic Foundation (RDF as format)
    │
    ├──→ 11. Executable Specification
    │    (source must be executable)
    │
    ├──→ 21. Constitutional Equation (Part III)
    │    (artifacts from source)
    │
    └──⊢ 35. Drift Detection (Part IV)
         (detect divergence from source)
```

*Rationale:* Single source of truth is the foundation of the constitutional equation.

---

**Pattern 11: Executable Specification**

```
11. Executable Specification
    │
    ├──← 3. Forces in Tension (Part I)
    ├──← 8. Competing Solutions (Part I)
    ├──← 10. Single Source of Truth
    │
    ├──↔ 12. Shape Constraint
    │    (shapes make specs executable)
    │
    ├──→ 21. Constitutional Equation (Part III)
    │    (transformation of specs)
    │
    └──→ 31. Test Before Code (Part IV)
         (specs define tests)
```

*Rationale:* Executable specifications are the input to the constitutional equation.

---

**Pattern 12: Shape Constraint**

```
12. Shape Constraint
    │
    ├──← 9. Semantic Foundation (SHACL validates RDF)
    │
    ├──↔ 11. Executable Specification
    │    (execution via validation)
    │
    ├──↔ 16. Layered Ontology
    │    (shapes per layer)
    │
    ├──→ 22. Normalization Stage (Part III)
    │    (validation first in pipeline)
    │
    └──⊢ 34. Shape Validation (Part IV)
         (checking in CI)
```

*Rationale:* Shape constraints are the guards of specification quality.

---

**Pattern 13: Vocabulary Boundary**

```
13. Vocabulary Boundary
    │
    ├──← 9. Semantic Foundation (organizes foundation)
    │
    ├──→ 16. Layered Ontology
    │    (layers use vocabularies)
    │
    └──→ 20. Traceability Thread
         (cross-vocabulary links)
```

*Rationale:* Vocabulary boundaries enable layering and traceability.

---

**Pattern 14: Property Path**

```
14. Property Path
    │
    ├──→ 23. Extraction Query (Part III)
    │    (paths enhance extraction)
    │
    └──↔ 20. Traceability Thread
         (trace via paths)
```

*Rationale:* Property paths enable sophisticated graph navigation.

---

**Pattern 15: Inference Rule**

```
15. Inference Rule
    │
    ├──→ 11. Executable Specification
    │    (inference makes specs executable)
    │
    └──→ 23. Extraction Query (Part III)
         (queries see inferred facts)
```

*Rationale:* Inference expands what queries can discover.

---

**Pattern 16: Layered Ontology**

```
16. Layered Ontology
    │
    ├──← 13. Vocabulary Boundary (layers have vocabularies)
    │
    ├──↔ 12. Shape Constraint (shapes per layer)
    │
    └──→ 28. Partial Regeneration (Part III)
         (layer isolation enables partial)
```

*Rationale:* Layering organizes complexity and enables optimization.

---

**Pattern 17: Domain-Specific Language**

```
17. Domain-Specific Language
    │
    ├──← 9. Semantic Foundation (DSL over RDF)
    │
    ├──→ 18. Narrative Specification
    │    (DSL for narratives)
    │
    └──↔ 12. Shape Constraint
         (DSL validated by shapes)
```

*Rationale:* DSLs improve ergonomics while remaining valid RDF.

---

**Pattern 18: Narrative Specification**

```
18. Narrative Specification
    │
    ├──← 17. Domain-Specific Language (DSL for narratives)
    │
    ├──↔ 11. Executable Specification
    │    (narrative for formal)
    │
    ├──→ 30. Human-Readable Artifact (Part III)
    │    (narrative in output)
    │
    └──→ 45. Living Documentation (Part V)
         (docs stay current)
```

*Rationale:* Narrative preserves human understanding alongside formal precision.

---

**Pattern 19: Acceptance Criterion**

```
19. Acceptance Criterion
    │
    ├──← 4. Circumstance of Struggle (Part I)
    ├──← 5. Outcome Desired (Part I)
    │
    ├──→ 31. Test Before Code (Part IV)
    │    (criteria become tests)
    │
    ├──→ 40. Outcome Measurement (Part V)
    │    (criteria define metrics)
    │
    └──↔ 20. Traceability Thread
         (criteria linked to specs)
```

*Rationale:* Acceptance criteria bridge outcomes and tests.

---

**Pattern 20: Traceability Thread**

```
20. Traceability Thread
    │
    ├──← 13. Vocabulary Boundary (cross-vocabulary links)
    │
    ├──↔ 14. Property Path (trace via paths)
    ├──↔ 19. Acceptance Criterion (criteria traced)
    │
    ├──→ 26. Receipt Generation (Part III)
    │    (receipts are traces)
    │
    └──⊢ 35. Drift Detection (Part IV)
         (detect broken traces)
```

*Rationale:* Traceability connects all levels of abstraction.

---

## Part III: Transformation Pattern Connections

Transformation patterns form the μ pipeline, with clear stage ordering.

### Visual Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TRANSFORMATION PATTERN CONNECTIONS                        │
│                                                                              │
│    ┌─────────────────────────────────────────────────────────────────┐      │
│    │                                                                  │      │
│    │   ┌─────────────────┐                                           │      │
│    │   │ 21. Constitutional                                          │      │
│    │   │     Equation    │◄──────────────────────────────────────────┼─┐    │
│    │   └────────┬────────┘                                           │ │    │
│    │            │                                                    │ │    │
│    │            ▼                                                    │ │    │
│    │   ┌─────────────────┐    ┌─────────────────┐                   │ │    │
│    │   │ 22. Normaliza-  │───►│ 23. Extraction  │                   │ │    │
│    │   │     tion Stage  │    │     Query       │                   │ │    │
│    │   │     (μ₁)        │    │     (μ₂)        │                   │ │    │
│    │   └─────────────────┘    └────────┬────────┘                   │ │    │
│    │                                   │                            │ │    │
│    │                                   ▼                            │ │    │
│    │                          ┌─────────────────┐                   │ │    │
│    │                          │ 24. Template    │                   │ │    │
│    │                          │     Emission    │                   │ │    │
│    │                          │     (μ₃)        │                   │ │    │
│    │                          └────────┬────────┘                   │ │    │
│    │                                   │                            │ │    │
│    │            ┌──────────────────────┼──────────────────────┐     │ │    │
│    │            ▼                      ▼                      ▼     │ │    │
│    │   ┌─────────────────┐    ┌─────────────────┐    ┌────────────┐│ │    │
│    │   │ 25. Canonical-  │───►│ 26. Receipt     │    │ 29. Multi- ││ │    │
│    │   │     ization     │    │     Generation  │    │     Target ││ │    │
│    │   │     (μ₄)        │    │     (μ₅)        │    └────────────┘│ │    │
│    │   └────────┬────────┘    └─────────────────┘                   │ │    │
│    │            │                                                    │ │    │
│    │            └────────────────────────────────────────────────────┘ │    │
│    │                                                                    │    │
│    │   THE μ PIPELINE                                                   │    │
│    └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐        │
│    │ 27. Idempotent  │    │ 28. Partial     │    │ 30. Human-      │        │
│    │     Transform   │    │     Regeneration│    │     Readable    │        │
│    │                 │    │                 │    │     Artifact    │        │
│    └─────────────────┘    └─────────────────┘    └─────────────────┘        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Connections

**Pattern 21: Constitutional Equation**

```
21. Constitutional Equation
    │
    ├──← 10. Single Source of Truth (Part II)
    ├──← 11. Executable Specification (Part II)
    │
    ├──↔ 22-26. Pipeline Stages
    │    (implemented by stages)
    │
    ├──→ 27. Idempotent Transform
    │    (must be idempotent)
    │
    ├──⊢ 35. Drift Detection (Part IV)
    └──⊢ 36. Receipt Verification (Part IV)
         (equation verified)
```

*Rationale:* The constitutional equation is the governing principle, implemented by the pipeline and verified by detection.

---

**Pattern 22: Normalization Stage (μ₁)**

```
22. Normalization Stage
    │
    ├──← 12. Shape Constraint (Part II) (uses SHACL)
    │
    ├──→ 23. Extraction Query
    │    (validated input to extraction)
    │
    └──→ 26. Receipt Generation
         (validation hash in receipt)
```

*Rationale:* Normalization ensures valid input before extraction begins.

---

**Pattern 23: Extraction Query (μ₂)**

```
23. Extraction Query
    │
    ├──← 14. Property Path (Part II) (navigation syntax)
    ├──← 15. Inference Rule (Part II) (sees inferred facts)
    ├──← 22. Normalization Stage (receives validated RDF)
    │
    └──→ 24. Template Emission
         (data for templates)
```

*Rationale:* Extraction pulls data for template rendering.

---

**Pattern 24: Template Emission (μ₃)**

```
24. Template Emission
    │
    ├──← 23. Extraction Query (receives data)
    │
    ├──→ 25. Canonicalization
    │    (output needs normalizing)
    │
    ├──→ 29. Multi-Target Emission
    │    (multiple templates)
    │
    └──→ 30. Human-Readable Artifact
         (readable output)
```

*Rationale:* Templates produce artifacts that need canonicalization.

---

**Pattern 25: Canonicalization (μ₄)**

```
25. Canonicalization
    │
    ├──← 24. Template Emission (normalizes output)
    │
    ├──→ 26. Receipt Generation
    │    (canonical hash)
    │
    └──→ 27. Idempotent Transform
         (enables idempotence)
```

*Rationale:* Canonicalization ensures consistent output for hashing and comparison.

---

**Pattern 26: Receipt Generation (μ₅)**

```
26. Receipt Generation
    │
    ├──← 22-25. All Prior Stages (hashes each stage)
    │
    ├──→ 35. Drift Detection (Part IV)
    │    (enables detection)
    │
    └──⊢ 36. Receipt Verification (Part IV)
         (verified by)
```

*Rationale:* Receipts provide cryptographic proof of the transformation.

---

**Pattern 27: Idempotent Transform**

```
27. Idempotent Transform
    │
    ├──← 21. Constitutional Equation (property of μ)
    ├──← 25. Canonicalization (consistent formatting)
    │
    ├──↔ 28. Partial Regeneration
    │    (partial must match full)
    │
    ├──⊢ 35. Drift Detection (Part IV)
    │    (regeneration safe)
    │
    └──→ 37. Continuous Validation (Part IV)
         (CI can regenerate safely)
```

*Rationale:* Idempotence enables safe regeneration anytime.

---

**Pattern 28: Partial Regeneration**

```
28. Partial Regeneration
    │
    ├──← 16. Layered Ontology (Part II) (layer isolation)
    │
    ├──↔ 27. Idempotent Transform
    │    (partial must match full)
    │
    └──→ 37. Continuous Validation (Part IV)
         (fast CI)
```

*Rationale:* Partial regeneration trades completeness for speed.

---

**Pattern 29: Multi-Target Emission**

```
29. Multi-Target Emission
    │
    ├──← 24. Template Emission (multiple templates)
    │
    ├──→ 30. Human-Readable Artifact
    │    (various formats)
    │
    └──→ 45. Living Documentation (Part V)
         (docs synced with code)
```

*Rationale:* Multi-target enables one source, many outputs.

---

**Pattern 30: Human-Readable Artifact**

```
30. Human-Readable Artifact
    │
    ├──← 7. Anxieties and Habits (Part I)
    ├──← 18. Narrative Specification (Part II)
    ├──← 24. Template Emission
    │
    ├──→ 45. Living Documentation (Part V)
    │    (readable docs)
    │
    └──⊢ 35. Drift Detection (Part IV)
         (check not edited)
```

*Rationale:* Human-readable output bridges machine generation and human consumption.

---

## Part IV: Verification Pattern Connections

Verification patterns ensure the constitutional equation holds and capabilities work correctly.

### Visual Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      VERIFICATION PATTERN CONNECTIONS                        │
│                                                                              │
│                         ┌─────────────────┐                                  │
│                         │ 34. Shape       │                                  │
│                         │     Validation  │                                  │
│                         └────────┬────────┘                                  │
│                                  │                                           │
│    ┌─────────────────┐          │          ┌─────────────────┐              │
│    │ 31. Test        │          │          │ 35. Drift       │              │
│    │     Before Code │          │          │     Detection   │              │
│    └────────┬────────┘          │          └────────┬────────┘              │
│             │                   │                   │                        │
│             │                   │                   │                        │
│             ├───────────────────┼───────────────────┤                        │
│             │                   │                   │                        │
│             │                   ▼                   │                        │
│             │          ┌─────────────────┐         │                        │
│             │          │ 37. Continuous  │         │                        │
│             └─────────►│     Validation  │◄────────┘                        │
│                        └────────┬────────┘                                  │
│                                 │                                            │
│    ┌─────────────────┐         │          ┌─────────────────┐              │
│    │ 32. Contract    │         │          │ 36. Receipt     │              │
│    │     Test        │─────────┤          │     Verification│              │
│    └────────┬────────┘         │          └────────┬────────┘              │
│             │                  │                   │                        │
│             ▼                  │                   │                        │
│    ┌─────────────────┐        │          ┌─────────────────┐              │
│    │ 33. Integration │        │          │ 38. Observable  │              │
│    │     Reality     │────────┴─────────►│     Execution   │              │
│    └─────────────────┘                   └─────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Connections

**Pattern 31: Test Before Code**

```
31. Test Before Code
    │
    ├──← 11. Executable Specification (Part II)
    ├──← 19. Acceptance Criterion (Part II)
    ├──← 21. Constitutional Equation (Part III)
    │
    ├──↔ 32. Contract Test
    │    (different focus)
    │
    └──→ 37. Continuous Validation
         (tests in CI)
```

*Rationale:* Tests come from specifications before implementation.

---

**Pattern 32: Contract Test**

```
32. Contract Test
    │
    ├──← 11. Executable Specification (Part II)
    │
    ├──↔ 31. Test Before Code
    │    (complementary)
    │
    ├──→ 33. Integration Reality
    │    (contracts then integration)
    │
    └──→ 37. Continuous Validation
         (fast CI)
```

*Rationale:* Contract tests verify interfaces; integration tests verify reality.

---

**Pattern 33: Integration Reality**

```
33. Integration Reality
    │
    ├──← 32. Contract Test (after contracts)
    │
    ├──↔ 38. Observable Execution
    │    (real telemetry)
    │
    └──→ 37. Continuous Validation
         (CI integration tests)
```

*Rationale:* Integration tests with real dependencies reveal real problems.

---

**Pattern 34: Shape Validation**

```
34. Shape Validation
    │
    ├──⊢ 12. Shape Constraint (Part II)
    ├──⊢ 22. Normalization Stage (Part III)
    │
    ├──→ 35. Drift Detection
    │    (shapes prevent drift)
    │
    └──→ 37. Continuous Validation
         (CI validation)
```

*Rationale:* Shape validation is the first line of defense against invalid specifications.

---

**Pattern 35: Drift Detection**

```
35. Drift Detection
    │
    ├──⊢ 21. Constitutional Equation (Part III)
    ├──← 26. Receipt Generation (Part III)
    ├──← 27. Idempotent Transform (Part III)
    │
    ├──⟷ 36. Receipt Verification
    │    (alternative approaches)
    │
    └──→ 37. Continuous Validation
         (CI drift checks)
```

*Rationale:* Drift detection catches constitutional violations through regeneration.

---

**Pattern 36: Receipt Verification**

```
36. Receipt Verification
    │
    ├──⊢ 21. Constitutional Equation (Part III)
    ├──⊢ 26. Receipt Generation (Part III)
    │
    ├──⟷ 35. Drift Detection
    │    (alternative approach)
    │
    └──→ 37. Continuous Validation
         (CI verification)
```

*Rationale:* Receipt verification catches violations through cryptographic proof.

---

**Pattern 37: Continuous Validation**

```
37. Continuous Validation
    │
    ├──← 31. Test Before Code
    ├──← 32. Contract Test
    ├──← 33. Integration Reality
    ├──← 34. Shape Validation
    ├──← 35. Drift Detection
    ├──← 36. Receipt Verification
    │
    └──→ 39. Feedback Loop (Part V)
         (validation data feeds improvement)
```

*Rationale:* Continuous validation runs all checks at appropriate stages.

---

**Pattern 38: Observable Execution**

```
38. Observable Execution
    │
    ├──← 11. Executable Specification (Part II)
    │
    ├──↔ 33. Integration Reality
    │    (real telemetry)
    │
    ├──→ 39. Feedback Loop (Part V)
    │    (telemetry data)
    │
    └──→ 40. Outcome Measurement (Part V)
         (metrics for outcomes)
```

*Rationale:* Observable execution provides the data that drives improvement.

---

## Part V: Evolution Pattern Connections

Evolution patterns close the loop, connecting production reality back to specification improvement.

### Visual Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       EVOLUTION PATTERN CONNECTIONS                          │
│                                                                              │
│    ┌─────────────────────────────────────────────────────────────────────┐  │
│    │                                                                      │  │
│    │   ┌─────────────────┐                                               │  │
│    │   │ 39. Feedback    │◄──────────────────────────────────────────────┼──┤
│    │   │     Loop        │                                               │  │
│    │   └────────┬────────┘                                               │  │
│    │            │                                                        │  │
│    │            ▼                                                        │  │
│    │   ┌─────────────────┐                                               │  │
│    │   │ 40. Outcome     │                                               │  │
│    │   │     Measurement │                                               │  │
│    │   └────────┬────────┘                                               │  │
│    │            │                                                        │  │
│    │            ▼                                                        │  │
│    │   ┌─────────────────┐                                               │  │
│    │   │ 41. Gap         │                                               │  │
│    │   │     Analysis    │                                               │  │
│    │   └────────┬────────┘                                               │  │
│    │            │                                                        │  │
│    │            ├──────────────────────────┐                             │  │
│    │            ▼                          ▼                             │  │
│    │   ┌─────────────────┐        ┌─────────────────┐                   │  │
│    │   │ 42. Specification│       │ 43. Branching   │                   │  │
│    │   │     Refinement  │◄──────►│     Exploration │                   │  │
│    │   └────────┬────────┘        └─────────────────┘                   │  │
│    │            │                                                        │  │
│    │            └────────────────────────────────────────────────────────┼──┘
│    │                                                                      │
│    │   BUILD → MEASURE → LEARN → BUILD                                   │
│    └─────────────────────────────────────────────────────────────────────┘
│                                                                              │
│    ┌─────────────────┐                    ┌─────────────────┐              │
│    │ 44. Deprecation │───────────────────►│ 45. Living      │              │
│    │     Path        │                    │     Documentation│             │
│    └─────────────────┘                    └─────────────────┘              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Detailed Connections

**Pattern 39: Feedback Loop**

```
39. Feedback Loop
    │
    ├──← 37. Continuous Validation (Part IV)
    ├──← 38. Observable Execution (Part IV)
    │
    ├──→ 40. Outcome Measurement
    │    (measure outcomes)
    │
    ├──→ 42. Specification Refinement
    │    (drive improvements)
    │
    └──↔ 41. Gap Analysis
         (find gaps)
```

*Rationale:* Feedback loops connect production data to specification evolution.

---

**Pattern 40: Outcome Measurement**

```
40. Outcome Measurement
    │
    ├──⊢ 5. Outcome Desired (Part I)
    │    (outcomes measured)
    ├──← 19. Acceptance Criterion (Part II)
    ├──← 38. Observable Execution (Part IV)
    │
    ├──→ 41. Gap Analysis
    │    (find gaps)
    │
    └──→ 42. Specification Refinement
         (inform changes)
```

*Rationale:* Outcome measurement provides the data for gap analysis.

---

**Pattern 41: Gap Analysis**

```
41. Gap Analysis
    │
    ├──← 5. Outcome Desired (Part I)
    ├──← 40. Outcome Measurement
    │
    ├──→ 42. Specification Refinement
    │    (fix gaps)
    │
    └──→ 43. Branching Exploration
         (explore solutions)
```

*Rationale:* Gap analysis prioritizes improvements based on importance and current performance.

---

**Pattern 42: Specification Refinement**

```
42. Specification Refinement
    │
    ├──← 39. Feedback Loop
    ├──← 40. Outcome Measurement
    ├──← 41. Gap Analysis
    │
    ├──↔ 21. Constitutional Equation (Part III)
    │    (equation preserved)
    │
    ├──→ 43. Branching Exploration
    │    (try alternatives)
    │
    └──→ 45. Living Documentation
         (docs update)
```

*Rationale:* Specification refinement is the disciplined way to evolve specifications.

---

**Pattern 43: Branching Exploration**

```
43. Branching Exploration
    │
    ├──← 3. Forces in Tension (Part I)
    ├──← 21. Constitutional Equation (Part III)
    ├──← 40. Outcome Measurement
    ├──← 41. Gap Analysis
    │
    └──↔ 42. Specification Refinement
         (validated approaches)
```

*Rationale:* Branching exploration tries multiple approaches before committing.

---

**Pattern 44: Deprecation Path**

```
44. Deprecation Path
    │
    ├──← 42. Specification Refinement
    │    (new replaces old)
    │
    ├──↔ 7. Anxieties and Habits (Part I)
    │    (ease transition)
    │
    ├──→ 8. Competing Solutions (Part I)
    │    (position new vs old)
    │
    └──→ 45. Living Documentation
         (deprecation visible)
```

*Rationale:* Deprecation manages the retirement of capabilities.

---

**Pattern 45: Living Documentation**

```
45. Living Documentation
    │
    ├──← 18. Narrative Specification (Part II)
    ├──← 21. Constitutional Equation (Part III)
    ├──← 24. Template Emission (Part III)
    ├──← 29. Multi-Target Emission (Part III)
    ├──← 30. Human-Readable Artifact (Part III)
    ├──← 42. Specification Refinement
    └──← 44. Deprecation Path
```

*Rationale:* Living documentation is the ultimate proof of the constitutional equation—always current, always generated.

---

## Key Pattern Sequences

### The Core Sequence

The fundamental path through the pattern language:

```
Understanding → Specification → Transformation → Verification → Evolution

2 → 5 → 11 → 21 → 31 → 39 → 42 → (repeat)

Customer Job → Outcome Desired → Executable Specification →
Constitutional Equation → Test Before Code → Feedback Loop →
Specification Refinement → (repeat)
```

This sequence represents one complete cycle of Build-Measure-Learn adapted for specification-driven development.

---

### The Quality Sequence

Ensuring correctness at every level:

```
Constraints → Validation → Testing → Monitoring

12 → 34 → 31 → 37 → 38

Shape Constraint → Shape Validation → Test Before Code →
Continuous Validation → Observable Execution
```

---

### The Automation Sequence

Achieving full automation from source to production:

```
Single Source → Generation → Verification → Documentation

10 → 21 → 36 → 45

Single Source of Truth → Constitutional Equation →
Receipt Verification → Living Documentation
```

---

### The Discovery Sequence

Understanding before building:

```
System → Jobs → Circumstances → Outcomes → Competition

1 → 2 → 4 → 5 → 8

Living System → Customer Job → Circumstance of Struggle →
Outcome Desired → Competing Solutions
```

---

### The Improvement Sequence

Closing the feedback loop:

```
Observe → Measure → Analyze → Refine

38 → 40 → 41 → 42

Observable Execution → Outcome Measurement →
Gap Analysis → Specification Refinement
```

---

## Cross-Part Connections Summary

### Part I → Part II

| From (Context) | To (Specification) | Relationship |
|----------------|-------------------|--------------|
| 3. Forces in Tension | 11. Executable Specification | → |
| 4. Circumstance | 19. Acceptance Criterion | → |
| 5. Outcome Desired | 19. Acceptance Criterion | → |
| 8. Competing Solutions | 11. Executable Specification | → |

---

### Part II → Part III

| From (Specification) | To (Transformation) | Relationship |
|---------------------|---------------------|--------------|
| 10. Single Source | 21. Constitutional Equation | → |
| 11. Executable Spec | 21. Constitutional Equation | → |
| 12. Shape Constraint | 22. Normalization Stage | → |
| 14. Property Path | 23. Extraction Query | → |
| 15. Inference Rule | 23. Extraction Query | → |
| 16. Layered Ontology | 28. Partial Regeneration | → |
| 18. Narrative Spec | 30. Human-Readable Artifact | → |
| 20. Traceability | 26. Receipt Generation | → |

---

### Part III → Part IV

| From (Transformation) | To (Verification) | Relationship |
|----------------------|-------------------|--------------|
| 21. Constitutional Equation | 35. Drift Detection | ⊢ |
| 21. Constitutional Equation | 36. Receipt Verification | ⊢ |
| 26. Receipt Generation | 35. Drift Detection | → |
| 26. Receipt Generation | 36. Receipt Verification | ⊢ |
| 27. Idempotent Transform | 35. Drift Detection | ⊢ |
| 27. Idempotent Transform | 37. Continuous Validation | → |
| 28. Partial Regeneration | 37. Continuous Validation | → |

---

### Part IV → Part V

| From (Verification) | To (Evolution) | Relationship |
|--------------------|----------------|--------------|
| 37. Continuous Validation | 39. Feedback Loop | → |
| 38. Observable Execution | 39. Feedback Loop | → |
| 38. Observable Execution | 40. Outcome Measurement | → |

---

### Part V → Other Parts

| From (Evolution) | To (Other Part) | Relationship |
|-----------------|-----------------|--------------|
| 40. Outcome Measurement | 5. Outcome Desired (I) | ⊢ |
| 42. Spec Refinement | 21. Constitutional Equation (III) | ↔ |
| 44. Deprecation Path | 7. Anxieties and Habits (I) | ↔ |
| 44. Deprecation Path | 8. Competing Solutions (I) | → |

---

## Using This Map

### When Starting Fresh

Follow the Core Sequence from Pattern 2 through Pattern 42, applying patterns in order.

### When Diagnosing Problems

1. Start with verification patterns (35, 36, 38) to understand current state
2. Use gap analysis (41) to identify problems
3. Apply specification refinement (42) to fix

### When Adding New Features

1. Start with context patterns (1-8) to understand the need
2. Define in specification patterns (9-20)
3. Transform with patterns (21-30)
4. Verify with patterns (31-38)
5. Evolve with patterns (39-45)

### When Improving Performance

Follow the Improvement Sequence: 38 → 40 → 41 → 42 (→ optionally 43)

---

## Summary

The 45 patterns in this language form a dense network of 100+ connections. Understanding these connections is essential—patterns derive their power not from isolation but from integration.

Key insights:

1. **The constitutional equation (21) is the hub** — More patterns connect to it than any other
2. **Context patterns feed specification patterns** — Understanding enables definition
3. **Transformation is linear but verification is parallel** — The pipeline is ordered; checks run together
4. **Evolution closes the loop** — Production reality feeds back to specification

> *"When you build a thing you cannot merely build that thing in isolation, but must also repair the world around it, and within it, so that the larger world at that one place becomes more coherent, and more whole."*
> — Christopher Alexander

The pattern connections ensure that building capabilities repairs and enhances the larger system of specification-driven development.

---

## Code References

The spec-kit codebase demonstrates these pattern connections:

| Connection | Source Files |
|------------|--------------|
| Constitutional Equation → Receipt | `ontology/cli-commands.ttl:10` → `src/specify_cli/runtime/receipt.py:112-156` |
| Shape Constraint → Normalization | `ontology/spec-kit-schema.ttl:466-516` → validation pipeline |
| Property Path → Extraction | SPARQL paths in `sparql/extract-commands.rq:14-20` |
| Emission → Human-Readable | `templates/command.tera:7-32` (provenance headers) |
| Observable Execution → Feedback | `src/specify_cli/core/telemetry.py` → metrics |

---

**Next:** Use the **[Pattern Index](./pattern-index.md)** to find specific patterns by number or use case.
