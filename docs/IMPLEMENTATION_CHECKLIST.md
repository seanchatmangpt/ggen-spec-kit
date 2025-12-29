# Implementation Checklist
## Detailed Step-by-Step Guide for Unified Roadmap

**Companion to**: UNIFIED_IMPLEMENTATION_ROADMAP.md
**Purpose**: Actionable checklist with exact commands and file changes
**Status**: Ready for Execution

---

## Phase 1: Foundation (Week 1) - Critical Path

### Day 1-2: Git Command Integration

#### Task 1.1: Create Git Command Module
```bash
# Create new git command file
touch src/specify_cli/commands/git.py
```

**File**: `src/specify_cli/commands/git.py`
```python
"""Git commands with constitutional equation enforcement."""
import typer
from rich.console import Console
from specify_cli.ops import git as git_ops
from specify_cli.runtime import git as git_runtime
from specify_cli.core.telemetry import timed

app = typer.Typer(help="Git operations with RDF awareness")
console = Console()

@app.command()
@timed
def status() -> None:
    """Show git status with constitutional violations."""
    result = git_ops.get_status()
    violations = git_ops.check_constitutional_violations()

    # Display standard git status
    console.print(result['output'])

    # Display violations if any
    if violations:
        console.print("\n[bold red]Constitutional Violations:[/bold red]")
        for violation in violations:
            console.print(f"  ❌ {violation['file']}: {violation['reason']}")

@app.command()
@timed
def add(files: list[str]) -> None:
    """Stage files for commit."""
    git_runtime.add_files(files)
    console.print(f"[green]Staged {len(files)} file(s)[/green]")

@app.command()
@timed
def commit(message: str = typer.Option(None, "-m", "--message")) -> None:
    """Create commit with constitutional checks."""
    # Check for violations
    violations = git_ops.check_constitutional_violations()
    if violations:
        console.print("[bold red]Cannot commit: Constitutional violations detected[/bold red]")
        for violation in violations:
            console.print(f"  ❌ {violation['file']}: {violation['reason']}")
        raise typer.Exit(code=1)

    # Interactive commit message if not provided
    if not message:
        message = git_ops.interactive_commit_message()

    # Add co-authorship
    message = git_ops.add_co_authorship(message)

    # Commit with HEREDOC format
    git_runtime.commit(message)
    console.print("[green]✓[/green] Commit created")

@app.command()
@timed
def push(remote: str = "origin", branch: str = None) -> None:
    """Push commits with safety checks."""
    # Verify receipts before push
    if not git_ops.verify_all_receipts():
        console.print("[bold red]Cannot push: Receipt verification failed[/bold red]")
        console.print("Run: specify verify --fix")
        raise typer.Exit(code=1)

    git_runtime.push(remote, branch)
    console.print("[green]✓[/green] Pushed successfully")
```

**Checklist**:
- [ ] File created: `src/specify_cli/commands/git.py`
- [ ] Imports correct (typer, rich, ops, runtime)
- [ ] Commands: status, add, commit, push
- [ ] Constitutional checks in commit
- [ ] Co-authorship auto-added
- [ ] Receipt verification in push

---

#### Task 1.2: Enhance Git Operations Layer
**File**: `src/specify_cli/ops/git.py` (enhance existing)

Add these functions:
```python
def check_constitutional_violations() -> list[dict]:
    """Check for constitutional equation violations."""
    violations = []

    # Get all modified files
    status = get_status()
    modified_files = status['modified'] + status['staged']

    for file in modified_files:
        # Check if file is generated
        if is_generated_file(file):
            # Verify receipt exists and is valid
            receipt_path = get_receipt_path(file)
            if not receipt_path.exists():
                violations.append({
                    'file': file,
                    'reason': 'Generated file modified without valid receipt',
                    'fix': f'Run: ggen sync && git add {receipt_path}'
                })
            else:
                # Verify receipt hash matches
                receipt = load_receipt(receipt_path)
                current_hash = hash_file(file)
                if receipt['output_hash'] != current_hash:
                    violations.append({
                        'file': file,
                        'reason': 'Receipt hash mismatch (file edited manually?)',
                        'fix': f'Run: ggen sync'
                    })

    return violations

def add_co_authorship(message: str) -> str:
    """Add Claude co-authorship to commit message."""
    co_author = "\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
    if co_author not in message:
        return message + co_author
    return message

def interactive_commit_message() -> str:
    """Prompt for commit message with validation."""
    console = Console()

    # Get recent commit messages for style reference
    recent = get_recent_commits(limit=5)
    console.print("\n[bold]Recent commits:[/bold]")
    for commit in recent:
        console.print(f"  {commit['hash'][:7]} {commit['message']}")

    console.print("\n[bold]Commit message (use Ctrl+D to finish):[/bold]")
    lines = []
    while True:
        try:
            line = input()
            lines.append(line)
        except EOFError:
            break

    return "\n".join(lines)

def is_generated_file(file: str) -> bool:
    """Check if file is generated from RDF."""
    generated_patterns = [
        'src/specify_cli/commands/*.py',
        'docs/*.md',
        'tests/e2e/test_commands_*.py',
    ]
    from pathlib import Path
    file_path = Path(file)

    for pattern in generated_patterns:
        if file_path.match(pattern):
            return True
    return False

def get_receipt_path(file: str) -> Path:
    """Get receipt path for generated file."""
    from pathlib import Path
    file_path = Path(file)
    receipt_name = f"{file_path.stem}.receipt.json"
    return Path(".ggen/receipts") / receipt_name
```

**Checklist**:
- [ ] Function: `check_constitutional_violations()`
- [ ] Function: `add_co_authorship()`
- [ ] Function: `interactive_commit_message()`
- [ ] Function: `is_generated_file()`
- [ ] Function: `get_receipt_path()`
- [ ] Tests added for all functions

---

#### Task 1.3: Enhance Git Runtime Layer
**File**: `src/specify_cli/runtime/git.py` (enhance existing)

Add these functions:
```python
def commit(message: str) -> subprocess.CompletedProcess:
    """Commit with HEREDOC message format."""
    # Use HEREDOC to properly handle multi-line messages
    cmd = [
        "git", "commit", "-m",
        f"$(cat <<'EOF'\n{message}\nEOF\n)"
    ]
    # Note: This needs special handling for heredoc
    # Alternative: Write message to temp file

    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write(message)
        msg_file = f.name

    try:
        cmd = ["git", "commit", "-F", msg_file]
        return run_logged(cmd)
    finally:
        Path(msg_file).unlink()

def verify_all_receipts() -> bool:
    """Verify all receipt hashes match current files."""
    from pathlib import Path
    import json
    import hashlib

    receipts_dir = Path(".ggen/receipts")
    if not receipts_dir.exists():
        return True  # No receipts yet

    for receipt_file in receipts_dir.glob("*.receipt.json"):
        receipt = json.loads(receipt_file.read_text())

        output_file = Path(receipt['output_file'])
        if not output_file.exists():
            continue

        # Verify hash
        current_hash = hashlib.sha256(output_file.read_bytes()).hexdigest()
        if f"sha256:{current_hash}" != receipt['output_hash']:
            return False

    return True
```

**Checklist**:
- [ ] Function: `commit()` with HEREDOC support
- [ ] Function: `verify_all_receipts()`
- [ ] Uses `run_logged()` for subprocess
- [ ] No `shell=True` usage
- [ ] Tests added

---

#### Task 1.4: Create Tests
```bash
# Create test files
touch tests/unit/test_git_ops.py
touch tests/integration/test_git_runtime.py
```

**File**: `tests/unit/test_git_ops.py`
```python
"""Tests for git operations layer."""
import pytest
from specify_cli.ops import git as git_ops

def test_check_constitutional_violations_empty():
    """Test no violations on clean repo."""
    violations = git_ops.check_constitutional_violations()
    assert isinstance(violations, list)

def test_add_co_authorship():
    """Test co-authorship added to message."""
    message = "feat: add feature"
    result = git_ops.add_co_authorship(message)
    assert "Co-Authored-By: Claude" in result

def test_add_co_authorship_idempotent():
    """Test co-authorship not duplicated."""
    message = "feat: add feature\n\nCo-Authored-By: Claude <noreply@anthropic.com>"
    result = git_ops.add_co_authorship(message)
    assert result.count("Co-Authored-By") == 1

def test_is_generated_file():
    """Test generated file detection."""
    assert git_ops.is_generated_file("src/specify_cli/commands/init.py")
    assert git_ops.is_generated_file("docs/README.md")
    assert not git_ops.is_generated_file("src/specify_cli/ops/git.py")
```

**Checklist**:
- [ ] Tests for `check_constitutional_violations()`
- [ ] Tests for `add_co_authorship()`
- [ ] Tests for `is_generated_file()`
- [ ] Tests for `get_receipt_path()`
- [ ] Coverage ≥ 80%

---

#### Task 1.5: Register Git Command
**File**: `src/specify_cli/commands/__init__.py`

Add:
```python
from specify_cli.commands import git

# In app registration section:
app.add_typer(git.app, name="git")
```

**Checklist**:
- [ ] Git command registered
- [ ] `specify git --help` works
- [ ] All subcommands appear in help

---

#### Task 1.6: Manual Testing
```bash
# Test git commands
uv run specify git status
uv run specify git add README.md
uv run specify git commit -m "test commit"
uv run specify git push --dry-run
```

**Checklist**:
- [ ] `specify git status` shows status + violations
- [ ] `specify git add` stages files
- [ ] `specify git commit` blocks on violations
- [ ] `specify git push` verifies receipts
- [ ] Co-authorship auto-added to commits

---

### Day 3-4: RDF Validator Integration

#### Task 2.1: Create RDF Validation Command
**File**: `src/specify_cli/commands/validate.py`

```python
"""RDF validation commands."""
import typer
from pathlib import Path
from rich.console import Console
from specify_cli.ops import ggen_shacl
from specify_cli.core.telemetry import timed

app = typer.Typer(help="RDF/Turtle validation")
console = Console()

@app.command(name="rdf")
@timed
def validate_rdf(
    files: list[Path] = typer.Argument(None),
    all: bool = typer.Option(False, "--all", help="Validate all TTL files"),
    shapes: bool = typer.Option(False, "--shapes", help="Validate SHACL shapes"),
) -> None:
    """Validate RDF/Turtle files."""

    if all:
        files = list(Path(".").rglob("*.ttl"))

    if not files:
        console.print("[red]No files specified. Use --all or provide file paths.[/red]")
        raise typer.Exit(code=1)

    results = ggen_shacl.validate_files(files, check_shapes=shapes)

    # Display results
    console.print(f"\n[bold]RDF Validation Report[/bold]")
    console.print("=" * 70)

    passed = sum(1 for r in results if r['valid'])
    failed = len(results) - passed

    console.print(f"\nFiles checked: {len(results)}")
    console.print(f"[green]✓ Passed: {passed}[/green]")
    if failed > 0:
        console.print(f"[red]✗ Failed: {failed}[/red]")

    # Show failures
    for result in results:
        if not result['valid']:
            console.print(f"\n[red]✗ {result['file']}[/red]")
            for error in result['errors']:
                console.print(f"  Line {error['line']}: {error['message']}")

    if failed > 0:
        raise typer.Exit(code=1)
```

**Checklist**:
- [ ] Command created: `validate rdf`
- [ ] Flags: `--all`, `--shapes`
- [ ] Rich console output
- [ ] Exit code 1 on failures

---

#### Task 2.2: Enhance SHACL Validation Ops
**File**: `src/specify_cli/ops/ggen_shacl.py` (enhance existing)

Add:
```python
def validate_files(files: list[Path], check_shapes: bool = False) -> list[dict]:
    """Validate multiple RDF files."""
    results = []

    for file in files:
        result = validate_file(file, check_shapes=check_shapes)
        results.append(result)

    return results

def validate_file(file: Path, check_shapes: bool = False) -> dict:
    """Validate single RDF file."""
    import rdflib
    from pyshacl import validate as shacl_validate

    result = {
        'file': str(file),
        'valid': True,
        'errors': []
    }

    # 1. Syntax validation
    try:
        g = rdflib.Graph()
        g.parse(file, format='turtle')
    except Exception as e:
        result['valid'] = False
        result['errors'].append({
            'type': 'syntax',
            'line': extract_line_number(str(e)),
            'message': str(e)
        })
        return result

    # 2. SHACL validation if requested
    if check_shapes:
        shapes_graph = load_shacl_shapes()
        conforms, results_graph, results_text = shacl_validate(
            g,
            shacl_graph=shapes_graph,
            inference='rdfs',
            abort_on_first=False,
        )

        if not conforms:
            result['valid'] = False
            result['errors'].extend(parse_shacl_results(results_text))

    return result

def load_shacl_shapes() -> rdflib.Graph:
    """Load all SHACL shape files."""
    g = rdflib.Graph()
    shapes_files = [
        Path("ontology/cli-command-shapes.ttl"),
        Path("ontology/jtbd-shapes.ttl"),
    ]

    for shapes_file in shapes_files:
        if shapes_file.exists():
            g.parse(shapes_file, format='turtle')

    return g

def parse_shacl_results(results_text: str) -> list[dict]:
    """Parse SHACL validation results into structured errors."""
    # Parse SHACL results text
    # Extract line numbers and messages
    # Return list of error dicts
    pass  # Implementation details
```

**Checklist**:
- [ ] Function: `validate_files()`
- [ ] Function: `validate_file()`
- [ ] Function: `load_shacl_shapes()`
- [ ] Syntax checking with rdflib
- [ ] SHACL validation with pyshacl
- [ ] Error messages with line numbers

---

#### Task 2.3: Add Pre-Commit Hook
**File**: `.pre-commit-config.yaml`

Add:
```yaml
  - repo: local
    hooks:
      - id: rdf-validate
        name: RDF/Turtle Validation
        entry: uv run specify validate rdf
        language: system
        files: \.ttl$
        pass_filenames: true
```

**Checklist**:
- [ ] Hook added to `.pre-commit-config.yaml`
- [ ] Test with: `pre-commit run rdf-validate --all-files`
- [ ] Hook blocks invalid RDF commits

---

#### Task 2.4: Add pyshacl Dependency
**File**: `pyproject.toml`

Add to dependencies:
```toml
dependencies = [
    # ... existing dependencies ...
    "pyshacl>=0.25.0",
]
```

**Checklist**:
- [ ] Dependency added
- [ ] Run: `uv sync`
- [ ] Import test: `python -c "import pyshacl"`

---

#### Task 2.5: Create Tests
**File**: `tests/unit/test_ggen_shacl.py`

```python
"""Tests for SHACL validation."""
import pytest
from pathlib import Path
from specify_cli.ops import ggen_shacl

def test_validate_file_valid(tmp_path):
    """Test validation of valid Turtle file."""
    ttl_file = tmp_path / "test.ttl"
    ttl_file.write_text("""
        @prefix ex: <http://example.org/> .
        ex:test a ex:Thing .
    """)

    result = ggen_shacl.validate_file(ttl_file)
    assert result['valid'] is True
    assert len(result['errors']) == 0

def test_validate_file_invalid_syntax(tmp_path):
    """Test validation of invalid Turtle syntax."""
    ttl_file = tmp_path / "test.ttl"
    ttl_file.write_text("invalid turtle syntax @@@")

    result = ggen_shacl.validate_file(ttl_file)
    assert result['valid'] is False
    assert len(result['errors']) > 0
    assert result['errors'][0]['type'] == 'syntax'
```

**Checklist**:
- [ ] Test valid TTL file
- [ ] Test invalid syntax
- [ ] Test SHACL violations
- [ ] Coverage ≥ 80%

---

#### Task 2.6: Manual Testing
```bash
# Test RDF validation
echo "@prefix ex: <http://example.org/> . ex:test a ex:Thing ." > test.ttl
uv run specify validate rdf test.ttl

# Test invalid RDF
echo "invalid syntax @@@" > invalid.ttl
uv run specify validate rdf invalid.ttl  # Should fail

# Test all RDF files
uv run specify validate rdf --all

# Test pre-commit hook
pre-commit run rdf-validate --all-files
```

**Checklist**:
- [ ] Valid files pass
- [ ] Invalid files fail with clear errors
- [ ] `--all` validates all TTL files
- [ ] Pre-commit hook works

---

### Day 5-7: Constitutional Equation Enforcement

#### Task 3.1: Create Receipt Management
**File**: `src/specify_cli/runtime/receipt.py` (enhance existing)

```python
"""Receipt management for constitutional equation."""
from pathlib import Path
import json
import hashlib
from datetime import datetime
from typing import Optional

class Receipt:
    """Receipt for RDF-to-code transformation."""

    def __init__(
        self,
        input_file: Path,
        output_file: Path,
        input_hash: str,
        output_hash: str,
        ggen_version: str = "5.0.2",
        stages: Optional[list[dict]] = None,
    ):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.input_file = str(input_file)
        self.output_file = str(output_file)
        self.input_hash = f"sha256:{input_hash}"
        self.output_hash = f"sha256:{output_hash}"
        self.ggen_version = ggen_version
        self.stages = stages or []
        self.idempotent = True

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'input_file': self.input_file,
            'output_file': self.output_file,
            'input_hash': self.input_hash,
            'output_hash': self.output_hash,
            'ggen_version': self.ggen_version,
            'stages': self.stages,
            'idempotent': self.idempotent,
            'verified': self.timestamp,
        }

    def save(self, receipts_dir: Path = Path(".ggen/receipts")) -> Path:
        """Save receipt to file."""
        receipts_dir.mkdir(parents=True, exist_ok=True)

        output_path = Path(self.output_file)
        receipt_name = f"{output_path.stem}.receipt.json"
        receipt_path = receipts_dir / receipt_name

        receipt_path.write_text(json.dumps(self.to_dict(), indent=2))
        return receipt_path

def hash_file(file_path: Path) -> str:
    """Calculate SHA256 hash of file."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()

def load_receipt(receipt_path: Path) -> dict:
    """Load receipt from file."""
    return json.loads(receipt_path.read_text())

def verify_receipt(receipt_path: Path) -> bool:
    """Verify receipt hash matches current file."""
    receipt = load_receipt(receipt_path)

    output_file = Path(receipt['output_file'])
    if not output_file.exists():
        return False

    current_hash = f"sha256:{hash_file(output_file)}"
    return current_hash == receipt['output_hash']
```

**Checklist**:
- [ ] Class: `Receipt`
- [ ] Method: `save()`
- [ ] Function: `hash_file()`
- [ ] Function: `load_receipt()`
- [ ] Function: `verify_receipt()`
- [ ] Receipts saved to `.ggen/receipts/`

---

#### Task 3.2: Create Constitutional Ops
**File**: `src/specify_cli/ops/constitutional.py` (new)

```python
"""Constitutional equation enforcement operations."""
from pathlib import Path
from specify_cli.runtime import receipt as receipt_runtime

def check_all_receipts() -> dict:
    """Check all receipts for violations."""
    receipts_dir = Path(".ggen/receipts")
    violations = []
    valid = []

    if not receipts_dir.exists():
        return {'valid': [], 'violations': [], 'total': 0}

    for receipt_file in receipts_dir.glob("*.receipt.json"):
        if receipt_runtime.verify_receipt(receipt_file):
            valid.append(str(receipt_file))
        else:
            violation = {
                'receipt': str(receipt_file),
                'reason': 'Hash mismatch - file modified manually?',
                'fix': 'Run: specify ggen sync'
            }
            violations.append(violation)

    return {
        'valid': valid,
        'violations': violations,
        'total': len(valid) + len(violations)
    }

def verify_idempotence(input_file: Path, output_file: Path) -> bool:
    """Verify μ∘μ = μ (idempotence)."""
    # Run ggen sync twice, verify same output
    import subprocess
    import tempfile
    import shutil

    # First run
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_output1 = Path(tmpdir) / "output1.md"
        # Run ggen sync
        # ... implementation ...

        hash1 = receipt_runtime.hash_file(tmp_output1)

        # Second run (use output1 as input if applicable)
        tmp_output2 = Path(tmpdir) / "output2.md"
        # Run ggen sync again
        # ... implementation ...

        hash2 = receipt_runtime.hash_file(tmp_output2)

        return hash1 == hash2
```

**Checklist**:
- [ ] Function: `check_all_receipts()`
- [ ] Function: `verify_idempotence()`
- [ ] Returns structured violation data
- [ ] Tests added

---

#### Task 3.3: Create Verify Command
**File**: `src/specify_cli/commands/verify.py` (new)

```python
"""Constitutional equation verification."""
import typer
from rich.console import Console
from specify_cli.ops import constitutional
from specify_cli.runtime import ggen
from specify_cli.core.telemetry import timed

app = typer.Typer(help="Verify constitutional equation")
console = Console()

@app.command()
@timed
def verify(
    fix: bool = typer.Option(False, "--fix", help="Auto-fix violations"),
) -> None:
    """Verify all receipts match current files."""

    console.print("[bold]Constitutional Equation Verification[/bold]")
    console.print("=" * 70)

    result = constitutional.check_all_receipts()

    console.print(f"\nTotal receipts: {result['total']}")
    console.print(f"[green]✓ Valid: {len(result['valid'])}[/green]")

    if result['violations']:
        console.print(f"[red]✗ Violations: {len(result['violations'])}[/red]")

        for violation in result['violations']:
            console.print(f"\n[red]✗ {violation['receipt']}[/red]")
            console.print(f"  Reason: {violation['reason']}")
            console.print(f"  Fix: {violation['fix']}")

        if fix:
            console.print("\n[yellow]Auto-fixing violations...[/yellow]")
            ggen.run_sync()
            console.print("[green]✓ Fixed. Re-run verify to confirm.[/green]")
        else:
            console.print("\n[yellow]Run with --fix to automatically fix violations.[/yellow]")
            raise typer.Exit(code=1)
    else:
        console.print("\n[green]✓ All receipts valid - constitutional equation holds[/green]")
```

**Checklist**:
- [ ] Command: `specify verify`
- [ ] Flag: `--fix` auto-fixes violations
- [ ] Rich console output
- [ ] Exit code 1 on violations

---

#### Task 3.4: Enhance ggen sync
**File**: `src/specify_cli/runtime/ggen.py` (enhance existing)

```python
def run_sync(generate_receipts: bool = True) -> subprocess.CompletedProcess:
    """Run ggen sync and generate receipts."""
    from specify_cli.runtime import receipt as receipt_runtime

    # Run ggen sync
    result = run_logged(["ggen", "sync"])

    if result.returncode != 0:
        return result

    # Generate receipts for all transformations
    if generate_receipts:
        # Parse ggen.toml to find transformations
        transformations = parse_ggen_config()

        for transform in transformations:
            input_file = Path(transform['input'])
            output_file = Path(transform['output'])

            if output_file.exists():
                receipt = receipt_runtime.Receipt(
                    input_file=input_file,
                    output_file=output_file,
                    input_hash=receipt_runtime.hash_file(input_file),
                    output_hash=receipt_runtime.hash_file(output_file),
                )
                receipt.save()

    return result

def parse_ggen_config(config_path: Path = Path("docs/ggen.toml")) -> list[dict]:
    """Parse ggen.toml to extract transformations."""
    import toml

    config = toml.load(config_path)
    transformations = []

    # Extract transformations from config
    # ... implementation ...

    return transformations
```

**Checklist**:
- [ ] Enhanced `run_sync()` to generate receipts
- [ ] Function: `parse_ggen_config()`
- [ ] Receipts created for all transformations
- [ ] Tests added

---

#### Task 3.5: Create .ggen Directory
```bash
mkdir -p .ggen/receipts
touch .ggen/receipts/.gitkeep
```

**File**: `.gitignore`
```gitignore
# Constitutional equation receipts
.ggen/receipts/*.receipt.json
!.ggen/receipts/.gitkeep
```

**Checklist**:
- [ ] Directory created: `.ggen/receipts/`
- [ ] `.gitkeep` file added
- [ ] `.gitignore` updated
- [ ] Receipts tracked in git

---

#### Task 3.6: Add to Pre-Commit
**File**: `.pre-commit-config.yaml`

Add:
```yaml
  - repo: local
    hooks:
      - id: constitutional-verify
        name: Constitutional Equation Verification
        entry: uv run specify verify
        language: system
        pass_filenames: false
        always_run: true
```

**Checklist**:
- [ ] Hook added
- [ ] Test: `pre-commit run constitutional-verify`
- [ ] Blocks commits with violations

---

#### Task 3.7: Create E2E Tests
**File**: `tests/e2e/test_constitutional_enforcement.py`

```python
"""End-to-end tests for constitutional enforcement."""
import pytest
from pathlib import Path
import subprocess

def test_verify_clean_repo(tmp_path, monkeypatch):
    """Test verify passes on clean repo."""
    monkeypatch.chdir(tmp_path)

    # Setup receipts
    (tmp_path / ".ggen/receipts").mkdir(parents=True)

    # Run verify
    result = subprocess.run(
        ["uv", "run", "specify", "verify"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "All receipts valid" in result.stdout

def test_verify_detects_violations(tmp_path, monkeypatch):
    """Test verify detects modified generated files."""
    monkeypatch.chdir(tmp_path)

    # Create fake receipt
    receipts_dir = tmp_path / ".ggen/receipts"
    receipts_dir.mkdir(parents=True)

    # Create receipt with wrong hash
    # ... setup ...

    # Run verify
    result = subprocess.run(
        ["uv", "run", "specify", "verify"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert "Violations:" in result.stdout

def test_verify_fix(tmp_path, monkeypatch):
    """Test verify --fix auto-heals violations."""
    # ... implementation ...
    pass
```

**Checklist**:
- [ ] Test: `verify` on clean repo
- [ ] Test: `verify` detects violations
- [ ] Test: `verify --fix` auto-heals
- [ ] Coverage ≥ 80%

---

#### Task 3.8: Update CLAUDE.md
**File**: `CLAUDE.md`

Add section:
```markdown
## Constitutional Equation Enforcement

The equation `spec.md = μ(feature.ttl)` is now automatically enforced:

1. **Pre-Commit Hooks**: RDF validation + receipt verification
2. **Git Commands**: Use `specify git commit` for constitutional checks
3. **Verification**: Run `specify verify` to check all receipts
4. **Auto-Fix**: Run `specify verify --fix` to regenerate violated files

### Workflow

```bash
# Edit RDF source
vim ontology/cli-commands.ttl

# Generate code
specify ggen sync

# Verify
specify verify

# Commit (with constitutional checks)
specify git add .
specify git commit

# Push (with receipt verification)
specify git push
```

### Violations

If you see "Constitutional violation" errors:
1. Check which generated file was modified: `specify git status`
2. Regenerate from RDF: `specify ggen sync`
3. Verify: `specify verify`
4. Commit RDF + generated files together
```

**Checklist**:
- [ ] Section added to CLAUDE.md
- [ ] Workflow documented
- [ ] Violation resolution steps clear
- [ ] Examples provided

---

#### Task 3.9: Manual Testing
```bash
# Full workflow test
echo "@prefix ex: <http://example.org/> ." > test.ttl
specify ggen sync
specify verify
specify git status
specify git add .
specify git commit -m "test: constitutional enforcement"
specify git push --dry-run

# Test violation detection
echo "// manual edit" >> src/specify_cli/commands/init.py
specify verify  # Should detect violation

# Test auto-fix
specify verify --fix
specify verify  # Should pass now
```

**Checklist**:
- [ ] Full workflow completes successfully
- [ ] Violations detected correctly
- [ ] Auto-fix works
- [ ] Pre-commit hooks block violations

---

## Phase 1 Completion Checklist

### Day 1-2: Git Commands ✅
- [ ] `specify git status` - Works, shows violations
- [ ] `specify git add` - Stages files
- [ ] `specify git commit` - Blocks on violations, adds co-authorship
- [ ] `specify git push` - Verifies receipts
- [ ] Tests pass, coverage ≥ 80%

### Day 3-4: RDF Validator ✅
- [ ] `specify validate rdf` - Validates TTL files
- [ ] SHACL validation working
- [ ] Pre-commit hook blocks invalid RDF
- [ ] Tests pass, coverage ≥ 80%

### Day 5-7: Constitutional Enforcement ✅
- [ ] `specify verify` - Checks all receipts
- [ ] `specify verify --fix` - Auto-heals violations
- [ ] `specify ggen sync` - Generates receipts
- [ ] Pre-commit hooks enforce equation
- [ ] Tests pass, coverage ≥ 80%
- [ ] CLAUDE.md updated

### Overall Phase 1 ✅
- [ ] All commands working
- [ ] Pre-commit hooks installed and working
- [ ] Test coverage ≥ 60% (target: 80% by Week 4)
- [ ] Documentation updated
- [ ] Zero constitutional violations in repo
- [ ] CI/CD passes (if configured)

---

## Next Steps

After Phase 1 completion:
1. **Review**: Check all acceptance criteria met
2. **Commit**: Commit Phase 1 work with proper receipt
3. **Tag**: Git tag `v0.1.0-phase1-complete`
4. **Plan**: Begin Phase 2 (Week 2) planning
5. **Retrospective**: Document learnings, adjust timeline if needed

---

**Status**: Ready for Implementation
**Estimated Time**: 7 days (Week 1)
**Risk**: Low (clear requirements, existing foundation)
**Next Review**: After Week 1 Friday checkpoint
