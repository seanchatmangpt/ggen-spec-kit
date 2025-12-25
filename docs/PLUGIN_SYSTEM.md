# Plugin System Guide

Comprehensive guide to the Specify CLI plugin system for extensibility, custom commands, and integrations.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Plugin Architecture](#plugin-architecture)
- [Creating Plugins](#creating-plugins)
- [Plugin Types](#plugin-types)
- [Plugin Marketplace](#plugin-marketplace)
- [Plugin Configuration](#plugin-configuration)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Security Considerations](#security-considerations)
- [API Reference](#api-reference)

## Overview

The Specify CLI plugin system provides a powerful, extensible architecture for adding custom functionality to the CLI. Plugins can:

- Add new CLI commands
- Integrate with external services (GitHub, Slack, Jira, etc.)
- Transform data and files
- Generate reports and documentation
- Extend existing functionality via hooks

### Key Features

- **Zero-configuration**: Auto-discovery from entry points and directories
- **Dynamic loading**: Load plugins at runtime without rebuilding
- **Version compatibility**: Automatic version checking
- **Dependency resolution**: Manage plugin dependencies
- **Hot-reloading**: Reload plugins during development
- **Marketplace integration**: Install plugins from PyPI or Git
- **Type-safe**: Full type hints and Protocol-based interfaces
- **Secure**: Permission system and optional sandboxing

## Quick Start

### Installing Plugins

```bash
# Search for plugins
$ specify plugin search github

# Install from marketplace
$ specify plugin install specify-plugin-github

# Install from Git
$ specify plugin install git+https://github.com/user/plugin.git

# Install from local directory
$ specify plugin install ./my-plugin
```

### Managing Plugins

```bash
# List installed plugins
$ specify plugin list

# Show plugin info
$ specify plugin info my-plugin

# Update plugin
$ specify plugin update my-plugin

# Uninstall plugin
$ specify plugin uninstall my-plugin

# Reload plugins (development)
$ specify plugin reload
```

### Creating Your First Plugin

1. Create a plugin file:

```python
# ~/.specify/plugins/user/hello_plugin.py
from specify_cli.plugins.api import BasePlugin, CommandPlugin, PluginMetadata
import typer
from rich.console import Console

console = Console()

class HelloPlugin(BasePlugin, CommandPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hello-plugin",
            version="1.0.0",
            description="Simple hello world command",
        )

    def _initialize_impl(self) -> None:
        console.print("[green]✓[/green] Hello plugin initialized")

    def get_commands(self) -> dict[str, typer.Typer]:
        app = typer.Typer(name="hello", help="Say hello")

        @app.command()
        def hello(name: str = "World") -> None:
            """Say hello to someone."""
            console.print(f"[bold cyan]Hello, {name}![/bold cyan]")

        return {"hello": app}

# Plugin instance for auto-discovery
plugin = HelloPlugin()
```

2. Use your plugin:

```bash
$ specify hello --name Alice
Hello, Alice!
```

## Plugin Architecture

The plugin system uses a three-layer architecture:

```
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
```

### Plugin Discovery

Plugins are discovered from:

1. **Python entry points**: Installed packages declaring `specify_cli.plugins` entry points
2. **Plugin directories**: Custom directories specified in configuration
3. **User plugins**: `~/.specify/plugins/user/` for user-installed plugins

### Plugin Lifecycle

1. **Discovery**: Plugin is found and metadata is registered
2. **Loading**: Plugin code is imported and instantiated
3. **Initialization**: Plugin's `initialize()` method is called
4. **Active**: Plugin is running and handling requests
5. **Shutdown**: Plugin's `shutdown()` method is called
6. **Unloaded**: Plugin is removed from memory

## Creating Plugins

### Plugin Types

#### 1. Command Plugin

Adds new CLI commands:

```python
from specify_cli.plugins.api import BasePlugin, CommandPlugin, PluginMetadata, PluginType
import typer

class MyCommandPlugin(BasePlugin, CommandPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-command-plugin",
            version="1.0.0",
            description="Adds custom commands",
            plugin_type=PluginType.COMMAND,
        )

    def _initialize_impl(self) -> None:
        # Initialization logic
        pass

    def get_commands(self) -> dict[str, typer.Typer]:
        app = typer.Typer(name="mycommand")

        @app.command()
        def run() -> None:
            """Run my command."""
            print("Running my command!")

        return {"mycommand": app}
```

#### 2. Integration Plugin

Integrates with external services:

```python
from specify_cli.plugins.api import BasePlugin, IntegrationPlugin, PluginMetadata
import httpx

class GitHubPlugin(BasePlugin, IntegrationPlugin):
    def __init__(self) -> None:
        super().__init__()
        self._client: httpx.Client | None = None

    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="github-plugin",
            version="1.0.0",
            description="GitHub integration",
            plugin_type=PluginType.INTEGRATION,
        )

    def _initialize_impl(self) -> None:
        # Get API token from config
        token = self._config.config.get("github_token")
        # Setup will happen in connect()

    def connect(self) -> None:
        """Connect to GitHub API."""
        self._client = httpx.Client(
            base_url="https://api.github.com",
            headers={"Authorization": f"Bearer {token}"},
        )

    def disconnect(self) -> None:
        """Disconnect from GitHub API."""
        if self._client:
            self._client.close()

    def is_connected(self) -> bool:
        """Check if connected."""
        return self._client is not None
```

#### 3. Reporter Plugin

Generates reports:

```python
from specify_cli.plugins.api import BasePlugin, ReporterPlugin, PluginMetadata
from pathlib import Path
from typing import Any

class ReportPlugin(BasePlugin, ReporterPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="report-plugin",
            version="1.0.0",
            description="Generate reports",
            plugin_type=PluginType.REPORTER,
        )

    def _initialize_impl(self) -> None:
        pass

    def generate_report(
        self,
        data: Any,
        output_path: Path,
        options: dict[str, Any] | None = None
    ) -> Path:
        """Generate report from data."""
        # Generate report
        report = self._format_report(data, options)

        # Write to file
        output_path.write_text(report)

        return output_path
```

#### 4. Transformer Plugin

Transforms data:

```python
from specify_cli.plugins.api import BasePlugin, TransformerPlugin, PluginMetadata
from typing import Any

class DataTransformerPlugin(BasePlugin, TransformerPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="transformer-plugin",
            version="1.0.0",
            description="Transform data",
            plugin_type=PluginType.TRANSFORMER,
        )

    def _initialize_impl(self) -> None:
        pass

    def transform(
        self,
        input_data: Any,
        options: dict[str, Any] | None = None
    ) -> Any:
        """Transform input data."""
        # Apply transformation
        return self._apply_transformation(input_data, options)
```

#### 5. Hook Plugin

Extends functionality via hooks:

```python
from specify_cli.plugins.api import BasePlugin, HookPlugin, PluginMetadata

class HookPlugin(BasePlugin, HookPlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hook-plugin",
            version="1.0.0",
            description="Extends via hooks",
            plugin_type=PluginType.HOOK,
        )

    def _initialize_impl(self) -> None:
        pass

    def get_hooks(self) -> dict[str, Callable]:
        """Return hook handlers."""
        return {
            "before_command": self._before_command,
            "after_command": self._after_command,
        }

    def _before_command(self, command_name: str, args: dict) -> None:
        """Hook called before command execution."""
        print(f"Running command: {command_name}")

    def _after_command(self, command_name: str, args: dict, result: Any) -> None:
        """Hook called after command execution."""
        print(f"Command completed: {command_name}")
```

### Plugin Metadata

Complete metadata example:

```python
from specify_cli.plugins.api import (
    PluginMetadata,
    PluginType,
    PluginDependency,
    PluginPermissions,
)

metadata = PluginMetadata(
    # Required
    name="my-plugin",
    version="1.0.0",
    description="My awesome plugin",

    # Author info
    author="Your Name",
    author_email="you@example.com",
    homepage="https://example.com",
    repository="https://github.com/user/plugin",
    license="MIT",

    # Plugin configuration
    plugin_type=PluginType.COMMAND,
    entry_point="my_plugin:plugin",

    # Dependencies
    dependencies=[
        PluginDependency(
            name="base-plugin",
            version_spec=">=1.0.0,<2.0.0",
            optional=False,
        ),
    ],
    python_dependencies=["httpx>=0.27.0", "rich>=13.0.0"],

    # Permissions
    permissions=[
        PluginPermissions.NETWORK_ACCESS,
        PluginPermissions.READ_FILES,
    ],

    # Searchability
    tags=["integration", "github", "vcs"],

    # Version compatibility
    min_cli_version="0.0.1",
    max_cli_version="*",

    # Flags
    experimental=False,
    deprecated=False,
)
```

## Plugin Marketplace

### Installing Plugins

#### From PyPI

```bash
# Install latest version
$ specify plugin install specify-plugin-github

# Install specific version
$ specify plugin install specify-plugin-github==1.0.0

# Upgrade existing plugin
$ specify plugin install --upgrade specify-plugin-github
```

#### From Git

```bash
# Install from Git repository
$ specify plugin install git+https://github.com/user/plugin.git

# Install from specific branch/tag
$ specify plugin install git+https://github.com/user/plugin.git@v1.0.0
```

#### From Local Directory

```bash
# Install from local directory
$ specify plugin install ./my-plugin

# Install in development mode (editable)
$ specify plugin install --editable ./my-plugin
```

### Publishing Plugins

To publish a plugin to PyPI:

1. Create `setup.py` or `pyproject.toml`:

```toml
[project]
name = "specify-plugin-myname"
version = "1.0.0"
description = "My plugin for Specify CLI"

[project.entry-points."specify_cli.plugins"]
my-plugin = "my_plugin:plugin"
```

2. Build and publish:

```bash
$ python -m build
$ python -m twine upload dist/*
```

Users can then install with:

```bash
$ specify plugin install specify-plugin-myname
```

## Plugin Configuration

### Configuration File

Plugins are configured in `~/.specify/plugins/<plugin-name>.json`:

```json
{
  "enabled": true,
  "auto_load": true,
  "priority": 100,
  "hot_reload": false,
  "config": {
    "api_key": "your-api-key",
    "base_url": "https://api.example.com",
    "custom_setting": "value"
  }
}
```

### Accessing Configuration

In your plugin:

```python
def _initialize_impl(self) -> None:
    # Access plugin configuration
    if self._config:
        api_key = self._config.config.get("api_key")
        base_url = self._config.config.get("base_url")
```

## Advanced Features

### Dependency Injection

Plugins can access the plugin manager and other plugins:

```python
class MyPlugin(BasePlugin):
    def __init__(self, manager: PluginManager | None = None) -> None:
        super().__init__()
        self._manager = manager

    def _initialize_impl(self) -> None:
        # Access other plugins
        if self._manager:
            other = self._manager.get_plugin("other-plugin")
```

### Event System

Register event handlers:

```python
from specify_cli.plugins.api import PluginHooks

class MyPlugin(BasePlugin, HookPlugin):
    def get_hooks(self) -> dict[str, Callable]:
        return {
            PluginHooks.ON_STARTUP.name: self._on_startup,
            PluginHooks.ON_SHUTDOWN.name: self._on_shutdown,
            PluginHooks.BEFORE_COMMAND.name: self._before_command,
        }

    def _on_startup(self) -> None:
        print("CLI starting up")

    def _before_command(self, command_name: str, args: dict) -> None:
        print(f"Running {command_name}")
```

### Hot-Reloading

Enable hot-reloading for development:

```python
manager = PluginManager()
manager.enable_hot_reload()

# Plugins will be automatically reloaded when changed
```

Or via CLI:

```bash
$ specify plugin reload
```

## Best Practices

### 1. Use Type Hints

Always use type hints for better IDE support and type checking:

```python
def transform(self, data: dict[str, Any]) -> dict[str, Any]:
    ...
```

### 2. Handle Errors Gracefully

Catch and handle errors appropriately:

```python
def _initialize_impl(self) -> None:
    try:
        self._setup_connection()
    except ConnectionError as e:
        raise PluginInitError(f"Failed to connect: {e}") from e
```

### 3. Document Your Plugin

Provide clear documentation:

```python
class MyPlugin(BasePlugin):
    """My awesome plugin.

    This plugin provides:
    - Feature A
    - Feature B
    - Feature C

    Configuration:
        api_key: API key for authentication
        timeout: Request timeout in seconds

    Example:
        $ specify mycommand --option value
    """
```

### 4. Use Semantic Versioning

Follow semver for version numbers:

- MAJOR version for incompatible API changes
- MINOR version for new functionality
- PATCH version for bug fixes

### 5. Declare Dependencies

Always declare plugin and Python dependencies:

```python
metadata = PluginMetadata(
    dependencies=[
        PluginDependency("base-plugin", ">=1.0.0,<2.0.0"),
    ],
    python_dependencies=[
        "httpx>=0.27.0",
        "pydantic>=2.0.0",
    ],
)
```

### 6. Test Your Plugin

Write comprehensive tests:

```python
import pytest
from my_plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin()
    config = PluginConfig()
    plugin.initialize(config)
    assert plugin.health_check()
```

## Security Considerations

### Permissions

Request only necessary permissions:

```python
permissions=[
    PluginPermissions.READ_FILES,  # Only if needed
    # Don't request WRITE_FILES unless necessary
]
```

### Input Validation

Always validate user input:

```python
def process(self, data: dict[str, Any]) -> None:
    # Validate input
    if not isinstance(data.get("name"), str):
        raise ValueError("Invalid name")

    # Sanitize file paths
    path = Path(data["path"]).resolve()
    if not path.is_relative_to(Path.cwd()):
        raise ValueError("Path outside workspace")
```

### Secrets Management

Never hardcode secrets:

```python
# ❌ DON'T
API_KEY = "hardcoded-secret"

# ✅ DO
def _initialize_impl(self) -> None:
    api_key = os.environ.get("MY_PLUGIN_API_KEY")
    # or from config
    api_key = self._config.config.get("api_key")
```

### Network Security

Use HTTPS and verify certificates:

```python
self._client = httpx.Client(
    base_url="https://api.example.com",  # HTTPS only
    verify=True,  # Verify certificates
    timeout=30.0,
)
```

## API Reference

### Base Classes

#### `BasePlugin`

Base class for all plugins.

**Methods:**
- `metadata() -> PluginMetadata`: Return plugin metadata
- `initialize(config: PluginConfig) -> None`: Initialize plugin
- `shutdown() -> None`: Shutdown plugin
- `health_check() -> bool`: Check plugin health

**Properties:**
- `state: PluginState`: Current plugin state
- `config: PluginConfig | None`: Plugin configuration
- `error: str | None`: Last error message

### Protocols

#### `CommandPlugin`

Protocol for plugins that provide commands.

**Methods:**
- `get_commands() -> dict[str, typer.Typer]`: Get plugin commands

#### `IntegrationPlugin`

Protocol for integration plugins.

**Methods:**
- `connect() -> None`: Connect to external service
- `disconnect() -> None`: Disconnect from service
- `is_connected() -> bool`: Check connection status

#### `ReporterPlugin`

Protocol for report generation plugins.

**Methods:**
- `generate_report(data: Any, output_path: Path, options: dict | None) -> Path`

#### `TransformerPlugin`

Protocol for data transformation plugins.

**Methods:**
- `transform(input_data: Any, options: dict | None) -> Any`

### Plugin Manager

#### `PluginManager`

Main plugin system manager.

**Methods:**
- `discover_plugins() -> list[PluginMetadata]`: Discover available plugins
- `load_plugin(name: str, config: PluginConfig | None) -> Plugin`: Load plugin
- `unload_plugin(name: str) -> None`: Unload plugin
- `load_all_plugins(auto_load_only: bool) -> list[str]`: Load all plugins
- `get_plugin(name: str) -> Plugin | None`: Get loaded plugin
- `list_plugins() -> list[tuple[str, PluginState]]`: List all plugins
- `register_hook(hook_name: str, handler: Callable) -> None`: Register hook

### Plugin Marketplace

#### `PluginMarketplace`

Plugin marketplace client.

**Methods:**
- `search(query: str, tags: list[str] | None, limit: int) -> list[PluginPackage]`
- `install(plugin_spec: str, upgrade: bool, force: bool) -> PluginMetadata`
- `update(plugin_name: str) -> PluginMetadata`
- `uninstall(plugin_name: str) -> None`
- `list_installed() -> list[PluginMetadata]`

## Examples

See the `examples/plugins/` directory for complete plugin examples:

- **hello_plugin.py**: Simple command plugin
- **github_plugin.py**: GitHub integration
- **report_plugin.py**: Report generation

## Troubleshooting

### Plugin Not Loading

1. Check plugin is in correct directory
2. Verify plugin metadata is valid
3. Check dependency requirements
4. Review error logs

### Version Conflicts

```bash
# Check plugin compatibility
$ specify plugin info my-plugin

# Update to compatible version
$ specify plugin update my-plugin
```

### Permission Errors

Ensure plugin has required permissions in configuration.

## Support

- Documentation: https://github.com/seanchatmangpt/ggen-spec-kit/tree/main/docs
- Issues: https://github.com/seanchatmangpt/ggen-spec-kit/issues
- Discussions: https://github.com/seanchatmangpt/ggen-spec-kit/discussions
