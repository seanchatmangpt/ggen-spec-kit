# specify version

Display version information for ggen spec-kit and installed components.

## Usage

```bash
specify version [OPTIONS]
```

## Description

The `version` command shows:
- Specify CLI version
- ggen transformation engine version
- Python version
- Installed optional components
- Dependency versions

## Options

### --verbose, -v
**Type:** Flag

Show detailed version information:

```bash
$ specify version --verbose
Specify CLI: 0.8.2
  Location: /usr/local/bin/specify
  Python: 3.12.0
  Edition: Full (all features)

ggen: 5.0.2
  Status: Ready

Components:
  typer: 0.9.2 (CLI framework)
  rich: 13.5.2 (Terminal output)
  httpx: 0.25.0 (HTTP client)
  platformdirs: 4.0.0 (Config directories)
  readchar: 4.0.1 (Terminal input)

Optional Components:
  pm4py: 2.7.0 (Process mining) ✓
  spiffworkflow: 1.2.1 (Workflow engine) ✓
  opentelemetry-sdk: 1.20.0 (Observability) ✓

System:
  OS: Linux 5.15.0 (Ubuntu 22.04)
  Architecture: x86_64
  Python executable: /usr/bin/python3
  Home directory: /home/user

License: Apache-2.0
```

### --json
**Type:** Flag

Output in JSON format (for scripting):

```bash
$ specify version --json
{
  "specify": "0.8.2",
  "ggen": "5.0.2",
  "python": "3.12.0",
  "components": {
    "typer": "0.9.2",
    "rich": "13.5.2"
  },
  "optional_components": {
    "pm4py": "2.7.0",
    "spiffworkflow": "1.2.1",
    "opentelemetry_sdk": "1.20.0"
  },
  "system": {
    "os": "linux",
    "python_executable": "/usr/bin/python3"
  }
}
```

### --check UPDATE
**Type:** Flag

Check for available updates:

```bash
$ specify version --check
Specify CLI: 0.8.2
✓ Latest version (no update available)

ggen: 5.0.2
✓ Latest version (no update available)

Optional components:
  ⚠ pm4py: 2.7.0 (update available: 2.8.0)
    Install: uv sync --upgrade pm4py

All up to date!
```

### --short, -s
**Type:** Flag

Show only version numbers:

```bash
$ specify version --short
specify 0.8.2
ggen 5.0.2
python 3.12.0
```

## Examples

### Quick Version Check
```bash
$ specify version
Specify CLI 0.8.2
```

### Detailed Information
```bash
$ specify version --verbose
# Shows everything (see above)
```

### For Scripting
```bash
# Get version as JSON
VERSION=$(specify version --json | jq -r '.specify')

# Check if version is specific value
specify version --json | jq '.specify == "0.8.2"'

# Check Python version
specify version --json | jq '.python' -r
# 3.12.0
```

### Check for Updates
```bash
$ specify version --check
# Shows available updates (if any)

# In CI/CD pipeline
if specify version --check | grep -q "update available"; then
  echo "Updates available"
  exit 1  # Fail to prompt update
fi
```

### Verify Installation
```bash
$ specify version --verbose

# Check everything is installed correctly
# All components should show version numbers
# Optional components show ✓ if installed
```

## Output Formats

### Default (Short)
```
Specify CLI 0.8.2
```

### Verbose
```
Specify CLI: 0.8.2
ggen: 5.0.2
Python: 3.12.0
Edition: Full
[... more details ...]
```

### JSON
```json
{
  "specify": "0.8.2",
  "ggen": "5.0.2",
  ...
}
```

### Short
```
specify 0.8.2
ggen 5.0.2
python 3.12.0
```

## Version Scheme

Specify follows semantic versioning: MAJOR.MINOR.PATCH

- **MAJOR** - Breaking changes
- **MINOR** - New features (backward compatible)
- **PATCH** - Bug fixes

Example:
- 0.8.2 - Version 0, minor version 8, patch version 2

## Release Channels

Specify can track different release channels:

```bash
# Current channel (default, stable)
specify --channel current

# Latest channel (cutting edge)
specify --channel latest

# LTS channel (long-term support)
specify --channel lts
```

Check your channel:
```bash
$ specify version --verbose | grep -i channel
Edition: Full (current - stable release)
```

## Troubleshooting

### Version Mismatch
```bash
$ specify version
Specify CLI 0.8.2

$ ggen --version
ggen 5.0.2

# Both should be compatible
# Check documentation for compatibility matrix
```

### Missing Components
```bash
$ specify version --verbose
...
Optional Components:
  pm4py: NOT INSTALLED
  spiffworkflow: NOT INSTALLED
...

# Install if needed:
uv sync --group pm      # For process mining
uv sync --group wf      # For workflows
uv sync --group all     # For everything
```

## See Also

- [check.md](./check.md) - Verify environment setup
- `/docs/guides/setup/` - Installation guides
- `/docs/reference/` - Version compatibility matrix
