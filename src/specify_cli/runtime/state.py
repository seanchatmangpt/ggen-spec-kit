from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from specify_cli.core.shell import timed
from specify_cli.core.telemetry import metric_counter, span


@dataclass
class ExecutionState:
    execution_id: str
    phase: str
    status: str
    start_time: str
    end_time: str | None = None
    duration: float = 0.0
    input_data: dict[str, Any] = field(default_factory=dict)
    output_data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class StateStore:
    def __init__(self, db_path: str | Path = ".spec-kit/executions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    execution_id TEXT PRIMARY KEY,
                    phase TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    duration REAL,
                    input_data TEXT,
                    output_data TEXT,
                    errors TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    @timed
    def save_execution(self, state: ExecutionState) -> None:
        with span("state.save_execution", execution_id=state.execution_id):
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO executions
                    (execution_id, phase, status, start_time, end_time, duration, 
                     input_data, output_data, errors, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    state.execution_id,
                    state.phase,
                    state.status,
                    state.start_time,
                    state.end_time,
                    state.duration,
                    json.dumps(state.input_data),
                    json.dumps(state.output_data),
                    json.dumps(state.errors),
                    json.dumps(state.metadata),
                ))
                conn.commit()
            metric_counter("state.executions.saved", 1)

    @timed
    def get_execution(self, execution_id: str) -> ExecutionState | None:
        with span("state.get_execution", execution_id=execution_id):
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute("""
                    SELECT execution_id, phase, status, start_time, end_time,
                           duration, input_data, output_data, errors, metadata
                    FROM executions WHERE execution_id = ?
                """, (execution_id,)).fetchone()

            if not row:
                return None

            return ExecutionState(
                execution_id=row[0],
                phase=row[1],
                status=row[2],
                start_time=row[3],
                end_time=row[4],
                duration=row[5],
                input_data=json.loads(row[6]) if row[6] else {},
                output_data=json.loads(row[7]) if row[7] else {},
                errors=json.loads(row[8]) if row[8] else [],
                metadata=json.loads(row[9]) if row[9] else {},
            )

    @timed
    def get_phase_executions(self, phase: str) -> list[ExecutionState]:
        with span("state.get_phase_executions", phase=phase):
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT execution_id, phase, status, start_time, end_time,
                           duration, input_data, output_data, errors, metadata
                    FROM executions WHERE phase = ? ORDER BY created_at DESC
                """, (phase,)).fetchall()

            return [
                ExecutionState(
                    execution_id=row[0],
                    phase=row[1],
                    status=row[2],
                    start_time=row[3],
                    end_time=row[4],
                    duration=row[5],
                    input_data=json.loads(row[6]) if row[6] else {},
                    output_data=json.loads(row[7]) if row[7] else {},
                    errors=json.loads(row[8]) if row[8] else [],
                    metadata=json.loads(row[9]) if row[9] else {},
                )
                for row in rows
            ]

    @timed
    def get_latest_execution(self) -> ExecutionState | None:
        with span("state.get_latest_execution"):
            with sqlite3.connect(self.db_path) as conn:
                row = conn.execute("""
                    SELECT execution_id, phase, status, start_time, end_time,
                           duration, input_data, output_data, errors, metadata
                    FROM executions ORDER BY created_at DESC LIMIT 1
                """).fetchone()

            if not row:
                return None

            return ExecutionState(
                execution_id=row[0],
                phase=row[1],
                status=row[2],
                start_time=row[3],
                end_time=row[4],
                duration=row[5],
                input_data=json.loads(row[6]) if row[6] else {},
                output_data=json.loads(row[7]) if row[7] else {},
                errors=json.loads(row[8]) if row[8] else [],
                metadata=json.loads(row[9]) if row[9] else {},
            )

    @timed
    def get_execution_history(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[ExecutionState]:
        with span("state.get_execution_history", limit=limit):
            with sqlite3.connect(self.db_path) as conn:
                rows = conn.execute("""
                    SELECT execution_id, phase, status, start_time, end_time,
                           duration, input_data, output_data, errors, metadata
                    FROM executions
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset)).fetchall()

            return [
                ExecutionState(
                    execution_id=row[0],
                    phase=row[1],
                    status=row[2],
                    start_time=row[3],
                    end_time=row[4],
                    duration=row[5],
                    input_data=json.loads(row[6]) if row[6] else {},
                    output_data=json.loads(row[7]) if row[7] else {},
                    errors=json.loads(row[8]) if row[8] else [],
                    metadata=json.loads(row[9]) if row[9] else {},
                )
                for row in rows
            ]

    @timed
    def clear_old_executions(self, days: int = 30) -> int:
        with span("state.clear_old_executions", days=days):
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    DELETE FROM executions
                    WHERE created_at < datetime('now', '-' || ? || ' days')
                """, (days,))
                conn.commit()
                count = cursor.rowcount
            metric_counter("state.executions.cleared", count)
            return count


_global_state_store: StateStore | None = None


def get_state_store() -> StateStore:
    global _global_state_store
    if _global_state_store is None:
        _global_state_store = StateStore()
    return _global_state_store
