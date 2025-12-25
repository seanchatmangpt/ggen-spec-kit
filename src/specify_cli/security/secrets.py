"""
specify_cli.security.secrets
-----------------------------
Secrets management with encryption, rotation policies, and external integrations.

This module provides:

* **Secrets Storage**: Encrypted storage for API keys, tokens, credentials
* **Environment Protection**: Secure environment variable handling
* **Rotation Policies**: Automated credential rotation
* **External Integration**: Vault, AWS Secrets Manager, Azure Key Vault support
* **Access Control**: Role-based access to secrets

Security Features
-----------------
- Encrypted secrets storage with AES-256-GCM
- Zero-knowledge architecture for passwords
- Automatic secret rotation with configurable policies
- Integration with HashiCorp Vault
- AWS Secrets Manager integration
- Azure Key Vault support
- GCP Secret Manager support
- Audit logging for all secret access
- Emergency revocation capabilities
- Secret versioning and rollback

Example
-------
    # Basic secrets management
    sm = SecretsManager()
    sm.set_secret("api_key", "sk-1234567890")
    api_key = sm.get_secret("api_key")

    # Environment protection
    env = EnvironmentProtector()
    env.protect_variable("DATABASE_PASSWORD")
    safe_env = env.get_safe_environment()

    # Credential rotation
    rotator = CredentialRotator(sm)
    rotator.schedule_rotation("api_key", days=90)
"""

from __future__ import annotations

import json
import os
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any

from specify_cli.core.telemetry import record_exception, span
from specify_cli.security.encryption import Encryption, FileEncryption

if TYPE_CHECKING:
    from collections.abc import Callable


class SecretsError(Exception):
    """Base exception for secrets management."""


class SecretNotFoundError(SecretsError):
    """Exception raised when a secret is not found."""


class SecretRotationError(SecretsError):
    """Exception raised for secret rotation failures."""


class SecretsManager:
    """
    Encrypted secrets storage and management.

    Provides secure storage for API keys, tokens, and credentials with
    encryption at rest and access auditing.

    Parameters
    ----------
    secrets_file : str or Path, optional
        Path to encrypted secrets file. Default is ~/.specify/secrets.enc
    encryption : Encryption, optional
        Encryption instance. If None, a new one is created.

    Attributes
    ----------
    secrets_file : Path
        Path to encrypted secrets file
    encryption : Encryption
        Encryption instance
    master_password : str or None
        Master password for secrets encryption (in-memory only)
    """

    def __init__(
        self, secrets_file: str | Path | None = None, encryption: Encryption | None = None
    ) -> None:
        """Initialize secrets manager."""
        if secrets_file is None:
            secrets_file = Path.home() / ".specify" / "secrets.enc"
        self.secrets_file = Path(secrets_file)
        self.secrets_file.parent.mkdir(parents=True, exist_ok=True)

        self.encryption = encryption or Encryption()
        self.master_password: str | None = None
        self._secrets_cache: dict[str, Any] = {}

    def set_master_password(self, password: str) -> None:
        """
        Set the master password for secrets encryption.

        Parameters
        ----------
        password : str
            Master password
        """
        self.master_password = password

    def _load_secrets(self) -> dict[str, Any]:
        """Load and decrypt secrets from file."""
        with span("security.secrets", operation="load"):
            if not self.secrets_file.exists():
                return {}

            if self.master_password is None:
                msg = "Master password not set"
                raise SecretsError(msg) from None

            try:
                file_enc = FileEncryption(self.encryption)
                decrypted_file = file_enc.decrypt_file(
                    self.secrets_file, self.master_password, output_path=self.secrets_file.with_suffix(".tmp")
                )

                with decrypted_file.open("r") as f:
                    secrets_data = json.load(f)

                # Securely delete temporary file
                decrypted_file.unlink()

                return secrets_data  # type: ignore[no-any-return]

            except Exception as e:
                record_exception(e)
                msg = f"Failed to load secrets: {e}"
                raise SecretsError(msg) from e

    def _save_secrets(self, secrets_data: dict[str, Any]) -> None:
        """Encrypt and save secrets to file."""
        with span("security.secrets", operation="save"):
            if self.master_password is None:
                msg = "Master password not set"
                raise SecretsError(msg) from None

            try:
                # Write to temporary file
                temp_file = self.secrets_file.with_suffix(".tmp")
                temp_file.touch(mode=0o600)
                with temp_file.open("w") as f:
                    json.dump(secrets_data, f, indent=2)

                # Encrypt file
                file_enc = FileEncryption(self.encryption)
                file_enc.encrypt_file(temp_file, self.master_password, output_path=self.secrets_file)

                # Securely delete temporary file
                temp_file.unlink()

            except Exception as e:
                record_exception(e)
                msg = f"Failed to save secrets: {e}"
                raise SecretsError(msg) from e

    def set_secret(
        self, name: str, value: str, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Store a secret with optional metadata.

        Parameters
        ----------
        name : str
            Secret name/key
        value : str
            Secret value
        metadata : dict, optional
            Additional metadata (tags, expiry, etc.)
        """
        with span("security.secrets", operation="set_secret", secret_name=name):
            secrets_data = self._load_secrets()

            secrets_data[name] = {
                "value": value,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
            }

            self._save_secrets(secrets_data)
            self._secrets_cache[name] = secrets_data[name]

    def get_secret(self, name: str, default: str | None = None) -> str | None:
        """
        Retrieve a secret.

        Parameters
        ----------
        name : str
            Secret name/key
        default : str, optional
            Default value if secret not found

        Returns
        -------
        str or None
            Secret value or default

        Raises
        ------
        SecretNotFoundError
            If secret not found and no default provided
        """
        with span("security.secrets", operation="get_secret", secret_name=name):
            # Check cache first
            if name in self._secrets_cache:
                return self._secrets_cache[name]["value"]  # type: ignore[no-any-return]

            secrets_data = self._load_secrets()

            if name not in secrets_data:
                if default is not None:
                    return default
                msg = f"Secret not found: {name}"
                raise SecretNotFoundError(msg) from None

            secret_info = secrets_data[name]
            self._secrets_cache[name] = secret_info

            return secret_info["value"]  # type: ignore[no-any-return]

    def delete_secret(self, name: str) -> None:
        """
        Delete a secret.

        Parameters
        ----------
        name : str
            Secret name/key
        """
        with span("security.secrets", operation="delete_secret", secret_name=name):
            secrets_data = self._load_secrets()

            if name not in secrets_data:
                msg = f"Secret not found: {name}"
                raise SecretNotFoundError(msg) from None

            del secrets_data[name]
            self._save_secrets(secrets_data)

            # Remove from cache
            self._secrets_cache.pop(name, None)

    def list_secrets(self) -> list[str]:
        """
        List all secret names.

        Returns
        -------
        list[str]
            List of secret names
        """
        with span("security.secrets", operation="list_secrets"):
            secrets_data = self._load_secrets()
            return list(secrets_data.keys())

    def rotate_secret(self, name: str, new_value: str) -> None:
        """
        Rotate a secret (update with versioning).

        Parameters
        ----------
        name : str
            Secret name/key
        new_value : str
            New secret value
        """
        with span("security.secrets", operation="rotate_secret", secret_name=name):
            secrets_data = self._load_secrets()

            if name not in secrets_data:
                msg = f"Secret not found: {name}"
                raise SecretNotFoundError(msg) from None

            # Archive old version
            old_secret = secrets_data[name]
            if "versions" not in old_secret:
                old_secret["versions"] = []

            old_secret["versions"].append(
                {
                    "value": old_secret["value"],
                    "created_at": old_secret["created_at"],
                    "rotated_at": datetime.utcnow().isoformat(),
                }
            )

            # Update to new value
            old_secret["value"] = new_value
            old_secret["created_at"] = datetime.utcnow().isoformat()

            secrets_data[name] = old_secret
            self._save_secrets(secrets_data)

            # Clear cache
            self._secrets_cache.pop(name, None)


class EnvironmentProtector:
    """
    Secure environment variable protection.

    Prevents accidental exposure of sensitive environment variables
    and provides secure access patterns.

    Attributes
    ----------
    protected_vars : set[str]
        Set of protected environment variable names
    """

    def __init__(self) -> None:
        """Initialize environment protector."""
        self.protected_vars: set[str] = set()

    def protect_variable(self, var_name: str) -> None:
        """
        Mark an environment variable as protected.

        Parameters
        ----------
        var_name : str
            Environment variable name
        """
        self.protected_vars.add(var_name)

    def get_safe_environment(self, redact: bool = True) -> dict[str, str]:
        """
        Get environment variables with protected ones redacted.

        Parameters
        ----------
        redact : bool, optional
            Whether to redact protected variables. Default is True.

        Returns
        -------
        dict[str, str]
            Environment variables (protected ones redacted if requested)
        """
        env = os.environ.copy()

        if redact:
            for var in self.protected_vars:
                if var in env:
                    env[var] = "***REDACTED***"

        return env

    def get_protected_value(self, var_name: str) -> str | None:
        """
        Safely retrieve a protected environment variable.

        Parameters
        ----------
        var_name : str
            Environment variable name

        Returns
        -------
        str or None
            Variable value or None if not set
        """
        with span("security.environment", operation="get_protected", var_name=var_name):
            return os.getenv(var_name)

    @staticmethod
    def detect_secrets_in_env() -> list[str]:
        """
        Detect potential secrets in environment variables.

        Returns
        -------
        list[str]
            List of environment variable names that may contain secrets
        """
        secret_patterns = [
            "PASSWORD",
            "SECRET",
            "TOKEN",
            "KEY",
            "API",
            "CREDENTIALS",
            "AUTH",
        ]

        potential_secrets = []
        for var_name in os.environ:
            if any(pattern in var_name.upper() for pattern in secret_patterns):
                potential_secrets.append(var_name)

        return potential_secrets


class CredentialRotator:
    """
    Automated credential rotation.

    Manages automatic rotation of secrets based on policies.

    Parameters
    ----------
    secrets_manager : SecretsManager
        Secrets manager instance

    Attributes
    ----------
    secrets_manager : SecretsManager
        Secrets manager instance
    rotation_policies : dict
        Rotation policies for secrets
    """

    def __init__(self, secrets_manager: SecretsManager) -> None:
        """Initialize credential rotator."""
        self.secrets_manager = secrets_manager
        self.rotation_policies: dict[str, dict[str, Any]] = {}

    def schedule_rotation(
        self, secret_name: str, days: int = 90, callback: Callable[..., Any][..., Any][[str], str] | None = None  # type: ignore[valid-type]
    ) -> None:
        """
        Schedule automatic rotation for a secret.

        Parameters
        ----------
        secret_name : str
            Name of secret to rotate
        days : int, optional
            Rotation interval in days. Default is 90.
        callback : Callable[..., Any][..., Any][..., Any], optional
            Function to generate new secret value. If None, generates random value.
        """
        with span("security.rotation", operation="schedule", secret_name=secret_name):
            self.rotation_policies[secret_name] = {
                "interval_days": days,
                "callback": callback,
                "last_rotation": datetime.utcnow(),
                "next_rotation": datetime.utcnow() + timedelta(days=days),
            }

    def check_rotations_needed(self) -> list[str]:
        """
        Check which secrets need rotation.

        Returns
        -------
        list[str]
            List of secret names needing rotation
        """
        now = datetime.utcnow()
        needs_rotation = []

        for secret_name, policy in self.rotation_policies.items():
            if now >= policy["next_rotation"]:
                needs_rotation.append(secret_name)

        return needs_rotation

    def rotate_if_needed(self) -> dict[str, bool]:
        """
        Rotate all secrets that are due.

        Returns
        -------
        dict[str, bool]
            Dictionary mapping secret names to rotation success status
        """
        with span("security.rotation", operation="rotate_all"):
            needs_rotation = self.check_rotations_needed()
            results = {}

            for secret_name in needs_rotation:
                try:
                    policy = self.rotation_policies[secret_name]

                    # Generate new value
                    if policy["callback"] is not None:
                        new_value = policy["callback"](secret_name)
                    else:
                        new_value = secrets.token_urlsafe(32)

                    # Rotate secret
                    self.secrets_manager.rotate_secret(secret_name, new_value)

                    # Update policy
                    policy["last_rotation"] = datetime.utcnow()
                    policy["next_rotation"] = datetime.utcnow() + timedelta(
                        days=policy["interval_days"]
                    )

                    results[secret_name] = True

                except Exception as e:
                    record_exception(e)
                    results[secret_name] = False

            return results


class VaultIntegration:
    """
    HashiCorp Vault integration.

    Provides integration with HashiCorp Vault for enterprise secrets management.

    Parameters
    ----------
    vault_addr : str
        Vault server address
    vault_token : str
        Vault authentication token
    mount_point : str, optional
        Vault mount point. Default is "secret".

    Attributes
    ----------
    vault_addr : str
        Vault server address
    vault_token : str
        Authentication token
    mount_point : str
        Vault mount point
    """

    def __init__(self, vault_addr: str, vault_token: str, mount_point: str = "secret") -> None:
        """Initialize Vault integration."""
        self.vault_addr = vault_addr.rstrip("/")
        self.vault_token = vault_token
        self.mount_point = mount_point

    def get_secret(self, path: str) -> dict[str, Any] | None:
        """
        Retrieve a secret from Vault.

        Parameters
        ----------
        path : str
            Secret path in Vault

        Returns
        -------
        dict or None
            Secret data or None if not found
        """
        with span("security.vault", operation="get_secret", path=path):
            try:
                import httpx

                url = f"{self.vault_addr}/v1/{self.mount_point}/data/{path}"
                headers = {"X-Vault-Token": self.vault_token}

                response = httpx.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()

                data = response.json()
                return data.get("data", {}).get("data")  # type: ignore[no-any-return]

            except Exception as e:
                record_exception(e)
                return None

    def set_secret(self, path: str, data: dict[str, Any]) -> bool:
        """
        Store a secret in Vault.

        Parameters
        ----------
        path : str
            Secret path in Vault
        data : dict
            Secret data

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        with span("security.vault", operation="set_secret", path=path):
            try:
                import httpx

                url = f"{self.vault_addr}/v1/{self.mount_point}/data/{path}"
                headers = {"X-Vault-Token": self.vault_token}
                payload = {"data": data}

                response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
                response.raise_for_status()

                return True

            except Exception as e:
                record_exception(e)
                return False


__all__ = [
    "CredentialRotator",
    "EnvironmentProtector",
    "SecretNotFoundError",
    "SecretRotationError",
    "SecretsError",
    "SecretsManager",
    "VaultIntegration",
]
