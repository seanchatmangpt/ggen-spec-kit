# 11. Executable Specification

★★

*A specification that cannot be executed is a wish. An executable specification is precise enough to drive validation, generation, and testing—eliminating the gap between what we intend and what we build. When specifications execute, interpretation vanishes and truth emerges.*

---

## The Interpretation Gap

You have a **[Single Source of Truth](./single-source-of-truth.md)**. But truth that sits inert is just documentation. Documentation is read, interpreted, and implemented based on human understanding. Each reader understands differently. Each implementer interprets differently. The gap between specification and implementation widens with every hand-off.

Traditional specifications are **passive**. They describe what should be built:

```
"The system shall allow users to authenticate using email and password."
```

A human reads this. What does "allow" mean? When should authentication happen? What happens on failure? How long is the session? What format is the email? The specification is silent on these questions, leaving them to interpretation.

Different developers interpret differently:
- Developer A implements immediate authentication
- Developer B adds a CAPTCHA first
- Developer C requires email verification
- Developer D allows social login as an alternative

All claim to satisfy the specification. All are different. None is definitively correct.

This is the **interpretation gap**—the space between what a specification says and what it means. In passive specifications, this gap is unbridgeable. Human judgment fills it, inconsistently.

---

## The Active Alternative

Executable specifications are **active**. They don't just describe—they *do*:

```turtle
sk:authentication a sk:Feature ;
    sk:precondition [
        a sk:Condition ;
        sk:requires sk:RegisteredUser ;
        sk:state sk:Unauthenticated
    ] ;
    sk:action [
        a sk:Action ;
        sk:input [ sk:name "email" ; sk:type xsd:string ; sk:format "email" ] ;
        sk:input [ sk:name "password" ; sk:type xsd:string ; sk:minLength 8 ]
    ] ;
    sk:postcondition [
        a sk:Condition ;
        sk:creates sk:Session ;
        sk:state sk:Authenticated ;
        sk:duration "PT24H"^^xsd:duration
    ] ;
    sk:errorCondition [
        a sk:ErrorCondition ;
        sk:when "InvalidCredentials" ;
        sk:produces sk:AuthenticationError ;
        sk:maxAttempts 5 ;
        sk:lockoutDuration "PT15M"^^xsd:duration
    ] .
```

This specification **executes** in multiple ways:

1. **Validation**: SHACL shapes verify implementations conform
2. **Generation**: SPARQL queries extract data for code generation
3. **Testing**: Acceptance criteria become automated tests
4. **Documentation**: Human-readable docs are generated

When a specification executes, there's no interpretation gap. The specification *is* the behavior definition. Questions that were left to human judgment are now answered by formal precision.

---

## The Problem Statement

**Passive specifications allow interpretation. Interpretation causes drift. Drift causes bugs, inconsistency, and wasted reconciliation effort.**

The cost of interpretation:

| Passive Specification | Cost |
|----------------------|------|
| Ambiguous requirement | Developer guesses wrong, rework required |
| Missing edge case | Bug discovered in production |
| Unclear constraint | Different implementations diverge |
| Undocumented assumption | Maintenance nightmare |
| Unverifiable claim | Testing is manual and incomplete |

Each passive specification is a liability—a source of potential misunderstanding waiting to surface at the worst possible moment.

---

## The Forces at Play

### Force 1: Precision vs. Accessibility

**Precision is hard.** Executable specifications require unambiguous definition. Every edge case must be considered. Every constraint must be explicit. This takes more effort than waving at intent with prose.

**Accessibility is easy.** Natural language specifications are quick to write and easy to read. Anyone can understand "users should be able to log in." Not everyone can read SHACL shapes.

```
Precision ←────────────────────────────→ Accessibility
(executable, complete)                   (readable, incomplete)
```

### Force 2: Completeness vs. Velocity

**Edge cases are tedious.** Real execution requires handling every case—the happy path, the error path, the weird corner cases nobody thinks about until they happen. Documentation can wave at edge cases: "errors are handled appropriately."

**Velocity demands shortcuts.** Under deadline pressure, specifying every edge case feels like overkill. Ship now, fix later.

```
Completeness ←────────────────────────→ Velocity
(handle every case)                     (ship the happy path)
```

### Force 3: Maintenance vs. Convenience

**Maintenance burden is real.** Executable specifications must stay updated. When behavior changes, the specification must change first. This is additional work that passive documentation doesn't require.

**Documentation can quietly rot.** Nobody enforces documentation accuracy. It drifts, becomes outdated, and everyone learns to ignore it. Convenient in the short term; catastrophic in the long term.

```
Maintenance ←────────────────────────→ Convenience
(keep specs current)                   (let docs rot)
```

### Force 4: Tooling Investment vs. Simplicity

**Tooling is required.** Execution requires infrastructure—validators, generators, test runners. This is upfront investment that passive specifications don't need.

**Simplicity is attractive.** A text editor and a wiki get you started immediately. No build pipeline, no learning curve, no dependencies.

```
Tooling Investment ←────────────────→ Simplicity
(infrastructure needed)               (text editor sufficient)
```

### Resolution

The tension is real: executable specifications are more valuable but more demanding. The investment must be worthwhile.

**The resolution:** Executable specifications pay compound interest. The upfront investment in precision, completeness, and tooling returns dividends every day through:

- Eliminated interpretation
- Automatic validation
- Generated artifacts
- Verifiable behavior
- Trustworthy documentation

The question isn't whether you can afford executable specifications. It's whether you can afford the alternative.

---

## Therefore: Make Specifications Executable

Make your RDF specifications executable through three primary mechanisms: validation, extraction, and generation.

### Mechanism 1: SHACL Validation

Every specification includes SHACL shapes that validate instances. Validation happens automatically—invalid specifications are rejected before they can cause downstream problems.

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

# Shape: Commands must have name, description, and valid arguments
sk:CommandShape a sh:NodeShape ;
    sh:targetClass sk:Command ;
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z][a-z0-9-]*$" ;
        sh:message "Command name must be lowercase alphanumeric with hyphens"
    ] ;
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:minLength 10 ;
        sh:message "Description must be at least 10 characters"
    ] ;
    sh:property [
        sh:path sk:hasArgument ;
        sh:node sk:ArgumentShape ;
        sh:message "Arguments must conform to ArgumentShape"
    ] .

# Shape: Arguments must have name, type, and required flag
sk:ArgumentShape a sh:NodeShape ;
    sh:property [
        sh:path sk:name ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[a-z_][a-z0-9_]*$" ;
        sh:message "Argument name must be valid Python identifier"
    ] ;
    sh:property [
        sh:path sk:type ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:in ( "String" "Integer" "Float" "Boolean" "Path" "List" ) ;
        sh:message "Type must be one of the allowed types"
    ] ;
    sh:property [
        sh:path sk:required ;
        sh:minCount 1 ;
        sh:maxCount 1 ;
        sh:datatype xsd:boolean
    ] .
```

This shape **executes** by validating every command definition:

```bash
# Validate specifications against shapes
pyshacl -s ontology/shapes.ttl -d ontology/commands.ttl

# Example validation output:
Validation Report
Conforms: False
Results (1):
  Constraint Violation in MinLengthConstraintComponent:
    Source Shape: sk:CommandShape
    Focus Node: sk:myCommand
    Value: "Do stuff"
    Message: Description must be at least 10 characters
```

Invalid commands are rejected before generation. The specification itself enforces quality.

### Mechanism 2: SPARQL Extraction

Every specification can be queried to extract structured data. SPARQL queries transform the semantic graph into structured data suitable for templates.

```sparql
# Extract command definitions for code generation
PREFIX sk: <https://spec-kit.io/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?name ?description ?argName ?argType ?argRequired ?argDefault ?argHelp
WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?name ;
         sk:description ?description .

    OPTIONAL {
        ?cmd sk:hasArgument ?arg .
        ?arg sk:name ?argName ;
             sk:type ?argType ;
             sk:required ?argRequired .
        OPTIONAL { ?arg sk:default ?argDefault }
        OPTIONAL { ?arg sk:help ?argHelp }
    }
}
ORDER BY ?name ?argName
```

This query **executes** by extracting data that drives template rendering:

```json
[
  {
    "name": "sync",
    "description": "Synchronize specifications with generated artifacts",
    "argName": "source",
    "argType": "Path",
    "argRequired": true,
    "argDefault": null,
    "argHelp": "Path to RDF specification source"
  },
  {
    "name": "sync",
    "description": "Synchronize specifications with generated artifacts",
    "argName": "format",
    "argType": "String",
    "argRequired": false,
    "argDefault": "turtle",
    "argHelp": "Output format for generated files"
  }
]
```

### Mechanism 3: Template Emission

Specifications drive code generation through templates. The extracted data fills templates to produce executable artifacts.

```jinja
{# command.py.tera - Template for generating Python commands #}
# GENERATED FROM ontology/commands.ttl - DO NOT EDIT
# Regenerate with: ggen sync

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer()

{% for command in commands %}
@app.command("{{ command.name }}")
def {{ command.name | replace("-", "_") }}_command(
    {% for arg in command.arguments %}
    {% if arg.required %}
    {{ arg.name }}: {{ arg.type | python_type }} = typer.Argument(
        ...,
        help="{{ arg.help | default(value='') }}"
    ),
    {% else %}
    {{ arg.name }}: Optional[{{ arg.type | python_type }}] = typer.Option(
        {{ arg.default | python_value }},
        help="{{ arg.help | default(value='') }}"
    ),
    {% endif %}
    {% endfor %}
) -> None:
    """{{ command.description }}"""
    from specify_cli.ops.{{ command.name | replace("-", "_") }} import execute
    execute({% for arg in command.arguments %}{{ arg.name }}{% if not loop.last %}, {% endif %}{% endfor %})

{% endfor %}
```

The template **executes** by producing code files from extracted data:

```python
# GENERATED FROM ontology/commands.ttl - DO NOT EDIT
# Regenerate with: ggen sync

import typer
from pathlib import Path
from typing import Optional

app = typer.Typer()

@app.command("sync")
def sync_command(
    source: Path = typer.Argument(
        ...,
        help="Path to RDF specification source"
    ),
    format: Optional[str] = typer.Option(
        "turtle",
        help="Output format for generated files"
    ),
) -> None:
    """Synchronize specifications with generated artifacts"""
    from specify_cli.ops.sync import execute
    execute(source, format)
```

---

## The Execution Pipeline

Every specification participates in a complete execution pipeline:

```
Specification (RDF)
      │
      │  ┌─────────────────────────────────────────┐
      │  │           EXECUTION PIPELINE            │
      │  └─────────────────────────────────────────┘
      │
      ├──[SHACL]──▶ μ₁ Validation
      │                 │
      │                 ├── Conforms? → Continue
      │                 └── Violation? → Reject with details
      │
      ├──[SPARQL]──▶ μ₂ Extraction
      │                  │
      │                  └── Structured JSON data
      │
      ├──[Tera]──▶ μ₃ Emission
      │                │
      │                ├── Code files (.py, .rs, .ts)
      │                ├── Test files (.py, .rs, .ts)
      │                ├── Documentation (.md, .html)
      │                └── Schemas (.json, .yaml)
      │
      ├──[Format]──▶ μ₄ Canonicalization
      │                  │
      │                  └── Consistent formatting, encoding
      │
      └──[Hash]──▶ μ₅ Receipt
                       │
                       └── Cryptographic proof of generation
```

If a specification can't be validated, extracted, or transformed, it's not executable—it's just documentation.

### Pipeline Properties

**Deterministic**: Same input always produces same output. No randomness, no timestamps in content, no environment dependencies.

**Idempotent**: Running the pipeline twice produces identical results. μ ∘ μ = μ.

**Atomic**: Either the entire pipeline succeeds or nothing changes. No partial generation.

**Traceable**: Every artifact links back to its source specification.

---

## Levels of Executability

Not all specifications need full executability. Consider a hierarchy of levels:

| Level | Execution Capability | Use Case | Example |
|-------|---------------------|----------|---------|
| 0 | None (prose only) | Background context | "Our users value simplicity" |
| 1 | Validation only | Constraint checking | SHACL shapes without generation |
| 2 | Validation + Extraction | Data queries | Extracting metrics without code gen |
| 3 | Full pipeline | Complete automation | Validation → Extraction → Generation |

### Level 0: Pure Documentation

```turtle
# Level 0: Narrative context
sk:philosophy rdfs:comment """
Our design philosophy prioritizes simplicity and clarity.
Users should be able to accomplish common tasks without
consulting documentation.
""" .
```

This is valuable context but doesn't execute. It informs human decisions without driving automation.

### Level 1: Validation Only

```turtle
# Level 1: Validatable but not generated
sk:ConfigShape a sh:NodeShape ;
    sh:targetClass sk:Config ;
    sh:property [
        sh:path sk:maxConnections ;
        sh:datatype xsd:integer ;
        sh:minInclusive 1 ;
        sh:maxInclusive 1000
    ] .
```

This shape validates configurations but doesn't generate code. Useful for constraints that don't map to generation.

### Level 2: Validation + Extraction

```turtle
# Level 2: Queryable but not code-generated
sk:deploymentMetrics a sk:MetricSet ;
    sk:metric [ sk:name "uptime" ; sk:unit "percent" ] ;
    sk:metric [ sk:name "latency_p99" ; sk:unit "ms" ] .
```

```sparql
# Extract metrics for dashboards (but don't generate code)
SELECT ?name ?unit WHERE {
    sk:deploymentMetrics sk:metric ?m .
    ?m sk:name ?name ; sk:unit ?unit .
}
```

The data can be extracted for visualization but doesn't drive code generation.

### Level 3: Full Pipeline

```turtle
# Level 3: Complete execution
sk:sync a sk:Command ;
    rdfs:label "sync" ;
    sk:description "Synchronize specifications" ;
    sk:hasArgument [ sk:name "source" ; sk:type "Path" ; sk:required true ] .
```

Full validation → extraction → generation → canonicalization → receipt.

### Targeting the Right Level

**Aim for Level 3** for core specifications—commands, features, APIs. These drive the system and benefit most from full automation.

**Accept Level 1-2** for supporting specifications—constraints, metrics, configurations. These need validation but may not need generation.

**Minimize Level 0** for context that can't be formalized. Keep prose for genuinely narrative content that resists formalization.

---

## Making Existing Specs Executable

If you have existing prose specifications, follow this migration path:

### Step 1: Identify Formal Content

Read through prose specifications and identify what can be precisely defined:

**Prose:**
> "The sync command takes a source path and an optional format parameter. It reads RDF files and generates code, documentation, and tests."

**Formal content extracted:**
- Command name: "sync"
- Required argument: source (Path)
- Optional argument: format (String, default: "turtle")
- Actions: generate code, documentation, tests
- Input: RDF files

### Step 2: Model in RDF

Express the formal content as triples:

```turtle
sk:sync a sk:Command ;
    rdfs:label "sync" ;
    sk:description "Synchronize RDF specifications with generated artifacts" ;
    sk:hasArgument [
        a sk:Argument ;
        sk:name "source" ;
        sk:type "Path" ;
        sk:required true ;
        sk:help "Path to RDF specification source"
    ] ;
    sk:hasOption [
        a sk:Option ;
        sk:name "format" ;
        sk:type "String" ;
        sk:required false ;
        sk:default "turtle" ;
        sk:help "Output format for generated files"
    ] ;
    sk:generates sk:PythonCode, sk:Documentation, sk:Tests ;
    sk:reads sk:RDFFiles .
```

### Step 3: Add SHACL Shapes

Define validation rules for the formal structure:

```turtle
sk:CommandShape a sh:NodeShape ;
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

### Step 4: Write SPARQL Queries

Extract data for generation:

```sparql
PREFIX sk: <https://spec-kit.io/ontology#>

SELECT ?name ?description ?argName ?argType ?argRequired
WHERE {
    ?cmd a sk:Command ;
         rdfs:label ?name ;
         sk:description ?description .
    OPTIONAL {
        ?cmd sk:hasArgument ?arg .
        ?arg sk:name ?argName ;
             sk:type ?argType ;
             sk:required ?argRequired .
    }
}
```

### Step 5: Create Templates

Generate artifacts from extracted data:

```jinja
{# command.py.tera #}
@app.command("{{ name }}")
def {{ name | replace("-", "_") }}_command(
    {% for arg in arguments %}
    {{ arg.name }}: {{ arg.type | python_type }},
    {% endfor %}
) -> None:
    """{{ description }}"""
    pass
```

### Step 6: Link Prose to Formal

Keep narrative as annotations on formal specs:

```turtle
sk:sync a sk:Command ;
    rdfs:label "sync" ;
    sk:description "Synchronize RDF specifications with generated artifacts" ;
    sk:rationale """
    The sync command is the heart of the specification-driven workflow.
    Developers edit RDF specifications, then run sync to propagate
    changes to all generated artifacts. This ensures consistency
    and eliminates manual synchronization.
    """ ;
    sk:usageNotes """
    Run sync after any specification change. The command is idempotent,
    so running it multiple times is safe. In CI, include sync verification
    to catch specifications that were changed without regeneration.
    """ .
```

The goal isn't to eliminate prose—it's to separate executable content from narrative context. Both have value; they serve different purposes.

---

## Executable Specification Patterns

### Pattern: Acceptance Criteria as SHACL

Transform Given-When-Then acceptance criteria into SHACL shapes:

**Prose:**
> Given a user with valid credentials, when they submit the login form, then a session is created.

**SHACL:**
```turtle
sk:LoginSuccessShape a sh:NodeShape ;
    sh:targetClass sk:LoginAttempt ;
    sh:property [
        sh:path sk:precondition ;
        sh:hasValue sk:ValidCredentials
    ] ;
    sh:property [
        sh:path sk:action ;
        sh:hasValue sk:SubmitLoginForm
    ] ;
    sh:property [
        sh:path sk:postcondition ;
        sh:hasValue sk:SessionCreated
    ] .
```

### Pattern: State Machines as RDF

Model state transitions formally:

```turtle
sk:UserState a rdfs:Class ;
    sk:states ( sk:Anonymous sk:Authenticated sk:Locked ) .

sk:loginTransition a sk:Transition ;
    sk:from sk:Anonymous ;
    sk:to sk:Authenticated ;
    sk:trigger sk:ValidLogin ;
    sk:guard sk:NotLocked .

sk:lockoutTransition a sk:Transition ;
    sk:from sk:Anonymous ;
    sk:to sk:Locked ;
    sk:trigger sk:FailedLoginLimit ;
    sk:action sk:SendLockoutNotification .
```

### Pattern: Feature Flags as RDF

Specify feature flags formally:

```turtle
sk:darkModeFlag a sk:FeatureFlag ;
    rdfs:label "dark-mode" ;
    sk:description "Enable dark mode UI theme" ;
    sk:default false ;
    sk:rolloutPercentage 25 ;
    sk:enabledFor sk:BetaUsers ;
    sk:prerequisite sk:themeEngineFlag .
```

### Pattern: Error Taxonomy as RDF

Define error hierarchies:

```turtle
sk:AuthenticationError a rdfs:Class ;
    rdfs:subClassOf sk:SecurityError ;
    sk:httpStatus 401 ;
    sk:retryable false .

sk:InvalidCredentialsError a rdfs:Class ;
    rdfs:subClassOf sk:AuthenticationError ;
    sk:message "The provided credentials are invalid" ;
    sk:suggestion "Check email and password, or reset password" .

sk:AccountLockedError a rdfs:Class ;
    rdfs:subClassOf sk:AuthenticationError ;
    sk:message "Account is temporarily locked" ;
    sk:suggestion "Wait {lockout_duration} or contact support" .
```

---

## Case Study: From Prose to Executable

### Before: The Prose Specification

```markdown
## Authentication Feature

Users should be able to log in with email and password. The system
should validate credentials and create a session. Failed logins
should be tracked and accounts locked after too many attempts.

### Requirements
- Email must be valid format
- Password must be at least 8 characters
- Sessions expire after 24 hours
- Lock account after 5 failed attempts
- Lockout lasts 15 minutes
```

This prose is:
- **Readable** but **ambiguous** (what's "valid format"?)
- **Incomplete** (what happens on success? on failure?)
- **Unverifiable** (how do we test "should"?)
- **Disconnected** from implementation

### After: The Executable Specification

```turtle
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .

# Feature definition
sk:authentication a sk:Feature ;
    rdfs:label "User Authentication" ;
    sk:description "Verify user identity via email and password" ;

    # Preconditions
    sk:precondition [
        sk:requires sk:RegisteredUser ;
        sk:state sk:Unauthenticated
    ] ;

    # Input validation
    sk:input [
        sk:name "email" ;
        sk:type xsd:string ;
        sk:format "^[^@]+@[^@]+\\.[^@]+$" ;
        sk:required true
    ] ;
    sk:input [
        sk:name "password" ;
        sk:type xsd:string ;
        sk:minLength 8 ;
        sk:required true
    ] ;

    # Success postcondition
    sk:postcondition [
        sk:creates sk:Session ;
        sk:sessionDuration "PT24H"^^xsd:duration ;
        sk:state sk:Authenticated
    ] ;

    # Error conditions
    sk:errorCondition [
        sk:type sk:InvalidCredentialsError ;
        sk:incrementsCounter sk:FailedAttempts
    ] ;
    sk:errorCondition [
        sk:type sk:AccountLockedError ;
        sk:when [ sk:failedAttempts [ sh:minInclusive 5 ] ] ;
        sk:lockDuration "PT15M"^^xsd:duration
    ] .

# SHACL validation shape
sk:AuthInputShape a sh:NodeShape ;
    sh:targetClass sk:AuthenticationInput ;
    sh:property [
        sh:path sk:email ;
        sh:pattern "^[^@]+@[^@]+\\.[^@]+$" ;
        sh:message "Email must be valid format"
    ] ;
    sh:property [
        sh:path sk:password ;
        sh:minLength 8 ;
        sh:message "Password must be at least 8 characters"
    ] .
```

This executable specification is:
- **Precise**: Every constraint is explicit
- **Complete**: Success and error paths defined
- **Verifiable**: SHACL validates conformance
- **Generative**: Drives code, tests, and docs

### Generated Artifacts

**Generated Test:**

```python
# GENERATED FROM ontology/features.ttl
import pytest
from datetime import timedelta

class TestAuthentication:
    def test_valid_credentials_creates_session(self, auth_service):
        """Given valid credentials, authentication creates session."""
        result = auth_service.authenticate(
            email="user@example.com",
            password="validpassword123"
        )
        assert result.success
        assert result.session is not None
        assert result.session.duration == timedelta(hours=24)

    def test_invalid_email_format_rejected(self, auth_service):
        """Email must match valid format pattern."""
        with pytest.raises(ValidationError) as exc:
            auth_service.authenticate(
                email="not-an-email",
                password="validpassword123"
            )
        assert "Email must be valid format" in str(exc.value)

    def test_short_password_rejected(self, auth_service):
        """Password must be at least 8 characters."""
        with pytest.raises(ValidationError) as exc:
            auth_service.authenticate(
                email="user@example.com",
                password="short"
            )
        assert "Password must be at least 8 characters" in str(exc.value)

    def test_account_locked_after_five_failures(self, auth_service):
        """Account locks after 5 failed attempts."""
        for _ in range(5):
            auth_service.authenticate(
                email="user@example.com",
                password="wrongpassword"
            )

        with pytest.raises(AccountLockedError) as exc:
            auth_service.authenticate(
                email="user@example.com",
                password="correctpassword"
            )
        assert exc.value.lock_duration == timedelta(minutes=15)
```

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: The Prose Escape Hatch

Adding prose descriptions that contradict or extend formal specifications:

```turtle
sk:sync a sk:Command ;
    rdfs:label "sync" ;
    sk:description "Synchronize files" ;
    sk:notes "Actually also validates and can run in dry-run mode..." .
```

If behavior isn't in the formal spec, it won't be generated. Keep prose for context, not behavior.

### Anti-Pattern 2: The Unvalidated Shape

Creating SHACL shapes that are never executed:

```turtle
# Shape defined but never validated against
sk:CommandShape a sh:NodeShape ;
    sh:targetClass sk:Command ;
    # ... constraints ...
```

Always integrate validation into the pipeline. Shapes that don't validate are decorative.

### Anti-Pattern 3: The Query Bypass

Extracting data by parsing RDF directly instead of using SPARQL:

```python
# Don't do this
for s, p, o in graph:
    if p == SK.name:
        # manual extraction...
```

SPARQL queries are declarative, composable, and part of the specification. Direct parsing bypasses the execution model.

### Anti-Pattern 4: The Hand-Edited Template Output

Modifying generated files "just this once":

```python
# GENERATED - DO NOT EDIT
# (but someone did edit it)

def sync_command(...):
    # Hand-added code here that will be lost on regeneration
    custom_behavior()
    ...
```

All customization belongs in the specification or in separate non-generated files.

---

## Implementation Checklist

### Foundation

- [ ] Choose validation framework (SHACL recommended)
- [ ] Choose query language (SPARQL recommended)
- [ ] Choose template engine (Tera, Jinja2, Handlebars)
- [ ] Design ontology structure for your domain
- [ ] Create base shapes for common patterns

### Per-Specification

- [ ] Model formal content as RDF triples
- [ ] Add SHACL shapes for validation
- [ ] Write SPARQL queries for extraction
- [ ] Create templates for generation
- [ ] Link narrative prose as annotations
- [ ] Test the full pipeline end-to-end

### Pipeline Integration

- [ ] Integrate validation into CI
- [ ] Automate extraction and generation
- [ ] Verify idempotence (regenerate and diff)
- [ ] Generate receipts for verification
- [ ] Document the pipeline for team

---

## Resulting Context

After applying this pattern, you have:

- **Specifications that actively validate** their instances
- **Specifications that drive** code and documentation generation
- **No gap between specification and implementation**
- **Automatic detection** when specifications are violated
- **Tests derived from** specifications, not invented separately
- **Documentation that's always current** because it's generated
- **Confidence** that what you specify is what you get

This enables the full **[Constitutional Equation](../transformation/constitutional-equation.md)** pipeline and supports **[Test Before Code](../verification/test-before-code.md)**.

---

## Code References

The following spec-kit source files implement executable specification concepts:

| Reference | Description |
|-----------|-------------|
| `ontology/cli-commands.ttl:33-77` | InitCommand as executable specification with arguments/options |
| `ontology/spec-kit-schema.ttl:466-578` | SHACL shapes making specifications validatable |
| `sparql/extract-commands.rq:1-23` | SPARQL query executing against specification |
| `templates/command.tera:87-225` | Tera template rendering specification to code |
| `src/specify_cli/runtime/receipt.py:188-209` | verify_idempotence() executing transformation |

---

## Related Patterns

- *Builds on:* **[10. Single Source of Truth](./single-source-of-truth.md)** — Source must be executable
- *Uses:* **[12. Shape Constraint](./shape-constraint.md)** — SHACL makes specs executable
- *Uses:* **[14. Property Path](./property-path.md)** — SPARQL navigates relationships
- *Enables:* **[21. Constitutional Equation](../transformation/constitutional-equation.md)** — Transformation of specs
- *Enables:* **[23. Extraction Query](../transformation/extraction-query.md)** — SPARQL for data
- *Supports:* **[31. Test Before Code](../verification/test-before-code.md)** — Specs define tests
- *Supports:* **[45. Living Documentation](../evolution/living-documentation.md)** — Docs from specs

---

## Philosophical Coda

> *"An ounce of specification is worth a pound of debugging."*

And an executable specification is worth a ton of passive documentation.

The executable specification represents a fundamental shift in how we think about requirements. Traditional requirements are **promises**—statements of intent that may or may not be fulfilled. Executable specifications are **contracts**—formally binding definitions that are automatically enforced.

When specifications execute, several things change:

1. **Authority shifts from interpretation to definition.** What the specification says is what the system does, not what someone thinks the specification means.

2. **Validation becomes continuous.** Instead of periodic audits, every change is validated instantly against the specification.

3. **Documentation is never wrong.** Generated documentation reflects actual behavior because it comes from the same source.

4. **Testing is systematic.** Test cases derive from specifications, ensuring coverage of specified behavior.

5. **Evolution is safe.** Changes to specifications propagate automatically to all affected artifacts.

The cost is precision—you must say exactly what you mean. The benefit is correctness—what you say is what you get.

---

## Exercises

### Exercise 1: Executability Assessment

Take an existing prose specification and assess its executability:
1. What can be formally modeled?
2. What constraints could become SHACL shapes?
3. What data could SPARQL extract?
4. What artifacts could templates generate?
5. What must remain prose?

### Exercise 2: Shape Design

For a domain you know well:
1. Identify the core entities
2. Define their required properties
3. Express constraints as SHACL shapes
4. Test shapes against valid and invalid examples

### Exercise 3: Pipeline Construction

Build a minimal execution pipeline:
1. Create one RDF specification
2. Add one SHACL shape
3. Write one SPARQL query
4. Create one template
5. Generate output and verify

### Exercise 4: Prose to RDF Migration

Take a prose requirements document and:
1. Identify all formal content
2. Model as RDF triples
3. Keep narrative as annotations
4. Verify nothing was lost
5. Demonstrate executable benefits

---

## Further Reading

- *Specification by Example* — Gojko Adzic
- *Behavior-Driven Development* — Dan North
- *Executable Specifications with Scrum* — Mario Cardinal
- *Model-Driven Development* — Stahl & Völter
- *SHACL Specification* — W3C Recommendation

