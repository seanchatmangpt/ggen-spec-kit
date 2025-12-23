# Error Prevention Through Poka-Yoke Design

Ggen spec-kit applies **Poka-Yoke** (error-proofing) design principles throughout the system to prevent errors before they occur, rather than catching them after the fact.

## What is Poka-Yoke?

**Poka-Yoke** (ポカヨケ) is a Japanese lean manufacturing concept meaning "mistake-proofing" or "foolproofing." The core principle:

> **Design systems so errors are impossible to make, not just detectable.**

Instead of:
- ❌ Waiting for errors to happen
- ❌ Catching errors with try-catch
- ❌ Teaching users not to make mistakes

We:
- ✅ Make mistakes impossible
- ✅ Design out the possibility of wrong inputs
- ✅ Build guardrails into the system

---

## Poka-Yoke Categories

### 1. Control Poka-Yoke (Prevention)

Make incorrect action impossible:

#### Type Checking
```python
# TypedDict enforces structure
class CliCommand(TypedDict):
    name: str          # Must be string
    description: str   # Must be string
    arguments: list[Argument]  # Must be list

# ✅ Correct usage
cmd: CliCommand = {
    "name": "check",
    "description": "Check availability",
    "arguments": [...]
}

# ❌ Type error - caught before runtime
cmd: CliCommand = {
    "name": "check",
    "description": 123,  # ❌ Int, not str - ERROR
    "arguments": {}  # ❌ Dict, not list - ERROR
}
```

**Benefit:** Errors caught at static analysis time, never at runtime.

#### RDF Schema Validation
```turtle
# In ontology/spec-kit-schema.ttl
sk:Command a owl:Class ;
    rdfs:comment "A CLI command" .

sk:hasArgument a rdf:Property ;
    rdfs:domain sk:Command ;
    rdfs:range sk:Argument .

sk:description a rdf:Property ;
    rdfs:domain sk:Documented ;
    rdfs:range rdfs:Literal ;
    # Constraint: required property
    owl:minCardinality 1 .
```

**SHACL validation during μ₁:**
```turtle
:CommandShape
    a sh:NodeShape ;
    sh:targetClass sk:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;  # Required
        sh:datatype xsd:string ;
        sh:pattern "^[a-z][a-z-]*$"  # Only lowercase + hyphens
    ] ;
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:minLength 10 ;  # Must be meaningful
        sh:datatype xsd:string
    ] .
```

When a command definition is written:
```turtle
# ❌ FAILS validation - no description
my:command a sk:Command ;
    rdfs:label "check" .
# Error: Property sk:description is required by SHACL shape

# ❌ FAILS validation - description too short
my:command a sk:Command ;
    rdfs:label "check" ;
    sk:description "OK" .  # 2 chars < 10 min
# Error: sh:minLength constraint violated

# ✅ PASSES validation
my:command a sk:Command ;
    rdfs:label "check" ;
    sk:description "Check that all required tools are available" .
```

**Benefit:** Specification quality errors caught at authoring time, ggen sync never fails.

---

#### Three-Tier Architecture
The three-tier design prevents logic-in-wrong-place errors:

```
Commands Layer (CLI interface only)
├─ ✅ Parse arguments
├─ ✅ Format output with Rich
├─ ❌ NO subprocess calls
├─ ❌ NO file I/O
└─ ❌ NO HTTP requests

Operations Layer (Pure business logic)
├─ ✅ Validation logic
├─ ✅ Transform data
├─ ✅ Return structured results
├─ ❌ NO subprocess calls
├─ ❌ NO file I/O
└─ ❌ NO HTTP requests

Runtime Layer (Side effects only)
├─ ✅ Subprocess calls via run_logged()
├─ ✅ All file I/O
├─ ✅ All HTTP requests
├─ ✅ All side effects
└─ ❌ NO imports from commands or ops
```

**Physical Enforcement:**
- Separate folders make violations obvious in code review
- Import checks prevent cross-layer imports
- Type hints make violations detectable

```python
# ❌ WRONG - in commands/check.py, doing file I/O
def check():
    with open("somefile.txt") as f:  # ❌ file I/O in commands!
        data = f.read()

# ✅ CORRECT - delegate to ops
def check():
    result = ops.check_impl()
    # ops/check.py handles the logic
    # runtime/process.py handles file I/O
```

**Benefit:** Separation of concerns is enforced by structure, not convention.

---

### 2. Warning Poka-Yoke (Detection)

Make wrong action easy to detect and fix:

#### Lint & Format Checks
```bash
# Automatic checks before commit
ruff check src/           # Syntax and style errors
mypy src/                 # Type errors
black --check src/        # Formatting violations
```

These fail the build, forcing fixes before merging.

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/python/black
    hooks:
      - id: black
        fail_fast: true  # Fail first error, don't continue

  - repo: https://github.com/astral-sh/ruff-pre-commit
    hooks:
      - id: ruff-check
        fail_fast: true

  - repo: https://github.com/pre-commit/mirrors-mypy
    hooks:
      - id: mypy
        additional_dependencies: ['types-all']
```

User tries to commit bad code:
```bash
$ git commit -m "my change"

# Pre-commit hooks run
- black...........PASSED
- ruff-check......FAILED
  E501 line too long (88 > 79 characters)
  E731 do not assign a lambda expression
- mypy............FAILED
  error: Unused "type: ignore" comment

# Commit is blocked until fixed
$ # User fixes errors
$ git add .
$ git commit -m "my change"
# Pre-commit hooks run again
- black...........PASSED
- ruff-check......PASSED
- mypy............PASSED
# Commit succeeds
```

**Benefit:** Errors caught at commit time, never at merge/deploy time.

#### Receipt Verification
```bash
$ ggen sync

# Receipt.json is created with SHA256 hashes
$ cat .ggen/receipt.json | jq .generated_files

{
  "src/specify_cli/commands/check.py": "sha256:abc123...",
  "src/specify_cli/commands/init.py": "sha256:def456...",
  "src/specify_cli/commands/cache.py": "sha256:ghi789..."
}

# Later, someone manually edits a generated file
$ echo "# bad code" >> src/specify_cli/commands/check.py

# Verification catches the change
$ specify ggen verify
✗ MISMATCH: src/specify_cli/commands/check.py
  Receipt hash: sha256:abc123...
  Current hash: sha256:xyz789...
  Status: MANUALLY EDITED
  Fix: Run 'ggen sync' to regenerate from RDF source
```

**Benefit:** Manual edits to generated files are detected immediately.

---

### 3. Communication Poka-Yoke (Feedback)

Make errors obvious through clear feedback:

#### Structured Error Messages
```python
# Bad error message (what not to do)
raise Exception("Error")

# Good error message (poka-yoke approach)
raise ValidationError(
    message="Project name must be lowercase with hyphens only",
    received="MyProject-123",
    expected_pattern="^[a-z][a-z0-9-]*$",
    help_text="Use: specify init my-project"
)
```

Output to user:
```
❌ ValidationError: Project name must be lowercase with hyphens only

   Received:        MyProject-123
   Expected:        ^[a-z][a-z0-9-]*$
   Valid examples:  my-project, my-awesome-project

   💡 Fix: specify init my-project
```

#### Clear CLI Help
```bash
$ specify init --help

Usage: specify init [OPTIONS] PROJECT_NAME

  Initialize a new ggen spec-kit project.

Arguments:
  PROJECT_NAME  Project name (lowercase + hyphens) [required]

Options:
  --template TEXT           Project template [default: default]
  --with-tests              Include test setup [default: false]
  --with-observability      Include OTEL setup [default: false]
  -v, --verbose             Verbose output
  -h, --help                Show this message and exit.

Examples:
  $ specify init my-project
  $ specify init my-project --with-tests --with-observability
```

**Benefit:** Users know exactly what's expected and how to fix mistakes.

#### Rich Error Formatting
```python
from rich.console import Console
from rich.table import Table

console = Console()

# Show context around error
console.print("[red]Error in ontology/cli-commands.ttl[/red]")
console.print(f"  Line 47: [yellow]{bad_line}[/yellow]")
console.print(f"  Problem: {error_description}")
console.print()
console.print("[green]Fix:[/green] Add required property 'sk:description'")
```

---

## Poka-Yoke in Practice

### Example 1: Preventing Bad RDF Specifications

**Without Poka-Yoke:**
- Write RDF specification
- Run `ggen sync`
- Get cryptic SPARQL error
- Spend 2 hours debugging

**With Poka-Yoke (SHACL validation at μ₁):**
- Write RDF specification
- Run `ggen sync`
- SHACL validation fails immediately
- Error message: "Command 'mycmd' missing required property sk:description"
- Fix takes 2 minutes
- SPARQL query never runs on invalid data

### Example 2: Preventing Cross-Layer Violations

**Without Poka-Yoke:**
- Write subprocess call in commands/ layer
- Tests pass locally
- Merge to main
- Two developers later, someone tries to test it in isolation
- Import fails, test fails, time wasted

**With Poka-Yoke (Physical separation):**
- Try to import subprocess in commands/
- IDE immediately shows red squiggle
- Type checker fails: "No module 'subprocess' in commands layer"
- Move code to runtime/ where it belongs
- Never broken in the first place

### Example 3: Preventing Manual Edits to Generated Files

**Without Poka-Yoke:**
- Generated file has bug
- Developer manually edits it
- `ggen sync` regenerates and overwrites the fix
- Developer's fix is lost, frustration ensues

**With Poka-Yoke (Receipt verification):**
- Developer edits generated file
- Pre-commit hook runs `specify ggen verify`
- Hash mismatch detected: file was manually edited
- Commit blocked with message:
  ```
  ❌ Cannot commit: src/commands/check.py was manually edited
  ✅ Fix: Run 'ggen sync' to regenerate from RDF source
  ```
- Developer regenerates from RDF
- Commit succeeds

---

## Defense in Depth

Ggen uses **multiple layers** of error prevention:

```
Layer 1: Type System
  ├─ TypedDict, Protocol, Union types
  └─ mypy static analysis
       ↓
Layer 2: RDF Schema
  ├─ SHACL constraint shapes
  └─ Validation at μ₁
       ↓
Layer 3: Architecture
  ├─ Three-tier layer separation
  └─ Import guards, type hints
       ↓
Layer 4: Testing
  ├─ Unit tests per module
  ├─ Integration tests
  └─ E2E tests
       ↓
Layer 5: Pre-commit Checks
  ├─ Format checks (black)
  ├─ Lint checks (ruff)
  ├─ Type checks (mypy)
  └─ Receipt verification
       ↓
Layer 6: CI/CD Checks
  ├─ Full test suite
  ├─ Coverage requirements
  └─ Build verification
       ↓
Layer 7: Receipt Verification
  └─ Post-deployment hash verification
```

If error somehow bypasses layers 1-6, it's still caught by layer 7.

---

## Costs vs. Benefits

### Upfront Costs
- Time to write SHACL shapes
- Time to write comprehensive types
- Time to set up pre-commit hooks
- Time to write tests

### Long-term Benefits
- Errors prevented, not caught
- Faster debugging (error at authoring time, not runtime)
- Fewer bugs in production
- Easier onboarding (clear constraints)
- Better documentation (types and shapes are self-documenting)

**ROI:** First saved error pays for all the prevention infrastructure.

---

## Best Practices

### DO ✅
- Use type hints on all functions
- Write SHACL shapes for all RDF classes
- Make invalid states impossible
- Fail fast with clear messages
- Use tests as specification
- Document constraints (via types, shapes, help text)

### DON'T ❌
- Rely on runtime error handling for common cases
- Write overly permissive schemas
- Hope users read documentation
- Catch exceptions and continue silently
- Use string types where you could use enums
- Test for things that should be impossible to do

---

## See Also

- `/docs/guides/architecture/implement-three-tier.md` - How three-tier separation works
- `/docs/guides/rdf/write-rdf-spec.md` - Writing SHACL shapes
- `/docs/guides/testing/run-tests.md` - Test as specification
- `/docs/reference/rdf-ontology.md` - RDF ontology reference
- `constitutional-equation.md` - Why this architecture works

---

**Philosophy:** Make the right thing easy to do and the wrong thing impossible to do.
