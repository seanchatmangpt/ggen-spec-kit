"""Minimal hyperdimensional analysis CLI commands.

This module provides a simple CLI interface to hyperdimensional computing
capabilities for semantic similarity analysis and decision support.

Commands:
- find: Find similar entities
- rank: Rank entities by objective
- check: Check constraint satisfaction
- show: Show all embeddings

Example:
    $ specify hd find init
    $ specify hd rank performance
    $ specify hd check three-tier-architecture
    $ specify hd show
"""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from specify_cli.core.telemetry import span
from specify_cli.hyperdimensional import (
    HyperdimensionalEmbedding,
    VectorOperations,
    initialize_speckit_embeddings,
)

app = typer.Typer(help="Hyperdimensional analysis and decision support")
console = Console()

# Lazy-loaded global store
_STORE = None


def _get_store():
    """Get or initialize embedding store."""
    global _STORE
    if _STORE is None:
        with console.status("[bold blue]Initializing embeddings..."):
            _STORE = initialize_speckit_embeddings()
    return _STORE


@app.command("find")
def find_similar(
    entity: Annotated[str, typer.Argument(help="Entity name to find similar items for")],
    entity_type: Annotated[
        str, typer.Option("--type", "-t", help="Entity type: command, job, outcome, feature")
    ] = "command",
    top_k: Annotated[int, typer.Option("--top", "-k", help="Number of results")] = 5,
) -> None:
    """Find entities similar to a given entity.

    Searches the embedding space for the most semantically similar entities.

    Example:
        $ specify hd find init
        $ specify hd find --type feature three-tier-architecture
    """
    with span("hd.find", entity=entity, entity_type=entity_type):
        try:
            store = _get_store()

            # Get entity embedding
            entity_key = f"{entity_type}:{entity}"
            query_vector = store.get_embedding(entity_key)

            if query_vector is None:
                console.print(f"[red]Entity not found: {entity_key}[/red]")
                console.print("\n[dim]Available entities:[/dim]")
                _show_available_entities(entity_type)
                raise typer.Exit(1)

            # Find similar entities
            hde = HyperdimensionalEmbedding()
            candidates = store.get_embeddings_by_type(entity_type)
            similar = hde.find_similar(query_vector, candidates, top_k=top_k + 1)

            # Display results (skip first one which is self)
            table = Table(title=f"Similar {entity_type}s to '{entity}'")
            table.add_column("Rank", style="cyan", justify="right")
            table.add_column("Entity", style="green")
            table.add_column("Similarity", justify="right", style="yellow")

            for rank, (entity_name, similarity) in enumerate(similar[1:], start=1):
                # Remove type prefix for display
                display_name = entity_name.split(":", 1)[-1]
                table.add_row(
                    str(rank),
                    display_name,
                    f"{similarity:.4f}",
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e


@app.command("rank")
def rank_by_objective(
    objective: Annotated[
        str, typer.Argument(help="Objective: performance, reliability, quality, usability")
    ],
    entity_type: Annotated[
        str, typer.Option("--type", "-t", help="Entity type to rank")
    ] = "feature",
    top_k: Annotated[int, typer.Option("--top", "-k", help="Number of results")] = 10,
) -> None:
    """Rank entities by how well they align with an objective.

    Uses semantic similarity to rank features, commands, or outcomes
    by alignment with a quality objective.

    Example:
        $ specify hd rank performance
        $ specify hd rank reliability --type outcome
    """
    with span("hd.rank", objective=objective, entity_type=entity_type):
        try:
            store = _get_store()
            hde = HyperdimensionalEmbedding()

            # Create objective vector from outcome
            objective_vector = hde.embed_outcome(objective)

            # Get all entities of requested type
            candidates = store.get_embeddings_by_type(entity_type)

            if not candidates:
                console.print(f"[red]No {entity_type}s found[/red]")
                raise typer.Exit(1)

            # Rank by similarity
            ranked = hde.find_similar(objective_vector, candidates, top_k=top_k)

            # Display results
            table = Table(title=f"{entity_type.capitalize()}s ranked by '{objective}'")
            table.add_column("Rank", style="cyan", justify="right")
            table.add_column(entity_type.capitalize(), style="green")
            table.add_column("Alignment", justify="right", style="yellow")
            table.add_column("Category", style="magenta")

            for rank, (entity_name, score) in enumerate(ranked, start=1):
                # Remove type prefix for display
                display_name = entity_name.split(":", 1)[-1]

                # Get metadata for category
                metadata = store.get_metadata(entity_name)
                category = ", ".join(metadata.get("tags", [])[:2]) if metadata else ""

                table.add_row(
                    str(rank),
                    display_name,
                    f"{score:.4f}",
                    category,
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e


@app.command("check")
def check_constraint(
    design: Annotated[str, typer.Argument(help="Design or feature to check")],
    design_type: Annotated[
        str, typer.Option("--type", "-t", help="Design type")
    ] = "feature",
) -> None:
    """Check how well a design satisfies architectural constraints.

    Analyzes semantic similarity between a design and all architectural
    constraints to identify potential violations.

    Example:
        $ specify hd check three-tier-architecture
        $ specify hd check process-mining --type feature
    """
    with span("hd.check", design=design, design_type=design_type):
        try:
            store = _get_store()
            hde = HyperdimensionalEmbedding()

            # Get design embedding
            design_key = f"{design_type}:{design}"
            design_vector = store.get_embedding(design_key)

            if design_vector is None:
                console.print(f"[red]Design not found: {design_key}[/red]")
                raise typer.Exit(1)

            # Get all constraints
            constraints = store.get_all_constraints()

            if not constraints:
                console.print("[yellow]No constraints defined[/yellow]")
                raise typer.Exit(0)

            # Check similarity with each constraint
            results: list[tuple[str, float]] = []
            for constraint_name, constraint_vector in constraints.items():
                similarity = VectorOperations.cosine_similarity(design_vector, constraint_vector)
                results.append((constraint_name, similarity))

            # Sort by similarity descending
            results.sort(key=lambda x: x[1], reverse=True)

            # Display results
            table = Table(title=f"Constraint Check: '{design}'")
            table.add_column("Constraint", style="cyan")
            table.add_column("Alignment", justify="right", style="yellow")
            table.add_column("Status", style="green")

            for constraint_name, similarity in results:
                # Remove type prefix
                display_name = constraint_name.split(":", 1)[-1]

                # Determine status
                if similarity > 0.7:
                    status = "✓ PASS"
                    style = "green"
                elif similarity > 0.4:
                    status = "⚠ WARN"
                    style = "yellow"
                else:
                    status = "✗ FAIL"
                    style = "red"

                # Apply color to status cell
                table.add_row(
                    display_name,
                    f"{similarity:.4f}",
                    f"[{style}]{status}[/{style}]",
                )

            console.print(table)

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e


@app.command("show")
def show_embeddings(
    entity_type: Annotated[
        str,
        typer.Option(
            "--type",
            "-t",
            help="Filter by type: command, job, outcome, feature, constraint, quality",
        ),
    ] = "all",
) -> None:
    """Show all available embeddings.

    Lists all entities in the embedding store with their metadata.

    Example:
        $ specify hd show
        $ specify hd show --type command
    """
    with span("hd.show", entity_type=entity_type):
        try:
            store = _get_store()

            # Get embeddings by type
            if entity_type == "all":
                embeddings = store.get_all_embeddings()
                title = "All Embeddings"
            else:
                embeddings = store.get_embeddings_by_type(entity_type)
                title = f"{entity_type.capitalize()} Embeddings"

            if not embeddings:
                console.print(f"[yellow]No {entity_type} embeddings found[/yellow]")
                raise typer.Exit(0)

            # Display results
            table = Table(title=title)
            table.add_column("Type", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Dimensions", justify="right", style="yellow")
            table.add_column("Tags", style="magenta")

            for entity_name, vector in sorted(embeddings.items()):
                # Split type and name
                parts = entity_name.split(":", 1)
                etype = parts[0] if len(parts) > 1 else "unknown"
                ename = parts[1] if len(parts) > 1 else entity_name

                # Get metadata
                metadata = store.get_metadata(entity_name)
                tags = ", ".join(metadata.get("tags", [])) if metadata else ""

                table.add_row(
                    etype,
                    ename,
                    str(len(vector)),
                    tags,
                )

            console.print(table)
            console.print(f"\n[dim]Total: {len(embeddings)} embeddings[/dim]")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1) from e


def _show_available_entities(entity_type: str) -> None:
    """Show available entities of a type."""
    from specify_cli.hyperdimensional.speckit_embeddings import (
        SPECKIT_COMMANDS,
        SPECKIT_CONSTRAINTS,
        SPECKIT_FEATURES,
        SPECKIT_JOBS,
        SPECKIT_OUTCOMES,
    )

    entities = {
        "command": SPECKIT_COMMANDS,
        "job": SPECKIT_JOBS,
        "outcome": SPECKIT_OUTCOMES[:10],  # Show first 10
        "feature": SPECKIT_FEATURES,
        "constraint": SPECKIT_CONSTRAINTS,
    }

    available = entities.get(entity_type, [])
    if available:
        console.print(", ".join(available))
        if entity_type == "outcome":
            console.print(f"[dim]... and {len(SPECKIT_OUTCOMES) - 10} more[/dim]")


if __name__ == "__main__":
    app()
