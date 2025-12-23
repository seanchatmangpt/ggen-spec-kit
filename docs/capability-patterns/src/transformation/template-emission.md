# 24. Template Emission

★★

*Data alone is not output. Template emission (μ₃) renders extracted data through templates, producing human-readable artifacts—code, documentation, configuration.*

---

After **[Extraction](./extraction-query.md)**, you have structured data. But data isn't the artifact. You need Markdown documentation, Python code, YAML configuration, HTML pages.

Template emission bridges this gap. Templates define the shape of output; data fills in the specifics. The combination produces artifacts that are both consistent (from templates) and specific (from data).

This is the creative act of the transformation pipeline. Extraction discovers what exists. Emission expresses it in the target format.

**The problem: Extracted data must be rendered into various output formats. Hardcoded generation is inflexible. Templates provide controlled flexibility.**

---

**The forces at play:**

- *Consistency wants standardization.* Generated artifacts should follow patterns.

- *Expressiveness wants flexibility.* Different specifications need different output.

- *Maintainability wants simplicity.* Complex templates become unmanageable.

- *Power wants features.* Conditionals, loops, filters enable rich generation.

The tension: powerful enough to generate diverse output, simple enough to maintain.

---

**Therefore:**

Implement emission (μ₃) using a template engine (Tera, Jinja2, Handlebars) that renders extracted data into target format.

**Template structure (Tera):**

```jinja
{# templates/command.py.tera #}
"""{{ description }}

Auto-generated from RDF specification. DO NOT EDIT.
Source: {{ source_file }}
Generated: {{ generated_at }}
"""
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(help="{{ description }}")

@app.command()
def {{ name | replace(from="-", to="_") }}(
    {% for arg in arguments %}
    {{ arg.name }}: {% if arg.type == "Path" %}Path{% else %}{{ arg.type }}{% endif %}{% if not arg.required %} = None{% endif %},
    {% endfor %}
) -> None:
    """{{ description }}"""
    # Implementation delegated to ops layer
    from specify_cli import ops
    result = ops.{{ name | replace(from="-", to="_") }}.execute(
        {% for arg in arguments %}
        {{ arg.name }}={{ arg.name }},
        {% endfor %}
    )
    _display_result(result)
```

**Data input:**

```json
{
  "name": "validate",
  "description": "Validate RDF files against SHACL shapes",
  "source_file": "ontology/cli-commands.ttl",
  "generated_at": "2025-01-15T10:30:00Z",
  "arguments": [
    {"name": "file", "type": "Path", "required": true},
    {"name": "output", "type": "Path", "required": false}
  ]
}
```

**Generated output:**

```python
"""Validate RDF files against SHACL shapes

Auto-generated from RDF specification. DO NOT EDIT.
Source: ontology/cli-commands.ttl
Generated: 2025-01-15T10:30:00Z
"""
import typer
from typing import Optional
from pathlib import Path

app = typer.Typer(help="Validate RDF files against SHACL shapes")

@app.command()
def validate(
    file: Path,
    output: Path = None,
) -> None:
    """Validate RDF files against SHACL shapes"""
    from specify_cli import ops
    result = ops.validate.execute(
        file=file,
        output=output,
    )
    _display_result(result)
```

**Template features:**

**Conditionals:**
```jinja
{% if arg.required %}
{{ arg.name }}: {{ arg.type }}
{% else %}
{{ arg.name }}: Optional[{{ arg.type }}] = None
{% endif %}
```

**Loops:**
```jinja
{% for arg in arguments %}
- {{ arg.name }}: {{ arg.help }}
{% endfor %}
```

**Filters:**
```jinja
{{ name | upper }}
{{ description | truncate(length=80) }}
{{ name | replace(from="-", to="_") }}
```

**Includes:**
```jinja
{% include "partials/header.tera" %}
{% include "partials/imports.tera" %}
```

**Template organization:**

```
templates/
├── command.py.tera         # Python command generation
├── command-test.py.tera    # Test generation
├── command.md.tera         # Documentation generation
├── api-schema.yaml.tera    # API schema generation
└── partials/
    ├── header.tera         # Common header
    ├── imports.tera        # Common imports
    └── docstring.tera      # Docstring format
```

---

**Resulting context:**

After applying this pattern, you have:

- Artifacts generated from data + templates
- Consistent structure across generated files
- Maintainable templates separate from data
- Clear provenance in generated files

This precedes **[Canonicalization](./canonicalization.md)** and contributes to **[Receipt Generation](./receipt-generation.md)**.

---

**Related patterns:**

- *Part of:* **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₃
- *Follows:* **[23. Extraction Query](./extraction-query.md)** — Receives structured data
- *Precedes:* **[25. Canonicalization](./canonicalization.md)** — Output needs normalizing
- *Supports:* **[29. Multi-Target Emission](./multi-target-emission.md)** — Multiple formats

---

> *"Content is king, but context is God."*

In template emission, data is content and templates are context. Together they produce meaningful artifacts.
