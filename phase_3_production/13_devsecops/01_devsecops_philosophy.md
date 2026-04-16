# DevSecOps Philosophy: Security as a Shared Responsibility

## Why This Matters in DevOps

In traditional software organizations, security is a gate at the end of the
development process. A security team reviews the application weeks before
release, finds vulnerabilities, and sends the project back for fixes. This
creates delays, antagonism between teams, and a false sense of security (the
review is a snapshot, not continuous protection).

DevSecOps integrates security into every stage of the software delivery lifecycle.
Security is not a separate team's problem -- it is everyone's responsibility.
Every developer writes secure code, every pipeline checks for vulnerabilities,
every deployment enforces security policies, and every runtime environment is
monitored for threats.

This shift is not optional. The cost of fixing a vulnerability increases
exponentially the later it is discovered: $100 in development, $1,500 in testing,
$10,000 in staging, and $100,000+ in production (including incident response,
customer notification, and reputation damage). DevSecOps is fundamentally about
economics: find and fix security issues early, when they are cheap.

---

## Core Concepts

### What Is DevSecOps?

DevSecOps is the practice of integrating security into DevOps workflows:

```
Traditional:
  Plan → Code → Build → Test → Release → [Security Review] → Deploy → Monitor
  (Security is a bottleneck at the end)

DevSecOps:
  Plan         → Threat modeling, security requirements
  Code         → Secure coding standards, IDE security plugins, pre-commit hooks
  Build        → SAST, dependency scanning, container scanning
  Test         → DAST, penetration testing, security integration tests
  Release      → Image signing, SBOM generation, compliance checks
  Deploy       → Policy enforcement, admission controllers, runtime policies
  Monitor      → Runtime security, anomaly detection, incident response
  (Security at every stage)
```

### Shift-Left Security

"Shift left" means moving security activities earlier (to the left) in the
development lifecycle:

```
                           Cost to Fix
                               │
  $100,000 ─────────────────── │ ──────────────────────────── ★ Production
                               │                          ★ Staging
                               │                     ★ Integration
                               │                ★ System Test
                               │           ★ Unit Test
      $100 ─ ★ Design/Code    │
              ─────────────────┴──────────────────────────────
              Early ◄──── Development Lifecycle ────► Late
```

Shift-left activities include:
- **Threat modeling** during design (before writing code)
- **Security linting** in the IDE (as the developer types)
- **Pre-commit hooks** that scan for secrets and vulnerabilities
- **SAST in CI** that runs on every pull request
- **Container scanning** on every image build
- **Policy-as-code** that prevents insecure configurations from being deployed

### Security in the SDLC

Each phase of the Software Development Lifecycle has specific security activities:

| SDLC Phase | Security Activities | Tools |
|---|---|---|
| Requirements | Security requirements, compliance mapping | Threat modeling frameworks |
| Design | Threat modeling, security architecture review | STRIDE, DREAD, PASTA |
| Implementation | Secure coding, code review, SAST | Semgrep, SonarQube, CodeQL |
| Testing | DAST, penetration testing, fuzzing | OWASP ZAP, Burp Suite |
| Deployment | Image signing, admission control, policy enforcement | Cosign, Kyverno, OPA |
| Operations | Runtime security, monitoring, incident response | Tetragon, Falco, SIEM |
| Maintenance | Vulnerability patching, dependency updates | Dependabot, Renovate |

### Threat Modeling

Threat modeling is a structured approach to identifying security threats:

**STRIDE** is the most common methodology:

| Threat | Description | Example |
|---|---|---|
| **S**poofing | Pretending to be someone else | Forged authentication tokens |
| **T**ampering | Modifying data or code | SQL injection, config file manipulation |
| **R**epudiation | Denying actions without proof | Inadequate audit logging |
| **I**nformation Disclosure | Exposing sensitive data | API returning credentials in errors |
| **D**enial of Service | Making services unavailable | Resource exhaustion, DDoS |
| **E**levation of Privilege | Gaining unauthorized access | Container escape, RBAC misconfiguration |

Threat modeling process:

```
1. Identify Assets     → What are we protecting? (data, services, credentials)
2. Map Architecture    → Draw the system diagram with trust boundaries
3. Identify Threats    → For each component and data flow, apply STRIDE
4. Assess Risk         → Likelihood x Impact = Risk score
5. Plan Mitigations    → For each threat, define a security control
6. Validate            → Verify mitigations are implemented and effective
```

Example threat model for a web application:

```
┌─────────────────────────────────────────────────────┐
│                    Internet                          │
│                      │                               │
│               ┌──────▼──────┐                       │
│               │   Ingress   │ ← TLS termination     │
│               │   (nginx)   │ ← Rate limiting       │
│               └──────┬──────┘                       │
│ ╔════════════════════╪══════════════════════════╗   │
│ ║ Trust Boundary     │                          ║   │
│ ║              ┌─────▼─────┐                    ║   │
│ ║              │  Frontend  │ ← Input validation ║   │
│ ║              │   (React)  │ ← CSP headers     ║   │
│ ║              └─────┬──────┘                    ║   │
│ ║                    │ API calls                 ║   │
│ ║              ┌─────▼─────┐                    ║   │
│ ║              │   API      │ ← AuthN/AuthZ     ║   │
│ ║              │  (Python)  │ ← Input validation ║   │
│ ║              └─────┬──────┘                    ║   │
│ ║                    │ SQL queries               ║   │
│ ║ ╔══════════════════╪════════════════════╗     ║   │
│ ║ ║ Data Boundary    │                    ║     ║   │
│ ║ ║            ┌─────▼─────┐              ║     ║   │
│ ║ ║            │ Database  │ ← Encryption ║     ║   │
│ ║ ║            │ (Postgres)│ ← Access ctrl║     ║   │
│ ║ ║            └───────────┘              ║     ║   │
│ ║ ╚═══════════════════════════════════════╝     ║   │
│ ╚═══════════════════════════════════════════════╝   │
└─────────────────────────────────────────────────────┘
```

### OWASP Top 10

The Open Web Application Security Project (OWASP) maintains a list of the ten
most critical web application security risks:

| # | Risk | Description | Mitigation |
|---|---|---|---|
| 1 | Broken Access Control | Users acting beyond permissions | RBAC, least privilege, testing |
| 2 | Cryptographic Failures | Weak encryption, exposed secrets | TLS everywhere, key management |
| 3 | Injection | SQL, NoSQL, OS command injection | Parameterized queries, input validation |
| 4 | Insecure Design | Flawed architecture | Threat modeling, secure design patterns |
| 5 | Security Misconfiguration | Default configs, open ports | Hardening, policy-as-code |
| 6 | Vulnerable Components | Known CVEs in dependencies | SCA scanning, dependency updates |
| 7 | Auth Failures | Broken authentication | MFA, session management, OIDC |
| 8 | Data Integrity Failures | Untrusted deserialization, unsigned updates | SBOM, code signing |
| 9 | Logging Failures | Insufficient monitoring | Centralized logging, alerting |
| 10 | SSRF | Server-Side Request Forgery | Input validation, network segmentation |

### The Cost of Late Security

```
Stage           │ Cost to Fix    │ Examples
────────────────┼────────────────┼──────────────────────────────────────
Design          │ $100           │ Architect mTLS from the start
Development     │ $500           │ Fix SQL injection in code review
CI/CD           │ $1,000         │ Fail the build on critical CVE
Staging         │ $5,000         │ Fix misconfiguration found in pen test
Production      │ $50,000+       │ Emergency patch, incident response
Breach          │ $1,000,000+    │ Customer notification, legal, fines
```

The 2023 IBM Cost of a Data Breach Report found the average cost of a data breach
is $4.45 million. Organizations with DevSecOps practices reduced this cost by
$1.68 million on average.

### Compliance Frameworks

| Framework | Focus | Key Requirements |
|---|---|---|
| **SOC 2** | Service organizations | Access controls, encryption, monitoring, incident response |
| **ISO 27001** | Information security | Risk assessment, security controls, continuous improvement |
| **PCI DSS** | Payment card data | Encryption, access control, vulnerability management, logging |
| **HIPAA** | Healthcare data | Data encryption, access controls, audit trails, breach notification |
| **GDPR** | EU personal data | Data protection, consent, right to erasure, breach notification |
| **FedRAMP** | US government cloud | Continuous monitoring, incident response, access control |

Compliance is not security. Compliance means meeting minimum requirements defined
by a framework. Security means protecting against real threats. A compliant system
can still be insecure. DevSecOps aims for actual security, with compliance as a
natural byproduct.

### Building a Security Culture

Security culture is not about tools; it is about mindset:

1. **Make security easy** - Provide secure defaults, pre-approved base images,
   security libraries, and templates that are secure by default.

2. **Make insecurity hard** - Use admission controllers to block insecure
   configurations, policy-as-code to enforce standards, and automated scanning
   to catch issues before merge.

3. **Educate continuously** - Security training, lunch-and-learns, capture-the-flag
   exercises, and shared incident post-mortems.

4. **Reward security** - Recognize developers who find and fix vulnerabilities,
   include security in performance reviews, celebrate security improvements.

5. **Blameless incidents** - When breaches happen, focus on systemic improvements,
   not individual blame. Fear of blame drives hiding vulnerabilities.

---

## Step-by-Step Practical

### Conducting a Basic Threat Model

```bash
# 1. Document the system architecture
# Create a simple architecture document

cat > architecture.md << 'EOF'
# System Architecture: E-Commerce Platform

## Components
- Frontend (React SPA, served by Nginx)
- API Gateway (Kong)
- Product Service (Python/FastAPI)
- Order Service (Go)
- Payment Service (Python, PCI-scoped)
- PostgreSQL Database
- Redis Cache
- RabbitMQ Message Queue

## Data Flows
1. User → Frontend (HTTPS)
2. Frontend → API Gateway (HTTPS)
3. API Gateway → Product Service (HTTP, internal)
4. API Gateway → Order Service (HTTP, internal)
5. Order Service → Payment Service (mTLS, PCI zone)
6. Services → PostgreSQL (TCP 5432, encrypted)
7. Services → Redis (TCP 6379, password auth)
8. Order Service → RabbitMQ (AMQP, TLS)

## Trust Boundaries
- Internet ↔ Cluster (Ingress)
- General Zone ↔ PCI Zone (Network Policy)
- Application ↔ Database (Network Policy + Auth)
EOF

# 2. Apply STRIDE to each component
cat > threat-model.md << 'EOF'
# Threat Model: E-Commerce Platform

## API Gateway
| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| Spoofing | High | JWT validation, rate limiting | Implemented |
| Tampering | Medium | Input validation, request signing | Partial |
| Repudiation | Medium | Access logging, audit trail | Implemented |
| Info Disclosure | High | Error sanitization, no stack traces | TODO |
| DoS | High | Rate limiting, WAF | Implemented |
| Elevation | Medium | RBAC, least privilege | Implemented |

## Payment Service
| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| Spoofing | Critical | mTLS, service mesh identity | Implemented |
| Tampering | Critical | Signed requests, integrity checks | TODO |
| Info Disclosure | Critical | Encryption at rest, tokenization | Implemented |
| DoS | High | Circuit breaker, bulkhead | Partial |

## Database
| Threat | Risk | Mitigation | Status |
|--------|------|------------|--------|
| Spoofing | High | Certificate auth, network policy | Implemented |
| Tampering | Critical | Audit logging, checksums | TODO |
| Info Disclosure | Critical | TDE, column-level encryption | Partial |
EOF

# 3. Prioritize by risk and create action items
cat > security-backlog.md << 'EOF'
# Security Backlog (Priority Order)

1. [CRITICAL] Payment Service - Add request signing/integrity
2. [CRITICAL] Database - Enable Transparent Data Encryption
3. [HIGH] API Gateway - Sanitize error responses
4. [HIGH] Payment Service - Add circuit breaker
5. [MEDIUM] API Gateway - Add request signing
6. [MEDIUM] Database - Add audit logging with checksums
7. [LOW] All services - Add security headers review
EOF
```

### Setting Up a Security Scanning Pipeline

```yaml
# .github/workflows/security.yaml
name: Security Scanning
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  secret-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Scan for secrets
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  dependency-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

  container-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build image
        run: docker build -t myapp:${{ github.sha }} .
      - name: Scan image with Trivy
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'myapp:${{ github.sha }}'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'
          format: 'sarif'
          output: 'trivy-results.sarif'
      - name: Upload scan results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

---

## Exercises

### Exercise 1: Threat Model
Choose a web application you are familiar with (or use the e-commerce platform
described above). Apply the STRIDE methodology to three components. For each
threat, assign a risk level (Critical/High/Medium/Low) and propose a mitigation.
Prioritize the mitigations by risk level.

### Exercise 2: OWASP Top 10 Assessment
For each of the OWASP Top 10 risks, describe one specific way it could manifest
in a Kubernetes-deployed microservices application. Then describe the DevSecOps
control that would prevent or detect it.

### Exercise 3: Compliance Mapping
Choose a compliance framework (SOC 2, PCI DSS, or HIPAA). List 10 specific
requirements and map each one to a DevSecOps tool or practice that helps meet
the requirement. For example, PCI DSS requirement 6.5.1 (injection flaws) maps
to SAST scanning with Semgrep in CI/CD.

### Exercise 4: Security Culture Assessment
Evaluate your team or organization against the five security culture principles
(make security easy, make insecurity hard, educate, reward, blameless). For
each principle, score 1-5 and describe one concrete action that would improve
the score.

### Exercise 5: Cost Analysis
Research three recent data breaches. For each, identify: what was breached,
how it was discovered, how long it took to detect, and the estimated cost.
Then identify the DevSecOps control that would have prevented or detected the
breach earlier.

---

## Knowledge Check

### Question 1
What does "shift left" mean in the context of DevSecOps?

**Answer:** "Shift left" means moving security testing and practices earlier in
the software development lifecycle, toward the left side of the timeline. Instead
of performing security reviews only before release, security activities happen
during design (threat modeling), coding (SAST, secret scanning), building
(dependency scanning, container scanning), and testing (DAST). The earlier a
vulnerability is found, the cheaper and faster it is to fix. A vulnerability
found in development costs $100 to fix; the same vulnerability found in
production can cost $50,000+ including incident response.

### Question 2
What is the STRIDE threat modeling methodology?

**Answer:** STRIDE is an acronym for six categories of threats: Spoofing
(impersonating another user or system), Tampering (unauthorized modification
of data or code), Repudiation (denying an action without adequate proof),
Information Disclosure (exposing data to unauthorized parties), Denial of
Service (making a system unavailable), and Elevation of Privilege (gaining
unauthorized access levels). During threat modeling, each component and data
flow in the system is analyzed against all six categories to systematically
identify potential threats.

### Question 3
Why is "compliance is not security" an important distinction?

**Answer:** Compliance means meeting the minimum requirements defined by a
regulatory framework (SOC 2, PCI DSS, HIPAA). These requirements are a baseline,
not a ceiling. A system can be compliant and still have significant
vulnerabilities that the framework does not cover. For example, a PCI-compliant
system might have a zero-day vulnerability in a library that PCI does not test
for. DevSecOps aims for actual security, which naturally produces compliance as
a byproduct. Organizations that target only compliance often have a false sense
of security and underinvest in practices that go beyond the checklist.

### Question 4
What are the five principles of building a security culture?

**Answer:** (1) Make security easy by providing secure defaults, pre-approved
base images, and security libraries. (2) Make insecurity hard by using admission
controllers, policy-as-code, and automated scanning to block insecure
configurations. (3) Educate continuously through training, capture-the-flag
exercises, and shared incident post-mortems. (4) Reward security by recognizing
developers who find vulnerabilities and including security in performance
reviews. (5) Blameless incidents by focusing on systemic improvements rather
than individual blame when breaches occur.

### Question 5
What is the economic argument for DevSecOps?

**Answer:** The cost of fixing a security vulnerability increases exponentially
the later it is discovered in the development lifecycle. A fix in design costs
~$100, in development ~$500, in CI ~$1,000, in staging ~$5,000, in production
~$50,000+, and after a breach $1,000,000+. The 2023 IBM Cost of a Data Breach
Report found that organizations with DevSecOps practices reduced breach costs
by $1.68 million on average. By investing in early detection (SAST, SCA,
container scanning) and prevention (policy-as-code, admission controllers),
organizations avoid the exponentially higher costs of late-stage discovery and
production incidents.
