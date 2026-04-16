# Secrets Management Philosophy

## Why This Matters in DevOps

Secret sprawl is one of the most common and dangerous problems in modern infrastructure. Every data breach investigation reveals the same patterns: hardcoded credentials in source code, unrotated API keys, shared passwords in Slack messages, and secrets stored in plaintext environment variables. The 2023 Uber breach started with a hardcoded credential in a PowerShell script. The 2024 Microsoft breach traced back to a test account without MFA. Secrets management is not a nice-to-have -- it is the foundation of your security posture. Every DevOps engineer must understand how to handle secrets correctly across applications, infrastructure, and CI/CD pipelines.

---

## Core Concepts

### What Counts as a Secret?

A secret is any piece of data that grants access to a system, resource, or capability. If it leaks, an attacker gains unauthorized access.

```
Category              Examples
─────────────────────────────────────────────────────────
Credentials           Database passwords, API keys, OAuth tokens
Certificates          TLS/SSL certificates, private keys
Cloud Credentials     AWS access keys, GCP service account keys
Infrastructure        SSH private keys, VPN certificates
Application           JWT signing keys, encryption keys
Third-party           Stripe API keys, Twilio tokens, SendGrid keys
CI/CD                 Docker Hub tokens, Helm repository passwords
Internal              Service-to-service auth tokens, mTLS certs
```

### The Problem with Hardcoded Secrets

```python
# THE WRONG WAY - hardcoded secrets (found in real codebases)
import boto3

client = boto3.client(
    's3',
    aws_access_key_id='AKIAIOSFODNN7EXAMPLE',      # NEVER DO THIS
    aws_secret_access_key='wJalrXUtnFEMI/K7MDENG',  # NEVER DO THIS
)

# THE WRONG WAY - .env files committed to git
DATABASE_URL=postgresql://admin:SuperSecret123@db.example.com:5432/prod

# THE WRONG WAY - hardcoded in Kubernetes manifests
apiVersion: v1
kind: Pod
spec:
  containers:
    - name: app
      env:
        - name: DB_PASSWORD
          value: "ProductionPassword123!"  # NEVER DO THIS
```

Statistics on secret exposure:
- GitGuardian detected 12.8 million secrets in public GitHub repositories in 2023
- Average time to exploit a leaked secret: 1 minute (automated scanners)
- Average cost of a data breach involving leaked credentials: $4.5 million

### Secret Sprawl

Secret sprawl occurs when secrets are duplicated across multiple systems without centralized management:

```
Secret Sprawl Example:
──────────────────────

Database Password "MyDBPass123"
  ├── Hardcoded in app/config.py (committed to Git)
  ├── In .env file on 3 developers' laptops
  ├── In CI/CD pipeline environment variables
  ├── In Kubernetes Secret (base64, not encrypted)
  ├── In deployment scripts on jump server
  ├── In a Slack message from 2022
  └── In a Confluence page titled "Production Credentials"

Problems:
  - Who has access? Unknown
  - When was it last rotated? Unknown
  - How to rotate without breaking things? Unclear
  - Has it been leaked? No way to tell
```

### Rotation Philosophy

Secrets should be treated as perishable, not permanent. The shorter the lifetime, the smaller the window for exploitation.

```
Secret Lifetime Spectrum:
──────────────────────────

Permanent (BAD)          Short-lived (GOOD)
◄────────────────────────────────────────────►
Static API keys          Dynamic credentials
Never rotated            Rotated every N hours
One breach = permanent   One breach = limited impact
Manual rotation          Automatic rotation

Best Practice Lifetimes:
  - Database passwords: ≤ 90 days (or use dynamic credentials)
  - API keys: ≤ 90 days
  - TLS certificates: ≤ 90 days (Let's Encrypt default)
  - OAuth tokens: ≤ 1 hour
  - Dynamic DB credentials: ≤ 1 hour (Vault)
  - Cloud session tokens: ≤ 12 hours (STS)
```

### Zero-Trust Secrets

The zero-trust approach to secrets management follows these principles:

1. **Never trust, always verify**: Every secret access is authenticated and authorized
2. **Least privilege**: Grant the minimum access needed, for the minimum time
3. **Assume breach**: Design systems to limit blast radius when secrets leak
4. **Audit everything**: Log every secret access, modification, and rotation
5. **Automate rotation**: Human-managed rotation will be skipped; automate it

### Envelope Encryption

Envelope encryption wraps your data encryption key (DEK) with a key encryption key (KEK). This is the industry standard pattern.

```
┌─────────────────────────────────────────────┐
│  Envelope Encryption                        │
│                                             │
│  Your Secret: "MyDatabasePassword"          │
│       │                                     │
│       ▼                                     │
│  Encrypted with DEK (Data Encryption Key)   │
│  → "aGVsbG8gd29ybGQ..."                    │
│       │                                     │
│       ▼                                     │
│  DEK is encrypted with KEK                  │
│  (Key Encryption Key, stored in KMS)        │
│  → Encrypted DEK stored alongside data      │
│                                             │
│  To decrypt:                                │
│  1. Send encrypted DEK to KMS              │
│  2. KMS returns decrypted DEK              │
│  3. Use DEK to decrypt the secret          │
│  4. DEK never leaves your application      │
└─────────────────────────────────────────────┘
```

Benefits:
- KEK never leaves the KMS (hardware security module)
- You can rotate KEKs without re-encrypting all data
- Different DEKs per secret limit blast radius
- Audit trail on KEK usage via KMS logs

### Secrets in Different Contexts

```
Context          Challenge                    Solution
─────────────────────────────────────────────────────────
Application      App needs DB password        Vault Agent, env injection,
                 at runtime                   SDK integration

Infrastructure   Terraform needs AWS creds    OIDC federation, short-lived
                 to provision resources       tokens, Vault dynamic secrets

CI/CD Pipeline   Pipeline needs Docker Hub    OIDC tokens, pipeline-specific
                 token to push images         short-lived credentials

Kubernetes       Pods need secrets at         External Secrets Operator,
                 startup                      Vault CSI driver, Sealed Secrets

Developer        Dev needs staging DB         Just-in-time access, temporary
                 access for debugging         credentials, access requests

GitOps           Secrets in Git repos         SOPS, Sealed Secrets, External
                 (encrypted)                  Secrets Operator
```

---

## Step-by-Step Practical

### Auditing Your Current Secret Hygiene

**Step 1: Scan for Hardcoded Secrets in Your Codebase**

```bash
# Install gitleaks
brew install gitleaks  # macOS
# or
docker pull ghcr.io/gitleaks/gitleaks:latest

# Scan your repository
gitleaks detect --source . --verbose --report-format json --report-path leaks.json

# Scan git history (finds secrets in old commits)
gitleaks detect --source . --verbose --log-opts="--all"
```

Expected output:
```
Finding:     aws_secret_access_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
Secret:      wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
RuleID:      aws-secret-access-key
Entropy:     4.5
File:        deploy/config.py
Line:        42
Commit:      abc123def456
Author:      developer@company.com
Date:        2023-06-15T10:30:00Z
```

**Step 2: Identify Secret Sprawl**

```bash
# Create a secret inventory
cat <<'EOF' > secret-inventory.yaml
secrets_inventory:
  - name: "Production Database Password"
    locations:
      - type: "environment_variable"
        system: "GitHub Actions"
        last_rotated: "2023-01-15"
        who_has_access: "all repo contributors"
      - type: "kubernetes_secret"
        system: "production cluster"
        last_rotated: "2023-01-15"
        who_has_access: "cluster admins"
      - type: "hardcoded"
        system: "app/config.py (line 42)"
        last_rotated: "never"
        who_has_access: "anyone with repo access"
    risk_level: "CRITICAL"
    recommendation: "Move to Vault with dynamic credentials"

  - name: "Stripe API Key"
    locations:
      - type: "environment_variable"
        system: "Vercel"
        last_rotated: "2022-11-01"
        who_has_access: "team leads"
    risk_level: "HIGH"
    recommendation: "Rotate immediately, move to secrets manager"
EOF
```

**Step 3: Set Up Pre-commit Hooks to Prevent Future Leaks**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
```

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Generate baseline (mark existing known secrets)
detect-secrets scan > .secrets.baseline

# Test - this commit should be blocked
echo 'AWS_SECRET_KEY="AKIAIOSFODNN7EXAMPLE"' > test.py
git add test.py
git commit -m "test"  # Should fail with gitleaks warning
```

---

## Exercises

1. **Secret Audit**: Run gitleaks against one of your repositories (or a public open-source project). Document all findings, classify them by severity, and create a remediation plan.

2. **Inventory Creation**: Create a comprehensive secrets inventory for a project you work on. List every secret, where it is stored, who has access, when it was last rotated, and what would break if it were revoked.

3. **Rotation Plan**: Design an automated rotation plan for the three most critical secrets in your organization. Include: rotation frequency, automation mechanism, notification process, and rollback procedure.

4. **Pre-commit Setup**: Configure gitleaks and detect-secrets as pre-commit hooks in a repository. Test them by attempting to commit various types of secrets (AWS keys, database URLs, API tokens).

5. **Threat Model**: Create a threat model for your application's secrets. Identify: what secrets exist, how they could be compromised, what the impact would be, and what mitigations are in place.

---

## Knowledge Check

**Q1: Why is base64 encoding (as used in Kubernetes Secrets) not encryption?**

<details>
<summary>Answer</summary>

Base64 is an encoding scheme, not encryption. It transforms binary data into ASCII text for transport but provides zero security. Anyone can decode base64 instantly: `echo "cGFzc3dvcmQ=" | base64 -d` outputs "password". Kubernetes Secrets store values in base64 by default, which means they are stored in plaintext in etcd (the Kubernetes backing store). To actually protect Kubernetes secrets, you need either: etcd encryption at rest (EncryptionConfiguration), an external secrets manager (Vault, AWS Secrets Manager), or encrypted secrets in Git (Sealed Secrets, SOPS).
</details>

**Q2: What is the difference between static and dynamic secrets?**

<details>
<summary>Answer</summary>

Static secrets are long-lived credentials created once and reused until manually rotated (e.g., a database password set during setup). Dynamic secrets are short-lived credentials generated on-demand for each client session (e.g., Vault generating a temporary database username/password that expires in 1 hour). Dynamic secrets are superior because: (1) each credential is unique per consumer, enabling attribution, (2) automatic expiration limits the blast radius of a breach, (3) no manual rotation needed, (4) revocation is granular (revoke one consumer without affecting others). Vault's dynamic secrets engine is the most common implementation.
</details>

**Q3: What is envelope encryption and why is it preferred over direct encryption?**

<details>
<summary>Answer</summary>

Envelope encryption uses two layers of keys: a Data Encryption Key (DEK) encrypts the actual secret, and a Key Encryption Key (KEK) encrypts the DEK. The KEK is stored in a Hardware Security Module (HSM) via a KMS (AWS KMS, Google Cloud KMS) and never leaves the HSM. Advantages over direct encryption: (1) key rotation is cheaper -- rotating the KEK only requires re-encrypting DEKs, not all data, (2) the KEK benefits from HSM hardware protection, (3) KMS audit logs track all key usage, (4) different DEKs per secret limit the blast radius of a compromised DEK.
</details>

**Q4: Why should secrets be rotated, and what is a good rotation frequency?**

<details>
<summary>Answer</summary>

Rotation limits the window of exploitation if a secret is compromised. If a secret is leaked but rotated within hours, the attacker's window is limited. Without rotation, a leaked secret remains valid indefinitely. Recommended frequencies: database passwords (90 days maximum, preferably dynamic/hourly), API keys (90 days), TLS certificates (90 days, automated via Let's Encrypt or cert-manager), OAuth tokens (1 hour), CI/CD tokens (per-pipeline or daily), SSH keys (90-180 days). The ideal is dynamic secrets that are created per-session and expire automatically, eliminating the need for rotation entirely.
</details>

**Q5: How do secrets end up in Git repositories, and how do you prevent it?**

<details>
<summary>Answer</summary>

Common causes: (1) developers hardcode secrets during development and forget to remove them, (2) configuration files with secrets are not in `.gitignore`, (3) secrets are pasted into code comments or documentation, (4) environment files (`.env`) are accidentally committed, (5) secrets appear in log output that is committed. Prevention requires multiple layers: (a) pre-commit hooks (gitleaks, detect-secrets) that scan for secret patterns before allowing commits, (b) CI/CD scanning that catches secrets missed by pre-commit, (c) `.gitignore` rules for `.env`, `*.pem`, `*.key` files, (d) education -- developers must understand why hardcoding is dangerous, (e) making the right way easy -- if getting a secret from Vault is harder than hardcoding, people will hardcode.
</details>
