# Explanation: Spec-Driven Development Philosophy

**Time to understand:** 20-25 minutes

## Core Belief

**Specifications should be the source of truth.**

Not code. Not documentation. **Specifications.**

### Why?

```
Code is implementation detail
  → Can have bugs
  → Can be misunderstood
  → Can drift from intent

Documentation is often wrong
  → Gets outdated
  → Often incomplete
  → Hard to verify

Specifications are unambiguous
  → Machine-verifiable
  → Can auto-generate correct code
  → Single source of truth
```

## The Shift

### Before (Traditional)

```
Ideas → Requirements → Design → Code → Tests → Docs

Problems:
- Each step introduces ambiguity
- Drift between phases
- Lots of manual work
- Errors accumulate
```

### After (Spec-Driven)

```
Specification (RDF)
    ↓ (ggen transformation)
Code + Tests + Docs (all from spec)

Benefits:
- No drift possible
- Minimal manual work
- Single source of truth
- Everything verifiable
```

## The Philosophy in Four Principles

### Principle 1: Specifications Are Executable

Specs aren't just documents to read.
**They should generate working code.**

```
RDF spec → ggen sync → Working code + tests + docs
```

### Principle 2: Single Source of Truth

Everything flows from one place: the RDF spec.

```
Change spec → Everything updates (code, tests, docs)
```

### Principle 3: Verifiable Alignment

Code, specs, and docs should be verifiable as aligned.

```
SHA256(spec) == SHA256(code) == SHA256(docs)
→ Proof of perfect alignment
```

### Principle 4: Minimize Manual Work

Let machines generate what they can.
Humans focus on business logic.

```
Machines: Generate boilerplate, tests, docs
Humans: Implement business logic, tests, edge cases
```

## Benefits

### For Developers
- Write spec once
- Code generates automatically
- Tests verify the spec
- Documentation is current
- Focus on logic, not boilerplate

### For Teams
- Single source of truth
- Clear contracts (specs)
- Automated integration
- Consistent patterns
- Easy onboarding

### For Product
- Features clearly defined
- Impact measurable
- Roadmap explicit
- Commitments verifiable

### For Quality
- No documentation drift
- Tests validate specs
- Specification violations caught early
- Perfect code-spec alignment

## The Constitutional Equation

```
spec.md = μ(feature.ttl)

"Markdown documentation is generated from RDF specifications"
```

This encapsulates the entire philosophy:
- **RDF** is the source (feature.ttl)
- **μ** is the transformation (deterministic, verifiable)
- **Markdown** is the output (generated from source)

**Everything flows from specs.**

## Comparison with Alternatives

### Code-First Development
```
Write code first
→ Specs describe code
→ Tests verify code
→ Docs describe code

Problem: Code and specs drift over time
```

### Model-Driven Development
```
Write model first
→ Generate code from model
→ Keep code and model in sync

Similar to spec-driven but less emphasis on documentation
```

### Spec-Driven Development (Our Approach)
```
Write RDF spec first
→ Generate code + tests + docs from spec
→ Perfect alignment guaranteed
→ No drift possible
```

## Cultural Change

### From "Does code match spec?" 
### To "Code is generated from spec"

### From "Keep docs updated"
### To "Docs generated from spec"

### From "Write tests to verify code"
### To "Generate tests from spec"

## Implementation

Spec-driven development requires:
1. **RDF to express specifications** (unambiguous, machine-readable)
2. **Transformation pipeline** (reliable, deterministic)
3. **Code generation** (correct, consistent)
4. **Verification** (proofs, receipts)

That's what Spec Kit provides.

## See Also
- [Explanation: Constitutional Equation](./constitutional-equation.md)
- [Explanation: RDF-First Development](./rdf-first-development.md)
- [Explanation: Three-Tier Architecture](./three-tier-architecture.md)
