"""
specify_cli.plugins.system - Plugin System Core
===============================================

Plugin discovery, loading, and lifecycle management.

This module provides:
- Plugin discovery from entry points and directories
- Dynamic plugin loading and unloading
- Plugin lifecycle management (initialize, activate, shutdown)
- Version compatibility checking
- Dependency resolution
- Hot-reloading support (development mode)

Architecture
-----------

    ┌────────────────────────────────────────────┐
    │  Plugin System (this module)               │
    │  • Discovery                               │
    │  • Loading/Unloading                       │
    │  • Lifecycle Management                    │
    │  • Dependency Resolution                   │
    └────────────────────────────────────────────┘
                       │
    ┌──────────────────▼─────────────────────────┐
    │  Plugin Instances                          │
    │  • Commands                                │
    │  • Integrations                            │
    │  • Data Sources                            │
    └────────────────────────────────────────────┘

Usage
-----
    from specify_cli.plugins.system import PluginManager

    manager = PluginManager()
    manager.discover_plugins()
    manager.load_all_plugins()

    # Get loaded plugins
    plugins = manager.get_loaded_plugins()

    # Unload plugin
    manager.unload_plugin("my-plugin")

See Also
--------
- :mod:`specify_cli.plugins.api` : Plugin protocols and interfaces
- :mod:`specify_cli.plugins.marketplace` : Plugin installation
"""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import sys
import traceback
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

from packaging.specifiers import SpecifierSet
from packaging.version import Version

from specify_cli.plugins.api import (
    BasePlugin,
    Plugin,
    PluginConfig,
    PluginDependencyError,
    PluginError,
    PluginInitError,
    PluginLoadError,
    PluginMetadata,
    PluginState,
    PluginVersionError,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class PluginRegistry:
    """Plugin registry for tracking discovered and loaded plugins.

    Attributes:
        _plugins: Discovered plugin metadata by name
        _loaded: Loaded plugin instances by name
        _states: Plugin states by name
        _dependencies: Plugin dependency graph
    """

    def __init__(self) -> None:
        """Initialize plugin registry."""
        self._plugins: dict[str, PluginMetadata] = {}
        self._loaded: dict[str, Plugin] = {}
        self._states: dict[str, PluginState] = {}
        self._dependencies: dict[str, list[str]] = defaultdict(list)

    def register(self, metadata: PluginMetadata) -> None:
        """Register plugin metadata.

        Args:
            metadata: Plugin metadata
        """
        self._plugins[metadata.name] = metadata
        self._states[metadata.name] = PluginState.DISCOVERED

        # Build dependency graph
        for dep in metadata.dependencies:
            self._dependencies[metadata.name].append(dep.name)

    def unregister(self, name: str) -> None:
        """Unregister plugin.

        Args:
            name: Plugin name
        """
        self._plugins.pop(name, None)
        self._loaded.pop(name, None)
        self._states.pop(name, None)
        self._dependencies.pop(name, None)

    def set_loaded(self, name: str, plugin: Plugin) -> None:
        """Mark plugin as loaded.

        Args:
            name: Plugin name
            plugin: Plugin instance
        """
        self._loaded[name] = plugin
        self._states[name] = PluginState.LOADED

    def set_state(self, name: str, state: PluginState) -> None:
        """Set plugin state.

        Args:
            name: Plugin name
            state: New plugin state
        """
        self._states[name] = state

    def get_metadata(self, name: str) -> PluginMetadata | None:
        """Get plugin metadata.

        Args:
            name: Plugin name

        Returns:
            Plugin metadata or None
        """
        return self._plugins.get(name)

    def get_plugin(self, name: str) -> Plugin | None:
        """Get loaded plugin instance.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._loaded.get(name)

    def get_state(self, name: str) -> PluginState | None:
        """Get plugin state.

        Args:
            name: Plugin name

        Returns:
            Plugin state or None
        """
        return self._states.get(name)

    def get_dependencies(self, name: str) -> list[str]:
        """Get plugin dependencies.

        Args:
            name: Plugin name

        Returns:
            List of dependency plugin names
        """
        return self._dependencies.get(name, [])

    def list_plugins(self) -> list[str]:
        """List all registered plugins.

        Returns:
            List of plugin names
        """
        return list(self._plugins.keys())

    def list_loaded(self) -> list[str]:
        """List loaded plugins.

        Returns:
            List of loaded plugin names
        """
        return list(self._loaded.keys())


class PluginLoader:
    """Plugin loader for dynamic loading and unloading.

    Attributes:
        _cli_version: Current CLI version
    """

    def __init__(self, cli_version: str = "0.0.25") -> None:
        """Initialize plugin loader.

        Args:
            cli_version: Current CLI version
        """
        self._cli_version = Version(cli_version)

    def load_from_entry_point(self, entry_point: str) -> Plugin:
        """Load plugin from entry point.

        Args:
            entry_point: Entry point string (module:attribute)

        Returns:
            Loaded plugin instance

        Raises:
            PluginLoadError: If loading fails
        """
        try:
            module_name, attr_name = entry_point.split(":")
            module = importlib.import_module(module_name)
            plugin_class = getattr(module, attr_name)

            # Instantiate plugin
            plugin = plugin_class()

            # Verify plugin implements Protocol
            if not isinstance(plugin, Plugin):
                raise PluginLoadError(
                    f"Plugin {entry_point} does not implement Plugin protocol"
                ) from None

            return plugin

        except ValueError as e:
            raise PluginLoadError(f"Invalid entry point format: {entry_point}") from e
        except (ImportError, AttributeError) as e:
            raise PluginLoadError(f"Failed to load plugin from {entry_point}: {e}") from e

    def load_from_file(self, file_path: Path) -> Plugin:
        """Load plugin from Python file.

        Args:
            file_path: Path to plugin Python file

        Returns:
            Loaded plugin instance

        Raises:
            PluginLoadError: If loading fails
        """
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", file_path)
            if spec is None or spec.loader is None:
                raise PluginLoadError(f"Cannot load spec from {file_path}")

            module = importlib.util.module_from_spec(spec)
            sys.modules["plugin_module"] = module
            spec.loader.exec_module(module)

            # Find Plugin class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BasePlugin) and attr is not BasePlugin:
                    plugin = attr()
                    return plugin

            raise PluginLoadError(f"No Plugin class found in {file_path}") from None

        except Exception as e:
            raise PluginLoadError(f"Failed to load plugin from {file_path}: {e}") from e

    def check_version_compatibility(self, metadata: PluginMetadata) -> bool:
        """Check if plugin is compatible with CLI version.

        Args:
            metadata: Plugin metadata

        Returns:
            True if compatible

        Raises:
            PluginVersionError: If incompatible
        """
        min_version = Version(metadata.min_cli_version)
        if metadata.max_cli_version != "*":
            max_version = Version(metadata.max_cli_version)
            compatible = min_version <= self._cli_version <= max_version
        else:
            compatible = self._cli_version >= min_version

        if not compatible:
            raise PluginVersionError(
                f"Plugin {metadata.name} requires CLI version "
                f"{metadata.min_cli_version}-{metadata.max_cli_version}, "
                f"but current version is {self._cli_version}"
            ) from None

        return True


class PluginManager:
    """Plugin manager for discovery, loading, and lifecycle management.

    Attributes:
        _registry: Plugin registry
        _loader: Plugin loader
        _config_dir: Plugin configuration directory
        _plugin_dirs: Additional plugin directories
        _hooks: Registered hook handlers
        _hot_reload: Enable hot-reloading
    """

    def __init__(
        self,
        config_dir: Path | None = None,
        plugin_dirs: list[Path] | None = None,
        cli_version: str = "0.0.25",
    ) -> None:
        """Initialize plugin manager.

        Args:
            config_dir: Plugin configuration directory
            plugin_dirs: Additional plugin directories to search
            cli_version: Current CLI version
        """
        self._registry = PluginRegistry()
        self._loader = PluginLoader(cli_version)
        self._config_dir = config_dir or Path.home() / ".specify" / "plugins"
        self._plugin_dirs = plugin_dirs or []
        self._hooks: dict[str, list[Callable[..., Any]]] = defaultdict(list)
        self._hot_reload = False

        # Ensure config directory exists
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def discover_plugins(self) -> list[PluginMetadata]:
        """Discover all available plugins.

        Discovers plugins from:
        1. Python entry points (installed packages)
        2. Plugin directories
        3. User plugin directory (~/.specify/plugins)

        Returns:
            List of discovered plugin metadata
        """
        discovered = []

        # Discover from entry points
        discovered.extend(self._discover_from_entry_points())

        # Discover from plugin directories
        for plugin_dir in self._plugin_dirs:
            discovered.extend(self._discover_from_directory(plugin_dir))

        # Discover from user plugin directory
        user_plugin_dir = self._config_dir / "user"
        if user_plugin_dir.exists():
            discovered.extend(self._discover_from_directory(user_plugin_dir))

        return discovered

    def _discover_from_entry_points(self) -> list[PluginMetadata]:
        """Discover plugins from entry points.

        Returns:
            List of discovered plugin metadata
        """
        discovered = []
        entry_points = importlib.metadata.entry_points()

        # Get specify-cli plugins
        specify_plugins = entry_points.select(group="specify_cli.plugins")

        for ep in specify_plugins:
            try:
                # Load plugin to get metadata
                plugin = self._loader.load_from_entry_point(f"{ep.value}")
                metadata = plugin.metadata()

                # Store entry point in metadata
                metadata.entry_point = f"{ep.value}"

                # Register plugin
                self._registry.register(metadata)
                discovered.append(metadata)

            except Exception:
                # Skip plugins that fail to load during discovery
                pass

        return discovered

    def _discover_from_directory(self, directory: Path) -> list[PluginMetadata]:
        """Discover plugins from directory.

        Args:
            directory: Directory to search

        Returns:
            List of discovered plugin metadata
        """
        discovered = []  # type: ignore[var-annotated]

        if not directory.exists():
            return discovered

        # Find all Python files
        for plugin_file in directory.glob("*.py"):
            try:
                # Load plugin to get metadata
                plugin = self._loader.load_from_file(plugin_file)
                metadata = plugin.metadata()

                # Store file path in metadata
                metadata.entry_point = str(plugin_file)

                # Register plugin
                self._registry.register(metadata)
                discovered.append(metadata)

            except Exception:
                # Skip plugins that fail to load during discovery
                pass

        return discovered

    def load_plugin(self, name: str, config: PluginConfig | None = None) -> Plugin:
        """Load and initialize plugin.

        Args:
            name: Plugin name
            config: Plugin configuration (uses default if None)

        Returns:
            Loaded plugin instance

        Raises:
            PluginLoadError: If plugin not found or loading fails
            PluginInitError: If initialization fails
        """
        # Get plugin metadata
        metadata = self._registry.get_metadata(name)
        if metadata is None:
            raise PluginLoadError(f"Plugin '{name}' not found") from None

        if self._registry.get_plugin(name) is not None:
            return self._registry.get_plugin(name)  # type: ignore[return-value]

        # Check version compatibility
        self._loader.check_version_compatibility(metadata)

        # Check dependencies
        self._check_dependencies(metadata)

        # Load plugin
        self._registry.set_state(name, PluginState.LOADING)

        try:
            if metadata.entry_point.endswith(".py"):
                # Load from file
                plugin = self._loader.load_from_file(Path(metadata.entry_point))
            else:
                # Load from entry point
                plugin = self._loader.load_from_entry_point(metadata.entry_point)

            self._registry.set_loaded(name, plugin)

            # Initialize plugin
            plugin_config = config or PluginConfig()
            self._registry.set_state(name, PluginState.INITIALIZING)
            plugin.initialize(plugin_config)

            self._registry.set_state(name, PluginState.ACTIVE)

            # Call on_plugin_load hook
            self._call_hook("on_plugin_load", plugin_name=name, metadata=metadata)

            return plugin

        except Exception as e:
            self._registry.set_state(name, PluginState.ERROR)
            raise PluginInitError(f"Failed to initialize plugin '{name}': {e}") from e

    def unload_plugin(self, name: str) -> None:
        """Unload plugin.

        Args:
            name: Plugin name

        Raises:
            PluginError: If plugin not loaded or unloading fails
        """
        plugin = self._registry.get_plugin(name)
        if plugin is None:
            raise PluginError(f"Plugin '{name}' not loaded") from None

        self._registry.set_state(name, PluginState.UNLOADING)

        try:
            # Call on_plugin_unload hook
            self._call_hook("on_plugin_unload", plugin_name=name)

            # Shutdown plugin
            plugin.shutdown()

            # Remove from loaded
            self._registry.unregister(name)

        except Exception as e:
            self._registry.set_state(name, PluginState.ERROR)
            raise PluginError(f"Failed to unload plugin '{name}': {e}") from e

    def load_all_plugins(self, auto_load_only: bool = True) -> list[str]:
        """Load all discovered plugins.

        Args:
            auto_load_only: Only load plugins with auto_load=True

        Returns:
            List of loaded plugin names
        """
        loaded = []

        for name in self._registry.list_plugins():
            try:
                # Load plugin configuration
                config = self._load_plugin_config(name)

                if not config.enabled:
                    continue
                if auto_load_only and not config.auto_load:
                    continue

                # Load plugin
                self.load_plugin(name, config)
                loaded.append(name)

            except Exception as e:
                # Log error but continue loading other plugins
                print(f"Failed to load plugin '{name}': {e}")
                traceback.print_exc()

        return loaded

    def unload_all_plugins(self) -> None:
        """Unload all loaded plugins."""
        for name in list(self._registry.list_loaded()):
            try:
                self.unload_plugin(name)
            except Exception as e:
                print(f"Failed to unload plugin '{name}': {e}")

    def get_plugin(self, name: str) -> Plugin | None:
        """Get loaded plugin.

        Args:
            name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._registry.get_plugin(name)

    def get_loaded_plugins(self) -> dict[str, Plugin]:
        """Get all loaded plugins.

        Returns:
            Dict mapping plugin names to instances
        """
        return {name: self._registry.get_plugin(name) for name in self._registry.list_loaded()}  # type: ignore[misc]

    def get_plugin_metadata(self, name: str) -> PluginMetadata | None:
        """Get plugin metadata.

        Args:
            name: Plugin name

        Returns:
            Plugin metadata or None
        """
        return self._registry.get_metadata(name)

    def list_plugins(self) -> list[tuple[str, PluginState]]:
        """List all plugins with their states.

        Returns:
            List of (name, state) tuples
        """
        return [
            (name, self._registry.get_state(name) or PluginState.DISCOVERED)
            for name in self._registry.list_plugins()
        ]

    def register_hook(self, hook_name: str, handler: Callable[..., Any][..., Any][..., Any]) -> None:  # type: ignore[valid-type]
        """Register hook handler.

        Args:
            hook_name: Hook name
            handler: Hook handler function
        """
        self._hooks[hook_name].append(handler)

    def _call_hook(self, hook_name: str, **kwargs: Any) -> list[Any]:
        """Call all handlers for hook.

        Args:
            hook_name: Hook name
            **kwargs: Hook arguments

        Returns:
            List of handler return values
        """
        results = []
        for handler in self._hooks[hook_name]:
            try:
                result = handler(**kwargs)
                results.append(result)
            except Exception as e:
                print(f"Hook handler error in {hook_name}: {e}")
                traceback.print_exc()
        return results

    def _check_dependencies(self, metadata: PluginMetadata) -> None:
        """Check if plugin dependencies are satisfied.

        Args:
            metadata: Plugin metadata

        Raises:
            PluginDependencyError: If dependencies not satisfied
        """
        for dep in metadata.dependencies:
            dep_plugin = self._registry.get_plugin(dep.name)
            if dep_plugin is None and not dep.optional:
                raise PluginDependencyError(
                    f"Plugin '{metadata.name}' requires '{dep.name}' which is not loaded"
                ) from None

            # Check version compatibility
            if dep_plugin is not None and dep.version_spec != "*":
                dep_metadata = self._registry.get_metadata(dep.name)
                if dep_metadata is not None:
                    dep_version = Version(dep_metadata.version)
                    spec = SpecifierSet(dep.version_spec)
                    if dep_version not in spec:
                        raise PluginDependencyError(
                            f"Plugin '{metadata.name}' requires '{dep.name}' "
                            f"{dep.version_spec}, but {dep_metadata.version} is loaded"
                        ) from None

    def _load_plugin_config(self, name: str) -> PluginConfig:
        """Load plugin configuration.

        Args:
            name: Plugin name

        Returns:
            Plugin configuration (defaults if not found)
        """
        config_file = self._config_dir / f"{name}.json"
        if config_file.exists():
            import json

            with open(config_file) as f:
                data = json.load(f)
                return PluginConfig(**data)
        return PluginConfig()

    def enable_hot_reload(self) -> None:
        """Enable hot-reloading for development.

        Note: This is experimental and may cause issues.
        """
        self._hot_reload = True

    def disable_hot_reload(self) -> None:
        """Disable hot-reloading."""
        self._hot_reload = False


__all__ = [
    "PluginLoader",
    "PluginManager",
    "PluginRegistry",
]
