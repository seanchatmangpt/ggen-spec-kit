"""
Unit tests for specify_cli.ops.dod
"""

import pytest

from specify_cli.core.dod_types import DoDCheckResult, DoDGate
from specify_cli.ops import dod


class TestValidateInputs:
    """Test input validation."""

    def test_validate_empty_inputs(self) -> None:
        """Empty inputs should pass validation."""
        result = dod.validate_inputs()
        assert result.get("valid") is True

    def test_validate_valid_inputs(self) -> None:
        """Valid inputs should pass validation."""
        result = dod.validate_inputs(test="value")
        assert result.get("valid") is True

    def test_validate_strict_flag(self) -> None:
        """Strict flag should be accepted."""
        result = dod.validate_inputs(strict=True)
        assert result.get("valid") is True

    def test_validate_invalid_strict_flag(self) -> None:
        """Invalid strict flag should raise ValueError."""
        with pytest.raises(ValueError):
            dod.validate_inputs(strict="invalid")


class TestDoDGate:
    """Test DoDGate dataclass."""

    def test_gate_creation(self) -> None:
        """DoDGate should be creatable with required fields."""
        gate = DoDGate(
            name="Test Gate",
            category="Test",
            passed=True,
        )
        assert gate.name == "Test Gate"
        assert gate.category == "Test"
        assert gate.passed is True
        assert gate.error is None

    def test_gate_with_details(self) -> None:
        """DoDGate should support details."""
        gate = DoDGate(
            name="Test Gate",
            category="Test",
            passed=True,
            details={"key": "value"},
        )
        assert gate.details == {"key": "value"}

    def test_gate_with_error(self) -> None:
        """DoDGate should support error tracking."""
        gate = DoDGate(
            name="Test Gate",
            category="Test",
            passed=False,
            error="Test error",
        )
        assert gate.error == "Test error"


class TestDoDCheckResult:
    """Test DoDCheckResult dataclass."""

    def test_result_creation(self) -> None:
        """DoDCheckResult should be creatable."""
        result = DoDCheckResult(success=True)
        assert result.success is True
        assert result.total_gates == 0
        assert result.passed_gates == 0

    def test_result_to_dict(self) -> None:
        """DoDCheckResult should convert to dict."""
        gate = DoDGate(
            name="Test Gate",
            category="Test",
            passed=True,
        )
        result = DoDCheckResult(
            success=True,
            total_gates=1,
            passed_gates=1,
            gates=[gate],
        )
        result_dict = result.to_dict()
        assert result_dict["success"] is True
        assert result_dict["total"] == 1
        assert result_dict["completed"] == 1
        assert result_dict["failed"] == 0
        assert len(result_dict["gates"]) == 1

    def test_result_with_failed_gates(self) -> None:
        """DoDCheckResult should track failed gates."""
        failed_gate = DoDGate(
            name="Failed Gate",
            category="Test",
            passed=False,
            error="Test error",
        )
        result = DoDCheckResult(
            success=False,
            total_gates=1,
            passed_gates=0,
            failed_gates=[failed_gate],
            gates=[failed_gate],
        )
        result_dict = result.to_dict()
        assert result_dict["success"] is False
        assert result_dict["failed"] == 1


class TestCheckDod:
    """Test check_dod operation."""

    def test_check_dod_returns_dict(self) -> None:
        """check_dod should return a dictionary."""
        result = dod.check_dod()
        assert isinstance(result, dict)
        assert "success" in result
        assert "total" in result
        assert "completed" in result

    def test_check_dod_with_strict_mode(self) -> None:
        """check_dod should accept strict mode."""
        result = dod.check_dod(strict=True)
        assert isinstance(result, dict)
        assert result.get("strict") is True

    def test_check_dod_structure(self) -> None:
        """check_dod result should have expected structure."""
        result = dod.check_dod()
        expected_keys = {"success", "total", "completed", "failed", "duration", "strict", "gates"}
        assert set(result.keys()) == expected_keys

    def test_check_dod_gates_list(self) -> None:
        """check_dod should return gates list."""
        result = dod.check_dod()
        assert "gates" in result
        assert isinstance(result["gates"], list)
        # Should have at least the basic gates
        assert len(result["gates"]) > 0


class TestExceptionHandling:
    """Test exception handling."""

    def test_validate_inputs_with_invalid_strict(self) -> None:
        """Invalid strict value should raise ValueError."""
        with pytest.raises(ValueError):
            dod.validate_inputs(strict="not_a_bool")

    def test_validate_inputs_error_message(self) -> None:
        """ValueError should contain helpful message."""
        with pytest.raises(ValueError, match="strict option must be boolean"):
            dod.validate_inputs(strict="invalid")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
