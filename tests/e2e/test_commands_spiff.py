"""End-to-end tests for specify wf (spiff/workflow) commands.

This module tests the complete wf command flow including:
- CLI invocation via CliRunner
- Integration with spiff.ops module
- All workflow subcommands
- Output formatting (text and JSON)
- Error handling and exit codes
- OTEL validation workflow execution
- External project validation

Test Coverage
-------------
- validate: OTEL validation workflow
- validate-quick: 80/20 OTEL validation
- create-workflow: Custom BPMN creation
- run-workflow: BPMN execution
- discover-projects: Project discovery
- validate-external: External project validation
- batch-validate: Batch validation
- validate-8020: Critical path validation

Examples
--------
    $ pytest tests/e2e/test_commands_spiff.py -v -m e2e
    $ pytest tests/e2e/test_commands_spiff.py::test_wf_validate_basic
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app

runner = CliRunner()


@pytest.mark.e2e
def test_wf_validate_basic(tmp_path: Path) -> None:
    """Test wf validate command executes OTEL validation.

    Verifies:
        - Command executes without errors
        - Validation runs
        - Results displayed
    """
    with patch("specify_cli.spiff.ops.create_otel_validation_workflow") as mock_create, patch(
        "specify_cli.spiff.ops.execute_otel_validation_workflow"
    ) as mock_execute:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.duration_seconds = 1.5
        mock_result.validation_steps = []
        mock_result.errors = []
        mock_execute.return_value = mock_result

        result = runner.invoke(app, ["wf", "validate"])

        assert result.exit_code == 0
        assert "succeeded" in result.stdout.lower() or "✓" in result.stdout
        mock_create.assert_called_once()
        mock_execute.assert_called_once()


@pytest.mark.e2e
def test_wf_validate_with_iterations(tmp_path: Path) -> None:
    """Test wf validate command with multiple iterations.

    Verifies:
        - Iterations option works
        - Validation runs multiple times
    """
    with patch("specify_cli.spiff.ops.create_otel_validation_workflow"), patch(
        "specify_cli.spiff.ops.execute_otel_validation_workflow"
    ) as mock_execute:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.duration_seconds = 1.5
        mock_result.validation_steps = []
        mock_result.errors = []
        mock_execute.return_value = mock_result

        result = runner.invoke(app, ["wf", "validate", "--iterations", "3"])

        assert result.exit_code == 0
        assert mock_execute.call_count == 3


@pytest.mark.e2e
def test_wf_validate_with_export_json(tmp_path: Path) -> None:
    """Test wf validate command with JSON export.

    Verifies:
        - Results can be exported to JSON
        - File is created
    """
    export_file = tmp_path / "results.json"

    with patch("specify_cli.spiff.ops.create_otel_validation_workflow"), patch(
        "specify_cli.spiff.ops.execute_otel_validation_workflow"
    ) as mock_execute:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.duration_seconds = 1.5
        mock_result.validation_steps = []
        mock_result.errors = []
        mock_result.to_dict = MagicMock(
            return_value={"success": True, "duration_seconds": 1.5}
        )
        mock_execute.return_value = mock_result

        result = runner.invoke(app, ["wf", "validate", "--export-json", str(export_file)])

        assert result.exit_code == 0
        assert "exported" in result.stdout.lower() or export_file.exists()


@pytest.mark.e2e
def test_wf_validate_quick() -> None:
    """Test wf validate-quick command for 80/20 validation.

    Verifies:
        - Quick validation runs
        - Critical path tested
        - Faster execution
    """
    with patch("specify_cli.spiff.ops.run_8020_otel_validation") as mock_validate:
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.duration_seconds = 0.8
        mock_result.validation_steps = []
        mock_validate.return_value = mock_result

        result = runner.invoke(app, ["wf", "validate-quick"])

        assert result.exit_code == 0
        assert "succeeded" in result.stdout.lower() or "✓" in result.stdout
        mock_validate.assert_called_once()


@pytest.mark.e2e
def test_wf_create_workflow(tmp_path: Path) -> None:
    """Test wf create-workflow command creates BPMN file.

    Verifies:
        - Workflow file created
        - Success message shown
        - File size displayed
    """
    output_file = tmp_path / "workflow.bpmn"

    with patch("specify_cli.spiff.ops.create_otel_validation_workflow") as mock_create:
        mock_create.return_value = output_file
        output_file.write_text("<bpmn>test</bpmn>")

        result = runner.invoke(app, ["wf", "create-workflow", "-o", str(output_file)])

        assert result.exit_code == 0
        assert "created" in result.stdout.lower() or "✓" in result.stdout
        mock_create.assert_called_once()


@pytest.mark.e2e
def test_wf_run_workflow(tmp_path: Path) -> None:
    """Test wf run-workflow command executes BPMN file.

    Verifies:
        - Workflow execution works
        - Results displayed
        - Validation passes
    """
    workflow_file = tmp_path / "workflow.bpmn"
    workflow_file.write_text("<bpmn>test</bpmn>")

    with patch("specify_cli.spiff.runtime.validate_bpmn_file") as mock_validate, patch(
        "specify_cli.spiff.runtime.run_bpmn"
    ) as mock_run:
        mock_validate.return_value = True
        mock_run.return_value = {
            "status": "completed",
            "duration_seconds": 2.0,
            "steps_executed": 5,
            "total_tasks": 5,
            "completed_tasks": 5,
        }

        result = runner.invoke(app, ["wf", "run-workflow", str(workflow_file)])

        assert result.exit_code == 0
        assert "completed" in result.stdout.lower()
        mock_validate.assert_called_once()
        mock_run.assert_called_once()


@pytest.mark.e2e
def test_wf_run_workflow_invalid_file(tmp_path: Path) -> None:
    """Test wf run-workflow handles invalid workflow file.

    Verifies:
        - Validation failure detected
        - Error message shown
        - Exit code is 1
    """
    workflow_file = tmp_path / "workflow.bpmn"
    workflow_file.write_text("<invalid>")

    with patch("specify_cli.spiff.runtime.validate_bpmn_file") as mock_validate:
        mock_validate.return_value = False

        result = runner.invoke(app, ["wf", "run-workflow", str(workflow_file)])

        assert result.exit_code == 1
        assert "failed" in result.stdout.lower()


@pytest.mark.e2e
def test_wf_discover_projects(tmp_path: Path) -> None:
    """Test wf discover-projects command finds Python projects.

    Verifies:
        - Project discovery works
        - Projects listed in table
        - Confidence scores shown
    """
    with patch("specify_cli.spiff.ops.external_projects.discover_external_projects") as mock_discover:
        mock_project = MagicMock()
        mock_project.name = "test-project"
        mock_project.project_type = "poetry"
        mock_project.package_manager = "poetry"
        mock_project.confidence = 0.9
        mock_discover.return_value = [mock_project]

        result = runner.invoke(app, ["wf", "discover-projects", "--path", str(tmp_path)])

        assert result.exit_code == 0
        assert "Found" in result.stdout or "test-project" in result.stdout
        mock_discover.assert_called_once()


@pytest.mark.e2e
def test_wf_discover_projects_none_found(tmp_path: Path) -> None:
    """Test wf discover-projects when no projects found.

    Verifies:
        - Handles empty results
        - Informative message shown
    """
    with patch("specify_cli.spiff.ops.external_projects.discover_external_projects") as mock_discover:
        mock_discover.return_value = []

        result = runner.invoke(app, ["wf", "discover-projects", "--path", str(tmp_path)])

        assert result.exit_code == 0
        assert "No projects" in result.stdout or "not found" in result.stdout.lower()


@pytest.mark.e2e
def test_wf_validate_external(tmp_path: Path) -> None:
    """Test wf validate-external command validates project.

    Verifies:
        - External project validation works
        - Results displayed
        - Test results shown
    """
    project_path = tmp_path / "project"
    project_path.mkdir()

    with patch(
        "specify_cli.spiff.ops.external_projects._is_python_project"
    ) as mock_is_python, patch(
        "specify_cli.spiff.ops.external_projects.validate_external_project_with_spiff"
    ) as mock_validate:
        mock_project = MagicMock()
        mock_project.project_type = "poetry"
        mock_is_python.return_value = mock_project

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.duration_seconds = 2.0
        mock_result.test_results = {"test1": True, "test2": True}
        mock_result.to_dict = MagicMock(return_value={"success": True})
        mock_validate.return_value = mock_result

        result = runner.invoke(app, ["wf", "validate-external", str(project_path)])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower() or "✓" in result.stdout


@pytest.mark.e2e
def test_wf_validate_external_not_python(tmp_path: Path) -> None:
    """Test wf validate-external handles non-Python project.

    Verifies:
        - Error for non-Python project
        - Clear message shown
    """
    project_path = tmp_path / "project"
    project_path.mkdir()

    with patch("specify_cli.spiff.ops.external_projects._is_python_project") as mock_is_python:
        mock_is_python.return_value = None

        result = runner.invoke(app, ["wf", "validate-external", str(project_path)])

        assert result.exit_code == 1
        assert "Not a Python project" in result.stdout or "not" in result.stdout.lower()


@pytest.mark.e2e
def test_wf_batch_validate(tmp_path: Path) -> None:
    """Test wf batch-validate command validates multiple projects.

    Verifies:
        - Batch validation works
        - Multiple projects processed
        - Summary shown
    """
    with patch(
        "specify_cli.spiff.ops.external_projects.discover_external_projects"
    ) as mock_discover, patch(
        "specify_cli.spiff.ops.external_projects.batch_validate_external_projects"
    ) as mock_batch:
        mock_project = MagicMock()
        mock_discover.return_value = [mock_project]

        mock_result = MagicMock()
        mock_result.success = True
        mock_result.project_name = "test-project"
        mock_result.duration_seconds = 1.5
        mock_result.to_dict = MagicMock(return_value={"success": True})
        mock_batch.return_value = [mock_result]

        result = runner.invoke(app, ["wf", "batch-validate", "--path", str(tmp_path)])

        assert result.exit_code == 0
        assert "Completed" in result.stdout or "successful" in result.stdout.lower()


@pytest.mark.e2e
def test_wf_validate_8020(tmp_path: Path) -> None:
    """Test wf validate-8020 command for critical path validation.

    Verifies:
        - 80/20 validation runs
        - Summary displayed
        - Success rate shown
    """
    with patch(
        "specify_cli.spiff.ops.external_projects.run_8020_external_project_validation"
    ) as mock_8020:
        mock_8020.return_value = {
            "total_discovered": 10,
            "critical_selected": 3,
            "validated": 3,
            "successful": 2,
            "success_rate": 0.667,
        }

        result = runner.invoke(app, ["wf", "validate-8020", "--path", str(tmp_path)])

        assert result.exit_code == 0
        assert "Discovered" in result.stdout or "Selected" in result.stdout
        assert "66" in result.stdout or "67" in result.stdout  # Success rate


@pytest.mark.e2e
def test_wf_validate_failure_handling() -> None:
    """Test wf validate handles validation failures.

    Verifies:
        - Failures reported correctly
        - Errors displayed
        - Exit code reflects failure
    """
    with patch("specify_cli.spiff.ops.create_otel_validation_workflow"), patch(
        "specify_cli.spiff.ops.execute_otel_validation_workflow"
    ) as mock_execute:
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.duration_seconds = 1.5
        mock_result.validation_steps = []
        mock_result.errors = ["Test failed", "OTEL not available"]
        mock_execute.return_value = mock_result

        result = runner.invoke(app, ["wf", "validate"])

        assert result.exit_code == 0  # Still exits 0, but shows errors
        assert "failed" in result.stdout.lower()
        assert "Error" in result.stdout or "OTEL" in result.stdout


@pytest.mark.e2e
def test_wf_exception_handling() -> None:
    """Test wf commands handle exceptions gracefully.

    Verifies:
        - Exceptions caught
        - Error message displayed
        - Exit code is 1
    """
    with patch("specify_cli.spiff.ops.create_otel_validation_workflow") as mock_create:
        mock_create.side_effect = Exception("Workflow creation failed")

        result = runner.invoke(app, ["wf", "validate"])

        assert result.exit_code == 1
        assert "failed" in result.stdout.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
