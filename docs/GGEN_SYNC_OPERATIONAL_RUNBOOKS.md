# ggen sync: Operational Runbooks

**Version**: 5.0.0 (Phase 1 Implementation)
**Date**: 2025-12-21
**Status**: Production-Ready Procedures

---

## Table of Contents

1. [Pre-Flight Checks Script](#pre-flight-checks-script)
2. [Production Sync Procedure](#production-sync-procedure)
3. [Failure Recovery Scenarios](#failure-recovery-scenarios)
4. [Quick Reference](#quick-reference)

---

## Pre-Flight Checks Script

Run this before each ggen sync operation to verify readiness:

```bash
#!/bin/bash
# pre-flight-checks.sh - Verify ggen sync readiness

set -e

echo "=== ggen sync Pre-Flight Checks ==="
echo ""

# Check 1: ggen installed
echo "1. Checking ggen installation..."
if ! command -v ggen &> /dev/null; then
    echo "   ✗ ggen not found - Install with: brew install seanchatmangpt/ggen/ggen"
    exit 1
fi
echo "   ✓ ggen $(ggen --version)"

# Check 2: ggen.toml exists
echo "2. Checking ggen.toml..."
if [ ! -f "ggen.toml" ]; then
    echo "   ✗ ggen.toml not found"
    exit 1
fi
echo "   ✓ ggen.toml found"

# Check 3: Disk space
echo "3. Checking disk space..."
AVAIL=$(df . | awk 'NR==2 {print $4}')
if [ "$AVAIL" -lt 10240 ]; then  # 10MB
    echo "   ⚠ Low disk space: $(( $AVAIL / 1024 ))MB available"
else
    echo "   ✓ Disk space OK: $(( $AVAIL / 1024 ))MB available"
fi

# Check 4: Output directory writable
echo "4. Checking output directory permissions..."
if [ -d "docs" ] && [ ! -w "docs" ]; then
    echo "   ✗ docs directory not writable"
    exit 1
fi
echo "   ✓ Output directory writable"

# Check 5: Input files exist
echo "5. Checking input files..."
if [ -f "ontology/spec.ttl" ]; then
    echo "   ✓ ontology/spec.ttl found"
else
    echo "   ⚠ ontology/spec.ttl not found"
fi

echo ""
echo "=== Pre-flight checks passed! ==="
echo "Ready for: ggen sync"
```

---

## Production Sync Procedure

### Standard Workflow

1. **Prepare**:
   ```bash
   # Run pre-flight checks
   bash pre-flight-checks.sh

   # Optional: backup existing output
   cp -r docs docs.backup-$(date +%s)
   ```

2. **Execute**:
   ```bash
   # Run ggen sync with safety enabled
   specify ggen sync \
     --manifest ggen.toml \
     --preflight \
     --verbose
   ```

3. **Verify**:
   ```bash
   # Check generated files
   ls -la docs/

   # Validate output (if applicable)
   # Example: Check markdown syntax
   markdownlint docs/*.md || true
   ```

4. **Commit**:
   ```bash
   # Add generated files to git
   git add docs/
   git commit -m "docs: regenerate from RDF spec"
   ```

### Advanced: Dry-Run Mode

Test without writing files:

```bash
# Preview what would be generated (using ggen capabilities)
ggen sync --dry-run

# OR with specify wrapper (simulated)
specify ggen sync --manifest ggen.toml --preflight --verbose
```

### Advanced: Watch Mode

Auto-regenerate on file changes:

```bash
# Continuous watch mode
specify ggen sync --watch --verbose

# Press Ctrl+C to stop
```

---

## Failure Recovery Scenarios

### Scenario 1: File Not Found During Sync

**Error**:
```
[red]✗ Input file not found[/red]
Path: ontology/spec.ttl
```

**Recovery**:
1. Verify file exists: `ls -la ontology/spec.ttl`
2. Check ggen.toml paths are correct
3. Verify relative paths from project root
4. Retry sync: `specify ggen sync`

---

### Scenario 2: Permission Denied on Output

**Error**:
```
[red]✗ Output directory not writable[/red]
Directory: docs/
```

**Recovery**:
1. Check permissions: `ls -ld docs/`
2. Grant write access: `chmod u+w docs/`
3. Verify owner: `stat docs/`
4. If needed, change owner: `chown $USER docs/`
5. Retry sync: `specify ggen sync`

---

### Scenario 3: Disk Full

**Error**:
```
[yellow]⚠ Low disk space: 5.2MB available[/yellow]
```

**Recovery**:
1. Check disk usage: `df -h .`
2. Clean up temporary files: `rm -rf .ggen-staging/`
3. Remove old backups: `rm -rf docs.backup-*/`
4. Expand disk or use different output location
5. Retry sync: `specify ggen sync`

---

### Scenario 4: SPARQL Query Timeout

**Error**:
```
[red]✗ SPARQL query execution timed out after 30s[/red]
Query: sparql/features.sparql
```

**Recovery**:
1. Review query complexity: `head sparql/features.sparql`
2. Test query on smaller dataset
3. Optimize SPARQL query:
   - Remove unnecessary conditions
   - Break into multiple queries
   - Add LIMIT clause for testing
4. Increase timeout in configuration (if available)
5. Retry sync: `specify ggen sync`

---

### Scenario 5: Another ggen sync Is Running

**Error**:
```
[red]✗ Another ggen sync Is Running[/red]
PID: 12345
```

**Recovery**:
1. Wait for other process: `sleep 60; specify ggen sync`
2. Check if process is stuck: `ps -p 12345`
3. Force kill if hung: `kill -9 12345`
4. Remove lock file: `rm -f .ggen.lock`
5. Retry sync: `specify ggen sync`

---

### Scenario 6: Invalid RDF/Turtle Syntax

**Error**:
```
[red]✗ Invalid RDF/Turtle Data[/red]
File: ontology/spec.ttl
Error: Unexpected character
```

**Recovery**:
1. Validate syntax: `rdflib validate ontology/spec.ttl`
2. Check file encoding: `file ontology/spec.ttl`
3. Fix syntax errors (missing quotes, brackets, etc.)
4. Test with simpler RDF first
5. Retry sync: `specify ggen sync`

---

### Scenario 7: Lock File Timeout (Concurrent Access)

**Error**:
```
[red]✗ Could not acquire lock on .ggen.lock within 30s[/red]
Held by PID: 56789
```

**Recovery**:
1. Check running process: `ps -p 56789`
2. Wait for completion (recommended)
3. Or kill stuck process: `kill 56789`
4. Remove lock: `rm -f .ggen.lock`
5. Ensure only one ggen sync runs at a time
6. Retry sync: `specify ggen sync`

---

## Quick Reference

### Commands

```bash
# Standard sync
specify ggen sync

# With custom manifest path
specify ggen sync --manifest custom.toml

# Verbose output
specify ggen sync --verbose

# Watch mode
specify ggen sync --watch

# Disable pre-flight checks (not recommended)
specify ggen sync --no-preflight

# JSON output (for automation)
specify ggen sync --json
```

### Directories

- **Configuration**: `ggen.toml`
- **Input RDF**: `ontology/`, `memory/`
- **Queries**: `sparql/`
- **Templates**: `templates/`
- **Output**: `docs/`, project-specific
- **Staging**: `.ggen-staging/` (temporary)
- **Recovery**: `.ggen-recovery/` (metadata)
- **Lock**: `.ggen.lock` (temporary)

### Environment Variables

None required. Optional:

- `GGEN_TIMEOUT=60` - Override SPARQL timeout (seconds)
- `GGEN_VERBOSE=1` - Enable verbose logging

---

## Monitoring and Alerts

### Monitor Sync Success

```bash
# Run sync with JSON output for monitoring
specify ggen sync --json | jq .

# Check exit code
specify ggen sync && echo "Success" || echo "Failed"

# Monitor logs
tail -f .ggen-recovery/*.json
```

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Partial files | Interrupted sync | Clean up `.ggen-staging/`, retry |
| Stale lock | Crashed process | Check PID, remove `.ggen.lock` |
| Slow sync | Complex queries | Optimize SPARQL, increase timeout |
| Wrong output | Manifest error | Validate `ggen.toml`, check paths |
| Permission errors | File ownership | Run with correct user or `sudo` |

---

## Best Practices

1. **Run pre-flight checks** before each sync
2. **Backup output** before making changes: `cp -r docs docs.backup`
3. **Use version control** to track changes
4. **Test changes** with small datasets first
5. **Monitor execution** with `--verbose` flag
6. **Clean up** after failures: `rm -rf .ggen-staging/`
7. **Schedule syncs** during low-traffic times in CI/CD
8. **Set reasonable timeouts** for your SPARQL queries

---

## Support and Debugging

### Debug Mode

Enable detailed logging:

```bash
# Verbose output
specify ggen sync --verbose

# Check recovery metadata
cat .ggen-recovery/current-attempt.json | jq .

# Review last failed attempt
cat .ggen-recovery/failed-*.json | jq .
```

### Manual Recovery

If automated recovery fails:

```bash
# Remove staging directory
rm -rf .ggen-staging/

# Remove lock file
rm -f .ggen.lock

# Check what was changed
git status
git diff docs/

# Restore from backup if needed
rm -rf docs/
cp -r docs.backup-<timestamp>/ docs/
```

---

**Created**: 2025-12-21
**Phase**: 1 (Production-Ready)
**Status**: Approved for Production Use
