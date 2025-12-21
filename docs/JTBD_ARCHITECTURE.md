# JTBD Measurement System Architecture

**Version:** 1.0.0
**Status:** Design Document
**Last Updated:** 2025-12-21

## Executive Summary

This document describes the complete architecture for the Jobs-to-be-Done (JTBD) measurement system in spec-kit. The system implements outcome-driven innovation by tracking customer job completions, outcome achievements, painpoint resolutions, and satisfaction metrics through OpenTelemetry integration.

**Key Features:**
- Real-time JTBD metric collection via OpenTelemetry
- RDF-first specification of jobs, outcomes, and personas
- Three-tier architecture (Commands → Ops → Runtime)
- Integration with existing telemetry infrastructure
- Storage via OTEL exporters and SQLite fallback

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Layers](#architecture-layers)
3. [Data Flow](#data-flow)
4. [Integration Points](#integration-points)
5. [Storage Strategy](#storage-strategy)
6. [API Design](#api-design)
7. [Implementation Plan](#implementation-plan)

---

## System Overview

### Purpose

The JTBD measurement system enables **customer-centric feature development** by:
1. Tracking which jobs users complete with spec-kit features
2. Measuring outcome achievement against success criteria
3. Identifying and resolving painpoints
4. Measuring time-to-outcome across the customer journey
5. Capturing user satisfaction with feature delivery

### Constitutional Equation

```
jtbd-metrics.json = μ(jtbd-spec.ttl, telemetry-data)
```

Where:
- `jtbd-spec.ttl` = RDF specification of jobs, outcomes, personas (source of truth)
- `telemetry-data` = OpenTelemetry spans/events with JTBD attributes
- `μ` = Transformation pipeline (SPARQL query + aggregation)
- `jtbd-metrics.json` = Derived metrics dashboard

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         JTBD Measurement System                          │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: Commands (CLI Interface)                                       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                          │
│  specify jtbd                      # JTBD command group                 │
│    ├─ track-job <job-id>          # Manually track job completion       │
│    ├─ track-outcome <outcome-id>  # Manually track outcome              │
│    ├─ dashboard [--persona X]     # View JTBD metrics dashboard         │
│    ├─ export [--format csv|json]  # Export JTBD data                    │
│    ├─ analyze [--job-id X]        # Analyze job performance             │
│    └─ sync                         # Sync RDF specs to metric store     │
│                                                                          │
│  Uses: Typer, Rich (formatting), JSON output                            │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: Operations (Pure Business Logic)                               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                          │
│  src/specify_cli/ops/jtbd.py                                            │
│    ├─ calculate_job_completion_rate(job_id, persona) → float           │
│    ├─ calculate_outcome_achievement(outcome_id) → dict                 │
│    ├─ calculate_opportunity_score(importance, satisfaction) → float    │
│    ├─ aggregate_painpoint_resolution(painpoint_id) → dict              │
│    ├─ generate_dashboard_data(filters) → dict                          │
│    ├─ compute_time_to_outcome_stats(outcome_id) → dict                 │
│    └─ validate_jtbd_tracking(job_completion) → bool                    │
│                                                                          │
│  Principles:                                                             │
│    • Pure functions (no side effects)                                    │
│    • Returns structured data (dicts, dataclasses)                       │
│    • Fully testable with mocked data                                    │
│    • NO subprocess calls, file I/O, or HTTP                             │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: Runtime (I/O & External Integrations)                          │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                          │
│  src/specify_cli/runtime/jtbd_store.py                                  │
│    ├─ store_job_completion(job: JobCompletion) → None                  │
│    ├─ store_outcome_achieved(outcome: OutcomeAchieved) → None          │
│    ├─ query_jobs(filters: dict) → list[JobCompletion]                  │
│    ├─ query_outcomes(filters: dict) → list[OutcomeAchieved]            │
│    ├─ export_metrics_csv(path: Path, data: dict) → None                │
│    └─ sync_rdf_specs(ontology_path: Path) → None                       │
│                                                                          │
│  Storage Backends:                                                       │
│    • PRIMARY: OpenTelemetry → OTLP Exporter → Backend                  │
│    • FALLBACK: SQLite (when OTEL unavailable)                          │
│    • CACHE: platformdirs cache for recent metrics                      │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ CORE: Existing Infrastructure (Reused)                                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                          │
│  src/specify_cli/core/jtbd_metrics.py         [EXISTING]               │
│    • JobCompletion, OutcomeAchieved dataclasses                         │
│    • track_job_completion(), track_outcome_achieved()                  │
│    • PainpointResolved, TimeToOutcome, UserSatisfaction                │
│                                                                          │
│  src/specify_cli/core/telemetry.py            [EXISTING]               │
│    • span(), metric_counter(), metric_histogram()                      │
│    • OpenTelemetry SDK integration                                      │
│    • Graceful degradation when OTEL unavailable                         │
│                                                                          │
│  src/specify_cli/core/instrumentation.py      [EXISTING]               │
│    • add_span_event(), add_span_attributes()                            │
│    • instrument_command() decorator                                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ STORAGE: Data Persistence Layer                                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                                          │
│  ┌───────────────────────┐        ┌────────────────────────┐           │
│  │ OpenTelemetry Backend │ ◄────  │  OTLP Exporter         │           │
│  │ (Jaeger, Tempo, etc.) │        │  (Primary Path)        │           │
│  └───────────────────────┘        └────────────────────────┘           │
│           │                                                              │
│           ▼                                                              │
│  ┌───────────────────────┐        ┌────────────────────────┐           │
│  │ SPARQL Query Engine   │        │  RDF Graph Store       │           │
│  │ (extract JTBD attrs)  │ ◄────  │  (ontology/*.ttl)      │           │
│  └───────────────────────┘        └────────────────────────┘           │
│           │                                                              │
│           ▼                                                              │
│  ┌───────────────────────┐        ┌────────────────────────┐           │
│  │ SQLite Fallback       │        │  Cache (platformdirs)  │           │
│  │ (~/.cache/specify/)   │        │  (recent metrics)      │           │
│  └───────────────────────┘        └────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Architecture Layers

### Layer 1: Commands Layer

**Location:** `src/specify_cli/commands/jtbd.py`

**Responsibilities:**
- Parse CLI arguments using Typer
- Format output with Rich (tables, JSON, etc.)
- Delegate to ops layer immediately
- Handle user-facing errors gracefully

**Design Pattern:**
```python
@app.command()
@instrument_command("jtbd.dashboard", track_args=True)
def dashboard(
    persona: str | None = typer.Option(None, "--persona", "-p"),
    format_type: str = typer.Option("table", "--format", "-f"),
) -> None:
    """Display JTBD metrics dashboard."""
    try:
        # Delegate to ops layer
        data = jtbd_ops.generate_dashboard_data(
            filters={"persona": persona} if persona else {}
        )

        if format_type == "json":
            dump_json(data)
        else:
            # Rich table formatting
            table = create_dashboard_table(data)
            console.print(table)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
```

**Commands:**

| Command | Description | Example |
|---------|-------------|---------|
| `specify jtbd track-job <job-id>` | Manually track job completion | `specify jtbd track-job deps-add --persona python-developer` |
| `specify jtbd track-outcome <outcome-id>` | Manually track outcome achievement | `specify jtbd track-outcome faster-dependency-mgmt` |
| `specify jtbd dashboard` | View JTBD metrics dashboard | `specify jtbd dashboard --persona python-developer` |
| `specify jtbd export` | Export JTBD data | `specify jtbd export --format csv --output metrics.csv` |
| `specify jtbd analyze <job-id>` | Analyze job performance | `specify jtbd analyze deps-add` |
| `specify jtbd sync` | Sync RDF specs to metric store | `specify jtbd sync` |

### Layer 2: Operations Layer

**Location:** `src/specify_cli/ops/jtbd.py`

**Responsibilities:**
- Pure business logic for JTBD calculations
- Aggregate metrics from tracking data
- Compute opportunity scores
- Validate JTBD data integrity
- Return structured results

**Design Principles:**
- ✅ Pure functions (same input → same output)
- ✅ No subprocess calls, file I/O, or HTTP
- ✅ Returns structured data (dicts, dataclasses)
- ✅ Fully testable with mocked runtime

**Key Functions:**

```python
from dataclasses import dataclass
from typing import Any

@dataclass
class JobMetrics:
    """Aggregated metrics for a job."""
    job_id: str
    persona: str
    total_completions: int
    avg_duration_seconds: float
    success_rate: float
    outcome_achievement_rate: float
    painpoints_resolved: int

def calculate_job_completion_rate(
    job_id: str,
    persona: str | None = None,
    time_range: dict[str, Any] | None = None,
) -> float:
    """Calculate completion rate for a job.

    Parameters
    ----------
    job_id : str
        Job identifier
    persona : str, optional
        Filter by persona
    time_range : dict, optional
        Time range filter (start_date, end_date)

    Returns
    -------
    float
        Completion rate (0.0 to 1.0)
    """
    # Pure calculation - delegates to runtime for data
    from specify_cli.runtime.jtbd_store import query_jobs

    jobs = query_jobs({
        "job_id": job_id,
        "persona": persona,
        "time_range": time_range,
    })

    if not jobs:
        return 0.0

    completed = sum(1 for j in jobs if j.status == JobStatus.COMPLETED)
    return completed / len(jobs)

def calculate_opportunity_score(
    importance: float,
    satisfaction: float,
) -> float:
    """Calculate Outcome-Driven Innovation opportunity score.

    Formula: Importance + (Importance - Satisfaction)

    Interpretation:
    - Score > 10: Underserved (innovation opportunity)
    - Score 5-10: Appropriately served
    - Score < 5: Overserved

    Parameters
    ----------
    importance : float
        How important this outcome is (1-10 scale)
    satisfaction : float
        Current satisfaction with solution (1-10 scale)

    Returns
    -------
    float
        Opportunity score
    """
    return importance + (importance - satisfaction)

def generate_dashboard_data(
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate JTBD dashboard data.

    Parameters
    ----------
    filters : dict, optional
        Filters to apply (persona, job_id, date_range)

    Returns
    -------
    dict
        Dashboard data with jobs, outcomes, painpoints
    """
    from specify_cli.runtime.jtbd_store import (
        query_jobs,
        query_outcomes,
        query_painpoints,
    )

    # Fetch data from runtime
    jobs = query_jobs(filters or {})
    outcomes = query_outcomes(filters or {})
    painpoints = query_painpoints(filters or {})

    # Aggregate metrics
    return {
        "summary": {
            "total_jobs": len(jobs),
            "completed_jobs": sum(1 for j in jobs if j.status == JobStatus.COMPLETED),
            "avg_completion_time": _avg([j.duration_seconds for j in jobs if j.duration_seconds]),
        },
        "outcomes": [
            {
                "outcome_id": o.outcome_id,
                "achievement_rate": o.achievement_rate,
                "exceeds_expectations": o.exceeds_expectations,
            }
            for o in outcomes
        ],
        "painpoints": [
            {
                "painpoint_id": p.painpoint_id,
                "resolution_effectiveness": p.resolution_effectiveness,
            }
            for p in painpoints
        ],
    }
```

### Layer 3: Runtime Layer

**Location:** `src/specify_cli/runtime/jtbd_store.py`

**Responsibilities:**
- Persist JTBD metrics to storage backends
- Query metrics from storage
- Export data to CSV/JSON files
- Sync RDF specs to metric store
- Handle storage backend failures gracefully

**Storage Backends:**

1. **Primary: OpenTelemetry**
   - JTBD metrics sent as OTEL span events/attributes
   - Stored in configured OTEL backend (Jaeger, Tempo, etc.)
   - Queried via OTEL API or backend-specific queries

2. **Fallback: SQLite**
   - Local SQLite database at `~/.cache/specify/jtbd_metrics.db`
   - Used when OTEL is unavailable
   - Schema mirrors JTBD dataclasses

3. **Cache: platformdirs**
   - Recent metrics cached for fast access
   - JSON files in `~/.cache/specify/jtbd/`

**Design Pattern:**

```python
from pathlib import Path
from typing import Any
from specify_cli.core.jtbd_metrics import JobCompletion, OutcomeAchieved
from specify_cli.core.telemetry import span

def store_job_completion(job: JobCompletion) -> None:
    """Store job completion in persistent storage.

    Uses OTEL as primary, SQLite as fallback.
    """
    with span("jtbd.store.job_completion", job_id=job.job_id):
        # Already tracked via core.jtbd_metrics.track_job_completion()
        # This adds persistent storage beyond OTEL

        if _otel_available():
            # Already sent via OTEL spans - no additional action
            pass
        else:
            # Fallback to SQLite
            _store_to_sqlite("job_completions", job)

        # Update cache for fast queries
        _update_cache("jobs", job)

def query_jobs(filters: dict[str, Any]) -> list[JobCompletion]:
    """Query job completions from storage.

    Parameters
    ----------
    filters : dict
        Filter criteria (job_id, persona, time_range)

    Returns
    -------
    list[JobCompletion]
        Matching job completions
    """
    with span("jtbd.query.jobs", filters=filters):
        # Try cache first
        cached = _query_cache("jobs", filters)
        if cached:
            return cached

        # Query from storage backend
        if _otel_available():
            return _query_from_otel("job_completions", filters)
        else:
            return _query_from_sqlite("job_completions", filters)

def export_metrics_csv(path: Path, data: dict[str, Any]) -> None:
    """Export JTBD metrics to CSV file."""
    import csv

    with span("jtbd.export.csv", path=str(path)):
        with path.open("w", newline="") as f:
            # Write CSV based on data structure
            writer = csv.DictWriter(f, fieldnames=_get_fieldnames(data))
            writer.writeheader()
            writer.writerows(_flatten_data(data))
```

---

## Data Flow

### 1. Automatic Tracking (Instrumented Commands)

```
User runs command
     │
     ▼
specify deps add httpx
     │
     ▼
@instrument_command("deps.add")  ◄─── Automatic OTEL span
     │
     ▼
core.jtbd_metrics.track_job_completion(
    JobCompletion(
        job_id="deps-add",
        persona="python-developer",
        feature_used="specify deps add",
    )
)
     │
     ▼
OpenTelemetry span events + attributes
     │
     ├─► OTEL Backend (Jaeger/Tempo)
     └─► SQLite fallback (if OTEL unavailable)
```

### 2. Manual Tracking (CLI Commands)

```
User tracks job manually
     │
     ▼
specify jtbd track-job deps-add --persona python-developer
     │
     ▼
commands.jtbd.track_job()
     │
     ▼
ops.jtbd.validate_tracking_data()
     │
     ▼
runtime.jtbd_store.store_job_completion()
     │
     ├─► OTEL Backend
     └─► SQLite fallback
```

### 3. Dashboard Generation

```
User requests dashboard
     │
     ▼
specify jtbd dashboard --persona python-developer
     │
     ▼
commands.jtbd.dashboard()
     │
     ▼
ops.jtbd.generate_dashboard_data(filters={"persona": "python-developer"})
     │
     ▼
runtime.jtbd_store.query_jobs()
runtime.jtbd_store.query_outcomes()
     │
     ├─► Cache (first)
     ├─► OTEL Backend (if miss)
     └─► SQLite (fallback)
     │
     ▼
ops.jtbd.calculate_job_completion_rate()
ops.jtbd.calculate_opportunity_score()
     │
     ▼
Rich table formatting
     │
     ▼
Display to user
```

### 4. RDF Spec Sync

```
User syncs RDF specs
     │
     ▼
specify jtbd sync
     │
     ▼
commands.jtbd.sync()
     │
     ▼
runtime.jtbd_store.sync_rdf_specs(ontology_path)
     │
     ▼
Parse ontology/*.ttl files
     │
     ▼
Extract jobs, outcomes, personas via SPARQL
     │
     ▼
Update metric store with RDF metadata
     │
     └─► SQLite metadata tables
```

---

## Integration Points

### 1. OpenTelemetry Integration

**Existing Infrastructure:**
- `src/specify_cli/core/telemetry.py` - OTEL setup
- `src/specify_cli/core/instrumentation.py` - Span decorators
- `src/specify_cli/core/jtbd_metrics.py` - Tracking functions

**Integration:**
```python
# Already integrated! Just use existing functions:
from specify_cli.core.jtbd_metrics import (
    track_job_completion,
    track_outcome_achieved,
    track_painpoint_resolved,
)

# Tracking is automatic via @instrument_command
@instrument_command("deps.add", track_args=True)
def add_dependency(package: str) -> None:
    job = JobCompletion(
        job_id="deps-add",
        persona="python-developer",
        feature_used="specify deps add",
    )
    track_job_completion(job)  # ← Sends to OTEL automatically
```

**OTEL Attributes:**
```
Span attributes:
- jtbd.job.id: "deps-add"
- jtbd.job.persona: "python-developer"
- jtbd.job.status: "completed"
- jtbd.job.duration_seconds: 8.5

Span events:
- job_completed
- outcome_achieved
- painpoint_resolved
```

### 2. RDF Ontology Integration

**Existing Infrastructure:**
- `ontology/jtbd-schema.ttl` - Core JTBD vocabulary
- `ontology/spec-kit-jtbd-extension.ttl` - Spec-kit integration
- `sparql/jtbd-*.rq` - SPARQL query templates
- `templates/jtbd-*.tera` - Report templates

**Integration:**
```python
# Query RDF specs via SPARQL
from specify_cli.runtime.jtbd_store import sync_rdf_specs

sync_rdf_specs(Path("ontology/"))

# Extract jobs and outcomes
jobs = extract_jobs_from_rdf("ontology/cli-commands-jtbd.ttl")
outcomes = extract_outcomes_from_rdf("ontology/cli-commands-jtbd.ttl")
```

### 3. ggen Transformation Integration

**Existing Infrastructure:**
- `src/specify_cli/runtime/ggen.py` - ggen CLI wrapper
- `docs/ggen.toml` - Transformation configuration

**Integration:**
```toml
# Add JTBD metrics transformation to ggen.toml
[[transform]]
id = "jtbd-metrics-dashboard"
source = "ontology/cli-commands-jtbd.ttl"
query = "sparql/jtbd-outcome-metrics.rq"
template = "templates/jtbd-metrics-dashboard.tera"
output = "docs/JTBD_METRICS.md"
```

### 4. CLI Command Integration

**Existing Infrastructure:**
- `src/specify_cli/commands/__init__.py` - Command registration
- `src/specify_cli/cli.py` - Main CLI app

**Integration:**
```python
# Add JTBD command group
from specify_cli.commands import jtbd

app.add_typer(jtbd.app, name="jtbd")
```

---

## Storage Strategy

### Schema Design

#### SQLite Schema (Fallback)

```sql
-- Job completions
CREATE TABLE job_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id TEXT NOT NULL,
    persona TEXT NOT NULL,
    feature_used TEXT NOT NULL,
    status TEXT NOT NULL,  -- started, in_progress, completed, failed
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_seconds REAL,
    context JSON,  -- Additional context as JSON
    UNIQUE(job_id, persona, started_at)
);

CREATE INDEX idx_job_id ON job_completions(job_id);
CREATE INDEX idx_persona ON job_completions(persona);
CREATE INDEX idx_started_at ON job_completions(started_at);

-- Outcome achievements
CREATE TABLE outcome_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outcome_id TEXT NOT NULL,
    metric TEXT NOT NULL,
    expected_value REAL NOT NULL,
    actual_value REAL NOT NULL,
    achievement_rate REAL NOT NULL,
    feature TEXT NOT NULL,
    persona TEXT,
    status TEXT NOT NULL,
    measured_at TIMESTAMP NOT NULL,
    context JSON,
    UNIQUE(outcome_id, feature, measured_at)
);

CREATE INDEX idx_outcome_id ON outcome_achievements(outcome_id);
CREATE INDEX idx_feature ON outcome_achievements(feature);
CREATE INDEX idx_measured_at ON outcome_achievements(measured_at);

-- Painpoint resolutions
CREATE TABLE painpoint_resolutions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    painpoint_id TEXT NOT NULL,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    feature TEXT NOT NULL,
    persona TEXT NOT NULL,
    severity_before INTEGER NOT NULL,
    severity_after INTEGER NOT NULL,
    resolution_effectiveness REAL,
    resolved_at TIMESTAMP NOT NULL,
    context JSON,
    UNIQUE(painpoint_id, feature, persona, resolved_at)
);

CREATE INDEX idx_painpoint_id ON painpoint_resolutions(painpoint_id);

-- Time to outcome measurements
CREATE TABLE time_to_outcome (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outcome_id TEXT NOT NULL,
    persona TEXT NOT NULL,
    feature TEXT NOT NULL,
    start_time REAL NOT NULL,
    end_time REAL,
    duration_seconds REAL,
    steps JSON,  -- Array of steps as JSON
    context JSON,
    UNIQUE(outcome_id, persona, feature, start_time)
);

-- User satisfaction
CREATE TABLE user_satisfaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    outcome_id TEXT NOT NULL,
    feature TEXT NOT NULL,
    persona TEXT NOT NULL,
    satisfaction_level TEXT NOT NULL,
    met_expectations BOOLEAN NOT NULL,
    would_recommend BOOLEAN NOT NULL,
    effort_score INTEGER,
    feedback_text TEXT,
    recorded_at TIMESTAMP NOT NULL,
    context JSON,
    UNIQUE(outcome_id, feature, persona, recorded_at)
);

-- RDF metadata cache
CREATE TABLE rdf_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,  -- job, outcome, persona, painpoint
    entity_id TEXT NOT NULL,
    metadata JSON NOT NULL,  -- Full RDF properties as JSON
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(entity_type, entity_id)
);
```

#### Cache Structure

```
~/.cache/specify/jtbd/
├── jobs/
│   ├── deps-add.json          # Recent job completions
│   └── generate-docs.json
├── outcomes/
│   ├── faster-dependency-mgmt.json
│   └── better-observability.json
├── personas/
│   ├── python-developer.json
│   └── devops-engineer.json
└── metadata/
    ├── last_sync.json         # Last RDF sync timestamp
    └── schema_version.json    # Cache schema version
```

### Data Retention

| Data Type | Retention | Cleanup Strategy |
|-----------|-----------|------------------|
| OTEL Spans | Backend-dependent | Configured in OTEL backend |
| SQLite Records | 90 days | Automated cleanup job |
| Cache Files | 7 days | LRU eviction |
| RDF Metadata | Indefinite | Version-controlled |

---

## API Design

### Commands API

```python
# src/specify_cli/commands/jtbd.py

import typer
from rich.console import Console

app = typer.Typer(
    name="jtbd",
    help="Jobs-to-be-Done measurement and analytics.",
)

@app.command()
def track_job(
    job_id: str = typer.Argument(..., help="Job identifier"),
    persona: str = typer.Option(..., "--persona", "-p", help="User persona"),
    feature: str = typer.Option(..., "--feature", "-f", help="Feature used"),
    status: str = typer.Option("completed", "--status", "-s"),
) -> None:
    """Track a job completion manually."""
    ...

@app.command()
def dashboard(
    persona: str | None = typer.Option(None, "--persona", "-p"),
    job_id: str | None = typer.Option(None, "--job-id", "-j"),
    format_type: str = typer.Option("table", "--format", "-f"),
) -> None:
    """Display JTBD metrics dashboard."""
    ...

@app.command()
def export(
    output: Path = typer.Option("jtbd_metrics.csv", "--output", "-o"),
    format_type: str = typer.Option("csv", "--format", "-f"),
    filters: str | None = typer.Option(None, "--filter"),
) -> None:
    """Export JTBD metrics to file."""
    ...

@app.command()
def analyze(
    job_id: str = typer.Argument(..., help="Job to analyze"),
    persona: str | None = typer.Option(None, "--persona", "-p"),
) -> None:
    """Analyze job performance and outcomes."""
    ...

@app.command()
def sync() -> None:
    """Sync RDF specs to JTBD metric store."""
    ...
```

### Operations API

```python
# src/specify_cli/ops/jtbd.py

from dataclasses import dataclass
from typing import Any

@dataclass
class JobMetrics:
    """Aggregated metrics for a job."""
    job_id: str
    persona: str
    total_completions: int
    avg_duration_seconds: float
    success_rate: float
    outcome_achievement_rate: float

def calculate_job_completion_rate(
    job_id: str,
    persona: str | None = None,
    time_range: dict[str, Any] | None = None,
) -> float:
    """Calculate completion rate for a job."""
    ...

def calculate_opportunity_score(
    importance: float,
    satisfaction: float,
) -> float:
    """Calculate ODI opportunity score."""
    ...

def generate_dashboard_data(
    filters: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate dashboard data."""
    ...

def validate_jtbd_tracking(
    job: JobCompletion,
) -> bool:
    """Validate JTBD tracking data."""
    ...
```

### Runtime API

```python
# src/specify_cli/runtime/jtbd_store.py

from pathlib import Path
from typing import Any
from specify_cli.core.jtbd_metrics import (
    JobCompletion,
    OutcomeAchieved,
    PainpointResolved,
)

def store_job_completion(job: JobCompletion) -> None:
    """Store job completion in persistent storage."""
    ...

def store_outcome_achieved(outcome: OutcomeAchieved) -> None:
    """Store outcome achievement."""
    ...

def query_jobs(filters: dict[str, Any]) -> list[JobCompletion]:
    """Query job completions."""
    ...

def query_outcomes(filters: dict[str, Any]) -> list[OutcomeAchieved]:
    """Query outcome achievements."""
    ...

def export_metrics_csv(path: Path, data: dict[str, Any]) -> None:
    """Export metrics to CSV."""
    ...

def sync_rdf_specs(ontology_path: Path) -> None:
    """Sync RDF specs to metric store."""
    ...
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)

**Goal:** Implement runtime storage layer

**Tasks:**
1. Create `src/specify_cli/runtime/jtbd_store.py`
   - SQLite schema creation
   - OTEL backend detection
   - Cache management

2. Implement storage functions:
   - `store_job_completion()`
   - `store_outcome_achieved()`
   - `query_jobs()`
   - `query_outcomes()`

3. Write unit tests for storage layer

**Deliverables:**
- [ ] `runtime/jtbd_store.py` with full storage backend
- [ ] 80%+ test coverage
- [ ] SQLite schema migrations

### Phase 2: Operations Layer (Week 2)

**Goal:** Implement business logic

**Tasks:**
1. Create `src/specify_cli/ops/jtbd.py`
   - Metric calculation functions
   - Dashboard data generation
   - Validation logic

2. Implement key operations:
   - `calculate_job_completion_rate()`
   - `calculate_opportunity_score()`
   - `generate_dashboard_data()`

3. Write unit tests (pure functions, mocked runtime)

**Deliverables:**
- [ ] `ops/jtbd.py` with all calculations
- [ ] 100% test coverage (pure functions)
- [ ] Performance benchmarks

### Phase 3: Commands Layer (Week 3)

**Goal:** Implement CLI interface

**Tasks:**
1. Create `src/specify_cli/commands/jtbd.py`
   - Command definitions
   - Rich formatting
   - Error handling

2. Implement commands:
   - `track-job`, `track-outcome`
   - `dashboard`
   - `export`, `analyze`, `sync`

3. Integration tests

**Deliverables:**
- [ ] `commands/jtbd.py` with full CLI
- [ ] Rich table/JSON output
- [ ] E2E integration tests

### Phase 4: RDF Integration (Week 4)

**Goal:** Sync RDF specs to metric store

**Tasks:**
1. Extend `sync_rdf_specs()` to parse JTBD ontologies
2. Create SPARQL queries for metadata extraction
3. Update ggen.toml with JTBD transformations

**Deliverables:**
- [ ] RDF metadata sync working
- [ ] SPARQL queries for jobs/outcomes
- [ ] Generated JTBD reports

### Phase 5: Documentation & Polish (Week 5)

**Goal:** Complete documentation and examples

**Tasks:**
1. Write user documentation
2. Create example RDF specs
3. Add usage examples to README
4. Performance optimization

**Deliverables:**
- [ ] User guide in `docs/JTBD_GUIDE.md`
- [ ] Example specs in `examples/jtbd/`
- [ ] README updated
- [ ] Performance < 100ms for dashboard

---

## Success Metrics

### System Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Dashboard load time | < 100ms | `specify jtbd dashboard` execution time |
| Storage write latency | < 10ms | Time to `store_job_completion()` |
| Query response time | < 50ms | Time to `query_jobs()` with filters |
| OTEL overhead | < 5% | Instrumented vs non-instrumented command time |
| Cache hit rate | > 80% | Cache hits / total queries |

### Data Quality

| Metric | Target | Validation |
|--------|--------|------------|
| Job completion accuracy | 100% | All completed jobs have duration |
| Outcome tracking coverage | > 90% | Features with outcome tracking / total features |
| Painpoint resolution rate | Track | Painpoints resolved / painpoints reported |
| RDF sync consistency | 100% | RDF metadata matches source TTL files |

### User Adoption

| Metric | Target | Measurement |
|--------|--------|-------------|
| JTBD commands usage | > 10/day | OTEL command count |
| Dashboard views | > 50/week | Dashboard command count |
| Export frequency | > 5/week | Export command count |

---

## References

### Internal Documentation

- [Constitutional Equation](/Users/sac/ggen-spec-kit/docs/CONSTITUTIONAL_EQUATION.md)
- [Three-Tier Architecture](/Users/sac/ggen-spec-kit/CLAUDE.md#architecture)
- [JTBD Core Module](/Users/sac/ggen-spec-kit/src/specify_cli/core/jtbd_metrics.py)
- [JTBD Schema](/Users/sac/ggen-spec-kit/ontology/jtbd-schema.ttl)

### External References

- [Jobs-to-be-Done Framework](https://jobs-to-be-done.com/)
- [Outcome-Driven Innovation](https://strategyn.com/outcome-driven-innovation/)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [SHACL Validation](https://www.w3.org/TR/shacl/)

---

**Document Status:** Ready for Implementation
**Next Steps:** Begin Phase 1 implementation
**Review Date:** 2026-01-21
