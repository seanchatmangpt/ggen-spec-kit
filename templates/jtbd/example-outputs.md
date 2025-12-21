# Example Template Outputs

This document shows expected outputs from each JTBD-focused template when applied to the example RDF data.

---

## 1. Feature Outcome Card Output

**Template**: `feature-outcome-card.tera`
**Input**: `example-feature-jtbd.ttl`

```markdown
# deps-add Feature

## Jobs & Outcomes

**RDF Designer Job**: Specify dependency management

**Delivered Outcome**: Add dependencies 50% faster than manual editing

**Success Metric**: Time to add dependency < 10 seconds

**Pain Point Resolved**: Manual SPARQL editing is error-prone and time-consuming

**Emotional Benefit**: Work confidently knowing dependencies are valid

## Feature Details

Add semantic dependencies to RDF project with automatic validation

### Why This Feature Exists

This feature helps **RDF Designer** accomplish their goal of specify dependency management.

By using this feature, users can add dependencies 50% faster than manual editing, measured by time per dependency addition.

### Success Criteria

We know this feature is successful when:
- Time to add dependency: **< 10 seconds**
- Users report work confidently knowing dependencies are valid
- Manual SPARQL editing is error-prone and time-consuming is eliminated

### Related Features

Features addressing the same job:
- [deps-remove](#deps-remove)
- [deps-list](#deps-list)
- [deps-sync](#deps-sync)

---

*Generated from JTBD specification | Last updated: 2025-12-21*
```

---

## 2. JTBD User Story Output

**Template**: `jtbd-user-story.tera`
**Input**: User story RDF (hypothetical)

```markdown
## User Story: DEPS-001

**Priority**: High | **Value**: 85

### Story

**As a** RDF Designer trying to add external ontologies without breaking semantic integrity,

**I need** deps-add command

**So I can** work confidently and stop experiencing manual SPARQL editing errors.

### Context

When I need to add external ontologies to my RDF project without breaking semantic integrity

### Acceptance Criteria

- [ ] Command completes in < 10 seconds
- [ ] Validates dependency URI is accessible
- [ ] Updates project configuration automatically
- [ ] Shows success confirmation with dependency details
- [ ] Prevents duplicate dependencies

### Job to be Done

**When**: When I need to add external ontologies to my RDF project without breaking semantic integrity

**I want to**: Add dependencies 50% faster

**So I can**: Work confidently

**Currently**: Manual SPARQL editing is error-prone

---

## Story Summary

Total stories: 1

- High Priority: 1
- Medium Priority: 0
- Low Priority: 0

---

*Generated from JTBD specifications | 2025-12-21*
```

---

## 3. Outcome-Focused Documentation Output

**Template**: `outcome-focused-docs.tera`
**Input**: `example-feature-jtbd.ttl`

```markdown
# deps-add - Job-Focused Documentation

## Why This Feature Exists

Every feature exists to help you accomplish a specific job. Here's what deps-add does for you:

### The Job

**As a RDF Designer**, you need to Specify dependency management.

### The Problem

Currently, you experience: **Manual SPARQL editing is error-prone and time-consuming**

### The Solution

deps-add helps you Add dependencies 50% faster than manual editing.

**Measurable Impact**: Time per dependency addition - Time to add dependency < 10 seconds

## Who This Is For

**Primary Persona**: RDF Designer

**When to Use This**: When you need to specify dependency management and want to add dependencies 50% faster than manual editing.

## How It Improves Your Outcomes

Using deps-add, you will:

1. **Stop experiencing**: Manual SPARQL editing is error-prone and time-consuming
2. **Start achieving**: Add dependencies 50% faster than manual editing
3. **Measure success by**: Time to add dependency (target: < 10 seconds)

## Usage

### Prerequisites

Initialized spec-kit project

### Example

```
specify deps add foaf http://xmlns.com/foaf/0.1/
```

### What Happens

Add semantic dependencies to RDF project with automatic validation

## Success Metrics to Track

Monitor these metrics to ensure deps-add delivers value:

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Time per dependency addition | < 10 seconds | Time to add dependency |

## Related Features

Other features that help with "Specify dependency management":

- **deps-remove**: Addresses the same job from a different angle
- **deps-list**: Addresses the same job from a different angle
- **deps-sync**: Addresses the same job from a different angle

Consider using these together for maximum impact.

## Getting Help

If deps-add doesn't help you add dependencies 50% faster than manual editing, or you still experience Manual SPARQL editing is error-prone and time-consuming:

1. Check the [troubleshooting guide](troubleshooting.md)
2. Review success metrics above
3. File an issue describing what outcome you need

Remember: Features exist to deliver outcomes. If this feature doesn't deliver your outcome, that's a product gap we want to fix.

---

*Documentation focused on jobs and outcomes | 2025-12-21*
```

---

## 4. JTBD Metrics Dashboard Output

**Template**: `jtbd-metrics-dashboard.tera`
**Input**: Multiple features with outcomes (hypothetical aggregation)

```markdown
# Feature Outcome Metrics Dashboard

> **Purpose**: Track which features deliver which outcomes and measure their impact

**Last Updated**: 2025-12-21

---

## Executive Summary

- **Total Outcomes Tracked**: 7
- **Total Features**: 9
- **Released Features**: 4
- **Coverage Rate**: 44.4%

---

## Outcomes by Category

### Add dependencies 50% faster

**Description**: Add dependencies 50% faster than manual editing

**Priority**: High

#### Features Delivering This Outcome

| Feature | Persona | Success Criteria | Target | Current | Status |
|---------|---------|------------------|--------|---------|--------|
| deps-add | RDF Designer | Time to add dependency | < 10 seconds | 8 seconds | Released |

### Eliminate dependency conflicts

**Description**: Eliminate dependency conflicts

**Priority**: High

#### Features Delivering This Outcome

| Feature | Persona | Success Criteria | Target | Current | Status |
|---------|---------|------------------|--------|---------|--------|
| deps-validate | RDF Designer | Conflicts detected | 0 conflicts | N/A | In Progress |

### Visualize entire dependency graph in < 5 seconds

**Description**: Understand dependency structure

**Priority**: Medium

#### Features Delivering This Outcome

| Feature | Persona | Success Criteria | Target | Current | Status |
|---------|---------|------------------|--------|---------|--------|
| deps-graph | RDF Designer | Graph render time | < 5 seconds | N/A | Planned |

---

## Coverage Analysis

### Outcomes by Feature Count

- **Add dependencies 50% faster**: 1 feature(s)
- **Eliminate dependency conflicts**: 1 feature(s)
- **Visualize entire dependency graph in < 5 seconds**: 1 feature(s)

### Features by Persona

#### RDF Designer

- Total features: 9
- Released: 4
- In Progress: 2
- Planned: 3

---

## Impact Metrics

### Performance Against Targets

| Feature | Outcome | Target | Current | Gap | Status |
|---------|---------|--------|---------|-----|--------|
| deps-add | Add dependencies 50% faster | 10 | 8 | 2 | ✅ |

---

## ROI Visualization

### Features by Status

```
Released:     4 ████████████████
In Progress:  2 ████████
Planned:      3 ████
```

### Priority Distribution

```
High:    6 (67%)
Medium:  2 (22%)
Low:     1 (11%)
```

---

## Recommended Actions

1. **Coverage Gaps**: Review outcomes with < 2 features
2. **Underperforming Features**: Investigate features not meeting targets
3. **Persona Balance**: Ensure each persona has adequate feature support
4. **Measurement**: Add `currentValue` data for all released features

---

*Generated from JTBD outcome mappings | Refresh this dashboard weekly*
```

---

## 5. JTBD Feature Roadmap Output

**Template**: `jtbd-roadmap.tera`
**Input**: `example-roadmap-jtbd.ttl`

```markdown
# JTBD-Driven Feature Roadmap

> **Philosophy**: Prioritize features by job frequency × importance, not features by complexity

**Generated**: 2025-12-21

---

## Roadmap Overview

**Timeline**: Q1 2025 - Q3 2025

**Total Features Planned**: 9

---

## Q1 2025: Dependency Management Foundation

**Theme**: Enable RDF designers to manage dependencies efficiently

**Features in Release**: 3

### Priority Matrix

| Job Frequency | Job Importance | Feature Count |
|---------------|----------------|---------------|
| High | Critical | 2 |
| High | High | 0 |
| Medium | High | 1 |

### Features

#### deps-add

**Job**: Specify dependency management
**Persona**: RDF Designer
**Outcome**: Add dependencies 50% faster

**Priority Factors**:
- Job Frequency: High
- Job Importance: Critical
- Estimated Effort: Small

**Risk Assessment**:
- Risk Level: Low
- Mitigation: Use established CLI patterns from existing commands

---

#### deps-validate

**Job**: Ensure semantic integrity
**Persona**: RDF Designer
**Outcome**: Eliminate dependency conflicts

**Priority Factors**:
- Job Frequency: High
- Job Importance: Critical
- Estimated Effort: Medium

**Dependencies**:
- deps-add

**Risk Assessment**:
- Risk Level: Medium
- Mitigation: Integrate with existing SHACL validation pipeline

---

#### deps-graph

**Job**: Visualize dependency structure
**Persona**: RDF Designer
**Outcome**: Visualize entire dependency graph in < 5 seconds

**Priority Factors**:
- Job Frequency: Medium
- Job Importance: High
- Estimated Effort: Medium

**Dependencies**:
- deps-add
- deps-validate

**Risk Assessment**:
- Risk Level: Low
- Mitigation: Reuse Mermaid integration from existing visualization features

---

---

## Q2 2025: Collaborative Specification

**Theme**: Enable teams to collaborate on RDF specifications

**Features in Release**: 2

### Priority Matrix

| Job Frequency | Job Importance | Feature Count |
|---------------|----------------|---------------|
| High | Critical | 0 |
| High | High | 1 |
| Medium | High | 1 |

### Features

#### collab-review

**Job**: Review ontology changes
**Persona**: Ontology Reviewer
**Outcome**: Reduce review time by 60%

**Priority Factors**:
- Job Frequency: High
- Job Importance: Medium
- Estimated Effort: Medium

**Risk Assessment**:
- Risk Level: Medium
- Mitigation: Integrate with GitHub PR workflow

---

#### collab-merge

**Job**: Merge RDF specifications
**Persona**: Team Lead
**Outcome**: Merge specifications without manual conflict resolution

**Priority Factors**:
- Job Frequency: Medium
- Job Importance: High
- Estimated Effort: Large

**Dependencies**:
- deps-validate

**Risk Assessment**:
- Risk Level: High
- Mitigation: Develop RDF-aware merge algorithm; extensive testing

---

---

## Jobs and Outcomes by Quarter

### Q1 2025

**Jobs Addressed**:
- Specify dependency management
  - Outcomes: Add dependencies 50% faster
- Ensure semantic integrity
  - Outcomes: Eliminate dependency conflicts
- Visualize dependency structure
  - Outcomes: Visualize entire dependency graph in < 5 seconds

### Q2 2025

**Jobs Addressed**:
- Review ontology changes
  - Outcomes: Reduce review time by 60%
- Merge RDF specifications
  - Outcomes: Merge specifications without manual conflict resolution

---

## Risk and Mitigation Summary

### High-Risk Features

| Quarter | Feature | Risk | Mitigation |
|---------|---------|------|------------|
| Q2 2025 | collab-merge | High | Develop RDF-aware merge algorithm; extensive testing |

---

## Dependency Timeline

Critical path analysis based on feature dependencies:

| Feature | Quarter | Depends On | Blocks |
|---------|---------|------------|--------|
| deps-validate | Q1 2025 | deps-add | 2 feature(s) |
| deps-graph | Q1 2025 | deps-add, deps-validate | 0 feature(s) |
| collab-merge | Q2 2025 | deps-validate | 0 feature(s) |

---

## Persona Coverage

Features by persona across all quarters:

| Persona | Total Features | Q1 | Q2 | Q3 | Q4 |
|---------|----------------|----|----|----|----|
| RDF Designer | 5 | 3 | 0 | 2 | 0 |
| Team Lead | 1 | 0 | 1 | 0 | 0 |
| Ontology Reviewer | 1 | 0 | 1 | 0 | 0 |
| Performance Engineer | 1 | 0 | 0 | 1 | 0 |

---

## Success Criteria

This roadmap succeeds when:

1. **Job Coverage**: All High-Frequency × Critical-Importance jobs have features
2. **Balanced Delivery**: Each quarter addresses 3+ distinct jobs
3. **Risk Management**: High-risk features have documented mitigation
4. **Dependency Flow**: No circular dependencies, clear critical path
5. **Persona Balance**: Each persona receives features every quarter

---

## How to Use This Roadmap

1. **Prioritization**: Focus on High Frequency × Critical Importance first
2. **Dependencies**: Start features with dependencies early in quarter
3. **Risk**: Allocate extra time for high-risk features
4. **Outcomes**: Track whether features deliver promised outcomes
5. **Adjustment**: Re-prioritize based on job frequency changes

---

*Roadmap driven by Jobs to be Done framework | Update quarterly based on job analysis*
```

---

## Summary

These templates demonstrate how to transform JTBD-focused RDF specifications into:

1. **Feature Cards** - Quick reference showing jobs, outcomes, and success metrics
2. **User Stories** - JTBD-formatted stories with clear acceptance criteria
3. **Documentation** - User-centric docs explaining features through jobs
4. **Dashboards** - Analytics showing feature-to-outcome coverage and impact
5. **Roadmaps** - Prioritized releases based on job frequency and importance

All generated from single-source-of-truth RDF specifications using `ggen sync`.
