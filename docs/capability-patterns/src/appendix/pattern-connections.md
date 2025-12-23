# Pattern Connections

Patterns don't stand alone. They form a network of relationships—some patterns set context for others, some complete others, some are alternatives to each other.

---

## Connection Types

### Sets Context For (→)

A pattern provides the foundation for another. Apply the first to enable the second.

### Completed By (↔)

Patterns that work together. One is incomplete without the other.

### Alternative To (⟷)

Patterns addressing similar problems with different approaches.

### Verified By (⊢)

A pattern that checks or validates another.

---

## Part I: Context Patterns

```
1. Living System
   → 2. Customer Job (understand system to find jobs)
   → 3. Forces in Tension (system reveals forces)

2. Customer Job
   ← 1. Living System (context)
   → 4. Circumstance of Struggle (when job arises)
   → 5. Outcome Desired (how to measure success)
   ↔ 6. Progress Maker (what helps today)

3. Forces in Tension
   ← 1. Living System (context)
   ← 2. Customer Job (job reveals forces)
   → 5. Outcome Desired (outcomes balance forces)
   → 11. Executable Specification (specs accommodate forces)

4. Circumstance of Struggle
   ← 2. Customer Job (instantiates job)
   → 5. Outcome Desired (outcomes are circumstance-specific)
   → 19. Acceptance Criterion (criteria address circumstances)

5. Outcome Desired
   ← 2. Customer Job (outcomes express job progress)
   ← 4. Circumstance of Struggle (context)
   → 6. Progress Maker (what makes progress possible)
   → 19. Acceptance Criterion (criteria derive from outcomes)
   ⊢ 40. Outcome Measurement (track outcome delivery)

6. Progress Maker
   ← 5. Outcome Desired (progress makers address outcomes)
   → 8. Competing Solutions (progress makers compete)
   → 7. Anxieties and Habits (current solutions shape habits)

7. Anxieties and Habits
   ← 6. Progress Maker (current solutions create habits)
   → 8. Competing Solutions (anxieties are competitive barriers)
   → 30. Human-Readable Artifact (address anxieties in output)

8. Competing Solutions
   ← 6. Progress Maker (progress makers are competitors)
   ← 7. Anxieties and Habits (habits favor incumbents)
   → 11. Executable Specification (specs address competitive position)
```

---

## Part II: Specification Patterns

```
9. Semantic Foundation
   → 10. Single Source of Truth (RDF files become source)
   → 12. Shape Constraint (SHACL validates)
   → 13. Vocabulary Boundary (namespaces organize)

10. Single Source of Truth
   ← 9. Semantic Foundation (RDF as format)
   → 11. Executable Specification (source drives generation)
   → 21. Constitutional Equation (artifacts from source)
   ⊢ 35. Drift Detection (detect divergence)

11. Executable Specification
   ← 10. Single Source of Truth (must be executable)
   ↔ 12. Shape Constraint (shapes make executable)
   → 21. Constitutional Equation (transformation of specs)
   → 31. Test Before Code (specs define tests)

12. Shape Constraint
   ↔ 11. Executable Specification (execution via validation)
   → 22. Normalization Stage (validation first)
   ⊢ 34. Shape Validation (checking in CI)

13. Vocabulary Boundary
   ← 9. Semantic Foundation (organizes foundation)
   → 16. Layered Ontology (layers use vocabularies)
   → 20. Traceability Thread (cross-vocabulary links)

14. Property Path
   → 23. Extraction Query (paths enhance extraction)
   ↔ 20. Traceability Thread (trace via paths)

15. Inference Rule
   → 11. Executable Specification (inference executes)
   → 23. Extraction Query (queries see inferred facts)

16. Layered Ontology
   ← 13. Vocabulary Boundary (layers have vocabularies)
   ↔ 12. Shape Constraint (shapes per layer)
   → 28. Partial Regeneration (layer isolation)

17. Domain-Specific Language
   ← 9. Semantic Foundation (DSL over RDF)
   → 18. Narrative Specification (DSL for narratives)
   ↔ 12. Shape Constraint (DSL validated by shapes)

18. Narrative Specification
   ↔ 11. Executable Specification (narrative for formal)
   → 30. Human-Readable Artifact (narrative in output)
   → 45. Living Documentation (docs stay current)

19. Acceptance Criterion
   ← 5. Outcome Desired (criteria address outcomes)
   → 31. Test Before Code (criteria become tests)
   → 40. Outcome Measurement (criteria define metrics)
   ↔ 20. Traceability Thread (criteria linked to specs)

20. Traceability Thread
   ← 13. Vocabulary Boundary (cross-vocabulary links)
   ↔ 19. Acceptance Criterion (criteria traced)
   → 26. Receipt Generation (receipts are traces)
   ⊢ 35. Drift Detection (detect broken traces)
```

---

## Part III: Transformation Patterns

```
21. Constitutional Equation
   ← 10. Single Source of Truth (requires single source)
   ↔ 22-26. Pipeline Stages (implemented by)
   → 27. Idempotent Transform (must be idempotent)
   ⊢ 36. Receipt Verification (equation verified)

22. Normalization Stage (μ₁)
   ← 12. Shape Constraint (uses SHACL)
   → 23. Extraction Query (validated input)
   → 26. Receipt Generation (validation hash)

23. Extraction Query (μ₂)
   ← 22. Normalization Stage (receives validated RDF)
   ↔ 14. Property Path (navigation syntax)
   → 24. Template Emission (data for templates)

24. Template Emission (μ₃)
   ← 23. Extraction Query (receives data)
   → 25. Canonicalization (output needs normalizing)
   → 29. Multi-Target Emission (multiple templates)

25. Canonicalization (μ₄)
   ← 24. Template Emission (normalizes output)
   → 26. Receipt Generation (canonical hash)
   → 27. Idempotent Transform (consistency)

26. Receipt Generation (μ₅)
   ← 22-25. All Stages (hashes each stage)
   ⊢ 36. Receipt Verification (verified by)
   → 35. Drift Detection (enables detection)

27. Idempotent Transform
   ← 21. Constitutional Equation (property of μ)
   ← 25. Canonicalization (consistent formatting)
   ⊢ 35. Drift Detection (regeneration safe)
   → 37. Continuous Validation (CI checks)

28. Partial Regeneration
   ← 16. Layered Ontology (layer isolation)
   ↔ 27. Idempotent Transform (partial must match full)
   → 37. Continuous Validation (fast CI)

29. Multi-Target Emission
   ← 24. Template Emission (multiple templates)
   → 30. Human-Readable Artifact (various formats)
   → 45. Living Documentation (docs synced)

30. Human-Readable Artifact
   ← 24. Template Emission (templates produce readable)
   ← 18. Narrative Specification (narrative in output)
   → 45. Living Documentation (readable docs)
   ⊢ 35. Drift Detection (check not edited)
```

---

## Part IV: Verification Patterns

```
31. Test Before Code
   ← 19. Acceptance Criterion (criteria become tests)
   ← 21. Constitutional Equation (tests are artifacts)
   → 37. Continuous Validation (tests in CI)
   ↔ 32. Contract Test (different focus)

32. Contract Test
   ↔ 31. Test Before Code (complementary)
   → 33. Integration Reality (contracts then integration)
   → 37. Continuous Validation (fast CI)
   ← 11. Executable Specification (specs define contracts)

33. Integration Reality
   ← 32. Contract Test (after contracts)
   → 37. Continuous Validation (CI integration tests)
   ↔ 38. Observable Execution (real telemetry)

34. Shape Validation
   ⊢ 12. Shape Constraint (enforces shapes)
   ⊢ 22. Normalization Stage (validation in pipeline)
   → 37. Continuous Validation (CI validation)
   → 35. Drift Detection (shapes prevent drift)

35. Drift Detection
   ⊢ 21. Constitutional Equation (equation enforced)
   ← 26. Receipt Generation (receipts enable)
   → 37. Continuous Validation (CI drift checks)
   ↔ 27. Idempotent Transform (regeneration safe)

36. Receipt Verification
   ⊢ 26. Receipt Generation (receipts checked)
   ↔ 35. Drift Detection (different approach)
   → 37. Continuous Validation (CI verification)
   ⊢ 21. Constitutional Equation (equation verified)

37. Continuous Validation
   ← 34. Shape Validation (SHACL in CI)
   ← 35. Drift Detection (drift in CI)
   ← 36. Receipt Verification (receipts in CI)
   → 39. Feedback Loop (validation data)

38. Observable Execution
   → 40. Outcome Measurement (metrics for outcomes)
   → 39. Feedback Loop (telemetry data)
   ⊢ 33. Integration Reality (real telemetry)
   ← 11. Executable Specification (telemetry specified)
```

---

## Part V: Evolution Patterns

```
39. Feedback Loop
   ← 38. Observable Execution (telemetry)
   → 40. Outcome Measurement (measure outcomes)
   → 42. Specification Refinement (drive improvements)
   ↔ 41. Gap Analysis (find gaps)

40. Outcome Measurement
   ⊢ 5. Outcome Desired (outcomes measured)
   ← 38. Observable Execution (telemetry)
   → 41. Gap Analysis (find gaps)
   → 42. Specification Refinement (inform changes)

41. Gap Analysis
   ← 40. Outcome Measurement (current performance)
   → 42. Specification Refinement (fix gaps)
   → 43. Branching Exploration (explore solutions)
   ← 5. Outcome Desired (targets defined)

42. Specification Refinement
   ← 41. Gap Analysis (identifies needs)
   ↔ 21. Constitutional Equation (equation preserved)
   → 43. Branching Exploration (try alternatives)
   → 45. Living Documentation (docs update)

43. Branching Exploration
   ← 42. Specification Refinement (validated approaches)
   ← 40. Outcome Measurement (compare variants)
   ← 21. Constitutional Equation (generation enables)
   ← 3. Forces in Tension (trade-offs to balance)

44. Deprecation Path
   ← 42. Specification Refinement (new replaces old)
   → 45. Living Documentation (deprecation visible)
   ↔ 7. Anxieties and Habits (ease transition)
   → 8. Competing Solutions (position new vs old)

45. Living Documentation
   ← 21. Constitutional Equation (docs as artifact)
   ← 18. Narrative Specification (human content)
   ← 24. Template Emission (doc generation)
   ← 44. Deprecation Path (deprecation visible)
```

---

## Key Pattern Sequences

### The Core Sequence

Understanding → Specification → Transformation → Verification → Evolution

```
2 → 5 → 11 → 21 → 31 → 39 → 42 → (repeat)
```

### The Quality Sequence

Constraints → Validation → Testing → Monitoring

```
12 → 34 → 31 → 37 → 38
```

### The Automation Sequence

Single Source → Generation → Verification → Documentation

```
10 → 21 → 36 → 45
```
