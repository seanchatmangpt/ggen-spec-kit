---
paths:
  - "src/**/*.py"
  - "tests/**/*.py"
---

# Python Code Rules

## Type Hints
- ✅ ALL functions MUST have complete type hints
- ✅ Use `from __future__ import annotations`
- ✅ Use `T | None` or `Optional[T]` for nullable
- ❌ Untyped parameters or return values

## Docstrings
- ✅ NumPy-style on public functions
- ✅ Include Parameters, Returns, Raises sections
- ✅ First line under 80 characters
- ❌ Missing descriptions on public APIs

## Imports
- ✅ Standard lib → third-party → local
- ✅ Absolute imports from `specify_cli`
- ❌ Wildcard imports (`from x import *`)
- ❌ Circular imports

## Error Handling
- ✅ Specific exception types
- ✅ Log exceptions with context
- ❌ Bare `except:` or generic Exception

## Code Style
- ✅ 88 char line length (Black)
- ✅ 4-space indentation
- ✅ Two blank lines between classes
- ❌ Lines over 88 characters

## Subprocess
- ✅ Use `run_logged()` (runtime layer)
- ✅ List-based: `["cmd", "arg"]`
- ❌ `shell=True`
- ❌ String-based commands

## Testing
- ✅ `test_<scenario>_<expected>()` naming
- ✅ Arrange/Act/Assert pattern
- ✅ 80%+ coverage (ops layer focus)
- ❌ Tests without fixtures
