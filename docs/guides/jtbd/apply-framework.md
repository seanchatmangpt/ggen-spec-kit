# How-to: Apply JTBD Framework

**Goal:** Use Jobs-to-be-Done for feature prioritization
**Time:** 20-30 minutes | **Level:** Intermediate

---

## Quick Overview

Instead of: "Build feature X"
Think: "Help user accomplish job Y"

**Example:**
```
❌ Feature: "Add dark mode"
✅ Job: "Help developers work at night without eye strain"
```

---

## The JTBD Structure

Every job has three parts:

```
Situation: When [context]
Task: I want to [action]
Outcome: So that [result]
```

### Example: Project Initialization

```
Situation: When I'm starting a new development project
Task: I want to set up a structured spec-driven system
Outcome: So that my code, docs, and specs never drift
```

---

## Step 1: Identify Jobs in Your Project

List what users (developers) need to accomplish:

```
1. Start new project quickly
   - Get complete project structure
   - Understand the methodology
   - Write first specification

2. Add features systematically
   - Write RDF specifications
   - Generate code from specs
   - Keep docs in sync

3. Verify code quality
   - Run comprehensive tests
   - Check code coverage
   - Validate specifications

4. Deploy with confidence
   - Know code matches spec
   - Have complete documentation
   - Trace all decisions
```

---

## Step 2: Define Job Outcomes

For each job, define measurable success:

**Job:** Add features systematically

```
Outcome 1: Feature is defined in RDF
  Measure: SHACL validation passes
  Success: spec.ttl is valid

Outcome 2: Code is auto-generated
  Measure: ggen sync produces files
  Success: Code compiles without errors

Outcome 3: Documentation is current
  Measure: Generated from RDF
  Success: Docs match code

Outcome 4: Tests validate specification
  Measure: All tests pass
  Success: Code matches specification
```

Create a document: `docs/JTBD_OUTCOMES.md`

```markdown
# JTBD Outcomes

## Job: Add Features Systematically

### Outcome 1: Feature is defined clearly
- **Measure:** RDF specification is complete
- **Target:** 0 validation errors from ggen

### Outcome 2: Code is generated automatically
- **Measure:** Generated files exist
- **Target:** 100% of commands auto-generated

### Outcome 3: Documentation stays current
- **Measure:** Generated from RDF
- **Target:** Docs hash matches spec hash

### Outcome 4: Tests validate the job
- **Measure:** All tests pass
- **Target:** >80% code coverage
```

---

## Step 3: Map Features to Jobs

For each feature, answer: "What job does this solve?"

```
Feature: ggen sync command
  Job: Transform specifications into code automatically
  Outcome: Code always matches specification
  Success Metric: All generated code passes tests

Feature: SHACL validation
  Job: Catch specification errors early
  Outcome: Bad specs fail before code generation
  Success Metric: 0 runtime errors from bad specs

Feature: OpenTelemetry integration
  Job: Understand what code is doing
  Outcome: Issues are visible and traceable
  Success Metric: All operations have traces

Feature: JTBD framework support
  Job: Prioritize features that matter
  Outcome: Build what users actually need
  Success Metric: Feature usage matches priority
```

Create: `docs/JTBD_FEATURES_MAP.md`

```markdown
# Feature → Job Mapping

## Feature: ggen sync
- **Job:** Transform specifications into code automatically
- **Outcome:** Code always matches specification
- **Success Metric:** 0% generated code errors
- **Importance:** Critical - enables code generation

## Feature: SHACL Validation
- **Job:** Catch specification errors early
- **Outcome:** Invalid specs fail immediately
- **Success Metric:** 100% of bad specs caught
- **Importance:** High - prevents bad outputs

## Feature: Test Generation
- **Job:** Verify code matches specification
- **Outcome:** Generated code is tested
- **Success Metric:** >80% coverage on generated code
- **Importance:** High - ensures quality
```

---

## Step 4: Prioritize Using JTBD

Use importance vs. difficulty matrix:

```
         High Impact
             ↑
    DO FIRST │ DO LATER
             │
─────────────┼─────────→ Low Effort
      DO NOW │
      HARD   │
             ↓
         Low Impact
```

### Example Prioritization

```
CRITICAL (Do First):
  ✓ Core RDF-to-code generation (high impact, medium effort)
  ✓ SHACL validation (high impact, medium effort)
  ✓ Test generation (high impact, low effort)

IMPORTANT (Do Next):
  ✓ Documentation generation (medium impact, low effort)
  ✓ OpenTelemetry support (medium impact, medium effort)
  ✓ JTBD framework (medium impact, low effort)

NICE-TO-HAVE (Do Later):
  - UI for ontology editor (low impact, high effort)
  - Legacy format support (low impact, high effort)
  - Exotic language generation (low impact, high effort)
```

---

## Step 5: Track Job Metrics

For each job, track success metrics:

Create: `docs/JTBD_METRICS.md`

```markdown
# JTBD Metrics & Outcomes

## Job 1: Start New Project

### Metric: Time to first working command
- **Target:** < 15 minutes
- **Current:** 20 minutes (measured)
- **Action:** Simplify tutorial

### Metric: User understanding of RDF-first
- **Target:** >80% understand core principle
- **Current:** 65% (survey)
- **Action:** Create explanation document

### Metric: Success rate (project initializes without errors)
- **Target:** 99%
- **Current:** 95%
- **Action:** Add better error messages

## Job 2: Add Features Systematically

### Metric: Code generation accuracy
- **Target:** 100% of generated code works
- **Current:** 100% ✓
- **Status:** Achieved

### Metric: Documentation currency
- **Target:** 0% docs drift from code
- **Current:** 0% ✓
- **Status:** Achieved
```

---

## Step 6: Use JTBD to Guide Development

When deciding what to build:

### Example: New Feature Request

**Request:** "Add support for GraphQL"

**Analysis Using JTBD:**

```
Question 1: What job does this help with?
Answer: "Let developers generate GraphQL servers"

Question 2: What outcome does user want?
Answer: "Fully functional GraphQL API from specification"

Question 3: Can we measure success?
Answer: "Generated API passes type validation"

Question 4: What's the priority?
Answer: Let's check:
- Impact: Medium (only for GraphQL users)
- Effort: High (new language, new templates)
- Status: Medium priority

Decision: Schedule after core features are complete
```

---

## Step 7: Communicate Outcomes

Share job definitions with team:

**Create:** `docs/JTBD_TEAM_GUIDE.md`

```markdown
# JTBD Team Guide

## Our Core Jobs

We help developers accomplish these jobs:

1. **Start projects quickly** with complete structure
2. **Define features precisely** using RDF
3. **Generate code automatically** that matches spec
4. **Keep documentation current** automatically
5. **Verify quality** with comprehensive tests

## How We Measure Success

- **Job 1:** Project initialization time < 15 min
- **Job 2:** 0 RDF validation errors
- **Job 3:** 100% of generated code works
- **Job 4:** 0% documentation drift
- **Job 5:** >80% test coverage

## How We Prioritize

We ask: "What job does this feature enable?"

Not: "What feature should we build?"

This keeps us focused on user value.
```

---

## Common Patterns

### Pattern: Discovering Hidden Jobs

Talk to users about pain points:

```
User: "I waste time keeping docs in sync"
Job: "Maintain consistency between code and documentation"
Outcome: "Documentation is always current"
Solution: Generate docs from RDF
```

### Pattern: Job Hierarchy

Jobs have sub-jobs:

```
Main Job: Add features systematically
├── Sub-job: Define feature in RDF
├── Sub-job: Transform RDF to code
├── Sub-job: Implement business logic
├── Sub-job: Write tests
└── Sub-job: Deploy with confidence
```

Each sub-job has outcomes and metrics.

---

## JTBD Document Template

Create this file: `docs/JTBD_TEMPLATE.md`

```markdown
# Job Template

## Job: [Name]

### Situation
When [context where job happens]

### Task
I want to [action the user wants to do]

### Outcome
So that [result they want to achieve]

### Success Criteria
- [ ] Metric 1: [measurable outcome]
- [ ] Metric 2: [measurable outcome]
- [ ] Metric 3: [measurable outcome]

### Related Features
- Feature 1: Helps accomplish this job
- Feature 2: Helps accomplish this job

### Metrics & Tracking
- Current state: [where we are]
- Target: [where we want to be]
- Actions: [how to improve]
```

---

## See Also

- [Tutorial 6: Exploring JTBD Framework](../../tutorials/06-exploring-jtbd.md)
- [Explanation: Why JTBD?](../../explanation/why-jtbd-framework.md)
- [Reference: JTBD Framework](../../reference/jtbd-framework.md)

---

## Next Steps

1. ✓ Identify 5-10 core jobs your project enables
2. ✓ Define outcomes for each job
3. ✓ Map features to jobs
4. ✓ Prioritize features using JTBD
5. ✓ Track metrics for each job
6. ✓ Share with team
7. ✓ Use JTBD for all feature decisions
