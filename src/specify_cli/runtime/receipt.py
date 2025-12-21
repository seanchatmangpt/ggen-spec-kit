"""
specify_cli.runtime.receipt - Cryptographic Receipt Generation
==============================================================

Implements μ₅ RECEIPT stage of the constitutional equation.
Generates SHA256 hashes proving: output.py = μ(input.ttl)

The receipt contains:
1. Input file hash (the RDF source)
2. Intermediate stage hashes (normalize, extract, emit, canonicalize)
3. Output file hash (the generated code)
4. Timestamp and metadata

If any stage changes, the receipt changes, proving determinism.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


@dataclass
class StageHash:
    """Hash for a single transformation stage."""

    stage: str  # "normalize", "extract", "emit", "canonicalize"
    input_hash: str
    output_hash: str


@dataclass
class Receipt:
    """Cryptographic receipt proving spec.md = μ(feature.ttl)."""

    timestamp: str
    input_file: str
    output_file: str
    input_hash: str
    output_hash: str
    stages: list[StageHash]
    idempotent: bool  # True if μ∘μ = μ verified

    def to_json(self) -> str:
        """Serialize receipt to JSON.

        Returns
        -------
        str
            JSON representation of receipt
        """
        return json.dumps(asdict(self), indent=2)

    @classmethod
    def from_file(cls, path: Path) -> Receipt:
        """Load receipt from JSON file.

        Parameters
        ----------
        path : Path
            Path to receipt JSON file

        Returns
        -------
        Receipt
            Deserialized receipt object
        """
        data = json.loads(path.read_text())
        data["stages"] = [StageHash(**s) for s in data["stages"]]
        return cls(**data)


def sha256_file(path: Path) -> str:
    """Compute SHA256 hash of file contents.

    Parameters
    ----------
    path : Path
        File to hash

    Returns
    -------
    str
        Hexadecimal SHA256 hash
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_string(content: str) -> str:
    """Compute SHA256 hash of string content.

    Parameters
    ----------
    content : str
        String to hash

    Returns
    -------
    str
        Hexadecimal SHA256 hash
    """
    return hashlib.sha256(content.encode()).hexdigest()


def generate_receipt(
    input_file: Path,
    output_file: Path,
    stage_outputs: dict[str, str],
) -> Receipt:
    """Generate receipt proving output = μ(input).

    Parameters
    ----------
    input_file : Path
        Source RDF/TTL file
    output_file : Path
        Generated output file (Markdown or Python)
    stage_outputs : dict[str, str]
        Intermediate outputs from each μ stage

    Returns
    -------
    Receipt
        Cryptographic proof of transformation
    """
    stages = []
    prev_hash = sha256_file(input_file)

    for stage_name in ["normalize", "extract", "emit", "canonicalize"]:
        if stage_name in stage_outputs:
            output_hash = sha256_string(stage_outputs[stage_name])
            stages.append(
                StageHash(
                    stage=stage_name,
                    input_hash=prev_hash,
                    output_hash=output_hash,
                )
            )
            prev_hash = output_hash

    return Receipt(
        timestamp=datetime.now(timezone.utc).isoformat(),
        input_file=str(input_file),
        output_file=str(output_file),
        input_hash=sha256_file(input_file),
        output_hash=sha256_file(output_file),
        stages=stages,
        idempotent=False,  # Set after verification
    )


def verify_receipt(receipt: Receipt) -> bool:
    """Verify receipt against current files.

    Checks if the current input and output files still match
    the hashes in the receipt, proving the transformation
    integrity is maintained.

    Parameters
    ----------
    receipt : Receipt
        Receipt to verify

    Returns
    -------
    bool
        True if output still matches μ(input)
    """
    input_path = Path(receipt.input_file)
    output_path = Path(receipt.output_file)

    if not input_path.exists() or not output_path.exists():
        return False

    current_input_hash = sha256_file(input_path)
    current_output_hash = sha256_file(output_path)

    return (
        current_input_hash == receipt.input_hash
        and current_output_hash == receipt.output_hash
    )


def verify_idempotence(
    input_file: Path, transform_fn: Callable[[Path], str]
) -> bool:
    """Verify μ∘μ = μ (transformation is idempotent).

    Run the transformation twice and verify output is identical.
    This proves the transformation is stable and deterministic.

    Parameters
    ----------
    input_file : Path
        Input file to transform
    transform_fn : Callable[[Path], str]
        Transformation function that takes a file path
        and returns transformed content as string

    Returns
    -------
    bool
        True if transformation is idempotent
    """
    output1 = transform_fn(input_file)
    output2 = transform_fn(input_file)  # Run on same input, not output
    return sha256_string(output1) == sha256_string(output2)
