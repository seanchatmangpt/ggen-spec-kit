# specify dashboards

Visualization and analytics dashboards for metrics, traces, and process insights.

## Usage

```bash
specify dashboards [SUBCOMMAND] [OPTIONS]
```

## Description

The `dashboards` command provides interactive web-based dashboards for:
- OpenTelemetry traces and metrics
- Process mining analytics
- JTBD satisfaction metrics
- Build/test results
- System performance
- Custom metrics

## Subcommands

### open

Open a dashboard in browser.

```bash
specify dashboards open [DASHBOARD_NAME] [OPTIONS]
```

**Available Dashboards:**
- `metrics` - OTEL metrics and performance
- `traces` - Distributed trace visualization
- `processes` - Process mining analytics
- `jtbd` - Jobs-to-be-Done satisfaction
- `builds` - CI/CD build status
- `system` - System health and resources
- `custom` - Custom dashboard

**Options:**
- `--port PORT` - Server port (default: 8080)
- `--backend URL` - Backend service URL (for metrics/traces)
- `--read-only` - Disable modifications
- `--dark-mode` - Use dark theme

**Example:**
```bash
specify dashboards open metrics --port 8080
✓ Dashboard started on http://localhost:8080
  Press Ctrl+C to stop
```

### list

List available dashboards and their status.

```bash
specify dashboards list [OPTIONS]
```

Shows available and configured dashboards:

```bash
specify dashboards list

Available Dashboards:

✓ metrics
  Connected to: Prometheus (http://localhost:9090)
  Status: LIVE
  Metrics: 47

⚠ traces
  Connected to: Jaeger (http://localhost:16686)
  Status: LIVE (with warnings)
  Traces: 1,245

✓ processes
  Connected to: Event log (events.xes)
  Status: READY
  Events: 5,632

○ jtbd
  Not configured
  Recommendation: Run 'specify jtbd report' first
```

### create

Create custom dashboard.

```bash
specify dashboards create DASHBOARD_NAME [OPTIONS]
```

Create new dashboard with custom layout:

**Options:**
- `--from-template` - Start from template
- `--width, --height` - Dashboard dimensions
- `--description` - Dashboard description

**Example:**
```bash
specify dashboards create data-quality \
  --description "Data quality metrics for ingestion pipeline"

✓ Created dashboard: data-quality
  Edit at: .dashboards/data-quality.json
```

### edit

Edit dashboard configuration.

```bash
specify dashboards edit DASHBOARD_NAME [OPTIONS]
```

Launch editor to customize dashboard:

```bash
specify dashboards edit metrics --editor vim

# Opens editor for dashboard configuration
# Add/remove widgets, configure colors, etc.
```

### add-widget

Add widget to dashboard.

```bash
specify dashboards add-widget DASHBOARD_NAME WIDGET_TYPE [OPTIONS]
```

**Widget Types:**
- `metric` - Single metric display
- `chart` - Time series graph
- `gauge` - Gauge display
- `heatmap` - Heatmap visualization
- `histogram` - Distribution chart
- `text` - Text block
- `table` - Data table

**Example:**
```bash
specify dashboards add-widget metrics metric \
  --title "Ggen Sync Duration" \
  --metric "ggen.sync.duration_ms" \
  --aggregation avg \
  --threshold 5000 critical

✓ Added widget to metrics dashboard
```

### export

Export dashboard data or configuration.

```bash
specify dashboards export DASHBOARD_NAME [OPTIONS]
```

**Options:**
- `--format` - Format (json, yaml, png, pdf, html)
- `--output FILE` - Output file path
- `--include-data` - Include current data (for snapshots)

**Example:**
```bash
specify dashboards export metrics --format html --output report.html

✓ Exported metrics dashboard
  Format: HTML (static, no data)
  Saved to: report.html

# Or with data snapshot
specify dashboards export metrics --format html --include-data --output snapshot.html
✓ HTML report created with current data
```

### share

Generate shareable dashboard link.

```bash
specify dashboards share DASHBOARD_NAME [OPTIONS]
```

Creates public/temporary link:

**Options:**
- `--read-only` - Read-only access
- `--expiry DURATION` - Link expiration (e.g., "7d", "24h")
- `--password` - Require password

**Example:**
```bash
specify dashboards share metrics --expiry 7d --read-only

✓ Share link created (expires in 7 days):
  https://dashboards.example.com/share/abc123xyz
  Read-only: Yes
```

### delete

Delete dashboard.

```bash
specify dashboards delete DASHBOARD_NAME
```

## Dashboard Types

### Metrics Dashboard

Shows system performance metrics:

```
┌─────────────────────────────────────────┐
│  Metrics Dashboard                      │
├─────────────────────────────────────────┤
│                                         │
│  Ggen Sync Duration       Throughput   │
│  ┌──────────────────┐    ┌─────────────┐
│  │ 2.1s avg        │    │ 45 ops/min  │
│  │ ↑ +12% vs week  │    │ ↓ -5% trend │
│  └──────────────────┘    └─────────────┘
│                                         │
│  Command Execution Rate                 │
│  ┌─────────────────────────────────────┐
│  │ ╭╮╭╮╭╮  60                          │
│  │ │││││││  50                          │
│  │ ╰╯╰╯╰╯  40 commands/minute         │
│  │                                     │
│  │  Time: [Yesterday] → [Today]        │
│  └─────────────────────────────────────┘
│                                         │
│  Error Rate                 Success Rate│
│  ┌──────────────────┐    ┌──────────────┐
│  │ 0.5%            │    │ 99.5%        │
│  │ ↓ Improving     │    │ ↑ Excellent  │
│  └──────────────────┘    └──────────────┘
│                                         │
└─────────────────────────────────────────┘
```

### Traces Dashboard

Shows execution traces from Jaeger/OTEL:

```
┌─────────────────────────────────────────┐
│  Distributed Traces                     │
├─────────────────────────────────────────┤
│ [Filter] [Search] [Time range]          │
│                                         │
│ ggen_sync [2.3ms] ✓                     │
│ └─ normalize [0.2ms] ✓                  │
│ └─ extract [0.5ms] ✓                    │
│ └─ emit [1.5ms] ⚠ (slow)               │
│    └─ render_command.tera [0.8ms]       │
│    └─ render_test.tera [0.7ms]          │
│ └─ canonicalize [0.05ms] ✓              │
│ └─ receipt [0.05ms] ✓                   │
│                                         │
│ [Latest] [Previous traces...]           │
└─────────────────────────────────────────┘
```

### Process Mining Dashboard

Shows workflow analytics:

```
┌─────────────────────────────────────────┐
│  Process Analytics                      │
├─────────────────────────────────────────┤
│                                         │
│  Process Model               Metrics    │
│  ┌─────────────┐            ┌────────┐  │
│  │  [Start]    │            │Throughput│ │
│  │    ↓        │            │70/hour  │  │
│  │  Process    │            │Cycle   │  │
│  │    ↓        │            │8.9s    │  │
│  │  Transform  │ ← BOTTLENECK         │
│  │    ↓        │            │Conform │  │
│  │  Save       │            │78%     │  │
│  │    ↓        │            │        │  │
│  │  [End]      │            └────────┘  │
│  └─────────────┘                        │
│                                         │
└─────────────────────────────────────────┘
```

## Configuration

Dashboards are configured in `.dashboards/`:

```
.dashboards/
├── config.json          # Global configuration
├── metrics.json         # Metrics dashboard config
├── traces.json          # Traces dashboard config
├── processes.json       # Process mining config
└── custom/
    └── data-quality.json  # Custom dashboards
```

Example config:

```json
{
  "metrics": {
    "backend": "prometheus",
    "endpoint": "http://localhost:9090",
    "refresh_interval": 5000,
    "theme": "dark",
    "widgets": [
      {
        "type": "metric",
        "title": "Ggen Sync Duration",
        "query": "avg(ggen_sync_duration_ms)"
      }
    ]
  }
}
```

## Integration Examples

### With Prometheus/OTEL Metrics
```bash
# Metrics collected automatically by instrumentation
# Dashboard queries and displays them
specify dashboards open metrics
# Shows live metrics from Prometheus
```

### With Jaeger Traces
```bash
# Start Jaeger (if not running)
docker-compose up -d jaeger

# Run commands with OTEL enabled
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
specify ggen sync
specify init my-project

# View traces
specify dashboards open traces
# Shows execution timeline in Jaeger UI
```

### With Process Logs
```bash
# Export workflow logs
specify spiff export-log workflow-123 --output trace.xes

# Analyze with process mining
specify pm analyze trace.xes

# View in dashboard
specify dashboards open processes
# Shows process model, bottlenecks, metrics
```

### With JTBD Metrics
```bash
# Collect JTBD satisfaction metrics
specify jtbd satisfaction "Process Data Files" --metrics

# Generate report
specify jtbd report --output jtbd-metrics.json

# View dashboard
specify dashboards open jtbd
# Shows outcome satisfaction over time
```

## Custom Metrics

Add custom metrics to dashboards:

```python
# In your ops code
from specify_cli.core.telemetry import meter

file_counter = meter.create_counter(
    "files.processed",
    description="Total files processed"
)

def process_file(path):
    # ... process file ...
    file_counter.add(1)  # Increment counter
```

Then add widget:
```bash
specify dashboards add-widget custom metric \
  --title "Files Processed" \
  --metric "files.processed"
```

## See Also

- `/docs/guides/observability/setup-otel.md` - OTEL setup
- `/docs/guides/observability/view-traces.md` - Viewing traces
- [pm.md](./pm.md) - Process mining (feeds data to dashboards)
- [spiff.md](./spiff.md) - Workflow execution (generates traces)
