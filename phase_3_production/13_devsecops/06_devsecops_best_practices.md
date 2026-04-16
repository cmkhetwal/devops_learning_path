# DevSecOps Best Practices: Building a Secure Software Delivery Pipeline

## Why This Matters in DevOps

The previous lessons covered individual security tools and techniques. This
lesson ties them together into a cohesive DevSecOps program. Having Trivy
installed is not DevSecOps. Having Trivy in CI/CD that fails builds, with a
triage process, SLA for fixes, dashboards for tracking, and a team culture
that cares about security -- that is DevSecOps.

A DevSecOps program is measured not by the number of scanners running but by
the mean time to remediate vulnerabilities, the percentage of builds that pass
security gates on the first try, and the number of security incidents that reach
production. This lesson covers the operational practices, organizational
structures, and continuous improvement processes that make DevSecOps work at
scale.

---

## Core Concepts

### Security Gates in CI/CD

Security gates are automated checkpoints in the CI/CD pipeline that prevent
insecure code from progressing. Each gate has defined criteria for pass/fail:

```
  Code ──→ [Gate 1] ──→ Build ──→ [Gate 2] ──→ Test ──→ [Gate 3] ──→ Deploy
              │                      │                      │
         Pre-commit            Build-time              Pre-deploy
         - Secret scan         - SAST scan              - DAST scan
         - Lint rules          - SCA scan                - Pen test (manual)
                               - Container scan          - Compliance check
                               - License check           - Image signature
                               - SBOM generation         - Policy validation
```

Gate configuration for different severity levels:

```yaml
# security-gates.yaml - Define gate criteria
gates:
  pre-commit:
    secret-scan:
      action: block        # Never allow secrets to be committed
    semgrep-quick:
      severity: critical
      action: block

  build:
    sast:
      severity: critical
      action: block         # Fail the build
      severity: high
      action: warn          # Warn but allow
    sca:
      severity: critical
      action: block
      severity: high
      action: block
      max-age-days: 30      # High vuln older than 30 days blocks
    container-scan:
      severity: critical
      action: block
      severity: high
      action: warn

  pre-deploy:
    image-signature:
      action: block         # Unsigned images cannot deploy
    dast:
      severity: high
      action: block
    compliance:
      action: block         # Must pass all compliance checks
```

### Vulnerability Management

Finding vulnerabilities is easy. Managing them is hard. A vulnerability
management program defines how findings flow from detection to resolution:

```
Discovery → Triage → Prioritization → Assignment → Remediation → Verification
    │          │           │               │              │              │
  Scanner    Is it      Risk score      Who fixes     Fix or         Rescan
  finds it   real?      (CVSS +         it? When?     accept risk    and close
             False      context)
             positive?
```

#### Triage Process

Not every finding is actionable. Triage evaluates each finding:

1. **Is it a true positive?** - Verify the finding is real, not a scanner error.
2. **Is it exploitable?** - Can the vulnerability be reached in your context?
3. **Is there a fix?** - Is a patched version available?
4. **What is the impact?** - What happens if it is exploited?

#### SLA for Fixes

Define time-to-remediate based on severity:

| Severity | SLA | Example |
|---|---|---|
| Critical (CVSS 9.0-10.0) | 24 hours | Remote Code Execution in public API |
| High (CVSS 7.0-8.9) | 7 days | SQL injection in authenticated endpoint |
| Medium (CVSS 4.0-6.9) | 30 days | Information disclosure in error messages |
| Low (CVSS 0.1-3.9) | 90 days | Missing security header |

```yaml
# Example: Tracking SLAs in a GitHub issue template
name: Security Vulnerability
about: Report a security vulnerability finding
labels: security
body:
  - type: dropdown
    id: severity
    attributes:
      label: Severity
      options:
        - Critical (24h SLA)
        - High (7d SLA)
        - Medium (30d SLA)
        - Low (90d SLA)
  - type: input
    id: cve
    attributes:
      label: CVE ID (if applicable)
  - type: textarea
    id: details
    attributes:
      label: Vulnerability Details
  - type: textarea
    id: remediation
    attributes:
      label: Recommended Fix
```

### Security Dashboards

Dashboards provide visibility into the security posture of your applications:

```
┌─────────────────────────────────────────────────────────┐
│                 Security Dashboard                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Open Vulnerabilities          SLA Compliance            │
│  ┌────────────────────┐       ┌────────────────────┐    │
│  │ Critical: 2 (!)    │       │ Within SLA: 85%    │    │
│  │ High:     12       │       │ Overdue:    15%    │    │
│  │ Medium:   45       │       │ Oldest:     12 days│    │
│  │ Low:      89       │       └────────────────────┘    │
│  └────────────────────┘                                  │
│                                                          │
│  Trend (Last 30 Days)          Build Security Rate       │
│  ┌────────────────────┐       ┌────────────────────┐    │
│  │ ▂▃▅▆▇▆▅▄▃▂▁▂▃▃▃▂ │       │ Pass: 92%          │    │
│  │ New: 15  Fixed: 28│       │ Fail: 8%           │    │
│  │ Net: -13 (better) │       │ Goal: 95%          │    │
│  └────────────────────┘       └────────────────────┘    │
│                                                          │
│  Top Affected Repositories     Scanner Coverage          │
│  ┌────────────────────┐       ┌────────────────────┐    │
│  │ 1. api-gateway  15 │       │ SAST:    100%      │    │
│  │ 2. user-service 12 │       │ SCA:     100%      │    │
│  │ 3. payment-svc   8 │       │ Container: 95%     │    │
│  │ 4. frontend      5 │       │ DAST:     60%      │    │
│  └────────────────────┘       └────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

Key metrics to track:

| Metric | What It Measures | Target |
|---|---|---|
| Mean Time to Remediate (MTTR) | Average time from detection to fix | <7 days for high |
| Vulnerability density | Vulns per 1,000 lines of code | Decreasing trend |
| Build pass rate | % of builds passing security gates | >95% |
| Scanner coverage | % of repos with automated scanning | 100% |
| SLA compliance | % of vulns fixed within SLA | >90% |
| Recurrence rate | % of previously fixed vulns reappearing | <5% |
| False positive rate | % of findings that are not real | <20% |

### Compliance as Code

Compliance requirements should be expressed as automated policies, not manual
checklists:

```yaml
# OPA/Rego policy for PCI DSS compliance
# Requirement 6.5.1: Injection flaws
package pci.requirement_6_5_1

violation[msg] {
    input.scan_results.sast.findings[_].category == "injection"
    input.scan_results.sast.findings[_].severity == "high"
    msg := "PCI DSS 6.5.1: Injection vulnerability found - must be remediated"
}

# Requirement 6.5.3: Insecure cryptographic storage
violation[msg] {
    input.scan_results.sast.findings[_].category == "crypto"
    input.scan_results.sast.findings[_].cwe == "CWE-327"
    msg := "PCI DSS 6.5.3: Insecure cryptography detected"
}

# Requirement 6.6: Public-facing application security
violation[msg] {
    input.scan_results.dast == null
    input.deployment.public_facing == true
    msg := "PCI DSS 6.6: Public-facing apps must have DAST scanning"
}
```

```yaml
# Kyverno policy for SOC 2 compliance
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: soc2-controls
  annotations:
    soc2.control: "CC6.1,CC6.3"
spec:
  validationFailureAction: Enforce
  rules:
    - name: require-encryption-at-rest
      match:
        resources:
          kinds: [PersistentVolumeClaim]
      validate:
        message: "SOC 2 CC6.1: Storage must be encrypted"
        pattern:
          spec:
            storageClassName: "encrypted-*"

    - name: require-resource-limits
      match:
        resources:
          kinds: [Pod]
      validate:
        message: "SOC 2 CC6.3: Containers must have resource limits"
        pattern:
          spec:
            containers:
              - resources:
                  limits:
                    cpu: "?*"
                    memory: "?*"
```

### Penetration Testing Basics

Penetration testing (pen testing) is manual or semi-automated testing by
security professionals who attempt to exploit vulnerabilities:

| Type | Scope | Frequency | Who |
|---|---|---|---|
| Network pen test | Infrastructure, firewalls, services | Annually | External firm |
| Application pen test | Web/mobile apps, APIs | Per major release | External firm or internal |
| Cloud pen test | Cloud configuration, IAM, S3 | Annually | External firm |
| Red team exercise | Full-scope attack simulation | Annually | Specialized team |
| Bug bounty | Public-facing assets | Continuous | External researchers |

Pen testing workflow:

```
1. Scope Definition  → What systems are in scope? What is off limits?
2. Reconnaissance    → Gather information about the target
3. Vulnerability ID  → Identify potential attack vectors
4. Exploitation      → Attempt to exploit vulnerabilities
5. Post-exploitation → Assess impact (data access, lateral movement)
6. Reporting         → Document findings, severity, and remediation
7. Remediation       → Fix identified vulnerabilities
8. Retest            → Verify fixes are effective
```

### Bug Bounty Programs

Bug bounty programs pay external researchers to find and report vulnerabilities:

```
Program Structure:
  Scope:       → Which assets are eligible (e.g., *.example.com, API)
  Exclusions:  → What is not eligible (DoS testing, social engineering)
  Rewards:     → Payment based on severity
  Rules:       → Responsible disclosure requirements
  SLA:         → Response time commitments

Typical Rewards:
  Critical: $5,000 - $50,000   (RCE, auth bypass, data breach)
  High:     $1,000 - $10,000   (SQL injection, stored XSS, SSRF)
  Medium:   $500 - $2,000      (Reflected XSS, CSRF, info disclosure)
  Low:      $100 - $500        (Missing headers, verbose errors)

Platforms:
  - HackerOne (most popular)
  - Bugcrowd
  - Synack (managed)
  - GitHub Security Advisories (for open source)
```

### Incident Response Plan

Every organization needs an incident response plan before an incident occurs:

```
Phase 1: Preparation
  - Incident response team defined
  - Communication channels established
  - Playbooks written for common scenarios
  - Tools and access pre-provisioned

Phase 2: Detection & Analysis
  - Alert triggers from monitoring/SIEM
  - Initial triage: severity classification
  - Evidence collection and preservation
  - Scope determination (what is affected?)

Phase 3: Containment
  - Short-term: isolate affected systems
  - Long-term: apply temporary fixes
  - Preserve evidence for forensics

Phase 4: Eradication
  - Remove threat from all systems
  - Patch vulnerabilities
  - Reset compromised credentials
  - Verify removal

Phase 5: Recovery
  - Restore systems from clean backups
  - Monitor for recurrence
  - Gradually restore access

Phase 6: Post-Incident
  - Blameless post-mortem
  - Root cause analysis
  - Update playbooks
  - Implement preventive measures
```

### Building a Security Champion Program

Security champions are developers who volunteer to be the security point of
contact for their team:

```
Security Champion Responsibilities:
  1. Attend monthly security training/sync
  2. Review security-related code changes on their team
  3. Triage security scanner findings for their services
  4. Advocate for security best practices
  5. Escalate concerns to the security team
  6. Share knowledge (lunch-and-learns, documentation)

Program Structure:
  - 1 champion per development team (5-10 engineers)
  - Monthly champion meetup (1 hour)
  - Quarterly training (half day)
  - Annual security conference attendance
  - Recognition (title, badge, bonus)

Success Metrics:
  - MTTR for security findings decreases
  - Build security pass rate increases
  - Fewer production security incidents
  - More security-related PRs from developers
  - Higher security awareness survey scores
```

### Security Certifications

Relevant certifications for DevSecOps engineers:

| Certification | Focus | Level | Provider |
|---|---|---|---|
| CompTIA Security+ | Broad security fundamentals | Entry | CompTIA |
| CKS (Certified Kubernetes Security) | Kubernetes security | Intermediate | CNCF |
| AWS Security Specialty | AWS security services | Intermediate | AWS |
| CISSP | Enterprise security management | Advanced | (ISC)2 |
| CEH (Certified Ethical Hacker) | Penetration testing | Intermediate | EC-Council |
| OSCP | Hands-on penetration testing | Advanced | OffSec |
| GIAC (various) | Specialized security domains | Various | SANS Institute |

---

## Step-by-Step Practical

### Building a Complete Security Pipeline

```yaml
# .github/workflows/devsecops-pipeline.yaml
name: DevSecOps Pipeline
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

permissions:
  contents: read
  security-events: write
  id-token: write

jobs:
  # Gate 1: Pre-build security checks
  pre-build:
    name: Pre-Build Security
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Secret scanning (gitleaks)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: SAST (Semgrep)
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/owasp-top-ten
          generateSarif: true

      - name: Upload SAST results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: semgrep.sarif
          category: sast

  # Gate 2: Build and scan
  build-and-scan:
    name: Build & Container Scan
    needs: pre-build
    runs-on: ubuntu-latest
    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Dependency scan (pip-audit)
        run: |
          pip install -r requirements.txt
          pip install pip-audit
          pip-audit --strict --format json --output pip-audit.json || true
          pip-audit --strict

      - name: Build container image
        id: build
        run: |
          docker build -t myapp:${{ github.sha }} .
          echo "digest=$(docker inspect --format='{{index .RepoDigests 0}}' myapp:${{ github.sha }} 2>/dev/null || echo 'local')" >> $GITHUB_OUTPUT

      - name: Container scan (Trivy)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
          format: 'sarif'
          output: 'trivy.sarif'

      - name: Upload container scan results
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: trivy.sarif
          category: container

      - name: Generate SBOM
        run: |
          curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
          syft myapp:${{ github.sha }} -o cyclonedx-json > sbom.cdx.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v4
        with:
          name: sbom
          path: sbom.cdx.json

  # Gate 3: Dynamic testing
  dast:
    name: DAST (OWASP ZAP)
    needs: build-and-scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Start application
        run: |
          docker build -t myapp:test .
          docker run -d -p 8080:8080 --name myapp myapp:test
          for i in $(seq 1 30); do
            curl -s http://localhost:8080/health && break || sleep 2
          done

      - name: OWASP ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.11.0
        with:
          target: 'http://localhost:8080'
          fail_action: true

      - name: Cleanup
        if: always()
        run: docker stop myapp || true

  # Gate 4: Sign and deploy
  sign-and-deploy:
    name: Sign & Deploy
    needs: [pre-build, build-and-scan, dast]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Install Cosign
        uses: sigstore/cosign-installer@v3

      - name: Build and push image
        run: |
          docker build -t ghcr.io/${{ github.repository }}:${{ github.sha }} .
          echo "${{ secrets.GITHUB_TOKEN }}" | docker login ghcr.io -u $ --password-stdin
          docker push ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: Sign image (keyless)
        run: cosign sign ghcr.io/${{ github.repository }}:${{ github.sha }}
        env:
          COSIGN_EXPERIMENTAL: 1

      - name: Download SBOM
        uses: actions/download-artifact@v4
        with:
          name: sbom

      - name: Attest SBOM
        run: |
          cosign attest \
            --predicate sbom.cdx.json \
            --type cyclonedx \
            ghcr.io/${{ github.repository }}:${{ github.sha }}

      - name: Deploy to production
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
          aws-region: us-east-1

      - name: Helm deploy
        run: |
          aws eks update-kubeconfig --name production
          helm upgrade --install myapp ./chart \
            --set image.tag=${{ github.sha }} \
            --atomic --timeout 5m
```

### Setting Up a Security Dashboard with Grafana

```yaml
# Prometheus rules for security metrics
groups:
  - name: security_metrics
    rules:
      - record: security:vulnerabilities:total
        expr: sum(trivy_vulnerability_count) by (severity, repository)

      - record: security:build_pass_rate
        expr: |
          sum(rate(ci_builds_total{security_gate="pass"}[7d]))
          / sum(rate(ci_builds_total[7d]))

      - record: security:mttr_days
        expr: |
          avg(time() - security_vulnerability_created_timestamp)
          by (severity) / 86400

      - alert: CriticalVulnerabilityOverdue
        expr: |
          security:vulnerability_age_days{severity="critical"} > 1
        labels:
          severity: critical
        annotations:
          summary: "Critical vulnerability exceeds 24-hour SLA"
          description: "{{ $labels.repository }} has a critical vulnerability older than 24 hours"
```

---

## Exercises

### Exercise 1: Security Gate Design
Design a complete set of security gates for a CI/CD pipeline. For each gate,
define: what scanners run, what severity levels block the pipeline, what
exceptions are allowed, and how exceptions are documented and approved.

### Exercise 2: Vulnerability Management SLA
Create a vulnerability management policy for your team. Define: severity levels,
SLA for each level, triage process, escalation path, exception/risk acceptance
process, and metrics to track. Implement the SLA as a GitHub Actions workflow
that creates issues with due dates based on severity.

### Exercise 3: Compliance as Code
Choose a compliance framework (SOC 2, PCI DSS, or HIPAA). Select 10 technical
controls and implement each as either a Kyverno/OPA policy, a CI/CD gate, or
a monitoring alert. Document the mapping between the compliance requirement
and the automated control.

### Exercise 4: Incident Response Tabletop
Write an incident response playbook for a container image supply chain attack.
The scenario: a popular base image on Docker Hub is discovered to have a
backdoor. Your playbook should cover: detection, scope assessment, containment
(which images are affected?), eradication (rebuild with clean base), recovery,
and post-incident improvements.

### Exercise 5: Security Champion Program
Design a security champion program for a 50-person engineering organization
with 6 teams. Define: selection criteria, training curriculum (6-month plan),
meeting cadence, responsibilities, recognition/rewards, and success metrics.
Create the presentation you would use to pitch this program to engineering
leadership.

---

## Knowledge Check

### Question 1
What are the key components of a vulnerability management program?

**Answer:** A vulnerability management program consists of: (1) Discovery --
automated scanners (SAST, SCA, DAST, container scanning) continuously finding
vulnerabilities. (2) Triage -- evaluating each finding for true/false positive
status and exploitability. (3) Prioritization -- assigning risk scores based
on CVSS, context (is it public-facing?), and exploitability. (4) SLA -- defined
time-to-remediate for each severity level (24 hours for critical, 7 days for
high, etc.). (5) Assignment -- routing findings to the responsible team.
(6) Remediation -- fixing the vulnerability or accepting the risk with
documentation. (7) Verification -- rescanning to confirm the fix.
(8) Metrics -- tracking MTTR, SLA compliance, vulnerability density, and trends.

### Question 2
Why is "compliance as code" important?

**Answer:** Manual compliance audits are periodic (annual or quarterly),
expensive, and provide only a point-in-time snapshot. Between audits,
compliance can drift without detection. Compliance as code expresses compliance
requirements as automated policies (OPA, Kyverno, CI/CD gates) that are
evaluated continuously. Every deployment is checked against compliance policies.
Non-compliant configurations are blocked before they reach production. This
provides continuous assurance instead of periodic snapshots, reduces audit
preparation effort (evidence is automatically generated), and catches
compliance violations immediately rather than months later during an audit.

### Question 3
What is a security champion program and why does it scale better than a
centralized security team?

**Answer:** A security champion program designates one developer per team as
the security point of contact. Champions receive additional security training
and serve as a bridge between the security team and development teams. This
scales better because: a centralized security team of 3-5 people cannot review
code for 50+ developers. Champions distribute security knowledge across the
organization. They provide immediate security feedback within their team
(no waiting for a security review queue). They understand their team's codebase
and business context better than external reviewers. They shift security left
by embedding it in daily development, not treating it as an external gate.

### Question 4
What are the phases of an incident response plan?

**Answer:** The six phases are: (1) Preparation -- defining the team, playbooks,
tools, and communication channels before an incident occurs. (2) Detection and
Analysis -- identifying the incident through monitoring, triaging severity,
collecting evidence, and determining scope. (3) Containment -- short-term
isolation (blocking network access, revoking credentials) and long-term
containment (applying temporary patches). (4) Eradication -- removing the threat
from all systems, patching vulnerabilities, and resetting compromised credentials.
(5) Recovery -- restoring systems from clean backups, monitoring for recurrence,
and gradually restoring access. (6) Post-Incident -- conducting a blameless
post-mortem, performing root cause analysis, updating playbooks, and implementing
preventive measures.

### Question 5
How should security scanner false positive rates be managed without creating
alert fatigue?

**Answer:** Manage false positives through a multi-layered approach:
(1) Tune scanner rules -- disable rules that consistently produce false positives
in your codebase. (2) Use tool-specific suppression with documentation --
Semgrep's `# nosemgrep: rule-id`, Trivy's `.trivyignore`, etc. Every suppression
must include a comment explaining why it is a false positive. (3) Create a
baseline -- accept existing findings and only alert on new findings.
(4) Layer scanners -- use SAST for detection and DAST for confirmation;
a finding confirmed by both is high-confidence. (5) Regular review -- quarterly
review of suppressed findings to ensure they are still valid. (6) Track metrics
-- if the false positive rate exceeds 20%, invest in tuning or switch tools.
The goal is to maintain developer trust in the scanning results; if developers
learn to ignore alerts, the security program loses effectiveness.
