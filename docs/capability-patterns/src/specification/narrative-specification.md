# 18. Narrative Specification

★

*Formal specifications capture structure. Narrative specifications capture intent, context, and rationale. Both are necessary for complete understanding.*

---

Your **[Executable Specifications](./executable-specification.md)** define *what* must be true. They're precise, validatable, transformable. But they don't explain *why*.

Why does this command exist? What problem drove its creation? What trade-offs were considered? What should implementers understand about the design intent?

Pure formal specifications are like assembly language—precise but opaque. The machine understands perfectly. Humans struggle. Future maintainers wonder: "What were they thinking?"

Narrative specifications provide the human context that formal specifications cannot.

**The problem: Formal specifications are necessary but not sufficient. Without narrative, intent is lost and maintenance becomes archaeology.**

---

**The forces at play:**

- *Formality enables automation.* Machines process structure, not stories.

- *Narrative enables understanding.* Humans understand through stories, not structure.

- *Separation risks drift.* Narrative in separate documents drifts from formal specs.

- *Integration risks noise.* Narrative in formal specs clutters structure.

The tension: keep narrative close to formal specs without cluttering them.

---

**Therefore:**

Embed narrative as structured annotations within formal specifications, then extract them during transformation.

**Annotation patterns:**

```turtle
cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;

    # Narrative annotations
    sk:rationale """
        Users frequently commit invalid RDF because validation
        is a separate, manual step. By making validation a
        first-class CLI command, we integrate it into the
        natural workflow.
    """ ;

    sk:designDecision """
        We chose streaming validation over loading the entire
        file to support large ontologies without memory issues.
    """ ;

    sk:usageScenario """
        Developer finishes editing ontology.ttl, runs
        'specify validate ontology.ttl', sees "Valid ✓",
        commits with confidence.
    """ ;

    sk:alternatives """
        - IDE plugin: Rejected because not all users use IDEs
        - Pre-commit hook: Offered as additional option
        - CI-only: Rejected because feedback too slow
    """ ;

    cli:hasArgument ... .
```

**Narrative property hierarchy:**

```turtle
# Core narrative properties
sk:rationale rdfs:subPropertyOf sk:narrative ;
    rdfs:comment "Why this element exists" .

sk:designDecision rdfs:subPropertyOf sk:narrative ;
    rdfs:comment "Key design choices made" .

sk:usageScenario rdfs:subPropertyOf sk:narrative ;
    rdfs:comment "How this is used in practice" .

sk:alternatives rdfs:subPropertyOf sk:narrative ;
    rdfs:comment "Options considered but not chosen" .

sk:caveat rdfs:subPropertyOf sk:narrative ;
    rdfs:comment "Warnings and limitations" .

sk:futureWork rdfs:subPropertyOf sk:narrative ;
    rdfs:comment "Potential enhancements" .
```

**Extraction for documentation:**

```sparql
# Extract narrative for documentation
SELECT ?command ?rationale ?scenario WHERE {
    ?command a cli:Command ;
             sk:rationale ?rationale ;
             sk:usageScenario ?scenario .
}
```

**Template with narrative:**

```jinja
# {{ name }}

{{ description }}

## Why This Command Exists

{{ rationale }}

## Usage Scenario

{{ usageScenario }}

## Design Decisions

{{ designDecision }}

{% if alternatives %}
## Alternatives Considered

{{ alternatives }}
{% endif %}
```

---

**Resulting context:**

After applying this pattern, you have:

- Narrative collocated with formal specification
- Extractable narrative for documentation generation
- Intent preserved for future maintainers
- Stories that help users understand purpose

This enhances **[Human-Readable Artifact](../transformation/human-readable-artifact.md)** and supports **[Living Documentation](../evolution/living-documentation.md)**.

---

**Related patterns:**

- *Complements:* **[11. Executable Specification](./executable-specification.md)** — Narrative for formal
- *Feeds:* **[30. Human-Readable Artifact](../transformation/human-readable-artifact.md)** — Narrative in docs
- *Enables:* **[45. Living Documentation](../evolution/living-documentation.md)** — Docs stay current

---

> *"Code tells you how. Comments tell you why."*

Specifications tell you what. Narrative tells you why. Both are essential.

---

**Narrative quality:**

Good narrative:
- Explains *why*, not *what* (the spec handles what)
- Captures context that might be lost
- Helps future maintainers understand intent
- Uses concrete scenarios, not abstract description

Bad narrative:
- Restates the formal specification in prose
- Describes implementation details
- Becomes stale and misleading
- Adds noise without insight

---

**Keeping narrative fresh:**

Narrative drifts when it's separate from specs. By embedding narrative in the same file as formal specs, changes naturally prompt narrative updates. The diff shows both structural changes and their explanation.
