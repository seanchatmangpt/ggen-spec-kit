"""Example usage of runtime.lint module.

This example demonstrates how to use the runtime.lint module
to run code quality checks with ruff and mypy.
"""

from pathlib import Path

from specify_cli.runtime.lint import (
    is_mypy_available,
    is_ruff_available,
    run_mypy,
    run_ruff_check,
    run_ruff_format,
)


def main() -> None:
    """Run lint examples."""
    # Check if tools are available
    print("Tool Availability")
    print("-" * 40)
    print(f"Ruff available: {is_ruff_available()}")
    print(f"Mypy available: {is_mypy_available()}")
    print()

    # Example: Run ruff check on src directory
    print("Ruff Check Example")
    print("-" * 40)
    src_path = Path("src/specify_cli")
    if src_path.exists():
        result = run_ruff_check([src_path])
        print(f"Success: {result['success']}")
        print(f"Violations: {len(result.get('violations', []))}")
        print(f"Duration: {result['duration']:.2f}s")
    print()

    # Example: Run ruff format check
    print("Ruff Format Example")
    print("-" * 40)
    if src_path.exists():
        result = run_ruff_format([src_path], check=True)
        print(f"All files formatted: {result['success']}")
        print(f"Files needing formatting: {len(result['modified_files'])}")
        print(f"Duration: {result['duration']:.2f}s")
    print()

    # Example: Run mypy type checking
    print("Mypy Type Check Example")
    print("-" * 40)
    if src_path.exists():
        result = run_mypy([src_path])
        print(f"Type check passed: {result['success']}")
        print(f"Type errors: {len(result['errors'])}")
        print(f"Duration: {result['duration']:.2f}s")
        if result["errors"]:
            print("\nFirst 5 errors:")
            for error in result["errors"][:5]:
                print(f"  {error}")
    print()

    # Example: Run ruff check with JSON output
    print("Ruff Check with JSON Output")
    print("-" * 40)
    if src_path.exists():
        result = run_ruff_check([src_path], output_format="json")
        print(f"Success: {result['success']}")
        print(f"Violations: {len(result['violations'])}")
        if result["violations"]:
            print("\nFirst violation:")
            import json

            print(json.dumps(result["violations"][0], indent=2))
    print()

    # Example: Run ruff check with auto-fix
    print("Ruff Check with Auto-Fix")
    print("-" * 40)
    test_file = Path("src/specify_cli/runtime/lint.py")
    if test_file.exists():
        result = run_ruff_check([test_file], fix=True)
        print(f"Fixed violations: {result['success']}")
        print(f"Duration: {result['duration']:.2f}s")


if __name__ == "__main__":
    main()
