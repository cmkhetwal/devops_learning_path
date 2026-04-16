# Helm Philosophy: Package Management for Kubernetes

## Why This Matters in DevOps

Every Kubernetes application requires multiple YAML manifests: Deployments, Services,
ConfigMaps, Secrets, Ingresses, ServiceAccounts, RBAC rules, and more. A single
microservice might need eight or more files. Multiply that by fifty microservices,
three environments, and two clusters, and you are managing thousands of YAML files
by hand. Helm exists to solve this problem.

Helm is the package manager for Kubernetes. Just as `apt` manages packages on Debian
or `pip` manages Python libraries, Helm manages Kubernetes applications. It bundles
related manifests into a single deployable unit called a **chart**, parameterizes them
with values, and tracks installed releases so you can upgrade, rollback, or uninstall
cleanly.

Without Helm, teams resort to fragile shell scripts that string together `kubectl apply`
commands, copy-paste YAML between environments, and lose track of what version is
deployed where. Helm replaces all of that with a repeatable, versioned, configurable
deployment mechanism.

---

## Core Concepts

### The Problem Helm Solves

Consider deploying a typical web application to Kubernetes:

```
my-app/
  deployment.yaml       # The workload
  service.yaml          # Internal networking
  ingress.yaml          # External access
  configmap.yaml        # Configuration
  secret.yaml           # Credentials
  hpa.yaml              # Autoscaling
  pdb.yaml              # Disruption budget
  serviceaccount.yaml   # Identity
  networkpolicy.yaml    # Security
```

Now consider these realities:
- Staging uses 2 replicas; production uses 6
- The image tag changes with every release
- Different environments have different domain names
- Resource limits vary per environment
- Some environments need TLS certificates, others do not

Manually maintaining separate copies of these files per environment is error-prone
and does not scale. Helm treats these manifests as templates and injects
environment-specific values at deploy time.

### What Is a Helm Chart?

A Helm chart is a collection of files that describe a Kubernetes application. It
contains:

- **Chart.yaml** - Metadata (name, version, description, dependencies)
- **values.yaml** - Default configuration values
- **templates/** - Kubernetes manifests with Go template syntax
- **charts/** - Dependency charts (subcharts)
- **README.md** - Documentation
- **LICENSE** - Licensing information

Charts are versioned independently from the application they deploy. Chart version
`1.3.0` might deploy application version `2.7.1`. This separation is intentional:
the chart (deployment packaging) evolves at a different pace than the application
(business logic).

### Helm 3 Architecture (No Tiller)

Helm 2 required a server-side component called **Tiller** that ran inside the
cluster with broad RBAC permissions. This was a significant security concern because
Tiller effectively had cluster-admin access.

Helm 3 removed Tiller entirely. The architecture is now client-only:

```
Helm 2:
  helm CLI --> Tiller (in-cluster) --> Kubernetes API

Helm 3:
  helm CLI --> Kubernetes API (directly)
```

Key improvements in Helm 3:
- **No Tiller** - Uses the user's kubeconfig credentials directly
- **Release namespaced** - Releases are namespace-scoped, not global
- **Three-way merge** - Upgrades consider the live state, not just the previous chart
- **JSON Schema validation** - Charts can validate values before rendering
- **OCI support** - Charts can be stored in OCI-compliant container registries

### Chart Repositories and Artifact Hub

Charts are distributed through **repositories**, which are HTTP servers hosting
an `index.yaml` file and packaged chart archives (`.tgz` files).

Common repositories:

| Repository | URL | Contents |
|---|---|---|
| Bitnami | https://charts.bitnami.com/bitnami | Databases, web servers, tools |
| Prometheus Community | https://prometheus-community.github.io/helm-charts | Monitoring stack |
| Ingress-Nginx | https://kubernetes.github.io/ingress-nginx | Nginx Ingress controller |
| Jetstack | https://charts.jetstack.io | cert-manager |

**Artifact Hub** (https://artifacthub.io) is a centralized search engine for Helm
charts, similar to Docker Hub for container images. It indexes charts from hundreds
of repositories and provides metadata, security reports, and documentation.

Starting with Helm 3.8, charts can also be stored as OCI artifacts in container
registries like Docker Hub, GitHub Container Registry (GHCR), Amazon ECR, and
Google Artifact Registry. This eliminates the need for separate chart repository
infrastructure.

```bash
# OCI-based chart operations
helm push my-chart-1.0.0.tgz oci://ghcr.io/myorg/charts
helm pull oci://ghcr.io/myorg/charts/my-chart --version 1.0.0
helm install my-release oci://ghcr.io/myorg/charts/my-chart --version 1.0.0
```

### Helm vs Kustomize: When to Use Each

Both tools solve the problem of managing Kubernetes manifests, but they take
fundamentally different approaches:

**Helm** uses **templates with values**:
- Manifests are Go templates with placeholders
- Values are injected at render time
- Output is generated from scratch each time

**Kustomize** uses **overlays on base manifests**:
- Manifests are plain YAML (no template syntax)
- Patches and overlays modify the base
- Output is the base plus applied patches

| Aspect | Helm | Kustomize |
|---|---|---|
| Approach | Templating | Patching |
| Learning curve | Moderate (Go templates) | Low (plain YAML) |
| Packaging | Charts (distributable) | Directories (not packaged) |
| Versioning | Built-in (Chart.yaml) | External (git tags) |
| Lifecycle management | Install/upgrade/rollback/uninstall | Apply only |
| Community ecosystem | Thousands of charts on Artifact Hub | Fewer shared bases |
| Built into kubectl | No | Yes (`kubectl apply -k`) |
| Conditionals/loops | Yes (if/range) | No |

**When to use Helm:**
- Deploying third-party software (databases, monitoring, ingress controllers)
- Distributing your application as a package for others to install
- When you need lifecycle management (rollback, release tracking)
- Complex applications with conditional resources

**When to use Kustomize:**
- Internal applications where you control all environments
- Simple environment differences (replica count, image tags)
- When you want to avoid template syntax in your manifests
- When GitOps tools like ArgoCD or Flux manage deployment

**Using both together** is common: use Helm to install third-party charts and
Kustomize to manage your own application manifests.

### The Philosophy of Reproducible Deployments

Helm enables reproducible deployments through several mechanisms:

1. **Chart versioning** - Every chart has a semantic version. Version `2.3.1`
   always contains the same templates.

2. **Values files** - Environment-specific configuration is separated from the
   chart, stored in version control, and applied at deploy time.

3. **Release history** - Helm records every release revision, including the
   values used, making it possible to reproduce any previous deployment.

4. **Atomic operations** - The `--atomic` flag ensures that failed deployments
   roll back automatically, preventing half-applied changes.

```bash
# Reproducible deployment across environments
helm upgrade --install my-app ./my-chart \
  -f values-production.yaml \
  --version 2.3.1 \
  --atomic \
  --timeout 5m
```

This single command is idempotent: it installs if the release does not exist and
upgrades if it does. It uses a specific chart version, applies production values,
and rolls back on failure. It can be run in CI/CD, by a developer, or by an
operator, and the result is the same.

---

## Step-by-Step Practical

### Exploring the Helm Ecosystem

```bash
# Install Helm (Linux/macOS)
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version
# version.BuildInfo{Version:"v3.14.0", GitCommit:"...", ...}

# Add the Bitnami repository
helm repo add bitnami https://charts.bitnami.com/bitnami
# "bitnami" has been added to your repositories

# Update repository index
helm repo update
# Hang tight while we grab the latest from your chart repositories...
# ...Successfully got an update from the "bitnami" chart repository

# Search for charts
helm search repo nginx
# NAME                  CHART VERSION   APP VERSION   DESCRIPTION
# bitnami/nginx         15.1.0          1.25.4        NGINX is an open source HTTP web server...
# bitnami/nginx-ingress 10.1.0          3.4.0         NGINX Ingress Controller...

# Search Artifact Hub from the CLI
helm search hub prometheus
# URL                                               CHART VERSION   APP VERSION   DESCRIPTION
# https://artifacthub.io/packages/helm/prometheus... 25.8.0         2.49.1        ...
```

### Understanding Chart Contents

```bash
# Inspect a chart without installing it
helm show chart bitnami/nginx
# apiVersion: v2
# appVersion: 1.25.4
# name: nginx
# version: 15.1.0
# ...

# View all configurable values
helm show values bitnami/nginx | head -50
# Shows the full values.yaml with all default settings

# Download and extract a chart locally
helm pull bitnami/nginx --untar
ls nginx/
# Chart.lock  Chart.yaml  README.md  charts/  templates/  values.yaml
```

### Examining a Chart's Structure

```bash
# Look at the template files
ls nginx/templates/
# NOTES.txt
# _helpers.tpl
# deployment.yaml
# health-ingress.yaml
# hpa.yaml
# ingress.yaml
# pdb.yaml
# server-block-configmap.yaml
# service.yaml
# serviceaccount.yaml
# tls-secret.yaml

# Preview what Helm would generate without installing
helm template my-nginx bitnami/nginx --set replicaCount=3
# Outputs all rendered Kubernetes manifests to stdout
```

---

## Exercises

### Exercise 1: Chart Repository Exploration
Add three different Helm repositories (Bitnami, Prometheus Community, and
Jetstack). List all repositories and search for a PostgreSQL chart. Write down
the chart name, version, and app version.

### Exercise 2: Chart Inspection
Use `helm show values` to inspect the Bitnami Redis chart. Identify the values
that control: replica count, persistence (storage size), authentication
(password), and resource limits. Document each value path.

### Exercise 3: Template Preview
Use `helm template` to render the Bitnami Nginx chart with custom values:
3 replicas, 512Mi memory limit, and a custom server block that returns
"Hello from Helm". Save the rendered output and identify each Kubernetes
resource that would be created.

### Exercise 4: Kustomize Comparison
Create a simple Nginx Deployment and Service as plain YAML files. Then create
a Kustomize overlay that changes the replica count for production. Compare this
workflow with the Helm approach. Write a short analysis of which you would
prefer for this use case and why.

### Exercise 5: OCI Chart Registry
Push a chart to an OCI-compatible registry (you can use a local registry with
`docker run -d -p 5000:5000 registry:2`). Pull it back and verify the contents
match. Document the commands you used.

---

## Knowledge Check

### Question 1
Why was Tiller removed in Helm 3, and how does Helm 3 authenticate with the
Kubernetes API?

**Answer:** Tiller was removed because it ran with cluster-admin privileges inside
the cluster, creating a significant security risk. Any user who could communicate
with Tiller effectively had cluster-admin access. Helm 3 authenticates directly
with the Kubernetes API using the credentials in the user's kubeconfig file,
inheriting the same RBAC permissions the user already has.

### Question 2
What is the difference between `helm install` and `helm template`?

**Answer:** `helm install` renders the templates, sends the resulting manifests to
the Kubernetes API server, creates resources in the cluster, and records a release
in the cluster (as a Secret in the release namespace). `helm template` only renders
the templates locally and prints the resulting YAML to stdout without contacting
the cluster. It is used for previewing, debugging, and piping output to other tools.

### Question 3
When would you choose Kustomize over Helm for managing an internal application?

**Answer:** Kustomize is preferable when the application is internal (not distributed
to external users), the environment differences are simple (image tags, replica
counts, resource limits), you want to avoid learning Go template syntax, and you
are already using GitOps tools that support Kustomize natively. Kustomize keeps
manifests as valid YAML that can be applied directly with `kubectl`, making them
easier to read and review without rendering.

### Question 4
Explain what a three-way merge means in the context of Helm 3 upgrades.

**Answer:** In Helm 2, upgrades compared only the old chart manifest with the new
chart manifest (two-way merge). If someone manually edited a resource with
`kubectl edit`, those changes would be silently overwritten. Helm 3 performs a
three-way merge that compares the old chart manifest, the new chart manifest, and
the live state of the resource in the cluster. This means manual changes are
preserved unless the new chart explicitly changes the same fields. This prevents
accidental data loss during upgrades.

### Question 5
What are the advantages of storing Helm charts in OCI registries versus
traditional chart repositories?

**Answer:** OCI-based storage eliminates the need for a separate chart repository
server (and its index.yaml). Charts are stored alongside container images in
the same registry infrastructure, simplifying operations. OCI registries provide
built-in authentication, authorization, replication, and scanning that would need
to be implemented separately for a traditional chart repository. Additionally,
OCI distribution is a standard, so any OCI-compliant registry works without
vendor-specific tooling.
