# ==============================================================================
# Multi-stage Dockerfile for specify-cli
# Optimized for security, performance, and minimal image size
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Base Builder - Install system dependencies and build tools
# ------------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS base-builder

# Security: Run as non-root user
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG APP_USER=specify
ARG APP_GROUP=specify

# Install system dependencies and security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        git \
        build-essential \
        libssl-dev \
        pkg-config \
        && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Create non-root user and group
RUN groupadd -g ${GROUP_ID} ${APP_GROUP} && \
    useradd -m -u ${USER_ID} -g ${APP_GROUP} -s /bin/bash ${APP_USER}

# Install uv (fast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# ------------------------------------------------------------------------------
# Stage 2: Rust Builder - Build ggen from source
# ------------------------------------------------------------------------------
FROM rust:1.75-slim-bookworm AS rust-builder

# Install system dependencies for Rust build
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libssl-dev \
        pkg-config \
        && \
    rm -rf /var/lib/apt/lists/*

# Build ggen (RDF-first code generation engine)
WORKDIR /build
RUN cargo install ggen-cli-lib --version 5.0.2 --locked

# ------------------------------------------------------------------------------
# Stage 3: Python Builder - Install Python dependencies
# ------------------------------------------------------------------------------
FROM base-builder AS python-builder

# Set working directory
WORKDIR /build

# Copy uv configuration and lock files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv (much faster than pip)
RUN /root/.cargo/bin/uv sync --frozen --no-dev

# Install optional dependencies (all groups)
RUN /root/.cargo/bin/uv sync --frozen --group all

# Copy source code
COPY src/ ./src/
COPY ontology/ ./ontology/
COPY memory/ ./memory/
COPY sparql/ ./sparql/
COPY templates/ ./templates/
COPY schema/ ./schema/
COPY README.md ./

# Build the package
RUN /root/.cargo/bin/uv build

# ------------------------------------------------------------------------------
# Stage 4: Runtime - Minimal production image
# ------------------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS runtime

# Metadata labels
LABEL maintainer="Sean Chatman <info@chatmangpt.com>"
LABEL version="0.0.25"
LABEL description="Specify CLI: RDF-first Spec-Driven Development toolkit"
LABEL org.opencontainers.image.source="https://github.com/github/spec-kit"
LABEL org.opencontainers.image.licenses="MIT"

# Security: Run as non-root user
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG APP_USER=specify
ARG APP_GROUP=specify

# Install minimal runtime dependencies
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        git \
        curl \
        && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean

# Create non-root user and group
RUN groupadd -g ${GROUP_ID} ${APP_GROUP} && \
    useradd -m -u ${USER_ID} -g ${APP_GROUP} -s /bin/bash ${APP_USER}

# Copy ggen binary from rust-builder
COPY --from=rust-builder /usr/local/cargo/bin/ggen /usr/local/bin/ggen

# Copy Python virtual environment from python-builder
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/.venv /app/.venv

# Copy application files
WORKDIR /app
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/src ./src
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/ontology ./ontology
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/memory ./memory
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/sparql ./sparql
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/templates ./templates
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/schema ./schema
COPY --from=python-builder --chown=${APP_USER}:${APP_GROUP} /build/pyproject.toml ./

# Set PATH to include virtual environment
ENV PATH="/app/.venv/bin:${PATH}"
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# Security: Remove setuid/setgid bits from all files
RUN find / -xdev -perm /6000 -type f -exec chmod a-s {} \; 2>/dev/null || true

# Security: Ensure proper permissions
RUN chown -R ${APP_USER}:${APP_GROUP} /app && \
    chmod -R 755 /app

# Switch to non-root user
USER ${APP_USER}

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD specify --version || exit 1

# Liveness probe endpoint (for Kubernetes)
EXPOSE 8080

# Set default command
CMD ["specify", "--help"]

# ------------------------------------------------------------------------------
# Stage 5: Development - Include dev dependencies and tools
# ------------------------------------------------------------------------------
FROM runtime AS development

USER root

# Install development dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        vim \
        less \
        procps \
        && \
    rm -rf /var/lib/apt/lists/*

# Copy dev dependencies
COPY --from=python-builder /build/.venv /app/.venv

USER ${APP_USER}

# Install pre-commit hooks
RUN git config --global --add safe.directory /app

CMD ["/bin/bash"]

# ------------------------------------------------------------------------------
# Stage 6: Testing - Include test dependencies
# ------------------------------------------------------------------------------
FROM development AS testing

USER root

# Copy test files
COPY --chown=${APP_USER}:${APP_GROUP} tests/ ./tests/
COPY --chown=${APP_USER}:${APP_GROUP} pyproject.toml ./

USER ${APP_USER}

# Run tests by default
CMD ["pytest", "tests/", "-v", "--cov=src/specify_cli"]
