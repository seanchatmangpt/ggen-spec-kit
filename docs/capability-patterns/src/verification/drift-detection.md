# 35. Drift Detection

★★

*Generated artifacts should match their source. Drift detection identifies when artifacts have been modified outside the transformation pipeline—catching violations of the constitutional equation before they cause harm.*

---

## The Sync Problem

The **[Constitutional Equation](../transformation/constitutional-equation.md)** promises that artifacts are generated from specifications: `spec.md = μ(feature.ttl)`. But equivalence can break. Specifications change without regeneration. Artifacts are manually edited. Systems drift apart.

Drift is insidious. The artifact works differently than the specification describes. Documentation doesn't match behavior. Tests don't test what's actually implemented. Confidence erodes.

Without drift detection, you discover problems when:
- Documentation contradicts behavior and users complain
- Generated code has bugs that shouldn't exist
- CI passes but production fails mysteriously
- Different team members have different understandings

Drift detection catches these violations before they cause harm.

---

## The Drift Problem

**The fundamental problem: Manual edits to generated files violate the constitutional equation. Without detection, drift accumulates silently until it causes visible problems.**

Let us examine how drift occurs:

### Source Drift

The specification changes, but the artifact isn't regenerated:

```
Timeline:
  T1: feature.ttl created
  T2: ggen sync → spec.md generated ✓
  T3: feature.ttl modified (new requirement)
  T4: Developer forgets to regenerate
  T5: spec.md is now STALE
```

The specification has evolved, but the artifact hasn't. They're out of sync.

### Artifact Drift

The artifact is manually edited, breaking the equation:

```
Timeline:
  T1: feature.ttl created
  T2: ggen sync → spec.md generated ✓
  T3: Developer makes "quick fix" directly in spec.md
  T4: spec.md ≠ μ(feature.ttl) anymore
  T5: Next ggen sync will OVERWRITE the fix
```

The artifact was manually modified. The constitutional equation is violated. The fix will be lost.

### Silent Conflict

Both specification and artifact change independently:

```
Timeline:
  T1: Both in sync
  T2: Developer A modifies feature.ttl
  T3: Developer B modifies spec.md (different change)
  T4: They're now DIVERGED
  T5: Which version is correct? Nobody knows.
```

---

## The Forces

Several tensions shape drift detection:

### Force: Convenience vs. Process

*Direct edits are convenient. But they break the process.*

A "quick fix" to generated code takes seconds. Updating the specification, regenerating, and testing takes minutes. The temptation is strong.

**Resolution:** Make the right path easy. Fast regeneration. Clear feedback. Detect violations immediately so the cost of deviation is paid now, not later.

### Force: Awareness vs. Scale

*Everyone should know which files are generated. But teams grow and files multiply.*

In a small project, everyone knows which files are generated. In a large project with many contributors, that knowledge is fragmented.

**Resolution:** Clear markers (headers, `.gitattributes`), automated detection, and onboarding documentation. The system should tell people when they're about to edit generated files.

### Force: Speed vs. Thoroughness

*Quick drift checks enable frequent checking. Thorough checks take time.*

Hash comparison is instant. Full regeneration takes time. Checking on every commit might slow down development.

**Resolution:** Tiered checking. Quick hash checks on every commit. Full regeneration on PR merge or release. Match thoroughness to criticality.

---

## Therefore

**Implement drift detection that compares generated artifacts against their receipts and regenerated output. Detect violations at the earliest possible point and provide clear guidance for resolution.**

Drift detection workflow:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  DRIFT DETECTION WORKFLOW                                                │
│                                                                          │
│  1. LOAD receipts from .ggen/receipts/                                   │
│     │                                                                    │
│     │  Each receipt contains:                                            │
│     │  - Artifact path and hash                                          │
│     │  - Source specification path and hash                              │
│     │  - Generation timestamp                                            │
│     │  - Pipeline version                                                │
│     │                                                                    │
│     ▼                                                                    │
│  2. CHECK each artifact for drift                                        │
│     │                                                                    │
│     │  Current artifact hash vs. receipt hash:                           │
│     │  - Same → No artifact drift                                        │
│     │  - Different → Artifact manually edited                            │
│     │                                                                    │
│     ▼                                                                    │
│  3. CHECK each source for staleness                                      │
│     │                                                                    │
│     │  Current source hash vs. receipt hash:                             │
│     │  - Same → Source unchanged                                         │
│     │  - Different → Artifact is stale                                   │
│     │                                                                    │
│     ▼                                                                    │
│  4. CLASSIFY status                                                      │
│     │                                                                    │
│     │  IN_SYNC:       Artifact matches, source unchanged                 │
│     │  STALE:         Source changed, artifact outdated                  │
│     │  DRIFTED:       Artifact manually edited                           │
│     │  CONFLICT:      Both changed independently                         │
│     │                                                                    │
│     ▼                                                                    │
│  5. REPORT and recommend                                                 │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Detection Methods

### Method 1: Receipt Verification

Compare artifact hash against receipt:

```python
# src/specify_cli/ops/drift.py
"""Drift detection operations."""

import json
import hashlib
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class DriftStatus(Enum):
    """Drift classification."""
    IN_SYNC = "in_sync"
    STALE = "stale"
    DRIFTED = "drifted"
    CONFLICT = "conflict"
    MISSING = "missing"


@dataclass
class DriftReport:
    """Report for a single artifact."""
    artifact: Path
    source: Path
    status: DriftStatus
    details: str
    recommendation: str


def check_drift_by_receipt(artifact_path: Path) -> DriftReport:
    """Check if artifact matches its receipt."""
    receipt_path = artifact_path.with_suffix(artifact_path.suffix + ".receipt")

    if not receipt_path.exists():
        return DriftReport(
            artifact=artifact_path,
            source=Path("unknown"),
            status=DriftStatus.MISSING,
            details="No receipt file found",
            recommendation="Run 'ggen sync' to generate receipt"
        )

    receipt = json.loads(receipt_path.read_text())

    # Check artifact hash
    current_artifact_hash = compute_sha256(artifact_path)
    recorded_artifact_hash = receipt['output']['hash']
    artifact_changed = current_artifact_hash != recorded_artifact_hash

    # Check source hash
    source_path = Path(receipt['input']['file'])
    current_source_hash = compute_sha256(source_path)
    recorded_source_hash = receipt['input']['hash']
    source_changed = current_source_hash != recorded_source_hash

    # Classify
    if artifact_changed and source_changed:
        return DriftReport(
            artifact=artifact_path,
            source=source_path,
            status=DriftStatus.CONFLICT,
            details="Both artifact and source modified since last sync",
            recommendation="Manual reconciliation required"
        )
    elif artifact_changed:
        return DriftReport(
            artifact=artifact_path,
            source=source_path,
            status=DriftStatus.DRIFTED,
            details="Artifact has been manually edited",
            recommendation="Update specification and run 'ggen sync --force'"
        )
    elif source_changed:
        return DriftReport(
            artifact=artifact_path,
            source=source_path,
            status=DriftStatus.STALE,
            details="Source updated, artifact not regenerated",
            recommendation="Run 'ggen sync' to update artifact"
        )
    else:
        return DriftReport(
            artifact=artifact_path,
            source=source_path,
            status=DriftStatus.IN_SYNC,
            details="Artifact matches specification",
            recommendation="None needed"
        )


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 hash of file."""
    content = file_path.read_bytes()
    return hashlib.sha256(content).hexdigest()
```

### Method 2: Regeneration Comparison

Regenerate and compare for definitive check:

```python
def check_drift_by_regeneration(artifact_path: Path, config_path: Path) -> DriftReport:
    """Check drift by regenerating and comparing."""
    import tempfile
    import subprocess

    # Save current artifact hash
    current_hash = compute_sha256(artifact_path)

    # Regenerate to temporary location
    with tempfile.TemporaryDirectory() as tmpdir:
        # Run ggen sync to temp output
        result = subprocess.run(
            ["ggen", "sync", "--output-dir", tmpdir],
            cwd=config_path.parent,
            capture_output=True
        )

        if result.returncode != 0:
            return DriftReport(
                artifact=artifact_path,
                source=Path("unknown"),
                status=DriftStatus.MISSING,
                details=f"Regeneration failed: {result.stderr.decode()}",
                recommendation="Fix regeneration errors"
            )

        # Find corresponding output
        regenerated = Path(tmpdir) / artifact_path.name
        regenerated_hash = compute_sha256(regenerated)

        if current_hash == regenerated_hash:
            return DriftReport(
                artifact=artifact_path,
                source=Path("regenerated"),
                status=DriftStatus.IN_SYNC,
                details="Regeneration produces identical output",
                recommendation="None needed"
            )
        else:
            return DriftReport(
                artifact=artifact_path,
                source=Path("regenerated"),
                status=DriftStatus.DRIFTED,
                details="Artifact differs from regenerated output",
                recommendation="Run 'ggen sync' to update"
            )
```

### Method 3: Git-Based Detection

Use git to detect changes:

```bash
#!/bin/bash
# scripts/check-drift.sh

# Regenerate all artifacts
ggen sync

# Check if anything changed
if ! git diff --exit-code; then
    echo "⚠️  DRIFT DETECTED"
    echo "Generated files don't match their sources."
    echo ""
    echo "Changed files:"
    git diff --stat
    echo ""
    echo "Options:"
    echo "  1. If you edited generated files: Update the specification"
    echo "  2. If source changed: Run 'ggen sync' before committing"
    exit 1
fi

echo "✓ No drift detected"
```

---

## Drift Command

```python
# src/specify_cli/commands/drift.py
"""Drift detection command."""

import typer
from pathlib import Path
from rich.console import Console
from rich.table import Table

from specify_cli.ops import drift

app = typer.Typer()
console = Console()


@app.command()
def check(
    receipts_dir: Path = typer.Option(".ggen/receipts", help="Receipts directory"),
    method: str = typer.Option("receipt", help="Detection method: receipt, regenerate, git"),
) -> None:
    """Check for drift between specifications and artifacts.

    Drift occurs when:
    - Generated artifacts are manually edited
    - Source specifications change without regeneration

    Examples:
        # Quick check using receipts
        specify drift check

        # Thorough check using regeneration
        specify drift check --method regenerate
    """
    reports = drift.detect_all_drift(receipts_dir)

    # Build summary table
    table = Table(title="Drift Detection Report")
    table.add_column("Artifact", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details")

    status_counts = {s: 0 for s in drift.DriftStatus}

    for report in reports:
        status_counts[report.status] += 1

        if report.status == drift.DriftStatus.IN_SYNC:
            status_str = "[green]✓ In Sync[/green]"
        elif report.status == drift.DriftStatus.STALE:
            status_str = "[yellow]⚠ Stale[/yellow]"
        elif report.status == drift.DriftStatus.DRIFTED:
            status_str = "[red]✗ Drifted[/red]"
        elif report.status == drift.DriftStatus.CONFLICT:
            status_str = "[red]⚠ Conflict[/red]"
        else:
            status_str = "[dim]? Unknown[/dim]"

        table.add_row(
            str(report.artifact),
            status_str,
            report.details
        )

    console.print(table)

    # Summary
    console.print()
    console.print(f"[green]✓ In sync:[/green] {status_counts[drift.DriftStatus.IN_SYNC]}")
    console.print(f"[yellow]⚠ Stale:[/yellow] {status_counts[drift.DriftStatus.STALE]}")
    console.print(f"[red]✗ Drifted:[/red] {status_counts[drift.DriftStatus.DRIFTED]}")
    console.print(f"[red]⚠ Conflict:[/red] {status_counts[drift.DriftStatus.CONFLICT]}")

    # Recommendations for problems
    problems = [r for r in reports if r.status != drift.DriftStatus.IN_SYNC]
    if problems:
        console.print("\n[bold]Recommendations:[/bold]")
        for report in problems:
            console.print(f"  {report.artifact}: {report.recommendation}")

    # Exit code
    if status_counts[drift.DriftStatus.DRIFTED] > 0 or status_counts[drift.DriftStatus.CONFLICT] > 0:
        raise typer.Exit(1)
    elif status_counts[drift.DriftStatus.STALE] > 0:
        raise typer.Exit(2)
```

---

## CI Integration

### GitHub Actions

```yaml
# .github/workflows/drift.yml
name: Drift Detection

on: [push, pull_request]

jobs:
  drift-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup environment
        run: |
          pip install specify-cli
          pip install ggen

      - name: Check for drift (receipts)
        run: specify drift check

      - name: Verify by regeneration
        if: github.event_name == 'pull_request'
        run: |
          ggen sync
          if ! git diff --exit-code; then
            echo "::error::Drift detected! Generated files don't match specifications."
            git diff --stat
            exit 1
          fi
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: drift-check
        name: Check for artifact drift
        entry: specify drift check
        language: system
        pass_filenames: false
        always_run: true
```

### .gitattributes Warning

```gitattributes
# Warn when editing generated files
src/commands/*.py linguist-generated=true
docs/commands/*.md linguist-generated=true
*.generated.* linguist-generated=true
```

---

## Resolving Drift

### Resolving Stale Artifacts

Source changed, artifact needs regeneration:

```bash
$ specify drift check
⚠ Stale: 3 artifacts need regeneration

  src/commands/validate.py <- ontology/cli-commands.ttl
  src/commands/check.py <- ontology/cli-commands.ttl
  docs/validate.md <- ontology/cli-commands.ttl

# Resolution: regenerate
$ ggen sync
Regenerating 3 artifacts from updated specifications...
✓ All artifacts now in sync

$ specify drift check
✓ All artifacts in sync
```

### Resolving Manual Edits

Artifact was manually edited:

```bash
$ specify drift check
✗ Drifted: 1 artifact manually edited

  src/commands/validate.py
    Lines 45-48 differ from specification

# Option 1: Discard manual edits
$ ggen sync --force
Overwriting drifted artifact...
✓ Artifact regenerated

# Option 2: Update specification to include the change
$ vim ontology/cli-commands.ttl  # Add the feature
$ ggen sync
✓ Artifact now matches updated specification

# Option 3: Register temporary exception
$ specify drift allow src/commands/validate.py \
    --until 2025-02-01 \
    --reason "Hotfix for production issue ISSUE-123"
Drift exception registered. Must be resolved by 2025-02-01.
```

### Resolving Conflicts

Both specification and artifact changed:

```bash
$ specify drift check
⚠ Conflict: 1 artifact has conflicting changes

  src/commands/validate.py
    Artifact modified: lines 45-48 added
    Source modified: validation logic changed

# Manual reconciliation required
# 1. Review both changes
$ git diff HEAD~5 src/commands/validate.py
$ git diff HEAD~5 ontology/cli-commands.ttl

# 2. Decide which changes to keep
# 3. Update specification with merged changes
$ vim ontology/cli-commands.ttl

# 4. Regenerate
$ ggen sync --force
✓ Conflict resolved
```

---

## Case Study: The Production Hotfix

*How drift detection prevented a lost hotfix.*

### The Situation

The PaymentAPI team had a critical bug: large transactions were failing validation. A developer made an emergency fix directly in the generated handler:

```python
# src/handlers/validate.py (generated file)
# Developer added this line manually at 3 AM:
if amount > MAX_TRANSACTION_LIMIT:
    return {"error": "Amount exceeds limit"}  # HOTFIX
```

### The Risk

Two weeks later, another developer updated the specification to add new validation rules. They ran `ggen sync` to regenerate—which would have:
- Overwritten the handler from specification
- Removed the manual hotfix
- Silently removed the transaction limit check

Large transactions would start failing again.

### The Detection

With drift detection:

```bash
$ ggen sync
Checking for drift before regeneration...

⚠️  DRIFT DETECTED in src/handlers/validate.py

This file has been manually modified since last generation.
Changes will be LOST if you proceed.

Diff:
+ if amount > MAX_TRANSACTION_LIMIT:
+     return {"error": "Amount exceeds limit"}

Options:
  1. Run 'ggen sync --force' to overwrite (manual changes LOST)
  2. Update specification to include these changes
  3. Run 'specify drift allow' to register exception

Aborting regeneration.
```

### The Resolution

The team:
1. Reviewed the hotfix
2. Added the transaction limit to the specification
3. Regenerated properly
4. Removed the drift

```turtle
# Added to cli-commands.ttl
cli:ValidateHandler cli:hasValidation [
    a cli:AmountLimit ;
    cli:maxAmount 10000 ;
    cli:errorMessage "Amount exceeds limit"
] .
```

```bash
$ ggen sync
✓ Regenerated src/handlers/validate.py
  (now includes transaction limit from specification)

$ specify drift check
✓ All artifacts in sync
```

### The Prevention

They added drift check to CI:

```yaml
- name: Check for drift
  run: |
    specify drift check
    if [ $? -eq 1 ]; then
      echo "::error::Drift detected. Manual edits to generated files."
      echo "Update the specification, not the generated file."
      exit 1
    fi
```

---

## Anti-Patterns

### Anti-Pattern: Ignore Drift Warnings

*"The tests pass, so drift is fine."*

Ignored drift accumulates. Eventually, specifications and artifacts diverge so far that reconciliation becomes painful.

**Resolution:** Fix drift immediately. Block merges with drift. Make drift visible and costly.

### Anti-Pattern: Force Overwrite Without Review

*"Just regenerate and push."*

Blind regeneration can destroy intentional manual changes that weren't properly migrated to specifications.

**Resolution:** Review drift before resolving. Understand what changed. Decide deliberately whether to discard or migrate.

### Anti-Pattern: Permanent Exceptions

*"That file is always drifted, it's fine."*

Permanent exceptions defeat the purpose. They become forgotten technical debt.

**Resolution:** Time-bound exceptions only. Require justification. Review and resolve before deadline.

---

## Implementation Checklist

### Detection

- [ ] Generate receipts during transformation
- [ ] Implement receipt-based drift detection
- [ ] Implement regeneration-based verification
- [ ] Create drift check command

### Integration

- [ ] Add drift check to CI pipeline
- [ ] Configure pre-commit hooks
- [ ] Set up .gitattributes warnings
- [ ] Document resolution procedures

### Enforcement

- [ ] Block merges with drift
- [ ] Support time-bound exceptions
- [ ] Log drift events for metrics
- [ ] Alert on accumulated drift

---

## Resulting Context

After implementing this pattern, you have:

- **Visibility into specification-artifact synchronization**
- **Early detection of manual edits** before they're overwritten
- **Prevention of stale artifacts** reaching production
- **Clear resolution paths** for each drift type
- **CI enforcement** preventing drift from merging

Drift detection is the guardian of the constitutional equation—ensuring that specifications and artifacts stay synchronized.

---

## Code References

The following spec-kit source files implement drift detection:

| Reference | Description |
|-----------|-------------|
| `src/specify_cli/runtime/receipt.py:80-93` | sha256_file() for comparing file hashes |
| `src/specify_cli/runtime/receipt.py:159-185` | verify_receipt() detecting file drift |
| `src/specify_cli/runtime/receipt.py:39-49` | Receipt storing expected hashes for comparison |

---

## Related Patterns

- **Verifies:** **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Equation enforced
- **Uses:** **[26. Receipt Generation](../transformation/receipt-generation.md)** — Receipts enable detection
- **Complements:** **[36. Receipt Verification](./receipt-verification.md)** — Different verification angle
- **Enables:** **[37. Continuous Validation](./continuous-validation.md)** — Drift checks in CI

---

## Philosophical Note

> *"Trust, but verify."*

Drift detection is the verification. We trust that developers follow the process—edit specifications, regenerate artifacts. But we verify that the process was followed. Trust without verification becomes assumption. Assumptions become bugs.

The constitutional equation is a promise. Drift detection ensures the promise is kept.

---

**Next:** Learn how **[36. Receipt Verification](./receipt-verification.md)** uses cryptographic proofs to verify transformation integrity.
