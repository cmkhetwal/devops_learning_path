# AI-Assisted Development for DevOps

## Why This Matters in DevOps

AI code assistants have become the most impactful productivity tool in a DevOps engineer's toolkit. GitHub Copilot, Claude, and similar tools can generate Dockerfiles, Kubernetes manifests, Terraform configurations, CI/CD pipelines, and shell scripts in seconds. Studies show 30-55% productivity improvements for routine DevOps tasks. However, blindly accepting AI-generated infrastructure code is dangerous -- hallucinated configurations, security blind spots, and outdated patterns can cause outages and breaches. This lesson teaches you to use AI effectively while maintaining the judgment that keeps production safe.

---

## Core Concepts

### AI for DevOps Code Generation

```
Task                          AI Effectiveness    Human Review Priority
─────────────────────────────────────────────────────────────────────────
Dockerfiles                   High (90%+ correct)  Medium (check base images)
K8s Deployments               High (85%+)          High (resource limits, security)
Helm charts                   Medium (75%+)        High (values, templates)
Terraform modules             Medium (70%+)        Very High (state, dependencies)
CI/CD workflows               High (85%+)          Medium (secrets, permissions)
Shell scripts                 High (90%+)          Medium (error handling)
Prometheus alert rules        Medium (70%+)        High (thresholds, labels)
Security policies (OPA)       Low-Medium (60%+)    Critical (logic correctness)
```

### Prompt Engineering for Infrastructure Code

Effective prompts for DevOps code generation follow this pattern:

```
Template:
─────────
Context: [technology, environment, constraints]
Task: [specific action needed]
Requirements: [security, performance, compliance]
Format: [YAML, HCL, Python, specific structure]
```

**Example 1: Dockerfile Generation**

```
Prompt:
"Generate a production Dockerfile for a Python FastAPI application.
Requirements:
- Multi-stage build for minimal image size
- Non-root user
- Health check endpoint at /health
- Pin all package versions
- Use Python 3.12 slim base
- Copy only necessary files (exclude tests, docs)
- Set proper SIGTERM handling"
```

AI output (verify each line):
```dockerfile
# Stage 1: Build
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production
FROM python:3.12-slim
LABEL maintainer="platform-team@mycompany.com"

# Security: non-root user
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Copy only installed packages
COPY --from=builder /install /usr/local

# Copy application code (exclude unnecessary files)
COPY src/ ./src/

# Security: non-root execution
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

EXPOSE 8080

# Proper signal handling
STOPSIGNAL SIGTERM
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

**Example 2: Kubernetes Manifest Generation**

```
Prompt:
"Generate a production Kubernetes deployment for a Python web service.
Requirements:
- 3 replicas across availability zones
- Resource requests and limits
- Liveness and readiness probes
- Pod disruption budget (allow 1 unavailable)
- Anti-affinity to spread across nodes
- Security context (non-root, read-only filesystem)
- Graceful shutdown (30s termination period)"
```

**Example 3: Terraform Module Generation**

```
Prompt:
"Generate a Terraform module for an AWS RDS PostgreSQL instance.
Requirements:
- Multi-AZ for production
- Encrypted storage with KMS
- Automated backups (30 days retention)
- Parameter group with performance tuning
- Security group allowing access from specific CIDR
- CloudWatch alarms for CPU, connections, storage
- Outputs: endpoint, port, connection string
- Variables with descriptions and validation"
```

### AI Code Review for Infrastructure

Use AI to review infrastructure code for common mistakes:

```
Review Prompt:
"Review this Terraform code for:
1. Security issues (open ports, missing encryption, public access)
2. Cost optimization (over-provisioned resources, missing auto-scaling)
3. Reliability (single points of failure, missing backups)
4. Best practices (naming conventions, tagging, modularization)
5. Potential state management issues

[paste code here]"
```

### AI-Generated Documentation

```
Prompt:
"Generate a runbook for the following Kubernetes deployment.
Include:
1. Service description (what it does, who owns it)
2. Architecture diagram (text-based)
3. Common failure modes and remediation steps
4. How to scale up/down
5. How to access logs and metrics
6. Emergency contacts

[paste deployment YAML here]"
```

### Limitations and Risks

```
Risk                           Example                        Mitigation
──────────────────────────────────────────────────────────────────────────
Hallucinated configs           AI generates non-existent       Always validate against
                               Terraform resource type         official documentation

Outdated patterns              AI suggests deprecated          Check version compatibility
                               K8s API version (v1beta1)       before applying

Security blind spots           AI omits encryption,            Run security scanning
                               uses default passwords          (checkov, tfsec) on output

Over-provisioned resources     AI defaults to large            Review instance sizes
                               instance types "to be safe"     against actual requirements

Missing error handling         AI shell scripts lack           Test failure scenarios
                               set -euo pipefail               manually

Confidentiality                Pasting production configs      Use AI tools with
                               into public AI tools            enterprise/private instances
```

---

## Step-by-Step Practical

### Using AI to Generate and Review Infrastructure Code

**Step 1: Generate a Complete EKS Terraform Module**

```
Prompt to AI:
"Generate a Terraform module for AWS EKS with:
- Managed node groups (general + spot)
- VPC with public and private subnets (3 AZs)
- IRSA (IAM Roles for Service Accounts) enabled
- Cluster autoscaler IAM role
- EBS CSI driver add-on
- CoreDNS and kube-proxy add-ons
- CloudWatch logging enabled
- Variables for cluster name, version, node instance types
- Security: encrypt secrets, restrict public API access"
```

**Step 2: Review the Generated Code**

```bash
# Save AI-generated code to files, then scan
# Install security scanner
pip install checkov

# Scan Terraform code
checkov -d ./terraform/ --framework terraform

# Expected output:
# Passed checks: 25
# Failed checks: 3
# - CKV_AWS_39: "Ensure Amazon EKS Secrets are encrypted"
# - CKV_AWS_58: "Ensure EKS endpoint is not publicly accessible"
# - CKV_AWS_37: "Ensure Amazon EKS control plane logging enabled"
```

**Step 3: Fix Issues Identified by Scanner**

```
Prompt:
"The following Terraform code failed these security checks:
1. CKV_AWS_39: EKS secrets not encrypted
2. CKV_AWS_58: EKS endpoint publicly accessible
3. CKV_AWS_37: Control plane logging not enabled

Fix these issues while maintaining the existing functionality.
[paste code]"
```

**Step 4: Generate Tests for the Infrastructure**

```
Prompt:
"Generate Terraform test files for this EKS module using
terraform test (HCL test framework). Test:
1. Cluster is created with correct version
2. Node groups have expected instance types
3. VPC has 3 AZs
4. Secrets encryption is enabled
5. Public endpoint is disabled"
```

**Step 5: Validate with Manual Review Checklist**

```markdown
## AI-Generated Code Review Checklist

### Security
- [ ] No hardcoded credentials or secrets
- [ ] Encryption enabled for data at rest and in transit
- [ ] Least-privilege IAM policies
- [ ] Network access restricted (no 0.0.0.0/0 on SSH)
- [ ] Security groups follow principle of least privilege

### Reliability
- [ ] Multi-AZ deployment
- [ ] Auto-scaling configured
- [ ] Health checks defined
- [ ] Backup and recovery configured
- [ ] Graceful shutdown handling

### Cost
- [ ] Instance types appropriate for workload
- [ ] Auto-scaling to zero for non-production
- [ ] Storage types and sizes reasonable
- [ ] Data transfer optimized

### Compliance
- [ ] Required tags present
- [ ] Logging enabled
- [ ] Naming conventions followed
- [ ] Resource versions up to date
```

---

## Exercises

1. **Prompt Engineering Lab**: Write prompts to generate: (a) a production Dockerfile, (b) a Kubernetes HPA configuration, (c) a GitHub Actions workflow with matrix testing. Review each output for correctness and security.

2. **AI Code Review**: Take an existing Terraform module and ask AI to review it. Compare the AI review findings with the output of `checkov` or `tfsec`. Document the overlap and gaps.

3. **Documentation Generation**: Use AI to generate a complete runbook for one of your production services. Have a team member follow the runbook during a simulated incident. Document where the AI-generated documentation was helpful and where it was wrong or incomplete.

4. **Security Blind Spot Testing**: Generate 10 Kubernetes manifests using AI and run them through `kubesec scan` and `checkov`. Track: what percentage have security issues? What are the most common blind spots?

5. **Comparative Analysis**: Generate the same Terraform module using three different AI tools (Copilot, Claude, Gemini). Compare: correctness, security posture, code quality, and documentation quality.

---

## Knowledge Check

**Q1: What are the main risks of using AI to generate infrastructure code?**

<details>
<summary>Answer</summary>

Five main risks: (1) **Hallucinated configurations** -- AI may generate resource types, parameters, or API versions that do not exist, causing deployment failures. (2) **Security blind spots** -- AI often omits encryption, uses default passwords, or creates overly permissive security groups. (3) **Outdated patterns** -- AI training data may include deprecated approaches (old API versions, removed features). (4) **Over-provisioning** -- AI tends to suggest larger instance types than needed. (5) **Confidentiality** -- pasting production configurations into public AI tools may expose sensitive information. Mitigation: always run security scanners (checkov, tfsec), validate against official documentation, and maintain a human review checklist.
</details>

**Q2: How should you structure prompts for infrastructure code generation?**

<details>
<summary>Answer</summary>

Effective prompts include four elements: (1) **Context** -- specify the technology (Terraform, Kubernetes), cloud provider (AWS, GCP), and environment (production, development). (2) **Task** -- clearly state what you need (create an EKS cluster, write a Dockerfile). (3) **Requirements** -- list specific constraints: security (encryption, non-root), performance (instance types, scaling), compliance (tagging, logging), and reliability (multi-AZ, backups). (4) **Format** -- specify the output format and structure (HCL module with variables and outputs, YAML with comments). The more specific your requirements, the better the output. Vague prompts produce generic, insecure code.
</details>

**Q3: Why should AI-generated infrastructure code always be scanned before deployment?**

<details>
<summary>Answer</summary>

Because AI models optimize for plausibility, not security. AI generates code that looks correct and often works, but may contain security vulnerabilities that are not obvious on visual inspection. Security scanners (checkov, tfsec, kubesec, trivy) check against databases of known security best practices and compliance requirements. Common issues found: missing encryption at rest, public S3 buckets, overly permissive IAM policies, missing logging, exposed API endpoints, and default credentials. The scanning step catches issues that even experienced engineers might miss during code review, providing defense in depth.
</details>

**Q4: How effective is AI at generating different types of DevOps code?**

<details>
<summary>Answer</summary>

Effectiveness varies by task: Dockerfiles and shell scripts are highly effective (90%+ correct) because they follow well-documented patterns with extensive training data. Kubernetes manifests are good (85%+) for standard resources but weaker for complex CRDs or operator configurations. CI/CD workflows are good (85%+) for major platforms but may use outdated action versions. Terraform is moderate (70%+) because it requires understanding provider-specific details, state implications, and cross-resource dependencies. Security policies (OPA, Kyverno) are the weakest (60%+) because they require understanding the logic of what should be allowed/denied. General rule: AI is best at generating boilerplate and worst at encoding complex business logic.
</details>
