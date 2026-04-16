# Lesson 05: GitOps Repository Structure

## Why This Matters in DevOps

The most common reason GitOps implementations fail is not tooling — it is repository
structure. Teams that dump everything into a single directory, mix application code
with deployment manifests, or lack a convention for environment promotion end up
with a tangled mess that is harder to manage than the manual process it replaced.

Good repository structure is the foundation of scalable GitOps. It determines how
teams collaborate, how changes flow between environments, how RBAC is enforced, and
how disaster recovery works. Getting this right early saves months of painful
refactoring later.

---

## Core Concepts

### App-of-Apps Pattern

Instead of manually creating each ArgoCD Application, you create one "root"
Application that points to a directory of Application manifests:

```
argocd-apps/              # Root app points here
  payment-service.yaml    # ArgoCD Application for payment-service
  user-service.yaml       # ArgoCD Application for user-service
  web-frontend.yaml       # ArgoCD Application for web-frontend
  monitoring.yaml         # ArgoCD Application for monitoring stack
```

```yaml
# root-app.yaml — The single Application you create manually
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/acme/platform-config.git
    targetRevision: HEAD
    path: argocd-apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
```

ArgoCD syncs the root app, which creates all child Applications, which in turn sync
their respective services. Adding a new service means adding one YAML file to the
`argocd-apps/` directory.

### Monorepo vs Polyrepo for GitOps

#### Monorepo (Single Config Repository)

```
platform-config/
  argocd-apps/
  apps/
    payment-service/
    user-service/
    web-frontend/
  infrastructure/
    cert-manager/
    ingress-nginx/
    monitoring/
  clusters/
    dev/
    staging/
    production/
```

Advantages:
- Single place to see the entire platform state
- Atomic commits across multiple services
- Easier to onboard new team members
- Simpler ArgoCD configuration

Disadvantages:
- Large repos become slow (Git operations, ArgoCD polling)
- RBAC is harder (everyone has access to everything)
- PR reviews become noisy

#### Polyrepo (Multiple Config Repositories)

```
payment-config/       # Owned by payments team
  base/
  overlays/

user-config/          # Owned by identity team
  base/
  overlays/

platform-infra/       # Owned by platform team
  cert-manager/
  ingress-nginx/
  monitoring/
```

Advantages:
- Clear ownership boundaries
- Fine-grained Git permissions
- Smaller repos are faster

Disadvantages:
- Cross-cutting changes require multiple PRs
- ArgoCD needs access to many repos
- Harder to see the full platform picture

**Recommendation**: Start with a monorepo. Split into polyrepos only when team
boundaries and repository size demand it. Many companies at scale use a hybrid:
one platform-infra repo owned by the platform team, plus per-team config repos.

### Directory Structure Conventions

A production-grade monorepo structure:

```
platform-config/
│
├── argocd-apps/                    # App-of-apps root
│   ├── payment-service.yaml
│   ├── user-service.yaml
│   └── infrastructure.yaml
│
├── apps/                           # Application workloads
│   ├── payment-service/
│   │   ├── base/
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   ├── hpa.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── dev/
│   │       │   └── kustomization.yaml
│   │       ├── staging/
│   │       │   └── kustomization.yaml
│   │       └── production/
│   │           ├── kustomization.yaml
│   │           └── replica-patch.yaml
│   │
│   └── user-service/
│       ├── base/
│       └── overlays/
│
├── infrastructure/                 # Cluster infrastructure
│   ├── cert-manager/
│   │   ├── base/
│   │   └── overlays/
│   ├── ingress-nginx/
│   │   ├── base/
│   │   └── overlays/
│   └── monitoring/
│       ├── base/
│       └── overlays/
│
├── clusters/                       # Cluster-specific configs
│   ├── dev/
│   │   └── cluster-config.yaml
│   ├── staging/
│   │   └── cluster-config.yaml
│   └── production/
│       ├── cluster-config.yaml
│       └── network-policies.yaml
│
└── README.md
```

### Kustomize with ArgoCD

Kustomize is the preferred configuration management tool for GitOps because it
produces plain YAML (no templating engine, no Tiller) and supports patching:

```yaml
# apps/payment-service/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - deployment.yaml
  - service.yaml
  - hpa.yaml

commonLabels:
  app.kubernetes.io/name: payment-service
  app.kubernetes.io/managed-by: argocd
```

```yaml
# apps/payment-service/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namespace: payment-production

images:
  - name: acme/payment-service
    newTag: v3.2.1

patches:
  - path: replica-patch.yaml
  - target:
      kind: Deployment
      name: payment-service
    patch: |
      - op: add
        path: /spec/template/spec/containers/0/env/-
        value:
          name: LOG_LEVEL
          value: "warn"

configMapGenerator:
  - name: payment-config
    literals:
      - DATABASE_HOST=db.production.internal
      - CACHE_TTL=300
```

ArgoCD detects Kustomize automatically when a `kustomization.yaml` file exists.

### Helm with ArgoCD

For third-party charts or when your team prefers Helm:

```yaml
# ArgoCD Application using a Helm chart
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ingress-nginx
  namespace: argocd
spec:
  source:
    repoURL: https://kubernetes.github.io/ingress-nginx
    chart: ingress-nginx
    targetRevision: 4.8.3
    helm:
      releaseName: ingress-nginx
      valuesObject:
        controller:
          replicaCount: 3
          service:
            type: LoadBalancer
          metrics:
            enabled: true
          resources:
            requests:
              cpu: 250m
              memory: 256Mi
  destination:
    server: https://kubernetes.default.svc
    namespace: ingress-system
```

For local Helm charts in your repo:

```
apps/payment-service/
  Chart.yaml
  values.yaml
  values-dev.yaml
  values-staging.yaml
  values-production.yaml
  templates/
    deployment.yaml
    service.yaml
```

```yaml
# ArgoCD Application with environment-specific values
spec:
  source:
    repoURL: https://github.com/acme/platform-config.git
    path: apps/payment-service
    helm:
      valueFiles:
        - values.yaml
        - values-production.yaml
```

### Managing Secrets in GitOps

The biggest challenge in GitOps: secrets cannot be stored in plain text in Git.
Three leading solutions:

#### Option 1: Sealed Secrets (Bitnami)

Encrypts secrets with a cluster-specific key. Only the controller in the cluster
can decrypt them.

```bash
# Install the controller
helm install sealed-secrets sealed-secrets/sealed-secrets \
  -n kube-system

# Install the CLI
brew install kubeseal   # or download from GitHub

# Seal a secret
kubectl create secret generic db-credentials \
  --from-literal=username=admin \
  --from-literal=password=s3cretP@ss \
  --dry-run=client -o yaml | \
  kubeseal --format=yaml > sealed-db-credentials.yaml
```

```yaml
# sealed-db-credentials.yaml (safe to commit to Git)
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: db-credentials
  namespace: payment-service
spec:
  encryptedData:
    username: AgBk3j9...long-encrypted-string...==
    password: AgCx8m2...long-encrypted-string...==
```

#### Option 2: External Secrets Operator

Fetches secrets from external providers (AWS Secrets Manager, HashiCorp Vault,
GCP Secret Manager, Azure Key Vault) at runtime.

```yaml
# Tell ESO where to find the secret
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: payment-service
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: db-credentials       # K8s Secret to create
  data:
    - secretKey: username
      remoteRef:
        key: production/payment-service/db
        property: username
    - secretKey: password
      remoteRef:
        key: production/payment-service/db
        property: password
```

#### Option 3: SOPS (Mozilla)

Encrypts YAML values in place using AWS KMS, GCP KMS, Azure Key Vault, or PGP.
ArgoCD has a plugin for SOPS.

```yaml
# Encrypted with SOPS (only values are encrypted, keys are readable)
apiVersion: v1
kind: Secret
metadata:
  name: db-credentials
data:
  username: ENC[AES256_GCM,data:k3j9...==,iv:...,tag:...]
  password: ENC[AES256_GCM,data:x8m2...==,iv:...,tag:...]
sops:
  kms:
    - arn: arn:aws:kms:us-east-1:123456789:key/abc-def
  version: 3.8.1
```

**Recommendation**: Use External Secrets Operator for cloud environments (it keeps
secrets out of Git entirely). Use Sealed Secrets for air-gapped or simpler setups.

---

## Step-by-Step Practical

### Set Up a Full GitOps Repository

**Step 1: Initialize the repository structure**

```bash
mkdir -p platform-config/{argocd-apps,apps/demo-api/{base,overlays/{dev,production}},infrastructure/monitoring/base}
cd platform-config
git init
```

**Step 2: Create the base application manifests**

```yaml
# apps/demo-api/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-api
spec:
  replicas: 1
  selector:
    matchLabels:
      app: demo-api
  template:
    metadata:
      labels:
        app: demo-api
    spec:
      containers:
        - name: api
          image: hashicorp/http-echo:0.2.3
          args: ["-text=Hello from demo-api"]
          ports:
            - containerPort: 5678
          resources:
            requests:
              cpu: 50m
              memory: 32Mi
            limits:
              cpu: 100m
              memory: 64Mi
```

```yaml
# apps/demo-api/base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: demo-api
spec:
  selector:
    app: demo-api
  ports:
    - port: 80
      targetPort: 5678
```

```yaml
# apps/demo-api/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml
```

**Step 3: Create environment overlays**

```yaml
# apps/demo-api/overlays/dev/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: demo-api-dev
```

```yaml
# apps/demo-api/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base
namespace: demo-api-production
patches:
  - target:
      kind: Deployment
      name: demo-api
    patch: |
      - op: replace
        path: /spec/replicas
        value: 3
      - op: replace
        path: /spec/template/spec/containers/0/resources/requests/cpu
        value: "250m"
images:
  - name: hashicorp/http-echo
    newTag: "0.2.3"
```

**Step 4: Create ArgoCD Application manifests**

```yaml
# argocd-apps/demo-api-dev.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: demo-api-dev
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/platform-config.git
    targetRevision: HEAD
    path: apps/demo-api/overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: demo-api-dev
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
    syncOptions:
      - CreateNamespace=true
```

```yaml
# argocd-apps/demo-api-production.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: demo-api-production
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/platform-config.git
    targetRevision: HEAD
    path: apps/demo-api/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: demo-api-production
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
    syncOptions:
      - CreateNamespace=true
```

**Step 5: Create the root app**

```yaml
# root-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root-app
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-org/platform-config.git
    targetRevision: HEAD
    path: argocd-apps
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
```

**Step 6: Deploy**

```bash
git add .
git commit -m "Initial platform config structure"
git remote add origin https://github.com/your-org/platform-config.git
git push -u origin main

# Apply only the root app manually — everything else is automated
kubectl apply -f root-app.yaml
```

**Step 7: Verify the cascade**

```bash
argocd app list
```

```
NAME                     STATUS   HEALTH    SYNC
argocd/root-app          Synced   Healthy   Synced
argocd/demo-api-dev      Synced   Healthy   Synced
argocd/demo-api-prod     Synced   Healthy   Synced
```

---

## Exercises

### Exercise 1: Build a Monorepo
Create a GitOps monorepo with three applications (web, api, worker) each with dev
and production overlays. Use the app-of-apps pattern to manage them all from a
single root application.

### Exercise 2: Add a New Service
With the app-of-apps pattern in place, add a new service by creating its directory
structure and one Application YAML file. Verify that ArgoCD detects and deploys it
automatically.

### Exercise 3: Sealed Secrets
Install the Sealed Secrets controller on your cluster. Seal a database credential
and commit the SealedSecret to your GitOps repo. Verify that ArgoCD syncs it and
the regular Kubernetes Secret is created in the cluster.

### Exercise 4: Helm Chart via ArgoCD
Add a third-party Helm chart (e.g., Redis or PostgreSQL) to your GitOps repo using
an ArgoCD Application with the `helm` source type. Configure custom values per
environment.

---

## Knowledge Check

### Question 1
What is the app-of-apps pattern and why is it useful?

<details>
<summary>Answer</summary>

The app-of-apps pattern uses a single "root" ArgoCD Application that points to a
directory of child Application YAML manifests. ArgoCD syncs the root app, which
creates all child Applications, which in turn sync their respective services. This
means adding or removing a service requires only adding or removing a YAML file in
Git — no manual `argocd app create` commands. It is the GitOps way of managing
ArgoCD itself.

</details>

### Question 2
What are the three main approaches to managing secrets in GitOps?

<details>
<summary>Answer</summary>

1. **Sealed Secrets** — Encrypts secrets with a cluster-specific key. The encrypted
   SealedSecret resource is committed to Git; only the controller can decrypt it.
2. **External Secrets Operator** — Stores secrets in an external provider (AWS
   Secrets Manager, Vault, etc.) and creates Kubernetes Secrets at runtime. Nothing
   secret is ever in Git.
3. **SOPS (Mozilla)** — Encrypts YAML values in place using KMS or PGP. An ArgoCD
   plugin decrypts them during sync.

</details>

### Question 3
When should you choose a polyrepo strategy over a monorepo for GitOps?

<details>
<summary>Answer</summary>

Use polyrepo when:
- Teams need strict ownership boundaries with separate Git permissions.
- The monorepo has grown so large that Git operations and ArgoCD polling are slow.
- Regulatory requirements mandate separation of concerns (e.g., infrastructure vs
  application configs must be in separate repos with different access controls).

Start with a monorepo and split only when these pressures appear.

</details>

### Question 4
Why is Kustomize often preferred over Helm for GitOps?

<details>
<summary>Answer</summary>

Kustomize operates on plain YAML using patches and overlays — there is no templating
engine, no intermediate state, and the output is standard Kubernetes manifests.
This makes diffs in pull requests easy to read and audit. Helm uses Go templates,
which can obscure what the final rendered YAML looks like. However, Helm is still
valuable for third-party charts and complex parameterization; the two approaches
are often used together (Helm for external charts, Kustomize for internal apps).

</details>
