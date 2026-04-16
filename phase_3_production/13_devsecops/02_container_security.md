# Container Security: Hardening Images and Runtime

## Why This Matters in DevOps

Containers are the deployment unit of modern applications, and every container
carries its own attack surface. A container image includes an operating system,
libraries, tools, and your application code. Each of these layers can contain
known vulnerabilities (CVEs), misconfigurations, or unnecessary tools that
attackers can exploit.

The container runtime environment adds another layer of risk. A container running
as root with all Linux capabilities can potentially escape the container boundary
and compromise the host. A container with a writable filesystem can be modified
by an attacker after deployment. A container without resource limits can starve
other workloads.

Container security is foundational to DevSecOps. If your container images are
vulnerable and your runtime configurations are permissive, no amount of network
policy or application security will protect you. This lesson covers how to build
secure images, scan for vulnerabilities, and enforce runtime security in
Kubernetes.

---

## Core Concepts

### Image Scanning with Trivy

Trivy is the most widely used open-source vulnerability scanner. It scans
container images, filesystems, Git repositories, and Kubernetes clusters:

```bash
# Scan a container image
trivy image python:3.12-slim
# python:3.12-slim (debian 12.4)
#
# Total: 45 (UNKNOWN: 0, LOW: 28, MEDIUM: 12, HIGH: 4, CRITICAL: 1)
#
# ┌──────────────────┬────────────────┬──────────┬───────────────────┬───────────────┬──────────────────────────────────┐
# │     Library      │ Vulnerability  │ Severity │ Installed Version │ Fixed Version │             Title                │
# ├──────────────────┼────────────────┼──────────┼───────────────────┼───────────────┼──────────────────────────────────┤
# │ libssl3          │ CVE-2024-0727  │ CRITICAL │ 3.0.11-1~deb12u2  │ 3.0.13-1      │ openssl: denial of service ...   │
# │ zlib1g           │ CVE-2023-45853 │ HIGH     │ 1:1.2.13.dfsg-1   │               │ zlib: integer overflow ...        │
# └──────────────────┴────────────────┴──────────┴───────────────────┴───────────────┴──────────────────────────────────┘

# Scan with severity filter
trivy image --severity CRITICAL,HIGH python:3.12-slim

# Fail if vulnerabilities are found (for CI/CD)
trivy image --exit-code 1 --severity CRITICAL python:3.12-slim

# Scan a local Dockerfile
trivy config Dockerfile

# Scan a filesystem (dependencies)
trivy fs --scanners vuln,secret .

# Output as JSON for programmatic processing
trivy image -f json -o results.json python:3.12-slim

# Scan with SARIF output (for GitHub Security tab)
trivy image -f sarif -o trivy.sarif python:3.12-slim
```

### Base Image Selection

The choice of base image has the largest impact on your vulnerability count:

| Base Image | Size | CVE Count (typical) | Use Case |
|---|---|---|---|
| `ubuntu:24.04` | ~78MB | 30-80 | General purpose, familiar tools |
| `debian:12-slim` | ~74MB | 20-50 | Standard Linux, smaller than Ubuntu |
| `alpine:3.19` | ~7MB | 0-5 | Minimal Linux with musl libc |
| `gcr.io/distroless/static` | ~2MB | 0-2 | Statically compiled binaries (Go, Rust) |
| `gcr.io/distroless/base` | ~20MB | 0-5 | Dynamically linked binaries |
| `gcr.io/distroless/python3` | ~52MB | 0-10 | Python applications |
| `scratch` | 0MB | 0 | Absolute minimum (no OS at all) |

**Distroless images** from Google contain only the application runtime (no
shell, no package manager, no utilities). This dramatically reduces the attack
surface because an attacker who compromises the application cannot use standard
tools (bash, curl, wget, nc) for lateral movement.

```dockerfile
# Multi-stage build: build in full image, run in distroless
FROM golang:1.22 AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o /server .

FROM gcr.io/distroless/static:nonroot
COPY --from=builder /server /server
USER 65534:65534
ENTRYPOINT ["/server"]
```

### Non-Root Containers

Running containers as root is the single most common container security mistake.
If an attacker exploits a vulnerability in a root container, they have root
access inside the container, which can be leveraged for container escape:

```dockerfile
# BAD: Running as root (default)
FROM python:3.12-slim
COPY app.py /app/
CMD ["python", "/app/app.py"]

# GOOD: Running as non-root
FROM python:3.12-slim
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser
WORKDIR /app
COPY --chown=appuser:appuser app.py .
USER appuser
CMD ["python", "app.py"]
```

In Kubernetes, enforce non-root at the pod level:

```yaml
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  containers:
    - name: app
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
```

### Read-Only Filesystems

A read-only root filesystem prevents attackers from modifying the container
after deployment (e.g., installing tools, dropping malware, modifying configs):

```yaml
spec:
  containers:
    - name: app
      securityContext:
        readOnlyRootFilesystem: true
      volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: var-run
          mountPath: /var/run
  volumes:
    - name: tmp
      emptyDir: {}
    - name: var-run
      emptyDir: {}
```

The `emptyDir` volumes provide writable directories where the application
needs them (temp files, PID files) while keeping the rest of the filesystem
read-only.

### Linux Capabilities

Linux capabilities break root privileges into fine-grained permissions. Containers
should drop ALL capabilities and add only what is specifically needed:

```yaml
securityContext:
  capabilities:
    drop:
      - ALL
    add:
      - NET_BIND_SERVICE  # Only if binding to ports < 1024
```

Common capabilities and their risks:

| Capability | Risk | When Needed |
|---|---|---|
| `SYS_ADMIN` | Near-root access, container escape | Almost never (avoid) |
| `NET_ADMIN` | Network configuration, sniffing | Network debugging tools only |
| `SYS_PTRACE` | Process tracing, debugging | Debugging tools only |
| `NET_RAW` | Raw sockets, packet crafting | ping, network diagnostics |
| `NET_BIND_SERVICE` | Bind to privileged ports (<1024) | Web servers on port 80/443 |
| `CHOWN` | Change file ownership | Initial setup only |
| `DAC_OVERRIDE` | Bypass file permissions | Avoid |

### Seccomp Profiles

Seccomp (Secure Computing) filters restrict which system calls a container can
make. The default Docker/containerd profile blocks about 44 dangerous syscalls:

```yaml
# Use the runtime default profile
spec:
  securityContext:
    seccompProfile:
      type: RuntimeDefault

# Or use a custom profile
spec:
  securityContext:
    seccompProfile:
      type: Localhost
      localhostProfile: profiles/my-profile.json
```

Custom seccomp profile example:

```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": [
        "read", "write", "open", "close", "stat", "fstat",
        "mmap", "mprotect", "munmap", "brk", "sigaction",
        "ioctl", "access", "pipe", "select", "socket",
        "connect", "accept", "sendto", "recvfrom", "bind",
        "listen", "clone", "execve", "exit", "exit_group",
        "futex", "epoll_wait", "epoll_ctl", "openat",
        "getdents64", "fcntl", "lseek"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

### Pod Security Standards

Kubernetes defines three Pod Security Standards that can be enforced per-namespace:

| Level | Description | Restrictions |
|---|---|---|
| **Privileged** | No restrictions | Anything goes (system-level workloads) |
| **Baseline** | Minimally restrictive | No privileged containers, no hostNetwork, no hostPID |
| **Restricted** | Heavily restricted | Non-root, read-only fs, drop all capabilities, seccomp |

```yaml
# Enforce restricted standard on a namespace
apiVersion: v1
kind: Namespace
metadata:
  name: production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/warn: restricted
    pod-security.kubernetes.io/audit: restricted
```

### OPA/Gatekeeper for Policy Enforcement

OPA (Open Policy Agent) Gatekeeper provides custom policy enforcement beyond
Pod Security Standards:

```yaml
# ConstraintTemplate: Define the policy logic
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
      validation:
        openAPIV3Schema:
          type: object
          properties:
            labels:
              type: array
              items:
                type: string
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }

---
# Constraint: Apply the policy
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredLabels
metadata:
  name: require-team-label
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
  parameters:
    labels:
      - "team"
      - "environment"
```

---

## Step-by-Step Practical

### Scanning and Hardening a Docker Image

```bash
# 1. Start with an insecure Dockerfile
cat > Dockerfile.insecure << 'EOF'
FROM python:3.12
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8080
CMD ["python", "app.py"]
EOF

# Create a sample app
cat > app.py << 'EOF'
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
EOF

cat > requirements.txt << 'EOF'
flask==3.0.0
gunicorn==21.2.0
EOF

# 2. Build the insecure image
docker build -f Dockerfile.insecure -t myapp:insecure .

# 3. Scan the insecure image
trivy image myapp:insecure
# Total: 150+ vulnerabilities (many HIGH and CRITICAL)

# 4. Check the image size
docker images myapp:insecure
# REPOSITORY   TAG        SIZE
# myapp        insecure   1.02GB

# 5. Create a hardened Dockerfile
cat > Dockerfile.secure << 'EOF'
# Stage 1: Build dependencies
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /sbin/nologin appuser && \
    mkdir -p /app && \
    chown appuser:appuser /app

# Copy only the installed packages
COPY --from=builder /install /usr/local

# Copy application code
WORKDIR /app
COPY --chown=appuser:appuser app.py .

# Switch to non-root user
USER appuser

# Use non-privileged port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
EOF

# 6. Build the secure image
docker build -f Dockerfile.secure -t myapp:secure .

# 7. Scan the secure image
trivy image myapp:secure
# Total: 5-15 vulnerabilities (mostly LOW/MEDIUM)

# 8. Compare sizes
docker images | grep myapp
# myapp   insecure   1.02GB
# myapp   secure     195MB

# 9. Verify the image runs as non-root
docker run --rm myapp:secure id
# uid=999(appuser) gid=999(appuser) groups=999(appuser)

# 10. Scan the Dockerfile itself for misconfigurations
trivy config Dockerfile.secure
# Should show no critical issues
```

### Deploying with Kubernetes Security Context

```yaml
# secure-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      automountServiceAccountToken: false  # Don't mount SA token unless needed
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: myapp
          image: myapp:secure
          ports:
            - containerPort: 8080
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          resources:
            limits:
              cpu: 500m
              memory: 256Mi
            requests:
              cpu: 100m
              memory: 128Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir:
            sizeLimit: 100Mi
```

```bash
# Deploy
kubectl apply -f secure-deployment.yaml

# Verify security settings
kubectl get pod -n production -o jsonpath='{.items[0].spec.containers[0].securityContext}' | jq .
# {
#   "allowPrivilegeEscalation": false,
#   "capabilities": { "drop": ["ALL"] },
#   "readOnlyRootFilesystem": true
# }

# Try to exec as root (should fail)
kubectl exec -n production deploy/myapp -- whoami
# appuser (not root)

# Try to write to filesystem (should fail)
kubectl exec -n production deploy/myapp -- touch /test
# touch: cannot touch '/test': Read-only file system

# Writing to /tmp should work
kubectl exec -n production deploy/myapp -- touch /tmp/test
# (succeeds)
```

---

## Exercises

### Exercise 1: Image Comparison
Build the same Python application using four different base images: `python:3.12`,
`python:3.12-slim`, `python:3.12-alpine`, and `gcr.io/distroless/python3`. Scan
each with Trivy and compare: image size, total CVE count, critical CVE count.
Create a table summarizing the results.

### Exercise 2: Dockerfile Hardening
Take the following insecure Dockerfile and apply all hardening best practices
(multi-stage build, non-root user, read-only filesystem, no cache, minimal
base image, health check):
```dockerfile
FROM node:20
WORKDIR /app
COPY . .
RUN npm install
CMD ["node", "server.js"]
```

### Exercise 3: Pod Security Standard Enforcement
Create a namespace with the `restricted` Pod Security Standard enforced. Try to
deploy a pod that violates the standard (running as root, with privileged
access). Document the error messages. Then fix the pod spec to comply with the
restricted standard.

### Exercise 4: OPA Gatekeeper Policy
Install OPA Gatekeeper and create a policy that: requires all containers to have
resource limits, requires all containers to use non-root, and requires all pods
to have a `team` label. Test by deploying pods that violate each policy.

### Exercise 5: Security Audit
Pull the `nginx:latest` image. Run a comprehensive security audit: scan with
Trivy for CVEs, check for secrets, verify it runs as non-root, check Linux
capabilities, and verify the seccomp profile. Document all findings and create
a hardened version that addresses every issue.

---

## Knowledge Check

### Question 1
Why are distroless images more secure than standard base images?

**Answer:** Distroless images contain only the application runtime (e.g., Python
interpreter, Java JRE) and no operating system utilities (no shell, no package
manager, no curl, no wget, no ls). This reduces the attack surface in two ways:
there are fewer packages that can have vulnerabilities (fewer CVEs), and if an
attacker compromises the application, they cannot use standard tools for
reconnaissance, lateral movement, or data exfiltration. Without a shell, even
remote code execution is significantly harder to exploit.

### Question 2
What does `readOnlyRootFilesystem: true` protect against?

**Answer:** A read-only root filesystem prevents an attacker from modifying the
container after it is deployed. Without this, an attacker who gains code
execution can: install additional tools (curl, nmap), modify application code
to inject backdoors, drop malware on the filesystem, modify configuration files
to change behavior, or create cron jobs for persistence. With a read-only
filesystem, the container is immutable at runtime, and any attempt to write to
the filesystem fails. Applications that need to write (temp files, caches) can
use `emptyDir` volumes for specific writable paths.

### Question 3
Why should containers drop ALL Linux capabilities?

**Answer:** Linux capabilities break root privileges into about 40 fine-grained
permissions. By default, containers are granted a set of capabilities even when
running as non-root. Some of these (like `NET_RAW` for crafting raw packets or
`SYS_CHROOT` for changing the root directory) can be abused by attackers.
Dropping ALL capabilities and then adding only the specific ones needed (if any)
follows the principle of least privilege. Most applications need zero
capabilities to function. The only common exception is `NET_BIND_SERVICE` for
binding to ports below 1024.

### Question 4
What is the difference between Pod Security Standards and OPA Gatekeeper?

**Answer:** Pod Security Standards are a built-in Kubernetes feature that enforces
three predefined security levels (Privileged, Baseline, Restricted) at the
namespace level. They are simple to set up but limited in what they can enforce.
OPA Gatekeeper is a general-purpose policy engine that can enforce any custom
policy written in Rego. It can enforce rules beyond pod security (required labels,
image registries, resource limits, naming conventions, etc.). Use Pod Security
Standards as a baseline and Gatekeeper for organization-specific policies.

### Question 5
What should a CI/CD pipeline do when Trivy finds a CRITICAL vulnerability?

**Answer:** The pipeline should fail the build (`trivy image --exit-code 1
--severity CRITICAL`), preventing the vulnerable image from being deployed.
The build failure should include: the CVE identifier, the affected package and
version, whether a fix is available (fixed version), and a link to the CVE
details. If a fix is available, the developer updates the base image or
dependency. If no fix is available, the team must assess the risk: is the
vulnerable component reachable? Is there a workaround? Can the CVE be accepted
with a documented risk acceptance? The key principle is that CRITICAL
vulnerabilities should never reach production without explicit, documented
acceptance.
