# Reference: RDF Schema (SHACL Shapes)

SHACL constraints that validate RDF specifications.

## Command Shape

Validates `sk:Command` instances.

**Required Properties:**
- `rdfs:label` - Command name (string)
- `sk:description` - What it does (string)
- `sk:hasModule` - Python module path (string)

**Optional Properties:**
- `sk:hasArgument` - Positional arguments
- `sk:hasOption` - Options/flags

**Constraints:**
- Label must be unique
- Module path must be valid
- Description must be non-empty

## Argument Shape

Validates `sk:Argument` instances.

**Required Properties:**
- `sk:name` - Argument name
- `sk:type` - Argument type (str, int, Path)
- `sk:required` - Boolean

**Optional Properties:**
- `sk:default` - Default value
- `sk:description` - Help text

## Option Shape

Validates `sk:Option` instances.

**Required Properties:**
- `sk:name` - Option name
- `sk:flag` - Boolean flag indicator

**Optional Properties:**
- `sk:default` - Default value
- `sk:description` - Help text

## Validation

```bash
ggen validate --shapes ontology/spec-kit-schema.ttl ontology/cli-commands.ttl
```

See file: `ontology/spec-kit-schema.ttl`
