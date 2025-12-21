"""
Unit tests for specify_cli.ops.init module.

Tests cover project initialization business logic with mocked runtime calls.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.ops.init import (
    DEFAULT_AI_ASSISTANT,
    DEFAULT_SCRIPT_TYPE,
    SUPPORTED_AI_ASSISTANTS,
    InitError,
    InitResult,
    determine_ai_assistant,
    initialize_project,
    validate_project_name,
)


class TestValidateProjectName:
    """Tests for validate_project_name() function."""

    def test_valid_simple_name(self) -> None:
        """Test valid simple project name."""
        is_valid, error = validate_project_name("myproject")
        assert is_valid is True
        assert error is None

    def test_valid_with_hyphen(self) -> None:
        """Test valid name with hyphen."""
        is_valid, error = validate_project_name("my-project")
        assert is_valid is True
        assert error is None

    def test_valid_with_underscore(self) -> None:
        """Test valid name with underscore."""
        is_valid, error = validate_project_name("my_project")
        assert is_valid is True
        assert error is None

    def test_valid_with_numbers(self) -> None:
        """Test valid name with numbers."""
        is_valid, error = validate_project_name("project123")
        assert is_valid is True
        assert error is None

    def test_invalid_empty_name(self) -> None:
        """Test empty name is invalid."""
        is_valid, error = validate_project_name("")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_invalid_starts_with_number(self) -> None:
        """Test name starting with number is invalid."""
        is_valid, error = validate_project_name("123project")
        assert is_valid is False
        assert "Must start with a letter" in error

    def test_invalid_starts_with_hyphen(self) -> None:
        """Test name starting with hyphen is invalid."""
        is_valid, error = validate_project_name("-project")
        assert is_valid is False
        assert "Must start with a letter" in error

    def test_invalid_special_characters(self) -> None:
        """Test name with special characters is invalid."""
        is_valid, error = validate_project_name("my@project")
        assert is_valid is False
        assert "Invalid project name" in error

    def test_invalid_reserved_name(self) -> None:
        """Test reserved names are invalid."""
        # These are caught by pattern regex (don't start with letter)
        for reserved in [".", ".."]:
            is_valid, error = validate_project_name(reserved)
            assert is_valid is False
            assert "Invalid project name" in error or "reserved" in error.lower()

        # These are caught by reserved name check
        for reserved in ["con", "prn", "aux", "nul"]:
            is_valid, error = validate_project_name(reserved)
            assert is_valid is False
            assert "reserved name" in error.lower()

    def test_valid_uppercase(self) -> None:
        """Test uppercase names are valid."""
        is_valid, error = validate_project_name("MyProject")
        assert is_valid is True
        assert error is None


class TestDetermineAiAssistant:
    """Tests for determine_ai_assistant() function."""

    def test_cli_value_takes_precedence(self) -> None:
        """Test CLI value is used when provided."""
        result = determine_ai_assistant(cli_value="cursor")
        assert result == "cursor"

    def test_env_value_when_no_cli(self) -> None:
        """Test environment variable is used when no CLI value."""
        with patch.dict("os.environ", {"SPECIFY_DEFAULT_AI": "copilot"}):
            result = determine_ai_assistant()
            assert result == "copilot"

    def test_default_when_nothing_set(self) -> None:
        """Test default is used when nothing specified."""
        with patch.dict("os.environ", {}, clear=True):
            result = determine_ai_assistant()
            assert result == DEFAULT_AI_ASSISTANT

    def test_invalid_cli_value_raises(self) -> None:
        """Test invalid CLI value raises InitError."""
        with pytest.raises(InitError) as exc_info:
            determine_ai_assistant(cli_value="invalid")

        assert "Unsupported AI assistant" in str(exc_info.value)
        assert exc_info.value.suggestions

    def test_all_supported_assistants(self) -> None:
        """Test all supported assistants are accepted."""
        for assistant in SUPPORTED_AI_ASSISTANTS:
            result = determine_ai_assistant(cli_value=assistant)
            assert result == assistant


class TestInitResult:
    """Tests for InitResult dataclass."""

    def test_default_values(self) -> None:
        """Test default values are set correctly."""
        result = InitResult(success=False)

        assert result.success is False
        assert result.project_path is None
        assert result.ai_assistant == ""
        assert result.script_type == ""
        assert result.git_initialized is False
        assert result.release_tag == ""
        assert result.files_extracted == 0
        assert result.duration == 0.0
        assert result.errors == []
        assert result.warnings == []

    def test_success_result(self) -> None:
        """Test successful result."""
        result = InitResult(
            success=True,
            project_path=Path("/test/project"),
            ai_assistant="claude",
            script_type="sh",
            git_initialized=True,
            release_tag="v1.0.0",
            duration=1.5,
        )

        assert result.success is True
        assert result.project_path == Path("/test/project")
        assert result.ai_assistant == "claude"


class TestInitError:
    """Tests for InitError exception."""

    def test_basic_error(self) -> None:
        """Test basic error creation."""
        error = InitError("Something went wrong")

        assert str(error) == "Something went wrong"
        assert error.recoverable is False
        assert error.suggestions == []

    def test_error_with_suggestions(self) -> None:
        """Test error with suggestions."""
        error = InitError(
            "Invalid input",
            suggestions=["Try option A", "Try option B"],
        )

        assert error.suggestions == ["Try option A", "Try option B"]

    def test_recoverable_error(self) -> None:
        """Test recoverable error."""
        error = InitError("Temporary failure", recoverable=True)

        assert error.recoverable is True


class TestInitializeProject:
    """Tests for initialize_project() function."""

    @pytest.fixture
    def mock_runtime(self) -> MagicMock:
        """Create mock runtime layer."""
        with patch("specify_cli.ops.init.github") as mock_github, patch(
            "specify_cli.ops.init.git"
        ) as mock_git, patch("specify_cli.ops.init.template") as mock_template:
            mock_github.fetch_latest_release.return_value = {
                "tag_name": "v1.0.0",
                "assets": [
                    {"name": "claude-sh.zip", "browser_download_url": "https://example.com/asset.zip"}
                ],
            }
            mock_github.find_matching_asset.return_value = {
                "name": "claude-sh.zip",
                "browser_download_url": "https://example.com/asset.zip",
            }
            mock_github.download_asset.return_value = Path("/tmp/template.zip")
            mock_template.ensure_executable_scripts.return_value = (3, [])

            yield {
                "github": mock_github,
                "git": mock_git,
                "template": mock_template,
            }

    def test_initialize_with_name(
        self, mock_runtime: dict[str, MagicMock], tmp_path: Path
    ) -> None:
        """Test initialization with project name."""
        with patch("specify_cli.ops.init.Path") as mock_path_class:
            mock_cwd = MagicMock()
            mock_cwd.__truediv__ = MagicMock(return_value=tmp_path / "test-project")
            mock_path_class.cwd.return_value = mock_cwd

            # Mock the exists check
            project_path = tmp_path / "test-project"
            with patch.object(Path, "exists", return_value=False):
                result = initialize_project(
                    name="test-project",
                    ai_assistant="claude",
                    project_path=project_path,
                )

            assert result.success is True
            assert result.ai_assistant == "claude"
            assert result.script_type == DEFAULT_SCRIPT_TYPE

    def test_initialize_here_flag(
        self, mock_runtime: dict[str, MagicMock], tmp_path: Path
    ) -> None:
        """Test initialization with --here flag."""
        import os

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            result = initialize_project(here=True)

            assert result.success is True
            assert result.project_path == tmp_path
        finally:
            os.chdir(original_cwd)

    def test_initialize_no_git(
        self, mock_runtime: dict[str, MagicMock], tmp_path: Path
    ) -> None:
        """Test initialization with --no-git flag."""
        result = initialize_project(
            name="test-project",
            no_git=True,
            project_path=tmp_path / "test-project",
        )

        assert result.success is True
        assert result.git_initialized is False
        mock_runtime["git"].init_repo.assert_not_called()

    def test_initialize_with_git(
        self, mock_runtime: dict[str, MagicMock], tmp_path: Path
    ) -> None:
        """Test initialization with git enabled."""
        result = initialize_project(
            name="test-project",
            project_path=tmp_path / "test-project",
        )

        assert result.success is True
        assert result.git_initialized is True
        mock_runtime["git"].init_repo.assert_called_once()

    def test_initialize_directory_exists(
        self, mock_runtime: dict[str, MagicMock], tmp_path: Path
    ) -> None:
        """Test error when directory already exists."""
        existing_dir = tmp_path / "existing-project"
        existing_dir.mkdir()

        with pytest.raises(InitError) as exc_info:
            initialize_project(
                name="existing-project",
                project_path=existing_dir,
            )

        assert "already exists" in str(exc_info.value)

    def test_initialize_no_name_no_here(self, mock_runtime: dict[str, MagicMock]) -> None:
        """Test error when neither name nor --here is provided."""
        with pytest.raises(InitError) as exc_info:
            initialize_project()

        assert "name or --here" in str(exc_info.value)

    def test_initialize_no_matching_asset(
        self, mock_runtime: dict[str, MagicMock], tmp_path: Path
    ) -> None:
        """Test error when no matching template found."""
        mock_runtime["github"].find_matching_asset.return_value = None

        with pytest.raises(InitError) as exc_info:
            initialize_project(
                name="test-project",
                ai_assistant="claude",
                project_path=tmp_path / "test-project",
            )

        assert "No template found" in str(exc_info.value)

    def test_initialize_git_failure_warning(
        self, mock_runtime: dict[str, MagicMock], tmp_path: Path
    ) -> None:
        """Test git failure is added as warning, not error."""
        mock_runtime["git"].init_repo.side_effect = Exception("Git failed")

        result = initialize_project(
            name="test-project",
            project_path=tmp_path / "test-project",
        )

        # Should still succeed
        assert result.success is True
        assert result.git_initialized is False
        assert any("Git initialization failed" in w for w in result.warnings)


class TestInitializeProjectIntegration:
    """Integration-style tests with more realistic mocking."""

    def test_full_initialization_flow(self, tmp_path: Path) -> None:
        """Test complete initialization flow."""
        with patch("specify_cli.ops.init.github") as mock_github, patch(
            "specify_cli.ops.init.git"
        ) as mock_git, patch("specify_cli.ops.init.template") as mock_template, patch(
            "tempfile.TemporaryDirectory"
        ) as mock_tempdir:
            # Setup mocks
            mock_github.fetch_latest_release.return_value = {
                "tag_name": "v1.0.0",
                "assets": [{"name": "claude-sh.zip"}],
            }
            mock_github.find_matching_asset.return_value = {
                "name": "claude-sh.zip",
                "browser_download_url": "https://example.com/asset.zip",
            }
            mock_github.download_asset.return_value = Path("/tmp/template.zip")
            mock_template.ensure_executable_scripts.return_value = (3, [])

            mock_tempdir_instance = MagicMock()
            mock_tempdir_instance.__enter__ = MagicMock(return_value="/tmp/test")
            mock_tempdir_instance.__exit__ = MagicMock(return_value=False)
            mock_tempdir.return_value = mock_tempdir_instance

            # Run initialization
            result = initialize_project(
                name="my-project",
                ai_assistant="claude",
                script_type="sh",
                project_path=tmp_path / "my-project",
            )

            # Verify flow
            assert result.success is True
            assert result.release_tag == "v1.0.0"
            assert result.ai_assistant == "claude"
            assert result.script_type == "sh"
            assert result.duration > 0

            # Verify runtime calls
            mock_github.fetch_latest_release.assert_called_once()
            mock_github.find_matching_asset.assert_called_once()
            mock_github.download_asset.assert_called_once()
            mock_template.extract_template.assert_called_once()
            mock_git.init_repo.assert_called_once()
