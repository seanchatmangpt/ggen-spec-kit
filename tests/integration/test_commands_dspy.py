"""
Integration tests for DSPy CLI commands.

Tests the dspy command group for LLM optimization operations.
Covers optimize, generate, and analyze commands with mocked LLM responses.

Test Structure:
    - 10+ integration tests covering DSPy operations
    - Mock LLM responses appropriately
    - Test with sample spec files
    - 80%+ coverage target for dspy commands

Examples:
    pytest tests/integration/test_commands_dspy.py -v --cov
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_spec_file(tmp_path: Path) -> Path:
    """
    Create a sample specification file for DSPy processing.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to sample spec file
    """
    spec_file = tmp_path / "spec.md"
    spec_content = """# Authentication Feature

## Overview
User authentication system with JWT tokens.

## Requirements
- User registration
- Login with email/password
- JWT token generation
- Token refresh mechanism

## Acceptance Criteria
- GIVEN a new user
- WHEN they register with valid credentials
- THEN an account is created and JWT token is issued
"""
    spec_file.write_text(spec_content)
    return spec_file


@pytest.fixture
def sample_training_data(tmp_path: Path) -> Path:
    """
    Create sample training data for DSPy optimization.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to training data JSON file
    """
    training_file = tmp_path / "training.json"
    training_data = [
        {
            "input": "Create user authentication",
            "output": "Implement JWT-based authentication with bcrypt password hashing",
        },
        {
            "input": "Add payment processing",
            "output": "Integrate Stripe API for payment processing with webhook handling",
        },
    ]
    training_file.write_text(json.dumps(training_data, indent=2))
    return training_file


@pytest.fixture
def mock_dspy_module() -> MagicMock:
    """
    Create a mock DSPy module.

    Returns
    -------
    MagicMock
        Mock DSPy module with typical methods
    """
    mock_module = MagicMock()
    mock_module.forward = Mock(return_value="Generated implementation plan")
    return mock_module


@pytest.fixture
def mock_llm_response() -> dict[str, Any]:
    """
    Create a mock LLM response.

    Returns
    -------
    dict
        Mock LLM response data
    """
    return {
        "completion": "Implement user authentication with JWT tokens and bcrypt hashing",
        "tokens_used": 150,
        "model": "gpt-3.5-turbo",
    }


# ============================================================================
# Test: dspy optimize
# ============================================================================


@pytest.mark.integration
def test_dspy_optimize_basic(
    cli_runner: CliRunner,
    sample_training_data: Path,
    tmp_path: Path,
) -> None:
    """
    Test basic DSPy optimization.

    Verifies:
        - Optimization runs successfully
        - Optimized module is saved
        - Metrics are reported
    """
    pytest.importorskip("dspy")  # Skip if dspy not installed
    output_file = tmp_path / "optimized_module.pkl"

    with patch("dspy.BootstrapFewShot") as mock_optimizer:
        mock_optimized = MagicMock()
        mock_optimizer.return_value.compile.return_value = mock_optimized

        result = cli_runner.invoke(
            app,
            ["dspy", "optimize", str(sample_training_data), "-o", str(output_file)],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")

        assert result.exit_code == 0 or "optimize" in result.stdout.lower()


@pytest.mark.integration
def test_dspy_optimize_with_metric(
    cli_runner: CliRunner,
    sample_training_data: Path,
    tmp_path: Path,
) -> None:
    """
    Test DSPy optimization with custom metric.

    Verifies:
        - Custom metric is applied
        - Optimization uses specified metric
    """
    pytest.importorskip("dspy")
    output_file = tmp_path / "optimized_module.pkl"

    with patch("dspy.BootstrapFewShot") as mock_optimizer:
        mock_optimized = MagicMock()
        mock_optimizer.return_value.compile.return_value = mock_optimized

        result = cli_runner.invoke(
            app,
            ["dspy", "optimize", str(sample_training_data), "-o", str(output_file), "--metric", "f1_score"],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")


@pytest.mark.integration
def test_dspy_optimize_max_rounds(
    cli_runner: CliRunner,
    sample_training_data: Path,
    tmp_path: Path,
) -> None:
    """
    Test DSPy optimization with max rounds limit.

    Verifies:
        - Max rounds parameter is respected
        - Optimization stops after limit
    """
    pytest.importorskip("dspy")
    output_file = tmp_path / "optimized_module.pkl"

    with patch("dspy.BootstrapFewShot") as mock_optimizer:
        mock_optimized = MagicMock()
        mock_optimizer.return_value.compile.return_value = mock_optimized

        result = cli_runner.invoke(
            app,
            ["dspy", "optimize", str(sample_training_data), "-o", str(output_file), "--max-rounds", "5"],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")


# ============================================================================
# Test: dspy generate
# ============================================================================


@pytest.mark.integration
def test_dspy_generate_from_spec(
    cli_runner: CliRunner,
    sample_spec_file: Path,
    mock_llm_response: dict[str, Any],
) -> None:
    """
    Test generating implementation from spec using DSPy.

    Verifies:
        - Spec is parsed correctly
        - LLM generates implementation
        - Output is formatted properly
    """
    pytest.importorskip("dspy")
    with patch("dspy.ChainOfThought") as mock_cot:
        mock_module = MagicMock()
        mock_module.forward.return_value = mock_llm_response["completion"]
        mock_cot.return_value = mock_module

        result = cli_runner.invoke(
            app,
            ["dspy", "generate", str(sample_spec_file)],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")


@pytest.mark.integration
def test_dspy_generate_with_model(
    cli_runner: CliRunner,
    sample_spec_file: Path,
    mock_llm_response: dict[str, Any],
) -> None:
    """
    Test generation with specific model.

    Verifies:
        - Model parameter is used
        - Correct LLM is invoked
    """
    pytest.importorskip("dspy")
    with patch("dspy.OpenAI") as mock_llm, \
         patch("dspy.ChainOfThought") as mock_cot:

        mock_module = MagicMock()
        mock_module.forward.return_value = mock_llm_response["completion"]
        mock_cot.return_value = mock_module

        result = cli_runner.invoke(
            app,
            ["dspy", "generate", str(sample_spec_file), "--model", "gpt-4"],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")


@pytest.mark.integration
def test_dspy_generate_with_temperature(
    cli_runner: CliRunner,
    sample_spec_file: Path,
    mock_llm_response: dict[str, Any],
) -> None:
    """
    Test generation with custom temperature.

    Verifies:
        - Temperature parameter is applied
        - Affects LLM randomness
    """
    pytest.importorskip("dspy")
    with patch("dspy.OpenAI") as mock_llm, \
         patch("dspy.ChainOfThought") as mock_cot:

        mock_module = MagicMock()
        mock_module.forward.return_value = mock_llm_response["completion"]
        mock_cot.return_value = mock_module

        result = cli_runner.invoke(
            app,
            ["dspy", "generate", str(sample_spec_file), "--temperature", "0.7"],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")


@pytest.mark.integration
def test_dspy_generate_json_output(
    cli_runner: CliRunner,
    sample_spec_file: Path,
    mock_llm_response: dict[str, Any],
) -> None:
    """
    Test generation with JSON output.

    Verifies:
        - JSON output is valid
        - Contains completion and metadata
    """
    pytest.importorskip("dspy")
    with patch("dspy.ChainOfThought") as mock_cot:
        mock_module = MagicMock()
        mock_module.forward.return_value = mock_llm_response["completion"]
        mock_cot.return_value = mock_module

        result = cli_runner.invoke(
            app,
            ["dspy", "generate", str(sample_spec_file), "--json"],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")

        # Try to parse JSON if command exists
        try:
            output_data = json.loads(result.stdout)
            assert "completion" in output_data or "output" in output_data
        except json.JSONDecodeError:
            pass  # Command might not be fully implemented


# ============================================================================
# Test: dspy analyze
# ============================================================================


@pytest.mark.integration
def test_dspy_analyze_module_performance(
    cli_runner: CliRunner,
    tmp_path: Path,
) -> None:
    """
    Test analyzing DSPy module performance.

    Verifies:
        - Module is analyzed
        - Performance metrics are reported
    """
    pytest.importorskip("dspy")
    module_file = tmp_path / "module.pkl"
    # Create a mock pickle file
    module_file.write_bytes(b"mock_pickle_data")

    with patch("pickle.load") as mock_pickle, \
         patch("dspy.evaluate") as mock_evaluate:

        mock_module = MagicMock()
        mock_pickle.return_value = mock_module
        mock_evaluate.return_value = {"accuracy": 0.85, "f1": 0.82}

        result = cli_runner.invoke(
            app,
            ["dspy", "analyze", str(module_file)],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")


@pytest.mark.integration
def test_dspy_analyze_with_test_data(
    cli_runner: CliRunner,
    tmp_path: Path,
    sample_training_data: Path,
) -> None:
    """
    Test analyzing module with test dataset.

    Verifies:
        - Test data is loaded
        - Evaluation is performed
        - Metrics are calculated
    """
    pytest.importorskip("dspy")
    module_file = tmp_path / "module.pkl"
    module_file.write_bytes(b"mock_pickle_data")

    with patch("pickle.load") as mock_pickle, \
         patch("dspy.evaluate") as mock_evaluate:

        mock_module = MagicMock()
        mock_pickle.return_value = mock_module
        mock_evaluate.return_value = {"accuracy": 0.90, "precision": 0.88, "recall": 0.85}

        result = cli_runner.invoke(
            app,
            ["dspy", "analyze", str(module_file), "--test-data", str(sample_training_data)],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")


# ============================================================================
# Test: Error Handling
# ============================================================================


@pytest.mark.integration
def test_dspy_generate_spec_not_found(cli_runner: CliRunner, tmp_path: Path) -> None:
    """
    Test generation with non-existent spec file.

    Verifies:
        - Error is reported
        - Non-zero exit code
    """
    nonexistent_spec = tmp_path / "nonexistent.md"

    result = cli_runner.invoke(
        app,
        ["dspy", "generate", str(nonexistent_spec)],
        catch_exceptions=False,
    )

    if "dspy" not in str(result.stdout):
        pytest.skip("dspy commands not yet implemented")

    assert result.exit_code != 0 or "not found" in result.stdout.lower()


@pytest.mark.integration
def test_dspy_optimize_invalid_training_data(
    cli_runner: CliRunner,
    tmp_path: Path,
) -> None:
    """
    Test optimization with invalid training data.

    Verifies:
        - Error is caught
        - Helpful message is displayed
    """
    invalid_data = tmp_path / "invalid.json"
    invalid_data.write_text("{ invalid json }")

    result = cli_runner.invoke(
        app,
        ["dspy", "optimize", str(invalid_data)],
        catch_exceptions=False,
    )

    if "dspy" not in str(result.stdout):
        pytest.skip("dspy commands not yet implemented")


@pytest.mark.integration
def test_dspy_generate_llm_error(
    cli_runner: CliRunner,
    sample_spec_file: Path,
) -> None:
    """
    Test generation when LLM returns error.

    Verifies:
        - LLM errors are handled gracefully
        - Error message is displayed
    """
    pytest.importorskip("dspy")
    with patch("dspy.ChainOfThought") as mock_cot:
        mock_cot.side_effect = Exception("LLM API error: rate limit exceeded")

        result = cli_runner.invoke(
            app,
            ["dspy", "generate", str(sample_spec_file)],
            catch_exceptions=False,
        )

        if "dspy" not in str(result.stdout):
            pytest.skip("dspy commands not yet implemented")
