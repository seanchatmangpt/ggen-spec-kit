# 44. Deprecation Path

★★

*All capabilities eventually become obsolete. Deprecation path provides a graceful way to retire capabilities—warning users, providing alternatives, and removing cleanly. This is how you evolve without abandoning users.*

---

## The Retirement Reality

Nothing lasts forever. Capabilities that once served well become:

- **Superseded** by better approaches
- **Incompatible** with new architectures
- **Burdensome** to maintain
- **Confusing** alongside newer features
- **Security risks** as they age without updates

The question isn't whether to retire old capabilities. The question is how.

### The Abandonment Anti-Pattern

```
Monday:
Feature X is available
Users depend on Feature X
Documentation describes Feature X

Tuesday:
New release removes Feature X
Users' workflows break
Support tickets flood in
Trust erodes
```

Abrupt removal breaks users. They invested in learning your capability. They built workflows around it. They trusted it would be there.

### The Eternal Maintenance Anti-Pattern

```
Year 1: Feature X works great
Year 2: Feature Y is better, but X still maintained
Year 3: Feature Z is even better, but X and Y still maintained
Year 4: Three overlapping features confuse new users
Year 5: Maintenance burden is crushing
Year 10: Still maintaining X, Y, and Z
```

Keeping everything forever creates technical debt. New users face confusing choices. Maintenance spreads thin across too many capabilities.

---

## The Graceful Retirement Problem

**The fundamental problem: Abrupt removal breaks users. Eternal maintenance creates debt. Deprecation path enables graceful retirement that respects users while enabling progress.**

Graceful retirement means:

1. **Warning**: Users know removal is coming
2. **Alternatives**: Users know what to use instead
3. **Time**: Users have time to migrate
4. **Help**: Users have guidance for migration
5. **Clean removal**: Eventually, the old capability is gone

This respects the investment users made while allowing the system to evolve.

---

## The Forces

### Force: Progress Wants Removal

*Old capabilities slow down new development. Simplification enables speed.*

Every maintained feature is a tax on development. Tests to run. Edge cases to consider. Documentation to update. Bugs to fix.

**Resolution:** Remove what's no longer needed. But remove gracefully.

### Force: Compatibility Wants Retention

*Users depend on existing capabilities. Breaking changes hurt.*

Users invested in your capabilities. Breaking their workflows damages trust and creates work for them.

**Resolution:** Give users time and help. Don't force abrupt migration.

### Force: Clarity Wants Decisiveness

*"Deprecated but kept forever" is confusing. Either remove or don't.*

Capabilities in permanent deprecation limbo confuse everyone. Is it going away or not?

**Resolution:** Set firm timelines. Deprecated means "going away on date X."

### Force: Trust Wants Communication

*Users need warning and alternatives. Surprises destroy trust.*

Trust is built by predictability. If users can't predict what you'll do, they can't trust you.

**Resolution:** Communicate clearly. Warn early. Provide alternatives. Honor timelines.

---

## Therefore

**Implement explicit deprecation paths with phases: soft deprecation (warning), hard deprecation (discourage), sunset (final warning), and removal. Provide alternatives and migration guidance throughout.**

### The Deprecation Phases

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  DEPRECATION PATH PHASES                                                       │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 1: SOFT DEPRECATION                                                │  │
│  │ Duration: Typically 2-3 months                                           │  │
│  │                                                                          │  │
│  │ Actions:                                                                 │  │
│  │   ✓ Mark documentation as deprecated                                    │  │
│  │   ✓ Emit runtime warnings (first use only)                              │  │
│  │   ✓ Prominently advertise alternative                                   │  │
│  │   ✓ Track usage metrics                                                 │  │
│  │   ✓ Announce deprecation in changelog                                   │  │
│  │                                                                          │  │
│  │ User experience:                                                         │  │
│  │   - Feature still works normally                                         │  │
│  │   - Warning appears on first use                                         │  │
│  │   - Docs show "Deprecated: Use X instead"                                │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 2: HARD DEPRECATION                                                │  │
│  │ Duration: Typically 2-3 months                                           │  │
│  │                                                                          │  │
│  │ Actions:                                                                 │  │
│  │   ✓ Warnings become more prominent (every use)                          │  │
│  │   ✓ New users prevented (feature flag)                                  │  │
│  │   ✓ Migration support provided                                          │  │
│  │   ✓ Removal date communicated clearly                                   │  │
│  │   ✓ Direct outreach to heavy users                                      │  │
│  │                                                                          │  │
│  │ User experience:                                                         │  │
│  │   - Feature still works but warns every time                            │  │
│  │   - Clear "will be removed on DATE" message                              │  │
│  │   - Migration guide prominent in docs                                    │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 3: SUNSET                                                          │  │
│  │ Duration: Typically 1 month                                              │  │
│  │                                                                          │  │
│  │ Actions:                                                                 │  │
│  │   ✓ Final warning period                                                │  │
│  │   ✓ Direct outreach to remaining users                                  │  │
│  │   ✓ Migration assistance offered                                        │  │
│  │   ✓ Firm removal date confirmed                                         │  │
│  │   ✓ Countdown in warnings                                               │  │
│  │                                                                          │  │
│  │ User experience:                                                         │  │
│  │   - "This will stop working in X days" on every use                     │  │
│  │   - Prominent banner in docs                                             │  │
│  │   - Last chance to migrate                                               │  │
│  │                                                                          │  │
│  └────────────────────────────────┬────────────────────────────────────────┘  │
│                                   │                                            │
│                                   ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PHASE 4: REMOVAL                                                         │  │
│  │                                                                          │  │
│  │ Actions:                                                                 │  │
│  │   ✓ Capability removed from codebase                                   │  │
│  │   ✓ Documentation moved to archive                                      │  │
│  │   ✓ Clear error for legacy calls                                        │  │
│  │   ✓ Redirect to alternative in error                                    │  │
│  │   ✓ Support available for stragglers                                    │  │
│  │                                                                          │  │
│  │ User experience:                                                         │  │
│  │   - "This command has been removed. Use X instead."                      │  │
│  │   - Link to migration guide in error                                     │  │
│  │   - Support available                                                    │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Deprecation Specification in RDF

```turtle
# ontology/cli-commands.ttl
@prefix cli: <http://github.com/spec-kit/cli#> .
@prefix sk: <http://github.com/spec-kit/schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

cli:ValidateLegacyCommand a cli:Command ;
    rdfs:label "validate-legacy" ;
    sk:description "Legacy validation command (DEPRECATED)" ;

    sk:deprecation [
        a sk:Deprecation ;

        # Timeline
        sk:announcementDate "2025-01-01"^^xsd:date ;
        sk:softDeprecationDate "2025-01-15"^^xsd:date ;
        sk:hardDeprecationDate "2025-04-15"^^xsd:date ;
        sk:sunsetDate "2025-06-15"^^xsd:date ;
        sk:removalDate "2025-07-15"^^xsd:date ;

        # Reason
        sk:reason """
            Superseded by streaming validation in 'validate' command.
            The legacy command loads entire files into memory, causing
            performance issues for large files. The new command uses
            streaming and meets P99 latency targets.
        """ ;

        # Alternative
        sk:alternative cli:ValidateCommand ;
        sk:alternativeDescription """
            Use 'specify validate' instead. The new command:
            - Supports streaming for large files
            - Has better error messages
            - Is 10x faster for large files
        """ ;

        # Migration
        sk:migrationGuide <docs/migration/validate-legacy.md> ;
        sk:migrationEffort "low" ;  # low, medium, high

        # Current phase
        sk:currentPhase "soft_deprecation" ;

        # Usage tracking
        sk:usageMetrics [
            sk:period "2025-01" ;
            sk:invocations 1234 ;
            sk:uniqueUsers 45
        ] ;
        sk:usageMetrics [
            sk:period "2025-02" ;
            sk:invocations 567 ;  # Declining!
            sk:uniqueUsers 23
        ]
    ] .
```

### Generated Deprecation Warning

```python
# Generated from deprecation specification
# src/commands/validate_legacy.py

import warnings
from datetime import date
import typer
from pathlib import Path
from rich.console import Console

console = Console()

# Deprecation metadata from spec
DEPRECATED_DATE = date(2025, 1, 15)
REMOVAL_DATE = date(2025, 7, 15)
ALTERNATIVE = "specify validate"
MIGRATION_GUIDE = "docs/migration/validate-legacy.md"


def _emit_deprecation_warning() -> None:
    """Emit deprecation warning based on current phase."""
    today = date.today()
    days_until_removal = (REMOVAL_DATE - today).days

    if days_until_removal <= 0:
        # Should have been removed
        console.print(
            "[red bold]ERROR: validate-legacy has been removed.[/red bold]\n"
            f"Use '{ALTERNATIVE}' instead.\n"
            f"Migration guide: {MIGRATION_GUIDE}"
        )
        raise typer.Exit(1)

    elif days_until_removal <= 30:
        # Sunset phase - warn every time with countdown
        console.print(
            f"[red bold]FINAL WARNING: validate-legacy will be removed "
            f"in {days_until_removal} days.[/red bold]\n"
            f"Migrate to '{ALTERNATIVE}' now.\n"
            f"Migration guide: {MIGRATION_GUIDE}\n"
        )

    elif days_until_removal <= 90:
        # Hard deprecation - warn every time
        console.print(
            f"[yellow bold]DEPRECATED: validate-legacy will be removed "
            f"on {REMOVAL_DATE}.[/yellow bold]\n"
            f"Use '{ALTERNATIVE}' instead.\n"
        )

    else:
        # Soft deprecation - warn once per session
        warnings.warn(
            f"validate-legacy is deprecated and will be removed on {REMOVAL_DATE}. "
            f"Use '{ALTERNATIVE}' instead. "
            f"See {MIGRATION_GUIDE} for migration guide.",
            DeprecationWarning,
            stacklevel=3
        )


@app.command("validate-legacy")
def validate_legacy_command(
    file: Path = typer.Argument(..., help="File to validate"),
    strict: bool = typer.Option(False, "--strict", help="Strict mode"),
) -> None:
    """[DEPRECATED] Legacy validation command.

    ⚠️  This command is deprecated and will be removed on 2025-07-15.

    Use 'specify validate' instead:
        specify validate file.ttl

    Migration guide: docs/migration/validate-legacy.md
    """
    _emit_deprecation_warning()

    # Track usage for deprecation metrics
    _track_deprecated_usage("validate-legacy")

    # Original implementation
    # ...
```

### Migration Guide Template

```markdown
# Migration Guide: validate-legacy → validate

## Overview

The `validate-legacy` command is deprecated and will be removed on **July 15, 2025**.
This guide helps you migrate to the new `validate` command.

## Why the change?

The new `validate` command provides:
- **10x faster validation** for large files using streaming
- **Better error messages** with line numbers and suggestions
- **Lower memory usage** for files over 1MB
- **New features** like format selection and parallel validation

## Quick Migration

For most users, migration is a simple command rename:

| Old Command | New Command |
|-------------|-------------|
| `validate-legacy file.ttl` | `validate file.ttl` |
| `validate-legacy --strict file.ttl` | `validate --strict file.ttl` |

## Detailed Changes

### Removed Options

| Old Option | Status | Alternative |
|------------|--------|-------------|
| `--old-format` | Removed | Use `--format legacy` if needed |
| `--no-streaming` | Removed | Streaming is adaptive now |

### Changed Behavior

1. **Error output format**
   - Old: Single line errors
   - New: Multi-line with context

   Old:
   ```
   Error: Invalid predicate at line 15
   ```

   New:
   ```
   Error at line 15, column 12:
     Invalid predicate 'has_name'
     Did you mean: 'hasName'?

     14 | ex:Person
     15 |     has_name "Alice" ;
        |     ^^^^^^^^
   ```

2. **Exit codes**
   - Old: 0 = success, 1 = any error
   - New: 0 = success, 1 = validation error, 2 = file error

### New Features (Optional)

The new command also supports:
- `--format json` for machine-readable output
- `--stream` for explicit streaming (auto-detected by default)
- `--parallel` for multi-file validation

## CI/CD Updates

If you use `validate-legacy` in CI/CD, update your scripts:

```yaml
# Old
- run: specify validate-legacy schema.ttl

# New
- run: specify validate schema.ttl
```

## Scripting Updates

If you parse the output programmatically:

```python
# Old
result = subprocess.run(["specify", "validate-legacy", file])
if result.returncode != 0:
    # Handle error

# New (recommended: use JSON output)
result = subprocess.run(
    ["specify", "validate", "--format", "json", file],
    capture_output=True
)
data = json.loads(result.stdout)
if not data["valid"]:
    for error in data["errors"]:
        print(f"Error at {error['line']}: {error['message']}")
```

## Getting Help

- **Documentation**: [/docs/commands/validate.md](/docs/commands/validate.md)
- **Issues**: [GitHub Issues](https://github.com/spec-kit/specify/issues)
- **Support**: support@spec-kit.dev

## Timeline

| Date | Event |
|------|-------|
| Jan 15, 2025 | Soft deprecation begins (warnings on first use) |
| Apr 15, 2025 | Hard deprecation (warnings on every use) |
| Jun 15, 2025 | Sunset period (final countdown warnings) |
| **Jul 15, 2025** | **Command removed** |

## Need More Time?

If you need more time to migrate, contact us at support@spec-kit.dev before
June 15, 2025. We can discuss options for your situation.
```

### Deprecation Tracking

```python
# src/specify_cli/ops/deprecation.py
"""Deprecation tracking and management."""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from enum import Enum


class DeprecationPhase(Enum):
    """Current phase of deprecation."""
    ANNOUNCED = "announced"
    SOFT = "soft_deprecation"
    HARD = "hard_deprecation"
    SUNSET = "sunset"
    REMOVED = "removed"


@dataclass
class DeprecationInfo:
    """Information about a deprecated capability."""
    capability: str
    reason: str
    alternative: str
    migration_guide: str
    announcement_date: date
    soft_date: date
    hard_date: date
    sunset_date: date
    removal_date: date


@dataclass
class UsageMetrics:
    """Usage metrics for deprecated capability."""
    period: str
    invocations: int
    unique_users: int


def get_current_phase(info: DeprecationInfo) -> DeprecationPhase:
    """Determine current deprecation phase."""
    today = date.today()

    if today >= info.removal_date:
        return DeprecationPhase.REMOVED
    elif today >= info.sunset_date:
        return DeprecationPhase.SUNSET
    elif today >= info.hard_date:
        return DeprecationPhase.HARD
    elif today >= info.soft_date:
        return DeprecationPhase.SOFT
    else:
        return DeprecationPhase.ANNOUNCED


def get_deprecation_report(deprecations: List[DeprecationInfo]) -> str:
    """Generate deprecation status report."""
    lines = [
        "Deprecation Status Report",
        "═" * 70,
        "",
    ]

    by_phase = {}
    for dep in deprecations:
        phase = get_current_phase(dep)
        by_phase.setdefault(phase, []).append(dep)

    for phase in DeprecationPhase:
        deps = by_phase.get(phase, [])
        if deps:
            lines.append(f"{phase.value.upper()} ({len(deps)})")
            lines.append("-" * 70)
            for dep in deps:
                days_to_removal = (dep.removal_date - date.today()).days
                lines.append(f"  {dep.capability}")
                lines.append(f"    Alternative: {dep.alternative}")
                lines.append(f"    Removal in: {days_to_removal} days")
                lines.append("")

    return "\n".join(lines)


def track_deprecated_usage(capability: str) -> None:
    """Track usage of deprecated capability for metrics."""
    # In production, this would record to telemetry/analytics
    from opentelemetry import metrics

    meter = metrics.get_meter(__name__)
    counter = meter.create_counter(
        "deprecated.usage",
        description="Usage of deprecated capabilities"
    )
    counter.add(1, {"capability": capability})
```

---

## The Communication Plan

Deprecation requires proactive communication:

### Announcement (Day 0)

```markdown
# Deprecation Notice: validate-legacy

We're deprecating the `validate-legacy` command in favor of the new
`validate` command.

**Timeline:**
- Soft deprecation: January 15, 2025
- Hard deprecation: April 15, 2025
- Removal: July 15, 2025

**What to do:**
Replace `validate-legacy` with `validate` in your workflows.
See [migration guide](/docs/migration/validate-legacy.md) for details.

**Why:**
The new command is 10x faster for large files and has better error messages.

**Questions?**
File an issue or contact support@spec-kit.dev.
```

### Changelog Entry

```markdown
## [2.5.0] - 2025-01-15

### Deprecated
- `validate-legacy` command - Use `validate` instead
  - Will be removed in version 3.0 (July 2025)
  - Migration guide: docs/migration/validate-legacy.md
  - Reason: Superseded by streaming validation with better performance
```

### Direct Outreach (Heavy Users)

```
Subject: Action Required: validate-legacy deprecation

Hi [User],

We noticed you're a heavy user of the validate-legacy command
(~500 invocations/month).

We're deprecating this command on July 15, 2025. The replacement
(validate) is faster and has better error messages.

We'd like to help you migrate:
- Migration guide: [link]
- Office hours: [calendar link]
- Direct support: reply to this email

Let us know if you have any concerns.

Best,
The Spec-Kit Team
```

---

## Case Study: The Graceful Goodbye

*A team retires a legacy command without breaking trust.*

### The Setup

The `convert-legacy` command had been around for 3 years. It worked, but:
- Used 10x more memory than necessary
- Had confusing error messages
- Didn't support the new format

A new `convert` command was ready.

### The Deprecation

**Month 0: Announcement**
- Blog post explaining change
- Changelog entry
- Migration guide written

**Month 1-3: Soft Deprecation**
- Warning on first use
- Usage tracking enabled
- 1,200 users in month 1

**Month 4-6: Hard Deprecation**
- Warning on every use
- Usage dropped to 400 users
- Direct outreach to top 50 users

**Month 7: Sunset**
- Countdown warnings
- Usage dropped to 80 users
- Personal assistance offered

**Month 8: Removal**
- Command removed
- Clear error with redirect
- 3 support tickets (all resolved quickly)

### The Results

| Metric | Value |
|--------|-------|
| Users at deprecation start | 1,200 |
| Users migrated before removal | 1,197 (99.75%) |
| Support tickets | 3 |
| Negative feedback | 0 |
| Trust maintained | ✓ |

Users appreciated the clear communication. Many said the new command was better. Nobody felt abandoned.

---

## Anti-Patterns

### Anti-Pattern: Surprise Removal

*"We removed it. Didn't you read the release notes?"*

Release notes aren't enough. Active deprecation warnings are required.

**Resolution:** Emit runtime warnings. Make deprecation impossible to miss.

### Anti-Pattern: Eternal Deprecation

*"It's been deprecated for 5 years but we haven't removed it."*

If you're never going to remove it, it's not deprecated.

**Resolution:** Set firm removal dates. Honor them.

### Anti-Pattern: No Alternative

*"We deprecated X but Y isn't ready yet."*

Deprecating without an alternative leaves users stranded.

**Resolution:** Only deprecate when the alternative is ready.

### Anti-Pattern: No Migration Path

*"Just rewrite your code."*

If migration is too hard, users won't do it.

**Resolution:** Provide clear migration guides. Minimize breaking changes.

---

## Implementation Checklist

### Preparation

- [ ] Verify alternative is ready and tested
- [ ] Write migration guide
- [ ] Plan timeline (typically 6 months minimum)
- [ ] Identify heavy users for outreach

### Announcement

- [ ] Create deprecation specification
- [ ] Update documentation with deprecation notice
- [ ] Add changelog entry
- [ ] Publish announcement (blog, email, etc.)

### Soft Deprecation

- [ ] Add runtime warning (first use)
- [ ] Track usage metrics
- [ ] Monitor migration progress
- [ ] Provide support for migrations

### Hard Deprecation

- [ ] Increase warning frequency (every use)
- [ ] Direct outreach to remaining users
- [ ] Confirm removal date

### Sunset

- [ ] Add countdown to warnings
- [ ] Final outreach to stragglers
- [ ] Prepare removal changeset

### Removal

- [ ] Remove capability from code
- [ ] Move docs to archive
- [ ] Add clear error with redirect
- [ ] Monitor for issues

---

## Exercises

### Exercise 1: Design a Deprecation

For a capability you want to retire, design the deprecation:

```turtle
sk:YourCapability sk:deprecation [
    sk:softDeprecationDate "???"^^xsd:date ;
    sk:hardDeprecationDate "???"^^xsd:date ;
    sk:sunsetDate "???"^^xsd:date ;
    sk:removalDate "???"^^xsd:date ;
    sk:reason "???" ;
    sk:alternative ??? ;
    sk:migrationGuide <???> ;
] .
```

### Exercise 2: Write a Migration Guide

Create a migration guide for the deprecated capability:
- What commands/options change?
- What behavior changes?
- What new features are available?
- Step-by-step migration instructions

### Exercise 3: Draft Communication

Write the deprecation announcement email/post:
- What is being deprecated?
- Why?
- What to use instead?
- Timeline?
- How to get help?

---

## Resulting Context

After implementing this pattern, you have:

- **Graceful retirement of obsolete capabilities** — no surprise breakage
- **Clear communication to users** — everyone knows what's happening
- **Structured migration support** — users have help
- **Clean removal without breaking changes** — trust maintained
- **Reduced maintenance burden** — old code eventually goes away

Deprecation path respects users while enabling progress. You can evolve without abandoning.

---

## Related Patterns

- **Follows:** **[42. Specification Refinement](./specification-refinement.md)** — New replaces old
- **Updates:** **[45. Living Documentation](./living-documentation.md)** — Docs reflect deprecation
- **Respects:** **[7. Anxieties and Habits](../context/anxieties-and-habits.md)** — Eases transition
- **Informs:** **[8. Competing Solutions](../context/competing-solutions.md)** — Position new vs old

---

## Philosophical Note

> *"Knowing when to stop is just as important as knowing when to start."*

Building is celebrated. Retiring is ignored. But retirement is equally important. Systems that only grow eventually collapse under their own weight.

Deprecation path provides the wisdom to stop—gracefully. It acknowledges that users invested in your capabilities. It respects that investment while still enabling progress.

The goal isn't to keep everything forever. The goal is to retire responsibly. Warn early. Provide alternatives. Help with migration. Then remove cleanly.

This is how you evolve without abandoning. This is how you grow while staying lean.

---

**Next:** Learn how **[45. Living Documentation](./living-documentation.md)** keeps documentation accurate through generation—including automatically reflecting deprecation status.
