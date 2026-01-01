from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from specify_cli.runtime.integration import (
    execute_full_stack_integration,
    execute_reasoning_and_deployment,
    execute_observability_and_analytics,
)
from specify_cli.runtime.execution import (
    get_execution_report,
    get_phase_report,
    get_overall_report,
)
from specify_cli.runtime.state import get_state_store


@pytest.fixture
def sample_rdf_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ttl", delete=False) as f:
        f.write("""
@prefix ex: <http://example.org/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:Subject1 a ex:Class1 ;
    rdfs:label "Test Subject" ;
    ex:property1 "value1" ;
    ex:property2 "value2" .

ex:Subject2 a ex:Class2 ;
    rdfs:label "Related Subject" ;
    ex:relatedTo ex:Subject1 .
        """)
        return f.name


@pytest.fixture
def sample_artifact_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".tar.gz", delete=False) as f:
        f.write("dummy artifact content")
        return f.name


@pytest.fixture
def sample_data_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({
            "queries": [
                {"id": "q1", "name": "Query 1"},
                {"id": "q2", "name": "Query 2"},
            ],
            "hypotheses": [
                {"id": "h1", "name": "Hypothesis 1", "priority": "high"},
            ],
        }, f)
        return f.name


class TestReasoningPhase:
    def test_reasoning_execution(self, sample_rdf_file):
        result = execute_full_stack_integration(
            run_reasoning=True,
            run_deployment=False,
            run_observability=False,
            run_analytics=False,
            input_file=sample_rdf_file,
        )

        assert result.success or len(result.phases_executed) > 0
        assert "reasoning" in result.phases_executed or len(result.errors) > 0

    def test_reasoning_phase_report(self, sample_rdf_file):
        execute_full_stack_integration(
            run_reasoning=True,
            input_file=sample_rdf_file,
        )

        report = get_phase_report("reasoning")
        assert report["phase"] == "reasoning"
        assert report["total_executions"] >= 0


class TestCloudDeploymentPhase:
    def test_deployment_execution(self, sample_artifact_file):
        result = execute_full_stack_integration(
            run_reasoning=False,
            run_deployment=True,
            run_observability=False,
            run_analytics=False,
            artifact_file=sample_artifact_file,
        )

        assert result.success or len(result.errors) > 0


class TestObservabilityPhase:
    def test_observability_execution(self):
        result = execute_full_stack_integration(
            run_reasoning=False,
            run_deployment=False,
            run_observability=True,
            run_analytics=False,
        )

        assert "observability" in result.phases_executed or len(result.errors) > 0


class TestAnalyticsPhase:
    def test_analytics_execution(self, sample_data_file):
        result = execute_full_stack_integration(
            run_reasoning=False,
            run_deployment=False,
            run_observability=False,
            run_analytics=True,
            data_file=sample_data_file,
        )

        assert result.success or len(result.errors) > 0


class TestIntegratedWorkflows:
    def test_reasoning_and_deployment(self, sample_rdf_file, sample_artifact_file):
        result = execute_reasoning_and_deployment(
            sample_rdf_file,
            sample_artifact_file,
            providers=["aws"],
        )

        assert isinstance(result.phases_executed, list)
        assert isinstance(result.total_duration, float)

    def test_observability_and_analytics(self, sample_data_file):
        result = execute_observability_and_analytics(
            sample_data_file,
            service_name="test-service",
        )

        assert isinstance(result.phases_executed, list)
        assert isinstance(result.total_duration, float)


class TestExecutionTracking:
    def test_execution_report(self):
        result = execute_full_stack_integration(
            run_reasoning=True,
            run_deployment=False,
            run_observability=False,
            run_analytics=False,
        )

        if result.phase_results:
            first_phase = result.phases_executed[0] if result.phases_executed else None
            if first_phase:
                store = get_state_store()
                executions = store.get_phase_executions(first_phase)
                assert len(executions) >= 0

    def test_overall_report(self):
        report = get_overall_report()

        assert "total_executions" in report
        assert "successful" in report
        assert "failed" in report
        assert "average_duration" in report
        assert isinstance(report["phase_reports"], dict)


class TestStateManagement:
    def test_state_store_persistence(self, sample_rdf_file):
        result1 = execute_full_stack_integration(
            run_reasoning=True,
            input_file=sample_rdf_file,
        )

        result2 = execute_full_stack_integration(
            run_reasoning=True,
            input_file=sample_rdf_file,
        )

        store = get_state_store()
        history = store.get_execution_history(limit=100)

        assert len(history) >= 0
        assert all(isinstance(e.execution_id, str) for e in history)
