# 10. Single Source of Truth

★★

*When the same information exists in multiple places, it will eventually diverge. Establishing a single source of truth—one authoritative location for each piece of knowledge—prevents drift and enables automation. This is not merely a technical pattern but a philosophical commitment to epistemic clarity.*

---

## The Scattered Knowledge Problem

You've chosen a **[Semantic Foundation](./semantic-foundation.md)**. Now face a fundamental question: where does truth live?

In traditional development, truth is scattered like seeds in the wind:

- **Requirements** in documents (Word, Google Docs, Confluence)
- **Design** in diagrams (Lucidchart, Miro, whiteboard photos)
- **Behavior** in code (Python, Java, JavaScript)
- **Documentation** in wikis (Confluence, Notion, README files)
- **Tests** in test files (pytest, JUnit, Jest)
- **Configuration** in config files (YAML, JSON, TOML)
- **API contracts** in OpenAPI specs or Postman collections
- **Database schemas** in migrations or ERD tools

Each location claims authority. Each evolves independently. Over time, they diverge like continental drift—slowly, imperceptibly, but inexorably.

The document says one thing; the code does another. The tests validate something the documentation doesn't describe. The API spec promises functionality the implementation doesn't provide. Nobody knows which source to trust because every source believes itself authoritative.

This scattered truth creates constant reconciliation work:
- "Did you update the docs?"
- "Did you update the tests?"
- "Did you update the requirements?"
- "Is the OpenAPI spec current?"
- "Does this match what's in Confluence?"

Every change requires manual synchronization across sources. And synchronization always fails eventually—not through malice or negligence, but through the entropy inherent in distributed knowledge.

---

## The Philosophical Foundation

### Epistemic Monism

Single source of truth embodies **epistemic monism**—the commitment to a unified knowledge foundation. In philosophy, monism holds that reality is fundamentally one substance. In specification-driven development, we hold that each domain of knowledge has one authoritative representation.

This contrasts with the implicit **epistemic pluralism** of scattered knowledge—multiple equally valid representations that somehow must stay synchronized. Pluralism sounds democratic but creates a coordination nightmare.

### The Copy Problem

Every copy is a fork waiting to happen. When you copy information:

1. **The copy diverges from the original** as one or both are updated
2. **Readers don't know which is authoritative** without institutional knowledge
3. **Reconciliation requires human judgment** that's expensive and error-prone
4. **Automation becomes impossible** because there's no single source to automate from

The only copy that never diverges is one that doesn't exist—because it's generated on demand from the single source.

### The DRY Principle Extended

"Don't Repeat Yourself" (DRY) is typically applied to code. Single source of truth extends DRY to all knowledge:

```
Traditional DRY: Don't duplicate code
Extended DRY:    Don't duplicate knowledge
```

Code duplication is bad because changes must be made in multiple places. Knowledge duplication is worse because changes must be made in multiple places across different formats, by different people, using different tools, with different update frequencies.

---

## The Problem Statement

**When truth is scattered across multiple sources, divergence is inevitable. Reconciliation becomes a never-ending burden. No one knows what to trust.**

Consider a typical scenario:

```
Day 1:   Requirements document written
Day 5:   Code implements requirements (mostly)
Day 10:  Tests written against code (not requirements)
Day 15:  Documentation written from code (not requirements)
Day 20:  API spec generated from code (not requirements)
Day 30:  Requirements updated (code not updated)
Day 45:  Tests updated (to match code, not new requirements)
Day 60:  Customer complains that docs don't match behavior
Day 75:  Developer doesn't know which source is correct
Day 90:  All sources are partially wrong in different ways
```

By day 90, no source is authoritative. Each contains some truth and some lies. Reconciliation requires archaeology—digging through commit history, interviewing stakeholders, testing actual behavior.

---

## The Forces at Play

### Force 1: Convenience vs. Correctness

**Convenience favors locality.** It's easier to update information where you're working than in a canonical location elsewhere. If you're editing code and spot a documentation error, it's convenient to fix the comment right there rather than navigate to the canonical documentation source.

**Correctness favors centralization.** If documentation lives in one place, there's one place to look, one place to update, one place to trust.

```
Convenience ←────────────────────────────→ Correctness
(edit locally)                             (edit centrally)
```

### Force 2: Specialization vs. Unification

**Different stakeholders need different views.** Developers want code. Business analysts want requirements. Users want documentation. Ops wants runbooks. Each view has its natural home and preferred format.

**Unification eliminates drift.** When all views derive from one source, they're automatically consistent. But they might not be in the optimal format for each stakeholder.

```
Specialization ←────────────────────────→ Unification
(each stakeholder's format)               (one format for all)
```

### Force 3: History vs. Intentionality

**History creates scattering.** As projects evolve, different decisions about where to put things accumulate into a mess. The first developer put requirements in Google Docs. The second preferred Confluence. The third just wrote comments. Each decision was locally reasonable; globally it's chaos.

**Intentionality requires discipline.** Maintaining a single source requires constantly resisting the pull toward convenience and historical precedent.

```
History ←────────────────────────────────→ Intentionality
(accumulated decisions)                    (deliberate structure)
```

### Force 4: Tool Centricity vs. Knowledge Centricity

**Tools assume their format is central.** Your IDE wants code to be authoritative. Your wiki wants documents. Your API tool wants OpenAPI specs. Each tool pulls toward itself as the center of the universe.

**Knowledge should be format-independent.** The knowledge "a user must authenticate before accessing protected resources" is independent of whether it's expressed in code, documentation, or specifications.

```
Tool Centricity ←────────────────────────→ Knowledge Centricity
(format-specific authority)                (semantic authority)
```

### Force 5: Speed vs. Sustainability

**Speed favors expediency.** Under deadline pressure, updating one place is faster than updating a canonical source and regenerating artifacts.

**Sustainability favors investment.** Time spent maintaining the single source pays compound interest over the project lifetime.

```
Speed ←────────────────────────────────→ Sustainability
(quick local edits)                      (disciplined central edits)
```

---

## Therefore: Designate One Source of Truth

Designate one source of truth for each domain of knowledge. For capabilities, that source is RDF.

### The Principle

**Any piece of knowledge that can be expressed in RDF must be expressed in RDF. All other representations are generated.**

```
RDF Source (truth)
      │
      ├──▶ Code (generated)
      ├──▶ Documentation (generated)
      ├──▶ Tests (generated)
      ├──▶ Schemas (generated)
      ├──▶ API specs (generated)
      └──▶ Configuration (generated)
```

### What Lives in RDF

The RDF source contains all semantic knowledge:

```turtle
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

# Command definitions (name, arguments, options)
sk:sync a sk:Command ;
    rdfs:label "sync" ;
    sk:description "Synchronize specifications with generated artifacts" ;
    sk:hasArgument [
        sk:name "source" ;
        sk:type "Path" ;
        sk:required true ;
        sk:description "Path to RDF specification source"
    ] ;
    sk:hasOption [
        sk:name "format" ;
        sk:type "String" ;
        sk:default "turtle" ;
        sk:description "Output format for generated files"
    ] .

# Feature specifications (behavior, constraints)
sk:authentication a sk:Feature ;
    rdfs:label "User Authentication" ;
    sk:description "Verify user identity before granting access" ;
    sk:precondition "User has registered credentials" ;
    sk:postcondition "User session is established" ;
    sk:errorCondition "Invalid credentials produce AuthenticationError" .

# Outcome definitions (metrics, targets)
sk:specDriftOutcome a sk:Outcome ;
    rdfs:label "Specification Drift" ;
    sk:direction "minimize" ;
    sk:metric "divergence_percentage" ;
    sk:target 0 ;
    sk:unit "percent" .

# Job definitions (functional, emotional, social)
sk:maintainConsistencyJob a sk:Job ;
    rdfs:label "Maintain specification consistency" ;
    sk:dimension sk:Functional ;
    sk:context "When updating capability definitions" ;
    sk:desiredProgress "Changes in one place automatically propagate" .

# Concept definitions (domain vocabulary)
sk:Capability a rdfs:Class ;
    rdfs:label "Capability" ;
    rdfs:comment "A unit of functionality that delivers customer value" ;
    sk:examples "Authentication, Authorization, Data Export" .
```

### What Is Generated

Generated artifacts are derived from the RDF source:

**Python Command Implementations:**

```python
# GENERATED FROM ontology/commands.ttl - DO NOT EDIT
# Regenerate with: ggen sync

import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def sync(
    source: Path = typer.Argument(..., help="Path to RDF specification source"),
    format: str = typer.Option("turtle", help="Output format for generated files"),
) -> None:
    """Synchronize specifications with generated artifacts."""
    # Implementation delegated to ops layer
    from specify_cli.ops.sync import execute_sync
    execute_sync(source, format)
```

**Documentation Pages:**

```markdown
<!-- GENERATED FROM memory/features.ttl - DO NOT EDIT -->
<!-- Regenerate with: ggen sync -->

# User Authentication

Verify user identity before granting access.

## Preconditions

- User has registered credentials

## Postconditions

- User session is established

## Error Conditions

- Invalid credentials produce AuthenticationError
```

**Test Stubs:**

```python
# GENERATED FROM ontology/commands.ttl - DO NOT EDIT
# Regenerate with: ggen sync

import pytest
from specify_cli.commands.sync import sync

class TestSyncCommand:
    """Tests for the sync command."""

    def test_sync_requires_source_argument(self):
        """sync requires a source path argument."""
        # Test that source argument is required
        pass

    def test_sync_default_format_is_turtle(self):
        """sync defaults to turtle output format."""
        # Test default format
        pass
```

**API Schemas:**

```yaml
# GENERATED FROM ontology/api.ttl - DO NOT EDIT
# Regenerate with: ggen sync

openapi: 3.0.0
paths:
  /api/sync:
    post:
      summary: Synchronize specifications
      parameters:
        - name: source
          in: body
          required: true
          schema:
            type: string
            format: path
```

---

## Rules for the Single Source

### Rule 1: One Write Location

**Edit only the RDF source.** Never edit generated files. Never create "override" files that shadow generated content. Never maintain "patches" to apply after generation.

```
✓ Edit ontology/commands.ttl
✗ Edit src/commands/sync.py (generated)
✗ Create src/commands/sync_override.py
✗ Maintain patches/sync.patch
```

When you need behavior that feels like an exception:

1. **Ask if the exception should be the rule** — Maybe the specification should allow this case
2. **Add the variation to the specification** — Express the exception formally
3. **Generate code that handles the exception** — Let the exception be part of the generated behavior

### Rule 2: One Read Location

**Queries extract from RDF.** When you need information about capabilities, query the RDF source. Don't parse generated files. Don't read documentation. Don't inspect code.

```sparql
# To find all commands with their arguments:
SELECT ?command ?name ?argName ?argType WHERE {
    ?command a sk:Command ;
             rdfs:label ?name ;
             sk:hasArgument ?arg .
    ?arg sk:name ?argName ;
         sk:type ?argType .
}
```

This query is:
- **Authoritative** — It reads from the source of truth
- **Current** — It always returns the latest specification
- **Structured** — It returns data in a processable format
- **Composable** — It can be combined with other queries

### Rule 3: Generated Artifacts Are Read-Only

**Never edit generated files.** They are build artifacts, like compiled binaries. You don't edit `.pyc` files; don't edit generated `.py` files either.

Mark generated files clearly:

```python
# ============================================================
# GENERATED FILE - DO NOT EDIT
#
# Source: ontology/commands.ttl
# Generator: ggen sync
# Generated: 2024-01-15T10:30:00Z
#
# To modify this file, edit the source and regenerate.
# ============================================================
```

Configure editors to prevent accidental edits:

```json
// .vscode/settings.json
{
    "files.readonlyInclude": {
        "src/commands/**": true,
        "tests/generated/**": true,
        "docs/generated/**": true
    }
}
```

### Rule 4: Regeneration Is Safe

**Running the transformation again produces identical output.** This is the **[Idempotent Transform](../transformation/idempotent-transform.md)** property. If regeneration changes anything, either:

1. The source changed (expected)
2. The generator is non-deterministic (bug)
3. Someone edited a generated file (violation)

```bash
# Safe regeneration workflow
ggen sync
git diff  # Should show no changes if source unchanged
```

---

## File Organization

Structure your repository to make the single source obvious:

```
project/
├── ontology/              # Source of truth for structure
│   ├── schema.ttl         # Core concepts and relationships
│   ├── commands.ttl       # Command specifications
│   ├── features.ttl       # Feature specifications
│   └── shapes.ttl         # SHACL validation shapes
│
├── memory/                # Source of truth for content
│   ├── jobs.ttl           # Customer jobs
│   ├── outcomes.ttl       # Desired outcomes
│   ├── requirements.ttl   # Business requirements
│   └── changelog.ttl      # Change history
│
├── sparql/                # Extraction queries
│   ├── commands.rq        # Extract command data
│   ├── features.rq        # Extract feature data
│   └── docs.rq            # Extract documentation
│
├── templates/             # Generation templates
│   ├── command.py.tera    # Python command template
│   ├── test.py.tera       # Test template
│   └── doc.md.tera        # Documentation template
│
├── ggen.toml              # Transformation configuration
│
├── # GENERATED BELOW - DO NOT EDIT
├── src/
│   └── commands/          # Generated from ontology/commands.ttl
│       ├── sync.py
│       └── validate.py
│
├── tests/
│   └── generated/         # Generated from ontology/commands.ttl
│       └── test_commands.py
│
└── docs/
    └── generated/         # Generated from memory/*.ttl
        ├── features.md
        └── requirements.md
```

### Marking Generated Directories

Use README files to mark generated directories:

```markdown
<!-- src/commands/README.md -->
# Generated Commands

**DO NOT EDIT FILES IN THIS DIRECTORY**

These files are generated from `ontology/commands.ttl`.

To modify commands:
1. Edit `ontology/commands.ttl`
2. Run `ggen sync`
3. Commit both the source and generated files

Generator: ggen sync
Source: ontology/commands.ttl
```

### Git Configuration

Track both source and generated files, but configure git to recognize the relationship:

```gitattributes
# .gitattributes
# Mark generated files for diff purposes
src/commands/* linguist-generated=true
tests/generated/* linguist-generated=true
docs/generated/* linguist-generated=true
```

---

## The Discipline

Single source of truth requires discipline that feels constraining at first but pays compound interest.

### Discipline 1: Never Edit Generated Files

When you see something wrong in generated code, **resist the urge to fix it directly**. Instead:

```
Wrong in generated code?
         │
         ├── Typo in description?
         │        └── Fix in RDF source → regenerate
         │
         ├── Missing argument?
         │        └── Add to RDF source → regenerate
         │
         ├── Wrong behavior?
         │        └── Update RDF specification → regenerate
         │
         └── Need custom logic?
                  └── Put in ops/runtime layer (not command layer)
```

The only exception is exploration during development—and even then, port your changes back to the source immediately.

### Discipline 2: Regenerate Frequently

Make regeneration part of your workflow:

```bash
# Development workflow
edit ontology/commands.ttl
ggen sync
git diff                    # Review changes
uv run pytest               # Verify tests pass
git add -A
git commit -m "feat: add new sync options"
```

Never let the generated files get stale. Regenerate:
- After every source edit
- Before every commit
- As part of CI/CD
- Whenever you're unsure

### Discipline 3: Verify Consistency

Use **[Receipt Verification](../verification/receipt-verification.md)** to ensure generated files match their source:

```bash
# Verify no drift
ggen verify

# If drift detected:
# - Someone edited a generated file
# - Source changed but regeneration didn't run
# - Generator produced non-deterministic output
```

Include verification in CI:

```yaml
# .github/workflows/verify.yml
name: Verify Single Source
on: [push, pull_request]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Regenerate
        run: ggen sync
      - name: Check for drift
        run: |
          if [[ -n $(git status --porcelain) ]]; then
            echo "Generated files are out of sync with source"
            git diff
            exit 1
          fi
```

### Discipline 4: Document the Boundary

Make it absolutely clear which files are source and which are generated:

**In documentation:**

```markdown
## Repository Structure

### Source Files (edit these)
- `ontology/*.ttl` - Capability specifications
- `memory/*.ttl` - Business knowledge
- `templates/*.tera` - Generation templates

### Generated Files (do not edit)
- `src/commands/*.py` - CLI commands
- `tests/generated/*.py` - Test stubs
- `docs/generated/*.md` - Documentation
```

**In code comments:**

```python
# ontology/commands.ttl - SOURCE OF TRUTH
# Edit this file to change command definitions

# src/commands/sync.py - GENERATED
# Do not edit. Changes will be overwritten.
```

**In directory structure:**

```
# Clear naming convention
source/          # Or: ontology/, specs/, truth/
generated/       # Or: build/, dist/, derived/
```

---

## When Multiple Sources Seem Necessary

Sometimes you'll feel you need multiple sources. Recognize these as temptations to resist:

### Temptation: "The RDF is too verbose"

*"For this simple case, just let me write it in YAML."*

**Response:** Add a transformation that simplifies RDF for the common case. Create a YAML-to-RDF converter if needed. Maintain one source; accept input from multiple formats.

```yaml
# Simple input format (accepted)
commands:
  - name: sync
    description: Synchronize files

# Transformed to canonical RDF (single source)
```

### Temptation: "The team knows YAML better"

*"Everyone knows YAML. Nobody knows Turtle."*

**Response:** Invest in team education. The learning curve is temporary; the benefits are permanent. Or create DSLs that hide RDF complexity while maintaining it as the canonical form.

### Temptation: "The tool requires JSON"

*"Our API gateway only accepts OpenAPI JSON."*

**Response:** Generate the required format from RDF. The tool can consume generated JSON. The JSON is not the source; the RDF is.

```
RDF (source) → Generator → OpenAPI JSON (generated) → API Gateway
```

### Temptation: "We need to move fast"

*"We don't have time to set up the generation pipeline. Let's just write the code directly for now."*

**Response:** "For now" becomes "forever." Technical debt compounds. The time you "save" now costs 10x later in reconciliation, debugging, and documentation drift. Invest in the single source early.

### The Drift Vectors

Every second source becomes a drift vector:

```
Source A ←→ Source B
     ↓           ↓
  Artifact    Artifact
     ↓           ↓
  Divergence detected
     ↓
  Which source is right?
     ↓
  Archaeological investigation
     ↓
  Manual reconciliation
     ↓
  Repeat forever
```

With a single source:

```
Source (RDF)
     ↓
  Generate all artifacts
     ↓
  Artifacts consistent by construction
     ↓
  No reconciliation needed
```

---

## Case Study: The Drift Disaster

### Before: Death by Documentation

A team maintained their API in three places:
1. **OpenAPI spec** — The "official" contract
2. **Python code** — The actual implementation
3. **Confluence wiki** — The human-readable documentation

For six months, this seemed fine. Then:

- **Month 7:** New endpoint added to code, forgotten in OpenAPI
- **Month 8:** Documentation updated with wrong parameter name
- **Month 9:** OpenAPI updated without updating code
- **Month 10:** Customer reports behavior doesn't match docs
- **Month 11:** Investigation reveals all three sources differ
- **Month 12:** Two weeks spent reconciling sources

Cost: **80 engineer-hours** of reconciliation + customer trust damage

### After: Single Source Transformation

The team adopted single source of truth:

```turtle
# api/endpoints.ttl - THE ONLY SOURCE
api:createUser a api:Endpoint ;
    api:method "POST" ;
    api:path "/users" ;
    api:parameter [
        api:name "email" ;
        api:type "string" ;
        api:required true
    ] ;
    api:parameter [
        api:name "name" ;
        api:type "string" ;
        api:required true
    ] ;
    api:response [
        api:status 201 ;
        api:schema api:UserSchema
    ] .
```

Generated artifacts:
- OpenAPI spec → automatic
- Python implementation skeleton → automatic
- Documentation → automatic

Now changes happen once, propagate everywhere:

```bash
# Change parameter name
edit api/endpoints.ttl    # Change "name" to "fullName"
ggen sync                 # Regenerate everything
git diff                  # See changes in all artifacts
git commit               # Commit atomic change
```

Time to propagate changes: **5 minutes** instead of **3 hours + forgotten updates**

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: The Shadow Source

Maintaining an unofficial "real" source alongside the official single source:

```
Official source: ontology/commands.ttl
Shadow source: team_wiki/command_reference.md (people actually read this)
```

The shadow source always wins because it's easier to update. Eventually the official source is ignored. Solution: Make the single source genuinely authoritative and usable.

### Anti-Pattern 2: The Override Layer

Creating an "override" mechanism that patches generated output:

```
Generated: src/commands/sync.py
Override: src/commands/sync_override.py (merged at runtime)
```

Overrides accumulate until they effectively replace generation. Solution: Extend the specification to express the variations, or put custom logic in a different layer (ops/runtime).

### Anti-Pattern 3: The Generation Gap

Running generation so rarely that nobody remembers how:

```
Last generated: 8 months ago
Source changes since: 47
Generated files edited: 23
State: Hopeless
```

Solution: Regenerate continuously. Make it part of CI. Make it part of every commit.

### Anti-Pattern 4: The Partial Source

Putting only "important" things in the single source:

```
In RDF: Major features
In code: "Minor" implementation details
In docs: "Obvious" behaviors
```

The boundary between important and minor is subjective and shifts. Eventually "minor" details become the majority. Solution: Everything that can be expressed formally belongs in the source.

---

## Implementation Checklist

### Initial Setup

- [ ] Identify all current sources of truth (documents, code, configs, wikis)
- [ ] Choose canonical source format (RDF recommended)
- [ ] Design ontology for your domain
- [ ] Create directory structure separating source from generated
- [ ] Set up generation pipeline (ggen or equivalent)
- [ ] Mark generated files clearly (headers, .gitattributes)
- [ ] Configure editor protections for generated files

### Migration

- [ ] Extract knowledge from scattered sources into RDF
- [ ] Create SPARQL queries for extraction
- [ ] Create templates for generation
- [ ] Generate artifacts and compare with existing
- [ ] Resolve discrepancies (fix source, not artifacts)
- [ ] Replace old artifacts with generated ones
- [ ] Delete old scattered sources
- [ ] Update team documentation and workflows

### Ongoing Discipline

- [ ] Regenerate as part of every source change
- [ ] Verify no drift in CI/CD
- [ ] Review generated files in PRs (to catch source errors)
- [ ] Never commit manual edits to generated files
- [ ] Educate team members on the discipline
- [ ] Resist temptations to create secondary sources

---

## Resulting Context

After applying this pattern, you have:

- **One authoritative location** for each piece of knowledge
- **Clear separation** between source and generated artifacts
- **Ability to regenerate** artifacts confidently at any time
- **Elimination of drift** between code, docs, and tests
- **Automated consistency** — changes propagate by generation
- **Single point of update** — change once, update everywhere
- **Trustworthy artifacts** — you know what to believe

This enables:
- **[Executable Specification](./executable-specification.md)** — Specs can drive generation
- **[Drift Detection](../verification/drift-detection.md)** — Compare generated with actual
- **[Constitutional Equation](../transformation/constitutional-equation.md)** — The transformation relationship
- **[Receipt Verification](../verification/receipt-verification.md)** — Cryptographic consistency proofs

---

## Code References

The following spec-kit source files implement single source of truth concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/cli-commands.ttl:10` | Constitutional equation comment: `commands/*.py = μ(cli-commands.ttl)` |
| `ggen.toml` | Configuration defining source-to-artifact transformation rules |
| `templates/command.tera:2-3` | Template header noting its source TTL file |
| `src/specify_cli/runtime/receipt.py:39-49` | Receipt dataclass linking input to output |
| `src/specify_cli/runtime/receipt.py:112-156` | generate_receipt() creating cryptographic proof |

---

## Related Patterns

- *Builds on:* **[9. Semantic Foundation](./semantic-foundation.md)** — RDF is the source format
- *Enables:* **[11. Executable Specification](./executable-specification.md)** — Source drives generation
- *Enables:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Artifacts are transformations
- *Verified by:* **[35. Drift Detection](../verification/drift-detection.md)** — Detect divergence
- *Verified by:* **[36. Receipt Verification](../verification/receipt-verification.md)** — Cryptographic proofs

---

## Philosophical Coda

> *"There should be one—and preferably only one—obvious way to do it."*
>
> — The Zen of Python

Apply this principle not just to code, but to knowledge itself. One source. One truth. Everything else flows from it.

The single source of truth is not a constraint—it's a liberation. Liberation from the endless reconciliation cycle. Liberation from the question "which source is right?" Liberation from the anxiety of not knowing what to trust.

When truth lives in one place, you can focus on what matters: making that truth correct, complete, and useful. The generation system handles the rest.

---

## Exercises

### Exercise 1: Drift Archaeology

Find a project with scattered knowledge sources. Document:
1. How many sources claim to be authoritative?
2. Where do they disagree?
3. Which would you trust for each type of question?
4. How long would reconciliation take?

### Exercise 2: Single Source Design

For a small domain (e.g., API endpoints, CLI commands, configuration options):
1. Design an RDF ontology for the domain
2. Populate it with sample data
3. Write templates to generate artifacts
4. Compare generated artifacts with hand-written equivalents

### Exercise 3: Migration Planning

For an existing project:
1. Inventory all knowledge sources
2. Categorize by domain (commands, features, docs, etc.)
3. Design target single-source structure
4. Create migration plan with phases
5. Identify risks and mitigation strategies

---

## Further Reading

- *Don't Repeat Yourself (DRY)* — The Pragmatic Programmer
- *Single Source Publishing* — Technical writing best practices
- *Configuration as Code* — Infrastructure automation patterns
- *Schema-Driven Development* — API-first design
- *Ontology-Driven Software Development* — Academic foundations

