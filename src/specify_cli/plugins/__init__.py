"""
specify_cli.plugins - Plugin System
===================================

Hyper-advanced plugin system for CLI extensibility with dynamic loading,
marketplace integration, and comprehensive plugin lifecycle management.

This package provides:
- Plugin discovery and loading (entry points, directories)
- Dynamic command registration
- Plugin lifecycle management (initialize, activate, shutdown)
- Version compatibility checking
- Plugin marketplace integration
- Install/update/uninstall operations
- Dependency resolution
- Plugin hot-reloading (development mode)
- Event system and hooks
- Plugin permissions and sandboxing

Architecture
-----------

    ┌────────────────────────────────────────────┐
    │  Plugin System                             │
    │  ┌──────────────────────────────────────┐  │
    │  │  API Layer                           │  │
    │  │  • Protocols & Interfaces            │  │
    │  │  • Base Classes                      │  │
    │  └──────────────────────────────────────┘  │
    │  ┌──────────────────────────────────────┐  │
    │  │  System Layer                        │  │
    │  │  • Discovery & Loading               │  │
    │  │  • Lifecycle Management              │  │
    │  └──────────────────────────────────────┘  │
    │  ┌──────────────────────────────────────┐  │
    │  │  Marketplace Layer                   │  │
    │  │  • Install/Update/Uninstall          │  │
    │  │  • Repository Integration            │  │
    │  └──────────────────────────────────────┘  │
    └────────────────────────────────────────────┘

Usage
-----

Creating a Plugin:

    from specify_cli.plugins.api import BasePlugin, PluginMetadata, PluginConfig

    class MyPlugin(BasePlugin):
        def metadata(self) -> PluginMetadata:
            return PluginMetadata(
                name="my-plugin",
                version="1.0.0",
                description="My awesome plugin",
            )

        def _initialize_impl(self) -> None:
            print("Plugin initialized!")

Using Plugin Manager:

    from specify_cli.plugins import PluginManager

    manager = PluginManager()
    manager.discover_plugins()
    manager.load_all_plugins()

Installing Plugins:

    from specify_cli.plugins import PluginMarketplace

    marketplace = PluginMarketplace()
    marketplace.install("specify-plugin-github")
    marketplace.update("specify-plugin-github")
    marketplace.uninstall("specify-plugin-github")

See Also
--------
- :mod:`specify_cli.plugins.api` : Plugin protocols and base classes
- :mod:`specify_cli.plugins.system` : Plugin loading and lifecycle
- :mod:`specify_cli.plugins.marketplace` : Plugin installation
"""

from .api import (
    BasePlugin,
    CommandPlugin,
    DataSourcePlugin,
    HookPlugin,
    IntegrationPlugin,
    Plugin,
    PluginConfig,
    PluginDependency,
    PluginError,
    PluginHooks,
    PluginMetadata,
    PluginPermission,
    PluginPermissions,
    PluginState,
    PluginType,
    ReporterPlugin,
    TransformerPlugin,
)
from .marketplace import PluginMarketplace, PluginPackage
from .system import PluginManager

__version__ = "1.0.0"

__all__ = [
    "BasePlugin",
    "CommandPlugin",
    "DataSourcePlugin",
    "HookPlugin",
    "IntegrationPlugin",
    "Plugin",
    "PluginConfig",
    "PluginDependency",
    "PluginError",
    "PluginHooks",
    "PluginManager",
    "PluginMarketplace",
    "PluginMetadata",
    "PluginPackage",
    "PluginPermission",
    "PluginPermissions",
    "PluginState",
    "PluginType",
    "ReporterPlugin",
    "TransformerPlugin",
]
