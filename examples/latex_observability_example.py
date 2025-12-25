#!/usr/bin/env python3
"""
examples.latex_observability_example
-------------------------------------
Comprehensive example demonstrating LaTeX observability infrastructure.

This example shows:
1. Basic telemetry collection
2. Metrics analysis and anomaly detection
3. Alerting and self-healing
4. Dashboard generation and export
5. Integration with a mock LaTeX compiler

Run:
    python examples/latex_observability_example.py
"""

from __future__ import annotations

import random
import time
from pathlib import Path

from specify_cli.dspy_latex.observability import (
    AlertingSystem,
    CompilationStage,
    MetricsAnalyzer,
    PerformanceDashboard,
    PerformanceThresholds,
    SelfHealingSystem,
    TelemetryCollector,
)


def simulate_latex_compilation(
    collector: TelemetryCollector,
    document_name: str,
    should_fail: bool = False,
    is_slow: bool = False,
) -> dict:
    """
    Simulate a LaTeX compilation with observability.

    Parameters
    ----------
    collector : TelemetryCollector
        Telemetry collector instance
    document_name : str
        Name of document to compile
    should_fail : bool
        Whether compilation should fail
    is_slow : bool
        Whether compilation should be slow

    Returns
    -------
    dict
        Compilation result
    """
    with collector.track_compilation(document_name) as ctx:
        try:
            # Stage 1: Preprocessing
            print(f"  [μ₁] Preprocessing {document_name}...")
            ctx.start_stage(CompilationStage.PREPROCESSING)
            time.sleep(random.uniform(0.01, 0.05))
            ctx.end_stage(CompilationStage.PREPROCESSING)

            # Stage 2: Validation
            print(f"  [μ₂] Validating {document_name}...")
            ctx.start_stage(CompilationStage.VALIDATION)
            time.sleep(random.uniform(0.01, 0.03))

            if should_fail:
                ctx.end_stage(CompilationStage.VALIDATION)
                error_msg = f"LaTeX syntax error in {document_name}"
                ctx.record_failure(error_msg)
                ctx.record_metric("error_count", random.randint(1, 5))
                raise ValueError(error_msg)

            ctx.end_stage(CompilationStage.VALIDATION)

            # Stage 3: LaTeX Compilation
            print(f"  [μ₃] Compiling {document_name}...")
            ctx.start_stage(CompilationStage.LATEX_COMPILE)

            if is_slow:
                time.sleep(random.uniform(2.0, 3.0))  # Slow compilation
            else:
                time.sleep(random.uniform(0.1, 0.3))

            ctx.end_stage(CompilationStage.LATEX_COMPILE)

            # Stage 4: Postprocessing (BibTeX, index)
            print(f"  [μ₄] Postprocessing {document_name}...")
            ctx.start_stage(CompilationStage.POSTPROCESSING)
            time.sleep(random.uniform(0.01, 0.05))
            ctx.end_stage(CompilationStage.POSTPROCESSING)

            # Stage 5: Optimization
            print(f"  [μ₅] Optimizing PDF...")
            ctx.start_stage(CompilationStage.OPTIMIZATION)
            time.sleep(random.uniform(0.02, 0.08))
            ctx.end_stage(CompilationStage.OPTIMIZATION)

            # Record quality metrics
            pdf_size = random.randint(500_000, 5_000_000)
            page_count = random.randint(10, 200)
            warning_count = random.randint(0, 15)

            ctx.record_metric("pdf.size_bytes", pdf_size)
            ctx.record_metric("page_count", page_count)
            ctx.record_metric("error_count", 0)
            ctx.record_metric("warning_count", warning_count)

            # Record performance metrics
            ctx.record_metric("memory_peak_bytes", random.randint(100_000_000, 400_000_000))
            ctx.record_metric("cpu_usage_percent", random.uniform(30, 70))

            # Cache simulation
            ctx.metrics.cache_hits = random.randint(5, 15)
            ctx.metrics.cache_misses = random.randint(1, 5)

            # Record success
            ctx.record_success()

            print(f"  ✓ Successfully compiled {document_name}")
            print(f"    PDF: {pdf_size / 1024:.1f}KB, {page_count} pages")

            return {
                "success": True,
                "pdf_size": pdf_size,
                "page_count": page_count,
                "warnings": warning_count,
            }

        except Exception as e:
            print(f"  ✗ Compilation failed: {e}")
            return {"success": False, "error": str(e)}


def demo_basic_telemetry():
    """Demonstrate basic telemetry collection."""
    print("\n" + "=" * 80)
    print("DEMO 1: Basic Telemetry Collection")
    print("=" * 80 + "\n")

    collector = TelemetryCollector()

    # Compile multiple documents
    documents = ["paper.tex", "thesis.tex", "presentation.tex", "report.tex", "book.tex"]

    for doc in documents:
        print(f"Compiling {doc}...")
        simulate_latex_compilation(collector, doc)
        print()

    # Get summary
    summary = collector.get_metrics_summary()

    print("\n📊 METRICS SUMMARY")
    print("-" * 80)
    print(f"Total Compilations:  {summary['total_compilations']}")
    print(f"Successful:          {summary['successful_compilations']}")
    print(f"Failed:              {summary['failed_compilations']}")
    print(f"Success Rate:        {summary['success_rate']:.1%}")
    print()
    print("Duration Statistics:")
    print(f"  Mean:    {summary['duration_stats']['mean']:.3f}s")
    print(f"  Median:  {summary['duration_stats']['median']:.3f}s")
    print(f"  P95:     {summary['duration_stats']['p95']:.3f}s")
    print(f"  P99:     {summary['duration_stats']['p99']:.3f}s")
    print()
    print("Error Statistics:")
    print(f"  Total Errors:   {summary['error_stats']['total']}")
    print(f"  Mean Errors:    {summary['error_stats']['mean']:.1f}")
    print()
    print("Warning Statistics:")
    print(f"  Total Warnings: {summary['warning_stats']['total']}")
    print(f"  Mean Warnings:  {summary['warning_stats']['mean']:.1f}")


def demo_anomaly_detection():
    """Demonstrate anomaly detection."""
    print("\n" + "=" * 80)
    print("DEMO 2: Anomaly Detection")
    print("=" * 80 + "\n")

    collector = TelemetryCollector()
    analyzer = MetricsAnalyzer(collector)

    # Compile 15 normal documents
    print("Compiling 15 normal documents...")
    for i in range(15):
        simulate_latex_compilation(collector, f"normal_{i}.tex")

    # Add 3 outliers
    print("\nCompiling 3 slow documents (outliers)...")
    for i in range(3):
        simulate_latex_compilation(collector, f"slow_{i}.tex", is_slow=True)

    print("\n🔍 ANOMALY DETECTION")
    print("-" * 80)

    anomalies = analyzer.detect_anomalies()

    if anomalies:
        print(f"Detected {len(anomalies)} anomalies:\n")
        for i, anomaly in enumerate(anomalies, 1):
            print(f"{i}. {anomaly.metric_name}")
            print(f"   Current Value:    {anomaly.current_value:.3f}")
            print(
                f"   Expected Range:   [{anomaly.expected_range[0]:.3f}, {anomaly.expected_range[1]:.3f}]"
            )
            print(f"   Deviation Score:  {anomaly.deviation_score:.2f}σ")
            print(f"   Confidence:       {anomaly.confidence:.1%}")
            print()
    else:
        print("No anomalies detected.")

    # Health score
    health_score = analyzer.calculate_health_score()
    print(f"System Health Score: {health_score:.1%}")

    if health_score >= 0.9:
        print("✅ System is HEALTHY")
    elif health_score >= 0.7:
        print("⚠️  System has minor issues")
    else:
        print("🚨 System health DEGRADED")


def demo_alerting():
    """Demonstrate alerting system."""
    print("\n" + "=" * 80)
    print("DEMO 3: Alerting System")
    print("=" * 80 + "\n")

    collector = TelemetryCollector()

    # Custom thresholds
    thresholds = PerformanceThresholds(
        max_compilation_duration=2.0,  # Strict
        max_error_count=0,
        max_warning_count=5,
        min_cache_hit_rate=0.6,
    )

    analyzer = MetricsAnalyzer(collector, thresholds)
    alerting = AlertingSystem(analyzer, thresholds)

    # Create some problematic compilations
    print("Compiling documents with various issues...")

    # Slow compilation
    simulate_latex_compilation(collector, "slow_doc.tex", is_slow=True)

    # Failed compilation
    simulate_latex_compilation(collector, "error_doc.tex", should_fail=True)

    # Normal compilation with high warnings
    with collector.track_compilation("warnings.tex") as ctx:
        ctx.record_metric("warning_count", 20)
        ctx.record_success()

    print("\n🔔 GENERATING ALERTS")
    print("-" * 80)

    alerts = alerting.generate_alerts()

    if alerts:
        print(f"Generated {len(alerts)} alerts:\n")

        # Group by severity
        for severity in ["critical", "error", "warning", "info"]:
            severity_alerts = [a for a in alerts if a.severity.value == severity]
            if severity_alerts:
                icon = {"critical": "🚨", "error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity]
                print(f"{icon} {severity.upper()} ({len(severity_alerts)})")

                for alert in severity_alerts:
                    print(f"   • {alert.title}")
                    print(f"     {alert.message}")
                    print(f"     → {alert.recommended_action}")
                    print()

        # Critical alerts only
        critical = alerting.get_critical_alerts()
        if critical:
            print(f"\n⚡ {len(critical)} CRITICAL/ERROR alerts require immediate attention!")
    else:
        print("No alerts generated. System operating normally.")


def demo_self_healing():
    """Demonstrate self-healing system."""
    print("\n" + "=" * 80)
    print("DEMO 4: Self-Healing System")
    print("=" * 80 + "\n")

    collector = TelemetryCollector()
    analyzer = MetricsAnalyzer(collector)
    alerting = AlertingSystem(analyzer)
    healing = SelfHealingSystem(alerting)

    # Create failure pattern
    print("Simulating failure scenario...")
    for i in range(15):
        if i < 10:
            # First 10: normal
            simulate_latex_compilation(collector, f"doc_{i}.tex")
        else:
            # Last 5: failures
            simulate_latex_compilation(collector, f"fail_{i}.tex", should_fail=True)

    print("\n🔧 SELF-HEALING ANALYSIS")
    print("-" * 80)

    # Analyze failures
    failure_analysis = healing.analyze_failures()
    print(f"Failure Rate:        {failure_analysis['failure_rate']:.1%}")
    print(f"Total Failures:      {failure_analysis['total_failures']}")

    if "error_categories" in failure_analysis:
        print("\nError Categories:")
        for category, count in failure_analysis["error_categories"].items():
            print(f"  {category:15s}: {count}")

    # Get recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 80)

    recommendations = healing.recommend_strategy_adjustment()

    if recommendations.get("status") == "no_recommendation":
        print("No recommendations needed. System operating normally.")
    else:
        for key, value in recommendations.items():
            if not key.endswith("_reason"):
                print(f"• {key}: {value}")
                reason_key = f"{key}_reason"
                if reason_key in recommendations:
                    print(f"  Reason: {recommendations[reason_key]}")

    # Cache decision
    print("\n🔄 CACHE DECISION")
    print("-" * 80)
    if healing.should_invalidate_cache():
        print("✓ Cache invalidation RECOMMENDED (low hit rate)")
    else:
        print("✗ Cache invalidation NOT needed")

    # Fallback decision
    print("\n🛡️  FALLBACK DECISION")
    print("-" * 80)
    if healing.should_activate_fallback():
        print("✓ Fallback mechanism ACTIVATED (high failure rate)")
    else:
        print("✗ Fallback NOT needed")

    # Apply self-healing
    print("\n⚡ APPLYING SELF-HEALING")
    print("-" * 80)
    actions = healing.apply_self_healing()

    if actions["actions_taken"]:
        print(f"Executed {len(actions['actions_taken'])} self-healing actions:\n")
        for i, action in enumerate(actions["actions_taken"], 1):
            print(f"{i}. {action['action']}")
            print(f"   Reason: {action['reason']}")
    else:
        print("No self-healing actions required.")


def demo_dashboard_export():
    """Demonstrate dashboard and export functionality."""
    print("\n" + "=" * 80)
    print("DEMO 5: Dashboard and Export")
    print("=" * 80 + "\n")

    collector = TelemetryCollector()
    analyzer = MetricsAnalyzer(collector)
    dashboard = PerformanceDashboard(collector, analyzer)

    # Generate data
    print("Compiling documents for dashboard...")
    for i in range(10):
        simulate_latex_compilation(collector, f"doc_{i}.tex")

    # Export Prometheus metrics
    print("\n📈 PROMETHEUS METRICS")
    print("-" * 80)
    prom_metrics = dashboard.export_prometheus()
    print(prom_metrics[:500] + "..." if len(prom_metrics) > 500 else prom_metrics)

    # Save to file
    output_dir = Path("reports")
    output_dir.mkdir(exist_ok=True)

    prom_file = output_dir / "metrics.prom"
    dashboard.save_prometheus_metrics(prom_file)
    print(f"\n✓ Saved Prometheus metrics to: {prom_file}")

    # Dashboard JSON
    dashboard_file = output_dir / "dashboard.json"
    dashboard.save_dashboard(dashboard_file)
    print(f"✓ Saved dashboard data to: {dashboard_file}")

    # Generate report
    print("\n📄 COMPILATION REPORT")
    print("-" * 80)
    report = analyzer.generate_report()

    # Save in multiple formats
    json_report = output_dir / "report.json"
    md_report = output_dir / "report.md"

    report.save(json_report, format="json")
    report.save(md_report, format="markdown")

    print(f"✓ Saved JSON report to: {json_report}")
    print(f"✓ Saved Markdown report to: {md_report}")

    # Display markdown report
    print("\n" + report.to_markdown())


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "LaTeX Observability Demo" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")

    try:
        demo_basic_telemetry()
        demo_anomaly_detection()
        demo_alerting()
        demo_self_healing()
        demo_dashboard_export()

        print("\n" + "=" * 80)
        print("✅ All demos completed successfully!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
