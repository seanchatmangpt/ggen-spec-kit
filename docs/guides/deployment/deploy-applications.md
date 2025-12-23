# How-to: Deploy Spec Kit Applications

**Goal:** Deploy generated applications to production
**Time:** 30-40 minutes | **Level:** Advanced

## Build Artifacts

Generate wheels:

```bash
uv run build
```

Creates:
- `dist/specify_cli-*.whl` (binary wheel)
- `dist/specify_cli-*.tar.gz` (source)

## Install

### From PyPI
```bash
pip install specify-cli
specify --version
```

### From Wheel
```bash
pip install dist/specify_cli-*.whl
```

### Development Install
```bash
pip install -e .
```

## Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY . .
RUN pip install uv && uv sync --no-dev

ENTRYPOINT ["uv", "run", "specify"]
```

Build and run:
```bash
docker build -t specify:latest .
docker run specify:latest --version
```

## Kubernetes

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: specify
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: specify
        image: specify:latest
        env:
        - name: OTEL_EXPORTER_OTLP_ENDPOINT
          value: "http://otel-collector:4317"
```

Deploy:
```bash
kubectl apply -f deployment.yaml
```

## Monitoring

Enable OTEL for production:

```bash
OTEL_EXPORTER_OTLP_ENDPOINT="https://otel.prod.example.com:4317" \
specify wf validate
```

View traces in observability platform.

## Rollback

Keep versions:
```bash
pip install specify-cli==0.0.24  # Rollback to previous
```

## See Also
- [How-to: Setup CI/CD](./setup-ci-cd.md)
- [How-to: Setup OTEL](../observability/setup-otel.md)
