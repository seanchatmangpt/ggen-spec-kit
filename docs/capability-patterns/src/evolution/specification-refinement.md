# 42. Specification Refinement

★★

*Specifications aren't static. As understanding deepens and feedback arrives, specifications must evolve. Specification refinement is the disciplined practice of improving specifications while maintaining consistency. This is how capabilities grow without chaos.*

---

## The Living Specification

In traditional development, specifications are written once and then abandoned. The code diverges. Requirements documents gather dust. Reality moves on while specs stay frozen.

Specification-driven development is different. Specifications are living documents. They evolve alongside understanding. But evolution without discipline leads to chaos—inconsistent specs, broken transformations, violated equations.

Specification refinement is disciplined evolution. It channels all changes through the specification, maintaining the **[Constitutional Equation](../transformation/constitutional-equation.md)**:

```
spec.md = μ(feature.ttl)
```

When you need to improve something, you don't patch the code. You refine the specification, then regenerate. The improvement flows through the entire system—from spec to test to implementation to documentation.

---

## The Ad-Hoc Change Problem

**The fundamental problem: Ad-hoc changes bypass specification, creating drift. Specification refinement channels all changes through the source of truth, maintaining constitutional consistency.**

Consider what happens without disciplined refinement:

### The Drift Spiral

```
Day 1:
spec.ttl says: validation returns errors
code says: validation returns errors
         ✓ Consistent

Day 30:
Bug found: "Need to include warnings too"
Quick fix: modify code directly

spec.ttl says: validation returns errors
code says: validation returns errors + warnings
         ✗ Inconsistent (drift begins)

Day 60:
Feature request: "Need severity levels"
Quick fix: modify code directly

spec.ttl says: validation returns errors
code says: validation returns errors + warnings + severity
         ✗ Major drift

Day 90:
New developer reads spec, implements based on it
Breaks production because spec is wrong
         ✗ Chaos
```

### The Regeneration Disaster

When drift accumulates, regeneration becomes dangerous:

```bash
$ ggen sync

# Regenerates from spec...
# Overwrites all the "quick fixes"
# Production breaks
# Developers stop trusting transformation
# Specs become permanently stale
```

### The Documentation Lie

If code changes without spec changes, documentation lies:

```markdown
## validate command

Returns validation errors.

# Reality: Returns errors, warnings, and severity levels
# But docs don't know because spec wasn't updated
```

---

## The Forces

### Force: Speed Wants Quick Fixes

*Patching code is faster than updating specs. There's pressure to "just fix it."*

Updating a spec, regenerating, verifying—this takes more time than a quick code change.

**Resolution:** Make refinement fast. Automate the regeneration. But never skip it. Quick fixes accumulate into eventual chaos.

### Force: Consistency Wants Discipline

*The constitutional equation must hold. Every artifact must derive from specification.*

Discipline requires effort. Effort has cost. But inconsistency has greater cost.

**Resolution:** Build habits. Make spec-first the automatic response. Make direct code changes feel wrong.

### Force: Evolution Wants Flexibility

*Specifications must accommodate change. Rigid specs become obsolete.*

If changing a spec is too hard, developers work around it.

**Resolution:** Make specs easy to change. Good schema design accommodates evolution. Refinement should be straightforward, not painful.

### Force: Stability Wants Caution

*Changes can break existing behavior. Stable systems resist change.*

Every refinement is a risk. Tests might break. Behavior might change unexpectedly.

**Resolution:** Verify changes thoroughly. Run tests before and after. Preview changes before applying. Make refinement safe through verification.

---

## Therefore

**Refine specifications through a disciplined process that maintains the constitutional equation and ensures changes are verified. Never patch artifacts directly—always change the source of truth.**

### The Refinement Workflow

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  SPECIFICATION REFINEMENT WORKFLOW                                             │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 1: IDENTIFY                                                        │  │
│  │                                                                          │  │
│  │  • Gap analysis reveals need for improvement                             │  │
│  │  • Feedback shows specification is incomplete                            │  │
│  │  • Bug indicates specification doesn't match intent                      │  │
│  │  • Feature request requires specification extension                      │  │
│  │                                                                          │  │
│  │  Document:                                                               │  │
│  │    - What needs to change                                                │  │
│  │    - Why it needs to change                                              │  │
│  │    - What artifacts will be affected                                     │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 2: PROPOSE                                                         │  │
│  │                                                                          │  │
│  │  • Draft specification changes in RDF                                    │  │
│  │  • Document rationale for each change                                    │  │
│  │  • Identify all affected artifacts                                       │  │
│  │  • Consider backwards compatibility                                      │  │
│  │                                                                          │  │
│  │  Create refinement record:                                               │  │
│  │    sk:Refinement with date, author, rationale                            │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 3: VALIDATE                                                        │  │
│  │                                                                          │  │
│  │  • Run SHACL validation on changed specs                                 │  │
│  │  • Verify internal consistency                                           │  │
│  │  • Check for unintended implications                                     │  │
│  │  • Review against ontology constraints                                   │  │
│  │                                                                          │  │
│  │  Catch problems before they propagate                                    │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 4: PREVIEW                                                         │  │
│  │                                                                          │  │
│  │  • Generate artifacts in preview/dry-run mode                            │  │
│  │  • Review diff of what would change                                      │  │
│  │  • Assess impact on existing tests                                       │  │
│  │  • Check for surprising changes                                          │  │
│  │                                                                          │  │
│  │  $ ggen sync --dry-run --diff                                            │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 5: TRANSFORM                                                       │  │
│  │                                                                          │  │
│  │  • Apply changes to specifications                                       │  │
│  │  • Run full transformation pipeline                                      │  │
│  │  • Generate all affected artifacts                                       │  │
│  │  • Update receipts                                                       │  │
│  │                                                                          │  │
│  │  $ ggen sync                                                             │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 6: TEST                                                            │  │
│  │                                                                          │  │
│  │  • Run existing tests (expect some failures from behavior changes)       │  │
│  │  • Update tests for new behavior                                         │  │
│  │  • Add tests for new acceptance criteria                                 │  │
│  │  • Verify all tests pass                                                 │  │
│  │                                                                          │  │
│  │  $ pytest tests/                                                         │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 7: COMMIT                                                          │  │
│  │                                                                          │  │
│  │  • Commit specification + artifacts TOGETHER                             │  │
│  │  • Include refinement rationale in message                               │  │
│  │  • Link to gap analysis / feedback source                                │  │
│  │  • Never commit spec without artifacts or vice versa                     │  │
│  │                                                                          │  │
│  │  $ git add ontology/ src/ tests/ docs/                                   │  │
│  │  $ git commit -m "feat(validate): add streaming mode [REFINE-2025-02]"   │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 8: MEASURE                                                         │  │
│  │                                                                          │  │
│  │  • Deploy and observe                                                    │  │
│  │  • Measure outcome metrics                                               │  │
│  │  • Confirm gap is addressed                                              │  │
│  │  • Document lessons learned                                              │  │
│  │                                                                          │  │
│  │  Close the feedback loop                                                 │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Refinement Tracking in RDF

```turtle
# ontology/cli-commands.ttl
@prefix sk: <http://github.com/spec-kit/schema#> .
@prefix cli: <http://github.com/spec-kit/cli#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Track refinement history on the capability
cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;

    # Current specification
    sk:hasArgument [
        a sk:Argument ;
        sk:name "file" ;
        sk:type "Path" ;
        sk:required true
    ] ;

    sk:hasOption [
        a sk:Option ;
        sk:name "--strict" ;
        sk:type "bool" ;
        sk:default "false" ;
        sk:help "Enable strict mode validation"
    ] ;

    sk:hasOption [
        a sk:Option ;
        sk:name "--stream" ;
        sk:type "bool" ;
        sk:default "false" ;
        sk:help "Use streaming validation for large files" ;
        # Added in refinement REFINE-2025-02-15
        sk:addedIn sk:REFINE-2025-02-15
    ] ;

    # Refinement history
    sk:refinementHistory sk:REFINE-2025-01-15 ;
    sk:refinementHistory sk:REFINE-2025-02-15 .


# Refinement records
sk:REFINE-2025-01-15 a sk:Refinement ;
    sk:date "2025-01-15"^^xsd:date ;
    sk:author "Alice" ;
    sk:type sk:Corrective ;
    sk:addressesGap jtbd:MinimizeErrorComprehensionTime ;
    sk:rationale """
        Feedback showed error messages were confusing.
        Added structured error output with line numbers
        and suggestions for common fixes.
    """ ;
    sk:changeDescription """
        Modified error output format:
        - Added line number for each error
        - Added column number for syntax errors
        - Added plain-language explanation
        - Added "did you mean?" suggestions
    """ ;
    sk:affectedArtifacts [
        sk:artifact "src/commands/validate.py" ;
        sk:changeType "modified"
    ] ;
    sk:verificationStatus "verified" ;
    sk:verificationDate "2025-01-16"^^xsd:date .


sk:REFINE-2025-02-15 a sk:Refinement ;
    sk:date "2025-02-15"^^xsd:date ;
    sk:author "Bob" ;
    sk:type sk:Performance ;
    sk:addressesGap jtbd:MinimizeValidationTime ;
    sk:rationale """
        Gap analysis showed P99 latency exceeded target for files > 1MB.
        Added streaming validation option to process large files
        incrementally rather than loading entirely into memory.
    """ ;
    sk:changeDescription """
        Added --stream option:
        - Processes file in chunks
        - Reports errors incrementally
        - Files > 1MB auto-enable streaming
    """ ;
    sk:affectedCriteria [
        sk:id "AC-VAL-P99" ;
        sk:before "P50 latency < 1 second" ;
        sk:after "P99 latency < 2 seconds for files up to 10MB"
    ] ;
    sk:affectedArtifacts [
        sk:artifact "src/commands/validate.py" ;
        sk:changeType "modified"
    ], [
        sk:artifact "tests/test_validate.py" ;
        sk:changeType "modified"
    ], [
        sk:artifact "docs/validate.md" ;
        sk:changeType "modified"
    ] ;
    sk:verificationStatus "verified" ;
    sk:verificationDate "2025-02-16"^^xsd:date .
```

### Refinement Types

```turtle
# Refinement type taxonomy
sk:RefinementType a rdfs:Class ;
    rdfs:label "Refinement Type" ;
    rdfs:comment "Category of specification refinement" .

sk:Additive a sk:RefinementType ;
    rdfs:label "Additive" ;
    rdfs:comment "Adds new capability without changing existing behavior" ;
    sk:riskLevel "low" ;
    sk:example "Adding new --format option to validate command" .

sk:Corrective a sk:RefinementType ;
    rdfs:label "Corrective" ;
    rdfs:comment "Fixes incorrect or unclear specification" ;
    sk:riskLevel "medium" ;
    sk:example "Clarifying error message format specification" .

sk:Performance a sk:RefinementType ;
    rdfs:label "Performance" ;
    rdfs:comment "Improves efficiency without changing behavior" ;
    sk:riskLevel "medium" ;
    sk:example "Adding streaming mode for large file processing" .

sk:Deprecation a sk:RefinementType ;
    rdfs:label "Deprecation" ;
    rdfs:comment "Phases out old behavior in favor of new" ;
    sk:riskLevel "high" ;
    sk:example "Deprecating --legacy flag, recommending --format instead" .

sk:Breaking a sk:RefinementType ;
    rdfs:label "Breaking" ;
    rdfs:comment "Changes existing behavior in incompatible way" ;
    sk:riskLevel "critical" ;
    sk:example "Changing default output format" ;
    sk:requires "Major version increment" .

sk:Clarification a sk:RefinementType ;
    rdfs:label "Clarification" ;
    rdfs:comment "Improves specification clarity without changing behavior" ;
    sk:riskLevel "minimal" ;
    sk:example "Adding examples to command documentation" .
```

### Refinement Command

```python
# src/specify_cli/commands/refine.py
"""Specification refinement command."""

import typer
from pathlib import Path
from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from specify_cli.ops import refine
from specify_cli.core.config import load_config

app = typer.Typer()
console = Console()


@app.command()
def propose(
    capability: str = typer.Argument(..., help="Capability to refine"),
    rationale: str = typer.Option(..., "--rationale", "-r", help="Why refinement is needed"),
    type: str = typer.Option("additive", "--type", "-t", help="Refinement type"),
    gap: str = typer.Option(None, "--gap", "-g", help="Gap ID being addressed"),
) -> None:
    """Propose a specification refinement.

    Creates a refinement record and prepares for changes.

    Example:
        specify refine propose validate \\
            --rationale "P99 latency exceeds target" \\
            --type performance \\
            --gap MinimizeValidationTime
    """
    config = load_config()

    # Create refinement proposal
    refinement_id = refine.create_proposal(
        capability=capability,
        rationale=rationale,
        refinement_type=type,
        gap_id=gap,
        author=config.get("author", "Unknown"),
        date=date.today()
    )

    console.print(Panel(
        f"""
Refinement Proposed: {refinement_id}

Capability: {capability}
Type: {type}
Rationale: {rationale}
Gap: {gap or 'Not specified'}

Next steps:
1. Edit specification: ontology/cli-commands.ttl
2. Validate changes: specify validate ontology/
3. Preview generation: ggen sync --dry-run --diff
4. Apply changes: ggen sync
5. Test: pytest tests/
6. Commit: git add -A && git commit
        """,
        title="Refinement Proposal",
        border_style="green"
    ))


@app.command()
def preview(
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Preview what would change if specification is regenerated.

    Shows diff between current artifacts and what would be generated.

    Example:
        specify refine preview
        specify refine preview --verbose
    """
    # Run dry-run generation
    changes = refine.preview_changes(verbose=verbose)

    if not changes:
        console.print("[green]No changes would be made.[/green]")
        return

    console.print(f"[yellow]{len(changes)} files would change:[/yellow]\n")

    for change in changes:
        console.print(f"  {change['status']} {change['file']}")
        if verbose and change.get('diff'):
            console.print(change['diff'])


@app.command()
def apply(
    dry_run: bool = typer.Option(False, "--dry-run", "-n"),
) -> None:
    """Apply specification refinement.

    Regenerates all artifacts from specifications.

    Example:
        specify refine apply
        specify refine apply --dry-run
    """
    if dry_run:
        preview(verbose=True)
        return

    result = refine.apply_changes()

    if result.success:
        console.print(Panel(
            f"""
Refinement applied successfully.

Files modified: {result.files_modified}
Tests to update: {result.tests_affected}

Next steps:
1. Run tests: pytest tests/
2. Fix any failing tests
3. Commit changes: git add -A && git commit
            """,
            title="Refinement Applied",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"Refinement failed: {result.error}",
            title="Error",
            border_style="red"
        ))
        raise typer.Exit(1)


@app.command()
def history(
    capability: str = typer.Argument(None, help="Filter by capability"),
    limit: int = typer.Option(10, "--limit", "-n"),
) -> None:
    """Show refinement history.

    Example:
        specify refine history
        specify refine history validate
        specify refine history --limit 5
    """
    refinements = refine.get_history(capability=capability, limit=limit)

    table = Table(title="Refinement History")
    table.add_column("ID", style="cyan")
    table.add_column("Date")
    table.add_column("Type")
    table.add_column("Capability")
    table.add_column("Author")
    table.add_column("Status")

    for r in refinements:
        table.add_row(
            r['id'],
            r['date'],
            r['type'],
            r['capability'],
            r['author'],
            r['status']
        )

    console.print(table)
```

### Preview Changes

```bash
# Preview what would change
$ ggen sync --dry-run --diff

Preview Mode: No files will be written

Changes detected:

--- src/commands/validate.py (current)
+++ src/commands/validate.py (would generate)
@@ -15,6 +15,12 @@
     file: Path = typer.Argument(...),
     strict: bool = typer.Option(False, "--strict"),
+    stream: bool = typer.Option(
+        False,
+        "--stream",
+        help="Use streaming validation for large files"
+    ),
 ) -> None:
     """Validate RDF files against SHACL shapes."""

--- tests/test_validate.py (current)
+++ tests/test_validate.py (would generate)
@@ -45,6 +45,15 @@
     assert result.exit_code == 0
     assert "Valid" in result.stdout

+def test_validate_stream_mode():
+    """Test streaming validation for large files."""
+    result = runner.invoke(app, ["validate", "--stream", "large.ttl"])
+    assert result.exit_code == 0

--- docs/validate.md (current)
+++ docs/validate.md (would generate)
@@ -20,6 +20,10 @@
 | `--strict` | bool | false | Enable strict mode |
+| `--stream` | bool | false | Streaming validation for large files |

Summary:
  3 files would be modified
  0 files would be created
  0 files would be deleted

Run 'ggen sync' to apply these changes.
```

---

## The Commit Protocol

Refinements must be committed atomically—specification and artifacts together:

```bash
# CORRECT: Atomic commit
git add ontology/cli-commands.ttl
git add src/commands/validate.py
git add tests/test_validate.py
git add docs/validate.md
git commit -m "$(cat <<'EOF'
feat(validate): add streaming validation for large files

Addresses gap: MinimizeValidationTime P99 latency exceeds target

Refinement: REFINE-2025-02-15
Type: Performance

Changes:
- Add --stream option for streaming validation
- Auto-enable streaming for files > 1MB
- Add AC-VAL-STREAM acceptance criterion

Artifacts regenerated with ggen sync.
Tests updated and passing.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"

# WRONG: Separate commits
git add ontology/cli-commands.ttl
git commit -m "Update spec"  # ❌ Spec without artifacts

git add src/commands/validate.py
git commit -m "Update code"  # ❌ Artifacts without spec
```

### Commit Message Format

```
<type>(<scope>): <description>

[Optional body explaining rationale]

Refinement: <refinement-id>
Type: <refinement-type>
Addresses: <gap-id or feedback-id>

Changes:
- <bullet points of what changed>

[Optional: breaking changes, migration notes]
```

---

## Case Study: The Controlled Evolution

*A team evolves their validation capability through disciplined refinement.*

### The Trigger

Gap analysis revealed:
- P99 latency for large files: 12 seconds (target: 2 seconds)
- Root cause: Loading entire file into memory before validation

### Phase 1: Identify

```
Gap: MinimizeValidationTime P99
Current: 12 seconds for files > 1MB
Target: < 2 seconds
Priority: 4.8 (HIGH)

Need: Streaming validation that processes file incrementally
```

### Phase 2: Propose

```turtle
# Proposed addition to cli:ValidateCommand
sk:hasOption [
    a sk:Option ;
    sk:name "--stream" ;
    sk:type "bool" ;
    sk:default "false" ;
    sk:help "Use streaming validation for large files" ;
    sk:addedIn sk:REFINE-2025-02-15
] ;

sk:acceptanceCriteria [
    sk:id "AC-VAL-STREAM" ;
    sk:criterion "P99 latency < 2 seconds for files up to 10MB" ;
    sk:rationale "Streaming enables large file validation within target"
] .
```

### Phase 3: Validate

```bash
$ specify validate ontology/cli-commands.ttl

Validating ontology/cli-commands.ttl...

✓ RDF syntax valid
✓ SHACL shapes satisfied
✓ No undefined references
✓ No conflicting option names

Validation passed.
```

### Phase 4: Preview

```bash
$ ggen sync --dry-run --diff

3 files would change:
  M src/commands/validate.py   (+12 lines)
  M tests/test_validate.py     (+15 lines)
  M docs/validate.md           (+8 lines)

[diff output showing changes...]
```

### Phase 5: Transform

```bash
$ ggen sync

Transforming specifications...

✓ src/commands/validate.py regenerated
✓ tests/test_validate.py regenerated
✓ docs/validate.md regenerated

3 files updated.
```

### Phase 6: Test

```bash
$ pytest tests/

tests/test_validate.py::test_validate_basic PASSED
tests/test_validate.py::test_validate_strict PASSED
tests/test_validate.py::test_validate_stream_mode PASSED  # New test
tests/test_validate.py::test_validate_large_file PASSED   # New test

4 passed in 2.34s
```

### Phase 7: Commit

```bash
$ git add -A
$ git commit -m "feat(validate): add streaming validation for large files..."
```

### Phase 8: Measure

Two weeks after deployment:

| Metric | Before | After |
|--------|--------|-------|
| P99 latency (>1MB files) | 12s | 1.8s |
| Memory usage (>1MB files) | 500MB | 50MB |
| User satisfaction (validation speed) | 2.3/5 | 4.1/5 |

Gap closed. Refinement verified.

---

## Anti-Patterns

### Anti-Pattern: Quick Fix First

*"I'll just fix the code now and update the spec later."*

"Later" never comes. The drift begins.

**Resolution:** Never touch code without specification. Make spec-first the only acceptable path.

### Anti-Pattern: Spec-Only Commit

*"I updated the spec but haven't regenerated yet."*

Commits with spec changes but not artifact changes create broken states.

**Resolution:** Always commit spec + artifacts together. Use pre-commit hooks to verify.

### Anti-Pattern: Undocumented Refinement

*"I changed the spec. What was the reason again?"*

Without rationale, future developers don't understand why changes were made.

**Resolution:** Require refinement records. Document the gap, rationale, and affected artifacts.

### Anti-Pattern: Skip Preview

*"Regeneration should be fine. Just run ggen sync."*

Unexpected changes in regenerated artifacts cause problems.

**Resolution:** Always preview first. Review diffs before applying.

---

## Implementation Checklist

### Preparation

- [ ] Set up refinement tracking in RDF
- [ ] Create refinement record template
- [ ] Configure ggen for dry-run preview
- [ ] Set up pre-commit hooks for verification

### Process

- [ ] Document the need (gap analysis, feedback)
- [ ] Create refinement proposal record
- [ ] Make specification changes
- [ ] Validate specification
- [ ] Preview regeneration
- [ ] Apply transformation
- [ ] Run and update tests
- [ ] Commit atomically

### Verification

- [ ] Verify constitutional equation holds
- [ ] Verify all tests pass
- [ ] Verify no unintended changes
- [ ] Verify documentation updated

### Follow-up

- [ ] Deploy to production
- [ ] Measure outcome improvement
- [ ] Update refinement record with results
- [ ] Share learnings

---

## Exercises

### Exercise 1: Create a Refinement Proposal

Document a proposed refinement for a capability:

```turtle
sk:REFINE-YOUR-DATE a sk:Refinement ;
    sk:date "???"^^xsd:date ;
    sk:author "???" ;
    sk:type ??? ;
    sk:addressesGap ??? ;
    sk:rationale """
        ???
    """ ;
    sk:changeDescription """
        ???
    """ .
```

### Exercise 2: Preview and Apply

Practice the preview-apply workflow:

```bash
# 1. Make a specification change
# 2. Preview
ggen sync --dry-run --diff
# 3. Review the changes
# 4. Apply
ggen sync
# 5. Test
pytest tests/
# 6. Commit
git add -A && git commit
```

### Exercise 3: Audit Refinement History

Query your refinement history:

```sparql
SELECT ?refinement ?date ?type ?rationale
WHERE {
    ?refinement a sk:Refinement ;
                sk:date ?date ;
                sk:type ?type ;
                sk:rationale ?rationale .
}
ORDER BY DESC(?date)
```

---

## Resulting Context

After implementing this pattern, you have:

- **Disciplined approach to specification evolution** — all changes flow through specs
- **Maintained constitutional equation** — artifacts always match specifications
- **Traceable refinement history** — know what changed, when, why, and by whom
- **Verified changes before deployment** — preview prevents surprises
- **Atomic commits** — spec and artifacts always in sync

Specification refinement transforms ad-hoc patches into disciplined evolution. The specification remains the source of truth, and improvements flow through it consistently.

---

## Related Patterns

- **Driven by:** **[41. Gap Analysis](./gap-analysis.md)** — Identifies what needs improvement
- **Maintains:** **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Equation preserved through refinement
- **Enables:** **[43. Branching Exploration](./branching-exploration.md)** — Try alternatives before refining
- **Supports:** **[45. Living Documentation](./living-documentation.md)** — Docs update with refinements

---

## Philosophical Note

> *"Change is the only constant."*

Systems that don't evolve die. But evolution without discipline leads to chaos. Specification refinement provides disciplined evolution—change that flows through the source of truth, change that maintains consistency, change that can be traced and understood.

The constitutional equation isn't a constraint on change. It's a guide for change. It says: "Change the specification, and the artifacts will follow." This makes change safe. This makes change traceable. This makes change disciplined.

Refine your specifications. Let the artifacts follow. Maintain the equation.

---

**Next:** Learn how **[43. Branching Exploration](./branching-exploration.md)** enables experimentation with multiple approaches before committing to a refinement.
