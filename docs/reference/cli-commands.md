# Reference: CLI Commands

Complete reference of all Specify CLI commands.

## Commands

### specify init
Initialize a new Spec Kit project.

**Usage:**
```bash
specify init <project-name> [--ai AGENT] [--script sh|ps] [--no-git]
```

**Options:**
- `--ai` - AI assistant: claude, gemini, copilot, etc.
- `--script` - Script variant: sh (bash/zsh) or ps (PowerShell)
- `--no-git` - Skip git initialization

**Example:**
```bash
specify init my-project --ai claude
```

### specify check
Verify all required tools are installed.

**Usage:**
```bash
specify check [--verbose]
```

**Checks:** git, ggen, uv, python, AI agents

### specify version
Show Specify CLI version and build info.

**Usage:**
```bash
specify version
```

### specify wf
Workflow and batch validation commands.

**Subcommands:**
- `validate` - Validate current project
- `discover-projects` - Find projects in directory
- `batch-validate` - Validate multiple projects

**Usage:**
```bash
specify wf validate
specify wf discover-projects [--path /some/dir]
specify wf batch-validate [--parallel]
```

## Environment Variables

See [Environment Variables Reference](./environment-variables.md)

## Configuration

See [Configuration Files Reference](./config-files.md)

## Error Codes

See [Error Codes Reference](./error-codes.md)
