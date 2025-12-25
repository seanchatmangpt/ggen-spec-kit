"""
Database Layer Examples
=======================

Comprehensive examples demonstrating the database layer features:
- Session management and connection pooling
- CRUD operations with repositories
- Advanced querying and filtering
- Performance metrics tracking
- Audit logging
- Cache management
- Database migrations

Run this example:
    uv run python examples/database_example.py
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

from rich.console import Console
from rich.table import Table

from specify_cli.db import (
    AuditAction,
    AuditLogRepository,
    CacheRepository,
    CommandRepository,
    ConfigurationRepository,
    ExecutionStatus,
    MetricType,
    PerformanceMetricRepository,
    ProjectRepository,
    RDFSpecificationRepository,
    UserRepository,
    close_db,
    get_session,
    init_db,
)
from specify_cli.db.queries import (
    CommandQueries,
    PerformanceMetricQueries,
    ProjectQueries,
    UserQueries,
)

console = Console()


def example_1_basic_setup():
    """Example 1: Initialize database and create tables."""
    console.print("\n[bold cyan]Example 1: Basic Setup[/bold cyan]")

    # Initialize database (uses SQLite by default)
    init_db("sqlite:///./example.db")
    console.print("[green]✓[/green] Database initialized with all tables created")


def example_2_user_management():
    """Example 2: User management with repository pattern."""
    console.print("\n[bold cyan]Example 2: User Management[/bold cyan]")

    with get_session() as session:
        repo = UserRepository(session)

        # Create users
        alice = repo.create_user(
            username="alice",
            email="alice@example.com",
            password_hash=b"hashed_password_alice",
            full_name="Alice Smith",
        )
        console.print(f"[green]✓[/green] Created user: {alice.username} (ID: {alice.id})")

        bob = repo.create_user(
            username="bob",
            email="bob@example.com",
            password_hash=b"hashed_password_bob",
            full_name="Bob Jones",
            is_admin=True,
        )
        console.print(f"[green]✓[/green] Created user: {bob.username} (ID: {bob.id})")

        # Query users
        found = repo.get_by_username("alice")
        console.print(f"[blue]→[/blue] Found user by username: {found.email}")

        # Update user
        repo.update(alice.id, {"full_name": "Alice Johnson"})
        console.print(f"[green]✓[/green] Updated user {alice.username}")


def example_3_project_tracking():
    """Example 3: Project tracking and organization."""
    console.print("\n[bold cyan]Example 3: Project Tracking[/bold cyan]")

    with get_session() as session:
        user_repo = UserRepository(session)
        project_repo = ProjectRepository(session)

        # Get existing user
        user = user_repo.get_by_username("alice")

        # Create projects
        project1 = project_repo.create_project(
            name="Awesome API",
            slug="awesome-api",
            owner_id=user.id,
            description="RESTful API service",
            repository_url="https://github.com/alice/awesome-api",
        )
        console.print(f"[green]✓[/green] Created project: {project1.name}")

        project2 = project_repo.create_project(
            name="Data Pipeline",
            slug="data-pipeline",
            owner_id=user.id,
            description="ETL data processing pipeline",
        )
        console.print(f"[green]✓[/green] Created project: {project2.name}")

        # Query user's projects
        queries = ProjectQueries(session)
        user_projects = queries.find_by_owner(user.id)
        console.print(f"[blue]→[/blue] User has {len(user_projects)} project(s)")


def example_4_command_execution():
    """Example 4: Track command execution history."""
    console.print("\n[bold cyan]Example 4: Command Execution Tracking[/bold cyan]")

    with get_session() as session:
        user_repo = UserRepository(session)
        project_repo = ProjectRepository(session)
        cmd_repo = CommandRepository(session)

        user = user_repo.get_by_username("alice")
        project = project_repo.get_by_slug("awesome-api")

        # Start command
        cmd = cmd_repo.start_command(
            name="specify init",
            args="--verbose --dry-run",
            user_id=user.id,
            project_id=project.id,
        )
        console.print(f"[green]✓[/green] Started command: {cmd.name} (ID: {cmd.command_id})")

        # Simulate command execution
        import time
        time.sleep(0.5)

        # Complete command
        completed = cmd_repo.complete_command(
            cmd.id,
            exit_code=0,
            stdout="Project initialized successfully",
        )
        console.print(f"[green]✓[/green] Completed command with exit code {completed.exit_code}")
        console.print(f"[blue]→[/blue] Duration: {completed.duration_ms:.2f}ms")

        # Query recent commands
        queries = CommandQueries(session)
        recent = queries.get_recent_commands(hours=24, limit=5)
        console.print(f"[blue]→[/blue] Found {len(recent)} recent command(s)")


def example_5_performance_metrics():
    """Example 5: Record and analyze performance metrics."""
    console.print("\n[bold cyan]Example 5: Performance Metrics[/bold cyan]")

    with get_session() as session:
        metric_repo = PerformanceMetricRepository(session)

        # Record metrics
        metrics_data = [
            ("api_response_time", 145.3, MetricType.TIMER, "ms"),
            ("database_query_time", 23.7, MetricType.TIMER, "ms"),
            ("memory_usage", 256.5, MetricType.GAUGE, "MB"),
            ("requests_count", 1523, MetricType.COUNTER, "count"),
        ]

        for name, value, type_, unit in metrics_data:
            metric_repo.record_metric(
                name=name,
                value=value,
                type=type_,
                unit=unit,
            )
            console.print(f"[green]✓[/green] Recorded metric: {name} = {value} {unit}")

        # Aggregate metrics
        queries = PerformanceMetricQueries(session)
        stats = queries.aggregate_by_name("api_response_time")

        table = Table(title="Performance Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", justify="right", style="green")

        table.add_row("Count", str(stats["count"]))
        table.add_row("Average", f"{stats['avg']:.2f}ms" if stats["avg"] else "N/A")
        table.add_row("Min", f"{stats['min']:.2f}ms" if stats["min"] else "N/A")
        table.add_row("Max", f"{stats['max']:.2f}ms" if stats["max"] else "N/A")

        console.print(table)


def example_6_audit_logging():
    """Example 6: Audit trail and compliance logging."""
    console.print("\n[bold cyan]Example 6: Audit Logging[/bold cyan]")

    with get_session() as session:
        user_repo = UserRepository(session)
        audit_repo = AuditLogRepository(session)

        user = user_repo.get_by_username("alice")

        # Log various actions
        actions = [
            (AuditAction.CREATE, "project", "1"),
            (AuditAction.UPDATE, "project", "1"),
            (AuditAction.EXECUTE, "command", "init"),
            (AuditAction.READ, "specification", "feature.ttl"),
        ]

        for action, resource_type, resource_id in actions:
            audit_repo.log_action(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user.id,
                ip_address="127.0.0.1",
                success=True,
            )
            console.print(f"[green]✓[/green] Logged: {action.value} on {resource_type}:{resource_id}")

        # Query audit logs
        queries = audit_repo.queries
        recent_logs = queries.get_recent_logs(hours=24)
        console.print(f"[blue]→[/blue] Found {len(recent_logs)} audit log(s)")


def example_7_cache_management():
    """Example 7: Cache operations for performance optimization."""
    console.print("\n[bold cyan]Example 7: Cache Management[/bold cyan]")

    with get_session() as session:
        cache_repo = CacheRepository(session)

        # Set cache entries
        cache_repo.set_cache(
            key="api_response_/users/1",
            value='{"id": 1, "name": "Alice"}',
            ttl_seconds=3600,
        )
        console.print("[green]✓[/green] Cached API response (TTL: 1 hour)")

        cache_repo.set_cache(
            key="config_version",
            value="1.2.3",
            ttl_seconds=86400,
        )
        console.print("[green]✓[/green] Cached configuration (TTL: 24 hours)")

        # Retrieve from cache
        value = cache_repo.get_cache("api_response_/users/1")
        console.print(f"[blue]→[/blue] Retrieved from cache: {value[:50]}...")

        # Clean up expired entries
        cleaned = cache_repo.cleanup_expired()
        console.print(f"[green]✓[/green] Cleaned up {cleaned} expired cache entries")


def example_8_configuration_storage():
    """Example 8: Project-specific configuration management."""
    console.print("\n[bold cyan]Example 8: Configuration Storage[/bold cyan]")

    with get_session() as session:
        project_repo = ProjectRepository(session)
        config_repo = ConfigurationRepository(session)

        project = project_repo.get_by_slug("awesome-api")

        # Set various configuration types
        config_repo.set_config(project.id, "api_url", "https://api.example.com")
        config_repo.set_config(project.id, "max_connections", 100)
        config_repo.set_config(project.id, "enable_logging", True)
        config_repo.set_config(project.id, "rate_limit", 60.0)
        config_repo.set_config(project.id, "features", {"auth": True, "cache": True})

        console.print("[green]✓[/green] Stored 5 configuration values")

        # Retrieve configurations
        api_url = config_repo.get_config(project.id, "api_url")
        max_conn = config_repo.get_config(project.id, "max_connections")
        logging = config_repo.get_config(project.id, "enable_logging")

        console.print(f"[blue]→[/blue] API URL: {api_url}")
        console.print(f"[blue]→[/blue] Max connections: {max_conn}")
        console.print(f"[blue]→[/blue] Logging enabled: {logging}")


def example_9_rdf_specifications():
    """Example 9: Track RDF specification metadata."""
    console.print("\n[bold cyan]Example 9: RDF Specification Tracking[/bold cyan]")

    with get_session() as session:
        project_repo = ProjectRepository(session)
        spec_repo = RDFSpecificationRepository(session)

        project = project_repo.get_by_slug("awesome-api")

        # Create RDF specification
        ttl_content = """
        @prefix api: <http://example.org/api/> .
        @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

        api:User a rdfs:Class ;
            rdfs:label "User" ;
            rdfs:comment "API user entity" .
        """

        spec = spec_repo.create_specification(
            project_id=project.id,
            file_path="ontology/api-schema.ttl",
            content=ttl_content,
            format="turtle",
            valid=True,
        )

        console.print(f"[green]✓[/green] Created RDF specification: {spec.file_path}")
        console.print(f"[blue]→[/blue] Content hash: {spec.content_hash[:16]}...")


def example_10_advanced_querying():
    """Example 10: Advanced querying and filtering."""
    console.print("\n[bold cyan]Example 10: Advanced Querying[/bold cyan]")

    with get_session() as session:
        # User search
        user_queries = UserQueries(session)
        results = user_queries.search_users("alice", limit=5)
        console.print(f"[blue]→[/blue] User search found {len(results)} result(s)")

        # Command statistics
        cmd_queries = CommandQueries(session)
        stats = cmd_queries.get_command_statistics()

        table = Table(title="Command Statistics")
        table.add_column("Status", style="cyan")
        table.add_column("Count", justify="right", style="green")

        for status, count in stats.get("by_status", {}).items():
            table.add_row(status, str(count))

        console.print(table)

        # Pagination
        page = user_queries.paginate(page=1, per_page=2)
        console.print(f"[blue]→[/blue] Page 1 of {page.pages} (Total: {page.total} users)")


def main():
    """Run all examples."""
    console.print("[bold green]Database Layer Examples[/bold green]")
    console.print("=" * 60)

    try:
        example_1_basic_setup()
        example_2_user_management()
        example_3_project_tracking()
        example_4_command_execution()
        example_5_performance_metrics()
        example_6_audit_logging()
        example_7_cache_management()
        example_8_configuration_storage()
        example_9_rdf_specifications()
        example_10_advanced_querying()

        console.print("\n[bold green]✓ All examples completed successfully![/bold green]")

    except Exception as e:
        console.print(f"\n[bold red]Error: {e}[/bold red]")
        import traceback
        traceback.print_exc()

    finally:
        # Clean up
        close_db()
        console.print("\n[dim]Database connection closed[/dim]")


if __name__ == "__main__":
    main()
