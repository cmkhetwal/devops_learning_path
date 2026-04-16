# Creating Helm Charts: From Scaffold to Production

## Why This Matters in DevOps

Installing community charts covers third-party software, but your own applications
need their own charts. Creating Helm charts is how you package your microservices,
APIs, and internal tools for consistent, repeatable deployment across environments.

A well-crafted chart is the contract between development and operations. Developers
define what their application needs (ports, environment variables, health checks),
and the chart translates those needs into Kubernetes resources with configurable
values for each environment. This separation of concerns is what makes Helm charts
powerful: the same chart deploys to development with 1 replica and to production
with 10 replicas, TLS, autoscaling, and pod disruption budgets.

Understanding chart creation is also essential for customizing community charts.
When a community chart does not quite fit your needs, you need to understand
templates to fork, extend, or wrap it.

---

## Core Concepts

### Chart Directory Structure

Running `helm create` generates a scaffold:

```
my-chart/
  Chart.yaml          # Chart metadata (name, version, dependencies)
  values.yaml         # Default configuration values
  .helmignore         # Patterns to ignore when packaging
  charts/             # Dependency charts (subcharts)
  templates/          # Kubernetes manifest templates
    NOTES.txt         # Post-install usage notes (rendered template)
    _helpers.tpl      # Named template definitions (partials)
    deployment.yaml   # Deployment template
    hpa.yaml          # HorizontalPodAutoscaler template
    ingress.yaml      # Ingress template
    service.yaml      # Service template
    serviceaccount.yaml # ServiceAccount template
    tests/
      test-connection.yaml  # Helm test pod
```

### Chart.yaml

The `Chart.yaml` file is the chart's identity:

```yaml
apiVersion: v2                    # v2 for Helm 3 charts
name: my-web-app                  # Chart name
version: 1.2.0                    # Chart version (SemVer)
appVersion: "3.5.1"               # Application version (informational)
description: A web application chart
type: application                 # "application" or "library"
keywords:
  - web
  - api
maintainers:
  - name: Platform Team
    email: platform@example.com
home: https://github.com/myorg/my-web-app
sources:
  - https://github.com/myorg/my-web-app
dependencies:
  - name: postgresql
    version: "14.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
```

**version** is the chart version (the packaging). **appVersion** is the version
of the software being deployed. They are independent: you might release chart
version `1.3.0` deploying app version `2.1.0`.

### Go Template Syntax

Helm templates use Go's `text/template` package with Sprig function library
extensions. Template directives are enclosed in `{{ }}`:

```yaml
# Variable substitution
replicas: {{ .Values.replicaCount }}

# Conditional blocks
{{- if .Values.ingress.enabled }}
apiVersion: networking.k8s.io/v1
kind: Ingress
# ...
{{- end }}

# Loops
{{- range .Values.ingress.hosts }}
  - host: {{ .host | quote }}
{{- end }}

# Whitespace control: {{- trims left whitespace, -}} trims right
```

The `-` inside template delimiters controls whitespace. `{{-` trims all
whitespace (including newlines) to the left, and `-}}` trims to the right.
This is critical for generating valid YAML.

### Built-in Objects

Helm provides several built-in objects accessible in templates:

```yaml
# .Release - Information about the release
{{ .Release.Name }}        # Release name (helm install <name>)
{{ .Release.Namespace }}   # Target namespace
{{ .Release.Revision }}    # Revision number (1 for install)
{{ .Release.IsInstall }}   # True if this is an install
{{ .Release.IsUpgrade }}   # True if this is an upgrade
{{ .Release.Service }}     # Always "Helm"

# .Values - Values from values.yaml and overrides
{{ .Values.replicaCount }}
{{ .Values.image.repository }}

# .Chart - Contents of Chart.yaml
{{ .Chart.Name }}          # Chart name
{{ .Chart.Version }}       # Chart version
{{ .Chart.AppVersion }}    # App version

# .Capabilities - Cluster capabilities
{{ .Capabilities.KubeVersion }}           # Kubernetes version
{{ .Capabilities.APIVersions.Has "autoscaling/v2" }}

# .Template - Current template information
{{ .Template.Name }}       # e.g., "my-chart/templates/deployment.yaml"
{{ .Template.BasePath }}   # e.g., "my-chart/templates"

# .Files - Access to non-template files in the chart
{{ .Files.Get "config.ini" }}
{{ .Files.AsSecrets }}
{{ .Files.AsConfig }}
```

### Template Functions

Helm includes the Sprig template function library plus some Helm-specific functions:

```yaml
# quote - Wrap in double quotes (safe for YAML strings)
value: {{ .Values.name | quote }}
# Result: value: "my-app"

# default - Provide a fallback value
replicas: {{ .Values.replicaCount | default 1 }}

# required - Fail with a message if the value is empty
image: {{ required "image.repository is required" .Values.image.repository }}

# toYaml - Convert a value to YAML
resources:
{{ toYaml .Values.resources | indent 2 }}

# indent / nindent - Indent text by N spaces
# indent adds to current position, nindent adds a newline first
spec:
  containers:
    resources:
{{ toYaml .Values.resources | indent 6 }}
    # vs
    resources:
      {{- toYaml .Values.resources | nindent 6 }}

# include - Render a named template and return it as a string
labels:
  {{- include "my-chart.labels" . | nindent 4 }}

# tpl - Render a string as a template
annotation: {{ tpl .Values.customAnnotation . }}

# lookup - Query the Kubernetes API from within a template
{{ $secret := lookup "v1" "Secret" .Release.Namespace "my-secret" }}

# ternary - Inline conditional
type: {{ ternary "ClusterIP" "LoadBalancer" .Values.internal }}

# printf - Formatted string
name: {{ printf "%s-%s" .Release.Name "api" }}
```

### Named Templates (_helpers.tpl)

Named templates (partials) are reusable template fragments defined with `define`
and invoked with `include`:

```yaml
# templates/_helpers.tpl

# Chart name, truncated to 63 characters
{{- define "my-chart.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end }}

# Fully qualified app name
{{- define "my-chart.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := default .Chart.Name .Values.nameOverride -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end }}

# Common labels
{{- define "my-chart.labels" -}}
helm.sh/chart: {{ include "my-chart.chart" . }}
app.kubernetes.io/name: {{ include "my-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

# Selector labels (subset of common labels used in matchLabels)
{{- define "my-chart.selectorLabels" -}}
app.kubernetes.io/name: {{ include "my-chart.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

# Chart name and version for the chart label
{{- define "my-chart.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end }}
```

Use `include` (not `template`) to invoke named templates because `include`
returns a string that can be piped to other functions:

```yaml
# Good: include returns a string, can be piped
labels:
  {{- include "my-chart.labels" . | nindent 4 }}

# Bad: template outputs directly, cannot be piped
labels:
  {{ template "my-chart.labels" . }}  # Indentation breaks
```

---

## Step-by-Step Practical

### Create a Chart for a Web Application

```bash
# Create the chart scaffold
helm create webapp
cd webapp
```

### Define the Values (values.yaml)

```yaml
# values.yaml
replicaCount: 2

image:
  repository: myorg/webapp
  tag: ""  # Defaults to Chart.appVersion
  pullPolicy: IfNotPresent

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  automount: true
  annotations: {}
  name: ""

podAnnotations: {}
podLabels: {}

service:
  type: ClusterIP
  port: 80
  targetPort: 8080

ingress:
  enabled: false
  className: nginx
  annotations: {}
  hosts:
    - host: webapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []

resources:
  limits:
    cpu: 500m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 10
  periodSeconds: 15

readinessProbe:
  httpGet:
    path: /ready
    port: http
  initialDelaySeconds: 5
  periodSeconds: 10

autoscaling:
  enabled: false
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

env: []
  # - name: DATABASE_URL
  #   value: "postgres://localhost:5432/mydb"
  # - name: API_KEY
  #   valueFrom:
  #     secretKeyRef:
  #       name: api-credentials
  #       key: api-key

configMap:
  enabled: false
  data: {}
    # app.conf: |
    #   setting1=value1
    #   setting2=value2

nodeSelector: {}
tolerations: []
affinity: {}
```

### Create the Deployment Template

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "webapp.fullname" . }}
  labels:
    {{- include "webapp.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "webapp.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        {{- if .Values.configMap.enabled }}
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- end }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "webapp.labels" . | nindent 8 }}
        {{- with .Values.podLabels }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "webapp.serviceAccountName" . }}
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          {{- with .Values.livenessProbe }}
          livenessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- with .Values.readinessProbe }}
          readinessProbe:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          {{- with .Values.env }}
          env:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          {{- if .Values.configMap.enabled }}
          volumeMounts:
            - name: config
              mountPath: /etc/webapp
              readOnly: true
          {{- end }}
      {{- if .Values.configMap.enabled }}
      volumes:
        - name: config
          configMap:
            name: {{ include "webapp.fullname" . }}-config
      {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### Create the ConfigMap Template

```yaml
# templates/configmap.yaml
{{- if .Values.configMap.enabled }}
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "webapp.fullname" . }}-config
  labels:
    {{- include "webapp.labels" . | nindent 4 }}
data:
  {{- range $key, $value := .Values.configMap.data }}
  {{ $key }}: |
    {{- $value | nindent 4 }}
  {{- end }}
{{- end }}
```

### Create Environment-Specific Values

```yaml
# values-dev.yaml
replicaCount: 1
image:
  tag: "latest"
resources:
  limits:
    cpu: 200m
    memory: 128Mi
  requests:
    cpu: 50m
    memory: 64Mi
env:
  - name: LOG_LEVEL
    value: "debug"
  - name: ENV
    value: "development"
```

```yaml
# values-production.yaml
replicaCount: 4
image:
  tag: "3.5.1"
resources:
  limits:
    cpu: "1"
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: webapp.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: webapp-tls
      hosts:
        - webapp.example.com
autoscaling:
  enabled: true
  minReplicas: 4
  maxReplicas: 20
  targetCPUUtilizationPercentage: 65
env:
  - name: LOG_LEVEL
    value: "warn"
  - name: ENV
    value: "production"
configMap:
  enabled: true
  data:
    app.conf: |
      workers=8
      timeout=30
      keepalive=true
```

### Validate and Test the Chart

```bash
# Lint the chart for errors
helm lint ./webapp
# ==> Linting ./webapp
# [INFO] Chart.yaml: icon is recommended
# 1 chart(s) linted, 0 chart(s) failed

# Render templates locally to verify output
helm template my-webapp ./webapp -f values-production.yaml

# Dry run against the cluster (validates with the API server)
helm install my-webapp ./webapp -f values-production.yaml --dry-run

# Install for real
helm install my-webapp ./webapp \
  -f values-dev.yaml \
  -n dev --create-namespace \
  --wait --timeout 3m

# Package the chart for distribution
helm package ./webapp
# Successfully packaged chart and saved it to: webapp-1.2.0.tgz
```

---

## Exercises

### Exercise 1: Chart Scaffold Analysis
Run `helm create practice-app` and read every generated file. For each file,
write a one-sentence description of its purpose. Identify which files use Go
template syntax and which are plain YAML.

### Exercise 2: Custom Template
Create a chart that deploys a CronJob. The values should allow configuring the
schedule, image, command, resource limits, and success/failure history limits.
Test with `helm template` and verify the output is valid YAML.

### Exercise 3: Conditional Resources
Extend the webapp chart to optionally create a PodDisruptionBudget. Add a
`pdb.enabled` value (default false) and a `pdb.minAvailable` value. The PDB
should only be rendered when enabled. Verify with `helm template` both with
and without the PDB enabled.

### Exercise 4: Template Debugging
Intentionally introduce three different template errors (wrong indentation,
missing variable, incorrect function name). Use `helm lint` and `helm template`
to identify each error. Document the error messages and how you fixed each one.

### Exercise 5: Multi-Container Pod
Create a chart that deploys a pod with a main application container and a sidecar
logging container. Both should be configurable through values.yaml. Use named
templates in `_helpers.tpl` to generate container specs.

---

## Knowledge Check

### Question 1
What is the difference between `template` and `include` in Helm, and why should
you prefer `include`?

**Answer:** Both render a named template, but `template` outputs the result
directly into the YAML stream while `include` returns the result as a string.
Because `include` returns a string, you can pipe it through functions like
`nindent`, `indent`, `trim`, or `quote`. With `template`, you cannot control
indentation after rendering, which often produces invalid YAML when the template
is used at different nesting levels. Always prefer `include`.

### Question 2
What does the `checksum/config` annotation in the Deployment pod template do?

**Answer:** The annotation `checksum/config: {{ include ... | sha256sum }}`
computes a hash of the ConfigMap template content. When the ConfigMap changes
(even if the Deployment spec does not), the annotation value changes, which
modifies the pod template spec. This causes Kubernetes to perform a rolling
restart of the pods, picking up the new ConfigMap. Without this pattern, pods
would continue running with the old (cached) ConfigMap values until manually
restarted.

### Question 3
Why does `values.yaml` set `image.tag: ""` with a comment saying it defaults
to `Chart.appVersion`?

**Answer:** In the template, the image is constructed as
`{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}`.
Setting `tag` to an empty string means the `default` function kicks in and uses
`Chart.appVersion`. This ensures the chart always has a valid image tag (the app
version) without requiring users to specify one. Users can override it with
`--set image.tag=v2.0.0` for specific deployments. This pattern ties the default
image to the chart's declared app version.

### Question 4
Explain the whitespace difference between `{{ }}` and `{{- -}}`.

**Answer:** `{{ }}` preserves whitespace on both sides of the directive.
`{{-` trims all whitespace (spaces, tabs, newlines) immediately before the
directive. `-}}` trims all whitespace immediately after the directive. This is
essential in YAML because extra blank lines or spaces produce invalid output.
For example, `{{- if .Values.enabled }}` removes the blank line that would
otherwise appear where the `if` statement is, keeping the rendered YAML clean.

### Question 5
What happens if you use `toYaml` without `indent` or `nindent`?

**Answer:** `toYaml` converts a Go data structure to YAML text, but it does not
add any indentation. If the YAML snippet needs to be nested inside another
structure (which it almost always does), the output will be at the wrong
indentation level, producing invalid YAML. You must always pair `toYaml` with
`indent N` (which adds N spaces to every line) or `nindent N` (which adds a
newline first, then indents by N spaces). The choice between `indent` and
`nindent` depends on where the directive appears in the template.
