# Architecture Overview

The specify-cli toolkit implements a strict three-tier architecture that separates concerns and ensures maintainability, testability, and observability.

## Architectural Principles

### Constitutional Equation

All specifications follow the constitutional equation:

```
spec.md = μ(feature.ttl)
```

Where μ is the five-stage transformation:
1. **μ₁ Normalize**: Validate SHACL shapes
2. **μ₂ Extract**: Execute SPARQL queries
3. **μ₃ Emit**: Render Tera templates
4. **μ₄ Canonicalize**: Format output
5. **μ₅ Receipt**: SHA256 hash proof

This ensures all CLI commands are derived from semantic RDF specifications.

## Three-Tier Architecture

```
┌────────────────────────────────────────────────────────────┐
│  CLI Application (app.py)                                  │
│  • Typer application assembly                              │
│  • Command registration                                    │
│  • Banner and help formatting                              │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│  Commands Layer (commands/)                                │
│  • Typer command handlers                                  │
│  • Argument parsing and validation                         │
│  • Rich output formatting                                  │
│  • @instrument_command decorators                          │
│  • Error display and user feedback                         │
│                                                             │
│  RULES:                                                     │
│  ✓ Parse CLI arguments                                     │
│  ✓ Format output with Rich                                 │
│  ✓ Delegate to ops layer immediately                       │
│  ✗ NO subprocess calls                                     │
│  ✗ NO file I/O                                             │
│  ✗ NO HTTP requests                                        │
│  ✗ NO business logic                                       │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│  Operations Layer (ops/)                                   │
│  • Pure business logic                                     │
│  • Data validation                                         │
│  • State management                                        │
│  • Algorithm implementation                                │
│  • Return structured data (dicts)                          │
│  • Telemetry span events                                   │
│                                                             │
│  RULES:                                                     │
│  ✓ Validate inputs                                         │
│  ✓ Pure computation                                        │
│  ✓ Return structured data                                  │
│  ✓ Record telemetry events                                 │
│  ✗ NO subprocess calls                                     │
│  ✗ NO file I/O                                             │
│  ✗ NO HTTP requests                                        │
│  ✗ NO side effects                                         │
└──────────────────────┬─────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────┐
│  Runtime Layer (runtime/)                                  │
│  • All subprocess execution                                │
│  • All file I/O operations                                 │
│  • All HTTP requests                                       │
│  • External tool integration                               │
│  • OpenTelemetry spans                                     │
│  • Error handling with context                             │
│                                                             │
│  RULES:                                                     │
│  ✓ Execute subprocesses with run_logged()                  │
│  ✓ Use shell=False (security)                              │
│  ✓ Validate paths before operations                        │
│  ✓ Handle errors with proper context                       │
│  ✓ Record comprehensive telemetry                          │
│  ✗ NO imports from commands or ops                         │
│  ✗ NO business logic                                       │
└────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### Commands Layer (`src/specify_cli/commands/`)

**Purpose**: Thin CLI interface that bridges user input to business logic.

**Responsibilities**:
- Parse command-line arguments using Typer
- Format output using Rich (tables, progress bars, colors)
- Display errors and user feedback
- Apply `@instrument_command` decorator for telemetry
- Delegate immediately to ops layer

**Example Structure**:

```python
# src/specify_cli/commands/deps.py
import typer
from rich.console import Console
from specify_cli.core.instrumentation import instrument_command
from specify_cli import ops

app = typer.Typer(help="Dependency management")
console = Console()

@app.command("add")
@instrument_command("deps.add")
def add_command(
    pkgs: list[str],
    dev: bool = typer.Option(False, "--dev", "-D"),
) -> None:
    """Add packages to project dependencies."""
    # 1. Parse arguments (done by Typer)
    # 2. Delegate to ops layer
    result = ops.deps.add(packages=pkgs, dev=dev)

    # 3. Format and display output
    if result["success"]:
        console.print(f"[green]✓[/] Added {len(pkgs)} package(s)")
    else:
        console.print(f"[red]✗[/] {result['error']}", style="bold red")
        raise typer.Exit(1)
```

**Key Features**:
- No side effects
- Immediate delegation
- Rich output formatting
- Comprehensive error display

### Operations Layer (`src/specify_cli/ops/`)

**Purpose**: Pure business logic with no side effects.

**Responsibilities**:
- Validate inputs and preconditions
- Implement algorithms and transformations
- Manage state and data structures
- Return structured data (dictionaries)
- Record telemetry events (but not I/O)
- Raise appropriate exceptions

**Example Structure**:

```python
# src/specify_cli/ops/deps.py
from typing import Any
from specify_cli.core.instrumentation import add_span_event, add_span_attributes
from specify_cli.core.telemetry import metric_counter

def add(packages: list[str], dev: bool = False) -> dict[str, Any]:
    """Add packages to dependencies (business logic)."""
    # 1. Validate inputs
    add_span_event("deps.add.started", {"package_count": len(packages)})

    if not packages:
        return {"success": False, "error": "No packages specified"}

    # 2. Validate package names
    for pkg in packages:
        if not _is_valid_package_name(pkg):
            return {"success": False, "error": f"Invalid package: {pkg}"}

    # 3. Build command parameters for runtime layer
    runtime_params = {
        "packages": packages,
        "dev": dev,
        "operation": "add",
    }

    # 4. Record metrics
    metric_counter("deps.add.operations")(1)
    add_span_event("deps.add.completed", {"status": "validated"})

    # 5. Return structured data
    return {
        "success": True,
        "command": "deps",
        "subcommand": "add",
        "params": runtime_params,
        "timestamp": datetime.utcnow().isoformat(),
    }

def _is_valid_package_name(name: str) -> bool:
    """Validate package name format (pure function)."""
    import re
    return bool(re.match(r'^[a-zA-Z0-9_-]+', name))
```

**Key Features**:
- Pure functions (no side effects)
- Comprehensive validation
- Structured return values
- Telemetry event recording
- Exception handling with context

### Runtime Layer (`src/specify_cli/runtime/`)

**Purpose**: Execute all side effects (subprocess, I/O, HTTP).

**Responsibilities**:
- Execute subprocess calls using `run_logged()`
- Perform file I/O operations
- Make HTTP requests
- Integrate with external tools
- Record OpenTelemetry spans
- Handle errors with proper context

**Example Structure**:

```python
# src/specify_cli/runtime/deps.py
from typing import Any
from pathlib import Path
import subprocess
from specify_cli.core.process import run_logged
from specify_cli.core.telemetry import span, metric_counter
from specify_cli.core.shell import timed

@timed
def add(packages: list[str], dev: bool = False) -> dict[str, Any]:
    """Execute uv add command (runtime I/O)."""
    with span("deps.add.runtime", package_count=len(packages)):
        try:
            # 1. Build command (list-based, NO shell=True)
            cmd = ["uv", "add"]

            if dev:
                cmd.append("--dev")

            cmd.extend(packages)

            # 2. Execute subprocess with logging
            output = run_logged(cmd, capture=True, check=True)

            # 3. Record success metrics
            metric_counter("deps.add.runtime.success")(1)

            return {
                "success": True,
                "output": output,
                "returncode": 0,
                "message": f"Added {len(packages)} package(s)",
            }

        except subprocess.CalledProcessError as e:
            # 4. Handle subprocess errors
            metric_counter("deps.add.runtime.failed")(1)
            return {
                "success": False,
                "error": str(e),
                "returncode": e.returncode,
                "message": f"Failed with exit code {e.returncode}",
            }

        except FileNotFoundError:
            # 5. Handle tool not found
            return {
                "success": False,
                "error": "uv not found in PATH",
                "returncode": 127,
                "message": "Install uv first",
            }
```

**Key Features**:
- All subprocess calls via `run_logged()`
- Security-first: `shell=False` always
- Path validation before I/O
- Comprehensive error handling
- Telemetry spans for all operations

## Core Utilities (`src/specify_cli/core/`)

Shared utilities used across all layers:

### telemetry.py
- OpenTelemetry setup and configuration
- Span, metric, and event creation
- Graceful degradation when OTEL unavailable

### instrumentation.py
- `@instrument_command` decorator
- Automatic span creation for CLI commands
- Span attribute and event helpers

### process.py
- `run()`: Execute subprocess with telemetry
- `run_logged()`: Execute with logging
- `which()`: Find executables in PATH
- Security-first subprocess execution

### shell.py
- `timed()`: Decorator for timing functions
- `colour()`: Terminal color output
- Rich traceback installation

### config.py
- Configuration file management
- Environment variable handling
- Settings validation

### error_handling.py
- Custom exception classes
- Error formatting and display
- Exception context management

## Data Flow

### Typical Command Execution Flow

```
User Input
    │
    ▼
┌─────────────────────────┐
│ CLI (commands/)         │
│ • Parse arguments       │
│ • Validate format       │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Ops (ops/)              │
│ • Validate business     │
│ • Check preconditions   │
│ • Compute parameters    │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Runtime (runtime/)      │
│ • Execute subprocess    │
│ • Perform I/O           │
│ • Return results        │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Ops (ops/)              │
│ • Process results       │
│ • Format data           │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ CLI (commands/)         │
│ • Display to user       │
│ • Exit with code        │
└─────────────────────────┘
```

### Example: `specify deps add requests`

```python
# 1. CLI Layer parses input
@app.command("add")
def add_command(pkgs: list[str], dev: bool = False):
    # 2. Delegate to ops layer
    validation_result = ops.deps.validate_add(pkgs, dev)

    if not validation_result["valid"]:
        console.print(f"[red]Error: {validation_result['error']}")
        raise typer.Exit(1)

    # 3. Ops layer validated, now execute via runtime
    runtime_result = runtime.deps.add(pkgs, dev)

    # 4. Display results
    if runtime_result["success"]:
        console.print(f"[green]✓[/] {runtime_result['message']}")
    else:
        console.print(f"[red]✗[/] {runtime_result['error']}")
        raise typer.Exit(runtime_result["returncode"])
```

## Telemetry Architecture

All layers emit OpenTelemetry signals:

### Spans
- **Commands**: Automatic via `@instrument_command`
- **Operations**: Manual via `span()` context manager
- **Runtime**: Automatic via `@timed` and `span()`

### Metrics
- **Counters**: Operation counts, success/failure rates
- **Histograms**: Duration measurements
- **Gauges**: Resource usage

### Events
- **Lifecycle**: start, complete, failed
- **Milestones**: validation, execution, result processing

## Project Structure

```
src/specify_cli/
├── app.py                    # Main Typer application
├── __init__.py               # Package exports
│
├── commands/                 # CLI Layer
│   ├── __init__.py
│   ├── deps.py              # Dependency management
│   ├── build.py             # Package building
│   ├── tests.py             # Test execution
│   ├── cache.py             # Cache management
│   ├── lint.py              # Code quality
│   ├── otel.py              # OpenTelemetry
│   ├── guides.py            # Development guides
│   ├── worktree.py          # Git worktree
│   ├── infodesign.py        # Information design
│   ├── mermaid.py           # Diagram generation
│   ├── dod.py               # Definition of Done
│   ├── docs.py              # Documentation
│   ├── terraform.py         # Infrastructure
│   ├── check.py             # Tool checking
│   ├── init.py              # Project initialization
│   ├── version.py           # Version management
│   ├── ggen.py              # RDF transformation
│   ├── spiff.py             # Workflow automation
│   └── pm.py                # Process mining
│
├── ops/                      # Operations Layer
│   ├── __init__.py
│   ├── deps.py              # deps business logic
│   ├── build.py             # build business logic
│   ├── tests.py             # tests business logic
│   ├── cache.py             # cache business logic
│   ├── lint.py              # lint business logic
│   ├── otel.py              # otel business logic
│   ├── guides.py            # guides business logic
│   ├── worktree.py          # worktree business logic
│   ├── infodesign.py        # infodesign business logic
│   ├── mermaid.py           # mermaid business logic
│   ├── dod.py               # dod business logic
│   ├── docs.py              # docs business logic
│   ├── terraform.py         # terraform business logic
│   ├── check.py             # Tool checking logic
│   ├── init.py              # Initialization logic
│   ├── version.py           # Version logic
│   ├── transform.py         # RDF transformation
│   └── process_mining.py    # Process mining logic
│
├── runtime/                  # Runtime Layer
│   ├── __init__.py
│   ├── deps.py              # uv subprocess calls
│   ├── build.py             # PyInstaller/build calls
│   ├── tests.py             # pytest subprocess calls
│   ├── cache.py             # Cache file operations
│   ├── lint.py              # ruff/mypy subprocess
│   ├── otel.py              # OTEL validation
│   ├── guides.py            # Guide file reading
│   ├── worktree.py          # git worktree calls
│   ├── infodesign.py        # Doc file operations
│   ├── mermaid.py           # Mermaid generation
│   ├── dod.py               # DoD file operations
│   ├── docs.py              # Doc generation calls
│   ├── terraform.py         # terraform subprocess
│   ├── ggen.py              # ggen subprocess calls
│   ├── git.py               # Git operations
│   ├── github.py            # GitHub API calls
│   ├── template.py          # Template file I/O
│   └── tools.py             # Tool detection
│
├── core/                     # Shared Utilities
│   ├── __init__.py
│   ├── telemetry.py         # OpenTelemetry setup
│   ├── instrumentation.py   # Decorator helpers
│   ├── process.py           # Subprocess execution
│   ├── shell.py             # Shell utilities
│   ├── config.py            # Configuration
│   ├── error_handling.py    # Error management
│   ├── semconv.py           # Semantic conventions
│   └── cache.py             # Caching utilities
│
└── cli/                      # CLI Utilities
    ├── __init__.py
    ├── banner.py            # Banner display
    ├── groups.py            # Command groups
    └── helpers.py           # CLI helpers
```

## Security Principles

1. **No Shell Execution**: Always use `shell=False` in subprocess calls
2. **List-Based Commands**: Build commands as lists, never strings
3. **Path Validation**: Validate all file paths before operations
4. **Input Sanitization**: Validate all user input in ops layer
5. **Secure Defaults**: Use safe defaults (e.g., 0o600 for temp files)
6. **Error Context**: Never expose sensitive data in error messages

## Testing Strategy

Each layer has distinct testing approaches:

### Commands Layer
- Integration tests with Click testing utilities
- Mock ops layer responses
- Verify output formatting
- Test error handling and exit codes

### Operations Layer
- Unit tests with comprehensive coverage
- Pure function testing
- No mocking (pure logic)
- Property-based testing where applicable

### Runtime Layer
- Integration tests with real tools
- Mock subprocess calls for unit tests
- Test error conditions (tool not found, etc.)
- Verify telemetry emission

## Performance Considerations

- **Lazy Loading**: Optional dependencies loaded on demand
- **Caching**: Results cached where appropriate
- **Parallelism**: Support parallel execution where safe
- **Streaming**: Large outputs streamed, not buffered
- **Telemetry Overhead**: Minimal with graceful degradation

## Extension Points

### Adding New Commands

1. Create RDF specification in `ontology/cli-commands-*.ttl`
2. Generate command stub from specification
3. Implement three layers:
   - Command in `commands/`
   - Operations in `ops/`
   - Runtime in `runtime/`
4. Add tests for each layer
5. Update documentation

See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for details.

## Next Steps

- See [UVMGR_USAGE_GUIDE.md](./UVMGR_USAGE_GUIDE.md) for user documentation
- See [IMPLEMENTATION_GUIDE.md](./IMPLEMENTATION_GUIDE.md) for adding commands
- See [RDF_SPECIFICATION.md](./RDF_SPECIFICATION.md) for RDF ontology
- See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for testing
- See [TELEMETRY_GUIDE.md](./TELEMETRY_GUIDE.md) for observability
