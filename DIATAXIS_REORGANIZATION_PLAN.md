# Diataxis Documentation Reorganization Plan

## Overview

This document outlines the reorganization of ggen Spec Kit documentation using the **Diataxis framework**, which divides documentation into four distinct types based on user needs and context.

---

## Diataxis Framework

The Diataxis framework organizes documentation into four quadrants:

```
                  Practical
                     ↑
                     │
      Tutorials ─────┼───── How-to Guides
      (Learning) │   │   │ (Tasks)
                 │   │   │
    ─────────────┼───┼───┼───────────→ Specific
                 │   │   │
   Reference ────┼───┼──→ Explanation
  (Information)  │   │    (Understanding)
                 │   │
    Theoretical  │   │
                 ↓
              General
```

### Four Documentation Types

1. **Tutorials** (Learning-oriented)
   - Goal: Help someone learn and understand the basics
   - Characteristics: Hands-on, practical, step-by-step, starts from zero
   - Audience: Complete beginners
   - Example: "Your First RDF Specification"

2. **How-to Guides** (Task-oriented)
   - Goal: Help someone accomplish a specific goal
   - Characteristics: Practical, procedural, goal-focused
   - Audience: Users with some experience
   - Example: "How to Add a CLI Command"

3. **Reference** (Information-oriented)
   - Goal: Provide authoritative technical information
   - Characteristics: Factual, organized for lookup, comprehensive
   - Audience: Developers looking for specific details
   - Example: "CLI Command Reference"

4. **Explanation** (Understanding-oriented)
   - Goal: Explain concepts, principles, and design decisions
   - Characteristics: Conceptual, contextual, discusses background
   - Audience: Users wanting to understand the "why"
   - Example: "Why RDF-First Development?"

---

## Current Documentation Mapping to Diataxis

### Existing Files by Category

#### TUTORIALS (Learning-oriented)
Currently scattered or missing:
- Quick start guides
- "Getting started" materials
- Hands-on walkthroughs
- First project setup

**Files to convert/create:**
- `docs/tutorials/01-getting-started.md` ← README.md quickstart sections
- `docs/tutorials/02-first-project.md` ← Installation + init
- `docs/tutorials/03-first-rdf-spec.md` ← RDF_WORKFLOW_GUIDE.md basics
- `docs/tutorials/04-first-test.md` ← COMMAND_TEST_QUICKSTART.md
- `docs/tutorials/05-first-ggen-sync.md` ← GGEN_PHASE2_GUIDE.md simplified
- `docs/tutorials/06-exploring-jtbd.md` ← JTBD_QUICK_REFERENCE.md intro
- `docs/tutorials/hyperdimensional-101.md` ← HYPERDIMENSIONAL_QUICKSTART.md

#### HOW-TO GUIDES (Task-oriented)
Currently scattered across many files:
- Procedural guides
- "How to X" documentation
- Step-by-step workflows
- Integration guides

**Files to create/reorganize:**
- `docs/guides/rdf/add-cli-command.md` ← From CLAUDE.md + ontology examples
- `docs/guides/rdf/write-rdf-specification.md` ← RDF_WORKFLOW_GUIDE.md detailed
- `docs/guides/rdf/custom-sparql-queries.md` ← SPARQL examples
- `docs/guides/rdf/use-tera-templates.md` ← Template examples
- `docs/guides/testing/setup-command-tests.md` ← COMMAND_TEST_GENERATION.md
- `docs/guides/testing/run-tests.md` ← pytest workflows
- `docs/guides/operations/run-ggen-sync.md` ← GGEN_SYNC_OPERATIONAL_RUNBOOKS.md
- `docs/guides/operations/troubleshoot-ggen.md` ← GGEN_SYNC_FMEA.md → solutions
- `docs/guides/architecture/implement-three-tier.md` ← CLAUDE.md architecture sections
- `docs/guides/jtbd/apply-jtbd-framework.md` ← JTBD_INTEGRATION_ROADMAP.md
- `docs/guides/deployment/setup-ci-cd.md` ← CI_CD_WORKFLOWS.md
- `docs/guides/observability/setup-otel.md` ← OpenTelemetry docs

#### REFERENCE (Information-oriented)
Currently the most comprehensive:
- API documentation
- Command reference
- Configuration reference
- Specifications reference

**Files to reorganize:**
- `docs/reference/cli-commands.md` ← docs/commands/*.md consolidated
- `docs/reference/rdf-ontology.md` ← GGEN_RDF_README.md
- `docs/reference/rdf-schema.md` ← Ontology schemas reference
- `docs/reference/sparql-queries.md` ← SPARQL query reference
- `docs/reference/tera-templates.md` ← Template reference
- `docs/reference/ggen-configuration.md` ← ggen.toml options
- `docs/reference/python-api.md` ← Python ops/runtime API
- `docs/reference/definition-of-done.md` ← DEFINITION_OF_DONE.md
- `docs/reference/jtbd-framework.md` ← JTBD concepts reference
- `docs/reference/quality-metrics.md` ← Coverage, performance targets

#### EXPLANATION (Understanding-oriented)
Currently scattered across philosophy and research docs:
- Architecture principles
- Design decisions
- "Why we do X"
- Foundational concepts

**Files to create/reorganize:**
- `docs/explanation/rdf-first-development.md` ← spec-driven.md + RDF_FIRST.md
- `docs/explanation/constitutional-equation.md` ← CONSTITUTIONAL_EQUATION.md
- `docs/explanation/three-tier-architecture.md` ← ARCHITECTURE.md
- `docs/explanation/why-jtbd-framework.md` ← JTBD_FRAMEWORK_RESEARCH.md
- `docs/explanation/spec-driven-philosophy.md` ← BLUE_OCEAN_THESIS_HUMANS_AS_FAILURE_MODE.md
- `docs/explanation/hyperdimensional-design.md` ← Hyperdimensional theoretical docs
- `docs/explanation/opentelemetry-design.md` ← OTEL instrumentation principles
- `docs/explanation/ggen-transformation-pipeline.md` ← GGEN_SYNC_ANALYSIS_README.md
- `docs/explanation/error-prevention-poka-yoke.md` ← GGEN_SYNC_POKA_YOKE.md

---

## New Documentation Directory Structure

```
/home/user/ggen-spec-kit/
├── README.md                           # Root entry point (updated to link to new structure)
├── QUICK_START.md                      # Direct link to tutorials
├── docs/
│   ├── index.md                        # Main documentation portal
│   │
│   ├── 📚 TUTORIALS/                   # Learning-oriented, hands-on guides
│   │   ├── 01-getting-started.md       # Install, verify, first look
│   │   ├── 02-first-project.md         # Create and initialize first project
│   │   ├── 03-first-rdf-spec.md        # Write your first RDF specification
│   │   ├── 04-first-test.md            # Create your first test
│   │   ├── 05-ggen-sync-first-time.md  # Run ggen sync for the first time
│   │   ├── 06-exploring-jtbd.md        # Introduction to JTBD framework
│   │   ├── 07-observability-basics.md  # First OpenTelemetry instrumentation
│   │   └── README.md                   # Tutorials index
│   │
│   ├── 🎯 GUIDES/                      # Task-oriented, goal-focused how-tos
│   │   ├── rdf/
│   │   │   ├── add-cli-command.md      # Add new CLI command from RDF
│   │   │   ├── write-rdf-spec.md       # Write complete RDF specification
│   │   │   ├── custom-sparql.md        # Create custom SPARQL queries
│   │   │   ├── tera-templates.md       # Build Tera code templates
│   │   │   └── README.md               # RDF guides index
│   │   ├── testing/
│   │   │   ├── setup-tests.md          # Set up test infrastructure
│   │   │   ├── run-tests.md            # Run and manage tests
│   │   │   ├── debug-tests.md          # Debug failing tests
│   │   │   └── README.md               # Testing guides index
│   │   ├── operations/
│   │   │   ├── run-ggen-sync.md        # Execute ggen sync transformations
│   │   │   ├── troubleshoot-ggen.md    # Troubleshoot ggen issues
│   │   │   ├── interpret-receipts.md   # Verify SHA256 receipts
│   │   │   └── README.md               # Operations guides index
│   │   ├── architecture/
│   │   │   ├── implement-three-tier.md # Build three-tier applications
│   │   │   ├── refactor-legacy.md      # Migrate to three-tier
│   │   │   └── README.md               # Architecture guides index
│   │   ├── jtbd/
│   │   │   ├── apply-framework.md      # Apply JTBD to your project
│   │   │   ├── measure-outcomes.md     # Define and measure outcomes
│   │   │   └── README.md               # JTBD guides index
│   │   ├── deployment/
│   │   │   ├── setup-ci-cd.md          # Set up CI/CD pipelines
│   │   │   ├── deploy-applications.md  # Deploy generate code
│   │   │   └── README.md               # Deployment guides index
│   │   ├── observability/
│   │   │   ├── setup-otel.md           # Configure OpenTelemetry
│   │   │   ├── view-traces.md          # Analyze OTEL traces
│   │   │   └── README.md               # Observability guides index
│   │   └── README.md                   # All guides index
│   │
│   ├── 📖 REFERENCE/                   # Authoritative, lookup-oriented information
│   │   ├── cli-commands.md             # All CLI commands reference
│   │   ├── rdf-ontology.md             # RDF ontology specification
│   │   ├── rdf-schema.md               # SHACL schema definitions
│   │   ├── sparql-queries.md           # Available SPARQL queries
│   │   ├── tera-templates.md           # Template syntax reference
│   │   ├── ggen-config.md              # ggen.toml configuration options
│   │   ├── python-api.md               # Python API reference
│   │   ├── config-files.md             # Configuration files reference
│   │   ├── environment-variables.md    # Environment variable reference
│   │   ├── quality-metrics.md          # Quality and performance targets
│   │   ├── error-codes.md              # Error codes and solutions
│   │   └── README.md                   # Reference index
│   │
│   ├── 💡 EXPLANATION/                 # Conceptual, understanding-oriented content
│   │   ├── rdf-first-development.md    # What is RDF-first development
│   │   ├── constitutional-equation.md  # The spec.md = μ(feature.ttl) principle
│   │   ├── three-tier-architecture.md  # Commands/Ops/Runtime separation
│   │   ├── why-jtbd-framework.md       # Jobs-to-be-Done benefits
│   │   ├── spec-driven-philosophy.md   # Philosophy behind spec-driven dev
│   │   ├── hyperdimensional-theory.md  # Hyperdimensional computing concepts
│   │   ├── opentelemetry-design.md     # Why and how we use OTEL
│   │   ├── ggen-pipeline.md            # Understanding the μ transformation
│   │   ├── error-prevention.md         # Poka-yoke error prevention
│   │   ├── governance/
│   │   │   ├── contributing.md         # Contribution philosophy
│   │   │   ├── code-of-conduct.md      # Community values
│   │   │   └── README.md               # Governance index
│   │   └── README.md                   # Explanation index
│   │
│   ├── 🔗 ECOSYSTEM/                   # Integration with external tools
│   │   ├── ai-agents.md                # Using AI agents (Claude Code)
│   │   ├── hyperdimensional-computing.md # HDC integration
│   │   ├── spiffworkflow.md            # BPMN via SpiffWorkflow
│   │   ├── process-mining.md           # PM4Py integration
│   │   └── README.md                   # Ecosystem index
│   │
│   ├── 🧪 EXAMPLES/                    # Concrete examples (organized by topic)
│   │   ├── rdf-specifications/         # Example RDF files
│   │   ├── python-code/                # Example Python implementations
│   │   ├── cli-commands/               # Example CLI command specs
│   │   ├── tera-templates/             # Example templates
│   │   ├── sparql-queries/             # Example SPARQL queries
│   │   └── README.md                   # Examples index
│   │
│   ├── 📊 RESEARCH/                    # Academic and in-depth research
│   │   ├── phd-thesis.md               # PhD thesis on RDF-spec-driven dev
│   │   ├── ggen-gap-analysis.md        # ggen transformation analysis
│   │   ├── ggen-fmea.md                # Failure Mode and Effects Analysis
│   │   ├── validation-report.md        # Comprehensive validation results
│   │   └── README.md                   # Research index
│   │
│   ├── docfx.json                      # DocFX configuration
│   └── ggen.toml                       # ggen transformation config
│
├── CLAUDE.md                           # (Keep at root for developer reference)
└── CONTRIBUTING.md                     # (Keep at root)
```

---

## Migration Plan: File Mappings

### Tutorials Migration

| Current Location | New Location | Content Updates |
|-----------------|--------------|-----------------|
| README.md (sections) | tutorials/01-getting-started.md | Simplify, make step-by-step |
| README.md (init section) | tutorials/02-first-project.md | Focus on first project |
| RDF_WORKFLOW_GUIDE.md (intro) | tutorials/03-first-rdf-spec.md | Beginner-friendly |
| COMMAND_TEST_QUICKSTART.md | tutorials/04-first-test.md | Simplified version |
| GGEN_PHASE2_GUIDE.md (intro) | tutorials/05-ggen-sync-first-time.md | First sync only |
| JTBD_QUICK_REFERENCE.md (intro) | tutorials/06-exploring-jtbd.md | Gentle introduction |
| HYPERDIMENSIONAL_QUICKSTART.md | tutorials/07-observability-basics.md | Basic OpenTelemetry |

### How-to Guides Migration

| Current Location | New Location | Content Updates |
|-----------------|--------------|-----------------|
| CLAUDE.md (commands section) | guides/rdf/add-cli-command.md | Extract as standalone |
| RDF_WORKFLOW_GUIDE.md (full) | guides/rdf/write-rdf-spec.md | Complete workflow |
| Examples + docs | guides/rdf/custom-sparql.md | SPARQL examples |
| Templates examples | guides/rdf/tera-templates.md | Template patterns |
| COMMAND_TEST_GENERATION.md | guides/testing/setup-tests.md | Setup instructions |
| docs/commands/*.md + examples | guides/testing/run-tests.md | Running tests |
| GGEN_SYNC_OPERATIONAL_RUNBOOKS.md | guides/operations/run-ggen-sync.md | Operating ggen |
| GGEN_SYNC_FMEA.md | guides/operations/troubleshoot-ggen.md | Solutions-focused |
| VERIFICATION_PROOF.md | guides/operations/interpret-receipts.md | Receipt verification |
| CLAUDE.md (three-tier section) | guides/architecture/implement-three-tier.md | Architecture patterns |
| JTBD_INTEGRATION_ROADMAP.md | guides/jtbd/apply-framework.md | Implementation guide |
| CI_CD_WORKFLOWS.md | guides/deployment/setup-ci-cd.md | CI/CD setup |
| OTEL docs + examples | guides/observability/setup-otel.md | OTEL configuration |

### Reference Migration

| Current Location | New Location | Content/Format |
|-----------------|--------------|-----------------|
| docs/commands/*.md (all) | reference/cli-commands.md | Consolidated table |
| GGEN_RDF_README.md | reference/rdf-ontology.md | RDF spec reference |
| ontology/*.ttl (extracted) | reference/rdf-schema.md | Schema definitions |
| sparql/*.rq files | reference/sparql-queries.md | Query catalog |
| templates/*.tera files | reference/tera-templates.md | Template reference |
| docs/ggen.toml | reference/ggen-config.md | Configuration options |
| CLAUDE.md (API sections) | reference/python-api.md | Function signatures |
| Multiple config files | reference/config-files.md | All configurations |
| DEFINITION_OF_DONE.md | reference/quality-metrics.md | Quality targets |
| Error handling docs | reference/error-codes.md | Error reference |

### Explanation Migration

| Current Location | New Location | Content Focus |
|-----------------|--------------|-----------------|
| spec-driven.md + RDF_FIRST.md | explanation/rdf-first-development.md | "Why RDF-first" |
| CONSTITUTIONAL_EQUATION.md | explanation/constitutional-equation.md | Full explanation |
| ARCHITECTURE.md | explanation/three-tier-architecture.md | Design rationale |
| JTBD_FRAMEWORK_RESEARCH.md | explanation/why-jtbd-framework.md | JTBD philosophy |
| BLUE_OCEAN_THESIS* | explanation/spec-driven-philosophy.md | Development philosophy |
| Hyperdimensional docs | explanation/hyperdimensional-theory.md | Theory + concepts |
| OTEL integration docs | explanation/opentelemetry-design.md | OTEL principles |
| GGEN_SYNC_ANALYSIS_README.md | explanation/ggen-pipeline.md | μ transformation |
| GGEN_SYNC_POKA_YOKE.md | explanation/error-prevention.md | Error prevention design |
| CONTRIBUTING.md | explanation/governance/contributing.md | Contribution philosophy |
| CODE_OF_CONDUCT.md | explanation/governance/code-of-conduct.md | Community values |

---

## Key Improvements

### 1. Clear User Pathways

**For Beginners:**
```
README → QUICK_START → tutorials/01 → tutorials/02 → tutorials/03
```

**For Developers:**
```
README → guides/rdf → guides/testing → guides/operations
```

**For Architects:**
```
README → explanation/three-tier → guides/architecture → reference/python-api
```

### 2. Better Information Architecture

- **Tutorials** are sequential and cumulative
- **Guides** are independent, task-focused reference items
- **Reference** is optimized for lookup and recall
- **Explanation** provides "why" for curious readers

### 3. Reduced Duplication

- Single source for each topic
- Clear inheritance: Tutorials → Guides → Reference
- Explanation provides depth without repetition

### 4. Improved Navigation

- Each section has a README with an index
- Cross-references between sections
- Sidebar/TOC navigation

---

## Implementation Steps

1. ✅ Analyze current documentation (DONE)
2. Create new directory structure
3. Migrate and rewrite tutorials
4. Convert guides from existing documentation
5. Consolidate reference documentation
6. Reorganize explanation content
7. Create new index and navigation files
8. Update README and entry points
9. Verify all links and cross-references
10. Commit changes with detailed message

---

## Navigation Enhancements

### Top-level Entry Points

**docs/index.md** - Documentation Portal
- Choose your path based on role/goal
- Quick links to all four sections
- Search and site map

**docs/tutorials/README.md** - Tutorial Index
- Sequential learning path
- Time estimates
- Prerequisites

**docs/guides/README.md** - Guides Index
- Organized by topic area
- Search/filter capabilities
- Quick links to specific tasks

**docs/reference/README.md** - Reference Index
- Alphabetical and categorical indexes
- API and specification reference
- Configuration tables

**docs/explanation/README.md** - Explanation Index
- Conceptual overview
- Deep dives and research

---

## Notes

- This maintains the RDF-first principle while improving user experience
- Generated files (from ggen sync) should be clearly marked
- Research and academic content stays in research/ folder
- Examples become a first-class citizen in examples/ folder
- CLAUDE.md stays at root as developer-focused reference

