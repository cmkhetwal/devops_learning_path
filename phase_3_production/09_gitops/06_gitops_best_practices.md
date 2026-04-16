# Lesson 06: GitOps Best Practices

## Why This Matters in DevOps

Adopting ArgoCD and structuring your repos correctly are necessary but not sufficient
for GitOps success. The difference between a team that thrives with GitOps and one
that abandons it within six months comes down to operational practices: separating
concerns, automating image updates, handling drift, planning for disaster recovery,
managing RBAC, and knowing the pitfalls.

This lesson distills hard-won lessons from production GitOps environments into
actionable best practices. These are the patterns that prevent the common failure
modes: secret sprawl, alert fatigue from ArgoCD notifications, broken multi-cluster
setups, and the dreaded "who changed what and when" audit trail gaps.

---

## Core Concepts

### Separating Application Repo from Config Repo

The most important structural decision in GitOps:

```
APPLICATION REPO (source code)          CONFIG REPO (deployment manifests)
================================        ================================
acme/payment-service                    acme/platform-config
  src/                                    apps/payment-service/
  tests/                                    base/deployment.yaml
  Dockerfile                                overlays/production/
  .github/workflows/ci.yaml

CI Pipeline (in app repo):
  1. Run tests
  2. Build Docker image
  3. Push to registry: acme/payment:v3.2.1
  4. Update config repo: image tag -> v3.2.1
```

Why separate?
- **Different change cadence**: Code changes multiple times per day; infrastructure
  config changes less frequently.
- **Different permissions**: Developers commit to the app repo; platform engineers
  review config repo changes.
- **Clean Git history**: The config repo history shows only deployment changes, not
  code commits. This is the audit log.
- **Decoupled pipelines**: A CI failure in the app repo does not affect deployment
  state. A config repo change does not trigger CI builds.

### Image Updater Automation

Manually updating image tags in the config repo after every CI build is tedious.
ArgoCD Image Updater automates this:

```bash
# Install ArgoCD Image Updater
kubectl apply -n argocd -f \
  https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
```

Configure an Application to use it:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service
  namespace: argocd
  annotations:
    # Watch for new tags matching semver pattern
    argocd-image-updater.argoproj.io/image-list: >
      app=acme/payment-service:~v3
    # Update strategy: semver (pick highest matching version)
    argocd-image-updater.argoproj.io/app.update-strategy: semver
    # Write changes back to Git (not just override in cluster)
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/write-back-target: kustomization
    argocd-image-updater.argoproj.io/git-branch: main
```

Flow:
1. CI builds `acme/payment-service:v3.2.2` and pushes to registry.
2. Image Updater polls the registry, detects `v3.2.2 > v3.2.1`.
3. Image Updater commits to the config repo: updates `kustomization.yaml`.
4. ArgoCD detects the new commit and syncs.

### Drift Detection and Remediation

Drift happens when the live cluster state differs from Git. Sources:
- Manual `kubectl` commands
- Horizontal Pod Autoscaler changing replica counts
- Admission webhooks injecting sidecars or labels
- Operators modifying resources they manage

Remediation strategies:

```yaml
# Strategy 1: Self-heal (ArgoCD reverts all drift)
syncPolicy:
  automated:
    selfHeal: true

# Strategy 2: Ignore known drift (e.g., HPA-managed replicas)
ignoreDifferences:
  - group: apps
    kind: Deployment
    jsonPointers:
      - /spec/replicas
  - group: apps
    kind: Deployment
    jqPathExpressions:
      - .spec.template.metadata.annotations."sidecar.istio.io/inject"
```

**Best practice**: Enable self-heal everywhere, but use `ignoreDifferences` for
fields managed by controllers (HPA, Istio sidecar injection, cert-manager
annotations).

### Disaster Recovery

GitOps provides inherent disaster recovery — the cluster state is in Git. But you
must plan for:

**Scenario 1: Cluster destroyed**
```bash
# Stand up new cluster
# Install ArgoCD
# Apply the root app
kubectl apply -f root-app.yaml
# ArgoCD recreates everything from Git
```

**Scenario 2: ArgoCD itself is destroyed**
```bash
# Re-install ArgoCD
kubectl apply -n argocd -f install.yaml
# Re-apply the root app
kubectl apply -f root-app.yaml
# All Application CRDs are recreated from Git
```

**Scenario 3: Git repository is corrupted**
- Maintain repository mirrors (GitHub -> GitLab mirror)
- Use Git repository backup tools
- ArgoCD caches the last-known-good manifests in Redis

**Scenario 4: Wrong change deployed**
```bash
# Revert the commit in Git
git revert HEAD
git push
# ArgoCD auto-syncs to the reverted state
```

### Multi-Cluster GitOps

Managing multiple clusters from a single ArgoCD instance:

```bash
# Register clusters with ArgoCD
argocd cluster add dev-cluster --name dev
argocd cluster add staging-cluster --name staging
argocd cluster add production-cluster --name production

# List registered clusters
argocd cluster list
```

```yaml
# ApplicationSet for multi-cluster deployment
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: payment-service-multi-cluster
  namespace: argocd
spec:
  generators:
    - clusters:
        selector:
          matchLabels:
            env: production
  template:
    metadata:
      name: "payment-service-{{name}}"
    spec:
      source:
        repoURL: https://github.com/acme/platform-config.git
        path: apps/payment-service/overlays/production
      destination:
        server: "{{server}}"
        namespace: payment-service
```

Architecture patterns:

```
Pattern 1: Hub-and-Spoke (Centralized)
=======================================
           ArgoCD (Hub)
          /      |      \
     Dev       Staging    Production
   Cluster    Cluster     Cluster

Pattern 2: ArgoCD per Cluster (Decentralized)
==============================================
  ArgoCD-Dev    ArgoCD-Stg    ArgoCD-Prod
      |              |              |
    Dev           Staging       Production
  Cluster        Cluster        Cluster
```

**Hub-and-spoke** is simpler but creates a single point of failure. **Per-cluster**
is more resilient but requires managing multiple ArgoCD instances.

### RBAC in ArgoCD

ArgoCD uses Projects for RBAC boundaries:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: payments-team
  namespace: argocd
spec:
  description: "Payment team applications"

  # Allowed source repositories
  sourceRepos:
    - "https://github.com/acme/platform-config.git"
    - "https://github.com/acme/payment-charts.git"

  # Allowed destination clusters and namespaces
  destinations:
    - server: https://kubernetes.default.svc
      namespace: "payment-*"

  # Deny deploying cluster-scoped resources
  clusterResourceWhitelist: []

  # Allow specific namespace-scoped resources
  namespaceResourceWhitelist:
    - group: ""
      kind: "Service"
    - group: "apps"
      kind: "Deployment"
    - group: "networking.k8s.io"
      kind: "Ingress"

  # Role definitions
  roles:
    - name: developer
      description: "Read-only access + sync"
      policies:
        - p, proj:payments-team:developer, applications, get, payments-team/*, allow
        - p, proj:payments-team:developer, applications, sync, payments-team/*, allow
      groups:
        - payments-devs      # SSO group

    - name: admin
      description: "Full access to payment apps"
      policies:
        - p, proj:payments-team:admin, applications, *, payments-team/*, allow
      groups:
        - payments-leads
```

### Notifications

ArgoCD Notifications sends alerts on sync events:

```yaml
# argocd-notifications-cm ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-notifications-cm
  namespace: argocd
data:
  service.slack: |
    token: $slack-token

  template.app-sync-succeeded: |
    message: |
      Application {{.app.metadata.name}} sync succeeded.
      Revision: {{.app.status.sync.revision}}

  template.app-sync-failed: |
    message: |
      Application {{.app.metadata.name}} sync FAILED.
      Details: {{.app.status.conditions}}

  trigger.on-sync-succeeded: |
    - when: app.status.operationState.phase in ['Succeeded']
      send: [app-sync-succeeded]

  trigger.on-sync-failed: |
    - when: app.status.operationState.phase in ['Error', 'Failed']
      send: [app-sync-failed]
```

Annotate Applications to subscribe:

```yaml
metadata:
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: "#deployments"
    notifications.argoproj.io/subscribe.on-sync-failed.slack: "#incidents"
```

### Monitoring ArgoCD Itself

ArgoCD exposes Prometheus metrics. Key metrics to monitor:

```yaml
# Prometheus alerting rules for ArgoCD
groups:
  - name: argocd
    rules:
      - alert: ArgoAppOutOfSync
        expr: argocd_app_info{sync_status="OutOfSync"} == 1
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "ArgoCD app {{ $labels.name }} is OutOfSync for 30m"

      - alert: ArgoAppDegraded
        expr: argocd_app_info{health_status="Degraded"} == 1
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "ArgoCD app {{ $labels.name }} is Degraded"

      - alert: ArgoRepoServerHighLatency
        expr: >
          histogram_quantile(0.99,
            sum(rate(argocd_git_request_duration_seconds_bucket[5m])) by (le)
          ) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "ArgoCD repo server p99 latency is above 10s"

      - alert: ArgoControllerReconcileErrors
        expr: >
          sum(rate(argocd_app_reconcile_count{result="error"}[5m])) > 0
        for: 5m
        labels:
          severity: warning
```

### Common Mistakes

1. **Storing secrets in plain text**: Even in "private" repos, plain-text secrets
   are a breach waiting to happen.

2. **Not separating app and config repos**: Mixing application code with deployment
   manifests leads to confusing Git history and unclear ownership.

3. **Auto-sync without self-heal**: If you auto-sync but do not self-heal, manual
   drift persists until the next Git change. Go all the way or document why not.

4. **Ignoring ArgoCD resource limits**: The repo server and application controller
   need adequate CPU and memory. Under-provisioned ArgoCD is slow and unreliable.

5. **Too many sync waves**: Complex sync wave chains are fragile. If wave 3 depends
   on wave 2 which depends on wave 1, a failure in wave 1 blocks everything. Keep
   it simple.

6. **Not using Projects for RBAC**: All apps in the `default` project can deploy
   anything anywhere. Set up Projects early.

7. **Manual Application creation**: Creating Applications with the CLI instead of
   YAML manifests in Git undermines GitOps principles.

8. **No webhook configuration**: Relying on 3-minute polling adds unnecessary delay.
   Configure webhooks for near-instant sync.

---

## Step-by-Step Practical

### Production ArgoCD Hardening Checklist

**Step 1: Change the admin password and disable admin login**

```bash
argocd account update-password
```

```yaml
# argocd-cm ConfigMap
data:
  admin.enabled: "false"    # Disable local admin after SSO is configured
  url: https://argocd.example.com
  oidc.config: |
    name: Okta
    issuer: https://example.okta.com
    clientID: abc123
    clientSecret: $oidc.okta.clientSecret
    requestedScopes: ["openid", "profile", "email", "groups"]
```

**Step 2: Configure resource limits for ArgoCD components**

```yaml
# Helm values for production ArgoCD
controller:
  resources:
    requests:
      cpu: 500m
      memory: 512Mi
    limits:
      cpu: 2000m
      memory: 2Gi
  metrics:
    enabled: true

repoServer:
  resources:
    requests:
      cpu: 250m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi
  replicas: 2

server:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
  replicas: 2
  ingress:
    enabled: true
    hosts:
      - argocd.example.com
    tls:
      - secretName: argocd-tls
        hosts:
          - argocd.example.com

redis:
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
```

**Step 3: Set up a Grafana dashboard for ArgoCD**

Import ArgoCD's official Grafana dashboard (ID: 14584) and add panels for:
- Application sync status distribution
- Reconciliation latency
- Git request duration
- API server request rate
- Repo server cache hit ratio

**Step 4: Configure webhook for your Git provider**

```bash
# GitHub webhook URL
https://argocd.example.com/api/webhook

# Content type: application/json
# Secret: (generate with `openssl rand -hex 32`)
# Events: Push events only
```

```yaml
# argocd-secret (add webhook secret)
apiVersion: v1
kind: Secret
metadata:
  name: argocd-secret
  namespace: argocd
stringData:
  webhook.github.secret: "your-webhook-secret-here"
```

**Step 5: Create Projects for team isolation**

```bash
argocd proj create payments-team \
  --src https://github.com/acme/platform-config.git \
  --dest https://kubernetes.default.svc,payment-* \
  --description "Payment team applications"
```

---

## Exercises

### Exercise 1: Config Repo Separation
Take an existing application with deployment manifests in the same repo as source
code. Move the manifests to a separate config repo. Set up CI in the app repo to
update image tags in the config repo after a successful build.

### Exercise 2: ArgoCD Image Updater
Install ArgoCD Image Updater and configure it to automatically detect new image tags
for one of your applications. Push a new image tag to your container registry and
verify the automatic update flow.

### Exercise 3: RBAC Setup
Create two ArgoCD Projects: one for the "frontend-team" (allowed to deploy to
frontend-* namespaces) and one for the "backend-team" (allowed to deploy to
backend-* namespaces). Verify that cross-project access is denied.

### Exercise 4: Disaster Recovery Drill
Intentionally delete ArgoCD from your cluster (the namespace and all resources).
Then reinstall ArgoCD and re-apply your root app. Document how long it takes for
full recovery and verify all applications are restored.

### Exercise 5: Monitoring Setup
Deploy Prometheus and Grafana alongside ArgoCD. Configure Prometheus to scrape
ArgoCD metrics. Create at least three alerting rules (OutOfSync for 30 minutes,
Degraded health, high reconciliation error rate).

---

## Knowledge Check

### Question 1
Why should the application source code repository be separate from the GitOps
configuration repository?

<details>
<summary>Answer</summary>

Separation provides:
1. **Clean audit trail** — The config repo shows only deployment changes, not
   interleaved code commits.
2. **Different permissions** — Developers push to the app repo; config changes go
   through a separate review process.
3. **Decoupled lifecycles** — CI failures do not affect deployment state. Config
   changes do not trigger builds.
4. **Different change cadences** — Code changes frequently; deployment config
   changes less often.

</details>

### Question 2
How does ArgoCD Image Updater automate the deployment pipeline?

<details>
<summary>Answer</summary>

ArgoCD Image Updater continuously polls container registries for new image tags
matching a configured pattern (e.g., semver ~v3). When it finds a newer tag, it
either: (a) overrides the image tag directly in the ArgoCD Application's live
parameters, or (b) writes the updated tag back to the Git config repo
(`write-back-method: git`). The Git write-back method is preferred because it
maintains the Git-as-source-of-truth principle.

</details>

### Question 3
What is the hub-and-spoke pattern for multi-cluster GitOps, and what is its main
risk?

<details>
<summary>Answer</summary>

In the hub-and-spoke pattern, a single centralized ArgoCD instance (the hub) manages
multiple remote clusters (the spokes). All Application definitions, sync policies,
and RBAC live in one place.

The main risk is a **single point of failure**: if the hub ArgoCD instance goes down,
no cluster can sync. Additionally, the hub needs network access to all spoke clusters,
which expands the security surface. Mitigation includes running ArgoCD in HA mode
with multiple replicas and ensuring spoke clusters can continue operating with their
last-known-good state until the hub recovers.

</details>

### Question 4
Name three common mistakes teams make when adopting GitOps.

<details>
<summary>Answer</summary>

1. **Storing secrets in plain text in Git** — even in private repos, this violates
   security best practices. Use Sealed Secrets, External Secrets Operator, or SOPS.
2. **Not separating app and config repos** — leads to confusing Git history, unclear
   ownership, and coupled pipelines.
3. **Creating Applications via CLI instead of YAML in Git** — undermines the GitOps
   principle that everything should be declarative and version-controlled.

Other common mistakes include: not configuring webhooks (relying on slow polling),
not setting up RBAC Projects, and under-provisioning ArgoCD resources.

</details>

### Question 5
What topics are covered in the GitOps Certified Associate (CGOA) exam?

<details>
<summary>Answer</summary>

The CNCF GitOps Certified Associate exam covers:
1. **GitOps Terminology** — Desired state, drift, reconciliation, living/dead state.
2. **GitOps Principles** — The four OpenGitOps principles (declarative, versioned,
   pulled automatically, continuously reconciled).
3. **Related Practices** — Configuration as Code, Infrastructure as Code, DevOps,
   CI/CD relationship to GitOps.
4. **GitOps Patterns** — Repo structure, environment promotion, secret management.
5. **Tooling** — ArgoCD and Flux as reference implementations, their architectures,
   and how they implement GitOps principles.

</details>
