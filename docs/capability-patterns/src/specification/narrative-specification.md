# 18. Narrative Specification

★

*Formal specifications capture structure. Narrative specifications capture intent, context, and rationale. Both are necessary for complete understanding. The narrative is the soul that animates the formal skeleton.*

---

## The Incompleteness of Precision

Your **[Executable Specifications](./executable-specification.md)** define *what* must be true. They're precise, validatable, transformable. A machine can read them, validate them, generate from them. But they don't explain *why*.

Consider this specification:

```turtle
cli:ValidateCommand a cli:Command ;
    sk:name "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;
    cli:hasArgument [
        sk:name "file" ;
        cli:type "Path" ;
        cli:required true
    ] ;
    cli:hasOption [
        sk:name "--strict" ;
        cli:type "bool" ;
        cli:default "false"
    ] .
```

This specification is perfectly precise. It tells you:
- There's a command called "validate"
- It takes a required file argument
- It has an optional --strict flag defaulting to false

But it doesn't tell you:
- **Why** does this command exist? What problem drove its creation?
- **What** trade-offs were considered? Why streaming validation instead of loading everything into memory?
- **When** should someone use --strict vs. default mode? What's the difference in practice?
- **Who** is this command for? Power users? Beginners? CI systems?
- **What** happens in edge cases? Large files? Network paths? Symlinks?

Pure formal specifications are like assembly language—precise but opaque. The machine understands perfectly. Humans struggle. Future maintainers wonder: "What were they thinking?"

---

## The Problem Statement

**Formal specifications are necessary but not sufficient. Without narrative context, intent is lost and maintenance becomes archaeology.**

The cost of missing narrative:
- **Misunderstanding**: Implementers interpret specs differently than authors intended
- **Wrong decisions**: Future maintainers make changes that violate implicit assumptions
- **Slow onboarding**: New team members can't understand *why* things are the way they are
- **Lost knowledge**: The reasoning behind decisions evaporates when original authors leave
- **Repeated mistakes**: Without documented alternatives considered, teams re-explore dead ends

---

## The Forces at Play

### Force 1: Formality vs. Humanity

**Formality enables automation.** Machines process structure, not stories. Validation, generation, and transformation need precise, parseable input.

**Humanity enables understanding.** Humans understand through stories, not structure. We need context, examples, and rationale to truly comprehend.

```
Formality ←──────────────────────────────→ Humanity
(machine-processable)                      (human-understandable)
```

### Force 2: Separation vs. Integration

**Separation risks drift.** Narrative in separate documents—wikis, design docs, email threads—inevitably drifts from formal specs. The spec changes; the narrative doesn't. Soon they contradict each other.

**Integration risks noise.** Narrative embedded in formal specs clutters the structure. Too much prose makes the specification hard to parse—for both machines and humans.

```
Separation ←─────────────────────────────→ Integration
(narrative elsewhere)                      (narrative in spec)
```

### Force 3: Completeness vs. Conciseness

**Completeness wants all context.** Every decision has history. Every constraint has rationale. Every edge case has explanation. Document it all.

**Conciseness wants focus.** Too much narrative overwhelms. Readers can't find the essential information. Important context drowns in verbose explanation.

```
Completeness ←───────────────────────────→ Conciseness
(document everything)                      (document essentials)
```

### Force 4: Permanence vs. Evolution

**Permanence wants stability.** Narrative explains why things *are* a certain way. It's historical record. Changing it rewrites history.

**Evolution wants currency.** As the spec evolves, narrative must too. Outdated rationale is worse than none—it actively misleads.

```
Permanence ←─────────────────────────────→ Evolution
(historical record)                        (current context)
```

---

## Therefore: Embed Narrative as Structured Annotations

**Embed narrative as structured RDF annotations within formal specifications, then extract them during transformation to generate documentation.**

The key insight: Narrative is data too. It can be represented in RDF, validated with shapes, extracted with queries, and transformed into documentation. By treating narrative as first-class data, we get:

- **Colocation**: Narrative lives next to the formal spec it explains
- **Structure**: Narrative categories (rationale, scenarios, alternatives) are explicit
- **Extraction**: Documentation generation pulls narrative automatically
- **Validation**: SHACL shapes can require certain narratives
- **Evolution**: Changing the spec naturally prompts narrative review

### The Narrative Ontology

```turtle
# ontology/narrative.ttl
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Base narrative property
sk:narrative a rdf:Property ;
    rdfs:label "narrative" ;
    rdfs:comment "Human-readable narrative context" ;
    rdfs:range xsd:string .

# Narrative categories (all subproperties of sk:narrative)

sk:rationale a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "rationale" ;
    rdfs:comment """
        Why this element exists. The problem it solves,
        the need it addresses, the motivation behind it.
    """ .

sk:designDecision a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "design decision" ;
    rdfs:comment """
        Key choices made in designing this element.
        Why this approach over alternatives.
    """ .

sk:usageScenario a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "usage scenario" ;
    rdfs:comment """
        Concrete scenarios showing how this is used.
        Real-world examples and workflows.
    """ .

sk:alternatives a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "alternatives considered" ;
    rdfs:comment """
        Options that were considered but not chosen.
        Why they were rejected.
    """ .

sk:caveat a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "caveat" ;
    rdfs:comment """
        Warnings, limitations, and things to watch out for.
        Known issues and edge cases.
    """ .

sk:futureWork a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "future work" ;
    rdfs:comment """
        Potential enhancements and improvements.
        Technical debt and known limitations to address.
    """ .

sk:example a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "example" ;
    rdfs:comment """
        Code examples, command invocations, or usage samples.
        Concrete illustrations of the specification.
    """ .

sk:seeAlso a rdf:Property ;
    rdfs:subPropertyOf sk:narrative ;
    rdfs:label "see also" ;
    rdfs:comment """
        Related specifications, external documentation,
        or other resources for additional context.
    """ .
```

---

## Annotating Specifications with Narrative

### Complete Example

```turtle
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix jtbd: <https://spec-kit.io/ontology/jtbd#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    sk:name "validate" ;
    sk:description "Validate RDF/Turtle files against SHACL shapes" ;

    # ═══════════════════════════════════════════════════════════
    # NARRATIVE CONTEXT
    # ═══════════════════════════════════════════════════════════

    sk:rationale """
        Users frequently commit invalid RDF because validation is
        a separate, manual step that's easy to forget. By making
        validation a first-class CLI command, we integrate it into
        the natural development workflow:

        - Pre-commit: Run before every commit
        - CI/CD: Run on every push
        - IDE: Integrate via command execution

        The goal is to make validation as natural as running tests.
        Invalid RDF should never reach the repository.
    """ ;

    sk:designDecision """
        1. **Streaming validation**: We chose streaming validation
           over loading the entire file to support large ontologies
           without memory issues. This means we can validate files
           larger than available RAM.

        2. **SHACL for shapes**: We use SHACL rather than custom
           validation because it's a W3C standard with existing
           tool support. Users can leverage their SHACL knowledge.

        3. **Exit codes**: We use Unix-standard exit codes:
           - 0: Validation successful
           - 1: Validation failed (invalid RDF)
           - 2: Input error (file not found, unreadable)
           This enables easy integration with CI systems.

        4. **Default behavior**: By default, validate checks only
           RDF syntax. SHACL shape validation requires explicit
           shapes file to avoid silent no-op when shapes missing.
    """ ;

    sk:usageScenario """
        **Scenario: Pre-commit validation**

        Developer finishes editing ontology.ttl:

        ```bash
        $ specify validate ontology.ttl
        Valid ✓ (156 triples in 0.23s)
        ```

        Sees validation pass, commits with confidence.

        **Scenario: CI validation**

        GitHub Action runs on push:

        ```yaml
        - name: Validate RDF
          run: specify validate ontology/*.ttl
        ```

        Build fails fast if any file is invalid.

        **Scenario: Shape validation**

        Developer validates data against shapes:

        ```bash
        $ specify validate data.ttl --shapes shapes.ttl --strict
        Validation failed:
          Line 45: Missing required property sk:name
          Line 67: Invalid type for cli:required (expected boolean)
        ```

        Gets actionable feedback on shape violations.
    """ ;

    sk:alternatives """
        **Considered: IDE plugin**

        We considered building IDE plugins (VSCode, IntelliJ) for
        inline validation. Rejected because:
        - Not all users use IDEs (vim, emacs, nano users exist)
        - Plugin maintenance across multiple IDEs is expensive
        - CLI can be wrapped by any IDE anyway

        **Considered: Pre-commit hook only**

        We considered making validation only a pre-commit hook.
        Rejected because:
        - Hooks can be bypassed (--no-verify)
        - CI needs independent validation anyway
        - Users sometimes want to validate without committing

        **Considered: CI-only validation**

        We considered validation only in CI, not locally. Rejected
        because:
        - Feedback loop too slow (push → wait → see failure)
        - Wastes CI resources on obviously invalid files
        - Developers want instant feedback

        **Result**: CLI command that can be used anywhere—locally,
        in hooks, in CI, from IDE terminals. Maximum flexibility.
    """ ;

    sk:caveat """
        **Performance on very large files**: While streaming handles
        large files, validation of 100MB+ files can take several
        seconds. Consider splitting very large ontologies.

        **Network paths**: File paths must be local. Remote URLs
        are not supported (security and performance concerns).
        Use `curl` or `wget` first if needed.

        **Strict mode gotcha**: With --strict, ALL triples must
        conform to shapes. This means you need complete shape
        coverage or validation fails unexpectedly.

        **Blank node comparison**: SHACL validation of blank nodes
        can be tricky. Named nodes are recommended for better
        error messages.
    """ ;

    sk:futureWork """
        - Watch mode: `specify validate --watch` to revalidate on
          file change
        - Format auto-detection: Support JSON-LD, N-Triples, RDF/XML
        - Parallel validation: Validate multiple files concurrently
        - Custom error formatters: JSON output for tool integration
        - Fix suggestions: Suggest corrections for common errors
    """ ;

    sk:example """
        ```bash
        # Basic syntax validation
        specify validate ontology.ttl

        # Validate multiple files
        specify validate ontology/*.ttl

        # Validate against shapes
        specify validate data.ttl --shapes shapes.ttl

        # Strict mode (all triples must match shapes)
        specify validate data.ttl --shapes shapes.ttl --strict

        # JSON output for tools
        specify validate ontology.ttl --format json

        # Quiet mode (only errors)
        specify validate ontology.ttl --quiet
        ```
    """ ;

    sk:seeAlso """
        - SHACL Specification: https://www.w3.org/TR/shacl/
        - Turtle Syntax: https://www.w3.org/TR/turtle/
        - Pattern: [Shape Constraint](./shape-constraint.md)
    """ ;

    # ═══════════════════════════════════════════════════════════
    # FORMAL SPECIFICATION
    # ═══════════════════════════════════════════════════════════

    cli:hasArgument [
        sk:name "file" ;
        cli:type "Path" ;
        cli:required true ;
        cli:help "RDF file(s) to validate" ;
        cli:metavar "FILE"
    ] ;

    cli:hasOption [
        sk:name "--shapes" ;
        cli:shortName "-s" ;
        cli:type "Path" ;
        cli:help "SHACL shapes file for validation"
    ] ;

    cli:hasOption [
        sk:name "--strict" ;
        cli:type "bool" ;
        cli:default "false" ;
        cli:help "Require all triples to conform to shapes"
    ] ;

    cli:hasOption [
        sk:name "--format" ;
        cli:shortName "-f" ;
        cli:type "string" ;
        cli:choices ("text" "json" "turtle") ;
        cli:default "text" ;
        cli:help "Output format for validation report"
    ] ;

    cli:hasOption [
        sk:name "--quiet" ;
        cli:shortName "-q" ;
        cli:type "bool" ;
        cli:default "false" ;
        cli:help "Suppress non-error output"
    ] ;

    cli:exitCodeSuccess 0 ;
    cli:exitCodeError 1 .
```

---

## Extracting Narrative for Documentation

### SPARQL Query for Documentation Generation

```sparql
PREFIX cli: <https://spec-kit.io/ontology/cli#>
PREFIX sk: <https://spec-kit.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# Extract all narrative for a command
SELECT ?name ?description ?rationale ?designDecision
       ?usageScenario ?alternatives ?caveat ?futureWork
       ?example ?seeAlso
WHERE {
    ?cmd a cli:Command ;
         sk:name ?name ;
         sk:description ?description .

    OPTIONAL { ?cmd sk:rationale ?rationale }
    OPTIONAL { ?cmd sk:designDecision ?designDecision }
    OPTIONAL { ?cmd sk:usageScenario ?usageScenario }
    OPTIONAL { ?cmd sk:alternatives ?alternatives }
    OPTIONAL { ?cmd sk:caveat ?caveat }
    OPTIONAL { ?cmd sk:futureWork ?futureWork }
    OPTIONAL { ?cmd sk:example ?example }
    OPTIONAL { ?cmd sk:seeAlso ?seeAlso }
}
ORDER BY ?name
```

### Template for Documentation

```jinja
{# templates/command-docs.tera #}
# {{ name }}

{{ description }}

{% if rationale %}
## Why This Command Exists

{{ rationale }}
{% endif %}

{% if usageScenario %}
## Usage Scenarios

{{ usageScenario }}
{% endif %}

{% if example %}
## Examples

{{ example }}
{% endif %}

{% if designDecision %}
## Design Decisions

{{ designDecision }}
{% endif %}

{% if alternatives %}
## Alternatives Considered

{{ alternatives }}
{% endif %}

{% if caveat %}
## Important Notes

{{ caveat }}
{% endif %}

{% if futureWork %}
## Roadmap

{{ futureWork }}
{% endif %}

{% if seeAlso %}
## See Also

{{ seeAlso }}
{% endif %}
```

### Generated Documentation

Running the template produces:

```markdown
# validate

Validate RDF/Turtle files against SHACL shapes

## Why This Command Exists

Users frequently commit invalid RDF because validation is
a separate, manual step that's easy to forget. By making
validation a first-class CLI command, we integrate it into
the natural development workflow:

- Pre-commit: Run before every commit
- CI/CD: Run on every push
- IDE: Integrate via command execution

The goal is to make validation as natural as running tests.
Invalid RDF should never reach the repository.

## Usage Scenarios

**Scenario: Pre-commit validation**

Developer finishes editing ontology.ttl:

```bash
$ specify validate ontology.ttl
Valid ✓ (156 triples in 0.23s)
```

...
```

---

## Validating Narrative with SHACL

Require certain narrative elements for completeness:

```turtle
# shapes/narrative-shapes.ttl
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix cli: <https://spec-kit.io/ontology/cli#> .

# Commands must have rationale
sk:CommandNarrativeShape a sh:NodeShape ;
    sh:targetClass cli:Command ;

    sh:property [
        sh:path sk:rationale ;
        sh:minCount 1 ;
        sh:minLength 50 ;
        sh:message "Commands must have a rationale explaining why they exist (at least 50 characters)"
    ] ;

    sh:property [
        sh:path sk:usageScenario ;
        sh:minCount 1 ;
        sh:message "Commands must have at least one usage scenario"
    ] ;

    sh:property [
        sh:path sk:example ;
        sh:minCount 1 ;
        sh:message "Commands must have at least one example"
    ] .

# Optional but encouraged
sk:ComprehensiveNarrativeShape a sh:NodeShape ;
    sh:targetClass cli:Command ;
    sh:severity sh:Warning ;

    sh:property [
        sh:path sk:designDecision ;
        sh:minCount 1 ;
        sh:message "Consider documenting key design decisions"
    ] ;

    sh:property [
        sh:path sk:caveat ;
        sh:message "Consider documenting any caveats or limitations"
    ] .
```

---

## Narrative Categories in Depth

### Rationale: The "Why"

Rationale explains why this element exists. It connects the specification to the problem it solves:

**Good rationale:**
```
Users frequently commit invalid RDF because validation is a
separate, manual step. By making validation a first-class CLI
command, we integrate it into the natural workflow.
```

**Bad rationale:**
```
This command validates RDF files.
```
(This just restates the description—no *why*.)

**Questions rationale should answer:**
- What problem does this solve?
- What user need does it address?
- What would happen if this didn't exist?
- What triggered the creation of this element?

### Design Decision: The "How and Why This Way"

Design decisions document choices made and their reasoning:

**Good design decision:**
```
We chose streaming validation over loading the entire file
to support large ontologies without memory issues. Trade-off:
Slightly slower for small files, but scalable for large ones.
```

**Bad design decision:**
```
Uses streaming.
```
(No *why*, no trade-off discussion.)

**Questions design decisions should answer:**
- What approach did you choose?
- What were the trade-offs?
- What would break if this changed?
- What assumptions does this rely on?

### Usage Scenario: The "When and How"

Scenarios show concrete usage in realistic contexts:

**Good scenario:**
```
Scenario: Pre-commit validation

Developer finishes editing ontology.ttl, runs
'specify validate ontology.ttl', sees "Valid ✓",
commits with confidence.
```

**Bad scenario:**
```
Use this to validate files.
```
(No concrete example, no context.)

**Scenario structure:**
1. **Context**: Who is doing this? In what situation?
2. **Action**: What exactly do they do?
3. **Outcome**: What happens? What do they see?

### Alternatives: The "What Else We Considered"

Alternatives document options that were rejected:

**Good alternatives:**
```
Considered: IDE plugin
Rejected because not all users use IDEs, and plugin
maintenance across multiple IDEs is expensive.
```

**Bad alternatives:**
```
We didn't use a plugin.
```
(Why not? What was considered?)

**Why document alternatives:**
- Prevents re-discovery of dead ends
- Shows the decision wasn't arbitrary
- Helps future maintainers understand constraints
- Provides ammunition against "why don't we just..."

### Caveat: The "Watch Out For"

Caveats document limitations, edge cases, and gotchas:

**Good caveat:**
```
Performance on very large files: While streaming handles
large files, validation of 100MB+ files can take several
seconds. Consider splitting very large ontologies.
```

**Bad caveat:**
```
May be slow sometimes.
```
(When? How slow? What to do about it?)

**What caveats should cover:**
- Performance limitations
- Edge cases that behave differently
- Common mistakes users make
- Interactions with other features

### Future Work: The "What's Next"

Future work documents planned improvements and known limitations:

**Good future work:**
```
- Watch mode: `specify validate --watch` to revalidate on
  file change
- Fix suggestions: Suggest corrections for common errors
```

**Bad future work:**
```
Make it better.
```
(How? What specifically?)

**Future work helps with:**
- Setting expectations (this isn't supported *yet*)
- Planning priorities
- Inviting contributions
- Documenting technical debt

---

## Narrative Quality Guidelines

### Rule 1: Explain Why, Not What

The formal specification already says *what*. Narrative adds *why*:

```turtle
# BAD: Restates the spec
sk:rationale "This command validates RDF files using SHACL shapes."

# GOOD: Explains the why
sk:rationale """
    Manual validation is error-prone and easily forgotten.
    By integrating validation into the CLI, we make it part
    of the natural workflow.
"""
```

### Rule 2: Be Concrete

Specific examples beat abstract descriptions:

```turtle
# BAD: Abstract
sk:usageScenario "Users can validate files before committing."

# GOOD: Concrete
sk:usageScenario """
    Developer finishes editing ontology.ttl:
    $ specify validate ontology.ttl
    Valid ✓ (156 triples in 0.23s)
    Commits with confidence.
"""
```

### Rule 3: Preserve Context That Might Be Lost

Document things that seem obvious now but won't be later:

```turtle
sk:designDecision """
    We use exit code 1 for validation failures because this
    matches POSIX conventions (1 = general error). We considered
    more specific codes (e.g., 10 = syntax error, 20 = shape
    violation) but POSIX only reserves 0-2. Custom codes 3+
    might conflict with shell-specific meanings.
"""
```

### Rule 4: Update Narrative When Spec Changes

Outdated narrative is worse than no narrative—it actively misleads:

```turtle
# When adding a new option, update the relevant narratives:
sk:caveat """
    ...
    **New in 1.2**: The --parallel flag enables concurrent
    validation but may produce interleaved output. Use
    --format json for machine-parseable results.
"""
```

### Rule 5: Write for Your Future Self

Imagine reading this narrative in 2 years, having forgotten all context:

```turtle
sk:rationale """
    In 2024, we discovered that 30% of CI failures were due to
    invalid RDF syntax that could have been caught locally. The
    validate command was created to shift this validation left,
    catching errors at development time rather than CI time.

    See: Incident Report 2024-03-15 (CI Reliability)
"""
```

---

## Case Study: The Orphaned Specification

### The Problem

A team inherits a specification with no narrative:

```turtle
cli:migrate a cli:Command ;
    sk:name "migrate" ;
    cli:hasArgument [ sk:name "from" ; cli:type "string" ] ;
    cli:hasArgument [ sk:name "to" ; cli:type "string" ] ;
    cli:hasOption [ sk:name "--dry-run" ; cli:type "bool" ] .
```

Questions the team can't answer:
- What does "migrate" migrate? Database? Files? Configuration?
- What are "from" and "to"? Versions? Directories? Formats?
- Why is this a separate command and not part of something else?
- What happens in dry-run mode? What's the output?

### The Archaeology

The team spends 2 weeks piecing together:
- Slack conversations from departed developers
- Git commit messages (mostly "fix migration")
- Runtime behavior observation
- Trial and error

### The Solution

After understanding, they add narrative:

```turtle
cli:migrate a cli:Command ;
    sk:name "migrate" ;

    sk:rationale """
        Schema evolution requires data migration between versions.
        This command migrates RDF data from an older schema version
        to a newer one, transforming triples according to migration
        rules defined in migration/*.ttl.

        Created after v2.0 breaking changes caused manual migration
        headaches. Automates what was previously a error-prone
        manual process.
    """ ;

    sk:designDecision """
        1. Version strings use semantic versioning (1.0.0 format)
        2. Migrations are specified as SPARQL CONSTRUCT queries
        3. Migrations are applied in order (1.0→1.1→1.2, not 1.0→1.2)
        4. No backward migrations (would require inverse CONSTRUCT)
    """ ;

    sk:usageScenario """
        After updating to schema v2.0:

        ```bash
        $ specify migrate 1.9.0 2.0.0 --dry-run
        Would transform 145 triples:
          - Rename sk:name → sk:identifier (45 triples)
          - Split sk:full_name → sk:firstName, sk:lastName (50 triples)
          - Add required sk:version (50 triples)

        $ specify migrate 1.9.0 2.0.0
        Migrated 145 triples successfully.
        ```
    """ ;

    sk:caveat """
        - NO UNDO: Migrations modify data in place. Backup first.
        - Large datasets: Use --batch-size for memory management
        - Custom types: Migration rules may need extension for
          domain-specific transformations
    """ ;

    cli:hasArgument [ sk:name "from" ; cli:type "string" ;
        cli:help "Source schema version (semver)" ] ;
    cli:hasArgument [ sk:name "to" ; cli:type "string" ;
        cli:help "Target schema version (semver)" ] ;
    cli:hasOption [ sk:name "--dry-run" ; cli:type "bool" ;
        cli:help "Show what would change without modifying data" ] .
```

### The Outcome

New team members can now understand the command in minutes, not weeks. Future maintainers won't repeat the archaeology.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: Narrative as Comment Dumping Ground

```turtle
# BAD: Stream of consciousness
sk:rationale """
    So we needed validation and I talked to John about it and
    he said we should probably do streaming because remember
    that one time the server crashed? Yeah so anyway this
    validates files I think it's pretty self-explanatory...
"""
```

**Problem:** No structure, no useful information, hard to extract.

### Anti-Pattern 2: Marketing Speak

```turtle
# BAD: Hyperbole, not information
sk:rationale """
    This revolutionary command provides world-class validation
    capabilities that will transform your development workflow
    and delight users with its blazing-fast performance!
"""
```

**Problem:** No actual content. Sounds like an ad.

### Anti-Pattern 3: Implementation Details

```turtle
# BAD: How instead of why
sk:rationale """
    Uses the RDF4J library to parse Turtle syntax into a
    temporary in-memory repository, then executes SHACL
    validation using TopBraid SHACL engine with parallel
    shape evaluation enabled.
"""
```

**Problem:** This belongs in code comments, not specification narrative.

### Anti-Pattern 4: Outdated Narrative

```turtle
# BAD: Narrative from v1.0, spec is now v3.0
sk:caveat "Limited to files under 1MB."  # Actually fixed in v2.0
```

**Problem:** Actively misleads users.

### Anti-Pattern 5: Duplicate Information

```turtle
# BAD: Narrative repeats formal spec
sk:description "Validate RDF files" ;
sk:rationale "This command validates RDF files." ;
sk:usageScenario "Use this command to validate RDF files." ;
```

**Problem:** No added value. Wasted space.

---

## Implementation Checklist

### Setting Up Narrative

- [ ] Define narrative properties in ontology
- [ ] Create SHACL shapes for narrative requirements
- [ ] Update templates to include narrative sections
- [ ] Add narrative extraction to documentation pipeline

### Writing Narrative

- [ ] Write rationale for every major specification element
- [ ] Include at least one concrete usage scenario
- [ ] Document any non-obvious design decisions
- [ ] Note caveats and limitations
- [ ] Record alternatives considered for significant decisions

### Maintaining Narrative

- [ ] Review narrative when changing specifications
- [ ] Version narrative alongside formal specs
- [ ] Include narrative in code review checklist
- [ ] Audit for outdated narrative periodically

---

## Resulting Context

After applying this pattern, you have:

- **Narrative collocated** with formal specification—they evolve together
- **Extractable narrative** for automatic documentation generation
- **Intent preserved** for future maintainers
- **Stories** that help users understand purpose and context
- **Validatable completeness**—SHACL can require narrative
- **Living context**—narrative updates with the spec

This enhances **[Human-Readable Artifact](../transformation/human-readable-artifact.md)** and supports **[Living Documentation](../evolution/living-documentation.md)**.

---

## Code References

The following spec-kit source files implement narrative specification concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/cli-commands.ttl:36` | rdfs:comment with narrative description |
| `ontology/spec-kit-schema.ttl:22-30` | rdfs:label and rdfs:comment for narrative |
| `ontology/jtbd-schema.ttl:24-45` | Job classes with embedded narrative context |
| `templates/command.tera:7-32` | Template extracting narrative for documentation |

---

## Related Patterns

- *Complements:* **[11. Executable Specification](./executable-specification.md)** — Narrative explains formal specs
- *Feeds:* **[30. Human-Readable Artifact](../transformation/human-readable-artifact.md)** — Narrative becomes documentation
- *Enables:* **[45. Living Documentation](../evolution/living-documentation.md)** — Docs stay current with specs
- *Validated by:* **[12. Shape Constraint](./shape-constraint.md)** — SHACL can require narratives

---

## Philosophical Coda

> *"Code tells you how. Comments tell you why."*

Specifications tell you what. Narrative tells you why. Both are essential.

A specification without narrative is a house without a story—structurally sound but soulless. Who lived here? What memories were made? What problems were solved? Without these answers, the house is just walls and roof, nothing more.

The narrative is what transforms a specification from a sterile contract into a living document. It carries the wisdom of decisions made, the context of problems solved, the lessons of mistakes avoided. It's the institutional memory that outlasts any individual.

Write narrative not for the machines, but for the humans who will maintain what you build. Write it for your future self, who will have forgotten what you now take for granted. Write it as an act of kindness to those who come after.

---

## Exercises

### Exercise 1: Narrative Archaeology

Find a specification in your codebase with minimal or no narrative. Investigate its history (git, conversations, runtime behavior) and write comprehensive narrative for it.

### Exercise 2: Narrative Review

Review the narrative for an existing specification. Does it:
- Explain why, not just what?
- Include concrete scenarios?
- Document alternatives considered?
- Note caveats and limitations?

Improve any gaps you find.

### Exercise 3: Narrative Templates

Create narrative templates for common specification types in your domain:
- Commands
- API endpoints
- Data models
- Configuration options

### Exercise 4: SHACL for Narrative

Write SHACL shapes that enforce narrative requirements for your project. Consider:
- Required narratives (rationale, examples)
- Encouraged narratives (alternatives, future work)
- Minimum lengths

---

## Further Reading

- *The Art of Readable Code* — Boswell & Foucher
- *A Philosophy of Software Design* — John Ousterhout
- *Design Rationale: Concepts, Techniques, and Use* — Moran & Carroll
- *Literate Programming* — Donald Knuth
- *Working Effectively with Legacy Code* — Michael Feathers

