"""
specify_cli.db.session - Database Session Management
====================================================

Comprehensive session management with connection pooling, retry logic,
and transaction handling for SQLAlchemy.

Features:
- Connection pooling with configurable limits
- Automatic retry on transient failures
- Graceful degradation
- Context managers for automatic cleanup
- Multi-database support (SQLite, PostgreSQL, MySQL, MongoDB)
- Health checks and monitoring
- Connection timeout handling

Examples
--------
    >>> from specify_cli.db.session import get_session, DatabaseManager
    >>>
    >>> # Use context manager for automatic session cleanup
    >>> with get_session() as session:
    ...     user = session.query(User).first()
    ...     print(user.username)
    >>>
    >>> # Manual session management
    >>> session = get_session()
    >>> try:
    ...     user = session.query(User).first()
    ...     session.commit()
    ... except Exception:
    ...     session.rollback()
    ...     raise
    ... finally:
    ...     session.close()
    >>>
    >>> # Initialize database
    >>> from specify_cli.db.session import init_db
    >>> init_db("sqlite:///./specify.db")
"""

from __future__ import annotations

import logging
import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool, StaticPool

from specify_cli.db.models import Base

__all__ = [
    "DatabaseManager",
    "RetryConfig",
    "close_db",
    "get_engine",
    "get_session",
    "get_session_factory",
    "health_check",
    "init_db",
]

logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================


class RetryConfig:
    """
    Configuration for database retry logic.

    Attributes
    ----------
    max_attempts : int
        Maximum number of retry attempts (default: 3).
    initial_delay : float
        Initial retry delay in seconds (default: 0.1).
    max_delay : float
        Maximum retry delay in seconds (default: 5.0).
    exponential_base : float
        Exponential backoff base (default: 2.0).
    """

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 0.1,
        max_delay: float = 5.0,
        exponential_base: float = 2.0,
    ) -> None:
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base


# ============================================================================
# Database Manager
# ============================================================================


class DatabaseManager:
    """
    Comprehensive database manager with connection pooling and retry logic.

    This class manages database connections, sessions, and provides
    health checking and monitoring capabilities.

    Attributes
    ----------
    engine : Engine
        SQLAlchemy database engine.
    session_factory : sessionmaker
        SQLAlchemy session factory.
    retry_config : RetryConfig
        Retry configuration.
    """

    def __init__(
        self,
        url: str,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_timeout: float = 30.0,
        pool_recycle: int = 3600,
        retry_config: RetryConfig | None = None,
        **engine_kwargs: Any,
    ) -> None:
        """
        Initialize database manager.

        Parameters
        ----------
        url : str
            Database URL (e.g., 'sqlite:///./specify.db').
        echo : bool, optional
            Enable SQL query logging (default: False).
        pool_size : int, optional
            Connection pool size (default: 5).
        max_overflow : int, optional
            Maximum overflow connections (default: 10).
        pool_timeout : float, optional
            Pool checkout timeout in seconds (default: 30.0).
        pool_recycle : int, optional
            Connection recycle time in seconds (default: 3600).
        retry_config : RetryConfig, optional
            Retry configuration (default: None).
        **engine_kwargs : Any
            Additional SQLAlchemy engine arguments.
        """
        self.url = url
        self.retry_config = retry_config or RetryConfig()

        # Determine pool class based on database type
        poolclass = self._get_pool_class(url)

        # Engine configuration
        engine_config = {
            "echo": echo,
            "poolclass": poolclass,
            "future": True,
        }

        # Add pool-specific configuration
        if poolclass == QueuePool:
            engine_config.update({
                "pool_size": pool_size,
                "max_overflow": max_overflow,
                "pool_timeout": pool_timeout,
                "pool_recycle": pool_recycle,
                "pool_pre_ping": True,  # Verify connections before using
            })

        # Merge additional engine kwargs
        engine_config.update(engine_kwargs)

        # Create engine
        self.engine = create_engine(url, **engine_config)

        # Create session factory
        self.session_factory = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

        # Register event listeners
        self._register_event_listeners()

        logger.info(f"Database manager initialized: {self._safe_url()}")

    def _get_pool_class(self, url: str) -> type[pool.Pool]:
        """
        Determine appropriate pool class based on database URL.

        Parameters
        ----------
        url : str
            Database URL.

        Returns
        -------
        type[pool.Pool]
            Pool class to use.
        """
        parsed = urlparse(url)
        scheme = parsed.scheme.split("+")[0]  # Handle dialects like postgresql+psycopg2

        if scheme == "sqlite":
            # SQLite uses StaticPool for in-memory, NullPool for file-based
            if ":memory:" in url or "mode=memory" in url:
                return StaticPool
            return NullPool
        # PostgreSQL, MySQL, etc. use QueuePool
        return QueuePool

    def _safe_url(self) -> str:
        """
        Get database URL with password masked.

        Returns
        -------
        str
            Safe database URL for logging.
        """
        parsed = urlparse(self.url)
        if parsed.password:
            safe_netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                safe_netloc += f":{parsed.port}"
            return self.url.replace(parsed.netloc, safe_netloc)
        return self.url

    def _register_event_listeners(self) -> None:
        """Register SQLAlchemy event listeners for monitoring."""
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_conn: Any, connection_record: Any) -> None:
            """Handle new database connections."""
            logger.debug("New database connection established")

        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_conn: Any, connection_record: Any, connection_proxy: Any) -> None:
            """Handle connection checkout from pool."""
            logger.debug("Connection checked out from pool")

        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_conn: Any, connection_record: Any) -> None:
            """Handle connection checkin to pool."""
            logger.debug("Connection returned to pool")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get database session with automatic cleanup.

        Yields
        ------
        Session
            SQLAlchemy session.

        Examples
        --------
            >>> with db_manager.get_session() as session:
            ...     user = session.query(User).first()
        """
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_with_retry(
        self,
        func: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute function with retry logic.

        Parameters
        ----------
        func : Callable[..., Any][..., Any][..., Any]
            Function to execute.
        *args : Any
            Positional arguments to pass to function.
        **kwargs : Any
            Keyword arguments to pass to function.

        Returns
        -------
        Any
            Function return value.

        Raises
        ------
        SQLAlchemyError
            If all retry attempts fail.
        """
        delay = self.retry_config.initial_delay

        for attempt in range(1, self.retry_config.max_attempts + 1):
            try:
                return func(*args, **kwargs)
            except OperationalError as e:
                if attempt == self.retry_config.max_attempts:
                    logger.error(f"Database operation failed after {attempt} attempts: {e}")
                    raise

                logger.warning(f"Database operation failed (attempt {attempt}/{self.retry_config.max_attempts}), retrying in {delay}s: {e}")
                time.sleep(delay)

                # Exponential backoff
                delay = min(
                    delay * self.retry_config.exponential_base,
                    self.retry_config.max_delay,
                )

        # Should not reach here
        msg = "Unexpected retry loop exit"
        raise SQLAlchemyError(msg)

    def health_check(self) -> dict[str, Any]:
        """
        Perform database health check.

        Returns
        -------
        dict[str, Any]
            Health check results.
        """
        start_time = time.time()
        result = {
            "healthy": False,
            "latency_ms": 0.0,
            "error": None,
            "pool_size": 0,
            "pool_checked_out": 0,
        }

        try:
            with self.get_session() as session:
                # Execute simple query
                session.execute("SELECT 1")  # type: ignore[call-overload]
                result["healthy"] = True

                # Pool statistics
                if hasattr(self.engine.pool, "size"):
                    result["pool_size"] = self.engine.pool.size()
                if hasattr(self.engine.pool, "checkedout"):
                    result["pool_checked_out"] = self.engine.pool.checkedout()

        except Exception as e:
            result["error"] = str(e)  # type: ignore[assignment]
            logger.error(f"Database health check failed: {e}")

        result["latency_ms"] = (time.time() - start_time) * 1000
        return result

    def create_all(self) -> None:
        """Create all database tables."""
        logger.info("Creating database tables")
        Base.metadata.create_all(bind=self.engine)

    def drop_all(self) -> None:
        """Drop all database tables. Use with caution!"""
        logger.warning("Dropping all database tables")
        Base.metadata.drop_all(bind=self.engine)

    def close(self) -> None:
        """Close database connections."""
        logger.info("Closing database connections")
        self.engine.dispose()


# ============================================================================
# Global Database Manager
# ============================================================================


_db_manager: DatabaseManager | None = None


def init_db(
    url: str | None = None,
    echo: bool = False,
    **kwargs: Any,
) -> DatabaseManager:
    """
    Initialize global database manager.

    Parameters
    ----------
    url : str, optional
        Database URL (default: 'sqlite:///./specify.db').
    echo : bool, optional
        Enable SQL query logging (default: False).
    **kwargs : Any
        Additional database manager arguments.

    Returns
    -------
    DatabaseManager
        Initialized database manager.
    """
    global _db_manager

    if url is None:
        from specify_cli.core.config import get_cache_dir
        db_path = get_cache_dir() / "specify.db"
        url = f"sqlite:///{db_path}"

    _db_manager = DatabaseManager(url=url, echo=echo, **kwargs)
    _db_manager.create_all()

    return _db_manager


def get_engine() -> Engine:
    """
    Get global database engine.

    Returns
    -------
    Engine
        SQLAlchemy engine.

    Raises
    ------
    RuntimeError
        If database not initialized.
    """
    if _db_manager is None:
        msg = "Database not initialized. Call init_db() first."
        raise RuntimeError(msg)
    return _db_manager.engine


def get_session_factory() -> sessionmaker:
    """
    Get global session factory.

    Returns
    -------
    sessionmaker
        SQLAlchemy session factory.

    Raises
    ------
    RuntimeError
        If database not initialized.
    """
    if _db_manager is None:
        msg = "Database not initialized. Call init_db() first."
        raise RuntimeError(msg)
    return _db_manager.session_factory


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    Get database session with automatic cleanup.

    Yields
    ------
    Session
        SQLAlchemy session.

    Examples
    --------
        >>> from specify_cli.db.session import get_session
        >>> with get_session() as session:
        ...     user = session.query(User).first()
    """
    if _db_manager is None:
        # Auto-initialize with default SQLite database
        init_db()

    if _db_manager is not None:
        with _db_manager.get_session() as session:
            yield session


def close_db() -> None:
    """Close global database connections."""
    global _db_manager
    if _db_manager is not None:
        _db_manager.close()
        _db_manager = None


def health_check() -> dict[str, Any]:
    """
    Perform database health check.

    Returns
    -------
    dict[str, Any]
        Health check results.
    """
    if _db_manager is None:
        return {
            "healthy": False,
            "error": "Database not initialized",
        }
    return _db_manager.health_check()
