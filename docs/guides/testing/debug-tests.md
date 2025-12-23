# How-to: Debug Test Failures

**Goal:** Systematically diagnose and fix failing tests
**Time:** 20-25 minutes | **Level:** Intermediate

## Debugging Process

### Step 1: Run with Verbose Output
```bash
uv run pytest tests/unit/test_hello_ops.py::test_specific -v -s
```

### Step 2: Check Error Message
```
FAILED tests/unit/test_hello_ops.py::test_specific
AssertionError: assert 'Hello' in 'Goodbye'
```

### Step 3: Add Print Debugging
```python
def test_something():
    result = operation("input")
    print(f"Actual result: {result}")
    print(f"Expected: contains 'Hello'")
    assert "Hello" in result
```

Run with `-s` to see prints:
```bash
pytest tests/ -s
```

### Step 4: Use pytest's Built-in Features

**Drop into debugger:**
```python
def test_something():
    result = operation("input")
    import pdb; pdb.set_trace()  # Execution pauses here
    assert result == expected
```

**Show local variables:**
```bash
pytest tests/ --tb=long
```

**Capture output:**
```bash
pytest tests/ -o log_cli=true -o log_cli_level=DEBUG
```

## Common Issues

### ImportError
- Missing module
- Wrong path
- Missing __init__.py

**Fix:**
```bash
python -c "import specify_cli.ops.hello"  # Test import
uv sync  # Update dependencies
```

### AssertionError
- Logic bug in code
- Wrong test expectation
- Edge case not handled

**Fix:**
- Print actual vs expected
- Simplify assertion
- Test edge cases

### AttributeError
- Typo in function/property
- Object doesn't have attribute
- Wrong type

**Fix:**
- Check spelling
- Verify object type
- Print type(obj)

### Timeout
- Infinite loop
- Blocking operation
- Resource exhaustion

**Fix:**
- Add timeout to test
- Break loop condition
- Check resource usage

## Strategies

**Strategy 1: Isolate**
- Run just failing test
- Remove other assertions
- Test one thing at a time

**Strategy 2: Simplify**
- Use simplest input
- Expected output clear
- No side effects

**Strategy 3: Compare**
- Manual execution
- Expected behavior
- What's different?

**Strategy 4: Instrument**
- Add logging
- Print variables
- Track execution flow

## Advanced Debugging

**Use pytest plugins:**
```bash
pip install pytest-sugar pytest-watch
ptw tests/  # Watch mode
```

**Profile slow tests:**
```bash
pytest tests/ --durations=10
```

**Analyze coverage gaps:**
```bash
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html
```

## See Also
- [How-to: Run Tests](./run-tests.md)
- [Patterns: Test Examples](../../examples/ai-learning/test-patterns.py)
