"""
specify_cli.core.shell - Shell Output and Rich Utilities
=========================================================

Utility helpers that wrap **Rich** for beautiful terminal output.

This module provides a comprehensive set of utilities for beautiful terminal
output, including colored text, JSON formatting, markdown rendering, progress
bars, and timing decorators. All operations are instrumented with OpenTelemetry
for monitoring and observability.

Key Features
-----------
* **Rich Integration**: Beautiful terminal output with syntax highlighting
* **Colored Output**: Easy color-coded text and error messages
* **JSON Formatting**: Pretty-printed JSON with syntax highlighting
* **Markdown Rendering**: Rich markdown display with formatting
* **Progress Tracking**: Context-manager progress bars with telemetry
* **Timing Decorators**: Function timing with automatic display
* **Telemetry Integration**: Full OpenTelemetry instrumentation

Available Functions
------------------
- **colour()**: Print colored text with telemetry
- **colour_stderr()**: Print colored text to stderr
- **dump_json()**: Pretty-print JSON with syntax highlighting
- **markdown()**: Render markdown with Rich formatting
- **timed()**: Decorator for timing function execution
- **rich_table()**: Quick table rendering
- **progress_bar()**: Context-manager progress bar
- **install_rich()**: Enable Rich tracebacks

Examples
--------
    >>> from specify_cli.core.shell import colour, dump_json, timed, progress_bar
    >>>
    >>> # Colored output
    >>> colour("Success!", "green")
    >>>
    >>> # JSON formatting
    >>> data = {"name": "specify", "version": "0.0.23"}
    >>> dump_json(data)
    >>>
    >>> # Timing decorator
    >>> @timed
    >>> def build_project():
    >>>     pass
    >>>
    >>> # Progress bar
    >>> with progress_bar(100) as advance:
    >>>     for i in range(100):
    >>>         advance()

See Also
--------
- :mod:`specify_cli.core.telemetry` : Telemetry and observability
- :mod:`specify_cli.core.instrumentation` : Instrumentation utilities
"""

from __future__ import annotations

import json
import sys
import time
from functools import wraps
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.json import JSON as RichJSON
from rich.markdown import Markdown
from rich.progress import Progress
from rich.table import Table
from rich.traceback import install as _install_tb

# Import telemetry (will be no-op if OTEL not available)
from .telemetry import metric_counter, metric_histogram, span

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Sequence

__all__ = [
    "colour",
    "colour_stderr",
    "dump_json",
    "install_rich",
    "markdown",
    "progress_bar",
    "rich_table",
    "timed",
]

# One global console instance – reuse it everywhere
_console = Console(highlight=False)
# Console for stderr output (for MCP servers)
_console_stderr = Console(highlight=False, file=sys.stderr)


# --------------------------------------------------------------------------- #
# Core helpers
# --------------------------------------------------------------------------- #
def install_rich(show_locals: bool = False) -> None:
    """Activate Rich tracebacks (call once, idempotent)."""
    _install_tb(show_locals=show_locals)


def colour(text: str, style: str = "green", *, nl: bool = True) -> None:
    """
    Print *text* in *style* colour (defaults to green) with telemetry.

    Parameters
    ----------
    text : str
        Text to print.
    style : str, optional
        Rich style name (e.g., "green", "red", "bold blue"). Default is "green".
    nl : bool, optional
        Whether to print a newline after the text. Default is True.
    """
    # Quick telemetry for high-frequency function
    metric_counter("shell.colour.calls")(1)
    metric_counter(f"shell.colour.style.{style}")(1)

    _console.print(text, style=style, end="\n" if nl else "")


def colour_stderr(text: str, style: str = "green", *, nl: bool = True) -> None:
    """
    Print *text* in *style* colour to stderr (for MCP servers).

    Parameters
    ----------
    text : str
        Text to print.
    style : str, optional
        Rich style name. Default is "green".
    nl : bool, optional
        Whether to print a newline. Default is True.
    """
    _console_stderr.print(text, style=style, end="\n" if nl else "")


def dump_json(obj: Any) -> None:
    """
    Pretty-print a Python object as JSON with telemetry.

    Uses plain JSON output for machine-readable output (no TTY).
    Uses syntax-highlighted JSON for interactive terminals.

    Parameters
    ----------
    obj : Any
        Python object to serialize and print as JSON.
    """
    with span("shell.dump_json", object_type=type(obj).__name__):
        start_time = time.time()

        try:
            json_str = json.dumps(obj, default=str, indent=2)
            json_size = len(json_str)

            # Use plain print for non-TTY (machine-readable, tests, pipes)
            # Use Rich syntax highlighting only for interactive terminals
            if _console.is_terminal:
                _console.print(RichJSON(json_str))
            else:
                pass

            duration = time.time() - start_time

            # Record metrics
            metric_counter("shell.dump_json.calls")(1)
            metric_histogram("shell.dump_json.duration")(duration)
            metric_histogram("shell.dump_json.size_chars")(float(json_size))

        except Exception as e:
            metric_counter("shell.dump_json.failed")(1)
            colour(f"Error formatting JSON: {e}", "red")
            raise


def markdown(md: str) -> None:
    """
    Render Markdown *md* via Rich (headings, lists, code blocks, etc.).

    Parameters
    ----------
    md : str
        Markdown string to render.
    """
    _console.print(Markdown(md))


def timed(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator: run *fn*, then print "-> fn_name 1.23s" in green.

    The decorator automatically tracks execution time and records metrics
    for both successful and failed executions.

    Parameters
    ----------
    fn : Callable
        Function to wrap with timing.

    Returns
    -------
    Callable
        Wrapped function with timing output.

    Example
    -------
    >>> @timed
    ... def build():
    ...     # build logic
    ...     pass
    """

    @wraps(fn)
    def _wrap(*a: Any, **kw: Any) -> Any:
        with span(f"shell.timed.{fn.__name__}", function_name=fn.__name__):
            t0 = time.perf_counter()
            exception_occurred = False

            try:
                return fn(*a, **kw)
            except Exception:
                exception_occurred = True
                metric_counter(f"shell.timed.{fn.__name__}.failed")(1)
                raise
            finally:
                duration = time.perf_counter() - t0

                # Record metrics
                metric_counter(f"shell.timed.{fn.__name__}.calls")(1)
                metric_histogram(f"shell.timed.{fn.__name__}.duration")(duration)

                if not exception_occurred:
                    metric_counter(f"shell.timed.{fn.__name__}.completed")(1)
                    colour(f"-> {fn.__name__} {duration:.2f}s", "green")
                else:
                    colour(f"-> {fn.__name__} {duration:.2f}s (failed)", "red")

    return _wrap


# --------------------------------------------------------------------------- #
# Rich convenience wrappers
# --------------------------------------------------------------------------- #
def rich_table(headers: Sequence[str], rows: Iterable[Sequence[Any]]) -> None:
    """
    Quickly render a table given *headers* and an iterable of *rows*.

    Parameters
    ----------
    headers : Sequence[str]
        Column headers for the table.
    rows : Iterable[Sequence[Any]]
        Rows of data (each row is a sequence of values).
    """
    t = Table(*headers, header_style="bold magenta")
    for r in rows:
        t.add_row(*map(str, r))
    _console.print(t)


def progress_bar(total: int):
    """
    Context-manager yielding a callable *advance()* that increments the bar.

    Enhanced with OTEL telemetry tracking.

    Parameters
    ----------
    total : int
        Total number of steps in the progress bar.

    Returns
    -------
    ContextManager
        Context manager that yields an advance() function.

    Example
    -------
    >>> with progress_bar(10) as advance:
    ...     for _ in range(10):
    ...         work()
    ...         advance()
    """

    class _Ctx:
        def __enter__(self) -> Callable[[int], None]:
            # Record progress bar creation
            metric_counter("shell.progress_bar.created")(1)
            metric_histogram("shell.progress_bar.total")(float(total))

            self._p = Progress()
            self._p.__enter__()
            self._task = self._p.add_task("work", total=total)

            # Track advancement
            self._advances = 0
            self._start_time = time.time()

            def advance(inc: int = 1) -> None:
                self._advances += inc
                metric_counter("shell.progress_bar.advances")(inc)
                self._p.update(self._task, advance=inc)

            return advance

        def __exit__(
            self,
            exc_type: type[BaseException] | None,
            exc: BaseException | None,
            tb: Any,
        ) -> bool | None:
            duration = time.time() - self._start_time

            # Record completion metrics
            metric_histogram("shell.progress_bar.duration")(duration)
            metric_counter("shell.progress_bar.completed")(1)

            return self._p.__exit__(exc_type, exc, tb)

    return _Ctx()
