# specify spiff

SpiffWorkflow integration for business process execution and automation.

## Usage

```bash
specify spiff [SUBCOMMAND] [OPTIONS]
```

## Description

The `spiff` command integrates SpiffWorkflow for executing business processes defined in BPMN 2.0. It:
- Runs workflow processes
- Manages process state and variables
- Handles human tasks and decisions
- Generates execution logs for analysis
- Integrates with pm4py for process mining

## Subcommands

### run

Execute a workflow process.

```bash
specify spiff run WORKFLOW_FILE [OPTIONS]
```

**Options:**
- `--data FILE` - Input data (JSON, YAML, CSV)
- `--save-log` - Save execution trace for analysis
- `--debug` - Show execution details
- `--timeout SECONDS` - Execution timeout

**Example:**
```bash
specify spiff run workflow.bpmn \
  --data input.json \
  --save-log execution.xes

✓ Workflow execution started
  Starting task: Process Data
  ✓ Process Data completed (2.1s)
  ✓ Validate Data completed (1.3s)
  → Waiting for human task: Review Results

# User completes Review Results task
  ✓ Review Results completed (15.2s)
  ✓ Save Results completed (0.8s)

✓ Workflow completed successfully
  Total duration: 19.4s
  Execution log saved to execution.xes
```

### list

List available workflows.

```bash
specify spiff list [OPTIONS]
```

Shows all BPMN files and their details:

```bash
specify spiff list

Available Workflows:

1. data-processing.bpmn
   Version: 1.2
   Tasks: 8 (6 automatic, 2 manual)
   Last modified: 2025-12-23 14:30

2. report-generation.bpmn
   Version: 2.0
   Tasks: 12 (10 automatic, 2 manual)
   Last modified: 2025-12-20 10:15

3. data-validation.bpmn
   Version: 0.9
   Tasks: 5 (5 automatic, 0 manual)
   Last modified: 2025-12-15 09:00
```

### validate

Validate BPMN 2.0 syntax and structure.

```bash
specify spiff validate WORKFLOW_FILE
```

Checks for common BPMN issues:

```bash
specify spiff validate workflow.bpmn

✓ Validation passed

BPMN Structure:
  Start events: 1
  End events: 1
  Tasks: 8
  Gateways: 2
  Data objects: 3

Checks:
  ✓ All sequences have source and target
  ✓ All tasks have descriptive names
  ✓ All gateways have conditions
  ✓ All data inputs/outputs defined
  ⚠ Task 'Manual Review' has no timeout (might block)
```

### execute

Execute workflow with custom options.

```bash
specify spiff execute WORKFLOW_FILE [OPTIONS]
```

Enhanced version of `run` with advanced controls:

**Options:**
- `--variable KEY=VALUE` - Set workflow variables
- `--parallel` - Allow parallel task execution
- `--save-state FILE` - Save workflow state for recovery
- `--resume STATE_FILE` - Resume from saved state

**Example:**
```bash
specify spiff execute workflow.bpmn \
  --variable user="alice" \
  --variable environment="production" \
  --save-state workflow-state.json

✓ Execution started with variables:
  user: alice
  environment: production
```

### task

Manage human workflow tasks.

```bash
specify spiff task [ACTION] [OPTIONS]
```

**Actions:**

**list** - Show pending human tasks:
```bash
specify spiff task list
✓ Pending tasks:
  1. Review Data Quality Results (assigned to: alice)
  2. Approve Report Distribution (assigned to: manager)
```

**assign** - Assign task to user:
```bash
specify spiff task assign 1 --user bob
✓ Task 1 assigned to bob
```

**complete** - Complete human task:
```bash
specify spiff task complete 1 --outcome approved
✓ Task 1 completed
  Outcome: approved
  Next step: Email stakeholders
```

**claim** - Claim task:
```bash
specify spiff task claim 1
✓ Task 1 claimed by alice
```

### state

Inspect workflow state.

```bash
specify spiff state WORKFLOW_ID [OPTIONS]
```

Shows current process state:

```bash
specify spiff state workflow-123

Workflow State:

Status: IN_PROGRESS
Current task: Validate Results
Progress: 5 of 8 tasks completed

Variables:
  input_file: /data/input.csv
  record_count: 1,450
  validation_errors: 23

Data Flow:
  [✓] Process Data
  [✓] Validate Data
  [✓] Clean Data
  [→] Validate Results (ACTIVE)
  [ ] Save Results
  [ ] Email Stakeholders
```

### history

Show execution history.

```bash
specify spiff history WORKFLOW_ID
```

Timeline of completed tasks:

```bash
specify spiff history workflow-123

Execution Timeline:

14:30:00 - Process Data (2.1s)
14:30:02 - Validate Data (1.3s)
14:30:04 - Clean Data (3.2s)
14:30:07 - Validate Results (1.5s)
  ↳ 23 validation errors detected
  ↳ Invalid records moved to error queue
14:30:08 - [WAITING] Review Results (human task)

User alice completed task at 14:45:30
  Decision: approved_with_warnings
  Comment: "Data looks good, proceed"
```

### export-log

Export execution trace for process mining.

```bash
specify spiff export-log WORKFLOW_ID [OPTIONS]
```

**Options:**
- `--format` - XES (default), CSV, JSON
- `--output FILE` - Output file path

**Example:**
```bash
specify spiff export-log workflow-123 --output execution.xes

✓ Exported execution log
  Format: XES (process mining)
  Events: 47
  Duration: 19.4 seconds
  Saved to execution.xes

# Now analyze with pm
specify pm analyze execution.xes
```

## Examples

### Simple Workflow Execution

```bash
# Define workflow in BPMN (workflow.bpmn)
# Create input data
cat > input.json << 'EOF'
{
  "records": [
    {"id": 1, "value": 100},
    {"id": 2, "value": 200}
  ]
}
EOF

# Execute
specify spiff run workflow.bpmn \
  --data input.json \
  --save-log log.xes

# Analyze execution
specify pm analyze log.xes
```

### Workflow with Human Tasks

```bash
# Start workflow
specify spiff run workflow.bpmn --data input.json

# Check pending tasks
specify spiff task list
# Shows: "Review Results (assigned to: alice)"

# Alice completes task
specify spiff task complete 1 --outcome approved

# Continue execution
specify spiff task list
# Shows: "Approve Report (assigned to: manager)"

# Manager approves
specify spiff task complete 2 --outcome approved

# Workflow completes
```

### Process Optimization

```bash
# Execute workflow and capture log
specify spiff run data-pipeline.bpmn --save-log v1.xes

# Analyze current performance
specify pm analyze v1.xes

# Identify bottlenecks
specify pm bottleneck v1.xes

# Optimize BPMN (parallel tasks, etc.)
vim data-pipeline.bpmn

# Re-execute and compare
specify spiff run data-pipeline.bpmn --save-log v2.xes
specify pm compare v1.xes v2.xes
# Shows improvement metrics
```

### Integration with ggen

```bash
# Define workflow in RDF spec
cat > ontology/workflows.ttl << 'EOF'
@prefix wf: <http://ggen-spec-kit.org/workflow#> .

wf:DataPipeline
    a wf:Workflow ;
    rdfs:label "Data Pipeline" ;
    wf:bpmnSource "workflow.bpmn" ;
    wf:generateCommand true .
EOF

# Generate command for workflow
specify ggen sync

# Now have a 'specify pipeline' command
# that wraps the workflow
specify pipeline --input data.csv
```

## BPMN Integration

### Creating Workflows

Use BPMN 2.0 editor (e.g., Camunda Modeler):
1. Define start event
2. Add tasks (service tasks for automation, user tasks for people)
3. Add decision gates
4. Connect to end event
5. Save as workflow.bpmn

### Task Types

- **Service Task** - Automated (calls code/API)
- **User Task** - Human interaction (waits for decision)
- **Manual Task** - Documentation
- **Script Task** - Execute script

### Gateways

- **Exclusive** - Only one path (if-then-else)
- **Parallel** - All paths execute
- **Inclusive** - Multiple paths (complex)
- **Event-based** - Triggered by events

## Error Handling

```bash
# Execution fails with error
specify spiff run workflow.bpmn --data input.json
✗ Execution failed: Task "Save Results" failed

Error Details:
  Task: Save Results
  Error: Database connection timeout
  Reason: Postgres unavailable

# Check state
specify spiff state workflow-123
# Shows: FAILED, task details

# Fix issue and resume
# (after fixing database)
specify spiff execute workflow.bpmn \
  --resume workflow-state.json

# Continues from where it failed
```

## Performance Monitoring

```bash
# Execute with logging
specify spiff run workflow.bpmn \
  --save-log execution.xes \
  --debug

# Analyze performance
specify pm analyze execution.xes
# Shows: bottlenecks, throughput, variance

# Identify slow tasks
specify pm bottleneck execution.xes
# Shows which tasks take longest

# Improve and re-test
```

## See Also

- [pm.md](./pm.md) - Process mining (analyzes workflow executions)
- `/docs/guides/workflow/` - Workflow how-to guides
- `/docs/reference/bpmn-reference.md` - BPMN syntax reference
- [Tutorial 11: Workflow Automation](../tutorials/11-workflow-automation.md) - Learning guide
