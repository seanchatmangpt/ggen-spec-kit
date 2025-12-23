# Reference: Environment Variables

Configuration via environment variables.

## OpenTelemetry

```bash
# OTEL SDK endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"

# Service name
export OTEL_SERVICE_NAME="specify-cli"

# Protocol: grpc or http/protobuf
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"

# Enable/disable
export OTEL_SDK_DISABLED="false"
```

## Python

```bash
# Python path
export PYTHONPATH="src/:$PYTHONPATH"

# Unbuffered output
export PYTHONUNBUFFERED=1
```

## Project

```bash
# Project root
export SPEC_KIT_ROOT="/path/to/project"

# Development mode
export SPEC_KIT_DEV="true"
```

## CI/CD

```bash
# CI environment
export CI="true"

# Build ID
export BUILD_ID="123"
```

## Usage

```bash
# Set and run
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
specify wf validate

# Or inline
OTEL_SDK_DISABLED=true pytest tests/
```
