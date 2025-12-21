# JTBD Customer Personas

## Overview

Spec-kit serves five primary personas, each with distinct jobs, desired outcomes, and contexts. This document provides detailed profiles for each persona to guide feature development and prioritization.

---

## Table of Contents

1. [RDF Ontology Designer](#1-rdf-ontology-designer)
2. [CLI Developer](#2-cli-developer)
3. [Operations Engineer](#3-operations-engineer)
4. [Data Analyst](#4-data-analyst)
5. [Documentation Writer](#5-documentation-writer)

---

## 1. RDF Ontology Designer

### Profile

**Who they are:**
- Software architects designing domain models
- Semantic web engineers building knowledge graphs
- Data engineers creating schema-first data platforms
- Research scientists formalizing domain knowledge

**Background:**
- Deep understanding of RDF, SPARQL, SHACL
- Familiar with ontology design patterns
- Values precision and semantic correctness
- Often works in research or highly regulated domains

**Tools they use:**
- Protégé, TopBraid Composer (ontology editors)
- SPARQL query engines (Jena, RDFLib)
- Git for version control
- VS Code or specialized RDF IDEs

### Primary Jobs

#### Job 1: Create Domain Ontology from Requirements

**Job Statement:**
> Create a precise RDF ontology that models my domain semantics so I can generate type-safe code across multiple languages while maintaining semantic consistency.

**Circumstances:**
- Starting a new project with complex domain logic
- Migrating legacy systems to schema-first architecture
- Building API contracts that need to evolve without breaking clients

**Functional Job:**
- Define classes, properties, and relationships in RDF/Turtle
- Establish SHACL constraints for validation
- Organize ontology files with clear namespaces

**Emotional Job:**
- Feel confident the ontology captures all domain nuances
- Feel proud of creating a reusable knowledge asset
- Avoid anxiety about missing edge cases

**Social Job:**
- Be recognized as a rigorous domain modeler
- Gain respect from peers for ontology design quality
- Demonstrate thought leadership in semantic technologies

#### Job 2: Validate Ontology Correctness

**Job Statement:**
> Validate that my RDF ontology has correct syntax and semantics so I can catch errors before they propagate to generated code.

**Circumstances:**
- Before committing ontology changes to git
- During code review of ontology pull requests
- When integrating ontologies from multiple sources

**Functional Job:**
- Check RDF/Turtle syntax errors
- Validate SHACL shape constraints
- Detect inconsistencies and contradictions

**Emotional Job:**
- Feel assured the ontology is correct
- Reduce stress of deploying broken schemas
- Gain confidence to refactor ontologies

**Social Job:**
- Avoid embarrassment of committing broken ontologies
- Be seen as thorough and detail-oriented
- Build trust with team through rigorous validation

#### Job 3: Generate Code from Ontology

**Job Statement:**
> Transform my RDF ontology into type-safe code for Python, TypeScript, Rust, and other languages so I can maintain a single source of truth while supporting heterogeneous technology stacks.

**Circumstances:**
- Building microservices in multiple languages
- Supporting client libraries across platforms
- Evolving schemas without breaking existing code

**Functional Job:**
- Run ggen sync to generate code
- Preview generated types before committing
- Validate generated code compiles correctly

**Emotional Job:**
- Trust that generated code faithfully represents ontology
- Feel empowered to evolve schemas confidently
- Enjoy automation replacing manual coding

**Social Job:**
- Be seen as modern and tool-savvy
- Demonstrate productivity gains to management
- Set new standards for schema-driven development

### Desired Outcomes

| Outcome | Direction | Importance | Current Satisfaction |
|---------|-----------|------------|---------------------|
| Time to detect syntax errors in ontology | Minimize | High | Medium |
| Likelihood of catching semantic inconsistencies | Maximize | High | Low |
| Time to generate code from updated ontology | Minimize | Medium | High |
| Confidence that generated code matches ontology | Maximize | High | Medium |
| Effort required to refactor ontology | Minimize | Medium | Low |
| Visibility into ontology structure and dependencies | Maximize | Medium | Medium |

### Painpoints

1. **Manual validation is tedious**: Running multiple tools (RDF validators, SHACL validators) separately
2. **Cryptic error messages**: SHACL violations are hard to interpret without deep expertise
3. **Late error detection**: Errors discovered during CI or production, not during development
4. **Ontology evolution anxiety**: Fear that changes will break downstream code
5. **No IDE integration**: Lack of real-time feedback while editing Turtle files
6. **Merge conflicts in RDF**: Hard to resolve conflicts in complex ontology files

### Success Metrics

- **Time to validate**: < 1 second for typical ontology (100-500 triples)
- **Error detection rate**: 95%+ of semantic errors caught before commit
- **Code generation time**: < 5 seconds for multi-language output
- **Refactoring confidence**: 80%+ confidence in safe ontology evolution

---

## 2. CLI Developer

### Profile

**Who they are:**
- Tool developers building command-line interfaces
- DevOps engineers creating automation scripts
- Platform engineers standardizing developer workflows
- Open-source maintainers building CLI-first tools

**Background:**
- Expert in Typer, Click, or argparse
- Values clean APIs and excellent UX
- Understands UNIX philosophy (composability, text streams)
- Focuses on developer experience

**Tools they use:**
- Python, Rust, or Go for CLI implementation
- Rich library for terminal UI
- pytest for testing
- GitHub Actions for CI/CD

### Primary Jobs

#### Job 1: Build Type-Safe CLI Commands from Specifications

**Job Statement:**
> Generate well-structured CLI commands from RDF ontology specifications so I can maintain consistent interfaces across all commands without manual boilerplate.

**Circumstances:**
- Adding new commands to existing CLI tool
- Refactoring inconsistent command structures
- Ensuring all commands follow organizational standards

**Functional Job:**
- Define command structure in RDF
- Generate Typer-based Python commands
- Ensure consistent argument/option patterns

**Emotional Job:**
- Avoid frustration of repetitive boilerplate code
- Feel confident CLI follows best practices
- Enjoy rapid iteration and experimentation

**Social Job:**
- Be recognized for creating intuitive, well-designed CLIs
- Build reputation for attention to UX details
- Demonstrate modern CLI development practices

#### Job 2: Validate CLI Consistency and Completeness

**Job Statement:**
> Ensure all CLI commands have complete help text, proper error handling, and consistent argument patterns so users have a predictable, professional experience.

**Circumstances:**
- Before releasing new CLI version
- During code review of new commands
- When onboarding new contributors

**Functional Job:**
- Check all commands have help text
- Validate argument types and defaults
- Ensure error messages are clear and actionable

**Emotional Job:**
- Feel proud of CLI polish and professionalism
- Reduce anxiety about missing edge cases
- Gain satisfaction from positive user feedback

**Social Job:**
- Build reputation for quality tooling
- Be seen as user-centric developer
- Set high standards for team

#### Job 3: Generate CLI Tests from Specifications

**Job Statement:**
> Automatically generate comprehensive test suites for CLI commands so I can ensure all commands work correctly without writing repetitive test code.

**Circumstances:**
- Implementing TDD for new commands
- Achieving high test coverage requirements
- Preventing regressions in command behavior

**Functional Job:**
- Generate pytest test cases from RDF specs
- Test all argument combinations
- Validate error handling and edge cases

**Emotional Job:**
- Trust that tests cover all scenarios
- Avoid tedium of writing boilerplate tests
- Feel secure making changes with safety net

**Social Job:**
- Demonstrate commitment to code quality
- Be seen as rigorous engineer
- Set testing standards for team

### Desired Outcomes

| Outcome | Direction | Importance | Current Satisfaction |
|---------|-----------|------------|---------------------|
| Time to add a new CLI command | Minimize | High | Medium |
| Consistency across all commands | Maximize | High | Low |
| Effort to write comprehensive tests | Minimize | High | Low |
| Clarity of help text and error messages | Maximize | Medium | Medium |
| Confidence that CLI follows best practices | Maximize | High | Medium |

### Painpoints

1. **Boilerplate code duplication**: Every command repeats similar patterns
2. **Inconsistent interfaces**: Different commands use different argument styles
3. **Manual test writing**: Tests are tedious and often incomplete
4. **Help text drift**: Documentation gets out of sync with implementation
5. **Type safety gaps**: Runtime errors from incorrect argument types
6. **Poor error messages**: Generic errors don't guide users to solutions

### Success Metrics

- **Time to add command**: < 30 minutes from spec to working implementation
- **Test coverage**: 90%+ for all CLI commands
- **Consistency score**: 100% of commands follow standard patterns
- **Help text completeness**: Every command, argument, and option documented

---

## 3. Operations Engineer

### Profile

**Who they are:**
- SREs managing production systems
- DevOps engineers building CI/CD pipelines
- Platform engineers ensuring infrastructure reliability
- Release engineers validating deployment readiness

**Background:**
- Expert in observability (OTEL, Prometheus, Grafana)
- Values automation and reproducibility
- Focuses on operational excellence
- Understands failure modes and resilience

**Tools they use:**
- Kubernetes, Docker for container orchestration
- Prometheus, Grafana for monitoring
- Jenkins, GitHub Actions for CI/CD
- Terraform for infrastructure as code

### Primary Jobs

#### Job 1: Validate System Health Before Deployment

**Job Statement:**
> Execute comprehensive validation checks on spec-kit tools and dependencies so I can ensure production deployments will succeed before rolling out changes.

**Circumstances:**
- Before deploying new version to production
- During CI/CD pipeline execution
- After infrastructure changes
- During incident recovery

**Functional Job:**
- Check all tool dependencies are installed
- Validate OTEL instrumentation is working
- Test SpiffWorkflow execution
- Verify external project integrations

**Emotional Job:**
- Feel confident deployment will succeed
- Reduce anxiety about production failures
- Sleep better knowing systems are validated

**Social Job:**
- Be recognized for operational excellence
- Build trust with development teams
- Demonstrate proactive problem prevention

#### Job 2: Monitor and Troubleshoot Production Issues

**Job Statement:**
> Trace request flows and performance bottlenecks using OpenTelemetry so I can quickly diagnose and resolve production incidents.

**Circumstances:**
- During active production incident
- When performance degradation reported
- During post-mortem analysis
- For proactive performance optimization

**Functional Job:**
- Query OTEL traces for specific requests
- Analyze span duration and dependencies
- Correlate logs with traces
- Identify error patterns

**Emotional Job:**
- Feel empowered to find root causes quickly
- Reduce frustration of blind debugging
- Gain satisfaction from fast incident resolution

**Social Job:**
- Be seen as reliable problem-solver
- Build reputation for rapid incident response
- Demonstrate observability expertise

#### Job 3: Batch Validate Multiple Projects

**Job Statement:**
> Run validation workflows across multiple external projects in parallel so I can ensure organization-wide quality gates are met efficiently.

**Circumstances:**
- Weekly quality audits across organization
- Before major release across products
- Compliance reporting requirements
- Technical debt assessment

**Functional Job:**
- Discover Python projects in directory
- Execute validation workflows in parallel
- Aggregate results across projects
- Generate compliance reports

**Emotional Job:**
- Trust that automation catches issues
- Avoid tedium of manual validation
- Feel organized and in control

**Social Job:**
- Be recognized for process automation
- Demonstrate scalability of quality practices
- Set standards for organizational excellence

### Desired Outcomes

| Outcome | Direction | Importance | Current Satisfaction |
|---------|-----------|------------|---------------------|
| Time to validate deployment readiness | Minimize | High | Medium |
| Confidence in production health | Maximize | High | Medium |
| Mean time to diagnose incidents (MTTD) | Minimize | High | Low |
| Coverage of validation checks | Maximize | High | Medium |
| Effort to validate multiple projects | Minimize | Medium | Low |
| Visibility into system performance | Maximize | High | Medium |

### Painpoints

1. **Manual validation steps**: Checklist-based validation is error-prone
2. **Limited observability**: Hard to trace issues across components
3. **Slow validation**: Sequential checks take too long
4. **False positives**: Noisy validation failures obscure real issues
5. **No baseline metrics**: Can't detect performance degradation
6. **Siloed tools**: Different validation tools don't integrate

### Success Metrics

- **Validation time**: < 5 minutes for full OTEL validation
- **Incident MTTD**: < 15 minutes average
- **Validation coverage**: 95%+ of critical paths checked
- **False positive rate**: < 5% of validation failures

---

## 4. Data Analyst

### Profile

**Who they are:**
- Business analysts mining process data
- Data scientists analyzing workflow patterns
- Quality engineers tracking metrics
- Product managers understanding user behavior

**Background:**
- Familiar with SQL, pandas, data visualization
- Values data-driven decision making
- Focuses on insights and actionable recommendations
- May have limited programming expertise

**Tools they use:**
- Jupyter notebooks for analysis
- pandas, matplotlib for data manipulation
- Tableau, Grafana for visualization
- SQL databases for storage

### Primary Jobs

#### Job 1: Discover Process Patterns from Event Logs

**Job Statement:**
> Extract process models from event logs using process mining so I can identify bottlenecks, deviations, and optimization opportunities.

**Circumstances:**
- Analyzing workflow efficiency
- Investigating process compliance
- Optimizing resource allocation
- Understanding user behavior patterns

**Functional Job:**
- Import CSV/XES event logs
- Run discovery algorithms (inductive, heuristic)
- Visualize discovered process models
- Export results for reporting

**Emotional Job:**
- Feel empowered to find insights in data
- Avoid frustration with complex tools
- Gain satisfaction from actionable findings

**Social Job:**
- Be recognized for data-driven insights
- Build credibility with stakeholders
- Demonstrate analytical expertise

#### Job 2: Measure Conformance to Expected Processes

**Job Statement:**
> Check whether actual execution traces conform to expected process models so I can detect deviations and ensure compliance.

**Circumstances:**
- Auditing process compliance
- Validating workflow implementations
- Investigating anomalies
- Generating compliance reports

**Functional Job:**
- Load event log and reference model
- Run conformance checking (token replay, alignment)
- Identify non-conforming cases
- Generate compliance metrics

**Emotional Job:**
- Trust that analysis is accurate
- Feel confident presenting findings
- Avoid anxiety about missing violations

**Social Job:**
- Be seen as rigorous analyst
- Build trust through thorough analysis
- Demonstrate compliance expertise

#### Job 3: Extract Statistics from Event Logs

**Job Statement:**
> Generate statistical summaries of event logs so I can understand process performance, resource utilization, and throughput.

**Circumstances:**
- Creating executive dashboards
- Tracking KPIs over time
- Benchmarking process variants
- Supporting capacity planning

**Functional Job:**
- Calculate case duration statistics
- Analyze activity frequencies
- Measure resource utilization
- Identify bottleneck activities

**Emotional Job:**
- Feel confident statistics are correct
- Enjoy ease of generating reports
- Gain satisfaction from clear insights

**Social Job:**
- Be recognized for reporting quality
- Build reputation for reliable analysis
- Demonstrate business acumen

### Desired Outcomes

| Outcome | Direction | Importance | Current Satisfaction |
|---------|-----------|------------|---------------------|
| Time to import and analyze event logs | Minimize | High | Medium |
| Accuracy of discovered process models | Maximize | High | Medium |
| Clarity of conformance violations | Maximize | High | Low |
| Ease of generating statistical reports | Maximize | Medium | Medium |
| Effort to visualize process insights | Minimize | Medium | Low |

### Painpoints

1. **Steep learning curve**: Process mining tools require expertise
2. **Data preparation overhead**: Event logs need significant cleanup
3. **Limited visualization options**: Hard to create compelling visuals
4. **No statistical context**: Don't know if findings are significant
5. **Manual export to BI tools**: No direct integration with Tableau/PowerBI
6. **Unclear error messages**: Hard to debug when analysis fails

### Success Metrics

- **Time to first insight**: < 10 minutes from raw log to process model
- **Analysis accuracy**: 90%+ precision in deviation detection
- **Report generation**: < 5 minutes for standard statistics
- **User skill required**: Usable by analysts with basic Python knowledge

---

## 5. Documentation Writer

### Profile

**Who they are:**
- Technical writers creating API documentation
- Developer advocates writing guides and tutorials
- Open-source maintainers keeping docs current
- Product managers documenting features

**Background:**
- Strong writing and communication skills
- Familiar with Markdown, static site generators
- Values accuracy and completeness
- May have limited programming knowledge

**Tools they use:**
- VS Code or Markdown editors
- MkDocs, Docusaurus for static sites
- Git for version control
- Grammarly or similar writing tools

### Primary Jobs

#### Job 1: Generate Documentation from RDF Specifications

**Job Statement:**
> Transform RDF ontology specifications into comprehensive Markdown documentation so I can maintain accurate, up-to-date API references without manual rewriting.

**Circumstances:**
- After ontology updates
- During release preparation
- When onboarding new users
- For compliance documentation

**Functional Job:**
- Run ggen sync to generate Markdown
- Preview generated documentation
- Customize templates for branding
- Publish to documentation site

**Emotional Job:**
- Trust documentation matches implementation
- Avoid anxiety about outdated docs
- Feel proud of professional documentation

**Social Job:**
- Be recognized for documentation quality
- Build reputation for clear communication
- Set documentation standards

#### Job 2: Ensure Documentation Stays Synchronized

**Job Statement:**
> Keep documentation synchronized with evolving RDF ontology so readers always have current, accurate information.

**Circumstances:**
- During active development
- In CI/CD validation
- Before releases
- When documentation drift detected

**Functional Job:**
- Detect when RDF changes affect docs
- Validate documentation completeness
- Regenerate affected sections
- Review and approve updates

**Emotional Job:**
- Feel secure docs won't drift
- Reduce stress of manual sync
- Gain satisfaction from automation

**Social Job:**
- Be seen as maintaining high standards
- Avoid embarrassment of stale docs
- Build trust through consistency

#### Job 3: Create Custom Documentation Templates

**Job Statement:**
> Design Tera templates that transform RDF data into branded, well-structured documentation so our docs have consistent style and formatting.

**Circumstances:**
- Establishing documentation standards
- Rebranding documentation site
- Supporting multiple doc formats
- Creating specialized reports

**Functional Job:**
- Write Tera templates with SPARQL queries
- Test template output
- Version control templates
- Share templates across team

**Emotional Job:**
- Feel empowered to customize docs
- Enjoy creative control over presentation
- Gain confidence in template quality

**Social Job:**
- Be recognized for design skills
- Demonstrate technical capability
- Set documentation aesthetic standards

### Desired Outcomes

| Outcome | Direction | Importance | Current Satisfaction |
|---------|-----------|------------|---------------------|
| Time to generate docs from RDF | Minimize | High | High |
| Accuracy of generated documentation | Maximize | High | Medium |
| Effort to customize doc templates | Minimize | Medium | Low |
| Likelihood of documentation drift | Minimize | High | Medium |
| Completeness of generated docs | Maximize | High | Medium |

### Painpoints

1. **Documentation drift**: Manually-written docs get out of sync
2. **Tedious regeneration**: Have to manually update docs after every change
3. **Limited template flexibility**: Hard to customize generated output
4. **No preview mode**: Can't see output before committing
5. **Unclear SPARQL**: Hard to write queries for custom templates
6. **Version mismatch**: Docs for wrong version get published

### Success Metrics

- **Generation time**: < 5 seconds for full documentation
- **Drift detection**: 100% of RDF changes trigger doc updates
- **Template customization**: Writers can create templates without programming
- **Documentation accuracy**: 0 incorrect facts in generated docs

---

## Persona Summary Table

| Persona | Primary Tool Usage | Top Job | Critical Outcome | Biggest Painpoint |
|---------|-------------------|---------|------------------|-------------------|
| **RDF Ontology Designer** | ggen, SHACL validators | Create domain ontology | Time to detect syntax errors | Late error detection |
| **CLI Developer** | Typer, pytest, Rich | Build type-safe CLI commands | Time to add new command | Boilerplate duplication |
| **Operations Engineer** | Docker, OTEL, CI/CD | Validate deployment health | Confidence in production | Limited observability |
| **Data Analyst** | pm4py, pandas | Discover process patterns | Time to first insight | Steep learning curve |
| **Documentation Writer** | ggen, MkDocs | Generate docs from RDF | Documentation accuracy | Documentation drift |

---

## Using These Personas

### In Feature Planning

For each proposed feature, ask:
1. **Which persona** does this serve?
2. **What job** does it help accomplish?
3. **Which outcomes** does it improve?
4. **What painpoints** does it address?

### In Prioritization

Use this framework:
- **High Priority**: High-importance outcome + low satisfaction + affects multiple personas
- **Medium Priority**: High-importance outcome + medium satisfaction + affects one persona
- **Low Priority**: Medium-importance outcome + high satisfaction

### In Measurement

Track these metrics per persona:
- **Adoption rate**: % of persona using the feature
- **Job success rate**: % of job executions that succeed
- **Outcome satisfaction**: Rating of outcome delivery (1-5)
- **NPS by persona**: Net Promoter Score segmented by persona

---

**Next Steps:**
- [Jobs & Outcomes Catalog](./jobs-outcomes-catalog.md) - Complete job inventory
- [Why Features Exist](./why-features-exist.md) - Feature justifications
- [Measurement Strategy](./measurement-strategy.md) - How to track outcomes
