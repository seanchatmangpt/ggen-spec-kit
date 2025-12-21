"""
specify_cli.hyperdimensional.speckit_embeddings
-----------------------------------------------
Concrete embeddings for all spec-kit domain entities.

This module pre-defines embeddings for:
- All 13+ CLI commands
- JTBD personas and jobs
- Measurable outcomes
- Features and capabilities
- Architectural constraints
- Quality metrics

These embeddings enable semantic similarity analysis, recommendation
systems, and intelligent routing in the spec-kit ecosystem.

Functions
---------
initialize_speckit_embeddings() -> EmbeddingStore
    Create and return all spec-kit embeddings
get_command_embeddings() -> VectorDict
    Get all command embeddings
get_job_embeddings() -> VectorDict
    Get all JTBD job embeddings

Example
-------
    >>> from specify_cli.hyperdimensional.speckit_embeddings import initialize_speckit_embeddings
    >>> store = initialize_speckit_embeddings()
    >>> init_vec = store.get_embedding("command:init")
    >>> check_vec = store.get_embedding("command:check")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from specify_cli.hyperdimensional.embedding_store import EmbeddingStore
from specify_cli.hyperdimensional.embeddings import HyperdimensionalEmbedding

if TYPE_CHECKING:
    from specify_cli.hyperdimensional.embeddings import VectorDict

# Spec-Kit Commands (13+ commands)
SPECKIT_COMMANDS = [
    "init",  # Initialize new spec-kit project
    "check",  # Check tool availability
    "ggen-sync",  # Sync RDF to Markdown via ggen
    "version",  # Show version information
    "pm-discover",  # Process mining discovery
    "pm-conform",  # Conformance checking
    "pm-stats",  # Process statistics
    "pm-filter",  # Filter event logs
    "pm-sample",  # Sample event logs
    "spiff-validate",  # Validate SpiffWorkflow
    "spiff-run-workflow",  # Run workflow
    "build",  # Build project
    "cache-clear",  # Clear cache
]

# JTBD Personas and Jobs
SPECKIT_JOBS = [
    "developer",  # Software developer building features
    "architect",  # System architect designing solutions
    "product-manager",  # PM defining requirements
    "technical-writer",  # Writer creating documentation
    "quality-engineer",  # QE ensuring quality standards
]

# Measurable Outcomes (50+ outcomes)
SPECKIT_OUTCOMES = [
    # Performance outcomes
    "fast-startup",  # < 500ms CLI startup
    "fast-command",  # < 100ms simple commands
    "fast-transform",  # < 5s RDF transformations
    "low-memory",  # < 100MB memory usage
    "efficient-caching",  # Fast cache operations
    # Reliability outcomes
    "reliable-builds",  # Consistent build results
    "reliable-tests",  # Deterministic tests
    "reliable-transforms",  # Predictable RDF transforms
    "graceful-degradation",  # Graceful failure handling
    "error-recovery",  # Automatic error recovery
    # Quality outcomes
    "high-test-coverage",  # 80%+ test coverage
    "type-safe",  # 100% type hints
    "well-documented",  # Complete docstrings
    "linted-code",  # Clean ruff/mypy
    "secure-code",  # No secrets, validated paths
    # Usability outcomes
    "intuitive-cli",  # Easy to use commands
    "helpful-errors",  # Clear error messages
    "rich-output",  # Formatted terminal output
    "interactive-prompts",  # User-friendly prompts
    "comprehensive-help",  # Detailed help text
    # Maintainability outcomes
    "modular-design",  # Well-separated concerns
    "testable-code",  # Easy to test
    "extensible-arch",  # Easy to extend
    "minimal-coupling",  # Low dependency coupling
    "clear-contracts",  # Well-defined interfaces
    # Observability outcomes
    "full-tracing",  # Complete OTEL traces
    "metric-collection",  # Comprehensive metrics
    "error-tracking",  # Exception recording
    "performance-monitoring",  # Performance visibility
    "telemetry-export",  # Exportable telemetry
    # Integration outcomes
    "git-integration",  # Seamless git workflows
    "github-integration",  # GitHub API integration
    "ggen-integration",  # ggen v5.0.2 integration
    "rdf-integration",  # RDF/SPARQL support
    "pm4py-integration",  # Process mining support
    # Development experience
    "fast-feedback",  # Quick test/build cycles
    "easy-debugging",  # Clear debug information
    "good-defaults",  # Sensible default config
    "flexible-config",  # Configurable options
    "reproducible-builds",  # Deterministic builds
    # Documentation outcomes
    "living-docs",  # Auto-generated from RDF
    "versioned-docs",  # Version-tracked docs
    "searchable-docs",  # Indexed documentation
    "example-driven",  # Rich examples
    "tutorial-coverage",  # Complete tutorials
]

# Features (spec-kit capabilities)
SPECKIT_FEATURES = [
    "three-tier-architecture",  # Commands/Ops/Runtime separation
    "rdf-first-development",  # RDF → Markdown via ggen
    "constitutional-equation",  # spec.md = μ(feature.ttl)
    "opentelemetry-integration",  # Full OTEL instrumentation
    "process-mining",  # pm4py integration
    "workflow-automation",  # SpiffWorkflow support
    "type-safety",  # Mypy strict typing
    "quality-enforcement",  # Ruff/mypy/pytest
    "semantic-specifications",  # RDF-based specs
    "jtbd-framework",  # Jobs-to-be-Done tracking
    "rich-cli",  # Beautiful terminal output
    "interactive-init",  # Project scaffolding
    "cache-management",  # Intelligent caching
    "git-workflows",  # Git integration
    "github-api",  # GitHub integration
    "external-tools",  # ggen, gh, uv integration
]

# Architectural Constraints
SPECKIT_CONSTRAINTS = [
    "no-side-effects-in-ops",  # Ops layer must be pure
    "subprocess-only-in-runtime",  # Only runtime can exec
    "three-tier-principle",  # Strict layer separation
    "no-circular-imports",  # Prevent import cycles
    "type-hints-required",  # 100% type coverage
    "test-coverage-80-percent",  # Minimum coverage
    "no-hardcoded-secrets",  # Security requirement
    "path-validation-required",  # Validate all paths
    "list-based-commands",  # No shell=True
    "graceful-otel-fallback",  # OTEL optional
    "dependency-minimalism",  # Lean core deps
    "optional-heavy-deps",  # pm4py/SpiffWorkflow optional
]

# Quality Metrics
SPECKIT_QUALITY_METRICS = [
    "speed",  # Execution speed
    "reliability",  # Consistency and stability
    "maintainability",  # Ease of maintenance
    "testability",  # Ease of testing
    "security",  # Security posture
    "usability",  # User experience
    "observability",  # Monitoring capability
    "extensibility",  # Extension points
    "documentation",  # Documentation quality
    "type-coverage",  # Type hint coverage
]


def initialize_speckit_embeddings(
    dimensions: int = 10000,
    version: str = "0.0.25",
) -> EmbeddingStore:
    """Initialize all spec-kit domain embeddings.

    Creates embeddings for all commands, jobs, outcomes, features,
    constraints, and quality metrics.

    Parameters
    ----------
    dimensions : int, optional
        Vector dimensionality (default: 10000)
    version : str, optional
        Spec-kit version tag (default: "0.0.25")

    Returns
    -------
    EmbeddingStore
        Store with all spec-kit embeddings

    Example
    -------
    >>> store = initialize_speckit_embeddings()
    >>> print(f"Loaded {len(store)} embeddings")
    >>> # Save to RDF
    >>> store.save_to_rdf("memory/speckit-embeddings.ttl")
    """
    hde = HyperdimensionalEmbedding(dimensions=dimensions)
    store = EmbeddingStore()

    # Create command embeddings
    for cmd in SPECKIT_COMMANDS:
        vector = hde.embed_command(cmd)
        store.save_embedding(
            f"command:{cmd}",
            vector,
            metadata={"version": version, "tags": ["command", "cli"]},
        )

    # Create job embeddings
    for job in SPECKIT_JOBS:
        vector = hde.embed_job(job)
        store.save_embedding(
            f"job:{job}",
            vector,
            metadata={"version": version, "tags": ["job", "jtbd", "persona"]},
        )

    # Create outcome embeddings
    for outcome in SPECKIT_OUTCOMES:
        vector = hde.embed_outcome(outcome)
        # Infer category from outcome name
        tags = ["outcome", "measurable"]
        if any(x in outcome for x in ("fast", "efficient", "low-memory", "performance")):
            tags.append("performance")
        elif any(x in outcome for x in ("reliable", "graceful", "recovery")):
            tags.append("reliability")
        elif any(x in outcome for x in ("coverage", "type-safe", "documented", "linted")):
            tags.append("quality")
        elif any(x in outcome for x in ("intuitive", "helpful", "rich", "interactive")):
            tags.append("usability")
        elif any(x in outcome for x in ("modular", "testable", "extensible", "coupling")):
            tags.append("maintainability")
        elif any(x in outcome for x in ("tracing", "metric", "monitoring", "telemetry")):
            tags.append("observability")

        store.save_embedding(
            f"outcome:{outcome}",
            vector,
            metadata={"version": version, "tags": tags},
        )

    # Create feature embeddings
    for feature in SPECKIT_FEATURES:
        vector = hde.embed_feature(feature)
        store.save_embedding(
            f"feature:{feature}",
            vector,
            metadata={"version": version, "tags": ["feature", "capability"]},
        )

    # Create constraint embeddings
    for constraint in SPECKIT_CONSTRAINTS:
        vector = hde.embed_constraint(constraint)
        store.save_embedding(
            f"constraint:{constraint}",
            vector,
            metadata={"version": version, "tags": ["constraint", "architecture", "rule"]},
        )

    # Create quality metric embeddings
    for metric in SPECKIT_QUALITY_METRICS:
        vector = hde.embed_outcome(f"quality-{metric}")
        store.save_embedding(
            f"quality:{metric}",
            vector,
            metadata={"version": version, "tags": ["quality", "metric"]},
        )

    return store


def get_command_embeddings(store: EmbeddingStore) -> VectorDict:
    """Extract all command embeddings from store.

    Parameters
    ----------
    store : EmbeddingStore
        Embedding store

    Returns
    -------
    VectorDict
        Command embeddings
    """
    return store.get_all_commands()


def get_job_embeddings(store: EmbeddingStore) -> VectorDict:
    """Extract all job embeddings from store.

    Parameters
    ----------
    store : EmbeddingStore
        Embedding store

    Returns
    -------
    VectorDict
        Job embeddings
    """
    return store.get_all_jobs()


def get_outcome_embeddings(store: EmbeddingStore) -> VectorDict:
    """Extract all outcome embeddings from store.

    Parameters
    ----------
    store : EmbeddingStore
        Embedding store

    Returns
    -------
    VectorDict
        Outcome embeddings
    """
    return store.get_all_outcomes()


def get_feature_embeddings(store: EmbeddingStore) -> VectorDict:
    """Extract all feature embeddings from store.

    Parameters
    ----------
    store : EmbeddingStore
        Embedding store

    Returns
    -------
    VectorDict
        Feature embeddings
    """
    return store.get_all_features()


def get_constraint_embeddings(store: EmbeddingStore) -> VectorDict:
    """Extract all constraint embeddings from store.

    Parameters
    ----------
    store : EmbeddingStore
        Embedding store

    Returns
    -------
    VectorDict
        Constraint embeddings
    """
    return store.get_all_constraints()


__all__ = [
    "SPECKIT_COMMANDS",
    "SPECKIT_CONSTRAINTS",
    "SPECKIT_FEATURES",
    "SPECKIT_JOBS",
    "SPECKIT_OUTCOMES",
    "SPECKIT_QUALITY_METRICS",
    "get_command_embeddings",
    "get_constraint_embeddings",
    "get_feature_embeddings",
    "get_job_embeddings",
    "get_outcome_embeddings",
    "initialize_speckit_embeddings",
]
