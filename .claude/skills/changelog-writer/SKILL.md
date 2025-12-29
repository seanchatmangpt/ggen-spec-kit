---
name: changelog-writer
description: Write semantic changelog entries following Keep a Changelog format. Use when documenting releases, version changes, or maintaining changelog.ttl.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Changelog Writer

Write semantic changelog entries in RDF format for Keep a Changelog output.

## Trigger Conditions

- Documenting new releases
- Recording breaking changes
- Tracking feature/fix/deprecation entries
- Maintaining CHANGELOG.md

## Key Capabilities

- Semantic versioning enforcement
- RDF changelog specification
- ggen transformation to Markdown
- Change categorization (Added/Changed/Fixed/Removed/etc)

## Integration

**ggen v5.0.2**: Transforms memory/changelog.ttl → CHANGELOG.md via ggen sync
**Architecture**: Pure Ops layer (RDF → structured data)

## Instructions

1. Capture notable changes
2. Follow semantic versioning
3. Write changes as RDF
4. Generate Markdown with ggen
5. Organize by change type

## Change Types

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security vulnerabilities

## RDF Format

### Release
```turtle
sk:Release_0_1_0 a sk:Release ;
    sk:versionNumber "0.1.0" ;
    sk:releaseDate "2025-12-20"^^xsd:date ;
    sk:breakingChanges false ;
    sk:hasChange sk:Change_0_1_0_1 ;
    .
```

### Change
```turtle
sk:Change_0_1_0_1 a sk:Change ;
    sk:changeType "Added" ;
    sk:changeDescription "Three-tier architecture" ;
    sk:changeScope "architecture" ;
    .
```

## Semantic Versioning

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

## Good Descriptions

```turtle
# ✅ Specific
sk:changeDescription "Add `--dry-run` flag to `specify init` command" ;

# ❌ Vague
sk:changeDescription "Fixed bugs" ;
```

### Patterns

- **Added**: "Add [feature] to [component]"
- **Changed**: "Change [behavior] from [old] to [new]"
- **Fixed**: "Fix [issue] when [condition]"
- **Removed**: "Remove [feature], use [alternative]"

## Workflow

```bash
# See changes since last release
git log --oneline $(git describe --tags --abbrev=0)..HEAD

# Add RDF entries to memory/changelog.ttl

# Validate
uv run python -c "from rdflib import Graph; Graph().parse('memory/changelog.ttl')"

# Generate
ggen sync --config docs/ggen.toml --spec changelog
```

## Output Format

```markdown
## Changelog Update

### Release: 0.2.0
- Date: 2025-12-20
- Breaking: No

### Changes
| Type | Description |
|------|-------------|
| Added | Three-tier architecture |
| Fixed | Import error |

### Generated Output
## [0.2.0] - 2025-12-20

### Added
- Three-tier architecture

### Fixed
- Import error
```
