# Configure AI Agents with Spec Kit

Learn how to set up and configure AI agents (like Claude Code) to work with ggen spec-kit for automated development tasks.

## Overview

AI agents can:
- Understand RDF specifications
- Generate code, tests, documentation automatically
- Maintain spec-code synchronization
- Suggest improvements and optimizations
- Analyze and debug issues

This guide covers configuration for optimal AI agent performance.

## Prerequisites

- ggen spec-kit project initialized
- AI agent with Claude Code or similar (e.g., Claude with API access)
- OpenTelemetry setup (optional but recommended)
- Basic understanding of your domain

## Core Configuration

### 1. Documentation Structure

Ensure AI-friendly documentation:

```bash
# Check documentation exists
ls -la docs/

# Verify structure
specify check --category documentation

# Key documents needed:
- docs/explanation/      # Conceptual understanding
- docs/guides/          # How-to procedures
- docs/reference/       # API and configuration reference
- docs/tutorials/       # Learning progressions
```

### 2. RDF Ontology Clarity

AI agents learn from your RDF ontology:

```turtle
# Example: Well-documented command
my:validate
    a sk:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF specifications against SHACL shapes" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "file" ;
        sk:type "File" ;
        sk:required true ;
        sk:description "Path to .ttl file to validate"
    ] ;
    sk:output [
        a sk:Output ;
        sk:type "ValidationReport" ;
        sk:description "SHACL validation results"
    ] .
```

**AI-friendly patterns:**
- Descriptive labels (not abbreviations)
- Complete descriptions (minimum 20 characters)
- Examples in comments
- Documented properties and types

### 3. Code Organization

Maintain clear architecture for AI understanding:

```
src/specify_cli/
├── commands/          # CLI wrappers (thin, generated)
├── ops/              # Business logic (pure, no I/O)
├── runtime/          # Side effects (I/O, subprocess)
└── core/             # Shared utilities

tests/
├── unit/             # Test ops/ layer
├── integration/      # Test ops + runtime interaction
└── e2e/             # Test end-to-end CLI

docs/
├── tutorials/        # Learning progressions
├── guides/          # How-to procedures
├── reference/       # Complete API docs
└── explanation/     # Conceptual foundation
```

AI agents learn architecture from structure. Clear separation = better agent understanding.

## Context Injection for Agents

### Strategy: Progressive Context

When asking AI agents to work on tasks, provide context in this order:

```
1. FOUNDATION
   ├─ Project structure (docs/explanation/architecture)
   ├─ Key concepts (docs/explanation/constitutional-equation)
   └─ CLAUDE.md (project-specific instructions)

2. TASK CONTEXT
   ├─ Relevant RDF spec (ontology/*.ttl)
   ├─ Related guides (docs/guides/*)
   └─ Examples from docs/examples/

3. IMPLEMENTATION CONTEXT
   ├─ Current code (src/specify_cli/)
   ├─ Test examples (tests/)
   └─ Error patterns (docs/reference/error-codes.md)

4. VERIFICATION
   ├─ Definition of Done (docs/reference/definition-of-done.md)
   ├─ Quality metrics (docs/reference/quality-metrics.md)
   └─ Test requirements
```

### Example: Setting Up an Agent for Feature Implementation

```markdown
# Task: Add "cache" command to Specify CLI

## Foundation (send first)
- Read: docs/explanation/constitutional-equation.md
- Read: CLAUDE.md
- Understand: RDF specs generate code/tests

## Task Context (send second)
- Feature: Add `specify cache` command
- RDF spec: ontology/cli-commands.ttl (see cache command)
- Similar example: Look at `check` command implementation
- Guide: docs/guides/architecture/implement-three-tier.md

## Implementation (send third)
- Commands: src/specify_cli/commands/cache.py
- Ops: src/specify_cli/ops/cache_ops.py
- Tests: tests/unit/ops/test_cache_ops.py
- Generated from: ontology/cli-commands.ttl (cache command)

## Verification (send last)
- Run: uv run pytest tests/
- Check: ruff check, mypy, black
- Verify: Definition of Done checklist
```

## Agent Capabilities by Setup Level

### Level 1: Basic Setup

**Agent can:**
- Understand project structure
- Generate simple functions
- Write basic tests
- Update documentation

**Requires:**
- Clear README
- docs/explanation/ files
- Code examples

### Level 2: RDF-Aware Setup

**Agent can:**
- Understand RDF specifications
- Generate code from specs
- Write tests matching specs
- Update RDF when needed

**Requires:**
- Level 1 +
- Well-documented RDF ontology
- Transformation examples
- docs/guides/ for workflows

### Level 3: Full Integration

**Agent can:**
- End-to-end feature implementation
- Maintain spec-code sync
- Suggest spec improvements
- Complex refactoring

**Requires:**
- Level 2 +
- CLAUDE.md with detailed instructions
- Semantic context injection
- Token optimization patterns

### Level 4: Advanced (AGI-Optimized)

**Agent can:**
- Autonomous feature development
- Architecture improvements
- Complex transformations
- Strategic decisions

**Requires:**
- Level 3 +
- docs/ecosystem/agi-ingestion.md
- Few-shot examples
- Semantic ontology for docs

## Configuration File: .ai-config.toml

Create configuration for AI agents:

```toml
[ai]
enabled = true
model = "claude-opus-4-5"

[ai.context]
# What to feed agent for each task
foundation = [
    "docs/explanation/constitutional-equation.md",
    "CLAUDE.md"
]

architecture = [
    "docs/explanation/three-tier-architecture.md",
    "docs/guides/architecture/implement-three-tier.md",
    "CLAUDE.md"
]

rdf_development = [
    "docs/explanation/rdf-first-development.md",
    "docs/guides/rdf/write-rdf-spec.md",
    "ontology/spec-kit-schema.ttl"
]

[ai.constraints]
# Hard rules for agent
no_hardcoded_secrets = true
no_shell_true = true
require_type_hints = true
min_test_coverage = 0.80

[ai.examples]
# Few-shot examples for learning
implementation = "docs/examples/python-code/"
testing = "docs/examples/"
rdf_specs = "docs/examples/rdf-specifications/"
sparql = "docs/examples/sparql-queries/"

[ai.output]
# What agent should deliver
code_format = "python"
doc_format = "markdown"
test_framework = "pytest"
```

## Few-Shot Examples for Agents

Create examples directory with patterns:

```bash
mkdir -p docs/examples/{python-code,rdf-specs,sparql-queries,tests}

# Add example implementations
cat > docs/examples/python-code/command-impl.py << 'EOF'
# Example: Simple command implementation
# Shows: Layer separation, error handling, testing pattern

from specify_cli import ops

def my_command(arg: str) -> dict:
    """CLI wrapper - parse args, delegate to ops"""
    result = ops.my_command_impl(arg)
    return result
EOF
```

See: `docs/guides/ai-integration/few-shot-patterns.md` for complete examples.

## Prompt Engineering for Agents

### Pattern 1: Specification-First

```
Given RDF specification:
[Show the relevant RDF snippet]

Generate Python code that:
1. Implements the command
2. Follows the three-tier architecture
3. Has comprehensive tests
4. Matches Definition of Done

Use examples from: docs/examples/python-code/
```

### Pattern 2: Context Injection

```
PROJECT CONTEXT:
[0-50 tokens] Brief overview
[CLAUDE.md excerpt] Relevant constraints

TASK:
[Clear task description]

EXAMPLES:
[2-3 similar completed examples]

CONSTRAINTS:
[Definition of Done checklist]

Please:
1. Understand the context
2. Implement the feature
3. Verify against constraints
4. Return complete, ready-to-commit code
```

### Pattern 3: Specification-Code Sync

```
RDF SPECIFICATION:
[ontology/cli-commands.ttl excerpt]

CURRENT IMPLEMENTATION:
[Show current code]

ISSUE:
[Describe drift/mismatch]

SOLUTION:
[Ask agent to regenerate or fix]

Verify:
- Run: ggen sync
- Check: Code matches spec
```

## Semantic Context Optimization

### Reduce Token Overhead

Instead of feeding entire files, use semantic abstracts:

```
# BAD - feeds entire 5KB file
Read: docs/explanation/constitutional-equation.md (entire file)
Tokens: 2,000+

# GOOD - semantic abstract
The constitutional equation states:
  spec.md = μ(feature.ttl)

This means RDF specifications deterministically generate
code/docs/tests through a 5-stage pipeline:
  μ₁ Normalize → μ₂ Extract → μ₃ Emit → μ₄ Canonicalize → μ₅ Receipt

[Continues with key points only - 200 tokens total]
```

See: `docs/guides/ai-integration/token-optimization.md` for techniques.

## Verification & Quality

### Pre-Merge Checklist for Agent Work

Before committing code from agents:

```bash
# 1. Run linting
ruff check src/

# 2. Run type checking
mypy src/

# 3. Run tests
uv run pytest tests/

# 4. Check coverage
uv run pytest --cov=src/ --cov-report=term-missing

# 5. Verify RDF sync
specify ggen verify

# 6. Check Definition of Done
# (see docs/reference/definition-of-done.md)
```

### Common Agent Issues

**Issue: Generated code has syntax errors**
- **Fix:** Provide more context, simpler examples
- **Prevent:** Test generation in sandboxed env first

**Issue: Code doesn't match architecture**
- **Fix:** Emphasize three-tier separation in prompts
- **Prevent:** Show anti-patterns to avoid

**Issue: Tests are incomplete**
- **Fix:** Provide test examples in docs/examples/
- **Prevent:** Use Definition of Done as constraint

**Issue: Documentation is vague**
- **Fix:** Provide documentation examples
- **Prevent:** Show Diataxis compliance requirements

## Integration with CI/CD

### GitHub Actions for Agent Work

```yaml
name: Agent-Generated Code

on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Check agent work quality
        run: |
          # Linting
          ruff check src/

          # Type checking
          mypy src/

          # Tests
          pytest tests/

          # Coverage
          pytest --cov=src/ --cov-report=fail-under=80

          # RDF sync
          specify ggen verify

          # Definition of Done
          python scripts/check-dod.py
```

## Advanced: Autonomous Agent Loop

For highest-capability agents:

```
Agent Planning Phase:
  1. Understand spec (RDF)
  2. Analyze current code
  3. Identify gaps
  4. Create implementation plan

Agent Implementation Phase:
  1. Write code (commands + ops + runtime)
  2. Write tests
  3. Generate documentation
  4. Run verification

Agent Verification Phase:
  1. Check: tests pass
  2. Check: linting passes
  3. Check: Definition of Done met
  4. Check: Spec-code sync verified

If all checks pass: Ready for merge
If checks fail: Self-correct and retry
```

## See Also

- `token-optimization.md` - Reduce context overhead
- `documentation-verification.md` - Verify AI-generated docs
- `few-shot-patterns.md` - Learning patterns for agents
- `/docs/ecosystem/agi-ingestion.md` - AGI-optimized documentation
- `/docs/reference/definition-of-done.md` - Quality standards
- `CLAUDE.md` - Project-specific agent instructions
