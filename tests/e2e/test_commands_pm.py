"""End-to-end tests for specify pm (process mining) commands.

This module tests the complete pm command flow including:
- CLI invocation via CliRunner
- Integration with ops.process_mining module
- All 5 subcommands: discover, conform, stats, filter, sample
- Output formatting (text and JSON)
- Error handling and exit codes

Test Coverage
-------------
- discover: Process model discovery from event logs
- conform: Conformance checking
- stats: Event log statistics extraction
- filter: Event log filtering
- sample: Event log sampling
- JSON output validation
- Error handling for missing files
- CSV/XES file support
- Algorithm selection

Examples
--------
    $ pytest tests/e2e/test_commands_pm.py -v -m e2e
    $ pytest tests/e2e/test_commands_pm.py::test_pm_discover_basic
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app

runner = CliRunner()


@pytest.mark.e2e
def test_pm_discover_basic(tmp_path: Path) -> None:
    """Test pm discover command executes successfully.

    Verifies:
        - Command executes without errors
        - Model is discovered and saved
        - Success message displayed
    """
    input_file = tmp_path / "log.csv"
    input_file.touch()
    output_file = tmp_path / "model.pnml"

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.discover_process_model"
    ) as mock_discover, patch("specify_cli.ops.process_mining.save_model") as mock_save:
        mock_log = MagicMock()
        mock_log.__len__ = MagicMock(return_value=100)
        mock_load.return_value = mock_log
        mock_discover.return_value = (MagicMock(), "petri_net")

        result = runner.invoke(
            app, ["pm", "discover", str(input_file), "-o", str(output_file)]
        )

        assert result.exit_code == 0
        assert "discovered successfully" in result.stdout.lower() or "✓" in result.stdout
        mock_discover.assert_called_once()
        mock_save.assert_called_once()


@pytest.mark.e2e
def test_pm_discover_with_algorithm(tmp_path: Path) -> None:
    """Test pm discover command with algorithm selection.

    Verifies:
        - Algorithm option works
        - Different algorithms can be selected
    """
    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.discover_process_model"
    ) as mock_discover, patch("specify_cli.ops.process_mining.save_model"):
        mock_log = MagicMock()
        mock_log.__len__ = MagicMock(return_value=100)
        mock_load.return_value = mock_log
        mock_discover.return_value = (MagicMock(), "petri_net")

        result = runner.invoke(app, ["pm", "discover", str(input_file), "-a", "heuristic"])

        assert result.exit_code == 0
        call_kwargs = mock_discover.call_args[1]
        assert call_kwargs["algorithm"] == "heuristic"


@pytest.mark.e2e
def test_pm_discover_json_output(tmp_path: Path) -> None:
    """Test pm discover command JSON output format.

    Verifies:
        - JSON output is valid
        - Contains required fields
    """
    import json

    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.discover_process_model"
    ) as mock_discover, patch("specify_cli.ops.process_mining.save_model"):
        mock_log = MagicMock()
        mock_log.__len__ = MagicMock(return_value=50)
        mock_load.return_value = mock_log
        mock_discover.return_value = (MagicMock(), "petri_net")

        result = runner.invoke(app, ["pm", "discover", str(input_file), "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert "algorithm" in data
        assert "num_cases" in data
        assert data["num_cases"] == 50


@pytest.mark.e2e
def test_pm_conform_basic(tmp_path: Path) -> None:
    """Test pm conform command executes successfully.

    Verifies:
        - Conformance checking runs
        - Results displayed
        - Fitness and precision shown
    """
    log_file = tmp_path / "log.csv"
    log_file.touch()
    model_file = tmp_path / "model.pnml"
    model_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.conform_trace"
    ) as mock_conform:
        mock_log = MagicMock()
        mock_log.__len__ = MagicMock(return_value=100)
        mock_load.return_value = mock_log
        mock_conform.return_value = {
            "method": "token",
            "fitness": 0.95,
            "precision": 0.87,
            "f1_score": 0.91,
            "num_traces": 100,
        }

        result = runner.invoke(app, ["pm", "conform", str(log_file), str(model_file)])

        assert result.exit_code == 0
        assert "Fitness" in result.stdout or "0.95" in result.stdout
        assert "Precision" in result.stdout or "0.87" in result.stdout


@pytest.mark.e2e
def test_pm_conform_json_output(tmp_path: Path) -> None:
    """Test pm conform command JSON output format.

    Verifies:
        - JSON contains conformance metrics
        - All required fields present
    """
    import json

    log_file = tmp_path / "log.csv"
    log_file.touch()
    model_file = tmp_path / "model.pnml"
    model_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.conform_trace"
    ) as mock_conform:
        mock_log = MagicMock()
        mock_log.__len__ = MagicMock(return_value=100)
        mock_load.return_value = mock_log
        mock_conform.return_value = {
            "method": "token",
            "fitness": 0.95,
            "precision": 0.87,
            "f1_score": 0.91,
            "num_traces": 100,
        }

        result = runner.invoke(
            app, ["pm", "conform", str(log_file), str(model_file), "--json"]
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert data["fitness"] == 0.95
        assert data["precision"] == 0.87
        assert data["f1_score"] == 0.91


@pytest.mark.e2e
def test_pm_stats_basic(tmp_path: Path) -> None:
    """Test pm stats command extracts log statistics.

    Verifies:
        - Statistics extraction works
        - Key metrics displayed
        - Cases, events, activities shown
    """
    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.get_log_statistics"
    ) as mock_stats:
        mock_log = MagicMock()
        mock_load.return_value = mock_log
        mock_stats.return_value = {
            "num_cases": 150,
            "num_events": 1200,
            "num_activities": 25,
            "num_variants": 45,
            "avg_trace_length": 8.0,
            "start_activities": {"Start": 150},
            "end_activities": {"End": 150},
        }

        result = runner.invoke(app, ["pm", "stats", str(input_file)])

        assert result.exit_code == 0
        assert "150" in result.stdout or "1200" in result.stdout
        assert "Statistics" in result.stdout or "Total" in result.stdout


@pytest.mark.e2e
def test_pm_stats_json_output(tmp_path: Path) -> None:
    """Test pm stats command JSON output format.

    Verifies:
        - JSON contains all statistics
        - Structure is correct
    """
    import json

    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.get_log_statistics"
    ) as mock_stats:
        mock_log = MagicMock()
        mock_load.return_value = mock_log
        stats_data = {
            "num_cases": 150,
            "num_events": 1200,
            "num_activities": 25,
            "num_variants": 45,
            "avg_trace_length": 8.0,
            "start_activities": {"Start": 150},
            "end_activities": {"End": 150},
        }
        mock_stats.return_value = stats_data

        result = runner.invoke(app, ["pm", "stats", str(input_file), "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["num_cases"] == 150
        assert data["num_events"] == 1200
        assert data["num_activities"] == 25


@pytest.mark.e2e
def test_pm_filter_basic(tmp_path: Path) -> None:
    """Test pm filter command filters event log.

    Verifies:
        - Filtering works
        - Filtered log saved
        - Reduction shown
    """
    input_file = tmp_path / "log.csv"
    input_file.touch()
    output_file = tmp_path / "filtered.csv"

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.filter_log"
    ) as mock_filter, patch("specify_cli.ops.process_mining.save_log"):
        mock_original = MagicMock()
        mock_original.__len__ = MagicMock(return_value=100)
        mock_filtered = MagicMock()
        mock_filtered.__len__ = MagicMock(return_value=60)
        mock_load.return_value = mock_original
        mock_filter.return_value = mock_filtered

        result = runner.invoke(
            app, ["pm", "filter", str(input_file), "-o", str(output_file)]
        )

        assert result.exit_code == 0
        assert "complete" in result.stdout.lower() or "✓" in result.stdout
        assert "100" in result.stdout and "60" in result.stdout


@pytest.mark.e2e
def test_pm_filter_json_output(tmp_path: Path) -> None:
    """Test pm filter command JSON output format.

    Verifies:
        - JSON shows filtering results
        - Original and filtered counts included
    """
    import json

    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.filter_log"
    ) as mock_filter, patch("specify_cli.ops.process_mining.save_log"):
        mock_original = MagicMock()
        mock_original.__len__ = MagicMock(return_value=100)
        mock_filtered = MagicMock()
        mock_filtered.__len__ = MagicMock(return_value=60)
        mock_load.return_value = mock_original
        mock_filter.return_value = mock_filtered

        result = runner.invoke(app, ["pm", "filter", str(input_file), "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert data["original_cases"] == 100
        assert data["filtered_cases"] == 60
        assert "reduction" in data


@pytest.mark.e2e
def test_pm_sample_basic(tmp_path: Path) -> None:
    """Test pm sample command samples event log.

    Verifies:
        - Sampling works
        - Sample size correct
        - Output saved
    """
    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.sample_log"
    ) as mock_sample, patch("specify_cli.ops.process_mining.save_log"):
        mock_original = MagicMock()
        mock_original.__len__ = MagicMock(return_value=1000)
        mock_sampled = MagicMock()
        mock_sampled.__len__ = MagicMock(return_value=100)
        mock_load.return_value = mock_original
        mock_sample.return_value = mock_sampled

        result = runner.invoke(app, ["pm", "sample", str(input_file), "-n", "100"])

        assert result.exit_code == 0
        assert "complete" in result.stdout.lower() or "✓" in result.stdout
        assert "1000" in result.stdout and "100" in result.stdout


@pytest.mark.e2e
def test_pm_sample_json_output(tmp_path: Path) -> None:
    """Test pm sample command JSON output format.

    Verifies:
        - JSON shows sampling results
        - Sample rate calculated
    """
    import json

    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.sample_log"
    ) as mock_sample, patch("specify_cli.ops.process_mining.save_log"):
        mock_original = MagicMock()
        mock_original.__len__ = MagicMock(return_value=1000)
        mock_sampled = MagicMock()
        mock_sampled.__len__ = MagicMock(return_value=100)
        mock_load.return_value = mock_original
        mock_sample.return_value = mock_sampled

        result = runner.invoke(app, ["pm", "sample", str(input_file), "-n", "100", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert data["original_cases"] == 1000
        assert data["sampled_cases"] == 100
        assert "sample_rate" in data


@pytest.mark.e2e
def test_pm_discover_file_not_found() -> None:
    """Test pm discover handles missing file gracefully.

    Verifies:
        - Error message displayed
        - Exit code is 1
    """
    result = runner.invoke(app, ["pm", "discover", "/nonexistent/log.csv"])

    assert result.exit_code == 1
    assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()


@pytest.mark.e2e
def test_pm_sample_missing_num_traces() -> None:
    """Test pm sample requires --num-traces or --num-events.

    Verifies:
        - Error when neither option provided
        - Clear error message
    """
    result = runner.invoke(app, ["pm", "sample", "/tmp/log.csv"])

    assert result.exit_code == 1
    assert "must specify" in result.stdout.lower() or "error" in result.stdout.lower()


@pytest.mark.e2e
@pytest.mark.parametrize(
    ("algorithm", "expected_algo"),
    [
        ("alpha", "alpha"),
        ("heuristic", "heuristic"),
        ("inductive", "inductive"),
    ],
)
def test_pm_discover_algorithm_variants(
    tmp_path: Path, algorithm: str, expected_algo: str
) -> None:
    """Test pm discover with different algorithms.

    Parameters
    ----------
    algorithm : str
        Algorithm to test.
    expected_algo : str
        Expected algorithm in call.

    Verifies:
        - All algorithms work
        - Correct algorithm passed
    """
    input_file = tmp_path / "log.csv"
    input_file.touch()

    with patch("specify_cli.ops.process_mining.load_event_log") as mock_load, patch(
        "specify_cli.ops.process_mining.discover_process_model"
    ) as mock_discover, patch("specify_cli.ops.process_mining.save_model"):
        mock_log = MagicMock()
        mock_log.__len__ = MagicMock(return_value=100)
        mock_load.return_value = mock_log
        mock_discover.return_value = (MagicMock(), "petri_net")

        result = runner.invoke(app, ["pm", "discover", str(input_file), "-a", algorithm])

        assert result.exit_code == 0
        call_kwargs = mock_discover.call_args[1]
        assert call_kwargs["algorithm"] == expected_algo


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "e2e"])
