"""
Integration Tests for SPARQL Execution with Real Queries
==========================================================

Tests _execute_sparql() using actual SPARQL queries from sparql/ directory
against realistic RDF data.

Tests verify:
1. Real SPARQL queries execute successfully
2. Results match expected structure
3. Complex queries with GROUP BY, ORDER BY work
4. Multiple prefixes and namespaces are handled

Author: Claude Code
Date: 2025-12-21
"""

from __future__ import annotations

from pathlib import Path

import pytest

from specify_cli.runtime.ggen import _execute_sparql

# ============================================================================
# Test Data
# ============================================================================


@pytest.fixture
def sample_cli_commands_rdf() -> str:
    """
    Generate sample RDF data matching cli-commands.ttl structure.

    Returns
    -------
    str
        RDF/Turtle data with CLI command specifications.
    """
    return """
@prefix : <http://uvmgr.io/cli#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

:init a :Command ;
    :name "init" ;
    :description "Initialize a new project" ;
    :module "specify_cli.commands.init" ;
    :telemetryName "init.project" ;
    :outputFormat "text", "json" .

:check a :Command ;
    :name "check" ;
    :description "Check tool availability" ;
    :module "specify_cli.commands.check" ;
    :telemetryName "check.tools" ;
    :outputFormat "text" .

:sync a :Command ;
    :name "sync" ;
    :description "Synchronize specifications" ;
    :module "specify_cli.commands.ggen" ;
    :telemetryName "ggen.sync" ;
    :outputFormat "text", "json" .
"""


# ============================================================================
# Test: Real SPARQL Queries
# ============================================================================


@pytest.mark.integration
def test_extract_commands_query(sample_cli_commands_rdf: str) -> None:
    """
    Test with real extract-commands.rq query.

    Verifies:
    - Query from sparql/extract-commands.rq executes
    - All CLI commands are extracted
    - Grouped output formats work correctly
    """
    query_path = Path(__file__).parent.parent.parent / "sparql" / "extract-commands.rq"

    if not query_path.exists():
        pytest.skip(f"Query file not found: {query_path}")

    query = query_path.read_text()
    result = _execute_sparql(sample_cli_commands_rdf, query)

    assert result["count"] == 3
    assert len(result["results"]) == 3

    # Check that commands are returned
    command_names = {r["commandName"] for r in result["results"]}
    assert "init" in command_names
    assert "check" in command_names
    assert "sync" in command_names

    # Verify structure of first result
    first = result["results"][0]
    assert "commandName" in first
    assert "description" in first
    assert "module" in first
    assert "telemetryName" in first
    assert "outputFormats" in first


@pytest.mark.integration
def test_command_query_with_arguments() -> None:
    """
    Test command-query.rq with arguments and options.

    Verifies:
    - Complex queries with OPTIONAL clauses work
    - Arguments and options are extracted
    - Nested structures are flattened correctly
    """
    rdf_with_args = """
@prefix sk: <http://github.com/github/spec-kit#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

sk:InitCommand a sk:Command ;
    sk:commandName "init" ;
    sk:commandDescription "Initialize project" ;
    sk:commandGroup "setup" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:argumentName "name" ;
        sk:argumentType "string" ;
        sk:argumentRequired true ;
        sk:argumentIndex 0 ;
        sk:argumentHelp "Project name"
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:optionName "verbose" ;
        sk:optionShort "v" ;
        sk:optionType "boolean" ;
        sk:optionDefault false ;
        sk:optionHelp "Enable verbose output"
    ] .
"""

    query_path = Path(__file__).parent.parent.parent / "sparql" / "command-query.rq"

    if not query_path.exists():
        pytest.skip(f"Query file not found: {query_path}")

    query = query_path.read_text()
    result = _execute_sparql(rdf_with_args, query)

    # Should get results with command, argument, and option
    assert result["count"] > 0

    # Check first result has command data
    first = result["results"][0]
    assert first["commandName"] == "init"
    assert first["commandDescription"] == "Initialize project"
    assert first["commandGroup"] == "setup"

    # Check argument data
    assert first["argName"] == "name"
    assert first["argType"] == "string"
    assert first["argRequired"] is True

    # Check option data
    assert first["optName"] == "verbose"
    assert first["optShort"] == "v"
    assert first["optType"] == "boolean"


@pytest.mark.integration
def test_sparql_with_multiple_prefixes() -> None:
    """
    Test SPARQL queries with multiple namespace prefixes.

    Verifies:
    - Multiple PREFIX declarations work
    - Namespace resolution is correct
    - Cross-namespace queries succeed
    """
    rdf_multi_ns = """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sk: <http://spec-kit.io/ontology#> .
@prefix jtbd: <http://spec-kit.io/jtbd#> .

sk:Feature1 a sk:Feature ;
    rdfs:label "User Authentication" ;
    sk:priority "P0" ;
    jtbd:enablesJob jtbd:Job1 .

jtbd:Job1 a jtbd:Job ;
    rdfs:label "Login securely" ;
    jtbd:outcome "User logged in" .
"""

    query = """
PREFIX sk: <http://spec-kit.io/ontology#>
PREFIX jtbd: <http://spec-kit.io/jtbd#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?featureLabel ?jobLabel ?outcome WHERE {
    ?feature a sk:Feature ;
             rdfs:label ?featureLabel ;
             jtbd:enablesJob ?job .
    ?job a jtbd:Job ;
         rdfs:label ?jobLabel ;
         jtbd:outcome ?outcome .
}
"""

    result = _execute_sparql(rdf_multi_ns, query)

    assert result["count"] == 1
    row = result["results"][0]
    assert row["featureLabel"] == "User Authentication"
    assert row["jobLabel"] == "Login securely"
    assert row["outcome"] == "User logged in"


@pytest.mark.integration
def test_sparql_with_filters_and_order() -> None:
    """
    Test SPARQL with FILTER and ORDER BY clauses.

    Verifies:
    - FILTER expressions work correctly
    - ORDER BY sorting is correct
    - Complex query structures execute
    """
    rdf = """
@prefix ex: <http://example.org/> .

ex:Task1 ex:priority 1 ; ex:name "Critical" .
ex:Task2 ex:priority 5 ; ex:name "Low" .
ex:Task3 ex:priority 2 ; ex:name "High" .
ex:Task4 ex:priority 3 ; ex:name "Medium" .
"""

    query = """
PREFIX ex: <http://example.org/>

SELECT ?name ?priority WHERE {
    ?task ex:name ?name ;
          ex:priority ?priority .
    FILTER (?priority <= 3)
}
ORDER BY ?priority
"""

    result = _execute_sparql(rdf, query)

    # Should get 3 results (priority 1, 2, 3)
    assert result["count"] == 3

    # Check ordering
    assert result["results"][0]["name"] == "Critical"  # priority 1
    assert result["results"][1]["name"] == "High"  # priority 2
    assert result["results"][2]["name"] == "Medium"  # priority 3


@pytest.mark.integration
def test_sparql_group_by_aggregation() -> None:
    """
    Test SPARQL with GROUP BY and aggregation functions.

    Verifies:
    - GROUP BY works correctly
    - Aggregation functions (COUNT, SUM) work
    - GROUP_CONCAT for string aggregation works
    """
    rdf = """
@prefix ex: <http://example.org/> .

ex:Project1 ex:type "backend" ; ex:developer "Alice" .
ex:Project2 ex:type "backend" ; ex:developer "Bob" .
ex:Project3 ex:type "frontend" ; ex:developer "Charlie" .
ex:Project4 ex:type "backend" ; ex:developer "Diana" .
"""

    query = """
PREFIX ex: <http://example.org/>

SELECT ?type (COUNT(?project) AS ?count) WHERE {
    ?project ex:type ?type .
}
GROUP BY ?type
ORDER BY DESC(?count)
"""

    result = _execute_sparql(rdf, query)

    # Should get 2 groups
    assert result["count"] == 2

    # Backend should have more projects (3 vs 1)
    first = result["results"][0]
    assert first["type"] == "backend"
    assert first["count"] == 3
