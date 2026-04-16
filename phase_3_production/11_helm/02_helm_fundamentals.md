# Helm Fundamentals: Installing, Managing, and Operating Charts

## Why This Matters in DevOps

A DevOps engineer spends a significant portion of their time deploying and managing
software on Kubernetes clusters. Without Helm, every deployment is a manual
orchestration of `kubectl apply` commands across dozens of YAML files with no
built-in rollback, no release tracking, and no configuration management.

Helm fundamentals are the bread and butter of Kubernetes operations. Knowing how
to search for charts, inspect their values, install with overrides, upgrade safely,
and roll back when things go wrong is essential for daily work. These operations
form the operational backbone of most production Kubernetes platforms.

This lesson covers the commands and workflows you will use every single day.

---

## Core Concepts

### Release Management

A **release** is a running instance of a chart with a specific configuration.
When you run `helm install my-app bitnami/nginx`, Helm creates a release named
`my-app`. Each release has:

- **Name** - A unique identifier within the namespace
- **Namespace** - The Kubernetes namespace where resources are created
- **Revision** - An incrementing number (1 for install, 2 for first upgrade, etc.)
- **Status** - deployed, failed, superseded, uninstalled, pending-install, etc.
- **Chart** - The chart name and version used
- **Values** - The configuration values applied

Helm stores release metadata as Kubernetes Secrets (by default) in the release
namespace. This means release history survives Helm CLI crashes and is accessible
from any machine with cluster access.

```bash
# Release Secrets follow this naming convention
# sh.helm.release.v1.<release-name>.v<revision>
kubectl get secrets -l owner=helm
# NAME                                TYPE                 DATA   AGE
# sh.helm.release.v1.my-app.v1       helm.sh/release.v1   1      5m
# sh.helm.release.v1.my-app.v2       helm.sh/release.v1   1      2m
```

### Values Hierarchy

Helm merges values from multiple sources. Later sources override earlier ones:

1. **chart/values.yaml** - Default values bundled with the chart
2. **Parent chart values** - Values from a parent chart (for subcharts)
3. **-f / --values** flags - Values files specified on the command line
4. **--set** flags - Individual values specified on the command line

```bash
# These are equivalent, from least to most specific
helm install my-app ./my-chart                           # Only defaults
helm install my-app ./my-chart -f staging.yaml           # Defaults + staging
helm install my-app ./my-chart -f staging.yaml --set replicas=5  # Override one value
```

Multiple `-f` flags are processed left to right, with later files winning:

```bash
# base.yaml sets replicas=2, production.yaml sets replicas=6
# Result: replicas=6
helm install my-app ./my-chart -f base.yaml -f production.yaml
```

### The --set Syntax

The `--set` flag uses a dot-separated path to target nested values:

```bash
# Simple value
--set replicaCount=3

# Nested value
--set resources.limits.memory=512Mi

# String value (force string type)
--set-string image.tag=v1.2.3

# Array value
--set ingress.hosts[0].host=example.com

# Multiple values
--set replicaCount=3,image.tag=v2.0.0

# Complex nested
--set "nodeSelector.kubernetes\.io/os=linux"
```

Use `--set` for quick overrides in development. Use `-f values.yaml` for
production deployments because values files are version-controlled and auditable.

---

## Step-by-Step Practical

### Installing Helm

```bash
# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# macOS
brew install helm

# Windows (chocolatey)
choco install kubernetes-helm

# Verify
helm version
# version.BuildInfo{Version:"v3.14.0", ...}
```

### Repository Operations

```bash
# Add repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

# List repositories
helm repo list
# NAME                  URL
# bitnami               https://charts.bitnami.com/bitnami
# prometheus-community  https://prometheus-community.github.io/helm-charts
# grafana               https://grafana.github.io/helm-charts
# ingress-nginx         https://kubernetes.github.io/ingress-nginx

# Update all repository indexes
helm repo update
# Hang tight while we grab the latest from your chart repositories...
# ...Successfully got an update from the "bitnami" chart repository
# ...Successfully got an update from the "prometheus-community" chart repository

# Search for charts
helm search repo postgres
# NAME                    CHART VERSION   APP VERSION   DESCRIPTION
# bitnami/postgresql      14.0.0          16.2.0        PostgreSQL is an object-relational database...
# bitnami/postgresql-ha   13.0.0          16.2.0        PostgreSQL HA with Pgpool, Repmgr...

# Search with version constraints
helm search repo nginx --version ">=14.0.0"

# Remove a repository
helm repo remove grafana
```

### Inspecting Charts Before Installation

```bash
# View chart metadata
helm show chart bitnami/nginx
# apiVersion: v2
# appVersion: 1.25.4
# description: NGINX Open Source is a web server...
# name: nginx
# version: 15.1.0

# View all configurable values (this is critical before installing)
helm show values bitnami/nginx
# Output is the full values.yaml - often hundreds of lines

# View the README
helm show readme bitnami/nginx

# View everything
helm show all bitnami/nginx
```

### Installing Charts

```bash
# Basic installation
helm install my-nginx bitnami/nginx
# NAME: my-nginx
# LAST DEPLOYED: Thu Mar 14 10:30:00 2024
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES:
#   ...installation notes from the chart...

# Install in a specific namespace (create if not exists)
helm install my-nginx bitnami/nginx -n web --create-namespace

# Install with a specific chart version
helm install my-nginx bitnami/nginx --version 15.0.0

# Install with custom values file
helm install my-nginx bitnami/nginx -f my-values.yaml

# Install with --set overrides
helm install my-nginx bitnami/nginx \
  --set replicaCount=3 \
  --set resources.limits.memory=256Mi \
  --set service.type=ClusterIP

# Generate a release name automatically
helm install bitnami/nginx --generate-name
# NAME: nginx-1710412200

# Dry run (render and validate without installing)
helm install my-nginx bitnami/nginx --dry-run
# Shows all rendered manifests without applying them

# Wait for all resources to be ready
helm install my-nginx bitnami/nginx --wait --timeout 5m

# Atomic: roll back on failure
helm install my-nginx bitnami/nginx --atomic --timeout 5m
```

### Querying Releases

```bash
# List releases in current namespace
helm list
# NAME       NAMESPACE   REVISION   UPDATED                   STATUS     CHART          APP VERSION
# my-nginx   default     1          2024-03-14 10:30:00 ...   deployed   nginx-15.1.0   1.25.4

# List releases in all namespaces
helm list -A

# List releases with a specific status
helm list --failed
helm list --pending
helm list --uninstalled  # Only if --keep-history was used

# Get detailed status of a release
helm status my-nginx
# NAME: my-nginx
# LAST DEPLOYED: Thu Mar 14 10:30:00 2024
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# NOTES: ...

# View release history
helm history my-nginx
# REVISION   UPDATED                    STATUS       CHART          APP VERSION   DESCRIPTION
# 1          Thu Mar 14 10:30:00 2024   deployed     nginx-15.1.0   1.25.4        Install complete

# Get the values used for a release
helm get values my-nginx
# USER-SUPPLIED VALUES:
# replicaCount: 3

# Get all values (including defaults)
helm get values my-nginx --all

# Get the rendered manifests
helm get manifest my-nginx

# Get everything (hooks, manifests, notes, values)
helm get all my-nginx
```

### Upgrading Releases

```bash
# Upgrade with new values
helm upgrade my-nginx bitnami/nginx --set replicaCount=5
# Release "my-nginx" has been upgraded. Happy Helming!

# Upgrade with a values file
helm upgrade my-nginx bitnami/nginx -f production-values.yaml

# Upgrade to a new chart version
helm upgrade my-nginx bitnami/nginx --version 15.2.0

# Reuse existing values and override specific ones
helm upgrade my-nginx bitnami/nginx --reuse-values --set image.tag=1.25.5

# Install or upgrade (idempotent - safe for CI/CD)
helm upgrade --install my-nginx bitnami/nginx -f values.yaml

# Atomic upgrade (auto-rollback on failure)
helm upgrade my-nginx bitnami/nginx -f values.yaml --atomic --timeout 5m

# Check history after upgrade
helm history my-nginx
# REVISION   UPDATED                    STATUS       CHART          APP VERSION   DESCRIPTION
# 1          Thu Mar 14 10:30:00 2024   superseded   nginx-15.1.0   1.25.4        Install complete
# 2          Thu Mar 14 11:00:00 2024   deployed     nginx-15.2.0   1.25.5        Upgrade complete
```

### Rolling Back

```bash
# Rollback to previous revision
helm rollback my-nginx
# Rollback was a success! Happy Helming!

# Rollback to a specific revision
helm rollback my-nginx 1

# Check history after rollback
helm history my-nginx
# REVISION   UPDATED                    STATUS       CHART          APP VERSION   DESCRIPTION
# 1          Thu Mar 14 10:30:00 2024   superseded   nginx-15.1.0   1.25.4        Install complete
# 2          Thu Mar 14 11:00:00 2024   superseded   nginx-15.2.0   1.25.5        Upgrade complete
# 3          Thu Mar 14 11:15:00 2024   deployed     nginx-15.1.0   1.25.4        Rollback to 1
```

### Uninstalling Releases

```bash
# Uninstall a release (deletes all resources)
helm uninstall my-nginx
# release "my-nginx" uninstalled

# Keep history (allows re-examination later)
helm uninstall my-nginx --keep-history
helm list --uninstalled  # Still visible

# Uninstall with a dry run
helm uninstall my-nginx --dry-run
```

### Practical: Deploy Nginx, Prometheus, and Grafana

```bash
# 1. Deploy Nginx as a web server
cat > nginx-values.yaml <<'EOF'
replicaCount: 2
service:
  type: ClusterIP
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
serverBlock: |-
  server {
    listen 8080;
    location / {
      return 200 'Hello from Helm-managed Nginx\n';
      add_header Content-Type text/plain;
    }
    location /health {
      return 200 'ok\n';
      add_header Content-Type text/plain;
    }
  }
EOF

helm install web-server bitnami/nginx \
  -f nginx-values.yaml \
  -n web --create-namespace \
  --wait --timeout 3m

# 2. Deploy Prometheus for monitoring
cat > prometheus-values.yaml <<'EOF'
prometheus:
  prometheusSpec:
    retention: 7d
    resources:
      limits:
        cpu: 500m
        memory: 1Gi
      requests:
        cpu: 250m
        memory: 512Mi
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 20Gi
alertmanager:
  enabled: true
  alertmanagerSpec:
    resources:
      limits:
        cpu: 100m
        memory: 128Mi
grafana:
  enabled: false  # We will install Grafana separately
EOF

helm install monitoring prometheus-community/kube-prometheus-stack \
  -f prometheus-values.yaml \
  -n monitoring --create-namespace \
  --wait --timeout 5m

# 3. Deploy Grafana with a custom datasource
cat > grafana-values.yaml <<'EOF'
replicas: 1
persistence:
  enabled: true
  size: 5Gi
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
      - name: Prometheus
        type: prometheus
        url: http://monitoring-kube-prometheus-prometheus.monitoring:9090
        access: proxy
        isDefault: true
dashboardProviders:
  dashboardproviders.yaml:
    apiVersion: 1
    providers:
      - name: default
        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/default
resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi
EOF

helm install grafana grafana/grafana \
  -f grafana-values.yaml \
  -n monitoring \
  --wait --timeout 3m

# 4. Verify all releases
helm list -A
# NAME         NAMESPACE    REVISION   STATUS     CHART                           APP VERSION
# web-server   web          1          deployed   nginx-15.1.0                    1.25.4
# monitoring   monitoring   1          deployed   kube-prometheus-stack-56.0.0    0.71.0
# grafana      monitoring   1          deployed   grafana-7.3.0                   10.3.1

# 5. Get Grafana admin password
kubectl get secret -n monitoring grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d
```

---

## Exercises

### Exercise 1: Full Lifecycle
Install the Bitnami Redis chart with 3 replicas and authentication enabled.
Upgrade it to change the password. Roll back to the original password. Uninstall
it. Document the `helm history` output at each step.

### Exercise 2: Values Investigation
Use `helm show values` to find how to configure the Bitnami PostgreSQL chart for:
a persistent volume of 50Gi, a custom database named `myapp`, a custom user named
`appuser`, and resource limits of 1Gi memory. Write the values file and install.

### Exercise 3: Dry Run Debugging
Install the Bitnami WordPress chart with `--dry-run` and redirect the output to
a file. Search the output for all `kind:` lines to list every Kubernetes resource
that would be created. Count the total number of resources.

### Exercise 4: Multi-Environment Deployment
Create three values files (dev.yaml, staging.yaml, production.yaml) for the
Bitnami Nginx chart. Dev should use 1 replica with 128Mi memory, staging should
use 2 replicas with 256Mi memory, and production should use 4 replicas with 512Mi
memory and a PodDisruptionBudget. Deploy all three to separate namespaces.

### Exercise 5: Release Forensics
After installing a chart, use `helm get manifest`, `helm get values`, and
`helm get hooks` to understand exactly what Helm deployed. Compare the manifest
output with `kubectl get all` in the release namespace. Explain any differences.

---

## Knowledge Check

### Question 1
What is the difference between `helm install` and `helm upgrade --install`?

**Answer:** `helm install` creates a new release and fails if a release with the
same name already exists. `helm upgrade --install` is idempotent: it installs
the release if it does not exist and upgrades it if it does. The `--install`
flag makes `helm upgrade` safe to run in CI/CD pipelines where you do not know
whether the release exists yet.

### Question 2
What does the `--atomic` flag do, and why should you use it in production?

**Answer:** The `--atomic` flag tells Helm to automatically roll back the release
to its previous state if the upgrade fails (resources do not become ready within
the timeout period). In production, this prevents deployments from leaving the
cluster in a partially updated, broken state. Without `--atomic`, a failed
upgrade leaves the new (broken) resources in place, and the release is marked
as `failed`. With `--atomic`, the release is rolled back and continues running
the previous working version.

### Question 3
Why is `--reuse-values` sometimes dangerous during upgrades?

**Answer:** `--reuse-values` takes the values from the previous release and
merges the new `--set` or `-f` values on top. This is dangerous when upgrading
to a new chart version because new default values introduced in the chart will
not be applied. If the new chart version adds a required configuration value
with a meaningful default, `--reuse-values` will not include it, potentially
causing unexpected behavior. The safer approach is to maintain a complete values
file and pass it with `-f` on every upgrade.

### Question 4
How does Helm store release metadata, and why does this design matter?

**Answer:** Helm stores release metadata as Kubernetes Secrets (type
`helm.sh/release.v1`) in the namespace where the release is installed. Each
revision gets its own Secret. This design matters because it means release
history is stored in the cluster itself, not on the operator's local machine.
Any team member with access to the namespace can view release history, roll back,
or upgrade without needing state files or a shared database. It also means that
if the Helm CLI crashes mid-operation, the release state is preserved.

### Question 5
Explain the values merge order when running:
`helm upgrade my-app ./chart -f base.yaml -f prod.yaml --set replicas=10`

**Answer:** Values are merged in this order, with later values overriding earlier
ones: (1) the chart's default values.yaml, (2) the base.yaml file, (3) the
prod.yaml file, (4) the `--set replicas=10` override. If the chart default has
`replicas: 1`, base.yaml has `replicas: 2`, and prod.yaml has `replicas: 6`,
the final value will be `replicas: 10` because `--set` always wins. Within
files, later `-f` flags override earlier ones for the same keys.
