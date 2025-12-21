# Jobs To Be Done (JTBD) Quick Reference for Spec-Kit

**Last Updated**: 2025-12-21

This document provides a quick reference for applying JTBD principles to spec-kit development and documentation.

---

## Core JTBD Statement for Spec-Kit

> "When I need to build software with evolving requirements, help me **maintain a single source of truth** that always generates correct, up-to-date implementations, so I can **pivot rapidly without accumulating technical debt**."

---

## Three Dimensions of Jobs

Every job has three dimensions:

| Dimension | Question | Spec-Kit Example |
|-----------|----------|------------------|
| **Functional** | What needs to be accomplished? | "Generate type-safe code from specifications" |
| **Emotional** | How should users feel? | "Feel confident specifications won't go stale" |
| **Social** | How should users be perceived? | "Be seen as maintaining high-quality documentation" |

---

## Primary Jobs Spec-Kit Helps Users Do

### 1. Eliminate Specification-Implementation Gap
- **Functional**: Keep specifications and code synchronized
- **Emotional**: Feel confident documentation is accurate
- **Social**: Be recognized for maintaining quality docs
- **Opportunity Score**: 17 (HIGH)

### 2. Enable Rapid Pivots
- **Functional**: Change implementation without rewriting code
- **Emotional**: Feel fearless about pivoting
- **Social**: Be seen as agile and responsive
- **Opportunity Score**: 16 (HIGH)

### 3. Maintain Type Safety Across Languages
- **Functional**: Define types once, generate for multiple languages
- **Emotional**: Feel relief that types won't drift
- **Social**: Be perceived as technology-agnostic architect
- **Opportunity Score**: 13 (MEDIUM)

---

## Five Primary Personas

### 1. Specification Maintainer
**Job**: "Never let specifications go stale"
- Struggles with manually updating docs
- Hires spec-kit for constitutional equation (spec.md = μ(feature.ttl))
- Values: Automated synchronization, SHACL validation

### 2. Multi-Language Architect
**Job**: "Maintain type safety across Python, TypeScript, Rust, etc."
- Struggles with duplicate type definitions
- Hires spec-kit for multi-language code generation
- Values: Single ontology → N languages

### 3. Rapid Pivoter
**Job**: "Pivot without massive code rewrites"
- Struggles with locked-in architecture decisions
- Hires spec-kit for regeneration vs. rewriting
- Values: Branching for exploration, cheap experimentation

### 4. Brownfield Modernizer
**Job**: "Preserve domain knowledge while modernizing legacy systems"
- Struggles with outdated/missing documentation
- Hires spec-kit for formalizing domain knowledge
- Values: Incremental evolution, RDF knowledge capture

### 5. Enterprise Constraint Enforcer
**Job**: "Enforce architectural standards automatically"
- Struggles with manual compliance checking
- Hires spec-kit for machine-enforceable rules
- Values: Constitutional principles, SHACL validation

---

## Opportunity Algorithm (Ulwick)

```
Opportunity Score = Importance + max(Importance - Satisfaction, 0)
```

**Interpretation**:
- **15+**: Major opportunity (invest here)
- **10-14**: Medium opportunity (optimize)
- **< 10**: Maintain or deprioritize

**Top Opportunities for Spec-Kit**:
1. Specification-code synchronization (17)
2. Rapid pivoting (16)
3. Code generation reliability (13)

---

## Competitive Jobs Analysis

### Job: "Keep specifications synchronized with code"

| Solution | Satisfaction | Why Users Switch to Spec-Kit |
|----------|--------------|------------------------------|
| Manual Documentation | 3/10 | Specs become stale immediately |
| Code-First | 4/10 | Code becomes authoritative, intent is lost |
| OpenAPI Codegen | 6/10 | Only covers API contracts, not domain |
| Low-Code Platforms | 7/10 | Vendor lock-in, no code ownership |
| **Spec-Kit** | **7/10** | **Constitutional equation prevents staleness** |

---

## JTBD Value Propositions (by Persona)

**General**: "Eliminate the gap between specifications and implementation, so you can pivot rapidly without accumulating technical debt"

**For Specification Maintainers**: "Keep specifications and code synchronized automatically, so documentation never becomes stale"

**For Multi-Language Architects**: "Define types once, generate for any language, so integration bugs disappear"

**For Rapid Pivoters**: "Regenerate code instead of rewriting it, so pivoting is fearless"

**For Brownfield Modernizers**: "Formalize domain knowledge incrementally, so legacy systems become maintainable"

**For Enterprise Constraint Enforcers**: "Encode standards as machine-enforceable rules, so compliance is automatic"

---

## JTBD Job Story Template

Replace traditional user stories with job stories:

```markdown
### Job Story: [Job Name]

**Job Context**: When I [situation/circumstance]...

**Functional Job**: [what needs to be accomplished]

**Emotional Job**: [how user wants to feel]

**Social Job**: [how user wants to be perceived]

**Desired Outcome**: Minimize/Maximize [measurable outcome]

**Acceptance Scenarios**:
1. **Given** [context], **When** [action], **Then** [outcome validates job]
```

**Example**:

```markdown
### Job Story: Organize Photos Efficiently

**Job Context**: When I have hundreds of vacation photos scattered across devices...

**Functional Job**: Organize photos into albums by date and location

**Emotional Job**: Feel in control of my photo library (not overwhelmed)

**Social Job**: Be seen as organized when sharing albums with friends

**Desired Outcome**: Minimize time to create albums and find specific photos

**Acceptance Scenarios**:
1. **Given** 200 vacation photos, **When** I create album "Italy 2024", **Then** photos are organized automatically by date
2. **Given** album created, **When** I search "Rome", **Then** relevant photos surface in < 2 seconds
```

---

## JTBD Clarification Questions

### Functional Job Questions
- What are you trying to accomplish?
- What does success look like?
- What would make this faster/easier?

### Emotional Job Questions
- How do you want to feel when using this?
- What would give you confidence?
- What would make you feel in control?

### Social Job Questions
- How do you want others to perceive your work?
- What would make you look professional/competent?
- What would demonstrate your expertise?

### Outcome Validation Questions
- How will we measure if this job is done well?
- What metric indicates success?
- What importance (1-10) does this outcome have?
- What satisfaction (1-10) do current solutions provide?

---

## Outcome-Based Success Criteria

Link success criteria to desired outcomes:

```turtle
sk:SuccessCriterion_001
    sk:criterionId "SC-001" ;
    sk:metric "Response time < 200ms" ;
    sk:satisfiesOutcome sk:Outcome_MinimizeWaitTime ;
    sk:jobContext "When users search for photos" ;
    sk:outcomeMeasure "Minimize time to retrieve search results" ;
    sk:importanceScore 9 ;
    sk:currentSatisfaction 6 ;
    sk:opportunityScore 12 .
```

---

## Hiring & Firing Triggers

### When Users Hire Spec-Kit

1. **Brownfield Modernization**: "Our documentation is 3 years out of date"
2. **Multi-Platform**: "Type definitions drift between Python and TypeScript"
3. **Rapid Iteration**: "Requirements change weekly but rewrites take months"
4. **Specification Staleness**: "PRDs are always out of sync with code"
5. **Enterprise Standards**: "50 microservices don't follow architectural principles"

### When Users Might Fire Spec-Kit

1. **Steep Learning Curve**: "RDF/Turtle syntax is unfamiliar"
2. **Tool Integration Friction**: "Doesn't integrate with our CI/CD"
3. **Debugging Difficulty**: "Can't trace generated code errors to TTL source"
4. **Vendor Dependency**: "What if ggen development stops?"

**Action**: Address firing triggers through better onboarding, debugging tools, and ecosystem integration.

---

## JTBD Integration Checklist

### Documentation
- [ ] Reframe value proposition with outcome language
- [ ] Replace feature lists with job descriptions
- [ ] Add "What jobs does this help with?" to each feature

### Specification Templates
- [ ] Add job context to `/speckit.specify`
- [ ] Replace user stories with job stories
- [ ] Link success criteria to desired outcomes

### Clarification Workflow
- [ ] Add emotional and social job questions to `/speckit.clarify`
- [ ] Validate features against outcome achievement
- [ ] Identify unmet needs in job execution

### Prioritization
- [ ] Calculate opportunity scores (importance + (importance - satisfaction))
- [ ] Prioritize features by opportunity score, not just stakeholder requests
- [ ] Track satisfaction scores over time

### Ontology
- [ ] Add `sk:Job`, `sk:DesiredOutcome`, `sk:OutcomeMetric` classes
- [ ] Link features to jobs they satisfy
- [ ] Include persona job definitions in RDF

---

## Quick JTBD Assessment Template

Use this to evaluate any feature proposal:

```markdown
## JTBD Assessment: [Feature Name]

### Job Context
When [situation/circumstance]...

### Jobs This Feature Helps With
- **Functional Job**: [what it accomplishes]
- **Emotional Job**: [how users feel]
- **Social Job**: [how users are perceived]

### Desired Outcomes
1. Minimize [undesirable outcome] - Importance: X/10, Satisfaction: Y/10
2. Maximize [desirable outcome] - Importance: X/10, Satisfaction: Y/10

### Opportunity Score
Highest score: [score] for "[outcome]"

### Competitive Job Performance
How well do alternatives satisfy this job?
- Alternative A: [score]/10
- Alternative B: [score]/10
- **This Feature**: [score]/10

### Decision
- [ ] Build (high opportunity score, better than alternatives)
- [ ] Optimize (medium opportunity, incremental improvement)
- [ ] Defer (low opportunity, focus elsewhere)

### Success Metrics
- Leading: [how we know users are trying to do this job]
- Lagging: [how we measure job satisfaction improvement]
```

---

## Key Takeaways

1. **Focus on outcomes, not features**: Users hire spec-kit to "eliminate spec-code gap", not for "RDF support"
2. **Three dimensions matter**: Functional (what), Emotional (feel), Social (perception)
3. **Opportunity = Importance + Gap**: Prioritize jobs with high importance and low satisfaction
4. **Context drives hiring**: Same user might hire different solutions in different contexts
5. **Measure satisfaction**: Track outcome achievement, not just feature adoption

---

## Further Reading

- Full Research Report: [JTBD_FRAMEWORK_RESEARCH.md](./JTBD_FRAMEWORK_RESEARCH.md)
- JTBD Theory: [jobs-to-be-done.com](https://jobs-to-be-done.com/)
- ODI Methodology: [anthonyulwick.com](https://anthonyulwick.com/outcome-driven-innovation/)
- JTBD vs Personas: [NN/g Article](https://www.nngroup.com/articles/personas-jobs-be-done/)

---

**Remember**: People don't want a quarter-inch drill—they want a quarter-inch hole.
People don't want spec-kit—they want specifications that never go stale.
