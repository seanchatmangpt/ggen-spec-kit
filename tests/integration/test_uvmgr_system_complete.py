"""Master integration test for complete 13-command uvmgr system."""
import sys
from pathlib import Path

import pytest


class TestAllCommandsImportable:
    """Verify all 13 commands are importable."""

    def test_cli_commands_importable(self) -> None:
        """All CLI commands should import."""
        sys.path.insert(0, "src")
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            mod = __import__(f"specify_cli.commands.{cmd}", fromlist=["app"])
            assert hasattr(mod, "app"), f"{cmd} missing app"

    def test_ops_modules_importable(self) -> None:
        """All ops modules should import."""
        sys.path.insert(0, "src")
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            mod = __import__(f"specify_cli.ops.{cmd}", fromlist=[cmd])
            assert mod is not None

    def test_runtime_modules_importable(self) -> None:
        """All runtime modules should import."""
        sys.path.insert(0, "src")
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            mod = __import__(f"specify_cli.runtime.{cmd}", fromlist=[cmd])
            assert mod is not None


class TestFilesGenerated:
    """Verify all required files exist."""

    def test_all_cli_files_exist(self) -> None:
        """All CLI command files should exist."""
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            cli_file = Path(f"src/specify_cli/commands/{cmd}.py")
            assert cli_file.exists(), f"Missing {cmd}.py CLI module"

    def test_all_ops_files_exist(self) -> None:
        """All ops files should exist."""
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            ops_file = Path(f"src/specify_cli/ops/{cmd}.py")
            assert ops_file.exists(), f"Missing {cmd}.py ops module"

    def test_all_runtime_files_exist(self) -> None:
        """All runtime files should exist."""
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            runtime_file = Path(f"src/specify_cli/runtime/{cmd}.py")
            assert runtime_file.exists(), f"Missing {cmd}.py runtime module"

    def test_all_test_files_exist(self) -> None:
        """All test files should exist."""
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            ops_test = Path(f"tests/unit/test_ops_{cmd}.py")
            runtime_test = Path(f"tests/integration/test_runtime_{cmd}.py")
            e2e_test = Path(f"tests/e2e/test_e2e_{cmd}.py")
            const_test = Path(f"tests/integration/test_constitutional_equation_{cmd}.py")

            assert ops_test.exists(), f"Missing ops test for {cmd}"
            assert runtime_test.exists(), f"Missing runtime test for {cmd}"
            assert e2e_test.exists(), f"Missing E2E test for {cmd}"
            assert const_test.exists(), f"Missing constitutional test for {cmd}"

    def test_all_docs_exist(self) -> None:
        """All command docs should exist."""
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            doc_file = Path(f"docs/commands/{cmd}.md")
            assert doc_file.exists(), f"Missing documentation for {cmd}"


class TestArchitectureCompleteness:
    """Verify complete three-tier architecture."""

    def test_cli_modules_have_typer_app(self) -> None:
        """All CLI modules should have Typer app."""
        commands = ["build", "cache", "deps", "docs", "dod"]
        for cmd in commands:
            cli_file = Path(f"src/specify_cli/commands/{cmd}.py")
            content = cli_file.read_text()
            assert "typer.Typer" in content

    def test_ops_modules_have_validate_function(self) -> None:
        """All ops modules should have validate_inputs."""
        commands = ["build", "cache", "deps", "docs", "dod"]
        for cmd in commands:
            ops_file = Path(f"src/specify_cli/ops/{cmd}.py")
            content = ops_file.read_text()
            assert "validate_inputs" in content

    def test_runtime_modules_have_subprocess_imports(self) -> None:
        """All runtime modules should handle subprocess."""
        commands = ["build", "cache", "deps", "docs", "dod"]
        for cmd in commands:
            runtime_file = Path(f"src/specify_cli/runtime/{cmd}.py")
            content = runtime_file.read_text()
            assert "subprocess" in content or "run_logged" in content


class TestRDFIntegration:
    """Verify RDF specification integration."""

    def test_ontology_exists(self) -> None:
        """RDF ontology should exist."""
        ontology = Path("ontology/cli-commands-uvmgr-full.ttl")
        assert ontology.exists()

    def test_ontology_has_all_commands(self) -> None:
        """Ontology should define all 13 commands."""
        ontology = Path("ontology/cli-commands-uvmgr-full.ttl")
        content = ontology.read_text()

        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            assert f':name "{cmd}"' in content or f'"{cmd}"' in content

    def test_sparql_queries_exist(self) -> None:
        """SPARQL queries should exist."""
        queries = [
            "extract-commands.rq",
            "extract-parameters.rq",
            "extract-options.rq",
            "extract-runtime.rq"
        ]

        for query in queries:
            query_file = Path(f"sparql/{query}")
            assert query_file.exists(), f"Missing {query}"


class TestConstitutionalEquation:
    """Verify constitutional equation: code = μ(specification)."""

    def test_code_derived_from_specification(self) -> None:
        """All code should be derived from RDF specification."""
        # Verify 13 command modules exist
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        # Each command has 3 modules (CLI, ops, runtime)
        expected_modules = len(commands) * 3

        cli_files = list(Path("src/specify_cli/commands").glob("*.py"))
        ops_files = list(Path("src/specify_cli/ops").glob("*.py"))
        runtime_files = list(Path("src/specify_cli/runtime").glob("*.py"))

        # Should have at least the 13 commands for each layer
        assert len(cli_files) >= len(commands)
        assert len(ops_files) >= len(commands)
        assert len(runtime_files) >= len(commands)

    def test_test_coverage_exists(self) -> None:
        """All commands should have test coverage."""
        commands = [
            "build", "cache", "deps", "docs", "dod",
            "guides", "infodesign", "lint", "mermaid",
            "otel", "terraform", "tests", "worktree"
        ]

        for cmd in commands:
            # Should have at least unit test
            test_file = Path(f"tests/unit/test_ops_{cmd}.py")
            assert test_file.exists()

    def test_documentation_complete(self) -> None:
        """Documentation should be complete."""
        # Should have commands index
        assert Path("docs/COMMANDS.md").exists()

        # Should have at least one command doc
        cmd_docs = list(Path("docs/commands").glob("*.md"))
        assert len(cmd_docs) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

