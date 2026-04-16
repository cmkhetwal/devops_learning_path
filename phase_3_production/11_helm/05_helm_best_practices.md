# Helm Best Practices: Production Workflows and Pitfalls

## Why This Matters in DevOps

Knowing Helm commands is necessary, but knowing how to use Helm in production is
what separates a junior from a senior engineer. Production Helm usage involves
versioning strategies, testing pipelines, multi-release management, CI/CD
integration, security scanning, and patterns that prevent downtime.

This lesson covers the operational wisdom that comes from running Helm at scale:
managing dozens of releases across multiple clusters, coordinating team workflows,
preventing configuration drift, and building guardrails that catch mistakes before
they reach production.

---

## Core Concepts

### Chart Versioning (Semantic Versioning)

Charts follow Semantic Versioning:

```
MAJOR.MINOR.PATCH

1.0.0 -> 1.0.1  # Patch: bug fix in templates, no value changes
1.0.1 -> 1.1.0  # Minor: new optional feature, backward-compatible values
1.1.0 -> 2.0.0  # Major: breaking changes to values structure
```

**When to bump each:**

- **Patch** - Fix a template bug, update documentation, adjust defaults
- **Minor** - Add a new optional resource (PDB, HPA), add new values with defaults
- **Major** - Rename or restructure values, remove resources, change required values

Keep `appVersion` synchronized with the application release but independent from
the chart version:

```yaml
# Chart version 3.2.1 deploys application version 5.0.0
version: 3.2.1
appVersion: "5.0.0"
```

### Chart Testing Strategies

#### 1. Static Analysis (Linting)

```bash
# Basic linting
helm lint ./my-chart

# Lint with values files
helm lint ./my-chart -f values-production.yaml

# Lint with strict mode (warnings become errors)
helm lint ./my-chart --strict

# Use ct (chart-testing) for CI
ct lint --charts ./my-chart --config ct.yaml
```

#### 2. Template Rendering

```bash
# Render templates and pipe to kubeval for schema validation
helm template my-release ./my-chart | kubeval --strict

# Render templates and pipe to kubeconform (faster, maintained)
helm template my-release ./my-chart | kubeconform -strict -summary

# Render with different value sets
for env in dev staging production; do
  echo "=== Testing $env ==="
  helm template my-release ./my-chart -f "values-${env}.yaml" | kubeconform -strict
done
```

#### 3. Integration Testing (helm test)

```bash
# Run tests after installation
helm install my-release ./my-chart --wait
helm test my-release

# In CI/CD, combine install and test
helm upgrade --install my-release ./my-chart \
  --wait --timeout 5m && \
  helm test my-release
```

#### 4. Chart Testing Tool (ct)

```yaml
# ct.yaml - chart-testing configuration
remote: origin
target-branch: main
chart-dirs:
  - charts
helm-extra-args: --timeout 300s
check-version-increment: true
validate-maintainers: false
```

```bash
# Install chart-testing
pip install yamllint
brew install chart-testing  # or download from GitHub releases

# Run full testing suite
ct lint-and-install --config ct.yaml
```

### Helmfile: Managing Multiple Releases

**Helmfile** declares all Helm releases in a single file, enabling declarative
management of an entire platform:

```yaml
# helmfile.yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami
  - name: prometheus-community
    url: https://prometheus-community.github.io/helm-charts
  - name: ingress-nginx
    url: https://kubernetes.github.io/ingress-nginx

environments:
  dev:
    values:
      - environments/dev/values.yaml
  staging:
    values:
      - environments/staging/values.yaml
  production:
    values:
      - environments/production/values.yaml

releases:
  - name: ingress
    namespace: ingress-nginx
    chart: ingress-nginx/ingress-nginx
    version: 4.9.0
    values:
      - values/ingress-nginx.yaml
      - values/ingress-nginx-{{ .Environment.Name }}.yaml
    wait: true
    timeout: 300

  - name: monitoring
    namespace: monitoring
    chart: prometheus-community/kube-prometheus-stack
    version: 56.0.0
    values:
      - values/prometheus.yaml
    needs:
      - ingress-nginx/ingress  # Dependency ordering

  - name: api
    namespace: api
    chart: ./charts/api
    values:
      - values/api.yaml
      - values/api-{{ .Environment.Name }}.yaml
    set:
      - name: image.tag
        value: {{ requiredEnv "API_IMAGE_TAG" }}
    needs:
      - monitoring/monitoring
    hooks:
      - events: ["presync"]
        showlogs: true
        command: "kubectl"
        args: ["apply", "-f", "prerequisites/"]

  - name: worker
    namespace: api
    chart: ./charts/worker
    values:
      - values/worker.yaml
    needs:
      - api/api
```

```bash
# Install helmfile
brew install helmfile  # or download from GitHub releases

# Apply all releases
helmfile apply

# Apply for a specific environment
helmfile -e production apply

# Diff before applying
helmfile diff

# Sync a specific release
helmfile -l name=api apply

# Destroy everything
helmfile destroy

# Template all releases
helmfile template
```

### Helm in CI/CD

#### GitHub Actions Example

```yaml
# .github/workflows/deploy.yaml
name: Deploy with Helm
on:
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        type: choice
        options: [staging, production]

env:
  CHART_PATH: ./charts/my-app

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Helm
        uses: azure/setup-helm@v4
        with:
          version: v3.14.0

      - name: Lint chart
        run: helm lint ${{ env.CHART_PATH }} --strict

      - name: Template and validate
        run: |
          helm template test ${{ env.CHART_PATH }} \
            -f ${{ env.CHART_PATH }}/values-staging.yaml | \
            kubeconform -strict -summary

  deploy-staging:
    needs: lint-and-test
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4

      - name: Install Helm
        uses: azure/setup-helm@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v4
        with:
          kubeconfig: ${{ secrets.KUBECONFIG_STAGING }}

      - name: Deploy to staging
        run: |
          helm upgrade --install my-app ${{ env.CHART_PATH }} \
            -f ${{ env.CHART_PATH }}/values-staging.yaml \
            --set image.tag=${{ github.sha }} \
            --namespace staging \
            --create-namespace \
            --atomic \
            --timeout 5m \
            --wait

      - name: Run Helm tests
        run: helm test my-app -n staging --timeout 2m

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.event.inputs.environment == 'production'
    steps:
      - uses: actions/checkout@v4

      - name: Install Helm
        uses: azure/setup-helm@v4

      - name: Configure kubectl
        uses: azure/k8s-set-context@v4
        with:
          kubeconfig: ${{ secrets.KUBECONFIG_PRODUCTION }}

      - name: Deploy to production
        run: |
          helm upgrade --install my-app ${{ env.CHART_PATH }} \
            -f ${{ env.CHART_PATH }}/values-production.yaml \
            --set image.tag=${{ github.sha }} \
            --namespace production \
            --atomic \
            --timeout 10m \
            --wait
```

### Helm with ArgoCD

ArgoCD can manage Helm charts natively:

```yaml
# argocd-application.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/helm-charts
    targetRevision: main
    path: charts/my-app
    helm:
      valueFiles:
        - values-production.yaml
      parameters:
        - name: image.tag
          value: "v2.5.0"
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 3
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### Common Patterns

#### ConfigMap Reloading with Reloader

```yaml
# values.yaml
configReloader:
  enabled: true

# deployment.yaml
metadata:
  annotations:
    {{- if .Values.configReloader.enabled }}
    reloader.stakater.com/auto: "true"
    {{- end }}
```

#### Init Containers for Dependencies

```yaml
# Wait for database to be ready before starting the app
initContainers:
  {{- if .Values.waitForDeps.enabled }}
  - name: wait-for-db
    image: busybox:1.36
    command: ['sh', '-c']
    args:
      - |
        until nc -z {{ include "myapp.fullname" . }}-postgresql 5432; do
          echo "Waiting for PostgreSQL..."
          sleep 2
        done
        echo "PostgreSQL is ready."
  - name: wait-for-redis
    image: busybox:1.36
    command: ['sh', '-c']
    args:
      - |
        until nc -z {{ include "myapp.fullname" . }}-redis-master 6379; do
          echo "Waiting for Redis..."
          sleep 2
        done
        echo "Redis is ready."
  {{- end }}
```

### Chart Security Scanning

```bash
# Scan Helm charts with checkov
pip install checkov
checkov -d ./my-chart --framework helm

# Example output:
# Passed checks: 12, Failed checks: 3, Skipped checks: 0
#
# Check: CKV_K8S_22: "Ensure readOnlyRootFilesystem is true"
#   FAILED for resource: Deployment
#   File: templates/deployment.yaml
#
# Check: CKV_K8S_28: "Ensure the Tiller (Helm v2) is not deployed"
#   PASSED
#
# Check: CKV_K8S_40: "Ensure containers do not run with AllowPrivilegeEscalation"
#   FAILED

# Scan with Trivy
trivy config ./my-chart

# Scan rendered output with kubesec
helm template my-app ./my-chart | kubesec scan -
```

### Chart Repository Setup

#### GitHub Pages Repository

```bash
# Create a chart repository using GitHub Pages
mkdir -p helm-repo
cd helm-repo

# Package charts
helm package ../charts/my-app
helm package ../charts/my-worker

# Generate index
helm repo index . --url https://myorg.github.io/helm-repo

# Commit and push to gh-pages branch
git add .
git commit -m "Update Helm charts"
git push origin gh-pages
```

#### ChartMuseum (Self-Hosted)

```bash
# Deploy ChartMuseum with Helm
helm install chartmuseum chartmuseum/chartmuseum \
  --set env.open.STORAGE=amazon \
  --set env.open.STORAGE_AMAZON_BUCKET=my-chart-bucket \
  --set env.open.STORAGE_AMAZON_REGION=us-east-1

# Push charts
curl --data-binary "@my-chart-1.0.0.tgz" http://chartmuseum.example.com/api/charts

# Add as a repo
helm repo add myrepo http://chartmuseum.example.com
```

### Common Mistakes and How to Avoid Them

| Mistake | Consequence | Fix |
|---|---|---|
| Using `--reuse-values` on chart upgrades | New default values are not applied | Maintain complete values files |
| Not using `--atomic` in CI/CD | Failed deploys leave broken releases | Always use `--atomic` in automation |
| Hardcoding the release name | Cannot install multiple instances | Use `{{ .Release.Name }}` in templates |
| Not setting resource limits | Pods can consume unlimited resources | Always set limits in values.yaml |
| Storing secrets in values.yaml | Secrets end up in version control | Use external secret operators |
| Skipping `helm diff` before upgrade | Surprises in production | Use `helm diff upgrade` plugin |
| Not pinning chart versions | Different versions on each install | Always specify `--version` |
| Ignoring `helm lint` warnings | Hidden issues surface in production | Run `helm lint --strict` |
| Not testing with multiple values files | Environment-specific bugs | Test every values file in CI |
| Forgetting `--create-namespace` | Fails if namespace does not exist | Always include in automation |

---

## Step-by-Step Practical

### Setting Up a Complete Helm Workflow

```bash
# 1. Install the Helm diff plugin
helm plugin install https://github.com/databus23/helm-diff

# 2. Preview changes before applying
helm diff upgrade my-app ./my-chart \
  -f values-production.yaml \
  --set image.tag=v2.1.0

# Output shows colored diff of what would change:
# default, my-app, Deployment (apps) has changed:
#   spec:
#     template:
#       spec:
#         containers:
# -         image: myorg/app:v2.0.0
# +         image: myorg/app:v2.1.0

# 3. Apply the upgrade with safety guardrails
helm upgrade --install my-app ./my-chart \
  -f values-production.yaml \
  --set image.tag=v2.1.0 \
  --namespace production \
  --atomic \
  --timeout 5m \
  --wait \
  --cleanup-on-fail

# 4. Verify the deployment
helm status my-app -n production
helm get values my-app -n production
kubectl get pods -n production -l app.kubernetes.io/instance=my-app

# 5. Run post-deploy tests
helm test my-app -n production --timeout 2m
```

### Setting Up Helmfile for Multi-Service Platform

```bash
# 1. Install helmfile
brew install helmfile  # macOS
# or download from https://github.com/helmfile/helmfile/releases

# 2. Create directory structure
mkdir -p platform/{charts,values,environments/{dev,staging,production}}

# 3. Create helmfile.yaml (shown in Core Concepts above)

# 4. Initialize and sync
helmfile repos  # Add/update all repositories
helmfile deps   # Build chart dependencies
helmfile diff   # Preview changes
helmfile apply  # Apply all releases

# 5. Environment-specific deployment
API_IMAGE_TAG=abc123 helmfile -e staging apply
API_IMAGE_TAG=v2.1.0 helmfile -e production apply

# 6. Selective deployment
helmfile -e production -l name=api apply     # Only the API
helmfile -e production -l namespace=monitoring apply  # Only monitoring
```

---

## Exercises

### Exercise 1: Helm Diff Workflow
Install the Helm diff plugin. Deploy a chart, then make a change to the values.
Use `helm diff upgrade` to preview the change before applying it. Document the
diff output and explain each change. Then apply the upgrade with `--atomic`.

### Exercise 2: Helmfile Multi-Environment
Create a Helmfile that manages three releases (Nginx, Redis, your app) across
three environments (dev, staging, production). Each environment should have
different resource allocations. Use `helmfile diff` and `helmfile apply` to
deploy.

### Exercise 3: CI/CD Pipeline
Write a GitHub Actions workflow that lints a Helm chart, renders templates for
all environments, validates them with kubeconform, and deploys to staging with
`--atomic`. Include a manual approval gate before production deployment.

### Exercise 4: Chart Security Audit
Take any Bitnami chart (e.g., nginx or postgresql), render it with `helm template`,
and scan the output with checkov and kubesec. Document all findings, categorize
them by severity, and write a values file that fixes the high-severity issues.

### Exercise 5: Chart Repository
Set up a Helm chart repository using GitHub Pages. Package a chart, generate
the repository index, push to a gh-pages branch, add the repository with
`helm repo add`, and install the chart from your repository.

---

## Knowledge Check

### Question 1
Why should you use `helm upgrade --install --atomic` in CI/CD instead of
separate `helm install` and `helm upgrade` commands?

**Answer:** `helm upgrade --install` is idempotent: it installs if the release
does not exist and upgrades if it does, eliminating the need for conditional
logic. `--atomic` ensures that if the upgrade fails (pods do not become ready
within the timeout), the release is automatically rolled back to the previous
working state. Without `--atomic`, a failed upgrade leaves broken resources in
the cluster, requiring manual intervention. Together, these flags make CI/CD
deployments reliable and self-healing.

### Question 2
What is the purpose of `helm diff` and why should it be part of every deployment
workflow?

**Answer:** The `helm diff` plugin compares the currently deployed release with
what would be deployed by an upgrade, showing a colored diff of all changes. It
serves the same purpose as `terraform plan`: it lets operators review changes
before applying them, preventing surprises. It catches unintended changes like
accidental value overrides, chart version differences, or template bugs. In
CI/CD, `helm diff` output can be posted as a PR comment for review before
deployment.

### Question 3
What problem does Helmfile solve that Helm alone does not?

**Answer:** Helm manages individual releases. Helmfile manages collections of
releases declaratively. When a platform has 20+ Helm releases with
inter-dependencies, ordering constraints, and environment-specific values,
managing each one with individual `helm upgrade` commands becomes unwieldy.
Helmfile declares all releases in a single file, supports environment-specific
values, enforces dependency ordering (via `needs`), and provides `helmfile diff`
and `helmfile apply` to manage the entire platform as a unit.

### Question 4
Why is `--reuse-values` dangerous when upgrading to a new chart version?

**Answer:** When upgrading to a new chart version, the new version might introduce
new values with meaningful defaults (e.g., a new security context, a new sidecar
container, or new resource limits). `--reuse-values` takes only the values from
the previous release and ignores new defaults. This means new features are
silently disabled and new security defaults are not applied. The safe approach is
to maintain a complete values file in version control and pass it with `-f` on
every upgrade, ensuring all values (both old and new) are explicitly set.

### Question 5
How does ArgoCD manage Helm charts differently from running `helm upgrade`
in CI/CD?

**Answer:** ArgoCD manages Helm charts using a GitOps approach: the desired state
(chart version, values) is declared in Git, and ArgoCD continuously reconciles
the cluster to match. With `helm upgrade` in CI/CD, deployment is push-based
(triggered by a pipeline run), and drift is not detected between runs. ArgoCD
renders the Helm templates itself and applies them using `kubectl apply`, meaning
the release is not tracked as a Helm release (no `helm list` output). ArgoCD
also provides self-healing (reverting manual changes) and automatic syncing when
Git changes, which raw Helm in CI/CD does not offer.
