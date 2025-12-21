"""
Unit tests for process mining operations layer.

Tests pure business logic in ops.process_mining module with mocked runtime dependencies.
No side effects - all pm4py imports are mocked.

Test Structure:
    - 12+ unit tests covering all process mining operations
    - Test with small test logs using fixtures
    - Test error handling (invalid logs, missing algorithms)
    - 85%+ coverage target for ops.process_mining

Examples:
    pytest tests/unit/test_ops_process_mining.py -v --cov=src/specify_cli/ops/process_mining
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

from specify_cli.ops import process_mining as pm_ops

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def mock_event_log() -> MagicMock:
    """
    Create a mock event log for testing.

    Returns
    -------
    MagicMock
        Mock event log with traces
    """
    log = MagicMock()
    log.__len__ = Mock(return_value=50)
    log.__iter__ = Mock(return_value=iter([MagicMock() for _ in range(50)]))
    return log


@pytest.fixture
def mock_petri_net() -> tuple[MagicMock, MagicMock, MagicMock]:
    """
    Create a mock Petri net.

    Returns
    -------
    tuple
        (net, initial_marking, final_marking)
    """
    net = MagicMock()
    net.places = [MagicMock() for _ in range(5)]
    net.transitions = [MagicMock() for _ in range(4)]

    initial_marking = MagicMock()
    final_marking = MagicMock()

    return (net, initial_marking, final_marking)


@pytest.fixture
def sample_csv_file(tmp_path: Path) -> Path:
    """
    Create a sample CSV file.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to CSV file
    """
    csv_file = tmp_path / "log.csv"
    csv_content = """case:concept:name,concept:name,time:timestamp
1,Start,2024-01-01 10:00:00
1,End,2024-01-01 11:00:00
"""
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def sample_xes_file(tmp_path: Path) -> Path:
    """
    Create a sample XES file path.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to XES file
    """
    xes_file = tmp_path / "log.xes"
    xes_content = '<?xml version="1.0" encoding="UTF-8"?><log></log>'
    xes_file.write_text(xes_content)
    return xes_file


# ============================================================================
# Test: load_event_log
# ============================================================================


@pytest.mark.unit
def test_load_event_log_csv(sample_csv_file: Path, mock_event_log: MagicMock) -> None:
    """
    Test loading event log from CSV file.

    Verifies:
        - CSV is read correctly
        - DataFrame is formatted
        - Event log is created
    """
    pytest.importorskip("pm4py")

    with patch("pm4py.read_xes") as mock_read_xes, \
         patch("pm4py.format_dataframe") as mock_format, \
         patch("pm4py.convert_to_event_log") as mock_convert, \
         patch("pandas.read_csv") as mock_read_csv:

        mock_df = MagicMock()
        mock_read_csv.return_value = mock_df
        mock_format.return_value = mock_df
        mock_convert.return_value = mock_event_log

        result = pm_ops.load_event_log(sample_csv_file)

        assert result == mock_event_log
        mock_read_csv.assert_called_once()
        mock_format.assert_called_once()
        mock_convert.assert_called_once()


@pytest.mark.unit
def test_load_event_log_xes(sample_xes_file: Path, mock_event_log: MagicMock) -> None:
    """
    Test loading event log from XES file.

    Verifies:
        - XES is read correctly
        - Event log is returned
    """
    pytest.importorskip("pm4py")

    with patch("pm4py.read_xes") as mock_read_xes:
        mock_read_xes.return_value = mock_event_log

        result = pm_ops.load_event_log(sample_xes_file)

        assert result == mock_event_log
        mock_read_xes.assert_called_once_with(str(sample_xes_file))


@pytest.mark.unit
def test_load_event_log_file_not_found(tmp_path: Path) -> None:
    """
    Test loading event log from non-existent file.

    Verifies:
        - FileNotFoundError is raised
    """
    pytest.importorskip("pm4py")
    nonexistent_file = tmp_path / "nonexistent.csv"

    with pytest.raises(FileNotFoundError, match="Input file not found"):
        pm_ops.load_event_log(nonexistent_file)


@pytest.mark.unit
def test_load_event_log_unsupported_format(tmp_path: Path) -> None:
    """
    Test loading event log from unsupported format.

    Verifies:
        - ValueError is raised for unsupported formats
    """
    pytest.importorskip("pm4py")
    unsupported_file = tmp_path / "log.txt"
    unsupported_file.write_text("unsupported format")

    with pytest.raises(ValueError, match="Unsupported file format"):
        pm_ops.load_event_log(unsupported_file)


# ============================================================================
# Test: discover_process_model
# ============================================================================


@pytest.mark.unit
def test_discover_process_model_alpha(
    mock_event_log: MagicMock,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test process discovery with alpha miner.

    Verifies:
        - Alpha algorithm is called
        - Petri net is returned
    """
    pytest.importorskip("pm4py")
    with patch("pm4py.discover_petri_net_alpha") as mock_alpha:
        mock_alpha.return_value = mock_petri_net

        model, model_type = pm_ops.discover_process_model(mock_event_log, algorithm="alpha")

        assert model == mock_petri_net
        assert model_type == "petri"
        mock_alpha.assert_called_once_with(mock_event_log)


@pytest.mark.unit
def test_discover_process_model_inductive(
    mock_event_log: MagicMock,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test process discovery with inductive miner.

    Verifies:
        - Inductive algorithm is called
        - Noise threshold is applied
    """
    pytest.importorskip("pm4py")
    with patch("pm4py.discover_petri_net_inductive") as mock_inductive:
        mock_inductive.return_value = mock_petri_net

        model, model_type = pm_ops.discover_process_model(
            mock_event_log,
            algorithm="inductive",
            noise_threshold=0.2,
        )

        assert model == mock_petri_net
        assert model_type == "petri"
        mock_inductive.assert_called_once_with(mock_event_log, noise_threshold=0.2)


@pytest.mark.unit
def test_discover_process_model_unknown_algorithm(mock_event_log: MagicMock) -> None:
    """
    Test process discovery with unknown algorithm.

    Verifies:
        - ValueError is raised
        - Error message includes algorithm name
    """
    pytest.importorskip("pm4py")
    with pytest.raises(ValueError, match="Unknown discovery algorithm: unknown"):
        pm_ops.discover_process_model(mock_event_log, algorithm="unknown")


# ============================================================================
# Test: conform_trace
# ============================================================================


@pytest.mark.unit
def test_conform_trace_token_replay(
    mock_event_log: MagicMock,
    tmp_path: Path,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test conformance checking with token-based replay.

    Verifies:
        - Token replay is executed
        - Fitness and precision are calculated
        - F1 score is computed
    """
    pytest.importorskip("pm4py")
    model_file = tmp_path / "model.pnml"
    model_file.write_text('<?xml version="1.0" encoding="UTF-8"?><pnml></pnml>')

    with patch("pm4py.read_pnml") as mock_read_pnml, \
         patch("pm4py.conformance_diagnostics_token_based_replay") as mock_conformance, \
         patch("pm4py.fitness_token_based_replay") as mock_fitness, \
         patch("pm4py.precision_token_based_replay") as mock_precision:

        mock_read_pnml.return_value = mock_petri_net
        mock_conformance.return_value = []
        mock_fitness.return_value = 0.95
        mock_precision.return_value = 0.88

        result = pm_ops.conform_trace(mock_event_log, model_file, method="token")

        assert result["fitness"] == 0.95
        assert result["precision"] == 0.88
        assert result["f1_score"] > 0  # Harmonic mean
        assert result["method"] == "token"
        assert result["num_traces"] == 50


@pytest.mark.unit
def test_conform_trace_alignment(
    mock_event_log: MagicMock,
    tmp_path: Path,
    mock_petri_net: tuple[MagicMock, MagicMock, MagicMock],
) -> None:
    """
    Test conformance checking with alignments.

    Verifies:
        - Alignment method is used
        - Results are computed
    """
    pytest.importorskip("pm4py")
    model_file = tmp_path / "model.pnml"
    model_file.write_text('<?xml version="1.0" encoding="UTF-8"?><pnml></pnml>')

    with patch("pm4py.read_pnml") as mock_read_pnml, \
         patch("pm4py.conformance_diagnostics_alignments") as mock_conformance, \
         patch("pm4py.fitness_alignments") as mock_fitness, \
         patch("pm4py.precision_alignments") as mock_precision:

        mock_read_pnml.return_value = mock_petri_net
        mock_conformance.return_value = []
        mock_fitness.return_value = {"log_fitness": 0.92}
        mock_precision.return_value = 0.85

        result = pm_ops.conform_trace(mock_event_log, model_file, method="alignment")

        assert result["fitness"] == 0.92
        assert result["precision"] == 0.85
        assert result["method"] == "alignment"


@pytest.mark.unit
def test_conform_trace_model_not_found(mock_event_log: MagicMock, tmp_path: Path) -> None:
    """
    Test conformance checking with non-existent model file.

    Verifies:
        - FileNotFoundError is raised
    """
    pytest.importorskip("pm4py")
    nonexistent_model = tmp_path / "nonexistent.pnml"

    with pytest.raises(FileNotFoundError, match="Model file not found"):
        pm_ops.conform_trace(mock_event_log, nonexistent_model)


# ============================================================================
# Test: get_log_statistics
# ============================================================================


@pytest.mark.unit
def test_get_log_statistics(mock_event_log: MagicMock) -> None:
    """
    Test extracting log statistics.

    Verifies:
        - All statistics are computed
        - Structure is correct
    """
    pytest.importorskip("pm4py")
    # Mock activities
    mock_activities = {"Start": 50, "Review": 40, "End": 50}

    # Mock variants
    mock_variants = [{"count": 30}, {"count": 20}]

    # Mock start/end activities
    mock_start_activities = {"Start": 50}
    mock_end_activities = {"End": 50}

    with patch("pm4py.get_event_attribute_values") as mock_get_attr, \
         patch("pm4py.statistics.traces.generic.log.case_statistics.get_variant_statistics") as mock_variants_fn, \
         patch("pm4py.statistics.start_activities.log.get.get_start_activities") as mock_start, \
         patch("pm4py.statistics.end_activities.log.get.get_end_activities") as mock_end:

        mock_get_attr.return_value = mock_activities
        mock_variants_fn.return_value = mock_variants
        mock_start.return_value = mock_start_activities
        mock_end.return_value = mock_end_activities

        # Mock trace lengths
        mock_event_log.__iter__ = Mock(
            return_value=iter([MagicMock(__len__=Mock(return_value=3)) for _ in range(50)])
        )

        result = pm_ops.get_log_statistics(mock_event_log)

        assert result["num_cases"] == 50
        assert result["num_events"] == 150
        assert result["num_activities"] == 3
        assert result["num_variants"] == 2
        assert result["avg_trace_length"] == 3.0


# ============================================================================
# Test: filter_log
# ============================================================================


@pytest.mark.unit
def test_filter_log_by_activity(mock_event_log: MagicMock) -> None:
    """
    Test filtering log by activity.

    Verifies:
        - Activity filter is applied
        - Filtered log is returned
    """
    pytest.importorskip("pm4py")
    filtered_log = MagicMock()

    with patch("pm4py.filter_event_attribute_values") as mock_filter:
        mock_filter.return_value = filtered_log

        result = pm_ops.filter_log(mock_event_log, filter_type="activity", filter_value="Review")

        assert result == filtered_log
        mock_filter.assert_called_once()


@pytest.mark.unit
def test_filter_log_by_length(mock_event_log: MagicMock) -> None:
    """
    Test filtering log by trace length.

    Verifies:
        - Length filter is applied
        - Min and max are respected
    """
    pytest.importorskip("pm4py")
    filtered_log = MagicMock()

    with patch("pm4py.filter_trace_length") as mock_filter:
        mock_filter.return_value = filtered_log

        result = pm_ops.filter_log(mock_event_log, filter_type="length", min_length=3, max_length=10)

        assert result == filtered_log
        mock_filter.assert_called_once_with(mock_event_log, 3, 10)


@pytest.mark.unit
def test_filter_log_invalid_parameters(mock_event_log: MagicMock) -> None:
    """
    Test filtering with invalid parameters.

    Verifies:
        - ValueError is raised
    """
    pytest.importorskip("pm4py")
    with pytest.raises(ValueError, match="Invalid filter type"):
        pm_ops.filter_log(mock_event_log, filter_type="invalid")


# ============================================================================
# Test: sample_log
# ============================================================================


@pytest.mark.unit
def test_sample_log_by_traces(mock_event_log: MagicMock) -> None:
    """
    Test sampling log by number of traces.

    Verifies:
        - Sampling is applied
        - Correct number of traces
    """
    pytest.importorskip("pm4py")
    sampled_log = MagicMock()

    with patch("pm4py.sample_log") as mock_sample:
        mock_sample.return_value = sampled_log

        result = pm_ops.sample_log(mock_event_log, num_traces=25)

        assert result == sampled_log
        mock_sample.assert_called_once_with(mock_event_log, n_traces=25)


@pytest.mark.unit
def test_sample_log_missing_parameters(mock_event_log: MagicMock) -> None:
    """
    Test sampling without required parameters.

    Verifies:
        - ValueError is raised
    """
    pytest.importorskip("pm4py")
    with pytest.raises(ValueError, match="Either num_traces or num_events must be specified"):
        pm_ops.sample_log(mock_event_log)


@pytest.mark.unit
def test_sample_log_unknown_method(mock_event_log: MagicMock) -> None:
    """
    Test sampling with unknown method.

    Verifies:
        - ValueError is raised
    """
    pytest.importorskip("pm4py")
    with pytest.raises(ValueError, match="Unknown sampling method"):
        pm_ops.sample_log(mock_event_log, num_traces=10, method="unknown")
