# 33. Integration Reality

★★

*Unit tests pass, integration fails. Integration reality tests verify that capabilities work in their actual environment—with real databases, real services, real tools. This is where mock fantasies meet production truth.*

---

## The Mock Delusion

Mocks are lies. Useful lies, necessary lies, but lies nonetheless.

A unit test with a mocked database passes because the mock behaves as expected. The mock returns the data you programmed it to return, in the format you specified, in the time you allow. But the real database might:

- Timeout under load
- Return unexpected NULL values
- Have connection limits you exhaust
- Behave differently after schema migration
- Encode text differently than expected

The mock can't tell you these things. It's a controlled fantasy—a simplified model of reality that passes tests while hiding real problems.

Integration reality tests dispel these fantasies. They use real dependencies:

- Real databases (not in-memory simulacra)
- Real file systems (not mock objects)
- Real external services (not stubs)
- Real CLI tools (not simulated responses)

These tests are slower, more complex, and occasionally flaky. But they catch problems that mocked tests systematically miss.

---

## The Integration Problem

**The fundamental problem: Tests with mocks can pass while the real system fails. Only integration reality tests reveal true behavior in production-like conditions.**

Let us examine how mocks fail us:

### The Timeout Surprise

```python
# Unit test with mock: PASSES
def test_fetch_data(mocker):
    mock_client = mocker.patch('requests.get')
    mock_client.return_value.json.return_value = {"data": "value"}

    result = fetch_data("http://api.example.com/data")

    assert result == {"data": "value"}  # ✓ Passes!


# Production: FAILS
# requests.exceptions.Timeout: HTTPConnectionPool: Read timed out
```

The mock returns instantly. The real API takes 30 seconds and times out.

### The Format Mismatch

```python
# Unit test with mock: PASSES
def test_parse_response(mocker):
    mock_response = {"timestamp": "2025-01-15T10:30:00Z"}

    result = parse_timestamp(mock_response)

    assert result.year == 2025  # ✓ Passes!


# Production: FAILS
# Real API returns: {"timestamp": 1705315800}  # Unix epoch, not ISO format!
```

The mock returns ISO format. The real API returns Unix epoch.

### The Connection Exhaustion

```python
# Unit test with mock: PASSES
def test_bulk_operation(mocker):
    mock_db = mocker.patch('database.connect')

    for i in range(1000):
        result = process_item(i)
        assert result.success  # ✓ All pass!


# Production: FAILS
# After 100 iterations: "too many connections"
# The mock doesn't track connection pool state
```

### The Encoding Horror

```python
# Unit test with mock: PASSES
def test_store_text(mocker):
    mock_db = mocker.patch('database.insert')
    mock_db.return_value = True

    result = store_text("Hello, 世界!")

    assert result == True  # ✓ Passes!


# Production: FAILS
# UnicodeEncodeError: 'latin-1' codec can't encode characters
# Real database has different encoding configuration
```

---

## The Forces

Several tensions shape integration reality testing:

### Force: Speed vs. Realism

*Mocks are fast. Real dependencies are slow.*

A test suite with 1000 mocked tests runs in seconds. The same tests with real dependencies might take minutes or hours.

**Resolution:** Tiered testing. Fast mocked tests for rapid feedback during development. Slower integration reality tests for pre-merge verification. The fastest tests run most often; the slowest run at critical checkpoints.

### Force: Isolation vs. Reality

*Mocks provide isolation. Real dependencies introduce shared state.*

Tests that share real databases can interfere with each other. Test A creates data; Test B sees it unexpectedly.

**Resolution:** Test isolation strategies:
- Unique test databases per test run
- Transaction rollback after each test
- Data cleanup in fixtures
- Unique identifiers to prevent collision

### Force: Reliability vs. Flakiness

*Mocks are deterministic. Real dependencies can be flaky.*

Real networks have latency. Real services have downtime. Real databases have performance variance.

**Resolution:** Retry strategies with backoff. Tolerance for transient failures. Separate flaky tests from deterministic ones. Mark tests that genuinely require external services.

### Force: Coverage vs. Complexity

*More integration tests mean more coverage. More coverage means more complexity.*

Setting up real databases, services, and tools is complex. Maintaining those test environments is ongoing work.

**Resolution:** Focus integration reality tests on critical paths. Use mocks for edge cases and error conditions that are hard to reproduce with real systems. Reserve integration reality for "this must work in production" scenarios.

---

## Therefore

**Include integration reality tests that use real dependencies, managed carefully for reliability. These tests complement mocked tests by verifying behavior with actual systems.**

Integration reality test architecture:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  INTEGRATION REALITY TEST ARCHITECTURE                                   │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ TEST ENVIRONMENT SETUP                                              │ │
│  │                                                                     │ │
│  │  Session fixtures → Start real services (databases, APIs, tools)   │ │
│  │  Function fixtures → Isolate each test (unique data, cleanup)      │ │
│  │  Skip conditions → Skip if dependencies unavailable                │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ REAL DEPENDENCIES                                                   │ │
│  │                                                                     │ │
│  │  ├── Real file system (tmp_path, actual directories)               │ │
│  │  ├── Real databases (PostgreSQL, SQLite, not in-memory)            │ │
│  │  ├── Real CLI tools (ggen, rdflib, shaclvalidate)                  │ │
│  │  ├── Real HTTP services (local test servers)                       │ │
│  │  └── Real RDF stores (Fuseki, GraphDB)                             │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │ RELIABILITY STRATEGIES                                              │ │
│  │                                                                     │ │
│  │  ├── Retry with exponential backoff                                │ │
│  │  ├── Timeout handling                                              │ │
│  │  ├── Resource cleanup                                              │ │
│  │  └── Graceful degradation (skip if unavailable)                    │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Test Environment Setup

### Fixtures for Real Dependencies

```python
# tests/integration/conftest.py
"""Fixtures for integration reality tests."""

import pytest
import subprocess
import tempfile
import time
from pathlib import Path


@pytest.fixture(scope="session")
def real_rdf_store():
    """Provide a real RDF store for integration tests.

    Starts a Fuseki server for the test session.
    """
    # Check if Fuseki is available
    try:
        subprocess.run(
            ["java", "-version"],
            capture_output=True,
            check=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        pytest.skip("Java not available for Fuseki")

    fuseki_jar = Path("tools/fuseki-server.jar")
    if not fuseki_jar.exists():
        pytest.skip("Fuseki not installed")

    # Start Fuseki with in-memory dataset
    proc = subprocess.Popen(
        [
            "java", "-jar", str(fuseki_jar),
            "--mem", "/test-dataset",
            "--port", "3030"
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for startup
    time.sleep(5)

    try:
        yield "http://localhost:3030/test-dataset"
    finally:
        proc.terminate()
        proc.wait(timeout=10)


@pytest.fixture(scope="session")
def real_ggen():
    """Verify real ggen tool is available.

    Returns the ggen command if available, skips if not.
    """
    result = subprocess.run(
        ["ggen", "--version"],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        pytest.skip("ggen not installed")

    # Verify minimum version
    version = result.stdout.strip()
    if "5.0" not in version:
        pytest.skip(f"ggen version too old: {version}")

    return "ggen"


@pytest.fixture
def real_file_system(tmp_path):
    """Provide real file system paths with standard structure.

    Creates a realistic project structure for integration tests.
    """
    # Create directory structure
    (tmp_path / "ontology").mkdir()
    (tmp_path / "shapes").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "sparql").mkdir()
    (tmp_path / "output").mkdir()

    # Create minimal ggen.toml
    (tmp_path / "ggen.toml").write_text("""
        # Test configuration

        [[targets]]
        source = "ontology/test.ttl"
        query = "sparql/extract.rq"
        template = "templates/output.tera"
        output = "output/result.md"
    """)

    return tmp_path


@pytest.fixture
def real_rdf_files(real_file_system):
    """Provide real RDF files for testing.

    Creates valid Turtle files in the test file system.
    """
    # Ontology file
    ontology = real_file_system / "ontology" / "test.ttl"
    ontology.write_text("""
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix ex: <http://example.org/> .

        ex:Person a rdfs:Class ;
            rdfs:label "Person" ;
            rdfs:comment "A human being" .

        ex:name a rdfs:Property ;
            rdfs:domain ex:Person ;
            rdfs:range rdfs:Literal .
    """)

    # SPARQL query
    sparql = real_file_system / "sparql" / "extract.rq"
    sparql.write_text("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?class ?label ?comment
        WHERE {
            ?class a rdfs:Class ;
                   rdfs:label ?label .
            OPTIONAL { ?class rdfs:comment ?comment }
        }
    """)

    # Template
    template = real_file_system / "templates" / "output.tera"
    template.write_text("""
        # Classes

        {% for item in results %}
        ## {{ item.label }}

        {{ item.comment | default("No description") }}

        {% endfor %}
    """)

    return real_file_system


@pytest.fixture
def real_shapes_file(real_file_system):
    """Provide real SHACL shapes file."""
    shapes = real_file_system / "shapes" / "test-shapes.ttl"
    shapes.write_text("""
        @prefix sh: <http://www.w3.org/ns/shacl#> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
        @prefix ex: <http://example.org/> .

        ex:ClassShape a sh:NodeShape ;
            sh:targetClass rdfs:Class ;
            sh:property [
                sh:path rdfs:label ;
                sh:minCount 1 ;
                sh:datatype xsd:string ;
                sh:message "Class must have a label"
            ] .
    """)

    return shapes
```

### Skip Conditions

```python
# tests/integration/conftest.py (continued)

import shutil


def is_tool_available(name: str) -> bool:
    """Check if a command-line tool is available."""
    return shutil.which(name) is not None


requires_ggen = pytest.mark.skipif(
    not is_tool_available("ggen"),
    reason="ggen not installed"
)

requires_java = pytest.mark.skipif(
    not is_tool_available("java"),
    reason="Java not installed"
)

requires_docker = pytest.mark.skipif(
    not is_tool_available("docker"),
    reason="Docker not installed"
)
```

---

## Integration Reality Tests

### File System Integration

```python
# tests/integration/test_file_integration.py
"""Integration tests with real file system."""

import subprocess
import pytest
from pathlib import Path


class TestFileSystemIntegration:
    """Tests that use real file system operations."""

    def test_validate_real_rdf_file(self, real_rdf_files):
        """Test validation against real RDF file with real parser.

        This uses the actual rdflib parser, not a mock.
        Any encoding issues, format quirks, or parser bugs
        will be caught here.
        """
        ontology = real_rdf_files / "ontology" / "test.ttl"

        result = subprocess.run(
            ["specify", "validate", str(ontology)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"Validation failed: {result.stderr}"
        )
        assert "Valid" in result.stdout or "✓" in result.stdout

    def test_validate_with_real_shapes(self, real_rdf_files, real_shapes_file):
        """Test SHACL validation with real shapes file.

        Uses actual SHACL validation, not mocked.
        """
        ontology = real_rdf_files / "ontology" / "test.ttl"

        result = subprocess.run(
            ["specify", "validate", str(ontology), "--shapes", str(real_shapes_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"SHACL validation failed: {result.stderr}"
        )

    def test_invalid_file_produces_real_errors(self, real_file_system):
        """Test that invalid files produce real parser errors.

        The actual error format from rdflib, not a mock.
        """
        invalid_file = real_file_system / "invalid.ttl"
        invalid_file.write_text("""
            this is not valid turtle
            @prefix missing closing angle bracket
            ex:thing ex:has ex:incomplete
        """)

        result = subprocess.run(
            ["specify", "validate", str(invalid_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode != 0
        # Real error should mention line number
        assert "line" in result.stderr.lower() or "error" in result.stderr.lower()

    def test_large_file_performance(self, real_file_system):
        """Test validation performance with large file.

        Mocks can't catch performance issues.
        """
        large_file = real_file_system / "large.ttl"

        # Generate large file
        content = ["@prefix ex: <http://example.org/> ."]
        for i in range(10000):
            content.append(f"ex:resource{i} a ex:Thing ; ex:index {i} .")
        large_file.write_text("\n".join(content))

        import time
        start = time.perf_counter()

        result = subprocess.run(
            ["specify", "validate", str(large_file)],
            capture_output=True,
            text=True
        )

        duration = time.perf_counter() - start

        assert result.returncode == 0
        assert duration < 30, f"Validation took too long: {duration:.1f}s"
```

### CLI Tool Integration

```python
# tests/integration/test_ggen_integration.py
"""Integration tests with real ggen tool."""

import subprocess
import pytest
from pathlib import Path


class TestGgenIntegration:
    """Tests that use real ggen tool."""

    @pytest.mark.skipif(
        subprocess.run(["ggen", "--version"], capture_output=True).returncode != 0,
        reason="ggen not installed"
    )
    def test_ggen_sync_produces_output(self, real_rdf_files):
        """Test ggen sync with real files and real tool.

        This catches issues like:
        - Template syntax errors
        - SPARQL query issues
        - File permission problems
        - Path resolution bugs
        """
        result = subprocess.run(
            ["ggen", "sync"],
            cwd=real_rdf_files,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, (
            f"ggen sync failed: {result.stderr}"
        )

        output_file = real_rdf_files / "output" / "result.md"
        assert output_file.exists(), "Output file not created"
        assert len(output_file.read_text()) > 0, "Output file is empty"

    def test_ggen_sync_idempotent(self, real_rdf_files):
        """Test that ggen sync is idempotent with real tool.

        Run twice, verify same output.
        """
        # First run
        subprocess.run(
            ["ggen", "sync"],
            cwd=real_rdf_files,
            capture_output=True,
            check=True
        )
        output_file = real_rdf_files / "output" / "result.md"
        first_content = output_file.read_text()
        first_mtime = output_file.stat().st_mtime

        # Second run
        subprocess.run(
            ["ggen", "sync"],
            cwd=real_rdf_files,
            capture_output=True,
            check=True
        )
        second_content = output_file.read_text()

        assert first_content == second_content, "Idempotence violated"

    def test_ggen_with_invalid_config(self, real_file_system):
        """Test ggen behavior with invalid configuration.

        Real error handling, not mocked.
        """
        # Create invalid config
        (real_file_system / "ggen.toml").write_text("""
            [invalid
            not_valid_toml
        """)

        result = subprocess.run(
            ["ggen", "sync"],
            cwd=real_file_system,
            capture_output=True,
            text=True
        )

        assert result.returncode != 0
        assert "error" in result.stderr.lower() or "invalid" in result.stderr.lower()
```

### External Service Integration

```python
# tests/integration/test_service_integration.py
"""Integration tests with real external services."""

import subprocess
import pytest
import requests
import time


class TestServiceIntegration:
    """Tests that use real external services."""

    @pytest.fixture
    def local_api_server(self, real_file_system):
        """Start local API server for testing."""
        proc = subprocess.Popen(
            ["python", "-m", "specify_cli.api", "--port", "8765"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Wait for startup
        for _ in range(30):
            try:
                response = requests.get("http://localhost:8765/health")
                if response.status_code == 200:
                    break
            except requests.ConnectionError:
                pass
            time.sleep(0.5)
        else:
            proc.kill()
            pytest.skip("Could not start API server")

        yield "http://localhost:8765"

        proc.terminate()
        proc.wait(timeout=10)

    def test_api_validation_endpoint(self, local_api_server):
        """Test API endpoint with real HTTP requests.

        This catches:
        - Serialization issues
        - Content-type problems
        - Real network behavior
        """
        response = requests.post(
            f"{local_api_server}/api/v1/validate",
            json={"content": "@prefix ex: <http://example.org/> . ex:a ex:b ex:c ."},
            timeout=10
        )

        assert response.status_code == 200
        data = response.json()
        assert "valid" in data
        assert data["valid"] == True

    def test_api_handles_large_payload(self, local_api_server):
        """Test API with large payload.

        Mocks can't catch memory issues, timeout issues,
        or chunked transfer problems.
        """
        # Generate large content
        lines = ["@prefix ex: <http://example.org/> ."]
        for i in range(1000):
            lines.append(f"ex:resource{i} a ex:Thing .")
        content = "\n".join(lines)

        response = requests.post(
            f"{local_api_server}/api/v1/validate",
            json={"content": content},
            timeout=60
        )

        assert response.status_code == 200

    def test_api_concurrent_requests(self, local_api_server):
        """Test API with concurrent requests.

        Real concurrency issues only appear with real services.
        """
        import concurrent.futures

        def make_request(i):
            return requests.post(
                f"{local_api_server}/api/v1/validate",
                json={"content": f"@prefix ex: <http://example.org/> . ex:item{i} a ex:Thing ."},
                timeout=30
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(50)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]

        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count >= 45, f"Too many failures: {50 - success_count}/50"
```

---

## Reliability Strategies

### Retry with Backoff

```python
# tests/integration/helpers.py
"""Reliability helpers for integration tests."""

import time
import functools
from typing import Callable, TypeVar

T = TypeVar('T')


def retry_with_backoff(
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator to retry function with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts
        initial_delay: Initial delay between attempts in seconds
        backoff_factor: Multiplier for delay after each attempt
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        delay *= backoff_factor

            raise last_exception

        return wrapper
    return decorator


# Usage in tests
@retry_with_backoff(max_attempts=3, exceptions=(requests.Timeout,))
def fetch_with_retry(url: str) -> dict:
    """Fetch URL with automatic retry on timeout."""
    response = requests.get(url, timeout=10)
    return response.json()
```

### Resource Cleanup

```python
# tests/integration/conftest.py (continued)

import contextlib


@contextlib.contextmanager
def managed_subprocess(cmd, **kwargs):
    """Context manager for subprocess with guaranteed cleanup."""
    proc = subprocess.Popen(cmd, **kwargs)
    try:
        yield proc
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()


@pytest.fixture
def clean_database(database_url):
    """Fixture that ensures database cleanup."""
    # Setup: create test schema
    conn = connect(database_url)
    conn.execute("CREATE SCHEMA IF NOT EXISTS test_schema")

    yield conn

    # Cleanup: drop test schema
    conn.execute("DROP SCHEMA test_schema CASCADE")
    conn.close()
```

---

## Case Study: The RDF Store Integration

*A team discovers critical bugs through integration reality tests.*

### The Situation

The SpecGraph team built a specification management system. Unit tests with mocked RDF stores passed. But production failed with mysterious errors.

### The Discovery

Integration reality tests revealed:

**Issue 1: SPARQL Dialect Differences**

```python
# Unit test with mock: PASSES
def test_query(mock_store):
    mock_store.query.return_value = [{"name": "Test"}]
    result = query_store("SELECT ?name WHERE { ?x rdfs:label ?name }")
    assert result == [{"name": "Test"}]

# Integration test with real Fuseki: FAILS
def test_query_real(real_fuseki):
    # Fuseki returns RDF terms, not plain strings!
    result = query_store("SELECT ?name WHERE { ?x rdfs:label ?name }")
    # result = [{"name": Literal("Test", lang="en")}]  # Different type!
```

**Issue 2: Transaction Isolation**

```python
# Unit test: PASSES (mock has no transaction concept)
# Integration test: FAILS due to concurrent access conflicts
```

**Issue 3: Memory Limits**

```python
# Unit test: PASSES (mock returns whatever you give it)
# Integration test: FAILS at 100K triples (real store has limits)
```

### The Fix

They added comprehensive integration reality tests:

```python
class TestRdfStoreIntegration:
    """Integration tests with real RDF store."""

    def test_sparql_result_types(self, real_fuseki):
        """Verify we handle actual SPARQL result types."""
        result = query(real_fuseki, "SELECT ?s WHERE { ?s a rdfs:Class }")

        for row in result:
            # Handle real RDF term types
            subject = row["s"]
            assert hasattr(subject, "toPython") or isinstance(subject, str)

    def test_large_dataset(self, real_fuseki):
        """Verify store handles expected data volume."""
        # Load 100K triples
        triples = generate_triples(100000)
        load_data(real_fuseki, triples)

        # Verify count
        result = query(real_fuseki, "SELECT (COUNT(*) as ?count) WHERE { ?s ?p ?o }")
        assert int(result[0]["count"]) == 100000

    def test_concurrent_writes(self, real_fuseki):
        """Verify concurrent write handling."""
        import concurrent.futures

        def write_data(i):
            insert(real_fuseki, f"<http://example.org/item{i}> a <http://example.org/Thing> .")

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(write_data, i) for i in range(100)]
            concurrent.futures.wait(futures)

        # Verify all writes succeeded
        result = query(real_fuseki, "SELECT (COUNT(*) as ?count) WHERE { ?s a <http://example.org/Thing> }")
        assert int(result[0]["count"]) == 100
```

### The Results

| Issue Type | Found by Unit Tests | Found by Integration Tests |
|------------|--------------------|-----------------------------|
| Type mismatches | 0 | 7 |
| Performance issues | 0 | 4 |
| Concurrency bugs | 0 | 3 |
| Encoding problems | 0 | 2 |

Integration reality tests caught 16 bugs that unit tests missed.

---

## Anti-Patterns

### Anti-Pattern: Mock Everything

*"Mocks make tests fast and reliable."*

Mocking everything creates a fantasy world. Tests pass while production fails.

**Resolution:** Use mocks for unit tests. Use real dependencies for integration tests. Both are necessary.

### Anti-Pattern: Integration Tests as Unit Tests

*"Our integration tests verify internal logic."*

Integration tests should verify system behavior with real dependencies, not internal implementation.

**Resolution:** Focus integration tests on real-world scenarios. Use unit tests for internal logic.

### Anti-Pattern: Ignoring Flakiness

*"That test is flaky, just retry it."*

Flaky tests may indicate real issues—race conditions, resource limits, timing problems.

**Resolution:** Investigate flaky tests. They often reveal real integration issues. Mark genuinely flaky tests separately.

### Anti-Pattern: No Cleanup

*"Tests should be independent."*

Without cleanup, tests accumulate state that affects subsequent tests.

**Resolution:** Use fixtures with cleanup. Verify each test starts with clean state.

---

## Implementation Checklist

### Environment Setup

- [ ] Create fixtures for real dependencies
- [ ] Implement skip conditions for unavailable dependencies
- [ ] Configure test isolation (unique databases, cleanup)
- [ ] Set up CI with required dependencies

### Test Coverage

- [ ] File system integration tests
- [ ] External tool integration tests
- [ ] Service/API integration tests
- [ ] Database integration tests
- [ ] Performance integration tests

### Reliability

- [ ] Implement retry strategies
- [ ] Add timeouts to all operations
- [ ] Ensure resource cleanup
- [ ] Handle transient failures gracefully

---

## Exercises

### Exercise 1: File Integration Test

Write an integration test that:
1. Creates real RDF files
2. Runs real validation
3. Verifies real output

### Exercise 2: Service Integration Test

Write an integration test that:
1. Starts a real local service
2. Makes real HTTP requests
3. Verifies real responses

### Exercise 3: Find the Mock Gap

Take a unit test with mocks. Write the corresponding integration test. What issues does the integration test reveal?

---

## Resulting Context

After implementing this pattern, you have:

- **Tests that reveal real integration issues** not caught by mocks
- **Confidence that the system works end-to-end** with actual dependencies
- **Early detection of environment problems** before production
- **Complement to faster unit/contract tests** for comprehensive coverage

Integration reality tests complete the testing pyramid—unit tests for speed, contract tests for interfaces, integration tests for truth.

---

## Related Patterns

- **Builds on:** **[32. Contract Test](./contract-test.md)** — Contracts verified before integration
- **Supports:** **[37. Continuous Validation](./continuous-validation.md)** — Integration tests in CI
- **Validates:** **[38. Observable Execution](./observable-execution.md)** — Real telemetry
- **Complements:** **[31. Test Before Code](./test-before-code.md)** — Different scope

---

## Philosophical Note

> *"All models are wrong, but some are useful."*
> — George Box

Mocks are useful models. They enable fast, isolated testing. But they are wrong—they don't capture the full complexity of real systems.

Integration reality tests don't model the production environment; they use pieces of it. They're not models at all—they're reality samples. And reality, unlike models, doesn't lie.

The wise approach uses both: mocks for speed and isolation, reality for truth.

---

**Next:** Learn how **[34. Shape Validation](./shape-validation.md)** uses SHACL to verify specifications before transformation.
