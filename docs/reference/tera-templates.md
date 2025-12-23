# Reference: Tera Template Syntax

Complete Tera template syntax for code generation.

## Variables

```jinja
{{ variable }}
{{ object.property }}
{{ array[0] }}
```

## Filters

```jinja
{{ text | uppercase }}
{{ text | lowercase }}
{{ text | truncate(length=50) }}
{{ number | round(precision=2) }}
{{ list | join(separator=", ") }}
{{ text | replace(from="old", to="new") }}
```

## Conditionals

```jinja
{% if condition %}
  ... content ...
{% elif other_condition %}
  ... content ...
{% else %}
  ... content ...
{% endif %}
```

## Loops

```jinja
{% for item in items %}
  {{ item.name }}
{% endfor %}

{% for item in items %}
  {{ item }}{{ "," if not loop.last }}
{% endfor %}
```

Loop variables:
- `loop.index` - 1-based index
- `loop.first` - True if first iteration
- `loop.last` - True if last iteration

## Includes

```jinja
{% include "other_template.tera" %}
```

## Macros

```jinja
{% macro render_command(name, description) %}
  @app.command()
  def {{ name }}():
      """{{ description }}"""
      pass
{% endmacro %}

{{ render_command("hello", "Greet user") }}
```

## Comments

```jinja
{# This is a comment #}
```

See: `templates/` directory for examples
