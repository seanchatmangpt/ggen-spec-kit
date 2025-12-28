# Validate Architecture

Validate three-tier architecture compliance and layer boundaries.

## Usage
```
/validate-architecture
```

## Instructions

Validate that the codebase follows the three-tier architecture:

**Layer Rules to Check:**

1. **Commands Layer** (`src/specify_cli/commands/`):
   - Should only parse arguments and format output
   - Should delegate to ops layer immediately
   - MUST NOT have subprocess, file I/O, or HTTP calls

2. **Operations Layer** (`src/specify_cli/ops/`):
   - Should contain pure business logic
   - Should return structured data (dicts)
   - MUST NOT have subprocess, file I/O, or HTTP calls

3. **Runtime Layer** (`src/specify_cli/runtime/`):
   - Should handle ALL side effects
   - All subprocess via `run_logged()`
   - All file I/O and HTTP here
   - MUST NOT import from commands or ops

**Checks to Perform:**
1. Search for `subprocess` imports in commands/ops layers
2. Search for `open()` calls in commands/ops layers
3. Search for `httpx`/`requests` in commands/ops layers
4. Verify runtime layer isolation
5. Check for circular dependencies

Report violations with file:line references and remediation steps.
