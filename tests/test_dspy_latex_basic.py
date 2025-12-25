"""
Basic tests for dspy_latex module.

Tests basic imports and class instantiation.
"""

import pytest
from pathlib import Path


def test_imports():
    """Test that all main classes can be imported."""
    from specify_cli.dspy_latex import (
        PDFCompiler,
        CompilationCache,
        ErrorRecovery,
        CompilationMetrics,
        CompilationBackend,
        StageType,
        ErrorSeverity,
    )

    assert PDFCompiler is not None
    assert CompilationCache is not None
    assert ErrorRecovery is not None
    assert CompilationMetrics is not None
    assert CompilationBackend is not None
    assert StageType is not None
    assert ErrorSeverity is not None


def test_compiler_instantiation():
    """Test PDFCompiler can be instantiated."""
    from specify_cli.dspy_latex import PDFCompiler, CompilationBackend

    # Default constructor
    compiler = PDFCompiler()
    assert compiler.backend == CompilationBackend.PDFLATEX
    assert compiler.enable_recovery is True
    assert compiler.max_retries == 3

    # Custom backend
    compiler_xe = PDFCompiler(backend=CompilationBackend.XELATEX)
    assert compiler_xe.backend == CompilationBackend.XELATEX


def test_cache_instantiation():
    """Test CompilationCache can be instantiated."""
    from specify_cli.dspy_latex import CompilationCache

    cache = CompilationCache()
    assert cache.cache_dir.name == ".latex_cache"
    assert cache.max_cache_size == 1000 * 1024 * 1024

    # Custom settings
    cache_custom = CompilationCache(
        cache_dir=Path("/tmp/test_cache"), max_cache_size=500
    )
    assert cache_custom.cache_dir == Path("/tmp/test_cache")
    assert cache_custom.max_cache_size == 500 * 1024 * 1024


def test_error_recovery_instantiation():
    """Test ErrorRecovery can be instantiated."""
    from specify_cli.dspy_latex import ErrorRecovery

    recovery = ErrorRecovery()
    assert recovery.max_fix_attempts == 3

    recovery_custom = ErrorRecovery(enable_dspy=False, max_fix_attempts=5)
    assert recovery_custom.max_fix_attempts == 5


def test_enums():
    """Test enum values."""
    from specify_cli.dspy_latex import (
        CompilationBackend,
        StageType,
        ErrorSeverity,
    )

    # CompilationBackend
    assert CompilationBackend.PDFLATEX.value == "pdflatex"
    assert CompilationBackend.XELATEX.value == "xelatex"
    assert CompilationBackend.LUALATEX.value == "lualatex"

    # StageType
    assert StageType.NORMALIZE.value == "normalize"
    assert StageType.PREPROCESS.value == "preprocess"
    assert StageType.COMPILE.value == "compile"
    assert StageType.POSTPROCESS.value == "postprocess"
    assert StageType.OPTIMIZE.value == "optimize"

    # ErrorSeverity
    assert ErrorSeverity.WARNING.value == "warning"
    assert ErrorSeverity.ERROR.value == "error"
    assert ErrorSeverity.CRITICAL.value == "critical"


def test_data_classes():
    """Test data class instantiation."""
    from specify_cli.dspy_latex import (
        LaTeXError,
        ErrorSeverity,
        CompilationMetrics,
    )

    # LaTeXError
    error = LaTeXError(
        severity=ErrorSeverity.ERROR,
        message="Test error",
        line=42,
    )
    assert error.severity == ErrorSeverity.ERROR
    assert error.message == "Test error"
    assert error.line == 42

    # CompilationMetrics
    metrics = CompilationMetrics()
    assert metrics.total_duration == 0.0
    assert metrics.error_count == 0

    metrics_dict = metrics.to_dict()
    assert isinstance(metrics_dict, dict)
    assert "total_duration" in metrics_dict


def test_stage_base_class():
    """Test CompilationStage base class."""
    from specify_cli.dspy_latex.compiler import CompilationStage, StageType

    stage = CompilationStage(StageType.NORMALIZE)
    assert stage.stage_type == StageType.NORMALIZE
    assert stage.enable_recovery is True
    assert stage.max_retries == 3

    # Test hash function
    hash1 = stage._hash("test content")
    assert len(hash1) == 64  # SHA256 hex
    assert hash1 == stage._hash("test content")  # Deterministic


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
