---
paths:
  - "templates/**/*.tera"
  - "templates/**/*.jinja2"
---

# Template Rules

Render extracted SPARQL data into generated files. Add notice to all outputs.

## Syntax
```jinja2
{# Comment #}
{{ variable }}
{% if condition %}...{% endif %}
{% for item in items %}...{% endfor %}
{{ value | filter }}
```

## DO
- ✅ Add "Generated from RDF" notice
- ✅ Use meaningful variable names
- ✅ Preserve indentation in output
- ✅ Handle empty collections
- ✅ Use macros for patterns

## DON'T
- ❌ Remove generation notices
- ❌ Complex nested logic
- ❌ Hardcode values (use SPARQL data)
- ❌ Ignore empty collections

## Python Code Template
```jinja2
"""{{ description }}

Generated from RDF specification. DO NOT EDIT MANUALLY.
"""
from __future__ import annotations
import typer
from rich.console import Console
from specify_cli.ops import {{ name }}_ops

app = typer.Typer()
console = Console()

@app.command()
def {{ name }}(
    {% for arg in arguments %}
    {{ arg.name }}: {{ arg.type }},
    {% endfor %}
) -> None:
    """{{ description }}"""
    result = {{ name }}_ops.execute({{ name }}={{ name }})
    console.print(result)
```

## Doc Template
```jinja2
# {{ title }}
{{ description }}

## Usage
```bash
specify {{ command }}
```

{% for arg in arguments %}
- `{{ arg.name }}` - {{ arg.description }}
{% endfor %}
```

## Common Filters
- `upper`, `lower`, `title`, `trim`, `default("x")`
