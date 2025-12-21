"""Interactive REPL for HDQL queries.

This module provides an interactive shell for exploring the knowledge graph.
"""

from __future__ import annotations

import cmd
import readline  # noqa: F401  # Enables readline features
from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

if TYPE_CHECKING:
    from specify_cli.hyperdimensional.embeddings import EmbeddingDatabase

console = Console()


class HDQLShell(cmd.Cmd):
    """Interactive HDQL shell."""

    intro = """
    [bold blue]Hyperdimensional Query Language (HDQL) REPL[/bold blue]

    Type 'help' for available commands.
    Type 'examples' to see example queries.
    Type 'exit' or 'quit' to exit.
    """
    prompt = "[bold cyan]hdql>[/bold cyan] "

    def __init__(self, db: EmbeddingDatabase | None = None) -> None:
        """Initialize REPL.

        Args:
            db: Embedding database (loads default if None)
        """
        super().__init__()
        self.db = db
        self.history: list[tuple[str, any]] = []

    def preloop(self) -> None:
        """Initialize before command loop."""
        if self.db is None:
            console.print("[yellow]Loading embedding database...[/yellow]")
            from specify_cli.hyperdimensional.embeddings import load_default_database

            self.db = load_default_database()
            console.print(f"[green]Loaded {len(self.db.get_all_entities())} entities[/green]\n")

    def default(self, line: str) -> bool:
        """Handle query execution (default for non-commands)."""
        if not line.strip():
            return False

        try:
            from specify_cli.hyperdimensional import execute_query

            result = execute_query(line, embedding_db=self.db, verbose=False)
            self._display_result(result)
            self.history.append((line, result))
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

        return False

    def do_help(self, arg: str) -> None:
        """Show help."""
        if arg:
            super().do_help(arg)
        else:
            console.print(
                """
[bold]Available Commands:[/bold]

  query <HDQL>       Execute a query
  parse <HDQL>       Parse query and show AST
  explain <HDQL>     Show execution plan
  show <type>        Show all entities of type (commands, jobs, features, outcomes, constraints)
  history            Show query history
  examples           Show example queries
  clear              Clear screen
  exit/quit          Exit REPL

[bold]Query Syntax:[/bold]

  Atomic:         command("deps")
  Relational:     command("deps") -> job("python-dev")
  Similarity:     similar_to(command("deps"), distance=0.2)
  Logical:        job("python-dev") AND outcome("test-coverage")
  Optimization:   maximize(outcome_coverage) subject_to(effort <= 100)

Type any HDQL query directly at the prompt to execute it.
"""
            )

    def do_examples(self, arg: str) -> None:
        """Show example queries."""
        console.print(
            """
[bold]Example Queries:[/bold]

1. Find all commands:
   [cyan]command("*")[/cyan]

2. Find commands for Python developers:
   [cyan]command("*") -> job("python-developer")[/cyan]

3. Find similar commands to deps:
   [cyan]similar_to(command("deps"), distance=0.2)[/cyan]

4. Find features with high coverage:
   [cyan]feature("*").outcome_coverage >= 0.8[/cyan]

5. Recommend next feature to build:
   [cyan]maximize(outcome_coverage - implementation_effort)[/cyan]

6. Solve analogy:
   [cyan]command("deps") is_to feature("add") as command("cache") is_to ?[/cyan]

7. Find jobs needing test coverage:
   [cyan]job("*") -> outcome("test-coverage")[/cyan]

8. Count commands for a job:
   [cyan]count(command("*") -> job("python-developer"))[/cyan]
"""
        )

    def do_show(self, arg: str) -> None:
        """Show entities of a given type."""
        if not arg:
            console.print("[red]Usage: show <type>[/red]")
            console.print("[yellow]Types: commands, jobs, features, outcomes, constraints[/yellow]")
            return

        # Map plural to singular
        type_map = {
            "commands": "command",
            "jobs": "job",
            "features": "feature",
            "outcomes": "outcome",
            "constraints": "constraint",
        }

        entity_type = type_map.get(arg.lower(), arg)
        entities = self.db.get_entities_by_type(entity_type)

        if not entities:
            console.print(f"[yellow]No {arg} found[/yellow]")
            return

        table = Table(title=f"{arg.capitalize()}")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="yellow")

        for entity in entities:
            table.add_row(entity.name, entity.description)

        console.print(table)

    def do_history(self, arg: str) -> None:
        """Show query history."""
        if not self.history:
            console.print("[yellow]No query history[/yellow]")
            return

        console.print("[bold]Query History:[/bold]\n")
        for i, (query, _) in enumerate(self.history, 1):
            console.print(f"{i}. [cyan]{query}[/cyan]")

    def do_query(self, arg: str) -> None:
        """Execute query."""
        self.default(arg)

    def do_parse(self, arg: str) -> None:
        """Parse query and show AST."""
        if not arg:
            console.print("[red]Usage: parse <query>[/red]")
            return

        try:
            from specify_cli.hyperdimensional.parser import parse_query

            ast = parse_query(arg)
            console.print("[bold]Abstract Syntax Tree:[/bold]")
            console.print(ast)
        except Exception as e:
            console.print(f"[red]Parse Error: {e}[/red]")

    def do_explain(self, arg: str) -> None:
        """Show execution plan."""
        if not arg:
            console.print("[red]Usage: explain <query>[/red]")
            return

        try:
            from specify_cli.hyperdimensional import QueryEngine

            engine = QueryEngine(self.db)
            explanation = engine.explain(arg)
            console.print(explanation)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def do_clear(self, arg: str) -> None:
        """Clear screen."""
        console.clear()

    def do_exit(self, arg: str) -> bool:
        """Exit REPL."""
        console.print("[green]Goodbye![/green]")
        return True

    def do_quit(self, arg: str) -> bool:
        """Exit REPL."""
        return self.do_exit(arg)

    def do_EOF(self, arg: str) -> bool:  # noqa: N802
        """Handle Ctrl+D."""
        console.print()
        return self.do_exit(arg)

    def _display_result(self, result: any) -> None:
        """Display query result."""
        from specify_cli.hyperdimensional.results import (
            RecommendationResult,
            VectorQueryResult,
        )

        if isinstance(result, VectorQueryResult):
            table = Table(title="Query Results")
            table.add_column("Entity", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Score", justify="right", style="green")

            for match in result.top_k(10):
                table.add_row(
                    match.entity.name,
                    match.entity.entity_type,
                    f"{match.score:.3f}",
                )

            console.print(table)
            console.print(
                f"\n[dim]{len(result.matching_entities)} results ({result.execution_time_ms:.2f}ms)[/dim]"
            )
        elif isinstance(result, RecommendationResult):
            console.print(result.explain())
        else:
            console.print(result)


def run_repl(db: EmbeddingDatabase | None = None) -> None:
    """Run interactive HDQL REPL.

    Args:
        db: Embedding database (loads default if None)
    """
    shell = HDQLShell(db=db)

    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        console.print("\n[green]Goodbye![/green]")
