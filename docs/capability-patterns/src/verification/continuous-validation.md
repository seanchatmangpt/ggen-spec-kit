# 37. Continuous Validation

★★

*Validation isn't a phase—it's continuous. Continuous validation runs checks at every stage: commit, push, pull request, merge, deploy.*

---

Traditional validation happens at milestones: code review, QA phase, release testing. Between milestones, quality can degrade.

Continuous validation closes these gaps. Every change triggers validation. Every push verifies consistency. Every merge confirms compliance.

In specification-driven development, continuous validation checks:
- Specification validity (SHACL shapes)
- Transformation correctness (receipts, idempotence)
- Test passage (generated tests)
- Drift absence (source-artifact consistency)

**The problem: Periodic validation allows problems to accumulate. Continuous validation catches problems when they're introduced.**

---

**The forces at play:**

- *Speed wants minimal checks.* Fast pipelines encourage commits.

- *Quality wants comprehensive checks.* More checks catch more problems.

- *Developer experience wants fast feedback.* Slow CI frustrates developers.

- *Confidence wants thoroughness.* Critical paths need full validation.

The tension: fast enough to not slow development, thorough enough to catch problems.

---

**Therefore:**

Implement tiered continuous validation that runs appropriate checks at each pipeline stage.

**Validation tiers:**

```
Tier 1: Local (pre-commit)        │ Seconds
  • File linting                  │
  • Basic syntax check            │
  • Local test subset             │
                                  │
Tier 2: Push (CI fast)            │ Minutes
  • Full lint                     │
  • SHACL validation              │
  • Unit tests                    │
  • Contract tests                │
  • Drift detection               │
                                  │
Tier 3: Pull Request (CI full)    │ Minutes
  • All Tier 2 checks             │
  • Integration tests             │
  • Receipt verification          │
  • Regeneration check            │
                                  │
Tier 4: Merge to Main            │ Minutes-Hours
  • All Tier 3 checks             │
  • Full integration tests        │
  • Performance tests             │
  • Security scans                │
                                  │
Tier 5: Release                   │ Hours
  • All Tier 4 checks             │
  • Full regeneration verify      │
  • End-to-end tests              │
  • Manual approval gates         │
```

**Pre-commit hook:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: validate-rdf
        name: Validate RDF specifications
        entry: specify validate ontology/*.ttl
        language: system
        files: '\.ttl$'

      - id: check-drift
        name: Check for artifact drift
        entry: ggen verify --level hash
        language: system
        pass_filenames: false
```

**GitHub Actions workflow:**

```yaml
# .github/workflows/ci.yml
name: Continuous Validation

on: [push, pull_request]

jobs:
  tier2-fast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: uv sync

      - name: Lint
        run: uv run ruff check src/

      - name: Type check
        run: uv run mypy src/

      - name: SHACL validation
        run: specify validate ontology/*.ttl

      - name: Unit tests
        run: uv run pytest tests/unit/ -v

      - name: Contract tests
        run: uv run pytest tests/contract/ -v

      - name: Drift detection
        run: |
          ggen sync
          git diff --exit-code

  tier3-pr:
    if: github.event_name == 'pull_request'
    needs: tier2-fast
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Integration tests
        run: uv run pytest tests/integration/ -v

      - name: Receipt verification
        run: ggen verify --level source

  tier4-main:
    if: github.ref == 'refs/heads/main'
    needs: tier3-pr
    runs-on: ubuntu-latest
    steps:
      - name: Full integration tests
        run: uv run pytest tests/ -v --cov

      - name: Full receipt verification
        run: ggen verify --level regenerate
```

**Validation dashboard:**

Track validation health over time:
- Pass rate trends
- Failure categories
- Time to detect problems
- Mean time to fix

---

**Resulting context:**

After applying this pattern, you have:

- Validation at every pipeline stage
- Appropriate check depth for each context
- Fast feedback for developers
- Confidence in code quality

This ties together all verification patterns and supports **[39. Feedback Loop](../evolution/feedback-loop.md)**.

---

**Related patterns:**

- *Uses:* **[34. Shape Validation](./shape-validation.md)** — SHACL in CI
- *Uses:* **[35. Drift Detection](./drift-detection.md)** — Drift in CI
- *Uses:* **[36. Receipt Verification](./receipt-verification.md)** — Receipts in CI
- *Enables:* **[39. Feedback Loop](../evolution/feedback-loop.md)** — Validation data

---

> *"Continuous attention to technical excellence and good design enhances agility."*
>
> — Agile Manifesto

Continuous validation is continuous attention. It maintains technical excellence at every commit.
