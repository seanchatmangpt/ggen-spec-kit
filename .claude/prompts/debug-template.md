# Debug Prompt Template

## Variables
- `{{error}}` - Error message or stack trace
- `{{context}}` - Additional context about when it occurs
- `{{expected}}` - Expected behavior

## Template

Debug the following issue:

### Error
```
{{error}}
```

### Context
{{context}}

### Expected Behavior
{{expected}}

## Debugging Process

### Step 1: Analyze the Error
- Parse the stack trace
- Identify the failing line
- Determine the layer (commands/ops/runtime)

### Step 2: Trace the Cause
- Examine the code path leading to the error
- Check input values and types
- Look for missing validation

### Step 3: Identify Root Cause
- Distinguish symptom from cause
- Consider edge cases
- Check for similar patterns elsewhere

### Step 4: Propose Fix
- Minimal change to fix the issue
- Ensure fix is in correct layer
- Consider side effects

### Step 5: Verify Fix
- Write/update test for the case
- Run affected tests
- Check for regressions

## Output Format

```markdown
## Root Cause
[One-line description of the actual cause]

## Analysis
[Step-by-step explanation of how you found the cause]

## Fix
```python
# Before
old_code()

# After
new_code()
```

## Test
```python
def test_{{issue_name}}():
    # Test that verifies the fix
    pass
```

## Prevention
[How to prevent similar issues in the future]
```
