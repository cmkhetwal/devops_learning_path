# Secrets in Pipelines: Secure Credential Management

## Why This Matters in DevOps

CI/CD pipelines need credentials to deploy code, push images, access cloud APIs,
and connect to databases. These credentials are the keys to your kingdom. If a
pipeline secret is leaked through logs, exposed in a pull request, or stolen from
a compromised CI server, an attacker has direct access to your production
infrastructure.

The 2023 CircleCI breach exposed customer secrets stored in the platform. The
2024 GitHub Actions supply chain attacks compromised popular actions to steal
secrets from downstream repositories. Codecov's bash uploader was modified to
exfiltrate environment variables containing secrets.

Secrets management in pipelines is not about making it possible to deploy -- it
is about making it possible to deploy without creating attack vectors. This
lesson covers how to handle credentials safely across CI/CD pipelines.

---

## Core Concepts

### Why Secrets in Pipelines Are Dangerous

Pipelines are attractive targets because they:

1. **Have broad access** - A deployment pipeline typically has credentials for
   cloud providers, container registries, Kubernetes clusters, databases, and
   monitoring systems.

2. **Process untrusted code** - In open-source projects, anyone can submit a PR
   that runs in your CI pipeline, potentially exfiltrating secrets.

3. **Generate extensive logs** - Pipeline logs can accidentally contain secrets
   printed by commands, error messages, or debugging output.

4. **Use third-party actions/plugins** - Each action is code you do not control
   that runs with access to your secrets.

5. **Are often over-provisioned** - Teams give pipelines admin credentials
   "because it is easier" instead of scoping permissions.

Common secret exposure vectors:

```
Pipeline Logs    → echo $SECRET, error messages containing credentials
PR from Fork     → Malicious PR triggers CI with access to secrets
env Variables    → Third-party actions reading process.env
Artifact Upload  → Build artifacts containing embedded credentials
Config Files     → Checked-in .env files, terraform.tfvars
Docker Layers    → Secrets copied into image layers during build
Git History      → Secrets committed and then "deleted" (still in history)
```

### GitHub Actions Secrets

GitHub Actions provides encrypted secrets at three levels:

```
Organization Secrets  → Available to all repos (or selected repos)
Repository Secrets    → Available to all workflows in the repo
Environment Secrets   → Available only to workflows targeting that environment
```

```yaml
# Using secrets in GitHub Actions
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production  # Required to access environment secrets
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1

      # Secrets are masked in logs
      - name: This will show *** in logs
        run: echo "${{ secrets.AWS_SECRET_ACCESS_KEY }}"
        # Output: ***

      # But they can still leak through indirect means
      - name: Dangerous - could leak via base64
        run: echo "${{ secrets.AWS_SECRET_ACCESS_KEY }}" | base64
        # Output: the base64 encoded secret (NOT masked!)
```

**Security rules for GitHub Actions secrets:**

- Secrets are not passed to workflows triggered by PRs from forks
- Secrets are masked in logs (but only exact matches, not encoded versions)
- Secrets cannot be read back from the GitHub UI after creation
- Use environments with required reviewers for production secrets
- Minimize the number of steps that have access to each secret

### Environment-Specific Secrets

```yaml
# GitHub Environments with protection rules
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging  # Uses staging secrets
    steps:
      - name: Deploy to staging
        run: |
          kubectl config use-context staging
          helm upgrade --install myapp ./chart
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG }}  # Staging kubeconfig

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production  # Requires manual approval + uses prod secrets
    steps:
      - name: Deploy to production
        run: |
          kubectl config use-context production
          helm upgrade --install myapp ./chart
        env:
          KUBECONFIG: ${{ secrets.KUBECONFIG }}  # Production kubeconfig
```

Environment protection rules:
- **Required reviewers** - One or more people must approve before the job runs
- **Wait timer** - Delay before the job starts (gives time to abort)
- **Branch restrictions** - Only specific branches can deploy to this environment
- **Deployment branches** - Only main can deploy to production

### OIDC for Cloud Authentication (Keyless Auth)

OIDC (OpenID Connect) eliminates the need for long-lived credentials in CI/CD
pipelines. Instead of storing AWS access keys as secrets, the pipeline
authenticates using a short-lived token issued by GitHub:

```
Traditional (static credentials):
  GitHub Secret: AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY
  → Long-lived (never expire unless rotated)
  → If leaked, attacker has permanent access
  → Must be rotated manually

OIDC (keyless):
  GitHub OIDC Provider → Issues JWT token
  AWS IAM → Trusts GitHub's OIDC provider
  Pipeline → Exchanges JWT for short-lived AWS credentials
  → Token valid for ~15 minutes
  → If intercepted, expires quickly
  → No secrets to manage or rotate
```

#### How OIDC Works

```
1. GitHub Actions job starts
2. GitHub OIDC provider issues a JWT with claims:
   {
     "iss": "https://token.actions.githubusercontent.com",
     "sub": "repo:myorg/myrepo:ref:refs/heads/main",
     "aud": "sts.amazonaws.com",
     "ref": "refs/heads/main",
     "repository": "myorg/myrepo",
     "actor": "developer",
     "workflow": "Deploy",
     "environment": "production"
   }
3. The JWT is sent to the cloud provider (AWS STS, GCP, Azure)
4. The cloud provider validates the JWT against GitHub's OIDC provider
5. If the claims match the trust policy, temporary credentials are returned
6. The pipeline uses the temporary credentials (expire in 15 min - 1 hour)
```

### Dynamic Credentials

Beyond OIDC, tools like HashiCorp Vault provide dynamic credentials that are
generated on demand and automatically revoked:

```bash
# Vault dynamic database credentials
vault read database/creds/readonly
# Key                Value
# ---                -----
# lease_id           database/creds/readonly/abc123
# lease_duration     1h
# username           v-github-readonly-abc123-1234567890
# password           A1B2C3D4-random-generated-password

# The credentials are valid for 1 hour and automatically revoked
```

```yaml
# Using Vault in GitHub Actions
steps:
  - name: Import Secrets from Vault
    uses: hashicorp/vault-action@v3
    with:
      url: https://vault.example.com
      method: jwt
      role: github-deploy
      secrets: |
        secret/data/production/database username | DB_USER ;
        secret/data/production/database password | DB_PASS ;
        secret/data/production/api-keys stripe | STRIPE_KEY

  - name: Deploy (secrets available as env vars)
    run: ./deploy.sh
    # DB_USER, DB_PASS, STRIPE_KEY are available
```

### Rotating Secrets

Secret rotation should be automated and frequent:

```bash
# AWS: Rotate IAM access keys automatically with AWS Secrets Manager
aws secretsmanager rotate-secret \
  --secret-id production/database \
  --rotation-rules '{"AutomaticallyAfterDays": 30}'

# Kubernetes: Rotate secrets with External Secrets Operator
cat > external-secret.yaml << 'EOF'
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: production
spec:
  refreshInterval: 1h  # Check for rotation every hour
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: database-credentials
    creationPolicy: Owner
  data:
    - secretKey: username
      remoteRef:
        key: production/database
        property: username
    - secretKey: password
      remoteRef:
        key: production/database
        property: password
EOF
```

### Scanning for Leaked Secrets

#### Gitleaks

```bash
# Install gitleaks
brew install gitleaks

# Scan the current repository
gitleaks detect
# Finding:  AWS Access Key ID
# Secret:   AKIAIOSFODNN7EXAMPLE
# File:     config/settings.py
# Line:     42
# Commit:   abc123
# Author:   developer@example.com

# Scan git history
gitleaks detect --log-opts="--all"

# Protect against future leaks (pre-commit hook)
gitleaks protect --staged

# Custom rules
cat > .gitleaks.toml << 'EOF'
title = "Custom Gitleaks Config"

[[rules]]
id = "internal-api-key"
description = "Internal API Key"
regex = '''INTERNAL_KEY_[A-Za-z0-9]{32}'''
secretGroup = 0

[allowlist]
paths = [
  '''\.gitleaks\.toml''',
  '''tests/.*'''
]
EOF

gitleaks detect -c .gitleaks.toml
```

#### TruffleHog

```bash
# Install trufflehog
brew install trufflehog

# Scan a git repository
trufflehog git file://. --only-verified
# Found verified result
# Detector Type: AWS
# Raw result: AKIAIOSFODNN7EXAMPLE
# File: deploy.sh
# Line: 15
# Commit: def456

# Scan a GitHub organization
trufflehog github --org myorg --only-verified

# Scan filesystem
trufflehog filesystem --directory ./src
```

---

## Step-by-Step Practical

### Setting Up OIDC Authentication for AWS from GitHub Actions

```bash
# Step 1: Create an OIDC provider in AWS
aws iam create-open-id-connect-provider \
  --url "https://token.actions.githubusercontent.com" \
  --client-id-list "sts.amazonaws.com" \
  --thumbprint-list "6938fd4d98bab03faadb97b34396831e3780aea1"

# Step 2: Create an IAM role trust policy
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:*"
        }
      }
    }
  ]
}
EOF

# Step 3: Create the IAM role
aws iam create-role \
  --role-name GitHubActionsDeployRole \
  --assume-role-policy-document file://trust-policy.json

# Step 4: Attach permissions (least privilege)
cat > deploy-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:us-east-1:ACCOUNT_ID:repository/myapp"
    },
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters"
      ],
      "Resource": "arn:aws:eks:us-east-1:ACCOUNT_ID:cluster/production"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name GitHubActionsDeployRole \
  --policy-name DeployPolicy \
  --policy-document file://deploy-policy.json
```

```yaml
# Step 5: Use OIDC in GitHub Actions workflow
name: Deploy with OIDC
on:
  push:
    branches: [main]

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials via OIDC
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::ACCOUNT_ID:role/GitHubActionsDeployRole
          aws-region: us-east-1
          # No access keys! Authentication happens via OIDC token

      - name: Login to Amazon ECR
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        run: |
          docker build -t ${{ secrets.ECR_REGISTRY }}/myapp:${{ github.sha }} .
          docker push ${{ secrets.ECR_REGISTRY }}/myapp:${{ github.sha }}

      - name: Deploy to EKS
        run: |
          aws eks update-kubeconfig --name production --region us-east-1
          helm upgrade --install myapp ./chart \
            --set image.tag=${{ github.sha }} \
            --atomic --timeout 5m
```

### Setting Up Pre-Commit Secret Scanning

```bash
# Install pre-commit
pip install pre-commit

# Create pre-commit configuration
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.1
    hooks:
      - id: gitleaks

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: detect-private-key
      - id: detect-aws-credentials
        args: ['--allow-missing-credentials']

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']
EOF

# Install the hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Test: try to commit a file with a secret
echo 'AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' > test.env
git add test.env
git commit -m "test"
# gitleaks...............................................................Failed
# - hook id: gitleaks
# - exit code: 1
# Finding: AWS Secret Access Key
```

---

## Exercises

### Exercise 1: OIDC Setup
Configure OIDC authentication between GitHub Actions and AWS (or GCP/Azure).
Create an IAM role with minimal permissions for deploying to EKS. Write a
GitHub Actions workflow that uses OIDC instead of static credentials. Verify
that no long-lived credentials are stored as secrets.

### Exercise 2: Secret Scanning
Run gitleaks on three different Git repositories (your own or public ones).
Document all findings, categorize by secret type (API keys, passwords, tokens),
and determine whether each finding is a true positive or false positive.
Configure a custom `.gitleaks.toml` to reduce false positives.

### Exercise 3: Pre-Commit Hooks
Set up pre-commit hooks with gitleaks, detect-secrets, and detect-private-key.
Create test files containing various secret patterns (AWS keys, GitHub tokens,
database URLs, private keys). Verify that each is caught by the hooks. Document
which tool catches which type of secret.

### Exercise 4: Secret Rotation
Design a secret rotation workflow for database credentials. The workflow should:
generate new credentials, update them in Vault or AWS Secrets Manager, update
Kubernetes secrets via External Secrets Operator, and verify the application
works with the new credentials. Document the zero-downtime rotation process.

### Exercise 5: Pipeline Security Audit
Audit an existing CI/CD pipeline for secret hygiene. Check: are there long-lived
credentials? Are secrets scoped to environments? Are there third-party actions
with secret access? Are secrets masked in logs? Do forks have access to secrets?
Create a remediation plan for each finding.

---

## Knowledge Check

### Question 1
Why is OIDC authentication preferred over static credentials for CI/CD pipelines?

**Answer:** OIDC authentication eliminates long-lived credentials. Static
credentials (access keys, tokens) never expire unless manually rotated, meaning
a leaked credential provides persistent access. OIDC uses short-lived tokens
(15 minutes to 1 hour) that are generated on demand and cannot be reused. There
is no secret to steal, store, or rotate. The cloud provider trusts the CI/CD
platform's OIDC identity, and temporary credentials are issued per job run.
If a token is somehow intercepted, it expires quickly. OIDC also provides
better auditability: each credential issuance is tied to a specific repository,
branch, and workflow.

### Question 2
How can secrets leak from CI/CD pipelines even when they are masked in logs?

**Answer:** Secrets can leak through several indirect channels: (1) Base64 or
hex encoding the secret produces a different string that is not masked.
(2) Error messages from APIs may include credentials in the error context.
(3) Third-party actions can read environment variables and exfiltrate them
via network requests. (4) Build artifacts may contain embedded credentials
(e.g., a .env file packaged into a Docker image layer). (5) Debug mode or
verbose logging in build tools may print credentials. (6) Multi-line secrets
are only masked if the entire string matches, not individual lines. (7) Writing
secrets to files that are then uploaded as artifacts.

### Question 3
What is the difference between gitleaks and trufflehog?

**Answer:** Both tools scan for secrets in Git repositories, but they take
different approaches. Gitleaks uses regex patterns to detect secret-like strings
and supports custom rules via TOML configuration. It is fast and suitable for
pre-commit hooks. TruffleHog uses both regex patterns and entropy analysis
(finding high-entropy strings that look random, like API keys). TruffleHog
can also verify findings by attempting to authenticate with the discovered
credential (`--only-verified`), reducing false positives. TruffleHog supports
scanning beyond Git: GitHub organizations, S3 buckets, and filesystems. Use
gitleaks for speed and pre-commit hooks; use trufflehog for comprehensive
audits with verification.

### Question 4
What are GitHub Actions environment protection rules and why do they matter?

**Answer:** Environment protection rules add security controls around which
workflows can access environment-specific secrets. Key rules include: required
reviewers (one or more people must approve before a job using that environment
runs), wait timers (a delay before the job starts, giving time to review and
abort), branch restrictions (only specific branches like main can deploy to
production), and deployment branches (limiting which branches can target each
environment). These matter because they prevent unauthorized deployments:
a developer cannot push to a feature branch and deploy to production because
the production environment requires main branch and manual approval.

### Question 5
What is the risk of using third-party GitHub Actions that have access to secrets?

**Answer:** Third-party GitHub Actions are code you do not control. When a
workflow step uses a third-party action (`uses: someorg/some-action@v1`) and
that step has access to secrets (directly or through environment variables),
the action's code can read and exfiltrate those secrets. Risks include: the
action author pushes a malicious update, the action's repository is compromised,
or a dependency of the action is compromised (supply chain attack). Mitigations
include: pin actions to a specific commit SHA (not a tag), audit action source
code, use `permissions` to limit token scope, minimize which steps have secret
access, and prefer official actions from verified publishers.
