# Database Layer Guide

Comprehensive guide to the hyper-advanced database layer in specify-cli.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Architecture](#architecture)
4. [Database Models](#database-models)
5. [Session Management](#session-management)
6. [Query Patterns](#query-patterns)
7. [Repository Pattern](#repository-pattern)
8. [Migrations](#migrations)
9. [Performance Tuning](#performance-tuning)
10. [Production Deployment](#production-deployment)
11. [Backup and Restore](#backup-and-restore)

## Overview

The database layer provides comprehensive data persistence and ORM capabilities using SQLAlchemy 2.0+ with:

- **10+ Data Models**: User, Project, Command, Metrics, Audit Logs, etc.
- **Connection Pooling**: Configurable pool sizes and overflow handling
- **Retry Logic**: Automatic retry on transient failures
- **Query Optimization**: Pre-built patterns with indexing
- **Repository Pattern**: Clean data access abstraction
- **Alembic Migrations**: Schema versioning and rollback
- **Multi-Database Support**: SQLite, PostgreSQL, MySQL

## Quick Start

### Installation

```bash
# Core dependencies (SQLAlchemy + Alembic)
uv sync

# Optional database drivers
uv sync --group db
```

### Basic Usage

```python
from specify_cli.db import init_db, get_session, UserRepository

# Initialize database
init_db("sqlite:///./specify.db")

# Use repository pattern
with get_session() as session:
    repo = UserRepository(session)
    user = repo.create_user(
        username="alice",
        email="alice@example.com",
        password_hash=b"hashed_password"
    )
    print(f"Created user: {user.id}")
```

## Architecture

### Three-Tier Integration

The database layer follows the three-tier architecture:

```
┌─────────────────────────────────────────────┐
│ Commands Layer (CLI)                        │
│ - Minimal DB interaction                    │
│ - Delegates to ops layer                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Operations Layer (Business Logic)          │
│ - Uses repositories for data access         │
│ - Pure functions, no side effects           │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Runtime Layer (Database)                    │
│ - Session management                        │
│ - Query execution                           │
│ - Connection pooling                        │
└─────────────────────────────────────────────┘
```

### Module Structure

```
src/specify_cli/db/
├── __init__.py          # Public API exports
├── models.py            # SQLAlchemy ORM models (400+ lines)
├── session.py           # Session management (250+ lines)
├── queries.py           # Query patterns (350+ lines)
├── repositories.py      # Data access patterns (300+ lines)
└── migrations.py        # Alembic integration (200+ lines)
```

## Database Models

### Core Models

#### User
User accounts and authentication:
```python
from specify_cli.db import User

user = User(
    username="alice",
    email="alice@example.com",
    password_hash=b"hashed_password",
    full_name="Alice Smith",
    is_active=True,
    is_admin=False
)
```

#### Project
Project organization and tracking:
```python
from specify_cli.db import Project

project = Project(
    name="Awesome API",
    slug="awesome-api",
    owner_id=user.id,
    description="RESTful API service",
    repository_url="https://github.com/alice/awesome-api"
)
```

#### Command
Command execution history:
```python
from specify_cli.db import Command, ExecutionStatus

command = Command(
    name="specify init",
    args="--verbose",
    user_id=user.id,
    project_id=project.id,
    status=ExecutionStatus.RUNNING,
    started_at=datetime.now(UTC)
)
```

#### PerformanceMetric
Performance tracking and analytics:
```python
from specify_cli.db import PerformanceMetric, MetricType

metric = PerformanceMetric(
    name="execution_time",
    value=150.5,
    type=MetricType.TIMER,
    unit="ms",
    command_id=command.id
)
```

### Supporting Models

- **AuditLog**: Audit trail and compliance
- **RDFSpecification**: RDF spec metadata tracking
- **TelemetryEvent**: OpenTelemetry events
- **CacheEntry**: Cache storage
- **Configuration**: Project configuration
- **SessionToken**: Session management

## Session Management

### Database Initialization

```python
from specify_cli.db import init_db

# SQLite (development)
init_db("sqlite:///./specify.db")

# PostgreSQL (production)
init_db("postgresql://user:password@localhost/specify_db")

# MySQL (alternative production)
init_db("mysql+pymysql://user:password@localhost/specify_db")
```

### Connection Pooling

```python
from specify_cli.db.session import DatabaseManager

manager = DatabaseManager(
    url="postgresql://user:password@localhost/db",
    pool_size=10,           # Base pool size
    max_overflow=20,        # Additional connections
    pool_timeout=30.0,      # Checkout timeout (seconds)
    pool_recycle=3600,      # Recycle connections (seconds)
)
```

### Retry Logic

```python
from specify_cli.db.session import RetryConfig

retry_config = RetryConfig(
    max_attempts=3,         # Retry attempts
    initial_delay=0.1,      # Initial delay (seconds)
    max_delay=5.0,          # Maximum delay (seconds)
    exponential_base=2.0    # Backoff multiplier
)

manager = DatabaseManager(
    url="postgresql://...",
    retry_config=retry_config
)
```

### Session Context Manager

```python
from specify_cli.db import get_session

# Automatic commit and cleanup
with get_session() as session:
    user = session.query(User).first()
    user.full_name = "Updated Name"
    # Automatically commits on exit
```

### Manual Session Management

```python
from specify_cli.db import get_session_factory

SessionFactory = get_session_factory()
session = SessionFactory()

try:
    user = session.query(User).first()
    session.commit()
except Exception:
    session.rollback()
    raise
finally:
    session.close()
```

## Query Patterns

### Basic Queries

```python
from specify_cli.db import get_session
from specify_cli.db.queries import UserQueries

with get_session() as session:
    queries = UserQueries(session)

    # Find by ID
    user = queries.get_by_id(1)

    # Find by username
    user = queries.find_by_username("alice")

    # Get all active users
    users = queries.get_active_users(limit=10)

    # Search users
    results = queries.search_users("alice", limit=5)
```

### Advanced Filtering

```python
from specify_cli.db.queries import CommandQueries

with get_session() as session:
    queries = CommandQueries(session)

    # Filter by status
    success_cmds = queries.find_by_status("success", limit=10)

    # Get recent commands
    recent = queries.get_recent_commands(hours=24, limit=100)

    # Get failed commands
    failed = queries.get_failed_commands(hours=24)
```

### Aggregation

```python
from specify_cli.db.queries import PerformanceMetricQueries

with get_session() as session:
    queries = PerformanceMetricQueries(session)

    # Aggregate by name
    stats = queries.aggregate_by_name(
        "execution_time",
        start_date=datetime.now(UTC) - timedelta(days=7)
    )

    print(f"Count: {stats['count']}")
    print(f"Average: {stats['avg']}")
    print(f"Min: {stats['min']}")
    print(f"Max: {stats['max']}")
```

### Pagination

```python
from specify_cli.db.queries import UserQueries

with get_session() as session:
    queries = UserQueries(session)

    # Get page 1 (20 items per page)
    page = queries.paginate(page=1, per_page=20)

    print(f"Page {page.page} of {page.pages}")
    print(f"Total items: {page.total}")
    print(f"Has next: {page.has_next}")
    print(f"Has previous: {page.has_prev}")

    for user in page.items:
        print(user.username)
```

## Repository Pattern

### CRUD Operations

```python
from specify_cli.db import UserRepository, get_session

with get_session() as session:
    repo = UserRepository(session)

    # Create
    user = repo.create_user(
        username="alice",
        email="alice@example.com",
        password_hash=b"hashed"
    )

    # Read
    user = repo.get(user.id)
    user = repo.get_by_username("alice")

    # Update
    updated = repo.update(user.id, {"full_name": "Alice Smith"})

    # Delete
    repo.delete(user.id)
```

### Bulk Operations

```python
from specify_cli.db import UserRepository

with get_session() as session:
    repo = UserRepository(session)

    # Bulk create
    users_data = [
        {"username": f"user{i}", "email": f"user{i}@example.com",
         "password_hash": b"hash"}
        for i in range(100)
    ]
    users = repo.bulk_create(users_data)

    # Bulk update
    updates = [
        {"id": 1, "full_name": "User One"},
        {"id": 2, "full_name": "User Two"},
    ]
    count = repo.bulk_update(updates)
```

### Domain-Specific Methods

```python
from specify_cli.db import CommandRepository, ExecutionStatus

with get_session() as session:
    repo = CommandRepository(session)

    # Start command
    cmd = repo.start_command(
        name="specify init",
        args="--verbose",
        user_id=1,
        project_id=1
    )

    # Complete command
    repo.complete_command(
        cmd.id,
        exit_code=0,
        stdout="Success"
    )

    # Fail command
    repo.fail_command(cmd.id, error="Validation failed")
```

## Migrations

### Initialize Migrations

```python
from specify_cli.db.migrations import MigrationManager

manager = MigrationManager()

# Initialize migration environment
manager.init()
```

### Create Migration

```python
# Auto-generate from model changes
manager.create_migration("add_user_fields")

# Manual migration
manager.create_migration("custom_data_migration", autogenerate=False)
```

### Apply Migrations

```python
# Upgrade to latest
manager.upgrade()

# Upgrade to specific revision
manager.upgrade("abc123")

# Downgrade one version
manager.downgrade()

# Downgrade to specific revision
manager.downgrade("xyz789")
```

### Migration History

```python
# Get current revision
current = manager.current()
print(f"Current revision: {current}")

# Get migration history
history = manager.history(verbose=True)
for entry in history:
    print(f"{entry['revision']}: {entry['message']}")
```

### Schema Verification

```python
from specify_cli.db.migrations import verify_schema
from specify_cli.db import get_engine

engine = get_engine()
result = verify_schema(engine)

if result["valid"]:
    print("Schema is valid")
else:
    print(f"Missing tables: {result['missing_tables']}")
    print(f"Extra tables: {result['extra_tables']}")
    print(f"Column issues: {result['column_issues']}")
```

## Performance Tuning

### Indexing Strategy

Models include optimized indexes:

```python
# Example from models.py
class Command(Base):
    # Single column indexes
    command_id = Column(String(36), index=True)
    name = Column(String(200), index=True)

    # Composite indexes
    __table_args__ = (
        Index("idx_command_user_project", "user_id", "project_id"),
        Index("idx_command_started_at", "started_at"),
        Index("idx_command_status_started", "status", "started_at"),
    )
```

### Query Optimization

```python
from specify_cli.db import get_session
from specify_cli.db.models import Command, User
from sqlalchemy.orm import joinedload

with get_session() as session:
    # Eager loading to avoid N+1 queries
    commands = (
        session.query(Command)
        .options(joinedload(Command.user))
        .filter(Command.status == "success")
        .all()
    )
```

### Connection Pool Tuning

```python
from specify_cli.db.session import DatabaseManager

# For high-traffic applications
manager = DatabaseManager(
    url="postgresql://...",
    pool_size=20,          # Larger pool
    max_overflow=40,       # More overflow
    pool_timeout=60.0,     # Longer timeout
    pool_recycle=1800,     # Recycle more frequently
)
```

### Query Result Caching

```python
from specify_cli.db import CacheRepository

with get_session() as session:
    cache_repo = CacheRepository(session)

    # Check cache first
    cached = cache_repo.get_cache("expensive_query_result")
    if cached:
        return cached

    # Execute expensive query
    result = expensive_query()

    # Cache result for 1 hour
    cache_repo.set_cache(
        "expensive_query_result",
        result,
        ttl_seconds=3600
    )
```

## Production Deployment

### PostgreSQL Configuration

```python
from specify_cli.db import init_db

init_db(
    url="postgresql://user:password@localhost:5432/specify_db",
    pool_size=20,
    max_overflow=40,
    echo=False  # Disable query logging in production
)
```

### Environment-Based Configuration

```python
import os
from specify_cli.db import init_db

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./specify.db"  # Default fallback
)

init_db(DATABASE_URL)
```

### Health Checks

```python
from specify_cli.db import health_check

result = health_check()

if result["healthy"]:
    print(f"Database OK (latency: {result['latency_ms']:.2f}ms)")
else:
    print(f"Database ERROR: {result['error']}")
```

### Read Replicas

For high-read workloads:

```python
from specify_cli.db.session import DatabaseManager

# Write database
write_db = DatabaseManager(
    url="postgresql://user:pass@primary:5432/db"
)

# Read replica
read_db = DatabaseManager(
    url="postgresql://user:pass@replica:5432/db"
)

# Use read replica for queries
with read_db.get_session() as session:
    users = session.query(User).all()

# Use primary for writes
with write_db.get_session() as session:
    user = User(username="new")
    session.add(user)
```

## Backup and Restore

### SQLite Backup

```python
from specify_cli.db.migrations import backup_database
from specify_cli.db import get_engine

engine = get_engine()
backup_database(engine, "backup_2025-01-15.db")
```

### PostgreSQL Backup

```bash
# Using pg_dump
pg_dump -U user -d specify_db -F c -f specify_backup.dump

# Using pg_basebackup for full cluster
pg_basebackup -D /backup/path -Ft -Xs -P
```

### Restore Database

```python
from specify_cli.db.migrations import restore_database

restore_database(
    backup_path="backup_2025-01-15.db",
    target_path="specify.db"
)
```

### Automated Backups

```python
from datetime import datetime
from pathlib import Path

def create_daily_backup():
    """Create timestamped daily backup."""
    from specify_cli.db import get_engine
    from specify_cli.db.migrations import backup_database

    engine = get_engine()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = Path(f"backups/specify_{timestamp}.db")
    backup_path.parent.mkdir(exist_ok=True)

    backup_database(engine, backup_path)
    print(f"Backup created: {backup_path}")
```

## Best Practices

### 1. Always Use Context Managers

```python
# Good
with get_session() as session:
    repo = UserRepository(session)
    user = repo.create_user(...)

# Avoid manual session management
```

### 2. Use Repositories, Not Raw Queries

```python
# Good - Repository pattern
with get_session() as session:
    repo = UserRepository(session)
    user = repo.get_by_username("alice")

# Avoid - Direct queries
with get_session() as session:
    user = session.query(User).filter_by(username="alice").first()
```

### 3. Leverage Query Patterns

```python
# Good - Pre-built query patterns
queries = CommandQueries(session)
recent = queries.get_recent_commands(hours=24)

# Avoid - Custom queries everywhere
```

### 4. Enable Connection Pooling in Production

```python
# Production
init_db(
    "postgresql://...",
    pool_size=20,
    max_overflow=40
)

# Development
init_db("sqlite:///./dev.db")
```

### 5. Monitor Database Health

```python
from specify_cli.db import health_check

# Regular health checks
result = health_check()
if not result["healthy"]:
    alert_admin(result["error"])
```

## Troubleshooting

### Connection Pool Exhausted

```python
# Increase pool size and overflow
manager = DatabaseManager(
    url="...",
    pool_size=30,  # Increased
    max_overflow=60  # Increased
)
```

### Slow Queries

```python
# Enable query logging to identify slow queries
manager = DatabaseManager(url="...", echo=True)

# Add indexes to frequently queried columns
# Check query execution plans
```

### Migration Conflicts

```python
# Verify current schema state
from specify_cli.db.migrations import verify_schema, get_current_revision

current = get_current_revision(engine)
schema = verify_schema(engine)

# Stamp database if needed
manager.stamp("head")
```

## Summary

The database layer provides:

- **Comprehensive Models**: 10+ tables with relationships
- **Session Management**: Connection pooling and retry logic
- **Query Optimization**: Pre-built patterns with indexes
- **Repository Pattern**: Clean data access abstraction
- **Migration Support**: Alembic-based schema versioning
- **Production Ready**: Multi-database, health checks, backups

For more examples, see `/examples/database_example.py`.
