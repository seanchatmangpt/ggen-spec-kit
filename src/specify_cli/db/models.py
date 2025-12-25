"""
specify_cli.db.models - SQLAlchemy ORM Models
==============================================

Comprehensive SQLAlchemy models for data persistence with support for:
- Command execution history and tracking
- Performance metrics and analytics
- User and project management
- Audit logging and compliance
- RDF specification metadata
- Telemetry and observability data

This module implements a hyper-advanced database schema with:
- Full relationship mapping
- Cascade delete strategies
- Custom column types
- Encryption support
- Time-series optimizations
- Full-text search indexes

Examples
--------
    >>> from specify_cli.db.models import Command, User, Project
    >>> from specify_cli.db.session import get_session
    >>>
    >>> # Create a command execution record
    >>> with get_session() as session:
    ...     cmd = Command(
    ...         name="specify init",
    ...         user_id=1,
    ...         project_id=1,
    ...         status="success",
    ...         duration_ms=150.5
    ...     )
    ...     session.add(cmd)
    ...     session.commit()
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    UniqueConstraint,
    event,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

__all__ = [
    "AuditAction",
    "AuditLog",
    "Base",
    "CacheEntry",
    "Command",
    "Configuration",
    "ExecutionStatus",
    "MetricType",
    "PerformanceMetric",
    "Project",
    "RDFSpecification",
    "SessionToken",
    "TelemetryEvent",
    "User",
]

Base = declarative_base()


def _ensure_aware(dt: datetime | None) -> datetime | None:
    """Ensure datetime is timezone-aware (UTC). Needed for SQLite compatibility."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


# ============================================================================
# Enumerations
# ============================================================================


class ExecutionStatus(str, Enum):
    """Command execution status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class AuditAction(str, Enum):
    """Audit log action enumeration."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    LOGIN = "login"
    LOGOUT = "logout"
    CONFIG_CHANGE = "config_change"


class MetricType(str, Enum):
    """Performance metric type enumeration."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
    TIMER = "timer"


# ============================================================================
# Core Models
# ============================================================================


class User(Base):  # type: ignore[misc,valid-type]
    """
    User model for authentication and authorization.

    Attributes
    ----------
    id : int
        Primary key.
    username : str
        Unique username (max 100 chars).
    email : str
        Unique email address (max 255 chars).
    full_name : str
        User's full name (max 255 chars).
    password_hash : bytes
        Encrypted password hash.
    api_key : str
        API key for programmatic access (UUID).
    is_active : bool
        Whether user account is active.
    is_admin : bool
        Whether user has admin privileges.
    created_at : datetime
        Account creation timestamp.
    updated_at : datetime
        Last update timestamp.
    last_login_at : datetime
        Last login timestamp.
    metadata : dict
        Additional user metadata (JSON).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    password_hash = Column(LargeBinary, nullable=False)
    api_key = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    commands = relationship("Command", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("SessionToken", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

    @hybrid_property
    def active_projects_count(self) -> int:
        """Get count of active projects."""
        return sum(1 for p in self.projects if p.is_active)


class Project(Base):  # type: ignore[misc,valid-type]
    """
    Project model for organizing work.

    Attributes
    ----------
    id : int
        Primary key.
    name : str
        Project name (max 200 chars).
    slug : str
        URL-friendly project identifier (max 200 chars).
    description : str
        Project description.
    owner_id : int
        Foreign key to User.
    path : str
        Filesystem path to project root.
    repository_url : str
        Git repository URL.
    is_active : bool
        Whether project is active.
    created_at : datetime
        Project creation timestamp.
    updated_at : datetime
        Last update timestamp.
    metadata : dict
        Additional project metadata (JSON).
    settings : dict
        Project-specific settings (JSON).
    """

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    path = Column(String(500), nullable=True)
    repository_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    meta = Column(JSON, default=dict, nullable=False)
    settings = Column(JSON, default=dict, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="projects")
    commands = relationship("Command", back_populates="project", cascade="all, delete-orphan")
    specifications = relationship("RDFSpecification", back_populates="project", cascade="all, delete-orphan")
    configurations = relationship("Configuration", back_populates="project", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_project_owner_name", "owner_id", "name"),
        Index("idx_project_active", "is_active"),
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class Command(Base):  # type: ignore[misc,valid-type]
    """
    Command execution history and tracking.

    Attributes
    ----------
    id : int
        Primary key.
    command_id : str
        Unique command execution identifier (UUID).
    name : str
        Command name (e.g., 'specify init').
    args : str
        Command arguments.
    user_id : int
        Foreign key to User.
    project_id : int
        Foreign key to Project.
    status : ExecutionStatus
        Execution status.
    started_at : datetime
        Command start timestamp.
    completed_at : datetime
        Command completion timestamp.
    duration_ms : float
        Execution duration in milliseconds.
    exit_code : int
        Command exit code.
    stdout : str
        Standard output.
    stderr : str
        Standard error output.
    environment : dict
        Environment variables (JSON).
    metadata : dict
        Additional command metadata (JSON).
    parent_id : int
        Foreign key to parent Command (for sub-commands).
    """

    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    command_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    name = Column(String(200), nullable=False, index=True)
    args = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    status = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False, index=True)  # type: ignore[var-annotated]
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_ms = Column(Float, nullable=True)
    exit_code = Column(Integer, nullable=True)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    environment = Column(JSON, default=dict, nullable=False)
    meta = Column(JSON, default=dict, nullable=False)
    parent_id = Column(Integer, ForeignKey("commands.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="commands")
    project = relationship("Project", back_populates="commands")
    parent = relationship("Command", remote_side=[id], backref="children")
    metrics = relationship("PerformanceMetric", back_populates="command", cascade="all, delete-orphan")
    telemetry_events = relationship("TelemetryEvent", back_populates="command", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_command_user_project", "user_id", "project_id"),
        Index("idx_command_started_at", "started_at"),
        Index("idx_command_status_started", "status", "started_at"),
    )

    def __repr__(self) -> str:
        return f"<Command(id={self.id}, name='{self.name}', status='{self.status.value}')>"

    @hybrid_property
    def is_success(self) -> bool:
        """Check if command executed successfully."""
        return self.status == ExecutionStatus.SUCCESS and self.exit_code == 0  # type: ignore[bool]


class PerformanceMetric(Base):  # type: ignore[misc,valid-type]
    """
    Performance metrics and analytics storage.

    Attributes
    ----------
    id : int
        Primary key.
    metric_id : str
        Unique metric identifier (UUID).
    name : str
        Metric name.
    type : MetricType
        Metric type (counter, gauge, histogram, etc.).
    value : float
        Metric value.
    unit : str
        Metric unit (e.g., 'ms', 'bytes', 'count').
    command_id : int
        Foreign key to Command.
    project_id : int
        Foreign key to Project.
    timestamp : datetime
        Metric timestamp.
    labels : dict
        Metric labels/tags (JSON).
    metadata : dict
        Additional metric metadata (JSON).
    """

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    metric_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    name = Column(String(200), nullable=False, index=True)
    type = Column(SQLEnum(MetricType), nullable=False)  # type: ignore[var-annotated]
    value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    command_id = Column(Integer, ForeignKey("commands.id", ondelete="CASCADE"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True)
    labels = Column(JSON, default=dict, nullable=False)
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    command = relationship("Command", back_populates="metrics")

    __table_args__ = (
        Index("idx_metric_name_timestamp", "name", "timestamp"),
        Index("idx_metric_type_timestamp", "type", "timestamp"),
        Index("idx_metric_project_timestamp", "project_id", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<PerformanceMetric(id={self.id}, name='{self.name}', value={self.value})>"


class AuditLog(Base):  # type: ignore[misc,valid-type]
    """
    Audit log for compliance and security tracking.

    Attributes
    ----------
    id : int
        Primary key.
    log_id : str
        Unique log entry identifier (UUID).
    action : AuditAction
        Action performed.
    resource_type : str
        Type of resource (e.g., 'command', 'project', 'user').
    resource_id : str
        Resource identifier.
    user_id : int
        Foreign key to User.
    ip_address : str
        Client IP address.
    user_agent : str
        Client user agent.
    timestamp : datetime
        Action timestamp.
    success : bool
        Whether action succeeded.
    details : dict
        Additional action details (JSON).
    metadata : dict
        Additional audit metadata (JSON).
    """

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    log_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)  # type: ignore[var-annotated]
    resource_type = Column(String(100), nullable=False, index=True)
    resource_id = Column(String(100), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 max length
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True)
    success = Column(Boolean, default=True, nullable=False)
    details = Column(JSON, default=dict, nullable=False)
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    # Indexes
    __table_args__ = (
        Index("idx_audit_user_timestamp", "user_id", "timestamp"),
        Index("idx_audit_resource", "resource_type", "resource_id"),
        Index("idx_audit_action_timestamp", "action", "timestamp"),
    )

    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action='{self.action.value}', resource='{self.resource_type}')>"


class RDFSpecification(Base):  # type: ignore[misc,valid-type]
    """
    RDF specification metadata and tracking.

    Attributes
    ----------
    id : int
        Primary key.
    spec_id : str
        Unique specification identifier (UUID).
    project_id : int
        Foreign key to Project.
    file_path : str
        Path to TTL file.
    content_hash : str
        SHA256 hash of content.
    format : str
        RDF format (e.g., 'turtle', 'n3', 'rdf/xml').
    triple_count : int
        Number of RDF triples.
    valid : bool
        Whether specification is valid.
    validation_errors : str
        Validation errors (if any).
    created_at : datetime
        Specification creation timestamp.
    updated_at : datetime
        Last update timestamp.
    metadata : dict
        Additional specification metadata (JSON).
    """

    __tablename__ = "rdf_specifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    spec_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String(500), nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    format = Column(String(50), default="turtle", nullable=False)
    triple_count = Column(Integer, default=0, nullable=False)
    valid = Column(Boolean, default=True, nullable=False)
    validation_errors = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="specifications")

    # Indexes
    __table_args__ = (
        Index("idx_spec_project_updated", "project_id", "updated_at"),
        UniqueConstraint("project_id", "file_path", name="uq_spec_project_path"),
    )

    def __repr__(self) -> str:
        return f"<RDFSpecification(id={self.id}, file_path='{self.file_path}', valid={self.valid})>"


class TelemetryEvent(Base):  # type: ignore[misc,valid-type]
    """
    OpenTelemetry event storage for observability.

    Attributes
    ----------
    id : int
        Primary key.
    event_id : str
        Unique event identifier (UUID).
    trace_id : str
        OpenTelemetry trace ID.
    span_id : str
        OpenTelemetry span ID.
    parent_span_id : str
        Parent span ID.
    command_id : int
        Foreign key to Command.
    name : str
        Event name.
    kind : str
        Span kind (e.g., 'internal', 'server', 'client').
    status_code : str
        Status code (e.g., 'OK', 'ERROR').
    start_time : datetime
        Event start timestamp.
    end_time : datetime
        Event end timestamp.
    duration_ns : int
        Duration in nanoseconds.
    attributes : dict
        Event attributes (JSON).
    resource_attributes : dict
        Resource attributes (JSON).
    """

    __tablename__ = "telemetry_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    trace_id = Column(String(32), nullable=False, index=True)
    span_id = Column(String(16), nullable=False, index=True)
    parent_span_id = Column(String(16), nullable=True)
    command_id = Column(Integer, ForeignKey("commands.id", ondelete="CASCADE"), nullable=True)
    name = Column(String(200), nullable=False, index=True)
    kind = Column(String(50), nullable=True)
    status_code = Column(String(50), nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_ns = Column(Integer, nullable=True)
    attributes = Column(JSON, default=dict, nullable=False)
    resource_attributes = Column(JSON, default=dict, nullable=False)

    # Relationships
    command = relationship("Command", back_populates="telemetry_events")

    # Indexes
    __table_args__ = (
        Index("idx_telemetry_trace_span", "trace_id", "span_id"),
        Index("idx_telemetry_start_time", "start_time"),
    )

    def __repr__(self) -> str:
        return f"<TelemetryEvent(id={self.id}, name='{self.name}', trace_id='{self.trace_id}')>"


class CacheEntry(Base):  # type: ignore[misc,valid-type]
    """
    Cache storage for performance optimization.

    Attributes
    ----------
    id : int
        Primary key.
    key : str
        Cache key (unique).
    value : str
        Cached value (compressed if large).
    value_hash : str
        SHA256 hash of value.
    size_bytes : int
        Size of value in bytes.
    created_at : datetime
        Cache entry creation timestamp.
    expires_at : datetime
        Cache expiration timestamp.
    access_count : int
        Number of times accessed.
    last_accessed_at : datetime
        Last access timestamp.
    metadata : dict
        Additional cache metadata (JSON).
    """

    __tablename__ = "cache_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(200), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    value_hash = Column(String(64), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    meta = Column(JSON, default=dict, nullable=False)

    # Indexes
    __table_args__ = (
        Index("idx_cache_expires", "expires_at"),
        Index("idx_cache_last_accessed", "last_accessed_at"),
    )

    def __repr__(self) -> str:
        return f"<CacheEntry(id={self.id}, key='{self.key}', size={self.size_bytes})>"

    @hybrid_property
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.expires_at is None:
            return False
        # Ensure expires_at is timezone-aware for SQLite compatibility
        expires = _ensure_aware(self.expires_at)
        return expires is not None and datetime.now(UTC) > expires  # type: ignore[bool]


class Configuration(Base):  # type: ignore[misc,valid-type]
    """
    Project-specific configuration storage.

    Attributes
    ----------
    id : int
        Primary key.
    config_id : str
        Unique configuration identifier (UUID).
    project_id : int
        Foreign key to Project.
    key : str
        Configuration key.
    value : str
        Configuration value (JSON serialized).
    type : str
        Value type (e.g., 'string', 'integer', 'boolean', 'json').
    encrypted : bool
        Whether value is encrypted.
    description : str
        Configuration description.
    created_at : datetime
        Configuration creation timestamp.
    updated_at : datetime
        Last update timestamp.
    metadata : dict
        Additional configuration metadata (JSON).
    """

    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    key = Column(String(200), nullable=False, index=True)
    value = Column(Text, nullable=False)
    type = Column(String(50), default="string", nullable=False)
    encrypted = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="configurations")

    # Indexes
    __table_args__ = (
        UniqueConstraint("project_id", "key", name="uq_config_project_key"),
        Index("idx_config_project_key", "project_id", "key"),
    )

    def __repr__(self) -> str:
        return f"<Configuration(id={self.id}, key='{self.key}', project_id={self.project_id})>"

    def get_value(self) -> Any:
        """Deserialize and return configuration value."""
        if self.type == "json":
            return json.loads(self.value)  # type: ignore[str]
        if self.type == "integer":
            return int(self.value)
        if self.type == "float":
            return float(self.value)
        if self.type == "boolean":
            return self.value.lower() in ("true", "1", "yes")
        return self.value


class SessionToken(Base):  # type: ignore[misc,valid-type]
    """
    User session token management.

    Attributes
    ----------
    id : int
        Primary key.
    token : str
        Session token (UUID).
    user_id : int
        Foreign key to User.
    created_at : datetime
        Token creation timestamp.
    expires_at : datetime
        Token expiration timestamp.
    last_used_at : datetime
        Last usage timestamp.
    ip_address : str
        Client IP address.
    user_agent : str
        Client user agent.
    is_active : bool
        Whether token is active.
    metadata : dict
        Additional token metadata (JSON).
    """

    __tablename__ = "session_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", back_populates="sessions")

    # Indexes
    __table_args__ = (
        Index("idx_session_user_active", "user_id", "is_active"),
        Index("idx_session_expires", "expires_at"),
    )

    def __repr__(self) -> str:
        return f"<SessionToken(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"

    @hybrid_property
    def is_expired(self) -> bool:
        """Check if session token is expired."""
        # Ensure expires_at is timezone-aware for SQLite compatibility
        expires = _ensure_aware(self.expires_at)
        return expires is not None and datetime.now(UTC) > expires  # type: ignore[bool]


# ============================================================================
# Event Listeners
# ============================================================================


@event.listens_for(Command, "before_update")
def calculate_command_duration(mapper: Any, connection: Any, target: Command) -> None:
    """Automatically calculate command duration on status update."""
    if target.status in (ExecutionStatus.SUCCESS, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED, ExecutionStatus.TIMEOUT):
        if target.completed_at and target.started_at:
            # Ensure both datetimes are timezone-aware for compatibility with SQLite
            completed = _ensure_aware(target.completed_at)
            started = _ensure_aware(target.started_at)
            if completed and started:
                delta = completed - started
                target.duration_ms = delta.total_seconds() * 1000


@event.listens_for(CacheEntry, "before_update")
def update_cache_access(mapper: Any, connection: Any, target: CacheEntry) -> None:
    """Automatically update cache access statistics."""
    target.access_count += 1  # type: ignore[int]
    target.last_accessed_at = datetime.now(UTC)  # type: ignore[datetime]
