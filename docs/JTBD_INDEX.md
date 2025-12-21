# Jobs To Be Done (JTBD) Framework Documentation Index

**Last Updated**: 2025-12-21
**Research Version**: 1.0

This index provides an overview of all JTBD framework research and integration documentation for spec-kit.

---

## Documentation Overview

| Document | Purpose | Audience | Reading Time |
|----------|---------|----------|--------------|
| **[JTBD_QUICK_REFERENCE.md](./JTBD_QUICK_REFERENCE.md)** | Quick lookup for JTBD principles and templates | All users | 10 min |
| **[JTBD_FRAMEWORK_RESEARCH.md](./JTBD_FRAMEWORK_RESEARCH.md)** | Comprehensive research report on JTBD for spec-kit | Product managers, architects | 45 min |
| **[JTBD_INTEGRATION_ROADMAP.md](./JTBD_INTEGRATION_ROADMAP.md)** | Implementation plan for integrating JTBD into spec-kit | Maintainers, contributors | 30 min |
| **[JTBD_SPARQL_IMPLEMENTATION.md](./JTBD_SPARQL_IMPLEMENTATION.md)** | SPARQL queries for JTBD ontology analysis | RDF developers, ontology designers | 20 min |

---

## Quick Start Guide

### For Users: "How do I use JTBD with spec-kit?"

**Start Here**: [JTBD_QUICK_REFERENCE.md](./JTBD_QUICK_REFERENCE.md)

**Learn**:
1. What jobs spec-kit helps you accomplish
2. How to write job stories instead of user stories
3. How to prioritize features by opportunity score

**Apply**:
- Use job story template when creating specifications
- Add job context to `/speckit.specify` prompts
- Validate features against desired outcomes

---

### For Product Managers: "Why should we adopt JTBD?"

**Start Here**: [JTBD_FRAMEWORK_RESEARCH.md](./JTBD_FRAMEWORK_RESEARCH.md) → Section 2: Outcome-Driven Innovation

**Key Findings**:
- **86% success rate** in new product development (vs. 17% industry average)
- **5x improvement** through outcome-focused innovation
- **3 high-opportunity jobs** identified for spec-kit (scores > 15)

**Business Impact**:
- Prioritize features by measurable outcomes, not just stakeholder requests
- Reduce wasted development on low-opportunity features
- Improve user satisfaction by focusing on unmet needs

---

### For Architects: "How does JTBD integrate with spec-kit's architecture?"

**Start Here**: [JTBD_INTEGRATION_ROADMAP.md](./JTBD_INTEGRATION_ROADMAP.md) → Phase 3: Ontology Extensions

**Technical Details**:
- New RDF classes: `sk:Job`, `sk:DesiredOutcome`, `sk:OutcomeMetric`
- SHACL shapes for job validation
- SPARQL queries for opportunity analysis
- Link features to jobs they satisfy

**Implementation**:
- 4-phase rollout (12 weeks)
- Backward-compatible extensions
- Optional but encouraged adoption

---

### For RDF Developers: "How do I query JTBD data?"

**Start Here**: [JTBD_SPARQL_IMPLEMENTATION.md](./JTBD_SPARQL_IMPLEMENTATION.md)

**Example Queries**:
- Find features by opportunity score
- List personas and their jobs
- Calculate outcome satisfaction
- Identify hiring/firing triggers

---

## Core Concepts

### The JTBD Statement

> "When I [situation], help me [motivation], so I can [expected outcome]."

**Spec-Kit Example**:
> "When I need to build software with evolving requirements, help me maintain a single source of truth, so I can pivot rapidly without accumulating technical debt."

---

### Three Dimensions of Jobs

Every job has:

1. **Functional**: What needs to be accomplished
   - Example: "Keep specifications synchronized with code"

2. **Emotional**: How users want to feel
   - Example: "Feel confident documentation won't go stale"

3. **Social**: How users want to be perceived
   - Example: "Be seen as maintaining high-quality documentation"

---

### The Opportunity Algorithm

```
Opportunity Score = Importance + max(Importance - Satisfaction, 0)
```

**Prioritization**:
- **15+**: Major opportunity (invest here!)
- **10-14**: Medium opportunity (optimize)
- **< 10**: Maintain or deprioritize

**Spec-Kit's Top Opportunities**:
1. Specification-code synchronization (Score: 17)
2. Rapid pivoting (Score: 16)
3. Code generation reliability (Score: 13)

---

### Five Primary Personas

| Persona | Job | Opportunity |
|---------|-----|-------------|
| **Specification Maintainer** | "Never let specs go stale" | 17 (HIGH) |
| **Multi-Language Architect** | "Maintain type safety across languages" | 13 (MEDIUM) |
| **Rapid Pivoter** | "Pivot without massive rewrites" | 16 (HIGH) |
| **Brownfield Modernizer** | "Preserve domain knowledge" | 12 (MEDIUM) |
| **Enterprise Constraint Enforcer** | "Enforce standards automatically" | 11 (MEDIUM) |

---

## Implementation Status

### Phase 1: Documentation & Communication ✅ COMPLETE
- [x] JTBD research report
- [x] Quick reference guide
- [x] Integration roadmap
- [x] SPARQL implementation guide
- [ ] Update README.md with JTBD value propositions
- [ ] Create PERSONAS.md
- [ ] Add competitive analysis

### Phase 2: Templates & Workflows 🔄 PLANNED
- [ ] Enhance `/speckit.specify` with job context
- [ ] Convert user stories to job stories
- [ ] Add outcome questions to `/speckit.clarify`
- [ ] Implement opportunity scoring in `/speckit.tasks`

### Phase 3: Ontology Extensions 🔄 PLANNED
- [ ] Create jtbd-extension.ttl
- [ ] Add SHACL shapes for validation
- [ ] Update spec-kit-schema.ttl
- [ ] Example persona instances in RDF

### Phase 4: Tooling & Automation 🔄 PLANNED
- [ ] Build `/speckit.metrics` command
- [ ] Automate satisfaction surveys
- [ ] Create opportunity dashboard
- [ ] Quarterly JTBD reviews

---

## Key Resources

### Internal Documents
- [Philosophy (RDF)](../memory/philosophy.ttl) - Spec-kit's constitutional principles
- [Schema](../ontology/spec-kit-schema.ttl) - Core RDF ontology
- [Spec Template](../templates/spec-template.md) - Feature specification template

### External Resources
- [Jobs-to-be-Done Book (Free PDF)](https://jobs-to-be-done-book.com/)
- [Anthony Ulwick - ODI Methodology](https://anthonyulwick.com/outcome-driven-innovation/)
- [NN/g - Personas vs JTBD](https://www.nngroup.com/articles/personas-jobs-be-done/)
- [THRV - JTBD Framework Guide](https://www.thrv.com/blog/jobs-to-be-done-vs-personas-the-ultimate-guide-to-unified-customer-understanding-in-product-development)

---

## Frequently Asked Questions

### Does JTBD replace user stories?

No, it enhances them. Job stories provide context (why, when, how users feel) that user stories lack. You can still use user stories, but frame them around jobs.

### Do I have to use all three job dimensions?

No. Start with functional jobs (what needs to be done). Add emotional and social dimensions when they provide meaningful insights.

### How often should we measure satisfaction scores?

**Recommended**: Quarterly for established features, monthly for new features.

### What if users can't articulate their jobs?

Use clarification questions:
- "What are you trying to accomplish?"
- "How do you want to feel when using this?"
- "What would make you feel confident/in control/productive?"

### Can I use JTBD without changing code?

Yes! Start with documentation (Phase 1). JTBD is first a mindset shift, then a tooling shift.

---

## Next Steps

### For First-Time Readers

1. **Read**: [JTBD_QUICK_REFERENCE.md](./JTBD_QUICK_REFERENCE.md) (10 minutes)
2. **Apply**: Use job story template in your next specification
3. **Measure**: Ask "What job does this feature help users accomplish?"

### For Contributors

1. **Review**: [JTBD_INTEGRATION_ROADMAP.md](./JTBD_INTEGRATION_ROADMAP.md)
2. **Start**: Phase 1 Quick Wins (12 hours of work)
3. **Iterate**: Collect feedback and refine

### For Maintainers

1. **Decide**: Which phases to prioritize
2. **Plan**: Allocate resources (12 weeks for full implementation)
3. **Measure**: Define success metrics for each phase

---

## Contributing

Found a job we missed? Have feedback on JTBD integration? Open an issue or PR:

- Issues: [spec-kit/issues](https://github.com/seanchatmangpt/ggen-spec-kit/issues)
- Discussions: Tag with `jtbd` label
- Contact: spec-kit maintainers

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-21 | Initial JTBD research and documentation |

---

**Remember**: Focus on outcomes (what users achieve), not features (what we build).

*"People don't want a quarter-inch drill—they want a quarter-inch hole."*
*"People don't want spec-kit—they want specifications that never go stale."*
