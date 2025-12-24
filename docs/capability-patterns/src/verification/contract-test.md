# 32. Contract Test

★★

*Interfaces are contracts. Contract tests verify that implementations honor their contracts, catching integration failures before they reach production. This is the handshake between what was promised and what was delivered.*

---

## The Interface as Promise

Every interface is a promise. A CLI command promises to accept certain arguments and produce certain outputs. An API endpoint promises to return specific formats for given inputs. A function promises to transform inputs predictably according to its signature.

These promises are contracts—implicit agreements between components. When you call `validate(file)`, you expect it to return validation results, not crash, not delete your files, not send emails. The function's interface implies a contract about its behavior.

Contract tests make these implicit promises explicit and verifiable:

```python
# The implicit promise:
def validate(file: Path) -> ValidationResult:
    """Validate an RDF file."""
    ...

# The explicit contract:
# - Accepts a Path
# - Returns a ValidationResult
# - On valid file: result.valid == True
# - On invalid file: result.valid == False
# - On missing file: raises FileNotFoundError
```

Contract tests verify these promises are kept.

---

## The Contract Problem

**The fundamental problem: Interface changes break integrations. Without contract tests, breaks are discovered in production or by downstream consumers long after the change was made.**

Let us examine how contract violations occur:

### The Silent Breaking Change

```python
# Version 1: Original contract
def validate(file: Path) -> dict:
    return {"valid": True, "errors": []}

# Consumer code relies on this contract
result = validate(some_file)
if result["valid"]:
    proceed()

# Version 2: Developer changes return type
def validate(file: Path) -> ValidationResult:
    return ValidationResult(is_valid=True, issues=[])

# Consumer code BREAKS!
result = validate(some_file)
if result["valid"]:  # KeyError! No "valid" key anymore
    proceed()
```

Without contract tests, this breaks in production.

### The Undocumented Behavior Change

```python
# Version 1: Exit code 0 for valid, 1 for invalid
def validate_command(file):
    if is_valid(file):
        return 0
    return 1

# Version 2: Developer adds exit code 2 for warnings
def validate_command(file):
    result = validate(file)
    if result.has_errors:
        return 1
    if result.has_warnings:  # NEW: exit code 2
        return 2
    return 0

# Consumer scripts that check "exit code != 0" now fail on warnings
```

The contract (exit codes) changed without anyone realizing consumers depended on it.

### The Performance Degradation

```python
# Original: Response in <100ms
# After changes: Response in >5000ms

# Consumers with timeout of 1000ms now fail
response = requests.get(url, timeout=1.0)  # TimeoutError!
```

Performance is part of the implicit contract. Significant degradation violates it.

---

## The Forces

Several tensions shape contract testing:

### Force: Speed vs. Thoroughness

*Contract tests should run fast. But thorough contract verification takes time.*

Full integration tests are slow. But skipping contract verification means discovering breaks late.

**Resolution:** Contract tests verify the interface contract specifically—input acceptance and output conformance—without testing internal logic. They're faster than full integration tests while still catching interface breaks.

### Force: Coupling vs. Independence

*Tests should verify contracts. But contracts can couple tests to implementation.*

Testing "returns a dict with keys X, Y, Z" couples the test to the specific structure. If that structure changes, tests break even if behavior is equivalent.

**Resolution:** Test the contract that matters. If consumers depend on specific keys, test those keys. If consumers depend only on "some success indicator," test for that abstractly.

### Force: Coverage vs. Maintenance

*Every contract term should be tested. But many tests require maintenance.*

Testing every detail of every interface creates a large, brittle test suite.

**Resolution:** Focus on consumer-visible contracts. Test what consumers depend on. Internal implementation details aren't contracts—don't test them as such.

### Force: Stability vs. Evolution

*Contracts should be stable. But interfaces need to evolve.*

Strict contract tests resist any change, even improvements.

**Resolution:** Design contracts with evolution in mind. Use versioning, optional fields, and backward-compatible extensions. Contract tests verify the stable core, not every detail.

---

## Therefore

**Generate contract tests from interface specifications that verify input acceptance and output conformance without testing internal logic. Contract tests focus on the interface promise, not the implementation mechanism.**

Contract test structure:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CONTRACT TEST STRUCTURE                                                 │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ INPUT CONTRACT                                                      │ │
│  │                                                                     │ │
│  │  ├── Required inputs are required                                  │ │
│  │  ├── Optional inputs are optional                                  │ │
│  │  ├── Type constraints are enforced                                 │ │
│  │  └── Invalid inputs produce documented errors                      │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ OUTPUT CONTRACT                                                     │ │
│  │                                                                     │ │
│  │  ├── Success outputs match documented format                       │ │
│  │  ├── Error outputs match documented format                         │ │
│  │  ├── Exit codes match documentation                                │ │
│  │  └── Side effects match documentation                              │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ BEHAVIOR CONTRACT                                                   │ │
│  │                                                                     │ │
│  │  ├── Idempotent operations are idempotent                          │ │
│  │  ├── Pure functions are pure                                       │ │
│  │  └── Performance stays within bounds                               │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Contract Specification

### CLI Command Contract

```turtle
@prefix cli: <https://spec-kit.org/cli#> .
@prefix sk: <https://spec-kit.org/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;

    # Input contract: Required arguments
    cli:acceptsArgument [
        a cli:Argument ;
        sk:name "file" ;
        cli:type "Path" ;
        cli:required true ;
        sk:description "Path to file to validate"
    ] ;

    # Input contract: Optional arguments
    cli:acceptsOption [
        a cli:Option ;
        sk:name "shapes" ;
        cli:flag "--shapes" ;
        cli:shortFlag "-s" ;
        cli:type "Path" ;
        cli:required false ;
        sk:description "Custom SHACL shapes file"
    ] ;

    cli:acceptsOption [
        a cli:Option ;
        sk:name "strict" ;
        cli:flag "--strict" ;
        cli:type "bool" ;
        cli:default false ;
        sk:description "Treat warnings as errors"
    ] ;

    # Output contract: Exit codes
    cli:returns [
        cli:exitCode 0 ;
        cli:when "File is valid (no violations)" ;
        cli:outputContains "Valid" ;
        cli:outputContains "✓"
    ] ;

    cli:returns [
        cli:exitCode 1 ;
        cli:when "File is invalid (violations found)" ;
        cli:outputContains "error" ;
        cli:outputContains "violation"
    ] ;

    cli:returns [
        cli:exitCode 2 ;
        cli:when "File not found or not readable" ;
        cli:outputContains "not found"
    ] ;

    # Behavior contract
    cli:behavior [
        cli:type "idempotent" ;
        sk:description "Running twice produces same result"
    ] ;

    cli:behavior [
        cli:type "read-only" ;
        sk:description "Does not modify input files"
    ] .
```

### API Endpoint Contract

```turtle
@prefix api: <https://spec-kit.org/api#> .
@prefix sk: <https://spec-kit.org/ontology#> .

api:ValidateEndpoint a api:Endpoint ;
    api:method "POST" ;
    api:path "/api/v1/validate" ;

    # Request contract
    api:accepts [
        api:contentType "application/json" ;
        api:schema [
            api:property [
                sk:name "content" ;
                api:type "string" ;
                api:required true
            ] ;
            api:property [
                sk:name "format" ;
                api:type "string" ;
                api:required false ;
                api:default "turtle"
            ]
        ]
    ] ;

    # Response contract: Success
    api:responds [
        api:statusCode 200 ;
        api:when "Validation successful" ;
        api:contentType "application/json" ;
        api:schema [
            api:property [ sk:name "valid" ; api:type "boolean" ] ;
            api:property [ sk:name "errors" ; api:type "array" ]
        ]
    ] ;

    # Response contract: Client error
    api:responds [
        api:statusCode 400 ;
        api:when "Invalid request format" ;
        api:contentType "application/json" ;
        api:schema [
            api:property [ sk:name "error" ; api:type "string" ]
        ]
    ] ;

    # Performance contract
    api:performance [
        api:metric "latency_p99" ;
        api:maxValue 500 ;
        api:unit "ms"
    ] .
```

---

## Generated Contract Tests

### CLI Contract Test

```python
# tests/contract/test_validate_contract.py
"""Contract tests for validate command.

⚠️  AUTO-GENERATED CONTRACT TESTS  ⚠️

Source: ontology/cli-commands.ttl
Template: templates/contract-test.py.tera
Generated: 2025-01-15T10:30:00Z

These tests verify the command honors its interface contract,
not its internal implementation. Contract tests catch interface
breaks before they reach consumers.
"""

import pytest
from pathlib import Path
from typer.testing import CliRunner
from specify_cli.app import app

runner = CliRunner()


class TestValidateContract:
    """Contract tests for validate command interface.

    These tests verify:
    - Input contract (arguments, options, types)
    - Output contract (exit codes, output format)
    - Behavior contract (idempotence, read-only)
    """

    # ═══════════════════════════════════════════════════════════════════
    # INPUT CONTRACT: Required Arguments
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_file_argument_required(self):
        """Contract: 'file' argument is required.

        The specification states:
            cli:acceptsArgument [ sk:name "file" ; cli:required true ]

        Missing required arguments should produce an error.
        """
        result = runner.invoke(app, ["validate"])

        # Contract: Missing required argument produces error
        assert result.exit_code != 0, (
            "Contract violation: Missing required 'file' argument should fail"
        )
        assert any(word in result.output.lower() for word in ["file", "required", "missing"]), (
            "Contract violation: Error should mention the missing argument"
        )

    def test_contract_file_argument_accepts_path(self, tmp_path):
        """Contract: 'file' argument accepts a Path.

        The specification states:
            cli:acceptsArgument [ sk:name "file" ; cli:type "Path" ]

        Valid paths should be accepted without argument parsing errors.
        """
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        result = runner.invoke(app, ["validate", str(test_file)])

        # Contract: Valid path should not fail due to argument parsing
        # (it may fail for other reasons, but not "invalid argument")
        assert "invalid" not in result.output.lower() or "argument" not in result.output.lower(), (
            "Contract violation: Valid path should be accepted as argument"
        )

    # ═══════════════════════════════════════════════════════════════════
    # INPUT CONTRACT: Optional Arguments
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_shapes_option_optional(self, tmp_path):
        """Contract: '--shapes' option is optional.

        The specification states:
            cli:acceptsOption [ sk:name "shapes" ; cli:required false ]

        Command should work without --shapes option.
        """
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        result = runner.invoke(app, ["validate", str(test_file)])

        # Contract: Should not fail due to missing optional argument
        assert "shapes" not in result.output.lower() or "required" not in result.output.lower(), (
            "Contract violation: Optional --shapes should not be required"
        )

    def test_contract_shapes_option_accepts_path(self, tmp_path):
        """Contract: '--shapes' option accepts a Path when provided.

        The specification states:
            cli:acceptsOption [ sk:name "shapes" ; cli:type "Path" ]
        """
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        shapes_file = tmp_path / "shapes.ttl"
        shapes_file.write_text("""
            @prefix sh: <http://www.w3.org/ns/shacl#> .
            @prefix ex: <http://example.org/> .
        """)

        result = runner.invoke(app, ["validate", str(test_file), "--shapes", str(shapes_file)])

        # Contract: Valid shapes path should be accepted
        assert "invalid" not in result.output.lower() or "shapes" not in result.output.lower(), (
            "Contract violation: Valid --shapes path should be accepted"
        )

    def test_contract_strict_option_accepts_boolean(self, tmp_path):
        """Contract: '--strict' option is a boolean flag.

        The specification states:
            cli:acceptsOption [ sk:name "strict" ; cli:type "bool" ]
        """
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        result = runner.invoke(app, ["validate", str(test_file), "--strict"])

        # Contract: Boolean flag should be accepted without value
        assert "invalid" not in result.output.lower() or "strict" not in result.output.lower(), (
            "Contract violation: --strict flag should be accepted"
        )

    # ═══════════════════════════════════════════════════════════════════
    # OUTPUT CONTRACT: Exit Codes
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_exit_0_for_valid_file(self, tmp_path):
        """Contract: Exit code 0 for valid file.

        The specification states:
            cli:returns [ cli:exitCode 0 ; cli:when "File is valid" ]
        """
        valid_file = tmp_path / "valid.ttl"
        valid_file.write_text("""
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix ex: <http://example.org/> .
            ex:Thing a rdfs:Class .
        """)

        result = runner.invoke(app, ["validate", str(valid_file)])

        assert result.exit_code == 0, (
            f"Contract violation: Exit code should be 0 for valid file. "
            f"Got {result.exit_code}. Output: {result.output}"
        )

    def test_contract_exit_1_for_invalid_file(self, tmp_path):
        """Contract: Exit code 1 for invalid file.

        The specification states:
            cli:returns [ cli:exitCode 1 ; cli:when "File is invalid" ]
        """
        invalid_file = tmp_path / "invalid.ttl"
        invalid_file.write_text("this is not valid turtle syntax at all")

        result = runner.invoke(app, ["validate", str(invalid_file)])

        assert result.exit_code == 1, (
            f"Contract violation: Exit code should be 1 for invalid file. "
            f"Got {result.exit_code}. Output: {result.output}"
        )

    def test_contract_exit_2_for_missing_file(self):
        """Contract: Exit code 2 for file not found.

        The specification states:
            cli:returns [ cli:exitCode 2 ; cli:when "File not found" ]
        """
        result = runner.invoke(app, ["validate", "/nonexistent/path/file.ttl"])

        assert result.exit_code == 2, (
            f"Contract violation: Exit code should be 2 for missing file. "
            f"Got {result.exit_code}. Output: {result.output}"
        )

    # ═══════════════════════════════════════════════════════════════════
    # OUTPUT CONTRACT: Output Format
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_valid_output_contains_success_indicator(self, tmp_path):
        """Contract: Valid file output contains success indicator.

        The specification states:
            cli:returns [ cli:exitCode 0 ; cli:outputContains "Valid" ; cli:outputContains "✓" ]
        """
        valid_file = tmp_path / "valid.ttl"
        valid_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        result = runner.invoke(app, ["validate", str(valid_file)])

        assert "valid" in result.output.lower() or "✓" in result.output, (
            f"Contract violation: Valid output should contain success indicator. "
            f"Got: {result.output}"
        )

    def test_contract_invalid_output_contains_error_info(self, tmp_path):
        """Contract: Invalid file output contains error information.

        The specification states:
            cli:returns [ cli:exitCode 1 ; cli:outputContains "error" ]
        """
        invalid_file = tmp_path / "invalid.ttl"
        invalid_file.write_text("not valid")

        result = runner.invoke(app, ["validate", str(invalid_file)])

        assert len(result.output) > 10, (
            f"Contract violation: Invalid output should contain error details. "
            f"Got only: {result.output}"
        )

    def test_contract_not_found_output_mentions_file(self):
        """Contract: Missing file output mentions the file path.

        The specification states:
            cli:returns [ cli:exitCode 2 ; cli:outputContains "not found" ]
        """
        missing_path = "/nonexistent/specific/path.ttl"
        result = runner.invoke(app, ["validate", missing_path])

        assert "not found" in result.output.lower() or "does not exist" in result.output.lower(), (
            f"Contract violation: Output should indicate file not found. "
            f"Got: {result.output}"
        )

    # ═══════════════════════════════════════════════════════════════════
    # BEHAVIOR CONTRACT: Idempotence
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_idempotent_same_result(self, tmp_path):
        """Contract: Running twice produces same result.

        The specification states:
            cli:behavior [ cli:type "idempotent" ]
        """
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        result1 = runner.invoke(app, ["validate", str(test_file)])
        result2 = runner.invoke(app, ["validate", str(test_file)])

        assert result1.exit_code == result2.exit_code, (
            f"Contract violation: Idempotence requires same exit code. "
            f"Run 1: {result1.exit_code}, Run 2: {result2.exit_code}"
        )

    # ═══════════════════════════════════════════════════════════════════
    # BEHAVIOR CONTRACT: Read-Only
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_read_only_no_modification(self, tmp_path):
        """Contract: Does not modify input files.

        The specification states:
            cli:behavior [ cli:type "read-only" ]
        """
        test_file = tmp_path / "test.ttl"
        original_content = "@prefix ex: <http://example.org/> . ex:a ex:b ex:c ."
        test_file.write_text(original_content)
        original_mtime = test_file.stat().st_mtime

        runner.invoke(app, ["validate", str(test_file)])

        after_content = test_file.read_text()
        after_mtime = test_file.stat().st_mtime

        assert original_content == after_content, (
            "Contract violation: Read-only behavior violated. File content changed."
        )
        assert original_mtime == after_mtime, (
            "Contract violation: Read-only behavior violated. File modification time changed."
        )
```

### API Contract Test

```python
# tests/contract/test_api_validate_contract.py
"""Contract tests for validate API endpoint."""

import pytest
import requests
import time

BASE_URL = "http://localhost:8000"


class TestValidateApiContract:
    """Contract tests for /api/v1/validate endpoint."""

    # ═══════════════════════════════════════════════════════════════════
    # REQUEST CONTRACT
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_accepts_json_content_type(self):
        """Contract: Accepts application/json content type."""
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            headers={"Content-Type": "application/json"},
            json={"content": "@prefix ex: <http://example.org/> ."}
        )

        # Should not reject due to content type
        assert response.status_code != 415, (
            "Contract violation: Should accept application/json"
        )

    def test_contract_content_field_required(self):
        """Contract: 'content' field is required."""
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            json={"format": "turtle"}  # Missing 'content'
        )

        assert response.status_code == 400, (
            "Contract violation: Missing 'content' should return 400"
        )

    def test_contract_format_field_optional(self):
        """Contract: 'format' field is optional, defaults to 'turtle'."""
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            json={"content": "@prefix ex: <http://example.org/> ."}  # No 'format'
        )

        # Should work without format (defaults to turtle)
        assert response.status_code in [200, 400], (
            "Contract violation: Should accept request without 'format'"
        )

    # ═══════════════════════════════════════════════════════════════════
    # RESPONSE CONTRACT: Success
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_200_returns_json(self):
        """Contract: Success response is application/json."""
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            json={"content": "@prefix ex: <http://example.org/> . ex:a ex:b ex:c ."}
        )

        assert response.headers.get("Content-Type", "").startswith("application/json"), (
            "Contract violation: Response should be application/json"
        )

    def test_contract_200_contains_valid_field(self):
        """Contract: Success response contains 'valid' boolean."""
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            json={"content": "@prefix ex: <http://example.org/> . ex:a ex:b ex:c ."}
        )

        data = response.json()
        assert "valid" in data, (
            "Contract violation: Response should contain 'valid' field"
        )
        assert isinstance(data["valid"], bool), (
            "Contract violation: 'valid' field should be boolean"
        )

    def test_contract_200_contains_errors_field(self):
        """Contract: Success response contains 'errors' array."""
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            json={"content": "@prefix ex: <http://example.org/> . ex:a ex:b ex:c ."}
        )

        data = response.json()
        assert "errors" in data, (
            "Contract violation: Response should contain 'errors' field"
        )
        assert isinstance(data["errors"], list), (
            "Contract violation: 'errors' field should be array"
        )

    # ═══════════════════════════════════════════════════════════════════
    # RESPONSE CONTRACT: Client Error
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_400_contains_error_field(self):
        """Contract: Error response contains 'error' string."""
        response = requests.post(
            f"{BASE_URL}/api/v1/validate",
            json={}  # Invalid request
        )

        if response.status_code == 400:
            data = response.json()
            assert "error" in data, (
                "Contract violation: 400 response should contain 'error' field"
            )
            assert isinstance(data["error"], str), (
                "Contract violation: 'error' field should be string"
            )

    # ═══════════════════════════════════════════════════════════════════
    # PERFORMANCE CONTRACT
    # ═══════════════════════════════════════════════════════════════════

    def test_contract_latency_under_limit(self):
        """Contract: Response latency under 500ms p99."""
        latencies = []

        for _ in range(10):
            start = time.perf_counter()
            requests.post(
                f"{BASE_URL}/api/v1/validate",
                json={"content": "@prefix ex: <http://example.org/> ."}
            )
            latency = (time.perf_counter() - start) * 1000
            latencies.append(latency)

        p99 = sorted(latencies)[int(len(latencies) * 0.99)]

        assert p99 < 500, (
            f"Contract violation: p99 latency {p99:.0f}ms exceeds 500ms limit"
        )
```

---

## Contract Test vs. Other Tests

### Comparison Matrix

| Aspect | Contract Test | Unit Test | Integration Test |
|--------|---------------|-----------|-----------------|
| **Focus** | Interface promise | Internal logic | System behavior |
| **Coupling** | To specification | To implementation | To environment |
| **Speed** | Fast | Fastest | Slow |
| **Stability** | Stable (interface) | May change (refactoring) | May flake (environment) |
| **Scope** | Input/output only | Single unit | Multiple components |
| **Purpose** | Catch breaking changes | Verify logic | Verify integration |

### When to Use Each

```
┌─────────────────────────────────────────────────────────────────────────┐
│  TEST TYPE SELECTION                                                     │
│                                                                          │
│  Use CONTRACT TESTS when:                                                │
│    • Verifying public interfaces                                         │
│    • Catching breaking changes                                           │
│    • Testing between components                                          │
│    • Documenting interface promises                                      │
│                                                                          │
│  Use UNIT TESTS when:                                                    │
│    • Verifying internal logic                                            │
│    • Testing edge cases                                                  │
│    • Driving design (TDD)                                                │
│    • Fast feedback during development                                    │
│                                                                          │
│  Use INTEGRATION TESTS when:                                             │
│    • Verifying system behavior                                           │
│    • Testing with real dependencies                                      │
│    • End-to-end scenarios                                                │
│    • Pre-deployment verification                                         │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Case Study: The API Migration

*A team uses contract tests to safely migrate from REST to GraphQL.*

### The Situation

The DataPlatform team needed to migrate their validation API from REST to GraphQL. They had hundreds of consumers depending on the REST API. A breaking change would affect all of them.

### The Problem

Without contract tests, they faced:
- Unknown consumer dependencies
- Fear of breaking changes
- Gradual migration with inconsistency
- Late discovery of breaks

### The Solution

**Step 1: Document the existing contract**

```turtle
api:LegacyValidateEndpoint a api:Endpoint ;
    api:method "POST" ;
    api:path "/api/v1/validate" ;
    api:responds [
        api:statusCode 200 ;
        api:schema [
            api:property [ sk:name "valid" ; api:type "boolean" ] ;
            api:property [ sk:name "errors" ; api:type "array" ]
        ]
    ] .
```

**Step 2: Generate contract tests**

```python
def test_contract_200_response_shape():
    """Contract: Response has valid and errors fields."""
    response = requests.post(f"{BASE_URL}/api/v1/validate", json={"content": "..."})
    data = response.json()
    assert "valid" in data
    assert "errors" in data
    assert isinstance(data["valid"], bool)
    assert isinstance(data["errors"], list)
```

**Step 3: Implement GraphQL with same contract**

```graphql
type ValidationResult {
    valid: Boolean!     # Same as REST contract
    errors: [String!]!  # Same as REST contract
}

type Mutation {
    validate(content: String!): ValidationResult!
}
```

**Step 4: Create adapter maintaining contract**

```python
@app.post("/api/v1/validate")
async def validate_rest(request: ValidateRequest):
    # Internally uses GraphQL, but maintains REST contract
    result = await graphql_validate(request.content)
    return {
        "valid": result.valid,      # Contract maintained
        "errors": result.errors     # Contract maintained
    }
```

**Step 5: Run contract tests against both**

```bash
# Test legacy endpoint
pytest tests/contract/ --base-url=http://legacy-api

# Test new endpoint with adapter
pytest tests/contract/ --base-url=http://new-api

# Both pass = contract maintained
```

### The Results

| Metric | Without Contract Tests | With Contract Tests |
|--------|----------------------|---------------------|
| Consumer breaks | 23 incidents | 0 incidents |
| Migration duration | 6 months | 2 months |
| Rollbacks needed | 7 | 0 |
| Developer confidence | Low | High |

Contract tests gave them confidence that the migration maintained compatibility.

---

## Anti-Patterns

### Anti-Pattern: Testing Implementation

*"Our contract tests verify the database schema."*

Database schemas are implementation details, not contracts. Testing them couples to implementation.

**Resolution:** Test the public interface only. What the consumer sees is the contract, not how it's implemented internally.

### Anti-Pattern: Over-Specifying

*"Our contract tests verify every field in the response."*

Testing every field makes tests brittle to any addition or change, even backward-compatible ones.

**Resolution:** Test the fields consumers depend on. Adding new fields shouldn't break contracts if consumers ignore unknown fields.

### Anti-Pattern: Under-Specifying

*"Our contract tests just check for HTTP 200."*

This misses the actual contract—the structure and content of the response.

**Resolution:** Test what consumers depend on. If they depend on specific fields, test those fields.

### Anti-Pattern: No Contract Specification

*"We write contract tests from intuition."*

Without explicit contracts, tests may not match what consumers actually depend on.

**Resolution:** Specify contracts explicitly in RDF or similar. Generate tests from specifications.

---

## Configuration

### Contract Test Configuration

```toml
# ggen.toml

[[targets]]
source = "ontology/cli-commands.ttl"
query = "sparql/cli-contract.rq"
template = "templates/contract-test.py.tera"
output = "tests/contract/test_{{ command | snake_case }}_contract.py"

[[targets]]
source = "ontology/api-endpoints.ttl"
query = "sparql/api-contract.rq"
template = "templates/api-contract-test.py.tera"
output = "tests/contract/test_{{ endpoint | snake_case }}_contract.py"
```

---

## Implementation Checklist

### Contract Specification

- [ ] Document input contracts (required/optional, types)
- [ ] Document output contracts (status codes, response shapes)
- [ ] Document behavior contracts (idempotence, side effects)
- [ ] Document performance contracts (latency limits)

### Test Generation

- [ ] Create SPARQL query for contract extraction
- [ ] Create contract test template
- [ ] Generate contract tests
- [ ] Verify tests match specification

### CI Integration

- [ ] Run contract tests on every PR
- [ ] Run against deployed environments
- [ ] Alert on contract violations
- [ ] Block deploys on failures

---

## Exercises

### Exercise 1: Write a Contract Specification

Document the contract for a "search" API endpoint that:
- Accepts a query string
- Returns paginated results
- Has a maximum latency of 200ms

### Exercise 2: Generate Contract Tests

From your specification in Exercise 1, generate tests that verify:
- Required parameters
- Response structure
- Performance bounds

### Exercise 3: Catch a Breaking Change

1. Write contract tests for an interface
2. Make a breaking change to the implementation
3. Verify the contract tests catch it

---

## Resulting Context

After implementing this pattern, you have:

- **Verified interface contracts** through explicit testing
- **Fast-running contract tests** that don't require full integration
- **Decoupled tests from implementation** focusing on interface only
- **Early detection of interface breaks** before consumers are affected
- **Documentation of promises** in executable form

Contract tests are the handshake between specification and implementation. They verify that what was promised is what was delivered.

---

## Code References

The following spec-kit source files implement contract test concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/cli-commands.ttl:38-76` | Command argument contracts with types and constraints |
| `ontology/spec-kit-schema.ttl:466-516` | FeatureShape as interface contract |
| `src/specify_cli/runtime/receipt.py:159-185` | verify_receipt() as transformation contract verification |

---

## Related Patterns

- **Complements:** **[31. Test Before Code](./test-before-code.md)** — Different focus (criteria vs. interface)
- **Enables:** **[33. Integration Reality](./integration-reality.md)** — Contracts verified before integration
- **Supports:** **[37. Continuous Validation](./continuous-validation.md)** — Fast CI tests
- **Derives from:** **[11. Executable Specification](../specification/executable-specification.md)** — Specifications define contracts

---

## Philosophical Note

> *"A contract is a meeting of minds."*

Contract tests verify that the implementation's mind matches the specification's mind. The specification promises certain behavior. The implementation delivers it. Contract tests confirm the meeting.

When contracts are explicit and tested, evolution becomes possible. You can change implementation freely as long as the contract holds. You can extend contracts carefully with backward compatibility. You can migrate systems confidently when contracts are verified.

Without contract tests, interfaces are promises on faith. With them, they're promises verified.

---

**Next:** Learn how **[33. Integration Reality](./integration-reality.md)** tests capabilities with real dependencies.
