# 42. Specification Refinement

★★

*Specifications aren't static. As understanding deepens and feedback arrives, specifications must evolve. Specification refinement is the disciplined practice of improving specifications while maintaining consistency.*

---

**[Gap Analysis](./gap-analysis.md)** revealed opportunities. **[Feedback Loop](./feedback-loop.md)** brought insights. Now what?

In specification-driven development, improvement means specification refinement. You don't patch the code—you improve the specification, then regenerate.

This discipline maintains the **[Constitutional Equation](../transformation/constitutional-equation.md)**:

```
spec.md = μ(feature.ttl)
```

Improvements flow through the specification, not around it.

**The problem: Ad-hoc changes bypass specification, creating drift. Specification refinement channels all changes through the source of truth.**

---

**The forces at play:**

- *Speed wants quick fixes.* Patching code is faster than updating specs.

- *Consistency wants discipline.* Constitutional equation must hold.

- *Evolution wants flexibility.* Specifications must accommodate change.

- *Stability wants caution.* Changes can break existing behavior.

The tension: evolve specifications while maintaining consistency and stability.

---

**Therefore:**

Refine specifications through a disciplined process that maintains the constitutional equation and ensures changes are verified.

**Refinement workflow:**

```
┌─────────────────────────────────────────────────────────────┐
│  SPECIFICATION REFINEMENT WORKFLOW                          │
│                                                             │
│  1. IDENTIFY                                                │
│     • Gap analysis identifies need                          │
│     • Feedback reveals insight                              │
│     • Document the refinement goal                          │
│                                                             │
│  2. PROPOSE                                                 │
│     • Draft specification changes in RDF                    │
│     • Document rationale for changes                        │
│     • Identify affected artifacts                           │
│                                                             │
│  3. VALIDATE                                                │
│     • Run SHACL validation on changed specs                 │
│     • Verify internal consistency                           │
│     • Check for unintended implications                     │
│                                                             │
│  4. PREVIEW                                                 │
│     • Generate artifacts in preview mode                    │
│     • Review diff of generated changes                      │
│     • Assess impact on existing tests                       │
│                                                             │
│  5. TEST                                                    │
│     • Run existing tests (expect some failures)             │
│     • Update tests for new behavior                         │
│     • Add tests for new acceptance criteria                 │
│                                                             │
│  6. COMMIT                                                  │
│     • Commit specification + artifacts together             │
│     • Include refinement rationale in commit message        │
│     • Link to gap analysis / feedback source                │
│                                                             │
│  7. MEASURE                                                 │
│     • Deploy and observe                                    │
│     • Measure outcome metrics                               │
│     • Confirm gap is addressed                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Refinement in RDF:**

```turtle
# Track refinement history
cli:ValidateCommand sk:refinementHistory [
    a sk:Refinement ;
    sk:date "2025-02-15"^^xsd:date ;
    sk:author "Alice" ;
    sk:rationale """
        Gap analysis showed large file validation exceeds target.
        Added streaming validation option to address P99 latency.
    """ ;
    sk:addressesGap jtbd:MinimizeValidationTime ;
    sk:changeDescription """
        Added --stream option for streaming validation of large files.
        Files > 1MB automatically use streaming unless disabled.
    """ ;
    sk:affectedCriteria sk:AC_VAL_LARGE_FILE
] .
```

**Refinement types:**

| Type | Description | Example |
|------|-------------|---------|
| Additive | Add new capability | New --stream flag |
| Corrective | Fix incorrect behavior | Better error messages |
| Performance | Improve efficiency | Streaming validation |
| Deprecation | Phase out old behavior | Remove legacy flag |
| Clarification | Improve specification clarity | Better description |

**Change preview:**

```bash
# Preview changes without applying
ggen sync --dry-run --diff

# Shows:
# --- src/commands/validate.py (current)
# +++ src/commands/validate.py (would generate)
# @@ -15,6 +15,10 @@
#      file: Path = typer.Argument(...),
# +    stream: bool = typer.Option(
# +        False, "--stream",
# +        help="Use streaming validation for large files"
# +    ),
#  ) -> None:
```

**Commit message format:**

```
feat(validate): add streaming validation for large files

Addresses gap: MinimizeValidationTime P99 latency exceeds target

Changes:
- Add --stream option for streaming validation
- Auto-enable streaming for files > 1MB
- Add AC-VAL-STREAM acceptance criterion

Refinement tracked in: ontology/cli-commands.ttl#refinement-2025-02-15

🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude <noreply@anthropic.com>
```

---

**Resulting context:**

After applying this pattern, you have:

- Disciplined approach to specification evolution
- Maintained constitutional equation
- Traceable refinement history
- Verified changes before deployment

This implements the improvement loop and supports **[45. Living Documentation](./living-documentation.md)**.

---

**Related patterns:**

- *Driven by:* **[41. Gap Analysis](./gap-analysis.md)** — Identifies needs
- *Maintains:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Equation preserved
- *Enables:* **[43. Branching Exploration](./branching-exploration.md)** — Try alternatives
- *Supports:* **[45. Living Documentation](./living-documentation.md)** — Docs update

---

> *"Change is the only constant."*

Specification refinement makes change disciplined, traceable, and consistent.
