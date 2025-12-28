# Sync RDF to Generated Files

Run the ggen transformation pipeline to generate files from RDF sources.

## Usage
```
/sync-rdf
```

## Instructions

Execute the constitutional equation transformation:
```
spec.md = μ(feature.ttl)
```

Steps:
1. Run `ggen sync` to transform RDF to generated files
2. Report which files were generated/updated
3. Run tests to verify the transformation
4. Check for any SHACL validation errors

```bash
ggen sync
```

After sync:
1. List files that were modified
2. Run `uv run pytest tests/ -v` to verify
3. Report any issues or warnings

Remember: Generated files are build artifacts - never edit them manually!
