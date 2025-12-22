"""
specify_cli.runtime.ggen - ggen CLI Wrapper
============================================

Runtime layer for ggen v5.0.2 (Graph Generator) CLI operations.

This module provides a wrapper around the ggen CLI tool for
RDF-to-Markdown transformations via ggen sync.

Install ggen via:
- brew install seanchatmangpt/ggen/ggen (recommended)
- cargo install ggen-cli-lib
- docker pull seanchatman/ggen:5.0.2

Key Features
-----------
* **Sync Operations**: Synchronize RDF specs to markdown via ggen.toml
* **Telemetry**: Full OTEL instrumentation
* **Error Handling**: Comprehensive error reporting

Security
--------
* List-based subprocess calls only (no shell=True)
* Path validation before operations

Examples
--------
    >>> from specify_cli.runtime.ggen import sync_specs
    >>>
    >>> sync_specs(project_path)

See Also
--------
- :mod:`specify_cli.runtime.tools` : Tool detection
- :mod:`specify_cli.core.process` : Process execution
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from specify_cli.core.instrumentation import add_span_event
from specify_cli.core.process import run, run_logged
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.ops.transform import (
    StageResult,
    TransformConfig,
    TransformResult,
    canonicalize_output,
    compose_transform,
)
from specify_cli.runtime.receipt import (
    generate_receipt,
    sha256_string,
)
from specify_cli.runtime.tools import check_tool

__all__ = [
    "GgenError",
    "get_ggen_version",
    "is_ggen_available",
    "run_logged",  # Re-export for patching in tests
    "run_transform",
    "sync_specs",
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
        except Exception:
            return None
        else:
            if output:
                # Parse version from output
                return output.strip()
            return "installed (version unknown)"


def sync_specs(
    project_path: Path,
    *,
    watch: bool = False,
    verbose: bool = False,
) -> bool:
    """Synchronize specification files using ggen sync.

    Executes the five-stage transformation pipeline:
    - μ₁ Normalize: Load RDF, validate SHACL
    - μ₂ Extract: Execute SPARQL queries
    - μ₃ Emit: Render Tera templates
    - μ₄ Canonicalize: Format output
    - μ₅ Receipt: Generate SHA256 hash proof

    Parameters
    ----------
    project_path : Path
        Project root directory (must contain ggen.toml).
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

        cmd = ["ggen", "sync"]

        if watch:
            cmd.append("--watch")

        if verbose:
            cmd.append("--verbose")

        try:
            run(cmd, capture=True, check=True, cwd=project_path)
        except Exception as e:
            duration = time.time() - start_time
            metric_counter("ggen.sync.error")(1)
            add_span_event("ggen.sync.failed", {"error": str(e)})
            raise GgenError(f"Spec sync failed: {e}") from e
        else:
            duration = time.time() - start_time
            metric_counter("ggen.sync.success")(1)
            metric_histogram("ggen.sync.duration")(duration)
            add_span_event("ggen.sync.completed", {"duration": duration})
            return True


@timed
def run_transform(config: TransformConfig) -> TransformResult:
    """Execute complete μ transformation pipeline.

    Implements: output = μ₅(μ₄(μ₃(μ₂(μ₁(input)))))

    Parameters
    ----------
    config : TransformConfig
        Transformation configuration from ggen.toml

    Returns
    -------
    TransformResult
        Complete result with all stage outputs and receipt
    """
    with span("ggen.transform", {"name": config.name}):
        stage_results = {}

        # μ₁ NORMALIZE: Load and validate RDF
        stage_results["normalize"] = _run_normalize(config)
        if not stage_results["normalize"].success:
            return compose_transform(config, stage_results)

        # μ₂ EXTRACT: Execute SPARQL
        normalize_output = stage_results["normalize"].output
        if normalize_output is None:
            stage_results["extract"] = StageResult(
                stage="extract",
                success=False,
                input_hash="",
                output_hash="",
                output=None,
                errors=["Normalize stage produced no output"],
            )
            return compose_transform(config, stage_results)

        stage_results["extract"] = _run_extract(config, normalize_output)
        if not stage_results["extract"].success:
            return compose_transform(config, stage_results)

        # μ₃ EMIT: Render template
        stage_results["emit"] = _run_emit(
            config,
            stage_results["extract"].output,
        )
        if not stage_results["emit"].success:
            return compose_transform(config, stage_results)

        # μ₄ CANONICALIZE: Format output
        stage_results["canonicalize"] = canonicalize_output(
            stage_results["emit"].output,
        )

        # Write output file
        output_path = Path(config.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(stage_results["canonicalize"].output)

        # μ₅ RECEIPT: Generate proof
        stage_results["receipt"] = _run_receipt(config, stage_results)

        return compose_transform(config, stage_results)


def _run_normalize(config: TransformConfig) -> StageResult:
    """μ₁ NORMALIZE: Load RDF and validate SHACL."""
    stage_start = time.time()
    with span("ggen.normalize"):
        errors = []

        # Load input files
        rdf_content = ""
        for input_file in config.input_files:
            path = Path(input_file)
            if not path.exists():
                errors.append(f"Input file not found: {input_file}")
                continue
            rdf_content += path.read_text() + "\n"

        if errors:
            return StageResult(
                stage="normalize",
                success=False,
                input_hash="",
                output_hash="",
                output=None,
                errors=errors,
            )

        # Validate SHACL shapes if specified
        if config.schema_files:
            validation = _validate_shacl(rdf_content, config.schema_files)
            if not validation["valid"]:
                errors.extend(validation["violations"])

        input_hash = sha256_string(rdf_content)
        output_hash = input_hash  # Normalize is identity for valid RDF

        # Record stage duration histogram
        stage_duration = time.time() - stage_start
        metric_histogram("ggen.stage.normalize.duration")(stage_duration)
        add_span_event("ggen.normalize.completed", {"duration_ms": stage_duration * 1000})

        return StageResult(
            stage="normalize",
            success=len(errors) == 0,
            input_hash=input_hash,
            output_hash=output_hash,
            output=rdf_content,
            errors=errors,
        )


def _run_extract(config: TransformConfig, rdf_content: str) -> StageResult:
    """μ₂ EXTRACT: Execute SPARQL query."""
    stage_start = time.time()
    with span("ggen.extract"):
        query_path = Path(config.sparql_query)
        if not query_path.exists():
            return StageResult(
                stage="extract",
                success=False,
                input_hash=sha256_string(rdf_content),
                output_hash="",
                output=None,
                errors=[f"SPARQL query not found: {config.sparql_query}"],
            )

        query = query_path.read_text()

        # Execute SPARQL via ggen or local engine
        result = _execute_sparql(rdf_content, query)

        output_hash = sha256_string(json.dumps(result))

        # Record stage duration histogram
        stage_duration = time.time() - stage_start
        metric_histogram("ggen.stage.extract.duration")(stage_duration)
        add_span_event("ggen.extract.completed", {"duration_ms": stage_duration * 1000})

        return StageResult(
            stage="extract",
            success=True,
            input_hash=sha256_string(rdf_content),
            output_hash=output_hash,
            output=result,
            errors=[],
        )


def _run_emit(config: TransformConfig, extracted_data: Any) -> StageResult:
    """μ₃ EMIT: Render Tera template."""
    stage_start = time.time()
    with span("ggen.emit"):
        template_path = Path(config.template)
        if not template_path.exists():
            return StageResult(
                stage="emit",
                success=False,
                input_hash=sha256_string(json.dumps(extracted_data)),
                output_hash="",
                output=None,
                errors=[f"Template not found: {config.template}"],
            )

        template = template_path.read_text()

        # Render Tera template via ggen or local engine
        rendered = _render_tera(template, extracted_data)

        # Record stage duration histogram
        stage_duration = time.time() - stage_start
        metric_histogram("ggen.stage.emit.duration")(stage_duration)
        add_span_event("ggen.emit.completed", {"duration_ms": stage_duration * 1000})

        return StageResult(
            stage="emit",
            success=True,
            input_hash=sha256_string(json.dumps(extracted_data)),
            output_hash=sha256_string(rendered),
            output=rendered,
            errors=[],
        )


def _run_receipt(
    config: TransformConfig,
    stage_results: dict[str, StageResult],
) -> StageResult:
    """μ₅ RECEIPT: Generate cryptographic proof."""
    with span("ggen.receipt"):
        input_path = Path(config.input_files[0])
        output_path = Path(config.output_file)

        stage_outputs = {
            stage: result.output
            for stage, result in stage_results.items()
            if result.output is not None and isinstance(result.output, str)
        }

        receipt = generate_receipt(input_path, output_path, stage_outputs)

        # Write receipt file
        receipt_path = output_path.with_suffix(output_path.suffix + ".receipt.json")
        receipt_path.write_text(receipt.to_json())

        return StageResult(
            stage="receipt",
            success=True,
            input_hash=receipt.input_hash,
            output_hash=receipt.output_hash,
            output=receipt.to_json(),
            errors=[],
        )


def _validate_shacl(rdf_content: str, schema_files: list[str]) -> dict[str, Any]:
    """Validate RDF against SHACL shapes.

    Parameters
    ----------
    rdf_content : str
        RDF data in Turtle format to validate.
    schema_files : list[str]
        List of SHACL shape file paths.

    Returns
    -------
    dict[str, Any]
        Validation result with 'valid' bool and 'violations' list.
    """
    try:
        # Import rdflib here to avoid import errors if not installed
        from rdflib import Graph  # noqa: PLC0415
    except ImportError:
        # Graceful degradation: if rdflib not available, skip validation
        return {"valid": True, "violations": [], "warning": "rdflib not available"}

    with span("ggen.shacl_validate"):
        try:
            # Load data graph
            data_graph = Graph()
            data_graph.parse(data=rdf_content, format="turtle")

            # Load SHACL shapes
            shapes_graph = Graph()
            for schema_file in schema_files:
                path = Path(schema_file)
                if not path.exists():
                    return {"valid": False, "violations": [f"Schema not found: {schema_file}"]}
                shapes_graph.parse(str(path), format="turtle")

            # Try to use pyshacl if available
            try:
                import pyshacl  # noqa: PLC0415

                conforms, _results_graph, results_text = pyshacl.validate(
                    data_graph,
                    shacl_graph=shapes_graph,
                    inference="rdfs",
                    abort_on_first=False,
                )

                violations = []
                if not conforms:
                    # Parse validation report for violations
                    violations = [results_text]

                add_span_event(
                    "ggen.shacl_validated",
                    {"conforms": conforms, "violations_count": len(violations)},
                )
                return {"valid": conforms, "violations": violations}  # noqa: TRY300

            except ImportError:
                # pyshacl not available - basic validation only
                # Just check that shapes can be parsed
                add_span_event(
                    "ggen.shacl_skipped",
                    {"reason": "pyshacl not installed"},
                )
                return {"valid": True, "violations": [], "warning": "pyshacl not available"}

        except Exception as e:
            add_span_event("ggen.shacl_failed", {"error": str(e)})
            return {"valid": False, "violations": [f"SHACL validation error: {e}"]}


def _execute_sparql(rdf_content: str, query: str) -> dict[str, Any]:
    """Execute SPARQL query against RDF content.

    Uses rdflib's SPARQL engine to execute queries against RDF data.

    Parameters
    ----------
    rdf_content : str
        RDF data in Turtle format.
    query : str
        SPARQL SELECT query.

    Returns
    -------
    dict[str, Any]
        Query results in JSON-compatible format:
        {
            "results": [
                {"var1": "value1", "var2": "value2", ...},
                ...
            ],
            "count": int
        }

    Raises
    ------
    Exception
        If query execution fails or rdflib is not available.
    """
    try:
        # Import rdflib here to avoid import errors if not installed
        from rdflib import Graph  # noqa: PLC0415
    except ImportError as e:
        raise ImportError(
            "rdflib is required for SPARQL execution. "
            "Install with: uv sync or pip install rdflib>=7.0.0"
        ) from e

    with span("ggen.sparql_execute", {"query_length": len(query)}):
        try:
            # Create and load graph
            graph = Graph()
            graph.parse(data=rdf_content, format="turtle")

            add_span_event("ggen.sparql_graph_loaded", {"triples_count": len(graph)})

            # Execute SPARQL query
            query_results = graph.query(query)

            # Convert results to list of dicts
            results = []
            for row in query_results:
                result_dict = {}
                for var_name in query_results.vars:
                    value = row[var_name]
                    # Convert RDF terms to Python types
                    if value is not None:
                        result_dict[str(var_name)] = _rdf_term_to_python(value)
                    else:
                        result_dict[str(var_name)] = None
                results.append(result_dict)

            add_span_event(
                "ggen.sparql_executed",
                {"results_count": len(results), "variables": [str(v) for v in query_results.vars]},
            )
            metric_counter("ggen.sparql.queries")(1)
            metric_histogram("ggen.sparql.result_count")(float(len(results)))

            return {"results": results, "count": len(results)}

        except Exception as e:
            metric_counter("ggen.sparql.failed")(1)
            add_span_event("ggen.sparql_failed", {"error": str(e)})
            raise


def _rdf_term_to_python(term: Any) -> Any:
    """Convert RDF term to Python type.

    Parameters
    ----------
    term : Any
        RDF term (Literal, URIRef, BNode).

    Returns
    -------
    Any
        Python value (str, int, float, bool, etc.).
    """
    from rdflib import BNode, Literal, URIRef  # noqa: PLC0415

    if isinstance(term, Literal):
        # Return the native Python value
        return term.toPython()
    if isinstance(term, URIRef):
        # Return URI as string
        return str(term)
    if isinstance(term, BNode):
        # Return blank node ID
        return f"_:{term}"
    return str(term)


def _render_tera(template: str, data: Any) -> str:
    """Render Tera template with data using Jinja2 (Tera-compatible).

    Tera templates use syntax very similar to Jinja2:
    - {{ variable }} for variable substitution
    - {% for item in list %}...{% endfor %} for loops
    - {% if condition %}...{% endif %} for conditionals
    - Filters: | filter_name(args...)

    This implements μ₃ EMIT stage of the constitutional equation.

    Parameters
    ----------
    template : str
        Tera template content
    data : Any
        Data to render (typically dict with 'results' or 'sparql_results' key)

    Returns
    -------
    str
        Rendered template output

    Raises
    ------
    ValueError
        If template rendering fails
    """
    with span("ggen.render_tera"):
        try:
            from datetime import datetime

            from jinja2 import Environment, StrictUndefined, select_autoescape

            # Create Jinja2 environment with Tera-compatible settings
            env = Environment(
                autoescape=select_autoescape(default=False),
                undefined=StrictUndefined,
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # Add Tera-compatible filters
            def tera_replace(value: str, from_str: str = "", to: str = "") -> str:
                """Tera replace filter: | replace(from="x", to="y")"""
                return str(value).replace(from_str, to)

            def tera_default(value: Any, value_: Any = "") -> Any:
                """Tera default filter: | default(value="x")"""
                return value if value is not None and value != "" else value_

            def tera_first(value: list) -> Any:
                """Tera first filter: | first"""
                if isinstance(value, (list, tuple)) and len(value) > 0:
                    return value[0]
                return None

            def tera_unique(value: list, attribute: str | None = None) -> list:
                """Tera unique filter: | unique(attribute="x")"""
                if not isinstance(value, (list, tuple)):
                    return []
                if attribute:
                    seen = set()
                    result = []
                    for item in value:
                        key = (
                            item.get(attribute)
                            if isinstance(item, dict)
                            else getattr(item, attribute, None)
                        )
                        if key not in seen:
                            seen.add(key)
                            result.append(item)
                    return result
                return list(dict.fromkeys(value))

            def tera_filter(value: list, attribute: str | None = None, value_: Any = None) -> list:
                """Tera filter filter: | filter(attribute="x", value="y") or | filter(attribute="x")"""
                if not isinstance(value, (list, tuple)):
                    return []
                result = []
                for item in value:
                    if isinstance(item, dict):
                        if attribute:
                            item_val = item.get(attribute)
                            if value_ is not None:
                                if item_val == value_:
                                    result.append(item)
                            elif item_val:  # Just check attribute exists and is truthy
                                result.append(item)
                        else:
                            result.append(item)
                    else:
                        result.append(item)
                return result

            def tera_sort(value: list, attribute: str | None = None) -> list:
                """Tera sort filter: | sort(attribute="x")"""
                if not isinstance(value, (list, tuple)):
                    return []
                if attribute:
                    return sorted(
                        value,
                        key=lambda x: x.get(attribute, "")
                        if isinstance(x, dict)
                        else getattr(x, attribute, ""),
                    )
                return sorted(value)

            def tera_repeat(value: str, count: int = 1) -> str:
                """Tera repeat filter: | repeat(count=N)"""
                return str(value) * count

            def tera_indent(
                value: str, first: bool = False, blank: bool = False, prefix: str = "    "
            ) -> str:
                """Tera indent filter: | indent(first=true, blank=false)"""
                lines = str(value).split("\n")
                result = []
                for i, line in enumerate(lines):
                    if (i == 0 and not first) or (not line.strip() and not blank):
                        result.append(line)
                    else:
                        result.append(prefix + line)
                return "\n".join(result)

            def tera_date(value: datetime, format_str: str = "%Y-%m-%d") -> str:
                """Tera date filter: | date(format="%Y-%m-%d")"""
                if isinstance(value, datetime):
                    return value.strftime(format_str)
                return str(value)

            # Register filters with Tera-compatible names
            env.filters["replace"] = tera_replace
            env.filters["default"] = tera_default
            env.filters["first"] = tera_first
            env.filters["unique"] = tera_unique
            env.filters["filter"] = tera_filter
            env.filters["sort"] = tera_sort
            env.filters["repeat"] = tera_repeat
            env.filters["indent"] = tera_indent
            env.filters["date"] = tera_date

            # Add Tera-compatible functions
            env.globals["now"] = datetime.now

            # Prepare data context
            context: dict[str, Any] = {}
            if isinstance(data, dict):
                context = data.copy()
                # Tera templates often use 'results' or 'sparql_results'
                if "results" not in context and "sparql_results" not in context:
                    context["results"] = data
            elif isinstance(data, (list, tuple)):
                context["results"] = data
                context["sparql_results"] = data
            else:
                context["data"] = data

            # Compile and render template
            jinja_template = env.from_string(template)
            rendered = jinja_template.render(**context)

            metric_counter("ggen.tera_render.success")(1)
            add_span_event(
                "tera.rendered",
                {
                    "template_length": len(template),
                    "output_length": len(rendered),
                },
            )

            return rendered

        except ImportError as e:
            metric_counter("ggen.tera_render.import_error")(1)
            raise ValueError(f"Jinja2 not installed for Tera rendering: {e}") from e
        except Exception as e:
            metric_counter("ggen.tera_render.error")(1)
            add_span_event("tera.render_error", {"error": str(e)})
            raise ValueError(f"Tera template rendering failed: {e}") from e
