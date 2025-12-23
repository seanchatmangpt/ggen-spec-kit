# 45. Living Documentation

★★★

*Documentation that maintains itself. Living documentation is generated from specifications, ensuring accuracy through the constitutional equation. When specs change, docs change. This is how you achieve documentation that never lies.*

---

## The Documentation Paradox

Documentation is essential. Without it, users can't learn, developers can't maintain, and knowledge dies with its creators.

Yet documentation routinely fails:

- It becomes stale within weeks of writing
- It contradicts the actual behavior
- It omits critical details
- It describes features that no longer exist
- It ignores features that were recently added

This isn't because writers are lazy. It's because manual documentation is structurally doomed. Code changes constantly. Documentation requires separate effort. When priorities conflict, code wins. Docs decay.

The paradox: documentation is essential, yet traditional documentation is unsustainable.

Living documentation resolves this paradox. Instead of maintaining documentation separately, generate it from specifications. The same source that drives code also drives docs. When one changes, both change.

```
spec.ttl → μ → code
          ↘
            docs
```

The constitutional equation extends to documentation:

```
docs.md = μ(spec.ttl)
```

---

## The Stale Documentation Problem

**The fundamental problem: Manual documentation becomes stale because it requires separate maintenance effort. Living documentation stays accurate because it's generated from the same source as code.**

Consider the lifecycle of manual documentation:

```
Day 1:
  Code: validate(file) → returns errors
  Docs: "validate returns errors"
        ✓ Accurate!

Day 30:
  Code: validate(file) → returns errors + warnings
  Docs: "validate returns errors"
        ✗ Incomplete (but not updated)

Day 60:
  Code: validate(file, strict=False) → returns errors + warnings
  Docs: "validate returns errors"
        ✗ Missing new parameter

Day 90:
  New developer reads docs
  Writes code based on docs
  Code fails because behavior differs
  "The docs are wrong!"
```

Manual docs require someone to:
1. Notice that code changed
2. Remember that docs need updating
3. Find time to update docs
4. Know what the docs should say
5. Actually make the update

Any break in this chain causes staleness.

### The Duplication Tax

Manual documentation duplicates information:
- What parameters does a command accept?
- What does each parameter do?
- What are the valid values?
- What errors can occur?

This information exists in code (or specs). Duplicating it in docs creates a synchronization problem. Every change requires two updates. Miss one, and they diverge.

### The Coverage Gap

Manual docs typically cover:
- The happy path
- Common use cases
- Whatever the writer thought of

They often miss:
- Error cases
- Edge cases
- Newly added features
- Recently changed behavior

Generated docs can be comprehensive—covering everything the spec defines.

---

## The Forces

### Force: Accuracy Wants Generation

*Generated docs are always accurate because they derive from the same source as code.*

Generation eliminates the synchronization problem. There's no duplication, so there's no divergence.

**Resolution:** Generate documentation from specifications. Make accuracy structural, not effortful.

### Force: Comprehensiveness Wants Automation

*Generated docs can cover everything. Manual docs cover whatever the writer remembered.*

Automation is thorough. It includes every parameter, every option, every error. Manual documentation is selective—and selections often miss important details.

**Resolution:** Generate comprehensive reference documentation. Reserve manual effort for tutorials and explanations.

### Force: Readability Wants Care

*Generated text can be mechanical. Good documentation needs human touch.*

Pure generation can produce dry, mechanical text. "Parameter X: Type Y. Default: Z." Accurate but uninspiring.

**Resolution:** Combine generation with templates. Generate structure and facts; templates provide prose and explanation. Include narrative in specifications.

### Force: Discoverability Wants Navigation

*Documentation must be findable. Generated structure enables consistent navigation.*

Manual docs often have inconsistent organization. What section is this feature in? Different writers organize differently.

**Resolution:** Generate consistent structure. Every command follows the same format. Every pattern has the same sections. Predictability enables discovery.

---

## Therefore

**Generate documentation from specifications using the transformation pipeline. Use templates to maintain readability. Reserve manual documentation for tutorials, explanations, and concepts that don't fit generation.**

### The Documentation Hierarchy

```
┌───────────────────────────────────────────────────────────────────────────────┐
│  LIVING DOCUMENTATION HIERARCHY                                                │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 1: GENERATED REFERENCE                                             │  │
│  │                                                                          │  │
│  │ Source: Specifications (spec.ttl)                                        │  │
│  │ Method: μ transformation                                                 │  │
│  │ Freshness: Always current                                                │  │
│  │                                                                          │  │
│  │ Contents:                                                                │  │
│  │   • Command reference (parameters, options, examples)                    │  │
│  │   • API documentation (endpoints, schemas, responses)                    │  │
│  │   • Configuration reference (all options, defaults, validation)          │  │
│  │   • Schema documentation (classes, properties, shapes)                   │  │
│  │   • Error catalog (all error codes, causes, solutions)                   │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 2: SEMI-GENERATED GUIDES                                           │  │
│  │                                                                          │  │
│  │ Source: Specification + Manual narrative                                 │  │
│  │ Method: Template rendering with facts from spec                          │  │
│  │ Freshness: Current facts, stable narrative                               │  │
│  │                                                                          │  │
│  │ Contents:                                                                │  │
│  │   • Quick start (generated commands + manual explanation)                │  │
│  │   • Migration guides (generated diffs + manual advice)                   │  │
│  │   • Troubleshooting (generated error list + manual solutions)            │  │
│  │   • Best practices (generated examples + manual guidance)                │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ LAYER 3: MANUAL CONCEPTS                                                 │  │
│  │                                                                          │  │
│  │ Source: Human expertise                                                  │  │
│  │ Method: Traditional writing                                              │  │
│  │ Freshness: Requires maintenance                                          │  │
│  │                                                                          │  │
│  │ Contents:                                                                │  │
│  │   • Philosophy and principles                                            │  │
│  │   • Architecture explanations                                            │  │
│  │   • Tutorials and walkthroughs                                           │  │
│  │   • Case studies and examples                                            │  │
│  │   • Design decisions and rationale                                       │  │
│  │                                                                          │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                │
└───────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation

### Documentation Specification in RDF

```turtle
# memory/documentation.ttl
@prefix docs: <http://github.com/spec-kit/docs#> .
@prefix sk: <http://github.com/spec-kit/schema#> .
@prefix cli: <http://github.com/spec-kit/cli#> .

# ============================================================================
# Documentation Schema
# ============================================================================

docs:Document a rdfs:Class ;
    rdfs:label "Document" ;
    rdfs:comment "A documentation artifact generated from specification" .

docs:CommandReference a docs:Document ;
    rdfs:label "Command Reference" ;
    docs:sourceSpec cli:ValidateCommand ;
    docs:template <templates/command-reference.tera> ;
    docs:output <docs/commands/validate.md> ;
    docs:includes [
        docs:section "Synopsis" ;
        docs:section "Description" ;
        docs:section "Arguments" ;
        docs:section "Options" ;
        docs:section "Examples" ;
        docs:section "Exit Codes" ;
        docs:section "See Also"
    ] .

# ============================================================================
# Content from Specification (generated into docs)
# ============================================================================

cli:ValidateCommand
    sk:description """
        Validate RDF files against SHACL shapes.

        The validate command checks RDF/Turtle files for syntax errors and
        validates them against defined SHACL shapes. It supports both single
        file and batch validation modes.

        For large files (>1MB), streaming validation is automatically enabled
        to maintain performance. Use --strict mode for comprehensive validation
        that catches additional style and consistency issues.
    """ ;

    sk:usage """
        # Validate a single file
        specify validate schema.ttl

        # Validate with strict mode
        specify validate --strict schema.ttl

        # Validate multiple files
        specify validate ontology/*.ttl

        # Output validation results as JSON
        specify validate --format json schema.ttl
    """ ;

    sk:exitCodes [
        sk:code 0 ;
        sk:meaning "Validation successful, no errors found"
    ], [
        sk:code 1 ;
        sk:meaning "Validation failed, errors found"
    ], [
        sk:code 2 ;
        sk:meaning "File not found or not readable"
    ], [
        sk:code 3 ;
        sk:meaning "Invalid SHACL shapes file"
    ] ;

    sk:seeAlso cli:CheckCommand, cli:InitCommand .
```

### Documentation Template

```jinja2
{# templates/command-reference.tera #}
# {{ command.label }}

{{ command.description }}

## Synopsis

```
specify {{ command.label }} [OPTIONS] {{ command.arguments | map(attribute="name") | join(" ") }}
```

## Description

{{ command.description | extended }}

{% if command.hasArgument %}
## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
{% for arg in command.hasArgument %}
| `{{ arg.name }}` | {{ arg.type }} | {{ arg.required | yesno }} | {{ arg.help }} |
{% endfor %}
{% endif %}

{% if command.hasOption %}
## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
{% for opt in command.hasOption %}
| `{{ opt.name }}` | {{ opt.type }} | {{ opt.default | default("none") }} | {{ opt.help }} |
{% endfor %}
{% endif %}

{% if command.usage %}
## Examples

```bash
{{ command.usage }}
```
{% endif %}

{% if command.exitCodes %}
## Exit Codes

| Code | Meaning |
|------|---------|
{% for exit in command.exitCodes %}
| {{ exit.code }} | {{ exit.meaning }} |
{% endfor %}
{% endif %}

{% if command.deprecation %}
## Deprecation Notice

> **Warning**: This command is deprecated and will be removed on {{ command.deprecation.removalDate }}.
>
> Use `{{ command.deprecation.alternative.label }}` instead.
>
> See [Migration Guide]({{ command.deprecation.migrationGuide }}) for details.
{% endif %}

{% if command.seeAlso %}
## See Also

{% for related in command.seeAlso %}
- [`{{ related.label }}`](./{{ related.label }}.md) - {{ related.description | truncate(60) }}
{% endfor %}
{% endif %}

---

*This documentation was generated from specification. Last updated: {{ now() | date }}*
*Source: `ontology/cli-commands.ttl`*
```

### Generated Documentation Example

```markdown
# validate

Validate RDF files against SHACL shapes.

## Synopsis

```
specify validate [OPTIONS] FILE
```

## Description

Validate RDF files against SHACL shapes.

The validate command checks RDF/Turtle files for syntax errors and
validates them against defined SHACL shapes. It supports both single
file and batch validation modes.

For large files (>1MB), streaming validation is automatically enabled
to maintain performance. Use --strict mode for comprehensive validation
that catches additional style and consistency issues.

## Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `FILE` | Path | Yes | Path to the RDF file to validate |

## Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--strict` | bool | false | Enable strict mode validation |
| `--format` | string | text | Output format (text, json, sarif) |
| `--stream` | bool | auto | Use streaming validation for large files |
| `--shapes` | Path | none | Custom SHACL shapes file |

## Examples

```bash
# Validate a single file
specify validate schema.ttl

# Validate with strict mode
specify validate --strict schema.ttl

# Validate multiple files
specify validate ontology/*.ttl

# Output validation results as JSON
specify validate --format json schema.ttl
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation successful, no errors found |
| 1 | Validation failed, errors found |
| 2 | File not found or not readable |
| 3 | Invalid SHACL shapes file |

## See Also

- [`check`](./check.md) - Check tool availability
- [`init`](./init.md) - Initialize a new project

---

*This documentation was generated from specification. Last updated: 2025-02-15*
*Source: `ontology/cli-commands.ttl`*
```

---

## Verifying Documentation

Living documentation should be verified like any other artifact:

```yaml
# .github/workflows/docs.yml
name: Documentation Verification

on:
  push:
    branches: [main]
    paths:
      - 'ontology/**'
      - 'memory/**'
      - 'templates/**'
  pull_request:
    paths:
      - 'ontology/**'
      - 'memory/**'
      - 'templates/**'

jobs:
  verify-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup
        run: pip install ggen specify-cli

      - name: Regenerate documentation
        run: ggen sync

      - name: Check for drift
        run: |
          if ! git diff --exit-code docs/; then
            echo "Documentation is out of sync with specifications"
            echo "Run 'ggen sync' to update"
            git diff docs/
            exit 1
          fi

      - name: Verify internal links
        run: |
          # Check that all links in docs resolve
          specify docs verify --check-links

      - name: Check for completeness
        run: |
          # Verify all commands have documentation
          specify docs verify --check-coverage
```

---

## Living Documentation Properties

| Property | Traditional | Living |
|----------|-------------|--------|
| Accuracy | Degrades over time | Always matches source |
| Maintenance | Manual effort | Automatic |
| Consistency | Varies by author | Guaranteed by template |
| Coverage | Often incomplete | Complete by construction |
| Trust | Uncertain | Verifiable through receipts |
| Staleness detection | Manual audit | Automatic drift detection |
| Update frequency | Sporadic | Every build |

---

## Case Study: The Self-Maintaining Docs

*A team achieves documentation that never goes stale.*

### The Before

The DocDebt team had a documentation problem:

- 47 CLI commands
- 23 documented (49%)
- 15 accurate (32%)
- 8 completely wrong

Every release, they'd try to update docs. Every release, they'd miss some. Documentation was a constant source of support tickets.

"Why doesn't `--format` work like the docs say?"
"What does `--strict` actually do?"
"The example command doesn't exist."

### The Transformation

They migrated to living documentation:

**Week 1: Specification Enhancement**
```turtle
# Added documentation fields to every command
cli:ValidateCommand
    sk:description """...""" ;
    sk:usage """...""" ;
    sk:exitCodes [...] ;
    ...
```

**Week 2: Template Creation**
```jinja2
{# Created comprehensive templates #}
# {{ command.label }}
{{ command.description }}
## Options
...
```

**Week 3: Generation Pipeline**
```bash
# Configured ggen for docs
ggen sync  # Now generates docs too
```

**Week 4: CI Integration**
```yaml
# Docs drift caught in CI
- name: Check docs
  run: |
    ggen sync
    git diff --exit-code docs/
```

### The Results

After 3 months:

| Metric | Before | After |
|--------|--------|-------|
| Commands documented | 23/47 (49%) | 47/47 (100%) |
| Accurate documentation | 15/47 (32%) | 47/47 (100%) |
| Doc-related support tickets | 12/week | 1/week |
| Time spent on docs | 8 hrs/week | 0 hrs/week |
| Docs updated on release | Sometimes | Always |

The documentation maintained itself. Spec changes propagated automatically. No more manual documentation effort.

---

## Anti-Patterns

### Anti-Pattern: Dual Source of Truth

*"We have specs and we have docs—they're both sources of truth."*

If both are sources of truth, neither is. They will diverge.

**Resolution:** Specs are the source of truth. Docs are generated. One direction only.

### Anti-Pattern: Generation Without Verification

*"We generate docs but don't check if they're right."*

Generated docs can have broken links, missing sections, or template errors.

**Resolution:** Verify generated docs in CI. Check links, coverage, and correctness.

### Anti-Pattern: All Manual

*"Generation is too complex. We'll just write docs manually."*

Manual docs will decay. It's not a question of if, but when.

**Resolution:** Start simple. Generate reference docs first. Expand gradually.

---

## Implementation Checklist

### Specification Setup

- [ ] Add documentation fields to schema (description, usage, examples)
- [ ] Document all commands in specifications
- [ ] Include exit codes and error messages
- [ ] Add deprecation information
- [ ] Include cross-references (seeAlso)

### Template Creation

- [ ] Create command reference template
- [ ] Create schema reference template
- [ ] Create error catalog template
- [ ] Test templates with sample data

### Generation Pipeline

- [ ] Configure ggen for documentation
- [ ] Set up SPARQL queries for extraction
- [ ] Configure output paths
- [ ] Test full generation

### Verification

- [ ] Add link checking
- [ ] Add coverage checking
- [ ] Add drift detection
- [ ] Configure CI for docs

---

## Resulting Context

After implementing this pattern, you have:

- **Documentation that never lies** — generated from source of truth
- **Complete coverage** — every capability documented
- **Consistent format** — templates ensure uniformity
- **Zero maintenance overhead** — updates are automatic
- **Verified accuracy** — CI catches drift

Living documentation transforms documentation from burden to benefit. It's always accurate, always complete, always current.

---

## Related Patterns

- **Uses:** **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — docs = μ(spec)
- **Uses:** **[23. Template Emission](../transformation/template-emission.md)** — Templates for docs
- **Verified by:** **[35. Drift Detection](../verification/drift-detection.md)** — Catch doc drift
- **Updated by:** **[42. Specification Refinement](./specification-refinement.md)** — Specs change, docs follow

---

## Philosophical Note

> *"Documentation is a love letter that you write to your future self."*
>
> — Damian Conway

If documentation is a love letter, then stale documentation is a broken promise. It says "I care about you" but delivers confusion and frustration.

Living documentation keeps the promise. It stays accurate because it can't help but be accurate. It's generated from the same truth that drives the code. When one changes, both change.

Write your love letters in specifications. Let the transformation deliver them accurately, forever.

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
