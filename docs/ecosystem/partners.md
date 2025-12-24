# Ecosystem Partners

Organizations and projects building on ggen spec-kit.

## Built-in Extensions

### Process Mining Support (pm4py)

**Project:** pm4py
**Type:** Process mining library
**Integration:** `specify pm` commands
**Features:**
- Discover process models from logs
- Conformance checking
- Performance analysis
- Bottleneck detection

**Use:** Analyze and optimize workflows

See: `/docs/commands/pm.md`

### Workflow Automation (SpiffWorkflow)

**Project:** SpiffWorkflow
**Type:** BPMN 2.0 workflow engine
**Integration:** `specify spiff` commands
**Features:**
- Execute BPMN workflows
- Human task management
- Parallel execution
- Process monitoring

**Use:** Automate business processes

See: `/docs/commands/spiff.md`

### Hyperdimensional Computing (HDC)

**Project:** Custom implementation
**Type:** Semantic computing engine
**Integration:** `specify hd` and `specify hdql` commands
**Features:**
- Semantic similarity search
- Analogical reasoning
- Knowledge representation
- Classification systems

**Use:** Semantic AI applications

See: `/docs/commands/hd.md`

## OpenTelemetry Ecosystem

### Jaeger

**Project:** jaegertracing/jaeger
**Type:** Distributed tracing
**Integration:** Automatic OTEL export
**Use:** Visualize execution traces

```bash
docker run -d -p 16686:16686 jaegertracing/all-in-one
export OTEL_EXPORTER_JAEGER_ENDPOINT=http://localhost:14250
```

### Prometheus

**Project:** prometheus/prometheus
**Type:** Metrics storage
**Integration:** OTEL metrics export
**Use:** Collect and alert on metrics

```bash
# Metrics automatically exported
curl http://localhost:8000/metrics
```

### Grafana

**Project:** grafana/grafana
**Type:** Visualization and dashboards
**Integration:** Query Prometheus
**Use:** Create dashboards

See: `/docs/guides/observability/setup-otel.md`

## Documentation Ecosystem

### Sphinx

**Project:** sphinx-doc/sphinx
**Type:** Documentation generator
**Use:** Build HTML documentation
**Integration:** Markdown to HTML conversion

### MkDocs

**Project:** mkdocs/mkdocs
**Type:** Project documentation tool
**Use:** Static site generation
**Integration:** Material theme support

### ReadTheDocs

**Project:** readthedocs/readthedocs.org
**Type:** Hosted documentation service
**Use:** Auto-deploy docs on push
**Integration:** GitHub integration

## Development Tools

### SPARQL Engines

| Project | License | Features |
|---------|---------|----------|
| Apache Jena | Apache 2.0 | Full SPARQL support |
| RDF4J | Eclipse | Java implementation |
| Virtuoso | Proprietary | Enterprise SPARQL |
| GraphDB | Proprietary | High performance |

### RDF Tools

**Protégé** - OWL/RDF ontology editor
**RDFtk** - RDF command-line toolkit
**rasqal** - SPARQL processor

### Tera Templates

**Project:** Keats/tera
**Type:** Jinja2-like template engine
**Use:** Code generation templates
**Integration:** Native support in ggen

## Code Quality

### Ruff

**Project:** astral-sh/ruff
**Type:** Python linter
**Use:** Static analysis
**Integration:** Pre-commit hooks

### Black

**Project:** psf/black
**Type:** Python formatter
**Use:** Code formatting
**Integration:** Automatic canonicalization

### MyPy

**Project:** python/mypy
**Type:** Static type checker
**Use:** Type safety
**Integration:** CI/CD validation

## Databases

### PostgreSQL

**Project:** postgres/postgres
**Type:** Relational database
**Use:** Store transformation logs
**Integration:** Optional logging backend

### SQLite

**Project:** sqlite/sqlite
**Type:** Embedded database
**Use:** Local development
**Integration:** Built-in dev database

### DuckDB

**Project:** duckdb/duckdb
**Type:** OLAP database
**Use:** Analyze metrics
**Integration:** Query transformation logs

## Cloud Providers

### AWS

**Services:**
- Lambda (serverless functions)
- S3 (storage)
- RDS (databases)
- ECS (container orchestration)

**Integration:** Deploy specify-cli on AWS

### Google Cloud

**Services:**
- Cloud Functions
- Cloud Run (containers)
- Firestore (database)
- BigQuery (analytics)

**Integration:** Deploy on GCP

### Azure

**Services:**
- Azure Functions
- Azure Container Instances
- Azure Database for PostgreSQL
- Application Insights (monitoring)

**Integration:** Deploy on Azure

## Collaboration Platforms

### GitHub

**Project:** github/github
**Type:** Git hosting + collaboration
**Use:** Repository hosting, CI/CD
**Integration:** Actions workflows

### GitLab

**Project:** gitlabhq/gitlabhq
**Type:** Git hosting + CI/CD
**Use:** Alternative to GitHub
**Integration:** GitLab CI pipelines

### Gitea

**Project:** go-gitea/gitea
**Type:** Lightweight Git service
**Use:** Self-hosted Git
**Integration:** Custom CI/CD

## Research & Academia

### Academic Projects Using Specify

**Institutions:**
- [To be filled with actual institutions]

**Research Areas:**
- RDF-first software development
- Specification-driven code generation
- Automated testing from specs
- Semantic web applications

## Community

### Discord Community

**Invite:** [To be added]
**Topics:** Help, ideas, announcements

### GitHub Discussions

**Location:** github.com/anthropics/ggen-spec-kit/discussions
**Topics:** Feature requests, Q&A, sharing

### Stack Overflow

**Tag:** [ggen-spec-kit]
**Use:** Answer questions

## Contributing Partners

Organizations contributing code, documentation, or bug reports:

- [To be filled with contributor list]

## Integration Request

Want to integrate with specify-kit?

1. **Review** integration options at `/docs/ecosystem/integrations.md`
2. **Create** issue on GitHub: "Integration request: [your tool]"
3. **Discuss** approach with maintainers
4. **Implement** integration
5. **Document** in this file and in integration guide

## See Also

- `integrations.md` - How to integrate tools
- `/docs/guides/deployment/` - Deployment guides
- `/docs/ecosystem/agi-ingestion.md` - AI integration
