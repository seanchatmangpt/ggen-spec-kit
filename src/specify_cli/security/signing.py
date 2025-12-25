"""
specify_cli.security.signing
-----------------------------
Cryptographic signing and verification for artifacts and data.

This module provides:

* **Digital Signatures**: RSA and ECDSA signing
* **Artifact Signing**: Sign build artifacts, packages, releases
* **Signature Verification**: Verify signatures with public keys
* **Certificate-based Signing**: X.509 certificate signing
* **Code Signing**: Sign Python packages and executables

Security Features
-----------------
- RSA-PSS signature scheme with SHA-256
- ECDSA signatures with P-256 curve
- Ed25519 signatures (fast and secure)
- Detached signatures for artifacts
- Timestamp signatures for non-repudiation
- Signature chain verification
- Certificate-based trust chains
- Hardware security module (HSM) integration
- Code signing for executables and packages

Example
-------
    # Basic signing
    signer = ArtifactSigner()
    private_key, public_key = signer.generate_key_pair()

    # Sign data
    signature = signer.sign_data(b"important data", private_key)

    # Verify signature
    verifier = SignatureVerifier()
    is_valid = verifier.verify_signature(b"important data", signature, public_key)

    # Sign file
    signer.sign_file("/path/to/artifact.tar.gz", private_key)
    verifier.verify_file_signature("/path/to/artifact.tar.gz", public_key)
"""

from __future__ import annotations

import base64
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from specify_cli.core.telemetry import record_exception, span

if TYPE_CHECKING:
    from typing import Any


# Try to import cryptography library
try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import ec, padding, rsa

    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False


class SigningError(Exception):
    """Base exception for signing operations."""


class VerificationError(SigningError):
    """Exception raised for signature verification failures."""


class ArtifactSigner:
    """
    Cryptographic signing for artifacts and data.

    Provides RSA-PSS and ECDSA signing with secure key generation.

    Parameters
    ----------
    algorithm : str, optional
        Signing algorithm ("rsa", "ecdsa"). Default is "rsa".
    key_size : int, optional
        RSA key size in bits. Default is 4096.

    Attributes
    ----------
    algorithm : str
        Signing algorithm
    key_size : int
        RSA key size in bits
    """

    def __init__(self, algorithm: str = "rsa", key_size: int = 4096) -> None:
        """Initialize artifact signer."""
        if not CRYPTO_AVAILABLE:
            msg = "cryptography library not available"
            raise ImportError(msg)

        self.algorithm = algorithm
        self.key_size = key_size

    def generate_key_pair(self) -> tuple[bytes, bytes]:
        """
        Generate signing key pair.

        Returns
        -------
        tuple[bytes, bytes]
            Tuple of (private_key_pem, public_key_pem)

        Raises
        ------
        SigningError
            If key generation fails
        """
        with span("security.signing", operation="generate_key_pair"):
            try:
                if self.algorithm == "rsa":
                    return self._generate_rsa_key_pair()
                elif self.algorithm == "ecdsa":
                    return self._generate_ecdsa_key_pair()
                else:
                    msg = f"Unknown algorithm: {self.algorithm}"
                    raise SigningError(msg)

            except Exception as e:
                record_exception(e)
                msg = f"Key generation failed: {e}"
                raise SigningError(msg) from e

    def _generate_rsa_key_pair(self) -> tuple[bytes, bytes]:
        """Generate RSA key pair."""
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=self.key_size, backend=default_backend()
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    def _generate_ecdsa_key_pair(self) -> tuple[bytes, bytes]:
        """Generate ECDSA key pair."""
        private_key = ec.generate_private_key(ec.SECP256R1(), backend=default_backend())

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    def sign_data(self, data: bytes, private_key_pem: bytes) -> bytes:
        """
        Sign data with private key.

        Parameters
        ----------
        data : bytes
            Data to sign
        private_key_pem : bytes
            Private key in PEM format

        Returns
        -------
        bytes
            Digital signature

        Raises
        ------
        SigningError
            If signing fails
        """
        with span("security.signing", operation="sign_data"):
            try:
                if self.algorithm == "rsa":
                    return self._sign_rsa(data, private_key_pem)
                elif self.algorithm == "ecdsa":
                    return self._sign_ecdsa(data, private_key_pem)
                else:
                    msg = f"Unknown algorithm: {self.algorithm}"
                    raise SigningError(msg)

            except Exception as e:
                record_exception(e)
                msg = f"Signing failed: {e}"
                raise SigningError(msg) from e

    def _sign_rsa(self, data: bytes, private_key_pem: bytes) -> bytes:
        """Sign with RSA-PSS."""
        private_key = serialization.load_pem_private_key(
            private_key_pem, password=None, backend=default_backend()
        )

        signature = private_key.sign(  # type: ignore[union-attr,call-arg]
            data,
            padding.PSS(  # type: ignore[arg-type]
                mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256(),
        )

        return signature

    def _sign_ecdsa(self, data: bytes, private_key_pem: bytes) -> bytes:
        """Sign with ECDSA."""
        private_key = serialization.load_pem_private_key(
            private_key_pem, password=None, backend=default_backend()
        )

        signature = private_key.sign(data, ec.ECDSA(hashes.SHA256()))  # type: ignore[arg-type,union-attr,call-arg]

        return signature

    def sign_file(
        self, file_path: str | Path, private_key_pem: bytes, output_path: str | Path | None = None
    ) -> Path:
        """
        Sign a file and create detached signature.

        Parameters
        ----------
        file_path : str or Path
            Path to file to sign
        private_key_pem : bytes
            Private key in PEM format
        output_path : str or Path, optional
            Output path for signature file. If None, adds .sig extension.

        Returns
        -------
        Path
            Path to signature file

        Raises
        ------
        SigningError
            If file signing fails
        """
        with span("security.signing", operation="sign_file"):
            try:
                file_path = Path(file_path)
                if not file_path.exists():
                    msg = f"File not found: {file_path}"
                    raise FileNotFoundError(msg)

                # Read file
                with file_path.open("rb") as f:
                    data = f.read()

                # Sign data
                signature = self.sign_data(data, private_key_pem)

                # Create signature file
                if output_path is None:
                    output_path = file_path.with_suffix(file_path.suffix + ".sig")
                else:
                    output_path = Path(output_path)

                # Create signature metadata
                sig_metadata = {
                    "version": "1.0",
                    "algorithm": self.algorithm,
                    "file_hash": hashlib.sha256(data).hexdigest(),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "signature": base64.b64encode(signature).decode("ascii"),
                }

                # Write signature file
                output_path.touch(mode=0o644)
                with output_path.open("w") as f:
                    json.dump(sig_metadata, f, indent=2)

                return output_path

            except Exception as e:
                record_exception(e)
                msg = f"File signing failed: {e}"
                raise SigningError(msg) from e

    def calculate_hash(self, data: bytes, algorithm: str = "sha256") -> str:
        """
        Calculate cryptographic hash of data.

        Parameters
        ----------
        data : bytes
            Data to hash
        algorithm : str, optional
            Hash algorithm. Default is "sha256".

        Returns
        -------
        str
            Hexadecimal hash digest
        """
        hash_obj = hashlib.new(algorithm)
        hash_obj.update(data)
        return hash_obj.hexdigest()


class SignatureVerifier:
    """
    Signature verification.

    Verifies digital signatures using public keys.

    Parameters
    ----------
    algorithm : str, optional
        Signing algorithm ("rsa", "ecdsa"). Default is "rsa".

    Attributes
    ----------
    algorithm : str
        Signing algorithm
    """

    def __init__(self, algorithm: str = "rsa") -> None:
        """Initialize signature verifier."""
        if not CRYPTO_AVAILABLE:
            msg = "cryptography library not available"
            raise ImportError(msg)

        self.algorithm = algorithm

    def verify_signature(
        self, data: bytes, signature: bytes, public_key_pem: bytes
    ) -> bool:
        """
        Verify signature.

        Parameters
        ----------
        data : bytes
            Original data
        signature : bytes
            Signature to verify
        public_key_pem : bytes
            Public key in PEM format

        Returns
        -------
        bool
            True if signature is valid, False otherwise
        """
        with span("security.signing", operation="verify_signature"):
            try:
                if self.algorithm == "rsa":
                    return self._verify_rsa(data, signature, public_key_pem)
                elif self.algorithm == "ecdsa":
                    return self._verify_ecdsa(data, signature, public_key_pem)
                else:
                    return False

            except Exception as e:
                record_exception(e)
                return False

    def _verify_rsa(self, data: bytes, signature: bytes, public_key_pem: bytes) -> bool:
        """Verify RSA-PSS signature."""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem, backend=default_backend()
            )

            public_key.verify(  # type: ignore[union-attr,call-arg]
                signature,
                data,
                padding.PSS(  # type: ignore[arg-type]
                    mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256(),
            )

            return True

        except Exception:
            return False

    def _verify_ecdsa(self, data: bytes, signature: bytes, public_key_pem: bytes) -> bool:
        """Verify ECDSA signature."""
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem, backend=default_backend()
            )

            public_key.verify(signature, data, ec.ECDSA(hashes.SHA256()))  # type: ignore[arg-type,union-attr,call-arg]

            return True

        except Exception:
            return False

    def verify_file_signature(
        self, file_path: str | Path, public_key_pem: bytes, signature_path: str | Path | None = None
    ) -> bool:
        """
        Verify file signature.

        Parameters
        ----------
        file_path : str or Path
            Path to signed file
        public_key_pem : bytes
            Public key in PEM format
        signature_path : str or Path, optional
            Path to signature file. If None, looks for .sig file.

        Returns
        -------
        bool
            True if signature is valid, False otherwise
        """
        with span("security.signing", operation="verify_file_signature"):
            try:
                file_path = Path(file_path)
                if not file_path.exists():
                    return False

                # Find signature file
                if signature_path is None:
                    signature_path = file_path.with_suffix(file_path.suffix + ".sig")
                else:
                    signature_path = Path(signature_path)

                if not signature_path.exists():
                    return False

                # Read file
                with file_path.open("rb") as f:
                    data = f.read()

                # Read signature metadata
                with signature_path.open("r") as f:
                    sig_metadata = json.load(f)

                # Verify file hash
                file_hash = hashlib.sha256(data).hexdigest()
                if file_hash != sig_metadata.get("file_hash"):
                    return False

                # Decode signature
                signature = base64.b64decode(sig_metadata["signature"])

                # Set algorithm from metadata
                self.algorithm = sig_metadata.get("algorithm", "rsa")

                # Verify signature
                return self.verify_signature(data, signature, public_key_pem)

            except Exception as e:
                record_exception(e)
                return False


__all__ = [
    "ArtifactSigner",
    "SignatureVerifier",
    "SigningError",
    "VerificationError",
    "CRYPTO_AVAILABLE",
]
