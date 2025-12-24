# 36. Receipt Verification

★★

*Receipts are proofs. Receipt verification checks those proofs, confirming that artifacts were correctly generated from their claimed sources. This is the audit trail of transformation.*

---

## The Proof

**[Receipt Generation](../transformation/receipt-generation.md)** creates cryptographic proofs. Receipt verification checks them.

A receipt claims:
- This artifact was generated from this source
- Through these transformation stages
- At this time
- With this hash
- Using this pipeline version

Without verification, these are just claims—assertions that could be false. With verification, they become proofs—assertions confirmed by cryptographic evidence.

---

## The Verification Problem

**The fundamental problem: Receipts without verification are just claims. Anyone can write a receipt file. Verification makes them trustworthy proofs.**

Let us examine what could go wrong without verification:

### Forged Receipts

```json
{
  "input": { "hash": "abc123..." },
  "output": { "hash": "xyz789..." },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

This receipt claims a relationship. But did the transformation actually happen? Is the hash correct? Was the timestamp accurate?

### Stale Receipts

The receipt was valid when created. But the source changed, the artifact was modified, or the pipeline was updated. The receipt is now stale—it describes a past state, not the current one.

### Corrupted Receipts

File corruption, merge conflicts, or partial writes can produce invalid receipts. Without validation, corrupted receipts cause silent failures.

---

## The Forces

### Force: Trust vs. Verify

*We want to trust receipts. But trust must be verified.*

**Resolution:** Verify receipts at critical points. Trust during development, verify before deployment.

### Force: Speed vs. Thoroughness

*Full verification takes time. Quick verification may miss problems.*

**Resolution:** Tiered verification. Quick hash checks for commits, thorough regeneration for releases.

### Force: Completeness vs. Practicality

*Every claim should be verified. But not all verification is practical.*

**Resolution:** Verify what matters. Hash correctness, source existence, pipeline compatibility.

---

## Therefore

**Implement receipt verification at multiple levels—from quick hash checks to full regeneration comparison. Use verification to build confidence that artifacts match their specifications.**

Verification architecture:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  VERIFICATION LEVELS                                                     │
│                                                                          │
│  Level 1: HASH CHECK (fast, ~ms)                                         │
│  ├── Artifact hash matches receipt hash?                                 │
│  └── Basic integrity verification                                        │
│                                                                          │
│  Level 2: SOURCE CHECK (medium, ~100ms)                                  │
│  ├── All Level 1 checks                                                  │
│  ├── Source file exists?                                                 │
│  ├── Source hash unchanged since generation?                             │
│  └── Template and shape hashes unchanged?                                │
│                                                                          │
│  Level 3: REGENERATION CHECK (slow, ~seconds)                            │
│  ├── All Level 2 checks                                                  │
│  ├── Regenerate from source                                              │
│  └── Compare regenerated output to current artifact                      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Verification Implementation

### Level 1: Hash Verification

```python
# src/specify_cli/ops/verify.py
"""Receipt verification operations."""

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class VerificationResult(Enum):
    VALID = "valid"
    INVALID = "invalid"
    STALE = "stale"
    MISSING = "missing"


@dataclass
class VerificationReport:
    """Result of verifying a single artifact."""
    artifact: Path
    level: int
    result: VerificationResult
    checks: List[dict]
    recommendation: Optional[str] = None


def verify_hash(artifact_path: Path) -> VerificationReport:
    """Level 1: Verify artifact hash matches receipt."""
    receipt_path = artifact_path.with_suffix(artifact_path.suffix + ".receipt")

    if not receipt_path.exists():
        return VerificationReport(
            artifact=artifact_path,
            level=1,
            result=VerificationResult.MISSING,
            checks=[{"check": "receipt_exists", "passed": False}],
            recommendation="Run 'ggen sync' to generate receipt"
        )

    receipt = json.loads(receipt_path.read_text())

    # Compute current hash
    current_hash = compute_sha256(artifact_path)
    expected_hash = receipt['output']['hash']

    if current_hash == expected_hash:
        return VerificationReport(
            artifact=artifact_path,
            level=1,
            result=VerificationResult.VALID,
            checks=[{"check": "artifact_hash", "passed": True, "expected": expected_hash[:16], "actual": current_hash[:16]}]
        )
    else:
        return VerificationReport(
            artifact=artifact_path,
            level=1,
            result=VerificationResult.INVALID,
            checks=[{"check": "artifact_hash", "passed": False, "expected": expected_hash[:16], "actual": current_hash[:16]}],
            recommendation="Artifact has been modified. Run 'ggen sync' to regenerate."
        )


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of file."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()
```

### Level 2: Source Verification

```python
def verify_source(artifact_path: Path) -> VerificationReport:
    """Level 2: Verify source unchanged since generation."""
    # First do Level 1 check
    level1 = verify_hash(artifact_path)
    if level1.result != VerificationResult.VALID:
        level1.level = 2
        return level1

    receipt_path = artifact_path.with_suffix(artifact_path.suffix + ".receipt")
    receipt = json.loads(receipt_path.read_text())

    checks = level1.checks.copy()

    # Check source file exists
    source_path = Path(receipt['input']['file'])
    if not source_path.exists():
        checks.append({"check": "source_exists", "passed": False, "file": str(source_path)})
        return VerificationReport(
            artifact=artifact_path,
            level=2,
            result=VerificationResult.INVALID,
            checks=checks,
            recommendation=f"Source file not found: {source_path}"
        )
    checks.append({"check": "source_exists", "passed": True})

    # Check source hash unchanged
    current_source_hash = compute_sha256(source_path)
    expected_source_hash = receipt['input']['hash']

    if current_source_hash != expected_source_hash:
        checks.append({"check": "source_hash", "passed": False, "expected": expected_source_hash[:16], "actual": current_source_hash[:16]})
        return VerificationReport(
            artifact=artifact_path,
            level=2,
            result=VerificationResult.STALE,
            checks=checks,
            recommendation="Source has changed. Run 'ggen sync' to update artifact."
        )
    checks.append({"check": "source_hash", "passed": True})

    # Check template hash if recorded
    if 'template' in receipt:
        template_path = Path(receipt['template']['file'])
        if template_path.exists():
            current_template_hash = compute_sha256(template_path)
            expected_template_hash = receipt['template']['hash']
            if current_template_hash != expected_template_hash:
                checks.append({"check": "template_hash", "passed": False})
                return VerificationReport(
                    artifact=artifact_path,
                    level=2,
                    result=VerificationResult.STALE,
                    checks=checks,
                    recommendation="Template has changed. Run 'ggen sync' to update artifact."
                )
        checks.append({"check": "template_hash", "passed": True})

    return VerificationReport(
        artifact=artifact_path,
        level=2,
        result=VerificationResult.VALID,
        checks=checks
    )
```

### Level 3: Regeneration Verification

```python
def verify_regeneration(artifact_path: Path, config_dir: Path) -> VerificationReport:
    """Level 3: Verify by regenerating and comparing."""
    import tempfile
    import subprocess

    # First do Level 2 checks
    level2 = verify_source(artifact_path)
    if level2.result not in [VerificationResult.VALID, VerificationResult.STALE]:
        level2.level = 3
        return level2

    checks = level2.checks.copy()

    # Regenerate to temporary location
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["ggen", "sync", "--output-dir", tmpdir],
            cwd=config_dir,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            checks.append({"check": "regeneration", "passed": False, "error": result.stderr[:200]})
            return VerificationReport(
                artifact=artifact_path,
                level=3,
                result=VerificationResult.INVALID,
                checks=checks,
                recommendation=f"Regeneration failed: {result.stderr[:100]}"
            )

        # Find and compare regenerated artifact
        regenerated_path = Path(tmpdir) / artifact_path.name
        if not regenerated_path.exists():
            checks.append({"check": "regeneration_output", "passed": False})
            return VerificationReport(
                artifact=artifact_path,
                level=3,
                result=VerificationResult.INVALID,
                checks=checks,
                recommendation="Regeneration did not produce expected output"
            )

        current_hash = compute_sha256(artifact_path)
        regenerated_hash = compute_sha256(regenerated_path)

        if current_hash == regenerated_hash:
            checks.append({"check": "regeneration_match", "passed": True})
            return VerificationReport(
                artifact=artifact_path,
                level=3,
                result=VerificationResult.VALID,
                checks=checks
            )
        else:
            checks.append({"check": "regeneration_match", "passed": False})
            return VerificationReport(
                artifact=artifact_path,
                level=3,
                result=VerificationResult.INVALID,
                checks=checks,
                recommendation="Regenerated output differs. Run 'ggen sync' to update."
            )
```

---

## Verification Command

```python
# src/specify_cli/commands/verify.py
"""Receipt verification command."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from specify_cli.ops import verify

app = typer.Typer()
console = Console()


@app.command()
def check(
    level: int = typer.Option(2, "--level", "-l", help="Verification level (1-3)"),
    receipts_dir: Path = typer.Option(".ggen/receipts", help="Receipts directory"),
    thorough: bool = typer.Option(False, "--thorough", "-t", help="Level 3 verification"),
) -> None:
    """Verify receipts against current state.

    Levels:
      1: Hash check (fast) - artifact matches receipt
      2: Source check (medium) - source unchanged since generation
      3: Regeneration (slow) - regenerate and compare

    Examples:
        # Quick verification
        ggen verify --level 1

        # Standard verification
        ggen verify

        # Thorough verification (before release)
        ggen verify --thorough
    """
    if thorough:
        level = 3

    reports = verify.verify_all(receipts_dir, level=level)

    # Display results
    for report in reports:
        display_verification(report)

    # Summary
    valid = sum(1 for r in reports if r.result == verify.VerificationResult.VALID)
    stale = sum(1 for r in reports if r.result == verify.VerificationResult.STALE)
    invalid = sum(1 for r in reports if r.result == verify.VerificationResult.INVALID)
    missing = sum(1 for r in reports if r.result == verify.VerificationResult.MISSING)

    console.print()
    console.print(f"[green]✓ Valid:[/green] {valid}")
    console.print(f"[yellow]⚠ Stale:[/yellow] {stale}")
    console.print(f"[red]✗ Invalid:[/red] {invalid}")
    console.print(f"[dim]? Missing:[/dim] {missing}")

    # Exit code
    if invalid > 0:
        raise typer.Exit(1)
    elif stale > 0:
        raise typer.Exit(2)


def display_verification(report: verify.VerificationReport) -> None:
    """Display single verification report."""
    result_str = {
        verify.VerificationResult.VALID: "[green]✓ VERIFIED[/green]",
        verify.VerificationResult.STALE: "[yellow]⚠ STALE[/yellow]",
        verify.VerificationResult.INVALID: "[red]✗ INVALID[/red]",
        verify.VerificationResult.MISSING: "[dim]? MISSING[/dim]",
    }[report.result]

    console.print(f"\n{report.artifact}")
    console.print(f"  Status: {result_str} (Level {report.level})")

    for check in report.checks:
        symbol = "[green]✓[/green]" if check["passed"] else "[red]✗[/red]"
        console.print(f"  {symbol} {check['check']}")

    if report.recommendation:
        console.print(f"  [dim]→ {report.recommendation}[/dim]")
```

---

## CI Integration

```yaml
# .github/workflows/verify.yml
name: Receipt Verification

on:
  push:
    branches: [main]
  pull_request:
  release:
    types: [published]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        run: pip install specify-cli ggen

      # Quick verification on every push
      - name: Quick verify (Level 1)
        if: github.event_name == 'push'
        run: ggen verify --level 1

      # Standard verification on PRs
      - name: Standard verify (Level 2)
        if: github.event_name == 'pull_request'
        run: ggen verify --level 2

      # Thorough verification on release
      - name: Thorough verify (Level 3)
        if: github.event_name == 'release'
        run: ggen verify --thorough
```

---

## Verification Report

```
$ ggen verify --thorough

Receipt Verification Report
═══════════════════════════════════════════════════════════════════════════

src/commands/validate.py
  Status: ✓ VERIFIED (Level 3)
  ✓ artifact_hash        sha256:a1b2c3...
  ✓ source_exists        ontology/cli-commands.ttl
  ✓ source_hash          sha256:d4e5f6...
  ✓ template_hash        sha256:789abc...
  ✓ regeneration_match   Identical output

src/commands/check.py
  Status: ⚠ STALE (Level 2)
  ✓ artifact_hash        sha256:def012...
  ✓ source_exists        ontology/cli-commands.ttl
  ✗ source_hash          Expected: sha256:d4e5f6... Actual: sha256:aabbcc...
  → Source has changed. Run 'ggen sync' to update artifact.

docs/validate.md
  Status: ✗ INVALID (Level 1)
  ✗ artifact_hash        Expected: sha256:112233... Actual: sha256:445566...
  → Artifact has been modified. Run 'ggen sync' to regenerate.

═══════════════════════════════════════════════════════════════════════════
Summary: 1 verified, 1 stale, 1 invalid

Run 'ggen sync' to fix stale and invalid artifacts.
```

---

## Anti-Patterns

### Anti-Pattern: Skip Verification

*"The build passed, so receipts must be valid."*

Build success doesn't verify receipts. Verification must be explicit.

**Resolution:** Always verify receipts. Make verification part of the standard workflow.

### Anti-Pattern: Only Hash Check

*"Hash matches, we're good."*

Hash matching only confirms the artifact wasn't modified. It doesn't confirm it's up-to-date with sources.

**Resolution:** Use Level 2+ verification for important checks.

### Anti-Pattern: Manual Verification

*"Someone should check these receipts."*

Manual verification is inconsistent and doesn't scale.

**Resolution:** Automate verification in CI. Make it part of every build.

---

## Implementation Checklist

- [ ] Implement Level 1 hash verification
- [ ] Implement Level 2 source verification
- [ ] Implement Level 3 regeneration verification
- [ ] Create verification command
- [ ] Add verification to CI pipeline
- [ ] Configure appropriate levels for different stages
- [ ] Document verification workflow

---

## Resulting Context

After implementing this pattern, you have:

- **Verified proofs** for all generated artifacts
- **Multiple verification levels** for different contexts
- **Clear verification reports** showing status
- **CI enforcement** of receipt validity
- **Audit trail** for artifact provenance

Receipt verification transforms receipts from claims into proofs.

---

## Code References

The following spec-kit source files implement receipt verification:

| Reference | Description |
|-----------|-------------|
| `src/specify_cli/runtime/receipt.py:159-185` | verify_receipt() comparing stored and current hashes |
| `src/specify_cli/runtime/receipt.py:61-77` | Receipt.from_file() loading receipt for verification |
| `src/specify_cli/runtime/receipt.py:80-93` | sha256_file() computing current file hash |
| `src/specify_cli/runtime/receipt.py:188-209` | verify_idempotence() verifying transformation stability |

---

## Related Patterns

- **Verifies:** **[26. Receipt Generation](../transformation/receipt-generation.md)** — Receipts checked
- **Complements:** **[35. Drift Detection](./drift-detection.md)** — Different approach
- **Enables:** **[37. Continuous Validation](./continuous-validation.md)** — CI verification
- **Part of:** **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Equation verified

---

**Next:** Learn how **[37. Continuous Validation](./continuous-validation.md)** ties all verification patterns together in automated pipelines.
