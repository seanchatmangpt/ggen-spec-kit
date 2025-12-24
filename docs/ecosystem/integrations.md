# Ecosystem Integrations

Integration points and third-party tool support for ggen spec-kit.

## RDF & Semantic Web Tools

### OpenRDF/Eclipse RDF4J

**Use:** RDF manipulation, SPARQL execution
**Integration:** Drop-in replacement for queries

```bash
# Use RDF4J for complex queries
java -jar rdf4j-server.jar

# Query spec-kit ontology
PREFIX sk: <http://ggen-spec-kit.org/>
SELECT ?command WHERE {
  ?command a sk:Command ;
  rdfs:label ?name .
}
```

### SPARQL Endpoints

**Use:** Query ontology as service
**Integration:** Public SPARQL endpoint for ontology

```bash
# Query public endpoint
curl "https://ontology.ggen-spec-kit.org/sparql?query=..."
```

### OWL & Protégé

**Use:** Ontology development and visualization
**Integration:** Export ontology to OWL format

```bash
# Convert TTL to OWL
rdfcat ontology/spec-kit-schema.ttl -out owl > schema.owl

# Open in Protégé for visual editing
open schema.owl
```

## Transformation Tools

### Apache Jena

**Use:** RDF processing, fusion
**Integration:** Use Jena for complex transformations

```bash
# Process RDF with Jena
sparql --data ontology/cli-commands.ttl \
        --query sparql/command-extract.rq
```

### Fuseki (SPARQL Server)

**Use:** Host ontology as SPARQL service
**Integration:** Deploy semantic API

```bash
# Start Fuseki server
fuseki-server --mem /ggen-spec-kit

# Accessible at http://localhost:3030/ggen-spec-kit
curl -X GET "http://localhost:3030/ggen-spec-kit/sparql?query=..."
```

## Observability & Monitoring

### OpenTelemetry Exporters

**Supported:** Jaeger, Prometheus, OTLP, Zipkin

```toml
[telemetry]
# Jaeger
exporter = "jaeger"
jaeger_endpoint = "http://localhost:14250"

# Or Prometheus
exporter = "prometheus"
prometheus_port = 8000

# Or OTLP
exporter = "otlp"
otlp_endpoint = "http://localhost:4317"
```

### Prometheus

**Use:** Metrics collection and storage
**Integration:** Automatic metric export

```bash
# Query metrics
curl http://localhost:9090/api/v1/query?query=ggen_sync_duration_ms

# Set up alerts
groups:
  - name: ggen
    rules:
      - alert: SlowGgenSync
        expr: avg(ggen_sync_duration_ms) > 5000
        for: 5m
```

### Grafana

**Use:** Dashboards and visualization
**Integration:** Query Prometheus for metrics

```yaml
# Grafana dashboard for ggen metrics
datasources:
  - name: Prometheus
    url: http://localhost:9090

dashboards:
  - ggen-performance.json
```

### Jaeger

**Use:** Distributed tracing
**Integration:** OTEL export, trace analysis

```bash
# View traces
open http://localhost:16686

# Query traces
curl http://localhost:16686/api/traces?service=specify-cli
```

## Code Generation & Development

### Tera Template Engine

**Use:** Code generation templates
**Integration:** Native support in ggen

```tera
{# Custom code generation template #}
{% for cmd in commands %}
def {{ cmd.name }}():
    """{{ cmd.description }}"""
    pass
{% endfor %}
```

### Black Code Formatter

**Use:** Format generated Python code
**Integration:** Automatic canonicalization

```bash
# Formats are automatically applied during μ₄
black src/

# Configuration in pyproject.toml
[tool.black]
line-length = 88
```

### MyPy Type Checker

**Use:** Static type checking
**Integration:** Pre-commit validation

```bash
mypy src/specify_cli/ --strict
```

## Database & Storage

### PostgreSQL

**Use:** Store transformation logs, metrics
**Integration:** Optional logging backend

```python
from specify_cli.runtime.database import get_session

session = get_session()
log = TransformLog(
    rdf_source="ontology/cli-commands.ttl",
    timestamp=datetime.now(),
    status="success"
)
session.add(log)
session.commit()
```

### SQLite

**Use:** Local development logging
**Integration:** Built-in dev database

```bash
# Development uses SQLite
.ggen/ggen.db

# Query logs
sqlite3 .ggen/ggen.db "SELECT * FROM transform_logs;"
```

### DuckDB

**Use:** Analyze transformation metrics
**Integration:** OLAP queries on logs

```sql
SELECT
  date_trunc('hour', timestamp) as hour,
  COUNT(*) as syncs,
  AVG(duration_ms) as avg_duration,
  MAX(duration_ms) as max_duration
FROM ggen_logs
GROUP BY 1
ORDER BY 1 DESC
```

## CI/CD Integration

### GitHub Actions

**Use:** Automated testing and deployment
**Integration:** Built-in workflow examples

```yaml
name: Verify Spec Sync

on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: ggen sync
      - run: git diff --exit-code
      - run: pytest tests/
```

### GitLab CI

**Use:** Alternative CI/CD platform
**Integration:** Docker images available

```yaml
test:
  image: specify-cli:latest
  script:
    - ggen sync
    - pytest tests/
```

### Jenkins

**Use:** Enterprise CI/CD
**Integration:** Trigger via webhooks

```groovy
pipeline {
    agent any
    stages {
        stage('Verify') {
            steps {
                sh 'ggen sync'
                sh 'pytest tests/'
            }
        }
    }
}
```

## Documentation

### Sphinx

**Use:** Generate documentation
**Integration:** Convert markdown to HTML

```bash
sphinx-build -b html docs/ _build/
```

### MkDocs

**Use:** Project documentation site
**Integration:** Markdown-based docs

```yaml
site_name: ggen Spec Kit
docs_dir: docs/
theme: material
plugins:
  - search
```

### ReadTheDocs

**Use:** Hosted documentation
**Integration:** Auto-build from GitHub

```toml
[build]
os: ubuntu-20.04
python: "3.11"
```

## Process Mining

### pm4py

**Use:** Process mining and discovery
**Integration:** Analyze execution traces

```python
from pm4py.objects.log.importer.xes import importer as xes_importer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

log = xes_importer.apply("traces.xes")
net, im, fm = inductive_miner.apply(log)
```

### Disco (Fluxicon)

**Use:** Visual process analysis
**Integration:** Import XES logs

```bash
# Export traces for Disco
specify spiff export-log workflow-123 --output traces.xes

# Open in Disco for visualization
open traces.xes  # Opens in Disco
```

## Workflow Engine

### Apache Airflow

**Use:** Orchestrate complex workflows
**Integration:** Generate Airflow DAGs from specs

```python
from airflow import DAG
from specify_cli.runtime.workflow import generate_dag

dag = generate_dag(
    "ontology/workflows.ttl",
    default_owner="airflow"
)
```

### Prefect

**Use:** Modern workflow orchestration
**Integration:** Trigger from spec-kit tasks

```python
from prefect import flow, task
from specify_cli import ops

@flow
def data_pipeline():
    data = ops.read_data()
    validated = ops.validate(data)
    return ops.save(validated)
```

## Machine Learning

### PyTorch/TensorFlow

**Use:** ML model integration
**Integration:** Call models from operations

```python
# In ops/ml_ops.py
import torch

def classify_data(data):
    """Use ML model for classification"""
    model = torch.load("models/classifier.pt")
    return model.predict(data)
```

## Cloud Platforms

### AWS Integration

**Use:** Deploy to AWS
**Integration:** S3, Lambda, RDS

```bash
# Deploy to Lambda
zip -r package.zip src/
aws lambda create-function \
  --function-name specify-cli \
  --runtime python3.11 \
  --zip-file fileb://package.zip
```

### Google Cloud

**Use:** GCP deployment
**Integration:** Cloud Functions, Cloud Run

```dockerfile
FROM python:3.11
RUN pip install ggen-spec-kit
ENTRYPOINT ["specify"]
CMD ["--help"]
```

### Azure

**Use:** Azure deployment
**Integration:** Azure Functions

```json
{
  "scriptFile": "run.py",
  "bindings": [
    {
      "type": "httpTrigger",
      "name": "req",
      "direction": "in"
    }
  ]
}
```

## Communication & Notifications

### Slack

**Use:** Notifications on events
**Integration:** Send alerts to Slack

```python
from specify_cli.runtime.notifications import send_slack

send_slack(
    webhook_url="https://hooks.slack.com/...",
    message="ggen sync completed",
    channel="#builds"
)
```

### Email

**Use:** Send reports
**Integration:** Built-in email notifications

```toml
[notifications]
email_enabled = true
smtp_server = "smtp.example.com"
smtp_port = 587
recipients = ["team@example.com"]
```

## API Gateways

### Kong

**Use:** API management and rate limiting
**Integration:** Expose SPARQL endpoints via Kong

```bash
curl -X POST http://localhost:8001/apis \
  -d "name=ggen-api" \
  -d "upstream_url=http://localhost:3030/ggen-spec-kit"
```

### AWS API Gateway

**Use:** Serverless API
**Integration:** Route requests to Lambda functions

```bash
aws apigateway create-rest-api \
  --name ggen-api
```

## See Also

- `partners.md` - Ecosystem partners
- `/docs/ecosystem/agi-ingestion.md` - AI agent integration
- `/docs/guides/deployment/` - Deployment guides
