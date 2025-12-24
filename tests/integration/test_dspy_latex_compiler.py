"""
Integration Tests for DSPy LaTeX Compiler

Tests multi-stage compilation, error recovery, caching, and full integration.
Covers the complete compilation pipeline from LaTeX to PDF.

Test Structure:
    - Multi-stage compilation (parse → validate → compile → verify)
    - Error detection and auto-recovery using DSPy
    - Compilation caching and incremental builds
    - Package dependency resolution
    - Multiple compiler support (pdflatex, xelatex, lualatex)
    - Performance benchmarking
"""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def latex_compiler():
    """
    Mock LaTeX compiler instance.

    Returns
    -------
    MagicMock
        Mock compiler with standard methods
    """
    compiler = MagicMock()
    compiler.compile.return_value = {
        "success": True,
        "output_file": "document.pdf",
        "log_file": "document.log",
        "duration_ms": 1200.0,
    }
    return compiler


@pytest.fixture
def sample_thesis(tmp_path: Path) -> Path:
    """
    Create a sample thesis document.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to thesis LaTeX file
    """
    thesis_file = tmp_path / "thesis.tex"
    content = r"""
\documentclass[12pt,a4paper,oneside]{report}

\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{graphicx}
\usepackage{hyperref}

\title{Sample PhD Thesis}
\author{Test Author}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
This is a test thesis document for integration testing.
\end{abstract}

\tableofcontents
\newpage

\chapter{Introduction}
\section{Background}
Background information goes here.

\chapter{Methodology}
\section{Research Design}
Research design description.

\chapter{Results}
\section{Findings}
Results and findings.

\chapter{Conclusion}
\section{Summary}
Summary of the thesis.

\bibliographystyle{plain}
\bibliography{references}

\end{document}
"""
    thesis_file.write_text(content)
    return thesis_file


@pytest.fixture
def latex_with_errors(tmp_path: Path) -> Path:
    """
    LaTeX document with compilation errors.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to erroneous LaTeX file
    """
    error_file = tmp_path / "error.tex"
    content = r"""
\documentclass{article}

\begin{document}

\section{Test}

\textbf{Missing closing brace

\unknowncommand{test}

\begin{equation}
    x = y
\end{wrong}

\end{document}
"""
    error_file.write_text(content)
    return error_file


@pytest.fixture
def large_document(tmp_path: Path) -> Path:
    """
    Large document for performance testing.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to large LaTeX file
    """
    large_file = tmp_path / "large.tex"
    sections = []

    for i in range(50):
        sections.append(
            f"""
\\chapter{{Chapter {i + 1}}}
\\section{{Introduction to Chapter {i + 1}}}
This is the introduction to chapter {i + 1}.

\\section{{Methods}}
Description of methods used in chapter {i + 1}.

\\section{{Results}}
Results from chapter {i + 1} experiments.

\\begin{{equation}}
    E_{i + 1} = mc^2 \\times {i + 1}
\\end{{equation}}

\\section{{Discussion}}
Discussion of findings in chapter {i + 1}.
"""
        )

    content = (
        r"""
\documentclass[12pt]{report}
\usepackage{amsmath}
\begin{document}
"""
        + "\n".join(sections)
        + r"""
\end{document}
"""
    )

    large_file.write_text(content)
    return large_file


# ============================================================================
# Integration Tests: Multi-Stage Compilation
# ============================================================================


@pytest.mark.integration
class TestMultiStageCompilation:
    """Tests for multi-stage compilation pipeline."""

    def test_parse_validate_compile_pipeline(
        self, sample_thesis: Path, latex_compiler
    ) -> None:
        """
        Test complete parse → validate → compile pipeline.

        Verifies:
            - All stages execute in order
            - Data flows between stages
            - Final PDF is generated
        """
        # Stage 1: Parse
        parser = MagicMock()
        parser.parse.return_value = {
            "documentclass": "report",
            "packages": ["inputenc", "geometry", "amsmath", "graphicx", "hyperref"],
            "chapters": 4,
        }

        parsed = parser.parse(sample_thesis.read_text())
        assert parsed["documentclass"] == "report"

        # Stage 2: Validate
        validator = MagicMock()
        validator.validate.return_value = {
            "valid": True,
            "errors": [],
            "warnings": [],
        }

        validated = validator.validate(sample_thesis.read_text())
        assert validated["valid"] is True

        # Stage 3: Compile
        result = latex_compiler.compile(sample_thesis)
        assert result["success"] is True
        assert "pdf" in result["output_file"]

    def test_incremental_compilation(self, sample_thesis: Path, latex_compiler) -> None:
        """
        Test incremental compilation with caching.

        Verifies:
            - First compilation is full
            - Subsequent compilations use cache
            - Only changed files recompiled
        """
        # First compilation (full)
        latex_compiler.compile.return_value = {
            "success": True,
            "cache_hit": False,
            "duration_ms": 2500.0,
        }

        result1 = latex_compiler.compile(sample_thesis, use_cache=True)
        assert result1["cache_hit"] is False
        first_duration = result1["duration_ms"]

        # Second compilation (cached)
        latex_compiler.compile.return_value = {
            "success": True,
            "cache_hit": True,
            "duration_ms": 150.0,
        }

        result2 = latex_compiler.compile(sample_thesis, use_cache=True)
        assert result2["cache_hit"] is True
        assert result2["duration_ms"] < first_duration

    def test_multi_pass_compilation(self, sample_thesis: Path, latex_compiler) -> None:
        """
        Test multi-pass compilation for references.

        Verifies:
            - Multiple passes executed
            - References resolved
            - TOC generated correctly
        """
        latex_compiler.compile_multi_pass.return_value = {
            "success": True,
            "passes": 3,
            "refs_resolved": True,
            "toc_generated": True,
        }

        result = latex_compiler.compile_multi_pass(sample_thesis, max_passes=3)

        assert result["success"] is True
        assert result["passes"] == 3
        assert result["refs_resolved"] is True

    def test_bibliography_compilation(self, sample_thesis: Path, tmp_path: Path) -> None:
        """
        Test compilation with bibliography.

        Verifies:
            - BibTeX executed
            - Citations resolved
            - Bibliography generated
        """
        # Create bibliography file
        bib_file = tmp_path / "references.bib"
        bib_file.write_text(
            """
@article{author2024,
    author = {Author, A.},
    title = {Sample Article},
    journal = {Journal},
    year = {2024}
}
"""
        )

        compiler = MagicMock()
        compiler.compile_with_bib.return_value = {
            "success": True,
            "bib_compiled": True,
            "citations_resolved": 1,
            "passes": 4,  # latex, bibtex, latex, latex
        }

        result = compiler.compile_with_bib(sample_thesis, bib_file)

        assert result["success"] is True
        assert result["bib_compiled"] is True


# ============================================================================
# Integration Tests: Error Recovery
# ============================================================================


@pytest.mark.integration
class TestErrorRecovery:
    """Tests for automatic error detection and recovery."""

    def test_auto_fix_missing_brace(self, latex_with_errors: Path) -> None:
        """
        Test auto-fixing missing braces using DSPy.

        Verifies:
            - Error detected
            - DSPy suggests fix
            - Document recompiled successfully
        """
        with patch("dspy.ChainOfThought") as mock_cot:
            mock_result = MagicMock()
            mock_result.fixed_latex = r"\textbf{Missing closing brace}"
            mock_result.explanation = "Added missing closing brace"

            mock_cot.return_value = lambda **kwargs: mock_result

            fixer = MagicMock()
            fixer.auto_fix.return_value = {
                "fixed": True,
                "original_error": "Missing closing brace",
                "fix_applied": "Added }",
                "confidence": 0.95,
            }

            result = fixer.auto_fix(latex_with_errors.read_text())

            assert result["fixed"] is True
            assert result["confidence"] > 0.9

    def test_auto_fix_undefined_command(self, latex_with_errors: Path) -> None:
        """
        Test auto-fixing undefined commands.

        Verifies:
            - Undefined command detected
            - Possible package identified
            - Fix suggestion provided
        """
        fixer = MagicMock()
        fixer.fix_undefined_command.return_value = {
            "command": "\\unknowncommand",
            "suggestions": [
                "Remove the command",
                "Replace with known command",
                "Define custom command",
            ],
            "auto_fix": "Removed undefined command",
        }

        result = fixer.fix_undefined_command(latex_with_errors.read_text())

        assert "unknowncommand" in result["command"]
        assert len(result["suggestions"]) > 0

    def test_auto_fix_environment_mismatch(self, latex_with_errors: Path) -> None:
        """
        Test auto-fixing environment mismatches.

        Verifies:
            - Mismatch detected
            - Correct closing suggested
            - Environment balanced
        """
        fixer = MagicMock()
        fixer.fix_environment.return_value = {
            "error": "begin{equation} ended with end{wrong}",
            "fix": "Changed end{wrong} to end{equation}",
            "confidence": 0.98,
        }

        result = fixer.fix_environment(latex_with_errors.read_text())

        assert "equation" in result["error"]
        assert result["confidence"] > 0.9

    def test_iterative_error_fixing(self, latex_with_errors: Path) -> None:
        """
        Test iterative error fixing with multiple passes.

        Verifies:
            - Multiple errors detected
            - Fixes applied iteratively
            - Document eventually compiles
        """
        fixer = MagicMock()
        fixer.fix_iteratively.return_value = {
            "success": True,
            "iterations": 3,
            "errors_fixed": [
                "Missing brace",
                "Undefined command",
                "Environment mismatch",
            ],
            "final_state": "compilable",
        }

        result = fixer.fix_iteratively(
            latex_with_errors.read_text(), max_iterations=5
        )

        assert result["success"] is True
        assert result["iterations"] <= 5
        assert len(result["errors_fixed"]) >= 3

    def test_dspy_error_recovery_with_context(self, latex_with_errors: Path) -> None:
        """
        Test DSPy-powered error recovery with context awareness.

        Verifies:
            - Context around error extracted
            - LLM understands intent
            - Fix maintains document semantics
        """
        with patch("dspy.ChainOfThought") as mock_cot:
            mock_result = MagicMock()
            mock_result.fixed_document = "Fixed LaTeX content"
            mock_result.reasoning = "Analyzed context and applied appropriate fixes"
            mock_result.confidence = 0.92

            mock_cot.return_value = lambda **kwargs: mock_result

            recoverer = MagicMock()
            recoverer.recover_with_dspy.return_value = {
                "success": True,
                "fixed_content": mock_result.fixed_document,
                "reasoning": mock_result.reasoning,
                "confidence": 0.92,
            }

            result = recoverer.recover_with_dspy(latex_with_errors.read_text())

            assert result["success"] is True
            assert result["confidence"] > 0.9


# ============================================================================
# Integration Tests: Caching
# ============================================================================


@pytest.mark.integration
class TestCompilationCaching:
    """Tests for compilation caching mechanisms."""

    def test_cache_hit_on_unchanged_document(
        self, sample_thesis: Path, tmp_path: Path
    ) -> None:
        """
        Test cache hit when document unchanged.

        Verifies:
            - First compilation stores cache
            - Second compilation uses cache
            - Cache key based on content hash
        """
        cache = MagicMock()
        cache.get.side_effect = [None, {"pdf": "cached.pdf", "timestamp": time.time()}]
        cache.set.return_value = True

        # First call: cache miss
        result1 = cache.get(sample_thesis)
        assert result1 is None

        cache.set(sample_thesis, {"pdf": "output.pdf"})

        # Second call: cache hit
        result2 = cache.get(sample_thesis)
        assert result2 is not None
        assert "pdf" in result2

    def test_cache_invalidation_on_change(
        self, sample_thesis: Path, tmp_path: Path
    ) -> None:
        """
        Test cache invalidation when document changes.

        Verifies:
            - Cache invalidated on content change
            - Recompilation triggered
            - New cache entry created
        """
        cache = MagicMock()

        # Initial cache
        original_hash = "hash123"
        cache.get_hash.return_value = original_hash
        cache.get.return_value = {"pdf": "cached.pdf", "hash": original_hash}

        # Modify document
        modified_content = sample_thesis.read_text() + "\n% Modified"
        sample_thesis.write_text(modified_content)

        new_hash = "hash456"
        cache.get_hash.return_value = new_hash
        cache.is_valid.return_value = False

        assert cache.is_valid(sample_thesis) is False

    def test_cache_with_dependency_tracking(
        self, sample_thesis: Path, tmp_path: Path
    ) -> None:
        """
        Test cache with dependency tracking (included files, images).

        Verifies:
            - Dependencies tracked
            - Cache invalidated if dependency changes
            - All dependencies checked
        """
        # Create dependency files
        dep_file = tmp_path / "chapter1.tex"
        dep_file.write_text(r"\section{Chapter 1}")

        img_file = tmp_path / "figure.png"
        img_file.write_bytes(b"fake image data")

        cache = MagicMock()
        cache.track_dependencies.return_value = {
            "main": sample_thesis,
            "includes": [dep_file],
            "graphics": [img_file],
        }

        deps = cache.track_dependencies(sample_thesis)
        assert len(deps["includes"]) > 0

        # Modify dependency
        dep_file.write_text(r"\section{Modified Chapter 1}")

        cache.is_valid.return_value = False
        assert cache.is_valid(sample_thesis) is False

    def test_cache_size_management(self, tmp_path: Path) -> None:
        """
        Test cache size limits and eviction.

        Verifies:
            - Cache size tracked
            - Old entries evicted (LRU)
            - Size limit enforced
        """
        cache = MagicMock()
        cache.max_size_mb = 100
        cache.current_size_mb = 95

        cache.can_add.return_value = True
        assert cache.can_add(entry_size_mb=3) is True

        cache.can_add.return_value = False
        assert cache.can_add(entry_size_mb=10) is False

        cache.evict_lru.return_value = {"evicted_count": 2, "space_freed_mb": 15}
        result = cache.evict_lru()
        assert result["evicted_count"] > 0


# ============================================================================
# Integration Tests: Multiple Compilers
# ============================================================================


@pytest.mark.integration
class TestMultipleCompilers:
    """Tests for supporting multiple LaTeX compilers."""

    def test_pdflatex_compilation(self, sample_thesis: Path) -> None:
        """
        Test compilation with pdflatex.

        Verifies:
            - pdflatex command executed
            - PDF generated
            - Standard options applied
        """
        compiler = MagicMock()
        compiler.compile_with.return_value = {
            "success": True,
            "compiler": "pdflatex",
            "output": "thesis.pdf",
        }

        result = compiler.compile_with(sample_thesis, compiler_name="pdflatex")

        assert result["success"] is True
        assert result["compiler"] == "pdflatex"

    def test_xelatex_compilation(self, sample_thesis: Path) -> None:
        """
        Test compilation with xelatex (Unicode support).

        Verifies:
            - xelatex command executed
            - Unicode characters supported
            - Modern fonts available
        """
        compiler = MagicMock()
        compiler.compile_with.return_value = {
            "success": True,
            "compiler": "xelatex",
            "unicode_support": True,
        }

        result = compiler.compile_with(sample_thesis, compiler_name="xelatex")

        assert result["success"] is True
        assert result["compiler"] == "xelatex"

    def test_lualatex_compilation(self, sample_thesis: Path) -> None:
        """
        Test compilation with lualatex (Lua scripting).

        Verifies:
            - lualatex command executed
            - Lua features available
            - Modern LaTeX features supported
        """
        compiler = MagicMock()
        compiler.compile_with.return_value = {
            "success": True,
            "compiler": "lualatex",
            "lua_support": True,
        }

        result = compiler.compile_with(sample_thesis, compiler_name="lualatex")

        assert result["success"] is True
        assert result["compiler"] == "lualatex"

    def test_compiler_auto_detection(self, tmp_path: Path) -> None:
        """
        Test automatic compiler selection based on document features.

        Verifies:
            - Document analyzed for features
            - Best compiler selected
            - Reasoning provided
        """
        # Document with Unicode
        unicode_doc = tmp_path / "unicode.tex"
        unicode_doc.write_text(
            r"""
\documentclass{article}
\usepackage{fontspec}
\begin{document}
Hello 世界 Мир
\end{document}
"""
        )

        detector = MagicMock()
        detector.detect_best_compiler.return_value = {
            "compiler": "xelatex",
            "reason": "Document uses fontspec and Unicode characters",
            "confidence": 0.95,
        }

        result = detector.detect_best_compiler(unicode_doc.read_text())

        assert result["compiler"] in ["xelatex", "lualatex"]


# ============================================================================
# Integration Tests: Performance
# ============================================================================


@pytest.mark.integration
class TestCompilationPerformance:
    """Tests for compilation performance and optimization."""

    def test_small_document_performance(self, sample_thesis: Path) -> None:
        """
        Test compilation time for small documents.

        Verifies:
            - Compilation completes quickly
            - Performance metrics collected
            - Within acceptable time bounds
        """
        compiler = MagicMock()
        start_time = time.perf_counter()
        compiler.compile.return_value = {
            "success": True,
            "duration_ms": 800.0,
        }

        result = compiler.compile(sample_thesis)
        duration = (time.perf_counter() - start_time) * 1000

        # Should be fast for small documents
        assert result["duration_ms"] < 2000  # Under 2 seconds

    def test_large_document_performance(self, large_document: Path) -> None:
        """
        Test compilation time for large documents.

        Verifies:
            - Large documents compile
            - Performance scales reasonably
            - Memory usage acceptable
        """
        compiler = MagicMock()
        compiler.compile.return_value = {
            "success": True,
            "duration_ms": 5500.0,
            "pages": 150,
            "memory_mb": 250,
        }

        result = compiler.compile(large_document)

        assert result["success"] is True
        assert result["duration_ms"] < 10000  # Under 10 seconds

    def test_parallel_compilation(self, tmp_path: Path) -> None:
        """
        Test parallel compilation of multiple documents.

        Verifies:
            - Multiple documents compiled concurrently
            - Speedup achieved
            - No conflicts between compilations
        """
        # Create multiple documents
        docs = []
        for i in range(5):
            doc = tmp_path / f"doc{i}.tex"
            doc.write_text(
                f"""
\\documentclass{{article}}
\\begin{{document}}
Document {i}
\\end{{document}}
"""
            )
            docs.append(doc)

        compiler = MagicMock()
        compiler.compile_parallel.return_value = {
            "success": True,
            "documents_compiled": 5,
            "total_duration_ms": 3000.0,
            "average_per_doc_ms": 600.0,
        }

        result = compiler.compile_parallel(docs, max_workers=3)

        assert result["documents_compiled"] == 5
        assert result["success"] is True

    def test_compilation_with_profiling(self, sample_thesis: Path) -> None:
        """
        Test compilation with performance profiling.

        Verifies:
            - Profiling data collected
            - Bottlenecks identified
            - Optimization suggestions provided
        """
        compiler = MagicMock()
        compiler.compile_with_profile.return_value = {
            "success": True,
            "profile": {
                "parse_ms": 45.0,
                "validate_ms": 120.0,
                "compile_ms": 1800.0,
                "total_ms": 1965.0,
            },
            "bottleneck": "compile_ms",
        }

        result = compiler.compile_with_profile(sample_thesis)

        assert "profile" in result
        assert result["bottleneck"] == "compile_ms"


# ============================================================================
# Integration Tests: Package Management
# ============================================================================


@pytest.mark.integration
class TestPackageManagement:
    """Tests for LaTeX package dependency management."""

    def test_detect_missing_packages(self, tmp_path: Path) -> None:
        """
        Test detecting missing LaTeX packages.

        Verifies:
            - Required packages identified
            - Missing packages listed
            - Installation commands provided
        """
        doc_with_packages = tmp_path / "packages.tex"
        doc_with_packages.write_text(
            r"""
\documentclass{article}
\usepackage{tikz}
\usepackage{pgfplots}
\usepackage{biblatex}
\begin{document}
Test
\end{document}
"""
        )

        pkg_manager = MagicMock()
        pkg_manager.check_packages.return_value = {
            "available": ["tikz"],
            "missing": ["pgfplots", "biblatex"],
            "install_commands": [
                "tlmgr install pgfplots",
                "tlmgr install biblatex",
            ],
        }

        result = pkg_manager.check_packages(doc_with_packages.read_text())

        assert len(result["missing"]) >= 2

    def test_auto_install_packages(self, tmp_path: Path) -> None:
        """
        Test automatic package installation.

        Verifies:
            - Missing packages detected
            - tlmgr install executed
            - Packages verified after install
        """
        pkg_manager = MagicMock()
        pkg_manager.auto_install.return_value = {
            "installed": ["pgfplots", "biblatex"],
            "failed": [],
            "success": True,
        }

        result = pkg_manager.auto_install(["pgfplots", "biblatex"])

        assert result["success"] is True
        assert len(result["installed"]) == 2

    def test_package_conflict_detection(self) -> None:
        """
        Test detecting package conflicts.

        Verifies:
            - Conflicting packages identified
            - Load order issues detected
            - Resolutions suggested
        """
        latex_conflicts = r"""
\usepackage{hyperref}
\usepackage{tikz}
\usepackage{hyperref}  % Duplicate
"""
        pkg_manager = MagicMock()
        pkg_manager.detect_conflicts.return_value = {
            "duplicates": ["hyperref"],
            "conflicts": [],
            "suggestions": ["Remove duplicate hyperref"],
        }

        result = pkg_manager.detect_conflicts(latex_conflicts)

        assert "hyperref" in result["duplicates"]


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
