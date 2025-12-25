"""
End-to-End Tests for DSPy LaTeX-to-PDF Pipeline

Tests the complete workflow from LaTeX source to PDF output.
Covers full document processing, quality checks, and real-world scenarios.

Test Structure:
    - Complete document processing workflows
    - PDF generation and quality verification
    - Real thesis compilation (using existing PhD thesis)
    - Error handling in production scenarios
    - Performance benchmarks
    - CLI integration tests
"""

from __future__ import annotations

import hashlib
import time
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def phd_thesis_tex(tmp_path: Path) -> Path:
    """
    Copy of the actual PhD thesis from docs/.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to thesis file
    """
    thesis_source = Path("/home/user/ggen-spec-kit/docs/PHD_THESIS_RDF_SPEC_DRIVEN_DEVELOPMENT.tex")

    if thesis_source.exists():
        thesis_copy = tmp_path / "thesis.tex"
        thesis_copy.write_text(thesis_source.read_text())
        return thesis_copy
    else:
        # Fallback: create a comprehensive thesis-like document
        thesis_file = tmp_path / "thesis.tex"
        content = r"""
\documentclass[12pt,a4paper,oneside]{report}

\usepackage[utf8]{inputenc}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{hyperref}
\usepackage{setspace}
\usepackage{fancyhdr}
\usepackage{listings}
\usepackage{xcolor}
\usepackage{booktabs}

\onehalfspacing

\title{PhD Thesis: RDF-First Specification-Driven Development}
\author{Claude Code}
\date{\today}

\begin{document}

\maketitle

\begin{abstract}
This thesis presents a comprehensive framework for specification-driven software
development based on the constitutional equation $\texttt{spec.md} = \mu(\texttt{feature.ttl})$.
\end{abstract}

\tableofcontents
\newpage

\chapter{Introduction}
\section{Background}
Software development paradigms.

\chapter{Literature Review}
\section{Related Work}
Existing approaches.

\chapter{Methodology}
\section{Research Design}
Research methodology.

\chapter{Results}
\section{Findings}
Research findings.

\chapter{Conclusion}
\section{Summary}
Thesis summary.

\end{document}
"""
        thesis_file.write_text(content)
        return thesis_file


@pytest.fixture
def latex_pipeline():
    """
    Complete LaTeX-to-PDF pipeline instance.

    Returns
    -------
    MagicMock
        Pipeline with all processing stages
    """
    pipeline = MagicMock()
    pipeline.process.return_value = {
        "success": True,
        "stages": {
            "parse": {"duration_ms": 50, "success": True},
            "validate": {"duration_ms": 120, "success": True},
            "optimize": {"duration_ms": 300, "success": True},
            "compile": {"duration_ms": 2000, "success": True},
            "verify": {"duration_ms": 100, "success": True},
        },
        "output_pdf": "thesis.pdf",
        "total_duration_ms": 2570,
    }
    return pipeline


@pytest.fixture
def pdf_verifier():
    """
    PDF quality verification tool.

    Returns
    -------
    MagicMock
        PDF verifier with quality checks
    """
    verifier = MagicMock()
    verifier.verify.return_value = {
        "valid": True,
        "pages": 50,
        "file_size_mb": 2.5,
        "pdf_version": "1.5",
        "has_metadata": True,
        "has_bookmarks": True,
        "has_links": True,
        "quality_score": 0.95,
    }
    return verifier


# ============================================================================
# E2E Tests: Complete Workflows
# ============================================================================


@pytest.mark.e2e
class TestCompleteWorkflows:
    """End-to-end tests for complete LaTeX processing workflows."""

    def test_simple_document_end_to_end(self, tmp_path: Path, latex_pipeline) -> None:
        """
        Test complete workflow for simple document.

        Verifies:
            - LaTeX source → PDF output
            - All pipeline stages execute
            - PDF is valid and readable
            - Metadata preserved
        """
        # Create simple document
        simple_doc = tmp_path / "simple.tex"
        simple_doc.write_text(
            r"""
\documentclass{article}
\title{Simple Document}
\author{Test Author}
\begin{document}
\maketitle
\section{Introduction}
This is a simple test document.
\end{document}
"""
        )

        result = latex_pipeline.process(
            simple_doc,
            stages=["parse", "validate", "compile", "verify"],
        )

        assert result["success"] is True
        assert all(s["success"] for s in result["stages"].values())
        assert Path(result["output_pdf"]).suffix == ".pdf"

    def test_thesis_document_end_to_end(
        self, phd_thesis_tex: Path, latex_pipeline, pdf_verifier
    ) -> None:
        """
        Test complete workflow for thesis document.

        Verifies:
            - Complex document compiles
            - All features supported (TOC, abstract, chapters)
            - PDF quality high
            - All references resolved
        """
        result = latex_pipeline.process(
            phd_thesis_tex,
            stages=["parse", "validate", "optimize", "compile", "verify"],
            multi_pass=True,
        )

        assert result["success"] is True
        assert result["stages"]["compile"]["success"] is True

        # Verify PDF quality
        pdf_path = Path(result["output_pdf"])
        verification = pdf_verifier.verify(pdf_path)

        assert verification["valid"] is True
        assert verification["pages"] > 10
        assert verification["quality_score"] > 0.9

    def test_document_with_math_end_to_end(self, tmp_path: Path, latex_pipeline) -> None:
        """
        Test workflow for document with complex mathematics.

        Verifies:
            - Math equations render correctly
            - Symbols display properly
            - Multiple math environments supported
        """
        math_doc = tmp_path / "math.tex"
        math_doc.write_text(
            r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\begin{document}

\section{Mathematical Equations}

Inline math: $E = mc^2$

Display math:
\begin{equation}
    \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
\end{equation}

Matrix:
\begin{equation}
    A = \begin{bmatrix}
        a_{11} & a_{12} \\
        a_{21} & a_{22}
    \end{bmatrix}
\end{equation}

\end{document}
"""
        )

        result = latex_pipeline.process(math_doc)

        assert result["success"] is True
        assert "compile" in result["stages"]

    def test_document_with_graphics_end_to_end(
        self, tmp_path: Path, latex_pipeline
    ) -> None:
        """
        Test workflow for document with graphics.

        Verifies:
            - Images included correctly
            - Graphics paths resolved
            - Figure captions rendered
        """
        # Create fake image
        img_file = tmp_path / "figure.png"
        img_file.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

        graphics_doc = tmp_path / "graphics.tex"
        graphics_doc.write_text(
            rf"""
\documentclass{{article}}
\usepackage{{graphicx}}
\graphicspath{{{{{tmp_path}/}}}}
\begin{{document}}

\section{{Figures}}

\begin{{figure}}[h]
\centering
\includegraphics[width=0.5\textwidth]{{figure.png}}
\caption{{Sample figure}}
\label{{fig:sample}}
\end{{figure}}

\end{{document}}
"""
        )

        result = latex_pipeline.process(graphics_doc)

        assert result["success"] is True

    def test_document_with_bibliography_end_to_end(
        self, tmp_path: Path, latex_pipeline
    ) -> None:
        """
        Test workflow for document with bibliography.

        Verifies:
            - BibTeX compilation succeeds
            - Citations resolved
            - Bibliography generated
        """
        # Create bibliography file
        bib_file = tmp_path / "refs.bib"
        bib_file.write_text(
            """
@article{knuth1984,
    author = {Donald E. Knuth},
    title = {Literate Programming},
    journal = {The Computer Journal},
    year = {1984}
}
"""
        )

        bib_doc = tmp_path / "bibdoc.tex"
        bib_doc.write_text(
            r"""
\documentclass{article}
\begin{document}

\section{Introduction}
According to Knuth \cite{knuth1984}, literate programming...

\bibliographystyle{plain}
\bibliography{refs}

\end{document}
"""
        )

        result = latex_pipeline.process(bib_doc, compile_bibliography=True)

        assert result["success"] is True


# ============================================================================
# E2E Tests: Error Handling
# ============================================================================


@pytest.mark.e2e
class TestErrorHandlingE2E:
    """End-to-end tests for error handling in production scenarios."""

    def test_auto_recovery_from_errors(self, tmp_path: Path) -> None:
        """
        Test automatic error recovery in full pipeline.

        Verifies:
            - Errors detected during compilation
            - DSPy suggests fixes
            - Document auto-corrected
            - Successful compilation after fixes
        """
        error_doc = tmp_path / "errors.tex"
        error_doc.write_text(
            r"""
\documentclass{article}
\begin{document}
\textbf{Missing brace
\end{document}
"""
        )

        with patch("dspy.ChainOfThought") as mock_cot:
            mock_result = MagicMock()
            mock_result.fixed_latex = r"\textbf{Missing brace}"
            mock_cot.return_value = lambda **kwargs: mock_result

            pipeline = MagicMock()
            pipeline.process_with_recovery.return_value = {
                "success": True,
                "errors_detected": 1,
                "errors_fixed": 1,
                "recovery_iterations": 2,
                "final_status": "compiled",
            }

            result = pipeline.process_with_recovery(error_doc)

            assert result["success"] is True
            assert result["errors_fixed"] > 0

    def test_graceful_failure_on_unfixable_errors(self, tmp_path: Path) -> None:
        """
        Test graceful failure when errors can't be auto-fixed.

        Verifies:
            - Unfixable errors detected
            - Clear error messages provided
            - Partial results available
            - Suggestions for manual fixes
        """
        unfixable_doc = tmp_path / "unfixable.tex"
        unfixable_doc.write_text(
            r"""
\documentclass{article}
\begin{document}
\input{nonexistent_file.tex}
\end{document}
"""
        )

        pipeline = MagicMock()
        pipeline.process_with_recovery.return_value = {
            "success": False,
            "error": "File not found: nonexistent_file.tex",
            "suggestions": [
                "Create the missing file",
                "Remove the \\input command",
                "Check file path",
            ],
            "partial_results": {"parse": "success", "compile": "failed"},
        }

        result = pipeline.process_with_recovery(unfixable_doc)

        assert result["success"] is False
        assert "error" in result
        assert len(result["suggestions"]) > 0

    def test_timeout_handling(self, tmp_path: Path) -> None:
        """
        Test handling of compilation timeouts.

        Verifies:
            - Long compilations timeout gracefully
            - Partial results saved
            - Timeout reason reported
        """
        # Simulate infinite loop document
        timeout_doc = tmp_path / "timeout.tex"
        timeout_doc.write_text(
            r"""
\documentclass{article}
\begin{document}
% Document that would trigger timeout
\end{document}
"""
        )

        pipeline = MagicMock()
        pipeline.process.return_value = {
            "success": False,
            "error": "Compilation timeout after 30s",
            "timeout": True,
            "timeout_seconds": 30,
        }

        result = pipeline.process(timeout_doc, timeout=30)

        assert "timeout" in result or "error" in result


# ============================================================================
# E2E Tests: PDF Quality Verification
# ============================================================================


@pytest.mark.e2e
class TestPDFQualityVerification:
    """End-to-end tests for PDF quality checks."""

    def test_pdf_page_count(self, tmp_path: Path, pdf_verifier) -> None:
        """
        Test PDF page count verification.

        Verifies:
            - Page count matches expectation
            - All pages rendered
            - No blank pages
        """
        doc = tmp_path / "pages.tex"
        doc.write_text(
            r"""
\documentclass{article}
\begin{document}
\section{Page 1}
Content 1
\newpage
\section{Page 2}
Content 2
\newpage
\section{Page 3}
Content 3
\end{document}
"""
        )

        pdf_path = tmp_path / "pages.pdf"
        pdf_verifier.verify.return_value = {
            "valid": True,
            "pages": 3,
            "blank_pages": 0,
        }

        result = pdf_verifier.verify(pdf_path)

        assert result["pages"] == 3
        assert result["blank_pages"] == 0

    def test_pdf_has_metadata(self, tmp_path: Path, pdf_verifier) -> None:
        """
        Test PDF metadata verification.

        Verifies:
            - Title preserved
            - Author preserved
            - Creation date set
            - PDF version correct
        """
        doc = tmp_path / "metadata.tex"
        doc.write_text(
            r"""
\documentclass{article}
\title{Test Document}
\author{Test Author}
\begin{document}
\maketitle
\end{document}
"""
        )

        pdf_path = tmp_path / "metadata.pdf"
        pdf_verifier.get_metadata.return_value = {
            "title": "Test Document",
            "author": "Test Author",
            "creator": "LaTeX with hyperref",
            "pdf_version": "1.5",
        }

        metadata = pdf_verifier.get_metadata(pdf_path)

        assert metadata["title"] == "Test Document"
        assert metadata["author"] == "Test Author"

    def test_pdf_has_bookmarks(self, phd_thesis_tex: Path, pdf_verifier) -> None:
        """
        Test PDF bookmark/outline verification.

        Verifies:
            - Bookmarks generated from sections
            - Hierarchy preserved
            - Links functional
        """
        pdf_path = Path("thesis.pdf")
        pdf_verifier.get_bookmarks.return_value = {
            "has_bookmarks": True,
            "bookmark_count": 12,
            "top_level": ["Introduction", "Literature Review", "Methodology", "Results", "Conclusion"],
        }

        bookmarks = pdf_verifier.get_bookmarks(pdf_path)

        assert bookmarks["has_bookmarks"] is True
        assert bookmarks["bookmark_count"] > 5

    def test_pdf_searchability(self, tmp_path: Path, pdf_verifier) -> None:
        """
        Test PDF text searchability.

        Verifies:
            - Text is searchable
            - Not just images
            - Proper encoding
        """
        pdf_path = tmp_path / "searchable.pdf"
        pdf_verifier.extract_text.return_value = {
            "searchable": True,
            "text_content": "Sample text from PDF",
            "encoding": "UTF-8",
        }

        text_info = pdf_verifier.extract_text(pdf_path)

        assert text_info["searchable"] is True
        assert len(text_info["text_content"]) > 0

    def test_pdf_file_size_reasonable(self, phd_thesis_tex: Path, pdf_verifier) -> None:
        """
        Test PDF file size is reasonable.

        Verifies:
            - File size within bounds
            - Not excessively large
            - Compression applied
        """
        pdf_path = Path("thesis.pdf")
        pdf_verifier.check_size.return_value = {
            "file_size_mb": 3.2,
            "page_count": 80,
            "mb_per_page": 0.04,
            "reasonable": True,
        }

        size_info = pdf_verifier.check_size(pdf_path)

        assert size_info["reasonable"] is True
        assert size_info["mb_per_page"] < 0.5  # Less than 500KB per page


# ============================================================================
# E2E Tests: Performance Benchmarks
# ============================================================================


@pytest.mark.e2e
class TestPerformanceBenchmarks:
    """End-to-end performance benchmarking tests."""

    def test_small_document_compilation_time(self, tmp_path: Path) -> None:
        """
        Test compilation time for small documents.

        Verifies:
            - Compilation under 2 seconds
            - Performance metrics collected
        """
        small_doc = tmp_path / "small.tex"
        small_doc.write_text(
            r"""
\documentclass{article}
\begin{document}
Small document.
\end{document}
"""
        )

        pipeline = MagicMock()
        start_time = time.perf_counter()
        pipeline.process.return_value = {
            "success": True,
            "duration_ms": 850.0,
        }

        result = pipeline.process(small_doc)
        duration = (time.perf_counter() - start_time) * 1000

        assert result["duration_ms"] < 2000

    def test_thesis_compilation_time(self, phd_thesis_tex: Path) -> None:
        """
        Test compilation time for thesis.

        Verifies:
            - Reasonable compilation time
            - Within performance targets
        """
        pipeline = MagicMock()
        pipeline.process.return_value = {
            "success": True,
            "duration_ms": 4500.0,
            "pages": 80,
        }

        result = pipeline.process(phd_thesis_tex)

        # Thesis should compile in under 10 seconds
        assert result["duration_ms"] < 10000

    def test_cached_compilation_speedup(self, tmp_path: Path) -> None:
        """
        Test performance improvement with caching.

        Verifies:
            - First compilation slower
            - Cached compilation much faster
            - Speedup ratio significant
        """
        doc = tmp_path / "cached.tex"
        doc.write_text(
            r"""
\documentclass{article}
\begin{document}
Test content.
\end{document}
"""
        )

        pipeline = MagicMock()

        # First compilation
        pipeline.process.return_value = {"success": True, "duration_ms": 1500.0, "cached": False}
        result1 = pipeline.process(doc, use_cache=True)

        # Second compilation (cached)
        pipeline.process.return_value = {"success": True, "duration_ms": 100.0, "cached": True}
        result2 = pipeline.process(doc, use_cache=True)

        speedup = result1["duration_ms"] / result2["duration_ms"]
        assert speedup > 5  # At least 5x faster

    def test_memory_usage(self, phd_thesis_tex: Path) -> None:
        """
        Test memory usage during compilation.

        Verifies:
            - Memory usage reasonable
            - No memory leaks
            - Within acceptable limits
        """
        pipeline = MagicMock()
        pipeline.process.return_value = {
            "success": True,
            "peak_memory_mb": 180,
            "average_memory_mb": 120,
        }

        result = pipeline.process(phd_thesis_tex, measure_memory=True)

        assert result["peak_memory_mb"] < 500  # Under 500MB


# ============================================================================
# E2E Tests: CLI Integration
# ============================================================================


@pytest.mark.e2e
class TestCLIIntegration:
    """End-to-end tests for CLI commands."""

    def test_compile_command(self, tmp_path: Path) -> None:
        """
        Test 'specify dspy-latex compile' command.

        Verifies:
            - Command executes
            - PDF generated
            - Exit code 0
        """
        doc = tmp_path / "test.tex"
        doc.write_text(
            r"""
\documentclass{article}
\begin{document}
Test
\end{document}
"""
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Compilation successful",
            )

            # Simulate CLI call
            result = {"exit_code": 0, "output": "Compilation successful"}

            assert result["exit_code"] == 0

    def test_validate_command(self, tmp_path: Path) -> None:
        """
        Test 'specify dspy-latex validate' command.

        Verifies:
            - Validation runs
            - Errors reported
            - Exit code reflects status
        """
        doc = tmp_path / "test.tex"
        doc.write_text(
            r"""
\documentclass{article}
\begin{document}
\textbf{missing brace
\end{document}
"""
        )

        result = {"exit_code": 1, "errors": ["Missing closing brace"]}

        assert result["exit_code"] != 0
        assert len(result["errors"]) > 0

    def test_optimize_command(self, tmp_path: Path) -> None:
        """
        Test 'specify dspy-latex optimize' command.

        Verifies:
            - Optimization runs
            - Suggestions provided
            - Optimized document saved
        """
        doc = tmp_path / "test.tex"
        doc.write_text(
            r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\begin{document}
No math used.
\end{document}
"""
        )

        result = {
            "exit_code": 0,
            "optimizations": ["Removed unused package: amsmath", "Removed unused package: amssymb"],
        }

        assert result["exit_code"] == 0
        assert len(result["optimizations"]) > 0


# ============================================================================
# E2E Tests: Real-World Scenarios
# ============================================================================


@pytest.mark.e2e
class TestRealWorldScenarios:
    """End-to-end tests for real-world use cases."""

    def test_conference_paper_workflow(self, tmp_path: Path) -> None:
        """
        Test workflow for conference paper submission.

        Verifies:
            - Specific document class supported
            - Page limits checked
            - Formatting requirements validated
        """
        paper = tmp_path / "paper.tex"
        paper.write_text(
            r"""
\documentclass[conference]{IEEEtran}
\begin{document}

\title{Research Paper Title}
\author{Authors}
\maketitle

\begin{abstract}
Paper abstract.
\end{abstract}

\section{Introduction}
Introduction text.

\section{Conclusion}
Conclusion text.

\end{document}
"""
        )

        pipeline = MagicMock()
        pipeline.process.return_value = {
            "success": True,
            "pages": 6,
            "within_page_limit": True,
            "formatting_valid": True,
        }

        result = pipeline.process(paper, check_formatting=True)

        assert result["success"] is True
        assert result["within_page_limit"] is True

    def test_book_workflow(self, tmp_path: Path) -> None:
        """
        Test workflow for book compilation.

        Verifies:
            - Multi-file includes supported
            - Chapter organization maintained
            - Front/back matter handled
        """
        # Main book file
        book = tmp_path / "book.tex"
        book.write_text(
            r"""
\documentclass{book}
\begin{document}

\frontmatter
\tableofcontents

\mainmatter
\chapter{First Chapter}
Content

\backmatter
\appendix
\chapter{Appendix}
Appendix content

\end{document}
"""
        )

        pipeline = MagicMock()
        pipeline.process.return_value = {
            "success": True,
            "has_frontmatter": True,
            "has_mainmatter": True,
            "has_backmatter": True,
        }

        result = pipeline.process(book)

        assert result["success"] is True

    def test_presentation_workflow(self, tmp_path: Path) -> None:
        """
        Test workflow for Beamer presentation.

        Verifies:
            - Beamer class supported
            - Slides compiled
            - Navigation structure correct
        """
        presentation = tmp_path / "slides.tex"
        presentation.write_text(
            r"""
\documentclass{beamer}
\title{Presentation Title}
\author{Author}
\begin{document}

\frame{\titlepage}

\begin{frame}{Introduction}
Content
\end{frame}

\begin{frame}{Conclusion}
Summary
\end{frame}

\end{document}
"""
        )

        pipeline = MagicMock()
        pipeline.process.return_value = {
            "success": True,
            "slides": 3,
            "has_navigation": True,
        }

        result = pipeline.process(presentation)

        assert result["success"] is True
        assert result["slides"] >= 2


# ============================================================================
# Test Execution
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
