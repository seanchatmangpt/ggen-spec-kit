Configuration
=============

Specify CLI uses multiple configuration files for different aspects of the system.

Project Configuration
---------------------

pyproject.toml
~~~~~~~~~~~~~~

The main Python project configuration:

.. code-block:: toml

   [project]
   name = "my-project"
   version = "0.1.0"
   requires-python = ">=3.11"

   dependencies = [
       "specify-cli>=0.0.25",
       # Add your dependencies here
   ]

   [dependency-groups]
   dev = [
       "ruff>=0.8.0",
       "mypy>=1.15.0",
       "pytest>=8.0.0",
   ]

RDF Configuration
-----------------

ggen.toml
~~~~~~~~~

Configuration for RDF-to-code transformation:

.. code-block:: toml

   # ggen.toml
   version = "1.0"

   [source]
   ontology = "ontology/"
   specifications = "memory/"
   templates = "templates/"
   queries = "sparql/"

   [[transformations]]
   name = "generate-commands"
   input = "ontology/cli-commands.ttl"
   query = "sparql/command-extract.rq"
   template = "templates/command.tera"
   output = "src/my_project/commands/"

   [[transformations]]
   name = "generate-tests"
   input = "ontology/cli-commands.ttl"
   query = "sparql/command-extract.rq"
   template = "templates/command-test.tera"
   output = "tests/e2e/"

OpenTelemetry Configuration
----------------------------

Environment Variables
~~~~~~~~~~~~~~~~~~~~~

Configure OpenTelemetry via environment variables:

.. code-block:: bash

   # OTLP Exporter
   export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
   export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"

   # Service identification
   export OTEL_SERVICE_NAME="my-project"
   export OTEL_SERVICE_VERSION="0.1.0"

   # Trace configuration
   export OTEL_TRACES_EXPORTER="otlp"
   export OTEL_METRICS_EXPORTER="otlp"
   export OTEL_LOGS_EXPORTER="otlp"

   # Sampling
   export OTEL_TRACES_SAMPLER="always_on"

Programmatic Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from specify_cli.core.telemetry import configure_telemetry

   configure_telemetry(
       service_name="my-project",
       service_version="0.1.0",
       endpoint="http://localhost:4318",
   )

Code Quality Configuration
---------------------------

Ruff (Linting & Formatting)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

   [tool.ruff]
   line-length = 100
   target-version = "py311"

   [tool.ruff.lint]
   select = ["E", "F", "W", "I", "N", "UP", "B", "A", "C4"]

MyPy (Type Checking)
~~~~~~~~~~~~~~~~~~~~

.. code-block:: toml

   [tool.mypy]
   python_version = "3.11"
   strict = false
   warn_return_any = true
   warn_unused_configs = true

Pytest (Testing)
~~~~~~~~~~~~~~~~

.. code-block:: toml

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   addopts = [
       "--cov=src/my_project",
       "--cov-report=term-missing",
       "-v",
   ]

AI Assistant Configuration
---------------------------

Claude Code (.claude/)
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .claude/config.yml
   commands:
     - name: "speckit.constitution"
       file: ".claude/commands/constitution.md"

     - name: "speckit.specify"
       file: ".claude/commands/specify.md"

GitHub Copilot (.github/)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # .github/copilot-instructions.md
   This project uses Specify CLI for spec-driven development.
   Follow the three-tier architecture pattern.

Environment-Specific Configuration
-----------------------------------

Development
~~~~~~~~~~~

.. code-block:: bash

   # .env.dev
   DEBUG=true
   LOG_LEVEL=debug
   OTEL_TRACES_EXPORTER=console

Production
~~~~~~~~~~

.. code-block:: bash

   # .env.prod
   DEBUG=false
   LOG_LEVEL=info
   OTEL_EXPORTER_OTLP_ENDPOINT=https://api.honeycomb.io

Configuration Files Reference
------------------------------

========================  ================================================
File                      Purpose
========================  ================================================
``pyproject.toml``        Python project metadata and dependencies
``ggen.toml``             RDF transformation configuration
``.editorconfig``         Editor formatting rules
``.gitignore``            Git ignore patterns
``ruff.toml``             Linting configuration (optional)
``mypy.ini``              Type checking configuration (optional)
========================  ================================================

Best Practices
--------------

1. **Version Control**:
   - Commit ``ggen.toml`` and ``pyproject.toml``
   - Do NOT commit ``.env`` files with secrets
   - Use ``.env.example`` for templates

2. **Environment Variables**:
   - Use environment-specific ``.env`` files
   - Never hardcode secrets in code
   - Use ``python-dotenv`` for local development

3. **RDF Configuration**:
   - Keep transformations idempotent
   - Use version control for ontologies
   - Document SPARQL queries

4. **Observability**:
   - Always configure OTEL in production
   - Use consistent service names
   - Enable sampling for high-volume services

Example Complete Configuration
-------------------------------

A typical project structure:

.. code-block:: text

   my-project/
   ├── pyproject.toml          # Python project config
   ├── ggen.toml               # RDF transformation config
   ├── .env.example            # Environment template
   ├── .editorconfig           # Editor config
   ├── .gitignore              # Git ignore
   ├── ontology/               # RDF schemas
   │   └── features.ttl
   ├── memory/                 # Specifications
   │   └── features.ttl
   ├── sparql/                 # SPARQL queries
   │   └── feature-extract.rq
   ├── templates/              # Tera templates
   │   └── feature.tera
   ├── src/                    # Generated code
   │   └── my_project/
   │       ├── commands/       # CLI layer
   │       ├── ops/            # Business logic
   │       └── runtime/        # Side effects
   └── tests/                  # Generated tests

See Also
--------

- :doc:`guides/rdf_first_development` - RDF-first principles
- :doc:`guides/observability` - OpenTelemetry guide
- :doc:`integrations/ggen` - ggen integration details
