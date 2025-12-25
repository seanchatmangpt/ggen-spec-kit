# Security Guide - Spec-Kit Security Layer

This guide provides comprehensive documentation for the hyper-advanced security layer in spec-kit.

## Table of Contents

- [Overview](#overview)
- [Encryption](#encryption)
- [Secrets Management](#secrets-management)
- [Audit Logging](#audit-logging)
- [Input Validation](#input-validation)
- [Cryptographic Signing](#cryptographic-signing)
- [Certificate Management](#certificate-management)
- [Rate Limiting](#rate-limiting)
- [Best Practices](#best-practices)
- [Compliance](#compliance)

## Overview

The spec-kit security layer provides enterprise-grade security capabilities including:

- **AES-256-GCM encryption** for data at rest
- **Secrets management** with rotation policies
- **Comprehensive audit logging** for compliance
- **Input validation** and injection prevention
- **Cryptographic signing** for artifacts
- **Certificate management** with TLS 1.3+ enforcement
- **Rate limiting** with adaptive thresholds

All security operations are instrumented with OpenTelemetry for observability.

## Encryption

### Basic Encryption

```python
from specify_cli.security import Encryption

# Initialize encryption
enc = Encryption()

# Encrypt data
plaintext = "sensitive data"
password = "my-secret-key"
encrypted = enc.encrypt_string(plaintext, password)

# Decrypt data
decrypted = enc.decrypt_string(encrypted, password)
```

### File Encryption

```python
from specify_cli.security import FileEncryption

# Initialize file encryption
file_enc = FileEncryption()

# Encrypt file
encrypted_file = file_enc.encrypt_file(
    "/path/to/sensitive.txt",
    password="strong-password"
)

# Decrypt file
decrypted_file = file_enc.decrypt_file(
    "/path/to/sensitive.txt.enc",
    password="strong-password"
)
```

### Key Derivation

```python
from specify_cli.security import KeyDerivation

# Initialize KDF with OWASP-recommended iterations
kdf = KeyDerivation(iterations=600_000)

# Derive key from password
key, salt = kdf.derive_key("my-password")

# Verify password
is_valid = kdf.verify_password("my-password", key, salt)
```

### Asymmetric Encryption

```python
from specify_cli.security.encryption import AsymmetricEncryption

# Initialize asymmetric encryption
asym = AsymmetricEncryption(key_size=4096)

# Generate key pair
private_key, public_key = asym.generate_key_pair()

# Encrypt with public key
plaintext = b"secret message"
encrypted = asym.encrypt_with_public_key(plaintext, public_key)

# Decrypt with private key
decrypted = asym.decrypt_with_private_key(encrypted, private_key)
```

## Secrets Management

### Basic Secrets Storage

```python
from specify_cli.security import SecretsManager

# Initialize secrets manager
sm = SecretsManager()
sm.set_master_password("master-password-123")

# Store secret
sm.set_secret("api_key", "sk-1234567890")

# Retrieve secret
api_key = sm.get_secret("api_key")

# List all secrets
secrets = sm.list_secrets()

# Delete secret
sm.delete_secret("old_api_key")
```

### Secret Rotation

```python
from specify_cli.security import CredentialRotator

# Initialize rotator
rotator = CredentialRotator(sm)

# Schedule automatic rotation (every 90 days)
rotator.schedule_rotation("api_key", days=90)

# Custom rotation callback
def generate_new_api_key(name: str) -> str:
    # Your key generation logic
    return f"sk-{secrets.token_hex(32)}"

rotator.schedule_rotation(
    "api_key",
    days=90,
    callback=generate_new_api_key
)

# Check and rotate if needed
results = rotator.rotate_if_needed()
```

### Environment Protection

```python
from specify_cli.security import EnvironmentProtector

# Initialize protector
protector = EnvironmentProtector()

# Protect sensitive environment variables
protector.protect_variable("DATABASE_PASSWORD")
protector.protect_variable("API_SECRET_KEY")

# Get safe environment (redacted)
safe_env = protector.get_safe_environment(redact=True)

# Safely access protected variable
password = protector.get_protected_value("DATABASE_PASSWORD")

# Auto-detect potential secrets
potential_secrets = EnvironmentProtector.detect_secrets_in_env()
```

### Vault Integration

```python
from specify_cli.security import VaultIntegration

# Initialize Vault client
vault = VaultIntegration(
    vault_addr="https://vault.example.com",
    vault_token="s.your-vault-token"
)

# Store secret in Vault
vault.set_secret("database/credentials", {
    "username": "admin",
    "password": "secret-password"
})

# Retrieve secret from Vault
credentials = vault.get_secret("database/credentials")
```

## Audit Logging

### Basic Audit Logging

```python
from specify_cli.security import AuditLogger

# Initialize audit logger
audit = AuditLogger()

# Log security event
audit.log_event(
    "user.login",
    severity="high",
    user_id="user123",
    ip_address="192.168.1.1",
    result="success"
)

# Log user action
audit.log_user_action(
    user_id="user123",
    action="delete",
    resource="/api/users/456",
    result="success"
)

# Log authentication
audit.log_authentication(
    user_id="user123",
    success=True,
    method="2fa",
    ip_address="192.168.1.1"
)

# Log data access
audit.log_data_access(
    user_id="user123",
    resource="/sensitive/data.txt",
    action="read",
    authorized=True
)
```

### Structured Security Events

```python
from specify_cli.security import SecurityEvent, AuditLogger

# Create structured event
event = SecurityEvent(
    event_type="authentication.failure",
    severity="critical",
    category="authentication",
    user_id="user123",
    ip_address="192.168.1.1",
    metadata={
        "attempt_number": 5,
        "reason": "invalid_password"
    }
)

# Log event
audit = AuditLogger()
event_id = audit.log_security_event(event)
```

### Query Audit Events

```python
from datetime import datetime, timedelta

# Query events
start = datetime.utcnow() - timedelta(days=7)
end = datetime.utcnow()

events = audit.query_events(
    start_time=start,
    end_time=end,
    event_type="user.login",
    severity="high"
)

# Filter by user
user_events = audit.query_events(user_id="user123")
```

### Compliance Logging

```python
from specify_cli.security import ComplianceLogger

# Initialize compliance logger
compliance = ComplianceLogger()

# Log GDPR event
compliance.log_gdpr_event(
    "data.deletion",
    subject_id="user123",
    data_category="personal_information",
    legal_basis="right_to_be_forgotten"
)

# Log HIPAA event
compliance.log_hipaa_event(
    "patient.record.access",
    patient_id="P12345",
    phi_accessed=True
)

# Log SOC2 event
compliance.log_soc2_event(
    "security.control.verified",
    control_id="CC6.1"
)

# Generate compliance report
report = compliance.generate_compliance_report(
    framework="GDPR",
    start_date=start,
    end_date=end
)
```

## Input Validation

### Email and URL Validation

```python
from specify_cli.security import Validator

validator = Validator()

# Validate email
try:
    email = validator.validate_email("user@example.com")
except ValidationError as e:
    print(f"Invalid email: {e}")

# Validate URL
try:
    url = validator.validate_url(
        "https://example.com",
        allowed_schemes=["https"]
    )
except ValidationError as e:
    print(f"Invalid URL: {e}")
```

### Integer and Pattern Validation

```python
# Validate integer with range
try:
    age = validator.validate_integer("25", min_value=0, max_value=120)
except ValidationError as e:
    print(f"Invalid age: {e}")

# Validate against pattern
try:
    username = validator.validate_pattern(
        "john_doe123",
        r"^[a-z_][a-z0-9_]{2,30}$"
    )
except ValidationError as e:
    print(f"Invalid username: {e}")

# Validate string length
try:
    password = validator.validate_length(
        "my-password",
        min_length=12,
        max_length=128
    )
except ValidationError as e:
    print(f"Invalid password: {e}")
```

### Path Validation

```python
from specify_cli.security import PathValidator

# Initialize with base directory
validator = PathValidator(base_dir="/safe/base/dir")

# Validate path (prevents traversal)
try:
    safe_path = validator.validate_path(
        "/safe/base/dir/subdir/file.txt",
        must_exist=False,
        allow_symlinks=False
    )
except PathTraversalError as e:
    print(f"Path traversal detected: {e}")

# Validate filename
try:
    filename = validator.validate_filename(
        "document.pdf",
        allowed_extensions=[".pdf", ".txt", ".md"]
    )
except ValidationError as e:
    print(f"Invalid filename: {e}")
```

### Input Sanitization

```python
from specify_cli.security import InputSanitizer

sanitizer = InputSanitizer()

# Sanitize HTML (XSS prevention)
user_input = "<script>alert('xss')</script>"
safe_html = sanitizer.sanitize_html(user_input)
# Result: "&lt;script&gt;alert('xss')&lt;/script&gt;"

# Sanitize SQL identifier
table_name = "users; DROP TABLE users; --"
safe_table = sanitizer.sanitize_sql(table_name)

# Sanitize shell command
command = "ls | cat /etc/passwd"
safe_command = sanitizer.sanitize_shell_command(command)
```

### Injection Prevention

```python
from specify_cli.security import InjectionPrevention

prevention = InjectionPrevention()

# Detect SQL injection
if prevention.detect_sql_injection(user_input):
    raise SecurityError("SQL injection detected")

# Safe SQL with parameters
query, params = prevention.prevent_sql_injection(
    "SELECT * FROM users WHERE id = ?",
    [user_id]
)

# Detect command injection
if prevention.detect_command_injection(user_input):
    raise SecurityError("Command injection detected")

# Sanitize shell command
safe_cmd = prevention.sanitize_shell_command(
    ["ls", "-la", user_provided_path]
)

# Detect XSS
if prevention.detect_xss(user_input):
    raise SecurityError("XSS attack detected")
```

## Cryptographic Signing

### Sign and Verify Data

```python
from specify_cli.security import ArtifactSigner, SignatureVerifier

# Generate key pair
signer = ArtifactSigner(algorithm="rsa", key_size=4096)
private_key, public_key = signer.generate_key_pair()

# Sign data
data = b"important artifact data"
signature = signer.sign_data(data, private_key)

# Verify signature
verifier = SignatureVerifier(algorithm="rsa")
is_valid = verifier.verify_signature(data, signature, public_key)
```

### Sign Files

```python
# Sign file (creates detached signature)
signature_file = signer.sign_file(
    "/path/to/artifact.tar.gz",
    private_key
)

# Verify file signature
is_valid = verifier.verify_file_signature(
    "/path/to/artifact.tar.gz",
    public_key
)

if is_valid:
    print("Signature valid - artifact is authentic")
else:
    print("Signature invalid - artifact may be tampered")
```

### ECDSA Signing

```python
# Use ECDSA for smaller signatures
signer = ArtifactSigner(algorithm="ecdsa")
private_key, public_key = signer.generate_key_pair()

signature = signer.sign_data(data, private_key)

verifier = SignatureVerifier(algorithm="ecdsa")
is_valid = verifier.verify_signature(data, signature, public_key)
```

## Certificate Management

### Generate Self-Signed Certificate

```python
from specify_cli.security import CertificateManager

manager = CertificateManager()

# Generate self-signed certificate
cert_pem, key_pem = manager.generate_self_signed_cert(
    common_name="example.com",
    validity_days=365,
    key_size=4096,
    san_dns_names=["www.example.com", "api.example.com"]
)

# Save certificate
manager.save_certificate(
    cert_pem,
    "/path/to/cert.pem",
    private_key=key_pem
)
```

### Certificate Validation

```python
from specify_cli.security import CertificateValidator

validator = CertificateValidator()

# Validate certificate file
is_valid = validator.validate_certificate_file("/path/to/cert.pem")

# Check expiration
cert = manager.load_certificate("/path/to/cert.pem")
expiry_info = validator.check_expiration(cert, warning_days=30)

if expiry_info["expired"]:
    print("Certificate expired!")
elif expiry_info["warning"]:
    print(f"Certificate expires in {expiry_info['days_until_expiry']} days")
```

### Certificate Pinning

```python
# Pin trusted certificate
fingerprint = validator.pin_certificate("/path/to/trusted.pem")

# Verify against pinned certificates
is_pinned = validator.verify_pinned_certificate("/path/to/cert.pem")

if not is_pinned:
    raise SecurityError("Certificate not in pinned set")
```

### Certificate Information

```python
# Get certificate details
info = validator.get_certificate_info("/path/to/cert.pem")

print(f"Subject: {info['subject']}")
print(f"Issuer: {info['issuer']}")
print(f"Valid from: {info['not_valid_before']}")
print(f"Valid until: {info['not_valid_after']}")
print(f"SAN: {info['san_dns_names']}")
print(f"Fingerprint: {info['fingerprint_sha256']}")
```

## Rate Limiting

### Token Bucket Rate Limiting

```python
from specify_cli.security import TokenBucket

# Create token bucket (100 tokens capacity, 10 tokens/sec refill)
bucket = TokenBucket(capacity=100, refill_rate=10)

# Try to consume tokens
if bucket.consume(5):
    # Process request
    process_request()
else:
    # Rate limited
    raise RateLimitExceeded("Too many requests")

# Check available tokens
available = bucket.get_tokens()

# Get wait time for tokens
wait_time = bucket.wait_time(tokens=5)
```

### Sliding Window Rate Limiting

```python
from specify_cli.security import RateLimiter

# Create rate limiter (100 requests per minute)
limiter = RateLimiter(rate=100, interval=60)

# Check if request allowed
if limiter.allow_request("user123"):
    # Process request
    process_request()
else:
    # Rate limited
    remaining = limiter.get_remaining("user123")
    reset_time = limiter.get_reset_time("user123")
    raise RateLimitExceeded(
        f"Rate limit exceeded. {remaining} remaining. "
        f"Resets in {reset_time:.0f} seconds."
    )

# Get rate limit headers
headers = limiter.get_headers("user123")
# {
#     "X-RateLimit-Limit": "100",
#     "X-RateLimit-Remaining": "95",
#     "X-RateLimit-Reset": "1234567890"
# }
```

### Adaptive Rate Limiting

```python
from specify_cli.security import AdaptiveRateLimiter

# Create adaptive limiter
limiter = AdaptiveRateLimiter(
    base_rate=100,
    interval=60,
    min_rate=50,
    max_rate=200
)

# Allow request
if limiter.allow_request("user123"):
    try:
        process_request()
    except Exception as e:
        # Record error for adaptive adjustment
        limiter.record_error()
        raise

# Manually adjust for system load
current_load = get_system_load()  # 0.0 to 1.0
limiter.adjust_for_load(current_load)

# Get statistics
stats = limiter.get_statistics()
print(f"Current rate: {stats['current_rate']}")
print(f"Error rate: {stats['error_rate']:.2%}")
```

## Best Practices

### 1. Encryption

- Always use AES-256-GCM for encryption (provides authenticity)
- Use PBKDF2 with at least 600,000 iterations (OWASP recommendation)
- Never hardcode encryption keys - use secrets management
- Rotate encryption keys regularly
- Use hardware security modules (HSM) for production

### 2. Secrets Management

- Set strong master passwords (min 16 characters, mixed case, symbols)
- Enable automatic secret rotation (90 days recommended)
- Never commit secrets to version control
- Use environment variable protection
- Integrate with external secret managers (Vault, AWS Secrets Manager)

### 3. Audit Logging

- Log all security-relevant events
- Include user ID, IP address, timestamp in all logs
- Enable integrity checking for immutable audit trails
- Implement log retention policies per compliance requirements
- Regularly review audit logs for anomalies

### 4. Input Validation

- Validate all user inputs at entry points
- Use whitelist validation over blacklist
- Sanitize data before output (prevent XSS)
- Always use parameterized queries (prevent SQL injection)
- Never execute user input as commands

### 5. Rate Limiting

- Implement rate limiting on all public APIs
- Use adaptive rate limiting for production
- Configure appropriate burst limits
- Log rate limit violations
- Combine with CAPTCHA for authentication endpoints

## Compliance

### GDPR Compliance

```python
from specify_cli.security import ComplianceLogger

compliance = ComplianceLogger()

# Log data processing
compliance.log_gdpr_event(
    "data.processing",
    subject_id=user_id,
    data_category="personal_information",
    legal_basis="consent"
)

# Log right to erasure
compliance.log_gdpr_event(
    "data.deletion",
    subject_id=user_id,
    data_category="all",
    legal_basis="right_to_be_forgotten"
)

# Generate GDPR compliance report
report = compliance.generate_compliance_report(
    framework="GDPR",
    start_date=start_date,
    end_date=end_date
)
```

### HIPAA Compliance

```python
# Log PHI access
compliance.log_hipaa_event(
    "patient.record.access",
    patient_id=patient_id,
    phi_accessed=True
)

# Log PHI disclosure
compliance.log_hipaa_event(
    "phi.disclosure",
    patient_id=patient_id,
    phi_accessed=True,
    disclosed_to="healthcare_provider"
)
```

### SOC2 Compliance

```python
# Log security control verification
compliance.log_soc2_event(
    "security.control.verified",
    control_id="CC6.1"
)

# Log access control review
compliance.log_soc2_event(
    "access.control.review",
    control_id="CC6.2"
)
```

## Integration Examples

See `/examples/security_integration.py` for complete integration examples.

## API Reference

Full API documentation available in module docstrings:

- `specify_cli.security.encryption`
- `specify_cli.security.secrets`
- `specify_cli.security.audit`
- `specify_cli.security.validation`
- `specify_cli.security.signing`
- `specify_cli.security.certificates`
- `specify_cli.security.rate_limiting`

## Security Reporting

To report security vulnerabilities, please email: security@specify-cli.com

Do NOT open public GitHub issues for security vulnerabilities.
