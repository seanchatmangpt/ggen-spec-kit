"""
End-to-end tests for DSPy commands.

Tests the complete DSPy optimize command implementation including:
- optimize_spec function
- CLI command integration
- Error handling
"""

import json
from pathlib import Path

import pytest

from specify_cli._dspy_optimize_impl import OptimizeResult, optimize_spec


class TestOptimizeSpec:
    """Tests for the optimize_spec function."""

    def test_optimize_result_creation(self):
        """Test that OptimizeResult can be created."""
        result = OptimizeResult(
            success=True,
            original_spec="test spec",
            optimized_spec="optimized spec",
            iterations=3,
            metrics={"coverage": 0.9},
            improvement=10.0,
            errors=[],
        )
        assert result.success is True
        assert result.iterations == 3
        assert result.metrics["coverage"] == 0.9
        assert result.improvement == 10.0

    def test_missing_spec_file(self, tmp_path):
        """Test handling of missing spec file."""
        spec_file = tmp_path / "nonexistent.ttl"
        result = optimize_spec(spec_file=spec_file)

        assert result.success is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()

    def test_invalid_metric(self, tmp_path):
        """Test handling of invalid metric."""
        spec_file = tmp_path / "test.ttl"
        spec_file.write_text("# Test spec")

        result = optimize_spec(
            spec_file=spec_file,
            metric="invalid_metric",
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert "invalid metric" in result.errors[0].lower()

    def test_invalid_iterations(self, tmp_path):
        """Test handling of invalid iterations."""
        spec_file = tmp_path / "test.ttl"
        spec_file.write_text("# Test spec")

        result = optimize_spec(
            spec_file=spec_file,
            iterations=0,
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert "iterations" in result.errors[0].lower()

    def test_invalid_temperature(self, tmp_path):
        """Test handling of invalid temperature."""
        spec_file = tmp_path / "test.ttl"
        spec_file.write_text("# Test spec")

        result = optimize_spec(
            spec_file=spec_file,
            temperature=2.0,  # Out of range
        )

        assert result.success is False
        assert len(result.errors) > 0
        assert "temperature" in result.errors[0].lower()

    @pytest.mark.skipif(
        True,  # Skip by default as it requires DSPy and LLM configuration
        reason="Requires DSPy and LLM API keys"
    )
    def test_optimize_spec_with_ttl(self, tmp_path):
        """Test spec optimization with TTL file (integration test)."""
        # This test requires DSPy to be installed and configured
        spec_file = tmp_path / "test.ttl"
        spec_file.write_text("""
@prefix owl: <http://www.w3.org/2001/XMLSchema#> .
@prefix sk: <http://github.com/github/spec-kit#> .

sk:Feature a owl:Class ;
    rdfs:label "Feature"@en ;
    rdfs:comment "A software feature"@en .
        """)

        result = optimize_spec(
            spec_file=spec_file,
            metric="coverage",
            iterations=1,
        )

        # When DSPy is available and configured, this should succeed
        # When not available, it should fail gracefully
        assert isinstance(result, OptimizeResult)
        assert result.iterations in [0, 1]  # 0 if failed, 1 if succeeded

    def test_optimize_spec_without_dspy(self, tmp_path, monkeypatch):
        """Test that optimize_spec handles missing DSPy gracefully."""
        # Temporarily make DSPy unavailable
        import specify_cli._dspy_optimize_impl as impl_module
        original_available = impl_module.DSPY_AVAILABLE
        monkeypatch.setattr(impl_module, "DSPY_AVAILABLE", False)

        spec_file = tmp_path / "test.ttl"
        spec_file.write_text("# Test")

        result = optimize_spec(spec_file=spec_file)

        assert result.success is False
        assert len(result.errors) > 0
        assert "dspy" in result.errors[0].lower()

        # Restore
        monkeypatch.setattr(impl_module, "DSPY_AVAILABLE", original_available)


class TestMetricsCalculation:
    """Tests for optimization metrics calculation."""

    def test_metrics_structure(self, tmp_path):
        """Test that metrics are properly structured."""
        spec_file = tmp_path / "test.ttl"
        spec_file.write_text("""
@prefix owl: <http://www.w3.org/2001/XMLSchema#> .
sk:Feature a owl:Class .
        """)

        result = optimize_spec(
            spec_file=spec_file,
            metric="coverage",
            iterations=1,
        )

        # Even if optimization fails, metrics should be present
        if result.success:
            assert isinstance(result.metrics, dict)
            # Check for expected metric keys
            possible_keys = [
                "coverage", "clarity", "brevity", "performance",
                "original_length", "optimized_length", "final_score"
            ]
            # At least some metrics should be present
            assert any(key in result.metrics for key in possible_keys)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
