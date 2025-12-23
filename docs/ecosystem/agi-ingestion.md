# AGI Ingestion & AI-Optimized Documentation

**Advanced guide for making ggen Spec Kit documentation maximally useful to AI agents and future AGI systems.**

---

## Table of Contents

1. [Overview](#overview)
2. [Documentation as Structured Data](#documentation-as-structured-data)
3. [RDF-Based Documentation](#rdf-based-documentation)
4. [Semantic Context Windows](#semantic-context-windows)
5. [Few-Shot Examples for AI](#few-shot-examples-for-ai)
6. [Token Optimization](#token-optimization)
7. [Graph-Based Documentation Queries](#graph-based-documentation-queries)
8. [AI-Readable Specifications](#ai-readable-specifications)
9. [Context Injection Patterns](#context-injection-patterns)
10. [Advanced Prompt Engineering](#advanced-prompt-engineering)

---

## Overview

Traditional documentation is optimized for human readers. **AGI-optimized documentation** is designed for both human and AI consumption, enabling:

- **Precise context injection** - AI agents get exactly the information they need
- **Semantic understanding** - Machine-readable structure enables deeper comprehension
- **Token efficiency** - Structured data reduces token overhead
- **Reasoning chains** - Documentation supports AI multi-step reasoning
- **Verification proofs** - Claims are linked to specifications and receipts
- **Cross-reference resolution** - All related concepts are explicitly connected

### Key Principle

```
Traditional Doc: Human-readable prose
AGI-Optimized Doc: Human-readable + Machine-queryable + Semantic + Verifiable
```

---

## Documentation as Structured Data

### Problem: Unstructured Documentation

Traditional Markdown documentation:
```markdown
# CLI Commands

The `specify` command supports the following options:
- `init`: Initialize a new project
- `check`: Check for installed tools
- `version`: Show version information
```

**Problem for AI:**
- Ambiguous structure
- Hard to query programmatically
- No formal semantics
- Can't verify claims without reading entire docs

### Solution: RDF-Based Documentation

```turtle
@prefix spec: <http://ggen-spec-kit.org/spec#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ex: <http://example.org/> .

# Define the CLI Command class
spec:CLICommand
    a rdfs:Class ;
    rdfs:label "CLI Command" ;
    rdfs:comment "A command-line interface command" .

# Define the `init` command
spec:init
    a spec:CLICommand ;
    rdfs:label "init" ;
    rdfs:comment "Initialize a new project" ;
    spec:hasArgument spec:projectName ;
    spec:hasOption spec:aiOption ;
    spec:hasOption spec:scriptOption ;
    spec:exitCode 0 ;
    spec:precedence 1 ;
    spec:documentation <http://docs/tutorials/02-first-project.md> .

# Document relationships
spec:init rdfs:seeAlso spec:check, spec:version .

# Document dependencies
spec:init spec:requires [
    spec:tool "git" ;
    spec:minVersion "2.0" ;
    spec:optional false
] .
```

**Benefits for AI:**
- ✅ Queryable structure
- ✅ Formal semantics
- ✅ Verifiable relationships
- ✅ Machine-executable

---

## RDF-Based Documentation

### Ontology for Documentation Itself

Create `docs/ontology/documentation.ttl`:

```turtle
@prefix doc: <http://ggen-spec-kit.org/documentation#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Documentation classes
doc:Documentation a rdfs:Class ;
    rdfs:label "Documentation" ;
    rdfs:comment "A piece of documentation" .

doc:Tutorial rdfs:subClassOf doc:Documentation ;
    rdfs:label "Tutorial" ;
    rdfs:comment "Learning-oriented documentation" .

doc:HowToGuide rdfs:subClassOf doc:Documentation ;
    rdfs:label "How-To Guide" ;
    rdfs:comment "Task-oriented documentation" .

doc:Reference rdfs:subClassOf doc:Documentation ;
    rdfs:label "Reference" ;
    rdfs:comment "Information-oriented documentation" .

doc:Explanation rdfs:subClassOf doc:Documentation ;
    rdfs:label "Explanation" ;
    rdfs:comment "Understanding-oriented documentation" .

# Documentation properties
doc:title a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range rdfs:Literal .

doc:content a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range rdfs:Literal .

doc:learningTime a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range xsd:duration ;
    rdfs:comment "Time to complete (e.g., PT10M)" .

doc:prerequisites a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range doc:Documentation .

doc:relatedTo a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range doc:Documentation .

doc:verifiedBy a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range doc:Specification ;
    rdfs:comment "Which specification verifies this documentation" .

doc:exampleCode a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range rdfs:Literal .

doc:difficultyLevel a rdf:Property ;
    rdfs:domain doc:Documentation ;
    rdfs:range [ rdf:type rdfs:Class ; rdfs:comment "Beginner, Intermediate, Advanced" ] .

# SHACL Shape for validation
doc:DocumentationShape
    a sh:NodeShape ;
    sh:targetClass doc:Documentation ;
    sh:property [
        sh:path doc:title ;
        sh:minCount 1 ;
        sh:datatype xsd:string
    ] ;
    sh:property [
        sh:path doc:content ;
        sh:minCount 1 ;
        sh:datatype xsd:string
    ] .
```

### Example: RDF-Based Tutorial

```turtle
@prefix doc: <http://ggen-spec-kit.org/documentation#> .
@prefix spec: <http://ggen-spec-kit.org/spec#> .
@prefix ex: <http://example.org/tutorial#> .

ex:tutorial-01-getting-started
    a doc:Tutorial ;
    doc:title "Tutorial 1: Getting Started" ;
    doc:learningTime "PT10M"^^xsd:duration ;
    doc:difficultyLevel "Beginner" ;
    doc:prerequisites [] ;  # No prerequisites
    doc:content "..." ;  # Full tutorial text
    doc:verifiedBy spec:Specify ;
    doc:relatedTo ex:tutorial-02-first-project ;
    doc:exampleCode "uv tool install specify-cli --from ..." ;
    doc:outcome [
        a doc:LearningOutcome ;
        rdfs:label "Understand RDF-first development" ;
        doc:verified true
    ] .

# Link to actual file for human reading
ex:tutorial-01-getting-started
    doc:markdownFile "docs/tutorials/01-getting-started.md" ;
    doc:htmlFile "docs/tutorials/01-getting-started.html" ;
    doc:jsonldFile "docs/tutorials/01-getting-started.jsonld" .
```

---

## Semantic Context Windows

### Problem: Token Waste

Traditional approach when AI needs help:
```
Include entire README.md (10,000 tokens)
+ entire ARCHITECTURE.md (8,000 tokens)
+ relevant how-to guide (5,000 tokens)
= 23,000 tokens just for context

With 100k context window: 77% wasted on irrelevant info
```

### Solution: Semantic Context Queries

Create `sparql/documentation-query.rq`:

```sparql
PREFIX doc: <http://ggen-spec-kit.org/documentation#>
PREFIX spec: <http://ggen-spec-kit.org/spec#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Query: "Get minimal documentation for implementing a CLI command"
SELECT ?title ?content ?example ?relatedConcept
WHERE {
    # Find the how-to guide
    ?guide a doc:HowToGuide ;
            rdfs:label "How to Add a CLI Command" ;
            doc:content ?content ;
            doc:exampleCode ?example ;
            doc:title ?title .

    # Get related concepts (but not full documentation)
    ?guide doc:relatedTo ?related .
    ?related rdfs:label ?relatedConcept ;
            doc:difficultyLevel ?level .

    # Filter to same difficulty level
    FILTER(?level = "Intermediate")
}
LIMIT 5
```

**Usage:**
```bash
# Query documentation for exact context needed
ggen query-docs --topic "add-cli-command" --maxTokens 2000
```

**Output:** Only ~2,000 tokens of relevant information.

---

## Few-Shot Examples for AI

Create `docs/examples/ai-learning/few-shot-patterns.md`:

### Pattern 1: RDF Specification Pattern

**Task:** Add a new CLI command

**Few-shot examples:**

```turtle
# Example 1: Simple command
sk:hello a sk:Command ;
    rdfs:label "hello" ;
    sk:description "Greet the user" .

# Example 2: Command with arguments
sk:init a sk:Command ;
    rdfs:label "init" ;
    sk:description "Initialize a project" ;
    sk:hasArgument sk:projectName ;
    sk:hasArgument sk:location .

# Example 3: Complex command with options
sk:build a sk:Command ;
    rdfs:label "build" ;
    sk:description "Build the project" ;
    sk:hasOption sk:outputFormat ;
    sk:hasOption sk:verbose ;
    sk:hasOption sk:parallel .
```

**Pattern:** AI can learn from examples and apply to new commands.

### Pattern 2: Test Pattern

**Few-shot test examples:**

```python
# Example 1: Simple unit test
def test_hello_operation(self):
    result = hello_operation()
    assert "Hello" in result

# Example 2: Parameterized test
@pytest.mark.parametrize("name,expected", [
    ("World", "Hello, World"),
    ("Alice", "Hello, Alice"),
])
def test_hello_with_names(self, name, expected):
    assert expected in hello_operation(name)

# Example 3: Edge case test
def test_hello_empty_string(self):
    with pytest.raises(ValueError):
        hello_operation("")
```

**Pattern:** AI can learn testing patterns and apply consistently.

### Pattern 3: Documentation Pattern

**Few-shot documentation examples:**

```markdown
# Example 1: Simple function doc
def operation(name: str) -> str:
    """Generate greeting.

    Parameters
    ----------
    name : str
        Person to greet

    Returns
    -------
    str
        Greeting message
    """

# Example 2: With raises
def operation(required: bool = True) -> str:
    """Do something.

    Raises
    ------
    ValueError
        If required is True but input is empty
    """

# Example 3: With examples
def operation(data: dict) -> dict:
    """Process data.

    Examples
    --------
    >>> operation({"name": "Alice"})
    {"greeting": "Hello, Alice"}
    """
```

---

## Token Optimization

### Strategy 1: Compressed Representations

Instead of full markdown:
```markdown
# Tutorial 1: Getting Started

This comprehensive tutorial teaches you the fundamentals of Spec Kit.
It covers installation, basic concepts, and your first project...
[500 lines of text]
= 2,000 tokens
```

Use compressed semantic representation:
```jsonld
{
  "@type": "doc:Tutorial",
  "@id": "tutorial-01",
  "title": "Getting Started",
  "duration": "PT10M",
  "prerequisites": [],
  "outcomes": [
    "Understand RDF-first development",
    "Install Specify CLI",
    "Verify installation"
  ],
  "nextSteps": ["tutorial-02"],
  "keyPoints": [
    "RDF is source of truth",
    "Three-tier architecture",
    "Constitutional equation"
  ]
}
= 150 tokens (7.5% original size)
```

### Strategy 2: Progressive Disclosure

Provide information in layers:

**Layer 1: Summary** (~100 tokens)
```
Topic: RDF Specifications
Summary: Machine-readable domain definitions
Key concept: Source of truth for code generation
```

**Layer 2: Details** (+300 tokens)
```
Structure:
- Uses Turtle syntax
- SHACL validation
- SPARQL queries for extraction
- Tera templates for code gen
```

**Layer 3: Full** (+2000 tokens)
```
Complete tutorial with examples...
```

AI requests only the layers needed.

### Strategy 3: Knowledge Graphs

Instead of prose, use structured facts:

```json
{
  "concept": "constitutional-equation",
  "equation": "spec.md = μ(feature.ttl)",
  "meaning": [
    "Markdown docs generated from RDF specs",
    "μ is 5-stage transformation",
    "RDF is source of truth"
  ],
  "components": {
    "feature.ttl": "RDF specification in Turtle",
    "μ₁": "Normalize (SHACL validation)",
    "μ₂": "Extract (SPARQL queries)",
    "μ₃": "Emit (Tera templates)",
    "μ₄": "Canonicalize (formatting)",
    "μ₅": "Receipt (SHA256 hash)"
  },
  "relatedTopics": ["three-tier-architecture", "rdf-first"],
  "verifiedBy": "GGEN_TRANSFORMATION_PROOF"
}
```

---

## Graph-Based Documentation Queries

### SPARQL Query Examples for AI

**Query 1: Find all prerequisites for a task**

```sparql
PREFIX doc: <http://ggen-spec-kit.org/documentation#>

# Find everything needed to implement a CLI command
SELECT ?tutorial ?guide ?reference ?difficulty
WHERE {
    # The goal
    ?howto a doc:HowToGuide ;
           rdfs:label "How to Add a CLI Command" .

    # Prerequisites (transitive)
    ?howto doc:requires* ?prereq .
    ?prereq a doc:Tutorial ;
            rdfs:label ?tutorial ;
            doc:difficultyLevel ?difficulty .

    # Related guides
    ?howto doc:relatedTo ?relatedGuide .
    ?relatedGuide rdfs:label ?guide .

    # Reference materials
    ?relatedGuide doc:references ?ref .
    ?ref a doc:Reference ;
         rdfs:label ?reference .
}
ORDER BY ?difficulty
```

**Query 2: Find verification proofs**

```sparql
PREFIX doc: <http://ggen-spec-kit.org/documentation#>
PREFIX spec: <http://ggen-spec-kit.org/spec#>

# Verify documentation claims with specifications
SELECT ?claim ?specification ?proofFile ?sha256
WHERE {
    ?doc doc:claim ?claim ;
         doc:verifiedBy ?specification .

    ?specification spec:sourceFile ?specFile ;
                   spec:generatedFile ?proofFile ;
                   spec:sha256 ?sha256 ;
                   spec:verified true .
}
```

**Query 3: Recommend next learning steps**

```sparql
PREFIX doc: <http://ggen-spec-kit.org/documentation#>

# Based on completed tutorials, recommend next steps
SELECT ?nextTutorial ?recommendedGuide ?difficulty
WHERE {
    # User completed this tutorial
    ?completed a doc:Tutorial ;
               rdfs:label "Tutorial 3: Write RDF Specs" .

    # Find tutorials that list this as prerequisite
    ?next doc:prerequisites ?completed ;
          doc:difficultyLevel ?difficulty ;
          rdfs:label ?nextTutorial .

    # Find related how-to guides
    ?next doc:relatedTo ?guide ;
    ?guide a doc:HowToGuide ;
           rdfs:label ?recommendedGuide .
}
ORDER BY ?difficulty
```

---

## AI-Readable Specifications

### Specification as Machine-Executable Code

Instead of documentation describing specifications, **make specs self-documenting**:

```turtle
@prefix spec: <http://ggen-spec-kit.org/spec#> .
@prefix shacl: <http://www.w3.org/ns/shacl#> .

# Define the Three-Tier Architecture as executable specification
spec:ThreeTierArchitecture
    a spec:ArchitecturalPattern ;
    spec:name "Three-Tier Architecture" ;
    spec:components (
        spec:CommandsLayer
        spec:OperationsLayer
        spec:RuntimeLayer
    ) ;
    spec:constraints [
        # Commands layer can call Ops
        shacl:sparql """
            SELECT $this WHERE {
                ?this a spec:CommandsLayer ;
                      spec:imports ?module .
                ?module spec:isIn spec:OperationsLayer .
            }
        """ ;
        shacl:message "Commands may only import from Ops layer"
    ] ;
    spec:constraints [
        # Ops layer cannot do I/O
        shacl:sparql """
            SELECT $this WHERE {
                ?this a spec:OperationsLayer ;
                      spec:contains ?function .
                ?function spec:hasSubprocess true .
            }
        """ ;
        shacl:message "Operations layer must not contain subprocess calls"
    ] ;
    spec:verification spec:ArchitectureValidator ;
    spec:verificationProof <http://receipts/architecture-proof.json> .
```

**AI can:**
- ✅ Read and understand the specification
- ✅ Validate code against it
- ✅ Generate code that satisfies it
- ✅ Detect violations automatically

---

## Context Injection Patterns

### Pattern 1: Minimal Context Injection

When AI needs to implement something, inject only relevant context:

```
CONTEXT_NEEDED: "Implement a new CLI command"

INJECTED_CONTEXT = {
    "task_type": "cli_command_implementation",
    "examples": [
        {
            "spec": "sk:hello a sk:Command; rdfs:label 'hello'",
            "code": "[example code]",
            "tests": "[example tests]"
        },
        {
            "spec": "sk:build a sk:Command; ...",
            "code": "[example code]",
            "tests": "[example tests]"
        }
    ],
    "guidelines": "[structured guidelines, not prose]",
    "files_to_edit": [
        "ontology/cli-commands.ttl",
        "src/specify_cli/ops/[command].py",
        "tests/unit/test_[command]_ops.py"
    ],
    "files_to_review": [
        "CLAUDE.md [relevant sections]"
    ],
    "do_not_edit": [
        "src/specify_cli/commands/[auto-generated]",
        "docs/commands/[auto-generated]"
    ]
}
```

### Pattern 2: Semantic Dependencies

Inject not just code, but relationship graphs:

```json
{
  "task": "add-cli-command",
  "dependencies": {
    "rdf_syntax": {
      "link": "ontology/spec-kit-schema.ttl",
      "compressed": true,
      "tokens_max": 500
    },
    "example_commands": {
      "link": "docs/examples/cli-commands/",
      "count": 3,
      "tokens_max": 1000
    },
    "testing_patterns": {
      "link": "docs/tutorials/04-first-test.md",
      "compressed": true,
      "tokens_max": 500
    },
    "architectural_constraints": {
      "link": "docs/explanation/three-tier-architecture.md",
      "compressed": true,
      "tokens_max": 300
    }
  },
  "total_context_tokens": 2300
}
```

### Pattern 3: Dynamic Context Assembly

Request context based on AI reasoning:

```
AI: "I need to understand SHACL validation for this RDF spec"

SYSTEM_RESPONSE:
{
  "concept": "SHACL",
  "definition": "[compressed definition]",
  "in_project_usage": [
    {
      "file": "ontology/spec-kit-schema.ttl",
      "excerpt": "[relevant SHACL shapes]",
      "purpose": "[why it's used here]"
    }
  ],
  "examples": [
    "[few-shot example 1]",
    "[few-shot example 2]"
  ],
  "references": [
    "W3C SHACL spec",
    "docs/reference/rdf-schema.md"
  ]
}
```

---

## Advanced Prompt Engineering

### Prompt 1: Chain-of-Thought Documentation

```
TASK: Implement a new CLI command for data validation

THOUGHT_CHAIN:
1. Understand RDF-first principle
   - Specs are source of truth
   - Code is generated from RDF
   - Tests validate specifications

2. Plan the RDF specification
   - What is the command name?
   - What arguments does it need?
   - What options should it support?
   - What does success look like?

3. Write the RDF specification
   - Edit ontology/cli-commands.ttl
   - Define all properties
   - Follow established patterns

4. Generate code
   - Run: ggen sync
   - Review generated skeleton
   - Understand what was auto-generated

5. Implement logic
   - Edit ops/[command].py
   - Add business logic
   - Keep pure (no side effects)

6. Write tests
   - Unit tests in tests/unit/
   - E2E tests in tests/e2e/
   - Achieve >80% coverage

7. Verify
   - Run: uv run pytest
   - All tests pass
   - No lint errors

CONTEXT_NEEDED: [inject relevant docs for each step]
```

### Prompt 2: Verification-Driven Documentation

```
TASK: Verify documentation matches code

VERIFICATION_CHAIN:
1. Load documentation RDF
   - Parse docs/ontology/documentation.ttl
   - Extract all claims

2. Load specification RDF
   - Parse ontology/cli-commands.ttl
   - Parse memory/*.ttl

3. Cross-reference
   - For each doc claim
   - Find corresponding spec
   - Check proof file (receipt.json)

4. Validate
   - Verify SHA256 hashes
   - Check code generation
   - Ensure no drift

5. Report
   - List verified claims
   - Flag unverified claims
   - Suggest updates

VERIFICATION_LOGIC:
if documentation_claim in specification:
    if sha256_hash_matches(claim, proof):
        return VERIFIED
    else:
        return OUTDATED
else:
    return UNVERIFIED
```

### Prompt 3: Token-Efficient Code Review

```
TASK: Review code against architectural constraints

REVIEW_FRAMEWORK:
1. Load constraints
   - Query: architectural-constraints.rq
   - Load: CLAUDE.md (three-tier section compressed)

2. Analyze code structure
   - Commands layer: [check imports]
   - Operations layer: [check for I/O]
   - Runtime layer: [check uses]

3. Validate against SHACL
   - Load: ontology/spec-kit-schema.ttl
   - Run: SHACL validator
   - Report violations

4. Cross-check with spec
   - Load: specification.ttl
   - Verify: code matches spec
   - Check: tests validate spec

5. Generate report
   - Compliance: Y/N
   - Issues: [list]
   - Recommendations: [list]
```

---

## Implementation Checklist

- [ ] Create RDF ontology for documentation (`docs/ontology/documentation.ttl`)
- [ ] Create SPARQL queries for documentation (`docs/sparql/documentation-*.rq`)
- [ ] Generate JSON-LD versions of all docs
- [ ] Create few-shot examples directory (`docs/examples/ai-learning/`)
- [ ] Build documentation query service
- [ ] Create semantic context injector
- [ ] Generate static documentation graph (`.jsonld`)
- [ ] Add verification proofs to documentation
- [ ] Create AI-friendly quick reference guides
- [ ] Build token counter/optimizer

---

## Example: Complete AGI Workflow

### Scenario: AI Agent Implementing New Feature

```
STEP 1: Request
  AI: "I need to implement a new 'validate' command"

STEP 2: System injects semantic context (2,300 tokens)
  - RDF specification pattern (compressed)
  - 3 similar command examples
  - Testing patterns
  - Architecture constraints

STEP 3: AI Plans (generates structured plan)
  1. Create RDF spec in ontology/cli-commands.ttl
  2. Run ggen sync to generate skeleton
  3. Implement ops/validate.py
  4. Write tests
  5. Verify against SHACL shapes

STEP 4: AI Executes each step
  - Creates RDF following few-shot patterns
  - Verifies against ontology shape
  - Generates code from RDF
  - Implements using code examples
  - Writes tests matching test patterns

STEP 5: System Verifies
  - Validates RDF syntax
  - Checks SHACL shapes
  - Verifies code matches spec
  - Confirms tests pass
  - Generates proof receipt (SHA256)

STEP 6: Documentation Updated
  - Generated from RDF
  - Verified against specification
  - Proof linked to documentation
  - Available in multiple formats (MD, HTML, JSON-LD, RDF/Turtle)

RESULT: Complete, verified implementation with self-documenting code
```

---

## Benefits for AGI Systems

### ✅ Precision
- Exact semantic understanding
- No ambiguity in specifications
- Machine-verifiable claims

### ✅ Efficiency
- Token-optimized context
- No wasted information
- Fast semantic queries

### ✅ Reasoning
- Documentation is queryable
- Relationships are explicit
- Multi-step reasoning supported

### ✅ Verification
- Specifications are executable
- Proofs are cryptographic (SHA256)
- No documentation drift

### ✅ Learning
- Few-shot examples are structured
- Patterns are machine-recognizable
- Generalization is systematic

### ✅ Autonomy
- AI can verify its own work
- Self-correcting systems
- Continuous improvement

---

## Future Directions

### 1. Self-Modifying Documentation
- AI updates RDF specifications
- System auto-generates new code
- Proofs track all changes

### 2. Documentation Search
- Semantic search across docs
- "Find all commands that create files"
- "What patterns do validation operations follow?"

### 3. Automatic Error Detection
- AI finds documentation errors
- Verifies against specifications
- Suggests corrections

### 4. Multi-Agent Coordination
- Multiple AI agents with shared RDF
- Coordinate via specifications
- Conflict resolution via SHACL

### 5. Continuous Documentation
- Real-time documentation updates
- Specifications drive everything
- Perfect synchronization

---

## Conclusion

AGI-optimized documentation:
- **Treats documentation as executable specifications**
- **Reduces token overhead by 10-50x**
- **Enables AI to verify and improve itself**
- **Creates foundation for autonomous agents**
- **Maintains perfect sync between spec and implementation**

The constitutional equation extends to documentation:
```
documentation.md = μ(documentation.ttl)
```

Where documentation is not just human-readable prose, but **machine-executable specifications that guide both humans and AI systems.**

---

## Related Resources

- [CLAUDE.md](../../CLAUDE.md) - Developer guide for AI agents
- [Explanation: Constitutional Equation](../explanation/constitutional-equation.md)
- [Explanation: RDF-First Development](../explanation/rdf-first-development.md)
- [Reference: RDF Ontology](../reference/rdf-ontology.md)
- [Reference: SPARQL Queries](../reference/sparql-queries.md)

