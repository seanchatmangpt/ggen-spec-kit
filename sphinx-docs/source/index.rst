Specify CLI Documentation
==========================

**Version:** 0.0.25

Specify CLI is an RDF-first specification development toolkit implementing the constitutional equation:

.. code-block:: text

   spec.md = μ(feature.ttl)

Built with a **three-tier architecture** (commands/ops/runtime) and full **OpenTelemetry** instrumentation.

.. image:: https://img.shields.io/badge/python-3.11+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/code%20style-ruff-000000.svg
   :target: https://github.com/astral-sh/ruff
   :alt: Code Style: Ruff

.. image:: https://img.shields.io/badge/types-mypy-blue.svg
   :target: http://mypy-lang.org/
   :alt: Type Checker: mypy

Quick Start
-----------

Install Specify CLI:

.. code-block:: bash

   pip install specify-cli

Initialize a new project:

.. code-block:: bash

   specify init my-project --ai claude

Navigate to your project:

.. code-block:: bash

   cd my-project

Start spec-driven development:

.. code-block:: bash

   /speckit.constitution    # Establish project principles
   /speckit.specify         # Create baseline specification
   /speckit.plan            # Create implementation plan
   /speckit.tasks           # Generate actionable tasks
   /speckit.implement       # Execute implementation

Key Features
------------

🧬 **RDF-First Development**
   Source of truth is RDF/Turtle, not code. Specifications drive generation.

🏗️ **Three-Tier Architecture**
   - **Commands**: CLI interface (Typer)
   - **Operations**: Pure business logic (no side effects)
   - **Runtime**: Subprocess execution and I/O

📊 **Hyperdimensional Computing**
   Information-theoretic metrics, cognitive entropy, and semantic embeddings.

🔬 **Full Observability**
   OpenTelemetry instrumentation for traces, metrics, and logs.

🎯 **Jobs-to-be-Done Framework**
   User-centered feature specifications and outcome metrics.

🔄 **Process Mining**
   pm4py integration for workflow discovery and conformance checking.

🤖 **AI-Native**
   Designed for Claude, Copilot, Gemini, and other AI assistants.

Documentation Structure
-----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   configuration
   examples/index

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   guides/architecture
   guides/rdf_first_development
   guides/three_tier_architecture
   guides/constitutional_equation
   guides/hyperdimensional_computing
   guides/observability
   guides/jtbd_framework
   guides/process_mining

.. toctree::
   :maxdepth: 2
   :caption: Integration Guides

   integrations/dspy_latex
   integrations/ggen
   integrations/jtbd
   integrations/opentelemetry
   integrations/hyperdimensional

.. toctree::
   :maxdepth: 3
   :caption: API Reference

   api/specify_cli
   api/commands
   api/ops
   api/runtime
   api/core
   api/hyperdimensional
   api/dspy_latex

.. toctree::
   :maxdepth: 2
   :caption: Advanced Topics

   advanced/architecture_diagrams
   advanced/dependency_graphs
   advanced/performance_optimization
   advanced/caching_strategies
   advanced/security_best_practices
   advanced/testing_strategies

.. toctree::
   :maxdepth: 1
   :caption: Development

   contributing
   changelog
   license

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

The Constitutional Equation
----------------------------

The core principle of Specify CLI is the **constitutional equation**:

.. code-block:: text

   spec.md = μ(feature.ttl)

This represents a transformation pipeline with five stages:

.. mermaid::

   graph LR
       A[feature.ttl] --> B[μ₁ NORMALIZE]
       B --> C[μ₂ EXTRACT]
       C --> D[μ₃ EMIT]
       D --> E[μ₄ CANONICALIZE]
       E --> F[μ₅ RECEIPT]
       F --> G[spec.md + receipt.json]

**Transformation Stages:**

1. **μ₁ Normalize**: Validate SHACL shapes
2. **μ₂ Extract**: Execute SPARQL queries
3. **μ₃ Emit**: Render Tera templates
4. **μ₄ Canonicalize**: Format output
5. **μ₅ Receipt**: SHA256 hash proof

Three-Tier Architecture
------------------------

Specify CLI enforces strict layer separation:

.. mermaid::

   graph TB
       subgraph Commands Layer
           CLI[CLI Interface<br/>Typer]
           Parser[Argument Parsing]
           Formatter[Output Formatting]
       end

       subgraph Operations Layer
           Logic[Business Logic]
           Validation[Validation]
           Transform[Data Transformation]
       end

       subgraph Runtime Layer
           Subprocess[Subprocess Execution]
           FileIO[File I/O]
           HTTP[HTTP Requests]
       end

       CLI --> Logic
       Parser --> Validation
       Formatter --> Transform
       Logic --> Subprocess
       Validation --> FileIO
       Transform --> HTTP

**Layer Rules:**

- **Commands**: ✅ Parse args, format output | ❌ NO subprocess, NO I/O
- **Operations**: ✅ Pure logic, validation | ❌ NO subprocess, NO I/O
- **Runtime**: ✅ ALL side effects | ❌ NO imports from commands/ops

Performance Targets
-------------------

- Command startup: **< 500ms**
- Simple operations: **< 100ms**
- Complex transformations: **< 5s**
- Memory usage: **< 100MB**

Community & Support
-------------------

- **GitHub**: https://github.com/github/spec-kit
- **Issues**: https://github.com/github/spec-kit/issues
- **Discussions**: https://github.com/github/spec-kit/discussions
- **Contributing**: :doc:`contributing`

License
-------

MIT License - see :doc:`license` for details.

Copyright (c) 2025 Sean Chatman
