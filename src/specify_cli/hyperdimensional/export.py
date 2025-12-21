"""
specify_cli.hyperdimensional.export - Export & Reporting Manager
================================================================

Export and reporting module with multiple output formats.

This module provides export capabilities for:
* **Report Generation**: Health reports, prioritization reports, quality assessments
* **Data Export**: JSON, CSV, HTML export formats
* **Presentation Generation**: Slides from analysis results

Examples
--------
    >>> from specify_cli.hyperdimensional.export import ExportManager
    >>>
    >>> exporter = ExportManager()
    >>> report = exporter.generate_semantic_health_report(system)
    >>> exporter.export_to_json(dashboard_data, "output.json")
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from specify_cli.core.telemetry import span
from specify_cli.hyperdimensional.dashboards import MetricData, VisualizationData

__all__ = [
    "ExportManager",
    "Report",
]


class Report:
    """Report data structure."""

    def __init__(
        self,
        title: str,
        summary: str,
        sections: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Initialize report.

        Parameters
        ----------
        title : str
            Report title.
        summary : str
            Executive summary.
        sections : list[dict[str, Any]]
            Report sections with content.
        metadata : dict[str, Any], optional
            Report metadata.
        """
        self.title = title
        self.summary = summary
        self.sections = sections
        self.metadata = metadata or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "title": self.title,
            "summary": self.summary,
            "sections": self.sections,
            "metadata": self.metadata,
        }


class ExportManager:
    """
    Export and reporting manager for hyperdimensional dashboards.

    This class provides comprehensive export and reporting capabilities
    in multiple formats (JSON, CSV, HTML, presentations).

    Attributes
    ----------
    default_format : str
        Default export format.
    output_dir : Path
        Default output directory for exports.
    """

    def __init__(
        self,
        default_format: str = "json",
        output_dir: Path | None = None,
    ) -> None:
        """
        Initialize export manager.

        Parameters
        ----------
        default_format : str, optional
            Default export format. Default is "json".
        output_dir : Path, optional
            Output directory. Default is current directory.
        """
        self.default_format = default_format
        self.output_dir = output_dir or Path.cwd()

    # =========================================================================
    # Report Generation
    # =========================================================================

    def generate_semantic_health_report(
        self,
        system: dict[str, Any],
    ) -> Report:
        """
        Generate overall semantic system health report.

        Comprehensive report on system health across all dimensions.

        Parameters
        ----------
        system : dict[str, Any]
            System data with metrics.

        Returns
        -------
        Report
            Health report.
        """
        with span("export.generate_semantic_health_report"):
            # Extract metrics
            spec_quality = system.get("specification_quality", 0.0)
            code_quality = system.get("code_quality", 0.0)
            test_coverage = system.get("test_coverage", 0.0)
            architecture_compliance = system.get("architecture_compliance", 0.0)

            # Calculate overall health score
            overall_health = (
                spec_quality + code_quality + test_coverage + architecture_compliance
            ) / 4.0

            # Determine health status
            if overall_health >= 0.8:
                status = "Excellent"
                health_class = "healthy"
            elif overall_health >= 0.6:
                status = "Good"
                health_class = "moderate"
            elif overall_health >= 0.4:
                status = "Fair"
                health_class = "warning"
            else:
                status = "Poor"
                health_class = "critical"

            # Build report sections
            sections = [
                {
                    "title": "Executive Summary",
                    "content": f"System Health: {status} ({overall_health:.2f}/1.00)",
                    "health_class": health_class,
                },
                {
                    "title": "Specification Quality",
                    "content": f"Score: {spec_quality:.2f}",
                    "metrics": {
                        "completeness": system.get("spec_completeness", 0.0),
                        "clarity": system.get("spec_clarity", 0.0),
                    },
                },
                {
                    "title": "Code Generation Quality",
                    "content": f"Fidelity: {code_quality:.2f}",
                    "metrics": {
                        "requirement_coverage": system.get("requirement_coverage", 0.0),
                    },
                },
                {
                    "title": "Test Coverage",
                    "content": f"Coverage: {test_coverage:.2f}",
                    "metrics": {
                        "unit_coverage": system.get("unit_coverage", 0.0),
                        "integration_coverage": system.get("integration_coverage", 0.0),
                    },
                },
                {
                    "title": "Architecture Compliance",
                    "content": f"Compliance: {architecture_compliance:.2f}",
                    "metrics": {
                        "layer_separation": system.get("layer_separation", 0.0),
                        "module_size": system.get("module_size_compliance", 0.0),
                    },
                },
            ]

            return Report(
                title="Semantic System Health Report",
                summary=f"Overall system health is {status.lower()} with a score of {overall_health:.2f}. "
                f"Key metrics include specification quality ({spec_quality:.2f}), "
                f"code quality ({code_quality:.2f}), and test coverage ({test_coverage:.2f}).",
                sections=sections,
                metadata={
                    "overall_health": overall_health,
                    "status": status,
                    "generated_at": "2024-01-01T00:00:00Z",  # Would use actual timestamp
                },
            )

    def generate_feature_prioritization_report(
        self,
        objectives: dict[str, float],
        features: list[dict[str, Any]],
    ) -> Report:
        """
        Generate feature prioritization report.

        Ranks features by alignment with objectives.

        Parameters
        ----------
        objectives : dict[str, float]
            Objectives with weights.
        features : list[dict[str, Any]]
            Features to prioritize.

        Returns
        -------
        Report
            Prioritization report.
        """
        with span("export.generate_feature_prioritization_report"):
            # Score features
            feature_scores = []
            for feature in features:
                score = 0.0
                for obj_name, obj_weight in objectives.items():
                    if obj_name in feature.get("addresses_objectives", []):
                        score += obj_weight

                total_weight = sum(objectives.values())
                normalized_score = score / total_weight if total_weight > 0 else 0.0

                feature_scores.append(
                    {
                        "name": feature.get("name", "unknown"),
                        "score": normalized_score,
                        "impact": feature.get("impact", 0.5),
                        "effort": feature.get("effort", 0.5),
                    }
                )

            # Sort by score
            feature_scores.sort(key=lambda f: f["score"], reverse=True)

            # Build sections
            sections = [
                {
                    "title": "Prioritization Criteria",
                    "content": f"Features ranked by alignment with {len(objectives)} objectives",
                    "objectives": list(objectives.keys()),
                },
                {
                    "title": "Top Priority Features",
                    "content": f"Top 5 features: {', '.join(f['name'] for f in feature_scores[:5])}",
                    "features": feature_scores[:5],
                },
                {
                    "title": "Complete Rankings",
                    "content": "All features ranked by priority",
                    "features": feature_scores,
                },
            ]

            return Report(
                title="Feature Prioritization Report",
                summary=f"Prioritized {len(features)} features based on {len(objectives)} objectives. "
                f"Top feature: {feature_scores[0]['name']} (score: {feature_scores[0]['score']:.2f})",
                sections=sections,
                metadata={
                    "n_features": len(features),
                    "n_objectives": len(objectives),
                },
            )

    def generate_outcome_delivery_report(
        self,
        features: list[dict[str, Any]],
    ) -> Report:
        """
        Generate outcome delivery report.

        Analyzes feature outcome delivery effectiveness.

        Parameters
        ----------
        features : list[dict[str, Any]]
            Features with delivery data.

        Returns
        -------
        Report
            Outcome delivery report.
        """
        with span("export.generate_outcome_delivery_report"):
            # Analyze delivery
            delivered = sum(1 for f in features if f.get("status") == "delivered")
            in_progress = sum(1 for f in features if f.get("status") == "in_progress")
            planned = sum(1 for f in features if f.get("status") == "planned")

            delivery_rate = delivered / len(features) if features else 0.0

            sections = [
                {
                    "title": "Delivery Status",
                    "content": f"Delivered: {delivered}, In Progress: {in_progress}, Planned: {planned}",
                    "metrics": {
                        "delivery_rate": delivery_rate,
                        "total_features": len(features),
                    },
                },
                {
                    "title": "Outcome Achievement",
                    "content": f"Delivery rate: {delivery_rate:.2%}",
                },
            ]

            return Report(
                title="Outcome Delivery Report",
                summary=f"{delivered} of {len(features)} features delivered ({delivery_rate:.2%} delivery rate)",
                sections=sections,
                metadata={"delivery_rate": delivery_rate},
            )

    def generate_quality_report(
        self,
        codebase: dict[str, Any],
    ) -> Report:
        """
        Generate quality assessment report.

        Comprehensive quality assessment of codebase.

        Parameters
        ----------
        codebase : dict[str, Any]
            Codebase metrics.

        Returns
        -------
        Report
            Quality report.
        """
        with span("export.generate_quality_report"):
            test_coverage = codebase.get("test_coverage", 0.0)
            layer_violations = codebase.get("layer_violations", 0)
            code_quality = codebase.get("code_quality", 0.0)

            sections = [
                {
                    "title": "Test Coverage",
                    "content": f"Overall coverage: {test_coverage:.2%}",
                    "status": "passing" if test_coverage >= 0.8 else "failing",
                },
                {
                    "title": "Architecture Compliance",
                    "content": f"Layer violations: {layer_violations}",
                    "status": "passing" if layer_violations == 0 else "failing",
                },
                {
                    "title": "Code Quality",
                    "content": f"Quality score: {code_quality:.2f}",
                },
            ]

            return Report(
                title="Quality Assessment Report",
                summary=f"Test coverage: {test_coverage:.2%}, Layer violations: {layer_violations}",
                sections=sections,
                metadata={},
            )

    # =========================================================================
    # Data Export
    # =========================================================================

    def export_to_json(
        self,
        data: Any,
        output_path: Path | str | None = None,
    ) -> str:
        """
        Export data to JSON format.

        Parameters
        ----------
        data : Any
            Data to export (dict, list, or dataclass).
        output_path : Path | str, optional
            Output file path. If None, returns JSON string.

        Returns
        -------
        str
            JSON string.
        """
        with span("export.export_to_json"):
            # Convert dataclasses to dicts
            if hasattr(data, "__dataclass_fields__") or isinstance(
                data, (VisualizationData, MetricData)
            ):
                data = asdict(data)
            elif isinstance(data, Report):
                data = data.to_dict()

            json_str = json.dumps(data, indent=2, default=str)

            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(json_str)

            return json_str

    def export_to_csv(
        self,
        data: list[dict[str, Any]],
        output_path: Path | str,
    ) -> None:
        """
        Export data to CSV format.

        Parameters
        ----------
        data : list[dict[str, Any]]
            List of dictionaries to export.
        output_path : Path | str
            Output file path.
        """
        with span("export.export_to_csv"):
            if not data:
                return

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Get all keys
            keys = set()
            for item in data:
                keys.update(item.keys())

            # Write CSV
            with open(output_file, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=sorted(keys))
                writer.writeheader()
                writer.writerows(data)

    def export_to_html(
        self,
        report: Report,
        output_path: Path | str | None = None,
    ) -> str:
        """
        Export report to HTML format.

        Parameters
        ----------
        report : Report
            Report to export.
        output_path : Path | str, optional
            Output file path. If None, returns HTML string.

        Returns
        -------
        str
            HTML string.
        """
        with span("export.export_to_html"):
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #333; }}
        h2 {{ color: #666; border-bottom: 1px solid #ddd; padding-bottom: 10px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-left: 4px solid #4CAF50; }}
        .section {{ margin: 30px 0; }}
        .healthy {{ color: #4CAF50; }}
        .moderate {{ color: #FFA500; }}
        .warning {{ color: #FF9800; }}
        .critical {{ color: #F44336; }}
    </style>
</head>
<body>
    <h1>{report.title}</h1>
    <div class="summary">
        <h2>Summary</h2>
        <p>{report.summary}</p>
    </div>
"""

            for section in report.sections:
                health_class = section.get("health_class", "")
                html += f"""
    <div class="section {health_class}">
        <h2>{section["title"]}</h2>
        <p>{section["content"]}</p>
"""

                if "metrics" in section:
                    html += "        <ul>\n"
                    for metric_name, metric_value in section["metrics"].items():
                        html += f"            <li>{metric_name}: {metric_value:.2f}</li>\n"
                    html += "        </ul>\n"

                html += "    </div>\n"

            html += """
</body>
</html>
"""

            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(html)

            return html

    def generate_presentation_slides(
        self,
        analysis: dict[str, Any],
        output_path: Path | str | None = None,
    ) -> str:
        """
        Generate presentation slides from analysis.

        Creates Markdown slides suitable for reveal.js or similar.

        Parameters
        ----------
        analysis : dict[str, Any]
            Analysis results.
        output_path : Path | str, optional
            Output file path.

        Returns
        -------
        str
            Markdown slides.
        """
        with span("export.generate_presentation_slides"):
            slides = f"""---
title: {analysis.get("title", "Analysis Results")}
---

# {analysis.get("title", "Analysis Results")}

{analysis.get("subtitle", "")}

---

## Summary

{analysis.get("summary", "No summary available")}

---

## Key Findings

"""

            findings = analysis.get("findings", [])
            for finding in findings:
                slides += f"- {finding}\n"

            slides += "\n---\n\n## Recommendations\n\n"

            recommendations = analysis.get("recommendations", [])
            for rec in recommendations:
                slides += f"- {rec}\n"

            slides += "\n---\n\n## Next Steps\n\n"

            next_steps = analysis.get("next_steps", [])
            for step in next_steps:
                slides += f"1. {step}\n"

            if output_path:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                output_file.write_text(slides)

            return slides
