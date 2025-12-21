# Why Features Exist: JTBD Justification for Each Command

## Overview

This document explains the **Jobs To Be Done** rationale for each spec-kit command. For every command, we document:

- **What jobs** it accomplishes
- **Which personas** benefit
- **Outcomes** delivered
- **Painpoints** eliminated
- **How success is measured**

Understanding the "why" behind each feature ensures we maintain customer focus and can objectively evaluate feature value.

---

## Table of Contents

### Core Commands
1. [init - Initialize Project](#init---initialize-project)
2. [check - Validate Dependencies](#check---validate-dependencies)
3. [version - Version Information](#version---version-information)

### Code Generation Commands (ggen)
4. [ggen sync - Transform RDF to Code/Docs](#ggen-sync---transform-rdf-to-codedocs)

### Process Mining Commands (pm)
5. [pm discover - Process Model Discovery](#pm-discover---process-model-discovery)
6. [pm conform - Conformance Checking](#pm-conform---conformance-checking)
7. [pm stats - Event Log Statistics](#pm-stats---event-log-statistics)

### Workflow Commands (wf/spiff)
8. [wf validate - OTEL Validation](#wf-validate---otel-validation)
9. [wf validate-quick - Quick Validation](#wf-validate-quick---quick-validation)
10. [wf discover-projects - Project Discovery](#wf-discover-projects---project-discovery)
11. [wf validate-external - External Project Validation](#wf-validate-external---external-project-validation)
12. [wf batch-validate - Batch Validation](#wf-batch-validate---batch-validation)
13. [wf run-workflow - Execute BPMN Workflow](#wf-run-workflow---execute-bpmn-workflow)

---

## init - Initialize Project

### Jobs Accomplished

**Primary Job:** Create project structure from template
> "Bootstrap a new spec-kit project with proper scaffolding so I can start defining RDF ontologies immediately without manual setup."

**Supporting Job:** Establish development environment
> "Set up git repository, AI assistant integration, and directory structure so my team has a consistent starting point."

### Personas Benefiting

1. **RDF Ontology Designer** (Primary)
   - Needs ontology file structure
   - Wants namespace templates
   - Requires SHACL shape examples

2. **CLI Developer** (Secondary)
   - Needs project scaffolding
   - Wants consistent structure
   - Requires build configuration

3. **Documentation Writer** (Secondary)
   - Needs documentation templates
   - Wants ggen configuration
   - Requires README structure

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to bootstrap project | 30-60 min (manual) | < 2 min (automated) | ⭐⭐⭐ |
| Consistency across projects | Low (varies by developer) | High (standardized template) | ⭐⭐⭐ |
| Setup errors | Frequent (missing files) | Rare (validated template) | ⭐⭐ |
| Onboarding time | Hours (documentation + trial) | Minutes (working example) | ⭐⭐⭐ |

### Painpoints Eliminated

**Before `specify init`:**
- ❌ Manual directory creation and file copying
- ❌ Forgetting required configuration files
- ❌ Inconsistent project structures across team
- ❌ No guidance on best practices
- ❌ Missing integration with AI assistants
- ❌ Long onboarding for new developers

**After `specify init`:**
- ✅ One command creates complete structure
- ✅ All required files included
- ✅ Standardized, documented structure
- ✅ Best practice examples included
- ✅ AI assistant slash commands configured
- ✅ Quick start for new team members

### Success Measurement

**Adoption Metrics:**
```python
@span("project.initialization")
def initialize_project(
    project_name: str,
    ai_type: str,
    here: bool
) -> InitResult:
    # Measure:
    # - Time to completion (target: < 2 min)
    # - Success rate (target: > 95%)
    # - AI integration adoption (target: > 80%)
    pass
```

**Quality Metrics:**
- **Setup success rate**: % of `specify init` runs that succeed
- **Template completeness**: % of projects missing no required files
- **AI integration rate**: % of initialized projects using AI features
- **Time to first commit**: Minutes from init to productive work

**Validation:**
- Unit tests: Verify all template files created
- Integration tests: Full project initialization scenarios
- E2E tests: Initialize, validate, and run ggen in new project

---

## check - Validate Dependencies

### Jobs Accomplished

**Primary Job:** Verify tool ecosystem health
> "Check that all required tools and dependencies are installed correctly so I can confidently use spec-kit without environment errors."

**Supporting Job:** Troubleshoot environment issues
> "Diagnose which tools are missing or misconfigured so I can fix problems before they cause failures."

### Personas Benefiting

1. **All Personas** (Universal need)
   - **RDF Ontology Designer**: Needs ggen, SPARQL validators
   - **CLI Developer**: Needs Python, uv, git
   - **Operations Engineer**: Needs Docker, OTEL collectors
   - **Data Analyst**: Needs pm4py dependencies
   - **Documentation Writer**: Needs ggen, MkDocs

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to diagnose missing tools | 15-30 min (trial-and-error) | < 10 sec (automated check) | ⭐⭐⭐ |
| Environment setup confidence | Low (uncertain) | High (validated) | ⭐⭐⭐ |
| Cryptic error messages | Frequent (tool not found) | Rare (clear guidance) | ⭐⭐⭐ |
| CI/CD setup errors | Common (wrong versions) | Rare (version check) | ⭐⭐ |

### Painpoints Eliminated

**Before `specify check`:**
- ❌ Trial-and-error to find missing tools
- ❌ Cryptic "command not found" errors
- ❌ Version compatibility issues discovered late
- ❌ No central place to verify setup
- ❌ Manual checking of each tool
- ❌ Unclear which tools are optional vs. required

**After `specify check`:**
- ✅ Comprehensive check in one command
- ✅ Clear pass/fail status for each tool
- ✅ Version compatibility warnings
- ✅ Installation guidance for missing tools
- ✅ Categorization: required vs. optional
- ✅ JSON output for automation

### Success Measurement

**Adoption Metrics:**
```python
@span("environment.validation")
def check_dependencies(
    verbose: bool,
    json: bool,
    include_optional: bool
) -> CheckResult:
    # Measure:
    # - Check duration (target: < 10s)
    # - Tools checked (count)
    # - Success rate (% passing)
    # - Issue detection rate
    pass
```

**Quality Metrics:**
- **Check speed**: < 10 seconds for all tools
- **Detection accuracy**: 100% of missing tools identified
- **False positive rate**: < 1% incorrect failures
- **Guidance clarity**: User survey on installation instructions

**Validation:**
- Test with missing tools (should detect)
- Test with wrong versions (should warn)
- Test with all tools present (should pass)
- Test JSON output parsing

---

## version - Version Information

### Jobs Accomplished

**Primary Job:** Identify installed version
> "Determine which version of spec-kit is installed so I can verify compatibility, report bugs accurately, and check for updates."

**Supporting Job:** Track build provenance
> "Understand when and how this version was built so I can reproduce environments and debug version-specific issues."

### Personas Benefiting

1. **Operations Engineer** (Primary)
   - Needs version tracking in deployments
   - Wants build metadata for debugging
   - Requires update notifications

2. **CLI Developer** (Secondary)
   - Needs version for bug reports
   - Wants compatibility information
   - Requires API version tracking

3. **All Personas** (Support)
   - Need version for documentation matching
   - Want update awareness
   - Require troubleshooting context

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to identify version | Minutes (find package info) | Seconds (`--version`) | ⭐⭐ |
| Bug report accuracy | Low (version often missing) | High (clear version info) | ⭐⭐⭐ |
| Update awareness | None (manual check) | High (check-updates flag) | ⭐⭐ |
| Build provenance | None (unknown build) | Complete (timestamp, commit) | ⭐⭐ |

### Painpoints Eliminated

**Before `specify version`:**
- ❌ Unclear which version is installed
- ❌ No easy way to check for updates
- ❌ Bug reports lack version context
- ❌ Can't verify expected version deployed
- ❌ No build provenance information

**After `specify version`:**
- ✅ Instant version identification
- ✅ Optional update checking
- ✅ Complete version metadata
- ✅ JSON output for automation
- ✅ Build timestamp and commit SHA

### Success Measurement

**Adoption Metrics:**
```python
@span("version.info")
def show_version(
    check_updates: bool,
    json: bool,
    verbose: bool
) -> VersionInfo:
    # Measure:
    # - Check-updates usage (%)
    # - JSON output usage (%)
    # - Verbose mode usage (%)
    pass
```

**Quality Metrics:**
- **Accuracy**: 100% correct version reported
- **Update detection**: % of outdated versions detected
- **Response time**: < 1s for version info
- **Metadata completeness**: All fields populated

---

## ggen sync - Transform RDF to Code/Docs

### Jobs Accomplished

**Primary Job:** Generate code from ontology
> "Transform my RDF ontology into type-safe code for Python, TypeScript, Rust, and other languages so I maintain a single source of truth across heterogeneous stacks."

**Supporting Job:** Generate documentation from RDF
> "Create comprehensive Markdown documentation from RDF specifications so technical writers have accurate, up-to-date API references."

### Personas Benefiting

1. **RDF Ontology Designer** (Primary)
   - Needs code generation from ontology
   - Wants multi-language support
   - Requires type safety guarantees

2. **Documentation Writer** (Primary)
   - Needs documentation generation
   - Wants synchronization with RDF
   - Requires customizable templates

3. **CLI Developer** (Secondary)
   - Benefits from generated type definitions
   - Uses generated API clients
   - Leverages generated tests

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to generate code | Manual (hours/days) | Automated (< 5s) | ⭐⭐⭐ |
| Code-ontology consistency | Low (manual drift) | Perfect (deterministic) | ⭐⭐⭐ |
| Multi-language support | Manual per language | Automatic (all targets) | ⭐⭐⭐ |
| Documentation drift | High (manual updates) | Zero (constitutional equation) | ⭐⭐⭐ |

### Painpoints Eliminated

**Before `ggen sync`:**
- ❌ Manual code writing from specifications
- ❌ Code drifts from ontology over time
- ❌ Each language requires separate implementation
- ❌ Documentation manually written and updated
- ❌ No guarantee of consistency
- ❌ Refactoring is risky and tedious

**After `ggen sync`:**
- ✅ Automatic code generation in seconds
- ✅ Perfect ontology-code synchronization
- ✅ One ontology → many languages
- ✅ Documentation auto-generated
- ✅ Constitutional equation guarantee
- ✅ Safe, reproducible refactoring

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("ggen.sync")
def ggen_sync(
    watch: bool,
    verbose: bool,
    dry_run: bool,
    json: bool
) -> SyncResult:
    # Measure:
    # - Generation time (target: < 5s)
    # - Files generated (count)
    # - Languages supported (count)
    # - Watch mode adoption (%)
    pass
```

**Quality Metrics:**
- **Generation speed**: < 5s for typical ontology
- **Accuracy**: 100% ontology concepts represented
- **Completeness**: 100% of ontology documented
- **Determinism**: Same ontology → identical code

**Validation:**
- Round-trip tests: Ontology → code → ontology
- Multi-language tests: All targets compile
- Documentation tests: All concepts documented
- Watch mode tests: Auto-regeneration works

---

## pm discover - Process Model Discovery

### Jobs Accomplished

**Primary Job:** Extract process patterns from logs
> "Discover process models from event logs using process mining so I can identify bottlenecks, deviations, and optimization opportunities."

**Supporting Job:** Understand actual workflow execution
> "Visualize how processes actually execute (not how we think they execute) so I can base improvements on empirical evidence."

### Personas Benefiting

1. **Data Analyst** (Primary)
   - Needs process pattern extraction
   - Wants workflow visualization
   - Requires bottleneck identification

2. **Operations Engineer** (Secondary)
   - Benefits from execution analysis
   - Uses models for optimization
   - Leverages deviation detection

3. **RDF Ontology Designer** (Tertiary)
   - Uses discovered models to inform ontology
   - Maps actual execution to formal models
   - Validates ontology against reality

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to extract process model | Hours (manual analysis) | Minutes (automated) | ⭐⭐⭐ |
| Model accuracy | Low (biased by assumptions) | High (data-driven) | ⭐⭐⭐ |
| Bottleneck identification | Difficult (hidden) | Clear (visualized) | ⭐⭐ |
| Algorithm selection | Manual (expert knowledge) | Guided (recommendations) | ⭐⭐ |

### Painpoints Eliminated

**Before `pm discover`:**
- ❌ Manual log analysis is tedious
- ❌ Subjective process understanding
- ❌ Miss rare but important variants
- ❌ No visualization of actual execution
- ❌ Algorithm selection requires expertise
- ❌ Long processing times

**After `pm discover`:**
- ✅ Automated process extraction
- ✅ Objective, data-driven models
- ✅ All variants captured
- ✅ Clear process visualizations
- ✅ Multiple algorithms available
- ✅ Fast processing (< 10 min for 1M events)

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("pm.discover")
def discover_process(
    input_file: Path,
    algorithm: str,
    noise: float,
    output: Optional[Path]
) -> DiscoveryResult:
    # Measure:
    # - Processing time (events/sec)
    # - Model quality (precision, recall)
    # - Algorithm usage distribution
    pass
```

**Quality Metrics:**
- **Processing speed**: > 10K events/sec
- **Model precision**: % of modeled behavior in log
- **Model recall**: % of logged behavior in model
- **Model simplicity**: Complexity score

**Validation:**
- Test with synthetic logs (known ground truth)
- Test with real-world logs (manual verification)
- Test all algorithms (quality comparison)
- Test noise filtering (robustness)

---

## pm conform - Conformance Checking

### Jobs Accomplished

**Primary Job:** Validate execution against model
> "Check whether actual execution traces conform to expected process models so I can detect deviations and ensure compliance."

**Supporting Job:** Identify process violations
> "Pinpoint which cases violate the expected workflow so I can investigate root causes and implement corrective actions."

### Personas Benefiting

1. **Data Analyst** (Primary)
   - Needs conformance validation
   - Wants deviation detection
   - Requires compliance reporting

2. **Operations Engineer** (Secondary)
   - Benefits from compliance monitoring
   - Uses violation alerts
   - Leverages for audit trails

3. **RDF Ontology Designer** (Tertiary)
   - Validates ontology against execution
   - Identifies model-reality gaps
   - Refines ontology based on violations

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to check conformance | Hours (manual) | Minutes (automated) | ⭐⭐⭐ |
| Violation detection rate | Low (sampling) | High (complete) | ⭐⭐⭐ |
| Compliance confidence | Low (uncertain) | High (measured) | ⭐⭐⭐ |
| Root cause clarity | Poor (vague) | Clear (specific) | ⭐⭐ |

### Painpoints Eliminated

**Before `pm conform`:**
- ❌ Manual conformance checking
- ❌ Sample-based (miss violations)
- ❌ Unclear which cases violate
- ❌ No quantitative compliance metrics
- ❌ Violations lack context
- ❌ Method selection requires expertise

**After `pm conform`:**
- ✅ Automated conformance checking
- ✅ Complete coverage (all traces)
- ✅ Specific violating cases identified
- ✅ Quantitative fitness/precision
- ✅ Violations with execution context
- ✅ Multiple methods available

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("pm.conformance")
def check_conformance(
    log_file: Path,
    model_file: Path,
    method: str
) -> ConformanceResult:
    # Measure:
    # - Processing time
    # - Violation count and types
    # - Fitness and precision scores
    pass
```

**Quality Metrics:**
- **Processing speed**: > 5K traces/sec
- **Detection accuracy**: 100% of violations found
- **False positive rate**: < 5%
- **Clarity score**: User understanding of violations

---

## pm stats - Event Log Statistics

### Jobs Accomplished

**Primary Job:** Generate log statistics
> "Extract statistical summaries from event logs so I can understand process performance, resource utilization, and throughput."

**Supporting Job:** Create executive reports
> "Produce clear, quantitative metrics for dashboards and reports so stakeholders understand process health."

### Personas Benefiting

1. **Data Analyst** (Primary)
   - Needs statistical summaries
   - Wants KPI calculation
   - Requires report generation

2. **Operations Engineer** (Secondary)
   - Benefits from performance metrics
   - Uses throughput statistics
   - Leverages for capacity planning

3. **Documentation Writer** (Tertiary)
   - Uses statistics in reports
   - Creates executive summaries
   - Visualizes trends

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to generate statistics | Hours (manual) | Seconds (automated) | ⭐⭐⭐ |
| Metric completeness | Partial (ad-hoc) | Complete (standard set) | ⭐⭐⭐ |
| Report generation | Manual (copy-paste) | Automated (JSON export) | ⭐⭐ |
| BI tool integration | Difficult (format mismatch) | Easy (JSON/CSV) | ⭐⭐ |

### Painpoints Eliminated

**Before `pm stats`:**
- ❌ Manual calculation tedious
- ❌ Inconsistent metrics across reports
- ❌ No standard output format
- ❌ Export to BI tools manual
- ❌ Limited visualization options
- ❌ Errors in manual calculations

**After `pm stats`:**
- ✅ Instant statistical calculation
- ✅ Standardized metric definitions
- ✅ JSON and CSV output formats
- ✅ Direct BI tool integration
- ✅ Visualization-ready data
- ✅ Accurate, reproducible results

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("pm.statistics")
def compute_statistics(
    input_file: Path,
    case_id: str,
    json: bool
) -> StatisticsResult:
    # Measure:
    # - Processing time
    # - Metrics calculated (count)
    # - Export format usage
    pass
```

**Quality Metrics:**
- **Processing speed**: < 1 min for 100K events
- **Metric completeness**: All standard metrics included
- **Accuracy**: 100% correct calculations
- **Export success**: Valid JSON/CSV output

---

## wf validate - OTEL Validation

### Jobs Accomplished

**Primary Job:** Validate deployment readiness
> "Execute comprehensive validation checks on spec-kit tools, OTEL instrumentation, and dependencies so I can ensure production deployments will succeed."

**Supporting Job:** Verify observability infrastructure
> "Confirm that OpenTelemetry instrumentation is working correctly so I can trust production monitoring and troubleshooting."

### Personas Benefiting

1. **Operations Engineer** (Primary)
   - Needs pre-deployment validation
   - Wants OTEL verification
   - Requires health check aggregation

2. **CLI Developer** (Secondary)
   - Benefits from integration testing
   - Uses OTEL validation in CI/CD
   - Leverages for quality gates

3. **RDF Ontology Designer** (Tertiary)
   - Validates tools before ontology work
   - Confirms ggen integration
   - Ensures complete toolchain

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to validate deployment | 15-30 min (manual checklist) | < 5 min (automated) | ⭐⭐⭐ |
| Validation coverage | Partial (manual steps) | Complete (BPMN workflow) | ⭐⭐⭐ |
| OTEL verification | None (assumed working) | Explicit (tested) | ⭐⭐⭐ |
| Confidence in deployment | Medium (uncertain) | High (validated) | ⭐⭐⭐ |

### Painpoints Eliminated

**Before `wf validate`:**
- ❌ Manual validation checklist
- ❌ Steps skipped or forgotten
- ❌ No OTEL verification
- ❌ Sequential validation slow
- ❌ Unclear validation coverage
- ❌ No historical validation data

**After `wf validate`:**
- ✅ Automated BPMN-driven workflow
- ✅ All steps guaranteed executed
- ✅ Explicit OTEL validation
- ✅ Parallel execution where possible
- ✅ Complete coverage reporting
- ✅ JSON export for trending

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("workflow.validation")
def validate_deployment(
    iterations: int,
    verbose: bool,
    export_json: Optional[Path]
) -> ValidationReport:
    # Measure:
    # - Total validation time
    # - Checks executed (count)
    # - Success rate (%)
    # - Issues detected
    pass
```

**Quality Metrics:**
- **Validation time**: < 5 min for full workflow
- **Coverage**: 95%+ of critical paths
- **Detection rate**: 100% of known issues caught
- **False positive rate**: < 5%

**Validation:**
- Test with broken OTEL (should detect)
- Test with missing tools (should detect)
- Test with valid setup (should pass)
- Test iterations parameter
- Test JSON export format

---

## wf validate-quick - Quick Validation

### Jobs Accomplished

**Primary Job:** Fast critical-path validation
> "Run 80/20 validation focused on critical paths so I can quickly verify deployment readiness without waiting for comprehensive checks."

**Supporting Job:** Iterative development validation
> "Get rapid feedback during development so I can validate changes quickly before committing."

### Personas Benefiting

1. **Operations Engineer** (Primary)
   - Needs fast validation for rapid iteration
   - Wants critical-only checks
   - Requires quick go/no-go decisions

2. **CLI Developer** (Primary)
   - Benefits from fast feedback loops
   - Uses in development workflow
   - Leverages for pre-commit checks

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to get validation feedback | 5 min (full validation) | < 1 min (quick mode) | ⭐⭐⭐ |
| Development cycle time | Slow (long validation) | Fast (quick feedback) | ⭐⭐⭐ |
| Critical issue detection | Same (comprehensive) | Same (focused 80/20) | ⭐⭐ |

### Painpoints Eliminated

**Before `wf validate-quick`:**
- ❌ Full validation too slow for iteration
- ❌ No fast critical-path-only option
- ❌ Development feedback delayed
- ❌ Temptation to skip validation

**After `wf validate-quick`:**
- ✅ Fast < 1 min validation
- ✅ Critical paths verified
- ✅ Rapid development feedback
- ✅ Validation remains practical

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("workflow.validation.quick")
def validate_quick(
    export_json: Optional[Path]
) -> QuickValidationReport:
    # Measure:
    # - Validation time (target: < 1 min)
    # - Critical checks executed
    # - Issues detected
    pass
```

**Quality Metrics:**
- **Speed**: < 1 minute
- **Critical coverage**: 80% of important checks
- **Detection rate**: 90%+ of critical issues
- **Development adoption**: % of commits using quick mode

---

## wf discover-projects - Project Discovery

### Jobs Accomplished

**Primary Job:** Automatically find Python projects
> "Discover all Python projects in a directory tree so I can batch-validate or analyze multiple projects without manual enumeration."

**Supporting Job:** Organization-wide assessment
> "Identify all projects for compliance audits or technical debt assessment so I can understand organizational portfolio."

### Personas Benefiting

1. **Operations Engineer** (Primary)
   - Needs project inventory
   - Wants batch operation targets
   - Requires compliance scope identification

2. **Data Analyst** (Secondary)
   - Benefits from project enumeration
   - Uses for portfolio analysis
   - Leverages for reporting

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to enumerate projects | Hours (manual search) | Seconds (automated) | ⭐⭐⭐ |
| Discovery accuracy | Medium (manual errors) | High (heuristic scoring) | ⭐⭐ |
| Large directory handling | Slow (full traversal) | Fast (depth limits) | ⭐⭐ |

### Painpoints Eliminated

**Before `wf discover-projects`:**
- ❌ Manual project enumeration
- ❌ Missed projects in subdirectories
- ❌ False positives (tool directories)
- ❌ No confidence scoring
- ❌ Slow for large directory trees

**After `wf discover-projects`:**
- ✅ Automatic project discovery
- ✅ Recursive directory scanning
- ✅ Confidence-based filtering
- ✅ Heuristic scoring system
- ✅ Configurable depth limits

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("workflow.project_discovery")
def discover_projects(
    path: Path,
    depth: int,
    confidence: float
) -> DiscoveryResult:
    # Measure:
    # - Scan time
    # - Projects found (count)
    # - Confidence distribution
    pass
```

**Quality Metrics:**
- **Precision**: % of discovered that are real projects
- **Recall**: % of real projects discovered
- **Speed**: Projects scanned per second
- **False positive rate**: < 10%

---

## wf validate-external - External Project Validation

### Jobs Accomplished

**Primary Job:** Validate external project
> "Run spec-kit validation on an external Python project so I can assess quality, detect issues, or ensure compliance."

**Supporting Job:** Portfolio quality assessment
> "Validate projects I don't maintain so I can understand their health before adoption or integration."

### Personas Benefiting

1. **Operations Engineer** (Primary)
   - Needs external project validation
   - Wants third-party quality assessment
   - Requires pre-integration checks

2. **CLI Developer** (Secondary)
   - Benefits from dependency validation
   - Uses for library evaluation
   - Leverages for security audits

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to validate external project | Manual (hours) | Automated (< 5 min) | ⭐⭐⭐ |
| Validation consistency | Low (ad-hoc) | High (standardized) | ⭐⭐⭐ |
| Risk assessment | Subjective (opinion) | Objective (metrics) | ⭐⭐ |

### Painpoints Eliminated

**Before `wf validate-external`:**
- ❌ Manual external project assessment
- ❌ Inconsistent validation criteria
- ❌ No automated health checks
- ❌ Subjective quality judgments

**After `wf validate-external`:**
- ✅ Automated external validation
- ✅ Standardized quality checks
- ✅ Objective metric reporting
- ✅ Consistent evaluation

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("workflow.external_validation")
def validate_external_project(
    project_path: Path,
    export_json: Optional[Path]
) -> ExternalValidationReport:
    # Measure:
    # - Validation time
    # - Checks executed
    # - Issues detected
    pass
```

**Quality Metrics:**
- **Validation time**: < 5 min per project
- **Coverage**: Same as internal projects
- **Accuracy**: Matches manual assessment

---

## wf batch-validate - Batch Validation

### Jobs Accomplished

**Primary Job:** Validate multiple projects in parallel
> "Run validation workflows across multiple projects simultaneously so I can ensure organization-wide quality gates efficiently."

**Supporting Job:** Generate compliance reports
> "Aggregate validation results across portfolio so I can create executive summaries and compliance documentation."

### Personas Benefiting

1. **Operations Engineer** (Primary)
   - Needs batch quality audits
   - Wants parallel execution
   - Requires aggregated reporting

2. **Data Analyst** (Secondary)
   - Benefits from portfolio metrics
   - Uses aggregated results
   - Leverages for trending analysis

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to validate 50 projects | Hours (sequential) | Minutes (parallel) | ⭐⭐⭐ |
| Validation effort | High (manual per project) | Low (automated batch) | ⭐⭐⭐ |
| Report aggregation | Manual (copy-paste) | Automated (JSON) | ⭐⭐⭐ |
| Portfolio visibility | Poor (fragmented) | Excellent (unified) | ⭐⭐⭐ |

### Painpoints Eliminated

**Before `wf batch-validate`:**
- ❌ Sequential validation too slow
- ❌ Manual per-project execution
- ❌ Aggregating results tedious
- ❌ No parallel execution
- ❌ Difficult to track progress
- ❌ Results scattered across projects

**After `wf batch-validate`:**
- ✅ Parallel execution (configurable workers)
- ✅ Automated project enumeration
- ✅ Unified result aggregation
- ✅ Progress tracking
- ✅ Centralized reporting
- ✅ Export to BI tools

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("workflow.batch_validation")
def batch_validate(
    path: Path,
    parallel: bool,
    workers: int,
    export_json: Optional[Path]
) -> BatchValidationReport:
    # Measure:
    # - Total time (vs. sequential baseline)
    # - Speedup factor (parallel vs. sequential)
    # - Projects validated (count)
    # - Issues detected (aggregate)
    pass
```

**Quality Metrics:**
- **Speedup**: 5-10x vs. sequential
- **Throughput**: > 10 projects/min with parallel
- **Success rate**: > 95% of projects validated
- **Report completeness**: All projects included

---

## wf run-workflow - Execute BPMN Workflow

### Jobs Accomplished

**Primary Job:** Execute custom validation workflow
> "Run a custom BPMN workflow file so I can orchestrate complex validation sequences with conditional logic and error handling."

**Supporting Job:** Reusable validation orchestration
> "Define validation workflows once and execute repeatedly so I can standardize and automate complex validation scenarios."

### Personas Benefiting

1. **Operations Engineer** (Primary)
   - Needs custom validation orchestration
   - Wants reusable workflow definitions
   - Requires complex conditional logic

2. **CLI Developer** (Secondary)
   - Benefits from workflow automation
   - Uses for integration testing
   - Leverages for CI/CD pipelines

### Outcomes Delivered

| Outcome | Before | After | Metric |
|---------|--------|-------|--------|
| Time to define complex validation | Hours (script writing) | Minutes (BPMN modeling) | ⭐⭐ |
| Workflow reusability | Low (script per scenario) | High (BPMN templates) | ⭐⭐⭐ |
| Error handling | Manual (ad-hoc) | Automatic (BPMN error events) | ⭐⭐ |
| Visualization | None (code only) | Clear (BPMN diagram) | ⭐⭐⭐ |

### Painpoints Eliminated

**Before `wf run-workflow`:**
- ❌ Complex validation requires custom scripts
- ❌ No visual workflow representation
- ❌ Difficult to reuse across scenarios
- ❌ Error handling ad-hoc
- ❌ Hard to communicate validation logic
- ❌ No standardized orchestration

**After `wf run-workflow`:**
- ✅ BPMN-based workflow definition
- ✅ Visual workflow diagrams
- ✅ Reusable workflow templates
- ✅ Built-in error handling
- ✅ Clear communication artifact
- ✅ SpiffWorkflow orchestration

### Success Measurement

**Adoption Metrics:**
```python
@timed
@span("workflow.execution")
def run_workflow(
    workflow_file: Path,
    export_json: Optional[Path]
) -> WorkflowResult:
    # Measure:
    # - Execution time
    # - Tasks executed (count)
    # - Success rate
    # - Error recovery rate
    pass
```

**Quality Metrics:**
- **Execution reliability**: > 95% success rate
- **Error recovery**: % of errors handled gracefully
- **Workflow clarity**: Survey on BPMN understandability
- **Reuse rate**: % of workflows executed > once

---

## Summary: Feature-Job-Outcome Mapping

### High-Value Features (Multiple Jobs, High Importance)

| Feature | Jobs | Personas | Priority Outcomes | Innovation Opportunity |
|---------|------|----------|-------------------|------------------------|
| `ggen sync` | 2 | 3 | Code generation, doc sync | ⭐⭐⭐ Template customization |
| `wf validate` | 2 | 3 | Deployment confidence, OTEL verification | ⭐⭐ Coverage expansion |
| `pm discover` | 2 | 3 | Process insights, bottleneck detection | ⭐⭐⭐ Model quality improvement |
| `check` | 2 | 5 (all) | Dependency diagnosis, setup confidence | ⭐ (already strong) |

### Innovation Priorities (Gap Analysis)

Based on importance-satisfaction gaps in [Jobs & Outcomes Catalog](./jobs-outcomes-catalog.md):

1. **SHACL Validation UX** (O1.2.2) - Better error messages, detection
   - **Features to enhance**: `check`, new `validate` command
   - **Painpoint**: Cryptic SHACL errors
   - **Opportunity**: Plain-English explanations, fix suggestions

2. **CLI Test Generation** (O2.1.3) - Auto-generate comprehensive tests
   - **Features to create**: New `generate-tests` command
   - **Painpoint**: Manual test writing tedium
   - **Opportunity**: RDF spec → pytest tests

3. **OTEL Troubleshooting** (O3.2.1) - Faster incident diagnosis
   - **Features to enhance**: Better OTEL queries, visualization
   - **Painpoint**: Distributed trace correlation
   - **Opportunity**: Trace UI, anomaly detection

4. **Process Mining Clarity** (O4.1.3) - Clearer conformance reports
   - **Features to enhance**: `pm conform` output
   - **Painpoint**: Violations lack context
   - **Opportunity**: Visual violation highlighting, root cause hints

5. **Template Customization** (O5.1.3) - Easier Tera templates
   - **Features to create**: Template editor, debugger
   - **Painpoint**: Tera/SPARQL learning curve
   - **Opportunity**: Visual template builder, validation

---

**Next Steps:**
- [Measurement Strategy](./measurement-strategy.md) - How to track outcome delivery
- [Getting Started with JTBD](./getting-started.md) - Tutorial for applying JTBD
- [Examples](./examples.md) - Complete worked examples
