# Reference: ggen.toml Configuration

Complete `docs/ggen.toml` configuration options.

## Main Section

```toml
[transformation]
source = "ontology/cli-commands.ttl"    # Input RDF file
sparql = "sparql/command-extract.rq"    # SPARQL query
template = "templates/command.tera"     # Output template
output = "src/specify_cli/commands/{name}.py"  # Output path
```

Output variables:
- `{name}` - From SPARQL query
- `{label}` - From SPARQL query
- Any column from SPARQL query

## Multiple Transformations

```toml
[[transformation]]
source = "ontology/cli-commands.ttl"
sparql = "sparql/command-extract.rq"
template = "templates/command.tera"
output = "src/specify_cli/commands/{name}.py"

[[transformation]]
source = "ontology/cli-commands.ttl"
sparql = "sparql/command-extract.rq"
template = "templates/test.tera"
output = "tests/e2e/test_commands_{name}.py"

[[transformation]]
source = "memory/documentation.ttl"
sparql = "sparql/docs-extract.rq"
template = "templates/docs.tera"
output = "docs/generated/{title}.md"
```

## Validation Section

```toml
[validation]
shapes = "ontology/spec-kit-schema.ttl"
```

SHACL shapes to validate RDF against.

## Receipt Section

```toml
[receipt]
enabled = true
format = "json"
algorithm = "sha256"
output = ".ggen-receipt.json"
```

Create cryptographic proof of transformation.

## Complete Example

```toml
[transformation]
source = "ontology/cli-commands.ttl"
sparql = "sparql/command-extract.rq"
template = "templates/command.tera"
output = "src/specify_cli/commands/{name}.py"

[validation]
shapes = "ontology/spec-kit-schema.ttl"

[receipt]
enabled = true
format = "json"
algorithm = "sha256"
```

See: `docs/ggen.toml`
