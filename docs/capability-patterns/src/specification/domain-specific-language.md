# 17. Domain-Specific Language

★

*Generic languages can express anything but optimize nothing. Domain-specific languages encode domain knowledge, making common operations simple and errors obvious.*

---

RDF is a universal representation. It can express any knowledge. But universality comes at a cost: expressing domain-specific concepts requires verbose, unfamiliar syntax.

Consider specifying a CLI command. In raw RDF:

```turtle
cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;
    cli:hasArgument [
        a cli:Argument ;
        sk:name "file" ;
        cli:type "Path" ;
        cli:required true ;
        cli:help "File to validate"
    ] ;
    cli:hasOption [
        a cli:Option ;
        sk:name "--strict" ;
        cli:type "bool" ;
        cli:default "false" ;
        cli:help "Enable strict mode"
    ] .
```

This is precise but verbose. Someone unfamiliar with the ontology struggles to write it. Someone experienced finds it tedious.

**The problem: Universal representations are verbose and unfamiliar for domain-specific tasks. Authors spend effort on syntax rather than content.**

---

**The forces at play:**

- *Power wants expressiveness.* RDF can represent anything.

- *Usability wants familiarity.* Authors want syntax they recognize.

- *Validation wants structure.* Arbitrary syntax is hard to validate.

- *Tooling wants standards.* Custom languages need custom tools.

The tension: make common domain operations simple without sacrificing RDF's power and ecosystem.

---

**Therefore:**

Create domain-specific patterns and templates that make common operations concise while remaining valid RDF.

**Approach 1: Standardized templates**

Create template files that authors fill in:

```turtle
# templates/command-template.ttl
# Copy and modify for new commands

cli:NewCommand a cli:Command ;
    rdfs:label "command-name" ;         # <-- Change this
    sk:description "Description" ;       # <-- Change this
    cli:hasArgument [
        # Copy this block for each argument
        a cli:Argument ;
        sk:name "arg-name" ;
        cli:type "TYPE" ;  # string, Path, int, bool
        cli:required true ;  # or false
        cli:help "Help text"
    ] .
```

**Approach 2: Simplified Turtle patterns**

Use blank nodes and shorthand consistently:

```turtle
# Idiomatic: Arguments inline with sequence
cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files" ;
    cli:args (
        [ sk:name "file" ; cli:type "Path" ; cli:required true ]
        [ sk:name "output" ; cli:type "Path" ; cli:required false ]
    ) .
```

**Approach 3: External DSL with translation**

For complex domains, create a simpler external DSL that compiles to RDF:

```yaml
# commands.yaml (external DSL)
validate:
  description: Validate RDF files
  arguments:
    - name: file
      type: Path
      required: true
    - name: output
      type: Path
      required: false
  options:
    - name: --strict
      type: bool
      default: false
```

Translate to RDF:
```bash
yaml-to-rdf commands.yaml > commands.ttl
```

**Approach 4: Macros and abbreviations**

Define abbreviations in ontology:

```turtle
# Shorthand properties
cli:arg a rdf:Property ;
    rdfs:subPropertyOf cli:hasArgument .

cli:opt a rdf:Property ;
    rdfs:subPropertyOf cli:hasOption .

# Usage becomes:
cli:ValidateCommand
    cli:arg [ sk:name "file" ; cli:type "Path" ] ;
    cli:opt [ sk:name "--strict" ; cli:type "bool" ] .
```

---

**Resulting context:**

After applying this pattern, you have:

- Reduced verbosity for common operations
- Familiar patterns for domain authors
- Valid RDF that works with all standard tools
- Flexibility to use full RDF power when needed

This supports author productivity while maintaining **[Semantic Foundation](./semantic-foundation.md)**.

---

**Related patterns:**

- *Simplifies:* **[9. Semantic Foundation](./semantic-foundation.md)** — DSL for RDF
- *Enables:* **[18. Narrative Specification](./narrative-specification.md)** — DSL for narratives
- *Complements:* **[12. Shape Constraint](./shape-constraint.md)** — DSL validated by shapes

---

> *"A language that doesn't affect the way you think about programming is not worth knowing."*
>
> — Alan Perlis

A domain-specific language, even a thin one over RDF, affects how you think about your domain. It encodes best practices, makes common tasks easy, and keeps the focus on content.

---

**DSL design principles:**

1. **Make the common case simple:** 90% of uses should be one-liners
2. **Allow escape to full power:** Complex cases can use raw RDF
3. **Fail clearly:** Bad DSL input should produce helpful errors
4. **Stay translatable:** DSL must map cleanly to RDF semantics
5. **Document idioms:** Show the patterns authors should follow
