# Tutorial 11: Workflow Automation with SpiffWorkflow

Automate business processes using BPMN 2.0 workflows with SpiffWorkflow integration.

**Duration:** 35 minutes
**Prerequisites:** Tutorial 1 (getting-started)
**Difficulty:** Advanced

## Learning Goals

- Design BPMN 2.0 workflows
- Execute workflows with SpiffWorkflow
- Handle human tasks and decisions
- Monitor workflow execution
- Analyze performance with process mining

## Part 1: Create Your First Workflow

### Design BPMN Process

Create a simple data processing workflow:

```
Start → Read Data → Validate → (Decision) → Save/Reject → End
                                   ↓
                              Manual Review (human task)
```

### Build BPMN File

Use Camunda Modeler or create manually:

```bash
cat > data-pipeline.bpmn << 'EOF'
<?xml version="1.0"?>
<bpmn2:definitions>
  <bpmn2:process id="DataPipeline">
    <!-- Start -->
    <bpmn2:startEvent id="start" name="Start"/>

    <!-- Read data -->
    <bpmn2:serviceTask id="read_data"
      name="Read Data Files"
      implementation="python:src.ops.read_data"/>

    <!-- Validate -->
    <bpmn2:serviceTask id="validate"
      name="Validate Data"
      implementation="python:src.ops.validate_data"/>

    <!-- Decision: valid?  -->
    <bpmn2:exclusiveGateway id="valid_decision"
      name="Data Valid?"/>

    <!-- Human review (invalid data) -->
    <bpmn2:userTask id="manual_review"
      name="Review Data Issues"/>

    <!-- Save (valid) -->
    <bpmn2:serviceTask id="save"
      name="Save Processed Data"
      implementation="python:src.ops.save_data"/>

    <!-- End -->
    <bpmn2:endEvent id="end" name="Complete"/>

    <!-- Sequences -->
    <bpmn2:sequenceFlow sourceRef="start" targetRef="read_data"/>
    <bpmn2:sequenceFlow sourceRef="read_data" targetRef="validate"/>
    <bpmn2:sequenceFlow sourceRef="validate" targetRef="valid_decision"/>

    <bpmn2:sequenceFlow
      sourceRef="valid_decision" targetRef="save"
      name="Valid"
      conditionExpression="data.is_valid"/>

    <bpmn2:sequenceFlow
      sourceRef="valid_decision" targetRef="manual_review"
      name="Invalid"
      conditionExpression="not data.is_valid"/>

    <bpmn2:sequenceFlow sourceRef="save" targetRef="end"/>
    <bpmn2:sequenceFlow sourceRef="manual_review" targetRef="end"/>
  </bpmn2:process>
</bpmn2:definitions>
EOF
```

## Part 2: Execute Workflow

### Prepare Input Data

```bash
cat > input.json << 'EOF'
{
  "files": [
    "/data/file1.csv",
    "/data/file2.csv",
    "/data/file3.csv"
  ],
  "validation_rules": {
    "require_headers": true,
    "min_rows": 10
  }
}
EOF
```

### Run Workflow

```bash
# Execute workflow
specify spiff run data-pipeline.bpmn \
  --data input.json \
  --save-log execution.xes

✓ Workflow execution started
  Starting task: Read Data

✓ Read Data completed (1.2s)
  Read 3 files successfully

✓ Validate Data completed (2.3s)
  Found 2 validation issues

→ Waiting for human task: Review Data Issues
```

## Part 3: Handle Human Tasks

### Check Pending Tasks

```bash
# See what's waiting for human input
specify spiff task list

Pending tasks:

1. Review Data Issues
   Status: Pending
   Assigned to: (unassigned)
   Description: Review validation issues found in data
   Context:
     - Files: 3
     - Valid: 2
     - Issues: 5 (missing headers, low row count)

2. [None - waiting on task 1]
```

### Complete Human Task

```bash
# Assign task to analyst
specify spiff task assign 1 --user alice

✓ Task 1 assigned to alice

# Alice reviews and completes
specify spiff task complete 1 \
  --outcome "approved_with_caveats" \
  --comment "Files look good, proceed with caution on file 3"

✓ Task completed by alice
  Decision: approved_with_caveats
  Comment: Files look good, proceed with caution on file 3

→ Continuing workflow...
✓ Save Processed Data completed (0.8s)
  Saved 3 files to /output/

✓ Workflow completed successfully!
  Total duration: 5.3 seconds
  Status: SUCCESS
```

## Part 4: Inspect Workflow State

### View Current State

```bash
# Check workflow progress
specify spiff state data-pipeline-123

Workflow State:

Status: IN_PROGRESS (waiting for human task)
Current task: Review Data Issues
Progress: 3 of 6 steps completed (50%)

Variables:
  files_read: 3
  files_valid: 2
  validation_errors: 5
  analyst_assigned: alice
  analyst_decision: (awaiting)

Data:
  input_files: [file1.csv, file2.csv, file3.csv]
  validation_results: {
    "file1.csv": "pass",
    "file2.csv": "pass",
    "file3.csv": "fail - 8 rows"
  }

Timeline:
  [✓] Start (2025-12-23 14:30:00)
  [✓] Read Data (14:30:01 - 14:30:02)
  [✓] Validate Data (14:30:02 - 14:30:04)
  [→] Manual Review (14:30:04 - awaiting...)
  [ ] Save Data (pending)
  [ ] End (pending)
```

## Part 5: Monitor Execution

### View History

```bash
# See completed steps
specify spiff history data-pipeline-123

Execution Timeline:

14:30:00 - Start process
14:30:01 - Read Data Files
  Input: 3 files
  Output: Data read successfully

14:30:02 - Validate Data
  Checks: Headers, Row count, Type validation
  Issues found: 5

14:30:04 - Manual Review
  Task waiting for: alice

  [Alice reviews at 14:45:30]
  Decision: Approved with caveats
  Comment: "Files look good, proceed with caution"

[Workflow continues if approved]
```

### Track Performance

```bash
# Get execution metrics
specify pm analyze execution.xes

Process Metrics:

Activities:
  Read Data: 1.2 seconds
  Validate Data: 2.3 seconds
  Manual Review: 15 minutes 26 seconds ← Human time!
  Save Data: 0.8 seconds

Timing:
  Total workflow time: 15 minutes 32 seconds
  Automated work: 4.3 seconds
  Human waiting/work: 15 minutes 28 seconds

Insight: 99.5% of time is human task!
(This is normal for workflows with human review)
```

## Part 6: Parallel Workflows

### Multiple Concurrent Workflows

```bash
# Run multiple instances
for i in 1 2 3; do
  specify spiff run data-pipeline.bpmn \
    --data "input-$i.json" \
    --save-log "execution-$i.xes" &
done

wait  # Wait for all to complete

# Analyze together
specify pm analyze execution-*.xes

Process Statistics:
  Total workflows: 3
  Successful: 3 (100%)
  Failed: 0
  Avg duration: 15.4 minutes
  Throughput: 0.19 workflows/hour
```

## Part 7: Advanced: Decision Logic

### Complex Workflows with Decisions

```bash
cat > complex-pipeline.bpmn << 'EOF'
<?xml version="1.0"?>
<bpmn2:definitions>
  <bpmn2:process id="ComplexPipeline">
    <!-- ... start and read tasks ... -->

    <!-- Quality check -->
    <bpmn2:exclusiveGateway id="quality_check"
      name="Quality OK?"/>

    <!-- Different paths based on quality -->
    <bpmn2:serviceTask id="fast_save"
      name="Save (Fast Path)"
      implementation="python:src.ops.save_data"/>

    <bpmn2:serviceTask id="deep_analysis"
      name="Deep Analysis"
      implementation="python:src.ops.analyze"/>

    <bpmn2:serviceTask id="slow_save"
      name="Save (After Analysis)"
      implementation="python:src.ops.save_data"/>

    <!-- Conditions -->
    <bpmn2:sequenceFlow
      sourceRef="quality_check" targetRef="fast_save"
      name="Good (>95%)"
      conditionExpression="quality_score > 0.95"/>

    <bpmn2:sequenceFlow
      sourceRef="quality_check" targetRef="deep_analysis"
      name="Fair (70-95%)"
      conditionExpression="0.70 &lt; quality_score &lt;= 0.95"/>

    <bpmn2:sequenceFlow
      sourceRef="deep_analysis" targetRef="slow_save"/>

    <!-- ... convergence to end ... -->
  </bpmn2:process>
</bpmn2:definitions>
EOF
```

**Execution variations:**
```
High quality (>95%):
  Read → Validate → Check → Save [Fast] → End
  (5 seconds)

Medium quality (70-95%):
  Read → Validate → Check → Analysis → Save [Slow] → End
  (60+ seconds)

Low quality (<70%):
  Read → Validate → Check → [Reject] → End
  (Manual intervention)
```

## Part 8: Error Handling

### Workflow Error Recovery

```bash
# Run workflow with error
specify spiff run data-pipeline.bpmn \
  --data bad-input.json

✗ Error in task: Read Data Files
  Error: File /data/missing.csv not found
  Attempting recovery...

[Recovery options]
1. Retry (run failed task again)
2. Skip (continue without this file)
3. Abort (stop workflow)

Recommendation: Retry with corrected input

# Fix and retry
specify spiff recover data-pipeline-123 \
  --action retry \
  --data "input-fixed.json"

✓ Workflow recovered and resumed
  From: Read Data Files
  Duration: 1.2 seconds
  Status: Continuing...

✓ Workflow completed successfully
```

## Summary

**BPMN Workflows:** Executable business process models
**Service Tasks:** Automated operations (Python code)
**User Tasks:** Human decision points
**Gateways:** Conditional branching
**Sequence Flows:** Define process flow
**Execution:** Run workflows with SpiffWorkflow
**Monitoring:** Track progress and performance
**Analytics:** Analyze with process mining

## Common Patterns

| Pattern | Use Case | Example |
|---------|----------|---------|
| Sequential | One step after another | Read → Validate → Save |
| Parallel | Multiple concurrent paths | [Task1 & Task2] → Merge |
| Decision | Conditional branching | If valid → Path A, else Path B |
| Loop | Repeat until condition | Retry failed step |
| Escalation | Timeouts/hand-offs | Wait 1 hour, escalate to manager |

## See Also

- `/docs/commands/spiff.md` - spiff command reference
- [pm.md](../commands/pm.md) - Process mining analysis
- `/docs/guides/workflow/` - Workflow guides
- BPMN 2.0 spec: https://www.bpmn.org/
