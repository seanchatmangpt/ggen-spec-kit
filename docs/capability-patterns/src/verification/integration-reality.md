# 33. Integration Reality

★★

*Unit tests pass, integration fails. Integration reality tests verify that capabilities work in their actual environment—with real databases, real services, real tools.*

---

Mocks are lies. Useful lies, but lies nonetheless.

A test that mocks the database passes because the mock behaves as expected. But the real database might timeout, return unexpected formats, or have connection limits.

Integration reality tests use real dependencies:
- Real databases (not in-memory simulacra)
- Real file systems (not mock objects)
- Real external services (not stubs)
- Real CLI tools (not simulated responses)

These tests are slower and more complex. But they catch problems that mocked tests miss.

**The problem: Tests with mocks can pass while the real system fails. Only integration reality tests reveal true behavior.**

---

**The forces at play:**

- *Speed wants mocks.* Real dependencies are slow.

- *Isolation wants mocks.* Real dependencies introduce flakiness.

- *Reality wants integration.* Real dependencies reveal real problems.

- *CI wants reliability.* Flaky tests destroy CI trust.

The tension: realistic enough to catch real problems, reliable enough to trust in CI.

---

**Therefore:**

Include integration reality tests that use real dependencies, managed carefully for reliability.

**Test environment setup:**

```python
# tests/integration/conftest.py
import pytest
import tempfile
import subprocess

@pytest.fixture(scope="session")
def real_rdf_store():
    """Provide a real RDF store for integration tests."""
    # Start real Fuseki server
    proc = subprocess.Popen([
        "java", "-jar", "fuseki-server.jar",
        "--mem", "/test-dataset"
    ])
    yield "http://localhost:3030/test-dataset"
    proc.terminate()
    proc.wait()

@pytest.fixture
def real_file_system(tmp_path):
    """Provide real file system paths."""
    # Create real directory structure
    (tmp_path / "ontology").mkdir()
    (tmp_path / "output").mkdir()
    return tmp_path

@pytest.fixture
def real_ggen():
    """Verify real ggen tool is available."""
    result = subprocess.run(["ggen", "--version"], capture_output=True)
    if result.returncode != 0:
        pytest.skip("ggen not installed")
    return "ggen"
```

**Integration reality test:**

```python
# tests/integration/test_validate_real.py
"""Integration tests using real RDF tools and files."""

import subprocess
import pytest

class TestValidateIntegration:
    """Integration tests with real dependencies."""

    def test_real_rdf_validation(self, real_file_system):
        """Test validation against real RDF file with real parser."""
        # Create real RDF file
        ontology = real_file_system / "ontology" / "test.ttl"
        ontology.write_text("""
            @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
            @prefix ex: <http://example.org/> .

            ex:Person a rdfs:Class ;
                rdfs:label "Person" .
        """)

        # Run real validation (not mocked)
        result = subprocess.run(
            ["specify", "validate", str(ontology)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Valid" in result.stdout

    def test_real_shacl_validation(self, real_file_system):
        """Test SHACL validation with real shapes file."""
        # Create real data
        data = real_file_system / "data.ttl"
        data.write_text("""
            @prefix ex: <http://example.org/> .
            ex:john a ex:Person ; ex:name "John" .
        """)

        # Create real shapes
        shapes = real_file_system / "shapes.ttl"
        shapes.write_text("""
            @prefix sh: <http://www.w3.org/ns/shacl#> .
            @prefix ex: <http://example.org/> .

            ex:PersonShape a sh:NodeShape ;
                sh:targetClass ex:Person ;
                sh:property [
                    sh:path ex:name ;
                    sh:minCount 1
                ] .
        """)

        result = subprocess.run(
            ["specify", "validate", str(data), "--shapes", str(shapes)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0

    def test_real_ggen_sync(self, real_file_system, real_ggen):
        """Test ggen sync with real files and tool."""
        # Create real configuration
        config = real_file_system / "ggen.toml"
        config.write_text("""
            [[targets]]
            source = "ontology/test.ttl"
            output = "output/test.md"
            template = "templates/doc.tera"
        """)

        # Create real source and template
        (real_file_system / "ontology").mkdir(exist_ok=True)
        (real_file_system / "ontology" / "test.ttl").write_text(
            '@prefix ex: <http://example.org/> . ex:Thing a rdfs:Class .'
        )

        (real_file_system / "templates").mkdir(exist_ok=True)
        (real_file_system / "templates" / "doc.tera").write_text(
            "# Generated\n"
        )

        # Run real ggen
        result = subprocess.run(
            [real_ggen, "sync"],
            cwd=real_file_system,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert (real_file_system / "output" / "test.md").exists()
```

**Reliability strategies:**

| Problem | Solution |
|---------|----------|
| Slow tests | Run in separate CI stage |
| Flaky network | Retry with backoff |
| Resource contention | Unique ports/paths per test |
| Cleanup failures | Fixtures with cleanup |
| Missing dependencies | Skip with clear message |

---

**Resulting context:**

After applying this pattern, you have:

- Tests that reveal real integration issues
- Confidence that the system works end-to-end
- Early detection of environment problems
- Complement to faster unit/contract tests

This builds on **[32. Contract Test](./contract-test.md)** and supports **[37. Continuous Validation](./continuous-validation.md)**.

---

**Related patterns:**

- *Builds on:* **[32. Contract Test](./contract-test.md)** — Contracts then integration
- *Supports:* **[37. Continuous Validation](./continuous-validation.md)** — CI integration tests
- *Validates:* **[38. Observable Execution](./observable-execution.md)** — Real telemetry
- *Complements:* **[31. Test Before Code](./test-before-code.md)** — Different scope

---

> *"All models are wrong, but some are useful."*
>
> — George Box

Mocks are useful models. But integration reality tests verify the actual system, not the model.
