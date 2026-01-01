from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span


@dataclass
class ExecutionRecord:
    execution_id: str
    workflow_id: str
    status: str
    result_data: dict[str, Any]
    timestamp: str
    duration: float = 0.0


@dataclass
class WorkflowRecord:
    workflow_id: str
    name: str
    config: dict[str, Any]
    created_at: str
    last_executed: str | None = None
    execution_count: int = 0


class DatabaseStore:
    def __init__(self, db_path: str | Path = ".spec-kit/database.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    config TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_executed TEXT,
                    execution_count INTEGER DEFAULT 0
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result_data TEXT NOT NULL,
                    duration REAL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(workflow_id)
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS artifacts (
                    artifact_id TEXT PRIMARY KEY,
                    execution_id TEXT NOT NULL,
                    artifact_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (execution_id) REFERENCES executions(execution_id)
                )
            """)

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflow_executions
                ON executions(workflow_id)
            """)

            conn.commit()

    @timed
    def save_workflow(self, workflow: WorkflowRecord) -> None:
        with span("db.save_workflow", workflow_id=workflow.workflow_id):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO workflows
                    (workflow_id, name, config, created_at, last_executed, execution_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    workflow.workflow_id,
                    workflow.name,
                    json.dumps(workflow.config),
                    workflow.created_at,
                    workflow.last_executed,
                    workflow.execution_count,
                ))
                conn.commit()
            metric_counter("db.workflows.saved", 1)

    @timed
    def save_execution(self, execution: ExecutionRecord) -> None:
        with span("db.save_execution", execution_id=execution.execution_id):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO executions
                    (execution_id, workflow_id, status, result_data, duration, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    execution.execution_id,
                    execution.workflow_id,
                    execution.status,
                    json.dumps(execution.result_data),
                    execution.duration,
                    execution.timestamp,
                ))
                conn.commit()
            metric_counter("db.executions.saved", 1)

    @timed
    def get_workflow(self, workflow_id: str) -> WorkflowRecord | None:
        with span("db.get_workflow", workflow_id=workflow_id):
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute("""
                    SELECT workflow_id, name, config, created_at, last_executed, execution_count
                    FROM workflows WHERE workflow_id = ?
                """, (workflow_id,)).fetchone()

            if not row:
                return None

            return WorkflowRecord(
                workflow_id=row[0],
                name=row[1],
                config=json.loads(row[2]),
                created_at=row[3],
                last_executed=row[4],
                execution_count=row[5],
            )

    @timed
    def get_workflow_executions(self, workflow_id: str) -> list[ExecutionRecord]:
        with span("db.get_workflow_executions", workflow_id=workflow_id):
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT execution_id, workflow_id, status, result_data, duration, timestamp
                    FROM executions WHERE workflow_id = ? ORDER BY timestamp DESC
                """, (workflow_id,)).fetchall()

            return [
                ExecutionRecord(
                    execution_id=row[0],
                    workflow_id=row[1],
                    status=row[2],
                    result_data=json.loads(row[3]),
                    duration=row[4],
                    timestamp=row[5],
                )
                for row in rows
            ]

    @timed
    def save_artifact(
        self,
        execution_id: str,
        artifact_type: str,
        content: str,
    ) -> str:
        with span("db.save_artifact", artifact_type=artifact_type):
            artifact_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().isoformat()

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO artifacts
                    (artifact_id, execution_id, artifact_type, content, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (artifact_id, execution_id, artifact_type, content, timestamp))
                conn.commit()

            metric_counter("db.artifacts.saved", 1)
            return artifact_id

    @timed
    def get_execution_artifacts(self, execution_id: str) -> dict[str, str]:
        with span("db.get_execution_artifacts", execution_id=execution_id):
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT artifact_type, content FROM artifacts
                    WHERE execution_id = ?
                """, (execution_id,)).fetchall()

            return {row[0]: row[1] for row in rows}

    @timed
    def get_workflow_statistics(self, workflow_id: str) -> dict[str, Any]:
        with span("db.get_workflow_statistics", workflow_id=workflow_id):
            with sqlite3.connect(self.db_path) as conn:
                executions = conn.execute("""
                    SELECT status, duration FROM executions WHERE workflow_id = ?
                """, (workflow_id,)).fetchall()

            total = len(executions)
            successful = sum(1 for e in executions if e[0] == "completed")
            failed = sum(1 for e in executions if e[0] == "failed")
            avg_duration = sum(e[1] for e in executions if e[1]) / total if total > 0 else 0

            return {
                "total_executions": total,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / total if total > 0 else 0,
                "average_duration": avg_duration,
            }

    @timed
    def list_workflows(self, limit: int = 100) -> list[WorkflowRecord]:
        with span("db.list_workflows", limit=limit):
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT workflow_id, name, config, created_at, last_executed, execution_count
                    FROM workflows ORDER BY created_at DESC LIMIT ?
                """, (limit,)).fetchall()

            return [
                WorkflowRecord(
                    workflow_id=row[0],
                    name=row[1],
                    config=json.loads(row[2]),
                    created_at=row[3],
                    last_executed=row[4],
                    execution_count=row[5],
                )
                for row in rows
            ]


_global_db: DatabaseStore | None = None


def get_database() -> DatabaseStore:
    global _global_db
    if _global_db is None:
        _global_db = DatabaseStore()
    return _global_db
