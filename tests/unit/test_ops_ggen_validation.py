"""Unit tests for ggen output validation."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from specify_cli.ops.ggen_validation import (
    validate_javascript,
    validate_json,
    validate_markdown,
    validate_python,
)


@pytest.fixture
def temp_dir() -> Path:
    """Create temporary directory."""
    with TemporaryDirectory() as tmp:
        yield Path(tmp)


class TestMarkdownValidation:
    """Tests for Markdown validation."""

    def test_valid_markdown(self, temp_dir: Path) -> None:
        """Test valid Markdown passes."""
        md_file = temp_dir / "test.md"
        md_file.write_text("# Title\n\nSome content.\n")

        result = validate_markdown(md_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_markdown_missing_file(self, temp_dir: Path) -> None:
        """Test missing Markdown file fails."""
        md_file = temp_dir / "missing.md"

        result = validate_markdown(md_file)

        assert result.valid is False
        assert any("not found" in e.lower() for e in result.errors)

    def test_markdown_unclosed_code_block(self, temp_dir: Path) -> None:
        """Test unclosed code block detection."""
        md_file = temp_dir / "test.md"
        md_file.write_text("# Title\n\n```python\ncode\n")

        result = validate_markdown(md_file)

        assert result.valid is False
        assert any("code block" in e.lower() for e in result.errors)

    def test_markdown_broken_link_warning(self, temp_dir: Path) -> None:
        """Test broken relative link warning."""
        md_file = temp_dir / "test.md"
        md_file.write_text("# Title\n\n[Link](missing.md)\n")

        result = validate_markdown(md_file)

        # Warnings don't fail validation
        assert result.valid is True
        assert any("broken link" in w.lower() for w in result.warnings)

    def test_markdown_duplicate_heading_warning(self, temp_dir: Path) -> None:
        """Test duplicate heading warning."""
        md_file = temp_dir / "test.md"
        md_file.write_text("# Title\n\nContent\n\n# Title\n\nMore content\n")

        result = validate_markdown(md_file)

        assert result.valid is True
        assert any("duplicate heading" in w.lower() for w in result.warnings)


class TestJSONValidation:
    """Tests for JSON validation."""

    def test_valid_json(self, temp_dir: Path) -> None:
        """Test valid JSON passes."""
        json_file = temp_dir / "test.json"
        json_file.write_text('{"key": "value", "number": 42}')

        result = validate_json(json_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_json_missing_file(self, temp_dir: Path) -> None:
        """Test missing JSON file fails."""
        json_file = temp_dir / "missing.json"

        result = validate_json(json_file)

        assert result.valid is False
        assert any("not found" in e.lower() for e in result.errors)

    def test_json_invalid_syntax(self, temp_dir: Path) -> None:
        """Test invalid JSON syntax."""
        json_file = temp_dir / "test.json"
        json_file.write_text('{"key": "value",}')  # Trailing comma

        result = validate_json(json_file)

        assert result.valid is False
        assert any("json" in e.lower() for e in result.errors)

    def test_json_large_file_warning(self, temp_dir: Path) -> None:
        """Test large JSON file warning."""
        json_file = temp_dir / "test.json"
        # Create >10MB JSON
        large_data = '{"data": "' + ("x" * (11 * 1024 * 1024)) + '"}'
        json_file.write_text(large_data)

        result = validate_json(json_file)

        assert result.valid is True
        assert any("large" in w.lower() for w in result.warnings)


class TestPythonValidation:
    """Tests for Python validation."""

    def test_valid_python(self, temp_dir: Path) -> None:
        """Test valid Python passes."""
        py_file = temp_dir / "test.py"
        py_file.write_text('def hello():\n    return "world"\n')

        result = validate_python(py_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_python_missing_file(self, temp_dir: Path) -> None:
        """Test missing Python file fails."""
        py_file = temp_dir / "missing.py"

        result = validate_python(py_file)

        assert result.valid is False
        assert any("not found" in e.lower() for e in result.errors)

    def test_python_syntax_error(self, temp_dir: Path) -> None:
        """Test Python syntax error."""
        py_file = temp_dir / "test.py"
        py_file.write_text('def hello(\n    return "world"')

        result = validate_python(py_file)

        assert result.valid is False
        assert any("syntax" in e.lower() for e in result.errors)

    def test_python_wildcard_import_warning(self, temp_dir: Path) -> None:
        """Test wildcard import warning."""
        py_file = temp_dir / "test.py"
        py_file.write_text("from os import *\n")

        result = validate_python(py_file)

        assert result.valid is True
        assert any("wildcard" in w.lower() for w in result.warnings)


class TestJavaScriptValidation:
    """Tests for JavaScript validation."""

    def test_valid_javascript(self, temp_dir: Path) -> None:
        """Test valid JavaScript passes."""
        js_file = temp_dir / "test.js"
        js_file.write_text("function hello() { return 'world'; }\n")

        result = validate_javascript(js_file)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_javascript_missing_file(self, temp_dir: Path) -> None:
        """Test missing JavaScript file fails."""
        js_file = temp_dir / "missing.js"

        result = validate_javascript(js_file)

        assert result.valid is False
        assert any("not found" in e.lower() for e in result.errors)

    def test_javascript_unbalanced_braces(self, temp_dir: Path) -> None:
        """Test unbalanced braces detection."""
        js_file = temp_dir / "test.js"
        js_file.write_text("function hello() { return 'world'; \n")

        result = validate_javascript(js_file)

        assert result.valid is False
        assert any("brace" in e.lower() for e in result.errors)

    def test_javascript_unbalanced_brackets(self, temp_dir: Path) -> None:
        """Test unbalanced brackets detection."""
        js_file = temp_dir / "test.js"
        js_file.write_text("var arr = [1, 2, 3; \n")

        result = validate_javascript(js_file)

        assert result.valid is False
        assert any("bracket" in e.lower() for e in result.errors)

    def test_javascript_unbalanced_parentheses(self, temp_dir: Path) -> None:
        """Test unbalanced parentheses detection."""
        js_file = temp_dir / "test.js"
        js_file.write_text("console.log('hello'; \n")

        result = validate_javascript(js_file)

        assert result.valid is False
        assert any("parenthes" in e.lower() for e in result.errors)

    def test_javascript_unterminated_string(self, temp_dir: Path) -> None:
        """Test unterminated string detection."""
        js_file = temp_dir / "test.js"
        js_file.write_text('var str = "unterminated\n')

        result = validate_javascript(js_file)

        assert result.valid is False
        assert any("string" in e.lower() for e in result.errors)
