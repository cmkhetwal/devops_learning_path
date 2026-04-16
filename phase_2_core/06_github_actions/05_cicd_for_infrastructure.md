# CI/CD for Infrastructure

## Why This Matters in DevOps

Applying CI/CD to application code is well understood. Applying CI/CD to infrastructure code is where DevOps engineers earn their keep. Infrastructure changes carry higher risk — a bad application deployment serves 404 errors; a bad infrastructure deployment takes down the entire network, deletes databases, or opens security holes.

The GitOps approach — infrastructure changes go through pull requests, are reviewed, validated by automation, and applied on merge — gives you the same safety net for infrastructure that CI/CD gives to application code. This lesson connects Terraform, Docker, Kubernetes, and security scanning into automated pipelines that handle infrastructure with the rigor it demands.

---

## Core Concepts

### Terraform in CI/CD: Plan on PR, Apply on Merge

The core pattern is simple and powerful:

```
PR opened/updated:
  1. terraform fmt -check (formatting)
  2. terraform init (initialize)
  3. terraform validate (syntax)
  4. terraform plan (show changes)
  5. Post plan as PR comment (for review)

PR merged to main:
  6. terraform init
  7. terraform plan (verify)
  8. terraform apply -auto-approve
```

**Complete workflow:**

```yaml
# .github/workflows/terraform.yml
name: Terraform

on:
  pull_request:
    paths:
      - 'infrastructure/**'
  push:
    branches: [main]
    paths:
      - 'infrastructure/**'

permissions:
  contents: read
  pull-requests: write
  id-token: write

env:
  TF_VERSION: "1.9.0"
  TF_WORKING_DIR: "infrastructure/environments/prod"

jobs:
  terraform-check:
    name: Validate
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Format Check
        run: terraform fmt -check -recursive
        working-directory: infrastructure/

      - name: Init (no backend)
        run: terraform init -backend=false
        working-directory: ${{ env.TF_WORKING_DIR }}

      - name: Validate
        run: terraform validate
        working-directory: ${{ env.TF_WORKING_DIR }}

  terraform-plan:
    name: Plan
    needs: terraform-check
    runs-on: ubuntu-latest
    timeout-minutes: 15
    if: github.event_name == 'pull_request'

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.TERRAFORM_ROLE_ARN }}
          aws-region: us-east-1

      - name: Init
        run: terraform init
        working-directory: ${{ env.TF_WORKING_DIR }}

      - name: Plan
        id: plan
        run: terraform plan -no-color -out=tfplan 2>&1 | tee plan_output.txt
        working-directory: ${{ env.TF_WORKING_DIR }}
        continue-on-error: true

      - name: Post Plan to PR
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync(
              '${{ env.TF_WORKING_DIR }}/plan_output.txt', 'utf8'
            );
            const truncated = plan.length > 60000
              ? plan.substring(0, 60000) + '\n\n... (truncated)'
              : plan;

            const status = '${{ steps.plan.outcome }}' === 'success'
              ? '**Plan Succeeded**' : '**Plan Failed**';

            const body = `## Terraform Plan
            ${status}

            <details>
            <summary>Show Plan</summary>

            \`\`\`
            ${truncated}
            \`\`\`

            </details>

            *Pusher: @${{ github.actor }}*`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

      - name: Fail if plan failed
        if: steps.plan.outcome == 'failure'
        run: exit 1

  terraform-apply:
    name: Apply
    needs: terraform-check
    runs-on: ubuntu-latest
    timeout-minutes: 30
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: production
    concurrency:
      group: terraform-apply-prod
      cancel-in-progress: false

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.TERRAFORM_ROLE_ARN }}
          aws-region: us-east-1

      - name: Init
        run: terraform init
        working-directory: ${{ env.TF_WORKING_DIR }}

      - name: Apply
        run: terraform apply -auto-approve
        working-directory: ${{ env.TF_WORKING_DIR }}
```

### Docker Build and Push to Registry

```yaml
jobs:
  docker:
    name: Build and Push Docker Image
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write

    outputs:
      image-digest: ${{ steps.build.outputs.digest }}
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Generate tags
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - name: Build and push
        id: build
        uses: docker/build-push-action@v5
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64

      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}:${{ github.sha }}
          format: table
          exit-code: 1
          severity: CRITICAL,HIGH
```

### Kubernetes Deployment from CI/CD

```yaml
jobs:
  deploy-k8s:
    name: Deploy to Kubernetes
    needs: docker
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.K8S_DEPLOY_ROLE }}
          aws-region: us-east-1

      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name prod-cluster --region us-east-1

      - name: Update deployment image
        run: |
          kubectl set image deployment/web-app \
            web-app=${{ needs.docker.outputs.image-tag }} \
            -n production

      - name: Wait for rollout
        run: |
          kubectl rollout status deployment/web-app \
            -n production \
            --timeout=300s

      - name: Verify deployment
        run: |
          kubectl get pods -n production -l app=web-app
          kubectl get svc -n production -l app=web-app
```

### Cost Estimation with Infracost

Infracost shows the cost impact of infrastructure changes directly in PRs:

```yaml
jobs:
  infracost:
    name: Cost Estimation
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    permissions:
      contents: read
      pull-requests: write

    steps:
      - uses: actions/checkout@v4

      - name: Setup Infracost
        uses: infracost/actions/setup@v3
        with:
          api-key: ${{ secrets.INFRACOST_API_KEY }}

      - name: Generate cost baseline
        run: |
          infracost breakdown \
            --path=${{ env.TF_WORKING_DIR }} \
            --format=json \
            --out-file=/tmp/infracost-base.json
        env:
          INFRACOST_VCS_BASE_BRANCH: main

      - name: Generate cost diff
        run: |
          infracost diff \
            --path=${{ env.TF_WORKING_DIR }} \
            --compare-to=/tmp/infracost-base.json \
            --format=json \
            --out-file=/tmp/infracost-diff.json

      - name: Post cost comment
        run: |
          infracost comment github \
            --path=/tmp/infracost-diff.json \
            --repo=${{ github.repository }} \
            --pull-request=${{ github.event.pull_request.number }} \
            --github-token=${{ secrets.GITHUB_TOKEN }}
```

Example PR comment from Infracost:

```
## Infracost Cost Estimate

Monthly cost will increase by $127.40 (from $543.20 to $670.60)

| Resource | Monthly Cost | Change |
|----------|-------------|--------|
| aws_instance.web | +$73.00 | t3.micro → t3.large |
| aws_nat_gateway.main | +$32.40 | New resource |
| aws_rds_instance.db | +$22.00 | db.t3.micro → db.t3.small |
```

### Security Scanning in Pipelines

```yaml
jobs:
  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Terraform security scanning
      - name: Checkov - Terraform
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: infrastructure/
          framework: terraform
          output_format: sarif
          output_file_path: checkov-results.sarif

      # Docker image vulnerability scanning
      - name: Trivy - Container
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: fs
          scan-ref: .
          format: table
          severity: CRITICAL,HIGH

      # Dependency vulnerability scanning
      - name: Snyk - Dependencies
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      # Secret scanning
      - name: Gitleaks - Secrets
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### The GitOps Bridge

GitOps is the pattern where Git is the single source of truth for both application code and infrastructure. CI/CD pipelines bridge the gap:

```
Developer commits Terraform code
        │
        ▼
CI pipeline validates and plans
        │
        ▼
PR reviewed by team (code + plan)
        │
        ▼
PR merged to main
        │
        ▼
CD pipeline applies Terraform
        │
        ▼
Infrastructure matches Git

Developer commits Kubernetes manifests
        │
        ▼
ArgoCD detects change in Git
        │
        ▼
ArgoCD syncs cluster to match Git
        │
        ▼
Kubernetes matches Git
```

---

## Step-by-Step Practical

### Complete Infrastructure Pipeline

```yaml
# .github/workflows/infrastructure.yml
name: Infrastructure Pipeline

on:
  pull_request:
    paths: ['infrastructure/**']
  push:
    branches: [main]
    paths: ['infrastructure/**']

permissions:
  contents: read
  pull-requests: write
  id-token: write
  security-events: write

env:
  TF_VERSION: "1.9.0"

jobs:
  # Step 1: Detect which environments changed
  detect-changes:
    runs-on: ubuntu-latest
    outputs:
      dev: ${{ steps.filter.outputs.dev }}
      prod: ${{ steps.filter.outputs.prod }}
    steps:
      - uses: actions/checkout@v4
      - uses: dorny/paths-filter@v3
        id: filter
        with:
          filters: |
            dev:
              - 'infrastructure/environments/dev/**'
              - 'infrastructure/modules/**'
            prod:
              - 'infrastructure/environments/prod/**'
              - 'infrastructure/modules/**'

  # Step 2: Validate all Terraform code
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - run: terraform fmt -check -recursive
        working-directory: infrastructure/
      - name: Checkov scan
        uses: bridgecrewio/checkov-action@v12
        with:
          directory: infrastructure/
          framework: terraform
          soft_fail: false

  # Step 3: Plan for each changed environment
  plan-dev:
    needs: [detect-changes, validate]
    if: needs.detect-changes.outputs.dev == 'true' && github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.DEV_TERRAFORM_ROLE }}
          aws-region: us-east-1
      - run: terraform init && terraform plan -no-color
        working-directory: infrastructure/environments/dev

  plan-prod:
    needs: [detect-changes, validate]
    if: needs.detect-changes.outputs.prod == 'true' && github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.PROD_TERRAFORM_ROLE }}
          aws-region: us-east-1
      - run: terraform init && terraform plan -no-color
        working-directory: infrastructure/environments/prod

  # Step 4: Apply on merge (dev auto, prod with approval)
  apply-dev:
    needs: [detect-changes, validate]
    if: needs.detect-changes.outputs.dev == 'true' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: dev
    concurrency:
      group: terraform-dev
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.DEV_TERRAFORM_ROLE }}
          aws-region: us-east-1
      - run: terraform init && terraform apply -auto-approve
        working-directory: infrastructure/environments/dev

  apply-prod:
    needs: [detect-changes, validate, apply-dev]
    if: |
      always() &&
      needs.detect-changes.outputs.prod == 'true' &&
      github.ref == 'refs/heads/main' &&
      (needs.apply-dev.result == 'success' || needs.apply-dev.result == 'skipped')
    runs-on: ubuntu-latest
    environment: production
    concurrency:
      group: terraform-prod
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: ${{ env.TF_VERSION }}
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ vars.PROD_TERRAFORM_ROLE }}
          aws-region: us-east-1
      - run: terraform init && terraform apply -auto-approve
        working-directory: infrastructure/environments/prod
```

---

## Exercises

### Exercise 1: Terraform PR Pipeline
Create a Terraform project with the local provider and a GitHub Actions workflow that runs `fmt`, `validate`, and `plan` on PRs, posting the plan as a comment. Test by opening a PR with a Terraform change.

### Exercise 2: Docker Build Pipeline
Create a Dockerfile and a workflow that builds the image, tags it with the commit SHA, scans it with Trivy, and pushes to GHCR only if the scan passes. Introduce a known vulnerable base image and verify the scan catches it.

### Exercise 3: Cost Estimation
Set up Infracost on a Terraform project that creates AWS resources. Make a PR that changes an instance type from t3.micro to t3.xlarge and observe the cost impact in the PR comment.

### Exercise 4: Security Gate
Create a workflow that runs checkov on Terraform code and gitleaks for secret detection. Deliberately introduce a security issue (publicly accessible S3 bucket) and verify the pipeline fails with a clear message.

### Exercise 5: Multi-Environment Pipeline
Build a pipeline that detects which environment's Terraform changed (dev vs prod), plans only the affected environment, applies dev automatically, and requires approval for prod.

---

## Knowledge Check

### Question 1
Why is "plan on PR, apply on merge" the standard pattern for Terraform in CI/CD?

<details>
<summary>Answer</summary>

This pattern provides safety at every stage: (1) the plan runs on PR creation, showing reviewers exactly what infrastructure will change, enabling informed code review, (2) the plan is posted as a PR comment so the entire team can see the impact before approving, (3) apply only runs after the PR is merged (approved by reviewers), ensuring no unapproved changes reach infrastructure, (4) applying on merge to main means only reviewed, approved changes are executed, (5) the plan acts as a preview that catches errors before they affect real infrastructure. This mirrors the application CI/CD pattern (test on PR, deploy on merge) adapted for infrastructure's higher risk profile.
</details>

### Question 2
What is OIDC authentication and why is it preferred over storing AWS keys as secrets?

<details>
<summary>Answer</summary>

OIDC (OpenID Connect) allows GitHub Actions to assume an AWS IAM role without storing long-lived access keys. GitHub provides a short-lived JWT token for each workflow run, and AWS trusts this token through an OIDC identity provider configuration. Benefits: (1) no long-lived secrets to manage, rotate, or risk leaking, (2) credentials are automatically scoped to each workflow run and expire quickly, (3) you can restrict which repositories, branches, and environments can assume the role using IAM conditions, (4) no secret rotation needed — tokens are generated fresh for each run. The `aws-actions/configure-aws-credentials` action with `role-to-assume` handles this automatically.
</details>

### Question 3
Why should you use concurrency control with `cancel-in-progress: false` for infrastructure applies?

<details>
<summary>Answer</summary>

Infrastructure applies must not be cancelled mid-execution because: (1) a partial apply can leave infrastructure in an inconsistent state — some resources created, others not, dependencies broken, (2) state file corruption can occur if a write is interrupted, (3) some resources cannot be safely re-created (databases, stateful services), (4) cancelled applies may leave state locks that require manual intervention. Setting `cancel-in-progress: false` means if a second apply is triggered while the first is running, it queues and waits rather than cancelling the in-progress apply. This ensures every apply completes fully, even if it means slightly longer wait times.
</details>

### Question 4
What is Infracost and how does it improve the infrastructure PR review process?

<details>
<summary>Answer</summary>

Infracost estimates the monthly cost impact of infrastructure changes and posts the results as PR comments. It improves the review process by: (1) making cost visible before changes are applied — reviewers can see that changing an instance type adds $73/month, (2) preventing cost surprises — a developer might not realize that adding a NAT gateway costs $32/month, (3) enabling cost-aware architecture decisions during code review, not after the bill arrives, (4) tracking cost trends over time. It works by analyzing Terraform plan output against cloud pricing APIs. In the PR comment, it shows a breakdown by resource with before/after costs. This is especially valuable in organizations without FinOps tooling.
</details>

### Question 5
What security scanning tools should be included in an infrastructure pipeline and what does each catch?

<details>
<summary>Answer</summary>

A comprehensive infrastructure pipeline should include: (1) Checkov/tfsec — scans Terraform code for security misconfigurations (public S3 buckets, unencrypted databases, overly permissive security groups, missing logging), (2) Trivy — scans Docker images for known vulnerabilities in OS packages and application dependencies, (3) Gitleaks/trufflehog — scans Git history and code for accidentally committed secrets (API keys, passwords, tokens), (4) Snyk/Safety — scans application dependencies for known vulnerabilities, (5) KICS/Kubesec — scans Kubernetes manifests for security misconfigurations. Each tool catches a different class of vulnerability, and they complement each other. The pipeline should fail on critical/high findings and allow teams to acknowledge and suppress accepted risks with documented justification.
</details>
