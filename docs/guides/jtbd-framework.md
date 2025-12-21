# Jobs To Be Done (JTBD) Framework in Spec-Kit

## Table of Contents

- [What is Jobs To Be Done?](#what-is-jobs-to-be-done)
- [Core JTBD Principles](#core-jtbd-principles)
- [JTBD vs. Feature-Driven Development](#jtbd-vs-feature-driven-development)
- [Why Spec-Kit Uses JTBD](#why-spec-kit-uses-jtbd)
- [JTBD Methodology in Practice](#jtbd-methodology-in-practice)
- [The JTBD Framework Components](#the-jtbd-framework-components)
- [Integrating JTBD with RDF Specifications](#integrating-jtbd-with-rdf-specifications)

---

## What is Jobs To Be Done?

**Jobs To Be Done (JTBD)** is a customer-centric framework that focuses on understanding the fundamental job a customer is trying to accomplish, rather than simply building features or products. The core insight of JTBD is that customers don't buy products or features—they "hire" solutions to make progress in specific circumstances.

### The JTBD Definition

> "A Job to be Done is the progress that a person is trying to make in a particular circumstance."
> — Clayton Christensen

When we build software, we're not building features for their own sake. We're helping users make progress toward their goals. JTBD helps us understand:

- **What job** the customer is hiring our tool to do
- **What circumstances** trigger the need for this job
- **What outcomes** define successful progress
- **What obstacles** prevent them from making progress

### The Classic Example: Milkshake Marketing

Clayton Christensen's famous milkshake study illustrates JTBD perfectly:

A fast-food restaurant wanted to increase milkshake sales. Traditional market research asked: "How can we improve our milkshakes?" (feature-driven thinking).

JTBD research instead asked: "What job are customers hiring a milkshake to do?"

The surprising answer: morning commuters hired milkshakes to make their boring commute more interesting and keep them full until lunch. The "job" wasn't nutrition or taste—it was **"make my commute less boring while keeping me satisfied."**

This insight led to very different improvements than "make it thicker" or "add more flavors."

---

## Core JTBD Principles

### 1. Functional, Emotional, and Social Jobs

Every job has three dimensions:

**Functional Job (Task-oriented)**
- The practical task the customer needs to accomplish
- Example: "Transform RDF specifications into Markdown documentation"

**Emotional Job (Feeling-oriented)**
- How the customer wants to feel while doing the job
- Example: "Feel confident that my generated documentation is accurate and complete"

**Social Job (Perception-oriented)**
- How the customer wants to be perceived by others
- Example: "Be seen as a rigorous engineer who maintains high-quality documentation"

### 2. Jobs Are Stable, Solutions Change

- **Jobs remain constant** over time (people have wanted to "communicate across distance" for centuries)
- **Solutions evolve** rapidly (telegraph → telephone → email → messaging apps)

This stability makes JTBD an excellent foundation for long-term product strategy.

### 3. Jobs Have Context

The same person might hire different solutions for the same functional job depending on circumstances:

- **Circumstance 1**: RDF ontology designer creating a new domain model → hires `specify init` to bootstrap project
- **Circumstance 2**: Operations engineer deploying to production → hires `specify wf validate` to ensure quality gates pass

### 4. Outcome-Driven Innovation

Customers don't want features—they want **outcomes**. Each job has measurable outcomes that define success:

- **Direction**: Minimize or maximize
- **Metric**: What to measure
- **Context**: When/where it matters

Example outcome: "Minimize the time it takes to validate RDF syntax errors in my ontology files"

### 5. Jobs Competition

Customers don't just compare your tool to competitors—they compare it to **all alternative ways** of getting the job done:

- Direct competitors (other RDF tools)
- Indirect solutions (manual validation, custom scripts)
- Non-consumption (not doing the job at all)

Understanding this broader competition reveals true innovation opportunities.

---

## JTBD vs. Feature-Driven Development

### Feature-Driven Development

**Approach**: Build features customers request

**Question**: "What features do users want?"

**Example**:
- User request: "Add a `--watch` flag to ggen sync"
- Response: Build the `--watch` flag
- Result: Feature exists, but may not solve the underlying job

**Problems**:
- Features don't guarantee progress toward goals
- Leads to feature bloat without addressing core jobs
- Different users want conflicting features
- Hard to prioritize feature requests objectively

### Jobs To Be Done Development

**Approach**: Understand the job, then design the best solution

**Question**: "What job is the user trying to accomplish?"

**Example**:
- Job: "Keep generated documentation synchronized with evolving RDF ontology"
- Research: What circumstances trigger this job? How often? What outcomes matter?
- Solution: `--watch` flag is ONE possible solution, but understanding the job might reveal better approaches:
  - Git hooks that auto-sync on commit
  - IDE integration for real-time preview
  - CI/CD validation that fails on drift
  - SPARQL-based change detection

**Benefits**:
- Reveals innovative solutions beyond initial requests
- Provides objective prioritization criteria (which outcomes matter most?)
- Unifies seemingly different feature requests under common jobs
- Enables measurement of actual progress, not just feature delivery

### Comparison Table

| Aspect | Feature-Driven | Jobs-Driven |
|--------|---------------|-------------|
| **Focus** | What to build | Why users need it |
| **Unit of value** | Features shipped | Outcomes achieved |
| **Prioritization** | Feature requests, opinions | Job importance, outcome criticality |
| **Success metric** | Features delivered | Progress enabled |
| **Innovation** | Incremental improvements | Breakthrough solutions |
| **Requirements** | "Add X feature" | "Help me accomplish Y job" |
| **Competition** | Other products with similar features | All ways to get the job done |

---

## Why Spec-Kit Uses JTBD

Spec-kit adopts JTBD for five strategic reasons:

### 1. **Aligns with Specification-Driven Development Philosophy**

JTBD's focus on **outcomes over outputs** mirrors spec-kit's constitutional principle:

```
spec.md = μ(feature.ttl)
```

Just as this equation says "documentation is a transformation of specifications" (outcome-focused), JTBD says "features are solutions to jobs" (outcome-focused).

### 2. **Enables Multi-Language Code Generation**

Spec-kit generates code for Python, TypeScript, Rust, Java, C#, and Go from a single RDF ontology. JTBD helps by:

- **Identifying common jobs** across all languages (e.g., "validate ontology syntax")
- **Understanding language-specific circumstances** that change solution approaches
- **Defining universal outcomes** that apply regardless of target language

### 3. **Provides Clear Measurement Strategy**

JTBD's outcome-driven approach integrates naturally with spec-kit's OpenTelemetry instrumentation:

- **Jobs** become span names in OTEL traces
- **Outcomes** become measurable attributes
- **Progress** becomes observable in production telemetry

Example:
```python
@timed  # Measures "minimize time to transform RDF"
def ggen_sync():
    with span("ggen.sync", outcome="documentation_generated"):
        # Implementation
```

### 4. **Supports the Constitutional Equation**

The constitutional equation `spec.md = μ(feature.ttl)` implies that **all features derive from specifications**. JTBD provides the framework for specifying the "why":

- **RDF ontology** defines WHAT the feature does (functional model)
- **JTBD specification** defines WHY the feature exists (customer job)
- **Together** they enable deterministic, purpose-driven code generation

### 5. **Facilitates Multi-Persona Product Development**

Spec-kit serves multiple distinct personas:

- RDF ontology designers
- CLI developers
- Operations engineers
- Data analysts
- Documentation writers

JTBD prevents building for a "generic user" by identifying **specific jobs for specific personas in specific circumstances**.

---

## JTBD Methodology in Practice

### Step 1: Identify the Job

**Questions to ask:**
- What is the user fundamentally trying to accomplish?
- What progress are they trying to make?
- What situation triggers the need for this job?

**Example:**
- Job: "Ensure my RDF ontology conforms to SHACL shape constraints before committing to git"
- Circumstance: Developer about to commit changes to ontology files
- Functional dimension: Validate syntax and semantic constraints
- Emotional dimension: Feel confident the ontology is correct
- Social dimension: Maintain reputation as a rigorous ontology designer

### Step 2: Identify Desired Outcomes

**Format:** [Direction] the [metric] to [object of control] when [contextual clarifier]

**Examples:**
- "Minimize the time it takes to discover RDF syntax errors"
- "Maximize the likelihood that SHACL validation catches semantic errors"
- "Minimize the number of steps required to run a complete validation"

### Step 3: Identify Obstacles (Painpoints)

What prevents users from achieving desired outcomes today?

**Examples:**
- Manual validation is slow and error-prone
- SHACL error messages are cryptic and hard to interpret
- Validation happens too late (after commit or during CI)
- No integration with existing development workflow

### Step 4: Identify Progress Makers (What helps them make progress?)

**Examples:**
- Fast feedback loop (results in < 1 second)
- Clear, actionable error messages with line numbers
- Git hook integration for automatic pre-commit validation
- IDE integration for real-time feedback

### Step 5: Design Solutions

Now that you understand the job, outcomes, and obstacles, design features that deliver outcomes:

**Solution: `specify check --validate-rdf` command**
- **Outcome delivered**: Minimize time to discover errors (< 1s feedback)
- **Painpoint addressed**: Manual validation eliminated
- **Progress maker**: Git hook integration available

---

## The JTBD Framework Components

### Job Statement Format

```
[Action verb] [Object of action] so I can [expected outcome] in [context/circumstance]
```

**Example:**
```
Transform RDF ontology specifications into Markdown documentation
so I can maintain up-to-date API references
during iterative ontology evolution
```

### Outcome Statement Format

```
[Direction: Minimize/Maximize] [Unit of measure] [Object of control] [Contextual clarifier]
```

**Example:**
```
Minimize the time it takes to generate documentation from updated RDF files
```

### Job Map (Process Steps)

Every job follows a process with 8 universal steps:

1. **Define** - Determine goals and plan approach
2. **Locate** - Gather inputs and resources
3. **Prepare** - Set up environment and prerequisites
4. **Confirm** - Validate that setup is correct
5. **Execute** - Perform the core task
6. **Monitor** - Track progress and status
7. **Modify** - Make adjustments as needed
8. **Conclude** - Complete the job and finalize

Each step has its own sub-jobs and outcomes.

**Example Job Map: "Generate Documentation from RDF"**

| Step | Sub-job | Outcome |
|------|---------|---------|
| **Define** | Determine which ontology files to process | Minimize time to identify target files |
| **Locate** | Find RDF source files and templates | Minimize likelihood of missing dependencies |
| **Prepare** | Validate RDF syntax and SHACL constraints | Minimize likelihood of generation failures |
| **Confirm** | Preview output structure | Maximize confidence that output will be correct |
| **Execute** | Run ggen sync transformation | Minimize time to complete generation |
| **Monitor** | Watch transformation progress | Maximize awareness of generation status |
| **Modify** | Adjust templates or queries if needed | Minimize iterations required |
| **Conclude** | Verify output and commit results | Maximize confidence in documentation accuracy |

---

## Integrating JTBD with RDF Specifications

Spec-kit uniquely combines JTBD with RDF-first development. Here's how they integrate:

### RDF Vocabulary for JTBD

```turtle
@prefix jtbd: <http://github.com/github/spec-kit/jtbd#> .
@prefix cli: <http://github.com/github/spec-kit/cli#> .

# Define a job
jtbd:ValidateOntologyJob a jtbd:Job ;
    rdfs:label "Validate RDF Ontology Syntax and Semantics" ;
    jtbd:functionalJob "Ensure ontology files are valid RDF/Turtle and conform to SHACL shapes" ;
    jtbd:emotionalJob "Feel confident that ontology is correct before sharing with team" ;
    jtbd:socialJob "Be seen as thorough and rigorous in ontology design" ;
    jtbd:circumstance "Before committing ontology changes to version control" ;
    jtbd:persona jtbd:RDFOntologyDesigner .

# Define outcomes
jtbd:MinimizeValidationTime a jtbd:Outcome ;
    rdfs:label "Minimize validation time" ;
    jtbd:direction "minimize" ;
    jtbd:metric "time" ;
    jtbd:objectOfControl "it takes to validate all ontology files" ;
    jtbd:importance "high" ;
    jtbd:satisfaction "low" .  # Current solutions don't satisfy this well

# Link outcomes to jobs
jtbd:ValidateOntologyJob jtbd:hasOutcome jtbd:MinimizeValidationTime .

# Link features to outcomes
cli:CheckCommand jtbd:delivers jtbd:MinimizeValidationTime ;
    jtbd:accomplishesJob jtbd:ValidateOntologyJob .
```

### Benefits of RDF-Encoded JTBD

1. **Machine-Readable Jobs**: AI agents can reason about which jobs features accomplish
2. **Traceability**: Link features → outcomes → jobs → personas
3. **Validation**: Ensure every feature maps to at least one job
4. **Prioritization**: Query RDF to find high-importance, low-satisfaction outcomes
5. **Documentation Generation**: Auto-generate "Why this feature exists" docs from RDF
6. **Measurement**: OTEL spans automatically tagged with job/outcome metadata

### Example SPARQL Query: Find Underserved Jobs

```sparql
PREFIX jtbd: <http://github.com/github/spec-kit/jtbd#>

SELECT ?job ?outcome ?importance ?satisfaction
WHERE {
  ?job a jtbd:Job ;
       jtbd:hasOutcome ?outcome .

  ?outcome jtbd:importance "high" ;
           jtbd:satisfaction "low" .

  FILTER NOT EXISTS {
    ?feature jtbd:delivers ?outcome .
  }
}
```

This query finds high-importance outcomes with low current satisfaction and no features delivering them—prime innovation opportunities.

---

## Summary

**Jobs To Be Done** transforms how we build software:

- **From**: Building features users request
- **To**: Understanding jobs users need done and designing optimal solutions

**Core JTBD principles**:
1. Focus on functional, emotional, and social job dimensions
2. Jobs are stable, solutions evolve
3. Context matters—same job, different circumstances
4. Measure outcomes, not feature delivery
5. Compete against all ways to get the job done

**Why spec-kit uses JTBD**:
1. Aligns with outcome-focused SDD philosophy
2. Enables multi-language code generation strategy
3. Provides clear measurement framework via OTEL
4. Supports the constitutional equation
5. Facilitates multi-persona development

**JTBD in practice**:
1. Identify the job (what progress are users trying to make?)
2. Identify desired outcomes (how do they measure success?)
3. Identify obstacles (what prevents progress?)
4. Identify progress makers (what helps?)
5. Design solutions that deliver outcomes

**RDF integration**:
- Encode jobs, outcomes, and personas in RDF ontology
- Link features to jobs they accomplish
- Query for innovation opportunities
- Auto-generate documentation
- Instrument OTEL with job/outcome metadata

JTBD isn't just a framework—it's a mindset shift from **outputs to outcomes**, from **features to progress**, from **what we build to why it matters**.

---

**Next Steps:**
- [JTBD Personas](../jtbd/personas.md) - Detailed customer segments
- [Jobs & Outcomes Catalog](../jtbd/jobs-outcomes-catalog.md) - Complete job inventory
- [Why Features Exist](../jtbd/why-features-exist.md) - Feature justifications
- [Getting Started with JTBD](../jtbd/getting-started.md) - Tutorial
