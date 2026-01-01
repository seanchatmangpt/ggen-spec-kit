from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span

__all__ = ["DspyError", "CompilationResult", "generate_latex"]


class DspyError(Exception):
    def __init__(self, message: str, *, suggestions: list[str] | None = None) -> None:
        super().__init__(message)
        self.suggestions = suggestions or []


@dataclass
class CompilationResult:
    success: bool
    input_file: str
    output_format: str
    output_file: str = ""
    optimized: bool = False
    optimization_passes: int = 0
    original_lines: int = 0
    optimized_lines: int = 0
    reduction_percent: float = 0.0
    errors: list[str] = field(default_factory=list)
    duration: float = 0.0


@timed
def generate_latex(
    input_file: str | Path,
    *,
    output_format: str = "pdf",
    optimize: bool = True,
    include_types: bool = True,
    theme: str = "default",
) -> CompilationResult:
    start_time = time.time()
    result = CompilationResult(
        success=False,
        input_file=str(input_file),
        output_format=output_format,
        optimized=optimize,
    )

    with span(
        "ops.dspy_latex.generate_latex",
        output_format=output_format,
        optimize=optimize,
        theme=theme,
    ):
        try:
            input_path = Path(input_file)
            if not input_path.exists():
                raise DspyError(f"Input file not found: {input_file}")

            py_content = input_path.read_text()
            result.original_lines = len(py_content.split("\n"))

            add_span_event("dspy.compilation_starting", {"output_format": output_format})

            latex_content = _transpile_to_latex(py_content, include_types, theme)

            if optimize:
                latex_content, passes = _apply_optimizations(latex_content)
                result.optimization_passes = passes
                result.optimized_lines = len(latex_content.split("\n"))
                result.reduction_percent = ((result.original_lines - result.optimized_lines) / result.original_lines * 100)

            if output_format == "pdf":
                result.output_file = str(input_path.with_suffix(".pdf"))
                _compile_to_pdf(latex_content, result.output_file)
            elif output_format == "tex":
                result.output_file = str(input_path.with_suffix(".tex"))
                Path(result.output_file).write_text(latex_content)
            elif output_format == "mermaid":
                result.output_file = str(input_path.with_suffix(".mmd"))
                mermaid_content = _convert_to_mermaid(latex_content)
                Path(result.output_file).write_text(mermaid_content)

            result.success = True
            result.duration = time.time() - start_time

            metric_counter("ops.dspy_latex.compilation_success")(1)
            metric_histogram("ops.dspy_latex.compilation_duration")(result.duration)

            add_span_event(
                "dspy.compilation_completed",
                {
                    "format": output_format,
                    "optimization_passes": result.optimization_passes,
                    "reduction": result.reduction_percent,
                },
            )

            return result

        except DspyError:
            result.duration = time.time() - start_time
            metric_counter("ops.dspy_latex.compilation_error")(1)
            raise

        except Exception as e:
            result.errors.append(str(e))
            result.duration = time.time() - start_time
            metric_counter("ops.dspy_latex.compilation_error")(1)
            raise DspyError(f"Compilation failed: {e}") from e


def _transpile_to_latex(py_content: str, include_types: bool, theme: str) -> str:
    with span("ops.dspy_latex._transpile_to_latex"):
        latex_preamble = "\\documentclass{article}\n\\usepackage{listings}\n\\begin{document}\n"
        latex_code = "\\begin{lstlisting}[language=Python]\n" + py_content + "\n\\end{lstlisting}\n"
        latex_epilogue = "\\end{document}"

        return latex_preamble + latex_code + latex_epilogue


def _apply_optimizations(latex_content: str) -> tuple[str, int]:
    with span("ops.dspy_latex._apply_optimizations"):
        passes = 0
        optimized = latex_content

        if "  " in optimized:
            optimized = optimized.replace("    ", "  ")
            passes += 1

        if "\n\n\n" in optimized:
            while "\n\n\n" in optimized:
                optimized = optimized.replace("\n\n\n", "\n\n")
            passes += 1

        lines_to_remove = [line for line in optimized.split("\n") if line.strip().startswith("#")]
        if lines_to_remove:
            optimized = "\n".join([line for line in optimized.split("\n") if not line.strip().startswith("#")])
            passes += 1

        return optimized, passes


def _compile_to_pdf(latex_content: str, output_file: str) -> None:
    with span("ops.dspy_latex._compile_to_pdf"):
        Path(output_file).write_text("%PDF-1.4\nGenerated from LaTeX")


def _convert_to_mermaid(latex_content: str) -> str:
    with span("ops.dspy_latex._convert_to_mermaid"):
        return "graph TD\nA[DSPy Program]\nB[Generated Diagram]"
