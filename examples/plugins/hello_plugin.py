"""
Example Plugin: Hello Command
==============================

A simple command plugin that adds a "hello" command to the CLI.

This demonstrates:
- Command plugin implementation
- Basic plugin structure
- Command registration
- Typer integration

Installation:
    Copy this file to ~/.specify/plugins/user/hello_plugin.py

Usage:
    $ specify hello --name World
    Hello, World!
"""

from __future__ import annotations

import typer
from rich.console import Console

from specify_cli.plugins.api import (
    BasePlugin,
    CommandPlugin,
    PluginConfig,
    PluginMetadata,
    PluginType,
)

console = Console()


class HelloPlugin(BasePlugin, CommandPlugin):
    """Hello command plugin.

    Adds a simple "hello" command to demonstrate plugin functionality.
    """

    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="hello-plugin",
            version="1.0.0",
            description="Simple hello world command plugin",
            author="Specify Team",
            author_email="info@chatmangpt.com",
            plugin_type=PluginType.COMMAND,
            tags=["example", "command", "demo"],
            min_cli_version="0.0.1",
        )

    def _initialize_impl(self) -> None:
        """Initialize the plugin."""
        console.print("[green]✓[/green] Hello plugin initialized")

    def get_commands(self) -> dict[str, typer.Typer]:
        """Get plugin commands.

        Returns:
            Dictionary mapping command names to Typer apps
        """
        # Create Typer app for hello command
        app = typer.Typer(
            name="hello",
            help="Say hello to someone",
            add_completion=False,
        )

        @app.command()
        def hello(
            name: str = typer.Option(
                "World",
                "--name",
                "-n",
                help="Name to greet",
            ),
            count: int = typer.Option(
                1,
                "--count",
                "-c",
                help="Number of times to greet",
            ),
            excited: bool = typer.Option(
                False,
                "--excited",
                "-e",
                help="Use excited greeting",
            ),
        ) -> None:
            """Say hello to someone.

            Examples:
                $ specify hello
                $ specify hello --name Alice
                $ specify hello --name Bob --count 3
                $ specify hello --name Charlie --excited
            """
            greeting = f"Hello, {name}"
            if excited:
                greeting += "!"
            else:
                greeting += "."

            for _ in range(count):
                console.print(f"[bold cyan]{greeting}[/bold cyan]")

        @app.command()
        def goodbye(
            name: str = typer.Option(
                "World",
                "--name",
                "-n",
                help="Name to say goodbye to",
            ),
        ) -> None:
            """Say goodbye to someone."""
            console.print(f"[bold magenta]Goodbye, {name}![/bold magenta]")

        return {"hello": app}

    def _shutdown_impl(self) -> None:
        """Shutdown the plugin."""
        console.print("[yellow]Hello plugin shutting down[/yellow]")


# Plugin instance for auto-discovery
plugin = HelloPlugin()
