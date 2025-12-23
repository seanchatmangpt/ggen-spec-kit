# specify check

Verify that all required tools and dependencies are available.

## Usage

```bash
specify check [OPTIONS]
```

## Description

The `check` command verifies system setup by testing:
- Python version and interpreter
- Required Python packages
- Optional tools (git, ggen, black, mypy, pytest)
- Environment configuration
- OpenTelemetry setup (if configured)
- File permissions and access

Returns success (exit 0) if all required tools are available, otherwise provides detailed diagnostics.

## Options

### --verbose, -v
**Type:** Flag

Show detailed output including version numbers:

```bash
$ specify check --verbose
✓ Python 3.12.0 (required: >=3.11)
✓ typer 0.9.2
✓ rich 13.5.2
✓ git 2.42.0
✓ black 23.10.0
✓ mypy 1.6.1
✓ pytest 7.4.3
✓ uv 0.1.5
```

### --output, -o
**Type:** String
**Options:** `text`, `json`, `csv`, `markdown`
**Default:** `text`

Output format:

```bash
# JSON output for parsing
specify check --output json

# CSV for spreadsheets
specify check --output csv

# Markdown for documentation
specify check --output markdown
```

### --category, -c
**Type:** String
**Options:** `all`, `required`, `optional`, `python`, `system`, `otel`
**Default:** `all`

Check specific category:

```bash
# Only Python dependencies
specify check --category python

# Only system tools
specify check --category system

# Only OTEL setup
specify check --category otel
```

### --fail-on-missing
**Type:** Flag
**Default:** true

Exit with error (1) if optional tools missing:

```bash
specify check --fail-on-missing
# Exits with 1 if pytest, black, mypy, or ggen not found

specify check --no-fail-on-missing
# Exits with 0 even if optional tools missing
```

### --config PATH
**Type:** File Path

Check against custom config file:

```bash
specify check --config custom-requirements.toml
```

## Examples

### Quick Check
```bash
$ specify check
✓ Environment check passed
  All required tools available
  Python 3.12.0
  11 packages installed
```

### Verbose Check
```bash
$ specify check --verbose
Checking required tools...
✓ Python 3.12.0 (>=3.11) ✓
✓ typer 0.9.2 ✓
✓ rich 13.5.2 ✓
✓ platformdirs 4.0.0 ✓
✓ httpx 0.25.0 ✓
✓ readchar 4.0.1 ✓

Checking optional tools...
✓ git 2.42.0 ✓
✓ black 23.10.0 ✓
✓ mypy 1.6.1 ✓
✓ ruff 0.1.8 ✓
✓ pytest 7.4.3 ✓
✓ ggen 5.0.2 ✓
✓ uv 0.1.5 ✓

Checking system configuration...
✓ HOME directory accessible
✓ Temporary directory writable
✓ Git configured
✓ Git user name: Alice Smith
✓ Git user email: alice@example.com

Checking OpenTelemetry setup...
⚠ OTEL_SDK not configured (optional, for observability)
  To enable: export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
```

### JSON Output
```bash
$ specify check --output json | jq
{
  "status": "pass",
  "python": {
    "version": "3.12.0",
    "required": ">=3.11",
    "check": true
  },
  "packages": [
    {"name": "typer", "version": "0.9.2", "check": true},
    {"name": "rich", "version": "13.5.2", "check": true}
  ],
  "tools": [
    {"name": "git", "version": "2.42.0", "available": true},
    {"name": "black", "version": "23.10.0", "available": true}
  ],
  "otel": {
    "configured": false,
    "endpoint": null
  }
}
```

### Check Only Python
```bash
$ specify check --category python
✓ Python 3.12.0
✓ 11 packages installed
✓ All required packages available
```

### Check After Environment Change
```bash
# You changed environment variables
$ specify check --category otel
✓ OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
✓ OTEL_EXPORTER_JAEGER_AGENT_HOST=localhost
✓ OTEL_EXPORTER_JAEGER_AGENT_PORT=6831
```

## Output Format

### Text (Default)
```
✓ All checks passed
  Python 3.12.0 (>=3.11)
  11 packages installed
  8 system tools available
  OpenTelemetry optional (not configured)
```

### JSON
Structured data with all details, suitable for CI/CD parsing.

### CSV
Tabular format for spreadsheets:
```
name,version,required,available
Python,3.12.0,>=3.11,true
typer,0.9.2,,true
git,2.42.0,,true
```

### Markdown
Formatted for documentation:
```markdown
# Environment Check

## Python
- Version: 3.12.0 (✓ Required: >=3.11)

## Packages (11 installed)
- typer: 0.9.2
- rich: 13.5.2
...
```

## What Gets Checked

### Required ✓ (Must Pass)
- Python version >=3.11
- typer (CLI framework)
- rich (terminal output)
- platformdirs (config directories)
- httpx (HTTP requests)
- readchar (terminal input)

### Optional ⚠ (Nice to Have)
- git (version control)
- black (code formatter)
- mypy (type checker)
- ruff (linter)
- pytest (testing)
- ggen (RDF transformation)
- uv (dependency management)

### System Configuration
- HOME directory accessible
- Temporary directory writable
- Git installation and configuration
- File permissions

### OpenTelemetry (Optional)
- SDK installation
- Exporter configuration
- Endpoint accessibility
- Agent connectivity

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All required checks passed |
| 1 | Required check failed (tool missing, Python too old, etc.) |
| 2 | Optional tool missing (only if --fail-on-missing) |
| 3 | Configuration error (invalid config file, bad permissions) |

## Troubleshooting

### Python Version Too Old
```bash
$ specify check
✗ Python 2.7.18 is too old (required: >=3.11)

💡 Fix: Install Python 3.11 or later
  https://www.python.org/downloads/
```

### Missing Required Package
```bash
$ specify check
✗ Package 'typer' not found

💡 Fix: Run 'uv sync' to install dependencies
  uv sync
```

### Git Not Configured
```bash
$ specify check --verbose
⚠ Git not configured

💡 Fix: Configure git user
  git config --global user.name "Your Name"
  git config --global user.email "you@example.com"
```

### OTEL Connection Failed
```bash
$ specify check --category otel
⚠ OTEL endpoint unreachable: http://localhost:14250

💡 Fix: Start Jaeger (if using Docker)
  docker-compose up -d jaeger
```

## See Also

- [Getting Started Tutorial](../tutorials/01-getting-started.md)
- [init.md](./init.md) - Initialize new project
- `/docs/guides/observability/setup-otel.md` - OTEL setup
- `/docs/guides/testing/setup-tests.md` - Test setup
