# 12. Shape Constraint

★★

*Freedom without constraint leads to chaos. Constraints without purpose lead to bureaucracy. Shape constraints define the structure of valid specifications—strict enough to prevent errors, flexible enough to allow expression. They are the grammar of your specification language.*

---

## The Need for Structure

You've committed to **[Executable Specifications](./executable-specification.md)**. Execution requires validation. Validation requires constraints. Without constraints, any RDF is valid—including nonsensical or incomplete specifications that will break downstream processing.

RDF's flexibility is both strength and weakness. You can say anything about anything. The triple `<person> <favorite-color> <42>` is syntactically valid RDF, even though it's semantically dubious. Without constraints, your specifications become a wilderness where anything goes.

Shape constraints tame this wilderness. They define what a well-formed specification looks like:

- **What properties must be present?** Every command needs a name.
- **What values are allowed?** Types must be one of a defined set.
- **What relationships must exist?** Arguments must have types.
- **What patterns must be followed?** Names must be lowercase alphanumeric.
- **What combinations are forbidden?** Required arguments can't have defaults.

These constraints are not bureaucracy imposed from outside. They are the grammar of your specification language—the rules that enable communication and automated processing. Just as natural language has grammar that enables understanding, shape constraints enable shared meaning and machine interpretation.

---

## The Constraint Philosophy

### Grammar, Not Red Tape

Constraints often feel restrictive. "Why can't I just..." is the natural response. But consider natural language: grammar constrains what sentences you can form. Without grammar, language becomes incomprehensible noise.

Shape constraints are the grammar of your specification language. They don't limit what you can express—they ensure what you express is coherent. A constraint that "every command must have a description" isn't red tape; it's ensuring every command is understandable.

### Fail Fast, Fail Clearly

The purpose of validation is to catch errors early—before they propagate through the pipeline. An invalid specification caught during editing is trivial to fix. The same error caught after code generation, deployment, and user complaints is expensive.

Validation should:
1. **Fail fast**: Catch errors as early as possible
2. **Fail clearly**: Provide actionable error messages
3. **Fail completely**: Don't partially validate and let some errors through

### The Constraint Spectrum

Constraints exist on a spectrum from permissive to restrictive:

```
Permissive                                              Restrictive
(any RDF)                                               (exact structure)
    │                                                           │
    ├── No shapes at all                                        │
    │                                                           │
    ├── Basic type constraints                                  │
    │   (values must be strings)                                │
    │                                                           │
    ├── Presence constraints                                    │
    │   (must have name and description)                        │
    │                                                           │
    ├── Pattern constraints                                     │
    │   (names must match [a-z][a-z0-9-]*)                      │
    │                                                           │
    ├── Relationship constraints                                │
    │   (arguments must have types)                             │
    │                                                           │
    ├── Conditional constraints                                 │
    │   (if type is File, path pattern required)                │
    │                                                           │
    └── Full structural constraints                             │
        (exact properties in exact order)              ─────────┘
```

Find your position on this spectrum. Too permissive: garbage gets through. Too restrictive: legitimate variation is rejected.

---

## The Problem Statement

**Without explicit constraints, specifications can be syntactically valid but semantically meaningless. Errors propagate through the pipeline until they surface as bugs, crashes, or confused users.**

Consider this sequence:

1. Developer writes command specification, forgets description
2. RDF is syntactically valid—no error
3. Generation pipeline runs, produces code with empty docstring
4. Tests pass (they don't check for descriptions)
5. Documentation is generated with "Description: [empty]"
6. User reads docs, doesn't understand command
7. Support ticket opened
8. Investigation traces back to missing description
9. Fix applied, but damage done

With a shape constraint requiring descriptions:

1. Developer writes command specification, forgets description
2. SHACL validation fails: "Command 'frobnicate' is missing description"
3. Developer adds description
4. Validation passes, pipeline proceeds
5. No downstream problems

The constraint caught the error at step 2 instead of step 7. Seconds of prevention versus hours of cure.

---

## The Forces at Play

### Force 1: Strictness vs. Flexibility

**Strict constraints catch errors early.** The more constrained, the more validation catches. Nothing invalid gets through.

**Strict constraints limit expression.** Over-constrained specifications become rigid forms, not living documents. Legitimate variations are rejected.

```
Strictness ←────────────────────────────→ Flexibility
(catch all errors)                         (allow all variations)
```

### Force 2: Draft vs. Production

**Different contexts need different constraints.** A draft specification needs flexibility—you're still figuring things out. A production specification needs strictness—errors have real consequences.

```
Draft Mode ←────────────────────────────→ Production Mode
(explore freely)                           (enforce strictly)
```

### Force 3: Validation Cost vs. Error Cost

**Constraints have maintenance cost.** Every constraint must be:
- Defined correctly
- Updated when requirements change
- Tested to ensure it works
- Documented for users

**Errors have higher cost.** But the cost of not catching errors is typically higher than the cost of maintaining constraints.

```
Constraint Maintenance ←──────────────→ Error Prevention
(effort to maintain)                    (value of catching)
```

### Force 4: Generic vs. Specific

**Generic constraints apply broadly.** "Every resource must have a label" applies to everything.

**Specific constraints target particular needs.** "Commands with file arguments must specify path patterns" applies only to a subset.

```
Generic ←────────────────────────────────→ Specific
(broad application)                        (narrow focus)
```

### Resolution: The Constraint Sweet Spot

Find the constraint sweet spot—strict enough to catch real errors, loose enough to allow legitimate variation. This sweet spot shifts based on:

- Maturity of the specification (stricter as it matures)
- Context of use (stricter for production)
- Frequency of violation (stricter for common errors)
- Cost of errors (stricter for critical paths)

---

## Therefore: Use SHACL for Shape Constraints

Use SHACL (Shapes Constraint Language) to define shape constraints for your specifications. SHACL is a W3C standard designed specifically for this purpose.

### Basic SHACL Structure

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Shape definition
sk:CommandShape a sh:NodeShape ;
    # What this shape applies to
    sh:targetClass sk:Command ;

    # Property constraints (detailed below)
    sh:property [ ... ] ;
    sh:property [ ... ] .
```

### Constraint Categories

#### Category 1: Cardinality Constraints

How many values can/must a property have?

```turtle
# Required (exactly one)
sh:property [
    sh:path rdfs:label ;
    sh:minCount 1 ;
    sh:maxCount 1 ;
    sh:message "Command must have exactly one name"
] .

# Required (at least one)
sh:property [
    sh:path sk:hasArgument ;
    sh:minCount 1 ;
    sh:message "Command must have at least one argument"
] .

# Optional (zero or one)
sh:property [
    sh:path sk:deprecated ;
    sh:maxCount 1 ;
    sh:message "At most one deprecation notice allowed"
] .

# Optional multiple (zero or more)
sh:property [
    sh:path sk:alias ;
    # No cardinality constraints = any number allowed
] .

# Required multiple
sh:property [
    sh:path sk:hasOption ;
    sh:minCount 0 ;
    sh:maxCount 10 ;
    sh:message "Command can have 0-10 options"
] .
```

#### Category 2: Type Constraints

What kind of value is required?

```turtle
# Datatype constraints
sh:property [
    sh:path sk:description ;
    sh:datatype xsd:string ;
    sh:message "Description must be a string"
] .

sh:property [
    sh:path sk:timeout ;
    sh:datatype xsd:integer ;
    sh:message "Timeout must be an integer"
] .

sh:property [
    sh:path sk:enabled ;
    sh:datatype xsd:boolean ;
    sh:message "Enabled flag must be boolean"
] .

# Class constraints
sh:property [
    sh:path sk:hasArgument ;
    sh:class sk:Argument ;
    sh:message "Arguments must be of class sk:Argument"
] .

# Node kind constraints
sh:property [
    sh:path sk:relatedTo ;
    sh:nodeKind sh:IRI ;
    sh:message "Related item must be a URI, not a literal"
] .

sh:property [
    sh:path sk:hasArgument ;
    sh:nodeKind sh:BlankNodeOrIRI ;
    sh:message "Argument can be blank node or URI"
] .
```

#### Category 3: Value Constraints

What specific values are allowed?

```turtle
# Pattern (regex)
sh:property [
    sh:path rdfs:label ;
    sh:pattern "^[a-z][a-z0-9-]*$" ;
    sh:flags "i" ;  # case-insensitive
    sh:message "Command name must be lowercase alphanumeric with hyphens"
] .

# Length constraints
sh:property [
    sh:path sk:description ;
    sh:minLength 10 ;
    sh:maxLength 500 ;
    sh:message "Description must be 10-500 characters"
] .

# Enumeration (one of)
sh:property [
    sh:path sk:priority ;
    sh:in ( "must" "should" "could" "wont" ) ;
    sh:message "Priority must be one of: must, should, could, wont"
] .

# Range constraints
sh:property [
    sh:path sk:timeout ;
    sh:minInclusive 0 ;
    sh:maxInclusive 3600 ;
    sh:message "Timeout must be 0-3600 seconds"
] .

# Specific value
sh:property [
    sh:path rdf:type ;
    sh:hasValue sk:Command ;
    sh:message "Must be typed as sk:Command"
] .
```

#### Category 4: Relationship Constraints

How must nodes relate to each other?

```turtle
# Nested shape (arguments must match ArgumentShape)
sh:property [
    sh:path sk:hasArgument ;
    sh:node sk:ArgumentShape ;
    sh:message "Each argument must conform to ArgumentShape"
] .

# Qualified constraints (at least 2 required arguments)
sh:property [
    sh:path sk:hasArgument ;
    sh:qualifiedMinCount 2 ;
    sh:qualifiedValueShape [
        sh:property [
            sh:path sk:required ;
            sh:hasValue true
        ]
    ] ;
    sh:message "Command must have at least 2 required arguments"
] .
```

#### Category 5: Conditional Constraints

Rules that apply only in certain conditions:

```turtle
# If type is "file", path pattern is required
sh:property [
    sh:path sk:hasArgument ;
    sh:node [
        sh:xone (
            [
                # Either type is NOT "file"
                sh:not [
                    sh:property [
                        sh:path sk:type ;
                        sh:hasValue "file"
                    ]
                ]
            ]
            [
                # Or type IS "file" AND pathPattern exists
                sh:and (
                    [
                        sh:property [
                            sh:path sk:type ;
                            sh:hasValue "file"
                        ]
                    ]
                    [
                        sh:property [
                            sh:path sk:pathPattern ;
                            sh:minCount 1
                        ]
                    ]
                )
            ]
        )
    ] ;
    sh:message "File-type arguments must specify a path pattern"
] .
```

### The ArgumentShape Example

A complete shape for command arguments:

```turtle
sk:ArgumentShape a sh:NodeShape ;
    sh:targetClass sk:Argument ;

    # Name: required, lowercase identifier
    sh:property [
        sh:path sk:name ;
        sh:name "argument-name" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z_][a-z0-9_]*$" ;
        sh:message "Argument name must be a valid Python identifier (lowercase)"
    ] ;

    # Type: required, from enumeration
    sh:property [
        sh:path sk:type ;
        sh:name "argument-type" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:in ( "String" "Integer" "Float" "Boolean" "Path" "List" ) ;
        sh:message "Type must be one of: String, Integer, Float, Boolean, Path, List"
    ] ;

    # Required flag: required boolean
    sh:property [
        sh:path sk:required ;
        sh:name "required-flag" ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:boolean ;
        sh:message "Required flag must be specified (true or false)"
    ] ;

    # Help text: optional but encouraged
    sh:property [
        sh:path sk:help ;
        sh:name "help-text" ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 5 ;
        sh:message "Help text, if provided, must be at least 5 characters"
    ] ;

    # Default: optional, only for non-required
    sh:property [
        sh:path sk:default ;
        sh:name "default-value" ;
        sh:maxCount 1 ;
        sh:message "At most one default value allowed"
    ] ;

    # Constraint: required arguments cannot have defaults
    sh:sparql [
        sh:message "Required arguments cannot have default values" ;
        sh:select """
            SELECT $this WHERE {
                $this sk:required true .
                $this sk:default ?default .
            }
        """
    ] .
```

---

## Constraint Layering

Define constraints at multiple levels, from general to specific:

### Layer 1: Core Shapes (All Entities)

```turtle
# Applies to everything in spec-kit
sk:EntityCoreShape a sh:NodeShape ;
    sh:targetClass sk:Entity ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:message "Every entity must have a label"
    ] .
```

### Layer 2: Domain Shapes (Commands, Jobs, etc.)

```turtle
# Applies to all commands
sk:CommandShape a sh:NodeShape ;
    sh:targetClass sk:Command ;

    # Inherit core constraints
    sh:node sk:EntityCoreShape ;

    # Add command-specific constraints
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:minLength 10 ;
        sh:message "Commands must have a description of at least 10 characters"
    ] ;
    sh:property [
        sh:path sk:hasArgument ;
        sh:node sk:ArgumentShape ;
        sh:message "Arguments must conform to ArgumentShape"
    ] .
```

### Layer 3: Context Shapes (Draft vs. Production)

```turtle
# Stricter constraints for production
sk:CommandProductionShape a sh:NodeShape ;
    sh:targetClass sk:Command ;

    # Include base command shape
    sh:node sk:CommandShape ;

    # Add production requirements
    sh:property [
        sh:path sk:hasTest ;
        sh:minCount 1 ;
        sh:message "Production commands must have at least one test"
    ] ;
    sh:property [
        sh:path sk:hasDocumentation ;
        sh:minCount 1 ;
        sh:message "Production commands must have documentation"
    ] ;
    sh:property [
        sh:path sk:version ;
        sh:minCount 1 ;
        sh:pattern "^\\d+\\.\\d+\\.\\d+$" ;
        sh:message "Production commands must have semantic version"
    ] .
```

### Selecting Shape Level

In your configuration, specify which shape level to use:

```toml
# ggen.toml
[validation]
# During development
shape = "sk:CommandShape"

# For production release
# shape = "sk:CommandProductionShape"
```

---

## Error Messages Matter

Good constraint messages guide correction. They should:

1. **Identify what's wrong**: Which constraint failed
2. **Locate the problem**: Which node/property
3. **Suggest the fix**: What to do about it

### Bad Error Messages

```
Validation failed.
```

```
Constraint violation.
```

```
sh:minCount not satisfied.
```

### Good Error Messages

```turtle
sh:property [
    sh:path sk:description ;
    sh:minCount 1 ;
    sh:message """
    Command '{?this rdfs:label}' is missing a description.

    Add a description like:
        sk:description "Describe what this command does" ;

    Good descriptions:
    - Start with a verb (Validates, Generates, Exports...)
    - Explain the purpose, not the implementation
    - Are 10-100 characters
    """
] .
```

### Structured Error Reports

SHACL produces structured validation reports:

```turtle
[
    a sh:ValidationReport ;
    sh:conforms false ;
    sh:result [
        a sh:ValidationResult ;
        sh:resultSeverity sh:Violation ;
        sh:focusNode cli:FrobnicateCommand ;
        sh:resultPath sk:description ;
        sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
        sh:resultMessage "Command 'frobnicate' is missing a description" ;
        sh:sourceShape sk:CommandShape
    ]
] .
```

This structured output enables:
- Programmatic error handling
- IDE integration
- CI/CD failure analysis
- Error aggregation and reporting

---

## Evolving Constraints

Constraints evolve as understanding deepens. The evolution process:

### Phase 1: Start Loose

When beginning, allow flexibility. You're learning the domain:

```turtle
# Initial: Minimal constraints
sk:CommandShapeV1 a sh:NodeShape ;
    sh:targetClass sk:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1
    ] .
```

### Phase 2: Tighten Gradually

As patterns emerge, add constraints that catch real errors:

```turtle
# After seeing commands without descriptions cause problems
sk:CommandShapeV2 a sh:NodeShape ;
    sh:targetClass sk:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:pattern "^[a-z][a-z0-9-]*$"
    ] ;
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:minLength 10
    ] .
```

### Phase 3: Document Rationale

Record why each constraint exists:

```turtle
sk:CommandShapeV3 a sh:NodeShape ;
    sh:targetClass sk:Command ;
    rdfs:comment """
    Command shape with lessons learned:
    - v1: Just required label
    - v2: Added description after doc generation showed empty descriptions
    - v3: Added pattern after mixed-case names caused CLI issues
    """ ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:pattern "^[a-z][a-z0-9-]*$" ;
        sh:description "Pattern added after 'MyCommand' caused POSIX CLI issues"
    ] .
```

### Phase 4: Version for Compatibility

Use versioned shapes for backwards compatibility:

```turtle
# Keep old shapes for migration
sk:CommandShapeV1 a sh:NodeShape ; ... .
sk:CommandShapeV2 a sh:NodeShape ; ... .
sk:CommandShapeV3 a sh:NodeShape ; ... .

# Current version alias
sk:CommandShape owl:sameAs sk:CommandShapeV3 .
```

```toml
# ggen.toml
[validation]
# Gradually upgrade
shape_version = "v2"  # Can upgrade to v3 when ready
```

---

## Case Study: The Constraint Evolution

### Initial State: No Constraints

Team starts with no SHACL validation. Any RDF is accepted.

**Problems encountered:**
- Commands without names (generation fails)
- Descriptions with HTML (breaks terminal output)
- Mixed-case names (inconsistent CLI behavior)
- Arguments without types (code generation guesses)

### Adding Constraints Iteratively

**Week 1:** Add basic presence constraints

```turtle
sh:property [ sh:path rdfs:label ; sh:minCount 1 ] ;
sh:property [ sh:path sk:description ; sh:minCount 1 ] .
```

**Week 3:** Add pattern constraints after naming issues

```turtle
sh:property [
    sh:path rdfs:label ;
    sh:pattern "^[a-z][a-z0-9-]*$"
] .
```

**Week 5:** Add argument type constraint after generation bugs

```turtle
sh:property [
    sh:path sk:hasArgument ;
    sh:node [
        sh:property [
            sh:path sk:type ;
            sh:minCount 1 ;
            sh:in ( "String" "Integer" "Float" "Boolean" "Path" "List" )
        ]
    ]
] .
```

### Result

After 8 weeks of iterative constraint addition:
- Zero invalid specifications reach generation
- New team members get immediate feedback
- Common mistakes are impossible
- CI catches constraint violations before merge

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: The Over-Constrained Form

Constraining every possible aspect until specifications become fill-in-the-blank forms:

```turtle
# Too restrictive: Exact property count, exact order
sh:property [
    sh:path sk:hasArgument ;
    sh:minCount 2 ;
    sh:maxCount 2 ;  # Exactly 2? Really?
    sh:order 1
] .
```

**Problem:** Legitimate variations are rejected. Authors feel constrained rather than guided.

### Anti-Pattern 2: The Decorative Shape

Defining shapes that are never validated:

```turtle
# Shape exists but validation never runs
sk:CommandShape a sh:NodeShape ; ... .

# Pipeline:
# 1. Read TTL
# 2. Extract (no validation)
# 3. Generate
```

**Problem:** Shapes provide false confidence. Invalid data still gets through.

### Anti-Pattern 3: The Message-Free Constraint

Constraints without helpful error messages:

```turtle
sh:property [
    sh:path sk:type ;
    sh:in ( "a" "b" "c" "d" "e" )
    # No sh:message!
] .
```

**Problem:** Users see cryptic errors like "Value 'f' not in allowed values" without understanding what the allowed values mean.

### Anti-Pattern 4: The Constraint Creep

Adding constraints without removing obsolete ones:

```turtle
# v1 constraint (no longer relevant)
sh:property [ sh:path sk:legacyFormat ; sh:minCount 1 ] ;

# v2 constraint (replaced legacyFormat)
sh:property [ sh:path sk:format ; sh:minCount 1 ] ;

# Now both are required, but legacyFormat is never used
```

**Problem:** Constraints accumulate, requiring properties that serve no purpose.

---

## Implementation Checklist

### Shape Design

- [ ] Identify core entities that need shapes
- [ ] Define cardinality constraints (required, optional, single, multiple)
- [ ] Define type constraints (datatypes, classes)
- [ ] Define value constraints (patterns, enumerations, ranges)
- [ ] Define relationship constraints (nested shapes)
- [ ] Add conditional constraints where needed
- [ ] Write clear, actionable error messages

### Validation Integration

- [ ] Integrate SHACL validation into pipeline
- [ ] Validate before any transformation
- [ ] Fail fast on constraint violations
- [ ] Report all violations (not just first)
- [ ] Provide structured error output

### Maintenance

- [ ] Version shapes for compatibility
- [ ] Document rationale for each constraint
- [ ] Review constraints periodically
- [ ] Remove obsolete constraints
- [ ] Add constraints when new error patterns emerge

---

## Resulting Context

After applying this pattern, you have:

- **Explicit definition** of valid specification structure
- **Early validation** that catches errors before processing
- **Clear error messages** that guide specification authors
- **Shared understanding** of what specifications must contain
- **Automated quality** enforcement through CI/CD
- **Evolving grammar** that grows with your domain

This supports **[Shape Validation](../verification/shape-validation.md)** and enables **[Normalization Stage](../transformation/normalization-stage.md)**.

---

## Code References

The following spec-kit source files implement SHACL shape constraints:

| Reference | Description |
|-----------|-------------|
| `ontology/spec-kit-schema.ttl:466-516` | FeatureShape with cardinality, pattern, and datatype constraints |
| `ontology/spec-kit-schema.ttl:522-578` | UserStoryShape with required properties and format validation |
| `ontology/spec-kit-schema.ttl:584-617` | AcceptanceScenarioShape with Given/When/Then structure |
| `ontology/spec-kit-schema.ttl:652-676` | SuccessCriterionShape with conditional constraints |
| `ontology/jtbd-schema.ttl:806-844` | JobShape with SPARQL-based constraints |
| `ontology/jtbd-schema.ttl:889-920` | DesiredOutcomeShape with direction/metric/object validation |

---

## Related Patterns

- *Enables:* **[11. Executable Specification](./executable-specification.md)** — Shapes make specs validatable
- *Part of:* **[22. Normalization Stage](../transformation/normalization-stage.md)** — Validation as first transformation step
- *Verified by:* **[34. Shape Validation](../verification/shape-validation.md)** — Checking shapes in CI
- *Supports:* **[16. Layered Ontology](./layered-ontology.md)** — Shapes at different layers

---

## Philosophical Coda

> *"Constraints are not the opposite of freedom. They are the precondition for meaningful choice."*

Shape constraints don't limit what you can express—they ensure what you express is coherent. They are the rules that make the game playable.

Consider poetry: A sonnet has strict constraints (14 lines, specific rhyme scheme, iambic pentameter). These constraints don't prevent creativity—they channel it. The constraint becomes the form within which meaning emerges.

Your shapes are the forms within which specifications become meaningful.

---

## Exercises

### Exercise 1: Constraint Archaeology

Take an existing specification that caused downstream problems. Design a SHACL shape that would have caught the error at validation time.

### Exercise 2: Progressive Strictness

Design three levels of shapes for the same entity:
1. Draft: Minimal constraints for exploration
2. Review: Moderate constraints for team review
3. Production: Strict constraints for deployment

### Exercise 3: Error Message Writing

Take existing shapes with poor error messages. Rewrite the messages to be:
- Clear about what's wrong
- Specific about where
- Helpful about how to fix

### Exercise 4: Conditional Constraints

Design constraints that express:
- "If A then B must also be present"
- "A and B are mutually exclusive"
- "At least one of A, B, or C must be present"

---

## Further Reading

- *SHACL Specification* — W3C Recommendation
- *Validating RDF Data* — José Emilio Labra Gayo
- *Shape Expressions (ShEx)* — Alternative constraint language
- *Constraint Satisfaction Problems* — AI background

