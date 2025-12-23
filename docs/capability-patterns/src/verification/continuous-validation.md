# 37. Continuous Validation

★★

*Validation isn't a phase—it's continuous. Continuous validation runs checks at every stage: commit, push, pull request, merge, deploy. This is quality as a constant, not an afterthought.*

---

## The Validation Gap

Traditional validation happens at milestones: code review, QA phase, release testing. Between milestones, quality can degrade. Problems introduced Monday aren't caught until Friday's QA cycle. By then, the developer has moved on, context is lost, and fixing is expensive.

Continuous validation closes these gaps. Every change triggers validation. Every push verifies consistency. Every merge confirms compliance.

```
Traditional:                    Continuous:

Mon: Change                     Mon: Change → Validate → ✓
Tue: Change                     Tue: Change → Validate → ✗ (caught!)
Wed: Change                     Wed: Change → Validate → ✓
Thu: Change                     Thu: Change → Validate → ✓
Fri: QA finds problems          Fri: All validated, ready to release
     from Tue
```

In specification-driven development, continuous validation checks:
- Specification validity (SHACL shapes)
- Transformation correctness (receipts, idempotence)
- Test passage (generated and manual tests)
- Drift absence (source-artifact consistency)
- Contract compliance (interface contracts)

---

## The Continuous Problem

**The fundamental problem: Periodic validation allows problems to accumulate. By the time they're found, context is lost and fixing is expensive. Continuous validation catches problems when they're introduced.**

### The Cost of Late Detection

```
Cost to fix a defect:

  During coding:      1x (immediate fix)
  In code review:     5x (context switch, explanation)
  In QA:             10x (reproduction, debugging)
  In production:    100x (incident response, rollback, hotfix)
```

Continuous validation shifts detection left—catching problems at 1x cost instead of 10x or 100x.

### The Feedback Delay

Without continuous validation:
```
Developer commits
  → pushes
    → goes to lunch
      → CI eventually runs
        → fails 2 hours later
          → developer has forgotten context
            → expensive debugging
```

With continuous validation:
```
Developer commits
  → pre-commit hook validates
    → fails immediately
      → developer still has context
        → quick fix
```

---

## The Forces

### Force: Speed vs. Thoroughness

*Comprehensive checks take time. Fast feedback enables flow.*

Running all tests on every keystroke isn't practical. But running nothing until release is dangerous.

**Resolution:** Tiered validation. Fast checks run frequently. Slow checks run at critical gates. Match check speed to check frequency.

### Force: Developer Experience vs. Rigor

*Developers want fast feedback. Security and compliance want thorough checks.*

Blocking every commit for 10-minute test suites frustrates developers. But skipping security scans risks vulnerabilities.

**Resolution:** Separate tiers for different audiences. Developers get fast feedback. CI runs additional checks. Release gates run comprehensive validation.

### Force: Local vs. Central

*Local checks are fast but inconsistent. Central checks are consistent but slow.*

Different developers have different environments. Local checks might pass while CI fails.

**Resolution:** Standardize environments. Use containers for consistency. Run the same checks locally and in CI.

---

## Therefore

**Implement tiered continuous validation that runs appropriate checks at each pipeline stage. Fast checks run often; thorough checks run at critical gates.**

Validation tiers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CONTINUOUS VALIDATION TIERS                                             │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TIER 1: LOCAL (pre-commit)                     Duration: ~seconds  │ │
│  │                                                                     │ │
│  │  • File syntax linting                                             │ │
│  │  • RDF/Turtle syntax check                                         │ │
│  │  • Quick unit tests                                                │ │
│  │  • Format check                                                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TIER 2: PUSH (CI fast)                         Duration: ~2-5 min  │ │
│  │                                                                     │ │
│  │  • All Tier 1 checks                                               │ │
│  │  • SHACL validation                                                │ │
│  │  • Full unit tests                                                 │ │
│  │  • Contract tests                                                  │ │
│  │  • Drift detection                                                 │ │
│  │  • Type checking                                                   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TIER 3: PR (CI full)                           Duration: ~10-15 min│ │
│  │                                                                     │ │
│  │  • All Tier 2 checks                                               │ │
│  │  • Integration tests                                               │ │
│  │  • Receipt verification (Level 2)                                  │ │
│  │  • Regeneration check                                              │ │
│  │  • Coverage report                                                 │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TIER 4: MAIN (merge to main)                   Duration: ~30 min   │ │
│  │                                                                     │ │
│  │  • All Tier 3 checks                                               │ │
│  │  • Full integration tests                                          │ │
│  │  • Performance tests                                               │ │
│  │  • Security scans                                                  │ │
│  │  • Full receipt verification                                       │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TIER 5: RELEASE                                Duration: ~1-2 hours│ │
│  │                                                                     │ │
│  │  • All Tier 4 checks                                               │ │
│  │  • End-to-end tests                                                │ │
│  │  • Full regeneration verify                                        │ │
│  │  • Manual approval gates                                           │ │
│  │  • Compliance checks                                               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  # Python linting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]

  # Type checking
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  # RDF validation
  - repo: local
    hooks:
      - id: validate-rdf
        name: Validate RDF specifications
        entry: specify validate ontology/*.ttl
        language: system
        files: '\.ttl$'

      - id: check-drift
        name: Check for artifact drift
        entry: ggen verify --level 1
        language: system
        pass_filenames: false

      - id: quick-tests
        name: Quick tests
        entry: pytest tests/unit/ -x -q --tb=no
        language: system
        pass_filenames: false
        stages: [commit]
```

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: Continuous Validation

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  PYTHON_VERSION: '3.11'

jobs:
  # ═══════════════════════════════════════════════════════════════════════
  # TIER 2: Fast checks on every push
  # ═══════════════════════════════════════════════════════════════════════
  tier2-fast:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install uv
          uv sync

      - name: Lint
        run: uv run ruff check src/

      - name: Type check
        run: uv run mypy src/

      - name: SHACL validation
        run: uv run specify validate ontology/*.ttl

      - name: Unit tests
        run: uv run pytest tests/unit/ -v

      - name: Contract tests
        run: uv run pytest tests/contract/ -v

      - name: Drift detection
        run: |
          uv run ggen sync
          git diff --exit-code

  # ═══════════════════════════════════════════════════════════════════════
  # TIER 3: Full checks on pull requests
  # ═══════════════════════════════════════════════════════════════════════
  tier3-pr:
    if: github.event_name == 'pull_request'
    needs: tier2-fast
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-groups

      - name: Integration tests
        run: uv run pytest tests/integration/ -v

      - name: Receipt verification (Level 2)
        run: uv run ggen verify --level 2

      - name: Coverage report
        run: |
          uv run pytest tests/ --cov=src/specify_cli --cov-report=xml
          uv run coverage report --fail-under=80

  # ═══════════════════════════════════════════════════════════════════════
  # TIER 4: Main branch checks
  # ═══════════════════════════════════════════════════════════════════════
  tier4-main:
    if: github.ref == 'refs/heads/main'
    needs: tier2-fast
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-groups

      - name: Full integration tests
        run: uv run pytest tests/ -v

      - name: Performance tests
        run: uv run pytest tests/performance/ -v --benchmark-autosave

      - name: Security scan
        uses: pyupio/safety@v1
        with:
          api-key: ${{ secrets.SAFETY_API_KEY }}

      - name: Full receipt verification
        run: uv run ggen verify --level 3
```

### Release Workflow

```yaml
# .github/workflows/release.yml
name: Release Validation

on:
  release:
    types: [published]

jobs:
  tier5-release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --all-groups

      - name: End-to-end tests
        run: uv run pytest tests/e2e/ -v

      - name: Full regeneration verify
        run: |
          # Regenerate all artifacts
          uv run ggen sync

          # Verify no changes
          if ! git diff --exit-code; then
            echo "::error::Artifacts out of sync with specifications"
            exit 1
          fi

          # Full receipt verification
          uv run ggen verify --thorough

      - name: Compliance check
        run: uv run specify compliance check

      - name: Build and verify package
        run: |
          uv build
          uv run twine check dist/*
```

---

## Validation Dashboard

Track validation health over time:

```python
# src/specify_cli/ops/metrics.py
"""Validation metrics for dashboard."""

from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class ValidationMetrics:
    """Metrics from a validation run."""
    timestamp: datetime
    tier: int
    duration_seconds: float
    checks_passed: int
    checks_failed: int
    checks_skipped: int

    @property
    def pass_rate(self) -> float:
        total = self.checks_passed + self.checks_failed
        return self.checks_passed / total if total > 0 else 0.0


def collect_metrics(results: List[dict]) -> ValidationMetrics:
    """Collect metrics from validation results."""
    passed = sum(1 for r in results if r["status"] == "passed")
    failed = sum(1 for r in results if r["status"] == "failed")
    skipped = sum(1 for r in results if r["status"] == "skipped")

    return ValidationMetrics(
        timestamp=datetime.now(),
        tier=results[0].get("tier", 0),
        duration_seconds=sum(r.get("duration", 0) for r in results),
        checks_passed=passed,
        checks_failed=failed,
        checks_skipped=skipped
    )
```

Key metrics to track:
- **Pass rate**: Percentage of checks passing over time
- **Mean time to detect (MTTD)**: How quickly problems are found
- **Mean time to fix (MTTF)**: How quickly problems are resolved
- **Failure distribution**: Which checks fail most often
- **Flaky tests**: Tests that sometimes pass, sometimes fail

---

## Case Study: The Release Confidence

*A team achieves release confidence through continuous validation.*

### The Before

The DataSync team had:
- Weekly QA cycles
- Regular "fire drill" releases
- Post-release hotfixes
- Low confidence in deployments

```
Mon: Develop features
Tue: Develop features
Wed: Develop features
Thu: QA cycle starts
Fri: Find problems, scramble to fix
Sat: Deploy (fingers crossed)
Sun: Hotfix (usually)
```

### The Implementation

They implemented continuous validation:

**Tier 1 (pre-commit):** 3 seconds
- RDF syntax check
- Python lint
- Quick unit tests

**Tier 2 (push):** 4 minutes
- SHACL validation
- All unit tests
- Drift detection

**Tier 3 (PR):** 12 minutes
- Integration tests
- Receipt verification
- Coverage check (80% minimum)

**Tier 4 (main):** 25 minutes
- Full tests
- Security scans
- Performance benchmarks

**Tier 5 (release):** 1 hour
- E2E tests
- Full regeneration verify
- Manual approval

### The Results

| Metric | Before | After |
|--------|--------|-------|
| Problems found in QA | 15/week | 2/week |
| Post-release hotfixes | 3/month | 0.3/month |
| Mean time to detect | 4 days | 4 minutes |
| Release confidence | Low | High |
| Developer satisfaction | 2/5 | 4/5 |

---

## Anti-Patterns

### Anti-Pattern: All-or-Nothing

*"Either run all checks or none."*

Running everything on every commit is slow. Running nothing until release is risky.

**Resolution:** Tier your validation. Fast checks often, slow checks selectively.

### Anti-Pattern: Ignored Failures

*"That test always fails, just ignore it."*

Ignored failures erode trust. If a check can be ignored, why run it?

**Resolution:** Fix or remove flaky tests. If a check matters, make it pass. If it doesn't matter, remove it.

### Anti-Pattern: Local-Only

*"It works on my machine."*

Local validation without CI allows environment differences to cause failures.

**Resolution:** Run the same checks locally and in CI. Use containers for consistency.

---

## Implementation Checklist

### Tier Setup

- [ ] Define validation tiers (1-5)
- [ ] Assign checks to appropriate tiers
- [ ] Set duration targets per tier
- [ ] Document tier purposes

### Local Integration

- [ ] Configure pre-commit hooks
- [ ] Document local setup
- [ ] Provide skip options for emergencies
- [ ] Test local hooks work

### CI Integration

- [ ] Create CI workflow
- [ ] Configure tier triggers (push, PR, main, release)
- [ ] Set up artifact caching
- [ ] Configure notifications

### Monitoring

- [ ] Track pass rates
- [ ] Monitor durations
- [ ] Alert on failures
- [ ] Report trends

---

## Resulting Context

After implementing this pattern, you have:

- **Validation at every pipeline stage** catching problems early
- **Fast feedback for developers** enabling flow
- **Comprehensive checks for releases** ensuring quality
- **Measurable validation health** through metrics
- **Confidence in deployments** through verification

Continuous validation transforms quality from a phase into a constant—a property of every commit, not just releases.

---

## Related Patterns

- **Uses:** **[34. Shape Validation](./shape-validation.md)** — SHACL in CI
- **Uses:** **[35. Drift Detection](./drift-detection.md)** — Drift in CI
- **Uses:** **[36. Receipt Verification](./receipt-verification.md)** — Receipts in CI
- **Enables:** **[39. Feedback Loop](../evolution/feedback-loop.md)** — Validation data feeds improvement

---

## Philosophical Note

> *"Continuous attention to technical excellence and good design enhances agility."*
> — Agile Manifesto

Continuous validation is continuous attention. It doesn't let quality slip between milestones. Every change is validated. Every commit is verified. Excellence isn't achieved in a final push—it's maintained at every step.

The investment in continuous validation pays off not in any single check, but in the cumulative confidence built over thousands of validations. Each green check adds a drop to the reservoir of trust that enables fast, confident releases.

---

**Next:** Learn how **[38. Observable Execution](./observable-execution.md)** instruments capabilities with telemetry for understanding and optimization.
