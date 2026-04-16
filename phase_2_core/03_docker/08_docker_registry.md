# Docker Registry

## Why This Matters in DevOps

A Docker registry is the distribution hub of your CI/CD pipeline. Every image your pipeline builds needs to be stored somewhere accessible by all environments -- development, staging, production, and every Kubernetes node that needs to pull it. The registry is where "build once, deploy anywhere" becomes reality.

For DevOps engineers, registry management is a daily responsibility. You choose the tagging strategy that determines how deployable and traceable your artifacts are. You configure access controls that determine who can push and pull images. You set up vulnerability scanning that catches security issues before they reach production. You manage image lifecycle policies that prevent registry storage from growing indefinitely.

A bad tagging strategy (everything tagged `latest`) makes rollbacks impossible and deployments non-deterministic. A registry without scanning is a pipeline without a security gate. A registry without lifecycle policies accumulates terabytes of unused images at significant cost. Understanding registries is understanding the artifact management layer of your delivery pipeline.

---

## Core Concepts

### What Is a Registry?

A registry is an HTTP-based service that stores and distributes Docker images. It implements the OCI Distribution Specification, which defines how images are pushed, pulled, and cataloged.

```
Developer  →  docker build  →  docker push  →  Registry
                                                    ↓
Production  ←  docker pull  ←  Kubernetes  ←  Registry
```

### Registry Types

| Registry | Type | Provider | Use Case |
|----------|------|----------|----------|
| Docker Hub | Public/Private | Docker Inc. | Default public registry, open-source images |
| Amazon ECR | Private | AWS | AWS-native workloads |
| Google GCR/Artifact Registry | Private | Google Cloud | GCP-native workloads |
| Azure ACR | Private | Microsoft | Azure-native workloads |
| Harbor | Self-hosted | CNCF | Enterprise self-hosted with scanning |
| GitLab Container Registry | Private | GitLab | GitLab CI/CD integration |
| GitHub Container Registry (ghcr.io) | Public/Private | GitHub | GitHub Actions integration |

### Image Naming Convention

The full name of an image follows this pattern:

```
registry.example.com/organization/repository:tag
│                    │              │          │
│                    │              │          └── Version identifier
│                    │              └── Image name
│                    └── Namespace/organization
└── Registry hostname (docker.io is the default)
```

Examples:

```
nginx                                    # docker.io/library/nginx:latest
nginx:1.25                               # docker.io/library/nginx:1.25
mycompany/api:v2.1.0                     # docker.io/mycompany/api:v2.1.0
123456789.dkr.ecr.us-east-1.amazonaws.com/api:v2.1.0  # AWS ECR
gcr.io/my-project/api:v2.1.0            # Google Container Registry
ghcr.io/myorg/api:v2.1.0                # GitHub Container Registry
```

### Image Tagging Strategy

Tagging determines how you identify and deploy specific versions. There are several strategies:

**Semantic Versioning:**
```
myapp:1.0.0
myapp:1.0.1
myapp:1.1.0
myapp:2.0.0
```

**Git SHA:**
```
myapp:a1b2c3d
myapp:e4f5g6h
```

**Combined (recommended):**
```
myapp:v1.2.0              # Human-readable version
myapp:v1.2.0-a1b2c3d      # Version + commit for traceability
myapp:a1b2c3d              # Git SHA for CI/CD references
myapp:latest               # Latest stable (use cautiously)
```

### The `latest` Tag Problem

The `latest` tag is the default when no tag is specified. It is NOT automatically updated and does NOT necessarily point to the most recent image. It is whatever was last pushed without an explicit tag.

**Problems with `latest` in production:**
1. Non-deterministic: you do not know which version you are running
2. Rollbacks are impossible: there is no previous version to roll back to
3. Caching issues: `latest` may or may not be re-pulled depending on the pull policy
4. Auditability: you cannot trace a deployment back to a specific commit

**Rule: Never use `latest` in production deployments. Always use explicit version tags.**

### Image Signing and Trust

Image signing uses cryptographic signatures to verify that an image was built by a trusted party and has not been tampered with. Docker Content Trust (DCT) and Cosign (from the Sigstore project) are common tools.

```
Build Pipeline:
  1. Build image
  2. Scan for vulnerabilities
  3. Sign image with private key
  4. Push to registry

Deployment:
  1. Pull image from registry
  2. Verify signature with public key
  3. Deploy only if signature is valid
```

---

## Step-by-Step Practical

### Pushing to Docker Hub

```bash
# Log in to Docker Hub
docker login
```

Expected output:

```
Login with your Docker ID to push and pull images from Docker Hub.
Username: yourusername
Password:
Login Succeeded
```

```bash
# Tag your image for Docker Hub
docker tag flask-api:1.0.0 yourusername/flask-api:1.0.0
docker tag flask-api:1.0.0 yourusername/flask-api:latest

# Push to Docker Hub
docker push yourusername/flask-api:1.0.0
```

Expected output:

```
The push refers to repository [docker.io/yourusername/flask-api]
a1b2c3d4: Pushed
e5f6g7h8: Pushed
i9j0k1l2: Pushed
1.0.0: digest: sha256:abc123... size: 1234
```

```bash
# Push all tags at once
docker push yourusername/flask-api --all-tags
```

### Working with AWS ECR

```bash
# Authenticate to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  123456789.dkr.ecr.us-east-1.amazonaws.com
```

Expected output:

```
Login Succeeded
```

```bash
# Create a repository (if it doesn't exist)
aws ecr create-repository --repository-name flask-api

# Tag for ECR
docker tag flask-api:1.0.0 \
  123456789.dkr.ecr.us-east-1.amazonaws.com/flask-api:1.0.0

# Push to ECR
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/flask-api:1.0.0
```

### Working with GitHub Container Registry

```bash
# Authenticate with a GitHub personal access token
echo $GITHUB_TOKEN | docker login ghcr.io -u yourusername --password-stdin

# Tag for ghcr.io
docker tag flask-api:1.0.0 ghcr.io/yourorg/flask-api:1.0.0

# Push
docker push ghcr.io/yourorg/flask-api:1.0.0
```

### Implementing a Tagging Strategy in CI/CD

```bash
#!/bin/bash
# ci-build.sh - Example CI/CD build and push script

# Variables from CI environment
GIT_SHA=$(git rev-parse --short HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
VERSION=$(cat VERSION)  # e.g., "1.2.0"
REGISTRY="123456789.dkr.ecr.us-east-1.amazonaws.com"
IMAGE="${REGISTRY}/flask-api"

# Build the image
docker build \
  --build-arg VERSION=${VERSION} \
  --build-arg GIT_SHA=${GIT_SHA} \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  -t ${IMAGE}:${GIT_SHA} \
  .

# Apply multiple tags
docker tag ${IMAGE}:${GIT_SHA} ${IMAGE}:${VERSION}
docker tag ${IMAGE}:${GIT_SHA} ${IMAGE}:${VERSION}-${GIT_SHA}

# Only tag 'latest' for main branch
if [ "${GIT_BRANCH}" = "main" ]; then
  docker tag ${IMAGE}:${GIT_SHA} ${IMAGE}:latest
fi

# Push all tags
docker push ${IMAGE}:${GIT_SHA}
docker push ${IMAGE}:${VERSION}
docker push ${IMAGE}:${VERSION}-${GIT_SHA}
if [ "${GIT_BRANCH}" = "main" ]; then
  docker push ${IMAGE}:latest
fi

echo "Pushed: ${IMAGE}:${VERSION}-${GIT_SHA}"
```

### Vulnerability Scanning

```bash
# Scan with Trivy (open source)
docker run --rm aquasec/trivy image yourusername/flask-api:1.0.0
```

Expected output:

```
yourusername/flask-api:1.0.0 (debian 12.5)
===========================================
Total: 15 (UNKNOWN: 0, LOW: 8, MEDIUM: 5, HIGH: 1, CRITICAL: 1)

Python (pip)
============
Total: 3 (HIGH: 1, MEDIUM: 2)

┌───────────┬──────────────┬──────────┬────────────┬────────────┐
│  Library  │Vulnerability │ Severity │ Installed  │   Fixed    │
├───────────┼──────────────┼──────────┼────────────┼────────────┤
│ werkzeug  │CVE-2024-XXXX │ HIGH     │ 2.3.0      │ 2.3.8      │
└───────────┴──────────────┴──────────┴────────────┴────────────┘
```

```bash
# Scan with Docker Scout (built into Docker)
docker scout cves yourusername/flask-api:1.0.0

# Fail CI if critical vulnerabilities are found
docker run --rm aquasec/trivy image \
  --severity CRITICAL \
  --exit-code 1 \
  yourusername/flask-api:1.0.0
```

### Image Signing with Cosign

```bash
# Install cosign
# (typically done in CI environment)

# Generate a key pair
cosign generate-key-pair

# Sign an image
cosign sign --key cosign.key yourusername/flask-api:1.0.0

# Verify an image signature
cosign verify --key cosign.pub yourusername/flask-api:1.0.0
```

Expected output:

```
Verification for yourusername/flask-api:1.0.0 --
The following checks were performed on each of these signatures:
  - The cosign claims were validated
  - The signatures were verified against the specified public key

[{"critical":{"identity":{"docker-reference":"yourusername/flask-api"},...}]
```

### Setting Up Image Lifecycle Policies (ECR)

```bash
# Create a lifecycle policy to clean up old images
aws ecr put-lifecycle-policy \
  --repository-name flask-api \
  --lifecycle-policy-text '{
    "rules": [
      {
        "rulePriority": 1,
        "description": "Keep only 10 untagged images",
        "selection": {
          "tagStatus": "untagged",
          "countType": "imageCountMoreThan",
          "countNumber": 10
        },
        "action": {
          "type": "expire"
        }
      },
      {
        "rulePriority": 2,
        "description": "Remove images older than 90 days except latest 20",
        "selection": {
          "tagStatus": "tagged",
          "tagPrefixList": ["v"],
          "countType": "sinceImagePushed",
          "countUnit": "days",
          "countNumber": 90
        },
        "action": {
          "type": "expire"
        }
      }
    ]
  }'
```

### Listing and Pulling Images

```bash
# List tags for an image on Docker Hub
docker search nginx

# Pull a specific version
docker pull nginx:1.25.4

# Pull by digest (immutable -- always the same image)
docker pull nginx@sha256:abc123def456...

# List images in an ECR repository
aws ecr list-images --repository-name flask-api
```

---

## Exercises

### Exercise 1: Push to Docker Hub

Build a simple application image, create a Docker Hub account (if you do not have one), and push the image with three tags: a semantic version, a Git SHA, and `latest`. Verify all three tags appear on Docker Hub. Then pull the image on a different machine (or after removing it locally) and run it.

### Exercise 2: Implement a Tagging Strategy

Write a shell script that implements the combined tagging strategy: given a VERSION file and the current Git SHA, it builds the image and tags it with `version`, `version-sha`, `sha`, and conditionally `latest` (only on main branch). Test the script on a feature branch and verify `latest` is not applied.

### Exercise 3: Vulnerability Scanning Pipeline

Set up a scanning workflow: build an image, scan it with Trivy, and fail the process if any CRITICAL or HIGH vulnerabilities are found. Fix the vulnerabilities (update base image or pin package versions) and re-scan until the image passes. Document the vulnerabilities found and how you fixed them.

### Exercise 4: Private Registry Setup

Run a local Docker registry using the `registry:2` image. Push images to it, pull from it, and configure it with basic authentication. This simulates managing a private registry for an organization that cannot use cloud-hosted registries.

### Exercise 5: Image Lifecycle Management

Push 15 images to a registry with dates spanning three months (simulate using different tags). Write a script or configure lifecycle policies that keep only the 5 most recent images and delete anything older than 30 days. Verify the cleanup works correctly.

---

## Knowledge Check

**Q1: Why is using the `latest` tag in production deployments dangerous?**

<details>
<summary>Answer</summary>

The `latest` tag is dangerous because: (1) it is non-deterministic -- you cannot know which version of the code is running without inspecting the image, (2) rollbacks are impossible -- there is no "previous latest" to roll back to, (3) it may or may not be re-pulled depending on the image pull policy, leading to different nodes running different versions, (4) it provides no audit trail -- you cannot trace a deployment back to a specific Git commit, and (5) two developers pushing `latest` in quick succession can override each other's work. Always use explicit version tags (semantic version, Git SHA, or both) for production deployments.

</details>

**Q2: What is the recommended image tagging strategy for a CI/CD pipeline?**

<details>
<summary>Answer</summary>

The recommended strategy uses multiple tags per image to serve different purposes:

1. **Git SHA tag** (`myapp:a1b2c3d`): Unique, immutable, ties the image to a specific commit. Used by CI/CD for automated deployments.
2. **Semantic version tag** (`myapp:v1.2.0`): Human-readable, follows SemVer. Used for release tracking and communication.
3. **Combined tag** (`myapp:v1.2.0-a1b2c3d`): Links the version to the exact commit. Used for debugging and traceability.
4. **`latest` tag**: Only applied on the main branch, only for convenience. Never used for production deployments.

This strategy provides traceability (which commit?), rollback capability (deploy the previous version tag), and human readability (what version is in production?).

</details>

**Q3: Why should vulnerability scanning be part of the CI/CD pipeline, not a manual process?**

<details>
<summary>Answer</summary>

Automated scanning ensures: (1) every image is scanned before it can be deployed -- no exceptions, (2) the pipeline fails automatically if critical vulnerabilities are found, preventing deployment, (3) scanning happens consistently with every build, not when someone remembers to do it, (4) new vulnerabilities in base images are caught when images are rebuilt, even if application code has not changed, and (5) scan results are logged and auditable for compliance. Manual scanning is sporadic, inconsistent, and easy to skip under time pressure -- exactly when it matters most.

</details>

**Q4: What is the difference between pulling by tag and pulling by digest?**

<details>
<summary>Answer</summary>

Pulling by tag (`nginx:1.25`) pulls whatever image currently has that tag. Tags are mutable -- someone can push a different image with the same tag, and your next pull gets the new image. This means `nginx:1.25` today might be different from `nginx:1.25` tomorrow.

Pulling by digest (`nginx@sha256:abc123...`) pulls a specific, immutable image identified by its content hash. The digest never changes for a given image. This guarantees reproducibility -- you always get exactly the same image.

For production deployments requiring maximum reproducibility, use digests. For general use where minor patch updates in a tag are acceptable, use specific version tags (not `latest`).

</details>

**Q5: What is image signing, and why does it matter for supply chain security?**

<details>
<summary>Answer</summary>

Image signing uses cryptographic signatures to verify two things: (1) the image was built by a trusted party (authenticity), and (2) the image has not been modified since it was signed (integrity). Without signing, anyone with registry access could push a malicious image with a legitimate-looking tag.

It matters for supply chain security because: (1) it prevents unauthorized images from being deployed (only signed images are trusted), (2) it detects tampering if a registry is compromised, (3) it provides non-repudiation (proof that a specific build pipeline produced the image), and (4) it is increasingly required by compliance frameworks (SLSA, NIST). Tools like Cosign (Sigstore) and Docker Content Trust enable signing in CI/CD pipelines.

</details>
