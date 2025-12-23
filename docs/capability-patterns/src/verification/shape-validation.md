# 34. Shape Validation

★★

*Before transformation, validation. Shape validation uses SHACL to verify that specifications conform to their structural requirements—catching errors at the earliest possible point.*

---

Shape validation is the gatekeeper. It stands at the entrance of the transformation pipeline, examining every specification before processing begins.

The **[Normalization Stage](../transformation/normalization-stage.md)** described how validation works within transformation. Shape Validation is the verification practice that ensures validation happens consistently, comprehensively, and helpfully.

**The problem: Invalid specifications can produce subtle errors. Shape validation catches structural problems before they propagate.**

---

**The forces at play:**

- *Early detection wants strict validation.* Catch everything at the gate.

- *Development wants flexibility.* Strict validation blocks experimentation.

- *Feedback wants clarity.* Errors should guide correction.

- *Evolution wants adaptability.* Shapes change as understanding grows.

The tension: strict enough to catch real errors, flexible enough to support development.

---

**Therefore:**

Implement comprehensive shape validation with clear feedback, severity levels, and evolution support.

**Validation pipeline:**

```bash
# Validate before any transformation
specify validate ontology/cli-commands.ttl --shapes shapes/

# Or as part of ggen sync
ggen sync  # Implicitly validates first
```

**SHACL shapes with severity:**

```turtle
sk:CommandShape a sh:NodeShape ;
    sh:targetClass cli:Command ;

    # Violation: Must have name (blocks transformation)
    sh:property [
        sh:path rdfs:label ;
        sh:minCount 1 ;
        sh:severity sh:Violation ;
        sh:message "Command must have a name"
    ] ;

    # Warning: Should have description (proceeds with warning)
    sh:property [
        sh:path sk:description ;
        sh:minCount 1 ;
        sh:severity sh:Warning ;
        sh:message "Command should have a description"
    ] ;

    # Info: Might have examples (informational only)
    sh:property [
        sh:path sk:example ;
        sh:minCount 1 ;
        sh:severity sh:Info ;
        sh:message "Consider adding usage examples"
    ] .
```

**Validation modes:**

```toml
# ggen.toml
[validation]
# strict: Violations block, warnings logged
# relaxed: Violations block, warnings ignored
# permissive: Everything logged, nothing blocks
# off: No validation (dangerous!)
mode = "strict"
```

**Error reporting:**

```
$ specify validate ontology/cli-commands.ttl

Validation Report: ontology/cli-commands.ttl
═══════════════════════════════════════════

✗ 2 Violations (blocking)
⚠ 1 Warning
ℹ 3 Info

───────────────────────────────────────────
VIOLATION 1/2
  Shape:   sk:CommandShape
  Focus:   cli:NewCommand
  Path:    rdfs:label
  Message: Command must have a name
  Line:    42

  Fix: Add 'rdfs:label "command-name"' to cli:NewCommand

───────────────────────────────────────────
VIOLATION 2/2
  Shape:   sk:ArgumentShape
  Focus:   cli:FileArg
  Path:    cli:type
  Message: Argument must specify a type
  Line:    47

  Fix: Add 'cli:type "Path"' or other valid type

───────────────────────────────────────────
WARNING 1/1
  Shape:   sk:CommandShape
  Focus:   cli:ValidateCommand
  Path:    sk:description
  Message: Command should have a description

───────────────────────────────────────────

Validation failed with 2 violations.
Fix violations and run again.
```

**CI integration:**

```yaml
# .github/workflows/validate.yml
- name: Validate RDF specifications
  run: |
    specify validate ontology/*.ttl --shapes shapes/
    if [ $? -ne 0 ]; then
      echo "RDF validation failed"
      exit 1
    fi
```

---

**Resulting context:**

After applying this pattern, you have:

- Early detection of specification errors
- Clear feedback guiding corrections
- Configurable severity for different contexts
- CI enforcement of specification quality

This implements **[12. Shape Constraint](../specification/shape-constraint.md)** and enables **[37. Continuous Validation](./continuous-validation.md)**.

---

**Related patterns:**

- *Implements:* **[12. Shape Constraint](../specification/shape-constraint.md)** — Shapes enforced
- *Part of:* **[22. Normalization Stage](../transformation/normalization-stage.md)** — Validation in pipeline
- *Enables:* **[37. Continuous Validation](./continuous-validation.md)** — CI validation
- *Supports:* **[35. Drift Detection](./drift-detection.md)** — Shapes prevent drift

---

> *"The best error message is the one that never shows up."*

Shape validation catches errors before they cause problems—the earlier the better, ideally before the code is even written.
