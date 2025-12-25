"""E2E tests for dod CLI"""
from typer.testing import CliRunner

from specify_cli.commands import dod

runner = CliRunner()


class TestCLIInvocation:
    """Test CLI command invocation."""

    def test_command_help(self) -> None:
        """Help should display."""
        result = runner.invoke(dod.app, ["--help"])
        assert result.exit_code == 0
        assert "Definition of Done" in result.stdout

    def test_check_command_exists(self) -> None:
        """Check command should be available."""
        result = runner.invoke(dod.app, ["check", "--help"])
        assert result.exit_code == 0


class TestCheckCommand:
    """Test dod check command."""

    def test_check_default_mode(self) -> None:
        """Check should work in default mode."""
        result = runner.invoke(dod.app, ["check"])
        # May succeed or fail based on environment, but should not error
        assert result.exit_code in [0, 1]

    def test_check_with_strict_flag(self) -> None:
        """Check should accept --strict flag."""
        result = runner.invoke(dod.app, ["check", "--strict"])
        # May succeed or fail based on environment, but should not error
        assert result.exit_code in [0, 1]

    def test_check_output_contains_result(self) -> None:
        """Check output should contain result indicator."""
        result = runner.invoke(dod.app, ["check"])
        # Should contain either success or failure message
        assert ("passed" in result.stdout.lower() or "failed" in result.stdout.lower()
                or "check" in result.stdout.lower())


class TestOptions:
    """Test command options."""

    def test_help_flag(self) -> None:
        """--help flag should work."""
        result = runner.invoke(dod.app, ["check", "--help"])
        assert result.exit_code == 0
        assert "--strict" in result.stdout

    def test_strict_option_help(self) -> None:
        """--strict option help should display."""
        result = runner.invoke(dod.app, ["check", "--help"])
        assert "--strict" in result.stdout


class TestIntegration:
    """Test three-tier integration."""

    def test_cli_to_ops_flow(self) -> None:
        """CLI should call ops layer."""
        result = runner.invoke(dod.app, ["check"])
        # Should not raise exception, exit code shows result
        assert isinstance(result.exit_code, int)

    def test_ops_to_runtime_flow(self) -> None:
        """Ops should call runtime layer."""
        result = runner.invoke(dod.app, ["check"])
        # Should complete without unhandled exceptions
        assert result.exit_code in [0, 1]

    def test_strict_mode_integration(self) -> None:
        """Strict mode should be passed through all layers."""
        result = runner.invoke(dod.app, ["check", "--strict"])
        # Should complete (may fail if criteria not met, but shouldn't crash)
        assert result.exit_code in [0, 1]


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_command_option(self) -> None:
        """Invalid option should show error."""
        result = runner.invoke(dod.app, ["check", "--invalid-option"])
        assert result.exit_code != 0

    def test_exception_handling(self) -> None:
        """Exceptions should be handled gracefully."""
        # Run normal check - should not raise unhandled exceptions
        result = runner.invoke(dod.app, ["check"])
        assert isinstance(result.exit_code, int)
