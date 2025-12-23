# CLI Commands Reference

Complete documentation for all `specify` CLI commands, organized by category.

## Command Categories

### Core Commands
- **[init](./init.md)** - Initialize a new ggen spec-kit project
- **[check](./check.md)** - Verify that required tools are available
- **[version](./version.md)** - Display version information

### RDF & Specification Commands
- **[ggen](./ggen.md)** - RDF specification generation and transformation (umbrella command)

### Advanced Features
- **[hd](./hd.md)** - Hyperdimensional computing operations
- **[hdql](./hdql.md)** - Hyperdimensional Query Language interpreter
- **[pm](./pm.md)** - Process mining and workflow analysis
- **[spiff](./spiff.md)** - SpiffWorkflow engine integration
- **[jtbd](./jtbd.md)** - Jobs-to-be-Done framework utilities
- **[dashboards](./dashboards.md)** - Visualization and dashboard tools
- **[generated](./generated.md)** - Manage and inspect generated files

---

## Quick Reference

| Command | Purpose | Use When |
|---------|---------|----------|
| `init` | Create new project | Starting a new ggen spec-kit project |
| `check` | Verify tools | Troubleshooting environment setup |
| `ggen` | Transform RDF | Editing specifications and regenerating code |
| `hd` | Semantic computing | Working with hyperdimensional spaces |
| `hdql` | HD queries | Querying semantic knowledge bases |
| `pm` | Process analysis | Understanding workflow execution |
| `spiff` | Workflows | Running workflow automation |
| `jtbd` | Job mapping | Defining user jobs and outcomes |
| `dashboards` | Visualization | Viewing metrics and insights |
| `generated` | File management | Inspecting/managing generated artifacts |
| `version` | Version info | Checking ggen spec-kit version |

---

## Command Structure

All commands follow this pattern:

```bash
specify [COMMAND] [SUBCOMMAND] [OPTIONS] [ARGUMENTS]
```

### Global Options

Available on all commands:

```bash
specify [COMMAND] \
  -v, --verbose          # Verbose output (show more details)
  -q, --quiet            # Quiet mode (suppress output)
  --config PATH          # Path to config file
  --profile PROFILE      # Config profile to use
  -h, --help            # Show help for command
```

---

## Examples by Task

### Task: Start a New Project
```bash
specify init my-awesome-project
```
See: [init.md](./init.md)

### Task: Regenerate Code from Specifications
```bash
specify ggen sync
```
See: [ggen.md](./ggen.md)

### Task: Check Everything is Set Up Correctly
```bash
specify check
```
See: [check.md](./check.md)

### Task: Explore Semantic Knowledge
```bash
specify hd query "What is red?"
specify hdql execute "SELECT ?color WHERE { ?obj IS_COLOR ?color }"
```
See: [hd.md](./hd.md), [hdql.md](./hdql.md)

### Task: Analyze Workflow Execution
```bash
specify pm analyze workflow.xml
```
See: [pm.md](./pm.md)

### Task: Run Workflow
```bash
specify spiff run workflow.bpmn
```
See: [spiff.md](./spiff.md)

### Task: Map Jobs-to-be-Done
```bash
specify jtbd map --user "data analyst"
```
See: [jtbd.md](./jtbd.md)

### Task: View Dashboards
```bash
specify dashboards open metrics
```
See: [dashboards.md](./dashboards.md)

### Task: Inspect Generated Files
```bash
specify generated list
specify generated verify
```
See: [generated.md](./generated.md)

---

## Getting Help

### Help for a Command
```bash
specify [COMMAND] --help
```

### Help for a Subcommand
```bash
specify [COMMAND] [SUBCOMMAND] --help
```

### Examples
```bash
# Show help for ggen command
specify ggen --help

# Show help for ggen sync subcommand
specify ggen sync --help

# Show help for hd query subcommand
specify hd query --help
```

---

## Exit Codes

Commands return standard exit codes:

| Code | Meaning | Example |
|------|---------|---------|
| 0 | Success | Command completed without errors |
| 1 | General error | Validation failed, file not found |
| 2 | Invalid arguments | Wrong argument type or missing required arg |
| 3 | Configuration error | Config file missing or invalid |
| 4 | Environment error | Required tool not available |
| 5 | Processing error | Error during execution |

---

## Shell Completion

Enable tab-completion for bash/zsh:

```bash
# Bash
specify --install-completion bash
source ~/.bashrc

# Zsh
specify --install-completion zsh
source ~/.zshrc

# Fish
specify --install-completion fish
source ~/.config/fish/config.fish
```

Then use:
```bash
specify [TAB]           # List all commands
specify init [TAB]      # List init options
```

---

## See Also

- `/docs/guides/` - How-to guides for common tasks
- `/docs/reference/cli-commands.md` - Alternative reference format
- `/docs/tutorials/` - Learning the CLI step by step
- `/docs/explanation/` - Understanding how commands work
