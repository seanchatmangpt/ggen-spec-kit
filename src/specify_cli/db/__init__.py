"""
specify_cli.db - Database Layer
================================

Comprehensive database layer with SQLAlchemy ORM, session management,
query patterns, repositories, and migrations.

This module provides a complete database abstraction layer following
the three-tier architecture pattern. All database operations are
isolated in the runtime layer with pure business logic in the ops layer.

Features
--------
- **Models**: SQLAlchemy ORM models for all entities
- **Session Management**: Connection pooling and transaction handling
- **Query Patterns**: Pre-built queries with optimization
- **Repositories**: Data access patterns with CRUD operations
- **Migrations**: Alembic integration for schema versioning

Supported Databases
-------------------
- SQLite (development/lightweight)
- PostgreSQL (production)
- MySQL (alternative production)

Quick Start
-----------
    >>> from specify_cli.db import init_db, get_session
    >>> from specify_cli.db import UserRepository, ProjectRepository
    >>>
    >>> # Initialize database
    >>> init_db("sqlite:///./specify.db")
    >>>
    >>> # Use repositories with session
    >>> with get_session() as session:
    ...     user_repo = UserRepository(session)
    ...     user = user_repo.create_user(
    ...         username="alice",
    ...         email="alice@example.com",
    ...         password_hash=b"hashed_password"
    ...     )
    ...
    >>> # Query data
    >>> with get_session() as session:
    ...     from specify_cli.db.queries import CommandQueries
    ...     queries = CommandQueries(session)
    ...     recent_commands = queries.get_recent_commands(hours=24)

Database Models
---------------
Available models:
- User: User accounts and authentication
- Project: Project organization
- Command: Command execution history
- PerformanceMetric: Performance tracking
- AuditLog: Audit trail and compliance
- RDFSpecification: RDF spec metadata
- TelemetryEvent: OpenTelemetry events
- CacheEntry: Cache storage
- Configuration: Project configuration
- SessionToken: Session management

Examples
--------
Create and query users:
    >>> from specify_cli.db import init_db, get_session, UserRepository
    >>> init_db()
    >>> with get_session() as session:
    ...     repo = UserRepository(session)
    ...     user = repo.create_user(
    ...         username="bob",
    ...         email="bob@example.com",
    ...         password_hash=b"hash"
    ...     )
    ...     found = repo.get_by_username("bob")

Track command execution:
    >>> from specify_cli.db import CommandRepository
    >>> with get_session() as session:
    ...     repo = CommandRepository(session)
    ...     cmd = repo.start_command(
    ...         name="specify init",
    ...         user_id=1,
    ...         project_id=1
    ...     )
    ...     # ... execute command ...
    ...     repo.complete_command(cmd.id, exit_code=0)

Performance metrics:
    >>> from specify_cli.db import PerformanceMetricRepository
    >>> with get_session() as session:
    ...     repo = PerformanceMetricRepository(session)
    ...     metric = repo.record_metric(
    ...         name="execution_time",
    ...         value=150.5,
    ...         unit="ms",
    ...         command_id=1
    ...     )

Migrations
----------
Use the MigrationManager for schema management:
    >>> from specify_cli.db.migrations import MigrationManager
    >>> manager = MigrationManager()
    >>> manager.init()  # Initialize migration environment
    >>> manager.create_migration("add_user_fields")
    >>> manager.upgrade()  # Apply migrations
    >>> manager.downgrade()  # Rollback

See Also
--------
- :mod:`specify_cli.db.models` : ORM model definitions
- :mod:`specify_cli.db.session` : Session management
- :mod:`specify_cli.db.queries` : Query patterns
- :mod:`specify_cli.db.repositories` : Data access patterns
- :mod:`specify_cli.db.migrations` : Migration management
"""

from __future__ import annotations

# Models
from specify_cli.db.models import (
    AuditAction,
    AuditLog,
    Base,
    CacheEntry,
    Command,
    Configuration,
    ExecutionStatus,
    MetricType,
    PerformanceMetric,
    Project,
    RDFSpecification,
    SessionToken,
    TelemetryEvent,
    User,
)

# Session Management
from specify_cli.db.session import (
    DatabaseManager,
    RetryConfig,
    close_db,
    get_engine,
    get_session,
    get_session_factory,
    health_check,
    init_db,
)

# Query Patterns
from specify_cli.db.queries import (
    AuditLogQueries,
    BaseQueries,
    CacheQueries,
    CommandQueries,
    ConfigurationQueries,
    PaginationResult,
    PerformanceMetricQueries,
    ProjectQueries,
    RDFSpecificationQueries,
    TelemetryEventQueries,
    UserQueries,
)

# Repositories
from specify_cli.db.repositories import (
    AuditLogRepository,
    BaseRepository,
    CacheRepository,
    CommandRepository,
    ConfigurationRepository,
    PerformanceMetricRepository,
    ProjectRepository,
    RDFSpecificationRepository,
    SessionTokenRepository,
    UserRepository,
)

# Migrations
from specify_cli.db.migrations import (
    MigrationManager,
    get_current_revision,
    get_migration_history,
    verify_schema,
)

__all__ = [
    # Models
    "Base",
    "User",
    "Project",
    "Command",
    "PerformanceMetric",
    "AuditLog",
    "RDFSpecification",
    "TelemetryEvent",
    "CacheEntry",
    "Configuration",
    "SessionToken",
    "ExecutionStatus",
    "AuditAction",
    "MetricType",
    # Session Management
    "init_db",
    "close_db",
    "get_engine",
    "get_session",
    "get_session_factory",
    "health_check",
    "DatabaseManager",
    "RetryConfig",
    # Query Patterns
    "BaseQueries",
    "UserQueries",
    "ProjectQueries",
    "CommandQueries",
    "PerformanceMetricQueries",
    "AuditLogQueries",
    "RDFSpecificationQueries",
    "TelemetryEventQueries",
    "CacheQueries",
    "ConfigurationQueries",
    "PaginationResult",
    # Repositories
    "BaseRepository",
    "UserRepository",
    "ProjectRepository",
    "CommandRepository",
    "PerformanceMetricRepository",
    "AuditLogRepository",
    "RDFSpecificationRepository",
    "CacheRepository",
    "ConfigurationRepository",
    "SessionTokenRepository",
    # Migrations
    "MigrationManager",
    "get_current_revision",
    "get_migration_history",
    "verify_schema",
]

__version__ = "0.1.0"
