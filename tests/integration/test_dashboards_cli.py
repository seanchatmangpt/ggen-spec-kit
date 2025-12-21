"""Integration tests for dashboard CLI commands."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

# Skip if dependencies not available
pytest.importorskip("numpy")
pytest.importorskip("sklearn")

from specify_cli.commands.dashboards import app

runner = CliRunner()


def test_show_semantic_space():
    """Test semantic space visualization command."""
    result = runner.invoke(app, ["show-semantic-space", "--method", "pca", "--dimensions", "2"])

    assert result.exit_code == 0
    assert "Semantic Space 2D Projection" in result.stdout
    assert "Method: pca" in result.stdout


def test_analyze_quality():
    """Test quality analysis command."""
    result = runner.invoke(app, ["analyze-quality"])

    assert result.exit_code == 0
    assert "Semantic System Health Report" in result.stdout
    assert "Specification Quality" in result.stdout


def test_recommend_features():
    """Test feature recommendation command."""
    result = runner.invoke(app, ["recommend-features", "--job", "python-developer", "--top-k", "3"])

    assert result.exit_code == 0
    assert "Recommendations" in result.stdout


def test_monitor_system():
    """Test system monitoring command."""
    result = runner.invoke(app, ["monitor-system"])

    assert result.exit_code == 0
    assert "System Monitoring" in result.stdout


def test_export_report_html(tmp_path):
    """Test HTML report export."""
    output_file = tmp_path / "report.html"

    result = runner.invoke(
        app,
        ["export-report", "--format", "html", "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert "Report exported" in result.stdout


def test_export_report_json(tmp_path):
    """Test JSON report export."""
    output_file = tmp_path / "report.json"

    result = runner.invoke(
        app,
        ["export-report", "--format", "json", "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()


def test_semantic_space_with_output(tmp_path):
    """Test semantic space with file output."""
    output_file = tmp_path / "viz.json"

    result = runner.invoke(
        app,
        ["show-semantic-space", "--output", str(output_file)],
    )

    assert result.exit_code == 0
    assert output_file.exists()
    assert "Visualization data saved" in result.stdout
