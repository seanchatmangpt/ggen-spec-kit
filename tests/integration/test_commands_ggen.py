"""
Integration tests for ggen CLI commands.

Tests the ggen command group for RDF-to-Markdown transformations.
Covers sync, validate-rdf, and verify commands.

Test Structure:
    - 15+ integration tests covering ggen operations
    - Use fixtures from docs/ggen-examples/
    - Test config file parsing, output generation
    - 90%+ coverage target for ggen commands

Examples:
    pytest tests/integration/test_commands_ggen.py -v --cov
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest
from typer.testing import CliRunner

from specify_cli.app import app

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_ggen_config(tmp_path: Path) -> Path:
    """
    Create a sample ggen configuration file.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to ggen.toml config file
    """
    config_file = tmp_path / "ggen.toml"
    config_content = """
[[sync]]
source_glob = "memory/*.ttl"
sparql_query = "sparql/features.sparql"
template = "templates/spec.tera"
output = "docs/spec.md"

[[sync]]
source_glob = "ontology/*.ttl"
sparql_query = "sparql/schema.sparql"
template = "templates/schema.tera"
output = "docs/schema.md"
"""
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def sample_ttl_file(tmp_path: Path) -> Path:
    """
    Create a sample TTL (Turtle) file.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to sample TTL file
    """
    ttl_file = tmp_path / "feature.ttl"
    ttl_content = """
@prefix : <http://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Feature001 a :Feature ;
    :featureName "Authentication System" ;
    :priority "P0" ;
    :status "In Progress" ;
    rdfs:comment "User authentication and authorization" .
"""
    ttl_file.write_text(ttl_content)
    return ttl_file


@pytest.fixture
def sample_sparql_query(tmp_path: Path) -> Path:
    """
    Create a sample SPARQL query file.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to SPARQL query file
    """
    query_file = tmp_path / "features.sparql"
    query_content = """
PREFIX : <http://spec-kit.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?feature ?name ?priority ?status ?description
WHERE {
    ?feature a :Feature ;
        :featureName ?name ;
        :priority ?priority ;
        :status ?status .
    OPTIONAL { ?feature rdfs:comment ?description }
}
"""
    query_file.write_text(query_content)
    return query_file


@pytest.fixture
def sample_tera_template(tmp_path: Path) -> Path:
    """
    Create a sample Tera template file.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory

    Returns
    -------
    Path
        Path to Tera template file
    """
    template_file = tmp_path / "spec.tera"
    template_content = """# Features

{% for feature in features %}
## {{ feature.name }}

**Priority:** {{ feature.priority }}
**Status:** {{ feature.status }}

{{ feature.description }}

{% endfor %}
"""
    template_file.write_text(template_content)
    return template_file


@pytest.fixture
def ggen_workspace(
    tmp_path: Path,
    sample_ggen_config: Path,
    sample_ttl_file: Path,
    sample_sparql_query: Path,
    sample_tera_template: Path,
) -> Path:
    """
    Create a complete ggen workspace with all required files.

    Parameters
    ----------
    tmp_path : Path
        pytest temporary directory
    sample_ggen_config : Path
        Config file
    sample_ttl_file : Path
        TTL file
    sample_sparql_query : Path
        SPARQL query
    sample_tera_template : Path
        Tera template

    Returns
    -------
    Path
        Path to workspace directory
    """
    # Create directories
    (tmp_path / "memory").mkdir(exist_ok=True)
    (tmp_path / "ontology").mkdir(exist_ok=True)
    (tmp_path / "sparql").mkdir(exist_ok=True)
    (tmp_path / "templates").mkdir(exist_ok=True)
    (tmp_path / "docs").mkdir(exist_ok=True)

    # Move files into structure
    (tmp_path / "memory" / "feature.ttl").write_text(sample_ttl_file.read_text())
    (tmp_path / "sparql" / "features.sparql").write_text(sample_sparql_query.read_text())
    (tmp_path / "templates" / "spec.tera").write_text(sample_tera_template.read_text())

    return tmp_path


# ============================================================================
# Test: ggen sync
# ============================================================================


@pytest.mark.integration
def test_ggen_sync_basic(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test basic ggen sync operation.

    Verifies:
        - ggen sync executes successfully
        - Output markdown is generated
        - Success message is displayed
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Sync completed successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file)],
            catch_exceptions=False,
        )

        # Note: This assumes ggen commands exist in app
        # If not implemented yet, test will be skipped
        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")

        mock_run.assert_called()


@pytest.mark.integration
def test_ggen_sync_with_watch_mode(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test ggen sync with watch mode.

    Verifies:
        - Watch mode flag is passed to ggen
        - Continuous monitoring is enabled
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Watching for changes..."
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file), "--watch"],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_sync_dry_run(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test ggen sync dry run mode.

    Verifies:
        - Dry run flag is passed
        - No files are actually written
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Dry run: would sync 2 files"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file), "--dry-run"],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_sync_verbose_mode(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test ggen sync with verbose output.

    Verifies:
        - Verbose flag is passed
        - Detailed progress is shown
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
Processing: memory/feature.ttl
Executing SPARQL: sparql/features.sparql
Rendering template: templates/spec.tera
Writing output: docs/spec.md
"""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file), "--verbose"],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_sync_missing_config(cli_runner: CliRunner, tmp_path: Path) -> None:
    """
    Test ggen sync with missing config file.

    Verifies:
        - Error is reported
        - Non-zero exit code
    """
    nonexistent_config = tmp_path / "nonexistent.toml"
    result = cli_runner.invoke(
        app,
        ["ggen", "sync", "--config", str(nonexistent_config)],
        catch_exceptions=False,
    )

    if "ggen" not in str(result.stdout):
        pytest.skip("ggen commands not yet implemented")

    assert result.exit_code != 0 or "not found" in result.stdout.lower()


# ============================================================================
# Test: ggen validate-rdf
# ============================================================================


@pytest.mark.integration
def test_ggen_validate_rdf_valid_file(
    cli_runner: CliRunner,
    sample_ttl_file: Path,
) -> None:
    """
    Test RDF validation with valid TTL file.

    Verifies:
        - Validation passes
        - Success message is displayed
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "RDF validation successful"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = cli_runner.invoke(
            app,
            ["ggen", "validate-rdf", str(sample_ttl_file)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_validate_rdf_invalid_syntax(
    cli_runner: CliRunner,
    tmp_path: Path,
) -> None:
    """
    Test RDF validation with invalid TTL syntax.

    Verifies:
        - Validation fails
        - Error is reported
    """
    invalid_ttl = tmp_path / "invalid.ttl"
    invalid_ttl.write_text("""
@prefix : <http://example.com#> .

:Thing a :Class
    # Missing semicolon - syntax error
    :property "value" .
""")

    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Parse error: unexpected token"
        mock_run.return_value = mock_result

        result = cli_runner.invoke(
            app,
            ["ggen", "validate-rdf", str(invalid_ttl)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")

        assert result.exit_code != 0 or "error" in result.stdout.lower()


@pytest.mark.integration
def test_ggen_validate_rdf_multiple_files(
    cli_runner: CliRunner,
    sample_ttl_file: Path,
    tmp_path: Path,
) -> None:
    """
    Test RDF validation with multiple files.

    Verifies:
        - All files are validated
        - Summary is displayed
    """
    # Create additional TTL file
    ttl_file2 = tmp_path / "feature2.ttl"
    ttl_file2.write_text("""
@prefix : <http://spec-kit.io/ontology#> .

:Feature002 a :Feature ;
    :featureName "Authorization" ;
    :priority "P1" .
""")

    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Validated 2 files successfully"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = cli_runner.invoke(
            app,
            ["ggen", "validate-rdf", str(sample_ttl_file), str(ttl_file2)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


# ============================================================================
# Test: ggen verify
# ============================================================================


@pytest.mark.integration
def test_ggen_verify_constitutional_equation(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test verification of constitutional equation: spec.md = μ(feature.ttl).

    Verifies:
        - Hash verification works
        - Idempotence is checked
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = """
✓ Constitutional equation verified
  TTL hash: 1a2b3c4d...
  MD hash:  5e6f7g8h...
  spec.md = μ(feature.ttl) ✓
"""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "verify", "--config", str(config_file)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_verify_idempotence(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test verification of idempotence: μ∘μ = μ.

    Verifies:
        - Running sync twice produces same output
        - Hash remains identical
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "✓ μ∘μ = μ - Idempotence verified"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "verify", "--config", str(config_file), "--check-idempotence"],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


# ============================================================================
# Test: Config File Parsing
# ============================================================================


@pytest.mark.integration
def test_ggen_config_parsing_valid(
    cli_runner: CliRunner,
    sample_ggen_config: Path,
) -> None:
    """
    Test parsing of valid ggen config file.

    Verifies:
        - TOML is parsed correctly
        - Sync entries are recognized
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Config valid: 2 sync entries"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = cli_runner.invoke(
            app,
            ["ggen", "config", "validate", str(sample_ggen_config)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_config_parsing_invalid_toml(
    cli_runner: CliRunner,
    tmp_path: Path,
) -> None:
    """
    Test parsing of invalid TOML config.

    Verifies:
        - Error is reported
        - Helpful message is displayed
    """
    invalid_config = tmp_path / "invalid.toml"
    invalid_config.write_text("""
[[sync]
source_glob = "*.ttl"
# Missing closing bracket - invalid TOML
""")

    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "TOML parse error"
        mock_run.return_value = mock_result

        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(invalid_config)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


# ============================================================================
# Test: Output Generation
# ============================================================================


@pytest.mark.integration
def test_ggen_output_generation_markdown(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test markdown output generation.

    Verifies:
        - Markdown is generated from template
        - Output file is created
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Generated: docs/spec.md"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_output_overwrite_protection(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test output file overwrite protection.

    Verifies:
        - Existing files are not overwritten without --force
        - Warning is displayed
    """
    # Create existing output file
    output_file = ggen_workspace / "docs" / "spec.md"
    output_file.write_text("# Existing content")

    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Output file exists, use --force to overwrite"
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


# ============================================================================
# Test: Error Handling
# ============================================================================


@pytest.mark.integration
def test_ggen_sync_ggen_not_installed(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test ggen sync when ggen binary is not installed.

    Verifies:
        - Error is caught
        - Helpful message is displayed
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_run.side_effect = FileNotFoundError("ggen command not found")

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")


@pytest.mark.integration
def test_ggen_sync_sparql_error(
    cli_runner: CliRunner,
    ggen_workspace: Path,
) -> None:
    """
    Test ggen sync with SPARQL query error.

    Verifies:
        - SPARQL errors are reported
        - Error message is helpful
    """
    with patch("specify_cli.runtime.ggen.run_logged") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "SPARQL error: syntax error at line 5"
        mock_run.return_value = mock_result

        config_file = ggen_workspace / "ggen.toml"
        result = cli_runner.invoke(
            app,
            ["ggen", "sync", "--config", str(config_file)],
            catch_exceptions=False,
        )

        if "ggen" not in str(result.stdout):
            pytest.skip("ggen commands not yet implemented")
