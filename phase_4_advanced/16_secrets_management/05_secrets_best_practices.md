# Secrets Best Practices

## Why This Matters in DevOps

Knowing how to use Vault or Infisical is only part of secrets management. The other part is building a comprehensive strategy that covers rotation automation, leak detection, GitOps integration, and cloud-native secrets services. This lesson brings together all the pieces: how to detect leaked secrets before they are exploited, how to manage secrets in GitOps workflows (where everything is in Git), how to choose between cloud-native and third-party tools, and how to build a rotation strategy that actually works. These are the practices that prevent breaches.

---

## Core Concepts

### Secret Rotation Automation

Manual rotation fails because humans forget, prioritize other work, or make mistakes. Automated rotation ensures secrets change on schedule without human intervention.

```
Rotation Architecture:
──────────────────────

┌──────────────────┐     ┌──────────────────┐
│  Rotation        │────►│ Secret Store     │
│  Controller      │     │ (Vault/SM/KV)    │
│  (CronJob/Lambda)│     └────────┬─────────┘
└──────────────────┘              │
                                  ▼
                         ┌──────────────────┐
                         │ Target System    │
                         │ (Database, API)  │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ Notify/Restart   │
                         │ Consumers        │
                         └──────────────────┘
```

**AWS Secrets Manager Rotation Example:**

```python
# lambda_rotation.py
"""AWS Secrets Manager rotation Lambda for RDS PostgreSQL."""

import json
import boto3
import psycopg2
import string
import secrets


def lambda_handler(event, context):
    """Rotate a database password in Secrets Manager."""
    secret_id = event['SecretId']
    step = event['Step']
    token = event['ClientRequestToken']

    sm_client = boto3.client('secretsmanager')

    if step == 'createSecret':
        # Generate new password
        new_password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + "!@#$%")
            for _ in range(32)
        )
        current = json.loads(
            sm_client.get_secret_value(SecretId=secret_id)['SecretString']
        )
        current['password'] = new_password
        sm_client.put_secret_value(
            SecretId=secret_id,
            ClientRequestToken=token,
            SecretString=json.dumps(current),
            VersionStages=['AWSPENDING'],
        )

    elif step == 'setSecret':
        # Update the password in the database
        pending = json.loads(
            sm_client.get_secret_value(
                SecretId=secret_id, VersionStage='AWSPENDING'
            )['SecretString']
        )
        current = json.loads(
            sm_client.get_secret_value(
                SecretId=secret_id, VersionStage='AWSCURRENT'
            )['SecretString']
        )
        conn = psycopg2.connect(
            host=current['host'], port=current['port'],
            dbname=current['dbname'], user=current['username'],
            password=current['password'],
        )
        with conn.cursor() as cur:
            cur.execute(
                f"ALTER USER {current['username']} WITH PASSWORD %s",
                (pending['password'],)
            )
        conn.commit()
        conn.close()

    elif step == 'testSecret':
        # Verify the new password works
        pending = json.loads(
            sm_client.get_secret_value(
                SecretId=secret_id, VersionStage='AWSPENDING'
            )['SecretString']
        )
        conn = psycopg2.connect(
            host=pending['host'], port=pending['port'],
            dbname=pending['dbname'], user=pending['username'],
            password=pending['password'],
        )
        conn.close()

    elif step == 'finishSecret':
        sm_client.update_secret_version_stage(
            SecretId=secret_id,
            VersionStage='AWSCURRENT',
            MoveToVersionId=token,
            RemoveFromVersionId=sm_client.get_secret_value(
                SecretId=secret_id
            )['VersionId'],
        )
```

### Detecting Leaked Secrets

**Pre-commit Scanning (Prevention):**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

**CI/CD Scanning (Detection):**

```yaml
# .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  secret-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for historical scan

      - name: Gitleaks scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: TruffleHog scan
        uses: trufflesecurity/trufflehog@main
        with:
          extra_args: --only-verified
```

**TruffleHog for Deep Scanning:**

```bash
# Install TruffleHog
pip install trufflehog

# Scan a repository (including all branches and history)
trufflehog git file://. --only-verified --json

# Scan a GitHub organization
trufflehog github --org=mycompany --only-verified

# Scan filesystem
trufflehog filesystem --directory=/path/to/code --only-verified
```

### Secrets in GitOps

GitOps stores everything in Git, but secrets cannot be in Git as plaintext. Three solutions:

**1. Sealed Secrets (Bitnami)**

```
┌──────────────┐    Encrypt    ┌────────────────┐
│ Secret YAML  │──────────────►│ SealedSecret   │
│ (plaintext)  │    kubeseal   │ (encrypted)    │
└──────────────┘               └───────┬────────┘
                                       │ Commit to Git
                                       ▼
                               ┌────────────────┐
                               │ Git Repo       │
                               └───────┬────────┘
                                       │ ArgoCD sync
                                       ▼
                               ┌────────────────┐
                               │ Sealed Secrets │
                               │ Controller     │
                               │ (decrypts)     │
                               └───────┬────────┘
                                       │
                                       ▼
                               ┌────────────────┐
                               │ K8s Secret     │
                               │ (plaintext     │
                               │  in cluster)   │
                               └────────────────┘
```

```bash
# Install Sealed Secrets controller
helm install sealed-secrets sealed-secrets/sealed-secrets \
  --namespace kube-system

# Install kubeseal CLI
brew install kubeseal

# Create a regular secret
kubectl create secret generic myapp-secrets \
  --from-literal=DB_PASSWORD=SuperSecret123 \
  --dry-run=client -o yaml > secret.yaml

# Seal it (encrypt with the controller's public key)
kubeseal --format yaml < secret.yaml > sealed-secret.yaml

# sealed-secret.yaml is safe to commit to Git
cat sealed-secret.yaml
```

**2. External Secrets Operator (ESO)**

```yaml
# external-secret.yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-secrets
  namespace: myapp
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: myapp-k8s-secrets
    creationPolicy: Owner
  data:
    - secretKey: DB_PASSWORD
      remoteRef:
        key: production/myapp/database
        property: password
    - secretKey: API_KEY
      remoteRef:
        key: production/myapp/api
        property: key
---
# cluster-secret-store.yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-secrets-manager
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets
```

**3. SOPS (Secrets OPerationS)**

```bash
# Install SOPS
brew install sops

# Configure SOPS to use AWS KMS
cat > .sops.yaml <<EOF
creation_rules:
  - path_regex: \.enc\.yaml$
    kms: "arn:aws:kms:us-east-1:123456789:key/abc123-def456"
  - path_regex: \.enc\.json$
    kms: "arn:aws:kms:us-east-1:123456789:key/abc123-def456"
EOF

# Create a secrets file
cat > secrets.yaml <<EOF
db_password: SuperSecret123
api_key: sk-live-abc123
redis_password: RedisPass456
EOF

# Encrypt with SOPS
sops --encrypt secrets.yaml > secrets.enc.yaml

# The encrypted file is safe to commit
cat secrets.enc.yaml
```

Expected encrypted output:
```yaml
db_password: ENC[AES256_GCM,data:abc123==,iv:xyz...,tag:...,type:str]
api_key: ENC[AES256_GCM,data:def456==,iv:abc...,tag:...,type:str]
redis_password: ENC[AES256_GCM,data:ghi789==,iv:def...,tag:...,type:str]
sops:
    kms:
        - arn: arn:aws:kms:us-east-1:123456789:key/abc123-def456
          created_at: "2024-01-15T10:30:00Z"
    lastmodified: "2024-01-15T10:30:00Z"
    version: 3.8.1
```

### Cloud-Native Secrets Comparison

| Feature | AWS Secrets Manager | Azure Key Vault | GCP Secret Manager | Vault |
|---|---|---|---|---|
| Auto rotation | Yes (Lambda) | Yes (Functions) | No (manual) | Yes (dynamic) |
| Versioning | Yes | Yes | Yes | Yes (KV v2) |
| Encryption | AWS KMS | Azure HSM | Google KMS | Built-in |
| Audit logs | CloudTrail | Azure Monitor | Cloud Audit | Audit device |
| Cross-region | Replication | Geo-replication | Replication | Manual |
| Pricing | $0.40/secret/mo | $0.03/operation | $0.06/10k ops | Free (OSS) |
| K8s integration | ESO, ASCP | ESO, CSI | ESO, CSI | Native |
| Dynamic secrets | No | No | No | Yes |
| Multi-cloud | No | No | No | Yes |

### Choosing the Right Tool

```
Decision Tree:
──────────────

Start
  │
  ├── Single cloud, simple needs?
  │   └── Use cloud-native (AWS SM, Azure KV, GCP SM)
  │
  ├── Need dynamic credentials?
  │   └── Vault (only tool with true dynamic secrets)
  │
  ├── Need encryption as a service?
  │   └── Vault Transit engine
  │
  ├── Small team, developer-focused?
  │   └── Infisical
  │
  ├── Multi-cloud?
  │   └── Vault or Infisical (cloud-agnostic)
  │
  ├── GitOps workflow?
  │   └── External Secrets Operator + any backend
  │
  └── Kubernetes-native, minimal overhead?
      └── Sealed Secrets or ESO
```

---

## Step-by-Step Practical

### Building a Complete Secrets Pipeline

**Step 1: Set Up External Secrets Operator**

```bash
# Install ESO
helm install external-secrets external-secrets/external-secrets \
  --namespace external-secrets \
  --create-namespace
```

**Step 2: Configure with AWS Secrets Manager**

```bash
# Create a secret in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "production/myapp/database" \
  --secret-string '{"host":"db.prod.internal","port":"5432","username":"app","password":"ProdPass123!"}'

aws secretsmanager create-secret \
  --name "production/myapp/api-keys" \
  --secret-string '{"stripe":"sk-live-abc123","sendgrid":"SG.xyz789"}'
```

**Step 3: Create ClusterSecretStore and ExternalSecret**

```yaml
# Apply the secret store and external secret
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: aws-sm
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-east-1
      auth:
        jwt:
          serviceAccountRef:
            name: eso-sa
            namespace: external-secrets
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: myapp-db
  namespace: myapp
spec:
  refreshInterval: 5m
  secretStoreRef:
    name: aws-sm
    kind: ClusterSecretStore
  target:
    name: myapp-db-secret
  data:
    - secretKey: DB_HOST
      remoteRef:
        key: production/myapp/database
        property: host
    - secretKey: DB_PORT
      remoteRef:
        key: production/myapp/database
        property: port
    - secretKey: DB_USERNAME
      remoteRef:
        key: production/myapp/database
        property: username
    - secretKey: DB_PASSWORD
      remoteRef:
        key: production/myapp/database
        property: password
```

```bash
kubectl apply -f eso-config.yaml

# Verify
kubectl get externalsecret -n myapp
kubectl get secret myapp-db-secret -n myapp
```

Expected output:
```
NAME        STORE   REFRESH INTERVAL   STATUS         READY
myapp-db    aws-sm  5m                 SecretSynced   True
```

**Step 4: Set Up Secret Leak Detection Pipeline**

```yaml
# .github/workflows/secret-scan.yml
name: Secret Scanning
on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  gitleaks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Run Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}

  trufflehog:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog OSS
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified
```

---

## Exercises

1. **Sealed Secrets Pipeline**: Install Sealed Secrets in a cluster. Create a workflow where a developer encrypts secrets locally with `kubeseal`, commits to Git, ArgoCD syncs, and the controller decrypts them in the cluster.

2. **External Secrets Operator**: Set up ESO with AWS Secrets Manager (or another backend). Create ExternalSecrets for 3 applications. Modify a secret in AWS SM and verify ESO syncs it to Kubernetes within the refresh interval.

3. **Secret Scanning CI**: Add gitleaks and TruffleHog to an existing CI pipeline. Intentionally add a test secret and verify the pipeline catches it. Create a `.gitleaksignore` file for known false positives.

4. **Rotation Automation**: Implement automated rotation for a database password using either AWS Secrets Manager rotation Lambda or a Kubernetes CronJob that calls Vault's API to rotate credentials.

5. **Comprehensive Comparison**: Deploy the same application with secrets from: (a) Kubernetes native Secrets, (b) Sealed Secrets, (c) External Secrets Operator + AWS SM, (d) Vault Agent Injector. Compare: setup time, operational complexity, security posture, rotation capability.

---

## Knowledge Check

**Q1: What is the External Secrets Operator and how does it fit into GitOps?**

<details>
<summary>Answer</summary>

The External Secrets Operator (ESO) is a Kubernetes operator that syncs secrets from external secret management systems (AWS Secrets Manager, Vault, Azure Key Vault, GCP Secret Manager, Infisical) into Kubernetes Secrets. In GitOps, you commit ExternalSecret resources (which contain references to secrets, not the secrets themselves) to Git. ArgoCD/Flux syncs the ExternalSecret to the cluster, and ESO resolves it into an actual Kubernetes Secret by fetching from the external store. This solves the "secrets in Git" problem without requiring encryption (unlike Sealed Secrets or SOPS) -- the Git repo only contains pointers, not secret values.
</details>

**Q2: When should you use Sealed Secrets vs External Secrets Operator vs SOPS?**

<details>
<summary>Answer</summary>

**Sealed Secrets**: Best when you want a pure Kubernetes-native solution with no external dependencies. Secrets are encrypted specifically for your cluster. Limitation: secrets are tied to the cluster's sealing key -- if the key is lost, secrets cannot be recovered. **External Secrets Operator**: Best when you already use a cloud secret store (AWS SM, Azure KV) and want automatic sync to Kubernetes. Supports rotation via refresh intervals. The source of truth lives outside the cluster. **SOPS**: Best when you want encrypted secrets directly in Git files (not just Kubernetes). Works with any format (YAML, JSON, env files). Commonly used with Terraform, Helm values, and general configuration. Can use multiple KMS providers for key management.
</details>

**Q3: Why is automated secret rotation important, and what are the challenges?**

<details>
<summary>Answer</summary>

Automated rotation is important because manual rotation is unreliable (humans forget, deprioritize, or make errors) and unrotated secrets have unlimited exposure time if leaked. Challenges: (1) **Coordinating consumers** -- when a database password rotates, all applications using it must get the new password without downtime. Solutions: dual-password support (old and new both valid during transition), or dynamic credentials per consumer. (2) **Rotation failures** -- if the new secret fails validation, you need automatic rollback. (3) **Cascading dependencies** -- rotating a root credential may require rotating downstream secrets. (4) **Testing** -- rotation code itself can have bugs. Always test rotation in staging first.
</details>

**Q4: What is the difference between gitleaks and TruffleHog?**

<details>
<summary>Answer</summary>

**Gitleaks** scans Git repositories for secrets using regex patterns and entropy analysis. It is fast, supports pre-commit hooks, and has a large rule database for common secret formats (AWS keys, GitHub tokens, etc.). Best for: pre-commit prevention and CI/CD integration. **TruffleHog** goes further by verifying detected secrets against their respective APIs. If it finds an AWS key, it actually tests whether the key is valid. This eliminates false positives (test keys, example values). TruffleHog also supports scanning beyond Git: S3 buckets, CI/CD logs, Jira, Confluence. Best for: verified secret detection and broader scanning scope. Many teams use both: gitleaks for speed in pre-commit, TruffleHog for thorough CI/CD scanning.
</details>

**Q5: How should you handle a leaked secret?**

<details>
<summary>Answer</summary>

Incident response for a leaked secret: (1) **Immediate**: Revoke/rotate the leaked secret within minutes, not hours. Automate this if possible. (2) **Assess blast radius**: Determine what the secret grants access to and check audit logs for unauthorized usage. (3) **Contain**: If the secret was used maliciously, isolate affected systems. (4) **Remediate**: Remove the secret from the source (Git history requires `git filter-repo` or BFG Repo Cleaner, not just deleting the file). (5) **Prevent recurrence**: Add pre-commit hooks, CI scanning, and review the process that led to the leak. (6) **Document**: Create an incident report documenting what happened, impact, and prevention measures. Never assume a leaked secret was not found by an attacker -- automated scanners on GitHub find exposed secrets within seconds.
</details>
