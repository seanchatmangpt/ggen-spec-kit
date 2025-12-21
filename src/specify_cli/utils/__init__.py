"""Utility modules for Specify CLI."""

from .commands import CLAUDE_LOCAL_PATH, check_tool, run_command
from .constants import AGENT_CONFIG, BANNER, SCRIPT_TYPE_CHOICES, TAGLINE
from .progress import StepTracker, get_key, select_with_arrows
from .templates import (
    download_and_extract_template,
    ensure_executable_scripts,
    handle_vscode_settings,
    merge_json_files,
)

__all__ = [
    # Constants
    "AGENT_CONFIG",
    "BANNER",
    "CLAUDE_LOCAL_PATH",
    "SCRIPT_TYPE_CHOICES",
    "TAGLINE",
    # Progress
    "StepTracker",
    "check_tool",
    "download_and_extract_template",
    "ensure_executable_scripts",
    "get_key",
    # Templates
    "handle_vscode_settings",
    "merge_json_files",
    # Commands
    "run_command",
    "select_with_arrows",
]
