# 28. Partial Regeneration

★

*Not every change requires regenerating everything. Partial regeneration transforms only what's affected, saving time while maintaining consistency.*

---

Full regeneration is safe but slow. When your specification grows to hundreds of commands, regenerating everything for a single change wastes time.

Partial regeneration solves this by tracking dependencies and regenerating only affected artifacts:
- Change one command's description? Regenerate only that command's files.
- Change a shared template? Regenerate all files using that template.
- Change a SHACL shape? Regenerate files validated by that shape.

This optimization requires careful dependency tracking. Get it wrong, and you have inconsistent artifacts.

**The problem: Full regeneration is slow for large specifications. Partial regeneration is fast but risks inconsistency if dependencies aren't tracked.**

---

**The forces at play:**

- *Speed wants minimal work.* Only regenerate what changed.

- *Safety wants completeness.* Missing a dependency causes inconsistency.

- *Simplicity wants full regeneration.* No dependency tracking needed.

- *Scale wants optimization.* Large projects need partial regeneration.

The tension: fast enough for interactive use, safe enough to trust.

---

**Therefore:**

Implement partial regeneration with explicit dependency tracking, falling back to full regeneration when uncertain.

**Dependency graph:**

```
┌─────────────────────────────────────────────────────────────┐
│  Dependency Graph                                           │
│                                                             │
│  ontology/cli-commands.ttl                                  │
│    ├──▶ src/commands/validate.py                            │
│    ├──▶ src/commands/check.py                               │
│    └──▶ docs/commands/index.md                              │
│                                                             │
│  templates/command.py.tera                                  │
│    ├──▶ src/commands/validate.py                            │
│    └──▶ src/commands/check.py                               │
│                                                             │
│  shapes/command-shape.ttl                                   │
│    ├──▶ src/commands/validate.py  (validation dependency)   │
│    └──▶ src/commands/check.py     (validation dependency)   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Change detection:**

```python
def detect_changes(since: str = "HEAD~1") -> set[Path]:
    """Detect changed source files."""
    result = subprocess.run(
        ["git", "diff", "--name-only", since],
        capture_output=True, text=True
    )
    return {Path(f) for f in result.stdout.strip().split('\n') if f}

def affected_outputs(changed: set[Path], deps: DependencyGraph) -> set[Path]:
    """Determine outputs affected by changed inputs."""
    affected = set()
    for source in changed:
        affected.update(deps.outputs_for(source))
    return affected
```

**Partial regeneration logic:**

```python
def regenerate(full: bool = False):
    """Regenerate artifacts."""
    if full:
        # Regenerate everything
        outputs = all_configured_outputs()
    else:
        # Detect changes and affected outputs
        changed = detect_changes()
        outputs = affected_outputs(changed, load_dependency_graph())

        # If dependency graph might be stale, do full regeneration
        if any(is_meta_file(f) for f in changed):
            print("Meta file changed, doing full regeneration")
            outputs = all_configured_outputs()

    for output in outputs:
        regenerate_single(output)
```

**Meta files triggering full regeneration:**

- `ggen.toml` — Configuration changed
- `shapes/*.ttl` — Validation rules changed
- `templates/*.tera` — Templates changed (unless tracked individually)

**Safety fallback:**

```bash
# When uncertain, full regeneration
ggen sync --full

# When confident, partial regeneration
ggen sync  # Detects changes automatically

# Force regeneration of specific outputs
ggen sync --target src/commands/validate.py
```

---

**Resulting context:**

After applying this pattern, you have:

- Fast regeneration for common cases
- Automatic change detection
- Dependency-aware rebuilding
- Safe fallback to full regeneration

This optimizes **[Idempotent Transform](./idempotent-transform.md)** for scale while maintaining **[Constitutional Equation](./constitutional-equation.md)** guarantees.

---

**Related patterns:**

- *Optimizes:* **[21. Constitutional Equation](./constitutional-equation.md)** — Faster pipeline
- *Requires:* **[27. Idempotent Transform](./idempotent-transform.md)** — Partial must match full
- *Uses:* **[20. Traceability Thread](../specification/traceability-thread.md)** — Dependency tracking
- *Supports:* **[37. Continuous Validation](../verification/continuous-validation.md)** — Fast CI

---

> *"Make it work, make it right, make it fast."*
>
> — Kent Beck

Partial regeneration is the "make it fast" for transformation. But only after full regeneration is working and right.
