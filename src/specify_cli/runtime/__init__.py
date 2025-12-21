"""
specify_cli.runtime - Runtime Execution Layer
==============================================

Runtime layer containing all side-effect operations for specify-cli.

This layer isolates all I/O operations including:
- GitHub API calls
- Template downloads and extraction
- Git repository operations
- Tool detection and execution
- ggen CLI wrapper

Layer Architecture
-----------------
The runtime layer is the lowest layer, directly interfacing with
external systems:

    Commands Layer → Ops Layer → Runtime Layer
                                       ↓
                               External Systems
                     (GitHub, Git, File System, Tools)

Design Principles
----------------
* **Isolation**: All side effects contained in this layer
* **Security**: List-based subprocess calls only (no shell=True)
* **Observability**: Full OpenTelemetry instrumentation
* **Testability**: Easy to mock for unit testing ops layer

Examples
--------
    >>> from specify_cli.runtime import github, git, template
    >>>
    >>> # Fetch release from GitHub
    >>> release = github.fetch_latest_release("github", "spec-kit")
    >>>
    >>> # Download and extract template
    >>> asset = github.find_matching_asset(release, "claude", "sh")
    >>> zip_path = github.download_asset(asset, download_dir)
    >>> template.extract_template(zip_path, project_path)
    >>>
    >>> # Initialize git repository
    >>> git.init_repo(project_path)

See Also
--------
- :mod:`specify_cli.ops` : Operations/business logic layer
- :mod:`specify_cli.commands` : CLI commands layer
- :mod:`specify_cli.core` : Core infrastructure
"""

from __future__ import annotations

# GitHub operations
from .github import (
    GitHubError,
    RateLimitError,
    download_asset,
    fetch_latest_release,
    find_matching_asset,
    format_rate_limit_error,
    github_auth_headers,
    github_token,
    parse_rate_limit_headers,
)

# Git operations
from .git import (
    GitError,
    add_all,
    commit,
    get_current_branch,
    init_repo,
    is_repo,
)

# Template operations
from .template import (
    TemplateError,
    ensure_executable_scripts,
    extract_template,
    handle_vscode_settings,
    merge_json_files,
)

# Tool detection
from .tools import (
    CLAUDE_LOCAL_PATH,
    OPTIONAL_TOOLS,
    REQUIRED_TOOLS,
    check_required_tools,
    check_tool,
    get_tool_versions,
    which_tool,
)

# ggen wrapper
from .ggen import (
    GgenError,
    get_ggen_version,
    is_ggen_available,
    sync_specs,
)

__all__ = [
    # GitHub
    "github_token",
    "github_auth_headers",
    "parse_rate_limit_headers",
    "format_rate_limit_error",
    "fetch_latest_release",
    "find_matching_asset",
    "download_asset",
    "GitHubError",
    "RateLimitError",
    # Git
    "is_repo",
    "init_repo",
    "add_all",
    "commit",
    "get_current_branch",
    "GitError",
    # Template
    "extract_template",
    "ensure_executable_scripts",
    "merge_json_files",
    "handle_vscode_settings",
    "TemplateError",
    # Tools
    "check_tool",
    "which_tool",
    "check_required_tools",
    "get_tool_versions",
    "CLAUDE_LOCAL_PATH",
    "REQUIRED_TOOLS",
    "OPTIONAL_TOOLS",
    # ggen
    "is_ggen_available",
    "get_ggen_version",
    "sync_specs",
    "GgenError",
]
