---
paths:
  - "src/specify_cli/commands/**/*.py"
  - "docs/*.md"
  - "CHANGELOG.md"
---

# Generated Files Protection

## Warning
These files are GENERATED from RDF specifications.

**DO NOT EDIT MANUALLY**

## Source of Truth

| Generated File | Source |
|----------------|--------|
| `src/specify_cli/commands/*.py` | `ontology/cli-commands.ttl` |
| `docs/*.md` | `memory/*.ttl` |
| `CHANGELOG.md` | `memory/changelog.ttl` |

## Correct Workflow

### To Change a Command
1. Edit `ontology/cli-commands.ttl`
2. Run `ggen sync`
3. Implement business logic in `ops/` or `runtime/`

### To Change Documentation
1. Edit the appropriate `memory/*.ttl` file
2. Run `ggen sync`
3. Verify the generated output

### To Add Changelog Entry
1. Edit `memory/changelog.ttl`
2. Run `ggen sync`
3. Verify CHANGELOG.md

## Verification

After any RDF change:
```bash
ggen sync
git diff  # Review what was generated
uv run pytest tests/
```

## Why This Matters

The constitutional equation:
```
spec.md = μ(feature.ttl)
```

Manual edits to generated files:
- Will be overwritten on next `ggen sync`
- Cause RDF and code to diverge
- Break the single source of truth principle
- Make specifications unreliable
