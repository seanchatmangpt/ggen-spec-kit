"""
Tests for security.encryption module.
"""

from __future__ import annotations

import pytest
from pathlib import Path

from specify_cli.security.encryption import (
    Encryption,
    FileEncryption,
    KeyDerivation,
    AsymmetricEncryption,
    EncryptionError,
    KeyDerivationError,
    CRYPTO_AVAILABLE,
)


@pytest.fixture
def temp_file(tmp_path: Path) -> Path:
    """Create temporary test file."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("This is a test file with sensitive data.")
    return test_file


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography library not available")
class TestKeyDerivation:
    """Tests for KeyDerivation class."""

    def test_derive_key_basic(self) -> None:
        """Test basic key derivation."""
        kdf = KeyDerivation(iterations=100_000)
        key, salt = kdf.derive_key("my-password")

        assert len(key) == 32  # 256 bits
        assert len(salt) == 32

    def test_derive_key_with_salt(self) -> None:
        """Test key derivation with provided salt."""
        kdf = KeyDerivation()
        salt = b"a" * 32
        key1, _ = kdf.derive_key("password", salt)
        key2, _ = kdf.derive_key("password", salt)

        assert key1 == key2  # Same password and salt = same key

    def test_verify_password_correct(self) -> None:
        """Test password verification with correct password."""
        kdf = KeyDerivation()
        key, salt = kdf.derive_key("correct-password")

        assert kdf.verify_password("correct-password", key, salt)

    def test_verify_password_incorrect(self) -> None:
        """Test password verification with incorrect password."""
        kdf = KeyDerivation()
        key, salt = kdf.derive_key("correct-password")

        assert not kdf.verify_password("wrong-password", key, salt)


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography library not available")
class TestEncryption:
    """Tests for Encryption class."""

    def test_encrypt_decrypt_bytes(self) -> None:
        """Test encryption and decryption of bytes."""
        enc = Encryption()
        plaintext = b"sensitive data"
        password = "my-secret-key"

        encrypted = enc.encrypt(plaintext, password)
        decrypted = enc.decrypt(encrypted, password)

        assert decrypted == plaintext

    def test_encrypt_decrypt_string(self) -> None:
        """Test encryption and decryption of strings."""
        enc = Encryption()
        plaintext = "sensitive data"
        password = "my-secret-key"

        encrypted = enc.encrypt(plaintext, password)
        decrypted = enc.decrypt(encrypted, password)

        assert decrypted.decode("utf-8") == plaintext

    def test_encrypt_string_base64(self) -> None:
        """Test string encryption with base64 encoding."""
        enc = Encryption()
        plaintext = "sensitive data"
        password = "my-secret-key"

        encrypted = enc.encrypt_string(plaintext, password)
        decrypted = enc.decrypt_string(encrypted, password)

        assert decrypted == plaintext

    def test_decrypt_with_wrong_password(self) -> None:
        """Test decryption with wrong password fails."""
        enc = Encryption()
        plaintext = b"sensitive data"
        password = "correct-password"

        encrypted = enc.encrypt(plaintext, password)

        with pytest.raises(EncryptionError):
            enc.decrypt(encrypted, "wrong-password")

    def test_generate_key(self) -> None:
        """Test key generation."""
        enc = Encryption()
        key = enc.generate_key()

        assert len(key) == 32  # 256 bits


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography library not available")
class TestFileEncryption:
    """Tests for FileEncryption class."""

    def test_encrypt_decrypt_file(self, temp_file: Path, tmp_path: Path) -> None:
        """Test file encryption and decryption."""
        file_enc = FileEncryption()
        password = "file-password"

        # Encrypt file
        encrypted_file = file_enc.encrypt_file(temp_file, password)
        assert encrypted_file.exists()
        assert encrypted_file.suffix == ".enc"

        # Decrypt file
        decrypted_file = file_enc.decrypt_file(encrypted_file, password)
        assert decrypted_file.exists()

        # Verify content
        assert decrypted_file.read_text() == temp_file.read_text()

    def test_encrypt_file_not_found(self, tmp_path: Path) -> None:
        """Test encrypting non-existent file raises error."""
        file_enc = FileEncryption()
        non_existent = tmp_path / "does-not-exist.txt"

        with pytest.raises(EncryptionError):
            file_enc.encrypt_file(non_existent, "password")

    def test_calculate_file_hash(self, temp_file: Path) -> None:
        """Test file hash calculation."""
        file_enc = FileEncryption()
        hash_value = file_enc.calculate_file_hash(temp_file)

        assert len(hash_value) == 64  # SHA-256 hex digest


@pytest.mark.skipif(not CRYPTO_AVAILABLE, reason="cryptography library not available")
class TestAsymmetricEncryption:
    """Tests for AsymmetricEncryption class."""

    def test_generate_key_pair(self) -> None:
        """Test RSA key pair generation."""
        asym = AsymmetricEncryption(key_size=2048)
        private_key, public_key = asym.generate_key_pair()

        assert b"BEGIN PRIVATE KEY" in private_key
        assert b"BEGIN PUBLIC KEY" in public_key

    def test_encrypt_decrypt(self) -> None:
        """Test asymmetric encryption and decryption."""
        asym = AsymmetricEncryption(key_size=2048)
        private_key, public_key = asym.generate_key_pair()

        plaintext = b"secret message"

        # Encrypt with public key
        encrypted = asym.encrypt_with_public_key(plaintext, public_key)

        # Decrypt with private key
        decrypted = asym.decrypt_with_private_key(encrypted, private_key)

        assert decrypted == plaintext

    def test_encrypt_too_large_data(self) -> None:
        """Test encrypting data too large for RSA."""
        asym = AsymmetricEncryption(key_size=2048)
        private_key, public_key = asym.generate_key_pair()

        # Data too large for RSA encryption
        large_data = b"a" * 500

        with pytest.raises(Exception):  # Should raise cryptography exception
            asym.encrypt_with_public_key(large_data, public_key)
