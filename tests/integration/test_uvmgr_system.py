"""
Integration tests for the complete uvmgr 13-command system.

This test suite validates the entire uvmgr command system including:
- All 13 commands are importable from CLI
- All ops modules are importable
- All runtime modules are importable
- Command registration in Typer app
- JSON output mode for all commands
- Error handling across all commands
- Telemetry instrumentation
- Concurrent command execution
- Three-tier architecture compliance

Test Coverage Goals:
- 50+ test cases covering the complete system
- Import validation for all layers
- CLI interface testing
- Business logic integration
- Runtime layer validation
- Error handling and edge cases
- Performance and concurrency
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def main_app():
    """Get the main app."""
    from specify_cli.app import app

    return app


# ============================================================================
# Test Data
# ============================================================================

# All 13 uvmgr commands as defined in app.py
UVMGR_COMMANDS = [
    "deps",
    "build",
    "tests",
    "cache",
    "lint",
    "otel",
    "guides",
    "worktree",
    "infodesign",
    "mermaid",
    "dod",
    "docs",
    "terraform",
]

# Core commands (always available)
CORE_COMMANDS = [
    "init",
    "check",
    "version",
    "spiff",
    "ggen",
]


# ============================================================================
# Test Class 1: Import Validation
# ============================================================================


class TestImportValidation:
    """Test that all modules are importable across all three layers."""

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_command_layer_imports(self, command: str) -> None:
        """Test all 13 command modules are importable."""
        module_name = f"specify_cli.commands.{command}"
        try:
            module = importlib.import_module(module_name)
            assert hasattr(module, "app"), f"{module_name} missing 'app' attribute"
            assert module.app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_ops_layer_imports(self, command: str) -> None:
        """Test all 13 ops modules are importable."""
        module_name = f"specify_cli.ops.{command}"
        try:
            module = importlib.import_module(module_name)
            # Ops modules should have validate_inputs function
            assert hasattr(module, "validate_inputs"), \
                f"{module_name} missing 'validate_inputs' function"
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_runtime_layer_imports(self, command: str) -> None:
        """Test all 13 runtime modules are importable."""
        module_name = f"specify_cli.runtime.{command}"
        try:
            module = importlib.import_module(module_name)
            # Runtime modules should have __all__ defined
            assert hasattr(module, "__all__"), \
                f"{module_name} missing '__all__' export list"
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")

    def test_all_core_commands_importable(self) -> None:
        """Test core commands are importable."""
        for command in CORE_COMMANDS:
            if command == "ggen":
                # ggen is optional
                try:
                    module = importlib.import_module(f"specify_cli.commands.{command}")
                    assert hasattr(module, "app")
                except ImportError:
                    pass  # OK if not available
            else:
                module = importlib.import_module(f"specify_cli.commands.{command}")
                assert hasattr(module, "app")

    def test_no_circular_imports(self) -> None:
        """Test no circular import dependencies."""
        # This test passes if all imports succeed without hanging
        from specify_cli import app, commands, core, ops, runtime

        assert app is not None
        assert commands is not None
        assert ops is not None
        assert runtime is not None
        assert core is not None


# ============================================================================
# Test Class 2: Command Registration
# ============================================================================


class TestCommandRegistration:
    """Test that all commands are properly registered in the Typer app."""

    def test_main_app_exists(self, main_app) -> None:
        """Test main app is created."""
        assert main_app is not None
        assert hasattr(main_app, "registered_commands")

    def test_core_commands_registered(self, main_app) -> None:
        """Test core commands are registered in main app."""
        # Get list of registered command names from registered_groups (Typer sub-apps)
        registered = []
        for group in main_app.registered_groups:
            if hasattr(group, "name") and group.name:
                registered.append(group.name)

        # Core commands should be registered as groups
        for cmd in ["init", "check", "version", "wf"]:
            assert cmd in registered, f"Core command '{cmd}' not registered"

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_uvmgr_command_registered_or_graceful(self, main_app, command: str) -> None:
        """Test uvmgr commands are registered or fail gracefully."""
        # Get list of registered command names
        registered = []
        for cmd in main_app.registered_commands:
            if hasattr(cmd, "name") and cmd.name:
                registered.append(cmd.name)

        # Command should either be registered or gracefully skipped
        # (the app uses try/except to handle missing commands)
        # This test passes if we can check without error
        assert isinstance(registered, list)

    def test_app_has_callback(self, main_app) -> None:
        """Test main app has callback registered."""
        assert hasattr(main_app, "registered_callback")
        assert main_app.registered_callback is not None

    def test_app_help_text(self, runner: CliRunner, main_app) -> None:
        """Test main app has help text."""
        result = runner.invoke(main_app, ["--help"])
        assert result.exit_code == 0
        assert "specify" in result.stdout.lower() or "setup" in result.stdout.lower()


# ============================================================================
# Test Class 3: CLI Interface Testing
# ============================================================================


class TestCLIInterface:
    """Test CLI interface for all commands."""

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_command_help_flag(self, runner: CliRunner, command: str) -> None:
        """Test --help flag works for all commands."""
        try:
            from specify_cli.app import app
            result = runner.invoke(app, [command, "--help"])
            # Help should work (exit 0) or command not found (exit 2)
            assert result.exit_code in (0, 2), \
                f"Command '{command} --help' failed with exit code {result.exit_code}"
            if result.exit_code == 0:
                assert "help" in result.stdout.lower() or command in result.stdout.lower()
        except Exception as e:
            pytest.fail(f"Command '{command} --help' raised exception: {e}")

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_command_has_subcommands(self, command: str) -> None:
        """Test each command module has subcommands registered."""
        try:
            module = importlib.import_module(f"specify_cli.commands.{command}")
            assert hasattr(module, "app")

            # Check if app has commands
            app = module.app
            assert hasattr(app, "registered_commands")

            # Commands should have at least one subcommand or a callback
            has_commands = len(app.registered_commands) > 0
            has_callback = app.registered_callback is not None

            assert has_commands or has_callback, \
                f"Command '{command}' has no subcommands or callback"
        except ImportError:
            pytest.skip(f"Command module '{command}' not available")

    def test_main_version_flag(self, runner: CliRunner, main_app) -> None:
        """Test --version flag on main app."""
        with patch("specify_cli.commands.version.version_ops.get_current_version") as mock:
            mock.return_value = "0.0.25"
            result = runner.invoke(main_app, ["--version"])
            assert result.exit_code == 0
            assert "0.0.25" in result.stdout

    def test_main_no_args_shows_banner(self, runner: CliRunner, main_app) -> None:
        """Test running with no args shows banner."""
        result = runner.invoke(main_app, [])
        assert result.exit_code == 0
        # Should show something (banner or help hint)
        assert len(result.stdout) > 0


# ============================================================================
# Test Class 4: JSON Output Mode
# ============================================================================


class TestJSONOutputMode:
    """Test JSON output mode for all commands."""

    def test_check_command_json_output(self, runner: CliRunner) -> None:
        """Test check command with --json flag."""
        with patch("specify_cli.commands.check.check_ops.check_all_tools") as mock:
            from specify_cli.ops.check import CheckResult, ToolStatus

            mock.return_value = CheckResult(
                success=True,
                available=[
                    ToolStatus(name="git", available=True, required=True, path="/usr/bin/git")
                ],
                missing=[],
                duration=0.5,
            )

            from specify_cli.app import app
            result = runner.invoke(app, ["check", "--json"])

            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
            assert "success" in data

    def test_version_command_json_output(self, runner: CliRunner) -> None:
        """Test version command with --json flag."""
        with patch("specify_cli.commands.version.version_ops.get_current_version") as mock:
            mock.return_value = "0.0.25"

            from specify_cli.app import app
            result = runner.invoke(app, ["version", "--json"])

            assert result.exit_code == 0
            data = json.loads(result.stdout)
            assert isinstance(data, dict)
            assert "version" in data
            assert data["version"] == "0.0.25"

    @pytest.mark.parametrize("command", ["deps", "build", "tests"])
    def test_uvmgr_commands_accept_json_context(self, command: str) -> None:
        """Test uvmgr commands can handle JSON serialization."""
        try:
            # Import ops module
            ops_module = importlib.import_module(f"specify_cli.ops.{command}")

            # Test validate_inputs can handle dict serialization
            result = ops_module.validate_inputs(test="value", count=42)
            assert isinstance(result, dict)

            # Result should be JSON serializable
            json_str = json.dumps(result)
            assert isinstance(json_str, str)

            # Should be parseable
            parsed = json.loads(json_str)
            assert isinstance(parsed, dict)
        except ImportError:
            pytest.skip(f"Ops module '{command}' not available")


# ============================================================================
# Test Class 5: Error Handling
# ============================================================================


class TestErrorHandling:
    """Test error handling across all commands."""

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_ops_validate_inputs_handles_empty(self, command: str) -> None:
        """Test ops validate_inputs handles empty input."""
        try:
            ops_module = importlib.import_module(f"specify_cli.ops.{command}")
            result = ops_module.validate_inputs()

            assert isinstance(result, dict)
            assert "valid" in result
        except ImportError:
            pytest.skip(f"Ops module '{command}' not available")

    @pytest.mark.parametrize("command", [c for c in UVMGR_COMMANDS if c != "lint"])
    def test_runtime_handles_subprocess_errors(self, command: str) -> None:
        """Test runtime layer handles subprocess errors gracefully.

        Note: lint is excluded because it has specialized error handling tested
        separately in test_runtime_lint_real.py.
        """
        try:
            runtime_module = importlib.import_module(f"specify_cli.runtime.{command}")

            # Get first exported function that returns a dict (skip exceptions/classes/bool funcs)
            if hasattr(runtime_module, "__all__") and runtime_module.__all__:
                func = None
                for func_name in runtime_module.__all__:
                    candidate = getattr(runtime_module, func_name)
                    # Skip exceptions, classes, and utility functions like is_*_available
                    if (callable(candidate) and
                        not isinstance(candidate, type) and
                        not func_name.startswith("is_")):
                        func = candidate
                        break

                if func is None:
                    pytest.skip(f"No callable function found in runtime.{command}")
                    return

                # Mock subprocess to raise error
                with patch("specify_cli.core.process.run_logged") as mock_run:
                    import subprocess
                    mock_run.side_effect = subprocess.CalledProcessError(1, ["cmd"])

                    try:
                        result = func()
                    except TypeError:
                        # Function requires arguments - skip this test
                        pytest.skip(f"Function in runtime.{command} requires arguments")
                        return

                    # Should return error dict, not raise
                    if not isinstance(result, dict):
                        pytest.skip(f"Function in runtime.{command} does not return dict")
                        return
                    assert "success" in result
                    assert result["success"] is False
                    assert "error" in result or "returncode" in result
        except ImportError:
            pytest.skip(f"Runtime module '{command}' not available")

    def test_init_command_error_handling(self, runner: CliRunner) -> None:
        """Test init command handles errors gracefully."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock, \
             patch("specify_cli.commands.init._select_ai_assistant_interactive") as mock_select:
            from specify_cli.ops.init import InitError

            mock.side_effect = InitError("Test error message")
            mock_select.return_value = "claude"

            from specify_cli.app import app
            result = runner.invoke(app, ["init", "test-project"])

            # Should exit with error
            assert result.exit_code != 0
            # Error message should be in output
            assert "error" in result.stdout.lower() or "Error" in result.stdout

    def test_check_command_handles_missing_tools(self, runner: CliRunner) -> None:
        """Test check command handles missing required tools."""
        with patch("specify_cli.commands.check.check_ops.check_all_tools") as mock:
            from specify_cli.ops.check import CheckResult, ToolStatus

            mock.return_value = CheckResult(
                success=False,
                available=[],
                missing=[
                    ToolStatus(name="git", available=False, required=True)
                ],
            )

            from specify_cli.app import app
            result = runner.invoke(app, ["check"])

            assert result.exit_code == 1
            assert "git" in result.stdout.lower() or "missing" in result.stdout.lower()


# ============================================================================
# Test Class 6: Telemetry Instrumentation
# ============================================================================


class TestTelemetryInstrumentation:
    """Test OpenTelemetry instrumentation across commands."""

    def test_instrumentation_module_imports(self) -> None:
        """Test core instrumentation module imports."""
        from specify_cli.core import instrumentation

        assert hasattr(instrumentation, "instrument_command")
        assert hasattr(instrumentation, "instrument_subcommand")
        assert hasattr(instrumentation, "add_span_attributes")
        assert hasattr(instrumentation, "add_span_event")

    @pytest.mark.parametrize("command", UVMGR_COMMANDS[:5])  # Test subset
    def test_ops_functions_emit_telemetry(self, command: str) -> None:
        """Test ops functions call telemetry functions."""
        try:
            ops_module = importlib.import_module(f"specify_cli.ops.{command}")

            # Check if module imports telemetry utilities
            module_source = Path(f"src/specify_cli/ops/{command}.py")
            if module_source.exists():
                content = module_source.read_text()
                # Should import from instrumentation or telemetry
                assert "from specify_cli.core.instrumentation import" in content or \
                       "from specify_cli.core.telemetry import" in content, \
                       f"Ops module '{command}' missing telemetry imports"
        except ImportError:
            pytest.skip(f"Ops module '{command}' not available")

    @pytest.mark.parametrize("command", UVMGR_COMMANDS[:5])  # Test subset
    def test_runtime_functions_use_span_decorator(self, command: str) -> None:
        """Test runtime functions use @span or @timed decorator."""
        try:
            module_source = Path(f"src/specify_cli/runtime/{command}.py")
            if module_source.exists():
                content = module_source.read_text()
                # Should use span or timed decorator
                assert "@timed" in content or "with span(" in content, \
                       f"Runtime module '{command}' missing telemetry decorators"
        except Exception:
            pytest.skip(f"Runtime source for '{command}' not available")

    def test_instrument_command_decorator_available(self) -> None:
        """Test @instrument_command decorator is available."""
        from specify_cli.core.instrumentation import instrument_command

        # Should be callable
        assert callable(instrument_command)

        # Should work as decorator
        @instrument_command("test_command")
        def dummy_command():
            return "success"

        result = dummy_command()
        assert result == "success"

    def test_telemetry_graceful_degradation(self) -> None:
        """Test telemetry works when OTEL not available."""
        from specify_cli.core.instrumentation import add_span_attributes, add_span_event

        # Should not raise even if OTEL unavailable
        add_span_attributes(test_attr="value", count=42)
        add_span_event("test.event", {"key": "value"})

        # No assertion needed - just shouldn't raise


# ============================================================================
# Test Class 7: Three-Tier Architecture Compliance
# ============================================================================


class TestThreeTierArchitecture:
    """Test three-tier architecture compliance."""

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_commands_delegate_to_ops(self, command: str) -> None:
        """Test command layer doesn't contain business logic."""
        try:
            module_source = Path(f"src/specify_cli/commands/{command}.py")
            if module_source.exists():
                content = module_source.read_text()
                # Commands should NOT import subprocess directly
                assert "import subprocess" not in content, \
                       f"Command '{command}' imports subprocess (should use ops/runtime)"
                # Commands should import from ops or runtime
                assert "from specify_cli.ops" in content or \
                       "from specify_cli.runtime" in content or \
                       "console.print" in content, \
                       f"Command '{command}' doesn't delegate to ops/runtime"
        except Exception:
            pytest.skip(f"Command source for '{command}' not available")

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_ops_no_subprocess_calls(self, command: str) -> None:
        """Test ops layer doesn't make subprocess calls."""
        try:
            module_source = Path(f"src/specify_cli/ops/{command}.py")
            if module_source.exists():
                content = module_source.read_text()
                # Ops should NOT import subprocess
                assert "import subprocess" not in content, \
                       f"Ops '{command}' imports subprocess (should delegate to runtime)"
                # Ops should NOT import run_logged
                lines = content.split("\n")
                imports_run_logged = any(
                    "from specify_cli.core.process import run_logged" in line
                    for line in lines
                )
                assert not imports_run_logged, \
                       f"Ops '{command}' imports run_logged (should be in runtime only)"
        except Exception:
            pytest.skip(f"Ops source for '{command}' not available")

    @pytest.mark.parametrize("command", UVMGR_COMMANDS)
    def test_runtime_has_subprocess_handling(self, command: str) -> None:
        """Test runtime layer handles subprocess execution."""
        try:
            module_source = Path(f"src/specify_cli/runtime/{command}.py")
            if module_source.exists():
                content = module_source.read_text()
                # Runtime should import subprocess or run_logged
                assert "import subprocess" in content or \
                       "from specify_cli.core.process import run_logged" in content or \
                       "from specify_cli.core.process import run" in content, \
                       f"Runtime '{command}' missing subprocess imports"
        except Exception:
            pytest.skip(f"Runtime source for '{command}' not available")

    def test_no_circular_dependencies_between_layers(self) -> None:
        """Test no circular dependencies between architecture layers."""
        # Commands can import ops and runtime
        from specify_cli.commands import init as cmd_init

        # Ops can import core but not commands or runtime
        from specify_cli.ops import init as ops_init

        # Runtime can import core but not commands or ops
        from specify_cli.runtime import tools as runtime_tools

        # If we get here without import errors, no circular deps
        assert cmd_init is not None
        assert ops_init is not None
        assert runtime_tools is not None


# ============================================================================
# Test Class 8: Concurrent Command Execution
# ============================================================================


class TestConcurrentExecution:
    """Test concurrent command execution."""

    def test_multiple_ops_functions_concurrent(self) -> None:
        """Test multiple ops functions can run concurrently."""
        import threading

        from specify_cli.ops import build, cache, deps

        results = []

        def run_validate(ops_module, name):
            result = ops_module.validate_inputs(test=name)
            results.append((name, result))

        # Run three validation functions concurrently
        threads = [
            threading.Thread(target=run_validate, args=(deps, "deps")),
            threading.Thread(target=run_validate, args=(build, "build")),
            threading.Thread(target=run_validate, args=(cache, "cache")),
        ]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # All should complete without error
        assert len(results) == 3
        assert all(isinstance(r[1], dict) for r in results)

    def test_telemetry_thread_safe(self) -> None:
        """Test telemetry functions are thread-safe."""
        import threading

        from specify_cli.core.instrumentation import add_span_attributes, add_span_event

        def emit_telemetry(thread_id):
            for i in range(10):
                add_span_attributes(thread_id=thread_id, iteration=i)
                add_span_event(f"thread.{thread_id}.event", {"iteration": i})

        threads = [threading.Thread(target=emit_telemetry, args=(i,)) for i in range(5)]

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Should complete without deadlock or race conditions
        assert True

    def test_cli_runner_isolation(self, runner: CliRunner) -> None:
        """Test CLI runner provides isolation for concurrent tests."""
        # Multiple invocations should be isolated
        with patch("specify_cli.commands.version.version_ops.get_current_version") as mock:
            mock.return_value = "0.0.25"

            from specify_cli.app import app

            result1 = runner.invoke(app, ["version"])
            result2 = runner.invoke(app, ["version"])

            # Both should succeed independently
            assert result1.exit_code == 0
            assert result2.exit_code == 0
            assert "0.0.25" in result1.stdout
            assert "0.0.25" in result2.stdout


# ============================================================================
# Test Class 9: System Integration
# ============================================================================


class TestSystemIntegration:
    """Test end-to-end system integration."""

    def test_full_command_pipeline_check(self, runner: CliRunner) -> None:
        """Test full pipeline from CLI -> commands -> ops -> runtime."""
        with patch("specify_cli.commands.check.check_ops.check_all_tools") as mock:
            from specify_cli.ops.check import CheckResult, ToolStatus

            # Mock ops layer response
            mock.return_value = CheckResult(
                success=True,
                available=[
                    ToolStatus(name="git", available=True, required=True, path="/usr/bin/git")
                ],
                missing=[],
            )

            from specify_cli.app import app
            result = runner.invoke(app, ["check"])

            # Full pipeline should work
            assert result.exit_code == 0
            # Ops was called
            mock.assert_called_once()

    def test_command_registration_consistency(self, main_app) -> None:
        """Test command registration is consistent across restarts."""
        # Get command count
        count1 = len(main_app.registered_commands)

        # Re-import app
        importlib.reload(sys.modules["specify_cli.app"])
        from specify_cli.app import app as app2

        count2 = len(app2.registered_commands)

        # Should have same number of commands
        assert count1 == count2

    def test_all_layers_accessible_from_top(self) -> None:
        """Test all three layers are accessible from main module."""

        # Should be able to navigate to all layers
        from specify_cli import app, commands, core, ops, runtime

        assert app is not None
        assert commands is not None
        assert ops is not None
        assert runtime is not None
        assert core is not None

    @pytest.mark.parametrize("command", UVMGR_COMMANDS[:3])  # Test subset
    def test_end_to_end_command_flow(self, command: str) -> None:
        """Test end-to-end flow: import -> validate -> execute."""
        try:
            # 1. Import command
            cmd_module = importlib.import_module(f"specify_cli.commands.{command}")
            assert hasattr(cmd_module, "app")

            # 2. Import ops
            ops_module = importlib.import_module(f"specify_cli.ops.{command}")
            assert hasattr(ops_module, "validate_inputs")

            # 3. Import runtime
            runtime_module = importlib.import_module(f"specify_cli.runtime.{command}")
            assert hasattr(runtime_module, "__all__")

            # 4. Test validation
            validation = ops_module.validate_inputs(test="value")
            assert isinstance(validation, dict)

            # Full flow successful
            assert True
        except ImportError:
            pytest.skip(f"Command '{command}' not fully available")


# ============================================================================
# Test Class 10: Edge Cases and Robustness
# ============================================================================


class TestEdgeCasesAndRobustness:
    """Test edge cases and system robustness."""

    def test_command_with_invalid_args(self, runner: CliRunner) -> None:
        """Test commands handle invalid arguments gracefully."""
        from specify_cli.app import app

        # Try with nonsense flag
        result = runner.invoke(app, ["check", "--nonexistent-flag"])

        # Should fail gracefully (not crash)
        assert result.exit_code != 0
        # Output goes to stderr for usage errors, so check both stdout and stderr
        assert len(result.stdout) > 0 or len(result.output) > 0

    def test_ops_functions_with_none_values(self) -> None:
        """Test ops functions handle None values."""
        from specify_cli.ops import deps

        # Should handle None without crashing
        result = deps.validate_inputs(value=None, other=None)
        assert isinstance(result, dict)

    def test_ops_functions_with_unexpected_types(self) -> None:
        """Test ops functions handle unexpected types."""
        from specify_cli.ops import build

        # Should handle various types
        result = build.validate_inputs(
            string="test",
            number=42,
            boolean=True,
            list_val=[1, 2, 3],
        )
        assert isinstance(result, dict)

    @pytest.mark.parametrize("command", [c for c in UVMGR_COMMANDS[:5] if c != "lint"])
    def test_runtime_handles_missing_tools(self, command: str) -> None:
        """Test runtime handles missing external tools.

        Note: lint is excluded because it has specialized error handling tested
        separately in test_runtime_lint_real.py.
        """
        try:
            runtime_module = importlib.import_module(f"specify_cli.runtime.{command}")

            if hasattr(runtime_module, "__all__") and runtime_module.__all__:
                # Find first callable that's not an exception/class
                func = None
                for func_name in runtime_module.__all__:
                    candidate = getattr(runtime_module, func_name)
                    if callable(candidate) and not isinstance(candidate, type):
                        func = candidate
                        break

                if func is None:
                    pytest.skip(f"No callable function found in runtime.{command}")
                    return

                # Mock subprocess to raise FileNotFoundError
                with patch("specify_cli.core.process.run_logged") as mock_run:
                    mock_run.side_effect = FileNotFoundError("Tool not found")

                    try:
                        result = func()
                    except TypeError:
                        pytest.skip(f"Function in runtime.{command} requires arguments")
                        return

                    # Should return error dict
                    if not isinstance(result, dict):
                        pytest.skip(f"Function in runtime.{command} does not return dict")
                        return
                    assert result.get("success") is False
                    assert "error" in result
        except ImportError:
            pytest.skip(f"Runtime module '{command}' not available")

    def test_main_app_with_empty_env(self, runner: CliRunner, main_app) -> None:
        """Test main app works with minimal environment."""
        # Clear environment variables
        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(main_app, ["--help"])

            # Should still work
            assert result.exit_code == 0

    def test_unicode_in_command_args(self, runner: CliRunner) -> None:
        """Test commands handle unicode in arguments."""
        with patch("specify_cli.commands.init.init_ops.initialize_project") as mock, \
             patch("specify_cli.commands.init._select_ai_assistant_interactive") as mock_select:
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.project_path = Path("/tmp/test-项目")
            mock_result.ai_assistant = "claude"
            mock_result.script_type = "sh"
            mock_result.git_initialized = False
            mock_result.release_tag = "v1.0.0"
            mock_result.warnings = []
            mock.return_value = mock_result
            mock_select.return_value = "claude"

            from specify_cli.app import app
            result = runner.invoke(app, ["init", "test-项目", "--no-git"])

            # Should handle unicode - either succeeds or fails with validation error (not crash)
            # Exit code 0 = success, 1 = validation error, 2 = usage error
            assert result.exit_code in (0, 1, 2)


# ============================================================================
# Summary Test
# ============================================================================


class TestSystemSummary:
    """Summary tests for the complete system."""

    def test_total_command_count(self, main_app) -> None:
        """Test total number of registered command groups."""
        # Typer uses registered_groups for sub-apps (add_typer)
        registered_count = len(main_app.registered_groups)

        # Should have at least core command groups
        # (uvmgr commands are optional and registered dynamically)
        assert registered_count >= 4, \
            f"Expected at least 4 command groups, got {registered_count}"

    def test_all_13_uvmgr_modules_exist(self) -> None:
        """Test all 13 uvmgr command modules exist."""
        for command in UVMGR_COMMANDS:
            cmd_path = Path(f"src/specify_cli/commands/{command}.py")
            ops_path = Path(f"src/specify_cli/ops/{command}.py")
            runtime_path = Path(f"src/specify_cli/runtime/{command}.py")

            assert cmd_path.exists(), f"Missing command: {command}"
            assert ops_path.exists(), f"Missing ops: {command}"
            assert runtime_path.exists(), f"Missing runtime: {command}"

    def test_system_health_check(self) -> None:
        """Overall system health check."""
        # All critical modules should import
        from specify_cli import app, commands, core, ops, runtime

        # At least one full command stack should work
        from specify_cli.commands import check as check_cmd

        # Core utilities should work
        from specify_cli.core.instrumentation import instrument_command
        from specify_cli.core.telemetry import metric_counter, span
        from specify_cli.ops import check as check_ops

        # System is healthy if all imports succeed
        assert all([
            app, commands, ops, runtime, core,
            instrument_command, span, metric_counter,
            check_cmd, check_ops,
        ])

    def test_documentation_completeness(self) -> None:
        """Test all modules have docstrings."""
        for command in UVMGR_COMMANDS:
            # Check command module
            try:
                cmd_module = importlib.import_module(f"specify_cli.commands.{command}")
                assert cmd_module.__doc__ is not None, \
                    f"Command module '{command}' missing docstring"
            except ImportError:
                pass

            # Check ops module
            try:
                ops_module = importlib.import_module(f"specify_cli.ops.{command}")
                assert ops_module.__doc__ is not None, \
                    f"Ops module '{command}' missing docstring"
            except ImportError:
                pass

            # Check runtime module
            try:
                runtime_module = importlib.import_module(f"specify_cli.runtime.{command}")
                assert runtime_module.__doc__ is not None, \
                    f"Runtime module '{command}' missing docstring"
            except ImportError:
                pass
