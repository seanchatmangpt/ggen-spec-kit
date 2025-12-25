Quick Start Guide
=================

This guide will walk you through creating your first Specify CLI project and understanding the spec-driven development workflow.

Create Your First Project
--------------------------

Initialize a new project:

.. code-block:: bash

   specify init my-project --ai claude

This creates a new project with:
- Project structure
- AI assistant configuration
- Git repository (if available)
- Slash commands for your AI assistant

Navigate to your project:

.. code-block:: bash

   cd my-project

Core Workflow Commands
----------------------

Specify CLI provides five core slash commands for spec-driven development:

1. Constitution
~~~~~~~~~~~~~~~

Establish project principles and architecture:

.. code-block:: bash

   /speckit.constitution

This prompts your AI assistant to create:
- Project philosophy
- Architectural decisions
- Coding standards
- Quality gates

Example output:
- ``CONSTITUTION.md`` - Project principles
- ``ARCHITECTURE.md`` - System design
- ``.editorconfig`` - Code formatting rules

2. Specify
~~~~~~~~~~

Create baseline specifications:

.. code-block:: bash

   /speckit.specify

Generates:
- Feature specifications in RDF/Turtle
- User stories
- Acceptance criteria
- Data models

Example:

.. code-block:: turtle

   @prefix sk: <http://spec-kit.org/ontology#> .

   sk:UserAuthentication
       a sk:Feature ;
       rdfs:label "User Authentication" ;
       sk:description "Users can securely log in and out" ;
       sk:priority "high" ;
       sk:acceptance [
           sk:criterion "Login with valid credentials succeeds" ;
           sk:criterion "Login with invalid credentials fails" ;
           sk:criterion "Session expires after 1 hour" ;
       ] .

3. Plan
~~~~~~~

Create implementation plan:

.. code-block:: bash

   /speckit.plan

Generates:
- Implementation roadmap
- Task breakdown
- Dependencies
- Milestones

Output:
- ``PLAN.md`` - Detailed implementation plan
- ``ROADMAP.md`` - High-level milestones

4. Tasks
~~~~~~~~

Generate actionable tasks:

.. code-block:: bash

   /speckit.tasks

Creates:
- GitHub issues (if using GitHub)
- Task checklist
- Prioritized backlog

Example ``TASKS.md``:

.. code-block:: markdown

   # Implementation Tasks

   ## Phase 1: Core Authentication
   - [ ] Implement login endpoint
   - [ ] Add password hashing (bcrypt)
   - [ ] Create session management
   - [ ] Add logout endpoint

   ## Phase 2: Security
   - [ ] Add rate limiting
   - [ ] Implement CSRF protection
   - [ ] Add security headers

5. Implement
~~~~~~~~~~~~

Execute implementation:

.. code-block:: bash

   /speckit.implement

Your AI assistant will:
1. Read specifications
2. Generate code following three-tier architecture
3. Write tests
4. Update documentation

Constitutional Equation in Action
----------------------------------

The core principle is: **spec.md = μ(feature.ttl)**

Example Workflow
~~~~~~~~~~~~~~~~

1. **Define Feature in RDF**:

.. code-block:: turtle

   # ontology/features.ttl
   sk:RESTAPIEndpoint
       a sk:Feature ;
       rdfs:label "REST API Endpoint" ;
       sk:path "/api/users" ;
       sk:method "GET" ;
       sk:returns "application/json" .

2. **Generate Code via ggen**:

.. code-block:: bash

   ggen sync  # Reads ggen.toml, transforms RDF → Code

3. **Verify Generated Code**:

.. code-block:: python

   # Generated: src/specify_cli/commands/users.py
   @app.get("/api/users")
   def get_users() -> dict[str, Any]:
       """Get all users.

       Returns:
           JSON response with users list.
       """
       return ops.get_users()  # Delegates to ops layer

4. **Run Tests**:

.. code-block:: bash

   uv run pytest tests/

Three-Tier Architecture
-----------------------

All generated code follows the three-tier pattern:

Commands Layer (``commands/``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # commands/users.py
   @app.command()
   def list_users(
       limit: int = 10,
       verbose: bool = False,
   ) -> None:
       """List all users."""
       result = ops.list_users(limit=limit)
       if verbose:
           console.print_json(data=result)
       else:
           for user in result["users"]:
               console.print(f"- {user['name']}")

Operations Layer (``ops/``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # ops/users.py
   def list_users(limit: int = 10) -> dict[str, Any]:
       """Pure business logic for listing users.

       Args:
           limit: Maximum number of users to return.

       Returns:
           Dictionary with users list.
       """
       users = runtime.fetch_users(limit=limit)
       return {
           "users": users,
           "count": len(users),
           "limit": limit,
       }

Runtime Layer (``runtime/``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # runtime/users.py
   def fetch_users(limit: int) -> list[dict[str, Any]]:
       """Fetch users from database.

       Args:
           limit: Maximum results to fetch.

       Returns:
           List of user dictionaries.
       """
       with span("runtime.fetch_users", limit=limit):
           result = run_logged([
               "psql",
               "-c",
               f"SELECT * FROM users LIMIT {limit}",
           ])
           return parse_psql_output(result.stdout)

Observability
-------------

All operations are automatically instrumented with OpenTelemetry:

.. code-block:: python

   from specify_cli.core.telemetry import span, timed

   @timed
   def expensive_operation():
       with span("operation.step", key="value"):
           # Your code here
           pass

View traces in Jaeger, Honeycomb, or any OTEL-compatible backend.

Next Steps
----------

1. **Learn the Architecture**: :doc:`guides/three_tier_architecture`
2. **Understand RDF-First**: :doc:`guides/rdf_first_development`
3. **Explore Integrations**: :doc:`integrations/index`
4. **Read API Docs**: :doc:`api/specify_cli`

Additional Resources
--------------------

- :doc:`examples/index` - Complete examples
- :doc:`guides/jtbd_framework` - User-centered design
- :doc:`guides/hyperdimensional_computing` - Advanced metrics
- :doc:`advanced/performance_optimization` - Performance tuning
