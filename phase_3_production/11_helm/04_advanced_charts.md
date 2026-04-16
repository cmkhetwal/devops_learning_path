# Advanced Helm Charts: Dependencies, Hooks, and Production Patterns

## Why This Matters in DevOps

Real-world applications are not standalone. A web application depends on a database,
a cache, and a message queue. A monitoring stack depends on a time-series database,
a visualization tool, and alert routing. Helm's dependency system lets you declare
these relationships and deploy the entire stack as a single operation.

Beyond dependencies, production charts need lifecycle hooks (run migrations before
upgrading, clean up after uninstalling), schema validation (catch configuration
errors before deployment), and testing (verify the deployed release works). These
features distinguish a proof-of-concept chart from a production-grade chart.

This lesson covers the advanced features that make charts robust enough for
production environments where failures cost money and downtime costs trust.

---

## Core Concepts

### Chart Dependencies

Dependencies are declared in `Chart.yaml`:

```yaml
# Chart.yaml
apiVersion: v2
name: my-fullstack-app
version: 1.0.0
appVersion: "2.5.0"
dependencies:
  - name: postgresql
    version: "14.x.x"              # SemVer constraint
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled   # Toggle dependency on/off
    alias: db                       # Reference as .Values.db instead of .Values.postgresql
  - name: redis
    version: "18.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
  - name: common
    version: "2.x.x"
    repository: https://charts.bitnami.com/bitnami
    tags:
      - infrastructure              # Group dependencies by tag
```

After declaring dependencies, run:

```bash
# Download dependencies into charts/ directory
helm dependency update ./my-fullstack-app
# Saving 3 charts
# Downloading postgresql from repo https://charts.bitnami.com/bitnami
# Downloading redis from repo https://charts.bitnami.com/bitnami
# Downloading common from repo https://charts.bitnami.com/bitnami
# Deleting outdated charts

# Verify
ls ./my-fullstack-app/charts/
# common-2.16.1.tgz  postgresql-14.0.5.tgz  redis-18.6.1.tgz

# Chart.lock is created (pinned versions)
cat ./my-fullstack-app/Chart.lock
# dependencies:
# - name: postgresql
#   repository: https://charts.bitnami.com/bitnami
#   version: 14.0.5
# ...
# digest: sha256:abc123...
# generated: "2024-03-14T10:00:00Z"
```

### Configuring Subchart Values

Pass values to subcharts using the subchart name (or alias) as a key:

```yaml
# values.yaml for the parent chart
postgresql:
  enabled: true
  auth:
    username: appuser
    password: changeme
    database: myappdb
  primary:
    persistence:
      size: 20Gi
    resources:
      limits:
        cpu: 500m
        memory: 512Mi

redis:
  enabled: true
  architecture: standalone
  auth:
    enabled: true
    password: redis-secret
  master:
    resources:
      limits:
        cpu: 200m
        memory: 256Mi

# If using alias "db" for postgresql:
db:
  enabled: true
  auth:
    username: appuser
```

### Global Values

Global values are accessible from any chart and subchart:

```yaml
# values.yaml
global:
  imageRegistry: registry.example.com
  imagePullSecrets:
    - name: registry-credentials
  storageClass: fast-ssd
  environment: production
```

In any template (parent or subchart):

```yaml
image: {{ .Values.global.imageRegistry }}/{{ .Values.image.repository }}
```

### Helm Hooks

Hooks are templates with special annotations that run at specific points in the
release lifecycle:

```yaml
# templates/pre-upgrade-migration.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "myapp.fullname" . }}-migration
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": pre-upgrade,pre-install
    "helm.sh/hook-weight": "1"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  backoffLimit: 3
  template:
    spec:
      restartPolicy: Never
      containers:
        - name: migration
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          command: ["python", "manage.py", "migrate", "--noinput"]
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: {{ include "myapp.fullname" . }}-db-credentials
                  key: url
```

Available hook types:

| Hook | When It Runs |
|---|---|
| `pre-install` | After templates render, before resources are created |
| `post-install` | After all resources are loaded into Kubernetes |
| `pre-delete` | Before any resources are deleted |
| `post-delete` | After all resources are deleted |
| `pre-upgrade` | After templates render, before resources are updated |
| `post-upgrade` | After all resources are updated |
| `pre-rollback` | Before rollback |
| `post-rollback` | After rollback |
| `test` | When `helm test` is invoked |

Hook delete policies:

| Policy | Behavior |
|---|---|
| `before-hook-creation` | Delete previous hook resource before creating new one |
| `hook-succeeded` | Delete the hook resource after it succeeds |
| `hook-failed` | Delete the hook resource if it fails |

Hook weights control execution order (lower weight runs first):

```yaml
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-weight": "-5"   # Runs before weight "0"
```

### Helm Tests

Tests are hooks with `"helm.sh/hook": test`. They verify a release is working:

```yaml
# templates/tests/test-connection.yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ include "myapp.fullname" . }}-test-connection
  labels:
    {{- include "myapp.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: wget
      image: busybox:1.36
      command: ['wget']
      args: ['{{ include "myapp.fullname" . }}:{{ .Values.service.port }}/health']
```

```bash
# Run tests
helm test my-release
# NAME: my-release
# LAST DEPLOYED: Thu Mar 14 10:30:00 2024
# NAMESPACE: default
# STATUS: deployed
# REVISION: 1
# TEST SUITE:     my-release-myapp-test-connection
# Last Started:   Thu Mar 14 10:35:00 2024
# Last Completed: Thu Mar 14 10:35:05 2024
# Phase:          Succeeded
```

### JSON Schema Validation

A `values.schema.json` file validates values before rendering templates:

```json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["image", "replicaCount"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1,
      "maximum": 50,
      "description": "Number of pod replicas"
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": {
          "type": "string",
          "pattern": "^[a-z0-9][a-z0-9._/-]*$",
          "description": "Container image repository"
        },
        "tag": {
          "type": "string",
          "description": "Container image tag"
        },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      }
    },
    "service": {
      "type": "object",
      "properties": {
        "type": {
          "type": "string",
          "enum": ["ClusterIP", "NodePort", "LoadBalancer"]
        },
        "port": {
          "type": "integer",
          "minimum": 1,
          "maximum": 65535
        }
      }
    },
    "resources": {
      "type": "object",
      "properties": {
        "limits": {
          "type": "object",
          "properties": {
            "cpu": { "type": "string" },
            "memory": { "type": "string" }
          }
        }
      }
    }
  }
}
```

```bash
# Schema validation happens automatically during install/upgrade/template
helm install my-app ./my-chart --set replicaCount=0
# Error: values don't meet the specifications of the schema(s):
# - replicaCount: Must be greater than or equal to 1

helm install my-app ./my-chart --set service.type=External
# Error: values don't meet the specifications of the schema(s):
# - service.type: Must be one of: ClusterIP, NodePort, LoadBalancer
```

### Library Charts

Library charts provide reusable template definitions but do not render any
resources themselves:

```yaml
# Chart.yaml
apiVersion: v2
name: my-library
version: 1.0.0
type: library  # Cannot be installed directly
```

Other charts depend on the library and use its templates:

```yaml
# In the consuming chart's Chart.yaml
dependencies:
  - name: my-library
    version: "1.x.x"
    repository: "https://charts.example.com"

# In the consuming chart's templates
{{- include "my-library.deployment" . }}
```

### OCI-Based Chart Storage

```bash
# Log in to an OCI registry
helm registry login ghcr.io -u myuser

# Package and push a chart
helm package ./my-chart
# Successfully packaged chart and saved it to: my-chart-1.0.0.tgz

helm push my-chart-1.0.0.tgz oci://ghcr.io/myorg/charts
# Pushed: ghcr.io/myorg/charts/my-chart:1.0.0
# Digest: sha256:abc123...

# Install from OCI
helm install my-release oci://ghcr.io/myorg/charts/my-chart --version 1.0.0

# Pull from OCI
helm pull oci://ghcr.io/myorg/charts/my-chart --version 1.0.0

# Show chart info from OCI
helm show chart oci://ghcr.io/myorg/charts/my-chart --version 1.0.0
```

### Signing Charts

Chart provenance files (`.prov`) verify chart integrity:

```bash
# Generate a GPG key (if you do not have one)
gpg --quick-generate-key "Helm Signer <helm@example.com>"

# Package and sign
helm package --sign --key "Helm Signer" --keyring ~/.gnupg/pubring.gpg ./my-chart
# Successfully packaged chart and saved it to: my-chart-1.0.0.tgz
# Successfully signed my-chart-1.0.0.tgz

# Verify a signed chart
helm verify my-chart-1.0.0.tgz
# Signed by: Helm Signer <helm@example.com>
# Using Key With Fingerprint: ABC123...
# Chart Hash Verified: sha256:def456...

# Install with verification
helm install my-release my-chart-1.0.0.tgz --verify --keyring ~/.gnupg/pubring.gpg
```

---

## Step-by-Step Practical

### Create a Production-Grade Chart with Dependencies

```bash
# Create the parent chart
helm create fullstack-app
cd fullstack-app
```

Update `Chart.yaml` with dependencies:

```yaml
# Chart.yaml
apiVersion: v2
name: fullstack-app
description: A full-stack web application with PostgreSQL and Redis
version: 1.0.0
appVersion: "2.0.0"
type: application
dependencies:
  - name: postgresql
    version: "14.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: "18.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

Create the database migration hook:

```yaml
# templates/hooks/migration-job.yaml
{{- if .Values.migration.enabled }}
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ include "fullstack-app.fullname" . }}-migrate
  labels:
    {{- include "fullstack-app.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "0"
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  backoffLimit: {{ .Values.migration.backoffLimit | default 3 }}
  activeDeadlineSeconds: {{ .Values.migration.timeout | default 300 }}
  template:
    metadata:
      labels:
        {{- include "fullstack-app.selectorLabels" . | nindent 8 }}
        app.kubernetes.io/component: migration
    spec:
      restartPolicy: Never
      containers:
        - name: migrate
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          command:
            {{- toYaml .Values.migration.command | nindent 12 }}
          env:
            - name: DATABASE_HOST
              value: {{ include "fullstack-app.fullname" . }}-postgresql
            - name: DATABASE_NAME
              value: {{ .Values.postgresql.auth.database | default "app" }}
            - name: DATABASE_USER
              value: {{ .Values.postgresql.auth.username | default "app" }}
            - name: DATABASE_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {{ include "fullstack-app.fullname" . }}-postgresql
                  key: password
          resources:
            {{- toYaml .Values.migration.resources | nindent 12 }}
{{- end }}
```

Create a comprehensive test:

```yaml
# templates/tests/test-app-health.yaml
apiVersion: v1
kind: Pod
metadata:
  name: {{ include "fullstack-app.fullname" . }}-test-health
  labels:
    {{- include "fullstack-app.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": test
    "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
spec:
  restartPolicy: Never
  containers:
    - name: test-api
      image: curlimages/curl:8.5.0
      command: ["/bin/sh", "-c"]
      args:
        - |
          echo "Testing API health endpoint..."
          response=$(curl -s -o /dev/null -w "%{http_code}" \
            http://{{ include "fullstack-app.fullname" . }}:{{ .Values.service.port }}/health)
          if [ "$response" = "200" ]; then
            echo "PASS: Health endpoint returned 200"
          else
            echo "FAIL: Health endpoint returned $response"
            exit 1
          fi

          echo "Testing API readiness endpoint..."
          response=$(curl -s -o /dev/null -w "%{http_code}" \
            http://{{ include "fullstack-app.fullname" . }}:{{ .Values.service.port }}/ready)
          if [ "$response" = "200" ]; then
            echo "PASS: Readiness endpoint returned 200"
          else
            echo "FAIL: Readiness endpoint returned $response"
            exit 1
          fi

          echo "All tests passed."
```

Add schema validation:

```json
// values.schema.json
{
  "$schema": "https://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["image", "replicaCount", "service"],
  "properties": {
    "replicaCount": {
      "type": "integer",
      "minimum": 1
    },
    "image": {
      "type": "object",
      "required": ["repository"],
      "properties": {
        "repository": {
          "type": "string",
          "minLength": 1
        },
        "tag": { "type": "string" },
        "pullPolicy": {
          "type": "string",
          "enum": ["Always", "IfNotPresent", "Never"]
        }
      }
    },
    "migration": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean" },
        "backoffLimit": {
          "type": "integer",
          "minimum": 0,
          "maximum": 10
        }
      }
    }
  }
}
```

Build and validate:

```bash
# Download dependencies
helm dependency update .
# Saving 2 charts
# Downloading postgresql ...
# Downloading redis ...

# Lint the chart
helm lint .
# ==> Linting .
# 1 chart(s) linted, 0 chart(s) failed

# Render templates to verify
helm template fullstack ./  \
  --set postgresql.enabled=true \
  --set redis.enabled=true \
  --set migration.enabled=true

# Package
helm package .
# Successfully packaged chart and saved it to: fullstack-app-1.0.0.tgz
```

---

## Exercises

### Exercise 1: Dependency Management
Create a chart for a WordPress-like application that depends on both MariaDB and
Memcached from the Bitnami repository. Configure the parent chart's values to
set the database name, user, and storage size. Use `condition` to make Memcached
optional. Test with `helm dependency update` and `helm template`.

### Exercise 2: Lifecycle Hooks
Add three hooks to a chart: a pre-install hook that creates an initial admin user,
a pre-upgrade hook that runs database migrations, and a post-delete hook that
archives logs to S3. Use hook weights to control execution order and appropriate
delete policies.

### Exercise 3: Schema Validation
Write a comprehensive `values.schema.json` for a chart that validates: image
repository is a non-empty string, replica count is between 1 and 100, service
port is a valid port number, resource limits use the Kubernetes resource format,
and ingress hosts are valid domain names. Test with both valid and invalid values.

### Exercise 4: Library Chart
Create a library chart that provides standardized templates for Deployment,
Service, and Ingress. Create two application charts that depend on this library
chart and use its templates. Verify that changes to the library affect both
applications.

### Exercise 5: Chart Signing Workflow
Generate a GPG key pair, sign a chart, and verify it. Then tamper with the
chart archive (add an extra file) and attempt verification again. Document what
happens and why chart signing matters in a production supply chain.

---

## Knowledge Check

### Question 1
What is the difference between `Chart.lock` and `Chart.yaml` dependencies?

**Answer:** `Chart.yaml` declares dependency constraints using SemVer ranges
(e.g., `version: "14.x.x"`), which allow any matching version. `Chart.lock`
records the exact versions that were resolved when `helm dependency update`
was run (e.g., `version: 14.0.5`). This is analogous to `package.json` vs
`package-lock.json` in Node.js. Running `helm dependency build` uses the
locked versions for reproducibility, while `helm dependency update` resolves
fresh versions and updates the lock file.

### Question 2
Why should hook Jobs have `"helm.sh/hook-delete-policy": before-hook-creation`?

**Answer:** Without this policy, the hook resource (e.g., a Job) persists after
completion. On the next upgrade, Helm tries to create the same Job again and
fails because it already exists. The `before-hook-creation` policy deletes the
previous hook resource before creating the new one, ensuring upgrades work
cleanly. Combining it with `hook-succeeded` provides the best behavior: delete
the old one before creating a new one, and delete the new one after it succeeds.

### Question 3
How do global values differ from subchart values, and when should you use each?

**Answer:** Subchart values are namespaced under the subchart name (e.g.,
`.Values.postgresql.auth.password`) and only accessible within that subchart.
Global values (`.Values.global.*`) are accessible from every chart and subchart
without namespacing. Use global values for shared configuration like image
registries, pull secrets, storage classes, and environment labels that every
component needs. Use subchart values for subchart-specific configuration like
database names, replica counts, and resource limits.

### Question 4
What happens if a pre-upgrade hook fails?

**Answer:** If a pre-upgrade hook fails, Helm aborts the upgrade and the release
remains at its current revision. The existing resources in the cluster are not
modified. The release status is set to `failed` for that attempted revision. If
`--atomic` was used, Helm rolls back to the last successful revision. The failed
hook resource (Pod or Job) remains in the cluster for debugging unless a delete
policy removes it. This is by design: hooks like database migrations should block
deployment if they fail.

### Question 5
What is the purpose of a library chart, and why can it not be installed directly?

**Answer:** A library chart (type: library in Chart.yaml) provides reusable
named templates that other charts can include. It cannot be installed directly
because it does not contain any resource templates of its own, only `define`
blocks in `_helpers.tpl` or similar files. This is useful for organizations that
want to standardize labels, annotations, security contexts, or entire resource
patterns across many charts. The library chart is declared as a dependency and
its templates are available via `include` in the consuming chart.
