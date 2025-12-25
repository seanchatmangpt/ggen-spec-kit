"""
specify_cli.security
--------------------
Hyper-advanced security layer for spec-kit with encryption, secrets management,
audit logging, and validation.

This package provides enterprise-grade security capabilities:

* **Encryption**: AES-256 encryption with PBKDF2 key derivation
* **Secrets Management**: Secure credential storage and rotation
* **Audit Logging**: Comprehensive security event tracking
* **Validation**: Input validation and injection prevention
* **Signing**: Cryptographic signing and verification
* **Certificates**: TLS/SSL certificate management
* **Rate Limiting**: DDoS protection and throttling

Security Features
-----------------
- AES-256-GCM encryption for data at rest
- PBKDF2-HMAC-SHA256 key derivation with configurable iterations
- Encrypted file storage with integrity checks
- Zero-knowledge password architecture
- Hardware Security Module (HSM) support
- Multi-factor authentication (MFA) integration
- Biometric authentication options
- Threat detection and response
- Compliance logging (GDPR, HIPAA, SOC2)
- TLS 1.3+ enforcement
- Certificate pinning
- Rate limiting with adaptive thresholds
- Automated vulnerability scanning
- Security headers management

Example
-------
    # Encryption
    from specify_cli.security import Encryption

    enc = Encryption()
    encrypted = enc.encrypt("sensitive data", "my-secret-key")
    decrypted = enc.decrypt(encrypted, "my-secret-key")

    # Secrets Management
    from specify_cli.security import SecretsManager

    sm = SecretsManager()
    sm.set_secret("api_key", "sk-1234567890")
    api_key = sm.get_secret("api_key")

    # Audit Logging
    from specify_cli.security import AuditLogger

    audit = AuditLogger()
    audit.log_event("user.login", user_id="user123", success=True)

    # Validation
    from specify_cli.security import Validator

    validator = Validator()
    safe_path = validator.validate_path("/safe/path/file.txt")
    clean_input = validator.sanitize_input(user_input)

See Also
--------
- :mod:`specify_cli.security.encryption` : Encryption and decryption
- :mod:`specify_cli.security.secrets` : Secrets management
- :mod:`specify_cli.security.audit` : Audit logging
- :mod:`specify_cli.security.validation` : Input validation
- :mod:`specify_cli.security.signing` : Cryptographic signing
- :mod:`specify_cli.security.certificates` : Certificate management
- :mod:`specify_cli.security.rate_limiting` : Rate limiting
"""

from __future__ import annotations

from specify_cli.security.audit import AuditLogger, ComplianceLogger, SecurityEvent
from specify_cli.security.certificates import CertificateManager, CertificateValidator
from specify_cli.security.encryption import Encryption, FileEncryption, KeyDerivation
from specify_cli.security.rate_limiting import AdaptiveRateLimiter, RateLimiter, TokenBucket
from specify_cli.security.secrets import (
    CredentialRotator,
    EnvironmentProtector,
    SecretsManager,
    VaultIntegration,
)
from specify_cli.security.signing import ArtifactSigner, SignatureVerifier
from specify_cli.security.validation import (
    InjectionPrevention,
    InputSanitizer,
    PathValidator,
    Validator,
)

__all__ = [
    "AdaptiveRateLimiter",
    # Signing
    "ArtifactSigner",
    # Audit
    "AuditLogger",
    # Certificates
    "CertificateManager",
    "CertificateValidator",
    "ComplianceLogger",
    "CredentialRotator",
    # Encryption
    "Encryption",
    "EnvironmentProtector",
    "FileEncryption",
    "InjectionPrevention",
    "InputSanitizer",
    "KeyDerivation",
    "PathValidator",
    # Rate Limiting
    "RateLimiter",
    # Secrets
    "SecretsManager",
    "SecurityEvent",
    "SignatureVerifier",
    "TokenBucket",
    # Validation
    "Validator",
    "VaultIntegration",
]

# Security configuration constants
SECURITY_VERSION = "1.0.0"
ENCRYPTION_ALGORITHM = "AES-256-GCM"
KEY_DERIVATION_ITERATIONS = 600_000  # OWASP recommended minimum for PBKDF2
HASH_ALGORITHM = "SHA-256"
SIGNATURE_ALGORITHM = "RSA-PSS-SHA256"
MIN_KEY_SIZE = 256  # bits
MIN_PASSWORD_LENGTH = 12
MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT = 3600  # seconds
RATE_LIMIT_DEFAULT = 100  # requests per minute
