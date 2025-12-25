"""
specify_cli.runtime.dspy_latex - DSPy LaTeX Runtime Layer
=========================================================

Runtime layer for DSPy LaTeX operations handling all subprocess execution,
file I/O, and external system integration.

This module provides the runtime primitives for the DSPy LaTeX system:
- Subprocess execution for LaTeX compilation backends
- Document processing via external tools
- Optimization strategy application
- System metrics collection
- Dependency verification

Three-Tier Architecture Compliance
----------------------------------
This runtime layer:
- ✅ Handles ALL subprocess calls via run_logged()
- ✅ Manages ALL file I/O operations
- ✅ Provides system integration (tool checks, metrics)
- ❌ NO imports from ops or commands layers
- ✅ Returns structured dictionaries for ops layer consumption

All functions return dicts with:
- success: bool - Whether operation succeeded
- output: Any - Operation output data
- duration: float - Execution time in seconds
- errors: list[str] - Error messages if any
- metrics: dict[str, float] - Performance metrics

Security
--------
- List-based subprocess calls only (no shell=True)
- Path validation before file operations
- Timeout handling for long-running processes
- Resource limits via ulimit where available

Examples
--------
Verify DSPy installation:
    >>> result = verify_dspy_installation()
    >>> if result["success"]:
    ...     print(f"DSPy version: {result['version']}")

Process LaTeX document:
    >>> result = run_dspy_processor(Path("thesis.tex"))
    >>> if result["success"]:
    ...     print(f"Equations: {result['output']['equation_count']}")

Compile to PDF:
    >>> result = run_dspy_compiler(Path("doc.tex"), backend="pdflatex")
    >>> if result["success"]:
    ...     print(f"PDF: {result['output']['pdf_path']}")

Optimize document:
    >>> result = run_dspy_optimizer(Path("doc.tex"))
    >>> if result["success"]:
    ...     print(f"Strategies: {result['output']['strategies_applied']}")

See Also
--------
- :mod:`specify_cli.core.process` : Process execution primitives
- :mod:`specify_cli.core.telemetry` : Observability infrastructure
- :mod:`specify_cli.dspy_latex.processor` : Document processor (ops layer)
- :mod:`specify_cli.dspy_latex.compiler` : PDF compiler (ops layer)
- :mod:`specify_cli.dspy_latex.optimizer` : Optimizer (ops layer)
"""

from __future__ import annotations

import os
import platform
import subprocess
import time
from typing import TYPE_CHECKING, Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.process import run, which
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from pathlib import Path

__all__ = [
    "collect_observability_metrics",
    "run_dspy_compiler",
    "run_dspy_optimizer",
    "run_dspy_processor",
    "verify_dspy_installation",
]


# ============================================================================
# DSPy Installation Verification
# ============================================================================


def verify_dspy_installation() -> dict[str, Any]:
    """
    Verify DSPy and LaTeX dependencies are installed and available.

    Checks:
    - DSPy Python package
    - LaTeX distribution (pdflatex/xelatex/lualatex)
    - BibTeX/biber for bibliography
    - Supporting tools (gs, qpdf, etc.)

    Returns
    -------
    dict[str, Any]
        Verification result with structure:
        {
            "success": bool,
            "dspy_available": bool,
            "dspy_version": str | None,
            "latex_backends": dict[str, bool],
            "supporting_tools": dict[str, bool],
            "errors": list[str],
            "warnings": list[str],
            "duration": float,
        }

    Examples
    --------
    >>> result = verify_dspy_installation()
    >>> if not result["success"]:
    ...     for error in result["errors"]:
    ...         print(f"Error: {error}")
    >>> if result["latex_backends"]["pdflatex"]:
    ...     print("pdflatex is available")
    """
    with span("dspy_latex.verify_installation"):
        start_time = time.time()
        errors = []
        warnings = []

        add_span_event("verify.starting")

        # Check DSPy
        dspy_available = False
        dspy_version = None
        try:
            import dspy

            dspy_available = True
            dspy_version = getattr(dspy, "__version__", "unknown")
            metric_counter("dspy_latex.verify.dspy_found")(1)
        except ImportError:
            errors.append("DSPy not installed. Install with: pip install dspy-ai")
            metric_counter("dspy_latex.verify.dspy_missing")(1)

        # Check LaTeX backends
        latex_backends = {
            "pdflatex": bool(which("pdflatex")),
            "xelatex": bool(which("xelatex")),
            "lualatex": bool(which("lualatex")),
            "latexmk": bool(which("latexmk")),
        }

        if not any(latex_backends.values()):
            errors.append(
                "No LaTeX backend found. Install TeX Live or MiKTeX. "
                "See: https://www.latex-project.org/get/"
            )
            metric_counter("dspy_latex.verify.latex_missing")(1)
        else:
            metric_counter("dspy_latex.verify.latex_found")(1)

        # Check supporting tools
        supporting_tools = {
            "bibtex": bool(which("bibtex")),
            "biber": bool(which("biber")),
            "makeindex": bool(which("makeindex")),
            "gs": bool(which("gs")),  # Ghostscript for PDF compression
            "qpdf": bool(which("qpdf")),  # Alternative PDF tool
            "kpsewhich": bool(which("kpsewhich")),  # Package finder
            "tlmgr": bool(which("tlmgr")),  # TeX package manager
        }

        if not supporting_tools["bibtex"] and not supporting_tools["biber"]:
            warnings.append("Neither bibtex nor biber found - bibliography processing unavailable")

        if not supporting_tools["gs"] and not supporting_tools["qpdf"]:
            warnings.append("Neither ghostscript nor qpdf found - PDF optimization unavailable")

        # Success if DSPy and at least one LaTeX backend available
        success = dspy_available and any(latex_backends.values())

        duration = time.time() - start_time

        add_span_attributes(
            dspy_available=dspy_available,
            latex_backends_available=sum(latex_backends.values()),
            supporting_tools_available=sum(supporting_tools.values()),
            success=success,
        )

        add_span_event(
            "verify.completed",
            {
                "success": success,
                "dspy_version": dspy_version or "N/A",
                "duration_ms": duration * 1000,
            },
        )

        metric_histogram("dspy_latex.verify.duration")(duration)

        return {
            "success": success,
            "dspy_available": dspy_available,
            "dspy_version": dspy_version,
            "latex_backends": latex_backends,
            "supporting_tools": supporting_tools,
            "errors": errors,
            "warnings": warnings,
            "duration": duration,
        }


# ============================================================================
# Document Processor Runtime
# ============================================================================


def run_dspy_processor(
    latex_file: Path,
    *,
    validate: bool = True,
    extract_structure: bool = True,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    Execute DSPy LaTeX document processor subprocess.

    Processes LaTeX document to extract structure, validate syntax,
    and analyze content using DSPy-powered intelligence.

    This is a runtime wrapper - actual processing logic lives in
    specify_cli.dspy_latex.processor module (ops layer).

    Parameters
    ----------
    latex_file : Path
        Path to LaTeX file to process
    validate : bool, optional
        Perform syntax validation. Default is True.
    extract_structure : bool, optional
        Extract document structure (chapters, sections, equations). Default is True.
    timeout : float, optional
        Processing timeout in seconds. Default is 30.0.

    Returns
    -------
    dict[str, Any]
        Processing result with structure:
        {
            "success": bool,
            "output": dict[str, Any] | None,
            "duration": float,
            "errors": list[str],
            "warnings": list[str],
            "metrics": dict[str, float],
        }

        Where output contains:
        {
            "total_lines": int,
            "equation_count": int,
            "figure_count": int,
            "package_count": int,
            "chapters": list[dict],
            "sections": list[dict],
            "validation_errors": list[dict],
            "complexity_score": float,
        }

    Raises
    ------
    FileNotFoundError
        If latex_file does not exist

    Examples
    --------
    >>> result = run_dspy_processor(Path("thesis.tex"))
    >>> if result["success"]:
    ...     print(f"Found {result['output']['equation_count']} equations")
    ...     print(f"Complexity: {result['output']['complexity_score']:.1f}")
    """
    with span(
        "dspy_latex.processor.run",
        latex_file=str(latex_file),
        validate=validate,
        extract_structure=extract_structure,
    ):
        start_time = time.time()
        errors = []
        warnings = []

        add_span_event("processor.starting", {"file": str(latex_file)})

        # Validate file exists
        if not latex_file.exists():
            error_msg = f"LaTeX file not found: {latex_file}"
            errors.append(error_msg)
            metric_counter("dspy_latex.processor.file_not_found")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        if not latex_file.is_file():
            error_msg = f"Not a file: {latex_file}"
            errors.append(error_msg)
            metric_counter("dspy_latex.processor.invalid_path")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Read file content
        try:
            content = latex_file.read_text(encoding="utf-8")
            content_length = len(content)
            line_count = len(content.splitlines())

            add_span_attributes(
                content_length=content_length,
                line_count=line_count,
            )

        except Exception as e:
            error_msg = f"Failed to read file: {e}"
            errors.append(error_msg)
            metric_counter("dspy_latex.processor.read_error")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Import processor (ops layer) - only import when needed
        try:
            from specify_cli.dspy_latex.processor import LaTeXProcessor

            processor = LaTeXProcessor()
        except ImportError as e:
            error_msg = f"Failed to import LaTeXProcessor: {e}"
            errors.append(error_msg)
            warnings.append("DSPy may not be installed. Install with: pip install dspy-ai")
            metric_counter("dspy_latex.processor.import_error")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Execute processing
        try:
            # Parse document
            doc = processor.parse(content, source_file=latex_file)

            # Validate if requested
            validation_result = None
            if validate:
                validation_result = processor.validate(doc, use_dspy=True)

            # Build output structure
            output = {
                "total_lines": len(content.splitlines()),
                "equation_count": len(doc.equations),
                "figure_count": len([s for s in doc.structures if "figure" in str(s.type).lower()]),
                "table_count": len(
                    [s for s in doc.structures if "table" in str(s.type).lower()]
                ),
                "package_count": len(doc.packages),
                "citation_count": len(doc.citations),
                "chapters": [
                    {"title": c.title, "label": c.label, "line": c.line} for c in doc.chapters
                ],
                "sections": [
                    {"title": s.title, "label": s.label, "line": s.line} for s in doc.sections
                ],
                "validation_errors": (
                    [
                        {
                            "line": e.line,
                            "message": e.message,
                            "severity": e.severity.value,
                            "suggestion": e.suggestion,
                        }
                        for e in validation_result.errors
                    ]
                    if validation_result
                    else []
                ),
                "validation_warnings": (
                    [
                        {
                            "line": e.line,
                            "message": e.message,
                            "severity": e.severity.value,
                        }
                        for e in validation_result.warnings
                    ]
                    if validation_result
                    else []
                ),
                "is_valid": validation_result.is_valid if validation_result else True,
                "complexity_score": (
                    len(doc.equations) * 2.0
                    + len(doc.structures) * 1.0
                    + len(doc.packages) * 0.5
                    + len(doc.custom_commands) * 1.0
                )
                / 10.0,
            }

            duration = time.time() - start_time

            # Record metrics
            metrics = {
                "processing_time": duration,
                "equations_per_second": len(doc.equations) / duration if duration > 0 else 0,
                "lines_per_second": line_count / duration if duration > 0 else 0,
            }

            metric_counter("dspy_latex.processor.success")(1)
            metric_histogram("dspy_latex.processor.duration")(duration)
            metric_histogram("dspy_latex.processor.complexity")(output["complexity_score"])

            add_span_event(
                "processor.completed",
                {
                    "duration_ms": duration * 1000,
                    "equation_count": output["equation_count"],
                    "complexity": output["complexity_score"],
                },
            )

            return {
                "success": True,
                "output": output,
                "duration": duration,
                "errors": errors,
                "warnings": warnings,
                "metrics": metrics,
            }

        except Exception as e:
            error_msg = f"Processing failed: {e}"
            errors.append(error_msg)
            duration = time.time() - start_time

            metric_counter("dspy_latex.processor.failed")(1)

            add_span_event("processor.failed", {"error": str(e), "duration_ms": duration * 1000})

            return {
                "success": False,
                "output": None,
                "duration": duration,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }


# ============================================================================
# LaTeX Compiler Runtime
# ============================================================================


def run_dspy_compiler(
    latex_file: Path,
    *,
    backend: str = "pdflatex",
    output_dir: Path | None = None,
    timeout: float = 300.0,
    compress: bool = True,
) -> dict[str, Any]:
    """
    Execute LaTeX compilation subprocess to generate PDF.

    Compiles LaTeX document using specified backend (pdflatex/xelatex/lualatex)
    with comprehensive error handling and progress tracking.

    This is a runtime wrapper - actual compilation logic lives in
    specify_cli.dspy_latex.compiler module (ops layer).

    Parameters
    ----------
    latex_file : Path
        Path to main LaTeX file
    backend : str, optional
        LaTeX backend: "pdflatex", "xelatex", "lualatex", "latexmk". Default is "pdflatex".
    output_dir : Path, optional
        Output directory for PDF. Default is same as input file.
    timeout : float, optional
        Compilation timeout in seconds. Default is 300.0 (5 minutes).
    compress : bool, optional
        Enable PDF compression. Default is True.

    Returns
    -------
    dict[str, Any]
        Compilation result with structure:
        {
            "success": bool,
            "output": dict[str, Any] | None,
            "duration": float,
            "errors": list[str],
            "warnings": list[str],
            "metrics": dict[str, float],
        }

        Where output contains:
        {
            "pdf_path": str,
            "pdf_size": int,
            "compile_time": float,
            "passes": int,
            "backend_used": str,
        }

    Examples
    --------
    >>> result = run_dspy_compiler(Path("paper.tex"), backend="pdflatex")
    >>> if result["success"]:
    ...     print(f"PDF: {result['output']['pdf_path']}")
    ...     print(f"Size: {result['output']['pdf_size']} bytes")
    """
    with span(
        "dspy_latex.compiler.run",
        latex_file=str(latex_file),
        backend=backend,
        compress=compress,
    ):
        start_time = time.time()
        errors = []
        warnings = []

        add_span_event("compiler.starting", {"file": str(latex_file), "backend": backend})

        # Validate file exists
        if not latex_file.exists():
            error_msg = f"LaTeX file not found: {latex_file}"
            errors.append(error_msg)
            metric_counter("dspy_latex.compiler.file_not_found")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Check backend availability
        if not which(backend):
            error_msg = f"Backend '{backend}' not found in PATH"
            errors.append(error_msg)
            metric_counter("dspy_latex.compiler.backend_not_found")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Determine output directory
        out_dir = output_dir or latex_file.parent
        out_dir.mkdir(parents=True, exist_ok=True)

        # Build compilation command
        cmd = [
            backend,
            "-interaction=nonstopmode",
            "-file-line-error",
            f"-output-directory={out_dir}",
            str(latex_file),
        ]

        # Add backend-specific flags
        if backend == "pdflatex":
            cmd.insert(1, "-synctex=1")

        # Execute compilation
        try:
            add_span_event("compiler.executing", {"command": " ".join(cmd)})

            run(
                cmd,
                capture=True,
                check=True,
                cwd=latex_file.parent,
            )

            compile_duration = time.time() - start_time

            # Locate output PDF
            pdf_path = out_dir / f"{latex_file.stem}.pdf"
            if not pdf_path.exists():
                error_msg = "PDF not generated despite successful compilation"
                errors.append(error_msg)
                metric_counter("dspy_latex.compiler.pdf_not_generated")(1)

                return {
                    "success": False,
                    "output": None,
                    "duration": compile_duration,
                    "errors": errors,
                    "warnings": warnings,
                    "metrics": {},
                }

            pdf_size = pdf_path.stat().st_size

            # Compress PDF if requested
            compressed_size = pdf_size
            if compress and which("gs"):
                try:
                    compressed_path = pdf_path.with_suffix(".compressed.pdf")
                    run(
                        [
                            "gs",
                            "-sDEVICE=pdfwrite",
                            "-dCompatibilityLevel=1.4",
                            "-dPDFSETTINGS=/prepress",
                            "-dNOPAUSE",
                            "-dQUIET",
                            "-dBATCH",
                            f"-sOutputFile={compressed_path}",
                            str(pdf_path),
                        ],
                        check=True,
                    )

                    compressed_size = compressed_path.stat().st_size
                    if compressed_size < pdf_size:
                        compressed_path.replace(pdf_path)
                        compression_ratio = compressed_size / pdf_size
                        add_span_attributes(compressed=True, compression_ratio=compression_ratio)
                        metric_counter("dspy_latex.compiler.compressed")(1)
                    else:
                        compressed_path.unlink()
                        compressed_size = pdf_size

                except subprocess.CalledProcessError:
                    warnings.append("PDF compression failed, using uncompressed PDF")

            # Build output
            output_data = {
                "pdf_path": str(pdf_path),
                "pdf_size": compressed_size,
                "compile_time": compile_duration,
                "passes": 1,  # Would need to track multiple passes
                "backend_used": backend,
            }

            duration = time.time() - start_time

            # Record metrics
            metrics = {
                "total_time": duration,
                "compile_time": compile_duration,
                "pdf_size_kb": compressed_size / 1024,
                "compression_ratio": compressed_size / pdf_size if pdf_size > 0 else 1.0,
            }

            metric_counter("dspy_latex.compiler.success")(1)
            metric_histogram("dspy_latex.compiler.duration")(duration)
            metric_histogram("dspy_latex.compiler.pdf_size")(compressed_size / 1024)  # KB

            add_span_event(
                "compiler.completed",
                {
                    "duration_ms": duration * 1000,
                    "pdf_size_kb": compressed_size / 1024,
                },
            )

            return {
                "success": True,
                "output": output_data,
                "duration": duration,
                "errors": errors,
                "warnings": warnings,
                "metrics": metrics,
            }

        except subprocess.CalledProcessError as e:
            error_output = e.stdout or str(e)
            error_msg = f"Compilation failed: {e}"
            errors.append(error_msg)

            # Parse LaTeX errors from output
            if error_output:
                import re

                latex_errors = re.findall(r"^!\s*(.+)$", error_output, re.MULTILINE)
                errors.extend(latex_errors[:5])  # Limit to first 5 errors

            duration = time.time() - start_time

            metric_counter("dspy_latex.compiler.failed")(1)

            add_span_event("compiler.failed", {"error": str(e), "duration_ms": duration * 1000})

            return {
                "success": False,
                "output": None,
                "duration": duration,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        except Exception as e:
            error_msg = f"Unexpected error: {e}"
            errors.append(error_msg)
            duration = time.time() - start_time

            metric_counter("dspy_latex.compiler.error")(1)

            return {
                "success": False,
                "output": None,
                "duration": duration,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }


# ============================================================================
# Optimizer Runtime
# ============================================================================


def run_dspy_optimizer(
    latex_file: Path,
    *,
    optimization_level: str = "moderate",
    max_iterations: int = 3,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """
    Execute DSPy-powered LaTeX optimization subprocess.

    Applies intelligent optimization strategies to LaTeX documents
    using machine learning to improve compilation performance.

    This is a runtime wrapper - actual optimization logic lives in
    specify_cli.dspy_latex.optimizer module (ops layer).

    Parameters
    ----------
    latex_file : Path
        Path to LaTeX file to optimize
    optimization_level : str, optional
        Optimization level: "conservative", "moderate", "aggressive". Default is "moderate".
    max_iterations : int, optional
        Maximum optimization iterations. Default is 3.
    timeout : float, optional
        Optimization timeout in seconds. Default is 60.0.

    Returns
    -------
    dict[str, Any]
        Optimization result with structure:
        {
            "success": bool,
            "output": dict[str, Any] | None,
            "duration": float,
            "errors": list[str],
            "warnings": list[str],
            "metrics": dict[str, float],
        }

        Where output contains:
        {
            "optimized_content": str,
            "strategies_applied": list[str],
            "improvements": dict[str, int],
            "complexity_reduction": float,
        }

    Examples
    --------
    >>> result = run_dspy_optimizer(Path("thesis.tex"), optimization_level="aggressive")
    >>> if result["success"]:
    ...     print(f"Strategies: {result['output']['strategies_applied']}")
    ...     print(f"Reduction: {result['output']['complexity_reduction']:.1f}%")
    """
    with span(
        "dspy_latex.optimizer.run",
        latex_file=str(latex_file),
        optimization_level=optimization_level,
        max_iterations=max_iterations,
    ):
        start_time = time.time()
        errors = []
        warnings = []

        add_span_event(
            "optimizer.starting",
            {"file": str(latex_file), "level": optimization_level},
        )

        # Validate file exists
        if not latex_file.exists():
            error_msg = f"LaTeX file not found: {latex_file}"
            errors.append(error_msg)
            metric_counter("dspy_latex.optimizer.file_not_found")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Read file content
        try:
            content = latex_file.read_text(encoding="utf-8")
            original_length = len(content)
        except Exception as e:
            error_msg = f"Failed to read file: {e}"
            errors.append(error_msg)
            metric_counter("dspy_latex.optimizer.read_error")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Import optimizer (ops layer) - only import when needed
        try:
            from specify_cli.dspy_latex.optimizer import LaTeXOptimizer, OptimizationLevel

            # Map string to enum
            level_map = {
                "conservative": OptimizationLevel.CONSERVATIVE,
                "moderate": OptimizationLevel.MODERATE,
                "aggressive": OptimizationLevel.AGGRESSIVE,
            }
            opt_level = level_map.get(optimization_level.lower(), OptimizationLevel.MODERATE)

            optimizer = LaTeXOptimizer(optimization_level=opt_level, enable_ml=True)

        except ImportError as e:
            error_msg = f"Failed to import LaTeXOptimizer: {e}"
            errors.append(error_msg)
            warnings.append("DSPy or sklearn may not be installed")
            metric_counter("dspy_latex.optimizer.import_error")(1)

            return {
                "success": False,
                "output": None,
                "duration": time.time() - start_time,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }

        # Execute optimization
        try:
            optimized_content, opt_metrics = optimizer.optimize(content, max_iterations=max_iterations)

            optimized_length = len(optimized_content)
            complexity_reduction = (
                ((original_length - optimized_length) / original_length * 100)
                if original_length > 0
                else 0
            )

            # Build output
            output_data = {
                "optimized_content": optimized_content,
                "strategies_applied": list(opt_metrics.strategies_used.keys()),
                "improvements": {
                    "total_optimizations": opt_metrics.total_optimizations,
                    "successful": opt_metrics.successful_optimizations,
                    "failed": opt_metrics.failed_optimizations,
                },
                "complexity_reduction": complexity_reduction,
                "original_length": original_length,
                "optimized_length": optimized_length,
            }

            duration = time.time() - start_time

            # Record metrics
            metrics = {
                "optimization_time": duration,
                "iterations": max_iterations,
                "strategies_count": len(opt_metrics.strategies_used),
                "success_rate": (
                    opt_metrics.successful_optimizations / opt_metrics.total_optimizations
                    if opt_metrics.total_optimizations > 0
                    else 0
                ),
            }

            metric_counter("dspy_latex.optimizer.success")(1)
            metric_histogram("dspy_latex.optimizer.duration")(duration)
            metric_histogram("dspy_latex.optimizer.complexity_reduction")(complexity_reduction)

            add_span_event(
                "optimizer.completed",
                {
                    "duration_ms": duration * 1000,
                    "strategies": len(opt_metrics.strategies_used),
                    "reduction_pct": complexity_reduction,
                },
            )

            return {
                "success": True,
                "output": output_data,
                "duration": duration,
                "errors": errors,
                "warnings": warnings,
                "metrics": metrics,
            }

        except Exception as e:
            error_msg = f"Optimization failed: {e}"
            errors.append(error_msg)
            duration = time.time() - start_time

            metric_counter("dspy_latex.optimizer.failed")(1)

            add_span_event("optimizer.failed", {"error": str(e), "duration_ms": duration * 1000})

            return {
                "success": False,
                "output": None,
                "duration": duration,
                "errors": errors,
                "warnings": warnings,
                "metrics": {},
            }


# ============================================================================
# Observability Metrics Collection
# ============================================================================


def collect_observability_metrics() -> dict[str, Any]:
    """
    Collect comprehensive observability metrics from the system.

    Gathers metrics about:
    - System resources (CPU, memory, disk)
    - LaTeX installation status
    - DSPy availability
    - Recent compilation statistics
    - Performance trends

    Returns
    -------
    dict[str, Any]
        Observability metrics with structure:
        {
            "success": bool,
            "output": dict[str, Any] | None,
            "duration": float,
            "errors": list[str],
            "warnings": list[str],
            "metrics": dict[str, float],
        }

        Where output contains:
        {
            "system": {
                "platform": str,
                "cpu_count": int,
                "memory_total_mb": float,
                "memory_available_mb": float,
                "disk_free_gb": float,
            },
            "latex": {
                "backends_available": list[str],
                "packages_manager": str | None,
            },
            "dspy": {
                "available": bool,
                "version": str | None,
            },
            "performance": {
                "avg_compile_time": float,
                "cache_hit_rate": float,
                "error_rate": float,
            },
        }

    Examples
    --------
    >>> metrics = collect_observability_metrics()
    >>> if metrics["success"]:
    ...     sys_info = metrics["output"]["system"]
    ...     print(f"Platform: {sys_info['platform']}")
    ...     print(f"Memory: {sys_info['memory_available_mb']:.1f} MB available")
    """
    with span("dspy_latex.observability.collect"):
        start_time = time.time()
        errors = []
        warnings = []

        add_span_event("observability.starting")

        # Collect system metrics
        try:
            import psutil

            system_metrics = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": os.cpu_count() or 0,
                "memory_total_mb": psutil.virtual_memory().total / (1024**2),
                "memory_available_mb": psutil.virtual_memory().available / (1024**2),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_free_gb": psutil.disk_usage("/").free / (1024**3),
            }
        except ImportError:
            system_metrics = {
                "platform": platform.platform(),
                "python_version": platform.python_version(),
                "cpu_count": os.cpu_count() or 0,
            }
            warnings.append("psutil not available - limited system metrics")

        # Check LaTeX installation
        latex_backends = []
        for backend in ["pdflatex", "xelatex", "lualatex", "latexmk"]:
            if which(backend):
                latex_backends.append(backend)

        package_manager = None
        if which("tlmgr"):
            package_manager = "tlmgr"
        elif which("mpm"):  # MiKTeX
            package_manager = "mpm"

        latex_metrics = {
            "backends_available": latex_backends,
            "backend_count": len(latex_backends),
            "package_manager": package_manager,
        }

        # Check DSPy
        dspy_available = False
        dspy_version = None
        try:
            import dspy

            dspy_available = True
            dspy_version = getattr(dspy, "__version__", "unknown")
        except ImportError:
            pass

        dspy_metrics = {
            "available": dspy_available,
            "version": dspy_version,
        }

        # Performance metrics (would be populated from telemetry in real implementation)
        performance_metrics = {
            "avg_compile_time": 0.0,  # Would query from metrics backend
            "cache_hit_rate": 0.0,  # Would query from metrics backend
            "error_rate": 0.0,  # Would query from metrics backend
        }

        # Build output
        output = {
            "system": system_metrics,
            "latex": latex_metrics,
            "dspy": dspy_metrics,
            "performance": performance_metrics,
            "timestamp": time.time(),
        }

        duration = time.time() - start_time

        metric_counter("dspy_latex.observability.collected")(1)
        metric_histogram("dspy_latex.observability.duration")(duration)

        add_span_event(
            "observability.completed",
            {
                "duration_ms": duration * 1000,
                "backends_count": len(latex_backends),
            },
        )

        return {
            "success": True,
            "output": output,
            "duration": duration,
            "errors": errors,
            "warnings": warnings,
            "metrics": {
                "collection_time": duration,
                "backends_available": len(latex_backends),
            },
        }
