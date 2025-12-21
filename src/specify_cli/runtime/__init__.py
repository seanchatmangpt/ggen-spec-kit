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

# ggen wrapper
from .ggen import (
    GgenError,
    get_ggen_version,
    is_ggen_available,
    sync_specs,
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

__all__ = [
    "CLAUDE_LOCAL_PATH",
    "OPTIONAL_TOOLS",
    "REQUIRED_TOOLS",
    "GgenError",
    "GitError",
    "GitHubError",
    "RateLimitError",
    "TemplateError",
    "add_all",
    "check_required_tools",
    # Tools
    "check_tool",
    "commit",
    "download_asset",
    "ensure_executable_scripts",
    # Template
    "extract_template",
    "fetch_latest_release",
    "find_matching_asset",
    "format_rate_limit_error",
    "get_current_branch",
    "get_ggen_version",
    "get_tool_versions",
    "github_auth_headers",
    # GitHub
    "github_token",
    "handle_vscode_settings",
    "init_repo",
    # ggen
    "is_ggen_available",
    # Git
    "is_repo",
    "merge_json_files",
    "parse_rate_limit_headers",
    "sync_specs",
    "which_tool",
]
