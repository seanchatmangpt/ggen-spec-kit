# How-to: Semantic Context Injection for AI Agents

**Goal:** Inject only the documentation context AI agents need, minimizing token overhead.

**Time:** 20 minutes | **Level:** Advanced

---

## Overview

Instead of dumping entire documentation into AI context, use semantic queries to inject exactly what's needed.

**Traditional approach:** 20,000+ tokens of context
**Semantic approach:** 2,000-3,000 tokens of context
**Efficiency gain:** 10x reduction

---

## Step 1: Build Documentation Graph

Create SPARQL queries to extract documentation relationships:

**File: `docs/sparql/doc-context-query.rq`**

```sparql
PREFIX doc: <http://ggen-spec-kit.org/documentation#>
PREFIX spec: <http://ggen-spec-kit.org/spec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Query: Get minimal context for implementing a feature
# This returns only the most relevant documentation
SELECT ?title ?brief ?examples ?constraints ?relatedDocs
WHERE {
    # The main topic (passed as parameter)
    ?topic rdfs:label ?title ;
           doc:briefSummary ?brief ;
           doc:exampleCode ?examples .

    # Constraints (from SHACL shapes)
    ?topic doc:constraints ?constraints .

    # Related concepts (but with summary only, not full content)
    ?topic doc:related ?related .
    ?related rdfs:label ?relatedDocs .

    # Exclude: Full documentation text (reduce tokens)
    # Include: Summaries, examples, relationships
}
ORDER BY ?relevance
LIMIT 5
```

---

## Step 2: Create Context Assembly Pipeline

Build a system to assemble context on-demand:

**File: `scripts/inject-context.py`**

```python
#!/usr/bin/env python3
"""Semantic context injection for AI agents."""

import json
from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ContextRequest:
    """What context an AI agent needs."""
    task: str  # e.g., "implement-cli-command"
    max_tokens: int = 2000
    include_examples: bool = True
    include_constraints: bool = True
    difficulty_level: str = "Intermediate"

class SemanticContextInjector:
    """Inject documentation context using semantic queries."""

    def __init__(self, documentation_graph: str):
        """Load documentation RDF graph.

        Parameters
        ----------
        documentation_graph : str
            Path to RDF graph file
        """
        self.graph = self._load_graph(documentation_graph)

    def inject_context(self, request: ContextRequest) -> Dict:
        """Assemble context for AI agent.

        Parameters
        ----------
        request : ContextRequest
            What context is needed

        Returns
        -------
        Dict
            Semantic context (token-optimized)
        """
        context = {
            "task": request.task,
            "estimated_tokens": 0,
            "content": {}
        }

        # 1. Get primary documentation (~800 tokens)
        primary_doc = self._query_primary_doc(request.task)
        context["content"]["primary"] = primary_doc
        context["estimated_tokens"] += 800

        # 2. Get examples (compressed) (~600 tokens)
        if request.include_examples:
            examples = self._query_examples(
                request.task,
                max_examples=3
            )
            context["content"]["examples"] = examples
            context["estimated_tokens"] += 600

        # 3. Get constraints (~400 tokens)
        if request.include_constraints:
            constraints = self._query_constraints(request.task)
            context["content"]["constraints"] = constraints
            context["estimated_tokens"] += 400

        # 4. Get related concepts (links only, ~200 tokens)
        related = self._query_related(request.task)
        context["content"]["related"] = related
        context["estimated_tokens"] += 200

        return context

    def _query_primary_doc(self, task: str) -> Dict:
        """Get primary documentation for task."""
        # Query documentation RDF
        query = f"""
        SELECT ?title ?summary ?outcome
        WHERE {{
            ?doc rdfs:label "{task}" ;
                 doc:title ?title ;
                 doc:summary ?summary ;
                 doc:outcome ?outcome .
        }}
        """
        # Execute SPARQL query...
        return {
            "title": "How to Add a CLI Command",
            "summary": "[compressed summary, ~200 words]",
            "outcomes": [
                "Define RDF specification",
                "Generate Python code",
                "Implement business logic",
                "Write tests"
            ]
        }

    def _query_examples(self, task: str, max_examples: int = 3) -> List[Dict]:
        """Get few-shot examples (compressed)."""
        return [
            {
                "name": "Simple Command",
                "rdf_spec": "sk:hello a sk:Command; ...",
                "implementation": "[compressed code ~50 tokens]",
                "tests": "[compressed test ~50 tokens]"
            },
            {
                "name": "Command with Arguments",
                "rdf_spec": "sk:init a sk:Command; ...",
                "implementation": "[compressed code ~50 tokens]",
                "tests": "[compressed test ~50 tokens]"
            },
            {
                "name": "Complex Command",
                "rdf_spec": "sk:build a sk:Command; ...",
                "implementation": "[compressed code ~50 tokens]",
                "tests": "[compressed test ~50 tokens]"
            }
        ]

    def _query_constraints(self, task: str) -> Dict:
        """Get architectural constraints."""
        return {
            "file_locations": {
                "rdf_spec": "ontology/cli-commands.ttl",
                "ops_code": "src/specify_cli/ops/[name].py",
                "tests": "tests/unit/test_[name]_ops.py",
                "do_not_edit": "src/specify_cli/commands/ [auto-generated]"
            },
            "patterns": [
                "Commands layer: thin wrapper, delegates to ops",
                "Operations layer: pure logic, no side effects",
                "Runtime layer: all I/O and subprocess"
            ],
            "validation": [
                "Must follow RDF specification",
                "SHACL validation must pass",
                "Tests must achieve >80% coverage"
            ]
        }

    def _query_related(self, task: str) -> List[Dict]:
        """Get links to related documentation (not full content)."""
        return [
            {
                "type": "tutorial",
                "title": "Tutorial 3: Write RDF Specifications",
                "link": "docs/tutorials/03-first-rdf-spec.md",
                "why_relevant": "Learn RDF syntax needed for step 1"
            },
            {
                "type": "explanation",
                "title": "Three-Tier Architecture",
                "link": "docs/explanation/three-tier-architecture.md",
                "why_relevant": "Understand code organization constraints"
            },
            {
                "type": "reference",
                "title": "RDF Ontology Reference",
                "link": "docs/reference/rdf-ontology.md",
                "why_relevant": "Look up RDF properties available"
            }
        ]

    def _load_graph(self, path: str):
        """Load RDF graph from file."""
        # In production: use rdflib or similar
        pass


# Usage
if __name__ == "__main__":
    injector = SemanticContextInjector("docs/ontology/documentation.ttl")

    request = ContextRequest(
        task="implement-cli-command",
        max_tokens=2000,
        difficulty_level="Intermediate"
    )

    context = injector.inject_context(request)
    print(json.dumps(context, indent=2))
```

---

## Step 3: Use Compressed Representations

Instead of full markdown content, use structured summaries:

**Full documentation (2,000 tokens):**
```markdown
# How to Add a CLI Command

This guide teaches you how to add new CLI commands to Spec Kit...
[Long explanation of RDF-first philosophy]
[Detailed examples]
[Common pitfalls]
... (hundreds of lines)
```

**Semantic context (200 tokens):**
```json
{
  "task": "add-cli-command",
  "steps": [
    {
      "number": 1,
      "action": "Edit ontology/cli-commands.ttl",
      "example": "sk:hello a sk:Command; rdfs:label 'hello'; ...",
      "why": "Define specification as RDF"
    },
    {
      "number": 2,
      "action": "Run: ggen sync",
      "what_happens": "Generates Python skeleton + tests + docs",
      "why": "Transforming RDF to code"
    },
    {
      "number": 3,
      "action": "Implement in src/specify_cli/ops/hello.py",
      "pattern": "def hello_operation() -> str: ...",
      "why": "Add business logic (pure function, no I/O)"
    },
    {
      "number": 4,
      "action": "Write tests in tests/unit/test_hello_ops.py",
      "pattern": "def test_hello_returns_greeting(): ...",
      "why": "Verify implementation"
    }
  ],
  "constraints": ["RDF syntax must be valid", "Commands are auto-generated", "Ops functions must be pure"],
  "files": {
    "edit": ["ontology/cli-commands.ttl", "src/specify_cli/ops/[name].py"],
    "auto_generated": ["src/specify_cli/commands/[name].py", "docs/commands/[name].md"],
    "do_not_edit": ["auto_generated files"]
  }
}
```

**Token reduction:** 90% less (2000 → 200 tokens)

---

## Step 4: Implement Dynamic Context Selection

Create a system that selects context based on what the AI is currently doing:

**File: `scripts/context-selector.py`**

```python
"""Dynamically select documentation context."""

class ContextSelector:
    """Select context based on AI task stage."""

    def select_context(self, stage: str, task: str) -> Dict:
        """Select context for current task stage.

        Parameters
        ----------
        stage : str
            Current stage: plan, implement, test, verify
        task : str
            What AI is implementing

        Returns
        -------
        Dict
            Context for this stage only
        """
        contexts = {
            "plan": self._context_for_planning,
            "implement": self._context_for_implementation,
            "test": self._context_for_testing,
            "verify": self._context_for_verification
        }

        return contexts[stage](task)

    def _context_for_planning(self, task: str) -> Dict:
        """Context for planning stage (~500 tokens)."""
        return {
            "high_level_overview": "...",
            "steps": "[ordered list of steps]",
            "output_artifacts": "[what will be created]",
            "dont_need_yet": "[implementation details]"
        }

    def _context_for_implementation(self, task: str) -> Dict:
        """Context for implementation stage (~1500 tokens)."""
        return {
            "step_by_step_instructions": "...",
            "code_examples": "[compressed examples]",
            "patterns_to_follow": "[style guide excerpts]",
            "files_to_edit": "[paths]",
            "architectural_constraints": "[rules to follow]"
        }

    def _context_for_testing(self, task: str) -> Dict:
        """Context for testing stage (~800 tokens)."""
        return {
            "test_patterns": "[few-shot test examples]",
            "coverage_targets": "[80%+ coverage]",
            "test_locations": "[where to put tests]",
            "assertion_patterns": "[common assertions]"
        }

    def _context_for_verification(self, task: str) -> Dict:
        """Context for verification stage (~600 tokens)."""
        return {
            "verification_checklist": "[what to verify]",
            "specification_reference": "[RDF spec excerpt]",
            "proof_receipt": "[SHA256 receipt]",
            "quality_gates": "[must pass these checks]"
        }
```

**Usage:**
```python
selector = ContextSelector()

# During planning
context = selector.select_context("plan", "implement-cli-command")
# Returns: ~500 tokens of planning guidance

# During implementation
context = selector.select_context("implement", "implement-cli-command")
# Returns: ~1500 tokens of implementation details

# During testing
context = selector.select_context("test", "implement-cli-command")
# Returns: ~800 tokens of testing patterns

# Total: ~2800 tokens distributed across stages
# Instead of: 20,000+ tokens injected all at once
```

---

## Step 5: Create Context Validation

Verify that injected context is accurate and up-to-date:

**File: `scripts/validate-context.py`**

```python
"""Validate semantic context accuracy."""

class ContextValidator:
    """Ensure injected context matches actual code."""

    def validate(self, context: Dict) -> Dict:
        """Validate context against current codebase.

        Returns
        -------
        Dict
            Validation results with warnings/errors
        """
        results = {
            "valid": True,
            "warnings": [],
            "errors": []
        }

        # Check 1: File paths are correct
        if not self._check_file_paths(context):
            results["errors"].append("File paths in context don't match actual project structure")
            results["valid"] = False

        # Check 2: Code examples compile
        if not self._check_examples_valid(context):
            results["warnings"].append("Code examples may not match current syntax")

        # Check 3: RDF specification is valid
        if not self._check_rdf_syntax(context):
            results["errors"].append("RDF specification syntax is invalid")
            results["valid"] = False

        # Check 4: Examples match actual patterns in codebase
        if not self._check_pattern_consistency(context):
            results["warnings"].append("Examples don't match current code patterns")

        return results
```

---

## Step 6: Monitor Context Token Usage

Track how much context each task type needs:

**File: `scripts/context-analytics.py`**

```python
"""Analyze and optimize context token usage."""

class ContextAnalytics:
    """Track context efficiency metrics."""

    def analyze_usage(self, task_type: str, context_used: Dict) -> Dict:
        """Analyze token usage for a task.

        Parameters
        ----------
        task_type : str
            Type of task (e.g., "add-cli-command")
        context_used : Dict
            Context that was injected

        Returns
        -------
        Dict
            Efficiency metrics and recommendations
        """
        metrics = {
            "task_type": task_type,
            "tokens_used": self._count_tokens(context_used),
            "efficiency": "?",
            "recommendations": []
        }

        # Benchmark: typical tasks should use 1500-3000 tokens
        if metrics["tokens_used"] > 5000:
            metrics["efficiency"] = "POOR"
            metrics["recommendations"].append("Context is too large, compress more aggressively")
        elif metrics["tokens_used"] > 3000:
            metrics["efficiency"] = "OK"
            metrics["recommendations"].append("Try to reduce by 30-40%")
        elif metrics["tokens_used"] < 2000:
            metrics["efficiency"] = "EXCELLENT"
        else:
            metrics["efficiency"] = "GOOD"

        return metrics

    def _count_tokens(self, context: Dict) -> int:
        """Estimate tokens in context."""
        # Simple estimation: ~4 characters per token
        text = json.dumps(context)
        return len(text) // 4
```

---

## Best Practices

### ✅ Do

- Inject context progressively (as needed by task stage)
- Use few-shot examples instead of long explanations
- Compress documentation to summaries + links
- Validate context accuracy before injection
- Monitor token usage continuously

### ❌ Don't

- Inject entire documentation at once
- Provide unnecessary files or examples
- Use prose when structured data works better
- Forget to validate context quality
- Assume AI will read full documentation

---

## Example: Complete Workflow

```
1. AI: "I want to implement a new CLI command"

2. System: Queries documentation for task type
   - Identifies: "implement-cli-command"
   - Selects injector: SemanticContextInjector

3. System: Assembles minimal context
   - Primary docs: 800 tokens
   - Examples: 600 tokens
   - Constraints: 400 tokens
   - Related docs: 200 tokens
   - TOTAL: ~2,000 tokens

4. AI: Executes task with context

5. System: Monitors progress
   - Stage: "plan" → inject planning context only
   - Stage: "implement" → inject implementation context
   - Stage: "test" → inject testing context
   - Stage: "verify" → inject verification context

6. System: Validates context accuracy
   - Check against actual codebase
   - Flag any inconsistencies
   - Alert if context is outdated

7. Result: AI completes task efficiently with minimal token overhead
```

---

## Summary

Semantic context injection:
- **Reduces tokens by 90%** (2,000 vs 20,000)
- **Improves AI accuracy** (relevant context only)
- **Enables token monitoring** (track efficiency)
- **Ensures consistency** (context validation)
- **Scales well** (works for any project size)

---

## See Also

- [AGI Ingestion Guide](../../ecosystem/agi-ingestion.md)
- [Token Optimization Guide](./token-optimization.md)
- [Few-Shot Learning Patterns](./few-shot-patterns.md)
