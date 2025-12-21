"""
Unit Tests for Receipt Module - Cryptographic Proof of Transformations
========================================================================

Tests verify the μ₅ RECEIPT stage of the constitutional equation.

Coverage:
- Receipt generation (generate_receipt)
- Receipt verification (verify_receipt)
- Idempotence verification (verify_idempotence)
- SHA256 hashing (sha256_file, sha256_string)
- Receipt serialization (to_json, from_file)

The receipt provides cryptographic proof that:
    output.py = μ(input.ttl)

Test Strategy
-------------
- 100% type hints and comprehensive docstrings
- Tests both success and failure paths
- Tests edge cases (missing files, invalid receipts)
- Minimum 80% coverage target
- Uses temporary files for isolation

Author: Claude Code
Date: 2025-12-21
"""

from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest

from specify_cli.runtime.receipt import (
    Receipt,
    StageHash,
    generate_receipt,
    sha256_file,
    sha256_string,
    verify_idempotence,
    verify_receipt,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def temp_dir() -> Any:
    """Create temporary directory for testing.

    Yields
    ------
    Path
        Temporary directory path.
    """
    with TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_input_file(temp_dir: Path) -> Path:
    """Create sample input file.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.

    Returns
    -------
    Path
        Input file path.
    """
    input_file = temp_dir / "input.ttl"
    input_file.write_text(
        """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix sk: <http://spec-kit.io/ontology#> .

sk:TestFeature a sk:Feature ;
    sk:priority "P1" .
"""
    )
    return input_file


@pytest.fixture
def sample_output_file(temp_dir: Path) -> Path:
    """Create sample output file.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.

    Returns
    -------
    Path
        Output file path.
    """
    output_file = temp_dir / "output.md"
    output_file.write_text("# Test Feature\n\nPriority: P1\n")
    return output_file


@pytest.fixture
def sample_stage_outputs() -> dict[str, str]:
    """Create sample stage outputs.

    Returns
    -------
    dict[str, str]
        Stage outputs for transformation.
    """
    return {
        "normalize": "normalized RDF content",
        "extract": '{"features": [{"name": "TestFeature"}]}',
        "emit": "# Test Feature\n\n",
        "canonicalize": "# Test Feature\n",
    }


# ============================================================================
# Test: SHA256 Hashing Functions
# ============================================================================


def test_sha256_string_basic() -> None:
    """Test sha256_string() with basic string."""
    content = "hello world"
    hash_value = sha256_string(content)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64  # SHA256 produces 64 hex characters
    assert hash_value == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_sha256_string_empty() -> None:
    """Test sha256_string() with empty string."""
    hash_value = sha256_string("")

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64
    # SHA256 of empty string
    assert hash_value == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_sha256_string_unicode() -> None:
    """Test sha256_string() with Unicode content."""
    content = "Hello 🌍 World! 日本語 Ελληνικά"
    hash_value = sha256_string(content)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


def test_sha256_string_deterministic() -> None:
    """Test sha256_string() produces deterministic output."""
    content = "test content"

    hash1 = sha256_string(content)
    hash2 = sha256_string(content)

    assert hash1 == hash2


def test_sha256_file_basic(sample_input_file: Path) -> None:
    """Test sha256_file() with basic file.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    """
    hash_value = sha256_file(sample_input_file)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


def test_sha256_file_deterministic(sample_input_file: Path) -> None:
    """Test sha256_file() produces deterministic output.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    """
    hash1 = sha256_file(sample_input_file)
    hash2 = sha256_file(sample_input_file)

    assert hash1 == hash2


def test_sha256_file_changes_with_content(temp_dir: Path) -> None:
    """Test sha256_file() changes when file content changes.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    test_file = temp_dir / "test.txt"

    test_file.write_text("content v1")
    hash1 = sha256_file(test_file)

    test_file.write_text("content v2")
    hash2 = sha256_file(test_file)

    assert hash1 != hash2


# ============================================================================
# Test: StageHash Dataclass
# ============================================================================


def test_stage_hash_creation() -> None:
    """Test StageHash dataclass creation."""
    stage = StageHash(
        stage="normalize",
        input_hash="abc123",
        output_hash="def456",
    )

    assert stage.stage == "normalize"
    assert stage.input_hash == "abc123"
    assert stage.output_hash == "def456"


def test_stage_hash_all_stages() -> None:
    """Test StageHash for all μ stages."""
    stages = ["normalize", "extract", "emit", "canonicalize"]

    for stage_name in stages:
        stage = StageHash(
            stage=stage_name,
            input_hash="input",
            output_hash="output",
        )
        assert stage.stage == stage_name


# ============================================================================
# Test: Receipt Dataclass
# ============================================================================


def test_receipt_creation() -> None:
    """Test Receipt dataclass creation."""
    receipt = Receipt(
        timestamp="2025-12-21T12:00:00Z",
        input_file="input.ttl",
        output_file="output.md",
        input_hash="abc123",
        output_hash="def456",
        stages=[],
        idempotent=False,
    )

    assert receipt.timestamp == "2025-12-21T12:00:00Z"
    assert receipt.input_file == "input.ttl"
    assert receipt.output_file == "output.md"
    assert receipt.input_hash == "abc123"
    assert receipt.output_hash == "def456"
    assert len(receipt.stages) == 0
    assert receipt.idempotent is False


def test_receipt_to_json() -> None:
    """Test Receipt serialization to JSON."""
    stage = StageHash(stage="normalize", input_hash="abc", output_hash="def")
    receipt = Receipt(
        timestamp="2025-12-21T12:00:00Z",
        input_file="input.ttl",
        output_file="output.md",
        input_hash="abc123",
        output_hash="def456",
        stages=[stage],
        idempotent=True,
    )

    json_str = receipt.to_json()

    assert isinstance(json_str, str)
    assert "timestamp" in json_str
    assert "input_file" in json_str
    assert "stages" in json_str

    # Verify it's valid JSON
    data = json.loads(json_str)
    assert data["timestamp"] == "2025-12-21T12:00:00Z"
    assert data["idempotent"] is True
    assert len(data["stages"]) == 1


def test_receipt_from_file(temp_dir: Path) -> None:
    """Test Receipt deserialization from file.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    receipt_file = temp_dir / "receipt.json"
    receipt_data = {
        "timestamp": "2025-12-21T12:00:00Z",
        "input_file": "input.ttl",
        "output_file": "output.md",
        "input_hash": "abc123",
        "output_hash": "def456",
        "stages": [
            {"stage": "normalize", "input_hash": "abc", "output_hash": "def"},
        ],
        "idempotent": True,
    }
    receipt_file.write_text(json.dumps(receipt_data))

    receipt = Receipt.from_file(receipt_file)

    assert receipt.timestamp == "2025-12-21T12:00:00Z"
    assert receipt.input_file == "input.ttl"
    assert receipt.idempotent is True
    assert len(receipt.stages) == 1
    assert receipt.stages[0].stage == "normalize"


def test_receipt_round_trip(temp_dir: Path) -> None:
    """Test Receipt serialization round-trip.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    receipt_file = temp_dir / "receipt.json"

    # Create receipt
    stage = StageHash(stage="normalize", input_hash="abc", output_hash="def")
    original = Receipt(
        timestamp="2025-12-21T12:00:00Z",
        input_file="input.ttl",
        output_file="output.md",
        input_hash="abc123",
        output_hash="def456",
        stages=[stage],
        idempotent=True,
    )

    # Serialize
    receipt_file.write_text(original.to_json())

    # Deserialize
    loaded = Receipt.from_file(receipt_file)

    assert loaded.timestamp == original.timestamp
    assert loaded.input_file == original.input_file
    assert loaded.output_file == original.output_file
    assert loaded.input_hash == original.input_hash
    assert loaded.output_hash == original.output_hash
    assert loaded.idempotent == original.idempotent
    assert len(loaded.stages) == len(original.stages)


# ============================================================================
# Test: Receipt Generation
# ============================================================================


def test_generate_receipt_basic(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test generate_receipt() with valid inputs.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    assert isinstance(receipt, Receipt)
    assert receipt.input_file == str(sample_input_file)
    assert receipt.output_file == str(sample_output_file)
    assert len(receipt.input_hash) == 64  # SHA256
    assert len(receipt.output_hash) == 64
    assert len(receipt.stages) == 4  # normalize, extract, emit, canonicalize


def test_generate_receipt_stage_sequence(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test generate_receipt() produces correct stage sequence.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    expected_stages = ["normalize", "extract", "emit", "canonicalize"]
    actual_stages = [s.stage for s in receipt.stages]

    assert actual_stages == expected_stages


def test_generate_receipt_stage_hashing(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test generate_receipt() computes correct stage hashes.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    # First stage input should be input file hash
    assert receipt.stages[0].input_hash == receipt.input_hash

    # Each stage output becomes next stage input
    for i in range(len(receipt.stages) - 1):
        current_output = receipt.stages[i].output_hash
        next_input = receipt.stages[i + 1].input_hash
        assert current_output == next_input


def test_generate_receipt_partial_stages(
    sample_input_file: Path,
    sample_output_file: Path,
) -> None:
    """Test generate_receipt() with partial stage outputs.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    """
    partial_outputs = {
        "normalize": "normalized content",
        "extract": "extracted data",
        # Missing emit and canonicalize
    }

    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        partial_outputs,
    )

    assert len(receipt.stages) == 2  # Only normalize and extract
    assert receipt.stages[0].stage == "normalize"
    assert receipt.stages[1].stage == "extract"


def test_generate_receipt_timestamp_format(
    sample_input_file: Path,
    sample_output_file: Path,
) -> None:
    """Test generate_receipt() produces ISO 8601 timestamp.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    """
    receipt = generate_receipt(sample_input_file, sample_output_file, {})

    # Should be ISO 8601 format with UTC timezone
    assert "T" in receipt.timestamp
    assert receipt.timestamp.endswith("Z") or "+" in receipt.timestamp


# ============================================================================
# Test: Receipt Verification
# ============================================================================


def test_verify_receipt_valid(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test verify_receipt() with valid receipt.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    is_valid = verify_receipt(receipt)

    assert is_valid is True


def test_verify_receipt_modified_input(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test verify_receipt() fails when input file is modified.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    # Modify input file
    sample_input_file.write_text("modified content")

    is_valid = verify_receipt(receipt)

    assert is_valid is False


def test_verify_receipt_modified_output(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test verify_receipt() fails when output file is modified.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    # Modify output file
    sample_output_file.write_text("modified output")

    is_valid = verify_receipt(receipt)

    assert is_valid is False


def test_verify_receipt_missing_input(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test verify_receipt() fails when input file is missing.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    # Delete input file
    sample_input_file.unlink()

    is_valid = verify_receipt(receipt)

    assert is_valid is False


def test_verify_receipt_missing_output(
    sample_input_file: Path,
    sample_output_file: Path,
    sample_stage_outputs: dict[str, str],
) -> None:
    """Test verify_receipt() fails when output file is missing.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    sample_stage_outputs : dict[str, str]
        Sample stage outputs.
    """
    receipt = generate_receipt(
        sample_input_file,
        sample_output_file,
        sample_stage_outputs,
    )

    # Delete output file
    sample_output_file.unlink()

    is_valid = verify_receipt(receipt)

    assert is_valid is False


# ============================================================================
# Test: Idempotence Verification
# ============================================================================


def test_verify_idempotence_true(temp_dir: Path) -> None:
    """Test verify_idempotence() with idempotent transformation.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    input_file = temp_dir / "input.txt"
    input_file.write_text("test content")

    def transform(_path: Path) -> str:
        """Deterministic transformation."""
        return "transformed content"

    is_idempotent = verify_idempotence(input_file, transform)

    assert is_idempotent is True


def test_verify_idempotence_false(temp_dir: Path) -> None:
    """Test verify_idempotence() with non-idempotent transformation.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    import time

    input_file = temp_dir / "input.txt"
    input_file.write_text("test content")

    def transform(_path: Path) -> str:
        """Non-deterministic transformation (includes timestamp)."""
        return f"transformed at {time.time()}"

    is_idempotent = verify_idempotence(input_file, transform)

    assert is_idempotent is False


def test_verify_idempotence_with_file_read(temp_dir: Path) -> None:
    """Test verify_idempotence() with transformation that reads file.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    input_file = temp_dir / "input.txt"
    input_file.write_text("hello")

    def transform(path: Path) -> str:
        """Transformation that reads and uppercases."""
        return path.read_text().upper()

    is_idempotent = verify_idempotence(input_file, transform)

    assert is_idempotent is True


def test_verify_idempotence_complex_transformation(temp_dir: Path) -> None:
    """Test verify_idempotence() with complex transformation.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    input_file = temp_dir / "input.ttl"
    input_file.write_text(
        """
@prefix sk: <http://spec-kit.io/ontology#> .
sk:Feature1 a sk:Feature .
"""
    )

    def transform(path: Path) -> str:
        """Complex but deterministic transformation."""
        content = path.read_text()
        lines = sorted(content.strip().split("\n"))
        return "\n".join(lines) + "\n"

    is_idempotent = verify_idempotence(input_file, transform)

    assert is_idempotent is True


# ============================================================================
# Test: Edge Cases and Error Handling
# ============================================================================


def test_receipt_with_empty_stages(
    sample_input_file: Path,
    sample_output_file: Path,
) -> None:
    """Test generate_receipt() with no stage outputs.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    """
    receipt = generate_receipt(sample_input_file, sample_output_file, {})

    assert len(receipt.stages) == 0
    assert receipt.input_hash  # Should still have input/output hashes
    assert receipt.output_hash


def test_receipt_with_binary_files(temp_dir: Path) -> None:
    """Test generate_receipt() with binary files.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    binary_file = temp_dir / "binary.bin"
    binary_file.write_bytes(b"\x00\x01\x02\x03\xff\xfe")

    output_file = temp_dir / "output.txt"
    output_file.write_text("output")

    receipt = generate_receipt(binary_file, output_file, {})

    assert len(receipt.input_hash) == 64
    assert len(receipt.output_hash) == 64


def test_sha256_file_with_large_file(temp_dir: Path) -> None:
    """Test sha256_file() with large file.

    Parameters
    ----------
    temp_dir : Path
        Temporary directory.
    """
    large_file = temp_dir / "large.txt"
    large_file.write_text("x" * 1_000_000)  # 1MB

    hash_value = sha256_file(large_file)

    assert isinstance(hash_value, str)
    assert len(hash_value) == 64


def test_receipt_idempotent_flag(
    sample_input_file: Path,
    sample_output_file: Path,
) -> None:
    """Test Receipt.idempotent flag defaults to False.

    Parameters
    ----------
    sample_input_file : Path
        Sample input file.
    sample_output_file : Path
        Sample output file.
    """
    receipt = generate_receipt(sample_input_file, sample_output_file, {})

    assert receipt.idempotent is False


# ============================================================================
# Run Tests Directly
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
