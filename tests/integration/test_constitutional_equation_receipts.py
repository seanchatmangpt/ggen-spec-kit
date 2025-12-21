"""Integration Tests for Constitutional Equation - Receipt Verification
========================================================================

This test suite verifies cryptographic proofs of the constitutional equation:
    spec.md = μ(feature.ttl)

Tests verify:
1. Receipt generation and verification
2. Idempotence: μ∘μ = μ
3. Determinism: Same input → Same output
4. SHA256 cryptographic proofs
5. Stage hash chain integrity
6. Receipt file I/O and serialization

This extends test_constitutional_equation.py with receipt-specific tests.

Test Strategy
-------------
- Uses real files and transformations
- Tests complete μ pipeline end-to-end
- Verifies cryptographic integrity
- Tests receipt persistence and loading
- Minimum 80% coverage target

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
def temp_project() -> Any:
    """Create temporary project directory.

    Yields
    ------
    Path
        Temporary project directory.
    """
    with TemporaryDirectory() as tmpdir:
        project = Path(tmpdir)

        # Create directory structure
        (project / "ontology").mkdir()
        (project / "templates").mkdir()
        (project / "docs").mkdir()

        yield project


@pytest.fixture
def sample_ttl_file(temp_project: Path) -> Path:
    """Create sample TTL input file.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.

    Returns
    -------
    Path
        TTL file path.
    """
    ttl_file = temp_project / "ontology" / "feature.ttl"
    ttl_file.write_text(
        """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sk: <http://spec-kit.io/ontology#> .

sk:AuthenticationFeature a sk:Feature ;
    rdfs:label "User Authentication" ;
    sk:priority "P1" ;
    sk:status "active" ;
    sk:description "Implement user authentication system" .
"""
    )
    return ttl_file


@pytest.fixture
def sample_markdown_file(temp_project: Path) -> Path:
    """Create sample Markdown output file.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.

    Returns
    -------
    Path
        Markdown file path.
    """
    md_file = temp_project / "docs" / "feature.md"
    md_file.write_text(
        """# User Authentication

**Priority**: P1
**Status**: active

## Description

Implement user authentication system
"""
    )
    return md_file


# ============================================================================
# Test: Receipt Generation and Verification
# ============================================================================


@pytest.mark.integration
def test_generate_and_verify_receipt(
    sample_ttl_file: Path,
    sample_markdown_file: Path,
) -> None:
    """Test complete receipt generation and verification workflow.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL input file.
    sample_markdown_file : Path
        Sample Markdown output file.
    """
    # Generate receipt
    stage_outputs = {
        "normalize": sample_ttl_file.read_text(),
        "extract": '{"features": [{"label": "User Authentication"}]}',
        "emit": "# User Authentication\n\n",
        "canonicalize": "# User Authentication\n",
    }

    receipt = generate_receipt(sample_ttl_file, sample_markdown_file, stage_outputs)

    # Verify receipt
    assert verify_receipt(receipt) is True

    # Verify receipt properties
    assert receipt.input_file == str(sample_ttl_file)
    assert receipt.output_file == str(sample_markdown_file)
    assert len(receipt.input_hash) == 64  # SHA256
    assert len(receipt.output_hash) == 64
    assert len(receipt.stages) == 4


@pytest.mark.integration
def test_receipt_detects_modified_input(
    sample_ttl_file: Path,
    sample_markdown_file: Path,
) -> None:
    """Test receipt verification fails when input is modified.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL input file.
    sample_markdown_file : Path
        Sample Markdown output file.
    """
    # Generate receipt with original content
    receipt = generate_receipt(sample_ttl_file, sample_markdown_file, {})

    # Verify original
    assert verify_receipt(receipt) is True

    # Modify input file
    original_content = sample_ttl_file.read_text()
    sample_ttl_file.write_text(original_content + "\n# Modified")

    # Verification should fail
    assert verify_receipt(receipt) is False


@pytest.mark.integration
def test_receipt_detects_modified_output(
    sample_ttl_file: Path,
    sample_markdown_file: Path,
) -> None:
    """Test receipt verification fails when output is modified.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL input file.
    sample_markdown_file : Path
        Sample Markdown output file.
    """
    # Generate receipt
    receipt = generate_receipt(sample_ttl_file, sample_markdown_file, {})

    # Verify original
    assert verify_receipt(receipt) is True

    # Modify output file (simulate manual edit)
    sample_markdown_file.write_text("# Modified Content\n")

    # Verification should fail (constitutional equation violated!)
    assert verify_receipt(receipt) is False


@pytest.mark.integration
def test_receipt_persistence(
    sample_ttl_file: Path,
    sample_markdown_file: Path,
    temp_project: Path,
) -> None:
    """Test receipt can be saved and loaded from JSON.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL input file.
    sample_markdown_file : Path
        Sample Markdown output file.
    temp_project : Path
        Temporary project directory.
    """
    # Generate receipt
    stage_outputs = {
        "normalize": "normalized",
        "extract": "extracted",
        "emit": "emitted",
        "canonicalize": "canonical",
    }
    original = generate_receipt(sample_ttl_file, sample_markdown_file, stage_outputs)

    # Save to file
    receipt_file = temp_project / "receipt.json"
    receipt_file.write_text(original.to_json())

    # Load from file
    loaded = Receipt.from_file(receipt_file)

    # Verify loaded receipt matches original
    assert loaded.input_file == original.input_file
    assert loaded.output_file == original.output_file
    assert loaded.input_hash == original.input_hash
    assert loaded.output_hash == original.output_hash
    assert len(loaded.stages) == len(original.stages)

    # Verify loaded receipt can verify files
    assert verify_receipt(loaded) is True


@pytest.mark.integration
def test_receipt_json_format(
    sample_ttl_file: Path,
    sample_markdown_file: Path,
) -> None:
    """Test receipt JSON format is valid and well-structured.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL input file.
    sample_markdown_file : Path
        Sample Markdown output file.
    """
    receipt = generate_receipt(sample_ttl_file, sample_markdown_file, {})
    json_str = receipt.to_json()

    # Parse JSON
    data = json.loads(json_str)

    # Verify required fields
    assert "timestamp" in data
    assert "input_file" in data
    assert "output_file" in data
    assert "input_hash" in data
    assert "output_hash" in data
    assert "stages" in data
    assert "idempotent" in data

    # Verify types
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["input_hash"], str)
    assert isinstance(data["stages"], list)
    assert isinstance(data["idempotent"], bool)


# ============================================================================
# Test: Stage Hash Chain Integrity
# ============================================================================


@pytest.mark.integration
def test_stage_hash_chain(
    sample_ttl_file: Path,
    sample_markdown_file: Path,
) -> None:
    """Test stage hash chain integrity (output of stage N = input of stage N+1).

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL input file.
    sample_markdown_file : Path
        Sample Markdown output file.
    """
    stage_outputs = {
        "normalize": "stage 1 output",
        "extract": "stage 2 output",
        "emit": "stage 3 output",
        "canonicalize": "stage 4 output",
    }

    receipt = generate_receipt(sample_ttl_file, sample_markdown_file, stage_outputs)

    # Verify chain: μ₅(μ₄(μ₃(μ₂(μ₁(input)))))
    # First stage input = file hash
    assert receipt.stages[0].input_hash == receipt.input_hash

    # Each stage output becomes next stage input
    for i in range(len(receipt.stages) - 1):
        current_output = receipt.stages[i].output_hash
        next_input = receipt.stages[i + 1].input_hash

        assert (
            current_output == next_input
        ), f"Chain broken between {receipt.stages[i].stage} and {receipt.stages[i + 1].stage}"


@pytest.mark.integration
def test_stage_order_enforcement(
    sample_ttl_file: Path,
    sample_markdown_file: Path,
) -> None:
    """Test stages are generated in correct μ₁→μ₂→μ₃→μ₄ order.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL input file.
    sample_markdown_file : Path
        Sample Markdown output file.
    """
    stage_outputs = {
        "normalize": "a",
        "extract": "b",
        "emit": "c",
        "canonicalize": "d",
    }

    receipt = generate_receipt(sample_ttl_file, sample_markdown_file, stage_outputs)

    expected_order = ["normalize", "extract", "emit", "canonicalize"]
    actual_order = [s.stage for s in receipt.stages]

    assert actual_order == expected_order


# ============================================================================
# Test: Idempotence Verification (μ∘μ = μ)
# ============================================================================


@pytest.mark.integration
def test_idempotence_simple_transformation(temp_project: Path) -> None:
    """Test verify_idempotence() with simple transformation.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    input_file = temp_project / "input.txt"
    input_file.write_text("test content")

    def uppercase_transform(path: Path) -> str:
        """Simple deterministic transformation."""
        return path.read_text().upper()

    is_idempotent = verify_idempotence(input_file, uppercase_transform)

    assert is_idempotent is True


@pytest.mark.integration
def test_idempotence_markdown_generation(temp_project: Path) -> None:
    """Test verify_idempotence() with Markdown generation.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    input_file = temp_project / "ontology" / "feature.ttl"
    input_file.write_text(
        """
@prefix sk: <http://spec-kit.io/ontology#> .
sk:F1 a sk:Feature ; sk:priority "P1" .
"""
    )

    def markdown_transform(path: Path) -> str:
        """Deterministic Markdown generation."""
        # Simplified transformation
        content = path.read_text()
        if "sk:F1" in content:
            return "# Feature F1\nPriority: P1\n"
        return "# Unknown\n"

    is_idempotent = verify_idempotence(input_file, markdown_transform)

    assert is_idempotent is True


@pytest.mark.integration
def test_non_idempotent_transformation(temp_project: Path) -> None:
    """Test verify_idempotence() detects non-idempotent transformations.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    import time

    input_file = temp_project / "input.txt"
    input_file.write_text("content")

    def timestamped_transform(_path: Path) -> str:
        """Non-deterministic transformation (includes timestamp)."""
        return f"Generated at {time.time()}"

    is_idempotent = verify_idempotence(input_file, timestamped_transform)

    assert is_idempotent is False


# ============================================================================
# Test: SHA256 Determinism
# ============================================================================


@pytest.mark.integration
def test_sha256_determinism(sample_ttl_file: Path) -> None:
    """Test SHA256 hashing is deterministic.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL file.
    """
    # Hash file multiple times
    hash1 = sha256_file(sample_ttl_file)
    hash2 = sha256_file(sample_ttl_file)
    hash3 = sha256_file(sample_ttl_file)

    assert hash1 == hash2 == hash3


@pytest.mark.integration
def test_sha256_changes_with_content(temp_project: Path) -> None:
    """Test SHA256 changes when content changes.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    test_file = temp_project / "test.txt"

    test_file.write_text("Version 1")
    hash1 = sha256_file(test_file)

    test_file.write_text("Version 2")
    hash2 = sha256_file(test_file)

    assert hash1 != hash2


@pytest.mark.integration
def test_sha256_string_vs_file_consistency(temp_project: Path) -> None:
    """Test sha256_string() and sha256_file() produce same hash for same content.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    content = "Test content for hashing"
    test_file = temp_project / "test.txt"
    test_file.write_text(content)

    string_hash = sha256_string(content)
    file_hash = sha256_file(test_file)

    assert string_hash == file_hash


# ============================================================================
# Test: Real-World Scenarios
# ============================================================================


@pytest.mark.integration
def test_complete_transformation_workflow(temp_project: Path) -> None:
    """Test complete μ transformation workflow with receipt.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    # Create input
    input_file = temp_project / "ontology" / "spec.ttl"
    input_file.write_text(
        """
@prefix sk: <http://spec-kit.io/ontology#> .

sk:UserAuth a sk:Feature ;
    sk:priority "P1" ;
    sk:status "active" .
"""
    )

    # Simulate μ stages
    stage_outputs = {}

    # μ₁ NORMALIZE
    normalized = input_file.read_text()
    stage_outputs["normalize"] = normalized

    # μ₂ EXTRACT (simulate SPARQL)
    stage_outputs["extract"] = '{"features": [{"name": "UserAuth", "priority": "P1"}]}'

    # μ₃ EMIT (simulate Tera)
    stage_outputs["emit"] = "# User Auth\n\nPriority: P1\n\n"

    # μ₄ CANONICALIZE
    stage_outputs["canonicalize"] = "# User Auth\n\nPriority: P1\n"

    # Write output
    output_file = temp_project / "docs" / "spec.md"
    output_file.write_text(stage_outputs["canonicalize"])

    # μ₅ RECEIPT
    receipt = generate_receipt(input_file, output_file, stage_outputs)

    # Verify receipt
    assert verify_receipt(receipt) is True
    assert len(receipt.stages) == 4

    # Save receipt
    receipt_file = output_file.with_suffix(".md.receipt.json")
    receipt_file.write_text(receipt.to_json())

    # Reload and verify
    loaded = Receipt.from_file(receipt_file)
    assert verify_receipt(loaded) is True


@pytest.mark.integration
def test_receipt_detects_tampering(temp_project: Path) -> None:
    """Test receipt detects manual file tampering.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    # Create files
    input_file = temp_project / "input.ttl"
    output_file = temp_project / "output.md"

    input_file.write_text("@prefix sk: <http://spec-kit.io/ontology#> .")
    output_file.write_text("# Generated Output\n")

    # Generate receipt
    receipt = generate_receipt(input_file, output_file, {})
    receipt_file = temp_project / "receipt.json"
    receipt_file.write_text(receipt.to_json())

    # Verify original
    assert verify_receipt(receipt) is True

    # Tamper with output (simulate manual edit)
    output_file.write_text("# Manually Edited Output\n")

    # Receipt should detect tampering
    assert verify_receipt(receipt) is False

    # This proves: output.md ≠ μ(input.ttl)
    # The constitutional equation is violated!


@pytest.mark.integration
def test_multiple_transformations_same_input(
    sample_ttl_file: Path,
    temp_project: Path,
) -> None:
    """Test multiple transformations of same input produce consistent receipts.

    Parameters
    ----------
    sample_ttl_file : Path
        Sample TTL file.
    temp_project : Path
        Temporary project directory.
    """
    # Transform 1: Generate Markdown
    md_output = temp_project / "output1.md"
    md_output.write_text("# Markdown Output\n")
    receipt1 = generate_receipt(sample_ttl_file, md_output, {})

    # Transform 2: Generate Python (same input, different output)
    py_output = temp_project / "output2.py"
    py_output.write_text("# Python Output\n")
    receipt2 = generate_receipt(sample_ttl_file, py_output, {})

    # Both should have same input hash
    assert receipt1.input_hash == receipt2.input_hash

    # But different output hashes
    assert receipt1.output_hash != receipt2.output_hash


# ============================================================================
# Test: Error Cases
# ============================================================================


@pytest.mark.integration
def test_receipt_missing_input_file(temp_project: Path) -> None:
    """Test receipt verification with missing input file.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    input_file = temp_project / "missing_input.ttl"
    output_file = temp_project / "output.md"

    output_file.write_text("Output exists")

    receipt = Receipt(
        timestamp="2025-12-21T12:00:00Z",
        input_file=str(input_file),
        output_file=str(output_file),
        input_hash="abc123",
        output_hash="def456",
        stages=[],
        idempotent=False,
    )

    # Should fail gracefully
    assert verify_receipt(receipt) is False


@pytest.mark.integration
def test_receipt_missing_output_file(temp_project: Path) -> None:
    """Test receipt verification with missing output file.

    Parameters
    ----------
    temp_project : Path
        Temporary project directory.
    """
    input_file = temp_project / "input.ttl"
    output_file = temp_project / "missing_output.md"

    input_file.write_text("Input exists")

    receipt = Receipt(
        timestamp="2025-12-21T12:00:00Z",
        input_file=str(input_file),
        output_file=str(output_file),
        input_hash="abc123",
        output_hash="def456",
        stages=[],
        idempotent=False,
    )

    # Should fail gracefully
    assert verify_receipt(receipt) is False


# ============================================================================
# Run Tests Directly
# ============================================================================


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "integration"])
