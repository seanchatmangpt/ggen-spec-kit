# 29. Multi-Target Emission

★

*One specification, many artifacts. Multi-target emission generates different outputs from the same source—code, documentation, tests, schemas—maintaining consistency across formats.*

---

A single command specification might generate:
- Python implementation code
- CLI documentation
- Test stubs
- API schema definitions
- Man pages
- Shell completions

Each format serves different consumers. Developers need code. Users need documentation. CI needs tests. All need consistency.

Multi-target emission generates all these from the same source specification. When the specification changes, all artifacts update together.

**The problem: Maintaining consistency across multiple output formats requires either manual synchronization (error-prone) or generation from a single source (this pattern).**

---

**The forces at play:**

- *Consumers want their format.* Developers want code. Users want docs.

- *Consistency wants single source.* Multiple sources drift.

- *Complexity wants simplicity.* Many templates are hard to maintain.

- *Specialization wants optimization.* Each format has its own concerns.

The tension: serve diverse consumers from a single source without creating maintenance burden.

---

**Therefore:**

Configure multiple emission targets in ggen.toml, each producing different output from the same or related sources.

**Configuration:**

```toml
# ggen.toml
[source]
default = "ontology/cli-commands.ttl"
shape = "shapes/command-shape.ttl"

# Target 1: Python implementation
[[targets]]
name = "python-commands"
query = "sparql/command-extract.rq"
template = "templates/command.py.tera"
output = "src/commands/{{ name }}.py"

# Target 2: Documentation
[[targets]]
name = "command-docs"
query = "sparql/command-docs-extract.rq"
template = "templates/command.md.tera"
output = "docs/commands/{{ name }}.md"

# Target 3: Test stubs
[[targets]]
name = "command-tests"
query = "sparql/command-extract.rq"
template = "templates/command-test.py.tera"
output = "tests/e2e/test_{{ name }}.py"

# Target 4: Shell completions
[[targets]]
name = "completions"
query = "sparql/completions-extract.rq"
template = "templates/completions.bash.tera"
output = "completions/specify.bash"

# Target 5: Index pages
[[targets]]
name = "command-index"
query = "sparql/command-list-extract.rq"
template = "templates/command-index.md.tera"
output = "docs/commands/index.md"
```

**Generation flow:**

```
                    cli-commands.ttl
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    command.rq      docs.rq         test.rq
          │               │               │
          ▼               ▼               ▼
    command.tera    docs.tera       test.tera
          │               │               │
          ▼               ▼               ▼
    validate.py   validate.md   test_validate.py
```

**Query specialization:**

Different targets may need different data shapes:

```sparql
# command-extract.rq - for code generation
SELECT ?name ?description ?argName ?argType ?argRequired
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?name ;
         sk:description ?description ;
         cli:hasArgument ?arg .
    ?arg sk:name ?argName ;
         cli:type ?argType ;
         cli:required ?argRequired .
}
```

```sparql
# command-docs-extract.rq - for documentation
SELECT ?name ?description ?argName ?argHelp ?example ?rationale
WHERE {
    ?cmd a cli:Command ;
         rdfs:label ?name ;
         sk:description ?description ;
         sk:rationale ?rationale .
    OPTIONAL {
        ?cmd cli:hasArgument ?arg .
        ?arg sk:name ?argName ;
             cli:help ?argHelp .
    }
    OPTIONAL { ?cmd sk:example ?example }
}
```

**Coordinated generation:**

```bash
# Generate all targets
ggen sync

# Generate specific target
ggen sync --target python-commands

# Generate documentation targets only
ggen sync --target command-docs --target command-index
```

---

**Resulting context:**

After applying this pattern, you have:

- Multiple output formats from single source
- Guaranteed consistency across formats
- Flexible addition of new targets
- Maintainable template collection

This extends **[Template Emission](./template-emission.md)** and produces **[Human-Readable Artifacts](./human-readable-artifact.md)**.

---

**Related patterns:**

- *Extends:* **[24. Template Emission](./template-emission.md)** — Multiple templates
- *Produces:* **[30. Human-Readable Artifact](./human-readable-artifact.md)** — Various formats
- *Uses:* **[23. Extraction Query](./extraction-query.md)** — Format-specific queries
- *Enables:* **[45. Living Documentation](../evolution/living-documentation.md)** — Docs stay synced

---

> *"Don't Repeat Yourself—even across languages and formats."*

Multi-target emission is DRY across the entire artifact space, not just within code.
