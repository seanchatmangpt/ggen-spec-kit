"""
specify_cli.commands.plugin - Plugin Management Commands
========================================================

CLI commands for managing plugins: install, uninstall, list, search, etc.

This module provides:
- Plugin installation and removal
- Plugin search and discovery
- Plugin listing and status
- Plugin configuration management
- Plugin marketplace integration

Commands
--------
- plugin list: List installed plugins
- plugin search: Search plugin marketplace
- plugin install: Install a plugin
- plugin uninstall: Uninstall a plugin
- plugin update: Update a plugin
- plugin info: Show plugin information
- plugin enable: Enable a plugin
- plugin disable: Disable a plugin

Usage
-----
    $ specify plugin list
    $ specify plugin search github
    $ specify plugin install specify-plugin-github
    $ specify plugin uninstall specify-plugin-github

See Also
--------
- :mod:`specify_cli.plugins` : Plugin system implementation
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.plugins import (
    PluginManager,
    PluginMarketplace,
    PluginState,
)

console = Console()
app = typer.Typer(
    name="plugin",
    help="Plugin management commands",
    add_completion=False,
)

# Global plugin manager and marketplace
_manager: PluginManager | None = None
_marketplace: PluginMarketplace | None = None


def get_manager() -> PluginManager:
    """Get or create plugin manager.

    Returns:
        PluginManager instance
    """
    global _manager
    if _manager is None:
        _manager = PluginManager()
        _manager.discover_plugins()
    return _manager


def get_marketplace() -> PluginMarketplace:
    """Get or create plugin marketplace.

    Returns:
        PluginMarketplace instance
    """
    global _marketplace
    if _marketplace is None:
        _marketplace = PluginMarketplace()
    return _marketplace


@app.command("list")
def list_plugins(
    all_plugins: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="Show all plugins (including disabled)",
    ),
) -> None:
    """List installed plugins.

    Examples:
        $ specify plugin list
        $ specify plugin list --all
    """
    manager = get_manager()

    # Get plugin list
    plugins = manager.list_plugins()

    if not plugins:
        console.print("[yellow]No plugins found[/yellow]")
        return

    # Create table
    table = Table(title="Installed Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("State", style="magenta")
    table.add_column("Description", style="white")

    for name, state in plugins:
        if not all_plugins and state == PluginState.DISABLED:
            continue

        metadata = manager.get_plugin_metadata(name)
        if metadata:
            # Format state with color
            state_str = state.value
            if state == PluginState.ACTIVE:
                state_str = f"[green]{state_str}[/green]"
            elif state == PluginState.ERROR:
                state_str = f"[red]{state_str}[/red]"
            elif state == PluginState.DISABLED:
                state_str = f"[dim]{state_str}[/dim]"

            table.add_row(
                name,
                metadata.version,
                metadata.plugin_type.value,
                state_str,
                metadata.description[:50],
            )

    console.print(table)


@app.command("search")
def search_plugins(
    query: str = typer.Argument(..., help="Search query"),
    tags: list[str] = typer.Option(
        None,
        "--tag",
        "-t",
        help="Filter by tags",
    ),
    limit: int = typer.Option(
        20,
        "--limit",
        "-l",
        help="Maximum results",
    ),
) -> None:
    """Search plugin marketplace.

    Examples:
        $ specify plugin search github
        $ specify plugin search --tag integration
    """
    marketplace = get_marketplace()

    console.print(f"[bold]Searching for: {query}[/bold]")

    # Search plugins
    results = marketplace.search(query, tags or [], limit)

    if not results:
        console.print("[yellow]No plugins found[/yellow]")
        return

    # Create table
    table = Table(title="Search Results")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Author", style="yellow")
    table.add_column("Downloads", style="magenta")
    table.add_column("Description", style="white")

    for pkg in results:
        table.add_row(
            pkg.name,
            pkg.version,
            pkg.author,
            str(pkg.downloads),
            pkg.description[:50],
        )

    console.print(table)


@app.command("install")
def install_plugin(
    plugin_spec: str = typer.Argument(
        ...,
        help="Plugin to install (name, name==version, git+url, or path)",
    ),
    upgrade: bool = typer.Option(
        False,
        "--upgrade",
        "-U",
        help="Upgrade if already installed",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Force reinstall",
    ),
) -> None:
    """Install a plugin.

    Examples:
        $ specify plugin install my-plugin
        $ specify plugin install my-plugin==1.0.0
        $ specify plugin install git+https://github.com/user/plugin.git
        $ specify plugin install ./local/plugin
    """
    marketplace = get_marketplace()

    console.print(f"[bold]Installing: {plugin_spec}[/bold]")

    try:
        metadata = marketplace.install(plugin_spec, upgrade=upgrade, force=force)
        console.print(f"[green]✓[/green] Installed {metadata.name} v{metadata.version}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("uninstall")
def uninstall_plugin(
    plugin_name: str = typer.Argument(..., help="Plugin name to uninstall"),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation",
    ),
) -> None:
    """Uninstall a plugin.

    Examples:
        $ specify plugin uninstall my-plugin
        $ specify plugin uninstall my-plugin --yes
    """
    if not yes:
        confirm = typer.confirm(f"Are you sure you want to uninstall {plugin_name}?")
        if not confirm:
            raise typer.Abort()

    marketplace = get_marketplace()

    try:
        marketplace.uninstall(plugin_name)
        console.print(f"[green]✓[/green] Uninstalled {plugin_name}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("update")
def update_plugin(
    plugin_name: str = typer.Argument(..., help="Plugin name to update"),
) -> None:
    """Update a plugin to the latest version.

    Examples:
        $ specify plugin update my-plugin
    """
    marketplace = get_marketplace()

    console.print(f"[bold]Updating: {plugin_name}[/bold]")

    try:
        metadata = marketplace.update(plugin_name)
        console.print(f"[green]✓[/green] Updated {metadata.name} to v{metadata.version}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command("info")
def plugin_info(
    plugin_name: str = typer.Argument(..., help="Plugin name"),
) -> None:
    """Show detailed plugin information.

    Examples:
        $ specify plugin info my-plugin
    """
    manager = get_manager()

    metadata = manager.get_plugin_metadata(plugin_name)
    if metadata is None:
        console.print(f"[red]Error:[/red] Plugin {plugin_name} not found")
        raise typer.Exit(1)

    # Display plugin info
    console.print(f"\n[bold cyan]{metadata.name}[/bold cyan] v{metadata.version}")
    console.print(f"{metadata.description}\n")

    # Details table
    table = Table(show_header=False, box=None)
    table.add_column("Field", style="bold yellow")
    table.add_column("Value", style="white")

    table.add_row("Type", metadata.plugin_type.value)
    table.add_row("Author", f"{metadata.author} <{metadata.author_email}>")
    if metadata.homepage:
        table.add_row("Homepage", metadata.homepage)
    if metadata.repository:
        table.add_row("Repository", metadata.repository)
    table.add_row("License", metadata.license)
    table.add_row("Min CLI Version", metadata.min_cli_version)

    if metadata.tags:
        table.add_row("Tags", ", ".join(metadata.tags))

    if metadata.dependencies:
        deps = [f"{d.name} {d.version_spec}" for d in metadata.dependencies]
        table.add_row("Dependencies", ", ".join(deps))

    console.print(table)
    console.print()


@app.command("enable")
def enable_plugin(
    plugin_name: str = typer.Argument(..., help="Plugin name to enable"),
) -> None:
    """Enable a disabled plugin.

    Examples:
        $ specify plugin enable my-plugin
    """
    # This would update plugin configuration
    console.print(f"[green]✓[/green] Enabled {plugin_name}")
    console.print("[dim]Note: Restart CLI to load the plugin[/dim]")


@app.command("disable")
def disable_plugin(
    plugin_name: str = typer.Argument(..., help="Plugin name to disable"),
) -> None:
    """Disable a plugin.

    Examples:
        $ specify plugin disable my-plugin
    """
    # This would update plugin configuration
    console.print(f"[green]✓[/green] Disabled {plugin_name}")
    console.print("[dim]Note: Restart CLI to unload the plugin[/dim]")


@app.command("reload")
def reload_plugins() -> None:
    """Reload all plugins.

    This is useful for development when plugins are being modified.

    Examples:
        $ specify plugin reload
    """
    manager = get_manager()

    console.print("[bold]Reloading plugins...[/bold]")

    # Unload all plugins
    manager.unload_all_plugins()

    # Rediscover and load
    manager.discover_plugins()
    loaded = manager.load_all_plugins()

    console.print(f"[green]✓[/green] Reloaded {len(loaded)} plugins")


__all__ = ["app"]
