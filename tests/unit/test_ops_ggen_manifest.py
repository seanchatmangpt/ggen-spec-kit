"""Unit tests for ggen manifest operations."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from specify_cli.ops.ggen_manifest import (
    GgenManifest,
    ManifestValidationResult,
    load_manifest,
    validate_manifest,
)


@pytest.fixture
def sample_manifest(tmp_path: Path) -> Path:
    """Create sample ggen.toml."""
    manifest = tmp_path / "ggen.toml"
    manifest.write_text("""
[project]
name = "test-project"
version = "1.0.0"

[[transformations]]
name = "spec"
input_files = ["ontology/spec.ttl"]
sparql_query = "sparql/features.sparql"
template = "templates/spec.tera"
output_file = "docs/spec.md"

[[transformations]]
name = "schema"
input_files = ["ontology/schema.ttl"]
sparql_query = "sparql/schema.sparql"
template = "templates/schema.tera"
output_file = "docs/schema.md"
""")
    return manifest


@pytest.fixture
def sample_files(tmp_path: Path) -> Path:
    """Create sample RDF and other files."""
    # Create directories
    (tmp_path / "ontology").mkdir()
    (tmp_path / "sparql").mkdir()
    (tmp_path / "templates").mkdir()
    (tmp_path / "docs").mkdir()

    # Create files
    (tmp_path / "ontology" / "spec.ttl").write_text("""
@prefix : <http://example.com/> .
:Feature1 a :Feature .
""")
    (tmp_path / "ontology" / "schema.ttl").write_text("@prefix : <http://example.com/> .")
    (tmp_path / "sparql" / "features.sparql").write_text("SELECT * WHERE {}")
    (tmp_path / "sparql" / "schema.sparql").write_text("SELECT * WHERE {}")
    (tmp_path / "templates" / "spec.tera").write_text("# Spec")
    (tmp_path / "templates" / "schema.tera").write_text("# Schema")

    return tmp_path


class TestLoadManifest:
    """Tests for load_manifest function."""

    def test_load_valid_manifest(self, sample_manifest: Path) -> None:
        """Test loading valid manifest file."""
        manifest = load_manifest(sample_manifest)

        assert isinstance(manifest, GgenManifest)
        assert manifest.project["name"] == "test-project"
        assert len(manifest.transformations) == 2

    def test_load_missing_manifest(self, tmp_path: Path) -> None:
        """Test loading non-existent manifest."""
        missing = tmp_path / "missing.toml"

        with pytest.raises(FileNotFoundError):
            load_manifest(missing)

    def test_load_invalid_toml(self, tmp_path: Path) -> None:
        """Test loading invalid TOML."""
        invalid = tmp_path / "invalid.toml"
        invalid.write_text("[[transformations\n# Missing closing bracket")

        with pytest.raises(ValueError):
            load_manifest(invalid)


class TestValidateManifest:
    """Tests for validate_manifest function."""

    def test_validate_valid_manifest(
        self,
        sample_manifest: Path,
        sample_files: Path,
    ) -> None:
        """Test validating valid manifest."""
        # Change to directory with files
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(sample_files)
            manifest = load_manifest(sample_manifest)
            result = validate_manifest(manifest)

            assert result.valid
            assert len(result.errors) == 0
        finally:
            os.chdir(old_cwd)

    def test_validate_missing_input_files(self, sample_manifest: Path) -> None:
        """Test validation fails when input files missing."""
        manifest = load_manifest(sample_manifest)
        result = validate_manifest(manifest)

        assert not result.valid
        assert any("not found" in error.lower() for error in result.errors)

    def test_validate_directory_traversal(self, tmp_path: Path) -> None:
        """Test validation prevents directory traversal."""
        manifest_file = tmp_path / "ggen.toml"
        manifest_file.write_text("""
[[transformations]]
input_files = ["input.ttl"]
output_file = "../../etc/passwd"
""")

        manifest = load_manifest(manifest_file)
        result = validate_manifest(manifest)

        assert not result.valid
        assert any("traversal" in error.lower() for error in result.errors)

    def test_validate_absolute_paths(self, tmp_path: Path) -> None:
        """Test validation rejects absolute paths."""
        manifest_file = tmp_path / "ggen.toml"
        manifest_file.write_text("""
[[transformations]]
input_files = ["input.ttl"]
output_file = "/etc/passwd"
""")

        manifest = load_manifest(manifest_file)
        result = validate_manifest(manifest)

        assert not result.valid
        assert any("absolute" in error.lower() for error in result.errors)
