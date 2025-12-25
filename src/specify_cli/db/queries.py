"""
specify_cli.db.queries - Advanced Query Patterns
=================================================

Comprehensive query patterns and optimization utilities for SQLAlchemy.

Features:
- Pre-built query patterns for common operations
- Advanced filtering and search capabilities
- Aggregation and analytics queries
- Pagination with cursor and offset-based approaches
- Query result caching
- Lazy loading optimization
- Full-text search
- Time-series queries

Examples
--------
    >>> from specify_cli.db.queries import CommandQueries, ProjectQueries
    >>> from specify_cli.db.session import get_session
    >>>
    >>> # Query commands with filters
    >>> with get_session() as session:
    ...     queries = CommandQueries(session)
    ...     commands = queries.find_by_status("success", limit=10)
    ...
    >>> # Paginate results
    >>> with get_session() as session:
    ...     queries = CommandQueries(session)
    ...     page = queries.paginate(page=1, per_page=20)
    ...     for cmd in page.items:
    ...         print(cmd.name)
    ...
    >>> # Aggregate metrics
    >>> with get_session() as session:
    ...     queries = PerformanceMetricQueries(session)
    ...     stats = queries.aggregate_by_name("execution_time")
    ...     print(f"Average: {stats['avg']}, Max: {stats['max']}")
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import and_, desc, func, or_
from sqlalchemy.orm import Session

from specify_cli.db.models import (
    AuditLog,
    CacheEntry,
    Command,
    Configuration,
    ExecutionStatus,
    PerformanceMetric,
    Project,
    RDFSpecification,
    TelemetryEvent,
    User,
)

__all__ = [
    "AuditLogQueries",
    "BaseQueries",
    "CacheQueries",
    "CommandQueries",
    "ConfigurationQueries",
    "PaginationResult",
    "PerformanceMetricQueries",
    "ProjectQueries",
    "RDFSpecificationQueries",
    "TelemetryEventQueries",
    "UserQueries",
]

logger = logging.getLogger(__name__)


# ============================================================================
# Pagination
# ============================================================================


class PaginationResult:
    """
    Pagination result container.

    Attributes
    ----------
    items : list
        Current page items.
    total : int
        Total number of items.
    page : int
        Current page number (1-indexed).
    per_page : int
        Items per page.
    pages : int
        Total number of pages.
    has_prev : bool
        Whether there is a previous page.
    has_next : bool
        Whether there is a next page.
    """

    def __init__(
        self,
        items: list[Any],
        total: int,
        page: int,
        per_page: int,
    ) -> None:
        self.items = items
        self.total = total
        self.page = page
        self.per_page = per_page
        self.pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        self.has_prev = page > 1
        self.has_next = page < self.pages

    def __repr__(self) -> str:
        return f"<PaginationResult(page={self.page}/{self.pages}, items={len(self.items)}, total={self.total})>"


# ============================================================================
# Base Query Pattern
# ============================================================================


class BaseQueries:
    """
    Base query pattern class with common operations.

    Parameters
    ----------
    session : Session
        SQLAlchemy session.
    model : type
        SQLAlchemy model class.
    """

    def __init__(self, session: Session, model: type) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, id_: int) -> Any | None:
        """
        Get record by ID.

        Parameters
        ----------
        id_ : int
            Record ID.

        Returns
        -------
        Any | None
            Record or None if not found.
        """
        return self.session.query(self.model).filter(self.model.id == id_).first()  # type: ignore[attr-defined]

    def get_all(self, limit: int | None = None, offset: int = 0) -> list[Any]:
        """
        Get all records.

        Parameters
        ----------
        limit : int, optional
            Maximum number of records to return.
        offset : int, optional
            Number of records to skip (default: 0).

        Returns
        -------
        list[Any]
            List of records.
        """
        query = self.session.query(self.model)  # type: ignore[var-annotated]
        if offset > 0:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def count(self) -> int:
        """
        Count total records.

        Returns
        -------
        int
            Total record count.
        """
        return self.session.query(func.count(self.model.id)).scalar()  # type: ignore[attr-defined,no-any-return]

    def paginate(
        self,
        page: int = 1,
        per_page: int = 20,
        order_by: Any | None = None,
    ) -> PaginationResult:
        """
        Paginate query results.

        Parameters
        ----------
        page : int, optional
            Page number (1-indexed, default: 1).
        per_page : int, optional
            Items per page (default: 20).
        order_by : Any, optional
            SQLAlchemy order_by clause.

        Returns
        -------
        PaginationResult
            Pagination result.
        """
        # Get total count
        total = self.count()

        # Build query
        query = self.session.query(self.model)  # type: ignore[var-annotated]
        if order_by is not None:
            query = query.order_by(order_by)

        # Apply pagination
        offset = (page - 1) * per_page
        items = query.offset(offset).limit(per_page).all()

        return PaginationResult(
            items=items,
            total=total,
            page=page,
            per_page=per_page,
        )

    def delete_by_id(self, id_: int) -> bool:
        """
        Delete record by ID.

        Parameters
        ----------
        id_ : int
            Record ID.

        Returns
        -------
        bool
            True if deleted, False if not found.
        """
        record = self.get_by_id(id_)
        if record is None:
            return False
        self.session.delete(record)
        self.session.commit()
        return True


# ============================================================================
# User Queries
# ============================================================================


class UserQueries(BaseQueries):
    """Query patterns for User model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        return self.session.query(User).filter(User.username == username).first()

    def find_by_email(self, email: str) -> User | None:
        """Find user by email."""
        return self.session.query(User).filter(User.email == email).first()

    def find_by_api_key(self, api_key: str) -> User | None:
        """Find user by API key."""
        return self.session.query(User).filter(User.api_key == api_key).first()

    def get_active_users(self, limit: int | None = None) -> list[User]:
        """Get all active users."""
        query = self.session.query(User).filter(User.is_active == True)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def get_admins(self) -> list[User]:
        """Get all admin users."""
        return self.session.query(User).filter(User.is_admin == True).all()

    def search_users(
        self,
        query_str: str,
        limit: int = 10,
    ) -> list[User]:
        """
        Search users by username, email, or full name.

        Parameters
        ----------
        query_str : str
            Search query string.
        limit : int, optional
            Maximum number of results (default: 10).

        Returns
        -------
        list[User]
            Matching users.
        """
        pattern = f"%{query_str}%"
        return (
            self.session.query(User)
            .filter(
                or_(
                    User.username.ilike(pattern),
                    User.email.ilike(pattern),
                    User.full_name.ilike(pattern),
                )
            )
            .limit(limit)
            .all()
        )


# ============================================================================
# Project Queries
# ============================================================================


class ProjectQueries(BaseQueries):
    """Query patterns for Project model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Project)

    def find_by_slug(self, slug: str) -> Project | None:
        """Find project by slug."""
        return self.session.query(Project).filter(Project.slug == slug).first()

    def find_by_owner(
        self,
        owner_id: int,
        active_only: bool = True,
    ) -> list[Project]:
        """
        Find projects by owner.

        Parameters
        ----------
        owner_id : int
            Owner user ID.
        active_only : bool, optional
            Only return active projects (default: True).

        Returns
        -------
        list[Project]
            Owner's projects.
        """
        query = self.session.query(Project).filter(Project.owner_id == owner_id)
        if active_only:
            query = query.filter(Project.is_active == True)
        return query.all()

    def get_active_projects(self, limit: int | None = None) -> list[Project]:
        """Get all active projects."""
        query = self.session.query(Project).filter(Project.is_active == True)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def search_projects(
        self,
        query_str: str,
        owner_id: int | None = None,
        limit: int = 10,
    ) -> list[Project]:
        """
        Search projects by name or description.

        Parameters
        ----------
        query_str : str
            Search query string.
        owner_id : int, optional
            Filter by owner ID.
        limit : int, optional
            Maximum number of results (default: 10).

        Returns
        -------
        list[Project]
            Matching projects.
        """
        pattern = f"%{query_str}%"
        query = self.session.query(Project).filter(
            or_(
                Project.name.ilike(pattern),
                Project.description.ilike(pattern),
            )
        )
        if owner_id is not None:
            query = query.filter(Project.owner_id == owner_id)
        return query.limit(limit).all()

    def get_recent_projects(
        self,
        days: int = 7,
        limit: int = 10,
    ) -> list[Project]:
        """
        Get recently updated projects.

        Parameters
        ----------
        days : int, optional
            Number of days to look back (default: 7).
        limit : int, optional
            Maximum number of results (default: 10).

        Returns
        -------
        list[Project]
            Recently updated projects.
        """
        cutoff = datetime.now(UTC) - timedelta(days=days)
        return (
            self.session.query(Project)
            .filter(Project.updated_at >= cutoff)
            .order_by(desc(Project.updated_at))
            .limit(limit)
            .all()
        )


# ============================================================================
# Command Queries
# ============================================================================


class CommandQueries(BaseQueries):
    """Query patterns for Command model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Command)

    def find_by_command_id(self, command_id: str) -> Command | None:
        """Find command by UUID."""
        return self.session.query(Command).filter(Command.command_id == command_id).first()

    def find_by_status(
        self,
        status: str | ExecutionStatus,
        limit: int | None = None,
    ) -> list[Command]:
        """Find commands by status."""
        if isinstance(status, str):
            status = ExecutionStatus(status)
        query = self.session.query(Command).filter(Command.status == status)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def find_by_user(
        self,
        user_id: int,
        limit: int | None = None,
    ) -> list[Command]:
        """Find commands by user."""
        query = self.session.query(Command).filter(Command.user_id == user_id)
        if limit is not None:
            query = query.limit(limit)
        return query.order_by(desc(Command.started_at)).all()

    def find_by_project(
        self,
        project_id: int,
        limit: int | None = None,
    ) -> list[Command]:
        """Find commands by project."""
        query = self.session.query(Command).filter(Command.project_id == project_id)
        if limit is not None:
            query = query.limit(limit)
        return query.order_by(desc(Command.started_at)).all()

    def get_recent_commands(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> list[Command]:
        """
        Get recent commands.

        Parameters
        ----------
        hours : int, optional
            Number of hours to look back (default: 24).
        limit : int, optional
            Maximum number of results (default: 100).

        Returns
        -------
        list[Command]
            Recent commands.
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        return (
            self.session.query(Command)
            .filter(Command.started_at >= cutoff)
            .order_by(desc(Command.started_at))
            .limit(limit)
            .all()
        )

    def get_failed_commands(
        self,
        hours: int = 24,
        limit: int = 50,
    ) -> list[Command]:
        """Get recent failed commands."""
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        return (
            self.session.query(Command)
            .filter(
                and_(
                    Command.status == ExecutionStatus.FAILED,
                    Command.started_at >= cutoff,
                )
            )
            .order_by(desc(Command.started_at))
            .limit(limit)
            .all()
        )

    def get_command_statistics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Get command execution statistics.

        Parameters
        ----------
        start_date : datetime, optional
            Start date filter.
        end_date : datetime, optional
            End date filter.

        Returns
        -------
        dict[str, Any]
            Statistics including counts, averages, etc.
        """
        query = self.session.query(Command)

        if start_date:
            query = query.filter(Command.started_at >= start_date)
        if end_date:
            query = query.filter(Command.started_at <= end_date)

        # Get counts by status
        status_counts = (
            query.with_entities(
                Command.status,
                func.count(Command.id).label("count"),
            )
            .group_by(Command.status)
            .all()
        )

        # Get duration statistics
        duration_stats = (
            query.with_entities(
                func.avg(Command.duration_ms).label("avg_duration"),
                func.min(Command.duration_ms).label("min_duration"),
                func.max(Command.duration_ms).label("max_duration"),
            )
            .filter(Command.duration_ms.isnot(None))
            .first()
        )

        return {
            "total": query.count(),
            "by_status": {status.value: count for status, count in status_counts},
            "duration": {
                "avg_ms": duration_stats.avg_duration if duration_stats else None,
                "min_ms": duration_stats.min_duration if duration_stats else None,
                "max_ms": duration_stats.max_duration if duration_stats else None,
            },
        }


# ============================================================================
# Performance Metric Queries
# ============================================================================


class PerformanceMetricQueries(BaseQueries):
    """Query patterns for PerformanceMetric model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, PerformanceMetric)

    def find_by_name(
        self,
        name: str,
        limit: int | None = None,
    ) -> list[PerformanceMetric]:
        """Find metrics by name."""
        query = self.session.query(PerformanceMetric).filter(
            PerformanceMetric.name == name
        )
        if limit is not None:
            query = query.limit(limit)
        return query.order_by(desc(PerformanceMetric.timestamp)).all()

    def find_by_command(self, command_id: int) -> list[PerformanceMetric]:
        """Find metrics by command."""
        return (
            self.session.query(PerformanceMetric)
            .filter(PerformanceMetric.command_id == command_id)
            .all()
        )

    def aggregate_by_name(
        self,
        name: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict[str, Any]:
        """
        Aggregate metrics by name.

        Parameters
        ----------
        name : str
            Metric name.
        start_date : datetime, optional
            Start date filter.
        end_date : datetime, optional
            End date filter.

        Returns
        -------
        dict[str, Any]
            Aggregated statistics.
        """
        query = self.session.query(PerformanceMetric).filter(
            PerformanceMetric.name == name
        )

        if start_date:
            query = query.filter(PerformanceMetric.timestamp >= start_date)
        if end_date:
            query = query.filter(PerformanceMetric.timestamp <= end_date)

        stats = (
            query.with_entities(
                func.count(PerformanceMetric.id).label("count"),
                func.avg(PerformanceMetric.value).label("avg"),
                func.min(PerformanceMetric.value).label("min"),
                func.max(PerformanceMetric.value).label("max"),
                func.sum(PerformanceMetric.value).label("sum"),
            )
            .first()
        )

        return {
            "count": stats.count or 0,
            "avg": stats.avg,
            "min": stats.min,
            "max": stats.max,
            "sum": stats.sum,
        }

    def get_time_series(
        self,
        name: str,
        hours: int = 24,
        interval_minutes: int = 60,
    ) -> list[dict[str, Any]]:
        """
        Get time-series data for a metric.

        Parameters
        ----------
        name : str
            Metric name.
        hours : int, optional
            Number of hours to look back (default: 24).
        interval_minutes : int, optional
            Aggregation interval in minutes (default: 60).

        Returns
        -------
        list[dict[str, Any]]
            Time-series data points.
        """
        cutoff = datetime.now(UTC) - timedelta(hours=hours)

        # This is a simplified version; for production, use window functions
        results = (
            self.session.query(PerformanceMetric)
            .filter(
                and_(
                    PerformanceMetric.name == name,
                    PerformanceMetric.timestamp >= cutoff,
                )
            )
            .order_by(PerformanceMetric.timestamp)
            .all()
        )

        # Group by interval
        series = []
        current_bucket = None
        bucket_values = []  # type: ignore[var-annotated]

        for metric in results:
            bucket_time = metric.timestamp.replace(
                minute=(metric.timestamp.minute // interval_minutes) * interval_minutes,
                second=0,
                microsecond=0,
            )

            if current_bucket != bucket_time:
                if current_bucket and bucket_values:
                    series.append({
                        "timestamp": current_bucket,
                        "avg": sum(bucket_values) / len(bucket_values),
                        "min": min(bucket_values),
                        "max": max(bucket_values),
                        "count": len(bucket_values),
                    })
                current_bucket = bucket_time
                bucket_values = []

            bucket_values.append(metric.value)

        # Add last bucket
        if current_bucket and bucket_values:
            series.append({
                "timestamp": current_bucket,
                "avg": sum(bucket_values) / len(bucket_values),
                "min": min(bucket_values),
                "max": max(bucket_values),
                "count": len(bucket_values),
            })

        return series


# ============================================================================
# Audit Log Queries
# ============================================================================


class AuditLogQueries(BaseQueries):
    """Query patterns for AuditLog model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, AuditLog)

    def find_by_user(
        self,
        user_id: int,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Find audit logs by user."""
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.user_id == user_id)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .all()
        )

    def find_by_resource(
        self,
        resource_type: str,
        resource_id: str | None = None,
    ) -> list[AuditLog]:
        """Find audit logs by resource."""
        query = self.session.query(AuditLog).filter(
            AuditLog.resource_type == resource_type
        )
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        return query.order_by(desc(AuditLog.timestamp)).all()

    def get_recent_logs(
        self,
        hours: int = 24,
        limit: int = 100,
    ) -> list[AuditLog]:
        """Get recent audit logs."""
        cutoff = datetime.now(UTC) - timedelta(hours=hours)
        return (
            self.session.query(AuditLog)
            .filter(AuditLog.timestamp >= cutoff)
            .order_by(desc(AuditLog.timestamp))
            .limit(limit)
            .all()
        )


# ============================================================================
# RDF Specification Queries
# ============================================================================


class RDFSpecificationQueries(BaseQueries):
    """Query patterns for RDFSpecification model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, RDFSpecification)

    def find_by_project(self, project_id: int) -> list[RDFSpecification]:
        """Find specifications by project."""
        return (
            self.session.query(RDFSpecification)
            .filter(RDFSpecification.project_id == project_id)
            .order_by(desc(RDFSpecification.updated_at))
            .all()
        )

    def find_by_hash(self, content_hash: str) -> list[RDFSpecification]:
        """Find specifications by content hash."""
        return (
            self.session.query(RDFSpecification)
            .filter(RDFSpecification.content_hash == content_hash)
            .all()
        )

    def get_invalid_specs(self) -> list[RDFSpecification]:
        """Get all invalid specifications."""
        return (
            self.session.query(RDFSpecification)
            .filter(RDFSpecification.valid == False)
            .all()
        )


# ============================================================================
# Telemetry Event Queries
# ============================================================================


class TelemetryEventQueries(BaseQueries):
    """Query patterns for TelemetryEvent model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, TelemetryEvent)

    def find_by_trace_id(self, trace_id: str) -> list[TelemetryEvent]:
        """Find events by trace ID."""
        return (
            self.session.query(TelemetryEvent)
            .filter(TelemetryEvent.trace_id == trace_id)
            .order_by(TelemetryEvent.start_time)
            .all()
        )

    def find_by_command(self, command_id: int) -> list[TelemetryEvent]:
        """Find events by command."""
        return (
            self.session.query(TelemetryEvent)
            .filter(TelemetryEvent.command_id == command_id)
            .order_by(TelemetryEvent.start_time)
            .all()
        )


# ============================================================================
# Cache Queries
# ============================================================================


class CacheQueries(BaseQueries):
    """Query patterns for CacheEntry model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, CacheEntry)

    def find_by_key(self, key: str) -> CacheEntry | None:
        """Find cache entry by key."""
        return self.session.query(CacheEntry).filter(CacheEntry.key == key).first()

    def get_expired_entries(self) -> list[CacheEntry]:
        """Get all expired cache entries."""
        now = datetime.now(UTC)
        return (
            self.session.query(CacheEntry)
            .filter(
                and_(
                    CacheEntry.expires_at.isnot(None),
                    CacheEntry.expires_at <= now,
                )
            )
            .all()
        )

    def cleanup_expired(self) -> int:
        """
        Delete expired cache entries.

        Returns
        -------
        int
            Number of entries deleted.
        """
        entries = self.get_expired_entries()
        count = len(entries)
        for entry in entries:
            self.session.delete(entry)
        self.session.commit()
        logger.info(f"Cleaned up {count} expired cache entries")
        return count


# ============================================================================
# Configuration Queries
# ============================================================================


class ConfigurationQueries(BaseQueries):
    """Query patterns for Configuration model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Configuration)

    def find_by_project_and_key(
        self,
        project_id: int,
        key: str,
    ) -> Configuration | None:
        """Find configuration by project and key."""
        return (
            self.session.query(Configuration)
            .filter(
                and_(
                    Configuration.project_id == project_id,
                    Configuration.key == key,
                )
            )
            .first()
        )

    def get_project_configs(self, project_id: int) -> list[Configuration]:
        """Get all configurations for a project."""
        return (
            self.session.query(Configuration)
            .filter(Configuration.project_id == project_id)
            .all()
        )
