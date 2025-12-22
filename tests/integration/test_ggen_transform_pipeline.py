"""
Integration tests for ggen transformation pipeline.

Tests the complete μ transformation: spec.md = μ(feature.ttl)
"""

from __future__ import annotations

import pytest

from specify_cli.ops.transform import (
    StageResult,
    TransformConfig,
    canonicalize_output,
    compose_transform,
    emit_template,
    extract_data,
    generate_receipt,
    normalize_rdf,
    verify_idempotence,
)


class TestNormalizeRDF:
    """Test μ₁ NORMALIZE stage."""

    def test_normalize_valid_rdf_with_prefix(self) -> None:
        """Valid RDF with @prefix should pass."""
        rdf = """@prefix ex: <http://example.org/> .
ex:thing a ex:Thing ."""
        result = normalize_rdf(rdf)
        assert result.success
        assert result.stage == "normalize"
        assert result.output == rdf

    def test_normalize_valid_rdf_with_base(self) -> None:
        """Valid RDF with @base should pass."""
        rdf = """@base <http://example.org/> .
<#thing> a <#Thing> ."""
        result = normalize_rdf(rdf)
        assert result.success

    def test_normalize_valid_rdf_with_uris(self) -> None:
        """RDF with absolute URIs should pass."""
        rdf = "<http://example.org/thing> a <http://example.org/Thing> ."
        result = normalize_rdf(rdf)
        assert result.success

    def test_normalize_empty_rdf_fails(self) -> None:
        """Empty RDF should fail."""
        result = normalize_rdf("")
        assert not result.success
        assert "Empty RDF content" in result.errors

    def test_normalize_rdf_no_prefix_fails(self) -> None:
        """RDF without prefix or base fails."""
        rdf = "ex:thing a ex:Thing ."
        result = normalize_rdf(rdf)
        assert not result.success
        assert any("@prefix" in err or "@base" in err for err in result.errors)

    def test_normalize_preserves_content(self) -> None:
        """Normalize should preserve content exactly."""
        rdf = "@prefix ex: <http://example.org/> .\nex:a ex:b ex:c ."
        result = normalize_rdf(rdf)
        assert result.output == rdf


class TestExtractData:
    """Test μ₂ EXTRACT stage."""

    def test_extract_valid_select_query(self) -> None:
        """SELECT SPARQL query should be valid."""
        query = "SELECT ?s WHERE { ?s a ?type }"
        result = extract_data("dummy rdf", query)
        assert result.success
        assert result.stage == "extract"

    def test_extract_valid_construct_query(self) -> None:
        """CONSTRUCT SPARQL query should be valid."""
        query = "CONSTRUCT { ?s a ?type } WHERE { ?s a ?type }"
        result = extract_data("dummy rdf", query)
        assert result.success

    def test_extract_valid_ask_query(self) -> None:
        """ASK SPARQL query should be valid."""
        query = "ASK { ?s a ?type }"
        result = extract_data("dummy rdf", query)
        assert result.success

    def test_extract_valid_describe_query(self) -> None:
        """DESCRIBE SPARQL query should be valid."""
        query = "DESCRIBE ?s WHERE { ?s a ?type }"
        result = extract_data("dummy rdf", query)
        assert result.success

    def test_extract_empty_query_fails(self) -> None:
        """Empty SPARQL query should fail."""
        result = extract_data("dummy rdf", "")
        assert not result.success
        assert "Empty SPARQL query" in result.errors

    def test_extract_invalid_query_fails(self) -> None:
        """Invalid SPARQL query should fail."""
        result = extract_data("dummy rdf", "INVALID QUERY")
        assert not result.success
        assert any("SELECT" in err or "CONSTRUCT" in err for err in result.errors)


class TestEmitTemplate:
    """Test μ₃ EMIT stage."""

    def test_emit_template_with_variables(self) -> None:
        """Template with Jinja2 variables should be valid."""
        template = "# Title\n{{ title }}\n{{ description }}"
        result = emit_template({}, template)
        assert result.success
        assert result.stage == "emit"

    def test_emit_template_with_for_loop(self) -> None:
        """Template with for loop should be valid."""
        template = "{% for item in items %}\n- {{ item }}\n{% endfor %}"
        result = emit_template({}, template)
        assert result.success

    def test_emit_template_with_if_statement(self) -> None:
        """Template with if statement should be valid."""
        template = "{% if show %}\nContent\n{% endif %}"
        result = emit_template({}, template)
        assert result.success

    def test_emit_template_with_filters(self) -> None:
        """Template with filters should be valid."""
        template = "{{ text | upper }}"
        result = emit_template({}, template)
        assert result.success

    def test_emit_empty_template_fails(self) -> None:
        """Empty template should fail."""
        result = emit_template({}, "")
        assert not result.success
        assert "Empty template" in result.errors

    def test_emit_no_tera_syntax_fails(self) -> None:
        """Template without Tera syntax should fail."""
        result = emit_template({}, "Plain text with no template syntax")
        assert not result.success
        assert "no Tera syntax" in result.errors[0]

    def test_emit_complex_template(self) -> None:
        """Complex template with multiple features should work."""
        template = """# Results
{% for result in results %}
## {{ result.name }}
{{ result.description }}
{% if result.details %}
- Details: {{ result.details }}
{% endif %}
{% endfor %}"""
        result = emit_template({}, template)
        assert result.success


class TestCanonicalizeOutput:
    """Test μ₄ CANONICALIZE stage."""

    def test_canonicalize_basic(self) -> None:
        """Basic canonicalization should work."""
        content = "Line 1\nLine 2\nLine 3"
        result = canonicalize_output(content)
        assert result.success
        assert result.output.endswith("\n")

    def test_canonicalize_line_endings(self) -> None:
        """Should normalize line endings to LF."""
        content = "Line 1\r\nLine 2\rLine 3"
        result = canonicalize_output(content)
        assert "\r" not in result.output
        assert result.output.count("\n") >= 3

    def test_canonicalize_trailing_whitespace(self) -> None:
        """Should trim trailing whitespace per line."""
        content = "Line 1   \nLine 2  \nLine 3"
        result = canonicalize_output(content)
        lines = result.output.split("\n")
        assert not lines[0].endswith("   ")
        assert not lines[1].endswith("  ")

    def test_canonicalize_final_newline(self) -> None:
        """Should ensure exactly one final newline."""
        content = "Content"
        result = canonicalize_output(content)
        assert result.output == "Content\n"

    def test_canonicalize_multiple_final_newlines(self) -> None:
        """Should reduce multiple final newlines to one."""
        content = "Content\n\n\n"
        result = canonicalize_output(content)
        assert result.output == "Content\n"

    def test_canonicalize_empty(self) -> None:
        """Empty content should return empty string."""
        result = canonicalize_output("")
        assert result.output == ""

    def test_canonicalize_whitespace_only(self) -> None:
        """Whitespace-only content should return single newline."""
        result = canonicalize_output("   \n  \n  ")
        # After trimming, we get empty lines, canonicalize adds single final newline
        assert result.output == "\n"


class TestGenerateReceipt:
    """Test μ₅ RECEIPT stage."""

    def test_receipt_deterministic(self) -> None:
        """Receipt generation should be deterministic."""
        content = "Test content"
        input_hash = "abc123"
        result1 = generate_receipt(content, input_hash)
        result2 = generate_receipt(content, input_hash)
        assert result1.output_hash == result2.output_hash

    def test_receipt_different_content(self) -> None:
        """Different content should produce different hash."""
        input_hash = "abc123"
        result1 = generate_receipt("Content 1", input_hash)
        result2 = generate_receipt("Content 2", input_hash)
        assert result1.output_hash != result2.output_hash

    def test_receipt_format(self) -> None:
        """Receipt should have valid format."""
        content = "Test content"
        input_hash = "abc123"
        result = generate_receipt(content, input_hash)
        assert result.success
        assert result.stage == "receipt"
        assert len(result.output_hash) == 64  # SHA256 is 64 hex chars
        assert result.input_hash == input_hash


class TestComposeTransform:
    """Test transform composition."""

    def test_compose_all_successful(self) -> None:
        """Composing all successful stages."""
        config = TransformConfig(
            name="test",
            description="Test",
            input_files=["test.ttl"],
            schema_files=[],
            sparql_query="test.rq",
            template="test.tera",
            output_file="test.md",
        )
        stages = {
            "normalize": StageResult("normalize", True, "h1", "h1", "rdf", []),
            "extract": StageResult("extract", True, "h1", "h2", {}, []),
            "emit": StageResult("emit", True, "h2", "h3", "output", []),
            "canonicalize": StageResult("canonicalize", True, "h3", "h4", "output\n", []),
            "receipt": StageResult("receipt", True, "h1", "h4", "{}", []),
        }
        result = compose_transform(config, stages)
        assert result.success
        assert result.input_hash == "h1"
        assert result.output_hash == "h4"

    def test_compose_one_failure(self) -> None:
        """Composing with one failed stage."""
        config = TransformConfig(
            name="test",
            description="Test",
            input_files=["test.ttl"],
            schema_files=[],
            sparql_query="test.rq",
            template="test.tera",
            output_file="test.md",
        )
        stages = {
            "normalize": StageResult("normalize", False, "", "", None, ["Error 1"]),
            "extract": StageResult("extract", True, "", "", {}, []),
        }
        result = compose_transform(config, stages)
        assert not result.success
        assert "Error 1" in result.errors


class TestIdempotenceVerification:
    """Test idempotence verification: μ∘μ = μ."""

    def test_idempotence_identical_results(self) -> None:
        """Identical results should verify idempotence."""
        config = TransformConfig(
            name="test",
            description="Test",
            input_files=["test.ttl"],
            schema_files=[],
            sparql_query="test.rq",
            template="test.tera",
            output_file="test.md",
        )
        stages = {
            "normalize": StageResult("normalize", True, "h1", "h1", "rdf", []),
            "extract": StageResult("extract", True, "h1", "h2", {}, []),
            "emit": StageResult("emit", True, "h2", "h3", "output", []),
            "canonicalize": StageResult("canonicalize", True, "h3", "h4", "output\n", []),
            "receipt": StageResult("receipt", True, "h1", "h4", "{}", []),
        }

        result1 = compose_transform(config, stages)
        result2 = compose_transform(config, stages)

        verification = verify_idempotence(result1, result2)
        assert verification["idempotent"]
        assert verification["first_hash"] == verification["second_hash"]
        assert len(verification["violations"]) == 0

    def test_idempotence_different_hashes(self) -> None:
        """Different hashes should detect idempotence failure."""
        config = TransformConfig(
            name="test",
            description="Test",
            input_files=["test.ttl"],
            schema_files=[],
            sparql_query="test.rq",
            template="test.tera",
            output_file="test.md",
        )
        stages1 = {
            "normalize": StageResult("normalize", True, "h1", "h1", "rdf1", []),
            "extract": StageResult("extract", True, "h1", "h2", {}, []),
            "emit": StageResult("emit", True, "h2", "h3", "output1", []),
            "canonicalize": StageResult("canonicalize", True, "h3", "h4", "output1\n", []),
            "receipt": StageResult("receipt", True, "h1", "h4", "{}", []),
        }
        stages2 = {
            "normalize": StageResult("normalize", True, "h1", "h1", "rdf2", []),
            "extract": StageResult("extract", True, "h1", "h2", {}, []),
            "emit": StageResult("emit", True, "h2", "h3", "output2", []),
            "canonicalize": StageResult("canonicalize", True, "h3", "h5", "output2\n", []),
            "receipt": StageResult("receipt", True, "h1", "h5", "{}", []),
        }

        result1 = compose_transform(config, stages1)
        result2 = compose_transform(config, stages2)

        verification = verify_idempotence(result1, result2)
        assert not verification["idempotent"]
        assert verification["first_hash"] != verification["second_hash"]
        assert len(verification["violations"]) > 0


class TestCompleteTransformationPipeline:
    """Test complete transformation pipeline with realistic data."""

    def test_pipeline_basic_rdf_to_markdown(self) -> None:
        """Test complete pipeline: RDF → SPARQL → Tera → Markdown."""
        # 1. Normalize
        rdf = "@prefix ex: <http://example.org/> .\nex:doc a ex:Document ."
        norm_result = normalize_rdf(rdf)
        assert norm_result.success

        # 2. Extract
        query = "SELECT ?s WHERE { ?s a ?type }"
        extract_result = extract_data(norm_result.output or "", query)
        assert extract_result.success

        # 3. Emit
        template = """# Document
{% for result in results %}
- {{ result.s }}
{% endfor %}"""
        emit_result = emit_template(extract_result.output or {}, template)
        assert emit_result.success

        # 4. Canonicalize
        canon_result = canonicalize_output(emit_result.output or "")
        assert canon_result.success

        # 5. Receipt
        receipt_result = generate_receipt(
            canon_result.output or "",
            "test_hash",
        )
        assert receipt_result.success

    def test_pipeline_error_handling(self) -> None:
        """Test pipeline with error recovery."""
        # Invalid RDF
        norm_result = normalize_rdf("")
        assert not norm_result.success

        # Continue with next stages despite error
        extract_result = extract_data("", "SELECT ?s WHERE { ?s a ?type }")
        assert extract_result.success  # Query validation passes

        emit_result = emit_template({}, "Plain text")
        assert not emit_result.success  # Template validation fails

    def test_pipeline_edge_cases(self) -> None:
        """Test pipeline with edge cases."""
        # Minimal RDF
        rdf = "<http://a.org/x> a <http://b.org/Y> ."
        assert normalize_rdf(rdf).success

        # Complex query
        query = """SELECT ?s ?p ?o WHERE {
            ?s ?p ?o .
            FILTER (?p != <http://example.org/internal>)
        }"""
        assert extract_data(rdf, query).success

        # Template with all features
        template = """{% for item in items %}
{%- if item.active %}
{{ item.name | upper }}
{%- endif %}
{% endfor %}"""
        assert emit_template({}, template).success


class TestTransformConfigValidation:
    """Test TransformConfig validation."""

    def test_config_valid(self) -> None:
        """Valid config should pass."""
        from specify_cli.ops.transform import validate_transform_config

        config = {
            "name": "test",
            "description": "Test config",
            "input_files": ["test.ttl"],
            "schema_files": ["shapes.ttl"],
            "sparql_query": "test.rq",
            "template": "test.tera",
            "output_file": "test.md",
            "deterministic": True,
        }
        result = validate_transform_config(config)
        assert result.name == "test"
        assert result.input_files == ["test.ttl"]

    def test_config_minimal(self) -> None:
        """Minimal valid config should pass."""
        from specify_cli.ops.transform import validate_transform_config

        config = {
            "name": "test",
            "input_files": ["test.ttl"],
            "sparql_query": "test.rq",
            "template": "test.tera",
            "output_file": "test.md",
        }
        result = validate_transform_config(config)
        assert result.deterministic is True  # Default

    def test_config_missing_required(self) -> None:
        """Missing required fields should raise ValueError."""
        from specify_cli.ops.transform import validate_transform_config

        config = {"name": "test"}
        with pytest.raises(ValueError, match="Missing required fields"):
            validate_transform_config(config)

    def test_config_empty_input_files(self) -> None:
        """Empty input_files list should raise ValueError."""
        from specify_cli.ops.transform import validate_transform_config

        config = {
            "name": "test",
            "input_files": [],
            "sparql_query": "test.rq",
            "template": "test.tera",
            "output_file": "test.md",
        }
        with pytest.raises(ValueError, match="non-empty list"):
            validate_transform_config(config)
