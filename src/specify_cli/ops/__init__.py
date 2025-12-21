"""
specify_cli.ops - Operations Layer
===================================

Business logic layer containing pure operations for specify-cli.

This layer contains all business logic with NO side effects:
- Project initialization logic
- Tool checking logic
- Version checking logic
- Process mining logic (optional, requires pm4py)

Layer Architecture
-----------------
The ops layer sits between commands and runtime:

    Commands Layer → Ops Layer → Runtime Layer
          ↑              ↑             ↑
      (Typer CLI)    (Pure Logic)   (I/O)

Design Principles
----------------
* **Pure Functions**: Same input → same output
* **No Side Effects**: No subprocess, file I/O, or network calls
* **Testable**: Easy to unit test with mocked runtime
* **Composable**: Operations can be combined safely

Examples
--------
    >>> from specify_cli.ops import init, check, version
    >>>
    >>> # Initialize a project
    >>> result = init.initialize_project(
    ...     name="my-project",
    ...     ai_assistant="claude",
    ... )
    >>>
    >>> # Check tools
    >>> check_result = check.check_all_tools()
    >>>
    >>> # Get version info
    >>> version_info = version.get_version_info()

See Also
--------
- :mod:`specify_cli.commands` : CLI commands layer
- :mod:`specify_cli.runtime` : Runtime execution layer
- :mod:`specify_cli.core` : Core infrastructure
"""

from __future__ import annotations

# Project initialization
from .init import (
    InitError,
    InitResult,
    determine_ai_assistant,
    initialize_project,
    validate_project_name,
)

# Tool checking
from .check import (
    CheckResult,
    ToolStatus,
    check_all_tools,
    check_tool,
    get_environment_info,
    get_tool_status,
)

# Version checking
from .version import (
    VersionInfo,
    check_for_updates,
    get_build_info,
    get_current_version,
    get_version_info,
)

# Process mining (optional, requires pm4py)
try:
    from .process_mining import (
        conform_trace,
        convert_model,
        discover_process_model,
        filter_log,
        get_log_statistics,
        load_event_log,
        sample_log,
        save_model,
        visualize_model,
    )

    _PM_AVAILABLE = True
except ImportError:
    _PM_AVAILABLE = False

__all__ = [
    # Init operations
    "initialize_project",
    "validate_project_name",
    "determine_ai_assistant",
    "InitResult",
    "InitError",
    # Check operations
    "check_all_tools",
    "check_tool",
    "get_tool_status",
    "get_environment_info",
    "CheckResult",
    "ToolStatus",
    # Version operations
    "get_version_info",
    "check_for_updates",
    "get_current_version",
    "get_build_info",
    "VersionInfo",
]

# Add process mining exports if available
if _PM_AVAILABLE:
    __all__.extend([
        "load_event_log",
        "save_model",
        "discover_process_model",
        "conform_trace",
        "get_log_statistics",
        "convert_model",
        "visualize_model",
        "filter_log",
        "sample_log",
    ])
