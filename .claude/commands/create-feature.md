# Create Feature (RDF-First)

Create a new feature following the RDF-first spec-driven approach.

## Usage
```
/create-feature [FEATURE_NAME]
```

## Arguments
- `$1` - Feature name (e.g., "validate", "export")

## Instructions

Create a new feature named `$1` following the constitutional equation.

**CRITICAL: Do NOT create Python files directly!**

Steps:
1. **Create RDF Specification** in `ontology/cli-commands.ttl`:
   ```turtle
   sk:$1
       a sk:Command ;
       rdfs:label "$1" ;
       sk:description "Description here" ;
       sk:hasArgument [
           a sk:Argument ;
           sk:name "arg_name" ;
           sk:type "str" ;
           sk:required true
       ] .
   ```

2. **Create SPARQL Query** if needed in `sparql/`

3. **Create Tera Template** if needed in `templates/`

4. **Run ggen sync** to generate Python code:
   ```bash
   ggen sync
   ```

5. **Implement Business Logic** in `src/specify_cli/ops/$1_ops.py`

6. **Implement Runtime** if needed in `src/specify_cli/runtime/`

7. **Run Tests** to verify:
   ```bash
   uv run pytest tests/ -v
   ```

Remember: The RDF specification is the source of truth!
