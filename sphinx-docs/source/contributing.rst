Contributing to Specify CLI
===========================

Thank you for your interest in contributing to Specify CLI! This guide will help you get started.

Code of Conduct
---------------

This project adheres to a code of conduct. By participating, you are expected to uphold this code.

Getting Started
---------------

1. **Fork the Repository**

   .. code-block:: bash

      # Fork on GitHub, then clone
      git clone https://github.com/YOUR-USERNAME/spec-kit.git
      cd spec-kit

2. **Set Up Development Environment**

   .. code-block:: bash

      # Install all development dependencies
      uv sync --group all

3. **Create a Branch**

   .. code-block:: bash

      git checkout -b feature/my-awesome-feature

Development Workflow
--------------------

RDF-First Development
~~~~~~~~~~~~~~~~~~~~~

Remember: **spec.md = μ(feature.ttl)**

1. Edit RDF specifications in ``ontology/`` or ``memory/``
2. Run ``ggen sync`` to generate code
3. Run tests
4. Commit both RDF and generated code

Example:

.. code-block:: bash

   # 1. Edit RDF
   vim ontology/cli-commands.ttl

   # 2. Generate code
   ggen sync

   # 3. Run tests
   uv run pytest tests/

   # 4. Commit
   git add ontology/ src/ tests/
   git commit -m "feat: add new command"

Three-Tier Architecture
~~~~~~~~~~~~~~~~~~~~~~~

All code must follow the three-tier pattern:

.. code-block:: text

   src/specify_cli/
   ├── commands/    # CLI interface - NO side effects
   ├── ops/         # Business logic - PURE functions
   └── runtime/     # Side effects ONLY

**Rules:**

- ✅ Commands: Parse args, format output
- ✅ Operations: Pure logic, validation
- ✅ Runtime: subprocess, file I/O, HTTP
- ❌ NO subprocess in commands or ops
- ❌ NO imports from commands/ops in runtime

Code Quality Standards
-----------------------

Type Hints
~~~~~~~~~~

100% type coverage required:

.. code-block:: python

   # ✅ GOOD
   def process_data(input: str, limit: int = 10) -> dict[str, Any]:
       """Process input data."""
       ...

   # ❌ BAD
   def process_data(input, limit=10):
       """Process input data."""
       ...

Docstrings
~~~~~~~~~~

NumPy style required for public APIs:

.. code-block:: python

   def calculate_metrics(data: list[float]) -> dict[str, float]:
       """Calculate statistical metrics.

       Parameters
       ----------
       data : list[float]
           Input data points.

       Returns
       -------
       dict[str, float]
           Dictionary with mean, median, std keys.

       Examples
       --------
       >>> calculate_metrics([1.0, 2.0, 3.0])
       {'mean': 2.0, 'median': 2.0, 'std': 0.816}
       """
       ...

Testing
~~~~~~~

80%+ coverage required:

.. code-block:: bash

   uv run pytest tests/ --cov=src/specify_cli

Write tests for:
- All new features
- Bug fixes
- Edge cases

.. code-block:: python

   # tests/test_ops_validation.py
   def test_validate_command_name():
       """Test command name validation."""
       assert validate_command_name("check") is True
       assert validate_command_name("Check") is False  # must be lowercase
       assert validate_command_name("check-tools") is False  # no hyphens

Linting
~~~~~~~

.. code-block:: bash

   # Run ruff
   uv run ruff check src/

   # Auto-fix
   uv run ruff check src/ --fix

   # Format
   uv run ruff format src/

Type Checking
~~~~~~~~~~~~~

.. code-block:: bash

   uv run mypy src/

Security
~~~~~~~~

.. code-block:: bash

   # No shell=True in subprocess
   # ❌ BAD
   subprocess.run("git status", shell=True)

   # ✅ GOOD
   subprocess.run(["git", "status"])

Commit Guidelines
-----------------

Conventional Commits
~~~~~~~~~~~~~~~~~~~~

Use the Conventional Commits format:

.. code-block:: text

   <type>(<scope>): <description>

   [optional body]

   [optional footer]

**Types:**

- ``feat``: New feature
- ``fix``: Bug fix
- ``docs``: Documentation
- ``style``: Code style (formatting, etc.)
- ``refactor``: Code refactoring
- ``test``: Tests
- ``chore``: Build/tooling changes

**Examples:**

.. code-block:: bash

   git commit -m "feat(commands): add terraform integration"
   git commit -m "fix(ops): handle empty RDF files"
   git commit -m "docs(guides): add JTBD framework guide"

Claude Code Attribution
~~~~~~~~~~~~~~~~~~~~~~~~

Add attribution footer:

.. code-block:: bash

   git commit -m "$(cat <<'EOF'
   feat(dspy): add LaTeX optimization

   Implement DSPy-powered LaTeX compilation with 10-agent
   maximum concurrency and full OpenTelemetry tracing.

   🤖 Generated with Claude Code

   Co-Authored-By: Claude <noreply@anthropic.com>
   EOF
   )"

Pull Request Process
--------------------

1. **Update Documentation**

   - Add docstrings
   - Update README if needed
   - Add examples

2. **Run Full Test Suite**

   .. code-block:: bash

      uv run pytest tests/
      uv run ruff check src/
      uv run mypy src/

3. **Update CHANGELOG**

   Add entry to ``CHANGELOG.md``:

   .. code-block:: markdown

      ## [Unreleased]

      ### Added
      - New terraform integration command

4. **Create Pull Request**

   - Describe changes
   - Link related issues
   - Add screenshots if UI changes

5. **Request Review**

   Tag relevant reviewers

Areas for Contribution
----------------------

Documentation
~~~~~~~~~~~~~

- Improve guides
- Add examples
- Fix typos
- Add diagrams

Testing
~~~~~~~

- Increase coverage
- Add integration tests
- Add performance benchmarks

Features
~~~~~~~~

High priority:

- Additional AI assistant integrations
- More process mining algorithms
- Enhanced hyperdimensional metrics
- Performance optimizations

Integrations
~~~~~~~~~~~~

- New workflow engines
- Additional LaTeX templates
- More SPARQL query patterns

Development Setup Tips
----------------------

VS Code
~~~~~~~

Recommended extensions:

.. code-block:: json

   {
     "recommendations": [
       "ms-python.python",
       "ms-python.vscode-pylance",
       "charliermarsh.ruff",
       "matangover.mypy",
       "stardog-union.stardog-rdf-grammars"
     ]
   }

Settings:

.. code-block:: json

   {
     "python.linting.enabled": true,
     "python.linting.mypyEnabled": true,
     "python.formatting.provider": "none",
     "[python]": {
       "editor.defaultFormatter": "charliermarsh.ruff",
       "editor.formatOnSave": true
     }
   }

PyCharm
~~~~~~~

1. Open project
2. Configure Python 3.11+ interpreter
3. Enable type checking
4. Install Ruff plugin

Command Line
~~~~~~~~~~~~

Useful aliases:

.. code-block:: bash

   alias ggsync='ggen sync'
   alias uvtest='uv run pytest tests/ -v'
   alias uvcov='uv run pytest --cov=src/specify_cli'
   alias uvlint='uv run ruff check src/ && uv run mypy src/'

Questions?
----------

- **GitHub Discussions**: https://github.com/github/spec-kit/discussions
- **Issues**: https://github.com/github/spec-kit/issues
- **Email**: info@chatmangpt.com

License
-------

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank You!
----------

Your contributions make Specify CLI better for everyone. Thank you! 🎉
