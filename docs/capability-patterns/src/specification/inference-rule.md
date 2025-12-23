# 15. Inference Rule

★

*Not all knowledge needs to be explicitly stated. Inference rules derive new facts from existing ones, keeping specifications DRY while enabling rich querying. The best facts are the ones you don't have to state—because they're derived.*

---

## The Explicit Knowledge Burden

Your specifications contain explicit knowledge: "Command X has argument Y." But they also imply knowledge that isn't directly stated:

- "Command X has at least one required argument" (implied by the arguments' properties)
- "Command X is a CLI element" (implied by class hierarchy)
- "Argument Y belongs to Command X" (inverse of "has argument")
- "Job Z is an opportunity" (implied by high-importance, low-satisfaction outcomes)

Without inference, you face a choice:

**Option 1: State Everything Explicitly**

```turtle
# Explicit everything (verbose, error-prone)
cli:ValidateCommand a cli:Command .
cli:ValidateCommand a sk:CLIElement .        # Redundant if Command subclassOf CLIElement
cli:ValidateCommand a sk:Entity .            # Redundant if CLIElement subclassOf Entity
cli:ValidateCommand cli:hasRequiredArg true . # Redundant if any argument is required
cli:FileArg cli:belongsTo cli:ValidateCommand . # Redundant inverse of hasArgument
```

This is:
- **Verbose**: Every implied fact must be written
- **Error-prone**: Facts can become inconsistent
- **Hard to maintain**: Changes require updating multiple places

**Option 2: Compute in Application Code**

```python
# Derived facts computed in code
def has_required_arg(command):
    return any(arg.required for arg in command.arguments)

def get_command_for_arg(arg, graph):
    for cmd in graph.commands:
        if arg in cmd.arguments:
            return cmd
```

This is:
- **Scattered**: Logic lives in code, not specifications
- **Unqueryable**: SPARQL can't see application-computed facts
- **Duplicated**: Different code paths may recompute the same logic

**Option 3: Declare Inference Rules**

```turtle
# Declare the rule
cli:Command rdfs:subClassOf sk:CLIElement .
cli:hasArgument rdfs:domain cli:Command .
cli:belongsTo owl:inverseOf cli:hasArgument .

# State the minimal facts
cli:ValidateCommand a cli:Command .
cli:ValidateCommand cli:hasArgument cli:FileArg .

# Reasoner computes the rest
# Inferred: cli:ValidateCommand a sk:CLIElement .
# Inferred: cli:FileArg cli:belongsTo cli:ValidateCommand .
```

This is the best of both worlds: minimal explicit facts, rich derived knowledge.

---

## The Problem Statement

**Explicitly stating all facts is verbose and error-prone. Computing derived facts in code scatters logic and prevents querying derived knowledge. Inference rules offer a declarative alternative that keeps specifications DRY while enabling rich querying.**

---

## The Forces at Play

### Force 1: Completeness vs. DRY

**Completeness wants all facts stated.** Queries work best with explicit data.

**DRY wants minimal redundancy.** Redundant facts can become inconsistent.

```
Completeness ←────────────────────────→ DRY
(state everything)                      (state once, derive rest)
```

### Force 2: Performance vs. Expressiveness

**Performance wants less computation.** Inference can be expensive.

**Expressiveness wants rich derivations.** The more you can infer, the simpler your explicit specifications.

```
Performance ←────────────────────────→ Expressiveness
(pre-computed facts)                   (derived on demand)
```

### Force 3: Transparency vs. Power

**Transparency wants visible logic.** Inferred facts can seem "magical."

**Power wants sophisticated reasoning.** Complex domain rules are best expressed as inference.

```
Transparency ←────────────────────────→ Power
(see everything)                        (derive everything)
```

---

## Therefore: Use Layered Inference Rules

Use RDFS and OWL inference rules judiciously, and supplement with SPARQL CONSTRUCT rules for domain-specific inference.

### Layer 1: RDFS Inference (Class/Property Hierarchies)

```turtle
# Class hierarchy
cli:ValidateCommand a cli:Command .
cli:Command rdfs:subClassOf sk:CLIElement .
# Inferred: cli:ValidateCommand a sk:CLIElement .
```

```turtle
# Property domains and ranges
cli:hasArgument rdfs:domain cli:Command .
cli:hasArgument rdfs:range cli:Argument .

cli:ValidateCommand cli:hasArgument cli:FileArg .
# Inferred: cli:ValidateCommand a cli:Command .
# Inferred: cli:FileArg a cli:Argument .
```

### Layer 2: OWL Inference (Use Sparingly)

```turtle
# Inverse properties
cli:argumentOf owl:inverseOf cli:hasArgument .

cli:ValidateCommand cli:hasArgument cli:FileArg .
# Inferred: cli:FileArg cli:argumentOf cli:ValidateCommand .
```

```turtle
# Transitive properties
rdfs:subClassOf a owl:TransitiveProperty .

cli:Command rdfs:subClassOf sk:CLIElement .
sk:CLIElement rdfs:subClassOf sk:Entity .
# Inferred: cli:Command rdfs:subClassOf sk:Entity .
```

### Layer 3: SPARQL CONSTRUCT for Domain Rules

```sparql
# Rule: Commands with all optional arguments are "relaxed"
CONSTRUCT {
    ?cmd cli:strictness "relaxed" .
}
WHERE {
    ?cmd a cli:Command .
    FILTER NOT EXISTS {
        ?cmd cli:hasArgument ?arg .
        ?arg cli:required true .
    }
}
```

```sparql
# Rule: Jobs with high-importance, low-satisfaction outcomes are "opportunity"
CONSTRUCT {
    ?job jtbd:status "opportunity" .
}
WHERE {
    ?job a jtbd:Job ;
         jtbd:hasOutcome ?outcome .
    ?outcome jtbd:importance "high" ;
             jtbd:satisfaction "low" .
}
```

### Inference Layering

```
Layer 1: Explicit facts (stated in .ttl files)
    │
    ▼
Layer 2: RDFS inference (class/property hierarchies)
    │
    ▼
Layer 3: OWL inference (inverses, transitivity)
    │
    ▼
Layer 4: SPARQL rules (domain-specific derivations)
    │
    ▼
Complete knowledge base (for querying)
```

---

## Inference Hygiene

1. **Document rules:** Each rule should have rdfs:comment explaining its purpose
2. **Test inference:** Verify derived facts are correct
3. **Limit depth:** Deep inference chains are hard to debug
4. **Make derivation visible:** Consider adding provenance to inferred facts
5. **Profile performance:** Inference can be expensive—measure impact

---

## When NOT to Infer

Some knowledge should be explicit:

- **Security-sensitive facts** (don't infer permissions)
- **Facts that might be wrong** (explicit is safer)
- **Facts users need to see and understand** (transparency)

Inference is powerful but not free. Use it for patterns that genuinely reduce maintenance burden and improve query expressiveness.

---

## Resulting Context

After applying this pattern, you have:

- Reduced redundancy in explicit specifications
- Rich derived facts available for querying
- Clear separation of explicit and derived knowledge
- Maintainable inference rules

This supports **[Executable Specification](./executable-specification.md)** and enhances **[Extraction Query](../transformation/extraction-query.md)**.

---

## Related Patterns

- *Enhances:* **[11. Executable Specification](./executable-specification.md)** — Inference executes rules
- *Supports:* **[23. Extraction Query](../transformation/extraction-query.md)** — Queries see inferred facts
- *Leverages:* **[16. Layered Ontology](./layered-ontology.md)** — Inference respects layers

---

> *"The best code is no code at all."*
>
> — Jeff Atwood

The best facts are the ones you don't have to state—because they're derived.

