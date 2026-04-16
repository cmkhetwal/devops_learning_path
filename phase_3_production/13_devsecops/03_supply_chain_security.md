# Supply Chain Security: SBOMs, Signing, and Verification

## Why This Matters in DevOps

The SolarWinds attack in 2020 compromised 18,000 organizations through a
tampered software update. The Log4Shell vulnerability in 2021 affected millions
of systems through a single library. The xz Utils backdoor in 2024 was a
multi-year social engineering attack on an open-source maintainer.

These attacks share a common pattern: they exploit the **software supply chain**
-- the chain of dependencies, build systems, and distribution mechanisms that
deliver software from developer to production. You do not just run your code;
you run your code plus every library it depends on, plus the base image, plus
the build tools, plus the CI/CD pipeline. Each link in this chain is an attack
surface.

Supply chain security ensures that every artifact in your software pipeline is
authentic, unmodified, and free from known vulnerabilities. It answers three
questions: What is in my software? (SBOM), Who built it? (Signing), and
Can I trust it? (Verification).

---

## Core Concepts

### What Is the Software Supply Chain?

```
Source Code          Build System         Artifact Registry      Runtime
    │                    │                      │                  │
    ▼                    ▼                      ▼                  ▼
┌────────┐         ┌──────────┐          ┌───────────┐      ┌──────────┐
│ Your   │         │ CI/CD    │          │ Container │      │ Kubernetes│
│ Code   │────────▶│ Pipeline │─────────▶│ Registry  │─────▶│ Cluster  │
│        │         │          │          │           │      │          │
│ Open   │         │ Build    │          │ Signed    │      │ Admission│
│ Source │         │ Tools    │          │ Images    │      │ Control  │
│ Deps   │         │ Base     │          │ SBOM      │      │ Policy   │
│        │         │ Images   │          │ Attestation│      │ Enforce  │
└────────┘         └──────────┘          └───────────┘      └──────────┘

 Threats:           Threats:              Threats:           Threats:
 - Malicious dep    - Compromised CI      - Registry breach  - Image tampering
 - Typosquatting    - Tampered build       - Tag mutation     - Missing signature
 - Abandoned lib    - Injected code        - Retagging        - Stale image
```

### SBOM (Software Bill of Materials)

An SBOM is a complete inventory of all components in a software artifact. It
lists every library, framework, and tool with their versions, licenses, and
sources:

```
SBOM for myapp:v2.1.0
├── Base Image: python:3.12-slim (Debian 12.4)
│   ├── libc6 2.36-9+deb12u4
│   ├── libssl3 3.0.11-1~deb12u2
│   ├── zlib1g 1:1.2.13.dfsg-1
│   └── ... (120 more OS packages)
├── Python 3.12.2
├── Application Dependencies:
│   ├── flask 3.0.0 (BSD-3-Clause)
│   ├── gunicorn 21.2.0 (MIT)
│   ├── requests 2.31.0 (Apache-2.0)
│   ├── sqlalchemy 2.0.25 (MIT)
│   ├── pydantic 2.5.3 (MIT)
│   └── ... (15 more packages)
└── Application Code: myapp 2.1.0 (proprietary)
```

Standard SBOM formats:

| Format | Maintained By | Focus |
|---|---|---|
| **SPDX** | Linux Foundation | Broad (licensing + security) |
| **CycloneDX** | OWASP | Security-focused |
| **SWID** | ISO/IEC | Software identification |

### SBOM Generation

#### With Syft

```bash
# Install Syft
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Generate SBOM from a container image
syft myapp:v2.1.0 -o spdx-json > sbom.spdx.json
syft myapp:v2.1.0 -o cyclonedx-json > sbom.cdx.json

# Generate SBOM from a directory
syft dir:./my-project -o spdx-json > sbom.spdx.json

# Generate SBOM from a Dockerfile
syft myapp:v2.1.0 -o table
# NAME              VERSION    TYPE
# flask             3.0.0      python
# gunicorn          21.2.0     python
# requests          2.31.0     python
# libc6             2.36-9     deb
# libssl3           3.0.11     deb
# ...

# Attach SBOM to OCI image as an attestation
syft attest --output cyclonedx-json myapp:v2.1.0 -k cosign.key > sbom-attestation.json
```

#### With Trivy

```bash
# Generate SBOM with Trivy
trivy image --format cyclonedx --output sbom.cdx.json myapp:v2.1.0

# Generate SBOM and scan for vulnerabilities in one pass
trivy sbom sbom.cdx.json
# Scans the SBOM for known vulnerabilities without needing the image
```

### SLSA Framework

SLSA (Supply-chain Levels for Software Artifacts, pronounced "salsa") is a
framework for ensuring the integrity of software artifacts throughout the
supply chain:

| Level | Requirements | Trust |
|---|---|---|
| **SLSA 0** | No guarantees | No protection |
| **SLSA 1** | Build process documented, provenance generated | Prevents accidental errors |
| **SLSA 2** | Hosted build service, authenticated provenance | Prevents tampering after build |
| **SLSA 3** | Hardened build platform, non-falsifiable provenance | Prevents tampering during build |
| **SLSA 4** | Two-person review, hermetic builds, reproducible | Prevents insider threats |

SLSA provenance is an attestation about how an artifact was built:

```json
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "subject": [{
    "name": "ghcr.io/myorg/myapp",
    "digest": { "sha256": "abc123..." }
  }],
  "predicateType": "https://slsa.dev/provenance/v1",
  "predicate": {
    "buildDefinition": {
      "buildType": "https://github.com/slsa-framework/slsa-github-generator",
      "externalParameters": {
        "source": {
          "uri": "git+https://github.com/myorg/myapp@refs/heads/main",
          "digest": { "sha1": "def456..." }
        }
      }
    },
    "runDetails": {
      "builder": {
        "id": "https://github.com/slsa-framework/slsa-github-generator/.github/workflows/generator_container_slsa3.yml@refs/tags/v1.9.0"
      }
    }
  }
}
```

### Image Signing with Cosign/Sigstore

Cosign (part of the Sigstore project) signs container images to verify their
authenticity:

```bash
# Install Cosign
brew install cosign  # macOS
# or download from https://github.com/sigstore/cosign/releases

# Generate a key pair (for key-based signing)
cosign generate-key-pair
# Enter password for private key:
# Private key written to cosign.key
# Public key written to cosign.pub

# Sign an image
cosign sign --key cosign.key ghcr.io/myorg/myapp:v2.1.0
# Pushing signature to: ghcr.io/myorg/myapp:sha256-abc123.sig

# Verify a signed image
cosign verify --key cosign.pub ghcr.io/myorg/myapp:v2.1.0
# Verification for ghcr.io/myorg/myapp:v2.1.0 --
# The following checks were performed on each of these signatures:
#   - The cosign claims were validated
#   - The signatures were verified against the specified public key
#
# [{"critical":{"identity":{"docker-reference":"ghcr.io/myorg/myapp"},...}]

# Keyless signing with Sigstore (OIDC-based, no key management)
cosign sign ghcr.io/myorg/myapp:v2.1.0
# Opens a browser for OIDC authentication
# Signs using a short-lived certificate from Fulcio
# Publishes signature to Rekor transparency log

# Verify keyless signature
cosign verify \
  --certificate-identity "user@example.com" \
  --certificate-oidc-issuer "https://accounts.google.com" \
  ghcr.io/myorg/myapp:v2.1.0

# Attach an SBOM to an image
cosign attach sbom --sbom sbom.cdx.json ghcr.io/myorg/myapp:v2.1.0

# Sign the SBOM attestation
cosign attest --key cosign.key \
  --predicate sbom.cdx.json \
  --type cyclonedx \
  ghcr.io/myorg/myapp:v2.1.0
```

### Admission Controllers for Enforcement

Admission controllers verify image signatures before allowing pods to run:

#### Kyverno

```yaml
# Require all images to be signed
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signature
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: verify-cosign-signature
      match:
        any:
          - resources:
              kinds:
                - Pod
      verifyImages:
        - imageReferences:
            - "ghcr.io/myorg/*"
          attestors:
            - entries:
                - keys:
                    publicKeys: |-
                      -----BEGIN PUBLIC KEY-----
                      MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...
                      -----END PUBLIC KEY-----
          attestations:
            - type: https://cyclonedx.org/bom
              conditions:
                - all:
                    - key: "{{ components[?vulnerabilities[?ratings[?severity == 'critical']]].name | length(@) }}"
                      operator: Equals
                      value: "0"
```

#### OPA Gatekeeper

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8strustedimages
spec:
  crd:
    spec:
      names:
        kind: K8sTrustedImages
      validation:
        openAPIV3Schema:
          type: object
          properties:
            registries:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8strustedimages
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not trusted_registry(container.image)
          msg := sprintf("Image '%v' is not from a trusted registry", [container.image])
        }
        trusted_registry(image) {
          registry := input.parameters.registries[_]
          startswith(image, registry)
        }

---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sTrustedImages
metadata:
  name: trusted-registries
spec:
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
  parameters:
    registries:
      - "ghcr.io/myorg/"
      - "gcr.io/distroless/"
```

### Dependency Scanning

```bash
# Scan Python dependencies
pip-audit
# Found 2 known vulnerabilities in 1 package
# Name    Version ID             Fix Versions
# ------- ------- -------------- ------------
# django  4.2.7   PYSEC-2024-001 4.2.9

# Scan Node.js dependencies
npm audit
# 3 vulnerabilities (1 moderate, 1 high, 1 critical)

# Scan Go dependencies
govulncheck ./...

# Automated dependency updates with Renovate or Dependabot
# .github/dependabot.yml
cat > .github/dependabot.yml << 'EOF'
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "daily"
    open-pull-requests-limit: 10
    labels:
      - "dependencies"
      - "security"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "docker"
      - "security"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
EOF
```

---

## Step-by-Step Practical

### Generate SBOM and Sign Images

```bash
# 1. Build an application image
cat > Dockerfile << 'EOF'
FROM python:3.12-slim
RUN groupadd -r app && useradd -r -g app app
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
USER app
CMD ["python", "app.py"]
EOF

cat > requirements.txt << 'EOF'
flask==3.0.0
requests==2.31.0
gunicorn==21.2.0
EOF

cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'
EOF

docker build -t myapp:v1.0.0 .

# 2. Generate SBOM with Syft
syft myapp:v1.0.0 -o spdx-json > sbom.spdx.json
syft myapp:v1.0.0 -o cyclonedx-json > sbom.cdx.json

# View SBOM summary
syft myapp:v1.0.0 -o table
# NAME              VERSION         TYPE
# Jinja2            3.1.3           python
# MarkupSafe        2.1.5           python
# Werkzeug          3.0.1           python
# blinker           1.7.0           python
# click             8.1.7           python
# flask             3.0.0           python
# gunicorn          21.2.0          python
# itsdangerous      2.1.2           python
# requests          2.31.0          python
# ...
# apt               2.6.1           deb
# base-files        12.4+deb12u5    deb
# libc6             2.36-9+deb12u4  deb
# libssl3           3.0.11-1~deb12u2 deb
# ...

# 3. Scan SBOM for vulnerabilities
trivy sbom sbom.cdx.json
# Scans without needing the image

# 4. Tag and push to a registry
docker tag myapp:v1.0.0 ghcr.io/myorg/myapp:v1.0.0
docker push ghcr.io/myorg/myapp:v1.0.0

# 5. Generate signing keys
cosign generate-key-pair
# Creates cosign.key (private) and cosign.pub (public)

# 6. Sign the image
cosign sign --key cosign.key ghcr.io/myorg/myapp:v1.0.0
# Enter password for cosign.key:
# Pushing signature to: ghcr.io/myorg/myapp:sha256-abc123.sig

# 7. Attach SBOM to the image
cosign attach sbom --sbom sbom.cdx.json ghcr.io/myorg/myapp:v1.0.0

# 8. Sign the SBOM attestation
cosign attest --key cosign.key \
  --predicate sbom.cdx.json \
  --type cyclonedx \
  ghcr.io/myorg/myapp:v1.0.0

# 9. Verify everything
cosign verify --key cosign.pub ghcr.io/myorg/myapp:v1.0.0
# Verification successful

cosign verify-attestation --key cosign.pub \
  --type cyclonedx \
  ghcr.io/myorg/myapp:v1.0.0
# Attestation verification successful

# 10. Complete CI/CD pipeline
cat > .github/workflows/supply-chain.yaml << 'PIPELINE'
name: Supply Chain Security
on:
  push:
    tags: ['v*']

jobs:
  build-sign-attest:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write  # For keyless signing

    steps:
      - uses: actions/checkout@v4

      - name: Build image
        run: docker build -t ghcr.io/${{ github.repository }}:${{ github.ref_name }} .

      - name: Push image
        run: |
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u $ --password-stdin
          docker push ghcr.io/${{ github.repository }}:${{ github.ref_name }}

      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Install Syft
        uses: anchore/sbom-action/download-syft@v0

      - name: Generate SBOM
        run: syft ghcr.io/${{ github.repository }}:${{ github.ref_name }} -o cyclonedx-json > sbom.cdx.json

      - name: Scan SBOM for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'sbom'
          scan-ref: 'sbom.cdx.json'
          severity: 'CRITICAL'
          exit-code: '1'

      - name: Sign image (keyless)
        run: cosign sign ghcr.io/${{ github.repository }}:${{ github.ref_name }}
        env:
          COSIGN_EXPERIMENTAL: 1

      - name: Attest SBOM
        run: |
          cosign attest \
            --predicate sbom.cdx.json \
            --type cyclonedx \
            ghcr.io/${{ github.repository }}:${{ github.ref_name }}
PIPELINE
```

---

## Exercises

### Exercise 1: SBOM Generation and Analysis
Build a Python or Node.js application image. Generate an SBOM using both Syft
and Trivy. Compare the two SBOMs: do they list the same components? Are there
differences? Scan the SBOM for vulnerabilities and document the findings.

### Exercise 2: Image Signing Workflow
Set up a complete image signing workflow: generate keys, build an image, push
it to a registry, sign it, attach an SBOM, sign the SBOM attestation, and
verify everything. Try to deploy the image to a cluster with a Kyverno policy
that requires signatures.

### Exercise 3: Dependency Audit
Run a dependency audit on a project in your preferred language (pip-audit for
Python, npm audit for Node.js, govulncheck for Go). Document all vulnerabilities
found, their severity, and whether fixes are available. Create a remediation
plan with prioritized updates.

### Exercise 4: Admission Controller Policy
Install Kyverno and create policies that: (1) require all images to come from
your organization's registry, (2) require all images to have a signed SBOM
attestation, (3) block images with critical vulnerabilities. Test by deploying
both compliant and non-compliant pods.

### Exercise 5: SLSA Level Assessment
Assess your current CI/CD pipeline against the SLSA framework. Determine your
current SLSA level. Identify what changes would be needed to reach SLSA Level 3.
Create a roadmap with specific GitHub Actions or pipeline changes for each
requirement.

---

## Knowledge Check

### Question 1
What is an SBOM and why is it important for security?

**Answer:** An SBOM (Software Bill of Materials) is a complete, structured
inventory of all components, libraries, and dependencies in a software artifact.
It is important because it enables vulnerability management (when a new CVE is
announced, you can instantly check if you are affected), license compliance
(verify all dependencies have acceptable licenses), incident response (quickly
identify which systems use a compromised library), and regulatory compliance
(SBOM generation is now required by US Executive Order 14028 for government
software). Without an SBOM, you cannot answer the question "are we affected by
this vulnerability?" without scanning every system from scratch.

### Question 2
How does keyless signing with Sigstore differ from key-based signing?

**Answer:** Key-based signing requires generating and managing a private key.
The key must be securely stored, rotated, and protected. If the key is
compromised, an attacker can sign malicious images. Keyless signing with
Sigstore eliminates key management by using OIDC (OpenID Connect) identity
providers (Google, GitHub, Microsoft). The signer authenticates via OIDC, Fulcio
(Sigstore's CA) issues a short-lived certificate (valid for ~20 minutes), the
image is signed with this certificate, and the signature is recorded in Rekor
(Sigstore's transparency log). Verification checks the OIDC identity and the
transparency log, not a static key. This is more secure because there is no
long-lived key to compromise.

### Question 3
What is SLSA and what problem does it solve?

**Answer:** SLSA (Supply-chain Levels for Software Artifacts) is a framework
that defines increasing levels of supply chain integrity. It solves the problem
of verifying that a software artifact was actually built from the claimed source
code by the claimed build system, without tampering. Each level adds stronger
guarantees: Level 1 requires documented build provenance, Level 2 requires a
hosted build service with authenticated provenance, Level 3 requires a hardened
build platform with non-falsifiable provenance, and Level 4 requires two-person
review and reproducible builds. SLSA provenance attestations answer "who built
this, from what source, using what process?"

### Question 4
How do admission controllers enforce supply chain security in Kubernetes?

**Answer:** Admission controllers intercept API requests to create or update
pods before the request is persisted. For supply chain security, they can:
verify that container images are signed with a trusted key (reject unsigned
images), verify that images have an SBOM attestation, check that the SBOM
contains no critical vulnerabilities, ensure images come from trusted registries
only, and verify SLSA provenance. Tools like Kyverno and OPA Gatekeeper
implement these checks as declarative policies. If an image fails any check,
the pod is rejected and never runs, providing a hard enforcement point.

### Question 5
Why is dependency scanning important and how does it complement container
image scanning?

**Answer:** Dependency scanning (SCA - Software Composition Analysis) checks
application-level dependencies (pip packages, npm modules, Go modules) for
known vulnerabilities. Container image scanning checks OS-level packages and
the overall image. They complement each other because image scanning may not
detect application-dependency vulnerabilities if the scanner does not understand
the package manager, and dependency scanning does not check OS packages. Running
both ensures comprehensive coverage. Additionally, dependency scanning runs
earlier in the pipeline (on source code, before building the image) which
provides faster feedback to developers.
