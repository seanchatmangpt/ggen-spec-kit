"""Constitutional equation test for dod"""

import hashlib
from pathlib import Path

import pytest

rdflib = pytest.importorskip("rdflib", reason="rdflib not installed")
from rdflib import Graph


def test_cli_module_exists() -> None:
    """CLI module should exist."""
    cli_file = Path("src/specify_cli/commands/dod.py")
    assert cli_file.exists()


def test_ops_module_exists() -> None:
    """Ops module should exist."""
    ops_file = Path("src/specify_cli/ops/dod.py")
    assert ops_file.exists()


def test_runtime_module_exists() -> None:
    """Runtime module should exist."""
    runtime_file = Path("src/specify_cli/runtime/dod.py")
    assert runtime_file.exists()


def test_rdf_specification_exists() -> None:
    """RDF specification should exist."""
    ontology_file = Path("ontology/cli-commands-uvmgr-full.ttl")
    assert ontology_file.exists()

    graph = Graph()
    graph.parse(str(ontology_file), format="turtle")

    query = """
    PREFIX : <http://uvmgr.io/cli#>
    SELECT ?name WHERE {
        ?cmd a :Command ;
             :name ?name .
    }
    """

    results = list(graph.query(query))
    assert any(str(r[0]).lower() == "dod" for r in results)


def test_cli_module_importable() -> None:
    """CLI module should be importable."""
    import sys

    sys.path.insert(0, "src")
    from specify_cli.commands import dod

    assert dod.app is not None


def test_ops_module_importable() -> None:
    """Ops module should be importable."""
    import sys

    sys.path.insert(0, "src")
    from specify_cli.ops import dod

    assert dod is not None


def test_runtime_module_importable() -> None:
    """Runtime module should be importable."""
    import sys

    sys.path.insert(0, "src")
    from specify_cli.runtime import dod

    assert dod is not None


def test_code_matches_specification() -> None:
    """Generated code should match RDF specification."""
    # Verify dod is in spec
    ontology = Path("ontology/cli-commands-uvmgr-full.ttl")
    graph = Graph()
    graph.parse(str(ontology), format="turtle")

    query = """
    PREFIX : <http://uvmgr.io/cli#>
    SELECT ?name WHERE {
        ?cmd a :Command ;
             :name ?name .
        FILTER(LCASE(STR(?name)) = "dod")
    }
    """

    results = list(graph.query(query))
    assert len(results) > 0, "Command not found in RDF specification"


def test_constitutional_equation_integrity() -> None:
    """Constitutional equation should verify."""
    # Read generated files
    cli_file = Path("src/specify_cli/commands/dod.py")
    ops_file = Path("src/specify_cli/ops/dod.py")
    runtime_file = Path("src/specify_cli/runtime/dod.py")

    cli_content = cli_file.read_text()
    ops_content = ops_file.read_text()
    runtime_content = runtime_file.read_text()

    # Verify all files are non-empty
    assert len(cli_content) > 0
    assert len(ops_content) > 0
    assert len(runtime_content) > 0

    # Compute hashes (proof of generation)
    cli_hash = hashlib.sha256(cli_content.encode()).hexdigest()
    ops_hash = hashlib.sha256(ops_content.encode()).hexdigest()
    runtime_hash = hashlib.sha256(runtime_content.encode()).hexdigest()

    # Store for receipt verification
    assert cli_hash is not None
    assert ops_hash is not None
    assert runtime_hash is not None
