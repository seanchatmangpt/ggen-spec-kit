# Explanation: RDF-First Development

**Time to understand:** 15-20 minutes

## Why RDF First?

Traditional development:
```
Write code → Write docs → Hope they stay in sync ❌
```

RDF-first development:
```
Write RDF specs → Generate code + docs ✅ (always in sync)
```

## What is RDF?

RDF = Resource Description Framework

It's a **semantic data format** that describes things and their relationships:

```turtle
sk:hello
    a sk:Command ;          # "hello" is a Command
    rdfs:label "hello" ;    # Its name is "hello"
    sk:description "..." .  # It does this thing
```

### Key Benefits

1. **Machine-Readable**
   - Computers can parse and understand it
   - Can be queried with SPARQL
   - Can be validated with SHACL

2. **Semantic**
   - Explicit meaning (not ambiguous)
   - Relationships are clear
   - Can be reasoned over

3. **Verifiable**
   - Can prove claims with proofs
   - Can detect violations
   - Can be validated formally

## Why Specs Should be RDF

### Traditional Specs (Natural Language)

```markdown
# User Login

The user can log in by providing username and password.
If login fails, show an error message.
The system should timeout after 3 attempts.
```

**Problems:**
- ❌ Ambiguous ("show error" - where? how?)
- ❌ Not machine-executable
- ❌ Drift between spec and code
- ❌ Can't verify conformance

### RDF Specs (Formal)

```turtle
spec:UserLogin
    a spec:Feature ;
    spec:requires spec:UsernameArg, spec:PasswordArg ;
    spec:validates [
        spec:condition "attempts < 3" ;
        spec:then spec:AllowLogin ;
        spec:else spec:TimeoutError
    ] .
```

**Benefits:**
- ✅ Unambiguous (formal definition)
- ✅ Machine-executable
- ✅ Can auto-generate code
- ✅ Can verify with SPARQL

## The Transformation

```
RDF Spec (source of truth)
    ↓
ggen transformation (deterministic)
    ↓
Code + Tests + Docs (always in sync)
```

Because code is **generated from specs**, they **cannot diverge**.

## From Spec to Code

1. **Write RDF**
   ```turtle
   sk:hello a sk:Command ;
       rdfs:label "hello" ;
       sk:description "Greet user" .
   ```

2. **Generate Code**
   ```bash
   ggen sync
   ```

3. **Generated Python**
   ```python
   @app.command()
   def hello():
       """Greet user"""
       pass
   ```

4. **Implement Logic**
   ```python
   def hello():
       return "Hello, World!"
   ```

## Why This Works

**RDF forces explicit specification:**
- What is the command? (`a sk:Command`)
- What is its name? (`rdfs:label "hello"`)
- What does it do? (`sk:description "..."`)
- What are its arguments? (`sk:hasArgument [...]`)
- What code module implements it? (`sk:hasModule "..."`)

**No ambiguity, no room for interpretation.**

**Code generation fills in the rest:**
- CLI argument parsing
- Error handling
- Help text
- Documentation

## Benefits

### For Developers
- ✅ Write specs, code generates automatically
- ✅ No manual boilerplate
- ✅ Focus on business logic
- ✅ Tests are auto-generated
- ✅ Documentation is current

### For Code Quality
- ✅ Perfect spec-code-doc sync
- ✅ No drift possible
- ✅ Verifiable transformations
- ✅ Can catch errors early
- ✅ Can prevent bad specs

### For Teams
- ✅ Single source of truth (RDF)
- ✅ Clear contracts (specs)
- ✅ Automated integration
- ✅ Easy onboarding
- ✅ Consistent patterns

## See Also
- [Explanation: Constitutional Equation](./constitutional-equation.md)
- [Explanation: Three-Tier Architecture](./three-tier-architecture.md)
- [Tutorial 1: Getting Started](../tutorials/01-getting-started.md)
