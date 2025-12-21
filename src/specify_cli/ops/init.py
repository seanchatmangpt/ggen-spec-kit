"""
specify_cli.ops.init - Project Initialization Operations
=========================================================

Business logic for project initialization operations.

This module contains pure business logic for initializing new specify
projects. It orchestrates runtime layer calls but contains no I/O itself.

Key Features
-----------
* **Project Validation**: Validate project names and paths
* **AI Assistant Selection**: Determine AI assistant configuration
* **Template Application**: Coordinate template download and extraction
* **Git Integration**: Initialize git repositories

Design Principles
----------------
* Pure functions (same input → same output)
* No direct I/O (delegates to runtime layer)
* Fully testable with mocked runtime
* Returns structured results for commands to format

Examples
--------
    >>> from specify_cli.ops.init import initialize_project
    >>>
    >>> result = initialize_project(
    ...     name="my-project",
    ...     ai_assistant="claude",
    ...     script_type="sh",
    ... )
    >>> print(result["success"])
    True

See Also
--------
- :mod:`specify_cli.runtime` : Runtime execution layer
- :mod:`specify_cli.commands.init` : CLI command handler
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from specify_cli.core.instrumentation import add_span_attributes, add_span_event
from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, metric_histogram, span
from specify_cli.runtime import git, github, template

__all__ = [
    "InitError",
    "InitResult",
    "determine_ai_assistant",
    "initialize_project",
    "validate_project_name",
]


# Valid project name pattern
PROJECT_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]*$")

# Supported AI assistants
SUPPORTED_AI_ASSISTANTS = ["claude", "cursor", "copilot"]

# Default values
DEFAULT_AI_ASSISTANT = "claude"
DEFAULT_SCRIPT_TYPE = "sh"


class InitError(Exception):
    """Project initialization error."""

    def __init__(
        self,
        message: str,
        *,
        recoverable: bool = False,
        suggestions: list[str] | None = None,
    ) -> None:
        super().__init__(message)
        self.recoverable = recoverable
        self.suggestions = suggestions or []


@dataclass
class InitResult:
    """Result of project initialization."""

    success: bool
    project_path: Path | None = None
    ai_assistant: str = ""
    script_type: str = ""
    git_initialized: bool = False
    release_tag: str = ""
    files_extracted: int = 0
    duration: float = 0.0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def validate_project_name(name: str) -> tuple[bool, str | None]:
    """Validate a project name.

    Parameters
    ----------
    name : str
        Project name to validate.

    Returns
    -------
    tuple[bool, str | None]
        (is_valid, error_message)
    """
    if not name:
        return False, "Project name cannot be empty"

    if not PROJECT_NAME_PATTERN.match(name):
        return False, (
            f"Invalid project name '{name}'. "
            "Must start with a letter and contain only letters, numbers, hyphens, and underscores."
        )

    # Check for reserved names
    reserved_names = {".", "..", "con", "prn", "aux", "nul"}
    if name.lower() in reserved_names:
        return False, f"'{name}' is a reserved name and cannot be used."

    return True, None


def determine_ai_assistant(
    cli_value: str | None = None,
    interactive: bool = False,
) -> str:
    """Determine which AI assistant to use.

    Priority:
    1. CLI argument (if provided)
    2. Environment variable (SPECIFY_DEFAULT_AI)
    3. Interactive prompt (if enabled and terminal)
    4. Default value

    Parameters
    ----------
    cli_value : str, optional
        Value passed via CLI argument.
    interactive : bool, optional
        Whether to prompt interactively.

    Returns
    -------
    str
        AI assistant type.

    Raises
    ------
    InitError
        If specified assistant is not supported.
    """
    import os

    # CLI argument takes precedence
    if cli_value:
        if cli_value not in SUPPORTED_AI_ASSISTANTS:
            raise InitError(
                f"Unsupported AI assistant: {cli_value}",
                suggestions=[f"Supported: {', '.join(SUPPORTED_AI_ASSISTANTS)}"],
            )
        return cli_value

    # Check environment variable
    env_value = os.getenv("SPECIFY_DEFAULT_AI", "").lower()
    if env_value and env_value in SUPPORTED_AI_ASSISTANTS:
        return env_value

    # Interactive mode handled by commands layer
    return DEFAULT_AI_ASSISTANT


def _check_project_path(
    name: str | None, here: bool, project_path: Path | None = None
) -> tuple[Path, bool]:
    """Determine project path and whether it's current directory.

    Returns
    -------
    tuple[Path, bool]
        (project_path, is_current_dir)
    """
    if here:
        return Path.cwd(), True

    if project_path:
        return project_path, False

    if name:
        return Path.cwd() / name, False

    raise InitError(
        "Either project name or --here flag must be specified",
        suggestions=[
            "Provide a project name: specify init my-project",
            "Use --here to initialize in current directory",
        ],
    )


@timed
def initialize_project(
    name: str | None = None,
    *,
    ai_assistant: str | None = None,
    script_type: str | None = None,
    here: bool = False,
    no_git: bool = False,
    project_path: Path | None = None,
    github_token: str | None = None,
) -> InitResult:
    """Initialize a new specify project.

    This is the main orchestration function for project initialization.
    It coordinates runtime layer calls to:
    1. Fetch the latest template release from GitHub
    2. Download and extract the template
    3. Initialize a git repository (optional)

    Parameters
    ----------
    name : str, optional
        Project name. Required unless --here is used.
    ai_assistant : str, optional
        AI assistant type (claude, cursor, copilot).
    script_type : str, optional
        Script type (sh, ps1).
    here : bool, optional
        Initialize in current directory.
    no_git : bool, optional
        Skip git initialization.
    project_path : Path, optional
        Explicit project path (overrides name).
    github_token : str, optional
        GitHub token for authenticated requests.

    Returns
    -------
    InitResult
        Result with success status and details.

    Raises
    ------
    InitError
        If initialization fails.
    """
    start_time = time.time()
    result = InitResult(success=False)

    with span(
        "ops.init.initialize_project",
        project_name=name or "",
        ai_assistant=ai_assistant or "",
        here=here,
    ):
        try:
            # Validate and resolve project path
            target_path, is_current_dir = _check_project_path(name, here, project_path)
            result.project_path = target_path

            add_span_event(
                "init.path_resolved", {"path": str(target_path), "is_current": is_current_dir}
            )

            # Validate project name if not using current dir
            if not is_current_dir and name:
                is_valid, error_msg = validate_project_name(name)
                if not is_valid:
                    raise InitError(error_msg or "Invalid project name")

            # Check if target already exists (for new projects)
            if not is_current_dir and target_path.exists():
                raise InitError(
                    f"Directory '{target_path.name}' already exists",
                    suggestions=[
                        "Choose a different name",
                        "Use --here to initialize in existing directory",
                    ],
                )

            # Determine AI assistant
            assistant = determine_ai_assistant(ai_assistant)
            result.ai_assistant = assistant

            # Determine script type
            stype = script_type or DEFAULT_SCRIPT_TYPE
            result.script_type = stype

            add_span_attributes(
                resolved_ai_assistant=assistant,
                resolved_script_type=stype,
            )

            # Fetch latest release
            add_span_event("init.fetching_release", {})
            release_data = github.fetch_latest_release(
                owner="github",
                repo="spec-kit",
                token=github_token,
            )
            result.release_tag = release_data.get("tag_name", "")

            add_span_event("init.release_fetched", {"tag": result.release_tag})

            # Find matching asset
            asset = github.find_matching_asset(release_data, assistant, stype)
            if not asset:
                available = [a.get("name", "?") for a in release_data.get("assets", [])]
                raise InitError(
                    f"No template found for {assistant}/{stype}",
                    suggestions=[
                        f"Available templates: {', '.join(available[:5])}",
                        "Try a different AI assistant or script type",
                    ],
                )

            # Download asset
            add_span_event("init.downloading_template", {"asset": asset.get("name", "")})
            import tempfile

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir)
                zip_path = github.download_asset(
                    asset,
                    tmp_path,
                    token=github_token,
                )

                # Extract template
                add_span_event("init.extracting_template", {})
                template.extract_template(
                    zip_path,
                    target_path,
                    is_current_dir=is_current_dir,
                )

            # Ensure scripts are executable
            updated, failures = template.ensure_executable_scripts(target_path)
            if failures:
                result.warnings.extend(failures)

            add_span_event("init.template_extracted", {"scripts_updated": updated})

            # Initialize git repository
            if not no_git:
                add_span_event("init.initializing_git", {})
                try:
                    git.init_repo(target_path)
                    result.git_initialized = True
                except Exception as e:
                    result.warnings.append(f"Git initialization failed: {e}")

            # Success
            result.success = True
            result.duration = time.time() - start_time

            # Record metrics
            metric_counter("ops.init.success")(1)
            metric_histogram("ops.init.duration")(result.duration)

            add_span_event(
                "init.completed",
                {
                    "success": True,
                    "duration": result.duration,
                    "git_initialized": result.git_initialized,
                },
            )

            return result

        except InitError:
            result.duration = time.time() - start_time
            metric_counter("ops.init.error")(1)
            raise

        except Exception as e:
            result.duration = time.time() - start_time
            result.errors.append(str(e))
            metric_counter("ops.init.error")(1)

            add_span_event("init.failed", {"error": str(e)})

            raise InitError(f"Project initialization failed: {e}") from e
