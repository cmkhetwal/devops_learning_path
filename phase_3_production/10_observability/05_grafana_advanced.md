# Lesson 05: Grafana Advanced

## Why This Matters in DevOps

Building a single dashboard is easy. Building a dashboard ecosystem that serves
SREs during incidents, provides executive visibility into reliability, enables
developers to debug performance issues, and survives team turnover — that is hard.

Advanced Grafana skills separate the engineer who creates "pretty charts" from the
one who builds actionable observability infrastructure. This includes designing
dashboards around methodologies (USE, RED, SLO), provisioning dashboards as code
through Terraform, embedding dashboards for stakeholders, and building SLO tracking
systems that drive real engineering decisions.

---

## Core Concepts

### Dashboard Best Practices

#### The USE Dashboard Template

Create one row per resource (CPU, memory, disk, network):

```
+------------------------------------------------------------------+
| CPU                                                                |
| [Utilization]        [Saturation]          [Errors]               |
| 73% used             0.2 load/core        0 MCE events           |
| [Time Series: CPU %] [Time Series: Load]  [Time Series: Errors]  |
+------------------------------------------------------------------+
| Memory                                                             |
| [Utilization]        [Saturation]          [Errors]               |
| 68% used             12 pages/s swapped   0 OOM kills             |
+------------------------------------------------------------------+
| Disk                                                               |
| [Utilization]        [Saturation]          [Errors]               |
| 45% used             23ms avg wait        0 I/O errors            |
+------------------------------------------------------------------+
| Network                                                            |
| [Utilization]        [Saturation]          [Errors]               |
| 120 Mbps / 1 Gbps    0 drops              0 errors               |
+------------------------------------------------------------------+
```

#### The RED Dashboard Template

One row per service:

```
+------------------------------------------------------------------+
| payment-service                                                    |
| [Rate]                 [Errors]              [Duration]            |
| 456 req/s              0.03%                 p50: 12ms p99: 89ms  |
| [Time Series: Rate]    [Time Series: Errors] [Heatmap: Latency]  |
+------------------------------------------------------------------+
| user-service                                                       |
| [Rate]                 [Errors]              [Duration]            |
| 1,230 req/s            0.01%                 p50: 5ms p99: 23ms   |
+------------------------------------------------------------------+
```

### Annotations

Annotations mark events on time series panels — deployments, incidents, scaling
events:

```promql
# Annotation query: show deployments
# Data source: Prometheus
# Query:
changes(kube_deployment_status_observed_generation{
  namespace="$namespace", deployment="$service"
}[2m]) > 0
```

Or use the Grafana API to push annotations from CI/CD:

```bash
# Push an annotation from a deployment pipeline
curl -X POST http://grafana:3000/api/annotations \
  -H "Authorization: Bearer <api-key>" \
  -H "Content-Type: application/json" \
  -d '{
    "dashboardUID": "abc123",
    "time": '$(date +%s000)',
    "tags": ["deployment", "payment-service"],
    "text": "Deployed payment-service v3.2.1"
  }'
```

Annotations create visual markers on graphs, making it trivial to correlate
deployments with metric changes.

### Alerting in Grafana

Grafana has its own alerting system (separate from Prometheus Alertmanager):

```yaml
# Alert rule provisioning
# /etc/grafana/provisioning/alerting/rules.yaml
apiVersion: 1
groups:
  - orgId: 1
    name: service-alerts
    folder: Alerts
    interval: 1m
    rules:
      - uid: high-error-rate
        title: High Error Rate
        condition: C
        data:
          - refId: A
            relativeTimeRange:
              from: 300
              to: 0
            datasourceUid: prometheus
            model:
              expr: >
                sum(rate(http_requests_total{status=~"5.."}[5m]))
                /
                sum(rate(http_requests_total[5m]))
          - refId: B
            relativeTimeRange:
              from: 300
              to: 0
            datasourceUid: __expr__
            model:
              type: reduce
              expression: A
              reducer: last
          - refId: C
            datasourceUid: __expr__
            model:
              type: threshold
              expression: B
              conditions:
                - evaluator:
                    type: gt
                    params: [0.01]
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: Error rate exceeds 1%
```

### Dashboard-as-Code

#### JSON Provisioning

Export and version-control dashboard JSON:

```bash
# Export all dashboards from a folder
for uid in $(curl -s http://admin:admin@localhost:3000/api/search?folderIds=1 | jq -r '.[].uid'); do
  curl -s http://admin:admin@localhost:3000/api/dashboards/uid/$uid | \
    jq '.dashboard | del(.id, .uid, .version)' > dashboards/${uid}.json
done
```

```yaml
# Kubernetes ConfigMap for dashboard provisioning
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboards
  namespace: monitoring
  labels:
    grafana_dashboard: "1"    # Sidecar picks this up
data:
  service-overview.json: |
    {
      "title": "Service Overview",
      "panels": [...]
    }
```

#### Grafana Terraform Provider

```hcl
# providers.tf
terraform {
  required_providers {
    grafana = {
      source  = "grafana/grafana"
      version = "~> 2.0"
    }
  }
}

provider "grafana" {
  url  = "http://grafana.example.com"
  auth = var.grafana_api_key
}

# Data sources
resource "grafana_data_source" "prometheus" {
  type = "prometheus"
  name = "Prometheus"
  url  = "http://prometheus:9090"

  json_data_encoded = jsonencode({
    timeInterval = "15s"
  })
}

resource "grafana_data_source" "loki" {
  type = "loki"
  name = "Loki"
  url  = "http://loki:3100"
}

# Folders
resource "grafana_folder" "platform" {
  title = "Platform"
}

resource "grafana_folder" "services" {
  title = "Services"
}

# Dashboard from JSON file
resource "grafana_dashboard" "service_overview" {
  folder      = grafana_folder.services.id
  config_json = file("dashboards/service-overview.json")

  overwrite = true
}

# Alert notification channel
resource "grafana_contact_point" "slack" {
  name = "Slack"

  slack {
    url     = var.slack_webhook_url
    channel = "#alerts"
  }
}

# Alert notification policy
resource "grafana_notification_policy" "default" {
  contact_point = grafana_contact_point.slack.name
  group_by      = ["alertname"]

  policy {
    contact_point = grafana_contact_point.slack.name
    matcher {
      label = "severity"
      match = "="
      value = "critical"
    }
  }
}
```

### Organizations and Teams

For multi-tenant environments:

```
Organization: ACME Corp
├── Team: Platform Engineering
│   ├── Folder: Platform Dashboards
│   └── Folder: Infrastructure
├── Team: Payments
│   ├── Folder: Payment Service
│   └── Folder: Payment SLOs
├── Team: Frontend
│   └── Folder: Frontend Services
└── Service Accounts
    ├── CI/CD Bot (annotation push)
    └── Terraform Bot (provisioning)
```

Teams can have Viewer, Editor, or Admin roles per folder. This enables self-service
dashboards while maintaining governance.

### Sharing and Embedding

```bash
# Public snapshots (time-limited, no live data)
# Dashboard > Share > Snapshot > Publish to snapshots.raintank.io

# Embedded panels (iframe)
# Dashboard > Panel > Share > Embed
# <iframe src="http://grafana:3000/d-solo/abc123/dashboard?panelId=2"
#   width="450" height="200" frameborder="0"></iframe>

# Direct link with time range
# http://grafana:3000/d/abc123/service-overview?from=now-6h&to=now&var-namespace=production
```

---

## Step-by-Step Practical

### Create an SRE Dashboard with SLO Tracking

**Step 1: Define SLO recording rules in Prometheus**

```yaml
# slo-recording-rules.yaml
groups:
  - name: slo_calculations
    interval: 60s
    rules:
      # 30-day availability (ratio of non-5xx requests)
      - record: slo:http_availability:ratio30d
        expr: |
          sum(increase(http_requests_total{status!~"5.."}[30d]))
          /
          sum(increase(http_requests_total[30d]))
        labels:
          slo: availability

      # 30-day latency SLI (ratio of requests < 500ms)
      - record: slo:http_latency:ratio30d
        expr: |
          sum(increase(http_request_duration_seconds_bucket{le="0.5"}[30d]))
          /
          sum(increase(http_request_duration_seconds_count[30d]))
        labels:
          slo: latency

      # Error budget remaining (availability)
      - record: slo:error_budget:remaining_availability
        expr: |
          1 - (
            (1 - slo:http_availability:ratio30d)
            / (1 - 0.999)
          )

      # Error budget remaining (latency)
      - record: slo:error_budget:remaining_latency
        expr: |
          1 - (
            (1 - slo:http_latency:ratio30d)
            / (1 - 0.99)
          )

      # Burn rate (how fast the budget is being consumed)
      - record: slo:burn_rate:1h
        expr: |
          (
            sum(rate(http_requests_total{status=~"5.."}[1h]))
            /
            sum(rate(http_requests_total[1h]))
          ) / 0.001
```

**Step 2: Build the SLO dashboard**

```
+------------------------------------------------------------------+
| SRE SLO Dashboard                     [30 days v] [production v]  |
+------------------------------------------------------------------+
| Availability SLO: 99.9%                                           |
| [Gauge]           [Stat]              [Time Series]               |
| Current: 99.94%   Budget Remaining:   Availability over time      |
|                   40.2%               [---____---__------]         |
+------------------------------------------------------------------+
| Latency SLO: 99% of requests < 500ms                             |
| [Gauge]           [Stat]              [Time Series]               |
| Current: 99.3%    Budget Remaining:   Latency SLI over time       |
|                   30.1%               [---____---__------]         |
+------------------------------------------------------------------+
| Error Budget Burn Rate                                             |
| [Time Series - Full Width]                                        |
| 1x = sustainable | >1x = burning | >14.4x = emergency            |
| [____/\____/\_____________________________]                       |
+------------------------------------------------------------------+
| Recent Incidents (Annotations)                                     |
| [Table: timestamp, duration, budget consumed, root cause]          |
+------------------------------------------------------------------+
```

Panel configurations:

Availability Gauge:
```promql
slo:http_availability:ratio30d{job="$service"} * 100
```
Settings: Min=99, Max=100, Thresholds: Red < 99.9, Yellow < 99.95, Green >= 99.95.

Error Budget Remaining:
```promql
slo:error_budget:remaining_availability{job="$service"} * 100
```
Settings: Unit = percent, Thresholds: Red < 10, Yellow < 30, Green >= 30.

Burn Rate:
```promql
slo:burn_rate:1h{job="$service"}
```
Settings: Y-axis min=0, Threshold lines at 1.0 (sustainable) and 14.4 (critical).

**Step 3: Add deployment annotations**

```promql
# Annotation: deployments
changes(kube_deployment_status_observed_generation{
  namespace="$namespace"
}[2m]) > 0
```

**Step 4: Provision via Terraform**

```hcl
resource "grafana_dashboard" "slo_dashboard" {
  folder      = grafana_folder.sre.id
  config_json = file("dashboards/slo-dashboard.json")
  overwrite   = true
}
```

**Step 5: Set up alert for error budget exhaustion**

```yaml
# Alert when error budget drops below 10%
- alert: ErrorBudgetNearlyExhausted
  expr: slo:error_budget:remaining_availability < 0.10
  for: 5m
  labels:
    severity: critical
    team: sre
  annotations:
    summary: "Error budget for {{ $labels.job }} is nearly exhausted"
    description: "Only {{ $value | humanizePercentage }} of error budget remains"
    action: "Freeze feature releases and focus on reliability"
```

---

## Exercises

### Exercise 1: USE Dashboard
Build a USE dashboard for your Kubernetes nodes. Each row should represent one
resource (CPU, memory, disk, network) with three panels (utilization, saturation,
errors).

### Exercise 2: SLO Tracking
Define SLOs for a service you operate. Create Prometheus recording rules for the
SLIs and build a Grafana dashboard showing current SLI values, error budget
remaining, and burn rate.

### Exercise 3: Terraform Provisioning
Use the Grafana Terraform provider to create a data source, a folder, and a
dashboard. Store the Terraform config in Git and run `terraform apply` to deploy.
Modify the dashboard and re-apply to verify the update flow.

### Exercise 4: Annotation Pipeline
Configure your CI/CD pipeline to push annotations to Grafana on every deployment.
Include the service name, version, deployer, and commit SHA in the annotation text.
Verify annotations appear on your time series panels.

### Exercise 5: Alert Notification Flow
Set up Grafana alerting with at least two contact points (e.g., Slack and email).
Create notification policies that route critical alerts to Slack immediately and
warning alerts to email as a daily digest.

---

## Knowledge Check

### Question 1
What is the difference between a USE dashboard and a RED dashboard?

<details>
<summary>Answer</summary>

A **USE dashboard** focuses on infrastructure resources (CPU, memory, disk, network).
Each resource row shows Utilization (% capacity used), Saturation (excess demand /
queueing), and Errors (resource-level error events).

A **RED dashboard** focuses on services and their request handling. Each service row
shows Rate (requests/second), Errors (failed requests/second), and Duration (latency
distribution).

USE answers "are the resources healthy?" while RED answers "is the service healthy
from the user's perspective?" Both are needed for complete observability.

</details>

### Question 2
How do you add deployment annotations to a Grafana dashboard?

<details>
<summary>Answer</summary>

Two approaches:

1. **PromQL-based**: Add an annotation query using a Prometheus metric that changes
   on deployment (e.g., `changes(kube_deployment_status_observed_generation[2m]) > 0`).

2. **API-based**: Push annotations from your CI/CD pipeline using the Grafana API
   (`POST /api/annotations`) with tags, text, and timestamp. This provides richer
   metadata (version, deployer, commit SHA).

Both create visual markers on time series panels that help correlate deployments
with metric changes during incident investigation.

</details>

### Question 3
What is an error budget burn rate, and what thresholds are commonly used?

<details>
<summary>Answer</summary>

Burn rate measures how fast the error budget is being consumed relative to the
allowed rate. A burn rate of 1.0 means the budget is being consumed exactly at the
sustainable rate (it will be exhausted at the end of the SLO window). A burn rate of
14.4 means the budget will be exhausted in 1/14.4 of the window (~2 days in a
30-day window).

Common thresholds:
- **< 1.0** — Budget is being consumed slower than allowed (safe)
- **1.0 - 5.0** — Elevated consumption (warning)
- **> 14.4** — Emergency: budget will be exhausted within 2 days at this rate
  (requires immediate action)

Google's multi-window, multi-burn-rate alerting uses 14.4x (2% budget/1h),
6x (5% budget/6h), and 1x (10% budget/3d) thresholds.

</details>

### Question 4
Why use the Grafana Terraform provider instead of manually creating dashboards?

<details>
<summary>Answer</summary>

The Terraform provider enables:
1. **Version control** — Dashboard definitions are in Git, reviewed via PRs.
2. **Reproducibility** — `terraform apply` recreates the exact same setup on any
   Grafana instance.
3. **Consistency** — Data sources, folders, alert policies, and dashboards are all
   managed together.
4. **Disaster recovery** — If Grafana is lost, run `terraform apply` to restore
   everything.
5. **Multi-environment** — Same dashboards can be deployed to dev, staging, and
   production Grafana instances with different variables.

</details>
