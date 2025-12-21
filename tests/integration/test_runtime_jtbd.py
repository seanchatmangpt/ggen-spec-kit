"""
Integration tests for specify_cli.runtime.jtbd module.

Tests JTBD runtime data persistence with actual file I/O.

Test Coverage
-------------
- JTBD data directory creation
- JSON Lines file operations (save/load)
- Job completion persistence
- Outcome achievement persistence
- Painpoint resolution persistence
- Satisfaction record persistence
- Time-to-outcome persistence
- Error handling for malformed data
- File system edge cases

Examples
--------
    $ pytest tests/integration/test_runtime_jtbd.py -v
    $ pytest tests/integration/test_runtime_jtbd.py::test_save_and_load_job_completion -v
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from specify_cli.runtime.jtbd import (
    get_jtbd_data_dir,
    load_job_completions,
    load_outcome_achievements,
    load_painpoint_resolutions,
    load_satisfaction_records,
    load_time_to_outcome_records,
    save_job_completion,
    save_outcome_achievement,
    save_painpoint_resolution,
    save_satisfaction_record,
    save_time_to_outcome,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_jtbd_dir(tmp_path: Path) -> Path:
    """Create a temporary JTBD data directory."""
    jtbd_dir = tmp_path / "jtbd"
    jtbd_dir.mkdir(parents=True, exist_ok=True)
    return jtbd_dir


@pytest.fixture
def mock_config(temp_jtbd_dir: Path) -> MagicMock:
    """Mock config with temporary cache directory."""
    mock_cfg = MagicMock()
    mock_cfg.cache_dir = temp_jtbd_dir.parent
    return mock_cfg


@pytest.fixture
def sample_job_data() -> dict[str, Any]:
    """Sample job completion data."""
    return {
        "job_id": "deps-add",
        "persona": "python-developer",
        "feature_used": "specify deps add",
        "status": "completed",
        "duration_seconds": 8.5,
        "context": {"package": "httpx"},
    }


@pytest.fixture
def sample_outcome_data() -> dict[str, Any]:
    """Sample outcome achievement data."""
    return {
        "outcome_id": "faster-dependency-management",
        "metric": "time_saved_seconds",
        "expected_value": 30.0,
        "actual_value": 40.0,
        "achievement_rate": 133.33,
        "feature": "specify deps add",
        "persona": "python-developer",
    }


@pytest.fixture
def sample_painpoint_data() -> dict[str, Any]:
    """Sample painpoint resolution data."""
    return {
        "painpoint_id": "manual-dependency-updates",
        "category": "manual_effort",
        "description": "Manually updating pyproject.toml",
        "feature": "specify deps add",
        "persona": "python-developer",
        "severity_before": 8,
        "severity_after": 2,
        "resolution_effectiveness": 75.0,
    }


@pytest.fixture
def sample_satisfaction_data() -> dict[str, Any]:
    """Sample user satisfaction data."""
    return {
        "outcome_id": "faster-dependency-management",
        "feature": "specify deps add",
        "persona": "python-developer",
        "satisfaction_level": "very_satisfied",
        "met_expectations": True,
        "would_recommend": True,
        "effort_score": 2,
    }


@pytest.fixture
def sample_tto_data() -> dict[str, Any]:
    """Sample time-to-outcome data."""
    return {
        "outcome_id": "dependency-added",
        "persona": "python-developer",
        "feature": "specify deps add",
        "duration_seconds": 8.5,
        "steps_count": 3,
        "steps": ["parse_args", "validate_package", "update_pyproject"],
    }


# =============================================================================
# Directory Management Tests
# =============================================================================


@pytest.mark.integration
class TestGetJTBDDataDir:
    """Tests for get_jtbd_data_dir function."""

    def test_get_jtbd_data_dir_creates_directory(self, mock_config: MagicMock) -> None:
        """Test that get_jtbd_data_dir creates the directory."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            data_dir = get_jtbd_data_dir()

            assert data_dir.exists()
            assert data_dir.is_dir()
            assert data_dir.name == "jtbd"

    def test_get_jtbd_data_dir_returns_path(self, mock_config: MagicMock) -> None:
        """Test that get_jtbd_data_dir returns correct path."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            data_dir = get_jtbd_data_dir()

            assert isinstance(data_dir, Path)
            assert str(data_dir).endswith("jtbd")

    def test_get_jtbd_data_dir_idempotent(self, mock_config: MagicMock) -> None:
        """Test that calling get_jtbd_data_dir multiple times is safe."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            dir1 = get_jtbd_data_dir()
            dir2 = get_jtbd_data_dir()

            assert dir1 == dir2
            assert dir1.exists()


# =============================================================================
# Job Completion Storage Tests
# =============================================================================


@pytest.mark.integration
class TestJobCompletionStorage:
    """Tests for job completion save/load operations."""

    def test_save_and_load_job_completion(
        self, mock_config: MagicMock, sample_job_data: dict[str, Any]
    ) -> None:
        """Test saving and loading a job completion record."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save record
            save_job_completion(sample_job_data)

            # Load records
            jobs = load_job_completions()

            assert len(jobs) == 1
            assert jobs[0]["job_id"] == "deps-add"
            assert jobs[0]["persona"] == "python-developer"

    def test_save_multiple_job_completions(
        self, mock_config: MagicMock, sample_job_data: dict[str, Any]
    ) -> None:
        """Test saving multiple job completion records."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save multiple records
            save_job_completion(sample_job_data)
            save_job_completion({**sample_job_data, "job_id": "docs-generate"})
            save_job_completion({**sample_job_data, "job_id": "lint-check"})

            # Load records
            jobs = load_job_completions()

            assert len(jobs) == 3
            assert {j["job_id"] for j in jobs} == {"deps-add", "docs-generate", "lint-check"}

    def test_load_job_completions_empty_file(self, mock_config: MagicMock) -> None:
        """Test loading job completions when file doesn't exist."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            jobs = load_job_completions()

            assert jobs == []

    def test_save_job_completion_with_special_characters(self, mock_config: MagicMock) -> None:
        """Test saving job completion with special characters in data."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            job_data = {
                "job_id": "test-job",
                "persona": "developer",
                "feature_used": "test feature",
                "context": {"message": "Special chars: \\n\\t\\r"},
            }

            save_job_completion(job_data)
            jobs = load_job_completions()

            assert len(jobs) == 1
            assert jobs[0]["context"]["message"] == "Special chars: \\n\\t\\r"


# =============================================================================
# Outcome Achievement Storage Tests
# =============================================================================


@pytest.mark.integration
class TestOutcomeAchievementStorage:
    """Tests for outcome achievement save/load operations."""

    def test_save_and_load_outcome_achievement(
        self, mock_config: MagicMock, sample_outcome_data: dict[str, Any]
    ) -> None:
        """Test saving and loading an outcome achievement record."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save record
            save_outcome_achievement(sample_outcome_data)

            # Load records
            outcomes = load_outcome_achievements()

            assert len(outcomes) == 1
            assert outcomes[0]["outcome_id"] == "faster-dependency-management"
            assert outcomes[0]["achievement_rate"] == 133.33

    def test_save_multiple_outcome_achievements(
        self, mock_config: MagicMock, sample_outcome_data: dict[str, Any]
    ) -> None:
        """Test saving multiple outcome achievement records."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save multiple records
            save_outcome_achievement(sample_outcome_data)
            save_outcome_achievement({**sample_outcome_data, "outcome_id": "better-documentation"})

            # Load records
            outcomes = load_outcome_achievements()

            assert len(outcomes) == 2

    def test_load_outcome_achievements_empty_file(self, mock_config: MagicMock) -> None:
        """Test loading outcome achievements when file doesn't exist."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            outcomes = load_outcome_achievements()

            assert outcomes == []


# =============================================================================
# Painpoint Resolution Storage Tests
# =============================================================================


@pytest.mark.integration
class TestPainpointResolutionStorage:
    """Tests for painpoint resolution save/load operations."""

    def test_save_and_load_painpoint_resolution(
        self, mock_config: MagicMock, sample_painpoint_data: dict[str, Any]
    ) -> None:
        """Test saving and loading a painpoint resolution record."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save record
            save_painpoint_resolution(sample_painpoint_data)

            # Load records
            painpoints = load_painpoint_resolutions()

            assert len(painpoints) == 1
            assert painpoints[0]["painpoint_id"] == "manual-dependency-updates"
            assert painpoints[0]["resolution_effectiveness"] == 75.0

    def test_save_multiple_painpoint_resolutions(
        self, mock_config: MagicMock, sample_painpoint_data: dict[str, Any]
    ) -> None:
        """Test saving multiple painpoint resolution records."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save multiple records
            save_painpoint_resolution(sample_painpoint_data)
            save_painpoint_resolution({**sample_painpoint_data, "painpoint_id": "slow-resolution"})

            # Load records
            painpoints = load_painpoint_resolutions()

            assert len(painpoints) == 2

    def test_load_painpoint_resolutions_empty_file(self, mock_config: MagicMock) -> None:
        """Test loading painpoint resolutions when file doesn't exist."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            painpoints = load_painpoint_resolutions()

            assert painpoints == []


# =============================================================================
# User Satisfaction Storage Tests
# =============================================================================


@pytest.mark.integration
class TestSatisfactionRecordStorage:
    """Tests for user satisfaction save/load operations."""

    def test_save_and_load_satisfaction_record(
        self, mock_config: MagicMock, sample_satisfaction_data: dict[str, Any]
    ) -> None:
        """Test saving and loading a satisfaction record."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save record
            save_satisfaction_record(sample_satisfaction_data)

            # Load records
            satisfaction = load_satisfaction_records()

            assert len(satisfaction) == 1
            assert satisfaction[0]["satisfaction_level"] == "very_satisfied"
            assert satisfaction[0]["met_expectations"] is True

    def test_save_multiple_satisfaction_records(
        self, mock_config: MagicMock, sample_satisfaction_data: dict[str, Any]
    ) -> None:
        """Test saving multiple satisfaction records."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save multiple records
            save_satisfaction_record(sample_satisfaction_data)
            save_satisfaction_record(
                {**sample_satisfaction_data, "satisfaction_level": "satisfied"}
            )

            # Load records
            satisfaction = load_satisfaction_records()

            assert len(satisfaction) == 2

    def test_load_satisfaction_records_empty_file(self, mock_config: MagicMock) -> None:
        """Test loading satisfaction records when file doesn't exist."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            satisfaction = load_satisfaction_records()

            assert satisfaction == []


# =============================================================================
# Time-to-Outcome Storage Tests
# =============================================================================


@pytest.mark.integration
class TestTimeToOutcomeStorage:
    """Tests for time-to-outcome save/load operations."""

    def test_save_and_load_time_to_outcome(
        self, mock_config: MagicMock, sample_tto_data: dict[str, Any]
    ) -> None:
        """Test saving and loading a time-to-outcome record."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save record
            save_time_to_outcome(sample_tto_data)

            # Load records
            tto = load_time_to_outcome_records()

            assert len(tto) == 1
            assert tto[0]["outcome_id"] == "dependency-added"
            assert tto[0]["duration_seconds"] == 8.5

    def test_save_multiple_time_to_outcome_records(
        self, mock_config: MagicMock, sample_tto_data: dict[str, Any]
    ) -> None:
        """Test saving multiple time-to-outcome records."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save multiple records
            save_time_to_outcome(sample_tto_data)
            save_time_to_outcome({**sample_tto_data, "outcome_id": "docs-generated"})

            # Load records
            tto = load_time_to_outcome_records()

            assert len(tto) == 2

    def test_load_time_to_outcome_records_empty_file(self, mock_config: MagicMock) -> None:
        """Test loading time-to-outcome records when file doesn't exist."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            tto = load_time_to_outcome_records()

            assert tto == []


# =============================================================================
# Error Handling and Edge Cases
# =============================================================================


@pytest.mark.integration
class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_load_with_malformed_json_lines(
        self, mock_config: MagicMock, temp_jtbd_dir: Path
    ) -> None:
        """Test loading file with malformed JSON lines."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            data_dir = get_jtbd_data_dir()
            jobs_file = data_dir / "jobs.jsonl"

            # Write malformed JSON lines
            with open(jobs_file, "w") as f:
                f.write('{"job_id": "test1", "persona": "dev1"}\n')
                f.write("MALFORMED LINE\n")  # This should be skipped
                f.write('{"job_id": "test2", "persona": "dev2"}\n')

            # Load should skip malformed line
            jobs = load_job_completions()

            assert len(jobs) == 2
            assert jobs[0]["job_id"] == "test1"
            assert jobs[1]["job_id"] == "test2"

    def test_load_with_empty_lines(self, mock_config: MagicMock, temp_jtbd_dir: Path) -> None:
        """Test loading file with empty lines."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            data_dir = get_jtbd_data_dir()
            jobs_file = data_dir / "jobs.jsonl"

            # Write with empty lines
            with open(jobs_file, "w") as f:
                f.write('{"job_id": "test1", "persona": "dev1"}\n')
                f.write("\n")  # Empty line
                f.write('{"job_id": "test2", "persona": "dev2"}\n')
                f.write("   \n")  # Whitespace line

            # Load should skip empty lines
            jobs = load_job_completions()

            assert len(jobs) == 2

    def test_save_with_datetime_objects(self, mock_config: MagicMock) -> None:
        """Test saving records with datetime objects (should be serialized)."""
        from datetime import UTC, datetime

        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            job_data = {
                "job_id": "test",
                "persona": "dev",
                "feature_used": "test",
                "timestamp": datetime.now(UTC),  # datetime object
            }

            # Should not raise error (json.dump uses default=str)
            save_job_completion(job_data)

            jobs = load_job_completions()
            assert len(jobs) == 1
            # Timestamp is converted to string
            assert isinstance(jobs[0]["timestamp"], str)

    def test_concurrent_writes(self, mock_config: MagicMock) -> None:
        """Test multiple concurrent writes to same file."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Write multiple records quickly
            for i in range(10):
                save_job_completion(
                    {
                        "job_id": f"test-{i}",
                        "persona": "dev",
                        "feature_used": "test",
                    }
                )

            jobs = load_job_completions()
            assert len(jobs) == 10

    def test_unicode_content(self, mock_config: MagicMock) -> None:
        """Test saving records with Unicode content."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            job_data = {
                "job_id": "test",
                "persona": "開発者",  # Japanese
                "feature_used": "тест",  # Cyrillic
                "context": {"emoji": "🚀"},
            }

            save_job_completion(job_data)
            jobs = load_job_completions()

            assert len(jobs) == 1
            assert jobs[0]["persona"] == "開発者"
            assert jobs[0]["feature_used"] == "тест"
            assert jobs[0]["context"]["emoji"] == "🚀"

    def test_large_record_count(self, mock_config: MagicMock) -> None:
        """Test handling many records efficiently."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save 100 records
            for i in range(100):
                save_outcome_achievement(
                    {
                        "outcome_id": f"outcome-{i}",
                        "metric": "test",
                        "expected_value": 100.0,
                        "actual_value": 90.0,
                        "achievement_rate": 90.0,
                        "feature": "test",
                    }
                )

            outcomes = load_outcome_achievements()
            assert len(outcomes) == 100


# =============================================================================
# Integration Tests
# =============================================================================


@pytest.mark.integration
class TestJTBDStorageIntegration:
    """Integration tests for complete JTBD storage workflows."""

    def test_complete_jtbd_workflow(
        self,
        mock_config: MagicMock,
        sample_job_data: dict[str, Any],
        sample_outcome_data: dict[str, Any],
        sample_painpoint_data: dict[str, Any],
        sample_satisfaction_data: dict[str, Any],
        sample_tto_data: dict[str, Any],
    ) -> None:
        """Test complete JTBD data collection workflow."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            # Save all types of records
            save_job_completion(sample_job_data)
            save_outcome_achievement(sample_outcome_data)
            save_painpoint_resolution(sample_painpoint_data)
            save_satisfaction_record(sample_satisfaction_data)
            save_time_to_outcome(sample_tto_data)

            # Load all types of records
            jobs = load_job_completions()
            outcomes = load_outcome_achievements()
            painpoints = load_painpoint_resolutions()
            satisfaction = load_satisfaction_records()
            tto = load_time_to_outcome_records()

            # Verify all records saved and loaded
            assert len(jobs) == 1
            assert len(outcomes) == 1
            assert len(painpoints) == 1
            assert len(satisfaction) == 1
            assert len(tto) == 1

    def test_data_directory_structure(self, mock_config: MagicMock) -> None:
        """Test that data directory has correct structure."""
        with patch("specify_cli.runtime.jtbd.get_config", return_value=mock_config):
            data_dir = get_jtbd_data_dir()

            # Save one of each record type
            save_job_completion({"job_id": "test", "persona": "test", "feature_used": "test"})
            save_outcome_achievement(
                {
                    "outcome_id": "test",
                    "metric": "test",
                    "expected_value": 1.0,
                    "actual_value": 1.0,
                    "achievement_rate": 100.0,
                    "feature": "test",
                }
            )
            save_painpoint_resolution(
                {
                    "painpoint_id": "test",
                    "category": "test",
                    "description": "test",
                    "feature": "test",
                    "persona": "test",
                    "severity_before": 10,
                    "severity_after": 5,
                }
            )
            save_satisfaction_record(
                {
                    "outcome_id": "test",
                    "feature": "test",
                    "persona": "test",
                    "satisfaction_level": "satisfied",
                    "met_expectations": True,
                    "would_recommend": True,
                }
            )
            save_time_to_outcome(
                {
                    "outcome_id": "test",
                    "persona": "test",
                    "feature": "test",
                    "duration_seconds": 1.0,
                }
            )

            # Verify all files exist
            assert (data_dir / "jobs.jsonl").exists()
            assert (data_dir / "outcomes.jsonl").exists()
            assert (data_dir / "painpoints.jsonl").exists()
            assert (data_dir / "satisfaction.jsonl").exists()
            assert (data_dir / "time_to_outcome.jsonl").exists()
