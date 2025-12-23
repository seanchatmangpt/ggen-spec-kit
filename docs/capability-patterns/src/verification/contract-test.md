# 32. Contract Test

★★

*Interfaces are contracts. Contract tests verify that implementations honor their contracts, catching integration failures before they reach production.*

---

A command promises to accept certain arguments and produce certain outputs. An API promises to return specific formats. A function promises to transform inputs predictably.

These promises are contracts. Contract tests verify that implementations honor them.

Unlike unit tests (which test internal logic) or integration tests (which test system behavior), contract tests focus on the interface—the promise between components.

**The problem: Interface changes break integrations. Without contract tests, breaks are discovered in production or by downstream consumers.**

---

**The forces at play:**

- *Speed wants fast tests.* Contract tests should be quicker than integration tests.

- *Coverage wants comprehensiveness.* Every contract term should be tested.

- *Evolution wants flexibility.* Contracts change; tests must adapt.

- *Independence wants isolation.* Contract tests shouldn't need the whole system.

The tension: verify contracts thoroughly without coupling tests to implementation details.

---

**Therefore:**

Generate contract tests from interface specifications that verify input acceptance and output conformance without testing internal logic.

**CLI contract (from specification):**

```turtle
cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    cli:acceptsArgument [
        sk:name "file" ;
        cli:type "Path" ;
        cli:required true
    ] ;
    cli:returns [
        cli:exitCode 0 ;
        cli:when "valid file"
    ] ;
    cli:returns [
        cli:exitCode 1 ;
        cli:when "invalid file"
    ] ;
    cli:returns [
        cli:exitCode 2 ;
        cli:when "file not found"
    ] .
```

**Generated contract test:**

```python
# tests/contract/test_validate_contract.py
"""Contract tests for validate command.

These tests verify the command honors its interface contract,
not its internal implementation.
"""

import pytest
from typer.testing import CliRunner
from specify_cli.app import app

runner = CliRunner()


class TestValidateContract:
    """Contract tests for validate command interface."""

    # ═══════════════════════════════════════════════════════════
    # Input Contract: Required arguments
    # ═══════════════════════════════════════════════════════════

    def test_contract_requires_file_argument(self):
        """Contract: 'file' argument is required."""
        result = runner.invoke(app, ["validate"])
        # Missing required argument should fail
        assert result.exit_code != 0
        assert "file" in result.output.lower() or "missing" in result.output.lower()

    def test_contract_accepts_file_path(self, tmp_path):
        """Contract: Command accepts a file path."""
        test_file = tmp_path / "test.ttl"
        test_file.write_text("@prefix ex: <http://example.org/> .")

        result = runner.invoke(app, ["validate", str(test_file)])
        # Should not fail due to argument parsing
        assert "argument" not in result.output.lower() or result.exit_code == 0

    # ═══════════════════════════════════════════════════════════
    # Output Contract: Exit codes
    # ═══════════════════════════════════════════════════════════

    def test_contract_exit_0_for_valid(self, tmp_path):
        """Contract: Exit code 0 for valid file."""
        valid = tmp_path / "valid.ttl"
        valid.write_text("@prefix ex: <http://example.org/> . ex:a ex:b ex:c .")

        result = runner.invoke(app, ["validate", str(valid)])
        assert result.exit_code == 0

    def test_contract_exit_1_for_invalid(self, tmp_path):
        """Contract: Exit code 1 for invalid file."""
        invalid = tmp_path / "invalid.ttl"
        invalid.write_text("not valid turtle syntax")

        result = runner.invoke(app, ["validate", str(invalid)])
        assert result.exit_code == 1

    def test_contract_exit_2_for_not_found(self):
        """Contract: Exit code 2 for file not found."""
        result = runner.invoke(app, ["validate", "/nonexistent/file.ttl"])
        assert result.exit_code == 2

    # ═══════════════════════════════════════════════════════════
    # Output Contract: Output format
    # ═══════════════════════════════════════════════════════════

    def test_contract_valid_includes_success_indicator(self, tmp_path):
        """Contract: Valid file output includes success indicator."""
        valid = tmp_path / "valid.ttl"
        valid.write_text("@prefix ex: <http://example.org/> .")

        result = runner.invoke(app, ["validate", str(valid)])
        assert "valid" in result.output.lower() or "✓" in result.output

    def test_contract_invalid_includes_error_details(self, tmp_path):
        """Contract: Invalid file output includes error details."""
        invalid = tmp_path / "invalid.ttl"
        invalid.write_text("invalid")

        result = runner.invoke(app, ["validate", str(invalid)])
        # Should mention what's wrong
        assert len(result.output) > 10  # More than just "Error"
```

**Contract vs. unit tests:**

| Aspect | Contract Test | Unit Test |
|--------|---------------|-----------|
| Focus | Interface promise | Internal logic |
| Coupling | To interface | To implementation |
| Scope | Input/output only | All branches |
| Stability | Stable (interface) | May change (refactoring) |

---

**Resulting context:**

After applying this pattern, you have:

- Verified interface contracts
- Fast-running contract tests
- Decoupled tests from implementation details
- Early detection of interface breaks

This complements **[31. Test Before Code](./test-before-code.md)** and enables **[33. Integration Reality](./integration-reality.md)**.

---

**Related patterns:**

- *Complements:* **[31. Test Before Code](./test-before-code.md)** — Different focus
- *Enables:* **[33. Integration Reality](./integration-reality.md)** — Contracts verified
- *Supports:* **[37. Continuous Validation](./continuous-validation.md)** — Fast CI tests
- *Derives from:* **[11. Executable Specification](../specification/executable-specification.md)** — Specs define contracts

---

> *"A contract is a meeting of minds."*

Contract tests verify that the implementation's mind matches the specification's mind. They're the handshake between what was promised and what was delivered.
