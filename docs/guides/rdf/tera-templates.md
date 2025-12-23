# How-to: Write Tera Code Generation Templates

**Goal:** Create templates to generate code from specifications
**Time:** 30-35 minutes | **Level:** Advanced

## Tera Basics

```jinja
@app.command()
def {{ label }}():
    """{{ description }}"""
    pass
```

## Template Variables

From SPARQL query results:

```
{
  "label": "hello",
  "description": "Greet user",
  "module": "specify_cli.commands.hello"
}
```

## Template Syntax

### Variables
```jinja
{{ label }}
{{ description }}
```

### Conditionals
```jinja
{% if required %}
{{ name }}: str = typer.Argument(...)
{% else %}
{{ name }}: str = typer.Option(None)
{% endif %}
```

### Loops
```jinja
{% for arg in arguments %}
    {{ arg.name }}: {{ arg.type }} = typer.Argument(...)
{% endfor %}
```

### Filters
```jinja
{{ label | uppercase }}
{{ description | truncate(length=100) }}
```

## Full Example

**Template: command.tera**
```jinja
import typer
from specify_cli.core.cli import app
from specify_cli.ops.{{ label }} import {{ label }}_operation

@app.command()
def {{ label }}(
    {%- for arg in arguments %}
    {{ arg.name }}: {{ arg.type }} = typer.Argument(
        ..., help="{{ arg.description }}"
    ){{ "," if not loop.last }}
    {%- endfor %}
):
    """{{ description }}"""
    result = {{ label }}_operation({% for arg in arguments %}{{ arg.name }}{{ "," if not loop.last }}{% endfor %})
    typer.echo(result)
```

## Integration with ggen

```toml
[transformation]
source = "ontology/cli-commands.ttl"
sparql = "sparql/command-extract.rq"
template = "templates/command.tera"
output = "src/specify_cli/commands/{{ label }}.py"
```

## Best Practices

✅ Use consistent formatting
✅ Clear variable names
✅ Handle edge cases
✅ Test with multiple inputs
✅ Document templates

See: `templates/` directory for examples
