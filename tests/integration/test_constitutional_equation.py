"""Integration tests for the Constitutional Equation: spec.md = μ(feature.ttl).

This test suite verifies:
1. Idempotence: Running μ twice produces identical output
2. Determinism: Same input always produces same output
3. Traceability: Generated files have provenance
4. Consistency: RDF source and generated files match

The constitutional equation is the foundation of Specification-Driven Development.
"""

import hashlib
import subprocess
from pathlib import Path

import pytest


@pytest.fixture
def project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def ggen_config(project_root: Path) -> Path:
    """Get the ggen configuration file."""
    config = project_root / "docs" / "ggen.toml"
    assert config.exists(), f"ggen.toml not found at {config}"
    return config


@pytest.fixture
def rdf_sources(project_root: Path) -> list[Path]:
    """Get all RDF source files."""
    sources = [
        project_root / "ontology" / "spec-kit-schema.ttl",
        project_root / "ontology" / "spec-kit-docs-extension.ttl",
        project_root / "memory" / "philosophy.ttl",
    ]
    for source in sources:
        assert source.exists(), f"RDF source not found: {source}"
    return sources


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def run_ggen_sync(project_root: Path) -> subprocess.CompletedProcess:
    """Run ggen sync from project root with manifest path."""
    result = subprocess.run(
        ["ggen", "sync", "--manifest", str(project_root / "docs" / "ggen.toml")],
        cwd=project_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result


class TestConstitutionalEquation:
    """Test suite for the constitutional equation: spec.md = μ(feature.ttl)."""

    @pytest.mark.xfail(reason="ggen v5 manifest format not yet configured")
    def test_idempotence_mu_compose_mu_equals_mu(
        self, project_root: Path, ggen_config: Path
    ) -> None:
        """Test idempotence: μ∘μ = μ.

        Running the transformation twice on the same input should produce
        identical output.
        """
        readme = project_root / "README.md"
        assert readme.exists(), "README.md should exist"

        # First transformation: μ(input)
        result1 = run_ggen_sync(project_root)
        assert result1.returncode == 0, f"First ggen sync failed: {result1.stderr}"
        hash1 = compute_file_hash(readme)

        # Second transformation: μ(μ(input))
        result2 = run_ggen_sync(project_root)
        assert result2.returncode == 0, f"Second ggen sync failed: {result2.stderr}"
        hash2 = compute_file_hash(readme)

        # Verify μ∘μ = μ
        assert hash1 == hash2, f"Idempotence violated: {hash1} != {hash2}. μ∘μ ≠ μ"

    @pytest.mark.xfail(reason="ggen v5 manifest format not yet configured")
    def test_transformation_produces_artifacts(self, project_root: Path) -> None:
        """Test that μ transformation produces expected artifacts."""
        expected_artifacts = [
            project_root / "README.md",
            project_root / "src" / "generated" / "python-dataclass",
            project_root / "src" / "generated" / "rust-struct",
            project_root / "src" / "generated" / "typescript-interface",
        ]

        # Run transformation
        result = run_ggen_sync(project_root)
        assert result.returncode == 0, f"ggen sync failed: {result.stderr}"

        # Verify all artifacts exist
        for artifact in expected_artifacts:
            assert artifact.exists(), f"Expected artifact not found: {artifact}"
            assert artifact.stat().st_size > 0, f"Artifact is empty: {artifact}"

    def test_rdf_sources_are_valid(self, rdf_sources: list[Path]) -> None:
        """Test that RDF source files are valid Turtle syntax."""
        for source in rdf_sources:
            # Basic syntax check: must have RDF prefixes
            content = source.read_text()
            assert "@prefix" in content or "PREFIX" in content, (
                f"Invalid Turtle: {source} missing prefix declarations"
            )

            # Check for common RDF namespaces
            assert any(
                ns in content for ns in ["rdfs:", "rdf:", "owl:", "xsd:", "sk:", "spec-kit:"]
            ), f"No RDF namespaces found in {source}"

    def test_ggen_config_declares_transformations(self, ggen_config: Path) -> None:
        """Test that ggen.toml declares all transformations."""
        config_content = ggen_config.read_text()

        # Check metadata section
        assert "[metadata]" in config_content
        assert 'name = "spec-kit-transformations"' in config_content

        # Check validation section
        assert "[validation]" in config_content
        assert "shacl_shapes" in config_content

        # Check transformations exist
        assert "[[transformations.specs]]" in config_content

        # Count transformations
        transformation_count = config_content.count("[[transformations")
        assert transformation_count > 0, "No transformations declared in ggen.toml"

    @pytest.mark.xfail(reason="ggen v5 manifest format not yet configured")
    def test_determinism_same_input_same_output(self, project_root: Path) -> None:
        """Test determinism: Same RDF input always produces same output.

        This is weaker than idempotence but still important:
        - Idempotence: μ∘μ = μ (running transformation on output)
        - Determinism: μ(x) always produces same result (given same input)
        """
        readme = project_root / "README.md"

        # Run transformation
        result1 = run_ggen_sync(project_root)
        assert result1.returncode == 0
        hash1 = compute_file_hash(readme)

        # Modify timestamp (simulating re-run at different time)
        # But input RDF is unchanged
        result2 = run_ggen_sync(project_root)
        assert result2.returncode == 0
        hash2 = compute_file_hash(readme)

        # Output should be identical
        assert hash1 == hash2, "Determinism violated: same input produced different output"

    def test_rdf_line_count_statistics(self, project_root: Path) -> None:
        """Test RDF specification statistics."""
        rdf_files = list(project_root.glob("ontology/*.ttl")) + list(
            project_root.glob("memory/*.ttl")
        )

        assert len(rdf_files) > 0, "No RDF files found"

        total_lines = 0
        for rdf_file in rdf_files:
            lines = len(rdf_file.read_text().splitlines())
            total_lines += lines
            assert lines > 0, f"Empty RDF file: {rdf_file}"

        # We should have substantial RDF specifications
        assert total_lines > 100, f"Too few RDF lines ({total_lines}), specifications incomplete"

    def test_constitutional_equation_documentation_exists(self, project_root: Path) -> None:
        """Test that constitutional equation documentation exists."""
        doc = project_root / "docs" / "CONSTITUTIONAL_EQUATION.md"
        assert doc.exists(), "CONSTITUTIONAL_EQUATION.md not found"

        content = doc.read_text()
        assert "spec.md = μ(feature.ttl)" in content
        assert "μ₁ NORMALIZE" in content
        assert "μ₂ EXTRACT" in content
        assert "μ₃ EMIT" in content
        assert "μ₄ CANONICALIZE" in content
        assert "μ₅ RECEIPT" in content

    def test_claude_md_references_spec_driven(self, project_root: Path) -> None:
        """Test that CLAUDE.md references spec-driven development."""
        claude_md = project_root / "CLAUDE.md"
        assert claude_md.exists(), "CLAUDE.md not found"

        content = claude_md.read_text()
        assert "Constitutional Equation" in content
        assert "spec.md = μ(feature.ttl)" in content
        assert "RDF is the source of truth" in content
        assert "Generated files are build artifacts" in content

    @pytest.mark.slow
    @pytest.mark.xfail(reason="ggen v5 manifest format not yet configured")
    def test_full_verification_pipeline(self, project_root: Path) -> None:
        """Test the complete verification pipeline.

        This is the full workflow for verifying the constitutional equation:
        1. Run ggen sync
        2. Verify idempotence
        3. Check generated artifacts
        4. Validate RDF sources
        """
        # Step 1: Run transformation
        result = run_ggen_sync(project_root)
        assert result.returncode == 0, f"Transformation failed: {result.stderr}"

        # Step 2: Verify idempotence
        readme = project_root / "README.md"
        hash1 = compute_file_hash(readme)

        result = run_ggen_sync(project_root)
        assert result.returncode == 0
        hash2 = compute_file_hash(readme)

        assert hash1 == hash2, "Idempotence verification failed"

        # Step 3: Check generated artifacts exist and are non-empty
        generated = project_root / "src" / "generated"
        assert generated.exists()
        assert len(list(generated.iterdir())) > 0, "No generated files found"

        # Step 4: Verify RDF sources are present
        ontology_dir = project_root / "ontology"
        assert ontology_dir.exists()
        assert len(list(ontology_dir.glob("*.ttl"))) > 0, "No ontology files found"

        memory_dir = project_root / "memory"
        assert memory_dir.exists()
        assert len(list(memory_dir.glob("*.ttl"))) > 0, "No memory files found"


class TestSpecDrivenWorkflow:
    """Test the spec-driven development workflow."""

    def test_edit_rdf_not_generated_files(self, project_root: Path) -> None:
        """Test that developers should edit RDF, not generated files.

        This is a documentation test that verifies the principle is documented.
        """
        claude_md = project_root / "CLAUDE.md"
        content = claude_md.read_text()

        # Check the principle is documented
        assert "Edit RDF" in content or "edit RDF" in content
        assert "NEVER edit" in content or "Never edit" in content
        assert "generated" in content

    def test_verification_script_exists(self, project_root: Path) -> None:
        """Test that the verification script exists and is executable."""
        script = project_root / "scripts" / "verify-constitutional-equation.sh"
        assert script.exists(), "Verification script not found"

        # Check if executable (on Unix-like systems)
        import stat

        mode = script.stat().st_mode
        is_executable = bool(mode & stat.S_IXUSR)
        assert is_executable, "Verification script is not executable"

    def test_transformation_count(self, project_root: Path) -> None:
        """Test that we have multiple transformations registered."""
        ggen_config = project_root / "docs" / "ggen.toml"
        content = ggen_config.read_text()

        # Count transformation declarations
        count = content.count("[[transformations.specs]]")

        # We should have at least 10 transformations
        assert count >= 10, f"Too few transformations: {count}, expected >= 10"
