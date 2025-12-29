---
paths:
  - "src/specify_cli/ops/**/*.py"
---

# Operations Layer Rules

Pure business logic. No side effects. Input → validate → transform → return data.

## DO
- Write pure functions (deterministic)
- Return structured data (dict/dataclass)
- Validate inputs, raise descriptive errors
- Be fully unit-testable (no mocking needed)

## DON'T
- Use subprocess, file I/O, or HTTP
- Import subprocess, pathlib, httpx
- Print output (return data instead)
- Access filesystem or network
- Contain I/O logic (runtime handles it)

## Pattern
```python
def process(data: dict[str, Any]) -> dict[str, Any]:
    """Process data and return result.

    Raises
    ------
    ValueError
        If data is invalid.
    """
    if not data.get("required_field"):
        raise ValueError("required_field missing")

    result = transform(data)
    return {"status": "success", "data": result}
```

## I/O Delegation
- Accept data, return data (not paths)
- Let runtime layer handle actual I/O
- Example: `process(content: str)` not `process(file_path: Path)`
