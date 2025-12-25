Installation
============

Specify CLI supports multiple installation methods for different use cases.

System Requirements
-------------------

- **Python**: 3.11 or higher
- **Operating Systems**: Linux, macOS, Windows
- **External Tools** (optional):
  - ``git`` - Version control
  - ``ggen`` v5.0.2 - RDF code generation
  - AI assistants (Claude Code, GitHub Copilot, etc.)

Quick Install
-------------

Using pip:

.. code-block:: bash

   pip install specify-cli

Using uv (recommended for development):

.. code-block:: bash

   uv pip install specify-cli

Development Installation
------------------------

For contributing or development:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/github/spec-kit.git
   cd spec-kit

   # Install with all development dependencies
   uv sync --group all

   # Or install specific groups
   uv sync --group dev     # Development tools (ruff, mypy, pytest)
   uv sync --group docs    # Documentation dependencies
   uv sync --group pm      # Process mining (pm4py)
   uv sync --group wf      # Workflows (SpiffWorkflow)
   uv sync --group hd      # Hyperdimensional computing

Optional Dependencies
---------------------

Process Mining
~~~~~~~~~~~~~~

.. code-block:: bash

   uv sync --group pm

Includes:
- pm4py >= 2.7.0
- pandas >= 2.0.0

Workflow Automation
~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uv sync --group wf

Includes:
- SpiffWorkflow >= 2.0.0

Hyperdimensional Computing
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   uv sync --group hd

Includes:
- numpy >= 1.24.0
- scikit-learn >= 1.3.0
- matplotlib >= 3.7.0
- plotly >= 5.18.0

Documentation
~~~~~~~~~~~~~

.. code-block:: bash

   uv sync --group docs

Includes:
- sphinx >= 7.2.0
- sphinx-rtd-theme >= 2.0.0
- sphinx-autodoc-typehints >= 1.25.0
- and more...

External Tools
--------------

ggen (RDF Code Generation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install ggen v5.0.2 for RDF-first development:

**macOS (Homebrew)**:

.. code-block:: bash

   brew install seanchatmangpt/ggen/ggen

**Cargo (all platforms)**:

.. code-block:: bash

   cargo install ggen-cli-lib

**Docker**:

.. code-block:: bash

   docker pull seanchatman/ggen:5.0.2

Verify installation:

.. code-block:: bash

   ggen --version
   # Output: ggen 5.0.2

Verification
------------

Verify your installation:

.. code-block:: bash

   specify --version
   specify check

The ``check`` command will verify:
- Python version
- Required dependencies
- Optional tools (git, ggen)
- AI assistant availability

Example output:

.. code-block:: text

   ✅ Python 3.11.5
   ✅ Specify CLI 0.0.25
   ✅ git 2.39.0
   ✅ ggen 5.0.2
   ⚠️  Claude Code not found (optional)

Troubleshooting
---------------

ImportError: No module named 'specify_cli'
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure you're in the correct Python environment:

.. code-block:: bash

   python --version  # Should be 3.11+
   pip show specify-cli

ggen not found
~~~~~~~~~~~~~~

Install ggen following the instructions above, or use ``--skip-tls`` if you can't install it:

.. code-block:: bash

   specify init my-project --ignore-agent-tools

SSL/TLS Issues
~~~~~~~~~~~~~~

If you encounter SSL verification errors:

.. code-block:: bash

   specify init my-project --skip-tls

.. warning::
   Using ``--skip-tls`` is not recommended for production use.

Next Steps
----------

After installation, proceed to :doc:`quickstart` to create your first project.
