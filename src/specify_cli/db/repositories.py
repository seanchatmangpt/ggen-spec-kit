"""
specify_cli.db.repositories - Data Access Patterns
===================================================

Repository pattern implementation for clean data access with:
- CRUD operations
- Batch operations
- Atomic transactions
- Complex queries
- Validation
- Error handling

Features:
- Repository pattern for each model
- Transaction management
- Bulk operations optimization
- Cascading delete handling
- Data validation
- Error recovery

Examples
--------
    >>> from specify_cli.db.repositories import UserRepository, ProjectRepository
    >>> from specify_cli.db.session import get_session
    >>>
    >>> # Create a new user
    >>> with get_session() as session:
    ...     repo = UserRepository(session)
    ...     user = repo.create({
    ...         "username": "alice",
    ...         "email": "alice@example.com",
    ...         "password_hash": b"hashed_password",
    ...     })
    ...
    >>> # Update user
    >>> with get_session() as session:
    ...     repo = UserRepository(session)
    ...     user = repo.update(1, {"full_name": "Alice Smith"})
    ...
    >>> # Batch create projects
    >>> with get_session() as session:
    ...     repo = ProjectRepository(session)
    ...     projects = repo.bulk_create([
    ...         {"name": "Project 1", "slug": "project-1", "owner_id": 1},
    ...         {"name": "Project 2", "slug": "project-2", "owner_id": 1},
    ...     ])
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from specify_cli.db.models import (
    AuditAction,
    AuditLog,
    CacheEntry,
    Command,
    Configuration,
    ExecutionStatus,
    PerformanceMetric,
    Project,
    RDFSpecification,
    SessionToken,
    User,
)
from specify_cli.db.queries import (
    AuditLogQueries,
    CacheQueries,
    CommandQueries,
    ConfigurationQueries,
    PerformanceMetricQueries,
    ProjectQueries,
    RDFSpecificationQueries,
    UserQueries,
)

__all__ = [
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
]

logger = logging.getLogger(__name__)


# ============================================================================
# Base Repository
# ============================================================================


class BaseRepository:
    """
    Base repository pattern with common CRUD operations.

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

    def create(self, data: dict[str, Any]) -> Any:
        """
        Create a new record.

        Parameters
        ----------
        data : dict[str, Any]
            Record data.

        Returns
        -------
        Any
            Created record.

        Raises
        ------
        IntegrityError
            If data violates constraints.
        """
        try:
            record = self.model(**data)
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
            logger.info(f"Created {self.model.__name__} with id={record.id}")
            return record
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to create {self.model.__name__}: {e}")
            raise

    def get(self, id_: int) -> Any | None:
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

    def update(self, id_: int, data: dict[str, Any]) -> Any | None:
        """
        Update record by ID.

        Parameters
        ----------
        id_ : int
            Record ID.
        data : dict[str, Any]
            Update data.

        Returns
        -------
        Any | None
            Updated record or None if not found.

        Raises
        ------
        IntegrityError
            If update violates constraints.
        """
        try:
            record = self.get(id_)
            if record is None:
                return None

            for key, value in data.items():
                if hasattr(record, key):
                    setattr(record, key, value)

            self.session.commit()
            self.session.refresh(record)
            logger.info(f"Updated {self.model.__name__} with id={id_}")
            return record
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to update {self.model.__name__} id={id_}: {e}")
            raise

    def delete(self, id_: int) -> bool:
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
        record = self.get(id_)
        if record is None:
            return False

        self.session.delete(record)
        self.session.commit()
        logger.info(f"Deleted {self.model.__name__} with id={id_}")
        return True

    def bulk_create(self, data_list: list[dict[str, Any]]) -> list[Any]:
        """
        Bulk create records.

        Parameters
        ----------
        data_list : list[dict[str, Any]]
            List of record data.

        Returns
        -------
        list[Any]
            Created records.

        Raises
        ------
        IntegrityError
            If any data violates constraints.
        """
        try:
            records = [self.model(**data) for data in data_list]
            self.session.bulk_save_objects(records, return_defaults=True)
            self.session.commit()
            logger.info(f"Bulk created {len(records)} {self.model.__name__} records")
            return records
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Failed to bulk create {self.model.__name__}: {e}")
            raise

    def bulk_update(
        self,
        updates: list[dict[str, Any]],
        id_key: str = "id",
    ) -> int:
        """
        Bulk update records.

        Parameters
        ----------
        updates : list[dict[str, Any]]
            List of update data (must include id_key).
        id_key : str, optional
            Key for record ID (default: "id").

        Returns
        -------
        int
            Number of records updated.

        Raises
        ------
        ValueError
            If id_key not in update data.
        """
        try:
            count = 0
            for update_data in updates:
                if id_key not in update_data:
                    msg = f"Missing {id_key} in update data"
                    raise ValueError(msg)

                id_ = update_data[id_key]
                data = {k: v for k, v in update_data.items() if k != id_key}

                if self.update(id_, data):
                    count += 1

            logger.info(f"Bulk updated {count} {self.model.__name__} records")
            return count
        except (IntegrityError, ValueError) as e:
            self.session.rollback()
            logger.error(f"Failed to bulk update {self.model.__name__}: {e}")
            raise

    def exists(self, id_: int) -> bool:
        """
        Check if record exists.

        Parameters
        ----------
        id_ : int
            Record ID.

        Returns
        -------
        bool
            True if exists, False otherwise.
        """
        return self.session.query(  # type: ignore[no-any-return]
            self.session.query(self.model)
            .filter(self.model.id == id_)  # type: ignore[attr-defined]
            .exists()
        ).scalar()


# ============================================================================
# User Repository
# ============================================================================


class UserRepository(BaseRepository):
    """Repository for User model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, User)
        self.queries = UserQueries(session)

    def create_user(
        self,
        username: str,
        email: str,
        password_hash: bytes,
        **kwargs: Any,
    ) -> User:
        """
        Create a new user.

        Parameters
        ----------
        username : str
            Username.
        email : str
            Email address.
        password_hash : bytes
            Hashed password.
        **kwargs : Any
            Additional user attributes.

        Returns
        -------
        User
            Created user.
        """
        data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]

    def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        return self.queries.find_by_username(username)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        return self.queries.find_by_email(email)

    def get_by_api_key(self, api_key: str) -> User | None:
        """Get user by API key."""
        return self.queries.find_by_api_key(api_key)

    def update_last_login(self, user_id: int) -> User | None:
        """Update user's last login timestamp."""
        return self.update(user_id, {"last_login_at": datetime.now(UTC)})

    def deactivate(self, user_id: int) -> User | None:
        """Deactivate user account."""
        return self.update(user_id, {"is_active": False})

    def activate(self, user_id: int) -> User | None:
        """Activate user account."""
        return self.update(user_id, {"is_active": True})


# ============================================================================
# Project Repository
# ============================================================================


class ProjectRepository(BaseRepository):
    """Repository for Project model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Project)
        self.queries = ProjectQueries(session)

    def create_project(
        self,
        name: str,
        slug: str,
        owner_id: int,
        **kwargs: Any,
    ) -> Project:
        """
        Create a new project.

        Parameters
        ----------
        name : str
            Project name.
        slug : str
            Project slug.
        owner_id : int
            Owner user ID.
        **kwargs : Any
            Additional project attributes.

        Returns
        -------
        Project
            Created project.
        """
        data = {
            "name": name,
            "slug": slug,
            "owner_id": owner_id,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]

    def get_by_slug(self, slug: str) -> Project | None:
        """Get project by slug."""
        return self.queries.find_by_slug(slug)

    def get_user_projects(self, user_id: int) -> list[Project]:
        """Get all projects for a user."""
        return self.queries.find_by_owner(user_id)

    def archive(self, project_id: int) -> Project | None:
        """Archive project (set inactive)."""
        return self.update(project_id, {"is_active": False})

    def unarchive(self, project_id: int) -> Project | None:
        """Unarchive project (set active)."""
        return self.update(project_id, {"is_active": True})


# ============================================================================
# Command Repository
# ============================================================================


class CommandRepository(BaseRepository):
    """Repository for Command model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Command)
        self.queries = CommandQueries(session)

    def create_command(
        self,
        name: str,
        user_id: int | None = None,
        project_id: int | None = None,
        **kwargs: Any,
    ) -> Command:
        """
        Create a new command execution record.

        Parameters
        ----------
        name : str
            Command name.
        user_id : int, optional
            User ID.
        project_id : int, optional
            Project ID.
        **kwargs : Any
            Additional command attributes.

        Returns
        -------
        Command
            Created command.
        """
        data = {
            "name": name,
            "user_id": user_id,
            "project_id": project_id,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]

    def start_command(
        self,
        name: str,
        args: str | None = None,
        user_id: int | None = None,
        project_id: int | None = None,
    ) -> Command:
        """
        Start a new command execution.

        Parameters
        ----------
        name : str
            Command name.
        args : str, optional
            Command arguments.
        user_id : int, optional
            User ID.
        project_id : int, optional
            Project ID.

        Returns
        -------
        Command
            Started command.
        """
        return self.create_command(
            name=name,
            args=args,
            user_id=user_id,
            project_id=project_id,
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(UTC),
        )

    def complete_command(
        self,
        command_id: int,
        exit_code: int,
        stdout: str | None = None,
        stderr: str | None = None,
    ) -> Command | None:
        """
        Mark command as completed.

        Parameters
        ----------
        command_id : int
            Command ID.
        exit_code : int
            Command exit code.
        stdout : str, optional
            Standard output.
        stderr : str, optional
            Standard error.

        Returns
        -------
        Command | None
            Updated command or None if not found.
        """
        status = ExecutionStatus.SUCCESS if exit_code == 0 else ExecutionStatus.FAILED
        return self.update(
            command_id,
            {
                "status": status,
                "exit_code": exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "completed_at": datetime.now(UTC),
            },
        )

    def fail_command(
        self,
        command_id: int,
        error: str,
    ) -> Command | None:
        """
        Mark command as failed.

        Parameters
        ----------
        command_id : int
            Command ID.
        error : str
            Error message.

        Returns
        -------
        Command | None
            Updated command or None if not found.
        """
        return self.update(
            command_id,
            {
                "status": ExecutionStatus.FAILED,
                "stderr": error,
                "completed_at": datetime.now(UTC),
            },
        )


# ============================================================================
# Performance Metric Repository
# ============================================================================


class PerformanceMetricRepository(BaseRepository):
    """Repository for PerformanceMetric model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, PerformanceMetric)
        self.queries = PerformanceMetricQueries(session)

    def record_metric(
        self,
        name: str,
        value: float,
        type: str = "gauge",
        unit: str | None = None,
        command_id: int | None = None,
        project_id: int | None = None,
        **kwargs: Any,
    ) -> PerformanceMetric:
        """
        Record a performance metric.

        Parameters
        ----------
        name : str
            Metric name.
        value : float
            Metric value.
        type : str, optional
            Metric type (default: "gauge").
        unit : str, optional
            Metric unit.
        command_id : int, optional
            Associated command ID.
        project_id : int, optional
            Associated project ID.
        **kwargs : Any
            Additional metric attributes.

        Returns
        -------
        PerformanceMetric
            Created metric.
        """
        data = {
            "name": name,
            "value": value,
            "type": type,
            "unit": unit,
            "command_id": command_id,
            "project_id": project_id,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]


# ============================================================================
# Audit Log Repository
# ============================================================================


class AuditLogRepository(BaseRepository):
    """Repository for AuditLog model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, AuditLog)
        self.queries = AuditLogQueries(session)

    def log_action(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str | None = None,
        user_id: int | None = None,
        success: bool = True,
        **kwargs: Any,
    ) -> AuditLog:
        """
        Log an audit action.

        Parameters
        ----------
        action : AuditAction
            Action performed.
        resource_type : str
            Type of resource.
        resource_id : str, optional
            Resource identifier.
        user_id : int, optional
            User ID.
        success : bool, optional
            Whether action succeeded (default: True).
        **kwargs : Any
            Additional audit log attributes.

        Returns
        -------
        AuditLog
            Created audit log.
        """
        data = {
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "user_id": user_id,
            "success": success,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]


# ============================================================================
# RDF Specification Repository
# ============================================================================


class RDFSpecificationRepository(BaseRepository):
    """Repository for RDFSpecification model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, RDFSpecification)
        self.queries = RDFSpecificationQueries(session)

    def create_specification(
        self,
        project_id: int,
        file_path: str,
        content: str,
        **kwargs: Any,
    ) -> RDFSpecification:
        """
        Create RDF specification with content hash.

        Parameters
        ----------
        project_id : int
            Project ID.
        file_path : str
            Path to TTL file.
        content : str
            RDF content.
        **kwargs : Any
            Additional specification attributes.

        Returns
        -------
        RDFSpecification
            Created specification.
        """
        # Calculate content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        data = {
            "project_id": project_id,
            "file_path": file_path,
            "content_hash": content_hash,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]

    def update_specification(
        self,
        spec_id: int,
        content: str,
        **kwargs: Any,
    ) -> RDFSpecification | None:
        """
        Update specification with new content hash.

        Parameters
        ----------
        spec_id : int
            Specification ID.
        content : str
            New RDF content.
        **kwargs : Any
            Additional update data.

        Returns
        -------
        RDFSpecification | None
            Updated specification or None if not found.
        """
        # Calculate new content hash
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        data = {
            "content_hash": content_hash,
            "updated_at": datetime.now(UTC),
            **kwargs,
        }
        return self.update(spec_id, data)


# ============================================================================
# Cache Repository
# ============================================================================


class CacheRepository(BaseRepository):
    """Repository for CacheEntry model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, CacheEntry)
        self.queries = CacheQueries(session)

    def set_cache(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> CacheEntry:
        """
        Set cache entry.

        Parameters
        ----------
        key : str
            Cache key.
        value : str
            Cache value.
        ttl_seconds : int, optional
            Time-to-live in seconds.

        Returns
        -------
        CacheEntry
            Created or updated cache entry.
        """
        # Calculate value hash and size
        value_hash = hashlib.sha256(value.encode()).hexdigest()
        size_bytes = len(value.encode())

        # Calculate expiration
        expires_at = None
        if ttl_seconds is not None:
            expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)

        # Check if entry exists
        existing = self.queries.find_by_key(key)
        if existing:
            self.update(
                existing.id,  # type: ignore[int]
                {
                    "value": value,
                    "value_hash": value_hash,
                    "size_bytes": size_bytes,
                    "expires_at": expires_at,
                },
            )
            return existing

        # Create new entry
        data = {
            "key": key,
            "value": value,
            "value_hash": value_hash,
            "size_bytes": size_bytes,
            "expires_at": expires_at,
        }
        return self.create(data)  # type: ignore[no-any-return]

    def get_cache(self, key: str) -> str | None:
        """
        Get cache entry value.

        Parameters
        ----------
        key : str
            Cache key.

        Returns
        -------
        str | None
            Cached value or None if not found/expired.
        """
        entry = self.queries.find_by_key(key)
        if entry is None:
            return None

        # Check if expired
        if entry.is_expired:
            self.delete(entry.id)  # type: ignore[int]
            return None

        # Update access stats
        self.update(
            entry.id,  # type: ignore[int]
            {
                "access_count": entry.access_count + 1,
                "last_accessed_at": datetime.now(UTC),
            },
        )

        return entry.value  # type: ignore[str]

    def cleanup_expired(self) -> int:
        """Clean up expired cache entries."""
        return self.queries.cleanup_expired()


# ============================================================================
# Configuration Repository
# ============================================================================


class ConfigurationRepository(BaseRepository):
    """Repository for Configuration model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Configuration)
        self.queries = ConfigurationQueries(session)

    def set_config(
        self,
        project_id: int,
        key: str,
        value: Any,
        **kwargs: Any,
    ) -> Configuration:
        """
        Set configuration value.

        Parameters
        ----------
        project_id : int
            Project ID.
        key : str
            Configuration key.
        value : Any
            Configuration value.
        **kwargs : Any
            Additional configuration attributes.

        Returns
        -------
        Configuration
            Created or updated configuration.
        """
        # Determine type and serialize value
        if isinstance(value, bool):
            type_ = "boolean"
            value_str = str(value)
        elif isinstance(value, int):
            type_ = "integer"
            value_str = str(value)
        elif isinstance(value, float):
            type_ = "float"
            value_str = str(value)
        elif isinstance(value, (dict, list)):
            import json
            type_ = "json"
            value_str = json.dumps(value)
        else:
            type_ = "string"
            value_str = str(value)

        # Check if exists
        existing = self.queries.find_by_project_and_key(project_id, key)
        if existing:
            self.update(
                existing.id,  # type: ignore[int]
                {
                    "value": value_str,
                    "type": type_,
                    **kwargs,
                },
            )
            return existing

        # Create new
        data = {
            "project_id": project_id,
            "key": key,
            "value": value_str,
            "type": type_,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]

    def get_config(
        self,
        project_id: int,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get configuration value.

        Parameters
        ----------
        project_id : int
            Project ID.
        key : str
            Configuration key.
        default : Any, optional
            Default value if not found.

        Returns
        -------
        Any
            Configuration value or default.
        """
        config = self.queries.find_by_project_and_key(project_id, key)
        if config is None:
            return default
        return config.get_value()


# ============================================================================
# Session Token Repository
# ============================================================================


class SessionTokenRepository(BaseRepository):
    """Repository for SessionToken model."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, SessionToken)

    def create_session(
        self,
        user_id: int,
        ttl_seconds: int = 3600,
        **kwargs: Any,
    ) -> SessionToken:
        """
        Create new session token.

        Parameters
        ----------
        user_id : int
            User ID.
        ttl_seconds : int, optional
            Time-to-live in seconds (default: 3600).
        **kwargs : Any
            Additional session attributes.

        Returns
        -------
        SessionToken
            Created session token.
        """
        expires_at = datetime.now(UTC) + timedelta(seconds=ttl_seconds)
        data = {
            "user_id": user_id,
            "expires_at": expires_at,
            **kwargs,
        }
        return self.create(data)  # type: ignore[no-any-return]

    def validate_token(self, token: str) -> SessionToken | None:
        """
        Validate session token.

        Parameters
        ----------
        token : str
            Session token.

        Returns
        -------
        SessionToken | None
            Valid session or None if invalid/expired.
        """
        session_token = (
            self.session.query(SessionToken)
            .filter(SessionToken.token == token)
            .first()
        )

        if session_token is None:
            return None

        # Check if expired or inactive
        if session_token.is_expired or not session_token.is_active:
            return None

        # Update last used
        self.update(
            session_token.id,  # type: ignore[int]
            {"last_used_at": datetime.now(UTC)},
        )

        return session_token

    def revoke_token(self, token: str) -> bool:
        """
        Revoke session token.

        Parameters
        ----------
        token : str
            Session token.

        Returns
        -------
        bool
            True if revoked, False if not found.
        """
        session_token = (
            self.session.query(SessionToken)
            .filter(SessionToken.token == token)
            .first()
        )

        if session_token is None:
            return False

        self.update(session_token.id, {"is_active": False})  # type: ignore[int]
        return True
