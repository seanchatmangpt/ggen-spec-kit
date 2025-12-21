"""
specify_cli.core.config - Configuration Management
===================================================

Configuration utilities for specify-cli with environment variable and file support.

This module provides a unified configuration system that supports:
- Environment variables (highest priority)
- TOML configuration files (~/.config/specify/config.toml)
- Default values (lowest priority)

Key Features
-----------
* **Environment Priority**: Environment variables override file config
* **TOML Support**: User-friendly TOML configuration files
* **Type Safe**: Dataclass-based configuration with validation
* **XDG Compliance**: Follows XDG Base Directory Specification

Examples
--------
    >>> from specify_cli.core.config import get_config, env_or
    >>>
    >>> # Get environment variable with default
    >>> value = env_or("MY_VAR", "default_value")
    >>>
    >>> # Get full configuration
    >>> config = get_config()
    >>> print(config.cache_dir)

Environment Variables
--------------------
- SPECIFY_CACHE_DIR : Override default cache directory
- SPECIFY_CONFIG_DIR : Override default config directory
- SPECIFY_DRY : Enable dry-run mode for commands
- SPECIFY_QUIET : Suppress command output
- SPECIFY_OTEL_ENABLED : Enable/disable OpenTelemetry

See Also
--------
- :mod:`specify_cli.core.cache` : Caching utilities
- :mod:`specify_cli.core.telemetry` : Telemetry configuration
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib  # type: ignore[import-not-found,no-redef]
except ImportError:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]

__all__ = [
    "SpecifyConfig",
    "env_or",
    "get_cache_dir",
    "get_config",
    "get_config_dir",
]


def env_or(key: str, default: str = "") -> str:
    """
    Get environment variable value or return default.

    Parameters
    ----------
    key : str
        Environment variable name.
    default : str, optional
        Default value if variable is not set. Default is empty string.

    Returns
    -------
    str
        Environment variable value or default.
    """
    return os.getenv(key, default)


def get_cache_dir() -> Path:
    """
    Get the cache directory path.

    Uses SPECIFY_CACHE_DIR if set, otherwise uses platform default:
    - Linux/macOS: ~/.cache/specify
    - Windows: %LOCALAPPDATA%/specify/cache

    Returns
    -------
    Path
        Path to cache directory.
    """
    if custom := env_or("SPECIFY_CACHE_DIR"):
        return Path(custom)

    # Use platformdirs if available, otherwise fallback
    try:
        from platformdirs import user_cache_dir

        return Path(user_cache_dir("specify", "specify-cli"))
    except ImportError:
        # Fallback to XDG or home directory
        xdg_cache = env_or("XDG_CACHE_HOME", str(Path.home() / ".cache"))
        return Path(xdg_cache) / "specify"


def get_config_dir() -> Path:
    """
    Get the configuration directory path.

    Uses SPECIFY_CONFIG_DIR if set, otherwise uses platform default:
    - Linux/macOS: ~/.config/specify
    - Windows: %APPDATA%/specify

    Returns
    -------
    Path
        Path to configuration directory.
    """
    if custom := env_or("SPECIFY_CONFIG_DIR"):
        return Path(custom)

    # Use platformdirs if available, otherwise fallback
    try:
        from platformdirs import user_config_dir

        return Path(user_config_dir("specify", "specify-cli"))
    except ImportError:
        # Fallback to XDG or home directory
        xdg_config = env_or("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        return Path(xdg_config) / "specify"


@dataclass
class SpecifyConfig:
    """
    Main configuration dataclass for specify-cli.

    Attributes
    ----------
    cache_dir : Path
        Directory for caching data.
    config_dir : Path
        Directory for configuration files.
    dry_run : bool
        If True, commands show what they would do without executing.
    quiet : bool
        If True, suppress non-essential output.
    otel_enabled : bool
        If True, OpenTelemetry instrumentation is active.
    github_token : str
        GitHub API token for authenticated requests.
    default_ai_assistant : str
        Default AI assistant type for new projects.
    """

    cache_dir: Path = field(default_factory=get_cache_dir)
    config_dir: Path = field(default_factory=get_config_dir)
    dry_run: bool = False
    quiet: bool = False
    otel_enabled: bool = True
    github_token: str = ""
    default_ai_assistant: str = "claude"

    @classmethod
    def from_env_and_file(cls) -> SpecifyConfig:
        """
        Load configuration from environment and config file.

        Priority (highest to lowest):
        1. Environment variables
        2. Config file (~/.config/specify/config.toml)
        3. Default values

        Returns
        -------
        SpecifyConfig
            Loaded configuration.
        """
        # Start with defaults
        config = cls()

        # Load from file if exists
        config_file = config.config_dir / "config.toml"
        if config_file.exists():
            try:
                with open(config_file, "rb") as f:
                    file_config = tomllib.load(f)

                # Apply file settings
                if "cache_dir" in file_config:
                    config.cache_dir = Path(file_config["cache_dir"])
                if "dry_run" in file_config:
                    config.dry_run = bool(file_config["dry_run"])
                if "quiet" in file_config:
                    config.quiet = bool(file_config["quiet"])
                if "otel_enabled" in file_config:
                    config.otel_enabled = bool(file_config["otel_enabled"])
                if "github_token" in file_config:
                    config.github_token = str(file_config["github_token"])
                if "default_ai_assistant" in file_config:
                    config.default_ai_assistant = str(file_config["default_ai_assistant"])
            except Exception:
                # Silently ignore config file errors
                pass

        # Environment overrides (highest priority)
        if cache_dir := env_or("SPECIFY_CACHE_DIR"):
            config.cache_dir = Path(cache_dir)
        if config_dir := env_or("SPECIFY_CONFIG_DIR"):
            config.config_dir = Path(config_dir)
        if env_or("SPECIFY_DRY") == "1":
            config.dry_run = True
        if env_or("SPECIFY_QUIET"):
            config.quiet = True
        if env_or("SPECIFY_OTEL_ENABLED", "true").lower() in ("false", "0", "no"):
            config.otel_enabled = False
        if token := env_or("GITHUB_TOKEN") or env_or("GH_TOKEN"):
            config.github_token = token
        if ai := env_or("SPECIFY_DEFAULT_AI"):
            config.default_ai_assistant = ai

        return config


# Cached global config instance
_config: SpecifyConfig | None = None


def get_config() -> SpecifyConfig:
    """
    Get the global configuration instance.

    Configuration is loaded once and cached. To reload, set
    `specify_cli.core.config._config = None` and call again.

    Returns
    -------
    SpecifyConfig
        Global configuration instance.
    """
    global _config
    if _config is None:
        _config = SpecifyConfig.from_env_and_file()
    return _config
