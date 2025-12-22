"""Unit tests for ggen incremental operations."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from specify_cli.ops.ggen_incremental import (
    FileHashRecord,
    IncrementalTracker,
)


@pytest.fixture
def temp_project() -> tuple[Path, Path]:
    """Create temporary project directory."""
    with TemporaryDirectory() as tmp:
        project_dir = Path(tmp)
        output_dir = project_dir / "output"
        output_dir.mkdir()
        yield project_dir, output_dir


class TestIncrementalTracker:
    """Tests for incremental tracking."""

    def test_init_creates_state_dir(self, temp_project: tuple[Path, Path]) -> None:
        """Test tracker initialization."""
        _, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        assert (output_dir / ".ggen-incremental").exists()
        assert tracker.state_file == output_dir / ".ggen-incremental" / "state.json"

    def test_needs_update_missing_file(self, temp_project: tuple[Path, Path]) -> None:
        """Test needs_update with missing file."""
        _, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        assert tracker.needs_update("missing.ttl") is True

    def test_needs_update_new_file(self, temp_project: tuple[Path, Path]) -> None:
        """Test needs_update when no prior state."""
        project_dir, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        # Create a file
        test_file = project_dir / "test.ttl"
        test_file.write_text("@prefix : <http://example.com/> .")

        # First time should need update
        assert tracker.needs_update(str(test_file)) is True

    def test_needs_update_unchanged_file(self, temp_project: tuple[Path, Path]) -> None:
        """Test needs_update when file unchanged."""
        project_dir, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        # Create a file
        test_file = project_dir / "test.ttl"
        content = "@prefix : <http://example.com/> ."
        test_file.write_text(content)

        # Record it
        tracker.record_input(str(test_file))
        tracker.save()

        # Reload tracker
        tracker2 = IncrementalTracker(output_dir)

        # Should not need update
        assert tracker2.needs_update(str(test_file)) is False

    def test_needs_update_changed_file(self, temp_project: tuple[Path, Path]) -> None:
        """Test needs_update when file changed."""
        project_dir, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        # Create a file
        test_file = project_dir / "test.ttl"
        test_file.write_text("@prefix : <http://example.com/> .")

        # Record it
        tracker.record_input(str(test_file))
        tracker.save()

        # Reload and modify
        tracker2 = IncrementalTracker(output_dir)
        test_file.write_text("@prefix : <http://example.com/> .\n:NewClass a :Class .")

        # Should need update
        assert tracker2.needs_update(str(test_file)) is True

    def test_record_input(self, temp_project: tuple[Path, Path]) -> None:
        """Test recording input file hash."""
        project_dir, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        test_file = project_dir / "test.ttl"
        test_file.write_text("content")

        tracker.record_input(str(test_file))

        assert str(test_file) in tracker.state.input_hashes
        record = tracker.state.input_hashes[str(test_file)]
        assert record.file_path == str(test_file)
        assert record.size == 7
        assert len(record.hash) == 64  # SHA256 hex

    def test_record_outputs(self, temp_project: tuple[Path, Path]) -> None:
        """Test recording transformation outputs."""
        _, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        outputs = ["output/spec.md", "output/index.md"]
        tracker.record_outputs("spec_transform", outputs)

        assert tracker.state.output_files["spec_transform"] == outputs

    def test_save_and_load(self, temp_project: tuple[Path, Path]) -> None:
        """Test saving and loading state."""
        project_dir, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        # Create and record a file
        test_file = project_dir / "test.ttl"
        test_file.write_text("content")
        tracker.record_input(str(test_file))
        tracker.record_outputs("test", ["output/test.md"])
        tracker.save()

        # Load in new tracker
        tracker2 = IncrementalTracker(output_dir)

        assert str(test_file) in tracker2.state.input_hashes
        assert tracker2.state.output_files["test"] == ["output/test.md"]

    def test_cleanup_stale(self, temp_project: tuple[Path, Path]) -> None:
        """Test cleanup of stale state."""
        project_dir, output_dir = temp_project
        tracker = IncrementalTracker(output_dir)

        # Create and record files
        file1 = project_dir / "file1.ttl"
        file2 = project_dir / "file2.ttl"
        file1.write_text("content1")
        file2.write_text("content2")

        # Create output files
        output_file1 = output_dir / "file1.md"
        output_file2 = output_dir / "file2.md"
        output_file1.write_text("output1")
        output_file2.write_text("output2")

        tracker.record_input(str(file1))
        tracker.record_input(str(file2))
        tracker.record_outputs("transform1", [str(output_file1)])
        tracker.record_outputs("transform2", [str(output_file2)])
        tracker.save()

        # Delete file2
        file2.unlink()

        # Cleanup
        tracker.cleanup_stale()

        assert str(file1) in tracker.state.input_hashes
        assert str(file2) not in tracker.state.input_hashes
        assert "transform1" in tracker.state.output_files
        assert "transform2" in tracker.state.output_files


class TestFileHashRecord:
    """Tests for FileHashRecord dataclass."""

    def test_creation(self) -> None:
        """Test creating FileHashRecord."""
        record = FileHashRecord(
            file_path="test.ttl",
            hash="abc123",
            timestamp="2025-12-21T00:00:00",
            size=100,
        )

        assert record.file_path == "test.ttl"
        assert record.hash == "abc123"
        assert record.size == 100
