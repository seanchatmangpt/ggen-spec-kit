"""
Comprehensive security integration examples for spec-kit.

This file demonstrates how to use all security features in a real-world application.
"""

from __future__ import annotations

import os
from pathlib import Path

# Import all security components
from specify_cli.security import (
    # Encryption
    Encryption,
    FileEncryption,
    KeyDerivation,
    # Secrets
    SecretsManager,
    EnvironmentProtector,
    CredentialRotator,
    # Audit
    AuditLogger,
    SecurityEvent,
    ComplianceLogger,
    # Validation
    Validator,
    PathValidator,
    InputSanitizer,
    InjectionPrevention,
    # Signing
    ArtifactSigner,
    SignatureVerifier,
    # Certificates
    CertificateManager,
    CertificateValidator,
    # Rate Limiting
    RateLimiter,
    AdaptiveRateLimiter,
)


class SecureApplication:
    """Example secure application using all security features."""

    def __init__(self) -> None:
        """Initialize secure application with all security components."""
        # Encryption
        self.encryption = Encryption()
        self.file_encryption = FileEncryption()

        # Secrets management
        self.secrets = SecretsManager()
        self.secrets.set_master_password(os.getenv("MASTER_PASSWORD", "default-master-password"))

        # Audit logging
        self.audit = AuditLogger()
        self.compliance = ComplianceLogger(self.audit)

        # Validation
        self.validator = Validator()
        self.path_validator = PathValidator(base_dir=Path.cwd())
        self.sanitizer = InputSanitizer()
        self.injection_prevention = InjectionPrevention()

        # Signing
        self.signer = ArtifactSigner(algorithm="rsa", key_size=4096)
        self.verifier = SignatureVerifier(algorithm="rsa")

        # Certificates
        self.cert_manager = CertificateManager()
        self.cert_validator = CertificateValidator()

        # Rate limiting
        self.rate_limiter = AdaptiveRateLimiter(base_rate=100, interval=60)

    def secure_user_login(self, username: str, password: str, ip_address: str) -> bool:
        """
        Secure user login with validation, rate limiting, and audit logging.

        Parameters
        ----------
        username : str
            Username to authenticate
        password : str
            Password to verify
        ip_address : str
            Client IP address

        Returns
        -------
        bool
            True if login successful, False otherwise
        """
        # Rate limiting
        if not self.rate_limiter.allow_request(ip_address):
            self.audit.log_authentication(
                user_id=username,
                success=False,
                ip_address=ip_address,
                metadata={"reason": "rate_limited"},
            )
            return False

        # Input validation
        try:
            username = self.validator.validate_pattern(
                username, r"^[a-zA-Z0-9_]{3,32}$"
            )
        except Exception as e:
            self.audit.log_authentication(
                user_id=username,
                success=False,
                ip_address=ip_address,
                metadata={"reason": "invalid_username"},
            )
            return False

        # Verify password (from encrypted storage)
        try:
            stored_hash = self.secrets.get_secret(f"user:{username}:password_hash")
            kdf = KeyDerivation()

            # In production, retrieve salt from user record
            key, salt = kdf.derive_key(password)

            # Compare with stored hash
            is_valid = kdf.verify_password(password, stored_hash.encode(), salt)

            if is_valid:
                self.audit.log_authentication(
                    user_id=username,
                    success=True,
                    ip_address=ip_address,
                )
                return True
            else:
                self.audit.log_authentication(
                    user_id=username,
                    success=False,
                    ip_address=ip_address,
                    metadata={"reason": "invalid_password"},
                )
                self.rate_limiter.record_error()
                return False

        except Exception as e:
            self.audit.log_event(
                "authentication.error",
                severity="high",
                user_id=username,
                metadata={"error": str(e)},
            )
            return False

    def secure_file_upload(
        self, file_path: str, user_id: str, encrypt: bool = True
    ) -> Path | None:
        """
        Secure file upload with validation, encryption, and signing.

        Parameters
        ----------
        file_path : str
            Path to file to upload
        user_id : str
            User uploading file
        encrypt : bool, optional
            Whether to encrypt file. Default is True.

        Returns
        -------
        Path or None
            Path to processed file, or None on failure
        """
        try:
            # Validate file path
            safe_path = self.path_validator.validate_path(
                file_path,
                must_exist=True,
                allow_symlinks=False,
            )

            # Validate filename
            filename = self.path_validator.validate_filename(
                safe_path.name,
                allowed_extensions=[".txt", ".pdf", ".jpg", ".png"],
            )

            # Log data access
            self.audit.log_data_access(
                user_id=user_id,
                resource=str(safe_path),
                action="upload",
                authorized=True,
            )

            # Encrypt file if requested
            if encrypt:
                password = self.secrets.get_secret("file_encryption_key")
                encrypted_path = self.file_encryption.encrypt_file(safe_path, password)
                safe_path = encrypted_path

            # Sign file for integrity
            private_key, public_key = self.signer.generate_key_pair()
            signature_path = self.signer.sign_file(safe_path, private_key)

            # Store public key for verification
            self.secrets.set_secret(
                f"file:{safe_path.name}:public_key",
                public_key.decode("ascii"),
            )

            return safe_path

        except Exception as e:
            self.audit.log_event(
                "file.upload.error",
                severity="high",
                user_id=user_id,
                metadata={"error": str(e), "file": file_path},
            )
            return None

    def secure_api_request(
        self, endpoint: str, user_id: str, data: dict[str, str]
    ) -> dict[str, str] | None:
        """
        Process secure API request with validation and sanitization.

        Parameters
        ----------
        endpoint : str
            API endpoint
        user_id : str
            User making request
        data : dict
            Request data

        Returns
        -------
        dict or None
            Sanitized data, or None on failure
        """
        try:
            # Validate endpoint
            endpoint = self.validator.validate_pattern(
                endpoint, r"^/api/[a-z_/]+$"
            )

            # Sanitize all string values
            sanitized_data = {}
            for key, value in data.items():
                # Detect potential injections
                if self.injection_prevention.detect_sql_injection(value):
                    raise ValueError(f"SQL injection detected in {key}")

                if self.injection_prevention.detect_xss(value):
                    raise ValueError(f"XSS detected in {key}")

                # Sanitize value
                sanitized_data[key] = self.sanitizer.sanitize_html(value)

            # Log API access
            self.audit.log_user_action(
                user_id=user_id,
                action="api_request",
                resource=endpoint,
                result="success",
            )

            return sanitized_data

        except Exception as e:
            self.audit.log_event(
                "api.request.error",
                severity="medium",
                user_id=user_id,
                metadata={"error": str(e), "endpoint": endpoint},
            )
            return None

    def secure_data_deletion(self, user_id: str, data_category: str) -> bool:
        """
        Secure data deletion with GDPR compliance logging.

        Parameters
        ----------
        user_id : str
            User whose data to delete
        data_category : str
            Category of data to delete

        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            # Log GDPR data deletion
            self.compliance.log_gdpr_event(
                "data.deletion",
                subject_id=user_id,
                data_category=data_category,
                legal_basis="right_to_be_forgotten",
            )

            # Delete user secrets
            secrets_to_delete = [
                s for s in self.secrets.list_secrets() if s.startswith(f"user:{user_id}:")
            ]

            for secret in secrets_to_delete:
                self.secrets.delete_secret(secret)

            # Log completion
            self.audit.log_event(
                "gdpr.data_deletion.complete",
                severity="medium",
                user_id=user_id,
                metadata={"category": data_category, "secrets_deleted": len(secrets_to_delete)},
            )

            return True

        except Exception as e:
            self.audit.log_event(
                "gdpr.data_deletion.error",
                severity="high",
                user_id=user_id,
                metadata={"error": str(e)},
            )
            return False

    def generate_compliance_report(self, framework: str, days: int = 30) -> dict:
        """
        Generate compliance report.

        Parameters
        ----------
        framework : str
            Compliance framework (GDPR, HIPAA, SOC2)
        days : int, optional
            Number of days to include. Default is 30.

        Returns
        -------
        dict
            Compliance report
        """
        from datetime import datetime, timedelta

        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        report = self.compliance.generate_compliance_report(
            framework=framework,
            start_date=start_date,
            end_date=end_date,
        )

        # Log report generation
        self.audit.log_event(
            "compliance.report.generated",
            severity="low",
            metadata={
                "framework": framework,
                "period_days": days,
                "total_events": report["total_events"],
            },
        )

        return report


def main() -> None:
    """Run example security integration."""
    # Initialize secure application
    app = SecureApplication()

    print("=== Secure Application Demo ===\n")

    # 1. Secure user login
    print("1. Secure User Login")
    success = app.secure_user_login(
        username="john_doe",
        password="secure-password-123",
        ip_address="192.168.1.100",
    )
    print(f"   Login result: {'Success' if success else 'Failed'}\n")

    # 2. Secure file upload
    print("2. Secure File Upload")
    # Create test file
    test_file = Path("/tmp/test_upload.txt")
    test_file.write_text("This is a test file for upload.")

    uploaded_path = app.secure_file_upload(
        file_path=str(test_file),
        user_id="john_doe",
        encrypt=True,
    )
    print(f"   Uploaded to: {uploaded_path}\n")

    # 3. Secure API request
    print("3. Secure API Request")
    api_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "message": "Hello, world!",
    }

    sanitized = app.secure_api_request(
        endpoint="/api/contact",
        user_id="john_doe",
        data=api_data,
    )
    print(f"   Sanitized data: {sanitized}\n")

    # 4. Generate compliance report
    print("4. Generate GDPR Compliance Report")
    report = app.generate_compliance_report(framework="GDPR", days=7)
    print(f"   Total events: {report['total_events']}")
    print(f"   Events by type: {report['events_by_type']}\n")

    print("=== Demo Complete ===")


if __name__ == "__main__":
    main()
