"""
specify_cli.plugins.integration - CLI Integration
=================================================

Integration of plugin system with the main CLI application.

This module provides:
- Plugin command registration in main CLI
- Automatic plugin discovery and loading
- Plugin lifecycle hooks
- Command injection

Usage
-----
    from specify_cli.plugins.integration import register_plugins

    app = typer.Typer()
    register_plugins(app)

See Also
--------
- :mod:`specify_cli.plugins.system` : Plugin system
- :mod:`specify_cli.app` : Main CLI application
"""

from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

from rich.console import Console

from specify_cli.plugins import CommandPlugin, PluginManager

if TYPE_CHECKING:
    import typer

console = Console()


def register_plugins(app: typer.Typer, auto_load: bool = True) -> PluginManager:
    """Register plugins with the main CLI application.

    This function:
    1. Creates a plugin manager
    2. Discovers available plugins
    3. Loads plugins with auto_load=True
    4. Registers plugin commands with the main CLI

    Args:
        app: Main Typer application
        auto_load: Whether to auto-load plugins

    Returns:
        PluginManager instance
    """
    # Create plugin manager
    manager = PluginManager()

    try:
        # Discover plugins
        discovered = manager.discover_plugins()

        if discovered:
            console.print(
                f"[dim]Discovered {len(discovered)} plugin(s)[/dim]",
                style="dim",
            )

        # Load plugins
        if auto_load:
            loaded = manager.load_all_plugins(auto_load_only=True)

            # Register plugin commands
            for plugin_name in loaded:
                plugin = manager.get_plugin(plugin_name)
                if isinstance(plugin, CommandPlugin):
                    commands = plugin.get_commands()

                    for cmd_name, cmd_app in commands.items():
                        # Register command with main app
                        app.add_typer(cmd_app, name=cmd_name)

                        console.print(
                            f"[dim]Registered plugin command: {cmd_name}[/dim]",
                            style="dim",
                        )

    except Exception as e:
        # Don't fail CLI startup on plugin errors
        console.print(
            f"[yellow]Warning:[/yellow] Plugin system initialization failed: {e}",
            style="dim",
        )
        traceback.print_exc()

    return manager


def initialize_plugin_hooks(manager: PluginManager) -> None:
    """Initialize plugin hooks.

    Registers standard CLI lifecycle hooks.

    Args:
        manager: Plugin manager
    """
    # Register startup hook
    def on_startup() -> None:
        console.print("[dim]CLI started with plugin support[/dim]")

    manager.register_hook("on_startup", on_startup)

    # Register shutdown hook
    def on_shutdown() -> None:
        console.print("[dim]Shutting down plugins...[/dim]")
        manager.unload_all_plugins()

    manager.register_hook("on_shutdown", on_shutdown)


__all__ = [
    "register_plugins",
    "initialize_plugin_hooks",
]
