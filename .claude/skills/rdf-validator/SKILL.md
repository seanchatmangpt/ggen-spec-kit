---
name: rdf-validator
description: Validate RDF/Turtle syntax and SHACL shape constraints. Use when checking TTL files for syntax errors, validating against SHACL shapes, or ensuring ontology compliance.
allowed-tools: Read, Glob, Grep, Bash
---

# RDF Validator

Validate Turtle syntax, SHACL shapes, and RDF quality.

## Instructions

1. Check Turtle syntax is parseable
2. Verify SHACL shape constraints
3. Check class and property usage
4. Validate cross-references
5. Ensure best practices

## Validation Commands

### Syntax Validation
```bash
uv run python -c "
from rdflib import Graph
g = Graph()
g.parse('path/to/file.ttl', format='turtle')
print(f'✅ Valid: {len(g)} triples')
"
```

### Validate All TTL Files
```bash
for f in $(find . -name "*.ttl" -type f); do
    echo -n "Validating $f... "
    uv run python -c "from rdflib import Graph; Graph().parse('$f')" 2>/dev/null && echo "✅" || echo "❌"
done
```

### SHACL Validation
```bash
uv run python -c "
from pyshacl import validate
from rdflib import Graph

data = Graph().parse('path/to/data.ttl')
shapes = Graph().parse('ontology/spec-kit-docs-extension.ttl')

conforms, _, text = validate(data, shacl_graph=shapes)
print('Conforms:', conforms)
if not conforms: print(text)
"
```

## Common Issues

### Prefix Not Defined
```turtle
# ❌ Error
sk:Feature a sk:Class .

# ✅ Fix
@prefix sk: <http://github.com/github/spec-kit#> .
sk:Feature a sk:Class .
```

### Missing Period
```turtle
# ❌ Error
sk:Feature a sk:Class ;
    sk:label "Feature"

# ✅ Fix
sk:Feature a sk:Class ;
    sk:label "Feature" .
```

### Invalid Datatype
```turtle
# ❌ Error
sk:Release sk:date "2025-12-20" .

# ✅ Fix
sk:Release sk:date "2025-12-20"^^xsd:date .
```

## Output Format

```markdown
## RDF Validation Report

### Files Validated
| File | Triples | Status |
|------|---------|--------|
| file.ttl | 35 | ✅ Valid |

### Syntax Errors
[None / List]

### SHACL Violations
[None / List]

### Overall: ✅ VALID / ❌ ERRORS
```
