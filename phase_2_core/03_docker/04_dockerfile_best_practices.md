# Dockerfile Best Practices

## Why This Matters in DevOps

A Dockerfile is not just a build script -- it is a security boundary, a performance specification, and a production contract. Every Dockerfile you write ends up running in production, and the choices you make in it determine your image size, build speed, runtime security, and vulnerability exposure.

In a DevOps pipeline, Dockerfiles are built hundreds of times per day. A poorly optimized Dockerfile that takes 10 minutes to build instead of 30 seconds wastes hours of developer time and compute resources daily. An image running as root with unnecessary packages is a security incident waiting to happen. A Dockerfile without a health check produces containers that Kubernetes cannot monitor.

These best practices are not optional refinements -- they are the difference between production-grade images and prototypes. Security teams will audit your Dockerfiles. SREs will reject images that are too large. Pipeline engineers will optimize build times. Understanding these practices from the start saves significant rework.

---

## Core Concepts

### Layer Caching Optimization

Every Dockerfile instruction creates a layer. Docker caches layers and reuses them when nothing has changed. The cache invalidation rule is simple: if a layer changes, every layer after it is rebuilt.

**Strategy: Order instructions from least frequently changed to most frequently changed.**

```dockerfile
# Optimal order:
FROM base-image              # Rarely changes
RUN install system packages  # Changes occasionally
COPY dependency-files        # Changes when dependencies change
RUN install dependencies     # Cached unless dependency files change
COPY application-code        # Changes on every commit (last!)
```

### Minimizing Image Size

Smaller images are faster to pull, have fewer vulnerabilities, and use less storage. Strategies:

1. **Use slim or Alpine base images** instead of full distributions
2. **Multi-stage builds** to exclude build tools from production
3. **Combine RUN commands** to reduce layer count
4. **Clean up in the same layer** that installs packages
5. **Use --no-cache-dir** for pip, --no-cache for apk
6. **Use distroless images** for maximum minimalism

Size comparison of common base images:

| Base Image | Size |
|-----------|------|
| `ubuntu:22.04` | ~77 MB |
| `python:3.12` | ~1 GB |
| `python:3.12-slim` | ~155 MB |
| `python:3.12-alpine` | ~52 MB |
| `gcr.io/distroless/python3` | ~52 MB |
| `alpine:3.19` | ~7 MB |

### Running as Non-Root

By default, containers run as root. This is a security risk because: if an attacker escapes the container, they have root access on the host (in some configurations). Always create and switch to a non-root user.

### HEALTHCHECK Instruction

HEALTHCHECK tells Docker how to test whether a container is still working. Without it, Docker only knows if the main process is running -- not whether it is actually serving requests. Kubernetes uses its own health checks, but Docker's HEALTHCHECK is valuable for Docker Compose and standalone Docker deployments.

### Security Scanning

Container images can contain known vulnerabilities in their base OS packages and application dependencies. Tools like Trivy, Snyk, and Docker Scout scan images against vulnerability databases. Scanning should be automated in your CI/CD pipeline.

### Linting with Hadolint

Hadolint is a Dockerfile linter that checks for common mistakes, security issues, and best practice violations. It catches problems before they reach a build.

---

## Step-by-Step Practical

### Layer Caching: Good vs Bad

```dockerfile
# BAD: Every code change reinstalls dependencies
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

```dockerfile
# GOOD: Dependencies are cached until requirements.txt changes
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Minimizing Image Size: Combining RUN Commands

```dockerfile
# BAD: Each RUN creates a layer; removed files still exist in previous layers
RUN apt-get update
RUN apt-get install -y curl wget git
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*
# The cleanup in layers 3-4 does NOT reduce image size because
# the files still exist in layers 1-2.
```

```dockerfile
# GOOD: Single layer, cleanup in the same RUN
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        wget \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
```

### Using Alpine and Slim Images

```dockerfile
# Production Python image using slim base
FROM python:3.12-slim AS base

# Install only runtime system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

### Running as Non-Root User

```dockerfile
FROM python:3.12-slim

# Create a non-root user and group
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

# Install dependencies as root (need write access to system dirs)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and set ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

```bash
# Verify the container runs as non-root
docker build -t secure-app:1.0.0 .
docker run --rm secure-app:1.0.0 whoami
```

Expected output:

```
appuser
```

### Adding HEALTHCHECK

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Health check: hit the /health endpoint every 30 seconds
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

```bash
# Build and run
docker build -t healthcheck-app:1.0.0 .
docker run -d --name hc-test healthcheck-app:1.0.0

# Check health status
docker inspect --format='{{.State.Health.Status}}' hc-test
```

Expected output (after start period):

```
healthy
```

```bash
# View health check details
docker inspect --format='{{json .State.Health}}' hc-test | python3 -m json.tool
```

### ARG vs ENV

```dockerfile
# ARG: available only during build, not in running container
ARG BUILD_DATE
ARG GIT_SHA

# ENV: available during build AND in running container
ENV APP_VERSION=1.0.0
ENV LOG_LEVEL=info

# Using ARG to set ENV
ARG VERSION=1.0.0
ENV APP_VERSION=${VERSION}

# Labels using build-time ARGs
LABEL build-date=${BUILD_DATE}
LABEL git-sha=${GIT_SHA}
```

```bash
# Pass ARG values at build time
docker build \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --build-arg GIT_SHA=$(git rev-parse --short HEAD) \
  --build-arg VERSION=2.1.0 \
  -t myapp:2.1.0 .
```

### COPY vs ADD

```dockerfile
# COPY: Simple, explicit, predictable
COPY config.yml /app/config.yml
COPY src/ /app/src/

# ADD: Automatically extracts tar archives
ADD archive.tar.gz /app/
# Result: /app/ contains the extracted contents

# ADD can fetch URLs (but DON'T -- use RUN curl instead)
# ADD https://example.com/file.txt /app/  # BAD: no caching, no checksum
# RUN curl -fsSL -o /app/file.txt https://example.com/file.txt  # GOOD
```

### Linting with Hadolint

```bash
# Install hadolint
docker pull hadolint/hadolint

# Lint a Dockerfile
docker run --rm -i hadolint/hadolint < Dockerfile
```

Expected output (for a Dockerfile with issues):

```
Dockerfile:3 DL3008 warning: Pin versions in apt get install
Dockerfile:5 DL3013 warning: Pin versions in pip
Dockerfile:8 DL3025 info: Use arguments JSON notation for CMD
Dockerfile:1 DL3007 warning: Using latest is prone to errors
```

```bash
# Lint with specific rules ignored
docker run --rm -i hadolint/hadolint --ignore DL3008 < Dockerfile
```

### Security Scanning with Trivy

```bash
# Install trivy (or use Docker)
docker run --rm aquasec/trivy image flask-api:1.0.0
```

Expected output:

```
flask-api:1.0.0 (debian 12.5)
================================
Total: 42 (UNKNOWN: 0, LOW: 25, MEDIUM: 12, HIGH: 4, CRITICAL: 1)

┌──────────────┬──────────────┬──────────┬────────────────┬────────────────┐
│   Library    │ Vulnerability│ Severity │ Installed Ver  │  Fixed Version │
├──────────────┼──────────────┼──────────┼────────────────┼────────────────┤
│ libssl3      │ CVE-2024-XXX │ CRITICAL │ 3.0.11-1       │ 3.0.13-1       │
│ curl         │ CVE-2024-YYY │ HIGH     │ 7.88.1-10      │ 7.88.1-10+deb │
└──────────────┴──────────────┴──────────┴────────────────┴────────────────┘
```

### Complete Production Dockerfile

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Production stage
FROM python:3.12-slim

# Build-time arguments for metadata
ARG BUILD_DATE
ARG GIT_SHA
ARG VERSION=1.0.0

# Labels for image metadata
LABEL maintainer="platform-team@example.com"
LABEL build-date=${BUILD_DATE}
LABEL git-sha=${GIT_SHA}
LABEL version=${VERSION}

# Install only runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

# Copy installed Python packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV APP_VERSION=${VERSION}
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Switch to non-root user
USER appuser

EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "4", "app:app"]
```

---

## Exercises

### Exercise 1: Optimize an Inefficient Dockerfile

Take this Dockerfile and optimize it for layer caching, image size, and security:

```dockerfile
FROM python:3.12
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y curl
CMD python app.py
```

Document each change you made and why.

### Exercise 2: Multi-Stage Build Comparison

Build the same application twice: once with a single-stage Dockerfile and once with a multi-stage Dockerfile. Compare the image sizes using `docker images`. Calculate the percentage size reduction.

### Exercise 3: Security Hardening

Take any existing Dockerfile and apply all security best practices: non-root user, pinned versions, no secrets in build args, minimal base image, and HEALTHCHECK. Scan both the original and hardened images with Trivy and compare vulnerability counts.

### Exercise 4: Hadolint Integration

Run hadolint on five different Dockerfiles (from your own projects or open-source repositories). Document the most common warnings and categorize them by type (security, efficiency, best practice). Fix all warnings in one Dockerfile and verify with a clean hadolint run.

### Exercise 5: Build Performance Measurement

Create a Dockerfile with intentionally poor caching (COPY . before dependency installation). Time the initial build and a rebuild after a code change. Then fix the caching order and time the same operations. Calculate the build time improvement.

---

## Knowledge Check

**Q1: Why should you run containers as a non-root user, and how do you implement this?**

<details>
<summary>Answer</summary>

Running as root inside a container is a security risk because: (1) if a container escape vulnerability exists, the attacker gains root on the host, (2) root can modify system files inside the container, potentially affecting mounted volumes, and (3) many compliance standards require non-root execution.

Implementation: Create a user and group with `RUN groupadd/useradd`, set file ownership with `COPY --chown`, and switch to the user with `USER appuser` before the `CMD` instruction. Install system packages before the `USER` switch (they require root), then run the application as the non-root user.

</details>

**Q2: What is the difference between ARG and ENV? When should you use each?**

<details>
<summary>Answer</summary>

`ARG` is available only during the build process and is not present in the running container. It is used for build-time customization: version numbers, build dates, Git SHAs, and toggling build features.

`ENV` is available during both build and runtime. It persists in the image and is visible in running containers. It is used for application configuration: log levels, port numbers, feature flags.

You can use ARG to set ENV: `ARG VERSION=1.0.0` then `ENV APP_VERSION=${VERSION}`. This lets you customize the runtime environment at build time while ensuring the value is available when the container runs.

Never put secrets in either ARG or ENV -- they are visible in image history and inspection.

</details>

**Q3: Why is cleaning up in the same RUN layer important for image size?**

<details>
<summary>Answer</summary>

Docker layers are additive. If you install packages in one layer and clean up in the next, the installed files still exist in the first layer -- the cleanup layer simply marks them as deleted in the overlay filesystem, but the data remains in the image.

```dockerfile
# BAD: 200MB image (cleanup is in a separate layer)
RUN apt-get update && apt-get install -y gcc
RUN rm -rf /var/lib/apt/lists/*

# GOOD: 150MB image (cleanup is in the same layer)
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
```

The only way to truly reduce image size is to clean up in the same `RUN` command that created the files, or to use multi-stage builds where the build artifacts are copied to a clean final stage.

</details>

**Q4: What does HEALTHCHECK do, and what are its key parameters?**

<details>
<summary>Answer</summary>

HEALTHCHECK defines a command that Docker runs periodically to verify the container is functioning correctly. It goes beyond process monitoring (is the process running?) to application monitoring (is the application serving requests?).

Key parameters:
- `--interval`: How often to run the check (default 30s)
- `--timeout`: Maximum time for a check to complete (default 30s)
- `--start-period`: Grace period after startup before checks count as failures (default 0s)
- `--retries`: Number of consecutive failures before marking unhealthy (default 3)

The container's health status becomes: `starting` (during start-period), `healthy` (check passing), or `unhealthy` (retries exhausted). Docker Compose and Swarm use this status for orchestration decisions.

</details>

**Q5: What is hadolint and why should it be part of your CI pipeline?**

<details>
<summary>Answer</summary>

Hadolint is a Dockerfile linter that validates Dockerfiles against best practices and security guidelines. It checks for: unpinned package versions (DL3008), running as root, using `latest` tag (DL3007), improper use of ADD vs COPY, unquoted variables, and shell best practices.

It should be in your CI pipeline because: (1) it catches problems before images are built, saving compute time, (2) it enforces consistent Dockerfile quality across all team members, (3) it identifies security issues like unpinned dependencies that could introduce vulnerabilities, and (4) it serves as automated documentation of Dockerfile standards. Running hadolint is fast (seconds) and prevents slow, expensive problems downstream.

</details>
