# Building an Internal Developer Platform

## Why This Matters in DevOps

An Internal Developer Platform (IDP) is more than just Backstage or a collection of tools -- it is an integrated system where each component connects to form a seamless developer experience. The difference between a good IDP and a collection of disconnected tools is integration: when a developer creates a new service in Backstage, it automatically gets a CI/CD pipeline, ArgoCD deployment, monitoring dashboard, and infrastructure provisioned via Crossplane -- all without the developer filing a single ticket. Building this requires understanding how components fit together and designing the integration architecture.

---

## Core Concepts

### Components of an IDP

```
┌────────────────────────────────────────────────────────┐
│                Internal Developer Platform              │
│                                                        │
│  Layer 1: Developer Interface                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Backstage (Portal)     │ CLI Tools   │ ChatOps   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  Layer 2: Integration & Orchestration                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ ArgoCD (GitOps)  │ Crossplane (IaC)  │ Vault     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  Layer 3: CI/CD                                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ GitHub Actions / Dagger │ Container Registry      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  Layer 4: Runtime                                      │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Kubernetes (EKS) │ Karpenter │ Service Mesh      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  Layer 5: Observability                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Prometheus │ Grafana │ Loki │ Tempo │ PagerDuty  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                        │
│  Layer 6: Security & Compliance                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │ OPA/Kyverno │ Trivy │ Falco │ Vault │ Cert-mgr  │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

### Reference Architecture: Backstage + ArgoCD + Crossplane

```
Developer Journey: "I need a new microservice with a database"
─────────────────────────────────────────────────────────────

1. Backstage Template Wizard
   Developer fills in: name, team, database size
   │
   ├── Creates GitHub repo from template
   │   ├── Application code (FastAPI/Express)
   │   ├── Dockerfile
   │   ├── Helm chart (deploy/)
   │   ├── CI/CD workflow (.github/workflows/)
   │   ├── catalog-info.yaml
   │   └── crossplane/ (infrastructure claims)
   │
   ├── Creates ArgoCD Application
   │   └── Points to deploy/ in the new repo
   │
   └── Registers in Backstage Catalog
       └── Service appears in portal immediately

2. Developer pushes code
   │
   ├── GitHub Actions runs:
   │   ├── Lint + Test
   │   ├── Build Docker image
   │   ├── Push to ECR
   │   └── Update Helm values (image tag)
   │
   └── ArgoCD detects change:
       ├── Syncs Helm chart to Kubernetes
       ├── Syncs Crossplane Claims (database)
       └── Application running with database

3. Crossplane provisions infrastructure
   │
   ├── Database Claim → RDS instance
   ├── Cache Claim → ElastiCache
   └── Connection secrets → Kubernetes Secrets
       └── Mounted in application pods

4. Monitoring automatically active
   │
   ├── Prometheus scrapes metrics (via annotations)
   ├── Grafana dashboard (from template)
   ├── Loki collects logs (via DaemonSet)
   └── PagerDuty alerts (via rules)
```

### Building Golden Paths

A golden path is implemented through multiple integrated components:

```yaml
# golden-path-definition.yaml
name: "Python Microservice Golden Path"
version: "2.0"

components:
  repository:
    template: "python-fastapi-template"
    structure:
      - src/           # Application code
      - tests/         # Test suite
      - deploy/        # Helm chart
        - Chart.yaml
        - values.yaml
        - values-dev.yaml
        - values-staging.yaml
        - values-prod.yaml
      - infra/          # Crossplane claims
        - database.yaml
        - cache.yaml
      - .github/workflows/
        - ci.yaml       # Build and test
        - cd.yaml       # Deploy via ArgoCD
      - Dockerfile
      - catalog-info.yaml
      - mkdocs.yml      # Documentation

  ci_cd:
    tool: "GitHub Actions"
    pipeline:
      - lint (ruff, mypy)
      - test (pytest, coverage > 80%)
      - security scan (trivy, gitleaks)
      - build (docker buildx multi-arch)
      - push (ECR)
      - deploy (update Helm values, ArgoCD syncs)

  deployment:
    tool: "ArgoCD"
    strategy: "progressive"
    environments:
      dev: auto-deploy on push to main
      staging: auto-deploy after dev succeeds
      production: manual approval required

  infrastructure:
    tool: "Crossplane"
    resources:
      database:
        claim: "Database"
        default_size: "small"
      cache:
        claim: "Cache"
        optional: true

  observability:
    metrics: "Prometheus (auto-scrape via annotations)"
    logging: "Loki (automatic via DaemonSet)"
    tracing: "Tempo (auto-instrumented via OpenTelemetry)"
    dashboards: "Grafana (provisioned from template)"
    alerting: "PagerDuty (on-call from Backstage ownership)"
```

---

## Step-by-Step Practical

### Design an IDP for Self-Service Microservice Deployment

**Step 1: Define the Developer Experience**

```
Developer Story:
"As a developer, I want to create a new microservice and have it
running in dev within 30 minutes, without talking to anyone."

Steps:
1. Go to Backstage → Create → "Python Microservice"
2. Fill in: name="payment-processor", team="team-payments"
3. Check: "needs database (PostgreSQL, medium)"
4. Click "Create"
5. Clone the generated repository
6. Write my business logic
7. Push → automatic deployment to dev
8. See my service in Backstage with monitoring links
```

**Step 2: Implement the Template**

```yaml
# backstage-template.yaml (simplified)
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: python-microservice
  title: Python Microservice
spec:
  owner: platform-team
  type: service
  parameters:
    - title: Service Details
      properties:
        name:
          type: string
          title: Service Name
        owner:
          type: string
          title: Team
          ui:field: OwnerPicker
        needsDatabase:
          type: boolean
          default: true
        databaseSize:
          type: string
          enum: ["small", "medium", "large"]
          default: "small"
  steps:
    - id: fetch
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          owner: ${{ parameters.owner }}
          needsDatabase: ${{ parameters.needsDatabase }}
          databaseSize: ${{ parameters.databaseSize }}
    - id: publish
      action: publish:github
      input:
        repoUrl: github.com?repo=${{ parameters.name }}&owner=mycompany
    - id: argocd
      action: argocd:create-resources
      input:
        appName: ${{ parameters.name }}
        repoUrl: ${{ steps.publish.output.remoteUrl }}
        path: deploy/
    - id: register
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: /catalog-info.yaml
```

**Step 3: Template Skeleton Files**

```yaml
# skeleton/deploy/values.yaml
replicaCount: 2
image:
  repository: 123456789.dkr.ecr.us-east-1.amazonaws.com/${{ values.name }}
  tag: latest
service:
  port: 8080
resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

{% if values.needsDatabase %}
database:
  enabled: true
  size: ${{ values.databaseSize }}
{% endif %}
```

```yaml
# skeleton/infra/database.yaml (only if needsDatabase)
{% if values.needsDatabase %}
apiVersion: platform.mycompany.io/v1alpha1
kind: Database
metadata:
  name: ${{ values.name }}-db
  namespace: ${{ values.name }}
spec:
  parameters:
    engine: postgresql
    size: ${{ values.databaseSize }}
    environment: dev
  compositionSelector:
    matchLabels:
      provider: aws
  writeConnectionSecretToRef:
    name: ${{ values.name }}-db-connection
{% endif %}
```

```yaml
# skeleton/.github/workflows/ci.yaml
name: CI/CD
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: ruff check src/
      - run: pytest tests/ --cov=src --cov-report=term-missing

  build-and-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions
          aws-region: us-east-1
      - uses: aws-actions/amazon-ecr-login@v2
      - run: |
          docker build -t ${{ values.name }}:$GITHUB_SHA .
          docker tag ${{ values.name }}:$GITHUB_SHA 123456789.dkr.ecr.us-east-1.amazonaws.com/${{ values.name }}:$GITHUB_SHA
          docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/${{ values.name }}:$GITHUB_SHA
      - run: |
          yq e ".image.tag = \"$GITHUB_SHA\"" -i deploy/values.yaml
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add deploy/values.yaml
          git commit -m "chore: update image tag to $GITHUB_SHA"
          git push
```

**Step 4: ArgoCD Application Template**

```yaml
# skeleton/deploy/argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ${{ values.name }}-dev
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/mycompany/${{ values.name }}.git
    targetRevision: main
    path: deploy
    helm:
      valueFiles:
        - values.yaml
        - values-dev.yaml
  destination:
    server: https://kubernetes.default.svc
    namespace: ${{ values.name }}
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

---

## Exercises

1. **IDP Architecture Design**: Design a complete IDP architecture diagram for a company with 50 engineers, 30 microservices, running on AWS EKS. Include every component, how they connect, and the data flow for a developer deploying a new feature.

2. **End-to-End Golden Path**: Implement a complete golden path: Backstage template that creates a repo with CI/CD (GitHub Actions), deploys to Kubernetes via ArgoCD, and provisions a database via Crossplane. Test the entire flow from template creation to running application.

3. **Multi-Environment Promotion**: Design and implement a promotion workflow: dev (auto-deploy on push) -> staging (auto-deploy after tests pass) -> production (manual approval in ArgoCD). Include smoke tests at each stage.

4. **Self-Service Infrastructure Menu**: Create a Crossplane Composition library with Claims for: PostgreSQL (small/medium/large), Redis (basic/ha), S3 Bucket (standard/archive), and SQS Queue. Register each as a Backstage template so developers can provision any of them.

5. **IDP Metrics Dashboard**: Build a Grafana dashboard that shows: number of services in the catalog, deployments per day, average lead time, failed deployments, and platform adoption rate (services using golden path vs. custom).

---

## Knowledge Check

**Q1: What are the essential layers of an Internal Developer Platform?**

<details>
<summary>Answer</summary>

Six essential layers: (1) **Developer Interface** -- the portal (Backstage), CLI tools, and ChatOps where developers interact with the platform. (2) **Integration & Orchestration** -- GitOps (ArgoCD/Flux) for deployment, Crossplane for infrastructure, Vault for secrets. (3) **CI/CD** -- build, test, and delivery pipelines (GitHub Actions, Dagger). (4) **Runtime** -- Kubernetes, Karpenter for scaling, service mesh for networking. (5) **Observability** -- metrics (Prometheus), logs (Loki), traces (Tempo), dashboards (Grafana), alerting (PagerDuty). (6) **Security & Compliance** -- policy engines (OPA/Kyverno), vulnerability scanning (Trivy), runtime security (Falco), certificate management.
</details>

**Q2: How do Backstage, ArgoCD, and Crossplane work together in an IDP?**

<details>
<summary>Answer</summary>

Backstage is the developer interface -- developers create new services using Software Templates. The template generates a Git repository with application code, Helm charts (for ArgoCD), and Crossplane Claims (for infrastructure). ArgoCD watches the repository and continuously syncs the Kubernetes manifests to the cluster, deploying the application. Crossplane Claims in the repository tell Crossplane to provision cloud resources (databases, caches, queues). The connection details flow back as Kubernetes Secrets that ArgoCD-deployed pods consume. All three tools operate declaratively through Git, creating a fully GitOps-driven platform.
</details>

**Q3: What is the difference between a golden path and a mandate?**

<details>
<summary>Answer</summary>

A golden path is the recommended, well-supported way to accomplish a task (deploying a service, provisioning a database). It is the easiest, fastest, and safest option. A mandate is a requirement that developers must follow. Golden paths are opt-in; mandates are forced. The distinction matters because: (1) mandates create resentment and workarounds, (2) golden paths create adoption through value -- developers choose them because they save time, (3) if the golden path does not cover a use case, developers can deviate, (4) high adoption of golden paths (>80%) indicates a successful platform. If you find yourself mandating the golden path, it is a sign the path needs improvement, not enforcement.
</details>

**Q4: How do you handle services that do not fit the golden path?**

<details>
<summary>Answer</summary>

Expect 10-20% of services to not fit the golden path. Handle them by: (1) Creating multiple golden paths for different service types (REST API, event-driven, static website, ML model serving). (2) Making templates extensible -- parameters that toggle optional features (database, cache, GPU). (3) Allowing customization -- developers can modify the generated code after scaffolding. (4) Tracking deviations -- when developers deviate, understand why and consider updating the golden path. (5) Not blocking -- if the platform cannot support a use case, let the team proceed with manual setup and create a backlog item to support it in the future.
</details>
