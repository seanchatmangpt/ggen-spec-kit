---
paths:
  - "templates/**/*.tera"
  - "templates/**/*.jinja2"
---

# Template Rules

## Purpose
Tera templates render extracted SPARQL data into generated files.

## Syntax
```jinja2
{# Comment #}
{{ variable }}
{% if condition %}...{% endif %}
{% for item in items %}...{% endfor %}
{{ value | filter }}
```

## Python Code Template
```jinja2
{# templates/command.tera #}
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
    {{ arg.name }}: {{ arg.type }}{% if not arg.required %} = None{% endif %},
    {% endfor %}
) -> None:
    """{{ description }}"""
    result = {{ name }}_ops.execute(
        {% for arg in arguments %}
        {{ arg.name }}={{ arg.name }},
        {% endfor %}
    )
    console.print(result)
```

## Documentation Template
```jinja2
{# templates/doc.tera #}
# {{ title }}

{{ description }}

## Usage

```bash
specify {{ command }} {{ usage }}
```

## Arguments

{% for arg in arguments %}
- `{{ arg.name }}` - {{ arg.description }}{% if arg.required %} (required){% endif %}
{% endfor %}

## Examples

{% for example in examples %}
```bash
{{ example }}
```
{% endfor %}
```

## Filters
- `| upper` - Uppercase
- `| lower` - Lowercase
- `| title` - Title case
- `| trim` - Remove whitespace
- `| default("value")` - Default value

## Best Practices
- Add generation notice to output
- Preserve indentation
- Handle empty collections gracefully
- Use macros for repeated patterns
