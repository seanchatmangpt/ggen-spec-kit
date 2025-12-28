# Debug Issue

Systematically debug an error or unexpected behavior.

## Usage
```
/debug [ERROR_OR_DESCRIPTION]
```

## Arguments
- `$ARGUMENTS` - Error message, stack trace, or description of the issue

## Instructions

Debug the following issue: $ARGUMENTS

Systematic debugging process:

1. **Reproduce**
   - Identify exact steps to reproduce
   - Note any environment factors

2. **Isolate**
   - Find the failing component
   - Trace the execution path
   - Identify the layer (commands/ops/runtime)

3. **Analyze**
   - Read relevant source code
   - Check recent changes (git log)
   - Look for similar issues/patterns

4. **Diagnose**
   - Form hypothesis about root cause
   - Verify with targeted tests
   - Check edge cases

5. **Fix**
   - Propose minimal fix
   - Consider side effects
   - Maintain layer boundaries

6. **Verify**
   - Run tests to confirm fix
   - Check for regressions

Provide:
- Root cause analysis
- Fix implementation
- Test to prevent regression
