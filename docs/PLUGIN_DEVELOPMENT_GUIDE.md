# Plugin Development Quick Start

Quick guide to developing plugins for the Specify CLI.

## Prerequisites

- Python 3.11+
- Specify CLI installed (`pip install specify-cli`)
- Basic understanding of Typer and Rich

## Creating a Plugin

### Step 1: Choose Plugin Type

Decide what kind of plugin you need:

- **Command**: Add new CLI commands
- **Integration**: Connect to external services
- **Reporter**: Generate reports
- **Transformer**: Transform data
- **Hook**: Extend existing functionality

### Step 2: Create Plugin File

Create a Python file in `~/.specify/plugins/user/`:

```python
# ~/.specify/plugins/user/my_plugin.py
from specify_cli.plugins.api import (
    BasePlugin,
    CommandPlugin,
    PluginConfig,
    PluginMetadata,
    PluginType,
)
import typer
from rich.console import Console

console = Console()

class MyPlugin(BasePlugin, CommandPlugin):
    """My custom plugin."""

    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="My custom plugin for Specify CLI",
            author="Your Name",
            author_email="you@example.com",
            plugin_type=PluginType.COMMAND,
            tags=["custom", "example"],
        )

    def _initialize_impl(self) -> None:
        """Initialize the plugin."""
        console.print("[green]✓[/green] My plugin initialized")

    def get_commands(self) -> dict[str, typer.Typer]:
        """Get plugin commands."""
        app = typer.Typer(
            name="mycmd",
            help="My custom command",
        )

        @app.command()
        def run(
            name: str = typer.Option("World", "--name", "-n"),
        ) -> None:
            """Run my custom command."""
            console.print(f"[bold]Hello from my plugin, {name}![/bold]")

        return {"mycmd": app}

    def _shutdown_impl(self) -> None:
        """Shutdown the plugin."""
        console.print("[yellow]My plugin shutting down[/yellow]")

# Plugin instance for auto-discovery
plugin = MyPlugin()
```

### Step 3: Test Your Plugin

```bash
# List plugins (should show your plugin)
$ specify plugin list

# Use your plugin command
$ specify mycmd run --name Alice
```

## Plugin Structure

### Minimal Plugin

```python
from specify_cli.plugins.api import BasePlugin, PluginMetadata

class MinimalPlugin(BasePlugin):
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="minimal",
            version="1.0.0",
            description="Minimal plugin",
        )

    def _initialize_impl(self) -> None:
        pass

plugin = MinimalPlugin()
```

### Command Plugin

```python
from specify_cli.plugins.api import BasePlugin, CommandPlugin
import typer

class CmdPlugin(BasePlugin, CommandPlugin):
    # ... metadata ...

    def get_commands(self) -> dict[str, typer.Typer]:
        app = typer.Typer()

        @app.command()
        def hello() -> None:
            print("Hello!")

        return {"hello": app}

plugin = CmdPlugin()
```

### Integration Plugin

```python
from specify_cli.plugins.api import BasePlugin, IntegrationPlugin
import httpx

class APIPlugin(BasePlugin, IntegrationPlugin):
    def __init__(self) -> None:
        super().__init__()
        self._client = None

    # ... metadata ...

    def connect(self) -> None:
        self._client = httpx.Client(base_url="https://api.example.com")

    def disconnect(self) -> None:
        if self._client:
            self._client.close()

    def is_connected(self) -> bool:
        return self._client is not None

plugin = APIPlugin()
```

## Adding Configuration

### 1. Define Configuration Schema

```python
def metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        description="Plugin with config",
        config_schema={
            "type": "object",
            "properties": {
                "api_key": {"type": "string"},
                "timeout": {"type": "integer", "default": 30},
            },
            "required": ["api_key"],
        },
    )
```

### 2. Create Configuration File

Create `~/.specify/plugins/my-plugin.json`:

```json
{
  "enabled": true,
  "auto_load": true,
  "config": {
    "api_key": "your-key-here",
    "timeout": 60
  }
}
```

### 3. Access Configuration

```python
def _initialize_impl(self) -> None:
    if self._config:
        api_key = self._config.config.get("api_key")
        timeout = self._config.config.get("timeout", 30)
```

## Adding Dependencies

### Plugin Dependencies

```python
from specify_cli.plugins.api import PluginDependency

def metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        description="Plugin with dependencies",
        dependencies=[
            PluginDependency(
                name="base-plugin",
                version_spec=">=1.0.0,<2.0.0",
            ),
        ],
    )
```

### Python Dependencies

```python
def metadata(self) -> PluginMetadata:
    return PluginMetadata(
        name="my-plugin",
        version="1.0.0",
        description="Plugin with Python deps",
        python_dependencies=[
            "httpx>=0.27.0",
            "pydantic>=2.0.0",
        ],
    )
```

## Testing

### Unit Tests

```python
import pytest
from my_plugin import MyPlugin
from specify_cli.plugins.api import PluginConfig

def test_plugin_initialization():
    """Test plugin initializes correctly."""
    plugin = MyPlugin()
    config = PluginConfig()

    plugin.initialize(config)

    assert plugin.health_check()
    assert plugin.state == PluginState.ACTIVE

def test_plugin_metadata():
    """Test plugin metadata."""
    plugin = MyPlugin()
    metadata = plugin.metadata()

    assert metadata.name == "my-plugin"
    assert metadata.version == "1.0.0"
```

### Integration Tests

```python
def test_plugin_command(cli_runner):
    """Test plugin command works."""
    from specify_cli.app import app

    result = cli_runner.invoke(app, ["mycmd", "run"])

    assert result.exit_code == 0
    assert "Hello" in result.output
```

## Publishing

### As Standalone File

Share the `.py` file directly. Users install by copying to `~/.specify/plugins/user/`.

### As Python Package

1. Create `pyproject.toml`:

```toml
[project]
name = "specify-plugin-myname"
version = "1.0.0"
description = "My plugin for Specify CLI"
dependencies = ["specify-cli>=0.0.1"]

[project.entry-points."specify_cli.plugins"]
my-plugin = "my_plugin:plugin"
```

2. Build and publish:

```bash
$ python -m build
$ python -m twine upload dist/*
```

3. Users install with:

```bash
$ specify plugin install specify-plugin-myname
```

## Common Patterns

### Adding Subcommands

```python
def get_commands(self) -> dict[str, typer.Typer]:
    app = typer.Typer()

    # Subcommand group
    list_app = typer.Typer()

    @list_app.command("all")
    def list_all() -> None:
        """List all items."""
        pass

    @list_app.command("active")
    def list_active() -> None:
        """List active items."""
        pass

    app.add_typer(list_app, name="list")

    return {"mycmd": app}
```

Usage: `specify mycmd list all`

### Rich Output

```python
from rich.table import Table
from rich.console import Console

console = Console()

def show_data(items: list[dict]) -> None:
    table = Table(title="Items")
    table.add_column("Name", style="cyan")
    table.add_column("Value", style="green")

    for item in items:
        table.add_row(item["name"], item["value"])

    console.print(table)
```

### Error Handling

```python
from specify_cli.plugins.api import PluginError

def _initialize_impl(self) -> None:
    try:
        self._setup()
    except Exception as e:
        raise PluginInitError(f"Failed to initialize: {e}") from e

def some_operation(self) -> None:
    if not self._is_valid():
        raise PluginError("Invalid state")
```

### Using Hooks

```python
from specify_cli.plugins.api import HookPlugin

class MyHookPlugin(BasePlugin, HookPlugin):
    def get_hooks(self) -> dict[str, Callable]:
        return {
            "before_command": self._before_cmd,
            "after_command": self._after_cmd,
        }

    def _before_cmd(self, command_name: str, args: dict) -> None:
        print(f"Running: {command_name}")

    def _after_cmd(self, command_name: str, args: dict, result: Any) -> None:
        print(f"Completed: {command_name}")
```

## Debugging

### Enable Debug Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def _initialize_impl(self) -> None:
    logger.debug("Initializing plugin")
    # ...
```

### Check Plugin State

```bash
$ specify plugin info my-plugin
$ specify plugin list --all
```

### Reload During Development

```bash
$ specify plugin reload
```

## Best Practices

1. **Use type hints** - Better IDE support and type checking
2. **Document everything** - Docstrings on all public methods
3. **Handle errors gracefully** - Catch and wrap exceptions
4. **Validate input** - Check all user input
5. **Test thoroughly** - Write unit and integration tests
6. **Follow conventions** - Use kebab-case for plugin names
7. **Version properly** - Use semantic versioning
8. **Declare dependencies** - List all requirements
9. **Keep it simple** - One plugin, one purpose
10. **Be secure** - Never hardcode secrets

## Resources

- **Full Documentation**: `/docs/PLUGIN_SYSTEM.md`
- **Example Plugins**: `/examples/plugins/`
- **API Reference**: See `specify_cli.plugins.api`
- **Source Code**: https://github.com/seanchatmangpt/ggen-spec-kit

## Getting Help

- Open an issue on GitHub
- Check existing plugins for examples
- Read the full plugin system documentation
- Join community discussions

Happy plugin development!
