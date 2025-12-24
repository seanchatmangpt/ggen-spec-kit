"""CLI command for AGI task planning.

Auto-generated from: ontology/agi-task-planning.ttl
Constitutional equation: agi_task_planner.py = μ(agi-task-planning.ttl)
DO NOT EDIT MANUALLY - Edit the RDF source instead.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.tree import Tree

from specify_cli.core.instrumentation import instrument_command
from specify_cli.ops import agi_task_planning
from specify_cli.core.telemetry import span

console = Console()

app = typer.Typer(
    name="agi-plan",
    help="AGI task planning and goal decomposition",
)


@app.command()
@instrument_command(operation_name="agi_plan_decompose")
def decompose(
    goal: str = typer.Argument(..., help="Goal description to decompose"),
    strategy: str = typer.Option(
        "hierarchical",
        "--strategy",
        "-s",
        help="Decomposition strategy (hierarchical, functional, data-flow)",
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output plan to file"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Decompose goal into tasks."""
    with span("agi_plan_decompose", goal=goal, strategy=strategy):
        try:
            # Execute decomposition
            tasks = agi_task_planning.decompose_goal(goal, goal, {}, strategy)

            # Format output
            if json_output:
                import json

                output_dict = {
                    "goal": goal,
                    "strategy": strategy,
                    "tasks": [
                        {
                            "name": t.name,
                            "complexity": t.complexity,
                            "duration": t.estimated_duration,
                            "dependencies": t.dependencies,
                        }
                        for t in tasks
                    ],
                }
                console.print_json(json.dumps(output_dict))
            else:
                # Display as tree
                tree = Tree(f"Goal: {goal}")
                for task in tasks:
                    tree.add(f"{task.name} (complexity={task.complexity:.2f})")

                panel = Panel(tree, title="Task Decomposition")
                console.print(panel)

            # Save if requested
            if output:
                output.write_text(str(tasks))
                console.print(f"[green]✓ Plan saved to {output}[/green]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e


@app.command()
@instrument_command(operation_name="agi_plan_generate")
def generate(
    goal: str = typer.Argument(..., help="Goal description"),
    strategy: str = typer.Option("hierarchical", "--strategy", "-s"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Generate execution plan."""
    with span("agi_plan_generate", goal=goal, strategy=strategy):
        try:
            # Call agi_task_planning.generate_execution_plan
            tasks = agi_task_planning.decompose_goal(goal, goal, {}, strategy)
            plan = agi_task_planning.generate_execution_plan(goal, tasks, strategy)

            if json_output:
                import json

                output_dict = {
                    "goal": goal,
                    "total_duration": plan.total_duration,
                    "parallelization_potential": plan.parallelization_potential,
                    "task_count": len(plan.tasks),
                    "critical_path": plan.critical_path,
                }
                console.print_json(json.dumps(output_dict))
            else:
                panel = Panel(
                    f"Execution plan generated with {len(plan.tasks)} tasks\n"
                    f"Total duration: {plan.total_duration:.2f}s\n"
                    f"Parallelization: {plan.parallelization_potential:.2%}",
                    title="Execution Plan",
                )
                console.print(panel)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e
