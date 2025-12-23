# How-to: Few-Shot Learning Patterns for AI

**Goal:** Enable AI agents to learn implementation patterns from examples.

**Time:** 25 minutes | **Level:** Advanced

---

## Overview

Few-shot learning lets AI learn patterns from examples rather than long explanations.

**Traditional:**
```
Explain RDF syntax in detail (2,000 tokens)
→ AI understands concept
→ AI writes correct RDF
```

**Few-shot:**
```
Show 3 RDF examples (300 tokens)
→ AI recognizes pattern
→ AI writes correct RDF
```

**Efficiency:** 85% reduction

---

## Step 1: Identify Key Patterns

What patterns does AI need to learn?

1. **RDF Specification Pattern** - How to write RDF specs
2. **Test Pattern** - How to write tests
3. **Implementation Pattern** - How to write ops functions
4. **Architecture Pattern** - Code organization
5. **Documentation Pattern** - How to document code

---

## Step 2: Create Few-Shot Example Sets

### Pattern 1: RDF Specification

**File: `docs/examples/ai-learning/rdf-patterns.ttl`**

```turtle
# SIMPLE COMMAND PATTERN
@prefix sk: <http://ggen-spec-kit.org/spec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Example 1: Simple command with no arguments
sk:hello
    a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet the user" ;
    sk:hasModule "specify_cli.commands.hello" .

# Example 2: Command with required argument
sk:greet
    a sk:Command ;
    rdfs:label "greet" ;
    sk:description "Greet a person by name" ;
    sk:hasModule "specify_cli.commands.greet" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "name" ;
        sk:description "Name to greet" ;
        sk:required true ;
        sk:type "str"
    ] .

# Example 3: Command with optional arguments
sk:build
    a sk:Command ;
    rdfs:label "build" ;
    sk:description "Build the project" ;
    sk:hasModule "specify_cli.commands.build" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "target" ;
        sk:description "Build target (wheel, sdist)" ;
        sk:required false ;
        sk:default "wheel"
    ] .

# Example 4: Command with options
sk:lint
    a sk:Command ;
    rdfs:label "lint" ;
    sk:description "Check code quality" ;
    sk:hasModule "specify_cli.commands.lint" ;
    sk:hasOption [
        a sk:Option ;
        sk:name "strict" ;
        sk:description "Strict mode" ;
        sk:flag true
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:name "output" ;
        sk:description "Output format" ;
        sk:flag false ;
        sk:default "text"
    ] .
```

**Pattern Recognition for AI:**
- Command declaration: `sk:[name] a sk:Command`
- Basic properties: `rdfs:label`, `sk:description`, `sk:hasModule`
- Arguments: nested structure with `sk:Argument`
- Options: nested structure with `sk:Option`
- Boolean flags: `sk:flag true/false`
- Default values: `sk:default`

### Pattern 2: Test Patterns

**File: `docs/examples/ai-learning/test-patterns.py`**

```python
"""Few-shot test patterns for AI learning."""

# PATTERN 1: Simple Unit Test
# When: Testing pure function with single output
def test_hello_operation():
    """Test hello_operation returns greeting."""
    result = hello_operation()
    assert "Hello" in result


# PATTERN 2: Parameterized Unit Test
# When: Testing function with multiple inputs
import pytest

@pytest.mark.parametrize("input_name,expected_substring", [
    ("World", "Hello, World"),
    ("Alice", "Hello, Alice"),
    ("Bob", "Hello, Bob"),
])
def test_greet_operation(input_name, expected_substring):
    """Test greet_operation with various names."""
    result = greet_operation(input_name)
    assert expected_substring in result


# PATTERN 3: Exception Testing
# When: Function should raise exception on bad input
def test_greet_empty_name_raises():
    """Test greet_operation raises on empty name."""
    with pytest.raises(ValueError):
        greet_operation("")


# PATTERN 4: End-to-End CLI Test
# When: Testing complete CLI command
from click.testing import CliRunner

def test_hello_command():
    """Test hello CLI command."""
    runner = CliRunner()
    result = runner.invoke(app, ["hello"])
    assert result.exit_code == 0
    assert "Hello" in result.output


# PATTERN 5: CLI Test with Options
def test_greet_command_with_name():
    """Test greet CLI command with custom name."""
    runner = CliRunner()
    result = runner.invoke(app, ["greet", "--name", "Alice"])
    assert result.exit_code == 0
    assert "Alice" in result.output


# PATTERN 6: Fixture Pattern
# When: Multiple tests need same setup
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {
        "names": ["Alice", "Bob", "Charlie"],
        "expected": ["Hello, Alice", "Hello, Bob", "Hello, Charlie"]
    }

def test_greet_all_names(sample_data):
    """Test greet_operation with fixture data."""
    for name, expected in zip(sample_data["names"], sample_data["expected"]):
        result = greet_operation(name)
        assert expected in result


# PATTERN 7: Coverage-Focused Test
# When: Need to cover all code paths
def test_operation_happy_path():
    """Test happy path."""
    assert operation(valid_input) == expected_output

def test_operation_edge_case_empty():
    """Test edge case: empty input."""
    with pytest.raises(ValueError):
        operation("")

def test_operation_edge_case_none():
    """Test edge case: None input."""
    with pytest.raises(TypeError):
        operation(None)

def test_operation_large_input():
    """Test with large input."""
    large_input = "x" * 10000
    result = operation(large_input)
    assert len(result) > 0
```

**Pattern Recognition for AI:**
- Test name format: `test_[function_or_command]_[scenario]`
- Assertion style: `assert [actual] [comparison] [expected]`
- Parametrized tests: `@pytest.mark.parametrize`
- Exception testing: `with pytest.raises(ExceptionType):`
- CLI testing: `runner.invoke(app, ["command", "--option", "value"])`
- Fixtures: `@pytest.fixture` decorator
- Coverage: test happy path + edge cases + large inputs

### Pattern 3: Implementation Patterns

**File: `docs/examples/ai-learning/implementation-patterns.py`**

```python
"""Few-shot implementation patterns."""

# PATTERN 1: Pure Function (Operations Layer)
# When: Business logic that has no side effects
def hello_operation() -> str:
    """Generate greeting message.

    Returns
    -------
    str
        Greeting message
    """
    return "Hello, World! Welcome to Spec Kit."


# PATTERN 2: Function with Parameters
def greet_operation(name: str) -> str:
    """Generate personalized greeting.

    Parameters
    ----------
    name : str
        Person to greet

    Returns
    -------
    str
        Personalized greeting

    Raises
    ------
    ValueError
        If name is empty
    """
    if not name:
        raise ValueError("Name cannot be empty")
    return f"Hello, {name}! Welcome to Spec Kit."


# PATTERN 3: Function with Optional Parameters
def build_operation(
    target: str = "wheel",
    verbose: bool = False
) -> Dict[str, Any]:
    """Build project artifacts.

    Parameters
    ----------
    target : str, optional
        Build target: "wheel", "sdist", or "all"
        Default is "wheel"
    verbose : bool, optional
        Enable verbose output
        Default is False

    Returns
    -------
    Dict[str, Any]
        Build results with "success", "artifacts", "time_seconds"
    """
    result = {
        "success": True,
        "artifacts": [f"dist/package-{target}.tar.gz"],
        "time_seconds": 2.5
    }
    return result


# PATTERN 4: Function with Validation
def validate_input(data: Dict) -> bool:
    """Validate input data structure.

    Parameters
    ----------
    data : Dict
        Data to validate

    Returns
    -------
    bool
        True if valid, raises exception if not

    Raises
    ------
    TypeError
        If data is not a dict
    ValueError
        If required fields are missing
    """
    if not isinstance(data, dict):
        raise TypeError("Data must be a dictionary")

    required_fields = ["name", "email"]
    missing = [f for f in required_fields if f not in data]
    if missing:
        raise ValueError(f"Missing required fields: {missing}")

    return True


# PATTERN 5: Function with Logging
from specify_cli.core.telemetry import get_logger

logger = get_logger(__name__)

def process_operation(items: List[str]) -> int:
    """Process list of items.

    Parameters
    ----------
    items : List[str]
        Items to process

    Returns
    -------
    int
        Number of items processed
    """
    logger.info("Processing items", extra={"count": len(items)})

    processed = 0
    for item in items:
        logger.debug("Processing item", extra={"item": item})
        processed += 1

    logger.info("Processing complete", extra={"total": processed})
    return processed


# PATTERN 6: Function with Observability
from specify_cli.core.telemetry import span, timed

@timed
def slow_operation(data: Dict) -> Dict:
    """Process data with timing instrumentation.

    Parameters
    ----------
    data : Dict
        Data to process

    Returns
    -------
    Dict
        Processed result
    """
    with span("validation", attributes={"data_size": len(data)}):
        # Validation logic
        pass

    with span("processing", attributes={"data_size": len(data)}):
        # Processing logic
        result = {"success": True}

    return result


# PATTERN 7: Function with Error Handling
def robust_operation(value: Any) -> str:
    """Operation with comprehensive error handling.

    Parameters
    ----------
    value : Any
        Value to process

    Returns
    -------
    str
        Result

    Raises
    ------
    TypeError
        If value type is unsupported
    ValueError
        If value is invalid
    """
    try:
        if not isinstance(value, (str, int, float)):
            raise TypeError(f"Unsupported type: {type(value)}")

        if isinstance(value, str) and not value:
            raise ValueError("String cannot be empty")

        result = f"Processed: {value}"
        return result

    except (TypeError, ValueError) as e:
        logger.error("Operation failed", exc_info=True)
        raise
```

**Pattern Recognition for AI:**
- Function signature with type hints
- Docstring format (NumPy style)
- Parameters section
- Returns section
- Raises section
- Error handling with try/except
- Logging with extra context
- Observability with @timed and span()
- Validation before processing

---

## Step 3: Create Pattern Index

**File: `docs/examples/ai-learning/pattern-index.md`**

```markdown
# AI Learning Patterns Index

## RDF Specification Patterns

### When to use which pattern:

| Pattern | When | Files |
|---------|------|-------|
| Simple Command | No arguments | examples/rdf-patterns.ttl #1 |
| Command with Arg | Required argument | examples/rdf-patterns.ttl #2 |
| Command with Optional | Optional arguments | examples/rdf-patterns.ttl #3 |
| Command with Options | --flags or --options | examples/rdf-patterns.ttl #4 |

## Test Patterns

### When to use which pattern:

| Pattern | When | Files |
|---------|------|-------|
| Simple Unit Test | Single assertion | examples/test-patterns.py #1 |
| Parameterized | Multiple inputs | examples/test-patterns.py #2 |
| Exception Test | Should raise | examples/test-patterns.py #3 |
| CLI Test | Test command | examples/test-patterns.py #4 |
| Fixture | Shared setup | examples/test-patterns.py #6 |
| Coverage | All code paths | examples/test-patterns.py #7 |

## Implementation Patterns

### When to use which pattern:

| Pattern | When | Files |
|---------|------|-------|
| Pure Function | No side effects | examples/implementation-patterns.py #1 |
| With Parameters | Function takes input | examples/implementation-patterns.py #2 |
| Optional Parameters | Default values | examples/implementation-patterns.py #3 |
| With Validation | Check inputs | examples/implementation-patterns.py #4 |
| With Logging | Need visibility | examples/implementation-patterns.py #5 |
| With Observability | Need tracing | examples/implementation-patterns.py #6 |
| Error Handling | Expected errors | examples/implementation-patterns.py #7 |

## Usage for AI

1. AI reads examples 1-2 from relevant pattern file
2. AI recognizes patterns
3. AI applies patterns to new code
4. AI writes correct, consistent code

## Pattern Verification

Each pattern is:
- Verified with tests
- Used in actual codebase
- Follows architecture constraints
- Includes docstrings
- Has observability
- Handles errors
```

---

## Step 4: Integrate Patterns with Context Injection

**File: `scripts/few-shot-injector.py`**

```python
"""Inject few-shot examples into AI context."""

class FewShotInjector:
    """Inject pattern examples for AI learning."""

    def inject_patterns(self, task: str, context_limit: int = 1000) -> Dict:
        """Inject few-shot examples.

        Parameters
        ----------
        task : str
            What AI is implementing
        context_limit : int
            Max tokens for examples

        Returns
        -------
        Dict
            Few-shot examples
        """
        examples = {
            "task": task,
            "patterns": [],
            "pattern_index": [],
            "estimated_tokens": 0
        }

        # Select appropriate patterns
        if task == "add-cli-command":
            examples["patterns"] = self._load_rdf_patterns(2)
            examples["patterns"] += self._load_test_patterns(2)
            examples["pattern_index"] = self._get_pattern_guide("cli-command")

        elif task == "write-test":
            examples["patterns"] = self._load_test_patterns(3)
            examples["pattern_index"] = self._get_pattern_guide("testing")

        elif task == "implement-function":
            examples["patterns"] = self._load_implementation_patterns(3)
            examples["pattern_index"] = self._get_pattern_guide("implementation")

        # Count tokens
        examples["estimated_tokens"] = self._count_tokens(examples)

        return examples

    def _load_rdf_patterns(self, count: int) -> List[Dict]:
        """Load RDF pattern examples."""
        patterns = []
        with open("docs/examples/ai-learning/rdf-patterns.ttl") as f:
            # Parse examples, return top `count`
            pass
        return patterns

    def _load_test_patterns(self, count: int) -> List[Dict]:
        """Load test pattern examples."""
        patterns = []
        with open("docs/examples/ai-learning/test-patterns.py") as f:
            # Parse examples, return top `count`
            pass
        return patterns

    def _load_implementation_patterns(self, count: int) -> List[Dict]:
        """Load implementation pattern examples."""
        patterns = []
        with open("docs/examples/ai-learning/implementation-patterns.py") as f:
            # Parse examples, return top `count`
            pass
        return patterns

    def _get_pattern_guide(self, pattern_type: str) -> Dict:
        """Get pattern selection guide."""
        with open("docs/examples/ai-learning/pattern-index.md") as f:
            # Extract relevant section
            pass
        return {}

    def _count_tokens(self, examples: Dict) -> int:
        """Estimate tokens."""
        text = json.dumps(examples)
        return len(text) // 4
```

---

## Step 5: Train AI with Few-Shot Examples

When AI needs to implement something, inject examples first:

```python
# In AI agent prompt:

CONTEXT = """
You are implementing a new CLI command. Here are examples of similar commands:

EXAMPLE 1: Simple Command
[RDF pattern]
[Test pattern]
[Implementation pattern]

EXAMPLE 2: Command with Arguments
[RDF pattern]
[Test pattern]
[Implementation pattern]

EXAMPLE 3: Complex Command
[RDF pattern]
[Test pattern]
[Implementation pattern]

PATTERN GUIDE:
- Use pattern #1 for simple commands
- Use pattern #2 for commands with arguments
- Use pattern #3 for complex commands

Now implement your command following these patterns.
"""
```

**Result:** AI learns from examples and generates consistent code.

---

## Best Practices

### ✅ Do

- Show 2-3 examples per pattern type
- Include complete working examples
- Verify examples pass tests
- Use examples from actual codebase
- Include pattern selection guide
- Show edge cases in examples

### ❌ Don't

- Show contrasting bad examples (confuses AI)
- Use incomplete or broken examples
- Show examples with comments explaining code
- Mix multiple pattern styles
- Forget to include pattern index

---

## Example: AI Learning a Pattern

```
1. AI Task: "Add a new CLI command called 'validate'"

2. System injects few-shot context:
   - 2 RDF specification examples
   - 2 test examples
   - 2 implementation examples
   - Pattern selection guide

3. AI analyzes examples:
   - "I see RDF commands have format: sk:[name] a sk:Command ..."
   - "Tests follow format: test_[name]_[scenario] ..."
   - "Implementations follow format: def [name]_operation(...) ..."

4. AI generates code:
   - RDF: sk:validate a sk:Command ; ...
   - Tests: test_validate_operation() ...
   - Implementation: def validate_operation(...) ...

5. Code matches patterns perfectly:
   - Same style as examples
   - Same architecture as examples
   - Same test coverage as examples
```

---

## Summary

Few-shot learning:
- **Reduces explanation overhead by 85%** (3 examples vs long docs)
- **Ensures consistency** (AI learns from actual patterns)
- **Enables rapid adaptation** (AI applies patterns to new tasks)
- **Scales to new domains** (just add new pattern examples)

---

## See Also

- [AGI Ingestion Guide](../../ecosystem/agi-ingestion.md)
- [Semantic Context Injection](./semantic-context.md)
- [Token Optimization](./token-optimization.md)
