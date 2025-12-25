# Deployment Guide - Specify CLI

Complete deployment automation infrastructure for the Specify CLI using Docker, Kubernetes, and GitOps.

## Table of Contents

- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Helm Deployment](#helm-deployment)
- [GitOps Deployment](#gitops-deployment)
- [CI/CD Pipeline](#cicd-pipeline)
- [Monitoring & Observability](#monitoring--observability)
- [Scaling & High Availability](#scaling--high-availability)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Quick Start

### Prerequisites

- Docker 24.0+ and Docker Compose 2.0+
- Kubernetes 1.28+
- Helm 3.13+
- kubectl 1.29+
- (Optional) Flux CD or Argo CD for GitOps

### 1. Docker Compose (Local Development)

```bash
# Start development stack
cd deployment
docker-compose -f docker-compose.dev.yml up -d

# Check status
docker-compose -f docker-compose.dev.yml ps

# View logs
docker-compose -f docker-compose.dev.yml logs -f specify-cli-dev

# Stop stack
docker-compose -f docker-compose.dev.yml down
```

### 2. Kubernetes (Production)

```bash
# Create namespace
kubectl create namespace specify

# Apply manifests
kubectl apply -f ../k8s/

# Check deployment
kubectl get all -n specify
kubectl rollout status deployment/specify-cli -n specify
```

### 3. Helm (Recommended)

```bash
# Install with default values
helm install specify ./helm/ --namespace specify --create-namespace

# Install with custom values (production)
helm install specify ./helm/ \
  --namespace specify \
  --create-namespace \
  --values ./helm/values-production.yaml

# Upgrade
helm upgrade specify ./helm/ --namespace specify

# Uninstall
helm uninstall specify --namespace specify
```

## Docker Deployment

### Architecture

The multi-stage Dockerfile provides optimized builds:

1. **base-builder** - System dependencies and tools
2. **rust-builder** - Builds ggen from source
3. **python-builder** - Python dependencies and app build
4. **runtime** - Minimal production image (~300MB)
5. **development** - Development tools included
6. **testing** - Test runner with test dependencies

### Building Images

```bash
# Build production image
docker build -f deployment/Dockerfile -t specify-cli:latest --target runtime .

# Build development image
docker build -f deployment/Dockerfile -t specify-cli:dev --target development .

# Build testing image
docker build -f deployment/Dockerfile -t specify-cli:test --target testing .

# Multi-platform build (ARM + AMD64)
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -f deployment/Dockerfile \
  -t specify-cli:latest \
  --target runtime \
  --push .
```

### Running Containers

```bash
# Run interactively
docker run -it --rm specify-cli:latest specify --help

# Run with environment variables
docker run -it --rm \
  -e LOG_LEVEL=DEBUG \
  -e DATABASE_URL=postgresql://user:pass@host/db \
  specify-cli:latest

# Run with volume mounts
docker run -it --rm \
  -v $(pwd)/data:/app/data \
  specify-cli:latest
```

### Docker Compose Stacks

#### Development Stack

```bash
# Start development environment
docker-compose -f deployment/docker-compose.dev.yml up -d

# Access development container
docker exec -it specify-cli-dev /bin/bash

# Run tests
docker exec -it specify-cli-dev pytest tests/ -v
```

#### Production Stack

```bash
# Start full production stack (with monitoring)
docker-compose -f deployment/docker-compose.yml up -d

# Scale application
docker-compose -f deployment/docker-compose.yml up -d --scale specify-cli=3

# View monitoring dashboards
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - Jaeger: http://localhost:16686
# - Kibana: http://localhost:5601
```

## Kubernetes Deployment

### Manual Deployment

```bash
# 1. Create namespace
kubectl create namespace specify

# 2. Create secrets (update values first!)
kubectl apply -f ../k8s/secret.yaml

# 3. Create ConfigMap
kubectl apply -f ../k8s/configmap.yaml

# 4. Create ServiceAccount and RBAC
kubectl apply -f ../k8s/serviceaccount.yaml

# 5. Create PersistentVolumeClaim
kubectl apply -f ../k8s/pvc.yaml

# 6. Deploy application
kubectl apply -f ../k8s/deployment.yaml

# 7. Create Service
kubectl apply -f ../k8s/service.yaml

# 8. Create Ingress (update domain first!)
kubectl apply -f ../k8s/ingress.yaml

# 9. Setup autoscaling
kubectl apply -f ../k8s/hpa.yaml

# 10. Setup pod disruption budget
kubectl apply -f ../k8s/pdb.yaml

# 11. Setup network policies
kubectl apply -f ../k8s/networkpolicy.yaml

# 12. Setup monitoring (if Prometheus Operator installed)
kubectl apply -f ../k8s/servicemonitor.yaml
```

### Verification

```bash
# Check all resources
kubectl get all -n specify

# Check pod status
kubectl get pods -n specify -o wide

# Check logs
kubectl logs -n specify -l app.kubernetes.io/name=specify -f

# Check events
kubectl get events -n specify --sort-by='.lastTimestamp'

# Check HPA status
kubectl get hpa -n specify

# Exec into pod
kubectl exec -it -n specify deployment/specify-cli -- /bin/bash
```

## Helm Deployment

### Installation

```bash
# Add dependencies (if using external charts)
helm dependency update ./helm/

# Install with default values
helm install specify ./helm/ \
  --namespace specify \
  --create-namespace

# Install with custom values
helm install specify ./helm/ \
  --namespace specify \
  --create-namespace \
  --values ./helm/values-production.yaml \
  --set image.tag=0.0.25 \
  --set ingress.hosts[0].host=specify.example.com

# Dry-run to preview
helm install specify ./helm/ \
  --namespace specify \
  --dry-run \
  --debug
```

### Management

```bash
# Upgrade release
helm upgrade specify ./helm/ \
  --namespace specify \
  --values ./helm/values-production.yaml

# Rollback to previous version
helm rollback specify -n specify

# Check history
helm history specify -n specify

# Get values
helm get values specify -n specify

# Uninstall
helm uninstall specify -n specify
```

### Environment-Specific Deployments

```bash
# Development
helm install specify-dev ./helm/ \
  --namespace specify-dev \
  --create-namespace \
  --values ./helm/values.yaml \
  --set env.ENVIRONMENT=development

# Staging
helm install specify-staging ./helm/ \
  --namespace specify-staging \
  --create-namespace \
  --values ./helm/values-staging.yaml

# Production
helm install specify ./helm/ \
  --namespace specify \
  --create-namespace \
  --values ./helm/values-production.yaml
```

## GitOps Deployment

### Flux CD

```bash
# 1. Install Flux
flux install

# 2. Bootstrap repository
flux bootstrap github \
  --owner=github \
  --repository=spec-kit \
  --branch=main \
  --path=./deployment/gitops/flux

# 3. Create source
kubectl apply -f deployment/gitops/flux/gitrepository.yaml

# 4. Create Kustomization
kubectl apply -f deployment/gitops/flux/kustomization.yaml

# 5. Create HelmRelease
kubectl apply -f deployment/gitops/flux/helmrelease.yaml

# Check reconciliation
flux get all
flux logs --all-namespaces
```

### Argo CD

```bash
# 1. Install Argo CD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 2. Access Argo CD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 3. Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# 4. Create application
kubectl apply -f deployment/gitops/argocd/application.yaml

# 5. Create ApplicationSet (multi-environment)
kubectl apply -f deployment/gitops/argocd/applicationset.yaml

# Check status
argocd app list
argocd app get specify-cli
argocd app sync specify-cli
```

## CI/CD Pipeline

### GitHub Actions Workflows

Three automated workflows are configured:

#### 1. Docker Build (`docker-build.yml`)

Triggers:
- Push to main, develop, or release branches
- Tags matching `v*.*.*`
- Manual dispatch

Features:
- Multi-platform builds (AMD64 + ARM64)
- Security scanning with Trivy
- Automated testing
- Push to GitHub Container Registry
- Release creation on tags

#### 2. Kubernetes Deploy (`k8s-deploy.yml`)

Triggers:
- Push to main/develop (changes to k8s/ or helm/)
- Manual dispatch with environment selection

Features:
- Manifest validation
- Multi-environment deployments (dev/staging/prod)
- Blue-green deployments for production
- Automated smoke tests
- Rollback on failure

#### 3. Helm Release (`helm-release.yml`)

Triggers:
- Push to main (changes to helm/)
- Release published
- Manual dispatch

Features:
- Chart linting with chart-testing
- Package and publish to GHCR
- Update Helm repository index
- Artifact Hub integration

### Running Workflows

```bash
# Trigger manual deployment
gh workflow run k8s-deploy.yml \
  -f environment=production \
  -f version=0.0.25

# Check workflow status
gh run list --workflow=docker-build.yml

# View logs
gh run view --log
```

## Monitoring & Observability

### Stack Components

- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards
- **Jaeger** - Distributed tracing
- **Elasticsearch** - Log storage
- **Kibana** - Log visualization
- **Logstash** - Log processing

### Access Dashboards

```bash
# Port-forward to access locally
kubectl port-forward -n specify svc/grafana 3000:3000
kubectl port-forward -n specify svc/prometheus 9090:9090
kubectl port-forward -n specify svc/jaeger 16686:16686
kubectl port-forward -n specify svc/kibana 5601:5601
```

Default credentials:
- Grafana: admin/admin
- Kibana: elastic/changeme

### Key Metrics

- **Request rate**: `rate(http_requests_total{job="specify-cli"}[5m])`
- **Error rate**: `rate(http_requests_total{status=~"5.."}[5m])`
- **Response time (p95)**: `histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))`
- **CPU usage**: `rate(process_cpu_seconds_total[5m]) * 100`
- **Memory usage**: `process_resident_memory_bytes / 1024 / 1024`

### Alerts

Critical alerts configured:
- Instance down > 5 minutes
- High error rate > 5%
- High response time > 1s (p95)
- Database connection failures
- High CPU/memory usage

## Scaling & High Availability

### Horizontal Scaling

```bash
# Manual scaling
kubectl scale deployment specify-cli -n specify --replicas=5

# Check autoscaling
kubectl get hpa -n specify
kubectl describe hpa specify-hpa -n specify
```

### Vertical Scaling

Update resource limits in values.yaml:

```yaml
resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi
```

### High Availability Features

- **3+ replicas** minimum for production
- **Pod anti-affinity** spreads pods across nodes
- **PodDisruptionBudget** ensures minimum availability
- **Rolling updates** with zero downtime
- **Health checks** (liveness, readiness, startup probes)
- **Blue-green deployments** for production
- **Multi-region** support via GitOps

## Security

### Security Features

1. **Container Security**
   - Non-root user (UID 1000)
   - Read-only root filesystem
   - No setuid/setgid binaries
   - Dropped ALL capabilities
   - seccomp profile

2. **Network Security**
   - NetworkPolicies restrict traffic
   - TLS/SSL enforced via Ingress
   - Rate limiting configured
   - CORS policies

3. **Secret Management**
   - Kubernetes Secrets
   - External secret management supported
   - SOPS encryption for GitOps

4. **Image Security**
   - Multi-stage builds minimize attack surface
   - Trivy security scanning in CI
   - Signed images (optional)
   - Regular base image updates

### Best Practices

```bash
# Use external secret management (production)
kubectl apply -f external-secrets.yaml

# Enable Pod Security Standards
kubectl label namespace specify pod-security.kubernetes.io/enforce=restricted

# Scan images
trivy image specify-cli:latest

# Check for vulnerabilities
kubectl auth can-i --list
```

## Troubleshooting

### Common Issues

#### Pod CrashLoopBackOff

```bash
# Check logs
kubectl logs -n specify -l app.kubernetes.io/name=specify --tail=100

# Describe pod
kubectl describe pod -n specify <pod-name>

# Check events
kubectl get events -n specify --sort-by='.lastTimestamp'
```

#### Image Pull Errors

```bash
# Check image pull secrets
kubectl get secrets -n specify

# Verify image exists
docker pull ghcr.io/github/spec-kit:0.0.25

# Check registry credentials
kubectl describe secret specify-image-pull-secret -n specify
```

#### Database Connection Issues

```bash
# Test database connectivity
kubectl run -it --rm debug --image=postgres:16 --restart=Never -- psql -h postgres-service -U specify

# Check database pod
kubectl logs -n specify postgres-0

# Verify secrets
kubectl get secret specify-secret -n specify -o yaml
```

#### High Memory/CPU Usage

```bash
# Check resource usage
kubectl top pods -n specify
kubectl top nodes

# Check HPA status
kubectl get hpa -n specify

# Review metrics
kubectl port-forward -n specify svc/prometheus 9090:9090
# Visit http://localhost:9090
```

### Debug Commands

```bash
# Execute commands in pod
kubectl exec -it -n specify deployment/specify-cli -- specify --version

# Port forward to pod
kubectl port-forward -n specify deployment/specify-cli 8080:8080

# Copy files from pod
kubectl cp specify/specify-cli-xxx:/app/data ./local-data

# Run debug container
kubectl debug -it specify-cli-xxx --image=busybox --target=specify-cli

# Check DNS
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup specify-service
```

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Flux CD Documentation](https://fluxcd.io/docs/)
- [Argo CD Documentation](https://argo-cd.readthedocs.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

## Support

For issues and questions:
- GitHub Issues: https://github.com/github/spec-kit/issues
- Documentation: https://github.com/github/spec-kit#readme
