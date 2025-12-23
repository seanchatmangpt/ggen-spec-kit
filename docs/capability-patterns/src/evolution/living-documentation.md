# 45. Living Documentation

★★

*Documentation that lies is worse than no documentation. Living documentation is generated from specifications and updated automatically—always accurate, always current.*

---

Traditional documentation:
- Written separately from code
- Maintained by humans
- Eventually becomes stale
- Trusted until it fails you

Living documentation:
- Generated from specifications
- Updated automatically
- Always matches reality
- Trusted because it's proven

The **[Constitutional Equation](../transformation/constitutional-equation.md)** applies to documentation too:

```
docs.md = μ(feature.ttl)
```

Documentation is a generated artifact. When specifications change, documentation updates automatically.

**The problem: Manual documentation drifts from reality. Living documentation is reality—generated from the same source that generates code.**

---

**The forces at play:**

- *Writing wants freedom.* Generated docs feel constrained.

- *Accuracy wants generation.* Manual docs become stale.

- *Readers want humanity.* Generated docs can feel robotic.

- *Maintenance wants automation.* Manual updates are forgotten.

The tension: accurate through generation, human through careful template design.

---

**Therefore:**

Generate documentation from the same RDF specifications that generate code, using templates designed for human readers.

**Documentation specification:**

```turtle
cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;
    sk:rationale """
        Users need confidence their RDF is correct before committing.
        Manual inspection is slow and unreliable. Automated validation
        catches errors instantly.
    """ ;
    sk:usageScenario """
        Developer finishes editing ontology.ttl, runs
        'specify validate ontology.ttl', sees "Valid ✓",
        and commits with confidence.
    """ ;
    sk:example [
        sk:title "Basic validation" ;
        sk:command "specify validate ontology.ttl" ;
        sk:output "Valid ✓"
    ] ;
    sk:example [
        sk:title "Strict mode" ;
        sk:command "specify validate --strict schema.ttl" ;
        sk:output "Valid ✓ (strict mode)"
    ] .
```

**Documentation template:**

```jinja
{# templates/command-docs.md.tera #}
# {{ name }}

{{ description }}

{% if rationale %}
## Why This Command Exists

{{ rationale }}
{% endif %}

## Usage

```bash
specify {{ name }} [options] <arguments>
```

{% if usageScenario %}
## Example Scenario

{{ usageScenario }}
{% endif %}

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
{% for arg in arguments %}
| `{{ arg.name }}` | {{ arg.type }} | {{ "Yes" if arg.required else "No" }} | {{ arg.help }} |
{% endfor %}

{% if options %}
## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
{% for opt in options %}
| `{{ opt.name }}` | {{ opt.type }} | {{ opt.default }} | {{ opt.help }} |
{% endfor %}
{% endif %}

{% if examples %}
## Examples

{% for example in examples %}
### {{ example.title }}

```bash
{{ example.command }}
```

{% if example.output %}
Output:
```
{{ example.output }}
```
{% endif %}
{% endfor %}
{% endif %}

---

> **Generated Documentation**
>
> This page was generated from [`{{ source_file }}`]({{ source_url }}).
> Last generated: {{ generated_at }}
>
> To update this documentation, edit the source specification and run `ggen sync`.
```

**Generated documentation:**

```markdown
# validate

Validate RDF files against SHACL shapes.

## Why This Command Exists

Users need confidence their RDF is correct before committing.
Manual inspection is slow and unreliable. Automated validation
catches errors instantly.

## Usage

```bash
specify validate [options] <arguments>
```

## Example Scenario

Developer finishes editing ontology.ttl, runs
'specify validate ontology.ttl', sees "Valid ✓",
and commits with confidence.

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `file` | Path | Yes | File to validate |

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--strict` | bool | false | Enable strict mode |

## Examples

### Basic validation

```bash
specify validate ontology.ttl
```

Output:
```
Valid ✓
```

### Strict mode

```bash
specify validate --strict schema.ttl
```

Output:
```
Valid ✓ (strict mode)
```

---

> **Generated Documentation**
>
> This page was generated from [`ontology/cli-commands.ttl`](../ontology/cli-commands.ttl).
> Last generated: 2025-01-15T10:30:00Z
>
> To update this documentation, edit the source specification and run `ggen sync`.
```

**Living documentation properties:**

| Property | Traditional | Living |
|----------|-------------|--------|
| Accuracy | Degrades over time | Always matches source |
| Maintenance | Manual effort | Automatic |
| Consistency | Varies | Guaranteed |
| Coverage | Often incomplete | Complete by construction |
| Trust | Uncertain | Verifiable |

---

**Resulting context:**

After applying this pattern, you have:

- Documentation that's always accurate
- Automatic updates when specifications change
- Consistent format across all documentation
- Trust through generation

This completes the Evolution Patterns and the pattern language.

---

**Related patterns:**

- *Implements:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Docs as artifact
- *Uses:* **[18. Narrative Specification](../specification/narrative-specification.md)** — Human content
- *Generated by:* **[24. Template Emission](../transformation/template-emission.md)** — Doc generation
- *Reflects:* **[44. Deprecation Path](./deprecation-path.md)** — Deprecation visible

---

## The Pattern Language Complete

You've completed all 45 patterns in this pattern language:

**Part I: Context Patterns (1-8)** — Understanding the territory
**Part II: Specification Patterns (9-20)** — Capturing intent
**Part III: Transformation Patterns (21-30)** — Generating artifacts
**Part IV: Verification Patterns (31-38)** — Ensuring correctness
**Part V: Evolution Patterns (39-45)** — Growing over time

These patterns form a generative grammar for capability creation. Applied thoughtfully, they produce capabilities that:
- Serve real customer jobs
- Are specified precisely
- Generate consistent artifacts
- Verify their own correctness
- Evolve based on feedback

Return to the **[Pattern Map](../pattern-map.md)** to see how they connect, or consult the **[Pattern Index](../appendix/pattern-index.md)** for quick reference.

> *"A pattern language gives you the power to generate coherent, beautiful things."*
>
> — Christopher Alexander
