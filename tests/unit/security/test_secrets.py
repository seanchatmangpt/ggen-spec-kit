"""
Tests for security.secrets module.
"""

from __future__ import annotations

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from specify_cli.security.secrets import (
    SecretsManager,
    EnvironmentProtector,
    CredentialRotator,
    VaultIntegration,
    SecretsError,
    SecretNotFoundError,
)


@pytest.fixture
def secrets_file(tmp_path: Path) -> Path:
    """Create temporary secrets file path."""
    return tmp_path / "secrets.enc"


@pytest.fixture
def secrets_manager(secrets_file: Path) -> SecretsManager:
    """Create secrets manager instance."""
    sm = SecretsManager(secrets_file=secrets_file)
    sm.set_master_password("master-password-123")
    return sm


class TestSecretsManager:
    """Tests for SecretsManager class."""

    def test_set_get_secret(self, secrets_manager: SecretsManager) -> None:
        """Test setting and getting a secret."""
        secrets_manager.set_secret("api_key", "sk-1234567890")
        api_key = secrets_manager.get_secret("api_key")

        assert api_key == "sk-1234567890"

    def test_get_secret_not_found(self, secrets_manager: SecretsManager) -> None:
        """Test getting non-existent secret raises error."""
        with pytest.raises(SecretNotFoundError):
            secrets_manager.get_secret("non-existent")

    def test_get_secret_with_default(self, secrets_manager: SecretsManager) -> None:
        """Test getting secret with default value."""
        value = secrets_manager.get_secret("non-existent", default="default-value")
        assert value == "default-value"

    def test_delete_secret(self, secrets_manager: SecretsManager) -> None:
        """Test deleting a secret."""
        secrets_manager.set_secret("temp_secret", "temp-value")
        secrets_manager.delete_secret("temp_secret")

        with pytest.raises(SecretNotFoundError):
            secrets_manager.get_secret("temp_secret")

    def test_list_secrets(self, secrets_manager: SecretsManager) -> None:
        """Test listing all secrets."""
        secrets_manager.set_secret("secret1", "value1")
        secrets_manager.set_secret("secret2", "value2")

        secrets = secrets_manager.list_secrets()
        assert "secret1" in secrets
        assert "secret2" in secrets

    def test_rotate_secret(self, secrets_manager: SecretsManager) -> None:
        """Test secret rotation."""
        secrets_manager.set_secret("rotatable", "old-value")
        secrets_manager.rotate_secret("rotatable", "new-value")

        value = secrets_manager.get_secret("rotatable")
        assert value == "new-value"

    def test_set_secret_with_metadata(self, secrets_manager: SecretsManager) -> None:
        """Test setting secret with metadata."""
        metadata = {"environment": "production", "region": "us-east-1"}
        secrets_manager.set_secret("api_key", "sk-123", metadata=metadata)

        # Secret should be retrievable
        value = secrets_manager.get_secret("api_key")
        assert value == "sk-123"

    def test_no_master_password(self, secrets_file: Path) -> None:
        """Test operations without master password fail."""
        sm = SecretsManager(secrets_file=secrets_file)

        with pytest.raises(SecretsError):
            sm.set_secret("key", "value")


class TestEnvironmentProtector:
    """Tests for EnvironmentProtector class."""

    def test_protect_variable(self) -> None:
        """Test protecting environment variable."""
        protector = EnvironmentProtector()
        protector.protect_variable("DATABASE_PASSWORD")

        assert "DATABASE_PASSWORD" in protector.protected_vars

    def test_get_safe_environment(self) -> None:
        """Test getting safe environment."""
        import os
        os.environ["DATABASE_PASSWORD"] = "secret123"

        protector = EnvironmentProtector()
        protector.protect_variable("DATABASE_PASSWORD")

        safe_env = protector.get_safe_environment(redact=True)
        assert safe_env["DATABASE_PASSWORD"] == "***REDACTED***"

        # Clean up
        del os.environ["DATABASE_PASSWORD"]

    def test_get_protected_value(self) -> None:
        """Test getting protected value."""
        import os
        os.environ["API_KEY"] = "secret-key"

        protector = EnvironmentProtector()
        value = protector.get_protected_value("API_KEY")

        assert value == "secret-key"

        # Clean up
        del os.environ["API_KEY"]

    def test_detect_secrets_in_env(self) -> None:
        """Test detecting potential secrets in environment."""
        import os
        os.environ["MY_SECRET_KEY"] = "secret"
        os.environ["REGULAR_VAR"] = "value"

        secrets = EnvironmentProtector.detect_secrets_in_env()

        assert "MY_SECRET_KEY" in secrets
        assert "REGULAR_VAR" not in secrets

        # Clean up
        del os.environ["MY_SECRET_KEY"]
        del os.environ["REGULAR_VAR"]


class TestCredentialRotator:
    """Tests for CredentialRotator class."""

    def test_schedule_rotation(self, secrets_manager: SecretsManager) -> None:
        """Test scheduling secret rotation."""
        rotator = CredentialRotator(secrets_manager)
        rotator.schedule_rotation("api_key", days=90)

        assert "api_key" in rotator.rotation_policies

    def test_check_rotations_needed_none(self, secrets_manager: SecretsManager) -> None:
        """Test checking rotations when none needed."""
        rotator = CredentialRotator(secrets_manager)
        rotator.schedule_rotation("api_key", days=90)

        needs_rotation = rotator.check_rotations_needed()
        assert len(needs_rotation) == 0

    def test_rotate_with_callback(self, secrets_manager: SecretsManager) -> None:
        """Test rotation with custom callback."""
        secrets_manager.set_secret("rotatable", "old-value")

        def custom_generator(name: str) -> str:
            return f"new-generated-value-for-{name}"

        rotator = CredentialRotator(secrets_manager)
        rotator.schedule_rotation("rotatable", days=0, callback=custom_generator)

        # Force rotation by setting next_rotation to past
        from datetime import datetime, timedelta
        rotator.rotation_policies["rotatable"]["next_rotation"] = (
            datetime.utcnow() - timedelta(days=1)
        )

        results = rotator.rotate_if_needed()
        assert results["rotatable"] is True

        value = secrets_manager.get_secret("rotatable")
        assert value == "new-generated-value-for-rotatable"


class TestVaultIntegration:
    """Tests for VaultIntegration class."""

    def test_init(self) -> None:
        """Test VaultIntegration initialization."""
        vault = VaultIntegration(
            vault_addr="http://localhost:8200",
            vault_token="test-token",
        )

        assert vault.vault_addr == "http://localhost:8200"
        assert vault.vault_token == "test-token"

    def test_get_secret_not_found(self) -> None:
        """Test getting non-existent secret returns None."""
        vault = VaultIntegration(
            vault_addr="http://localhost:8200",
            vault_token="test-token",
        )

        # This will fail to connect, returning None
        secret = vault.get_secret("non-existent")
        assert secret is None
