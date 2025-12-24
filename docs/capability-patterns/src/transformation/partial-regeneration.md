# 28. Partial Regeneration

★

*Not every change requires regenerating everything. Partial regeneration transforms only what's affected, saving time while maintaining consistency. This is the optimization that makes specification-driven development practical at scale.*

---

## The Efficiency Imperative

Full regeneration is safe. Every `ggen sync` guarantees all artifacts match their specifications. But as your specification grows—100 commands, 500 commands, 1000 commands—full regeneration becomes slow.

```bash
# At 50 commands: ggen sync takes 2 seconds. Acceptable.
# At 500 commands: ggen sync takes 45 seconds. Annoying.
# At 5000 commands: ggen sync takes 8 minutes. Unacceptable.
```

You changed one command's description. Do you really need to regenerate 5000 files?

Partial regeneration answers: No. Regenerate only what's affected—the files that depend on what changed. Change one command? Regenerate that command's files. Change a template? Regenerate all files using that template. Change a shape? Regenerate files validated by that shape.

The key is dependency tracking: understanding what depends on what, so you know what to regenerate when something changes.

---

## The Selective Update Problem

**The fundamental challenge: Full regeneration wastes time on unchanged artifacts. But selective regeneration risks missing affected artifacts. The solution requires tracking dependencies accurately.**

Let us examine the dependency landscape:

### Direct Dependencies

A generated file depends directly on its source specification:

```
cli-commands.ttl → src/commands/validate.py
                 → src/commands/check.py
                 → docs/commands/validate.md
```

Change `cli-commands.ttl`, and all these files need regeneration.

### Template Dependencies

Multiple files depend on the same template:

```
command.py.tera → src/commands/validate.py
                → src/commands/check.py
                → src/commands/transform.py
                → ... (all command files)
```

Change the template, all files using it need regeneration.

### Shape Dependencies

Files validated by a shape indirectly depend on it:

```
command-shape.ttl ─validates→ cli-commands.ttl → all command files
```

Change the shape, and validation behavior changes. All files validated by that shape might need regeneration.

### Query Dependencies

Files using a SPARQL query depend on it:

```
command-extract.rq → extract step → template → all command files
```

Change the query, extraction changes, files need regeneration.

### Transitive Dependencies

Dependencies chain:

```
shapes/common.ttl (shared shape)
    ↓ (imported by)
shapes/command-shape.ttl
    ↓ (validates)
cli-commands.ttl
    ↓ (generates)
src/commands/*.py, docs/commands/*.md
```

Change `common.ttl` at the top, everything downstream might need regeneration.

---

## The Forces

Several tensions shape partial regeneration:

### Force: Speed vs. Safety

*Partial regeneration is fast. Full regeneration is safe. How do you choose?*

Partial regeneration might miss a dependency. The result: inconsistent artifacts. Full regeneration never misses. The result: correct but slow.

**Resolution:** Track dependencies conservatively. When uncertain, regenerate more. Default to full regeneration if dependency graph might be stale.

### Force: Precision vs. Complexity

*Fine-grained tracking enables precise regeneration. But fine-grained tracking is complex.*

You could track every property of every resource. Then you'd know exactly which files need regeneration for any change. But the tracking overhead might exceed the regeneration savings.

**Resolution:** Track at appropriate granularity. File-level is usually sufficient. Property-level is overkill for most projects.

### Force: Freshness vs. Caching

*Caches speed up regeneration. But stale caches cause inconsistency.*

Cache query results? They might be stale if the source changed. Cache template output? The template might have changed.

**Resolution:** Invalidate caches based on hash changes. Hash the inputs; if the hash changes, the cache is invalid.

### Force: Developer Experience vs. CI Rigor

*Developers want fast feedback. CI wants guaranteed correctness.*

```bash
# Developer workflow: partial regeneration for speed
ggen sync  # Only regenerate affected files

# CI workflow: full regeneration for safety
ggen sync --full  # Regenerate everything
```

**Resolution:** Partial for development, full for CI. Or: partial always, with periodic full verification.

---

## Therefore

**Implement partial regeneration with explicit dependency tracking, regenerating only files affected by changes. Fall back to full regeneration when dependency information is uncertain or when critical files change.**

The partial regeneration algorithm:

```
┌────────────────────────────────────────────────────────────────────┐
│  PARTIAL REGENERATION                                               │
│                                                                     │
│  1. DETECT changes                                                  │
│     ├── Compare current file hashes to previous run                │
│     ├── Or use git diff against last sync                          │
│     └── Build changed file set                                     │
│                                                                     │
│  2. CHECK for meta-file changes                                     │
│     ├── If ggen.toml changed → FULL REGENERATION                   │
│     ├── If shapes changed → FULL REGENERATION (or shape-aware)     │
│     └── If templates changed → regenerate all using that template  │
│                                                                     │
│  3. COMPUTE affected outputs                                        │
│     ├── Load dependency graph                                      │
│     ├── For each changed file, find dependent outputs              │
│     └── Include transitive dependencies                            │
│                                                                     │
│  4. REGENERATE affected outputs only                                │
│     ├── Run μ pipeline for each affected output                    │
│     └── Update dependency graph with new hashes                    │
│                                                                     │
│  5. VERIFY consistency (optional)                                   │
│     └── Periodically run full regeneration to verify               │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Tracking

### Dependency Graph Structure

```python
@dataclass
class DependencyGraph:
    """Track dependencies between files."""

    # Output file → list of input files it depends on
    dependencies: dict[Path, list[Path]]

    # Input file → list of output files that depend on it
    reverse: dict[Path, list[Path]]

    # File → hash of contents
    hashes: dict[Path, str]

    def outputs_for(self, input_file: Path) -> set[Path]:
        """Find all outputs affected by an input file change."""
        return set(self.reverse.get(input_file, []))

    def inputs_for(self, output_file: Path) -> set[Path]:
        """Find all inputs that an output file depends on."""
        return set(self.dependencies.get(output_file, []))
```

### Building the Dependency Graph

```python
def build_dependency_graph(config: Config) -> DependencyGraph:
    """Build dependency graph from configuration."""

    graph = DependencyGraph(
        dependencies={},
        reverse={},
        hashes={}
    )

    for target in config.targets:
        output_pattern = target.output  # e.g., "src/commands/{{ name }}.py"
        source = target.source
        query = target.query
        template = target.template

        # For each concrete output this target generates
        for output in expand_output_pattern(output_pattern, source):
            # Record dependencies
            deps = [source, query, template]

            # Add shape dependencies
            for shape in config.shapes:
                deps.append(shape)

            graph.dependencies[output] = deps

            # Build reverse index
            for dep in deps:
                if dep not in graph.reverse:
                    graph.reverse[dep] = []
                graph.reverse[dep].append(output)

            # Record current hash
            if output.exists():
                graph.hashes[output] = compute_hash(output)

    return graph
```

### Detecting Changes

```python
def detect_changes(
    current_graph: DependencyGraph,
    previous_graph: DependencyGraph
) -> set[Path]:
    """Detect files that changed since last run."""

    changed = set()

    # Check all inputs in current graph
    all_inputs = set(current_graph.reverse.keys())

    for input_file in all_inputs:
        current_hash = compute_hash(input_file)
        previous_hash = previous_graph.hashes.get(input_file)

        if current_hash != previous_hash:
            changed.add(input_file)

    return changed


def detect_changes_git(since: str = "HEAD~1") -> set[Path]:
    """Detect changes using git diff."""
    result = subprocess.run(
        ["git", "diff", "--name-only", since],
        capture_output=True, text=True, check=True
    )
    return {Path(f) for f in result.stdout.strip().split('\n') if f}
```

### Computing Affected Outputs

```python
def affected_outputs(
    changed: set[Path],
    graph: DependencyGraph
) -> set[Path]:
    """Compute all outputs affected by changed inputs."""

    affected = set()

    for changed_file in changed:
        # Direct dependents
        direct = graph.outputs_for(changed_file)
        affected.update(direct)

        # Handle special cases
        if is_template(changed_file):
            # Template change affects all outputs using it
            affected.update(graph.outputs_for(changed_file))

        if is_shape(changed_file):
            # Shape change affects all validated specifications
            # which in turn affects all their outputs
            for spec in specs_validated_by(changed_file):
                affected.update(graph.outputs_for(spec))

    return affected
```

---

## Meta-File Handling

Certain files affect everything when changed:

### Configuration Changes

```python
META_FILES = {
    "ggen.toml",      # Pipeline configuration
    "pyproject.toml", # Project configuration
}

def requires_full_regeneration(changed: set[Path]) -> bool:
    """Check if changes require full regeneration."""
    for changed_file in changed:
        if changed_file.name in META_FILES:
            return True
    return False
```

### Shape Changes

Shape changes are particularly important:

```python
def handle_shape_change(
    changed_shape: Path,
    graph: DependencyGraph,
    config: Config
) -> set[Path]:
    """Handle shape file change."""

    affected = set()

    # Find all specs validated by this shape
    for target in config.targets:
        if changed_shape in target.shapes:
            # This shape validates this target's source
            source = target.source
            # All outputs from this source are affected
            affected.update(graph.outputs_for(source))

    return affected
```

### Template Changes

```python
def handle_template_change(
    changed_template: Path,
    graph: DependencyGraph,
    config: Config
) -> set[Path]:
    """Handle template file change."""

    affected = set()

    # Find all targets using this template
    for target in config.targets:
        if target.template == changed_template:
            # All outputs from this target are affected
            for output in expand_output_pattern(target.output, target.source):
                affected.add(output)

    return affected
```

---

## Configuration

```toml
# ggen.toml

[regeneration]
mode = "partial"  # partial | full
track_dependencies = true

# When to force full regeneration
[regeneration.full_triggers]
config_change = true     # ggen.toml changed
shape_change = true      # Any shape file changed
all_templates = false    # Any template changed (vs. per-template)

# Dependency graph storage
[regeneration.graph]
file = ".ggen/deps.json"
hash_algorithm = "sha256"

# Safety options
[regeneration.safety]
verify_interval = 10     # Full verification every N partial runs
warn_on_uncertainty = true
fallback_to_full = true  # When uncertain, do full regeneration
```

---

## Case Study: The 10x Speedup

*A team achieves dramatic speedup through partial regeneration.*

### The Situation

The PlatformAPI team had 2,847 API endpoints specified in RDF. Full regeneration:
- Generated Python handlers
- Generated OpenAPI schemas
- Generated TypeScript clients
- Generated documentation

Total time: 4 minutes 23 seconds per run.

For a one-line description change, this was unacceptable.

### The Analysis

Breaking down the regeneration:

```
Regeneration breakdown:
  Normalization (SHACL validation): 45s
  Extraction (SPARQL queries):      62s
  Emission (template rendering):    98s
  Canonicalization:                 18s
  Receipt generation:               12s
  File I/O:                         28s
  Total:                           263s (4m23s)
```

Most time was spent processing unchanged endpoints.

### The Implementation

**Step 1: Dependency Tracking**

```toml
[regeneration]
mode = "partial"
track_dependencies = true
```

**Step 2: Hash-Based Change Detection**

```python
# .ggen/deps.json
{
  "hashes": {
    "ontology/api-endpoints.ttl": "sha256:abc123...",
    "templates/handler.py.tera": "sha256:def456...",
    "shapes/endpoint-shape.ttl": "sha256:ghi789..."
  },
  "dependencies": {
    "src/handlers/users_get.py": [
      "ontology/api-endpoints.ttl",
      "templates/handler.py.tera",
      "shapes/endpoint-shape.ttl"
    ]
  }
}
```

**Step 3: Partial Regeneration Logic**

```python
def sync():
    changed = detect_changes()

    if requires_full_regeneration(changed):
        return full_sync()

    affected = affected_outputs(changed)
    print(f"Regenerating {len(affected)} of 11,388 outputs")

    for output in affected:
        regenerate_single(output)
```

### The Results

After implementing partial regeneration:

| Scenario | Before | After | Speedup |
|----------|--------|-------|---------|
| One endpoint description change | 4m23s | 0.8s | 328x |
| One template change | 4m23s | 45s | 5.8x |
| One shape change | 4m23s | 4m23s | 1x (full) |
| New endpoint added | 4m23s | 3.2s | 82x |

Average development cycle improvement: **10.2x faster**

---

## Anti-Patterns

### Anti-Pattern: Incomplete Dependency Tracking

*"We track source → output, but not template → output."*

Missing dependencies means affected files aren't regenerated. Inconsistency ensues.

**Resolution:** Track all dependencies: sources, templates, shapes, queries, config.

### Anti-Pattern: Stale Dependency Graph

*"We built the dependency graph once."*

The graph becomes stale as files are added, removed, or renamed.

**Resolution:** Rebuild or update the graph on each run. Or invalidate when config changes.

### Anti-Pattern: Over-Precise Tracking

*"We track which property of which resource affects which line of which output."*

This level of precision has massive overhead and diminishing returns.

**Resolution:** File-level tracking is usually sufficient. Property-level is rarely worth it.

### Anti-Pattern: Never Full Regeneration

*"Partial regeneration is always faster, so we never do full."*

Dependency tracking bugs accumulate. Inconsistencies develop.

**Resolution:** Periodic full regeneration. CI always does full. Partial for development only.

---

## Implementation Checklist

### Dependency Tracking

- [ ] Define dependency graph structure
- [ ] Implement graph building from config
- [ ] Track source → output dependencies
- [ ] Track template → output dependencies
- [ ] Track shape → spec → output dependencies
- [ ] Track query → output dependencies
- [ ] Persist graph between runs

### Change Detection

- [ ] Implement hash-based change detection
- [ ] Implement git-based change detection
- [ ] Handle file additions and deletions
- [ ] Handle file renames

### Partial Regeneration

- [ ] Implement affected output computation
- [ ] Handle transitive dependencies
- [ ] Implement meta-file detection
- [ ] Implement fallback to full regeneration
- [ ] Update graph after regeneration

### Safety

- [ ] Periodic full verification
- [ ] CI uses full regeneration
- [ ] Warn on uncertain dependencies
- [ ] Log regeneration decisions

---

## Exercises

### Exercise 1: Build a Dependency Graph

Create a dependency graph for a simple configuration:

```toml
[[targets]]
source = "specs/commands.ttl"
query = "sparql/cmd.rq"
template = "templates/cmd.py.tera"
output = "src/{{ name }}.py"
```

What are the dependencies for `src/validate.py`?

### Exercise 2: Change Detection

Implement change detection using file hashes:

```python
def detect_changes(previous: dict[Path, str], current_dir: Path) -> set[Path]:
    """Detect files that changed."""
    # Your implementation
```

### Exercise 3: Affected Computation

Given a dependency graph and changed files, compute affected outputs:

```python
def affected_outputs(changed: set[Path], graph: DependencyGraph) -> set[Path]:
    """Compute affected outputs."""
    # Your implementation
```

Handle transitive dependencies correctly.

### Exercise 4: Benchmark

Measure speedup from partial regeneration:

1. Create a specification with 100 entries
2. Measure full regeneration time
3. Implement partial regeneration
4. Change one entry
5. Measure partial regeneration time
6. Report speedup factor

---

## Resulting Context

After implementing this pattern, you have:

- **Fast development cycles:** Regenerate only what changed
- **Maintained consistency:** Dependency tracking ensures completeness
- **Scalable transformation:** Large specifications don't mean slow regeneration
- **Safe fallbacks:** Full regeneration when uncertain
- **Auditable decisions:** Logs show what was regenerated and why

Partial regeneration transforms specification-driven development from a batch process to an incremental one, making it practical for large-scale projects.

---

## Code References

The following spec-kit source files implement partial regeneration concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/spec-kit-schema.ttl:250-300` | Dependency tracking properties (sk:dependsOn, sk:derivedFrom) |
| `src/specify_cli/runtime/receipt.py:30-37` | StageHash tracking which stages need rerun |
| `ggen.toml` | Configuration for selective file regeneration |

---

## Related Patterns

- **Requires:** **[27. Idempotent Transform](./idempotent-transform.md)** — Partial must match full
- **Uses:** **[20. Traceability Thread](../specification/traceability-thread.md)** — Dependency tracking
- **Supports:** **[37. Continuous Validation](../verification/continuous-validation.md)** — Fast CI
- **Optimizes:** **[21. Constitutional Equation](./constitutional-equation.md)** — Faster pipeline

---

## Philosophical Note

> *"Make it work, make it right, make it fast."*
> — Kent Beck

Partial regeneration is the "make it fast" for transformation. But only after full regeneration is working (it works) and idempotent (it's right). Optimization before correctness leads to fast wrong answers.

The order matters:
1. Full regeneration that's correct (it works)
2. Idempotent regeneration that's reliable (it's right)
3. Partial regeneration that's efficient (it's fast)

---

**Next:** Learn how **[29. Multi-Target Emission](./multi-target-emission.md)** generates multiple artifact types from the same specification.
