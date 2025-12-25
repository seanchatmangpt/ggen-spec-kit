"""
specify_cli.db.migrations - Database Migration Management
==========================================================

Alembic integration for database schema migrations with:
- Schema versioning
- Auto-generation from models
- Rollback capabilities
- Data migrations
- Migration verification

Features:
- Automatic migration generation
- Safe rollback procedures
- Migration history tracking
- Data migration support
- Schema validation

Examples
--------
    >>> from specify_cli.db.migrations import MigrationManager
    >>>
    >>> # Initialize migration environment
    >>> manager = MigrationManager()
    >>> manager.init()
    >>>
    >>> # Create a new migration
    >>> manager.create_migration("add_user_fields")
    >>>
    >>> # Apply migrations
    >>> manager.upgrade()
    >>>
    >>> # Rollback one version
    >>> manager.downgrade()
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from alembic import command
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import inspect
from sqlalchemy.engine import Engine

from specify_cli.db.models import Base
from specify_cli.db.session import get_engine

__all__ = [
    "MigrationManager",
    "get_current_revision",
    "get_migration_history",
    "verify_schema",
]

logger = logging.getLogger(__name__)


# ============================================================================
# Migration Manager
# ============================================================================


class MigrationManager:
    """
    Database migration manager using Alembic.

    Provides high-level interface for managing database schema migrations
    with automatic generation, upgrade, downgrade, and verification.

    Parameters
    ----------
    alembic_ini_path : str, optional
        Path to alembic.ini file.
    migrations_dir : str, optional
        Path to migrations directory.
    """

    def __init__(
        self,
        alembic_ini_path: str | None = None,
        migrations_dir: str | None = None,
    ) -> None:
        """Initialize migration manager."""
        # Default paths
        if alembic_ini_path is None:
            alembic_ini_path = str(Path.cwd() / "alembic.ini")
        if migrations_dir is None:
            migrations_dir = str(Path.cwd() / "migrations")

        self.alembic_ini_path = alembic_ini_path
        self.migrations_dir = migrations_dir

        # Create Alembic config
        self.config = self._create_config()

    def _create_config(self) -> Config:
        """
        Create Alembic configuration.

        Returns
        -------
        Config
            Alembic configuration object.
        """
        # If alembic.ini doesn't exist, create in-memory config
        if not Path(self.alembic_ini_path).exists():
            config = Config()
            config.set_main_option("script_location", self.migrations_dir)
            config.set_main_option("prepend_sys_path", ".")
            config.set_main_option("version_path_separator", "os")
        else:
            config = Config(self.alembic_ini_path)

        # Set SQLAlchemy URL from engine
        try:
            engine = get_engine()
            config.set_main_option("sqlalchemy.url", str(engine.url))
        except RuntimeError:
            # Database not initialized yet
            logger.warning("Database not initialized - some operations may fail")

        return config

    def init(self, template: str = "generic") -> None:
        """
        Initialize migration environment.

        Creates the migrations directory structure and configuration.

        Parameters
        ----------
        template : str, optional
            Alembic template to use (default: "generic").
        """
        logger.info(f"Initializing migration environment in {self.migrations_dir}")

        # Create migrations directory if it doesn't exist
        migrations_path = Path(self.migrations_dir)
        if migrations_path.exists():
            logger.warning(f"Migrations directory already exists: {self.migrations_dir}")
            return

        # Initialize Alembic
        try:
            command.init(self.config, self.migrations_dir, template=template)
            logger.info("Migration environment initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize migration environment: {e}")
            raise

    def create_migration(
        self,
        message: str,
        autogenerate: bool = True,
    ) -> str | None:
        """
        Create a new migration.

        Parameters
        ----------
        message : str
            Migration message.
        autogenerate : bool, optional
            Auto-generate migration from model changes (default: True).

        Returns
        -------
        str | None
            Migration revision ID or None if failed.
        """
        logger.info(f"Creating migration: {message}")

        try:
            # Generate migration
            if autogenerate:
                command.revision(
                    self.config,
                    message=message,
                    autogenerate=True,
                )
            else:
                command.revision(
                    self.config,
                    message=message,
                )

            # Get the new revision
            script = ScriptDirectory.from_config(self.config)
            revision = script.get_current_head()

            logger.info(f"Created migration: {revision} - {message}")
            return revision

        except Exception as e:
            logger.error(f"Failed to create migration: {e}")
            raise

    def upgrade(
        self,
        revision: str = "head",
        sql: bool = False,
    ) -> None:
        """
        Upgrade database to a later version.

        Parameters
        ----------
        revision : str, optional
            Target revision (default: "head").
        sql : bool, optional
            Generate SQL script instead of executing (default: False).
        """
        logger.info(f"Upgrading database to {revision}")

        try:
            if sql:
                command.upgrade(self.config, revision, sql=True)
            else:
                command.upgrade(self.config, revision)
            logger.info(f"Successfully upgraded to {revision}")
        except Exception as e:
            logger.error(f"Failed to upgrade database: {e}")
            raise

    def downgrade(
        self,
        revision: str = "-1",
        sql: bool = False,
    ) -> None:
        """
        Revert database to a previous version.

        Parameters
        ----------
        revision : str, optional
            Target revision (default: "-1" for one step back).
        sql : bool, optional
            Generate SQL script instead of executing (default: False).
        """
        logger.info(f"Downgrading database to {revision}")

        try:
            if sql:
                command.downgrade(self.config, revision, sql=True)
            else:
                command.downgrade(self.config, revision)
            logger.info(f"Successfully downgraded to {revision}")
        except Exception as e:
            logger.error(f"Failed to downgrade database: {e}")
            raise

    def current(self) -> str | None:
        """
        Get current database revision.

        Returns
        -------
        str | None
            Current revision ID or None if no migrations applied.
        """
        try:
            engine = get_engine()
            return get_current_revision(engine)
        except Exception as e:
            logger.error(f"Failed to get current revision: {e}")
            return None

    def history(self, verbose: bool = False) -> list[dict[str, Any]]:
        """
        Get migration history.

        Parameters
        ----------
        verbose : bool, optional
            Include detailed information (default: False).

        Returns
        -------
        list[dict[str, Any]]
            Migration history.
        """
        try:
            engine = get_engine()
            return get_migration_history(engine, verbose=verbose)
        except Exception as e:
            logger.error(f"Failed to get migration history: {e}")
            return []

    def stamp(self, revision: str = "head") -> None:
        """
        Stamp database with a specific revision without running migrations.

        Parameters
        ----------
        revision : str, optional
            Revision to stamp (default: "head").
        """
        logger.info(f"Stamping database with revision {revision}")

        try:
            command.stamp(self.config, revision)
            logger.info(f"Successfully stamped database with {revision}")
        except Exception as e:
            logger.error(f"Failed to stamp database: {e}")
            raise

    def verify(self) -> dict[str, Any]:
        """
        Verify database schema against models.

        Returns
        -------
        dict[str, Any]
            Verification results.
        """
        try:
            engine = get_engine()
            return verify_schema(engine)
        except Exception as e:
            logger.error(f"Failed to verify schema: {e}")
            return {
                "valid": False,
                "error": str(e),
            }


# ============================================================================
# Utility Functions
# ============================================================================


def get_current_revision(engine: Engine) -> str | None:
    """
    Get current database revision.

    Parameters
    ----------
    engine : Engine
        SQLAlchemy engine.

    Returns
    -------
    str | None
        Current revision ID or None if no migrations applied.
    """
    with engine.connect() as connection:
        context = MigrationContext.configure(connection)
        current_rev = context.get_current_revision()
        return current_rev


def get_migration_history(
    engine: Engine,
    verbose: bool = False,
) -> list[dict[str, Any]]:
    """
    Get migration history.

    Parameters
    ----------
    engine : Engine
        SQLAlchemy engine.
    verbose : bool, optional
        Include detailed information (default: False).

    Returns
    -------
    list[dict[str, Any]]
        Migration history.
    """
    history = []

    # Get script directory
    alembic_ini_path = str(Path.cwd() / "alembic.ini")
    if Path(alembic_ini_path).exists():
        config = Config(alembic_ini_path)
        script = ScriptDirectory.from_config(config)

        # Get all revisions
        for revision in script.walk_revisions():
            entry = {
                "revision": revision.revision,
                "down_revision": revision.down_revision,
                "branch_labels": revision.branch_labels,
                "message": revision.doc,
            }

            if verbose:
                entry.update({
                    "module_path": revision.module._source_path if hasattr(revision.module, "_source_path") else None,
                })

            history.append(entry)

    return history


def verify_schema(engine: Engine) -> dict[str, Any]:
    """
    Verify database schema against SQLAlchemy models.

    Parameters
    ----------
    engine : Engine
        SQLAlchemy engine.

    Returns
    -------
    dict[str, Any]
        Verification results including missing/extra tables and columns.
    """
    inspector = inspect(engine)

    # Get table names from database
    db_tables = set(inspector.get_table_names())

    # Get table names from models
    model_tables = set(Base.metadata.tables.keys())

    # Compare
    missing_tables = model_tables - db_tables
    extra_tables = db_tables - model_tables

    # Check columns for common tables
    common_tables = model_tables & db_tables
    column_issues = {}

    for table_name in common_tables:
        # Get columns from database
        db_columns = {col["name"] for col in inspector.get_columns(table_name)}

        # Get columns from model
        model_table = Base.metadata.tables[table_name]
        model_columns = {col.name for col in model_table.columns}

        # Compare
        missing_columns = model_columns - db_columns
        extra_columns = db_columns - model_columns

        if missing_columns or extra_columns:
            column_issues[table_name] = {
                "missing": list(missing_columns),
                "extra": list(extra_columns),
            }

    # Build result
    result = {
        "valid": not (missing_tables or extra_tables or column_issues),
        "missing_tables": list(missing_tables),
        "extra_tables": list(extra_tables),
        "column_issues": column_issues,
    }

    return result


# ============================================================================
# Data Migration Utilities
# ============================================================================


def create_data_migration(
    manager: MigrationManager,
    message: str,
) -> str | None:
    """
    Create a data migration (non-autogenerated).

    Parameters
    ----------
    manager : MigrationManager
        Migration manager instance.
    message : str
        Migration message.

    Returns
    -------
    str | None
        Migration revision ID or None if failed.
    """
    return manager.create_migration(message, autogenerate=False)


def backup_database(
    engine: Engine,
    backup_path: str | Path,
) -> bool:
    """
    Create a database backup.

    Note: This is a simple implementation for SQLite. For production
    databases (PostgreSQL, MySQL), use native backup tools.

    Parameters
    ----------
    engine : Engine
        SQLAlchemy engine.
    backup_path : str | Path
        Path to backup file.

    Returns
    -------
    bool
        True if backup succeeded, False otherwise.
    """
    try:
        # Only works for SQLite
        if not str(engine.url).startswith("sqlite:"):
            logger.warning("Backup only supported for SQLite databases")
            return False

        import shutil

        # Get database file path
        db_path = str(engine.url).replace("sqlite:///", "")

        # Create backup
        shutil.copy2(db_path, backup_path)
        logger.info(f"Database backed up to {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to backup database: {e}")
        return False


def restore_database(
    backup_path: str | Path,
    target_path: str | Path,
) -> bool:
    """
    Restore database from backup.

    Note: This is a simple implementation for SQLite. For production
    databases (PostgreSQL, MySQL), use native restore tools.

    Parameters
    ----------
    backup_path : str | Path
        Path to backup file.
    target_path : str | Path
        Path to target database file.

    Returns
    -------
    bool
        True if restore succeeded, False otherwise.
    """
    try:
        import shutil

        # Restore backup
        shutil.copy2(backup_path, target_path)
        logger.info(f"Database restored from {backup_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to restore database: {e}")
        return False
