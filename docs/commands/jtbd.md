# specify jtbd

Jobs-to-be-Done framework utilities for user-centric requirement definition and prioritization.

## Usage

```bash
specify jtbd [SUBCOMMAND] [OPTIONS]
```

## Description

The `jtbd` command implements the Jobs-to-be-Done (JTBD) framework for understanding user needs as "jobs" rather than features. JTBD helps:
- Understand what users are trying to accomplish
- Define outcomes more precisely than feature requirements
- Prioritize work based on job importance
- Build user empathy into specifications

## Subcommands

### map

Create a job map for a user persona.

```bash
specify jtbd map USER_TYPE [OPTIONS]
```

**Options:**
- `--job JOB_NAME` - Specific job to map
- `--output FILE` - Save map to file
- `--format` - Format (markdown, json, diagram)

**Example:**
```bash
specify jtbd map "data analyst" --output analyst-jobs.md

✓ Created job map for: data analyst

Job: Process Data Files
  Core job: Take raw data files and transform into analysis-ready formats
  Subprocesses:
    1. Import data from various sources (CSV, JSON, SQL)
    2. Validate data quality
    3. Transform/normalize structures
    4. Export in standard formats

Job: Analyze Patterns
Job: Build Reports
Job: Share Insights
```

### define

Define a specific job with outcomes.

```bash
specify jtbd define JOB_NAME [OPTIONS]
```

**Options:**
- `--actor ROLE` - Who performs job
- `--outcome OUTCOME` - Desired outcome
- `--context SITUATION` - When/where job occurs
- `--constraint CONSTRAINT` - Limitations
- `--save` - Save to specification

**Example:**
```bash
specify jtbd define "Process Data Files" \
  --actor "data analyst" \
  --outcome "data ready for analysis in standard format" \
  --context "daily data ingestion workflow" \
  --constraint "under 5 minutes for 10GB file" \
  --save

✓ Job defined and saved to memory/jtbd.ttl
```

### outcome

Define desired outcomes for a job.

```bash
specify jtbd outcome JOB_NAME [OPTIONS]
```

Outcomes are measurable results, not features:

```bash
specify jtbd outcome "Process Data Files" \
  --define "Files validated in < 30 seconds" \
  --define "Transform errors caught before processing" \
  --define "Schema consistency verified across sources" \
  --define "Processed data directly usable in analysis"

✓ Outcomes defined:
  1. Files validated in < 30 seconds
  2. Transform errors caught before processing
  3. Schema consistency verified across sources
  4. Processed data directly usable in analysis
```

### prioritize

Prioritize jobs using JTBD framework.

```bash
specify jtbd prioritize [OPTIONS]
```

Considers: importance, frequency, satisfaction gaps.

**Options:**
- `--by METRIC` - Prioritization metric (importance, frequency, gap)
- `--user USER_TYPE` - Filter to user type
- `--format` - Output format (text, json, matrix)

**Example:**
```bash
specify jtbd prioritize --by importance

Priority Matrix:

High Importance, High Frequency (FOCUS):
  ✓ Process Data Files (importance: 9/10, frequency: daily)
  ✓ Analyze Patterns (importance: 8/10, frequency: daily)

High Importance, Low Frequency (SCHEDULE):
  ⚠ Setup New Data Source (importance: 9/10, frequency: monthly)
  ⚠ Build Custom Report (importance: 7/10, frequency: quarterly)

Low Importance, High Frequency (AUTOMATE):
  ◇ Archive Old Files (importance: 4/10, frequency: weekly)

Low Importance, Low Frequency (RECONSIDER):
  ○ Generate Stats Dashboard (importance: 3/10, frequency: annually)
```

### satisfaction

Measure satisfaction gap for job outcomes.

```bash
specify jtbd satisfaction JOB_NAME [OPTIONS]
```

Shows gap between desired and current outcomes:

```bash
specify jtbd satisfaction "Process Data Files"

Outcome satisfaction:
  ✓ Files validated < 30s
    Current: 45 seconds (tool takes time)
    Gap: 15 seconds (MEDIUM GAP)

  ✓ Errors caught before processing
    Current: 70% accuracy (some slip through)
    Gap: 30% accuracy (LARGE GAP - PRIORITY)

  ✓ Schema consistency verified
    Current: Manual verification (error-prone)
    Gap: Needs automation (MEDIUM GAP)

  ✓ Data directly usable
    Current: Requires post-processing
    Gap: Needs better output format (MEDIUM GAP)
```

### template

Create JTBD specification template for a job.

```bash
specify jtbd template JOB_NAME [OPTIONS]
```

Generates Turtle/RDF template for specification:

```bash
specify jtbd template "Process Data Files" --output job-spec.ttl

# Generated file structure:
@prefix jtbd: <http://ggen-spec-kit.org/jtbd#> .
@prefix job: <http://example.org/jobs#> .

job:ProcessDataFiles
    a jtbd:Job ;
    rdfs:label "Process Data Files" ;
    jtbd:actor job:DataAnalyst ;
    jtbd:context job:DailyIngestion ;
    jtbd:outcome [
        a jtbd:Outcome ;
        rdfs:label "Data validated in < 30 seconds" ;
        jtbd:measurable true ;
        jtbd:satisfactionGap "medium"
    ] ;
    jtbd:outcome [
        a jtbd:Outcome ;
        rdfs:label "Transform errors caught" ;
        jtbd:measurable true ;
        jtbd:satisfactionGap "large"
    ] .
```

### report

Generate JTBD analysis report.

```bash
specify jtbd report [OPTIONS]
```

Comprehensive analysis of all jobs, priorities, gaps:

```bash
specify jtbd report --output jtbd-analysis.md --format markdown

# Generates: 15-page comprehensive report
# Including:
#   - Job map with all jobs and subprocesses
#   - Satisfaction gap analysis
#   - Priority matrix
#   - Feature recommendations by job
#   - Implementation roadmap
```

## Examples

### Mapping User Jobs

```bash
# Map all jobs for data analysts
specify jtbd map "data analyst"

# Define specific job
specify jtbd define "Validate Data Quality" \
  --actor "data analyst" \
  --outcome "identify all data quality issues before analysis" \
  --context "start of analysis workflow" \
  --constraint "must complete in < 5 minutes"

# Define outcomes
specify jtbd outcome "Validate Data Quality" \
  --define "Missing values detected and highlighted" \
  --define "Duplicate records identified" \
  --define "Outliers flagged for review" \
  --define "Data type mismatches caught"

# Check satisfaction
specify jtbd satisfaction "Validate Data Quality"
# Shows what's missing compared to outcomes
```

### Prioritization Example

```bash
# See which jobs matter most
specify jtbd prioritize --by frequency

# Result shows:
# Daily jobs (do first):
#   - Process Data Files
#   - Analyze Patterns
# Monthly jobs (schedule):
#   - Setup New Data Source
# Quarterly jobs (nice to have):
#   - Build Custom Report
```

### Generating Specifications

```bash
# Create RDF specification from job
specify jtbd template "Build Reports" \
  --output report-job-spec.ttl

# Now edit and extend the RDF spec
vim report-job-spec.ttl

# Generate requirements from the spec
specify ggen sync
# Generates code, tests, docs from the JTBD-based spec
```

## Integration with Other Commands

### With ggen
```bash
# Jobs define what to build
specify jtbd define "Process Data Files" ... --save

# ggen generates code from jobs specification
specify ggen sync

# Tests verify job outcomes are met
uv run pytest tests/
```

### With PM (Process Mining)
```bash
# Define job subprocess
specify jtbd map "data analyst"

# Analyze actual execution flow
specify pm analyze workflow.xml

# Compare defined vs. actual process
specify pm compare defined-job.ttl actual-workflow.xml
```

## JTBD Framework Concepts

### Jobs vs. Features

❌ **Feature-based** thinking:
- "Add data validation"
- "Implement error handling"
- "Build reporting dashboard"

✅ **Job-based** thinking:
- "Catch data quality issues before analysis"
- "Prevent downstream errors from bad data"
- "Communicate findings to stakeholders"

### Job Structure

A job has:
1. **Actor** - Who performs it
2. **Context** - When and where
3. **Core Task** - What they're trying to accomplish
4. **Subprocesses** - Steps within the job
5. **Outcomes** - Desired results

### Outcomes (Not Features)

Outcomes are measurable results:
```
✓ "Data validated in < 30 seconds"
✓ "Transform errors caught before processing"
✓ "Schema consistency verified"

✗ "Add validation button"
✗ "Create error logger"
✗ "Build schema checker"
```

Features are implementation details that serve outcomes.

## Performance Metrics

Track job success through outcome satisfaction:

```bash
# Measure current satisfaction
specify jtbd satisfaction "Process Data Files" --metrics

Metrics:
  validation_time: 45s (target: 30s, gap: 50% slower)
  error_detection: 70% (target: 100%, gap: 30% miss rate)
  schema_consistency: manual (target: automated, gap: high)
  post_processing: 10 min (target: 0 min, gap: unnecessary work)

Recommendations:
  1. Optimize validation performance (highest impact)
  2. Improve error detection accuracy (large gap)
  3. Automate schema checking (high impact)
  4. Improve output format (reduce post-processing)
```

## See Also

- `/docs/guides/jtbd/apply-framework.md` - Detailed how-to guide
- `/docs/guides/jtbd/measure-outcomes.md` - Measuring outcome satisfaction
- `/docs/explanation/why-jtbd-framework.md` - Framework philosophy
- `/docs/reference/jtbd-framework.md` - Complete JTBD reference
- [Tutorial 6: Exploring JTBD](../tutorials/06-exploring-jtbd.md) - Learning guide
