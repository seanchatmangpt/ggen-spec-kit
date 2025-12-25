"""
Tests for security.signing module.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from specify_cli.security.signing import (
    ArtifactSigner,
    SignatureVerifier,
    SigningError,
    CRYPTO_AVAILABLE,
)


@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """Create temporary test file."""
    test_file = tmp_path / "artifact.tar.gz"
    test_file.write_bytes(b"This is a test artifact for signing.")
    return test_file


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography library not available")
class TestArtifactSigner:
    """Tests for ArtifactSigner class."""

    def test_generate_key_pair_rsa(self) -> None:
        """Test RSA key pair generation."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        assert b"BEGIN PRIVATE KEY" in private_key
        assert b"BEGIN PUBLIC KEY" in public_key

    def test_generate_key_pair_ecdsa(self) -> None:
        """Test ECDSA key pair generation."""
        signer = ArtifactSigner(algorithm="ecdsa")
        private_key, public_key = signer.generate_key_pair()

        assert b"BEGIN PRIVATE KEY" in private_key
        assert b"BEGIN PUBLIC KEY" in public_key

    def test_sign_data_rsa(self) -> None:
        """Test RSA data signing."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        data = b"important data to sign"
        signature = signer.sign_data(data, private_key)

        assert len(signature) > 0

    def test_sign_data_ecdsa(self) -> None:
        """Test ECDSA data signing."""
        signer = ArtifactSigner(algorithm="ecdsa")
        private_key, public_key = signer.generate_key_pair()

        data = b"important data to sign"
        signature = signer.sign_data(data, private_key)

        assert len(signature) > 0

    def test_sign_file(self, temp_file: Path, tmp_path: Path) -> None:
        """Test file signing."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        signature_file = signer.sign_file(temp_file, private_key)

        assert signature_file.exists()
        assert signature_file.suffix == ".sig"

    def test_sign_file_not_found(self, tmp_path: Path) -> None:
        """Test signing non-existent file raises error."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        non_existent = tmp_path / "does-not-exist.txt"

        with pytest.raises(SigningError):
            signer.sign_file(non_existent, private_key)

    def test_calculate_hash(self) -> None:
        """Test hash calculation."""
        signer = ArtifactSigner()
        data = b"test data"
        hash_value = signer.calculate_hash(data)

        assert len(hash_value) == 64  # SHA-256 hex digest


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography library not available")
class TestSignatureVerifier:
    """Tests for SignatureVerifier class."""

    def test_verify_signature_rsa_valid(self) -> None:
        """Test RSA signature verification with valid signature."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        data = b"important data"
        signature = signer.sign_data(data, private_key)

        verifier = SignatureVerifier(algorithm="rsa")
        is_valid = verifier.verify_signature(data, signature, public_key)

        assert is_valid

    def test_verify_signature_rsa_invalid_data(self) -> None:
        """Test RSA signature verification with tampered data."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        original_data = b"important data"
        signature = signer.sign_data(original_data, private_key)

        tampered_data = b"tampered data"

        verifier = SignatureVerifier(algorithm="rsa")
        is_valid = verifier.verify_signature(tampered_data, signature, public_key)

        assert not is_valid

    def test_verify_signature_ecdsa_valid(self) -> None:
        """Test ECDSA signature verification with valid signature."""
        signer = ArtifactSigner(algorithm="ecdsa")
        private_key, public_key = signer.generate_key_pair()

        data = b"important data"
        signature = signer.sign_data(data, private_key)

        verifier = SignatureVerifier(algorithm="ecdsa")
        is_valid = verifier.verify_signature(data, signature, public_key)

        assert is_valid

    def test_verify_file_signature_valid(self, temp_file: Path) -> None:
        """Test file signature verification with valid signature."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        # Sign file
        signature_file = signer.sign_file(temp_file, private_key)

        # Verify signature
        verifier = SignatureVerifier(algorithm="rsa")
        is_valid = verifier.verify_file_signature(temp_file, public_key)

        assert is_valid

    def test_verify_file_signature_tampered(self, temp_file: Path) -> None:
        """Test file signature verification with tampered file."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        # Sign file
        signature_file = signer.sign_file(temp_file, private_key)

        # Tamper with file
        temp_file.write_bytes(b"tampered content")

        # Verify signature (should fail)
        verifier = SignatureVerifier(algorithm="rsa")
        is_valid = verifier.verify_file_signature(temp_file, public_key)

        assert not is_valid

    def test_verify_file_signature_not_found(self, tmp_path: Path) -> None:
        """Test verifying signature for non-existent file."""
        signer = ArtifactSigner(algorithm="rsa", key_size=2048)
        private_key, public_key = signer.generate_key_pair()

        non_existent = tmp_path / "does-not-exist.txt"

        verifier = SignatureVerifier(algorithm="rsa")
        is_valid = verifier.verify_file_signature(non_existent, public_key)

        assert not is_valid
