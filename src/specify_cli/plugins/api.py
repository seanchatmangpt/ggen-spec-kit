"""
specify_cli.plugins.api - Plugin API and Protocols
==================================================

Plugin interface definitions, protocols, and base classes for extending the CLI.

This module provides:
- Plugin protocol definitions
- Hook system for extending functionality
- Plugin metadata and configuration schemas
- Base classes for common plugin types

Architecture
-----------

    ┌────────────────────────────────────────────┐
    │  Plugin API (this module)                  │
    │  • Protocol definitions                    │
    │  • Hook interfaces                         │
    │  • Configuration schemas                   │
    │  • Base classes                            │
    └────────────────────────────────────────────┘
                       │
    ┌──────────────────▼─────────────────────────┐
    │  Plugin Implementations                     │
    │  • Custom commands                         │
    │  • Integrations                            │
    │  • Data sources                            │
    │  • Transformations                         │
    └────────────────────────────────────────────┘

Usage
-----
    from specify_cli.plugins.api import Plugin, PluginMetadata, Hook

    class MyPlugin(Plugin):
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="my-plugin",
                version="1.0.0",
                description="My awesome plugin",
            )

        def initialize(self) -> None:
            # Plugin initialization logic
            pass

See Also
--------
- :mod:`specify_cli.plugins.system` : Plugin loading and lifecycle
- :mod:`specify_cli.plugins.marketplace` : Plugin installation
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    import typer


# Type variables
T = TypeVar("T")
HookCallable = Callable[..., Any | Awaitable[Any]]


class PluginType(str, Enum):
    """Plugin type enumeration.

    Defines the category of plugin functionality:
    - COMMAND: Adds new CLI commands
    - INTEGRATION: Integrates with external services (GitHub, Slack, etc.)
    - DATA_SOURCE: Provides data from external sources
    - TRANSFORMER: Transforms data or files
    - REPORTER: Generates reports or documentation
    - HOOK: Extends existing functionality via hooks
    - COMPOSITE: Combines multiple plugin types
    """

    COMMAND = "command"
    INTEGRATION = "integration"
    DATA_SOURCE = "data_source"
    TRANSFORMER = "transformer"
    REPORTER = "reporter"
    HOOK = "hook"
    COMPOSITE = "composite"


class PluginState(str, Enum):
    """Plugin lifecycle state.

    States:
    - DISCOVERED: Found but not loaded
    - LOADING: Currently being loaded
    - LOADED: Successfully loaded
    - INITIALIZING: Running initialization
    - ACTIVE: Fully initialized and active
    - ERROR: Failed to load or initialize
    - DISABLED: Explicitly disabled by user
    - UNLOADING: Currently being unloaded
    - UNLOADED: Successfully unloaded
    """

    DISCOVERED = "discovered"
    LOADING = "loading"
    LOADED = "loaded"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"
    UNLOADING = "unloading"
    UNLOADED = "unloaded"


@dataclass(frozen=True)
class PluginDependency:
    """Plugin dependency specification.

    Attributes:
        name: Dependency plugin name
        version_spec: Version specification (e.g., ">=1.0.0,<2.0.0")
        optional: Whether dependency is optional
        extras: Optional extras to install
    """

    name: str
    version_spec: str = "*"
    optional: bool = False
    extras: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PluginPermission:
    """Plugin permission definition.

    Attributes:
        name: Permission identifier
        description: Human-readable description
        required: Whether permission is required for plugin
        dangerous: Whether permission is potentially dangerous
    """

    name: str
    description: str
    required: bool = True
    dangerous: bool = False


class PluginPermissions:
    """Standard plugin permissions."""

    # File system permissions
    READ_FILES = PluginPermission(
        "read_files", "Read files from the filesystem", required=False
    )
    WRITE_FILES = PluginPermission(
        "write_files", "Write files to the filesystem", required=False, dangerous=True
    )
    EXECUTE_FILES = PluginPermission(
        "execute_files", "Execute files or commands", required=False, dangerous=True
    )

    # Network permissions
    NETWORK_ACCESS = PluginPermission(
        "network_access", "Make network requests", required=False
    )

    # System permissions
    SUBPROCESS = PluginPermission(
        "subprocess", "Execute subprocesses", required=False, dangerous=True
    )
    ENVIRONMENT = PluginPermission(
        "environment", "Read/modify environment variables", required=False
    )

    # Plugin system permissions
    PLUGIN_COMMUNICATION = PluginPermission(
        "plugin_communication", "Communicate with other plugins", required=False
    )
    HOOK_REGISTRATION = PluginPermission(
        "hook_registration", "Register hooks in the system", required=False
    )


@dataclass
class PluginMetadata:
    """Plugin metadata and configuration.

    Attributes:
        name: Unique plugin identifier (kebab-case)
        version: Semantic version string
        description: Short description of plugin functionality
        author: Plugin author name
        author_email: Plugin author email
        homepage: Plugin homepage URL
        repository: Source code repository URL
        license: License identifier (SPDX)
        plugin_type: Type of plugin (command, integration, etc.)
        entry_point: Python entry point (module:attribute)
        dependencies: Plugin dependencies
        python_dependencies: Python package dependencies
        permissions: Required permissions
        config_schema: JSON schema for plugin configuration
        tags: Searchable tags
        min_cli_version: Minimum CLI version required
        max_cli_version: Maximum CLI version supported
        experimental: Whether plugin is experimental
        deprecated: Whether plugin is deprecated
    """

    name: str
    version: str
    description: str
    author: str = ""
    author_email: str = ""
    homepage: str = ""
    repository: str = ""
    license: str = "MIT"
    plugin_type: PluginType = PluginType.COMMAND
    entry_point: str = ""
    dependencies: list[PluginDependency] = field(default_factory=list)
    python_dependencies: list[str] = field(default_factory=list)
    permissions: list[PluginPermission] = field(default_factory=list)
    config_schema: dict[str, Any] | None = None
    tags: list[str] = field(default_factory=list)
    min_cli_version: str = "0.0.1"
    max_cli_version: str = "*"
    experimental: bool = False
    deprecated: bool = False


@dataclass
class PluginConfig:
    """Plugin configuration.

    Attributes:
        enabled: Whether plugin is enabled
        auto_load: Whether to auto-load on startup
        priority: Load priority (higher = earlier)
        config: Plugin-specific configuration dict
        hot_reload: Enable hot-reloading in dev mode
    """

    enabled: bool = True
    auto_load: bool = True
    priority: int = 100
    config: dict[str, Any] = field(default_factory=dict)
    hot_reload: bool = False


@dataclass
class HookSpec:
    """Hook specification.

    Attributes:
        name: Hook identifier
        description: Hook description
        parameters: Expected parameters dict
        return_type: Expected return type
        async_hook: Whether hook is async
        multi_return: Whether to collect returns from all handlers
    """

    name: str
    description: str
    parameters: dict[str, type] = field(default_factory=dict)
    return_type: type | None = None
    async_hook: bool = False
    multi_return: bool = False


class PluginHooks:
    """Standard plugin hooks.

    Hooks are called at specific points in the CLI lifecycle.
    """

    # Lifecycle hooks
    BEFORE_COMMAND = HookSpec(
        "before_command",
        "Called before any command execution",
        {"command_name": str, "args": dict},
    )

    AFTER_COMMAND = HookSpec(
        "after_command",
        "Called after command execution",
        {"command_name": str, "args": dict, "result": Any},
    )

    ON_ERROR = HookSpec(
        "on_error",
        "Called when an error occurs",
        {"error": Exception, "context": dict},
    )

    # Initialization hooks
    ON_STARTUP = HookSpec(
        "on_startup",
        "Called when CLI starts up",
        {},
    )

    ON_SHUTDOWN = HookSpec(
        "on_shutdown",
        "Called when CLI shuts down",
        {},
    )

    # Plugin lifecycle hooks
    ON_PLUGIN_LOAD = HookSpec(
        "on_plugin_load",
        "Called when a plugin is loaded",
        {"plugin_name": str, "metadata": PluginMetadata},
    )

    ON_PLUGIN_UNLOAD = HookSpec(
        "on_plugin_unload",
        "Called when a plugin is unloaded",
        {"plugin_name": str},
    )


@runtime_checkable
class Plugin(Protocol):
    """Base plugin protocol.

    All plugins must implement this protocol to be discovered and loaded
    by the plugin system.
    """

    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata.

        Returns:
            PluginMetadata: Plugin metadata and configuration
        """
        ...

    @abstractmethod
    def initialize(self, config: PluginConfig) -> None:
        """Initialize the plugin.

        Args:
            config: Plugin configuration

        Raises:
            PluginError: If initialization fails
        """
        ...

    def shutdown(self) -> None:
        """Shutdown the plugin.

        Called when plugin is being unloaded. Default implementation does nothing.
        """

    def health_check(self) -> bool:
        """Check plugin health.

        Returns:
            bool: True if plugin is healthy
        """
        return True


@runtime_checkable
class CommandPlugin(Plugin, Protocol):
    """Plugin that provides CLI commands.

    Command plugins add new Typer commands to the CLI.
    """

    @abstractmethod
    def get_commands(self) -> dict[str, typer.Typer]:
        """Get plugin commands.

        Returns:
            dict: Mapping of command names to Typer apps
        """
        ...


@runtime_checkable
class IntegrationPlugin(Plugin, Protocol):
    """Plugin that integrates with external services.

    Integration plugins provide connections to external services like
    GitHub, Slack, Jira, etc.
    """

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to external service.

        Raises:
            PluginError: If connection fails
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from external service."""
        ...

    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to external service.

        Returns:
            bool: True if connected
        """
        ...


@runtime_checkable
class DataSourcePlugin(Plugin, Protocol):
    """Plugin that provides data from external sources.

    Data source plugins fetch and provide data from external sources.
    """

    @abstractmethod
    def fetch_data(self, query: dict[str, Any]) -> Any:
        """Fetch data from source.

        Args:
            query: Query parameters

        Returns:
            Fetched data

        Raises:
            PluginError: If fetch fails
        """
        ...


@runtime_checkable
class TransformerPlugin(Plugin, Protocol):
    """Plugin that transforms data or files.

    Transformer plugins apply transformations to data or files.
    """

    @abstractmethod
    def transform(self, input_data: Any, options: dict[str, Any] | None = None) -> Any:
        """Transform input data.

        Args:
            input_data: Data to transform
            options: Transformation options

        Returns:
            Transformed data

        Raises:
            PluginError: If transformation fails
        """
        ...


@runtime_checkable
class ReporterPlugin(Plugin, Protocol):
    """Plugin that generates reports.

    Reporter plugins generate reports or documentation from data.
    """

    @abstractmethod
    def generate_report(
        self, data: Any, output_path: Path, options: dict[str, Any] | None = None
    ) -> Path:
        """Generate report.

        Args:
            data: Data to report on
            output_path: Output file path
            options: Report generation options

        Returns:
            Path to generated report

        Raises:
            PluginError: If report generation fails
        """
        ...


@runtime_checkable
class HookPlugin(Plugin, Protocol):
    """Plugin that extends functionality via hooks.

    Hook plugins register handlers for system hooks.
    """

    @abstractmethod
    def get_hooks(self) -> dict[str, HookCallable]:
        """Get plugin hooks.

        Returns:
            dict: Mapping of hook names to handler functions
        """
        ...


class BasePlugin(ABC):
    """Base plugin implementation.

    Provides common functionality for plugin implementations.

    Attributes:
        _config: Plugin configuration
        _state: Current plugin state
        _error: Last error message if in error state
    """

    def __init__(self) -> None:
        """Initialize base plugin."""
        self._config: PluginConfig | None = None
        self._state: PluginState = PluginState.DISCOVERED
        self._error: str | None = None

    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        ...

    def initialize(self, config: PluginConfig) -> None:
        """Initialize the plugin.

        Args:
            config: Plugin configuration
        """
        self._config = config
        self._state = PluginState.INITIALIZING
        try:
            self._initialize_impl()
            self._state = PluginState.ACTIVE
        except Exception as e:
            self._state = PluginState.ERROR
            self._error = str(e)
            raise

    @abstractmethod
    def _initialize_impl(self) -> None:
        """Plugin-specific initialization logic."""
        ...

    def shutdown(self) -> None:
        """Shutdown the plugin."""
        self._state = PluginState.UNLOADING
        self._shutdown_impl()
        self._state = PluginState.UNLOADED

    def _shutdown_impl(self) -> None:
        """Plugin-specific shutdown logic."""

    def health_check(self) -> bool:
        """Check plugin health."""
        return self._state == PluginState.ACTIVE

    @property
    def config(self) -> PluginConfig | None:
        """Get plugin configuration."""
        return self._config

    @property
    def state(self) -> PluginState:
        """Get current plugin state."""
        return self._state

    @property
    def error(self) -> str | None:
        """Get last error message."""
        return self._error


class PluginError(Exception):
    """Base exception for plugin errors."""



class PluginLoadError(PluginError):
    """Exception raised when plugin fails to load."""



class PluginInitError(PluginError):
    """Exception raised when plugin fails to initialize."""



class PluginDependencyError(PluginError):
    """Exception raised when plugin dependency is missing or incompatible."""



class PluginPermissionError(PluginError):
    """Exception raised when plugin lacks required permission."""



class PluginVersionError(PluginError):
    """Exception raised when plugin version is incompatible."""



__all__ = [
    "BasePlugin",
    "CommandPlugin",
    "DataSourcePlugin",
    "HookCallable",
    "HookPlugin",
    "HookSpec",
    "IntegrationPlugin",
    "Plugin",
    "PluginConfig",
    "PluginDependency",
    "PluginDependencyError",
    "PluginError",
    "PluginHooks",
    "PluginInitError",
    "PluginLoadError",
    "PluginMetadata",
    "PluginPermission",
    "PluginPermissionError",
    "PluginPermissions",
    "PluginState",
    "PluginType",
    "PluginVersionError",
    "ReporterPlugin",
    "TransformerPlugin",
]
