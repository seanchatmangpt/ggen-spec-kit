---
paths:
  - "src/specify_cli/ops/**/*.py"
---

# Operations Layer Rules

## Purpose
The ops layer contains pure business logic with NO side effects.

## MUST DO
- Implement pure functions (same input = same output)
- Return structured data (dictionaries, dataclasses)
- Validate inputs and raise descriptive exceptions
- Be fully unit-testable without mocking I/O

## MUST NOT
- Import `subprocess` or execute commands
- Open files with `open()` or `Path.read_text()`
- Make HTTP requests
- Access the filesystem directly
- Print to console (return data instead)

## Pattern
```python
def process_data(input_data: dict[str, Any]) -> dict[str, Any]:
    """Process input and return structured result.

    Parameters
    ----------
    input_data : dict
        The input data to process.

    Returns
    -------
    dict
        Structured result with status and data.

    Raises
    ------
    ValueError
        If input_data is invalid.
    """
    # Validate
    if not input_data.get("required_field"):
        raise ValueError("required_field is missing")

    # Pure logic
    result = transform(input_data)

    # Return structured data
    return {
        "status": "success",
        "data": result,
        "metadata": {"processed_at": "..."}
    }
```

## When I/O is Needed
If an operation needs file/network I/O, it should:
1. Accept data as input (not paths)
2. Return data as output
3. Let the runtime layer handle actual I/O
