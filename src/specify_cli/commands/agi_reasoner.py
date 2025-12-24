"""CLI command for AGI reasoning engine.

Auto-generated from: ontology/agi-reasoning.ttl
Constitutional equation: agi_reasoner.py = μ(agi-reasoning.ttl)
DO NOT EDIT MANUALLY - Edit the RDF source instead.
"""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from specify_cli.core.instrumentation import instrument_command
from specify_cli.ops import agi_reasoning
from specify_cli.core.telemetry import span

console = Console()

app = typer.Typer(
    name="agi-reason",
    help="AGI reasoning and decision-making",
)


@app.command()
@instrument_command(operation_name="agi_reason_cot")
def chain_of_thought(
    question: str = typer.Argument(..., help="Question to reason about"),
    premises: Optional[str] = typer.Option(
        None, "--premises", "-p", help="Initial premises (comma-separated)"
    ),
    max_steps: int = typer.Option(10, "--max-steps", "-m"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Execute chain-of-thought reasoning."""
    with span("agi_reason_cot", question=question, max_steps=max_steps):
        try:
            # Parse premises
            premise_list = []
            if premises:
                for p in premises.split(","):
                    premise_list.append(agi_reasoning.Premise(p.strip(), confidence=1.0))

            # Execute reasoning
            chain = agi_reasoning.chain_of_thought(question, premise_list, max_steps)

            if json_output:
                import json

                output_dict = {
                    "question": question,
                    "steps": [
                        {
                            "premise": step.premise.statement,
                            "conclusion": step.conclusion,
                            "confidence": step.confidence,
                        }
                        for step in chain.steps
                    ],
                }
                console.print_json(json.dumps(output_dict))
            else:
                panel = Panel(
                    f"Question: {question}\n"
                    f"Steps: {len(chain.steps)}\n"
                    f"Final Confidence: {chain.steps[-1].confidence:.2f}" if chain.steps else "No steps",
                    title="Reasoning Chain",
                )
                console.print(panel)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e


@app.command()
@instrument_command(operation_name="agi_reason_alternatives")
def alternatives(
    goal: str = typer.Argument(..., help="Goal to find alternatives for"),
    count: int = typer.Option(10, "--count", "-c"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Generate design alternatives."""
    with span("agi_reason_alternatives", goal=goal, count=count):
        try:
            # Generate alternatives
            requirements = {"feasibility": 1.0, "optimality": 1.0, "simplicity": 0.8}
            alts = agi_reasoning.generate_alternatives(requirements, count=count)

            if json_output:
                import json

                console.print_json(json.dumps({"alternatives": alts}))
            else:
                panel = Panel(
                    f"Generated {len(alts)} alternatives for: {goal}",
                    title="Design Alternatives",
                )
                console.print(panel)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e
