# Reference: Configuration Files

All configuration files and options.

## ggen.toml

Main transformation configuration.

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

## pyproject.toml

Python project configuration.

```toml
[project]
name = "specify-cli"
version = "0.0.25"
description = "RDF-first specification development"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src"

[tool.coverage.run]
source = ["src"]

[tool.mypy]
python_version = "3.11"
strict = true
```

## docfx.json

Documentation generation configuration.

```json
{
  "metadata": [
    {
      "src": "docs",
      "dest": "_site"
    }
  ]
}
```

See also: Environment variables in `.env`
