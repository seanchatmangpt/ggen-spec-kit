# 44. Deprecation Path

★★

*All capabilities eventually become obsolete. Deprecation path provides a graceful way to retire capabilities—warning users, providing alternatives, and removing cleanly.*

---

Nothing lasts forever. Capabilities that once served well become:
- Superseded by better approaches
- Incompatible with new architectures
- Burdensome to maintain
- Confusing alongside newer features

Removing capabilities abruptly breaks users. But keeping them forever creates technical debt.

Deprecation path provides the middle ground: a structured approach to retiring capabilities that respects users while enabling progress.

**The problem: Abrupt removal breaks users. Eternal maintenance creates debt. Deprecation path enables graceful retirement.**

---

**The forces at play:**

- *Progress wants removal.* Old capabilities slow down new development.

- *Compatibility wants retention.* Users depend on existing capabilities.

- *Clarity wants decisiveness.* "Deprecated but kept forever" is confusing.

- *Trust wants communication.* Users need warning and alternatives.

The tension: retire capabilities responsibly without carrying debt forever.

---

**Therefore:**

Implement explicit deprecation paths with warnings, alternatives, timelines, and clean removal.

**Deprecation specification:**

```turtle
cli:OldValidateCommand a cli:Command ;
    rdfs:label "validate-legacy" ;
    sk:deprecation [
        a sk:Deprecation ;
        sk:deprecatedDate "2025-01-15"^^xsd:date ;
        sk:removalDate "2025-07-15"^^xsd:date ;
        sk:reason "Superseded by streaming validation" ;
        sk:alternative cli:ValidateCommand ;
        sk:migrationGuide <docs/migration/validate-legacy.md>
    ] .
```

**Deprecation phases:**

```
Phase 1: SOFT DEPRECATION (warnings begin)
───────────────────────────────────────────
• Documentation marked as deprecated
• Runtime warnings emitted
• Alternative prominently advertised
• Usage metrics tracked

Phase 2: HARD DEPRECATION (usage discouraged)
───────────────────────────────────────────
• Warnings become more prominent
• New users prevented (feature flag)
• Migration support provided
• Removal date communicated

Phase 3: SUNSET (final warning)
───────────────────────────────────────────
• Final warning period
• Direct outreach to remaining users
• Migration assistance offered
• Firm removal date

Phase 4: REMOVAL
───────────────────────────────────────────
• Capability removed from codebase
• Documentation moved to archive
• Error message for legacy calls
• Redirect to alternative
```

**Generated deprecation warning:**

```python
# Generated from deprecation specification
import warnings

@app.command("validate-legacy")
def validate_legacy_command(file: Path) -> None:
    """[DEPRECATED] Legacy validation command.

    ⚠️  This command is deprecated and will be removed on 2025-07-15.

    Use 'specify validate' instead:
        specify validate file.ttl

    Migration guide: docs/migration/validate-legacy.md
    """
    warnings.warn(
        "validate-legacy is deprecated and will be removed on 2025-07-15. "
        "Use 'specify validate' instead. "
        "See docs/migration/validate-legacy.md for migration guide.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... implementation ...
```

**Usage tracking for deprecation:**

```turtle
cli:OldValidateCommand sk:usageMetrics [
    sk:period "2025-01" ;
    sk:invocations 1234 ;
    sk:uniqueUsers 45
] ;
sk:usageMetrics [
    sk:period "2025-02" ;
    sk:invocations 567 ;  # Declining!
    sk:uniqueUsers 23
] .
```

**Migration support:**

```markdown
# Migration Guide: validate-legacy to validate

## Why the change?

The new `validate` command uses streaming validation, providing:
- 10x faster validation for large files
- Lower memory usage
- Better error messages

## Migration steps

1. Replace `validate-legacy file.ttl` with `validate file.ttl`
2. Remove any `--old-format` flags (no longer needed)
3. Update CI scripts

## Comparison

| Old | New |
|-----|-----|
| `validate-legacy file.ttl` | `validate file.ttl` |
| `validate-legacy --strict file.ttl` | `validate --strict file.ttl` |

## Need help?

Contact support or file an issue.
```

---

**Resulting context:**

After applying this pattern, you have:

- Graceful retirement of obsolete capabilities
- Clear communication to users
- Structured migration support
- Clean removal without breaking changes

This completes the Evolution Patterns and supports sustainable capability development.

---

**Related patterns:**

- *Follows:* **[42. Specification Refinement](./specification-refinement.md)** — New replaces old
- *Updates:* **[45. Living Documentation](./living-documentation.md)** — Docs reflect deprecation
- *Respects:* **[7. Anxieties and Habits](../context/anxieties-and-habits.md)** — Ease transition
- *Informs:* **[8. Competing Solutions](../context/competing-solutions.md)** — Position new vs old

---

> *"Knowing when to stop is just as important as knowing when to start."*

Deprecation path provides the wisdom to stop—gracefully.
