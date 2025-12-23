# How-to: Troubleshoot ggen Issues

**Goal:** Diagnose and fix ggen transformation errors
**Time:** 20-30 minutes | **Level:** Advanced

## Common Errors

### 1. Turtle Syntax Error

**Error:** 
```
Error: Invalid Turtle syntax in ontology/cli-commands.ttl
  Line 15: Unexpected character '€'
```

**Cause:** Invalid RDF syntax

**Fix:**
- Check line 15
- Ensure all `;` and `.` are present
- Use ASCII characters only in strings
- Validate with `rdf-validate`

### 2. SHACL Validation Error

**Error:**
```
Error: SHACL validation failed
  Target: sk:hello
  Shape: sk:CommandShape
  Message: Missing required property sk:hasModule
```

**Cause:** Missing required properties

**Fix:**
```turtle
sk:hello
    a sk:Command ;
    rdfs:label "hello" ;
    sk:description "..." ;
    sk:hasModule "specify_cli.commands.hello" .  # Add this
```

### 3. SPARQL Error

**Error:**
```
Error: SPARQL query error: Undefined variable ?name
```

**Cause:** Variable not selected in query

**Fix:**
```sparql
SELECT ?name ?description WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?name ;
         sk:description ?description .
}
```

### 4. Template Error

**Error:**
```
Error: Template error in command.tera
  Undefined variable: 'description'
```

**Cause:** SPARQL query not extracting variable

**Fix:**
- Check SPARQL query
- Add `SELECT ?description`
- Ensure RDF has the property

### 5. File Permission Error

**Error:**
```
Error: Permission denied writing to src/specify_cli/commands/hello.py
```

**Cause:** File locked or no write permission

**Fix:**
```bash
# Check permissions
ls -la src/specify_cli/commands/

# Fix permissions
chmod 644 src/specify_cli/commands/hello.py

# Close editor if open
# Retry ggen sync
```

## Debugging Steps

1. **Check RDF Syntax**
   ```bash
   ggen validate ontology/cli-commands.ttl
   ```

2. **Test SPARQL Query**
   ```bash
   # Manually run SPARQL query
   # against your RDF data
   ```

3. **Verify Templates**
   ```bash
   # Check template file exists
   ls -la templates/command.tera
   ```

4. **Check Configuration**
   ```bash
   cat docs/ggen.toml
   # Verify paths are correct
   ```

5. **Run with Verbose**
   ```bash
   ggen sync --verbose
   ```

## Prevention

✅ Validate before running:
```bash
ggen validate ontology/
```

✅ Check configuration:
```bash
cat docs/ggen.toml
```

✅ Run incrementally:
```bash
# Test simple spec first
# Then add complexity
```

✅ Verify receipts:
```bash
cat .ggen-receipt.json
```

## See Also
- [How-to: Run ggen Sync](./run-ggen-sync.md)
- [Reference: ggen Configuration](../../reference/ggen-config.md)
