# Token Optimization for AI Context

Techniques to minimize token usage when sharing documentation with AI agents while maintaining semantic completeness.

## Problem: Token Overhead

Sharing full documentation files wastes tokens:

```
Full file: docs/explanation/constitutional-equation.md
Size: 5,200 bytes
Tokens: ~2,000 tokens

AI only needs:
- Core concept (1 sentence)
- 5-stage pipeline diagram
- How to use (2 paragraphs)

Optimized: 400 tokens (80% reduction!)
```

## Core Principle: Semantic Abstraction

Instead of full text, extract semantic meaning:

| Approach | Tokens | Quality |
|----------|--------|---------|
| Full file | 2,000 | 100% but wasteful |
| Semantic abstract | 200 | 95% core meaning |
| Bullet points | 150 | 80% main concepts |
| JSON structure | 300 | 90% queryable format |

## Technique 1: Semantic Abstracts

Distill file to core concepts:

### Example: Constitutional Equation

**Full file:** 2,000 tokens

**Semantic abstract:**
```
Constitutional Equation: spec.md = μ(feature.ttl)

Meaning: RDF specifications deterministically generate code/docs/tests.

Five-stage pipeline:
  μ₁ Normalize    - SHACL validation of RDF
  μ₂ Extract      - Execute SPARQL queries
  μ₃ Emit         - Render Tera templates
  μ₄ Canonicalize - Format output
  μ₅ Receipt      - Create SHA256 proof

Key properties:
  - Deterministic: Same input → Same output
  - Idempotent: μ(μ(x)) = μ(x)
  - Verifiable: Receipt proves transformation
  - Reversible: Can trace output back to source

Usage: Never edit generated files directly.
Always edit RDF source, then run: ggen sync

Result: 300 tokens (85% reduction)
```

### How to Create Abstracts

1. **Identify core concept** (1 sentence)
2. **List main sections** (5-10 bullet points)
3. **Add key examples** (2-3 real cases)
4. **Note key properties** (3-5 critical facts)
5. **Include how-to** (1 paragraph)

## Technique 2: Structured Formats

Use JSON/YAML for machine-readable summaries:

```yaml
# docs/explanation/constitutional-equation.yaml
concept:
  name: "Constitutional Equation"
  formula: "spec.md = μ(feature.ttl)"
  meaning: "RDF specs generate code/docs/tests deterministically"

pipeline:
  stages:
    - name: "Normalize (μ₁)"
      input: "Raw RDF/Turtle"
      output: "Validated RDF"
      function: "SHACL validation"

    - name: "Extract (μ₂)"
      input: "Validated RDF"
      output: "JSON/structured data"
      function: "SPARQL queries"

    - name: "Emit (μ₃)"
      input: "Extracted data"
      output: "Generated code/docs"
      function: "Tera templates"

properties:
  deterministic: true
  idempotent: true
  verifiable: true
  reversible: true
```

**Token savings:**
- YAML structure: 400 tokens
- Same info as 2,000-token file
- 80% reduction

## Technique 3: Progressive Disclosure

Give information in layers based on agent need:

```
# Layer 1: Core Concept (100 tokens)
What is this?
  RDF specifications generate code deterministically.

# Layer 2: How It Works (300 tokens - add if needed)
5-stage pipeline...
[Include stages]

# Layer 3: Examples (500 tokens - add if needed)
Here are 3 real examples...
[Include examples]

# Layer 4: Deep Dive (1,000+ tokens - add if needed)
Complete reference with all details...
```

**Usage:**
```
Task: Add new CLI command

Agent: "I understand RDF generates code. What's the command structure?"

System: [Provide Layer 2 + Layer 3]

Agent: "Can you show an example?"

System: [Provide Layer 4 examples]
```

## Technique 4: Indexed References

Instead of embedding text, use references + index:

```
PROJECT SEMANTIC INDEX:

[[core-concepts]]
constitutional-equation = "spec.md = μ(feature.ttl)"
  tokens: 300
  location: docs/explanation/constitutional-equation.yaml

three-tier-architecture = "Commands/Ops/Runtime separation"
  tokens: 250
  location: docs/explanation/three-tier-architecture.yaml

[[how-tos]]
implement-command = "Step-by-step: Add CLI command"
  tokens: 400
  location: docs/guides/architecture/implement-three-tier.md

[[examples]]
command-impl = "Example: complete command implementation"
  tokens: 200
  location: docs/examples/python-code/command-impl.py
```

**Usage:**
```
Agent: "I need to understand RDF generation"

System: [Send only index]

Agent: "Show me [core-concepts.constitutional-equation]"

System: [Send 300 tokens with details]
```

## Technique 5: Differential Updates

Only send changed content:

```
# First request: Full context
[Project overview, architecture, examples]
Total tokens: 2,000

# Second request: Same task, new file
"Also update this file..."

# WRONG: Re-send full context
[Project overview, architecture, examples] (AGAIN)
Total tokens: 4,000 (wasteful!)

# RIGHT: Send only diff
"You have the context from before.
The change needed is:
[3 paragraphs about specific change]"
Total new tokens: 200
```

## Technique 6: Knowledge Graph Summary

Create lightweight knowledge graph:

```json
{
  "entities": {
    "ggen": "RDF transformation engine",
    "Turtle": "RDF text format",
    "SHACL": "RDF validation shapes",
    "SPARQL": "RDF query language"
  },
  "relationships": {
    "ggen uses": ["Turtle", "SHACL", "SPARQL"],
    "SHACL validates": "Turtle",
    "SPARQL queries": "Turtle"
  },
  "workflows": {
    "generate_code": ["Normalize", "Extract", "Emit"],
    "validate_spec": ["Parse Turtle", "Apply SHACL"]
  }
}
```

**Tokens: 200**
**Same info as:** 4-5 explanation files (2,000+ tokens)
**Reduction:** 90%

## Technique 7: Examples Over Explanation

Show working code instead of explaining:

### Example: Wrong Way

```
"The three-tier architecture separates concerns.
The commands layer provides the CLI interface,
the ops layer contains pure business logic,
and the runtime layer handles all I/O..."

[2 paragraphs - 300 tokens]
```

### Example: Right Way

```python
# Show the actual pattern
# commands/check.py - thin wrapper
def check():
    result = ops.check_impl()  # Delegate to ops
    display_result(result)      # Format output

# ops/check.py - pure logic
def check_impl() -> dict:
    tools = [python, git, black, pytest]
    return {tool: verify(tool) for tool in tools}

# runtime/process.py - I/O
def verify(tool: str) -> bool:
    try:
        result = run_logged([tool, "--version"])
        return result.returncode == 0
    except FileNotFoundError:
        return False
```

**Tokens: 150 (half the explanation)**
**Understanding:** Better (concrete code)**
**Reusability:** Higher (copy-paste ready)**

## Complete Example: Token-Optimized Context Package

```
# Package everything an agent needs for feature implementation

[README - 200 tokens]
Task: Add "cache" command to Specify CLI

[Constitutional Equation - 300 tokens]
RDF spec drives code generation

[Three-Tier Example - 150 tokens]
Show working command implementation

[RDF Spec Snippet - 100 tokens]
@prefix sk: <http://ggen-spec-kit.org/>
my:cache a sk:Command ;
  rdfs:label "cache" ;
  sk:description "Manage cached files" .

[Test Example - 100 tokens]
def test_cache_create():
    result = cache.create("my-cache")
    assert result.success

[Definition of Done - 200 tokens]
Checklist of 20 critical items

[TOTAL: 1,050 tokens]

What would be sent without optimization:
  [Full docs/explanation/ files] - 5,000 tokens
  [Full docs/guides/ files] - 3,000 tokens
  [Full source code] - 2,000 tokens
  TOTAL: 10,000 tokens

Reduction: 89% (10,000 → 1,050 tokens)
```

## Creating Token-Optimized Documentation

### Step 1: Analyze Current Docs

```bash
# Count tokens in each file
find docs/ -name "*.md" -exec \
  wc -w {} \; | awk '{print $1 * 0.35}' | \
  paste docs/ - | sort -nr | head -20

# Shows which files use most tokens
```

### Step 2: Extract Abstracts

For each large file:

```
1. Read file completely
2. Write 1-line summary
3. Identify 5 key points
4. Add 2-3 examples
5. Note critical properties
6. Combine into abstract
7. Estimate tokens (usually 15-20% of original)
```

### Step 3: Create Supplementary Formats

```
docs/explanation/
├── constitutional-equation.md (full, 2,000 tokens)
├── constitutional-equation.yaml (abstract, 300 tokens)
├── constitutional-equation.json (indexed, 200 tokens)
└── constitutional-equation-examples.md (3 examples, 400 tokens)

Agents use: .yaml + examples (700 tokens)
Instead of: full .md (2,000 tokens)
Savings: 65%
```

## Implementation: Token Budget System

Set token budget for different tasks:

```toml
[token_budgets]
# Budget tokens for different task types

simple_feature = 1000        # Small feature: 1K tokens max
complex_feature = 3000       # Large feature: 3K tokens max
bug_fix = 500               # Bug fix: 500 tokens max
documentation = 1500        # Doc update: 1.5K tokens max
refactoring = 2000          # Refactor: 2K tokens max
architecture = 2500         # Architecture: 2.5K tokens max

[documentation_tokens]
# Token allocation within budget

foundation = 200             # Project context
task_context = 150          # Task-specific info
examples = 300              # Code examples
error_handling = 100        # Error cases
verification = 100          # QA requirements
remaining = 150             # Flexible allocation
```

## Measuring Effectiveness

Track token efficiency:

```python
# Before optimization
files_sent = ["explanation/constitutional-equation.md", ...]
total_tokens_before = 5000
task_tokens_used = 2000
efficiency_before = 2000 / 5000 = 40%

# After optimization
files_sent = ["constitutional-equation.yaml", "examples.md"]
total_tokens_after = 700
task_tokens_used = 1950  # Same quality task result
efficiency_after = 1950 / 700 = 280% (2.8x more efficient)
savings = (5000 - 700) / 5000 = 86%
```

## Best Practices

### DO ✅

- Use semantic abstracts for foundational concepts
- Provide structured formats (YAML, JSON) for reference
- Create lightweight indexes for large documentation
- Use examples to show instead of explain
- Allocate tokens strategically by task type
- Track which abstracts work best
- Test different compression approaches

### DON'T ❌

- Don't send full files when abstract works
- Don't repeat context between requests
- Don't include irrelevant examples
- Don't optimize at cost of accuracy
- Don't skip critical information
- Don't assume agent remembers previous context

## See Also

- `setup-ai-agents.md` - Configuring agents
- `few-shot-patterns.md` - Learning patterns
- `documentation-verification.md` - Verifying AI-generated work
- `/docs/ecosystem/agi-ingestion.md` - AGI-specific optimization techniques
