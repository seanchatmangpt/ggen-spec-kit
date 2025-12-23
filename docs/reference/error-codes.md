# Reference: Error Codes

Error messages and their solutions.

## RDF Syntax Errors

### E001: Invalid Turtle Syntax
```
Error: Invalid Turtle syntax at line 15
```
**Cause:** Malformed RDF/Turtle
**Fix:** Check parentheses, semicolons, periods

### E002: Undefined Prefix
```
Error: Undefined prefix 'myprefix'
```
**Cause:** Prefix not declared
**Fix:** Add `@prefix myprefix: <http://...>`

## Validation Errors

### E101: SHACL Validation Failed
```
Error: SHACL validation failed
  Shape: CommandShape
  Message: Missing required property
```
**Cause:** Missing required RDF properties
**Fix:** Add all required properties

### E102: Type Mismatch
```
Error: Type mismatch for property
  Expected: string
  Got: integer
```
**Cause:** Wrong data type
**Fix:** Use correct type

## Generation Errors

### E201: Template Error
```
Error: Template rendering failed
  Undefined variable: description
```
**Cause:** SPARQL query not extracting variable
**Fix:** Update SPARQL query

### E202: Output Permission Denied
```
Error: Permission denied
  File: src/specify_cli/commands/hello.py
```
**Cause:** File locked or no write permission
**Fix:** Close editor, check permissions

## Runtime Errors

### E301: Import Error
```
Error: ImportError: No module named 'specify_cli'
```
**Cause:** Dependencies not installed
**Fix:** Run `uv sync`

### E302: Module Not Found
```
Error: ModuleNotFoundError: specify_cli.ops.hello
```
**Cause:** Implementation module missing
**Fix:** Create the file

## Test Errors

### E401: Test Failure
```
FAILED test_hello
AssertionError: assert 'Hello' in 'Goodbye'
```
**Cause:** Test failed
**Fix:** Debug test or fix code

### E402: Import Error in Tests
```
ImportError: No module named test module
```
**Cause:** Test can't import code
**Fix:** Check PYTHONPATH, run `uv sync`

## Solutions

For each error, see:
1. What caused it
2. How to fix it
3. How to prevent it
