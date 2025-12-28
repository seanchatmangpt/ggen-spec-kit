# Architecture Decision Records

## ADR-001: Three-Tier Architecture

### Status
Accepted

### Context
Need clear separation between CLI, business logic, and I/O operations for testability and maintainability.

### Decision
Implement three-tier architecture:
- **Commands**: Typer CLI, Rich formatting only
- **Operations**: Pure functions, return dicts
- **Runtime**: All subprocess, file I/O, HTTP

### Consequences
- High testability (ops layer is pure)
- Clear boundaries prevent side-effect leakage
- Slight overhead in layer separation

---

## ADR-002: RDF as Source of Truth

### Status
Accepted

### Context
Need a specification-driven approach where code is generated from specifications.

### Decision
Use RDF/Turtle files as the source of truth. Implement the constitutional equation: `spec.md = μ(feature.ttl)`

### Consequences
- Single source of truth in RDF
- Generated code is a build artifact
- Requires discipline not to edit generated files
- Enables idempotent transformations

---

## ADR-003: OpenTelemetry Instrumentation

### Status
Accepted

### Context
Need observability for CLI operations and debugging.

### Decision
Use OpenTelemetry with graceful degradation when OTEL is unavailable.

### Consequences
- Full tracing when OTEL configured
- Zero overhead when disabled
- Consistent instrumentation patterns

---

## ADR-004: No shell=True

### Status
Accepted

### Context
Security requirement to prevent command injection.

### Decision
Never use `shell=True` in subprocess calls. Always use list-based command construction.

### Consequences
- Prevents command injection
- Slightly more verbose command construction
- Safer execution model
