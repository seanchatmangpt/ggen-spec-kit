"""
specify_cli.runtime.ggen - ggen CLI Wrapper
============================================

Runtime layer for ggen v5.0.2 (Graphen Generator) CLI operations.

This module provides a wrapper around the ggen CLI tool for
ontology compilation and code generation operations.

Install ggen via:
- brew install seanchatmangpt/ggen/ggen (recommended)
- cargo install ggen-cli-lib
- docker pull seanchatman/ggen:5.0.2

Key Features
-----------
* **Ontology Compilation**: Compile RDF/OWL ontologies
* **Code Generation**: Generate code from specifications
* **Sync Operations**: Synchronize spec files
* **Telemetry**: Full OTEL instrumentation

Security
--------
* List-based subprocess calls only (no shell=True)
* Path validation before operations

Examples
--------
    >>> from specify_cli.runtime.ggen import compile_ontology, sync_specs
    >>>
    >>> compile_ontology(ontology_path, output_dir)
    >>> sync_specs(project_path)

See Also
--------
- :mod:`specify_cli.runtime.tools` : Tool detection
- :mod:`specify_cli.core.process` : Process execution
"""

from __future__ import annotations

import time
from pathlib import Path

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.process import run
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.runtime.tools import check_tool, which_tool

__all__ = [
    "is_ggen_available",
    "get_ggen_version",
    "compile_ontology",
    "sync_specs",
    "generate_code",
    "GgenError",
]


class GgenError(Exception):
    """ggen operation error."""

    def __init__(self, message: str, command: list[str] | None = None) -> None:
        super().__init__(message)
        self.command = command


def is_ggen_available() -> bool:
    """Check if ggen CLI is available.

    Returns
    -------
    bool
        True if ggen is installed and available.
    """
    return check_tool("ggen")


def get_ggen_version() -> str | None:
    """Get the installed ggen version.

    Returns
    -------
    str | None
        Version string or None if not installed.
    """
    if not is_ggen_available():
        return None

    with span("ggen.version"):
        try:
            output = run(["ggen", "--version"], capture=True, check=False)
            if output:
                # Parse version from output
                return output.strip()
            return "installed (version unknown)"
        except Exception:
            return None


def compile_ontology(
    ontology_path: Path,
    output_dir: Path | None = None,
    *,
    format: str = "ttl",
    validate: bool = True,
) -> bool:
    """Compile an RDF/OWL ontology using ggen.

    Parameters
    ----------
    ontology_path : Path
        Path to the ontology file.
    output_dir : Path, optional
        Output directory. Defaults to same as input.
    format : str, optional
        Output format (ttl, rdf, owl). Default is "ttl".
    validate : bool, optional
        Whether to validate before compilation. Default is True.

    Returns
    -------
    bool
        True if compilation succeeded.

    Raises
    ------
    GgenError
        If ggen is not available or compilation fails.
    """
    if not is_ggen_available():
        raise GgenError(
            "ggen is not installed. Install with: "
            "brew install seanchatmangpt/ggen/ggen or cargo install ggen-cli-lib"
        )

    start_time = time.time()

    with span(
        "ggen.compile",
        ontology=str(ontology_path),
        output=str(output_dir) if output_dir else "",
        format=format,
    ):
        add_span_event("ggen.compile.starting", {"file": str(ontology_path)})

        try:
            cmd = ["ggen", "compile", str(ontology_path)]

            if output_dir:
                cmd.extend(["--output", str(output_dir)])

            cmd.extend(["--format", format])

            if validate:
                cmd.append("--validate")

            run(cmd, capture=True, check=True)

            duration = time.time() - start_time

            metric_counter("ggen.compile.success")(1)
            metric_histogram("ggen.compile.duration")(duration)

            add_span_event(
                "ggen.compile.completed",
                {"duration": duration, "format": format},
            )

            return True

        except Exception as e:
            duration = time.time() - start_time

            metric_counter("ggen.compile.error")(1)
            metric_histogram("ggen.compile.duration")(duration)

            add_span_event("ggen.compile.failed", {"error": str(e)})

            raise GgenError(f"Ontology compilation failed: {e}") from e


def sync_specs(
    project_path: Path,
    *,
    watch: bool = False,
    verbose: bool = False,
) -> bool:
    """Synchronize specification files using ggen.

    Parameters
    ----------
    project_path : Path
        Project root directory.
    watch : bool, optional
        Watch for file changes. Default is False.
    verbose : bool, optional
        Enable verbose output. Default is False.

    Returns
    -------
    bool
        True if sync succeeded.

    Raises
    ------
    GgenError
        If ggen is not available or sync fails.
    """
    if not is_ggen_available():
        raise GgenError(
            "ggen is not installed. Install with: "
            "brew install seanchatmangpt/ggen/ggen or cargo install ggen-cli-lib"
        )

    start_time = time.time()

    with span("ggen.sync", project=str(project_path), watch=watch):
        add_span_event("ggen.sync.starting", {"path": str(project_path)})

        try:
            cmd = ["ggen", "sync"]

            if watch:
                cmd.append("--watch")

            if verbose:
                cmd.append("--verbose")

            run(cmd, capture=True, check=True, cwd=project_path)

            duration = time.time() - start_time

            metric_counter("ggen.sync.success")(1)
            metric_histogram("ggen.sync.duration")(duration)

            add_span_event("ggen.sync.completed", {"duration": duration})

            return True

        except Exception as e:
            duration = time.time() - start_time

            metric_counter("ggen.sync.error")(1)

            add_span_event("ggen.sync.failed", {"error": str(e)})

            raise GgenError(f"Spec sync failed: {e}") from e


def generate_code(
    spec_path: Path,
    output_dir: Path,
    *,
    language: str = "python",
    template: str | None = None,
) -> bool:
    """Generate code from specifications using ggen.

    Parameters
    ----------
    spec_path : Path
        Path to specification file.
    output_dir : Path
        Output directory for generated code.
    language : str, optional
        Target language. Default is "python".
    template : str, optional
        Template to use for generation.

    Returns
    -------
    bool
        True if generation succeeded.

    Raises
    ------
    GgenError
        If ggen is not available or generation fails.
    """
    if not is_ggen_available():
        raise GgenError(
            "ggen is not installed. Install with: "
            "brew install seanchatmangpt/ggen/ggen or cargo install ggen-cli-lib"
        )

    start_time = time.time()

    with span(
        "ggen.generate",
        spec=str(spec_path),
        output=str(output_dir),
        language=language,
    ):
        add_span_event(
            "ggen.generate.starting",
            {"spec": str(spec_path), "language": language},
        )

        try:
            cmd = [
                "ggen",
                "generate",
                str(spec_path),
                "--output",
                str(output_dir),
                "--language",
                language,
            ]

            if template:
                cmd.extend(["--template", template])

            run(cmd, capture=True, check=True)

            duration = time.time() - start_time

            metric_counter("ggen.generate.success")(1)
            metric_histogram("ggen.generate.duration")(duration)

            add_span_event(
                "ggen.generate.completed",
                {"duration": duration, "language": language},
            )

            return True

        except Exception as e:
            duration = time.time() - start_time

            metric_counter("ggen.generate.error")(1)

            add_span_event("ggen.generate.failed", {"error": str(e)})

            raise GgenError(f"Code generation failed: {e}") from e
