"""
Unit Tests for SPARQL Execution in ggen Runtime
================================================

Tests for _execute_sparql() and _validate_shacl() functions in specify_cli.runtime.ggen.

Tests verify:
1. SPARQL query execution with rdflib
2. Result conversion to JSON-compatible format
3. Error handling for invalid queries/RDF
4. SHACL validation (when pyshacl available)
5. Graceful degradation when libraries not available

Author: Claude Code
Date: 2025-12-21
"""

from __future__ import annotations

import pytest

from specify_cli.runtime.ggen import _execute_sparql, _validate_shacl

# ============================================================================
# Test Data
# ============================================================================


@pytest.fixture
def sample_rdf() -> str:
    """
    Generate sample RDF/Turtle data for testing.

    Returns
    -------
    str
        Valid RDF/Turtle content with multiple triples.
    """
    return """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sk: <http://spec-kit.io/ontology#> .

sk:Feature1 a sk:Feature ;
    rdfs:label "Authentication" ;
    sk:priority "P0" ;
    sk:status "active" .

sk:Feature2 a sk:Feature ;
    rdfs:label "Authorization" ;
    sk:priority "P1" ;
    sk:status "planned" .
"""


@pytest.fixture
def simple_sparql_query() -> str:
    """
    Generate a simple SPARQL SELECT query.

    Returns
    -------
    str
        SPARQL query to select all features.
    """
    return """
PREFIX sk: <http://spec-kit.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?feature ?label ?priority WHERE {
    ?feature a sk:Feature .
    ?feature rdfs:label ?label .
    ?feature sk:priority ?priority .
}
ORDER BY ?priority
"""


# ============================================================================
# Test: SPARQL Execution
# ============================================================================


@pytest.mark.unit
def test_execute_sparql_with_results(sample_rdf: str, simple_sparql_query: str) -> None:
    """
    Test _execute_sparql() returns correct results.

    Verifies:
    - Query executes successfully
    - Results are returned as list of dicts
    - All variables are present in results
    - Values are correctly converted to Python types
    """
    result = _execute_sparql(sample_rdf, simple_sparql_query)

    assert "results" in result
    assert "count" in result
    assert result["count"] == 2
    assert len(result["results"]) == 2

    # Check first result (P0 priority)
    first_result = result["results"][0]
    assert "feature" in first_result
    assert "label" in first_result
    assert "priority" in first_result
    assert first_result["label"] == "Authentication"
    assert first_result["priority"] == "P0"


@pytest.mark.unit
def test_execute_sparql_empty_results(sample_rdf: str) -> None:
    """
    Test _execute_sparql() with query that returns no results.

    Verifies:
    - Query executes without error
    - Empty results list is returned
    - Count is 0
    """
    query = """
PREFIX sk: <http://spec-kit.io/ontology#>

SELECT ?feature WHERE {
    ?feature a sk:NonExistentType .
}
"""

    result = _execute_sparql(sample_rdf, query)

    assert result["count"] == 0
    assert result["results"] == []


@pytest.mark.unit
def test_execute_sparql_invalid_query(sample_rdf: str) -> None:
    """
    Test _execute_sparql() with invalid SPARQL syntax.

    Verifies:
    - Exception is raised for invalid queries
    """
    invalid_query = "INVALID SPARQL SYNTAX"

    with pytest.raises(Exception, match=r".*"):  # rdflib will raise parse exception
        _execute_sparql(sample_rdf, invalid_query)


@pytest.mark.unit
def test_execute_sparql_invalid_rdf() -> None:
    """
    Test _execute_sparql() with invalid RDF content.

    Verifies:
    - Exception is raised for malformed RDF
    """
    invalid_rdf = "This is not valid RDF/Turtle"
    query = "SELECT ?s WHERE { ?s ?p ?o }"

    with pytest.raises(Exception, match=r".*"):  # rdflib will raise parse error
        _execute_sparql(invalid_rdf, query)


@pytest.mark.unit
def test_execute_sparql_various_datatypes() -> None:
    """
    Test _execute_sparql() with various RDF datatypes.

    Verifies:
    - String literals are converted correctly
    - Integer literals are converted correctly
    - Boolean literals are converted correctly
    - URIs are converted to strings
    """
    rdf_with_types = """
@prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

ex:Test1 ex:stringProp "test string" ;
         ex:intProp 42 ;
         ex:boolProp true ;
         ex:floatProp 3.14 .
"""

    query = """
PREFIX ex: <http://example.org/>

SELECT ?stringVal ?intVal ?boolVal ?floatVal WHERE {
    ex:Test1 ex:stringProp ?stringVal ;
             ex:intProp ?intVal ;
             ex:boolProp ?boolVal ;
             ex:floatProp ?floatVal .
}
"""

    result = _execute_sparql(rdf_with_types, query)

    assert result["count"] == 1
    row = result["results"][0]

    assert row["stringVal"] == "test string"
    assert row["intVal"] == 42
    assert row["boolVal"] is True
    # RDF literals convert to Decimal, so compare as float
    assert abs(float(row["floatVal"]) - 3.14) < 0.01


# ============================================================================
# Test: SHACL Validation
# ============================================================================


@pytest.mark.unit
def test_validate_shacl_basic(sample_rdf: str, tmp_path) -> None:
    """
    Test _validate_shacl() with basic validation (no pyshacl).

    Verifies:
    - Validation passes when RDF is well-formed
    - Returns valid=True when pyshacl not available
    - Schema files are checked for existence
    """
    # Create a dummy schema file
    schema_file = tmp_path / "schema.ttl"
    schema_file.write_text("""
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <http://spec-kit.io/ontology#> .

# Empty schema for basic test
""")

    result = _validate_shacl(sample_rdf, [str(schema_file)])

    assert "valid" in result
    assert "violations" in result
    # Should be valid (either through pyshacl or graceful degradation)
    assert result["valid"] is True


@pytest.mark.unit
def test_validate_shacl_missing_schema(sample_rdf: str) -> None:
    """
    Test _validate_shacl() with missing schema file.

    Verifies:
    - Returns valid=False when schema file not found
    - Error message indicates missing file
    """
    result = _validate_shacl(sample_rdf, ["/nonexistent/schema.ttl"])

    assert result["valid"] is False
    assert len(result["violations"]) > 0
    assert "not found" in result["violations"][0]


@pytest.mark.unit
def test_validate_shacl_invalid_rdf() -> None:
    """
    Test _validate_shacl() with invalid RDF content.

    Verifies:
    - Returns valid=False for malformed RDF
    - Error is captured in violations
    """
    invalid_rdf = "This is not valid Turtle"

    result = _validate_shacl(invalid_rdf, [])

    # Should fail to parse RDF
    assert result["valid"] is False
    assert len(result["violations"]) > 0


# ============================================================================
# Test: Integration Between Functions
# ============================================================================


@pytest.mark.unit
def test_sparql_after_validation(sample_rdf: str, simple_sparql_query: str) -> None:
    """
    Test full pipeline: validate RDF, then query it.

    Verifies:
    - Validated RDF can be queried
    - Both operations work on same data
    """
    # First validate (will pass without schema)
    validation_result = _validate_shacl(sample_rdf, [])

    # Should be valid or have graceful degradation warning
    assert validation_result["valid"] is True or "warning" in validation_result

    # Then query the same RDF
    query_result = _execute_sparql(sample_rdf, simple_sparql_query)

    assert query_result["count"] == 2
    assert len(query_result["results"]) == 2
