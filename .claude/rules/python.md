---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Python Code Rules

## Type Hints
- ALL functions MUST have complete type hints
- Use `from __future__ import annotations` for forward references
- Use `Optional[T]` or `T | None` for nullable types
- Use `TypedDict` for complex dictionary structures

## Docstrings
- NumPy-style docstrings on all public functions
- Include Parameters, Returns, Raises, Examples sections
- Keep first line under 80 characters

## Imports
- Standard library first, then third-party, then local
- Use absolute imports from `specify_cli`
- No wildcard imports (`from x import *`)

## Error Handling
- Use specific exception types
- Never bare `except:`
- Log exceptions with context

## Code Style
- Max line length: 88 characters (Black default)
- 4-space indentation
- Two blank lines between top-level definitions
- One blank line between method definitions

## Subprocess Calls
- NEVER use `shell=True`
- Use list-based command construction
- Use `run_logged()` from runtime layer

## Testing
- Test files: `test_*.py`
- Test functions: `test_*`
- Use pytest fixtures
- Aim for 80%+ coverage
