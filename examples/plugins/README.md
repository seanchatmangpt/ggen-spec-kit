# Plugin Examples

This directory contains example plugins demonstrating various plugin types and features.

## Available Examples

### 1. Hello Plugin (`hello_plugin.py`)

A simple command plugin that demonstrates:
- Basic plugin structure
- Command registration
- Multiple subcommands
- Option handling
- Rich console output

**Features:**
- `hello` command with customizable greeting
- `goodbye` command
- Options for name, count, and excitement level

**Installation:**
```bash
# Copy to user plugins directory
cp hello_plugin.py ~/.specify/plugins/user/

# Or use directly
$ specify hello --name Alice
$ specify hello --name Bob --count 3 --excited
```

### 2. GitHub Plugin (`github_plugin.py`)

An integration plugin that demonstrates:
- External API integration
- HTTP client management
- Configuration handling
- Multiple command groups
- Table output with Rich

**Features:**
- List repositories for an organization
- List issues for a repository
- Configurable GitHub token and default organization

**Configuration:**

Create `~/.specify/plugins/github-plugin.json`:
```json
{
  "enabled": true,
  "auto_load": true,
  "config": {
    "github_token": "your_github_token_here",
    "default_org": "your_organization"
  }
}
```

**Installation:**
```bash
# Copy to user plugins directory
cp github_plugin.py ~/.specify/plugins/user/

# Configure plugin
nano ~/.specify/plugins/github-plugin.json

# Use plugin
$ specify gh repos list --org myorg
$ specify gh issues list --repo owner/repo
```

### 3. Report Plugin (`report_plugin.py`)

A reporter plugin that demonstrates:
- Report generation
- Multiple output formats (Markdown, JSON, HTML)
- File operations
- Template rendering
- Data formatting

**Features:**
- Generate metrics reports
- Generate coverage reports
- Generate dependency reports
- Multiple output formats

**Installation:**
```bash
# Copy to user plugins directory
cp report_plugin.py ~/.specify/plugins/user/

# Generate reports
$ specify report generate --type metrics --output metrics.md
$ specify report generate --type coverage --format html --output coverage.html
$ specify report list-types
```

## Using the Examples

### Method 1: Copy to User Plugins Directory

```bash
# Copy all examples
cp *.py ~/.specify/plugins/user/

# List plugins
$ specify plugin list

# Use plugin commands
$ specify hello
$ specify gh repos list
$ specify report generate
```

### Method 2: Install as Package

Each example can be packaged and installed:

1. Create `pyproject.toml`:
```toml
[project]
name = "specify-plugin-hello"
version = "1.0.0"
description = "Hello plugin example"
dependencies = ["specify-cli>=0.0.1"]

[project.entry-points."specify_cli.plugins"]
hello-plugin = "hello_plugin:plugin"
```

2. Install:
```bash
$ pip install -e .
```

### Method 3: Direct Import

For development and testing:

```python
from examples.plugins.hello_plugin import HelloPlugin

plugin = HelloPlugin()
plugin.initialize(PluginConfig())
```

## Modifying Examples

Feel free to modify these examples to create your own plugins:

### Example: Customizing Hello Plugin

```python
# Add a new command
@app.command()
def greet(
    name: str = typer.Argument(...),
    language: str = typer.Option("en", "--lang"),
) -> None:
    """Greet in different languages."""
    greetings = {
        "en": "Hello",
        "es": "Hola",
        "fr": "Bonjour",
    }
    greeting = greetings.get(language, "Hello")
    console.print(f"[bold]{greeting}, {name}![/bold]")
```

### Example: Adding GitHub Features

```python
# Add pull request support
pr_app = typer.Typer(name="pr", help="Pull request management")

@pr_app.command("list")
def list_prs(repo: str) -> None:
    """List pull requests."""
    response = self._client.get(f"/repos/{repo}/pulls")
    # ... display PRs
```

## Learning Path

1. **Start with Hello Plugin** - Learn basic plugin structure
2. **Study GitHub Plugin** - Understand external integrations
3. **Explore Report Plugin** - Learn file generation and formatting
4. **Create Your Own** - Combine concepts to build custom plugins

## Common Modifications

### Adding Options

```python
@app.command()
def cmd(
    required: str = typer.Argument(..., help="Required argument"),
    optional: str = typer.Option("default", "--opt", help="Optional"),
    flag: bool = typer.Option(False, "--flag", help="Boolean flag"),
) -> None:
    pass
```

### Rich Tables

```python
from rich.table import Table

table = Table(title="Data")
table.add_column("Column 1", style="cyan")
table.add_column("Column 2", style="green")
table.add_row("Value 1", "Value 2")
console.print(table)
```

### Error Handling

```python
from specify_cli.plugins.api import PluginError

try:
    result = some_operation()
except Exception as e:
    console.print(f"[red]Error:[/red] {e}")
    raise typer.Exit(1) from e
```

### Configuration

```python
def _initialize_impl(self) -> None:
    if self._config:
        setting = self._config.config.get("setting", "default")
```

## Testing Examples

```python
import pytest
from hello_plugin import HelloPlugin

def test_hello_plugin():
    plugin = HelloPlugin()
    metadata = plugin.metadata()

    assert metadata.name == "hello-plugin"
    assert metadata.version == "1.0.0"
```

## Resources

- **Plugin System Guide**: `/docs/PLUGIN_SYSTEM.md`
- **Development Guide**: `/docs/PLUGIN_DEVELOPMENT_GUIDE.md`
- **API Documentation**: See `specify_cli.plugins.api`

## Contributing

If you create a useful plugin based on these examples, consider:
- Publishing it to PyPI
- Sharing in GitHub discussions
- Contributing to the official plugin registry

## Support

- Open an issue for bugs or questions
- Check documentation for detailed guides
- Explore the source code for more examples
