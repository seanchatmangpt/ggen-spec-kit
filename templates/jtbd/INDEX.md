# JTBD Templates Index

Complete reference for Jobs-to-be-Done (JTBD) Tera templates in spec-kit.

---

## Start Here

**New to JTBD templates?** Start with:
1. [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - One-page cheat sheet
2. [README.md](README.md) - Template overview
3. [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md) - Complete workflow

---

## Templates (5)

Located in `templates/` directory:

1. **feature-outcome-card.tera** (63 lines)
   - Input: Feature + JTBD mappings
   - Output: Markdown feature card
   - Use: Quick reference cards for features

2. **jtbd-user-story.tera** (74 lines)
   - Input: User stories with jobs/outcomes
   - Output: JTBD-formatted stories
   - Use: Product backlog and sprint planning

3. **outcome-focused-docs.tera** (105 lines)
   - Input: Features with complete JTBD context
   - Output: Job-focused documentation
   - Use: User-facing feature documentation

4. **jtbd-metrics-dashboard.tera** (139 lines)
   - Input: All features with outcome mappings
   - Output: Analytics dashboard
   - Use: Track feature performance and coverage

5. **jtbd-roadmap.tera** (185 lines)
   - Input: Planned features with job analysis
   - Output: Prioritized quarterly roadmap
   - Use: Product planning and release planning

---

## Documentation Files

All in `templates/jtbd/` directory:

### Getting Started
- **QUICK_REFERENCE.md** - One-page cheat sheet (must-read)
- **README.md** - Template overview and schema requirements
- **INTEGRATION_GUIDE.md** - Complete workflow guide

### Examples
- **example-feature-jtbd.ttl** - Feature with complete JTBD mappings
- **example-roadmap-jtbd.ttl** - Multi-quarter roadmap example
- **example-sparql-queries.rq** - All SPARQL queries for templates
- **example-outputs.md** - Expected outputs from each template

### Reference
- **INDEX.md** - This file

---

## Quick Start (3 Steps)

### 1. Copy Example Files

```bash
# Copy JTBD schema to your ontology
cp templates/jtbd/example-feature-jtbd.ttl ontology/jtbd-schema.ttl

# Copy example data to memory
cp templates/jtbd/example-feature-jtbd.ttl memory/features-jtbd.ttl

# Copy SPARQL queries
cp templates/jtbd/example-sparql-queries.rq sparql/jtbd-features.rq
```

### 2. Configure ggen

Add to `docs/ggen.toml`:

```toml
[[transformations.docs]]
name = "feature-cards"
input_files = ["memory/features-jtbd.ttl"]
schema_files = ["ontology/jtbd-schema.ttl"]
sparql_query = "sparql/jtbd-features.rq"
template = "templates/feature-outcome-card.tera"
output_file = "docs/features.md"
deterministic = true
```

### 3. Generate Docs

```bash
ggen sync --config docs/ggen.toml --transformation feature-cards
```

---

## File Organization

```
your-project/
├── ontology/
│   └── jtbd-schema.ttl              # JTBD ontology classes/properties
├── memory/
│   ├── features-jtbd.ttl            # Feature specifications
│   └── roadmap-jtbd.ttl             # Roadmap plans
├── sparql/
│   ├── jtbd-features.rq             # Feature card query
│   ├── jtbd-user-stories.rq         # User story query
│   ├── jtbd-docs.rq                 # Documentation query
│   ├── jtbd-metrics.rq              # Dashboard query
│   └── jtbd-roadmap.rq              # Roadmap query
├── templates/
│   ├── feature-outcome-card.tera    # Template 1
│   ├── jtbd-user-story.tera         # Template 2
│   ├── outcome-focused-docs.tera    # Template 3
│   ├── jtbd-metrics-dashboard.tera  # Template 4
│   ├── jtbd-roadmap.tera            # Template 5
│   └── jtbd/                        # Documentation
│       ├── README.md
│       ├── INTEGRATION_GUIDE.md
│       ├── QUICK_REFERENCE.md
│       └── examples...
└── docs/
    ├── ggen.toml                    # Transformation config
    ├── features.md                  # Generated docs
    └── ROADMAP.md                   # Generated roadmap
```

---

## Use Cases

### Product Management
- Generate feature cards for roadmap discussions
- Create metrics dashboard to track outcome delivery
- Prioritize roadmap by job frequency × importance

### Engineering
- Generate user stories from JTBD specifications
- Create outcome-focused feature documentation
- Track which features deliver which outcomes

### Customer Success
- Share job-focused documentation with customers
- Demonstrate measurable outcomes from features
- Identify gaps in outcome coverage

---

## Core Concepts

### Jobs to be Done (JTBD)

**Job**: A goal or task customers are trying to accomplish

**Outcome**: A measurable result customers want to achieve

**Persona**: A customer segment with specific jobs and needs

**Pain Point**: Current frustration or obstacle

**Feature**: A solution that helps accomplish a job

### The JTBD Equation

```
Feature Success = Job Frequency × Job Importance × Outcome Delivery
```

Features should be prioritized by:
1. How often the job occurs (Frequency)
2. How critical the job is (Importance)
3. How well the feature delivers outcomes

NOT by:
- Feature complexity
- Technical coolness
- Developer preference

---

## Template Variable Reference

Quick reference for SPARQL query variables each template expects:

### All Templates Need
- `?featureName` - Name of feature
- `?personaName` - Target persona
- `?jobTitle` - Job being accomplished

### Template-Specific

**feature-outcome-card**:
- `?outcome`, `?successCriteria`, `?targetValue`, `?painpoint`, `?emotionalBenefit`

**jtbd-user-story**:
- `?storyId`, `?jobContext`, `?desiredOutcome`, `?acceptanceCriteria`, `?priority`

**outcome-focused-docs**:
- `?featureDescription`, `?usageExample`, `?prerequisites`, `?relatedFeatures`

**jtbd-metrics-dashboard**:
- `?outcomeDescription`, `?currentValue`, `?featureStatus`, `?priority`

**jtbd-roadmap**:
- `?quarter`, `?releaseName`, `?jobFrequency`, `?jobImportance`, `?riskLevel`, `?dependencies`

---

## Common Tasks

### Add a New Feature

```turtle
:new-feature a sk:Feature ;
    sk:featureName "new-feature" ;
    sk:featureDescription "What it does" ;
    jtbd:accomplishesJob :job ;
    jtbd:deliversOutcome :outcome ;
    jtbd:targetPersona :persona ;
    sk:featureStatus "Planned" .
```

### Track Performance

```turtle
:outcome a jtbd:Outcome ;
    jtbd:targetValue "< 10s" ;
    jtbd:currentValue "8s" .  # Add after measuring
```

### Prioritize Roadmap

```turtle
:feature a jtbd:PlannedFeature ;
    jtbd:jobFrequency "High" ;      # How often
    jtbd:jobImportance "Critical" ;  # How important
    jtbd:quarter "Q1 2025" .
```

---

## Troubleshooting

**Problem**: Template generates empty output
**Solution**: Check SPARQL variable names match template expectations

**Problem**: Missing data in output
**Solution**: Add `OPTIONAL` clauses in SPARQL for optional fields

**Problem**: RDF validation fails
**Solution**: Ensure all required properties are present (see QUICK_REFERENCE.md)

**Problem**: ggen transformation fails
**Solution**: Verify paths in ggen.toml match your file structure

---

## Learning Path

1. **Beginner**: Read QUICK_REFERENCE.md, copy examples, generate first docs
2. **Intermediate**: Customize SPARQL queries, add custom properties
3. **Advanced**: Create custom templates, extend JTBD ontology

---

## Support

- **Questions**: See [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **Examples**: See `example-*.ttl` and `example-outputs.md`
- **Bugs**: File issue on GitHub
- **Feature Requests**: Describe job you're trying to accomplish

---

## References

- [Jobs to be Done Framework](https://jtbd.info/)
- [Outcome-Driven Innovation](https://jobs-to-be-done.com/)
- [spec-kit Documentation](../../README.md)
- [ggen Documentation](../../docs/GGEN_RDF_README.md)

---

**Version**: 1.0.0
**Last Updated**: 2025-12-21
**Status**: Production-Ready

---

**Quick Links**:
[Quick Reference](QUICK_REFERENCE.md) |
[Integration Guide](INTEGRATION_GUIDE.md) |
[README](README.md) |
[Examples](example-outputs.md)
