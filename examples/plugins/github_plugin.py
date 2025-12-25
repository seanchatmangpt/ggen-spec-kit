"""
Example Plugin: GitHub Integration
===================================

A GitHub integration plugin that provides commands for interacting with GitHub.

This demonstrates:
- Integration plugin implementation
- External API integration
- Command plugin with multiple subcommands
- Configuration handling
- Error handling

Installation:
    Copy this file to ~/.specify/plugins/user/github_plugin.py

Configuration:
    Create ~/.specify/plugins/github-plugin.json:
    {
        "enabled": true,
        "auto_load": true,
        "config": {
            "github_token": "your_token_here",
            "default_org": "your_org"
        }
    }

Usage:
    $ specify gh repos list --org myorg
    $ specify gh issues list --repo myrepo
    $ specify gh pr create --title "New feature" --body "Description"
"""

from __future__ import annotations

from typing import Any

import httpx
import typer
from rich.console import Console
from rich.table import Table

from specify_cli.plugins.api import (
    BasePlugin,
    CommandPlugin,
    IntegrationPlugin,
    PluginConfig,
    PluginMetadata,
    PluginPermissions,
    PluginType,
)

console = Console()


class GitHubPlugin(BasePlugin, CommandPlugin, IntegrationPlugin):
    """GitHub integration plugin.

    Provides commands for interacting with GitHub repositories, issues, and PRs.
    """

    def __init__(self) -> None:
        """Initialize GitHub plugin."""
        super().__init__()
        self._client: httpx.Client | None = None
        self._token: str | None = None
        self._default_org: str | None = None

    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="github-plugin",
            version="1.0.0",
            description="GitHub integration for repository, issue, and PR management",
            author="Specify Team",
            author_email="info@chatmangpt.com",
            homepage="https://github.com/seanchatmangpt/ggen-spec-kit",
            plugin_type=PluginType.INTEGRATION,
            permissions=[
                PluginPermissions.NETWORK_ACCESS,
            ],
            tags=["github", "integration", "vcs", "api"],
            min_cli_version="0.0.1",
        )

    def _initialize_impl(self) -> None:
        """Initialize the plugin."""
        # Get configuration
        if self._config:
            config_data = self._config.config
            self._token = config_data.get("github_token")
            self._default_org = config_data.get("default_org")

        console.print("[green]✓[/green] GitHub plugin initialized")

    def connect(self) -> None:
        """Establish connection to GitHub API."""
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers=headers,
            timeout=30.0,
        )

    def disconnect(self) -> None:
        """Disconnect from GitHub API."""
        if self._client:
            self._client.close()
            self._client = None

    def is_connected(self) -> bool:
        """Check if connected to GitHub API."""
        return self._client is not None

    def get_commands(self) -> dict[str, typer.Typer]:
        """Get plugin commands."""
        # Create main GitHub command app
        app = typer.Typer(
            name="gh",
            help="GitHub integration commands",
            add_completion=False,
        )

        # Repositories subcommand
        repos_app = typer.Typer(name="repos", help="Repository management")

        @repos_app.command("list")
        def list_repos(
            org: str = typer.Option(
                None,
                "--org",
                "-o",
                help="Organization name",
            ),
            limit: int = typer.Option(
                10,
                "--limit",
                "-l",
                help="Maximum number of repos to show",
            ),
        ) -> None:
            """List repositories for an organization."""
            if not self.is_connected():
                self.connect()

            org_name = org or self._default_org
            if not org_name:
                console.print("[red]Error:[/red] No organization specified")
                raise typer.Exit(1)

            try:
                response = self._client.get(f"/orgs/{org_name}/repos", params={"per_page": limit})  # type: ignore[union-attr]
                response.raise_for_status()
                repos = response.json()

                # Create table
                table = Table(title=f"Repositories in {org_name}")
                table.add_column("Name", style="cyan")
                table.add_column("Stars", style="yellow")
                table.add_column("Forks", style="green")
                table.add_column("Description", style="white")

                for repo in repos:
                    table.add_row(
                        repo["name"],
                        str(repo["stargazers_count"]),
                        str(repo["forks_count"]),
                        repo.get("description", "")[:50],
                    )

                console.print(table)

            except httpx.HTTPError as e:
                console.print(f"[red]Error:[/red] Failed to fetch repositories: {e}")
                raise typer.Exit(1) from e

        # Issues subcommand
        issues_app = typer.Typer(name="issues", help="Issue management")

        @issues_app.command("list")
        def list_issues(
            repo: str = typer.Option(
                ...,
                "--repo",
                "-r",
                help="Repository name (format: owner/repo)",
            ),
            state: str = typer.Option(
                "open",
                "--state",
                "-s",
                help="Issue state (open, closed, all)",
            ),
            limit: int = typer.Option(
                10,
                "--limit",
                "-l",
                help="Maximum number of issues to show",
            ),
        ) -> None:
            """List issues for a repository."""
            if not self.is_connected():
                self.connect()

            try:
                response = self._client.get(  # type: ignore[union-attr]
                    f"/repos/{repo}/issues",
                    params={"state": state, "per_page": limit},
                )
                response.raise_for_status()
                issues = response.json()

                # Create table
                table = Table(title=f"Issues in {repo}")
                table.add_column("Number", style="cyan")
                table.add_column("State", style="yellow")
                table.add_column("Title", style="white")
                table.add_column("Author", style="green")

                for issue in issues:
                    table.add_row(
                        str(issue["number"]),
                        issue["state"],
                        issue["title"][:50],
                        issue["user"]["login"],
                    )

                console.print(table)

            except httpx.HTTPError as e:
                console.print(f"[red]Error:[/red] Failed to fetch issues: {e}")
                raise typer.Exit(1) from e

        # Add subcommands
        app.add_typer(repos_app)
        app.add_typer(issues_app)

        return {"gh": app}

    def _shutdown_impl(self) -> None:
        """Shutdown the plugin."""
        self.disconnect()
        console.print("[yellow]GitHub plugin shutting down[/yellow]")


# Plugin instance for auto-discovery
plugin = GitHubPlugin()
