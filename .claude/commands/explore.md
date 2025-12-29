# Explore Codebase

Explore and understand codebase structure, patterns, and architecture through systematic investigation.

## Description
Conducts thorough codebase analysis to map components, understand data flows, identify patterns, and document architecture.

## Usage
```bash
/explore [TOPIC]
```

## Arguments
- `TOPIC` (optional) - Specific area to explore (e.g., "telemetry", "ggen integration", "three-tier architecture")

## Examples
```bash
# Explore entire codebase structure
/explore

# Explore specific subsystem
/explore telemetry

# Explore integration points
/explore ggen integration

# Explore layer architecture
/explore three-tier architecture

# Explore testing patterns
/explore test patterns

# Explore RDF specifications
/explore RDF workflow
```

## What This Command Does

### Without Topic: Full Codebase Overview

Provides comprehensive project analysis:

1. **Directory Structure**
   ```bash
   # Use Glob to map directory tree
   **/*.py, **/*.ttl, **/*.toml, **/*.md
   ```

2. **Architecture Layers**
   ```
   src/specify_cli/
   ├── commands/     # CLI interface (Typer)
   ├── ops/          # Business logic (pure)
   ├── runtime/      # Side effects (I/O, subprocess)
   ├── core/         # Shared utilities
   └── cli/          # CLI helpers
   ```

3. **RDF-First Components**
   ```
   ontology/         # Schema definitions (source of truth)
   memory/           # Specifications (source of truth)
   sparql/           # Query templates
   templates/        # Code generation templates
   ```

### With Topic: Focused Investigation

Deep dive into specific area:

1. **Search for Relevant Files**
   ```bash
   # Use parallel Glob and Grep
   Glob("**/*{topic}*.py")
   Grep("{topic}", output_mode="files_with_matches")
   ```

2. **Read Key Files**
   ```bash
   # Parallel Read of discovered files
   Read("src/path/to/module1.py")
   Read("src/path/to/module2.py")
   Read("tests/path/to/test.py")
   ```

3. **Map Dependencies**
   ```bash
   # Find import relationships
   Grep("^import|^from", output_mode="content")
   ```

4. **Identify Entry Points**
   ```bash
   # Find CLI commands, main functions
   Grep("@app.command|def main|if __name__", output_mode="content")
   ```

## Investigation Strategy

### Phase 1: Discovery (Parallel)
```python
# Execute these in parallel for speed
Glob("**/*.py", path="src/specify_cli")
Glob("**/*.ttl", path="ontology")
Glob("**/*.toml")
Grep("class |def ", output_mode="files_with_matches")
```

### Phase 2: Analysis (Parallel Reads)
```python
# Read discovered files in parallel
Read("file1.py")
Read("file2.py")
Read("file3.py")
Read("ontology/schema.ttl")
```

### Phase 3: Synthesis
- Map relationships
- Identify patterns
- Document flows
- Note observations

## Output Format

Provides structured exploration report:

### Executive Summary
- Project type and purpose
- Primary languages and frameworks
- Architecture style
- Key design patterns

### Directory Structure
```
/home/user/ggen-spec-kit/
├── src/specify_cli/          # Source code
│   ├── commands/             # CLI commands (generated)
│   ├── ops/                  # Business logic (pure)
│   ├── runtime/              # Side effects (I/O)
│   └── core/                 # Shared utilities
├── ontology/                 # RDF schemas (SOURCE OF TRUTH)
├── memory/                   # RDF specifications (SOURCE OF TRUTH)
├── tests/                    # Test suites
│   ├── unit/                 # Unit tests
│   └── e2e/                  # End-to-end tests
├── sparql/                   # SPARQL queries
└── templates/                # Tera templates
```

### Component Map

For each major component:

| Component | Location | Purpose | Dependencies |
|-----------|----------|---------|--------------|
| Telemetry | `core/telemetry.py` | OTEL instrumentation | `opentelemetry-sdk` |
| Process | `core/process.py` | Subprocess wrapper | `subprocess`, telemetry |
| GGen Ops | `ops/ggen_ops.py` | ggen business logic | None (pure) |
| GGen Runtime | `runtime/ggen_runtime.py` | ggen subprocess execution | process, telemetry |

### Data Flow Diagrams

```
User Command → CLI (commands/) → Operations (ops/) → Runtime (runtime/) → External Tools
                ↓                      ↓                    ↓
            Parse args         Business logic        Subprocess/I/O
            Format output      Return data           Run ggen, git, etc.
```

### Key Patterns

#### Three-Tier Architecture
```python
# Commands Layer (thin wrapper)
def command(arg: str):
    result = ops.operation(arg)  # Delegate to ops
    display(result)              # Format output

# Operations Layer (pure logic)
def operation(arg: str) -> dict:
    # Pure business logic
    return {"data": processed}

# Runtime Layer (side effects)
def execute(cmd: list[str]) -> str:
    return run_logged(cmd)  # All I/O here
```

#### RDF-First Development
```turtle
# Source: ontology/cli-commands.ttl
sk:command a sk:Command ;
           rdfs:label "command" .

# ↓ ggen sync ↓

# Generated: commands/command_cmd.py
def command(): ...
```

#### OpenTelemetry Instrumentation
```python
from specify_cli.core.telemetry import span, timed

@timed
def operation():
    with span("operation.step"):
        # instrumented code
```

### Entry Points

| Entry Point | Location | Purpose |
|-------------|----------|---------|
| `specify` | `src/specify_cli/__main__.py` | Main CLI entry |
| `ggen sync` | External (v5.0.2) | RDF transformation |
| `pytest` | `tests/` | Test execution |

### Dependencies

#### Core Dependencies
```toml
typer         # CLI framework
rich          # Terminal formatting
httpx         # HTTP client
platformdirs  # Cross-platform paths
opentelemetry # Observability
```

#### Development Dependencies
```toml
pytest        # Testing
ruff          # Linting
mypy          # Type checking
```

### Code Metrics

- Total Python files: X
- Total lines of code: Y
- Test coverage: Z%
- Type hint coverage: W%

### Observations and Recommendations

- Architecture compliance status
- Code quality highlights
- Potential improvements
- Missing documentation
- Testing gaps

## Common Exploration Topics

### Telemetry System
```bash
/explore telemetry
# → core/telemetry.py
# → @timed decorators usage
# → span() context managers
# → OTEL configuration
```

### GGen Integration
```bash
/explore ggen integration
# → ops/ggen_ops.py (business logic)
# → runtime/ggen_runtime.py (subprocess)
# → ontology/*.ttl (specifications)
# → templates/*.tera (code generation)
```

### Testing Strategy
```bash
/explore test patterns
# → tests/unit/ (isolated tests)
# → tests/e2e/ (integration tests)
# → Generated tests vs manual tests
# → Coverage gaps
```

### CLI Commands
```bash
/explore CLI commands
# → commands/*.py (generated)
# → ontology/cli-commands.ttl (source)
# → How commands are registered
# → Argument parsing patterns
```

## Integration

Works with:
- `Glob` - File pattern matching
- `Grep` - Content search
- `Read` - File reading (use parallel calls!)
- Git history - Change analysis
- OTEL traces - Runtime analysis

## Performance Tips

**Use Parallel Tool Calls!**

```python
# ✅ GOOD: Parallel exploration
[Single Message]:
  Glob("**/*.py")
  Glob("**/*.ttl")
  Grep("class ", output_mode="files")
  Grep("def ", output_mode="files")

# ❌ BAD: Sequential exploration
Message 1: Glob("**/*.py")
Message 2: Glob("**/*.ttl")     # Should be parallel!
Message 3: Grep("class ")       # Should be parallel!
```

## Notes
- Start broad, then narrow focus
- Use parallel tool calls for discovery phase
- Read multiple files in parallel when possible
- Map dependencies to understand coupling
- Identify layer violations during exploration
- Document architectural patterns found
- Note any constitutional equation violations
