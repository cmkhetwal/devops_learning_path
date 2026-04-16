# Lesson 03: ArgoCD Applications

## Why This Matters in DevOps

A single ArgoCD Application pointing at one directory is fine for learning. In
production, you manage dozens or hundreds of services across multiple environments
(dev, staging, production) with different configurations, scaling requirements, and
rollout policies. ArgoCD provides sophisticated mechanisms for this: sync policies,
sync waves, hooks, and ApplicationSets. Mastering these features is the difference
between a toy GitOps setup and one that handles real enterprise complexity.

Understanding Application manifests deeply means you can encode your entire
deployment strategy as code — when things sync, in what order, what happens before
and after, and how to generate applications at scale.

---

## Core Concepts

### Application YAML Manifest

The Application custom resource is the fundamental building block of ArgoCD:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service
  namespace: argocd
  labels:
    team: payments
    env: production
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: payments-deploys
  finalizers:
    - resources-finalizer.argocd.argoproj.io   # Clean up K8s resources on delete
spec:
  project: payments-team       # RBAC boundary

  source:
    repoURL: https://github.com/acme/platform-config.git
    targetRevision: main       # Branch, tag, or commit SHA
    path: apps/payment-service/overlays/production

    # For Kustomize sources:
    kustomize:
      images:
        - acme/payment-service:v3.2.1

    # For Helm sources (alternative to kustomize block):
    # helm:
    #   releaseName: payment-service
    #   valueFiles:
    #     - values-production.yaml
    #   parameters:
    #     - name: image.tag
    #       value: v3.2.1

  destination:
    server: https://kubernetes.default.svc
    namespace: payment-service

  syncPolicy:
    automated:
      prune: true        # Delete resources removed from Git
      selfHeal: true     # Revert manual cluster changes
      allowEmpty: false  # Prevent accidental deletion of all resources
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas    # Ignore HPA-managed replica count
```

### Sync Policies

#### Manual Sync

With no `syncPolicy.automated` block, ArgoCD reports OutOfSync but takes no action.
A human must click "Sync" in the UI or run `argocd app sync`.

Use manual sync when:
- Deploying to production and wanting explicit human approval
- Running in a regulated environment requiring change control

#### Automatic Sync

```yaml
syncPolicy:
  automated:
    prune: false      # Do NOT delete orphaned resources
    selfHeal: false   # Do NOT revert manual changes
```

With `automated` enabled, ArgoCD syncs whenever it detects OutOfSync status. But the
two sub-options matter enormously:

**prune** — When `true`, resources that exist in the cluster but no longer exist in
Git are deleted. When `false`, orphaned resources are left running.

```
Scenario: You remove a ConfigMap from Git.
  prune: true  -> ArgoCD deletes the ConfigMap from the cluster
  prune: false -> ConfigMap remains, ArgoCD ignores it
```

**selfHeal** — When `true`, if someone manually changes a resource (e.g.,
`kubectl edit`), ArgoCD reverts the change within seconds.

```
Scenario: Someone runs kubectl scale deploy/api --replicas=10
  selfHeal: true  -> ArgoCD scales back to the value in Git
  selfHeal: false -> The manual change persists until next Git change
```

Production recommendation: `prune: true` + `selfHeal: true` for full GitOps. But
enable these incrementally — start with both false, gain confidence, then enable.

### Sync Waves and Hooks

Complex deployments require ordering. You cannot deploy a microservice before its
database schema is migrated, or create a Deployment before its Namespace exists.

#### Sync Waves

Resources are assigned a wave number via annotation. Lower waves sync first.

```yaml
# Wave 0: Namespace (default wave)
apiVersion: v1
kind: Namespace
metadata:
  name: payment-service
  annotations:
    argocd.argoproj.io/sync-wave: "0"

---
# Wave 1: ConfigMap and Secrets
apiVersion: v1
kind: ConfigMap
metadata:
  name: payment-config
  namespace: payment-service
  annotations:
    argocd.argoproj.io/sync-wave: "1"

---
# Wave 2: Database migration job
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migrate
  namespace: payment-service
  annotations:
    argocd.argoproj.io/sync-wave: "2"
    argocd.argoproj.io/hook: PreSync

---
# Wave 3: Application deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  namespace: payment-service
  annotations:
    argocd.argoproj.io/sync-wave: "3"
```

ArgoCD processes waves sequentially: all wave-0 resources must be healthy before
wave-1 begins, and so on.

#### Sync Hooks

Hooks run at specific phases of the sync lifecycle:

| Hook        | When It Runs                          | Use Case                    |
|-------------|---------------------------------------|-----------------------------|
| `PreSync`   | Before the main sync                  | Database migrations, backups|
| `Sync`      | During the main sync (with manifests) | Rarely used explicitly      |
| `PostSync`  | After all resources are healthy       | Smoke tests, notifications  |
| `SyncFail`  | When sync fails                       | Cleanup, alerts             |
| `Skip`      | Skips the resource during sync        | Manual-only resources       |

```yaml
# PostSync hook: run smoke tests after deployment
apiVersion: batch/v1
kind: Job
metadata:
  name: smoke-test
  namespace: payment-service
  annotations:
    argocd.argoproj.io/hook: PostSync
    argocd.argoproj.io/hook-delete-policy: HookSucceeded
spec:
  template:
    spec:
      containers:
        - name: smoke
          image: acme/smoke-tests:latest
          command: ["./run-tests.sh", "--target=payment-service"]
      restartPolicy: Never
  backoffLimit: 1
```

`hook-delete-policy` controls cleanup:
- `HookSucceeded` — Delete the Job after it succeeds
- `HookFailed` — Delete after failure
- `BeforeHookCreation` — Delete previous hook before creating new one

### Managing Multiple Environments

Use Kustomize overlays to manage environment-specific configurations:

```
apps/payment-service/
  base/
    deployment.yaml
    service.yaml
    kustomization.yaml
  overlays/
    dev/
      kustomization.yaml          # patches for dev
      replica-count-patch.yaml
    staging/
      kustomization.yaml
    production/
      kustomization.yaml
      replica-count-patch.yaml
      resource-limits-patch.yaml
```

```yaml
# base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namePrefix: prod-
namespace: payment-production
patches:
  - path: replica-count-patch.yaml
  - path: resource-limits-patch.yaml
images:
  - name: acme/payment-service
    newTag: v3.2.1
```

```yaml
# overlays/production/replica-count-patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
spec:
  replicas: 10
```

Create one ArgoCD Application per environment:

```yaml
# Application for production
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: payment-service-production
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/acme/platform-config.git
    path: apps/payment-service/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: payment-production
```

### ApplicationSets

When you have 50 services across 3 environments, writing 150 Application manifests
is tedious. ApplicationSets generate Applications from templates.

#### List Generator

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: payment-service-environments
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - env: dev
            cluster: https://dev-cluster.example.com
            revision: develop
          - env: staging
            cluster: https://staging-cluster.example.com
            revision: release/3.2
          - env: production
            cluster: https://prod-cluster.example.com
            revision: main
  template:
    metadata:
      name: "payment-service-{{env}}"
    spec:
      project: payments-team
      source:
        repoURL: https://github.com/acme/platform-config.git
        targetRevision: "{{revision}}"
        path: "apps/payment-service/overlays/{{env}}"
      destination:
        server: "{{cluster}}"
        namespace: "payment-{{env}}"
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

This single ApplicationSet creates three Applications: `payment-service-dev`,
`payment-service-staging`, and `payment-service-production`.

#### Git Directory Generator

Automatically create Applications for every directory matching a pattern:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: all-apps
  namespace: argocd
spec:
  generators:
    - git:
        repoURL: https://github.com/acme/platform-config.git
        revision: HEAD
        directories:
          - path: "apps/*/overlays/production"
  template:
    metadata:
      name: "{{path[1]}}"    # Extracts service name from path
    spec:
      project: default
      source:
        repoURL: https://github.com/acme/platform-config.git
        targetRevision: HEAD
        path: "{{path}}"
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{path[1]}}"
```

Adding a new service is as simple as creating a new directory under `apps/`.

---

## Step-by-Step Practical

### Deploy a Multi-Environment Application

**Step 1: Create the directory structure**

```bash
mkdir -p apps/web-app/{base,overlays/{dev,staging,production}}
```

**Step 2: Write the base manifests**

```yaml
# apps/web-app/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
        - name: web
          image: nginx:1.25
          ports:
            - containerPort: 80
          env:
            - name: ENVIRONMENT
              value: "base"
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 200m
              memory: 256Mi
```

```yaml
# apps/web-app/base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  selector:
    app: web-app
  ports:
    - port: 80
      targetPort: 80
```

```yaml
# apps/web-app/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

**Step 3: Create environment overlays**

```yaml
# apps/web-app/overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: web-app-dev
patches:
  - target:
      kind: Deployment
      name: web-app
    patch: |
      - op: replace
        path: /spec/replicas
        value: 1
      - op: replace
        path: /spec/template/spec/containers/0/env/0/value
        value: "development"
```

```yaml
# apps/web-app/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: web-app-production
patches:
  - target:
      kind: Deployment
      name: web-app
    patch: |
      - op: replace
        path: /spec/replicas
        value: 5
      - op: replace
        path: /spec/template/spec/containers/0/env/0/value
        value: "production"
      - op: replace
        path: /spec/template/spec/containers/0/resources/requests/cpu
        value: "500m"
      - op: replace
        path: /spec/template/spec/containers/0/resources/limits/cpu
        value: "1000m"
```

**Step 4: Create the ApplicationSet**

```yaml
# applicationset-web-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: web-app
  namespace: argocd
spec:
  generators:
    - list:
        elements:
          - env: dev
          - env: staging
          - env: production
  template:
    metadata:
      name: "web-app-{{env}}"
    spec:
      project: default
      source:
        repoURL: https://github.com/your-org/platform-config.git
        targetRevision: HEAD
        path: "apps/web-app/overlays/{{env}}"
      destination:
        server: https://kubernetes.default.svc
        namespace: "web-app-{{env}}"
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
          - CreateNamespace=true
```

```bash
kubectl apply -f applicationset-web-app.yaml

# Verify three applications were created
argocd app list
```

Expected output:

```
NAME                 CLUSTER                         NAMESPACE            STATUS   HEALTH
argocd/web-app-dev   https://kubernetes.default.svc  web-app-dev          Synced   Healthy
argocd/web-app-stg   https://kubernetes.default.svc  web-app-staging      Synced   Healthy
argocd/web-app-prod  https://kubernetes.default.svc  web-app-production   Synced   Healthy
```

---

## Exercises

### Exercise 1: Sync Waves in Practice
Create an application with three sync waves: (0) Namespace and ConfigMap, (1) a
database StatefulSet, (2) the application Deployment. Verify that ArgoCD deploys
them in order by watching the sync progress.

### Exercise 2: PreSync Hook for Database Migration
Add a Kubernetes Job as a PreSync hook that runs a database migration script before
the main application is deployed. Verify the Job completes before the Deployment
starts.

### Exercise 3: Self-Heal Experiment
Enable `selfHeal: true` on an application. Manually change a resource with
`kubectl edit` and observe how quickly ArgoCD reverts the change. Measure the time.

### Exercise 4: ApplicationSet with Git Generator
Create an ApplicationSet that uses the Git directory generator to automatically
create Applications for every subdirectory under `apps/`. Add a new service
directory and verify a new Application appears automatically.

### Exercise 5: Ignore Differences
Deploy an application with an HPA (Horizontal Pod Autoscaler). Configure ArgoCD to
ignore the `spec.replicas` field so it does not fight with the HPA. Verify that
scaling events do not cause OutOfSync status.

---

## Knowledge Check

### Question 1
What is the difference between `prune: true` and `selfHeal: true`?

<details>
<summary>Answer</summary>

**prune** controls what happens to resources that exist in the cluster but have been
removed from Git. When true, ArgoCD deletes them. When false, they are orphaned.

**selfHeal** controls what happens when someone manually changes a resource in the
cluster. When true, ArgoCD reverts the change to match Git. When false, the manual
change persists until the next Git-triggered sync.

</details>

### Question 2
In what order does ArgoCD process sync waves?

<details>
<summary>Answer</summary>

ArgoCD processes sync waves in ascending numeric order (lowest wave number first).
All resources in a wave must reach a healthy state before the next wave begins.
Negative wave numbers are allowed and processed first. The default wave is 0.

</details>

### Question 3
What are the three types of sync hooks, and when does each run?

<details>
<summary>Answer</summary>

- **PreSync** — Runs before the main resources are synced. Used for database
  migrations, backups, and pre-deployment checks.
- **Sync** — Runs alongside the main resources during sync.
- **PostSync** — Runs after all resources are synced and healthy. Used for smoke
  tests, notifications, and cleanup.

Additional hooks: **SyncFail** (runs when sync fails) and **Skip** (resource is
excluded from sync).

</details>

### Question 4
How do ApplicationSets reduce repetitive configuration?

<details>
<summary>Answer</summary>

ApplicationSets use generators (list, git, cluster, matrix, merge) to produce
parameters that are substituted into an Application template. Instead of writing one
Application manifest per service per environment, you write one ApplicationSet that
generates all of them. Adding a new environment or service requires only updating
the generator input, not creating new manifests.

</details>
