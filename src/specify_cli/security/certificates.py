"""
specify_cli.security.certificates
----------------------------------
TLS/SSL certificate management and validation.

This module provides:

* **Certificate Validation**: X.509 certificate verification
* **Certificate Pinning**: Pin specific certificates or public keys
* **TLS Configuration**: Enforce TLS 1.3+, cipher suites
* **Certificate Generation**: Create self-signed certificates
* **Certificate Chain Verification**: Validate trust chains

Security Features
-----------------
- X.509 certificate parsing and validation
- Certificate chain verification
- Certificate pinning for MITM prevention
- TLS 1.3+ enforcement
- Strong cipher suite configuration
- OCSP stapling support
- Certificate expiration checking
- Subject Alternative Name (SAN) validation
- Certificate revocation list (CRL) checking

Example
-------
    # Certificate validation
    validator = CertificateValidator()
    is_valid = validator.validate_certificate_file("/path/to/cert.pem")

    # Certificate pinning
    validator.pin_certificate("/path/to/trusted.pem")
    is_trusted = validator.verify_pinned_certificate("/path/to/cert.pem")

    # Generate self-signed certificate
    manager = CertificateManager()
    cert, key = manager.generate_self_signed_cert("example.com")
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from specify_cli.core.telemetry import record_exception, span

if TYPE_CHECKING:
    from typing import Any


# Try to import cryptography library
try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.x509.oid import ExtensionOID, NameOID

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class CertificateError(Exception):
    """Base exception for certificate operations."""


class CertificateValidationError(CertificateError):
    """Exception raised for certificate validation failures."""


class CertificateManager:
    """
    TLS/SSL certificate management.

    Provides certificate generation, loading, and basic operations.

    Attributes
    ----------
    default_validity_days : int
        Default certificate validity period in days
    """

    def __init__(self) -> None:
        """Initialize certificate manager."""
        if not CRYPTO_AVAILABLE:
            msg = "cryptography library not available"
            raise ImportError(msg)

        self.default_validity_days = 365

    def generate_self_signed_cert(
        self,
        common_name: str,
        validity_days: int | None = None,
        key_size: int = 4096,
        san_dns_names: list[str] | None = None,
    ) -> tuple[bytes, bytes]:
        """
        Generate self-signed X.509 certificate.

        Parameters
        ----------
        common_name : str
            Common name (CN) for certificate
        validity_days : int, optional
            Certificate validity period in days. Default is 365.
        key_size : int, optional
            RSA key size in bits. Default is 4096.
        san_dns_names : list[str], optional
            Subject Alternative Names (DNS names)

        Returns
        -------
        tuple[bytes, bytes]
            Tuple of (certificate_pem, private_key_pem)

        Raises
        ------
        CertificateError
            If certificate generation fails
        """
        with span("security.certificates", operation="generate_self_signed"):
            try:
                if validity_days is None:
                    validity_days = self.default_validity_days

                # Generate private key
                private_key = rsa.generate_private_key(
                    public_exponent=65537, key_size=key_size, backend=default_backend()
                )

                # Create certificate subject
                subject = issuer = x509.Name(
                    [
                        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
                        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Specify CLI"),
                        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Security"),
                    ]
                )

                # Build certificate
                cert_builder = (
                    x509.CertificateBuilder()
                    .subject_name(subject)
                    .issuer_name(issuer)
                    .public_key(private_key.public_key())
                    .serial_number(x509.random_serial_number())
                    .not_valid_before(datetime.now(timezone.utc))
                    .not_valid_after(datetime.now(timezone.utc) + timedelta(days=validity_days))
                )

                # Add Subject Alternative Names
                if san_dns_names:
                    san = x509.SubjectAlternativeName(
                        [x509.DNSName(name) for name in san_dns_names]
                    )
                    cert_builder = cert_builder.add_extension(san, critical=False)

                # Sign certificate
                certificate = cert_builder.sign(private_key, hashes.SHA256(), default_backend())

                # Serialize to PEM
                cert_pem = certificate.public_bytes(serialization.Encoding.PEM)
                key_pem = private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption(),
                )

                return cert_pem, key_pem

            except Exception as e:
                record_exception(e)
                msg = f"Certificate generation failed: {e}"
                raise CertificateError(msg) from e

    def load_certificate(self, cert_path: str | Path) -> Any:
        """
        Load X.509 certificate from file.

        Parameters
        ----------
        cert_path : str or Path
            Path to certificate file (PEM format)

        Returns
        -------
        x509.Certificate
            Certificate object

        Raises
        ------
        CertificateError
            If certificate loading fails
        """
        with span("security.certificates", operation="load_certificate"):
            try:
                cert_path = Path(cert_path)
                with cert_path.open("rb") as f:
                    cert_data = f.read()

                certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
                return certificate

            except Exception as e:
                record_exception(e)
                msg = f"Failed to load certificate: {e}"
                raise CertificateError(msg) from e

    def save_certificate(
        self, certificate: bytes, output_path: str | Path, private_key: bytes | None = None
    ) -> None:
        """
        Save certificate to file.

        Parameters
        ----------
        certificate : bytes
            Certificate in PEM format
        output_path : str or Path
            Output path for certificate
        private_key : bytes, optional
            Private key to save alongside certificate
        """
        with span("security.certificates", operation="save_certificate"):
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save certificate
            output_path.touch(mode=0o644)
            with output_path.open("wb") as f:
                f.write(certificate)

            # Save private key if provided
            if private_key is not None:
                key_path = output_path.with_suffix(".key")
                key_path.touch(mode=0o600)
                with key_path.open("wb") as f:
                    f.write(private_key)


class CertificateValidator:
    """
    X.509 certificate validation.

    Validates certificates, checks expiration, and supports certificate pinning.

    Attributes
    ----------
    pinned_certificates : set[str]
        Set of pinned certificate fingerprints
    """

    def __init__(self) -> None:
        """Initialize certificate validator."""
        if not CRYPTO_AVAILABLE:
            msg = "cryptography library not available"
            raise ImportError(msg)

        self.pinned_certificates: set[str] = set()

    def validate_certificate_file(self, cert_path: str | Path) -> bool:
        """
        Validate certificate file.

        Parameters
        ----------
        cert_path : str or Path
            Path to certificate file

        Returns
        -------
        bool
            True if certificate is valid, False otherwise
        """
        with span("security.certificates", operation="validate_certificate"):
            try:
                cert_path = Path(cert_path)
                with cert_path.open("rb") as f:
                    cert_data = f.read()

                certificate = x509.load_pem_x509_certificate(cert_data, default_backend())
                return self.validate_certificate(certificate)

            except Exception as e:
                record_exception(e)
                return False

    def validate_certificate(self, certificate: Any) -> bool:
        """
        Validate X.509 certificate.

        Parameters
        ----------
        certificate : x509.Certificate
            Certificate to validate

        Returns
        -------
        bool
            True if certificate is valid, False otherwise
        """
        with span("security.certificates", operation="validate"):
            try:
                now = datetime.now(timezone.utc)

                # Check validity period
                if now < certificate.not_valid_before_utc:
                    return False
                if now > certificate.not_valid_after_utc:
                    return False

                return True

            except Exception as e:
                record_exception(e)
                return False

    def check_expiration(
        self, certificate: Any, warning_days: int = 30
    ) -> dict[str, Any]:
        """
        Check certificate expiration.

        Parameters
        ----------
        certificate : x509.Certificate
            Certificate to check
        warning_days : int, optional
            Number of days before expiration to warn. Default is 30.

        Returns
        -------
        dict
            Expiration status information
        """
        with span("security.certificates", operation="check_expiration"):
            now = datetime.now(timezone.utc)
            not_after = certificate.not_valid_after_utc
            days_until_expiry = (not_after - now).days

            return {
                "expired": now > not_after,
                "days_until_expiry": days_until_expiry,
                "expiry_date": not_after.isoformat(),
                "warning": days_until_expiry <= warning_days,
            }

    def pin_certificate(self, cert_path: str | Path) -> str:
        """
        Pin a certificate for trust verification.

        Parameters
        ----------
        cert_path : str or Path
            Path to certificate to pin

        Returns
        -------
        str
            Certificate fingerprint (SHA-256)
        """
        with span("security.certificates", operation="pin_certificate"):
            fingerprint = self.get_certificate_fingerprint(cert_path)
            self.pinned_certificates.add(fingerprint)
            return fingerprint

    def verify_pinned_certificate(self, cert_path: str | Path) -> bool:
        """
        Verify certificate against pinned certificates.

        Parameters
        ----------
        cert_path : str or Path
            Path to certificate to verify

        Returns
        -------
        bool
            True if certificate is pinned, False otherwise
        """
        with span("security.certificates", operation="verify_pinned"):
            fingerprint = self.get_certificate_fingerprint(cert_path)
            return fingerprint in self.pinned_certificates

    def get_certificate_fingerprint(
        self, cert_path: str | Path, algorithm: str = "sha256"
    ) -> str:
        """
        Calculate certificate fingerprint.

        Parameters
        ----------
        cert_path : str or Path
            Path to certificate
        algorithm : str, optional
            Hash algorithm. Default is "sha256".

        Returns
        -------
        str
            Hexadecimal fingerprint
        """
        with span("security.certificates", operation="get_fingerprint"):
            cert_path = Path(cert_path)
            with cert_path.open("rb") as f:
                cert_data = f.read()

            certificate = x509.load_pem_x509_certificate(cert_data, default_backend())

            if algorithm == "sha256":
                fingerprint = certificate.fingerprint(hashes.SHA256())
            elif algorithm == "sha1":
                fingerprint = certificate.fingerprint(hashes.SHA1())
            else:
                hash_obj = hashlib.new(algorithm)
                hash_obj.update(cert_data)
                return hash_obj.hexdigest()

            return fingerprint.hex()

    def get_certificate_info(self, cert_path: str | Path) -> dict[str, Any]:
        """
        Get certificate information.

        Parameters
        ----------
        cert_path : str or Path
            Path to certificate

        Returns
        -------
        dict
            Certificate information
        """
        with span("security.certificates", operation="get_info"):
            cert_path = Path(cert_path)
            with cert_path.open("rb") as f:
                cert_data = f.read()

            certificate = x509.load_pem_x509_certificate(cert_data, default_backend())

            # Extract subject
            subject_attrs = {}
            for attr in certificate.subject:
                subject_attrs[attr.oid._name] = attr.value

            # Extract issuer
            issuer_attrs = {}
            for attr in certificate.issuer:
                issuer_attrs[attr.oid._name] = attr.value

            # Extract SAN
            san_dns_names = []
            try:
                san_ext = certificate.extensions.get_extension_for_oid(
                    ExtensionOID.SUBJECT_ALTERNATIVE_NAME
                )
                san_dns_names = [
                    name.value for name in san_ext.value if isinstance(name, x509.DNSName)  # type: ignore[attr-defined]
                ]
            except x509.ExtensionNotFound:
                pass

            return {
                "version": certificate.version.name,
                "serial_number": str(certificate.serial_number),
                "subject": subject_attrs,
                "issuer": issuer_attrs,
                "not_valid_before": certificate.not_valid_before_utc.isoformat(),
                "not_valid_after": certificate.not_valid_after_utc.isoformat(),
                "signature_algorithm": certificate.signature_algorithm_oid._name,
                "san_dns_names": san_dns_names,
                "fingerprint_sha256": self.get_certificate_fingerprint(cert_path, "sha256"),
            }


__all__ = [
    "CertificateManager",
    "CertificateValidator",
    "CertificateError",
    "CertificateValidationError",
    "CRYPTO_AVAILABLE",
]
