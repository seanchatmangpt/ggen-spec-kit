# Tutorial 4: Your First Test

**Time to complete:** 15-20 minutes
**Prerequisites:** Complete [Tutorial 3: Write Your First RDF Specification](./03-first-rdf-spec.md)
**What you'll learn:** How to write and run tests for your code

---

## Overview

Testing is essential in Spec Kit. We use pytest to verify that:
- Your RDF specifications are correctly transformed
- Your business logic works as intended
- Your code meets quality standards

---

## Step 1: Understand the Test Structure

Your project has tests organized in three directories:

```
tests/
├── unit/          # Tests for individual functions
├── e2e/           # End-to-end tests for CLI commands
└── conftest.py    # Pytest configuration and fixtures
```

### Test Types

| Type | Purpose | Example |
|------|---------|---------|
| **Unit Tests** | Test individual functions | Test the `hello_operation` function |
| **E2E Tests** | Test complete CLI commands | Test running `specify hello` command |
| **Integration Tests** | Test multiple components together | Test RDF → code generation |

---

## Step 2: Find Your Generated Test

From Tutorial 3, ggen created a test file for your command. Find it:

```bash
find tests/ -name "*hello*"
```

You should find: `tests/e2e/test_commands_hello.py`

Open it:

```bash
cat tests/e2e/test_commands_hello.py
```

It probably looks like:

```python
def test_hello_command(runner):
    """Test the hello command"""
    from click.testing import CliRunner
    runner = CliRunner()
    # Test implementation here
```

---

## Step 3: Write Your First Unit Test

Let's create a unit test for your business logic. Create a new file:

```bash
touch tests/unit/test_hello_ops.py
```

Edit it with this content:

```python
"""Tests for hello operations."""

import pytest
from specify_cli.ops.hello import hello_operation


class TestHelloOperation:
    """Tests for the hello_operation function."""

    def test_hello_default_name(self):
        """Test hello with default name."""
        result = hello_operation()
        assert "Hello, World" in result
        assert "Spec Kit" in result

    def test_hello_custom_name(self):
        """Test hello with custom name."""
        result = hello_operation(name="Alice")
        assert "Hello, Alice" in result
        assert "Spec Kit" in result

    def test_hello_empty_string(self):
        """Test hello with empty string."""
        result = hello_operation(name="")
        assert "Hello," in result

    def test_hello_long_name(self):
        """Test hello with long name."""
        long_name = "A" * 100
        result = hello_operation(name=long_name)
        assert long_name in result
```

This test file:
- Imports your `hello_operation` function
- Creates a test class
- Defines multiple test methods
- Each test checks one thing (the "A" in AIDA)
- Uses assertions to verify behavior

---

## Step 4: Run Your Tests

Run pytest to execute your tests:

```bash
# Run a specific test file
uv run pytest tests/unit/test_hello_ops.py -v

# Run all unit tests
uv run pytest tests/unit/ -v

# Run all tests
uv run pytest tests/ -v
```

Expected output:

```
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_default_name PASSED
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_custom_name PASSED
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_empty_string PASSED
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_long_name PASSED

===== 4 passed in 0.05s =====
```

---

## Step 5: Write an End-to-End Test

Now let's update the generated E2E test to test the full CLI command:

Edit `tests/e2e/test_commands_hello.py`:

```python
"""End-to-end tests for the hello command."""

from click.testing import CliRunner
from specify_cli.cli import app


@pytest.fixture
def runner():
    """Provide a CLI test runner."""
    return CliRunner()


class TestHelloCommand:
    """Tests for the hello CLI command."""

    def test_hello_default(self, runner):
        """Test hello command with default name."""
        result = runner.invoke(app, ["hello"])
        assert result.exit_code == 0
        assert "Hello, World" in result.output

    def test_hello_custom_name(self, runner):
        """Test hello command with custom name."""
        result = runner.invoke(app, ["hello", "--name", "Bob"])
        assert result.exit_code == 0
        assert "Hello, Bob" in result.output

    def test_hello_help(self, runner):
        """Test hello command help."""
        result = runner.invoke(app, ["hello", "--help"])
        assert result.exit_code == 0
        assert "Greet the user" in result.output
        assert "--name" in result.output
```

Key testing patterns:
- **runner.invoke()** - Simulates running the CLI command
- **result.exit_code** - Should be 0 for success
- **result.output** - What was printed to console
- **assert** - Verify expectations

---

## Step 6: Understand pytest Fixtures

The `runner` fixture in E2E tests is a special pytest function that:
1. Creates a CLI test runner
2. Provides it to each test function
3. Automatically cleans up after each test

```python
@pytest.fixture
def runner():
    """Provide a CLI test runner."""
    return CliRunner()
```

Fixtures are great for:
- Setting up test data
- Creating temporary files/databases
- Providing common objects to multiple tests

---

## Step 7: Run All Tests

Now run all your tests together:

```bash
uv run pytest tests/ -v
```

With verbose output (`-v`), you'll see each test:

```
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_default_name PASSED
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_custom_name PASSED
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_empty_string PASSED
tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_long_name PASSED
tests/e2e/test_commands_hello.py::TestHelloCommand::test_hello_default PASSED
tests/e2e/test_commands_hello.py::TestHelloCommand::test_hello_custom_name PASSED
tests/e2e/test_commands_hello.py::TestHelloCommand::test_hello_help PASSED

===== 7 passed in 0.15s =====
```

---

## Step 8: Check Test Coverage

See how much of your code is tested:

```bash
uv run pytest --cov=src/specify_cli tests/ -v
```

This shows:
- What percentage of your code is covered by tests
- Which lines are not tested
- Coverage trends

Spec Kit aims for 80%+ coverage.

---

## Step 9: Fix Failing Tests

If tests fail, pytest shows you why:

```
FAILED tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_default_name

AssertionError: assert 'Hello, World' in 'Howdy, World'
```

This tells you:
1. Which test failed
2. What assertion failed
3. What the actual value was

Fix your code to match the assertion, or update the assertion to match your implementation.

---

## Step 10: Test-Driven Development

Spec Kit supports Test-Driven Development (TDD):

1. **Write a test** for what you want to build
2. **Run it** - watch it fail
3. **Implement** the simplest code to make it pass
4. **Refactor** to improve the implementation

Example:

```python
# Step 1: Write the test (this test will fail)
def test_hello_emoji(self):
    """Test hello with emoji."""
    result = hello_operation(name="🌍")
    assert "🌍" in result

# Step 2: Run it - it fails
# Step 3: Implement
def hello_operation(name: str = "World") -> str:
    return f"Hello, {name}! Welcome to Spec Kit."

# Step 4: Test passes!
# Step 5: Refactor as needed
```

---

## Step 11: Best Practices for Testing

### Write Meaningful Test Names

```python
# ✅ Good - describes what it tests
def test_hello_with_special_characters(self):
    pass

# ❌ Bad - vague
def test_hello_1(self):
    pass
```

### One Assertion Per Test (Usually)

```python
# ✅ Good - tests one thing
def test_hello_returns_greeting(self):
    result = hello_operation()
    assert "Hello" in result

# ❌ Bad - tests multiple things
def test_hello(self):
    result = hello_operation("Alice")
    assert "Hello" in result
    assert "Alice" in result
    assert len(result) > 5
    # etc.
```

### Use Descriptive Assertions

```python
# ✅ Good - clear what's expected
assert result.exit_code == 0, "Command should exit successfully"

# ❌ Bad - unclear
assert result.exit_code == 0
```

### Test Edge Cases

```python
# Test normal cases
test_hello_custom_name()

# Test edge cases
test_hello_empty_string()
test_hello_very_long_name()
test_hello_special_characters()
test_hello_unicode()
```

---

## Next Steps

You've learned:
- ✅ How to write unit tests
- ✅ How to write end-to-end tests
- ✅ How to run and debug tests
- ✅ How to measure test coverage
- ✅ Test-driven development

**Next tutorial:** [Tutorial 5: Running ggen Sync](./05-ggen-sync-first-time.md)

Or explore:
- **[How-to: Run Tests](../guides/testing/run-tests.md)** - Advanced testing
- **[How-to: Debug Tests](../guides/testing/debug-tests.md)** - Troubleshoot test failures

---

## Quick Reference

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/unit/test_hello_ops.py -v

# Run specific test class
uv run pytest tests/unit/test_hello_ops.py::TestHelloOperation -v

# Run specific test method
uv run pytest tests/unit/test_hello_ops.py::TestHelloOperation::test_hello_default_name -v

# Show test coverage
uv run pytest --cov=src/specify_cli tests/ -v

# Run tests with print output visible
uv run pytest tests/ -v -s

# Stop on first failure
uv run pytest tests/ -x
```

---

## Summary

Tests are essential for:
- Verifying your code works correctly
- Catching bugs early
- Enabling safe refactoring
- Documenting expected behavior

In Spec Kit, tests verify that RDF specifications are correctly transformed into working code!
