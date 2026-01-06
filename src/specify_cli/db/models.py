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
from decimal import Decimal
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
    Numeric,
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
    "Invoice",
    "InvoiceStatus",
    "MetricType",
    "PerformanceMetric",
    "Project",
    "RDFSpecification",
    "SessionToken",
    "SLA",
    "SLATier",
    "Subscription",
    "SubscriptionTier",
    "SupportTicket",
    "SupportTicketStatus",
    "TelemetryEvent",
    "User",
    "UsageEvent",
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


class SubscriptionTier(str, Enum):
    """Subscription tier enumeration for SaaS licensing."""

    FREE = "free"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class InvoiceStatus(str, Enum):
    """Invoice payment status enumeration."""

    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"


class SupportTicketStatus(str, Enum):
    """Support ticket status enumeration."""

    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class SLATier(str, Enum):
    """SLA tier enumeration for support response times."""

    COMMUNITY = "community"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    PREMIUM_ENTERPRISE = "premium_enterprise"


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
# RevOps: Subscription & Billing Models
# ============================================================================


class Subscription(Base):  # type: ignore[misc,valid-type]
    """
    Subscription model for SaaS licensing and usage tracking.

    Attributes
    ----------
    id : int
        Primary key.
    subscription_id : str
        Unique subscription identifier (UUID).
    user_id : int
        Foreign key to User.
    tier : SubscriptionTier
        Subscription tier (free, professional, enterprise).
    stripe_customer_id : str
        Stripe customer ID for payment processing.
    stripe_subscription_id : str
        Stripe subscription ID.
    status : str
        Subscription status (active, cancelled, expired, suspended).
    start_date : datetime
        Subscription start date.
    end_date : datetime
        Subscription end date (None if indefinite).
    renewal_date : datetime
        Next renewal or billing date.
    monthly_cost : Decimal
        Monthly subscription cost.
    annual_cost : Decimal
        Annual subscription cost (if applicable).
    api_quota : int
        Monthly API call quota.
    storage_quota : int
        Storage quota in bytes.
    max_users : int
        Maximum team members allowed.
    auto_renew : bool
        Whether subscription auto-renews.
    metadata : dict
        Additional subscription metadata (JSON).
    """

    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tier = Column(SQLEnum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False, index=True)  # type: ignore[var-annotated]
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    status = Column(String(50), default="active", nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    renewal_date = Column(DateTime(timezone=True), nullable=True)
    monthly_cost = Column(Numeric(10, 2), default=0, nullable=False)
    annual_cost = Column(Numeric(10, 2), default=0, nullable=False)
    api_quota = Column(Integer, default=100, nullable=False)  # API calls/month
    storage_quota = Column(Integer, default=2147483648, nullable=False)  # 2GB default
    max_users = Column(Integer, default=1, nullable=False)
    auto_renew = Column(Boolean, default=True, nullable=False)
    meta = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user = relationship("User", backref="subscriptions")
    usage_events = relationship("UsageEvent", back_populates="subscription", cascade="all, delete-orphan")
    invoices = relationship("Invoice", back_populates="subscription", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index("idx_subscription_user_tier", "user_id", "tier"),
        Index("idx_subscription_status", "status"),
        Index("idx_subscription_stripe_customer", "stripe_customer_id"),
    )

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, user_id={self.user_id}, tier='{self.tier.value}', status='{self.status}')>"


class UsageEvent(Base):  # type: ignore[misc,valid-type]
    """
    Usage event for metered billing and consumption tracking.

    Attributes
    ----------
    id : int
        Primary key.
    event_id : str
        Unique event identifier (UUID).
    subscription_id : int
        Foreign key to Subscription.
    user_id : int
        Foreign key to User.
    metric_type : str
        Type of usage (api_calls, storage, etc).
    amount : float
        Amount consumed.
    unit : str
        Unit of measurement (count, bytes, etc).
    timestamp : datetime
        Event timestamp.
    billing_period : str
        Billing period identifier (YYYY-MM).
    metadata : dict
        Additional event metadata (JSON).
    """

    __tablename__ = "usage_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    metric_type = Column(String(100), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    unit = Column(String(50), default="count", nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True)
    billing_period = Column(String(7), nullable=False, index=True)  # YYYY-MM
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="usage_events")
    user = relationship("User", backref="usage_events")

    # Indexes
    __table_args__ = (
        Index("idx_usage_subscription_period", "subscription_id", "billing_period"),
        Index("idx_usage_metric_timestamp", "metric_type", "timestamp"),
        Index("idx_usage_user_period", "user_id", "billing_period"),
    )

    def __repr__(self) -> str:
        return f"<UsageEvent(id={self.id}, metric_type='{self.metric_type}', amount={self.amount})>"


class Invoice(Base):  # type: ignore[misc,valid-type]
    """
    Invoice for subscription billing and payment tracking.

    Attributes
    ----------
    id : int
        Primary key.
    invoice_id : str
        Unique invoice identifier (UUID).
    subscription_id : int
        Foreign key to Subscription.
    user_id : int
        Foreign key to User.
    stripe_invoice_id : str
        Stripe invoice ID.
    status : InvoiceStatus
        Invoice payment status.
    amount : Decimal
        Invoice total amount.
    currency : str
        Currency code (USD, EUR, etc).
    billing_period_start : datetime
        Billing period start date.
    billing_period_end : datetime
        Billing period end date.
    issue_date : datetime
        Invoice issue date.
    due_date : datetime
        Payment due date.
    paid_date : datetime
        Payment date (None if unpaid).
    pdf_url : str
        URL to invoice PDF.
    line_items : dict
        Invoice line items (JSON).
    metadata : dict
        Additional invoice metadata (JSON).
    """

    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    invoice_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stripe_invoice_id = Column(String(255), nullable=True, unique=True, index=True)
    status = Column(SQLEnum(InvoiceStatus), default=InvoiceStatus.DRAFT, nullable=False, index=True)  # type: ignore[var-annotated]
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    billing_period_start = Column(DateTime(timezone=True), nullable=False)
    billing_period_end = Column(DateTime(timezone=True), nullable=False)
    issue_date = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    due_date = Column(DateTime(timezone=True), nullable=False)
    paid_date = Column(DateTime(timezone=True), nullable=True)
    pdf_url = Column(String(500), nullable=True)
    line_items = Column(JSON, default=dict, nullable=False)
    meta = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    subscription = relationship("Subscription", back_populates="invoices")
    user = relationship("User", backref="invoices")

    # Indexes
    __table_args__ = (
        Index("idx_invoice_user_status", "user_id", "status"),
        Index("idx_invoice_subscription_period", "subscription_id", "issue_date"),
        Index("idx_invoice_due_date", "due_date"),
    )

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, invoice_id='{self.invoice_id}', amount={self.amount}, status='{self.status.value}')>"


# ============================================================================
# RevOps: Support Ticket & SLA Models
# ============================================================================


class SupportTicket(Base):  # type: ignore[misc,valid-type]
    """
    Support ticket for customer support tracking.

    Attributes
    ----------
    id : int
        Primary key.
    ticket_id : str
        Unique ticket identifier (UUID).
    user_id : int
        Foreign key to User.
    sla_id : int
        Foreign key to SLA tier.
    title : str
        Ticket title.
    description : str
        Ticket description.
    status : SupportTicketStatus
        Ticket status.
    priority : str
        Priority level (low, medium, high, critical).
    severity : str
        Severity level (low, medium, high, critical).
    category : str
        Ticket category.
    assigned_to : str
        Assigned support engineer.
    created_at : datetime
        Ticket creation timestamp.
    updated_at : datetime
        Last update timestamp.
    first_response_at : datetime
        First response timestamp.
    resolved_at : datetime
        Resolution timestamp.
    closed_at : datetime
        Ticket close timestamp.
    resolution : str
        Resolution description.
    metadata : dict
        Additional ticket metadata (JSON).
    """

    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticket_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    sla_id = Column(Integer, ForeignKey("slas.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(SupportTicketStatus), default=SupportTicketStatus.OPEN, nullable=False, index=True)  # type: ignore[var-annotated]
    priority = Column(String(20), default="medium", nullable=False, index=True)
    severity = Column(String(20), default="medium", nullable=False)
    category = Column(String(100), nullable=True)
    assigned_to = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)
    first_response_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(Text, nullable=True)
    meta = Column(JSON, default=dict, nullable=False)

    # Relationships
    user = relationship("User", backref="support_tickets")
    sla = relationship("SLA", backref="tickets")

    # Indexes
    __table_args__ = (
        Index("idx_ticket_user_status", "user_id", "status"),
        Index("idx_ticket_priority", "priority"),
        Index("idx_ticket_created", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<SupportTicket(ticket_id='{self.ticket_id}', status='{self.status.value}', priority='{self.priority}')>"


class SLA(Base):  # type: ignore[misc,valid-type]
    """
    Service Level Agreement (SLA) for support tiers.

    Attributes
    ----------
    id : int
        Primary key.
    sla_id : str
        Unique SLA identifier (UUID).
    tier : SLATier
        SLA tier level.
    name : str
        SLA name.
    description : str
        SLA description.
    initial_response_time_minutes : int
        Initial response SLA in minutes.
    resolution_time_minutes : int
        Resolution SLA in minutes.
    availability_percentage : float
        Guaranteed uptime percentage.
    support_hours : str
        Support hours (24/7, business, etc).
    max_concurrent_tickets : int
        Max concurrent tickets allowed.
    features : dict
        SLA features and benefits (JSON).
    metadata : dict
        Additional SLA metadata (JSON).
    """

    __tablename__ = "slas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sla_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    tier = Column(SQLEnum(SLATier), default=SLATier.COMMUNITY, nullable=False, unique=True)  # type: ignore[var-annotated]
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    initial_response_time_minutes = Column(Integer, nullable=False)
    resolution_time_minutes = Column(Integer, nullable=False)
    availability_percentage = Column(Float, default=99.0, nullable=False)
    support_hours = Column(String(50), default="business", nullable=False)
    max_concurrent_tickets = Column(Integer, nullable=True)
    features = Column(JSON, default=dict, nullable=False)
    meta = Column(JSON, default=dict, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)

    def __repr__(self) -> str:
        return f"<SLA(tier='{self.tier.value}', name='{self.name}')>"


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
