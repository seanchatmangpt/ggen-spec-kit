# 22. Normalization Stage

★★

*Before transformation, validation. The normalization stage (μ₁) ensures source specifications conform to their shapes, failing fast when they don't. This is the gatekeeper that prevents bad specifications from producing bad artifacts.*

---

## The Gatekeeper

The **[Constitutional Equation](./constitutional-equation.md)** begins its work with normalization. This first stage (μ₁) takes raw RDF input and validates it against SHACL shapes before any other processing occurs.

Consider what happens without this gate:

```turtle
# A malformed specification
:validateCommand a cli:Command ;
    rdfs:label "validate" ;
    # Missing required description!
    cli:hasArgument [
        cli:type "Path" ;
        # Missing argument name!
    ] .
```

Without normalization, this specification enters the pipeline. The extraction query might succeed (with nulls). The template might render (with blanks). The output looks almost right—but it's subtly wrong. A command exists without a description. An argument has a type but no name.

These subtle errors are the worst kind. They don't crash the system; they corrupt it. Users encounter inexplicable behavior. Debugging is difficult because the symptom is far from the cause.

Normalization prevents this by validating at the start. Invalid specifications fail immediately, with clear messages pointing to exactly what's wrong. No corruption propagates.

---

## The Validation Challenge

**The core problem: Invalid specifications can produce subtle errors that surface far from their source, making debugging difficult and eroding trust. Early validation catches problems when they're cheapest to fix.**

Let us examine why this matters:

### The Cost of Late Failure

Errors discovered later cost more to fix:

| Discovery Point | Relative Cost | Example |
|-----------------|---------------|---------|
| During specification | 1x | "This shape is invalid" |
| During extraction | 5x | "Query failed - missing property" |
| During emission | 10x | "Template error - null value" |
| During runtime | 50x | "Command crashes with NoneType" |
| In production | 100x | "Customer reports feature doesn't work" |

Normalization catches errors at the 1x cost level—the cheapest possible point.

### The Clarity of Shape Validation

SHACL shapes provide remarkably clear validation:

```turtle
sk:CommandShape a sh:NodeShape ;
    sh:targetClass cli:Command ;
    sh:property [
        sh:path cli:description ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 10 ;
        sh:message "Command must have a description of at least 10 characters" ;
    ] .
```

When validation fails, the message tells you exactly:
- Which shape failed (`CommandShape`)
- Which node is invalid (`cli:ValidateCommand`)
- Which property is wrong (`cli:description`)
- What the constraint requires (at least 10 characters)
- What to fix (add a proper description)

Compare this to a runtime error: "AttributeError: NoneType has no attribute 'strip'"

### The Contract Enforcement

SHACL shapes are not just validation—they're contracts. The shape defines what a valid specification looks like. Any specification that passes validation is guaranteed to have the structure subsequent stages expect.

This guarantee is powerful:
- **Extraction queries** can assume required properties exist
- **Templates** can assume non-null values
- **Downstream code** can assume correct types

---

## The Forces

Several tensions shape normalization design:

### Force: Speed vs. Thoroughness

*Validation takes time. Thorough validation takes more time.*

For a small specification, validation is instant. For a large knowledge graph with complex shapes, validation might take seconds. How much validation is too much?

```
Validation Thoroughness
         │
         │    ┌─── Production: Comprehensive
         │    │
         ├────┼─── Development: Standard
         │    │
         │    └─── Prototyping: Minimal
         │
         └────────────────────────────► Speed
```

The resolution: configurable validation modes that allow developers to trade thoroughness for speed during development, with strict validation enforced for production.

### Force: Clarity vs. Completeness

*Error messages should be clear and actionable. But comprehensive validation produces many errors.*

When ten things are wrong, should you report all ten at once? Or stop at the first error?

Arguments for all-at-once:
- Developer can fix everything in one pass
- No "whack-a-mole" fixing

Arguments for first-only:
- Simpler error output
- Later errors might cascade from earlier ones

The resolution: report all errors, but group and prioritize them meaningfully.

### Force: Strictness vs. Flexibility

*Strict validation catches more errors. But draft specifications might intentionally be incomplete.*

During exploration, you might write:

```turtle
:newCommand a cli:Command ;
    rdfs:label "new-command" .
    # Still figuring out arguments...
```

This is intentionally incomplete. Should validation fail?

```
        Strictness
             │
   Reject    │    Accept
   incomplete│    incomplete
             │
             ├────────────────────────►
             │                    Flexibility
             │
   strict mode    warn mode    skip mode
```

The resolution: validation modes (strict/warn/skip) that developers can select based on context.

### Force: Schema Evolution

*SHACL shapes evolve. Old specifications might not match new shapes.*

You add a new required property to your shape:

```turtle
# New constraint added
sh:property [
    sh:path cli:rationale ;
    sh:minCount 1 ;
    sh:message "All commands must have a rationale" ;
] .
```

Now all existing specifications are invalid. How do you migrate?

The resolution: versioned shapes, migration tooling, and transitional validation that warns about new requirements before making them mandatory.

---

## Therefore

**Implement normalization (μ₁) as the first transformation stage, validating source RDF against SHACL shapes before any other processing. Fail fast with clear, actionable error messages when validation fails.**

The normalization pipeline:

```
┌────────────────────────────────────────────────────────────────────┐
│  μ₁ NORMALIZE                                                       │
│                                                                     │
│  1. LOAD source RDF file                                           │
│     ├── Parse Turtle syntax                                        │
│     ├── Resolve prefixes                                           │
│     └── Build in-memory graph                                      │
│                                                                     │
│  2. LOAD SHACL shapes                                               │
│     ├── Parse shape definitions                                    │
│     ├── Resolve shape inheritance                                  │
│     └── Build shape index                                          │
│                                                                     │
│  3. VALIDATE against shapes                                         │
│     ├── For each target class, find instances                      │
│     ├── For each instance, check all shape constraints             │
│     ├── Collect all violations                                     │
│     └── Build validation report                                    │
│                                                                     │
│  4. IF violations:                                                  │
│     ├── Format clear error messages                                │
│     ├── Include line numbers and context                           │
│     ├── Group by severity                                          │
│     └── Exit with failure status                                   │
│                                                                     │
│  5. IF valid:                                                       │
│     ├── Output normalized RDF for next stage                       │
│     ├── Record validation timestamp                                │
│     └── Compute input hash for receipt                             │
│                                                                     │
│  Input: feature.ttl (raw)                                          │
│  Output: feature.ttl (validated) OR validation_report.json (error) │
└────────────────────────────────────────────────────────────────────┘
```

---

## SHACL Shape Design

### Basic Shape Structure

Every shape targets a class and defines property constraints:

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <http://spec-kit.dev/ontology#> .
@prefix cli: <http://spec-kit.dev/cli#> .

# Shape for CLI commands
sk:CommandShape a sh:NodeShape ;
    sh:targetClass cli:Command ;
    sh:nodeKind sh:IRI ;  # Commands must be named resources

    # Required properties
    sh:property [
        sh:path rdfs:label ;
        sh:name "command name" ;
        sh:description "The CLI command name (e.g., 'validate', 'check')" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z][a-z0-9-]*$" ;
        sh:message "Command must have exactly one label matching pattern [a-z][a-z0-9-]*" ;
    ] ;

    sh:property [
        sh:path cli:description ;
        sh:name "description" ;
        sh:description "Human-readable command description" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 10 ;
        sh:maxLength 500 ;
        sh:message "Command must have a description (10-500 characters)" ;
    ] ;

    # Optional but constrained properties
    sh:property [
        sh:path cli:hasArgument ;
        sh:name "arguments" ;
        sh:description "Command arguments" ;
        sh:node sk:ArgumentShape ;  # Arguments validated by their own shape
    ] ;

    # Value constraints
    sh:property [
        sh:path cli:exitCode ;
        sh:datatype xsd:integer ;
        sh:minInclusive 0 ;
        sh:maxInclusive 255 ;
        sh:message "Exit code must be 0-255" ;
    ] .
```

### Nested Shape Validation

Shapes can reference other shapes for nested validation:

```turtle
# Shape for command arguments
sk:ArgumentShape a sh:NodeShape ;
    sh:targetClass cli:Argument ;

    sh:property [
        sh:path cli:name ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z][a-z0-9_]*$" ;
        sh:message "Argument name must be lowercase with underscores" ;
    ] ;

    sh:property [
        sh:path cli:type ;
        sh:minCount 1 ;
        sh:in ( "Path" "str" "int" "bool" "float" ) ;
        sh:message "Argument type must be one of: Path, str, int, bool, float" ;
    ] ;

    sh:property [
        sh:path cli:required ;
        sh:maxCount 1 ;
        sh:datatype xsd:boolean ;
        sh:defaultValue false ;
    ] ;

    sh:property [
        sh:path cli:help ;
        sh:datatype xsd:string ;
        sh:minLength 5 ;
        sh:message "Help text should be at least 5 characters" ;
    ] .
```

### Conditional Constraints

SHACL supports conditional validation:

```turtle
# If a command has --output option, it must also have --format
sk:OutputFormatShape a sh:NodeShape ;
    sh:targetClass cli:Command ;

    sh:sparql [
        sh:message "Commands with --output must also have --format" ;
        sh:select """
            SELECT $this
            WHERE {
                $this cli:hasOption ?output .
                ?output cli:name "output" .
                FILTER NOT EXISTS {
                    $this cli:hasOption ?format .
                    ?format cli:name "format" .
                }
            }
        """ ;
    ] .
```

### Severity Levels

Not all violations are equal:

```turtle
# Violation = hard failure
sh:property [
    sh:path cli:description ;
    sh:minCount 1 ;
    sh:severity sh:Violation ;
    sh:message "REQUIRED: Commands must have a description" ;
] .

# Warning = soft failure (depends on mode)
sh:property [
    sh:path cli:example ;
    sh:minCount 1 ;
    sh:severity sh:Warning ;
    sh:message "RECOMMENDED: Commands should have usage examples" ;
] .

# Info = advisory (never fails)
sh:property [
    sh:path cli:seeAlso ;
    sh:severity sh:Info ;
    sh:message "SUGGESTION: Consider linking to related commands" ;
] .
```

---

## Error Reporting

### Validation Report Structure

When validation fails, produce structured error reports:

```json
{
  "valid": false,
  "file": "ontology/cli-commands.ttl",
  "timestamp": "2025-01-15T10:30:00Z",
  "validator": "pyshacl v0.25.0",

  "summary": {
    "violations": 3,
    "warnings": 1,
    "info": 2
  },

  "results": [
    {
      "severity": "Violation",
      "shape": "sk:CommandShape",
      "focus": "cli:ValidateCommand",
      "path": "cli:description",
      "message": "Command must have a description (10-500 characters)",
      "value": null,
      "source_line": 42,
      "context": [
        "40: cli:ValidateCommand a cli:Command ;",
        "41:     rdfs:label \"validate\" ;",
        "42:     # description is missing!",
        "43:     cli:hasArgument [ ... ] ."
      ],
      "suggestion": "Add: cli:description \"Validates RDF files against SHACL shapes\" ;"
    },
    {
      "severity": "Violation",
      "shape": "sk:ArgumentShape",
      "focus": "_:b1",
      "path": "cli:name",
      "message": "Argument name must be lowercase with underscores",
      "value": "File",
      "source_line": 45,
      "suggestion": "Change 'File' to 'file'"
    }
  ]
}
```

### Human-Readable Output

For terminal display:

```
╔══════════════════════════════════════════════════════════════════════╗
║  VALIDATION FAILED: ontology/cli-commands.ttl                        ║
╚══════════════════════════════════════════════════════════════════════╝

┌─ Error 1/3 ─────────────────────────────────────────────────────────┐
│  Shape:   sk:CommandShape                                            │
│  Node:    cli:ValidateCommand                                        │
│  Path:    cli:description                                            │
│  Message: Command must have a description (10-500 characters)        │
│                                                                      │
│  Location: line 42                                                   │
│                                                                      │
│    40 │ cli:ValidateCommand a cli:Command ;                          │
│    41 │     rdfs:label "validate" ;                                  │
│  > 42 │     # description is missing!                                │
│    43 │     cli:hasArgument [ ... ] .                                │
│                                                                      │
│  Fix: Add cli:description "Validates RDF files..." ;                 │
└──────────────────────────────────────────────────────────────────────┘

┌─ Error 2/3 ─────────────────────────────────────────────────────────┐
│  Shape:   sk:ArgumentShape                                           │
│  Node:    _:b1 (blank node in ValidateCommand)                      │
│  Path:    cli:name                                                   │
│  Message: Argument name must be lowercase with underscores           │
│  Value:   "File" (should be "file")                                  │
│                                                                      │
│  Location: line 45                                                   │
│  Fix: Change cli:name "File" to cli:name "file"                     │
└──────────────────────────────────────────────────────────────────────┘

┌─ Warning 1/1 ───────────────────────────────────────────────────────┐
│  Shape:   sk:CommandShape                                            │
│  Node:    cli:CheckCommand                                           │
│  Path:    cli:example                                                │
│  Message: Commands should have usage examples                        │
│                                                                      │
│  Suggestion: Add cli:example "check file.ttl" ;                      │
└──────────────────────────────────────────────────────────────────────┘

════════════════════════════════════════════════════════════════════════
  3 violations must be fixed before transformation can proceed.
  1 warning can be addressed later.

  Run with --mode=warn to continue despite warnings.
════════════════════════════════════════════════════════════════════════
```

---

## Configuration

### Validation Modes

```toml
# ggen.toml
[validation]
mode = "strict"  # Options: strict | warn | skip

# Mode behaviors:
# strict: All violations and warnings are failures
# warn:   Only violations are failures; warnings are logged
# skip:   No validation (use carefully!)

# Shape files to use
shapes = [
    "shapes/command-shape.ttl",
    "shapes/argument-shape.ttl",
    "shapes/option-shape.ttl"
]

# Error handling
[validation.errors]
format = "pretty"      # pretty | json | compact
include_context = true # Show surrounding lines
line_numbers = true    # Show source line numbers
suggestions = true     # Generate fix suggestions
max_errors = 50        # Stop after N errors (0 = no limit)

# Severity handling
[validation.severity]
violation = "error"   # error | warn | ignore
warning = "warn"      # error | warn | ignore
info = "ignore"       # error | warn | ignore
```

### Per-Target Configuration

Different targets might need different validation:

```toml
[[targets]]
name = "production-commands"
source = "ontology/cli-commands.ttl"
validation.mode = "strict"
validation.shapes = ["shapes/full-command-shape.ttl"]

[[targets]]
name = "experimental-commands"
source = "ontology/experimental.ttl"
validation.mode = "warn"
validation.shapes = ["shapes/minimal-command-shape.ttl"]
```

### Development vs. Production

```toml
# development.toml
[validation]
mode = "warn"  # Continue despite warnings during dev

# production.toml (extends development.toml)
[validation]
mode = "strict"  # Strict in production
```

---

## Implementation Patterns

### The Validation Function

```python
from pyshacl import validate
from rdflib import Graph

def normalize_specification(
    source_path: Path,
    shape_paths: list[Path],
    mode: str = "strict"
) -> tuple[Graph, ValidationReport]:
    """
    Normalize (validate) a specification against SHACL shapes.

    Args:
        source_path: Path to Turtle specification
        shape_paths: Paths to SHACL shape files
        mode: Validation mode (strict|warn|skip)

    Returns:
        Tuple of (validated graph, validation report)

    Raises:
        ValidationError: If validation fails in strict mode
    """
    # Load source
    source_graph = Graph()
    source_graph.parse(source_path, format="turtle")

    # Load and merge shapes
    shapes_graph = Graph()
    for shape_path in shape_paths:
        shapes_graph.parse(shape_path, format="turtle")

    # Skip validation if requested
    if mode == "skip":
        return source_graph, ValidationReport(valid=True, skipped=True)

    # Run SHACL validation
    conforms, results_graph, results_text = validate(
        data_graph=source_graph,
        shacl_graph=shapes_graph,
        inference='rdfs',  # Enable RDFS inference
        abort_on_first=False,  # Collect all errors
        advanced=True,  # Enable SPARQL-based constraints
    )

    # Parse results
    report = parse_validation_results(results_graph, source_path)

    # Apply mode logic
    if not conforms:
        if mode == "strict":
            raise ValidationError(report)
        elif mode == "warn":
            log_warnings(report)

    return source_graph, report
```

### Error Enhancement

Add source context to validation errors:

```python
def enhance_validation_error(
    error: SHACLResult,
    source_lines: list[str]
) -> EnhancedError:
    """Add source context and suggestions to validation error."""

    # Find the source line (requires line number tracking during parse)
    line_num = find_source_line(error.focus_node, source_lines)

    # Extract context window
    context_start = max(0, line_num - 2)
    context_end = min(len(source_lines), line_num + 2)
    context = source_lines[context_start:context_end]

    # Generate fix suggestion
    suggestion = generate_suggestion(error)

    return EnhancedError(
        severity=error.severity,
        shape=error.source_shape,
        focus=error.focus_node,
        path=error.result_path,
        message=error.message,
        value=error.value,
        source_line=line_num,
        context=context,
        suggestion=suggestion
    )

def generate_suggestion(error: SHACLResult) -> str:
    """Generate actionable fix suggestion."""

    if error.path and error.min_count and not error.value:
        # Missing required property
        return f"Add: {error.path} \"...\" ;"

    elif error.pattern and error.value:
        # Value doesn't match pattern
        return f"Change '{error.value}' to match pattern {error.pattern}"

    elif error.in_values and error.value:
        # Value not in allowed set
        return f"Change '{error.value}' to one of: {', '.join(error.in_values)}"

    else:
        return "Check the constraint and fix accordingly"
```

### Hash Generation for Receipts

After validation succeeds, compute hashes for the receipt:

```python
def compute_validation_hashes(
    source_graph: Graph,
    shapes_graph: Graph
) -> dict:
    """Compute hashes for receipt generation."""

    # Serialize to canonical form (N-Triples sorted)
    source_canonical = source_graph.serialize(format='nt')
    source_canonical = '\n'.join(sorted(source_canonical.strip().split('\n')))

    shapes_canonical = shapes_graph.serialize(format='nt')
    shapes_canonical = '\n'.join(sorted(shapes_canonical.strip().split('\n')))

    return {
        "source_hash": hashlib.sha256(source_canonical.encode()).hexdigest(),
        "shapes_hash": hashlib.sha256(shapes_canonical.encode()).hexdigest(),
        "combined_hash": hashlib.sha256(
            (source_canonical + shapes_canonical).encode()
        ).hexdigest()
    }
```

---

## Case Study: The SHACL Migration

*A team evolves their shapes while maintaining compatibility.*

### The Situation

The DataOps team had been using specification-driven development for eight months. Their SHACL shapes worked well, but new requirements emerged:

1. All commands now needed a "rationale" explaining why they exist
2. Arguments needed more type specificity (Path vs. FilePath vs. DirectoryPath)
3. Commands needed to declare their resource usage (CPU/memory hints)

The problem: 47 existing specifications would fail validation with new shapes.

### The Migration Strategy

**Phase 1: Warning Period**

Add new constraints at Warning severity:

```turtle
# New constraint as warning (not failure)
sh:property [
    sh:path cli:rationale ;
    sh:minCount 1 ;
    sh:severity sh:Warning ;  # Warning, not Violation
    sh:message "UPCOMING REQUIREMENT: Commands will need a rationale" ;
] .
```

CI logs warnings but doesn't fail. Developers see what's coming.

**Phase 2: Gradual Compliance**

Track compliance progress:

```bash
$ ggen validate --report=compliance

Compliance Report: 2025-01-15
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Upcoming Requirements:
  cli:rationale     34/47 commands compliant (72%)
  cli:resourceHint  12/47 commands compliant (26%)
  Refined types     41/47 commands compliant (87%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Deadline: 2025-03-01 (45 days remaining)
```

**Phase 3: Deadline Enforcement**

On the deadline, elevate to Violation:

```turtle
sh:property [
    sh:path cli:rationale ;
    sh:minCount 1 ;
    sh:severity sh:Violation ;  # Now required
    sh:message "Command must have a rationale" ;
] .
```

Non-compliant specifications now fail.

**Phase 4: Version Tagging**

Tag shape versions for rollback capability:

```turtle
sk:CommandShape
    a sh:NodeShape ;
    owl:versionInfo "2.0.0" ;
    sk:compatibleWith "1.x" ;  # Can still validate 1.x specs
    rdfs:comment "Requires rationale since v2.0" .
```

### The Results

- Zero surprise failures (warnings gave advance notice)
- Three-week migration window (developers fixed at their pace)
- 100% compliance by deadline
- Clear version history for audit

---

## Anti-Patterns

### Anti-Pattern: Validation Avoidance

*"Validation is slow, let's skip it for local development."*

Skipping validation locally means developers write invalid specifications, only discovering problems in CI (or production). The "time saved" is paid back with interest.

**Resolution:** Optimize validation instead of skipping it. Use incremental validation for unchanged portions.

### Anti-Pattern: Shape Sprawl

*"Each command gets its own shape with copy-pasted constraints."*

```turtle
# Shape sprawl - don't do this
sk:ValidateCommandShape a sh:NodeShape ;
    sh:targetNode cli:ValidateCommand ;
    sh:property [ sh:path cli:description ; ... ] .

sk:CheckCommandShape a sh:NodeShape ;
    sh:targetNode cli:CheckCommand ;
    sh:property [ sh:path cli:description ; ... ] .  # Same constraints!
```

**Resolution:** Use inheritance and composition:

```turtle
# Base shape
sk:CommandShape a sh:NodeShape ;
    sh:targetClass cli:Command ;
    sh:property [ sh:path cli:description ; ... ] .

# Specialized shapes inherit via sh:and
sk:AdminCommandShape a sh:NodeShape ;
    sh:targetClass cli:AdminCommand ;
    sh:and ( sk:CommandShape ) ;  # Inherit all constraints
    sh:property [ sh:path cli:requiresAdmin ; sh:hasValue true ] .
```

### Anti-Pattern: Silent Warnings

*"Warnings are just logged—nobody reads logs."*

If warnings are ignored, they're useless. If they're annoying, they get filtered out. Either way, the warning capability is wasted.

**Resolution:** Make warnings visible and actionable:
- Summary in CI output
- Dashboard tracking warning trends
- Periodic escalation of persistent warnings

### Anti-Pattern: Validator Version Mismatch

*"The CI validator is different from my local one."*

Different SHACL implementations have subtle differences. What passes locally might fail in CI (or vice versa).

**Resolution:** Pin validator versions in both environments. Use containers for consistency.

---

## Implementation Checklist

### Shape Development

- [ ] Define shapes for all specification classes
- [ ] Use inheritance for shared constraints
- [ ] Add custom error messages to all constraints
- [ ] Include pattern constraints for naming conventions
- [ ] Define severity levels (Violation/Warning/Info)
- [ ] Add validation for cross-property constraints

### Validation Pipeline

- [ ] Implement validation as first pipeline stage
- [ ] Configure validation modes (strict/warn/skip)
- [ ] Enhance errors with source context
- [ ] Generate actionable suggestions
- [ ] Compute hashes for receipts
- [ ] Cache validation results for unchanged files

### Error Reporting

- [ ] Support multiple output formats (pretty/json/compact)
- [ ] Include source line numbers
- [ ] Show context window around errors
- [ ] Group errors by type/severity
- [ ] Generate machine-readable reports for CI

### Workflow Integration

- [ ] Add pre-commit validation hook
- [ ] Configure CI validation step
- [ ] Create validation dashboard
- [ ] Document shape evolution process
- [ ] Set up compliance tracking for migrations

---

## Exercises

### Exercise 1: First Shape

Create a SHACL shape for a simple class:

1. Define a shape for `Book` requiring title, author, and ISBN
2. Add pattern constraints for ISBN format
3. Add cardinality constraints
4. Write a valid and invalid book specification
5. Run validation and observe the output

### Exercise 2: Error Enhancement

Improve error reporting:

1. Take a validation error from pyshacl
2. Parse source file to find line numbers
3. Extract context window
4. Generate fix suggestion
5. Format for human display

### Exercise 3: Migration Simulation

Simulate a shape migration:

1. Create v1 shape with basic constraints
2. Write specifications conforming to v1
3. Create v2 shape adding new requirements as warnings
4. Run validation, observe warnings
5. Elevate to violations, observe failures
6. Fix specifications, achieve compliance

### Exercise 4: Custom Constraint

Write a SPARQL-based custom constraint:

1. Design a constraint that can't be expressed with basic SHACL
   (e.g., "commands can't have duplicate argument names")
2. Implement as sh:sparql constraint
3. Test with valid and invalid specifications
4. Document the constraint

---

## Resulting Context

After implementing this pattern, you have:

- **Early failure** for invalid specifications, catching problems at lowest cost
- **Clear error messages** with source context and fix suggestions
- **Configurable strictness** for development vs. production needs
- **Validated input** for subsequent pipeline stages
- **Hash generation** feeding into receipt creation
- **Migration support** through severity levels and versioning

This stage establishes the foundation for trustworthy transformation. Invalid input cannot produce valid output—normalization ensures only valid input enters the pipeline.

---

## Related Patterns

- **Part of:** **[21. Constitutional Equation](./constitutional-equation.md)** — Stage μ₁
- **Uses:** **[12. Shape Constraint](../specification/shape-constraint.md)** — SHACL shapes
- **Precedes:** **[23. Extraction Query](./extraction-query.md)** — Next pipeline stage
- **Feeds:** **[26. Receipt Generation](./receipt-generation.md)** — Validation hashes

---

## Philosophical Note

> *"An ounce of prevention is worth a pound of cure."*
> — Benjamin Franklin

Normalization is prevention. It catches errors before they propagate through extraction, emission, deployment, and production. The investment in good shapes and clear validation pays dividends at every subsequent stage.

The shape is a contract. Validation enforces the contract. With enforcement, contracts can be trusted. With trust, systems can be built that assume the contract holds.

This is the essence of specification-driven development: declare your contracts formally, enforce them automatically, and build on the assumption that they hold.

---

**Next:** The validated specification flows to **[23. Extraction Query](./extraction-query.md)**, where SPARQL queries shape the data for template consumption.
