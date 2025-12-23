# 17. Domain-Specific Language

★

*Generic languages can express anything but optimize nothing. Domain-specific languages encode domain knowledge, making common operations simple and errors obvious. They are the native tongue of your problem space—fluent where general languages are stilted.*

---

## The Verbosity Burden

RDF is a universal representation. It can express any knowledge. But universality comes at a cost: expressing domain-specific concepts requires verbose, unfamiliar syntax that obscures rather than reveals intent.

Consider specifying a CLI command. In raw RDF:

```turtle
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

cli:ValidateCommand a cli:Command ;
    rdfs:label "validate" ;
    sk:description "Validate RDF files against SHACL shapes" ;
    sk:version "1.0.0" ;
    cli:exitCodeSuccess 0 ;
    cli:exitCodeError 1 ;
    cli:hasArgument [
        a cli:Argument ;
        sk:name "file" ;
        cli:type "Path" ;
        cli:position 0 ;
        cli:required true ;
        cli:help "The RDF file to validate" ;
        cli:metavar "FILE"
    ] ;
    cli:hasArgument [
        a cli:Argument ;
        sk:name "shapes" ;
        cli:type "Path" ;
        cli:position 1 ;
        cli:required false ;
        cli:help "SHACL shapes file (optional)" ;
        cli:metavar "SHAPES"
    ] ;
    cli:hasOption [
        a cli:Option ;
        sk:name "--strict" ;
        cli:shortName "-s" ;
        cli:type "bool" ;
        cli:default "false" ;
        cli:help "Enable strict validation mode"
    ] ;
    cli:hasOption [
        a cli:Option ;
        sk:name "--output" ;
        cli:shortName "-o" ;
        cli:type "Path" ;
        cli:help "Output file for validation report"
    ] ;
    cli:hasOption [
        a cli:Option ;
        sk:name "--format" ;
        cli:shortName "-f" ;
        cli:type "string" ;
        cli:default "text" ;
        cli:choices ("text" "json" "turtle") ;
        cli:help "Output format for report"
    ] .
```

This specification is precise and machine-readable—excellent for transformation. But it's painful to write, error-prone to maintain, and daunting for newcomers to read. The ceremony overwhelms the content.

---

## The Problem Statement

**Universal representations are verbose and unfamiliar for domain-specific tasks. Authors spend mental effort on syntax rather than content. The signal-to-noise ratio is poor.**

The symptoms of verbosity:
- **Author friction**: Too much typing for simple concepts
- **Error likelihood**: More syntax means more opportunities for mistakes
- **Learning curve**: New team members struggle with unfamiliar patterns
- **Maintenance burden**: Updates require touching many places
- **Review difficulty**: Reviewers can't see the forest for the trees

---

## The Forces at Play

### Force 1: Power vs. Usability

**Power wants expressiveness.** RDF can represent anything. Arbitrary graphs, complex relationships, nuanced semantics. This power is why we chose it.

**Usability wants familiarity.** Authors want syntax they recognize. Natural expressions for their domain. Minimal ceremony for common operations.

```
Power ←──────────────────────────────────→ Usability
(express anything)                         (express common things easily)
```

### Force 2: Standards vs. Customization

**Standards enable tooling.** The RDF ecosystem provides validators, query engines, visualization tools. Custom syntax loses this ecosystem.

**Customization enables fit.** Your domain has unique patterns. Generic RDF syntax doesn't match how domain experts think about their work.

```
Standards ←──────────────────────────────→ Customization
(use existing tools)                       (match domain thinking)
```

### Force 3: Validation vs. Flexibility

**Validation wants structure.** Schemas and shapes can validate structured RDF. Arbitrary syntax is harder to check.

**Flexibility wants freedom.** Authors shouldn't be constrained by validation limits. Edge cases need escape hatches.

```
Validation ←─────────────────────────────→ Flexibility
(catch errors early)                       (allow unusual cases)
```

### Force 4: Abstraction vs. Transparency

**Abstraction wants hiding.** Authors shouldn't need to know RDF details. Just express domain concepts directly.

**Transparency wants visibility.** When things go wrong, authors need to understand what's happening under the hood.

```
Abstraction ←────────────────────────────→ Transparency
(hide complexity)                          (reveal when needed)
```

---

## Therefore: Create Domain-Specific Patterns and Languages

**Design domain-specific languages (DSLs) and patterns that make common operations concise while remaining valid RDF or translating cleanly to RDF.**

The key insight: You don't have to choose between expressiveness and usability. A well-designed DSL provides both—domain-native syntax that translates to full RDF power.

### The DSL Spectrum

DSLs exist on a spectrum from "syntactic sugar" to "external language":

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DSL SPECTRUM                                  │
│                                                                      │
│  Native Turtle ◄────────────────────────────────────────► External  │
│                                                                      │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐        │
│  │ Idiomatic │  │ Template  │  │  Embedded │  │  External │        │
│  │  Turtle   │  │  Patterns │  │    DSL    │  │    DSL    │        │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘        │
│                                                                      │
│  Valid RDF ◄──────────────────────────────────────────► Translated │
│  (direct use)                                           (compiled)  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Approach 1: Idiomatic Turtle Patterns

The lightest approach: establish conventions for writing Turtle that's more readable without changing the language.

### Property Abbreviations

Define short-form properties that expand to standard ones:

```turtle
# In your ontology schema
cli:arg rdfs:subPropertyOf cli:hasArgument .
cli:opt rdfs:subPropertyOf cli:hasOption .
cli:req owl:equivalentProperty cli:required .

# Usage becomes terser
cli:ValidateCommand
    cli:arg [ sk:name "file" ; cli:type "Path" ; cli:req true ] ;
    cli:opt [ sk:name "--strict" ; cli:type "bool" ] .
```

### Blank Node Sequences

Use RDF lists for ordered elements:

```turtle
# Arguments in order using list syntax
cli:ValidateCommand cli:arguments (
    [ sk:name "file" ; cli:type "Path" ]
    [ sk:name "shapes" ; cli:type "Path" ; cli:req false ]
) .
```

### Consistent Ordering

Establish property order conventions that aid scanning:

```turtle
# Standard order: identity, description, structure, behavior
cli:ValidateCommand a cli:Command ;
    # 1. Identity
    sk:name "validate" ;
    sk:identifier "validate" ;
    sk:version "1.0.0" ;

    # 2. Description
    sk:description "Validate RDF files" ;
    cli:help "Validates RDF/Turtle files against SHACL shapes" ;

    # 3. Structure
    cli:hasArgument :file_arg ;
    cli:hasOption :strict_opt ;

    # 4. Behavior
    cli:exitCodeSuccess 0 ;
    cli:exitCodeError 1 .
```

### Inline vs. Referenced

Define when to use inline blank nodes vs. named references:

```turtle
# Inline: Simple, used once
cli:validate cli:hasOption [
    sk:name "--verbose" ;
    cli:type "bool"
] .

# Referenced: Complex, reused, or needs independent testing
:output_format_opt a cli:Option ;
    sk:name "--format" ;
    cli:type "string" ;
    cli:choices ("text" "json" "turtle" "html") ;
    cli:default "text" ;
    sk:description "Output format for generated artifacts" .

cli:validate cli:hasOption :output_format_opt .
cli:generate cli:hasOption :output_format_opt .  # Reused!
```

---

## Approach 2: Template Patterns

Create template files that authors copy and modify:

### Command Template

```turtle
# templates/command-template.ttl
# Copy this file and modify the marked sections

@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix sk: <https://spec-kit.io/ontology#> .
@prefix : <https://spec-kit.io/specs/commands#> .

# ═══════════════════════════════════════════════════════════════
# COMMAND DEFINITION
# Replace all [PLACEHOLDERS] with your values
# ═══════════════════════════════════════════════════════════════

:[COMMAND_ID] a cli:Command ;
    # ───────────────────────────────────────────────────────────
    # IDENTITY (Required)
    # ───────────────────────────────────────────────────────────
    sk:name "[command-name]" ;           # CLI name users type
    sk:identifier "[command_id]" ;        # Machine identifier
    sk:version "1.0.0" ;                  # Semantic version

    # ───────────────────────────────────────────────────────────
    # DESCRIPTION (Required)
    # ───────────────────────────────────────────────────────────
    sk:description "[One-line description]" ;
    cli:help """
        [Longer help text shown with --help]
        Can span multiple lines.
    """ ;

    # ───────────────────────────────────────────────────────────
    # ARGUMENTS (Zero or more)
    # Copy this block for each positional argument
    # ───────────────────────────────────────────────────────────
    cli:hasArgument [
        sk:name "[arg-name]" ;
        cli:type "[string|Path|int|float]" ;
        cli:required [true|false] ;
        cli:help "[Argument description]"
    ] ;

    # ───────────────────────────────────────────────────────────
    # OPTIONS (Zero or more)
    # Copy this block for each flag/option
    # ───────────────────────────────────────────────────────────
    cli:hasOption [
        sk:name "--[option-name]" ;
        cli:shortName "-[x]" ;            # Optional
        cli:type "[string|bool|int|Path]" ;
        cli:default "[default-value]" ;   # Optional
        cli:help "[Option description]"
    ] ;

    # ───────────────────────────────────────────────────────────
    # BEHAVIOR (Optional)
    # ───────────────────────────────────────────────────────────
    cli:exitCodeSuccess 0 ;
    cli:exitCodeError 1 .

# ═══════════════════════════════════════════════════════════════
# DELETE THIS SECTION after filling in the template
# ═══════════════════════════════════════════════════════════════
```

### Argument Type Templates

```turtle
# templates/argument-types.ttl
# Common argument patterns - copy the relevant one

# ───────────────────────────────────────────────────────────────
# FILE PATH ARGUMENT (required)
# ───────────────────────────────────────────────────────────────
:file_arg a cli:Argument ;
    sk:name "file" ;
    cli:type "Path" ;
    cli:required true ;
    cli:help "Path to input file" ;
    cli:metavar "FILE" .

# ───────────────────────────────────────────────────────────────
# OPTIONAL OUTPUT PATH
# ───────────────────────────────────────────────────────────────
:output_arg a cli:Argument ;
    sk:name "output" ;
    cli:type "Path" ;
    cli:required false ;
    cli:help "Path to output file (stdout if not specified)" ;
    cli:metavar "OUTPUT" .

# ───────────────────────────────────────────────────────────────
# MULTIPLE FILES (variadic)
# ───────────────────────────────────────────────────────────────
:files_arg a cli:Argument ;
    sk:name "files" ;
    cli:type "Path" ;
    cli:variadic true ;
    cli:minCount 1 ;
    cli:help "One or more input files" ;
    cli:metavar "FILES..." .

# ───────────────────────────────────────────────────────────────
# CHOICE ARGUMENT
# ───────────────────────────────────────────────────────────────
:format_arg a cli:Argument ;
    sk:name "format" ;
    cli:type "string" ;
    cli:choices ("json" "yaml" "toml") ;
    cli:default "json" ;
    cli:help "Output format" .
```

---

## Approach 3: Embedded DSL

Embed a simpler syntax within Turtle using string literals with special processing:

### YAML-in-Turtle

```turtle
# Define commands using embedded YAML (processed during transformation)
cli:commands sk:yamlSource """
validate:
  description: Validate RDF files against SHACL shapes
  arguments:
    - name: file
      type: Path
      required: true
      help: File to validate
  options:
    - name: --strict
      short: -s
      type: bool
      default: false
      help: Enable strict mode
    - name: --format
      short: -f
      type: string
      choices: [text, json, turtle]
      default: text
      help: Output format

generate:
  description: Generate artifacts from specifications
  arguments:
    - name: spec
      type: Path
      required: true
      help: Specification file
  options:
    - name: --output
      short: -o
      type: Path
      help: Output directory
""" .
```

### Processing the Embedded DSL

```python
# transformer/yaml_dsl.py
import yaml
from rdflib import Graph, Namespace, Literal, BNode

CLI = Namespace("https://spec-kit.io/ontology/cli#")
SK = Namespace("https://spec-kit.io/ontology#")

def expand_yaml_commands(graph: Graph) -> Graph:
    """Expand YAML-embedded command definitions to full RDF."""
    expanded = Graph()
    expanded += graph  # Copy existing triples

    # Find YAML sources
    for subj, pred, obj in graph.triples((None, SK.yamlSource, None)):
        commands = yaml.safe_load(str(obj))
        for name, spec in commands.items():
            cmd_node = CLI[f"{name.title()}Command"]
            expand_command(expanded, cmd_node, name, spec)

    # Remove YAML source triples (they've been expanded)
    for triple in graph.triples((None, SK.yamlSource, None)):
        expanded.remove(triple)

    return expanded

def expand_command(graph, cmd_node, name, spec):
    """Expand a single command from YAML to RDF."""
    graph.add((cmd_node, RDF.type, CLI.Command))
    graph.add((cmd_node, SK.name, Literal(name)))
    graph.add((cmd_node, SK.description, Literal(spec['description'])))

    for arg in spec.get('arguments', []):
        arg_node = BNode()
        graph.add((cmd_node, CLI.hasArgument, arg_node))
        graph.add((arg_node, RDF.type, CLI.Argument))
        graph.add((arg_node, SK.name, Literal(arg['name'])))
        # ... expand remaining properties

    for opt in spec.get('options', []):
        opt_node = BNode()
        graph.add((cmd_node, CLI.hasOption, opt_node))
        # ... expand remaining properties
```

### Table-in-Turtle

For tabular data, embed markdown tables:

```turtle
cli:commandTable sk:markdownTable """
| Command   | Description                    | Category   |
|-----------|--------------------------------|------------|
| validate  | Validate RDF against shapes    | validation |
| generate  | Generate artifacts from specs  | generation |
| query     | Query specifications           | query      |
| init      | Initialize new project         | setup      |
| check     | Check tool availability        | utility    |
""" .
```

---

## Approach 4: External DSL with Translation

For complex domains, create a standalone DSL that compiles to RDF:

### YAML Command DSL

```yaml
# commands.yaml - External DSL file
version: "1.0"
namespace: "https://spec-kit.io/specs/commands#"

commands:
  validate:
    type: validation
    description: Validate RDF files against SHACL shapes
    long_help: |
      Validates one or more RDF/Turtle files against SHACL shape
      definitions. Returns exit code 0 if valid, non-zero otherwise.

    arguments:
      - name: file
        type: Path
        required: true
        help: Path to the RDF file to validate
        completion: file:*.ttl

      - name: shapes
        type: Path
        required: false
        help: Optional SHACL shapes file

    options:
      - name: --strict
        short: -s
        type: bool
        default: false
        help: Enable strict validation mode

      - name: --format
        short: -f
        type: choice
        choices: [text, json, turtle]
        default: text
        help: Output format for validation report

      - name: --quiet
        short: -q
        type: bool
        default: false
        help: Suppress non-error output

    examples:
      - command: specify validate ontology.ttl
        description: Validate a single file

      - command: specify validate ontology.ttl --strict
        description: Strict validation

      - command: specify validate data.ttl shapes.ttl
        description: Validate against specific shapes

    exit_codes:
      0: Validation successful
      1: Validation failed
      2: File not found
      3: Invalid RDF syntax

    accomplishes_jobs:
      - PreCommitValidation
      - CIValidation

  generate:
    type: generation
    # ... more commands
```

### DSL Compiler

```python
#!/usr/bin/env python3
# tools/yaml2rdf.py - Compile YAML DSL to RDF/Turtle

import yaml
import sys
from pathlib import Path

def compile_yaml_to_turtle(yaml_path: Path) -> str:
    """Compile YAML command DSL to RDF/Turtle."""
    with open(yaml_path) as f:
        spec = yaml.safe_load(f)

    lines = [
        "# Generated from {}".format(yaml_path.name),
        "# DO NOT EDIT - Edit the YAML source instead",
        "",
        "@prefix cli: <https://spec-kit.io/ontology/cli#> .",
        "@prefix sk: <https://spec-kit.io/ontology#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        f"@prefix : <{spec['namespace']}> .",
        "",
    ]

    for name, cmd in spec.get('commands', {}).items():
        lines.extend(compile_command(name, cmd))
        lines.append("")

    return "\n".join(lines)

def compile_command(name: str, cmd: dict) -> list[str]:
    """Compile a single command to Turtle triples."""
    cmd_id = f":{name}"
    cmd_type = f"cli:{cmd.get('type', '').title()}Command" if cmd.get('type') else "cli:Command"

    lines = [
        f"{cmd_id} a {cmd_type} ;",
        f'    sk:name "{name}" ;',
        f'    sk:description "{cmd["description"]}" ;',
    ]

    if cmd.get('long_help'):
        lines.append(f'    cli:help """{cmd["long_help"]}""" ;')

    # Compile arguments
    for i, arg in enumerate(cmd.get('arguments', [])):
        arg_lines = compile_argument(arg, i)
        lines.append(f'    cli:hasArgument {arg_lines} ;')

    # Compile options
    for opt in cmd.get('options', []):
        opt_lines = compile_option(opt)
        lines.append(f'    cli:hasOption {opt_lines} ;')

    # Exit codes
    if cmd.get('exit_codes'):
        lines.append(f'    cli:exitCodeSuccess {list(cmd["exit_codes"].keys())[0]} ;')

    # Close the command
    lines[-1] = lines[-1].rstrip(' ;') + ' .'

    return lines

def compile_argument(arg: dict, position: int) -> str:
    """Compile an argument to inline Turtle."""
    parts = [
        f'sk:name "{arg["name"]}"',
        f'cli:type "{arg["type"]}"',
        f'cli:position {position}',
        f'cli:required {str(arg.get("required", False)).lower()}',
    ]
    if arg.get('help'):
        parts.append(f'cli:help "{arg["help"]}"')

    return "[\n        " + " ;\n        ".join(parts) + "\n    ]"

def compile_option(opt: dict) -> str:
    """Compile an option to inline Turtle."""
    parts = [f'sk:name "{opt["name"]}"']

    if opt.get('short'):
        parts.append(f'cli:shortName "{opt["short"]}"')

    parts.append(f'cli:type "{opt["type"]}"')

    if opt.get('default') is not None:
        default = str(opt['default']).lower() if opt['type'] == 'bool' else opt['default']
        parts.append(f'cli:default "{default}"')

    if opt.get('choices'):
        choices = ' '.join(f'"{c}"' for c in opt['choices'])
        parts.append(f'cli:choices ({choices})')

    if opt.get('help'):
        parts.append(f'cli:help "{opt["help"]}"')

    return "[\n        " + " ;\n        ".join(parts) + "\n    ]"

if __name__ == '__main__':
    yaml_file = Path(sys.argv[1])
    print(compile_yaml_to_turtle(yaml_file))
```

### Integration with Build

```makefile
# Makefile
YAML_SOURCES := $(wildcard dsl/*.yaml)
TTL_TARGETS := $(YAML_SOURCES:dsl/%.yaml=memory/%.ttl)

memory/%.ttl: dsl/%.yaml
	python tools/yaml2rdf.py $< > $@

all: $(TTL_TARGETS)
	ggen sync

clean:
	rm -f $(TTL_TARGETS)
```

---

## Approach 5: Macro System

Define macros that expand to common patterns:

### Macro Definitions

```turtle
# ontology/macros.ttl
@prefix macro: <https://spec-kit.io/macro#> .

# Required Path argument macro
macro:RequiredPathArg a macro:ArgumentMacro ;
    macro:expands """
        [ a cli:Argument ;
          sk:name "{name}" ;
          cli:type "Path" ;
          cli:required true ;
          cli:help "{help}" ;
          cli:metavar "{metavar}" ]
    """ ;
    macro:parameters ( "name" "help" "metavar" ) .

# Boolean flag macro
macro:BoolFlag a macro:OptionMacro ;
    macro:expands """
        [ a cli:Option ;
          sk:name "--{name}" ;
          cli:shortName "-{short}" ;
          cli:type "bool" ;
          cli:default "false" ;
          cli:help "{help}" ]
    """ ;
    macro:parameters ( "name" "short" "help" ) .

# Choice option macro
macro:ChoiceOption a macro:OptionMacro ;
    macro:expands """
        [ a cli:Option ;
          sk:name "--{name}" ;
          cli:type "string" ;
          cli:choices {choices} ;
          cli:default "{default}" ;
          cli:help "{help}" ]
    """ ;
    macro:parameters ( "name" "choices" "default" "help" ) .
```

### Using Macros

```turtle
# commands.ttl - Using macros
@prefix cli: <https://spec-kit.io/ontology/cli#> .
@prefix macro: <https://spec-kit.io/macro#> .

cli:validate a cli:Command ;
    sk:name "validate" ;
    sk:description "Validate RDF files" ;

    # Macro invocations (expanded by preprocessor)
    cli:hasArgument [
        macro:invoke macro:RequiredPathArg ;
        macro:param "name" "file" ;
        macro:param "help" "File to validate" ;
        macro:param "metavar" "FILE"
    ] ;

    cli:hasOption [
        macro:invoke macro:BoolFlag ;
        macro:param "name" "strict" ;
        macro:param "short" "s" ;
        macro:param "help" "Enable strict mode"
    ] ;

    cli:hasOption [
        macro:invoke macro:ChoiceOption ;
        macro:param "name" "format" ;
        macro:param "choices" ("text" "json" "turtle") ;
        macro:param "default" "text" ;
        macro:param "help" "Output format"
    ] .
```

---

## DSL Design Principles

### Principle 1: Make the Common Case Simple

90% of uses should be one-liners. Optimize for the frequent cases:

```yaml
# Common: Simple required argument
arguments:
  - file: Path!  # Shorthand: "Path!" means required Path

# Common: Boolean flag with short name
options:
  - verbose: -v  # Shorthand: bool flag with short name

# Less common: Full specification still available
arguments:
  - name: files
    type: Path
    variadic: true
    min_count: 1
    max_count: 10
    help: Input files to process
    completion: file:*.ttl
```

### Principle 2: Allow Escape to Full Power

Complex cases can use raw RDF. Don't force everything through the DSL:

```yaml
commands:
  simple:
    description: A simple command
    # DSL handles this easily

  complex:
    # Escape hatch: raw Turtle for complex cases
    raw_turtle: |
      :complex a cli:Command ;
          sk:name "complex" ;
          # ... arbitrarily complex RDF
```

### Principle 3: Fail Clearly

Bad DSL input should produce helpful errors:

```python
def validate_command(name: str, spec: dict) -> list[str]:
    """Validate a command specification, returning error messages."""
    errors = []

    if not spec.get('description'):
        errors.append(f"Command '{name}': missing required 'description'")

    for i, arg in enumerate(spec.get('arguments', [])):
        if not arg.get('name'):
            errors.append(f"Command '{name}' argument {i}: missing 'name'")
        if arg.get('type') not in VALID_TYPES:
            errors.append(
                f"Command '{name}' argument '{arg.get('name')}': "
                f"invalid type '{arg.get('type')}', "
                f"must be one of {VALID_TYPES}"
            )

    return errors
```

### Principle 4: Stay Translatable

DSL must map cleanly to RDF semantics. No concepts that can't be expressed in the target:

```yaml
# GOOD: Maps directly to RDF
arguments:
  - name: file
    type: Path

# BAD: No RDF equivalent
arguments:
  - file: Path
    depends_on: other_arg  # Complex dependency - where does this go in RDF?
```

### Principle 5: Document Idioms

Show the patterns authors should follow:

```yaml
# ═══════════════════════════════════════════════════════════════
# IDIOM: File Processing Command
# Use this pattern for commands that read files and produce output
# ═══════════════════════════════════════════════════════════════
file_processor:
  description: Process input file(s)

  arguments:
    - name: input
      type: Path
      required: true
      help: Input file

  options:
    - name: --output
      short: -o
      type: Path
      help: Output file (stdout if not specified)

    - name: --format
      short: -f
      type: choice
      choices: [text, json, yaml]
      default: text
      help: Output format

    - name: --quiet
      short: -q
      type: bool
      help: Suppress non-error output
```

---

## Case Study: Command DSL Evolution

### Phase 1: Raw Turtle (Week 1)

Team starts with raw RDF. First command specification:

```turtle
cli:validate a cli:Command ;
    sk:name "validate" ;
    sk:description "Validate files" ;
    cli:hasArgument [
        a cli:Argument ;
        sk:name "file" ;
        cli:type "Path" ;
        cli:required true
    ] .
```

**Problem:** Takes 15 minutes to write, easy to make syntax errors.

### Phase 2: Templates (Week 2)

Team creates templates. Now copying and modifying:

```turtle
# Copied from template, modified placeholders
cli:generate a cli:Command ;
    sk:name "generate" ;
    sk:description "Generate artifacts" ;
    cli:hasArgument [
        a cli:Argument ;
        sk:name "spec" ;
        cli:type "Path" ;
        cli:required true
    ] .
```

**Improvement:** 5 minutes per command, fewer errors.
**Problem:** Still lots of boilerplate, easy to miss updating a placeholder.

### Phase 3: YAML DSL (Week 4)

Team adopts YAML DSL:

```yaml
generate:
  description: Generate artifacts
  arguments:
    - name: spec
      type: Path
      required: true
```

**Improvement:** 1 minute per command, near-zero errors.
**Problem:** Some complex commands need features not in DSL.

### Phase 4: Hybrid (Week 6)

Team uses DSL for common cases, raw Turtle for complex:

```yaml
commands:
  # Simple commands via DSL
  validate:
    description: Validate files
    arguments:
      - file: Path!

  # Complex command escapes to Turtle
  complex:
    raw_turtle: |
      :complex a cli:AdvancedCommand ;
          # ... complex structure
```

**Result:** Best of both worlds. Fast for common cases, full power when needed.

---

## Anti-Patterns to Avoid

### Anti-Pattern 1: DSL That Can't Express Edge Cases

```yaml
# DSL that's too limited
commands:
  validate:
    args: [file]  # Can't specify type, requirements, help...
```

**Problem:** Forces workarounds or escape hatches for basic needs.

### Anti-Pattern 2: DSL More Complex Than Target

```yaml
# DSL with more concepts than RDF
commands:
  validate:
    conditional_args:
      - if: format == "json"
        then_require: schema
```

**Problem:** DSL is harder to learn than just writing RDF.

### Anti-Pattern 3: No Validation

DSL that produces invalid RDF silently:

```python
# Bad: Generates whatever, no checking
def compile(yaml_str):
    data = yaml.load(yaml_str)
    return generate_turtle(data)  # Could be invalid!
```

**Problem:** Errors appear late, far from source.

### Anti-Pattern 4: Lost Semantics

DSL that doesn't preserve RDF's semantic richness:

```yaml
# Flat DSL loses graph structure
commands:
  validate:
    args: [file, shapes]
    opts: [strict, format]
# Where are types? Requirements? Relationships?
```

**Problem:** Generated RDF is impoverished.

---

## Implementation Checklist

### Choosing Your Approach

- [ ] Assess domain complexity and authoring frequency
- [ ] Survey team familiarity with RDF vs. preferred formats
- [ ] Identify common patterns that need simplification
- [ ] Determine escape hatch requirements

### Building the DSL

- [ ] Define syntax (YAML, custom, embedded)
- [ ] Implement parser/compiler
- [ ] Write comprehensive error messages
- [ ] Create test suite with known inputs/outputs
- [ ] Document all constructs with examples

### Integration

- [ ] Add to build pipeline (Makefile/CI)
- [ ] Validate generated RDF against shapes
- [ ] Preserve source line information for debugging
- [ ] Version the DSL spec alongside schema versions

### Documentation

- [ ] Quick-start guide for common tasks
- [ ] Reference for all DSL constructs
- [ ] Migration guide from raw RDF
- [ ] Escape hatch documentation

---

## Resulting Context

After applying this pattern, you have:

- **Reduced verbosity** for common operations
- **Familiar patterns** for domain authors
- **Valid RDF** that works with all standard tools
- **Flexibility** to use full RDF power when needed
- **Faster authoring** with fewer errors
- **Lower barrier** to entry for new team members

This supports author productivity while maintaining **[Semantic Foundation](./semantic-foundation.md)**.

---

## Related Patterns

- *Simplifies:* **[9. Semantic Foundation](./semantic-foundation.md)** — DSL makes RDF accessible
- *Enables:* **[18. Narrative Specification](./narrative-specification.md)** — DSL for embedding narrative
- *Complements:* **[12. Shape Constraint](./shape-constraint.md)** — DSL output validated by shapes
- *Supports:* **[23. Extraction Query](../transformation/extraction-query.md)** — DSL simplifies query patterns

---

## Philosophical Coda

> *"A language that doesn't affect the way you think about programming is not worth knowing."*
>
> — Alan Perlis

A domain-specific language, even a thin one over RDF, affects how you think about your domain. It encodes best practices, makes common tasks easy, and keeps the focus on content rather than syntax.

The DSL becomes a conversation between the domain and the computer—a shared vocabulary that both parties understand. When the conversation flows smoothly, productivity soars. When it stutters, so does progress.

Design your DSL to match how domain experts naturally express their knowledge, and the specifications will write themselves.

---

## Exercises

### Exercise 1: Pattern Identification

Review the raw Turtle specifications in your project. Identify:
1. The three most common structural patterns
2. Properties that are always used together
3. Values that follow predictable patterns

Design shorthand for each.

### Exercise 2: DSL Design

Design a YAML DSL for specifying JTBD outcomes. It should support:
- Direction (minimize/maximize)
- Metric
- Target value
- Current baseline
- Priority

### Exercise 3: Compiler Implementation

Implement a compiler that translates your YAML DSL to RDF/Turtle. Include:
- Validation of required fields
- Helpful error messages with line numbers
- Pretty-printed output with comments

### Exercise 4: Escape Hatch

Add an escape hatch to your DSL that allows embedding raw Turtle for cases the DSL can't handle. How do you validate the mixed result?

---

## Further Reading

- *Domain-Specific Languages* — Martin Fowler
- *Language Implementation Patterns* — Terence Parr
- *The Pragmatic Programmer* — On little languages
- *Structure and Interpretation of Computer Programs* — On embedded languages
- *YAML Ain't Markup Language* — YAML specification

