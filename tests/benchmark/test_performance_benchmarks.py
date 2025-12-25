"""
Performance benchmark tests for specify-cli.

This module uses pytest-benchmark to measure and track performance of
critical operations across the codebase.

Benchmarks include:
- Hyperdimensional vector operations
- RDF parsing and transformation
- Process execution
- Template rendering
- SPARQL query execution

Run with: pytest --benchmark-enable tests/benchmark/
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pytest

# Mark all tests in this module as benchmarks
pytestmark = pytest.mark.benchmark


# ============================================================================
# Hyperdimensional Computing Benchmarks
# ============================================================================


class TestHyperdimensionalBenchmarks:
    """Benchmark tests for hyperdimensional computing operations."""

    @pytest.fixture
    def random_vectors(self) -> tuple[np.ndarray, np.ndarray]:
        """Generate random hyperdimensional vectors for benchmarking."""
        dim = 10000
        v1 = np.random.choice([-1.0, 1.0], size=dim)
        v2 = np.random.choice([-1.0, 1.0], size=dim)
        return v1, v2

    def test_benchmark_vector_binding(self, benchmark: Any, random_vectors: tuple[np.ndarray, np.ndarray]) -> None:
        """Benchmark vector binding (element-wise multiplication)."""
        v1, v2 = random_vectors

        def bind_vectors() -> np.ndarray:
            return v1 * v2

        result = benchmark(bind_vectors)
        assert result.shape == v1.shape

    def test_benchmark_vector_bundling(self, benchmark: Any) -> None:
        """Benchmark vector bundling (sum and normalize)."""
        dim = 10000
        n_vectors = 10
        vectors = [np.random.choice([-1.0, 1.0], size=dim) for _ in range(n_vectors)]

        def bundle_vectors() -> np.ndarray:
            bundled = np.sum(vectors, axis=0)
            return np.sign(bundled)

        result = benchmark(bundle_vectors)
        assert result.shape == (dim,)

    def test_benchmark_cosine_similarity(self, benchmark: Any, random_vectors: tuple[np.ndarray, np.ndarray]) -> None:
        """Benchmark cosine similarity calculation."""
        v1, v2 = random_vectors

        def compute_similarity() -> float:
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))

        result = benchmark(compute_similarity)
        assert -1 <= result <= 1

    def test_benchmark_hamming_distance(self, benchmark: Any, random_vectors: tuple[np.ndarray, np.ndarray]) -> None:
        """Benchmark Hamming distance calculation."""
        v1, v2 = random_vectors

        def compute_distance() -> int:
            return int(np.sum(v1 != v2))

        result = benchmark(compute_distance)
        assert 0 <= result <= len(v1)


# ============================================================================
# RDF/Turtle Parsing Benchmarks
# ============================================================================


class TestRDFBenchmarks:
    """Benchmark tests for RDF operations."""

    @pytest.fixture
    def sample_turtle(self) -> str:
        """Generate sample Turtle RDF data."""
        return """
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sk: <http://spec-kit.org/schema#> .

sk:TestClass
    a rdfs:Class ;
    rdfs:label "Test Class" ;
    rdfs:comment "A test class for benchmarking" .

sk:testProperty
    a rdf:Property ;
    rdfs:label "Test Property" ;
    rdfs:domain sk:TestClass ;
    rdfs:range rdfs:Literal .
"""

    def test_benchmark_turtle_parsing(self, benchmark: Any, sample_turtle: str) -> None:
        """Benchmark Turtle RDF parsing."""
        try:
            from rdflib import Graph
        except ImportError:
            pytest.skip("rdflib not available")

        def parse_turtle() -> Graph:
            g = Graph()
            g.parse(data=sample_turtle, format="turtle")
            return g

        result = benchmark(parse_turtle)
        assert len(result) > 0

    def test_benchmark_turtle_serialization(self, benchmark: Any, sample_turtle: str) -> None:
        """Benchmark Turtle RDF serialization."""
        try:
            from rdflib import Graph
        except ImportError:
            pytest.skip("rdflib not available")

        g = Graph()
        g.parse(data=sample_turtle, format="turtle")

        def serialize_turtle() -> str:
            return g.serialize(format="turtle")

        result = benchmark(serialize_turtle)
        assert len(result) > 0


# ============================================================================
# Template Rendering Benchmarks
# ============================================================================


class TestTemplateRenderingBenchmarks:
    """Benchmark tests for template rendering operations."""

    @pytest.fixture
    def sample_template(self) -> str:
        """Generate sample Jinja2 template."""
        return """
# {{ title }}

## Description
{{ description }}

## Features
{% for feature in features %}
- {{ feature.name }}: {{ feature.description }}
{% endfor %}

## Configuration
```toml
[{{ section }}]
{% for key, value in config.items() %}
{{ key }} = "{{ value }}"
{% endfor %}
```
"""

    @pytest.fixture
    def template_data(self) -> dict[str, Any]:
        """Generate sample template data."""
        return {
            "title": "Test Document",
            "description": "A test document for benchmarking template rendering",
            "section": "general",
            "features": [
                {"name": "Feature 1", "description": "First feature"},
                {"name": "Feature 2", "description": "Second feature"},
                {"name": "Feature 3", "description": "Third feature"},
            ],
            "config": {
                "option1": "value1",
                "option2": "value2",
                "option3": "value3",
            },
        }

    def test_benchmark_jinja2_rendering(
        self,
        benchmark: Any,
        sample_template: str,
        template_data: dict[str, Any],
    ) -> None:
        """Benchmark Jinja2 template rendering."""
        from jinja2 import Template

        template = Template(sample_template)

        def render_template() -> str:
            return template.render(**template_data)

        result = benchmark(render_template)
        assert "Test Document" in result
        assert "Feature 1" in result


# ============================================================================
# File I/O Benchmarks
# ============================================================================


class TestFileIOBenchmarks:
    """Benchmark tests for file I/O operations."""

    @pytest.fixture
    def temp_file(self) -> Path:
        """Create a temporary file for benchmarking."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            data = {"key": "value", "items": list(range(1000))}
            json.dump(data, f)
            return Path(f.name)

    def test_benchmark_json_read(self, benchmark: Any, temp_file: Path) -> None:
        """Benchmark JSON file reading."""

        def read_json() -> dict[str, Any]:
            return json.loads(temp_file.read_text())

        result = benchmark(read_json)
        assert "items" in result
        assert len(result["items"]) == 1000

        # Cleanup
        temp_file.unlink()

    def test_benchmark_json_write(self, benchmark: Any) -> None:
        """Benchmark JSON file writing."""
        data = {"key": "value", "items": list(range(1000))}

        def write_json() -> None:
            with tempfile.NamedTemporaryFile(mode="w", delete=True, suffix=".json") as f:
                json.dump(data, f)

        benchmark(write_json)


# ============================================================================
# NumPy Operations Benchmarks
# ============================================================================


class TestNumpyBenchmarks:
    """Benchmark tests for NumPy operations used in hyperdimensional computing."""

    def test_benchmark_matrix_multiplication(self, benchmark: Any) -> None:
        """Benchmark matrix multiplication."""
        size = 1000
        a = np.random.rand(size, size)
        b = np.random.rand(size, size)

        def matmul() -> np.ndarray:
            return np.dot(a, b)

        result = benchmark(matmul)
        assert result.shape == (size, size)

    def test_benchmark_element_wise_operations(self, benchmark: Any) -> None:
        """Benchmark element-wise operations."""
        size = 100000
        a = np.random.rand(size)
        b = np.random.rand(size)

        def element_wise() -> np.ndarray:
            return a * b + a / (b + 1e-10)

        result = benchmark(element_wise)
        assert result.shape == (size,)

    def test_benchmark_argmax(self, benchmark: Any) -> None:
        """Benchmark argmax operation."""
        size = 1000000
        arr = np.random.rand(size)

        def find_argmax() -> int:
            return int(np.argmax(arr))

        result = benchmark(find_argmax)
        assert 0 <= result < size


# ============================================================================
# String Processing Benchmarks
# ============================================================================


class TestStringProcessingBenchmarks:
    """Benchmark tests for string processing operations."""

    @pytest.fixture
    def large_text(self) -> str:
        """Generate large text for benchmarking."""
        return "\n".join([f"Line {i}: This is a test line with some content." for i in range(10000)])

    def test_benchmark_string_split(self, benchmark: Any, large_text: str) -> None:
        """Benchmark string splitting."""

        def split_lines() -> list[str]:
            return large_text.split("\n")

        result = benchmark(split_lines)
        assert len(result) == 10000

    def test_benchmark_string_join(self, benchmark: Any) -> None:
        """Benchmark string joining."""
        lines = [f"Line {i}" for i in range(10000)]

        def join_lines() -> str:
            return "\n".join(lines)

        result = benchmark(join_lines)
        assert len(result) > 0

    def test_benchmark_string_replace(self, benchmark: Any, large_text: str) -> None:
        """Benchmark string replacement."""

        def replace_text() -> str:
            return large_text.replace("test", "example")

        result = benchmark(replace_text)
        assert "example" in result
