# Add Changelog Entry

Add a semantic changelog entry following Keep a Changelog format via RDF-first approach.

## Description
Creates changelog entries by editing RDF source (`memory/changelog.ttl`) and regenerating CHANGELOG.md via constitutional equation transformation.

## Usage
```bash
/changelog TYPE DESCRIPTION
```

## Arguments
- `TYPE` (required) - Change category: added, changed, deprecated, removed, fixed, security
- `DESCRIPTION` (required) - Clear description of the change

## Examples
```bash
# New feature
/changelog added "RDF-first changelog management with ggen sync"

# Bug fix
/changelog fixed "Subprocess timeout handling in runtime layer"

# Security improvement
/changelog security "Path validation before file operations"

# Breaking change
/changelog changed "Three-tier architecture now strictly enforced"

# Deprecation notice
/changelog deprecated "Legacy init command (use specify init instead)"

# Removal
/changelog removed "Shell=True support in subprocess calls"
```

## What This Command Does

Follows the constitutional equation: `CHANGELOG.md = μ(changelog.ttl)`

1. **Edit RDF Source** (`memory/changelog.ttl`):
   ```turtle
   :entry-2025-12-29-1
       a :ChangelogEntry ;
       :changeType "added" ;
       :description "RDF-first changelog management" ;
       :date "2025-12-29" ;
       :version "Unreleased" .
   ```

2. **Run Transformation**:
   ```bash
   ggen sync  # Uses v5.0.2
   ```

3. **Verify Output** (`CHANGELOG.md`):
   ```markdown
   ## [Unreleased]

   ### Added
   - RDF-first changelog management
   ```

## Change Categories

Following [Keep a Changelog](https://keepachangelog.com/):

| Type | Description | Example |
|------|-------------|---------|
| `added` | New features | "CLI command for RDF validation" |
| `changed` | Changes to existing functionality | "Updated ggen integration to v5.0.2" |
| `deprecated` | Features to be removed | "Legacy subprocess module" |
| `removed` | Removed features | "Shell=True subprocess support" |
| `fixed` | Bug fixes | "Path handling on Windows" |
| `security` | Security fixes | "Input validation for user paths" |

## Output Format

After execution:
1. Shows edited RDF entry in `memory/changelog.ttl`
2. Reports `ggen sync` transformation results
3. Displays generated CHANGELOG.md section
4. Confirms receipt.json hash verification

## Integration

Works with:
- `memory/changelog.ttl` - Source of truth for changelog
- `sparql/changelog-extract.rq` - SPARQL query for extraction
- `templates/changelog.tera` - Tera template for Markdown generation
- `ggen sync` - Transformation pipeline (v5.0.2)

## CRITICAL: RDF-First Rule

**Never edit CHANGELOG.md directly!**

The file is generated from RDF:
- Edit: `memory/changelog.ttl` (source)
- Transform: `ggen sync` (build)
- Result: `CHANGELOG.md` (artifact)

Violating this breaks the constitutional equation and causes divergence between source and generated files.

## Notes
- Each entry needs a unique ID (use date + sequence number)
- Date should be ISO 8601 format (YYYY-MM-DD)
- Version defaults to "Unreleased" for ongoing work
- Entries automatically sorted by date in generated output
