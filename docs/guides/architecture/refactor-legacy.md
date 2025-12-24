# Refactor Legacy Code to Three-Tier Architecture

Step-by-step guide to migrate existing code to ggen spec-kit's three-tier (Commands/Ops/Runtime) architecture.

## Overview

The three-tier architecture separates concerns:

```
Commands Layer  ← CLI interface (thin wrappers)
     ↓
Operations Layer ← Pure business logic (no side effects)
     ↓
Runtime Layer ← All I/O and side effects (subprocess, files, HTTP)
```

This guide helps you refactor existing code into this structure.

## Phase 1: Assessment

### Step 1: Map Current Code

```
Existing code structure:
main.py
  └─ check_files()          ← Mix of logic + I/O
     └─ reads files         ← FILE I/O
     └─ validates data      ← LOGIC
     └─ updates database    ← HTTP I/O
     └─ prints output       ← CLI OUTPUT
```

### Step 2: Identify Layers

For each function, mark which layer it belongs to:

```python
# main.py - MIX OF LAYERS (WRONG)
def check_files(path: str):
    # COMMANDS: parse argument
    if not path:
        print("Path required")  # ← COMMANDS
        return

    # RUNTIME: file I/O
    try:
        files = os.listdir(path)  # ← RUNTIME
    except FileNotFoundError:
        print("Path not found")  # ← COMMANDS
        return

    # OPERATIONS: validate
    valid = [f for f in files if f.endswith('.txt')]  # ← OPERATIONS

    # RUNTIME: HTTP
    response = requests.post("http://api.example.com", data=valid)  # ← RUNTIME

    # COMMANDS: output
    print(f"Checked {len(valid)} files")  # ← COMMANDS
    return response.json()
```

**Result:** Everything mixed together. Need refactoring.

### Step 3: List Functions to Refactor

Create inventory:

```
Function          | Current Layer | Should Be | Effort
================  | ============== | ========= | ======
check_files()     | Mixed          | Ops       | High
read_config()     | Mixed          | Runtime   | Low
validate_data()   | Mixed          | Ops       | Medium
log_result()      | Mixed          | Commands  | Low
call_api()        | Mixed          | Runtime   | Medium
```

## Phase 2: Extract Operations Layer

Operations layer contains **pure business logic** with **no side effects**.

### Step 1: Create Operations Module

```bash
mkdir -p src/specify_cli/ops/
touch src/specify_cli/ops/check_ops.py
```

### Step 2: Extract Pure Logic

```python
# src/specify_cli/ops/check_ops.py
# Pure business logic - NO FILE I/O, NO HTTP, NO SIDE EFFECTS

def filter_valid_files(files: list[str]) -> list[str]:
    """Filter to .txt files (pure logic)"""
    return [f for f in files if f.endswith('.txt')]

def validate_file_data(file_data: dict) -> bool:
    """Validate file data against rules (pure logic)"""
    required = {'size', 'date', 'hash'}
    return all(k in file_data for k in required)

def create_check_report(valid: list[str], total: int) -> dict:
    """Create check result report (pure logic)"""
    return {
        'valid_count': len(valid),
        'total_count': total,
        'valid_files': valid,
        'success_rate': len(valid) / total if total > 0 else 0
    }
```

**Characteristics:**
- ✅ Takes parameters, returns values
- ✅ No imports from runtime layer
- ✅ No imports from commands layer
- ✅ No file I/O, subprocess, HTTP
- ✅ Deterministic (same input → same output)
- ✅ Fully testable in isolation

### Step 3: Write Tests First

```python
# tests/unit/ops/test_check_ops.py

def test_filter_valid_files():
    files = ['doc.txt', 'image.png', 'script.py', 'readme.txt']
    result = filter_valid_files(files)
    assert result == ['doc.txt', 'readme.txt']

def test_validate_file_data_success():
    data = {'size': 100, 'date': '2025-12-23', 'hash': 'abc123'}
    assert validate_file_data(data) is True

def test_validate_file_data_missing_field():
    data = {'size': 100, 'date': '2025-12-23'}  # missing 'hash'
    assert validate_file_data(data) is False

def test_create_check_report():
    report = create_check_report(['a.txt', 'b.txt'], 5)
    assert report['valid_count'] == 2
    assert report['total_count'] == 5
    assert report['success_rate'] == 0.4
```

Run tests:
```bash
uv run pytest tests/unit/ops/test_check_ops.py -v

# All should pass
tests/unit/ops/test_check_ops.py::test_filter_valid_files PASSED
tests/unit/ops/test_check_ops.py::test_validate_file_data_success PASSED
tests/unit/ops/test_check_ops.py::test_validate_file_data_missing_field PASSED
tests/unit/ops/test_check_ops.py::test_create_check_report PASSED
```

## Phase 3: Extract Runtime Layer

Runtime layer contains **all I/O operations** (files, subprocess, HTTP, etc.)

### Step 1: Create Runtime Module

```bash
mkdir -p src/specify_cli/runtime/
touch src/specify_cli/runtime/file_ops.py
```

### Step 2: Extract I/O Operations

```python
# src/specify_cli/runtime/file_ops.py
# I/O only - reads from filesystem, returns data

def read_directory(path: str) -> list[str]:
    """Read directory listing (file I/O)"""
    return os.listdir(path)

def read_file_metadata(path: str) -> dict:
    """Read file metadata (file I/O)"""
    stat = os.stat(path)
    return {
        'size': stat.st_size,
        'date': stat.st_mtime,
        'hash': compute_hash(path)  # ← Can call another I/O function
    }

def send_to_api(data: dict, endpoint: str) -> dict:
    """Send data to API (HTTP I/O)"""
    response = requests.post(endpoint, json=data)
    return response.json()
```

**Characteristics:**
- ✅ Performs actual I/O
- ✅ Takes parameters, returns data
- ✅ No imports from operations layer
- ✅ No business logic (just I/O)
- ✅ Can be mocked in tests

### Step 3: Write Integration Tests

```python
# tests/integration/runtime/test_file_ops.py

import tempfile
import os

def test_read_directory():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        open(os.path.join(tmpdir, 'file1.txt'), 'w').close()
        open(os.path.join(tmpdir, 'file2.txt'), 'w').close()

        result = read_directory(tmpdir)
        assert 'file1.txt' in result
        assert 'file2.txt' in result
```

## Phase 4: Create Commands Layer

Commands layer provides **CLI interface** using the ops and runtime layers.

### Step 1: Create Commands Module

```bash
mkdir -p src/specify_cli/commands/
touch src/specify_cli/commands/check.py
```

### Step 2: Implement Command

```python
# src/specify_cli/commands/check.py
# CLI interface - parse args, delegate to ops, format output

import typer
from rich.console import Console
from specify_cli import ops, runtime

console = Console()
app = typer.Typer()

@app.command()
def check(path: str = typer.Argument(..., help="Path to directory")):
    """Check files in directory"""

    # Validate arguments (COMMANDS LAYER)
    if not path:
        console.print("[red]Error: Path required[/red]")
        raise typer.Exit(1)

    try:
        # Call runtime to read directory (RUNTIME LAYER)
        files = runtime.file_ops.read_directory(path)

        # Call operations to process (OPERATIONS LAYER)
        valid = ops.check_ops.filter_valid_files(files)
        report = ops.check_ops.create_check_report(valid, len(files))

        # Format output (COMMANDS LAYER)
        console.print(f"[green]Checked {report['valid_count']} files[/green]")
        console.print(f"Success rate: {report['success_rate']:.1%}")

    except FileNotFoundError:
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    return report
```

**Characteristics:**
- ✅ Thin wrapper (no business logic)
- ✅ Parses CLI arguments
- ✅ Delegates to ops/runtime
- ✅ Formats output for user
- ✅ Handles errors

### Step 3: Write E2E Tests

```python
# tests/e2e/test_check_command.py

from typer.testing import CliRunner
from src.specify_cli.commands.check import app

runner = CliRunner()

def test_check_command_success(tmp_path):
    # Create test files
    (tmp_path / 'file1.txt').touch()
    (tmp_path / 'file2.txt').touch()

    result = runner.invoke(app, ['check', str(tmp_path)])

    assert result.exit_code == 0
    assert 'Checked 2 files' in result.stdout

def test_check_command_not_found():
    result = runner.invoke(app, ['check', '/nonexistent'])

    assert result.exit_code == 1
    assert 'Path not found' in result.stdout
```

## Phase 5: Verify Architecture

### Verification Checklist

```bash
# 1. Check imports
grep -r "from specify_cli.commands" src/specify_cli/ops/  # Should be empty
grep -r "from specify_cli.commands" src/specify_cli/runtime/  # Should be empty

# 2. Check file I/O
grep -r "open(" src/specify_cli/ops/  # Should be empty
grep -r "requests.post" src/specify_cli/ops/  # Should be empty

# 3. Run tests
uv run pytest tests/ -v

# 4. Run lint
ruff check src/specify_cli/

# 5. Run type check
mypy src/specify_cli/
```

### Architecture Validator

Use the architecture validator tool:

```bash
specify architecture validate

✓ Commands layer: Correct (no I/O, no ops imports)
✓ Operations layer: Correct (pure logic, no side effects)
✓ Runtime layer: Correct (I/O only, no business logic)
✓ No circular imports: Pass
✓ Dependency flow: Correct (Commands → Ops/Runtime)
```

## Phase 6: Refactor Remaining Code

Repeat phases 2-5 for other functions:

1. **Identify:** Which functions need moving?
2. **Extract:** Create ops/runtime functions
3. **Test:** Write unit/integration tests
4. **Integrate:** Use in commands layer
5. **Verify:** Check architecture compliance

## Common Patterns

### Pattern 1: Function That Does Everything

**Before:**
```python
def process_user_data(user_id: int):
    # Read from database (I/O)
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")

    # Validate (LOGIC)
    if not user:
        return None

    # Process (LOGIC)
    user['formatted_name'] = f"{user['first']} {user['last']}"

    # Write to cache (I/O)
    cache.set(f"user:{user_id}", user)

    return user
```

**After:**
```python
# ops/user_ops.py - Pure logic
def format_user_name(first: str, last: str) -> str:
    return f"{first} {last}"

def process_user_data(user: dict) -> dict:
    return {
        **user,
        'formatted_name': format_user_name(user['first'], user['last'])
    }

# runtime/database.py - I/O
def get_user(user_id: int) -> dict:
    return db.query(f"SELECT * FROM users WHERE id={user_id}")

def cache_user(user_id: int, user: dict):
    cache.set(f"user:{user_id}", user)

# commands/users.py - CLI
def get_user_command(user_id: int):
    user = runtime.database.get_user(user_id)
    if not user:
        console.print("User not found")
        return

    processed = ops.user_ops.process_user_data(user)
    runtime.database.cache_user(user_id, processed)

    console.print(f"Name: {processed['formatted_name']}")
```

### Pattern 2: External API Calls

**Before:**
```python
def analyze_document(path: str):
    # Read file (I/O)
    text = open(path).read()

    # Send to external API (I/O)
    response = requests.post("http://api/analyze", json={'text': text})

    # Parse response (LOGIC)
    result = response.json()
    summary = result['summary']
    entities = result['entities']

    # Return structured data
    return {'summary': summary, 'entities': entities}
```

**After:**
```python
# runtime/external_api.py - I/O
def analyze_with_api(text: str) -> dict:
    response = requests.post("http://api/analyze", json={'text': text})
    return response.json()

def read_file(path: str) -> str:
    return open(path).read()

# ops/analysis_ops.py - LOGIC
def extract_analysis_results(api_response: dict) -> dict:
    return {
        'summary': api_response['summary'],
        'entities': api_response['entities']
    }

# commands/analyze.py - CLI
def analyze_command(path: str):
    # I/O
    text = runtime.external_api.read_file(path)

    # I/O
    api_result = runtime.external_api.analyze_with_api(text)

    # LOGIC
    results = ops.analysis_ops.extract_analysis_results(api_result)

    # OUTPUT
    console.print(f"Summary: {results['summary']}")
```

## Migration Checklist

- [ ] Phase 1: Code assessed and mapped
- [ ] Phase 2: Operations layer created with tests
- [ ] Phase 3: Runtime layer created with tests
- [ ] Phase 4: Commands layer created with tests
- [ ] Phase 5: Architecture verified
- [ ] Phase 6: All functions refactored
- [ ] Phase 7: All tests passing
- [ ] Phase 8: Linting and type checking pass
- [ ] Phase 9: Code reviewed
- [ ] Phase 10: Merged to main

## See Also

- `implement-three-tier.md` - Three-tier architecture details
- `/docs/reference/definition-of-done.md` - Quality standards
- `/docs/guides/testing/run-tests.md` - Writing and running tests
- `CLAUDE.md` - Project architecture guidelines
