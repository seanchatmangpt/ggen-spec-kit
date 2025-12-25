"""
Unit tests for database layer.

Tests cover:
- Models and relationships
- Session management
- Query patterns
- Repositories
- Migrations
"""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from specify_cli.db import (
    AuditAction,
    AuditLog,
    AuditLogRepository,
    CacheEntry,
    CacheRepository,
    Command,
    CommandRepository,
    Configuration,
    ConfigurationRepository,
    ExecutionStatus,
    MetricType,
    PerformanceMetric,
    PerformanceMetricRepository,
    Project,
    ProjectRepository,
    RDFSpecification,
    RDFSpecificationRepository,
    SessionToken,
    SessionTokenRepository,
    User,
    UserRepository,
)
from specify_cli.db.migrations import verify_schema
from specify_cli.db.models import Base
from specify_cli.db.queries import (
    CommandQueries,
    PerformanceMetricQueries,
    ProjectQueries,
    UserQueries,
)
from specify_cli.db.session import DatabaseManager, RetryConfig


@pytest.fixture
def db_engine():
    """Create in-memory SQLite database engine for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine):
    """Create database session for testing."""
    Session = sessionmaker(bind=db_engine)
    session = Session()
    yield session
    session.close()


# ============================================================================
# Model Tests
# ============================================================================


def test_user_model(db_session):
    """Test User model creation and relationships."""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=b"hashed_password",
        full_name="Test User",
    )
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.is_admin is False
    assert user.api_key is not None


def test_project_model(db_session):
    """Test Project model creation and relationships."""
    # Create user first
    user = User(
        username="owner",
        email="owner@example.com",
        password_hash=b"hash",
    )
    db_session.add(user)
    db_session.commit()

    # Create project
    project = Project(
        name="Test Project",
        slug="test-project",
        owner_id=user.id,
        description="A test project",
    )
    db_session.add(project)
    db_session.commit()

    assert project.id is not None
    assert project.name == "Test Project"
    assert project.slug == "test-project"
    assert project.owner_id == user.id
    assert project.is_active is True


def test_command_model(db_session):
    """Test Command model creation and execution tracking."""
    # Create user and project
    user = User(username="user", email="user@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.commit()

    project = Project(name="Project", slug="project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    # Create command
    command = Command(
        name="specify init",
        args="--verbose",
        user_id=user.id,
        project_id=project.id,
        status=ExecutionStatus.RUNNING,
    )
    db_session.add(command)
    db_session.commit()

    assert command.id is not None
    assert command.command_id is not None
    assert command.name == "specify init"
    assert command.status == ExecutionStatus.RUNNING


def test_command_duration_calculation(db_session):
    """Test automatic duration calculation on command completion."""
    start_time = datetime.now(UTC)
    command = Command(
        name="test",
        status=ExecutionStatus.RUNNING,
        started_at=start_time,
    )
    db_session.add(command)
    db_session.commit()

    # Complete command
    command.status = ExecutionStatus.SUCCESS
    command.completed_at = start_time + timedelta(seconds=2)
    db_session.flush()

    assert command.duration_ms is not None
    assert command.duration_ms >= 2000  # At least 2 seconds


def test_cache_entry_expiration(db_session):
    """Test cache entry expiration checking."""
    # Create expired entry
    expired = CacheEntry(
        key="expired",
        value="test",
        value_hash="hash",
        size_bytes=4,
        expires_at=datetime.now(UTC) - timedelta(hours=1),
    )
    db_session.add(expired)

    # Create valid entry
    valid = CacheEntry(
        key="valid",
        value="test",
        value_hash="hash",
        size_bytes=4,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    db_session.add(valid)
    db_session.commit()

    assert expired.is_expired is True
    assert valid.is_expired is False


# ============================================================================
# Session Management Tests
# ============================================================================


def test_database_manager_creation():
    """Test DatabaseManager initialization."""
    manager = DatabaseManager(
        url="sqlite:///:memory:",
        pool_size=5,
        max_overflow=10,
    )

    assert manager.url == "sqlite:///:memory:"
    assert manager.engine is not None
    assert manager.session_factory is not None

    manager.close()


def test_database_manager_health_check():
    """Test database health check."""
    manager = DatabaseManager(url="sqlite:///:memory:")
    manager.create_all()

    health = manager.health_check()

    assert health["healthy"] is True
    assert "latency_ms" in health
    assert health["latency_ms"] >= 0

    manager.close()


def test_retry_config():
    """Test retry configuration."""
    config = RetryConfig(
        max_attempts=5,
        initial_delay=0.5,
        max_delay=10.0,
        exponential_base=2.0,
    )

    assert config.max_attempts == 5
    assert config.initial_delay == 0.5
    assert config.max_delay == 10.0
    assert config.exponential_base == 2.0


# ============================================================================
# Query Pattern Tests
# ============================================================================


def test_user_queries(db_session):
    """Test UserQueries pattern."""
    # Create test users
    user1 = User(username="alice", email="alice@example.com", password_hash=b"hash")
    user2 = User(username="bob", email="bob@example.com", password_hash=b"hash", is_admin=True)
    db_session.add_all([user1, user2])
    db_session.commit()

    queries = UserQueries(db_session)

    # Test find by username
    found = queries.find_by_username("alice")
    assert found is not None
    assert found.username == "alice"

    # Test find by email
    found = queries.find_by_email("bob@example.com")
    assert found is not None
    assert found.email == "bob@example.com"

    # Test get admins
    admins = queries.get_admins()
    assert len(admins) == 1
    assert admins[0].username == "bob"

    # Test search
    results = queries.search_users("alice")
    assert len(results) >= 1


def test_project_queries(db_session):
    """Test ProjectQueries pattern."""
    # Create user and projects
    user = User(username="owner", email="owner@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.commit()

    project1 = Project(name="Project 1", slug="project-1", owner_id=user.id)
    project2 = Project(name="Project 2", slug="project-2", owner_id=user.id, is_active=False)
    db_session.add_all([project1, project2])
    db_session.commit()

    queries = ProjectQueries(db_session)

    # Test find by slug
    found = queries.find_by_slug("project-1")
    assert found is not None
    assert found.name == "Project 1"

    # Test find by owner
    projects = queries.find_by_owner(user.id, active_only=True)
    assert len(projects) == 1

    # Test get active projects
    active = queries.get_active_projects()
    assert len(active) >= 1


def test_command_queries(db_session):
    """Test CommandQueries pattern."""
    # Create commands
    cmd1 = Command(name="cmd1", status=ExecutionStatus.SUCCESS)
    cmd2 = Command(name="cmd2", status=ExecutionStatus.FAILED)
    db_session.add_all([cmd1, cmd2])
    db_session.commit()

    queries = CommandQueries(db_session)

    # Test find by status
    success_cmds = queries.find_by_status(ExecutionStatus.SUCCESS)
    assert len(success_cmds) >= 1

    # Test get statistics
    stats = queries.get_command_statistics()
    assert stats["total"] >= 2
    assert "by_status" in stats


def test_pagination(db_session):
    """Test pagination functionality."""
    # Create multiple users
    for i in range(25):
        user = User(
            username=f"user{i}",
            email=f"user{i}@example.com",
            password_hash=b"hash",
        )
        db_session.add(user)
    db_session.commit()

    queries = UserQueries(db_session)

    # Test pagination
    page1 = queries.paginate(page=1, per_page=10)
    assert len(page1.items) == 10
    assert page1.total == 25
    assert page1.pages == 3
    assert page1.has_next is True
    assert page1.has_prev is False

    page2 = queries.paginate(page=2, per_page=10)
    assert len(page2.items) == 10
    assert page2.has_next is True
    assert page2.has_prev is True


# ============================================================================
# Repository Tests
# ============================================================================


def test_user_repository_create(db_session):
    """Test UserRepository create operation."""
    repo = UserRepository(db_session)

    user = repo.create_user(
        username="newuser",
        email="new@example.com",
        password_hash=b"hashed",
        full_name="New User",
    )

    assert user.id is not None
    assert user.username == "newuser"
    assert user.email == "new@example.com"


def test_user_repository_get_by_username(db_session):
    """Test UserRepository get by username."""
    repo = UserRepository(db_session)

    user = repo.create_user(
        username="testuser",
        email="test@example.com",
        password_hash=b"hash",
    )

    found = repo.get_by_username("testuser")
    assert found is not None
    assert found.id == user.id


def test_user_repository_update(db_session):
    """Test UserRepository update operation."""
    repo = UserRepository(db_session)

    user = repo.create_user(
        username="user",
        email="user@example.com",
        password_hash=b"hash",
    )

    updated = repo.update(user.id, {"full_name": "Updated Name"})
    assert updated is not None
    assert updated.full_name == "Updated Name"


def test_project_repository_create(db_session):
    """Test ProjectRepository create operation."""
    # Create user first
    user_repo = UserRepository(db_session)
    user = user_repo.create_user(
        username="owner",
        email="owner@example.com",
        password_hash=b"hash",
    )

    # Create project
    project_repo = ProjectRepository(db_session)
    project = project_repo.create_project(
        name="New Project",
        slug="new-project",
        owner_id=user.id,
    )

    assert project.id is not None
    assert project.name == "New Project"
    assert project.slug == "new-project"


def test_command_repository_lifecycle(db_session):
    """Test Command repository complete lifecycle."""
    repo = CommandRepository(db_session)

    # Start command
    cmd = repo.start_command(
        name="test command",
        args="--verbose",
    )
    assert cmd.status == ExecutionStatus.RUNNING

    # Complete command
    completed = repo.complete_command(
        cmd.id,
        exit_code=0,
        stdout="Success",
    )
    assert completed is not None
    assert completed.status == ExecutionStatus.SUCCESS
    assert completed.exit_code == 0


def test_performance_metric_repository(db_session):
    """Test PerformanceMetricRepository."""
    repo = PerformanceMetricRepository(db_session)

    metric = repo.record_metric(
        name="execution_time",
        value=150.5,
        type=MetricType.TIMER,
        unit="ms",
    )

    assert metric.id is not None
    assert metric.name == "execution_time"
    assert metric.value == 150.5


def test_cache_repository(db_session):
    """Test CacheRepository operations."""
    repo = CacheRepository(db_session)

    # Set cache
    entry = repo.set_cache("key1", "value1", ttl_seconds=3600)
    assert entry.key == "key1"
    assert entry.value == "value1"

    # Get cache
    value = repo.get_cache("key1")
    assert value == "value1"

    # Get non-existent
    value = repo.get_cache("nonexistent")
    assert value is None


def test_configuration_repository(db_session):
    """Test ConfigurationRepository."""
    # Create project
    user = User(username="user", email="user@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.commit()

    project = Project(name="Project", slug="project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    repo = ConfigurationRepository(db_session)

    # Set config
    config = repo.set_config(project.id, "setting", "value")
    assert config.key == "setting"
    assert config.value == "value"

    # Get config
    value = repo.get_config(project.id, "setting")
    assert value == "value"

    # Get with default
    value = repo.get_config(project.id, "nonexistent", default="default")
    assert value == "default"


def test_audit_log_repository(db_session):
    """Test AuditLogRepository."""
    repo = AuditLogRepository(db_session)

    log = repo.log_action(
        action=AuditAction.CREATE,
        resource_type="project",
        resource_id="1",
        success=True,
    )

    assert log.id is not None
    assert log.action == AuditAction.CREATE
    assert log.resource_type == "project"


def test_rdf_specification_repository(db_session):
    """Test RDFSpecificationRepository."""
    # Create project
    user = User(username="user", email="user@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.commit()

    project = Project(name="Project", slug="project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    repo = RDFSpecificationRepository(db_session)

    # Create specification
    content = "@prefix : <http://example.org/> ."
    spec = repo.create_specification(
        project_id=project.id,
        file_path="ontology/test.ttl",
        content=content,
        format="turtle",
    )

    assert spec.id is not None
    assert spec.file_path == "ontology/test.ttl"
    assert spec.content_hash == hashlib.sha256(content.encode()).hexdigest()


# ============================================================================
# Migration Tests
# ============================================================================


def test_schema_verification(db_engine):
    """Test schema verification."""
    result = verify_schema(db_engine)

    assert "valid" in result
    assert "missing_tables" in result
    assert "extra_tables" in result
    assert "column_issues" in result


def test_bulk_operations(db_session):
    """Test bulk create and update operations."""
    repo = UserRepository(db_session)

    # Bulk create
    users_data = [
        {
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "password_hash": b"hash",
        }
        for i in range(5)
    ]
    users = repo.bulk_create(users_data)
    assert len(users) == 5


def test_repository_exists(db_session):
    """Test repository exists check."""
    repo = UserRepository(db_session)

    user = repo.create_user(
        username="user",
        email="user@example.com",
        password_hash=b"hash",
    )

    assert repo.exists(user.id) is True
    assert repo.exists(9999) is False


def test_repository_delete(db_session):
    """Test repository delete operation."""
    repo = UserRepository(db_session)

    user = repo.create_user(
        username="user",
        email="user@example.com",
        password_hash=b"hash",
    )

    result = repo.delete(user.id)
    assert result is True

    assert repo.get(user.id) is None


def test_session_token_repository(db_session):
    """Test SessionTokenRepository."""
    # Create user
    user = User(username="user", email="user@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.commit()

    repo = SessionTokenRepository(db_session)

    # Create session
    session_token = repo.create_session(user.id, ttl_seconds=3600)
    assert session_token.id is not None
    assert session_token.user_id == user.id
    assert session_token.is_active is True

    # Validate token
    validated = repo.validate_token(session_token.token)
    assert validated is not None
    assert validated.id == session_token.id

    # Revoke token
    revoked = repo.revoke_token(session_token.token)
    assert revoked is True


def test_configuration_type_handling(db_session):
    """Test Configuration value type handling."""
    user = User(username="user", email="user@example.com", password_hash=b"hash")
    db_session.add(user)
    db_session.commit()

    project = Project(name="Project", slug="project", owner_id=user.id)
    db_session.add(project)
    db_session.commit()

    repo = ConfigurationRepository(db_session)

    # Test different types
    repo.set_config(project.id, "string_val", "test")
    repo.set_config(project.id, "int_val", 42)
    repo.set_config(project.id, "bool_val", True)
    repo.set_config(project.id, "float_val", 3.14)
    repo.set_config(project.id, "json_val", {"key": "value"})

    assert repo.get_config(project.id, "string_val") == "test"
    assert repo.get_config(project.id, "int_val") == 42
    assert repo.get_config(project.id, "bool_val") is True
    assert repo.get_config(project.id, "float_val") == 3.14
    assert repo.get_config(project.id, "json_val") == {"key": "value"}
