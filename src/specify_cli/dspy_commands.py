"""
DSPy Commands for Specify CLI

Provides Typer commands for working with DSPy (Declarative Self-improving Python)
to enable LLM-powered specification generation and optimization.
"""

import json
import os
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

try:
    import dspy

    DSPY_AVAILABLE = True
except ImportError:
    DSPY_AVAILABLE = False

console = Console()

# Create the DSPy subcommand app
dspy_app = typer.Typer(
    name="dspy",
    help="DSPy commands for LLM-powered specification generation",
    add_completion=False,
)

# Default configuration file path
DEFAULT_CONFIG_PATH = Path(".specify") / "dspy_config.json"

# Supported LM providers
LM_PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo",
            "gpt-3.5-turbo",
            "o1",
            "o1-mini",
            "o1-preview",
        ],
        "env_var": "OPENAI_API_KEY",
    },
    "anthropic": {
        "name": "Anthropic",
        "models": [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
        "env_var": "ANTHROPIC_API_KEY",
    },
    "google": {
        "name": "Google",
        "models": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash-exp"],
        "env_var": "GOOGLE_API_KEY",
    },
    "ollama": {
        "name": "Ollama (Local)",
        "models": ["llama3.2", "llama3.1", "mistral", "codellama", "qwen2.5-coder"],
        "env_var": None,
    },
}


def check_dspy_available() -> None:
    """Check if DSPy is available and raise error if not."""
    if not DSPY_AVAILABLE:
        console.print(
            Panel(
                "[red]DSPy is not installed.[/red]\n\n"
                "Install it with:\n"
                "[cyan]pip install dspy[/cyan]\n\n"
                "Or reinstall specify-cli with DSPy support.",
                title="DSPy Not Available",
                border_style="red",
            )
        )
        raise typer.Exit(1) from None


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load DSPy configuration from file."""
    path = config_path or DEFAULT_CONFIG_PATH
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_config(config: dict[str, Any], config_path: Path | None = None) -> None:
    """Save DSPy configuration to file."""
    path = config_path or DEFAULT_CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(config, f, indent=2)
    console.print(f"[green]Configuration saved to {path}[/green]")


def get_configured_lm(config: dict[str, Any] | None = None) -> Any:
    """Get a configured DSPy LM instance based on stored config."""
    check_dspy_available()

    if config is None:
        config = load_config()

    provider = config.get("provider", "openai")
    model = config.get("model", "gpt-4o-mini")

    provider_info = LM_PROVIDERS.get(provider, {})
    env_var = provider_info.get("env_var")

    # Check for API key if required
    if env_var and not os.getenv(env_var):
        console.print(
            Panel(
                f"[red]Missing API key for {provider_info.get('name', provider)}[/red]\n\n"
                f"Set the [cyan]{env_var}[/cyan] environment variable:\n"
                f"[dim]export {env_var}=your-api-key[/dim]",
                title="API Key Required",
                border_style="red",
            )
        )
        raise typer.Exit(1) from None

    # Configure the LM based on provider
    if provider == "openai":
        lm = dspy.LM(f"openai/{model}")
    elif provider == "anthropic":
        lm = dspy.LM(f"anthropic/{model}")
    elif provider == "google":
        lm = dspy.LM(f"google/{model}")
    elif provider == "ollama":
        base_url = config.get("base_url", "http://localhost:11434")
        lm = dspy.LM(f"ollama_chat/{model}", api_base=base_url)
    else:
        lm = dspy.LM(f"{provider}/{model}")

    return lm


@dspy_app.command()
def configure(
    provider: str | None = typer.Option(
        None, "--provider", "-p", help="LM provider: openai, anthropic, google, ollama"
    ),
    model: str | None = typer.Option(None, "--model", "-m", help="Model name to use"),
    base_url: str | None = typer.Option(
        None, "--base-url", help="Base URL for Ollama or custom endpoints"
    ),
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
) -> None:
    """
    Configure DSPy language model settings.

    Examples:
        specify dspy configure --provider openai --model gpt-4o
        specify dspy configure --provider anthropic --model claude-3-5-sonnet-20241022
        specify dspy configure --provider ollama --model llama3.2 --base-url http://localhost:11434
        specify dspy configure --show
    """
    check_dspy_available()

    config = load_config()

    if show:
        if not config:
            console.print("[yellow]No DSPy configuration found.[/yellow]")
            console.print(
                "[dim]Run 'specify dspy configure --provider <provider> --model <model>' to set up.[/dim]"
            )
            return

        table = Table(title="DSPy Configuration", show_header=True, header_style="bold cyan")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="white")

        for key, value in config.items():
            table.add_row(key, str(value))

        console.print(table)

        # Show available providers
        console.print("\n[bold]Available Providers:[/bold]")
        for pkey, pinfo in LM_PROVIDERS.items():
            env_status = ""
            if pinfo.get("env_var"):
                env_set = os.getenv(pinfo["env_var"])
                env_status = (
                    " [green](configured)[/green]" if env_set else " [red](API key missing)[/red]"
                )
            console.print(f"  [cyan]{pkey}[/cyan]: {pinfo['name']}{env_status}")
        return

    if provider:
        if provider not in LM_PROVIDERS:
            console.print(f"[red]Unknown provider: {provider}[/red]")
            console.print(f"[dim]Available: {', '.join(LM_PROVIDERS.keys())}[/dim]")
            raise typer.Exit(1) from None
        config["provider"] = provider

        # Set default model if not specified
        if not model and not config.get("model"):
            config["model"] = LM_PROVIDERS[provider]["models"][0]

    if model:
        config["model"] = model

    if base_url:
        config["base_url"] = base_url

    if provider or model or base_url:
        save_config(config)

        # Show the new configuration
        console.print(
            Panel(
                f"[bold]Provider:[/bold] {config.get('provider', 'not set')}\n"
                f"[bold]Model:[/bold] {config.get('model', 'not set')}\n"
                f"[bold]Base URL:[/bold] {config.get('base_url', 'default')}",
                title="[green]DSPy Configuration Updated[/green]",
                border_style="green",
            )
        )
    else:
        console.print(
            "[yellow]No changes made. Use --provider, --model, or --base-url to configure.[/yellow]"
        )
        console.print("[dim]Use --show to view current configuration.[/dim]")


@dspy_app.command()
def run(
    signature: str = typer.Argument(
        ..., help="DSPy signature (e.g., 'question -> answer' or 'context, question -> answer')"
    ),
    input_text: str | None = typer.Option(
        None, "--input", "-i", help="Input text for the signature"
    ),
    input_file: Path | None = typer.Option(None, "--file", "-f", help="Read input from file"),
    output_file: Path | None = typer.Option(None, "--output", "-o", help="Write output to file"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed output"),
) -> None:
    """
    Run a DSPy signature with input.

    Examples:
        specify dspy run "question -> answer" --input "What is Python?"
        specify dspy run "context, question -> answer" --file context.txt --input "Summarize this"
        specify dspy run "text -> summary" --file document.md --output summary.txt
    """
    check_dspy_available()

    config = load_config()
    if not config:
        console.print("[red]DSPy not configured. Run 'specify dspy configure' first.[/red]")
        raise typer.Exit(1) from None

    # Get input
    if input_file:
        if not input_file.exists():
            console.print(f"[red]File not found: {input_file}[/red]")
            raise typer.Exit(1) from None
        file_content = input_file.read_text()
    else:
        file_content = None

    if not input_text and not file_content:
        console.print("[red]Provide input with --input or --file[/red]")
        raise typer.Exit(1) from None

    # Configure DSPy
    lm = get_configured_lm(config)
    dspy.configure(lm=lm)

    # Parse signature and create predictor
    try:
        predictor = dspy.Predict(signature)
    except Exception as e:
        console.print(f"[red]Invalid signature: {e}[/red]")
        raise typer.Exit(1) from None

    # Prepare inputs based on signature
    inputs = {}
    sig_parts = signature.split("->")
    if len(sig_parts) == 2:
        input_fields = [f.strip() for f in sig_parts[0].split(",")]

        # Map inputs to fields
        if len(input_fields) == 1:
            inputs[input_fields[0]] = input_text or file_content
        elif len(input_fields) == 2 and file_content and input_text:
            inputs[input_fields[0]] = file_content
            inputs[input_fields[1]] = input_text
        else:
            inputs[input_fields[0]] = input_text or file_content

    if verbose:
        console.print(
            Panel(
                f"[bold]Signature:[/bold] {signature}\n"
                f"[bold]Provider:[/bold] {config.get('provider')}\n"
                f"[bold]Model:[/bold] {config.get('model')}\n"
                f"[bold]Inputs:[/bold] {list(inputs.keys())}",
                title="Running DSPy Signature",
                border_style="cyan",
            )
        )

    # Run the predictor
    try:
        with console.status("[cyan]Running DSPy signature...[/cyan]"):
            result = predictor(**inputs)

        # Extract output field from signature
        output_field = sig_parts[1].strip() if len(sig_parts) == 2 else "output"
        output_value = getattr(result, output_field, str(result))

        if output_file:
            output_file.write_text(str(output_value))
            console.print(f"[green]Output written to {output_file}[/green]")
        else:
            console.print(
                Panel(
                    str(output_value),
                    title=f"[green]Result ({output_field})[/green]",
                    border_style="green",
                )
            )

        if verbose:
            console.print("\n[dim]Full result object:[/dim]")
            console.print(result)

    except Exception as e:
        console.print(f"[red]Error running signature: {e}[/red]")
        raise typer.Exit(1) from None


@dspy_app.command()
def generate(
    spec_type: str = typer.Argument(
        ..., help="Type of specification to generate: requirement, user-story, task, plan"
    ),
    description: str = typer.Option(
        ..., "--description", "-d", help="Description or context for generation"
    ),
    output_file: Path | None = typer.Option(None, "--output", "-o", help="Write output to file"),
    format_type: str = typer.Option(
        "markdown", "--format", "-f", help="Output format: markdown, ttl, json"
    ),
) -> None:
    """
    Generate specifications using DSPy.

    Examples:
        specify dspy generate requirement -d "User authentication system"
        specify dspy generate user-story -d "As a user, I want to login" -o story.md
        specify dspy generate task -d "Implement login API" --format ttl
        specify dspy generate plan -d "Build a REST API for user management"
    """
    check_dspy_available()

    config = load_config()
    if not config:
        console.print("[red]DSPy not configured. Run 'specify dspy configure' first.[/red]")
        raise typer.Exit(1) from None

    # Define signatures for different spec types
    signatures = {
        "requirement": "description -> requirement_id, title, description, acceptance_criteria, priority",
        "user-story": "description -> story_id, as_a, i_want, so_that, acceptance_criteria",
        "task": "description -> task_id, title, description, steps, estimated_effort, dependencies",
        "plan": "description -> plan_id, title, overview, phases, milestones, risks, success_criteria",
    }

    if spec_type not in signatures:
        console.print(f"[red]Unknown spec type: {spec_type}[/red]")
        console.print(f"[dim]Available: {', '.join(signatures.keys())}[/dim]")
        raise typer.Exit(1) from None

    # Configure DSPy
    lm = get_configured_lm(config)
    dspy.configure(lm=lm)

    # Create a more sophisticated signature class for structured output
    if spec_type == "requirement":

        class GenerateRequirement(dspy.Signature):
            """Generate a formal software requirement specification."""

            description: str = dspy.InputField(desc="Description of the requirement")
            requirement_id: str = dspy.OutputField(
                desc="Unique requirement identifier (e.g., REQ-001)"
            )
            title: str = dspy.OutputField(desc="Short title for the requirement")
            requirement_text: str = dspy.OutputField(desc="Formal requirement statement")
            acceptance_criteria: str = dspy.OutputField(desc="List of acceptance criteria")
            priority: str = dspy.OutputField(desc="Priority level: High, Medium, or Low")

        predictor = dspy.Predict(GenerateRequirement)

    elif spec_type == "user-story":

        class GenerateUserStory(dspy.Signature):
            """Generate a user story in standard format."""

            description: str = dspy.InputField(desc="Description or context for the user story")
            story_id: str = dspy.OutputField(desc="Unique story identifier (e.g., US-001)")
            as_a: str = dspy.OutputField(desc="The user role")
            i_want: str = dspy.OutputField(desc="The desired functionality")
            so_that: str = dspy.OutputField(desc="The benefit or value")
            acceptance_criteria: str = dspy.OutputField(desc="List of acceptance criteria")

        predictor = dspy.Predict(GenerateUserStory)

    elif spec_type == "task":

        class GenerateTask(dspy.Signature):
            """Generate a development task specification."""

            description: str = dspy.InputField(desc="Description of the task")
            task_id: str = dspy.OutputField(desc="Unique task identifier (e.g., TASK-001)")
            title: str = dspy.OutputField(desc="Short task title")
            task_description: str = dspy.OutputField(desc="Detailed task description")
            steps: str = dspy.OutputField(desc="Implementation steps")
            estimated_effort: str = dspy.OutputField(desc="Estimated effort (e.g., 2 hours, 1 day)")
            dependencies: str = dspy.OutputField(desc="Dependencies on other tasks or requirements")

        predictor = dspy.Predict(GenerateTask)

    else:  # plan

        class GeneratePlan(dspy.Signature):
            """Generate a project implementation plan."""

            description: str = dspy.InputField(desc="Description of what to plan")
            plan_id: str = dspy.OutputField(desc="Unique plan identifier (e.g., PLAN-001)")
            title: str = dspy.OutputField(desc="Plan title")
            overview: str = dspy.OutputField(desc="Plan overview and objectives")
            phases: str = dspy.OutputField(desc="Implementation phases")
            milestones: str = dspy.OutputField(desc="Key milestones")
            risks: str = dspy.OutputField(desc="Potential risks and mitigations")
            success_criteria: str = dspy.OutputField(desc="Success criteria for the plan")

        predictor = dspy.Predict(GeneratePlan)

    # Run generation
    try:
        with console.status(f"[cyan]Generating {spec_type}...[/cyan]"):
            result = predictor(description=description)

        # Format output based on format_type
        if format_type == "markdown":
            output = format_as_markdown(spec_type, result)
        elif format_type == "ttl":
            output = format_as_ttl(spec_type, result)
        elif format_type == "json":
            output = format_as_json(spec_type, result)
        else:
            output = str(result)

        if output_file:
            output_file.write_text(output)
            console.print(f"[green]Output written to {output_file}[/green]")
        elif format_type == "markdown":
            console.print(
                Panel(
                    output,
                    title=f"[green]Generated {spec_type.title()}[/green]",
                    border_style="green",
                )
            )
        elif format_type == "ttl":
            syntax = Syntax(output, "turtle", theme="monokai", line_numbers=True)
            console.print(
                Panel(
                    syntax,
                    title=f"[green]Generated {spec_type.title()} (Turtle)[/green]",
                    border_style="green",
                )
            )
        elif format_type == "json":
            syntax = Syntax(output, "json", theme="monokai", line_numbers=True)
            console.print(
                Panel(
                    syntax,
                    title=f"[green]Generated {spec_type.title()} (JSON)[/green]",
                    border_style="green",
                )
            )
        else:
            console.print(output)

    except Exception as e:
        console.print(f"[red]Error generating {spec_type}: {e}[/red]")
        raise typer.Exit(1) from None


def format_as_markdown(spec_type: str, result) -> str:
    """Format DSPy result as Markdown."""
    if spec_type == "requirement":
        return f"""# {getattr(result, "title", "Requirement")}

**ID:** {getattr(result, "requirement_id", "REQ-XXX")}
**Priority:** {getattr(result, "priority", "Medium")}

## Description

{getattr(result, "requirement_text", getattr(result, "description", ""))}

## Acceptance Criteria

{getattr(result, "acceptance_criteria", "")}
"""
    if spec_type == "user-story":
        return f"""# User Story: {getattr(result, "story_id", "US-XXX")}

**As a** {getattr(result, "as_a", "")}

**I want** {getattr(result, "i_want", "")}

**So that** {getattr(result, "so_that", "")}

## Acceptance Criteria

{getattr(result, "acceptance_criteria", "")}
"""
    if spec_type == "task":
        return f"""# {getattr(result, "title", "Task")}

**ID:** {getattr(result, "task_id", "TASK-XXX")}
**Estimated Effort:** {getattr(result, "estimated_effort", "TBD")}

## Description

{getattr(result, "task_description", getattr(result, "description", ""))}

## Implementation Steps

{getattr(result, "steps", "")}

## Dependencies

{getattr(result, "dependencies", "None")}
"""
    # plan
    return f"""# {getattr(result, "title", "Implementation Plan")}

**ID:** {getattr(result, "plan_id", "PLAN-XXX")}

## Overview

{getattr(result, "overview", "")}

## Phases

{getattr(result, "phases", "")}

## Milestones

{getattr(result, "milestones", "")}

## Risks

{getattr(result, "risks", "")}

## Success Criteria

{getattr(result, "success_criteria", "")}
"""


def format_as_ttl(spec_type: str, result) -> str:
    """Format DSPy result as RDF Turtle."""
    prefix = """@prefix spec: <http://spec-kit.dev/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

"""
    if spec_type == "requirement":
        req_id = getattr(result, "requirement_id", "REQ-001").replace("-", "_")
        return (
            prefix
            + f"""spec:{req_id} a spec:FunctionalRequirement ;
    rdfs:label "{getattr(result, "title", "")}" ;
    spec:priority "{getattr(result, "priority", "Medium")}" ;
    spec:description \"\"\"{getattr(result, "requirement_text", getattr(result, "description", ""))}\"\"\" ;
    spec:acceptanceCriteria \"\"\"{getattr(result, "acceptance_criteria", "")}\"\"\" .
"""
        )
    if spec_type == "user-story":
        story_id = getattr(result, "story_id", "US-001").replace("-", "_")
        return (
            prefix
            + f"""spec:{story_id} a spec:UserStory ;
    spec:asA "{getattr(result, "as_a", "")}" ;
    spec:iWant "{getattr(result, "i_want", "")}" ;
    spec:soThat "{getattr(result, "so_that", "")}" ;
    spec:acceptanceCriteria \"\"\"{getattr(result, "acceptance_criteria", "")}\"\"\" .
"""
        )
    if spec_type == "task":
        task_id = getattr(result, "task_id", "TASK-001").replace("-", "_")
        return (
            prefix
            + f"""spec:{task_id} a spec:Task ;
    rdfs:label "{getattr(result, "title", "")}" ;
    spec:description \"\"\"{getattr(result, "task_description", getattr(result, "description", ""))}\"\"\" ;
    spec:estimatedEffort "{getattr(result, "estimated_effort", "TBD")}" ;
    spec:steps \"\"\"{getattr(result, "steps", "")}\"\"\" .
"""
        )
    # plan
    plan_id = getattr(result, "plan_id", "PLAN-001").replace("-", "_")
    return (
        prefix
        + f"""spec:{plan_id} a spec:Plan ;
    rdfs:label "{getattr(result, "title", "")}" ;
    spec:overview \"\"\"{getattr(result, "overview", "")}\"\"\" ;
    spec:phases \"\"\"{getattr(result, "phases", "")}\"\"\" ;
    spec:milestones \"\"\"{getattr(result, "milestones", "")}\"\"\" ;
    spec:risks \"\"\"{getattr(result, "risks", "")}\"\"\" ;
    spec:successCriteria \"\"\"{getattr(result, "success_criteria", "")}\"\"\" .
"""
    )


def format_as_json(spec_type: str, result) -> str:
    """Format DSPy result as JSON."""
    data = {}

    if spec_type == "requirement":
        data = {
            "id": getattr(result, "requirement_id", "REQ-001"),
            "type": "FunctionalRequirement",
            "title": getattr(result, "title", ""),
            "description": getattr(result, "requirement_text", getattr(result, "description", "")),
            "priority": getattr(result, "priority", "Medium"),
            "acceptanceCriteria": getattr(result, "acceptance_criteria", ""),
        }
    elif spec_type == "user-story":
        data = {
            "id": getattr(result, "story_id", "US-001"),
            "type": "UserStory",
            "asA": getattr(result, "as_a", ""),
            "iWant": getattr(result, "i_want", ""),
            "soThat": getattr(result, "so_that", ""),
            "acceptanceCriteria": getattr(result, "acceptance_criteria", ""),
        }
    elif spec_type == "task":
        data = {
            "id": getattr(result, "task_id", "TASK-001"),
            "type": "Task",
            "title": getattr(result, "title", ""),
            "description": getattr(result, "task_description", getattr(result, "description", "")),
            "estimatedEffort": getattr(result, "estimated_effort", "TBD"),
            "steps": getattr(result, "steps", ""),
            "dependencies": getattr(result, "dependencies", ""),
        }
    else:  # plan
        data = {
            "id": getattr(result, "plan_id", "PLAN-001"),
            "type": "Plan",
            "title": getattr(result, "title", ""),
            "overview": getattr(result, "overview", ""),
            "phases": getattr(result, "phases", ""),
            "milestones": getattr(result, "milestones", ""),
            "risks": getattr(result, "risks", ""),
            "successCriteria": getattr(result, "success_criteria", ""),
        }

    return json.dumps(data, indent=2)


@dspy_app.command()
def optimize(
    spec_file: Path = typer.Argument(..., help="Path to specification file (TTL or JSON)"),
    metric: str = typer.Option(
        "coverage",
        "--metric",
        "-m",
        help="Optimization metric: coverage, clarity, brevity, performance",
    ),
    iterations: int = typer.Option(
        3, "--iterations", "-i", help="Number of optimization iterations"
    ),
    model: str | None = typer.Option(None, "--model", help="Override LLM model for optimization"),
    temperature: float = typer.Option(0.7, "--temperature", "-t", help="LLM temperature (0.0-1.0)"),
    output_file: Path | None = typer.Option(
        None, "--output", "-o", help="Output path for optimized spec"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed optimization progress"
    ),
) -> None:
    """
    Optimize a specification using DSPy with LLM-powered iterative refinement.

    This command uses DSPy's ChainOfThought to iteratively improve specifications
    based on the selected metric (coverage, clarity, brevity, or performance).

    The optimization process:
    1. Loads the specification file (TTL or JSON format)
    2. Creates a DSPy program for spec optimization
    3. Runs N iterations of improvement
    4. Measures improvement at each iteration
    5. Returns optimized spec with metrics

    Examples:
        # Optimize for coverage (default)
        specify dspy optimize ontology/spec-kit-schema.ttl

        # Optimize for clarity with 5 iterations
        specify dspy optimize memory/documentation.ttl --metric clarity --iterations 5

        # Save optimized output
        specify dspy optimize spec.json --output optimized_spec.json

        # Use specific model with low temperature
        specify dspy optimize spec.ttl --model gpt-4o --temperature 0.3 --verbose
    """
    from specify_cli.core.shell import timed

    @timed
    def run_optimization() -> None:
        _optimize_spec_cli(
            spec_file=spec_file,
            metric=metric,
            iterations=iterations,
            model=model,
            temperature=temperature,
            output_file=output_file,
            verbose=verbose,
        )

    run_optimization()


def _optimize_spec_cli(
    spec_file: Path,
    metric: str,
    iterations: int,
    model: str | None,
    temperature: float,
    output_file: Path | None,
    verbose: bool,
) -> None:
    """CLI wrapper for optimize_spec (separated for testing)."""
    check_dspy_available()

    # Validate inputs
    if not spec_file.exists():
        console.print(f"[red]Spec file not found: {spec_file}[/red]")
        raise typer.Exit(1) from None

    if metric not in ["coverage", "clarity", "brevity", "performance"]:
        console.print(
            f"[red]Invalid metric: {metric}. Choose: coverage, clarity, brevity, performance[/red]"
        )
        raise typer.Exit(1) from None

    if iterations < 1 or iterations > 10:
        console.print("[red]Iterations must be between 1 and 10[/red]")
        raise typer.Exit(1) from None

    if temperature < 0.0 or temperature > 1.0:
        console.print("[red]Temperature must be between 0.0 and 1.0[/red]")
        raise typer.Exit(1) from None

    # Load configuration
    config = load_config()
    if not config:
        console.print("[red]DSPy not configured. Run 'specify dspy configure' first.[/red]")
        raise typer.Exit(1) from None

    # Override model if specified
    if model:
        config["model"] = model

    # Load spec file format
    try:
        spec_format = "ttl" if spec_file.suffix.lower() in [".ttl", ".turtle", ".rdf"] else "json"
    except Exception as e:
        console.print(f"[red]Error reading spec file: {e}[/red]")
        raise typer.Exit(1) from None

    # Configure DSPy with temperature
    try:
        lm = get_configured_lm(config)
        # Update temperature if different from default
        if hasattr(lm, "kwargs"):
            lm.kwargs["temperature"] = temperature
        elif hasattr(lm, "model_kwargs"):
            lm.model_kwargs["temperature"] = temperature

        dspy.configure(lm=lm)
    except Exception as e:
        console.print(f"[red]Error configuring DSPy: {e}[/red]")
        raise typer.Exit(1) from None

    # Show optimization parameters
    console.print(
        Panel(
            f"[bold]Spec File:[/bold] {spec_file}\n"
            f"[bold]Format:[/bold] {spec_format.upper()}\n"
            f"[bold]Metric:[/bold] {metric}\n"
            f"[bold]Iterations:[/bold] {iterations}\n"
            f"[bold]Provider:[/bold] {config.get('provider', 'openai')}\n"
            f"[bold]Model:[/bold] {config.get('model', 'gpt-4o-mini')}\n"
            f"[bold]Temperature:[/bold] {temperature}",
            title="[cyan]DSPy Spec Optimization[/cyan]",
            border_style="cyan",
        )
    )

    # Run optimization using the imported function
    from specify_cli._dspy_optimize_impl import optimize_spec

    try:
        result = optimize_spec(
            spec_file=spec_file,
            metric=metric,
            iterations=iterations,
            model=config.get("model", "gpt-4o-mini"),
            temperature=temperature,
        )

        if not result.success:
            console.print(
                Panel(
                    "[red]Optimization failed[/red]\n\n"
                    "[bold]Errors:[/bold]\n" + "\n".join(f"- {e}" for e in result.errors),
                    title="Optimization Failed",
                    border_style="red",
                )
            )
            raise typer.Exit(1) from None

        # Display results
        console.print(
            Panel(
                f"[bold]Iterations:[/bold] {result.iterations}\n"
                f"[bold]Improvement:[/bold] {result.improvement:.1f}%\n"
                f"[bold]Metrics:[/bold]\n"
                + "\n".join(f"  - {k}: {v:.2f}" for k, v in result.metrics.items()),
                title="[green]Optimization Complete[/green]",
                border_style="green",
            )
        )

        # Save or display optimized spec
        if output_file:
            output_file.write_text(result.optimized_spec)
            console.print(f"[green]Optimized spec saved to: {output_file}[/green]")
        else:
            if verbose:
                console.print("\n[bold]Original Spec:[/bold]")
                console.print(
                    Panel(
                        result.original_spec[:500] + "..."
                        if len(result.original_spec) > 500
                        else result.original_spec
                    )
                )

            console.print("\n[bold cyan]Optimized Spec:[/bold cyan]")
            syntax = Syntax(result.optimized_spec, spec_format, theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="green"))

    except Exception as e:
        console.print(f"[red]Optimization error: {e}[/red]")
        if verbose:
            import traceback

            console.print(f"[dim]{traceback.format_exc()}[/dim]")
        raise typer.Exit(1) from None


@dspy_app.command()
def info() -> None:
    """
    Show DSPy installation and configuration information.
    """
    table = Table(title="DSPy Information", show_header=True, header_style="bold cyan")
    table.add_column("Item", style="cyan")
    table.add_column("Value", style="white")

    if DSPY_AVAILABLE:
        table.add_row("DSPy Installed", "[green]Yes[/green]")
        table.add_row(
            "DSPy Version", dspy.__version__ if hasattr(dspy, "__version__") else "unknown"
        )
    else:
        table.add_row("DSPy Installed", "[red]No[/red]")

    config = load_config()
    if config:
        table.add_row("Configured", "[green]Yes[/green]")
        table.add_row("Provider", config.get("provider", "not set"))
        table.add_row("Model", config.get("model", "not set"))
        if "base_url" in config:
            table.add_row("Base URL", config.get("base_url"))
    else:
        table.add_row("Configured", "[yellow]No[/yellow]")

    # Check API keys
    table.add_row("", "")
    table.add_row("[bold]API Keys[/bold]", "")
    for _provider, info in LM_PROVIDERS.items():
        if info.get("env_var"):
            env_set = os.getenv(info["env_var"])
            status = "[green]Set[/green]" if env_set else "[dim]Not set[/dim]"
            table.add_row(f"  {info['name']}", status)

    console.print(table)

    if not DSPY_AVAILABLE:
        console.print("\n[yellow]Install DSPy with: pip install dspy[/yellow]")


def get_dspy_app():
    """Return the DSPy Typer app for integration with main CLI."""
    return dspy_app


# Export optimize_spec function and result class for use in other modules
from specify_cli._dspy_optimize_impl import OptimizeResult, optimize_spec  # noqa: E402

__all__ = ["OptimizeResult", "dspy_app", "get_dspy_app", "optimize_spec"]
