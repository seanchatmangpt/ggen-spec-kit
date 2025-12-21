# Jobs & Outcomes Catalog

## Overview

This catalog provides a comprehensive inventory of all customer jobs, associated outcomes, painpoints, progress makers, and features that address each outcome in spec-kit.

**Structure:**
- Organized by persona
- Each job includes outcomes with priorities
- Outcomes linked to addressing features
- Painpoints and progress makers documented
- Measurement criteria defined

---

## Table of Contents

1. [RDF Ontology Designer Jobs](#rdf-ontology-designer-jobs)
2. [CLI Developer Jobs](#cli-developer-jobs)
3. [Operations Engineer Jobs](#operations-engineer-jobs)
4. [Data Analyst Jobs](#data-analyst-jobs)
5. [Documentation Writer Jobs](#documentation-writer-jobs)
6. [Cross-Cutting Jobs](#cross-cutting-jobs)
7. [Outcome Priority Matrix](#outcome-priority-matrix)

---

## RDF Ontology Designer Jobs

### Job 1.1: Create Domain Ontology from Requirements

**Job Statement:**
> Create a precise RDF ontology that models my domain semantics so I can generate type-safe code across multiple languages while maintaining semantic consistency.

**Circumstances:**
- Starting greenfield projects with complex domains
- Migrating legacy systems to ontology-first architecture
- Building API contracts that evolve without breaking changes
- Formalizing implicit domain knowledge

#### Outcomes

##### O1.1.1: Minimize time to bootstrap ontology structure
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: to create initial ontology file structure with namespaces and imports
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- `specify init` - Creates project structure with ontology scaffolding
- Template system - Provides example ontology patterns

**Measurement:**
```python
@timed  # OTEL span: ontology.bootstrap.duration
def initialize_ontology_structure():
    # Time from `specify init` to first valid ontology file
    pass
```

**Painpoints:**
- Forgetting required namespace declarations
- Inconsistent file organization across projects
- No guidance on recommended ontology patterns

**Progress Makers:**
- Pre-configured templates with common namespaces
- Example ontology files showing best practices
- Clear file naming conventions

---

##### O1.1.2: Maximize confidence that ontology captures all domain requirements
- **Direction**: Maximize
- **Metric**: Confidence score (1-5)
- **Object**: that ontology fully represents domain semantics
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- SHACL shape validation - Ensures ontology completeness
- Documentation generation - Makes ontology reviewable by non-technical stakeholders
- SPARQL queries - Enables ontology exploration and validation

**Measurement:**
- Survey ontology designers: "How confident are you that the ontology captures all requirements?"
- Coverage metric: % of domain concepts represented in ontology
- Review feedback: % of ontology reviews with semantic gaps identified

**Painpoints:**
- Hard to know if all edge cases are modeled
- No checklist for completeness review
- Difficult to get feedback from domain experts on RDF

**Progress Makers:**
- Generated Markdown documentation domain experts can review
- Ontology visualization tools (GraphViz output)
- SPARQL queries that verify expected patterns exist

---

##### O1.1.3: Minimize effort to refactor ontology structure
- **Direction**: Minimize
- **Metric**: Effort (hours)
- **Object**: to reorganize classes, properties, and relationships
- **Importance**: Medium
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- (Future) Ontology refactoring tools
- (Future) Automated migration scripts
- Git-based version control support

**Measurement:**
```python
@span("ontology.refactoring")
def refactor_ontology_classes(old_class, new_class):
    # Track: number of files touched, lines changed, compilation errors
    pass
```

**Painpoints:**
- Breaking changes cascade to all generated code
- Manual find-replace is error-prone
- Hard to preview refactoring impact
- No semantic-aware refactoring tools

**Progress Makers:**
- Clear deprecation warnings in generated code
- Migration guides auto-generated from ontology diffs
- Version-aware code generation

---

### Job 1.2: Validate Ontology Correctness

**Job Statement:**
> Validate that my RDF ontology has correct syntax and semantics so I can catch errors before they propagate to generated code.

**Circumstances:**
- Before committing ontology changes to git
- During code review of ontology pull requests
- When integrating ontologies from multiple sources
- After bulk ontology updates

#### Outcomes

##### O1.2.1: Minimize time to detect RDF syntax errors
- **Direction**: Minimize
- **Metric**: Time (seconds)
- **Object**: to identify Turtle syntax errors in ontology files
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- `specify check` - Validates RDF syntax
- Pre-commit hooks - Automatic validation before commit
- IDE integration - Real-time error feedback (planned)

**Measurement:**
```python
@timed
def validate_rdf_syntax(ontology_file: Path) -> ValidationResult:
    # Target: < 1 second for typical ontology
    # Metric: success rate, error detection rate
    pass
```

**Painpoints:**
- Manual validation is slow and forgotten
- Error messages don't point to specific lines
- Validation happens too late (CI/CD, not pre-commit)
- No integration with IDE for real-time feedback

**Progress Makers:**
- Fast validation (< 1s)
- Clear error messages with line numbers
- Git hook integration
- Watch mode for continuous validation

---

##### O1.2.2: Maximize likelihood of detecting SHACL violations
- **Direction**: Maximize
- **Metric**: Detection rate (%)
- **Object**: of semantic constraint violations before code generation
- **Importance**: High
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- SHACL shape validation in `specify check`
- (Future) SHACL constraint editor
- (Future) Custom constraint libraries

**Measurement:**
- Detection rate: % of known violations caught
- False positive rate: % of flagged issues that aren't real violations
- Coverage: % of SHACL shapes actually validated

**Painpoints:**
- SHACL error messages are cryptic
- Don't know which shapes to apply
- No guidance on writing good constraints
- Validation is all-or-nothing (no severity levels)

**Progress Makers:**
- Plain-English SHACL error explanations
- Shape libraries for common patterns
- Validation severity levels (error, warning, info)
- Fix suggestions for common violations

---

##### O1.2.3: Minimize number of steps to run complete validation
- **Direction**: Minimize
- **Metric**: Steps (count)
- **Object**: required to validate syntax, semantics, and constraints
- **Importance**: Medium
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- `specify check --validate-rdf` - One command for all validation
- Pre-commit hooks - Zero-step automatic validation
- CI/CD integration - Validation in pipeline

**Measurement:**
- Steps required: Manual count
- Automation rate: % of validations triggered automatically
- Developer workflow friction: Survey data

**Painpoints:**
- Have to run multiple tools manually
- Different tools have different interfaces
- Validation is not part of natural workflow
- No "validate all" command

**Progress Makers:**
- Single command for comprehensive validation
- Automatic validation on file save
- Integration with development workflow
- Fast feedback (< 5s for all checks)

---

### Job 1.3: Generate Code from Ontology

**Job Statement:**
> Transform my RDF ontology into type-safe code for Python, TypeScript, Rust, and other languages so I can maintain a single source of truth while supporting heterogeneous technology stacks.

**Circumstances:**
- After ontology updates
- Building microservices in multiple languages
- Supporting client libraries across platforms
- Ensuring type consistency across systems

#### Outcomes

##### O1.3.1: Minimize time to generate code from updated ontology
- **Direction**: Minimize
- **Metric**: Time (seconds)
- **Object**: to run ggen sync and produce type-safe code
- **Importance**: Medium
- **Current Satisfaction**: High (4/5)

**Addressing Features:**
- `ggen sync` - Fast code generation
- `specify ggen sync` - Wrapper with better error handling
- `--watch` mode - Automatic regeneration on file changes

**Measurement:**
```python
@timed
def ggen_sync(config: Path) -> CodeGenResult:
    # Target: < 5s for typical ontology
    # Metric: generation time, code size, language count
    pass
```

**Painpoints:**
- Have to manually run generation after changes
- Don't know if generation succeeded until checking files
- No progress indicator for large ontologies

**Progress Makers:**
- Fast generation (< 5s)
- Watch mode for automatic regeneration
- Progress feedback during generation
- Clear success/failure indication

---

##### O1.3.2: Maximize confidence that generated code matches ontology
- **Direction**: Maximize
- **Metric**: Confidence score (1-5)
- **Object**: that code faithfully represents ontology semantics
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- Deterministic code generation
- Round-trip validation (code → RDF → code)
- Generated tests that validate ontology constraints
- Documentation showing ontology → code mapping

**Measurement:**
- Round-trip accuracy: % of ontology recovered from generated code
- Constraint preservation: % of SHACL constraints enforced in code
- User confidence surveys

**Painpoints:**
- Can't verify generated code without deep inspection
- No visual mapping from ontology to code
- Unclear which ontology patterns map to which code patterns
- Template customization might break guarantees

**Progress Makers:**
- Code comments showing source ontology triples
- Side-by-side ontology/code documentation
- Validation that generated code satisfies SHACL shapes
- Template verification tools

---

##### O1.3.3: Minimize effort to support additional target languages
- **Direction**: Minimize
- **Metric**: Effort (hours)
- **Object**: to add code generation for new programming language
- **Importance**: Low
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- ggen template system
- Language-specific template libraries
- Template reuse across languages

**Measurement:**
- Time to add language: Engineer hours
- Template reuse: % of templates shared across languages
- Language coverage: Number of supported languages

**Painpoints:**
- Have to understand ggen template language
- No template debugger or validation
- Hard to test templates before using in production
- Limited documentation on template patterns

**Progress Makers:**
- Template examples for common languages
- Template testing framework
- Visual template editor (future)
- Template marketplace/sharing

---

## CLI Developer Jobs

### Job 2.1: Build Type-Safe CLI Commands from Specifications

**Job Statement:**
> Generate well-structured CLI commands from RDF ontology specifications so I can maintain consistent interfaces across all commands without manual boilerplate.

**Circumstances:**
- Adding new commands to existing CLI tool
- Refactoring inconsistent command structures
- Ensuring organizational CLI standards
- Onboarding new contributors

#### Outcomes

##### O2.1.1: Minimize time to add new CLI command
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: from RDF specification to working command implementation
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- RDF command specifications (`cli-commands.ttl`)
- Code generation from RDF to Typer commands
- Command template library

**Measurement:**
```python
@timed
def create_cli_command(command_spec: RDF) -> CommandModule:
    # Target: < 30 minutes
    # Includes: RDF spec, code generation, basic tests
    pass
```

**Painpoints:**
- Repetitive boilerplate for each command
- Inconsistent argument/option patterns
- Manual Typer setup for each command
- No template for common command patterns

**Progress Makers:**
- RDF spec automatically generates 80% of code
- Consistent patterns across all commands
- Auto-generated help text from RDF descriptions
- Type-safe command interfaces

---

##### O2.1.2: Maximize consistency across all CLI commands
- **Direction**: Maximize
- **Metric**: Consistency score (%)
- **Object**: of argument patterns, naming, error handling
- **Importance**: High
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- Enforced patterns via RDF schema
- Shared base command classes
- Linting rules for CLI consistency
- (Future) CLI consistency validator

**Measurement:**
- Consistency metrics:
  - % of commands with `--verbose` flag
  - % of commands with `--json` output
  - % of commands with standardized error handling
- Pattern violations detected in code review

**Painpoints:**
- Different developers use different patterns
- No enforcement of CLI conventions
- Inconsistencies discovered late (after merge)
- Manual consistency reviews are tedious

**Progress Makers:**
- RDF schema enforces conventions
- Auto-generated commands follow patterns
- CI/CD checks validate consistency
- Clear contribution guidelines

---

##### O2.1.3: Minimize effort to write comprehensive CLI tests
- **Direction**: Minimize
- **Metric**: Effort (hours)
- **Object**: to achieve 90%+ test coverage for CLI commands
- **Importance**: High
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- Auto-generated test suites from RDF specs
- Pytest fixtures for CLI testing
- Test coverage requirements in CI/CD

**Measurement:**
```python
@timed
def generate_cli_tests(command_spec: RDF) -> TestSuite:
    # Target: Tests generated automatically
    # Coverage: 90%+ for all commands
    pass
```

**Painpoints:**
- Writing tests is tedious and repetitive
- Easy to miss edge cases
- Maintaining tests when commands evolve
- No test generation from specs

**Progress Makers:**
- Tests generated from RDF specifications
- Automated edge case testing
- Test coverage tracked and enforced
- Easy to update tests when specs change

---

### Job 2.2: Validate CLI Consistency and Completeness

**Job Statement:**
> Ensure all CLI commands have complete help text, proper error handling, and consistent argument patterns so users have predictable, professional experience.

**Circumstances:**
- Before releasing new CLI version
- During code review of new commands
- When onboarding new contributors
- After major refactoring

#### Outcomes

##### O2.2.1: Maximize clarity of help text and error messages
- **Direction**: Maximize
- **Metric**: Clarity score (1-5)
- **Object**: of CLI documentation and error guidance
- **Importance**: Medium
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- Rich-formatted help text
- Typer's auto-generated documentation
- Error messages with suggested fixes
- (Future) Interactive error recovery

**Measurement:**
- User surveys: "How clear are error messages?"
- Help text completeness: % of commands with full documentation
- Error actionability: % of errors with clear next steps

**Painpoints:**
- Help text gets out of sync with implementation
- Error messages are generic and unhelpful
- No guidance on fixing errors
- Inconsistent terminology

**Progress Makers:**
- Help text auto-generated from RDF
- Structured error types with recovery hints
- Consistent terminology enforced
- Examples in help text

---

##### O2.2.2: Maximize confidence that CLI follows best practices
- **Direction**: Maximize
- **Metric**: Confidence score (1-5)
- **Object**: that CLI design follows industry standards
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- Typer framework (follows Click best practices)
- CLI design linting
- Best practices documentation
- Code reviews for CLI changes

**Measurement:**
- Best practice adherence: % of commands following guidelines
- Code review feedback: Issues per PR related to CLI design
- User experience surveys

**Painpoints:**
- No automated checking of CLI best practices
- Best practices documentation scattered
- Subjective interpretation of guidelines
- Hard to enforce consistency

**Progress Makers:**
- Automated CLI linting
- Clear best practices guide
- Examples of well-designed commands
- Code review checklist

---

## Operations Engineer Jobs

### Job 3.1: Validate System Health Before Deployment

**Job Statement:**
> Execute comprehensive validation checks on spec-kit tools and dependencies so I can ensure production deployments will succeed before rolling out changes.

**Circumstances:**
- Pre-deployment validation in CI/CD
- After infrastructure changes
- During incident recovery
- Before major releases

#### Outcomes

##### O3.1.1: Minimize time to validate deployment readiness
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: to run all health checks and validation workflows
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- `specify wf validate` - Comprehensive OTEL validation workflow
- `specify wf validate-quick` - 80/20 critical path validation
- `specify check` - Dependency and tool validation

**Measurement:**
```python
@timed
def validate_deployment_readiness() -> ValidationReport:
    # Target: < 5 minutes for full validation
    # Target: < 1 minute for quick validation
    pass
```

**Painpoints:**
- Validation takes too long (blocks deployment)
- Sequential validation wastes time
- Don't know which checks are critical
- Manual checklist validation

**Progress Makers:**
- Parallel validation execution
- Quick mode for critical checks only
- Clear pass/fail criteria
- Automated validation in CI/CD

---

##### O3.1.2: Maximize confidence in production health
- **Direction**: Maximize
- **Metric**: Confidence score (1-5)
- **Object**: that deployment will succeed without incidents
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- SpiffWorkflow-based validation orchestration
- OTEL instrumentation validation
- External project validation
- Health check aggregation

**Measurement:**
- Deployment success rate after validation
- Incident rate: Deployments with validation vs. without
- False positive rate: % of validation failures that weren't real issues

**Painpoints:**
- Validation doesn't catch all issues
- False positives undermine trust
- No historical validation data
- Unclear validation coverage

**Progress Makers:**
- Comprehensive validation coverage
- Low false positive rate (< 5%)
- Historical validation trends
- Clear coverage reporting

---

##### O3.1.3: Maximize coverage of validation checks
- **Direction**: Maximize
- **Metric**: Coverage (%)
- **Object**: of critical paths validated before deployment
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- SpiffWorkflow BPMN validation workflows
- Pluggable validation tasks
- Coverage reporting
- (Future) Validation gap analysis

**Measurement:**
- Path coverage: % of execution paths validated
- Dependency coverage: % of external dependencies checked
- Integration coverage: % of integrations validated

**Painpoints:**
- Don't know what's not being validated
- Adding new checks is manual
- Coverage gaps discovered during incidents
- No visibility into validation blind spots

**Progress Makers:**
- Coverage reporting in validation output
- Easy plugin architecture for new checks
- Gap analysis tools
- Validation recommendations

---

### Job 3.2: Monitor and Troubleshoot Production Issues

**Job Statement:**
> Trace request flows and performance bottlenecks using OpenTelemetry so I can quickly diagnose and resolve production incidents.

**Circumstances:**
- Active production incidents
- Performance degradation investigation
- Post-mortem analysis
- Proactive performance optimization

#### Outcomes

##### O3.2.1: Minimize mean time to diagnose incidents (MTTD)
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: to identify root cause of production issues
- **Importance**: High
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- OpenTelemetry trace instrumentation
- Span correlation across components
- Structured logging with trace context
- (Future) OTEL query interface

**Measurement:**
```python
# Incident timeline:
# - Time to first alert: MTTA
# - Time to start investigation: MTTE (engage)
# - Time to identify root cause: MTTD ← measure this
# - Time to resolve: MTTR

@span("incident.diagnosis", incident_id="INC-123")
def diagnose_incident(symptoms: List[str]) -> RootCause:
    # Target: < 15 minutes MTTD
    pass
```

**Painpoints:**
- Distributed traces hard to correlate
- Missing instrumentation in critical paths
- No centralized trace UI
- Traces expire before investigation completes

**Progress Makers:**
- Comprehensive instrumentation
- Long trace retention
- Trace visualization tools
- Automatic anomaly detection

---

##### O3.2.2: Maximize visibility into system performance
- **Direction**: Maximize
- **Metric**: Visibility score (1-5)
- **Object**: of request flows, dependencies, and bottlenecks
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- OpenTelemetry SDK integration
- Span attributes for business context
- Metrics correlation with traces
- Service dependency mapping

**Measurement:**
- Instrumentation coverage: % of functions with spans
- Attribute completeness: % of spans with required attributes
- Correlation success: % of traces with complete context

**Painpoints:**
- Blind spots in request flows
- Missing business context in traces
- Can't correlate metrics with traces
- No dependency visualization

**Progress Makers:**
- Automatic instrumentation where possible
- Standardized span attributes
- Unified observability platform
- Dependency graphs auto-generated

---

### Job 3.3: Batch Validate Multiple Projects

**Job Statement:**
> Run validation workflows across multiple external projects in parallel so I can ensure organization-wide quality gates are met efficiently.

**Circumstances:**
- Weekly quality audits
- Before major releases
- Compliance reporting
- Technical debt assessment

#### Outcomes

##### O3.3.1: Minimize effort to validate multiple projects
- **Direction**: Minimize
- **Metric**: Effort (hours)
- **Object**: to run validation across all organization projects
- **Importance**: Medium
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- `specify wf discover-projects` - Automatic project discovery
- `specify wf batch-validate` - Parallel batch validation
- `specify wf validate-8020` - Quick critical-path validation
- JSON export for reporting

**Measurement:**
```python
@timed
def batch_validate_projects(root: Path) -> BatchResults:
    # Target: < 10 minutes for 50 projects
    # Metric: projects/minute throughput
    pass
```

**Painpoints:**
- Manual validation of each project
- Sequential validation too slow
- Hard to aggregate results
- No project auto-discovery

**Progress Makers:**
- Automatic project discovery
- Parallel validation execution
- Aggregated reporting
- Export to BI tools

---

##### O3.3.2: Maximize accuracy of project discovery
- **Direction**: Maximize
- **Metric**: Accuracy (%)
- **Object**: of identifying Python projects in directory tree
- **Importance**: Medium
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- Heuristic-based project detection
- Configurable confidence thresholds
- Multiple indicator scoring
- Manual override support

**Measurement:**
- Precision: % of discovered projects that are real projects
- Recall: % of real projects discovered
- False positive rate: % of non-projects identified

**Painpoints:**
- Misses projects with non-standard layouts
- False positives on tool directories
- No customization for org-specific patterns
- Can't exclude known non-projects

**Progress Makers:**
- Configurable detection heuristics
- Organization-specific templates
- Exclusion patterns
- Confidence scoring

---

## Data Analyst Jobs

### Job 4.1: Discover Process Patterns from Event Logs

**Job Statement:**
> Extract process models from event logs using process mining so I can identify bottlenecks, deviations, and optimization opportunities.

**Circumstances:**
- Analyzing workflow efficiency
- Investigating process compliance
- Optimizing resource allocation
- Understanding user behavior

#### Outcomes

##### O4.1.1: Minimize time to import and analyze event logs
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: from raw CSV/XES file to process model visualization
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- `specify pm discover` - Process discovery from event logs
- Support for CSV and XES formats
- Multiple discovery algorithms (alpha, inductive, heuristic)
- Automatic visualization generation

**Measurement:**
```python
@timed
def discover_process_model(log_file: Path) -> ProcessModel:
    # Target: < 2 minutes for 10K events
    # Target: < 10 minutes for 1M events
    pass
```

**Painpoints:**
- Data preparation overhead
- Long processing times for large logs
- Format conversion required
- Manual algorithm selection

**Progress Makers:**
- Fast discovery algorithms
- Automatic format detection
- Algorithm recommendation
- Progress indicators

---

##### O4.1.2: Maximize accuracy of discovered process models
- **Direction**: Maximize
- **Metric**: Accuracy (%)
- **Object**: of process model vs. actual execution patterns
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- Inductive miner with noise filtering
- Configurable noise thresholds
- Model quality metrics
- Conformance checking validation

**Measurement:**
- Precision: % of modeled behavior that occurs in log
- Recall: % of logged behavior captured in model
- Fitness: % of log traces that fit model
- Simplicity: Model complexity score

**Painpoints:**
- Over-fitting to noise
- Under-fitting misses variants
- No quality metrics
- Can't compare algorithms

**Progress Makers:**
- Model quality scoring
- Algorithm comparison
- Noise parameter tuning
- Validation feedback

---

##### O4.1.3: Maximize clarity of conformance violations
- **Direction**: Maximize
- **Metric**: Clarity score (1-5)
- **Object**: of deviations between log and expected model
- **Importance**: High
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- `specify pm conform` - Conformance checking
- Deviation highlighting
- Violation categorization
- (Future) Root cause analysis

**Measurement:**
- Violation detection rate
- False positive rate
- Actionability: % of violations with clear cause
- User understanding surveys

**Painpoints:**
- Violations reported without context
- Don't know why deviations occurred
- Can't prioritize serious vs. minor violations
- No remediation suggestions

**Progress Makers:**
- Contextual violation reports
- Severity scoring
- Pattern analysis of violations
- Remediation recommendations

---

### Job 4.2: Extract Statistics from Event Logs

**Job Statement:**
> Generate statistical summaries of event logs so I can understand process performance, resource utilization, and throughput.

**Circumstances:**
- Creating executive dashboards
- Tracking KPIs over time
- Benchmarking process variants
- Supporting capacity planning

#### Outcomes

##### O4.2.1: Minimize time to generate statistical reports
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: to produce comprehensive log statistics
- **Importance**: Medium
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- `specify pm stats` - Event log statistics
- JSON output for BI tool integration
- Pre-configured report templates
- Export to CSV/Excel

**Measurement:**
```python
@timed
def generate_log_statistics(log_file: Path) -> Statistics:
    # Target: < 1 minute for 100K events
    # Metrics: case count, activity frequency, duration stats
    pass
```

**Painpoints:**
- Manual calculation tedious
- Export to BI tools manual
- No standard report format
- Limited visualization options

**Progress Makers:**
- One command for full statistics
- JSON export for automation
- BI tool integration
- Visualization generation

---

##### O4.2.2: Maximize ease of generating custom reports
- **Direction**: Maximize
- **Metric**: Ease score (1-5)
- **Object**: of creating tailored statistical reports
- **Importance**: Medium
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- (Future) Custom report templates
- (Future) SPARQL queries on event data
- (Future) Report builder UI

**Measurement:**
- Time to create custom report
- Coding skill required
- Template reuse rate

**Painpoints:**
- Custom reports require programming
- No template library
- Can't combine multiple metrics easily
- Inflexible output formats

**Progress Makers:**
- Report template library
- No-code report builder
- Flexible output formats
- Template sharing

---

## Documentation Writer Jobs

### Job 5.1: Generate Documentation from RDF Specifications

**Job Statement:**
> Transform RDF ontology specifications into comprehensive Markdown documentation so I can maintain accurate, up-to-date API references without manual rewriting.

**Circumstances:**
- After ontology updates
- During release preparation
- When onboarding new users
- For compliance documentation

#### Outcomes

##### O5.1.1: Minimize time to generate documentation from RDF
- **Direction**: Minimize
- **Metric**: Time (seconds)
- **Object**: to run ggen and produce complete Markdown docs
- **Importance**: High
- **Current Satisfaction**: High (4/5)

**Addressing Features:**
- `ggen sync` - Fast documentation generation
- Tera templates for Markdown
- SPARQL queries for content extraction
- Watch mode for continuous generation

**Measurement:**
```python
@timed
def generate_documentation(ontology: Path) -> DocumentationSet:
    # Target: < 5 seconds for typical ontology
    # Output: Complete Markdown documentation
    pass
```

**Painpoints:**
- Manual regeneration after changes
- Slow generation for large ontologies
- No incremental generation
- Unclear generation status

**Progress Makers:**
- Fast generation (< 5s)
- Watch mode for auto-regeneration
- Incremental generation
- Progress feedback

---

##### O5.1.2: Maximize accuracy of generated documentation
- **Direction**: Maximize
- **Metric**: Accuracy (%)
- **Object**: of documentation vs. source RDF ontology
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- Deterministic template transformation
- Round-trip validation
- Documentation testing
- Version synchronization

**Measurement:**
- Fact accuracy: % of documented facts correct
- Completeness: % of ontology concepts documented
- Freshness: Time since last regeneration

**Painpoints:**
- Can't verify documentation correctness
- Manual documentation can drift
- No testing for documentation
- Version mismatches

**Progress Makers:**
- Automated documentation testing
- Constitutional equation guarantees
- Version watermarks
- Drift detection

---

##### O5.1.3: Minimize effort to customize documentation templates
- **Direction**: Minimize
- **Metric**: Effort (hours)
- **Object**: to create branded, custom documentation formats
- **Importance**: Medium
- **Current Satisfaction**: Low (2/5)

**Addressing Features:**
- Tera template system
- Template libraries
- SPARQL query helpers
- Template documentation

**Measurement:**
- Time to customize template
- Template complexity (LOC)
- Skill level required

**Painpoints:**
- Tera syntax learning curve
- SPARQL queries complex
- No template debugger
- Limited template examples

**Progress Makers:**
- Template tutorials
- Template examples library
- Template testing framework
- Visual template editor (future)

---

### Job 5.2: Ensure Documentation Stays Synchronized

**Job Statement:**
> Keep documentation synchronized with evolving RDF ontology so readers always have current, accurate information.

**Circumstances:**
- During active development
- In CI/CD validation
- Before releases
- When drift detected

#### Outcomes

##### O5.2.1: Minimize likelihood of documentation drift
- **Direction**: Minimize
- **Metric**: Drift probability (%)
- **Object**: between RDF source and published documentation
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- Constitutional equation enforcement
- CI/CD documentation validation
- Git hooks for auto-regeneration
- Drift detection tools

**Measurement:**
- Drift incidents: Count per quarter
- Time to detect drift: Minutes
- Documentation freshness: Age since last generation

**Painpoints:**
- Manual regeneration forgotten
- Drift detected too late
- No automated sync
- Published docs out of date

**Progress Makers:**
- Automatic regeneration on commit
- CI/CD validation prevents drift
- Documentation deployment coupled with code
- Drift alerts

---

##### O5.2.2: Maximize confidence in documentation currency
- **Direction**: Maximize
- **Metric**: Confidence score (1-5)
- **Object**: that documentation reflects latest RDF state
- **Importance**: High
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- SHA256 receipt verification
- Version watermarks
- Last-updated timestamps
- Build provenance tracking

**Measurement:**
- User surveys: "How confident are you in doc accuracy?"
- Drift detection rate
- Documentation age distribution

**Painpoints:**
- Can't verify documentation is current
- No provenance information
- Manual verification tedious
- Trust issues with stale docs

**Progress Makers:**
- Cryptographic receipts
- Version verification tools
- Automatic currency checks
- Provenance display in docs

---

## Cross-Cutting Jobs

### Job X.1: Understand Tool Ecosystem and Dependencies

**Job Statement:**
> Verify that all required tools and dependencies are installed correctly so I can successfully use spec-kit without environment issues.

**Applies to:** All personas

**Circumstances:**
- Initial spec-kit installation
- After system updates
- Troubleshooting errors
- Setting up CI/CD

#### Outcomes

##### OX.1.1: Minimize time to diagnose missing dependencies
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: to identify which tools are missing or misconfigured
- **Importance**: High
- **Current Satisfaction**: High (4/5)

**Addressing Features:**
- `specify check` - Comprehensive tool validation
- `specify check --verbose` - Detailed diagnostic information
- `specify check --json` - Machine-readable output

**Measurement:**
```python
@timed
def check_dependencies() -> DependencyReport:
    # Target: < 10 seconds for all checks
    # Output: Required tools, optional tools, versions, paths
    pass
```

**Painpoints:**
- Trial-and-error to find missing tools
- Cryptic error messages
- Version compatibility unclear
- No installation guidance

**Progress Makers:**
- Fast comprehensive check
- Clear pass/fail for each tool
- Version compatibility warnings
- Installation instructions

---

### Job X.2: Learn Spec-Kit Capabilities and Usage

**Job Statement:**
> Discover what spec-kit can do and how to use it effectively so I can leverage the right tools for my jobs.

**Applies to:** All personas

**Circumstances:**
- Onboarding to spec-kit
- Exploring new features
- Solving unfamiliar problems
- Training new team members

#### Outcomes

##### OX.2.1: Minimize time to find relevant commands
- **Direction**: Minimize
- **Metric**: Time (minutes)
- **Object**: to identify which command solves my problem
- **Importance**: Medium
- **Current Satisfaction**: Medium (3/5)

**Addressing Features:**
- `specify --help` - Command listing
- Command groups (ggen, pm, wf)
- Rich CLI documentation
- (Future) Search functionality

**Measurement:**
- Time to find command: User studies
- Help text usage: Telemetry
- Support questions: Ticket analysis

**Painpoints:**
- Too many commands to browse
- Don't know which group has what I need
- No keyword search
- Examples lacking

**Progress Makers:**
- Organized command groups
- Keyword search
- Use case examples
- Interactive help

---

## Outcome Priority Matrix

### High-Importance, Low-Satisfaction (Top Priority)

These outcomes represent the biggest innovation opportunities:

| ID | Outcome | Persona | Importance | Satisfaction | Gap |
|----|---------|---------|------------|--------------|-----|
| O1.2.2 | Maximize SHACL violation detection | RDF Designer | High | Low | ⭐⭐⭐ |
| O1.2.3 | Minimize validation steps | RDF Designer | Medium | Low | ⭐⭐ |
| O1.3.2 | Maximize confidence in generated code | RDF Designer | High | Medium | ⭐⭐ |
| O2.1.2 | Maximize CLI consistency | CLI Developer | High | Low | ⭐⭐⭐ |
| O2.1.3 | Minimize test writing effort | CLI Developer | High | Low | ⭐⭐⭐ |
| O3.2.1 | Minimize MTTD | Ops Engineer | High | Low | ⭐⭐⭐ |
| O3.3.1 | Minimize batch validation effort | Ops Engineer | Medium | Low | ⭐⭐ |
| O4.1.3 | Maximize conformance clarity | Data Analyst | High | Low | ⭐⭐⭐ |
| O4.2.2 | Maximize custom report ease | Data Analyst | Medium | Low | ⭐⭐ |
| O5.1.3 | Minimize template customization effort | Doc Writer | Medium | Low | ⭐⭐ |

### High-Importance, High-Satisfaction (Maintain)

These outcomes are being delivered well—maintain quality:

| ID | Outcome | Persona | Importance | Satisfaction |
|----|---------|---------|------------|--------------|
| O1.3.1 | Minimize code generation time | RDF Designer | Medium | High |
| O5.1.1 | Minimize documentation generation time | Doc Writer | High | High |
| OX.1.1 | Minimize dependency diagnosis time | All | High | High |

### Innovation Focus Areas

Based on gap analysis, prioritize:

1. **SHACL Validation UX** (O1.2.2) - Improve error messages, detection rate
2. **CLI Test Generation** (O2.1.3) - Auto-generate comprehensive test suites
3. **OTEL Troubleshooting** (O3.2.1) - Better trace correlation, visualization
4. **Process Mining Insights** (O4.1.3) - Clearer conformance reporting
5. **Template Customization** (O5.1.3) - Easier Tera template development

---

**Next Steps:**
- [Why Features Exist](./why-features-exist.md) - Feature justifications mapped to outcomes
- [Measurement Strategy](./measurement-strategy.md) - How to track outcome delivery
- [Getting Started with JTBD](./getting-started.md) - Tutorial
