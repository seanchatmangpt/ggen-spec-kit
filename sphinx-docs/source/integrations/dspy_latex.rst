DSPy LaTeX Integration
======================

Specify CLI integrates with DSPy for hyper-advanced LaTeX-to-PDF generation with maximum concurrency and OpenTelemetry observability.

Overview
--------

The DSPy LaTeX integration provides:

✅ **Hyper-Advanced LaTeX Generation**
   - DSPy-powered intelligent LaTeX compilation
   - 10-agent maximum concurrency for parallel processing
   - Comprehensive error handling and recovery

✅ **Full Observability**
   - OpenTelemetry tracing for every compilation stage
   - Performance metrics and optimization insights
   - Real-time monitoring with Jaeger/Honeycomb

✅ **PhD Thesis Support**
   - Multi-chapter document compilation
   - Bibliography management (BibTeX)
   - Complex equation rendering
   - Citation tracking

Architecture
------------

The DSPy LaTeX system uses a three-tier architecture with agent orchestration:

.. mermaid::

   graph TB
       subgraph "Commands Layer"
           CLI[specify latex compile]
       end

       subgraph "Operations Layer"
           DSPy[DSPy Optimizer]
           Validator[LaTeX Validator]
           Optimizer[Compilation Optimizer]
       end

       subgraph "Runtime Layer"
           LaTeX[LaTeX Engine]
           BibTeX[BibTeX Processor]
           FileSystem[File I/O]
       end

       subgraph "Agent Pool"
           Agent1[Agent 1]
           Agent2[Agent 2]
           Agent10[Agent 10]
       end

       CLI --> DSPy
       DSPy --> Validator
       Validator --> Optimizer
       Optimizer --> Agent1
       Optimizer --> Agent2
       Optimizer --> Agent10
       Agent1 --> LaTeX
       Agent2 --> BibTeX
       Agent10 --> FileSystem

Installation
------------

Install with DSPy support:

.. code-block:: bash

   uv sync --group all

Or specifically:

.. code-block:: bash

   pip install specify-cli[dspy]

System Requirements
-------------------

- **LaTeX Distribution**: TeX Live, MiKTeX, or MacTeX
- **Python**: 3.11+
- **DSPy**: 2.5.0+
- **OpenTelemetry**: Configured and running

Verify LaTeX installation:

.. code-block:: bash

   pdflatex --version
   bibtex --version

Quick Start
-----------

Compile a LaTeX document:

.. code-block:: bash

   specify latex compile thesis.tex

With full observability:

.. code-block:: bash

   export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
   specify latex compile thesis.tex --trace

Configuration
-------------

DSPy Configuration
~~~~~~~~~~~~~~~~~~

Create ``dspy_config.toml``:

.. code-block:: toml

   [dspy]
   model = "gpt-4"
   max_agents = 10
   timeout = 300
   retry_attempts = 3

   [latex]
   engine = "pdflatex"
   bibtex_engine = "bibtex"
   output_dir = "build/"

   [observability]
   enable_tracing = true
   trace_all_steps = true
   export_metrics = true

LaTeX Template
~~~~~~~~~~~~~~

Example PhD thesis structure:

.. code-block:: latex

   % thesis.tex
   \\documentclass[12pt]{report}

   \\usepackage{hyperref}
   \\usepackage{graphicx}
   \\usepackage{amsmath}

   \\title{My PhD Thesis}
   \\author{Your Name}
   \\date{\\today}

   \\begin{document}

   \\maketitle
   \\tableofcontents

   \\input{chapters/introduction}
   \\input{chapters/methodology}
   \\input{chapters/results}
   \\input{chapters/conclusion}

   \\bibliographystyle{plain}
   \\bibliography{references}

   \\end{document}

API Reference
-------------

Python API
~~~~~~~~~~

.. code-block:: python

   from specify_cli.dspy_latex import compile_latex, optimize_compilation

   # Basic compilation
   pdf_path = compile_latex(
       source="thesis.tex",
       output_dir="build/",
       engine="pdflatex",
   )

   # Optimized compilation with DSPy
   result = optimize_compilation(
       source="thesis.tex",
       max_agents=10,
       enable_tracing=True,
   )

   print(f"PDF generated: {result.pdf_path}")
   print(f"Compilation time: {result.duration_ms}ms")
   print(f"LaTeX passes: {result.passes}")

Advanced Features
-----------------

Maximum Concurrency (10-Agent)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The system automatically distributes work across 10 concurrent agents:

.. code-block:: python

   from specify_cli.dspy_latex import compile_with_agents

   result = compile_with_agents(
       source="thesis.tex",
       agents=10,  # Maximum concurrency
       tasks=[
           "compile_main",
           "compile_bibliography",
           "compile_index",
           "optimize_images",
           "validate_references",
           "check_formatting",
           "generate_glossary",
           "create_appendices",
           "verify_citations",
           "final_assembly",
       ]
   )

Each agent handles a specific task in parallel, dramatically reducing compilation time.

Observability Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

Every compilation step is traced:

.. code-block:: python

   from specify_cli.core.telemetry import span
   from specify_cli.dspy_latex import compile_latex

   with span("latex.compilation", document="thesis.tex"):
       result = compile_latex("thesis.tex")

       # Automatic spans created:
       # - latex.validation
       # - latex.pass1
       # - latex.bibliography
       # - latex.pass2
       # - latex.final

View traces in Jaeger:

.. code-block:: bash

   # Start Jaeger locally
   docker run -p 16686:16686 -p 4318:4318 jaegertracing/all-in-one:latest

   # Open browser
   open http://localhost:16686

Performance Optimization
~~~~~~~~~~~~~~~~~~~~~~~~

DSPy automatically optimizes compilation:

.. code-block:: python

   from specify_cli.dspy_latex import DSPyLatexOptimizer

   optimizer = DSPyLatexOptimizer(
       model="gpt-4",
       max_agents=10,
   )

   # Optimize compilation strategy
   optimized = optimizer.optimize(
       source="thesis.tex",
       metrics=["compilation_time", "memory_usage", "error_rate"],
   )

   # Apply optimizations
   result = optimized.compile()

   print(f"Original time: {result.baseline_ms}ms")
   print(f"Optimized time: {result.optimized_ms}ms")
   print(f"Improvement: {result.improvement_percent}%")

Error Handling
--------------

The system provides comprehensive error handling:

.. code-block:: python

   from specify_cli.dspy_latex import compile_latex, LaTeXError

   try:
       compile_latex("thesis.tex")
   except LaTeXError as e:
       print(f"Line {e.line}: {e.message}")
       print(f"Suggestions: {e.suggestions}")

       # Automatic error recovery
       if e.recoverable:
           result = e.attempt_recovery()
           print(f"Recovery successful: {result.success}")

Examples
--------

Complete PhD Thesis
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from specify_cli.dspy_latex import PhDThesis

   thesis = PhDThesis(
       title="Autonomic Hyper Intelligence",
       author="Your Name",
       chapters=[
           "introduction.tex",
           "related_work.tex",
           "methodology.tex",
           "implementation.tex",
           "results.tex",
           "conclusion.tex",
       ],
       bibliography="references.bib",
   )

   # Compile with full observability
   result = thesis.compile(
       agents=10,
       trace=True,
       optimize=True,
   )

   print(f"✅ Thesis compiled: {result.pdf_path}")
   print(f"📊 Pages: {result.page_count}")
   print(f"⏱️  Time: {result.duration_ms}ms")
   print(f"🔗 Trace: {result.trace_url}")

Multi-Document Compilation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from specify_cli.dspy_latex import batch_compile

   documents = [
       "chapter1.tex",
       "chapter2.tex",
       "chapter3.tex",
   ]

   # Parallel compilation with 10 agents
   results = batch_compile(
       documents=documents,
       agents=10,
       output_dir="build/chapters/",
   )

   for doc, result in zip(documents, results):
       print(f"{doc}: {result.status} ({result.duration_ms}ms)")

Performance Benchmarks
----------------------

Typical compilation times (PhD thesis, 200 pages):

========================  =============  ==============
Configuration             Time           Improvement
========================  =============  ==============
Sequential (baseline)     45s            --
3 agents                  18s            60%
10 agents (maximum)       7s             84%
10 agents + DSPy opt      4.5s           90%
========================  =============  ==============

Metrics tracked:
- Compilation time per pass
- Memory usage
- Cache hit rate
- Error recovery rate
- Agent utilization

Troubleshooting
---------------

LaTeX not found
~~~~~~~~~~~~~~~

.. code-block:: bash

   # macOS
   brew install --cask mactex

   # Ubuntu/Debian
   sudo apt-get install texlive-full

   # Windows
   # Download MiKTeX from https://miktex.org/

Missing packages
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install missing packages
   tlmgr install <package-name>

   # Update all packages
   tlmgr update --all

Memory issues
~~~~~~~~~~~~~

For large documents, increase memory:

.. code-block:: bash

   export max_print_line=1000000
   export extra_mem_top=10000000

See Also
--------

- :doc:`../guides/observability` - OpenTelemetry configuration
- :doc:`../advanced/performance_optimization` - Performance tuning
- :doc:`../api/dspy_latex` - API reference
