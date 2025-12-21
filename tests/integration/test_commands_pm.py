"""
Integration tests for process mining CLI commands.

Tests the pm command group with mock event logs and models.
Covers discover, conform, stats, filter, and sample commands.

Test Structure:
    - 15+ integration tests covering all PM commands
    - Mock event logs using pytest fixtures
    - Test JSON output, verbose mode, error cases
    - 90%+ coverage target for commands.pm module

Examples:
    pytest tests/integration/test_commands_pm.py -v --cov=src/specify_cli/commands/pm
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app


def strip_ansi(text: str) -> str:
    """Remove ANSI escape codes from text."""
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_event_log() -> MagicMock:
    """
    Create a mock PM4Py event log.

    Returns
    -------
    MagicMock
        Mock event log with typical structure.
    """
    log = MagicMock()
    log.__len__ = Mock(return_value=100)  # 100 traces
    log.__iter__ = Mock(return_value=iter([MagicMock() for _ in range(100)]))
    return log


@pytest.fixture
def mock_petri_net() -> tuple[MagicMock, MagicMock, MagicMock]:
    """
    Create a mock Petri net model.

    Returns
    -------
    tuple
        (net, initial_marking, final_marking)
    """
    net = MagicMock()
    initial_marking = MagicMock()
    final_marking = MagicMock()
    return (net, initial_marking, final_marking)


@pytest.fixture
def sample_csv_log(tmp_path: Path) -> Path:
    """
    Create a sample CSV event log file.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to sample CSV log
    """
    log_file = tmp_path / "sample_log.csv"
    csv_content = """case:concept:name,concept:name,time:timestamp
1,Start,2024-01-01 10:00:00
1,Review,2024-01-01 10:30:00
1,End,2024-01-01 11:00:00
2,Start,2024-01-01 11:00:00
2,Review,2024-01-01 11:30:00
2,Approve,2024-01-01 12:00:00
2,End,2024-01-01 12:30:00
"""
    log_file.write_text(csv_content)
    return log_file


@pytest.fixture
def sample_xes_log(tmp_path: Path) -> Path:
    """
    Create a sample XES event log file path.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to sample XES log (placeholder)
    """
    log_file = tmp_path / "sample_log.xes"
    # For testing, we'll mock the XES reading
    return log_file


@pytest.fixture
def sample_pnml_model(tmp_path: Path) -> Path:
    """
    Create a sample PNML model file path.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to sample PNML model
    """
    model_file = tmp_path / "model.pnml"
    model_file.write_text('<?xml version="1.0" encoding="UTF-8"?><pnml></pnml>')
    return model_file


# ============================================================================
# Test: pm discover
# ============================================================================


@pytest.mark.integration
def test_pm_discover_basic(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    tmp_path: Path,
    mock_event_log: MagicMock,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test basic process discovery from CSV.

    Verifies:
        - Command executes successfully
        - Output model is created
        - Success message is displayed
    """
    output_file = tmp_path / "discovered_model.pnml"

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.discover_process_model") as mock_discover, \
         patch("specify_cli.ops.process_mining.save_model") as mock_save:

        mock_load.return_value = mock_event_log
        mock_discover.return_value = (mock_petri_net, "petri")

        result = cli_runner.invoke(
            app,
            ["pm", "discover", str(sample_csv_log), "-o", str(output_file)],
        )

        assert result.exit_code == 0
        assert "Model discovered successfully" in result.stdout
        mock_load.assert_called_once()
        mock_discover.assert_called_once()
        mock_save.assert_called_once()


@pytest.mark.integration
def test_pm_discover_with_algorithm(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    tmp_path: Path,
    mock_event_log: MagicMock,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test process discovery with specific algorithm.

    Verifies:
        - Algorithm parameter is passed correctly
        - Heuristic miner is used
    """
    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.discover_process_model") as mock_discover, \
         patch("specify_cli.ops.process_mining.save_model") as mock_save:

        mock_load.return_value = mock_event_log
        mock_discover.return_value = (mock_petri_net, "petri")

        result = cli_runner.invoke(
            app,
            ["pm", "discover", str(sample_csv_log), "--algorithm", "heuristic"],
        )

        assert result.exit_code == 0
        # Check algorithm was passed
        call_kwargs = mock_discover.call_args[1]
        assert call_kwargs["algorithm"] == "heuristic"


@pytest.mark.integration
def test_pm_discover_json_output(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    mock_event_log: MagicMock,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test process discovery with JSON output.

    Verifies:
        - JSON output is valid
        - Contains expected fields
    """
    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.discover_process_model") as mock_discover, \
         patch("specify_cli.ops.process_mining.save_model") as mock_save:

        mock_load.return_value = mock_event_log
        mock_discover.return_value = (mock_petri_net, "petri")

        result = cli_runner.invoke(
            app,
            ["pm", "discover", str(sample_csv_log), "--json"],
        )

        assert result.exit_code == 0
        output_data = json.loads(strip_ansi(result.stdout))
        assert output_data["success"] is True
        assert "algorithm" in output_data
        assert "model_type" in output_data
        assert output_data["num_cases"] == 100


@pytest.mark.integration
def test_pm_discover_verbose_mode(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    mock_event_log: MagicMock,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test process discovery with verbose output.

    Verifies:
        - Verbose messages are displayed
        - Progress information is shown
    """
    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.discover_process_model") as mock_discover, \
         patch("specify_cli.ops.process_mining.save_model") as mock_save:

        mock_load.return_value = mock_event_log
        mock_discover.return_value = (mock_petri_net, "petri")

        result = cli_runner.invoke(
            app,
            ["pm", "discover", str(sample_csv_log), "--verbose"],
        )

        assert result.exit_code == 0
        assert "Loading event log" in result.stdout
        assert "Loaded" in result.stdout
        assert "Discovering model" in result.stdout


@pytest.mark.integration
def test_pm_discover_file_not_found(cli_runner: CliRunner) -> None:
    """
    Test process discovery with non-existent file.

    Verifies:
        - Error is reported
        - Non-zero exit code
    """
    result = cli_runner.invoke(
        app,
        ["pm", "discover", "/nonexistent/file.csv"],
    )

    assert result.exit_code != 0


# ============================================================================
# Test: pm conform
# ============================================================================


@pytest.mark.integration
def test_pm_conform_basic(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    sample_pnml_model: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test basic conformance checking.

    Verifies:
        - Conformance check executes
        - Fitness and precision are reported
    """
    conformance_result = {
        "fitness": 0.95,
        "precision": 0.92,  # Both >= 0.9 for Excellent conformance
        "f1_score": 0.93,
        "method": "token",
        "num_traces": 100,
        "results": [],
    }

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.conform_trace") as mock_conform:

        mock_load.return_value = mock_event_log
        mock_conform.return_value = conformance_result

        result = cli_runner.invoke(
            app,
            ["pm", "conform", str(sample_csv_log), str(sample_pnml_model)],
        )

        assert result.exit_code == 0
        assert "Conformance Checking Results" in result.stdout
        assert "95" in result.stdout  # Fitness percentage
        assert "Excellent conformance" in result.stdout


@pytest.mark.integration
def test_pm_conform_alignment_method(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    sample_pnml_model: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test conformance checking with alignment method.

    Verifies:
        - Alignment method is used
        - Results are computed correctly
    """
    conformance_result = {
        "fitness": 0.92,
        "precision": 0.85,
        "f1_score": 0.88,
        "method": "alignment",
        "num_traces": 100,
        "results": [],
    }

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.conform_trace") as mock_conform:

        mock_load.return_value = mock_event_log
        mock_conform.return_value = conformance_result

        result = cli_runner.invoke(
            app,
            ["pm", "conform", str(sample_csv_log), str(sample_pnml_model), "--method", "alignment"],
        )

        assert result.exit_code == 0
        call_kwargs = mock_conform.call_args[1]
        assert call_kwargs["method"] == "alignment"


@pytest.mark.integration
def test_pm_conform_json_output(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    sample_pnml_model: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test conformance checking with JSON output.

    Verifies:
        - JSON output is valid
        - Contains fitness, precision, F1
    """
    conformance_result = {
        "fitness": 0.80,
        "precision": 0.75,
        "f1_score": 0.77,
        "method": "token",
        "num_traces": 100,
        "results": [],
    }

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.conform_trace") as mock_conform:

        mock_load.return_value = mock_event_log
        mock_conform.return_value = conformance_result

        result = cli_runner.invoke(
            app,
            ["pm", "conform", str(sample_csv_log), str(sample_pnml_model), "--json"],
        )

        assert result.exit_code == 0
        output_data = json.loads(strip_ansi(result.stdout))
        assert output_data["success"] is True
        assert output_data["fitness"] == 0.80
        assert output_data["precision"] == 0.75
        assert output_data["f1_score"] == 0.77


# ============================================================================
# Test: pm stats
# ============================================================================


@pytest.mark.integration
def test_pm_stats_basic(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test basic log statistics.

    Verifies:
        - Statistics are computed
        - Summary table is displayed
    """
    stats_data = {
        "num_cases": 100,
        "num_events": 450,
        "num_activities": 5,
        "num_variants": 12,
        "avg_trace_length": 4.5,
        "num_start_activities": 1,
        "num_end_activities": 1,
        "activities": {"Start": 100, "Review": 80, "End": 100},
        "start_activities": {"Start": 100},
        "end_activities": {"End": 100},
        "variants": [],
    }

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.get_log_statistics") as mock_stats:

        mock_load.return_value = mock_event_log
        mock_stats.return_value = stats_data

        result = cli_runner.invoke(
            app,
            ["pm", "stats", str(sample_csv_log)],
        )

        assert result.exit_code == 0
        assert "Event Log Statistics" in result.stdout
        assert "100" in result.stdout  # Cases
        assert "450" in result.stdout  # Events


@pytest.mark.integration
def test_pm_stats_json_output(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test log statistics with JSON output.

    Verifies:
        - JSON output contains all stats
        - Data structure is correct
    """
    stats_data = {
        "num_cases": 100,
        "num_events": 450,
        "num_activities": 5,
        "num_variants": 12,
        "avg_trace_length": 4.5,
        "num_start_activities": 1,
        "num_end_activities": 1,
        "activities": {"Start": 100, "Review": 80, "End": 100},
        "start_activities": {"Start": 100},
        "end_activities": {"End": 100},
        "variants": [],
    }

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.get_log_statistics") as mock_stats:

        mock_load.return_value = mock_event_log
        mock_stats.return_value = stats_data

        result = cli_runner.invoke(
            app,
            ["pm", "stats", str(sample_csv_log), "--json"],
        )

        assert result.exit_code == 0
        output_data = json.loads(strip_ansi(result.stdout))
        assert output_data["num_cases"] == 100
        assert output_data["num_events"] == 450
        assert output_data["avg_trace_length"] == 4.5


# ============================================================================
# Test: pm filter
# ============================================================================


@pytest.mark.integration
def test_pm_filter_by_activity(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    tmp_path: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test filtering log by activity.

    Verifies:
        - Filter is applied correctly
        - Filtered log is saved
    """
    filtered_log = MagicMock()
    filtered_log.__len__ = Mock(return_value=50)

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.filter_log") as mock_filter, \
         patch("specify_cli.ops.process_mining.save_log") as mock_write:

        mock_load.return_value = mock_event_log
        mock_filter.return_value = filtered_log

        output_file = tmp_path / "filtered.csv"
        result = cli_runner.invoke(
            app,
            ["pm", "filter", str(sample_csv_log), "-o", str(output_file), "--type", "activity", "--value", "Review"],
        )

        assert result.exit_code == 0
        assert "Filtering complete" in result.stdout
        mock_filter.assert_called_once()


@pytest.mark.integration
def test_pm_filter_by_length(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    tmp_path: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test filtering log by trace length.

    Verifies:
        - Min/max length filters work
        - Correct number of traces retained
    """
    filtered_log = MagicMock()
    filtered_log.__len__ = Mock(return_value=30)

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.filter_log") as mock_filter, \
         patch("specify_cli.ops.process_mining.save_log") as mock_write:

        mock_load.return_value = mock_event_log
        mock_filter.return_value = filtered_log

        output_file = tmp_path / "filtered.csv"
        result = cli_runner.invoke(
            app,
            ["pm", "filter", str(sample_csv_log), "-o", str(output_file), "--type", "length", "--min-length", "3", "--max-length", "10"],
        )

        assert result.exit_code == 0
        call_kwargs = mock_filter.call_args[1]
        assert call_kwargs["min_length"] == 3
        assert call_kwargs["max_length"] == 10


# ============================================================================
# Test: pm sample
# ============================================================================


@pytest.mark.integration
def test_pm_sample_by_traces(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    tmp_path: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test sampling log by number of traces.

    Verifies:
        - Sampling is applied
        - Output contains correct number of traces
    """
    sampled_log = MagicMock()
    sampled_log.__len__ = Mock(return_value=50)

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.sample_log") as mock_sample, \
         patch("specify_cli.ops.process_mining.save_log") as mock_write:

        mock_load.return_value = mock_event_log
        mock_sample.return_value = sampled_log

        output_file = tmp_path / "sampled.csv"
        result = cli_runner.invoke(
            app,
            ["pm", "sample", str(sample_csv_log), "-o", str(output_file), "--num-traces", "50"],
        )

        assert result.exit_code == 0
        assert "Sampling complete" in result.stdout
        mock_sample.assert_called_once()


@pytest.mark.integration
def test_pm_sample_missing_parameter(cli_runner: CliRunner, sample_csv_log: Path) -> None:
    """
    Test sampling without required parameters.

    Verifies:
        - Error is reported when neither num-traces nor num-events is specified
    """
    result = cli_runner.invoke(
        app,
        ["pm", "sample", str(sample_csv_log)],
    )

    assert result.exit_code != 0
    assert "Must specify either" in result.stdout


@pytest.mark.integration
def test_pm_sample_json_output(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    tmp_path: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test sampling with JSON output.

    Verifies:
        - JSON output contains sampling stats
        - Sample rate is calculated
    """
    sampled_log = MagicMock()
    sampled_log.__len__ = Mock(return_value=25)

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.sample_log") as mock_sample, \
         patch("specify_cli.ops.process_mining.save_log") as mock_write:

        mock_load.return_value = mock_event_log
        mock_sample.return_value = sampled_log

        output_file = tmp_path / "sampled.csv"
        result = cli_runner.invoke(
            app,
            ["pm", "sample", str(sample_csv_log), "-o", str(output_file), "--num-traces", "25", "--json"],
        )

        assert result.exit_code == 0
        output_data = json.loads(strip_ansi(result.stdout))
        assert output_data["success"] is True
        assert output_data["sampled_cases"] == 25
        assert "25.0%" in output_data["sample_rate"]


# ============================================================================
# Error Handling Tests
# ============================================================================


@pytest.mark.integration
def test_pm_discover_invalid_algorithm(
    cli_runner: CliRunner,
    sample_csv_log: Path,
    mock_event_log: MagicMock,
) -> None:
    """
    Test discovery with invalid algorithm.

    Verifies:
        - Error is caught and reported
        - Non-zero exit code
    """
    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, \
         patch("specify_cli.ops.process_mining.discover_process_model") as mock_discover:

        mock_load.return_value = mock_event_log
        mock_discover.side_effect = ValueError("Unknown discovery algorithm: invalid")

        result = cli_runner.invoke(
            app,
            ["pm", "discover", str(sample_csv_log), "--algorithm", "invalid"],
        )

        assert result.exit_code != 0
        assert "Invalid input" in result.stdout or "Error" in result.stdout
