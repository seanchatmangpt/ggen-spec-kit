ggen Integration
================

ggen v5.0.2 is the RDF-first code generation engine that powers Specify CLI's constitutional equation.

Overview
--------

**ggen** transforms RDF/Turtle specifications into executable code through a five-stage pipeline:

.. code-block:: text

   spec.md = μ(feature.ttl)

Where **μ** represents the μ-calculus transformation with stages:
1. μ₁ NORMALIZE - SHACL validation
2. μ₂ EXTRACT - SPARQL queries
3. μ₃ EMIT - Tera template rendering
4. μ₄ CANONICALIZE - Format output
5. μ₅ RECEIPT - SHA256 proof generation

Installation
------------

macOS (Homebrew)
~~~~~~~~~~~~~~~~

.. code-block:: bash

   brew install seanchatmangpt/ggen/ggen

Cargo (All Platforms)
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cargo install ggen-cli-lib

Docker
~~~~~~

.. code-block:: bash

   docker pull seanchatman/ggen:5.0.2

Verification
~~~~~~~~~~~~

.. code-block:: bash

   ggen --version
   # Output: ggen 5.0.2

Configuration
-------------

ggen.toml
~~~~~~~~~

The ``ggen.toml`` file configures RDF transformations:

.. code-block:: toml

   version = "1.0"

   [source]
   ontology = "ontology/"          # RDF schemas (source of truth)
   specifications = "memory/"       # Feature specifications
   templates = "templates/"         # Tera code generation templates
   queries = "sparql/"             # SPARQL extraction queries

   [output]
   code = "src/specify_cli/"
   tests = "tests/e2e/"
   docs = "docs/"

   # Transformation: CLI Commands → Python Code
   [[transformations]]
   name = "generate-commands"
   description = "Generate CLI commands from RDF"

   # Stage 1 (μ₁): Normalize - validate input
   input = "ontology/cli-commands.ttl"
   shacl = "ontology/command-shapes.ttl"

   # Stage 2 (μ₂): Extract - run SPARQL query
   query = "sparql/command-extract.rq"

   # Stage 3 (μ₃): Emit - render template
   template = "templates/command.tera"

   # Stage 4 (μ₄): Canonicalize - format output
   output = "src/specify_cli/commands/{name}.py"
   formatter = "ruff format"

   # Stage 5 (μ₅): Receipt - generate proof
   receipt = "build/receipts/{name}.json"
   hash_algorithm = "sha256"

   # Transformation: Commands → Tests
   [[transformations]]
   name = "generate-tests"
   input = "ontology/cli-commands.ttl"
   query = "sparql/command-extract.rq"
   template = "templates/command-test.tera"
   output = "tests/e2e/test_commands_{name}.py"

   # Transformation: Features → Documentation
   [[transformations]]
   name = "generate-docs"
   input = "memory/features.ttl"
   query = "sparql/docs-extract.rq"
   template = "templates/feature-doc.tera"
   output = "docs/{name}.md"

Basic Usage
-----------

Sync (Only Command)
~~~~~~~~~~~~~~~~~~~

In ggen v5.0.2, **ONLY** the ``sync`` command is available:

.. code-block:: bash

   # Run all transformations defined in ggen.toml
   ggen sync

   # From specific directory (reads ./ggen.toml)
   cd /path/to/project
   ggen sync

.. important::
   ggen v5.0.2 has **ONE command**: ``sync``

   Previous versions had ``compile``, ``validate``, ``watch`` - these are **REMOVED**.

Workflow
--------

1. Edit RDF Specification
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: turtle

   # ontology/cli-commands.ttl
   @prefix sk: <http://spec-kit.org/ontology#> .

   sk:CheckCommand
       a sk:Command ;
       rdfs:label "check" ;
       sk:description "Check tool availability" ;
       sk:hasOption [
           a sk:Option ;
           sk:name "verbose" ;
           sk:type "bool" ;
           sk:default false ;
       ] .

2. Run ggen sync
~~~~~~~~~~~~~~~~

.. code-block:: bash

   ggen sync

3. Verify Generated Code
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Generated: src/specify_cli/commands/check.py
   @app.command()
   def check(
       verbose: bool = typer.Option(False, "--verbose", "-v"),
   ) -> None:
       """Check tool availability.

       Args:
           verbose: Show detailed output.
       """
       result = ops.check_tools(verbose=verbose)
       console.print_json(data=result)

4. Run Tests
~~~~~~~~~~~~

.. code-block:: bash

   uv run pytest tests/e2e/test_commands_check.py

SPARQL Queries
--------------

Example extraction query:

.. code-block:: sparql

   # sparql/command-extract.rq
   PREFIX sk: <http://spec-kit.org/ontology#>
   PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

   SELECT ?name ?description ?option_name ?option_type
   WHERE {
       ?command a sk:Command ;
                rdfs:label ?name ;
                sk:description ?description .

       OPTIONAL {
           ?command sk:hasOption ?option .
           ?option sk:name ?option_name ;
                   sk:type ?option_type .
       }
   }
   ORDER BY ?name ?option_name

Tera Templates
--------------

Example code generation template:

.. code-block:: jinja

   {# templates/command.tera #}
   """{{ description }}"""

   import typer
   from specify_cli import ops
   from rich.console import Console

   app = typer.Typer()
   console = Console()

   @app.command()
   def {{ name }}(
       {% for option in options %}
       {{ option.name }}: {{ option.type }} = typer.Option(
           {{ option.default }},
           "--{{ option.name }}",
           help="{{ option.description }}",
       ),
       {% endfor %}
   ) -> None:
       """{{ description }}

       Args:
       {% for option in options %}
           {{ option.name }}: {{ option.description }}
       {% endfor %}
       """
       result = ops.{{ name }}(
           {% for option in options %}
           {{ option.name }}={{ option.name }},
           {% endfor %}
       )
       console.print_json(data=result)

Receipt Generation
------------------

Every transformation generates a cryptographic receipt:

.. code-block:: json

   {
     "transformation": "generate-commands",
     "input": "ontology/cli-commands.ttl",
     "input_hash": "sha256:a1b2c3...",
     "output": "src/specify_cli/commands/check.py",
     "output_hash": "sha256:d4e5f6...",
     "timestamp": "2025-12-25T07:30:00Z",
     "ggen_version": "5.0.2",
     "transformation_id": "uuid-1234-5678"
   }

Receipts prove:
- Input specification hasn't changed
- Output was generated from input
- Transformation is reproducible
- No manual edits to generated files

Validation
----------

Check Receipt Integrity
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Verify all receipts match current state
   ggen sync

   # If receipts don't match:
   # - Input RDF was modified → re-run ggen sync
   # - Output was manually edited → VIOLATION of constitutional equation

.. danger::
   **NEVER manually edit generated files!**

   Always edit the RDF source and re-run ``ggen sync``.

Advanced Usage
--------------

Custom Transformation Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from specify_cli.ops.ggen import run_transformation

   result = run_transformation(
       name="generate-commands",
       config_path="ggen.toml",
       dry_run=False,
   )

   print(f"Generated {result.files_created} files")
   print(f"Updated {result.files_updated} files")
   print(f"Receipts: {result.receipt_path}")

Conditional Generation
~~~~~~~~~~~~~~~~~~~~~~

Use SPARQL ``FILTER`` to conditionally generate code:

.. code-block:: sparql

   # Only generate for high-priority features
   SELECT ?feature ?name ?priority
   WHERE {
       ?feature a sk:Feature ;
                rdfs:label ?name ;
                sk:priority ?priority .

       FILTER(?priority = "high")
   }

Multi-Stage Pipelines
~~~~~~~~~~~~~~~~~~~~~

Chain transformations in ``ggen.toml``:

.. code-block:: toml

   # Stage 1: Generate models from ontology
   [[transformations]]
   name = "generate-models"
   input = "ontology/domain-model.ttl"
   output = "src/models/"

   # Stage 2: Generate migrations from models
   [[transformations]]
   name = "generate-migrations"
   input = "src/models/"      # Output from stage 1
   output = "migrations/"

   # Stage 3: Generate tests from migrations
   [[transformations]]
   name = "generate-migration-tests"
   input = "migrations/"      # Output from stage 2
   output = "tests/migrations/"

Best Practices
--------------

1. **Version Control RDF First**

   .. code-block:: bash

      git add ontology/ memory/ sparql/ templates/
      git commit -m "Update RDF specifications"

      # THEN generate code
      ggen sync

      git add src/ tests/ docs/
      git commit -m "Regenerate code from RDF"

2. **Never Edit Generated Files**

   .. code-block:: bash

      # ❌ WRONG
      vim src/specify_cli/commands/check.py

      # ✅ CORRECT
      vim ontology/cli-commands.ttl
      ggen sync

3. **Validate Before Committing**

   .. code-block:: bash

      ggen sync
      uv run pytest tests/
      git add .
      git commit -m "Add feature"

4. **Use Receipts for CI/CD**

   .. code-block:: bash

      # In CI pipeline
      ggen sync

      # Verify no manual changes
      if git diff --exit-code; then
          echo "✅ Code matches RDF specifications"
      else
          echo "❌ Manual changes detected"
          exit 1
      fi

Troubleshooting
---------------

SHACL Validation Errors
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   ggen sync
   # Error: SHACL validation failed at shape CommandShape

Fix the RDF:

.. code-block:: turtle

   # Add required properties
   sk:MyCommand
       a sk:Command ;
       rdfs:label "mycommand" ;      # Required
       sk:description "Description" ; # Required

SPARQL Query Issues
~~~~~~~~~~~~~~~~~~~

Test queries independently:

.. code-block:: bash

   # Use a SPARQL tool to test queries
   sparql --data=ontology/cli-commands.ttl --query=sparql/command-extract.rq

Template Rendering Errors
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Error: Template variable 'options' not found

Check SPARQL query returns expected variables:

.. code-block:: sparql

   # Ensure query selects 'options'
   SELECT ?name ?description ?options
   WHERE { ... }

See Also
--------

- :doc:`../guides/rdf_first_development` - RDF-first principles
- :doc:`../guides/constitutional_equation` - μ-calculus explained
- Official ggen docs: https://github.com/seanchatmangpt/ggen
