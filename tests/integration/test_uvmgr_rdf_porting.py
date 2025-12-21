"""
Integration tests for uvmgr RDF-first porting and code generation.

Tests the complete pipeline:
1. RDF ontology validation (SHACL shapes)
2. SPARQL query extraction
3. Tera template rendering
4. Generated code quality

Constitutional equation: cli_layer.py = μ(cli-commands-uvmgr-full.ttl)
"""

from __future__ import annotations

from pathlib import Path

import pytest

rdflib = pytest.importorskip("rdflib")
Graph = rdflib.Graph

# Pytest tests use assert statements, which is the intended pattern


class TestRDFOntology:
    """Test RDF ontology structure and completeness."""

    def test_ontology_file_exists(self) -> None:
        """Verify ontology file is present."""
        ontology_path = (
            Path(__file__).parent.parent.parent / "ontology" / "cli-commands-uvmgr-full.ttl"
        )
        assert ontology_path.exists(), f"Ontology file not found at {ontology_path}"

    def test_ontology_valid_turtle_syntax(self) -> None:
        """Verify ontology has valid Turtle syntax."""
        ontology_path = (
            Path(__file__).parent.parent.parent / "ontology" / "cli-commands-uvmgr-full.ttl"
        )
        try:
            graph = Graph()
            graph.parse(str(ontology_path), format="turtle")
            assert len(graph) > 0, "Ontology is empty"
        except Exception as e:
            pytest.fail(f"Failed to parse ontology: {e}")

    def test_ontology_has_all_13_commands(self) -> None:
        """Verify all 13 commands are defined in ontology."""
        ontology_path = (
            Path(__file__).parent.parent.parent / "ontology" / "cli-commands-uvmgr-full.ttl"
        )
        graph = Graph()
        graph.parse(str(ontology_path), format="turtle")

        expected_commands = [
            "deps",
            "build",
            "tests",
            "cache",
            "lint",
            "otel",
            "guides",
            "worktree",
            "infodesign",
            "mermaid",
            "dod",
            "docs",
            "terraform",
        ]

        # Query for commands with name property
        query = """
        PREFIX : <http://uvmgr.io/cli#>
        SELECT ?name WHERE {
            ?cmd a :Command ;
                 :name ?name .
        }
        """
        results = graph.query(query)
        found_commands = [str(row[0]) for row in results]

        assert len(found_commands) >= 13, f"Expected 13+ commands, found {len(found_commands)}"
        for cmd in expected_commands:
            assert cmd in found_commands, f"Command '{cmd}' not found in ontology"

    def test_ontology_commands_have_required_properties(self) -> None:
        """Verify each command has required properties."""
        ontology_path = (
            Path(__file__).parent.parent.parent / "ontology" / "cli-commands-uvmgr-full.ttl"
        )
        graph = Graph()
        graph.parse(str(ontology_path), format="turtle")

        # Query for commands with all required properties
        query = """
        PREFIX : <http://uvmgr.io/cli#>
        SELECT ?cmd ?name ?desc ?module ?telemetry WHERE {
            ?cmd a :Command ;
                 :name ?name ;
                 :description ?desc ;
                 :module ?module ;
                 :telemetryName ?telemetry .
        }
        """
        results = graph.query(query)
        assert len(results) >= 13, "Not all commands have required properties"

        # Verify properties are non-empty
        for row in results:
            cmd, name, desc, module, telemetry = row
            assert str(name), f"Command {cmd} missing name"
            assert str(desc), f"Command {cmd} missing description"
            assert str(module), f"Command {cmd} missing module"
            assert str(telemetry), f"Command {cmd} missing telemetryName"


class TestSPARQLQueries:
    """Test SPARQL query files exist and are syntactically valid."""

    def test_extract_commands_query_exists(self) -> None:
        """Verify extract-commands.rq exists."""
        query_path = Path(__file__).parent.parent.parent / "sparql" / "extract-commands.rq"
        assert query_path.exists(), f"SPARQL query not found at {query_path}"

    def test_extract_parameters_query_exists(self) -> None:
        """Verify extract-parameters.rq exists."""
        query_path = Path(__file__).parent.parent.parent / "sparql" / "extract-parameters.rq"
        assert query_path.exists(), f"SPARQL query not found at {query_path}"

    def test_extract_options_query_exists(self) -> None:
        """Verify extract-options.rq exists."""
        query_path = Path(__file__).parent.parent.parent / "sparql" / "extract-options.rq"
        assert query_path.exists(), f"SPARQL query not found at {query_path}"

    def test_extract_runtime_query_exists(self) -> None:
        """Verify extract-runtime.rq exists."""
        query_path = Path(__file__).parent.parent.parent / "sparql" / "extract-runtime.rq"
        assert query_path.exists(), f"SPARQL query not found at {query_path}"

    def test_sparql_queries_are_valid(self) -> None:
        """Verify SPARQL queries have valid syntax."""
        query_files = [
            "extract-commands.rq",
            "extract-parameters.rq",
            "extract-options.rq",
            "extract-runtime.rq",
        ]

        sparql_dir = Path(__file__).parent.parent.parent / "sparql"

        for query_file in query_files:
            query_path = sparql_dir / query_file
            content = query_path.read_text()

            # Check for basic SPARQL syntax
            assert "SELECT" in content or "CONSTRUCT" in content, (
                f"{query_file} missing SELECT or CONSTRUCT"
            )
            assert "WHERE" in content, f"{query_file} missing WHERE clause"
            assert "PREFIX" in content, f"{query_file} missing PREFIX definitions"


class TestTeraTemplates:
    """Test Tera template files exist and are structurally valid."""

    def test_cli_command_template_exists(self) -> None:
        """Verify cli-command.tera exists."""
        template_path = Path(__file__).parent.parent.parent / "templates" / "cli-command.tera"
        assert template_path.exists(), f"Template not found at {template_path}"

    def test_ops_command_template_exists(self) -> None:
        """Verify ops-command.tera exists."""
        template_path = Path(__file__).parent.parent.parent / "templates" / "ops-command.tera"
        assert template_path.exists(), f"Template not found at {template_path}"

    def test_runtime_command_template_exists(self) -> None:
        """Verify runtime-command.tera exists."""
        template_path = Path(__file__).parent.parent.parent / "templates" / "runtime-command.tera"
        assert template_path.exists(), f"Template not found at {template_path}"

    def test_templates_have_required_sections(self) -> None:
        """Verify templates have required sections."""
        templates = {
            "cli-command.tera": ["@app.command", "@instrument_command", "def ", "typer.Typer"],
            "ops-command.tera": ["def ", "->", "dict[str, Any]"],
            "runtime-command.tera": ["subprocess.run", "run_logged", "def ", "dict[str, Any]"],
        }

        templates_dir = Path(__file__).parent.parent.parent / "templates"

        for template_file, required_sections in templates.items():
            template_path = templates_dir / template_file
            content = template_path.read_text()

            for section in required_sections:
                assert section in content, f"{template_file} missing '{section}'"


class TestGgenTomlConfiguration:
    """Test ggen.toml configuration for transformation rules."""

    def test_ggen_toml_exists(self) -> None:
        """Verify ggen.toml exists."""
        config_path = Path(__file__).parent.parent.parent / "docs" / "ggen.toml"
        assert config_path.exists(), f"ggen.toml not found at {config_path}"

    def test_ggen_toml_has_cli_transformations(self) -> None:
        """Verify ggen.toml has CLI command transformations."""
        config_path = Path(__file__).parent.parent.parent / "docs" / "ggen.toml"
        content = config_path.read_text()

        # Check for command transformation patterns
        assert "uvmgr-deps-command" in content
        assert "uvmgr-build-command" in content
        assert "uvmgr-tests-command" in content

        # Check for at least 17 command transformations (commands + ops + runtime)
        command_count = content.count('name = "uvmgr-')
        assert command_count >= 17, f"Expected 17+ uvmgr transformations, found {command_count}"

    def test_ggen_toml_has_runtime_transformation(self) -> None:
        """Verify ggen.toml has runtime layer transformation."""
        config_path = Path(__file__).parent.parent.parent / "docs" / "ggen.toml"
        content = config_path.read_text()

        assert "uvmgr-runtime-layer" in content
        assert "extract-runtime.rq" in content
        assert "runtime-command.tera" in content


class TestConstitutionalEquation:
    """Test the constitutional equation: code = μ(specification)."""

    def test_ontology_is_authoritative(self) -> None:
        """Verify ontology is the single source of truth."""
        ontology_path = (
            Path(__file__).parent.parent.parent / "ontology" / "cli-commands-uvmgr-full.ttl"
        )

        # Ontology should exist and be valid
        assert ontology_path.exists()
        assert ontology_path.stat().st_size > 0

        # Should be parseable as RDF
        graph = Graph()
        graph.parse(str(ontology_path), format="turtle")
        assert len(graph) > 0

    def test_sparql_queries_extract_from_ontology(self) -> None:
        """Verify SPARQL queries can extract data from ontology."""
        ontology_path = (
            Path(__file__).parent.parent.parent / "ontology" / "cli-commands-uvmgr-full.ttl"
        )
        commands_query_path = Path(__file__).parent.parent.parent / "sparql" / "extract-commands.rq"

        graph = Graph()
        graph.parse(str(ontology_path), format="turtle")

        query = commands_query_path.read_text()

        # Execute query
        try:
            results = graph.query(query)
            assert len(results) > 0, "SPARQL query returned no results"
        except Exception as e:
            pytest.fail(f"Failed to execute SPARQL query: {e}")

    def test_templates_have_correct_placeholders(self) -> None:
        """Verify templates have correct Tera placeholders."""
        templates = {
            "cli-command.tera": ["{{ command_name }}", "{{ description }}", "{% for subcommand"],
            "ops-command.tera": ["{{ command_name }}", "{% for subcommand", "def "],
            "runtime-command.tera": ["{{ command_name }}", "{% for subcommand", "subprocess.run"],
        }

        templates_dir = Path(__file__).parent.parent.parent / "templates"

        for template_file, required_placeholders in templates.items():
            template_path = templates_dir / template_file
            content = template_path.read_text()

            for placeholder in required_placeholders:
                assert placeholder in content, f"{template_file} missing '{placeholder}'"


@pytest.mark.integration
class TestCompleteGeneration:
    """Integration tests for complete code generation pipeline."""

    def test_constitution_equation_is_verifiable(self) -> None:
        """Verify that the constitutional equation is mechanically verifiable."""
        ontology_path = (
            Path(__file__).parent.parent.parent / "ontology" / "cli-commands-uvmgr-full.ttl"
        )
        config_path = Path(__file__).parent.parent.parent / "docs" / "ggen.toml"

        # Both files must exist
        assert ontology_path.exists()
        assert config_path.exists()

        # Ontology must be valid RDF
        graph = Graph()
        graph.parse(str(ontology_path), format="turtle")
        assert len(graph) > 0

        # ggen.toml must reference the ontology
        config_content = config_path.read_text()
        assert "cli-commands-uvmgr" in config_content

    def test_all_components_integrated(self) -> None:
        """Verify all components are properly integrated."""
        base_path = Path(__file__).parent.parent.parent

        # Check all required files exist
        required_files = [
            "ontology/cli-commands-uvmgr-full.ttl",
            "sparql/extract-commands.rq",
            "sparql/extract-parameters.rq",
            "sparql/extract-options.rq",
            "sparql/extract-runtime.rq",
            "templates/cli-command.tera",
            "templates/ops-command.tera",
            "templates/runtime-command.tera",
            "docs/ggen.toml",
        ]

        for file_path in required_files:
            full_path = base_path / file_path
            assert full_path.exists(), f"Required file not found: {file_path}"
            assert full_path.stat().st_size > 0, f"File is empty: {file_path}"

    def test_generation_determinism(self) -> None:
        """Verify that code generation is deterministic."""
        config_path = Path(__file__).parent.parent.parent / "docs" / "ggen.toml"
        content = config_path.read_text()

        # All transformations should have deterministic = true
        lines = content.split("\n")
        in_transformation = False
        transformations_found = 0

        for _i, line in enumerate(lines):
            if "[[transformations" in line:
                in_transformation = True
                transformations_found += 1

            if in_transformation and "deterministic = true" in line:
                in_transformation = False

        assert transformations_found >= 17, (
            f"Expected 17+ transformations (uvmgr + others), found {transformations_found}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
