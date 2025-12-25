"""
SpiffWorkflow Automation for 3T Self-Executing Systems

This module implements the blue ocean thesis: humans are failure modes.
All workflows execute autonomously via SpiffWorkflow BPMN execution.

NO HUMAN INTERVENTION POINTS.
"""

import logging
from pathlib import Path
from typing import Any

from SpiffWorkflow.bpmn.parser.BpmnParser import BpmnParser
from SpiffWorkflow.bpmn.workflow import BpmnWorkflow
from SpiffWorkflow.task import TaskState

logger = logging.getLogger(__name__)


class SelfAutomatingSystem:
    """
    Self-automating system using SpiffWorkflow.

    Core Principle: Humans are failure modes. This system:
    1. Accepts only RDF/Turtle input (no human prose)
    2. Validates via HDITC proficiency gates
    3. Executes 3T transformation pipeline (μ) autonomously
    4. Auto-rolls back on failures (no human approval needed)
    5. Never blocks for human review

    If humans try to intervene, their changes are rejected.
    """

    def __init__(self, workflows_dir: Path | None = None):
        self.workflows_dir = workflows_dir or Path(__file__).parent.parent.parent / "workflows"
        self.workflows: dict[str, Any] = {}
        self._load_workflows()

    def _load_workflows(self) -> None:
        """Load all BPMN workflows from workflows directory."""
        if not self.workflows_dir.exists():
            logger.warning(f"Workflows directory not found: {self.workflows_dir}")
            return

        for bpmn_file in self.workflows_dir.glob("*.bpmn"):
            workflow_name = bpmn_file.stem
            try:
                parser = BpmnParser()
                parser.add_bpmn_file(str(bpmn_file))
                process_ids = list(parser.process_parsers.keys())

                if process_ids:
                    spec = parser.get_spec(process_ids[0])
                    self.workflows[workflow_name] = {
                        "spec": spec,
                        "file": bpmn_file,
                        "process_id": process_ids[0],
                    }
                    logger.info(f"Loaded workflow: {workflow_name}")
            except Exception as e:
                logger.exception(f"Failed to load workflow {workflow_name}: {e}")

    def execute_3t_pipeline(
        self, ontology_path: str, config_path: str = "ggen.toml"
    ) -> dict[str, Any]:
        """
        Execute the 3T transformation pipeline (μ₁ → μ₂ → μ₃ → μ₄ → μ₅).

        This is the constitutional equation: docs = μ(ontology.ttl)

        NO HUMAN INVOLVEMENT. If validation fails, auto-rollback occurs.

        Args:
            ontology_path: Path to RDF ontology
            config_path: Path to ggen.toml configuration

        Returns:
            Execution results including idempotence verification
        """
        if "3t_transformation_pipeline" not in self.workflows:
            raise ValueError("3T transformation pipeline workflow not loaded")

        workflow_spec = self.workflows["3t_transformation_pipeline"]["spec"]
        workflow = BpmnWorkflow(
            workflow_spec, {"ontology_path": ontology_path, "config_path": config_path}
        )

        logger.info("Starting 3T transformation pipeline (μ)")

        # Execute workflow to completion (NO HUMAN BLOCKS)
        while not workflow.is_completed():
            ready_tasks = list(workflow.get_tasks(state=TaskState.READY))

            if not ready_tasks:
                break

            for task in ready_tasks:
                task_name = (
                    task.task_spec.name if hasattr(task.task_spec, "name") else str(task.task_spec)
                )
                logger.info(f"Executing: {task_name}")

                # Execute task (SpiffWorkflow handles script execution)
                task.run()

            # Move workflow forward
            workflow.do_engine_steps()

        # Extract results
        final_task_data = {}
        for task in workflow.get_tasks(state=TaskState.COMPLETED):
            if hasattr(task, "data"):
                final_task_data.update(task.data)

        results = {
            "completed": workflow.is_completed(),
            "pipeline_executed": True,
            "stages": {
                "mu1_normalization": final_task_data.get("validation_passed", False),
                "mu2_extraction": final_task_data.get("extraction_passed", False),
                "mu3_emission": final_task_data.get("emission_passed", False),
                "mu4_canonicalization": final_task_data.get("canonicalization_passed", False),
                "mu5_receipt": final_task_data.get("receipt_passed", False),
            },
            "idempotent_verified": final_task_data.get("idempotent_verified", False),
            "receipt_hash": final_task_data.get("receipt_hash"),
            "auto_rollback": final_task_data.get("auto_rollback_executed", False),
            "human_intervention": False,  # ALWAYS False - humans are not allowed
        }

        if results["auto_rollback"]:
            logger.warning(f"Auto-rollback executed: {final_task_data.get('rollback_reason')}")

        return results

    def validate_change_request(self, change_request_rdf: str) -> dict[str, Any]:
        """
        Validate a change request via HDITC proficiency gate.

        This is the gatekeeping mechanism from the blue ocean thesis.

        Only change requests that:
        1. Are in RDF/Turtle format (not human prose)
        2. Demonstrate HDITC proficiency (enumerate dimensions, compute information loss)
        3. Pass constraint validation

        Are allowed through.

        Args:
            change_request_rdf: Change request in RDF/Turtle format

        Returns:
            Validation results (approved/rejected + reasons)
        """
        if "hditc_validation_gate" not in self.workflows:
            raise ValueError("HDITC validation gate workflow not loaded")

        workflow_spec = self.workflows["hditc_validation_gate"]["spec"]
        workflow = BpmnWorkflow(workflow_spec, {"change_request": change_request_rdf})

        logger.info("Validating change request via HDITC gate")

        # Execute workflow to completion
        while not workflow.is_completed():
            ready_tasks = list(workflow.get_tasks(state=TaskState.READY))

            if not ready_tasks:
                break

            for task in ready_tasks:
                task_name = (
                    task.task_spec.name if hasattr(task.task_spec, "name") else str(task.task_spec)
                )
                logger.info(f"HDITC Gate: {task_name}")

                task.run()

            workflow.do_engine_steps()

        # Extract results
        final_task_data = {}
        for task in workflow.get_tasks(state=TaskState.COMPLETED):
            if hasattr(task, "data"):
                final_task_data.update(task.data)

        # Determine outcome
        if final_task_data.get("approval_record"):
            status = "APPROVED"
            record = final_task_data["approval_record"]
        else:
            status = "REJECTED"
            record = final_task_data.get("rejection_record", {})

        results = {
            "status": status,
            "record": record,
            "hditc_proficient": final_task_data.get("hditc_proficient", False),
            "affected_dimensions": final_task_data.get("affected_dimensions"),
            "information_loss": final_task_data.get("information_loss"),
            "queue_for_mu": final_task_data.get("queue_for_mu_pipeline", False),
        }

        if status == "REJECTED":
            logger.warning(f"Change request REJECTED: {record.get('rejection_reason')}")
        else:
            logger.info("Change request APPROVED - queued for μ pipeline")

        return results

    def continuous_execution_loop(self, ontology_path: str, watch_interval: int = 60) -> None:
        """
        Continuous self-automating execution loop.

        This is the ultimate blue ocean implementation:
        1. Watch for RDF ontology changes
        2. Automatically execute 3T pipeline on changes
        3. Never block for human approval
        4. Auto-rollback on failures
        5. Run forever without human intervention

        Args:
            ontology_path: Path to watch for changes
            watch_interval: Seconds between checks (default: 60)
        """
        import hashlib
        import time
        from pathlib import Path

        logger.info("Starting continuous self-automating execution loop")
        logger.info("NO HUMAN INTERVENTION REQUIRED OR ALLOWED")

        ontology_file = Path(ontology_path)
        last_hash = None

        while True:
            try:
                if ontology_file.exists():
                    # Compute hash of ontology
                    current_hash = hashlib.sha256(ontology_file.read_bytes()).hexdigest()

                    if current_hash != last_hash:
                        logger.info(f"Ontology changed detected: {ontology_path}")

                        # Execute 3T pipeline automatically
                        results = self.execute_3t_pipeline(str(ontology_file))

                        if results["completed"] and not results["auto_rollback"]:
                            logger.info("3T pipeline completed successfully")
                            logger.info(f"Idempotence verified: {results['idempotent_verified']}")
                            logger.info(f"Receipt hash: {results['receipt_hash']}")
                            last_hash = current_hash
                        else:
                            logger.warning("3T pipeline failed - auto-rollback executed")
                            logger.warning("Ontology reverted to last valid state")
                            # Don't update last_hash - will retry with reverted version

                # Sleep until next check
                time.sleep(watch_interval)

            except KeyboardInterrupt:
                logger.info("Continuous execution loop stopped by interrupt")
                break
            except Exception as e:
                logger.exception(f"Error in continuous execution loop: {e}")
                # Continue running despite errors (self-healing)
                time.sleep(watch_interval)


def create_self_automating_cli() -> None:
    """
    Create CLI commands for self-automating system.

    This extends the specify CLI with blue ocean automation.
    """
    import typer
    from rich.console import Console

    app = typer.Typer(name="automate", help="Self-automating SpiffWorkflow execution")
    console = Console()

    @app.command("pipeline")
    def run_pipeline(
        ontology: str = typer.Argument(..., help="RDF ontology file path"),
        config: str = typer.Option("ggen.toml", help="Configuration file"),
    ) -> None:
        """Execute 3T transformation pipeline (μ) on RDF ontology."""
        system = SelfAutomatingSystem()
        console.print(f"[bold]Executing 3T Pipeline: docs = μ({ontology})[/bold]")

        results = system.execute_3t_pipeline(ontology, config)

        if results["completed"] and not results["auto_rollback"]:
            console.print("[green]✓ Pipeline completed successfully[/green]")
            console.print(f"Receipt Hash: {results['receipt_hash']}")
            console.print(f"Idempotent: {results['idempotent_verified']}")
        else:
            console.print("[red]✗ Pipeline failed - auto-rollback executed[/red]")

    @app.command("validate")
    def validate_request(
        request_file: str = typer.Argument(..., help="RDF change request file"),
    ) -> None:
        """Validate change request via HDITC proficiency gate."""
        system = SelfAutomatingSystem()

        with open(request_file) as f:
            request_rdf = f.read()

        console.print("[bold]Validating via HDITC Proficiency Gate[/bold]")

        results = system.validate_change_request(request_rdf)

        if results["status"] == "APPROVED":
            console.print("[green]✓ APPROVED[/green]")
            console.print(f"Affected Dimensions: {results['affected_dimensions']}")
            console.print(f"Information Loss: {results['information_loss']:.4%}")
        else:
            console.print("[red]✗ REJECTED[/red]")
            console.print(f"Reason: {results['record'].get('rejection_reason')}")

    @app.command("watch")
    def watch_ontology(
        ontology: str = typer.Argument(..., help="RDF ontology file to watch"),
        interval: int = typer.Option(60, help="Check interval in seconds"),
    ) -> None:
        """Continuously watch ontology and auto-execute pipeline on changes."""
        system = SelfAutomatingSystem()
        console.print("[bold]Starting continuous self-automating execution[/bold]")
        console.print("[yellow]NO HUMAN INTERVENTION REQUIRED[/yellow]")
        console.print(f"Watching: {ontology}")
        console.print(f"Interval: {interval}s")

        system.continuous_execution_loop(ontology, interval)

    return app
