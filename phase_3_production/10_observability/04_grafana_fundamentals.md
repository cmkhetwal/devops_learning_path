# Lesson 04: Grafana Fundamentals

## Why This Matters in DevOps

Prometheus collects and stores metrics. Loki stores logs. Tempo stores traces. But
none of them have a strong visualization layer. Grafana is the visualization and
exploration platform that ties all observability data together into a single pane
of glass.

Grafana is used by millions of developers across industries — from startups to NASA.
It is not just a dashboarding tool; it is the interface through which engineering
teams understand their systems. An SRE who cannot build effective Grafana dashboards
is like a pilot who cannot read instruments. The system may be working, but you
cannot tell.

---

## Core Concepts

### What Is Grafana?

Grafana is an open-source analytics and interactive visualization platform. It
connects to dozens of data sources (Prometheus, Loki, Tempo, Elasticsearch,
PostgreSQL, MySQL, CloudWatch, and more), provides a rich query editor, and offers
powerful dashboard capabilities.

Key features:
- **Multi-data-source**: One dashboard can combine Prometheus metrics, Loki logs,
  and Tempo traces.
- **Templating**: Variables make dashboards dynamic and reusable.
- **Alerting**: Built-in alert rules with notification channels.
- **Provisioning**: Dashboards and data sources can be defined as code.
- **Plugins**: Hundreds of community panels and data source plugins.

### Data Sources

Data sources are the backends Grafana queries. Configuration:

```yaml
# Grafana data source provisioning
# /etc/grafana/provisioning/datasources/datasources.yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
    jsonData:
      timeInterval: '15s'
      exemplarTraceIdDestinations:
        - name: traceID
          datasourceUid: tempo

  - name: Loki
    type: loki
    url: http://loki:3100
    access: proxy
    jsonData:
      derivedFields:
        - name: TraceID
          matcherRegex: '"trace_id":"(\w+)"'
          url: '$${__value.raw}'
          datasourceUid: tempo

  - name: Tempo
    type: tempo
    url: http://tempo:3200
    access: proxy
    jsonData:
      tracesToLogs:
        datasourceUid: loki
        tags: ['service.name']
      tracesToMetrics:
        datasourceUid: prometheus
        tags: ['service.name']
```

### Dashboard Creation

A Grafana dashboard is a collection of panels arranged on a grid:

```
+------------------------------------------------------------------+
|                    Service Overview Dashboard                      |
+------------------------------------------------------------------+
| [Stat]          [Stat]          [Stat]          [Stat]            |
| Request Rate    Error Rate      P99 Latency     Uptime            |
| 1,234 req/s     0.02%          145ms            99.97%            |
+------------------------------------------------------------------+
| [Time Series - Full Width]                                        |
| Request Rate Over Time                                            |
|  ___    ___                                                       |
| /   \  /   \    ___                                               |
|/     \/     \__/   \                                              |
+------------------------------------------------------------------+
| [Time Series]              | [Heatmap]                            |
| Error Rate by Endpoint     | Latency Distribution                 |
|                            |                                       |
+------------------------------------------------------------------+
| [Table]                                                           |
| Top 10 Slowest Endpoints                                          |
+------------------------------------------------------------------+
```

### Panel Types

#### Time Series (Graph)

The most common panel. Displays metrics over time.

```promql
# Query for a time series panel
rate(http_requests_total{job="web-service"}[5m])

# Multiple queries on one panel:
# A: rate(http_requests_total{status=~"2.."}[5m])   # Success (green)
# B: rate(http_requests_total{status=~"4.."}[5m])   # Client error (yellow)
# C: rate(http_requests_total{status=~"5.."}[5m])   # Server error (red)
```

#### Stat

Single large number with optional sparkline. Ideal for KPIs.

```promql
# Current request rate
sum(rate(http_requests_total{job="web-service"}[5m]))

# Thresholds:
#   Green: 0 - 1000
#   Yellow: 1000 - 5000
#   Red: > 5000
```

#### Gauge

A circular or bar gauge showing a value against min/max.

```promql
# CPU utilization as a percentage
100 * (1 - avg(rate(node_cpu_seconds_total{mode="idle"}[5m])))

# Thresholds:
#   Green: 0 - 70
#   Yellow: 70 - 85
#   Red: 85 - 100
```

#### Table

Tabular data with sorting, filtering, and column formatting.

```promql
# Top endpoints by latency
topk(10,
  histogram_quantile(0.99,
    sum by (endpoint, le) (rate(http_request_duration_seconds_bucket[5m]))
  )
)
```

#### Heatmap

Visualizes distribution over time. Perfect for latency histograms.

```promql
# Histogram buckets for heatmap
sum by (le) (increase(http_request_duration_seconds_bucket[1m]))

# Format: Heatmap
# Data format: Time series buckets
# Y-axis: le values
# Color: Spectral (cool to hot)
```

#### Bar Chart

Categorical data comparison.

```promql
# Requests per service
sum by (service) (increase(http_requests_total[1h]))
```

### Variables (Template Queries)

Variables make dashboards interactive and reusable:

```yaml
# Variable: namespace
Type: Query
Data source: Prometheus
Query: label_values(kube_pod_info, namespace)
# Creates a dropdown of all namespaces

# Variable: service
Type: Query
Data source: Prometheus
Query: label_values(http_requests_total{namespace="$namespace"}, service)
# Cascading: filtered by selected namespace

# Variable: interval
Type: Interval
Values: 1m, 5m, 15m, 1h
Auto: enabled (adjusts based on time range)
```

Using variables in queries:

```promql
# $namespace and $service are replaced by dropdown selections
rate(http_requests_total{namespace="$namespace", service="$service"}[$__rate_interval])

# $__rate_interval is a special Grafana variable that automatically picks the
# correct rate window based on scrape interval and dashboard time range
```

### Dashboard Provisioning

Dashboards-as-code using provisioning files:

```yaml
# /etc/grafana/provisioning/dashboards/dashboards.yaml
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: 'Platform'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
      foldersFromFilesStructure: true
```

Dashboard JSON can be exported from the UI and committed to Git:

```bash
# Export a dashboard
curl -s http://admin:admin@localhost:3000/api/dashboards/uid/abc123 | \
  jq '.dashboard' > dashboards/service-overview.json

# The JSON file goes into the provisioning path
```

### Folder Organization

```
Dashboards/
  Platform/
    Cluster Overview
    Node Health
    Namespace Resources
  Services/
    API Gateway
    Payment Service
    User Service
  SRE/
    SLO Dashboard
    Error Budget Tracker
    Incident Timeline
  Infrastructure/
    Database Performance
    Redis Metrics
    Message Queue Health
```

---

## Step-by-Step Practical

### Build a Comprehensive Service Dashboard

**Step 1: Access Grafana**

```bash
# If using kube-prometheus-stack, Grafana is included
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Default credentials: admin / prom-operator
```

**Step 2: Create a new dashboard**

Navigate to Dashboards > New Dashboard > Add visualization.

**Step 3: Add the header row (Stat panels)**

Panel 1 — Request Rate:
```promql
sum(rate(http_requests_total{namespace="$namespace", service="$service"}[$__rate_interval]))
```
Settings: Unit = requests/sec (reqps), Stat style = Big value with sparkline.

Panel 2 — Error Rate:
```promql
sum(rate(http_requests_total{namespace="$namespace", service="$service", status=~"5.."}[$__rate_interval]))
/
sum(rate(http_requests_total{namespace="$namespace", service="$service"}[$__rate_interval]))
```
Settings: Unit = percentunit, Thresholds: Green < 0.001, Yellow < 0.01, Red >= 0.01.

Panel 3 — P99 Latency:
```promql
histogram_quantile(0.99,
  sum by (le) (rate(http_request_duration_seconds_bucket{
    namespace="$namespace", service="$service"
  }[$__rate_interval]))
)
```
Settings: Unit = seconds, Thresholds: Green < 0.2, Yellow < 0.5, Red >= 0.5.

Panel 4 — Uptime (30 days):
```promql
avg_over_time(up{namespace="$namespace", job="$service"}[30d]) * 100
```
Settings: Unit = percent, Decimals = 3.

**Step 4: Add the request rate time series**

```promql
# Query A (label: 2xx)
sum(rate(http_requests_total{namespace="$namespace", service="$service", status=~"2.."}[$__rate_interval]))

# Query B (label: 4xx)
sum(rate(http_requests_total{namespace="$namespace", service="$service", status=~"4.."}[$__rate_interval]))

# Query C (label: 5xx)
sum(rate(http_requests_total{namespace="$namespace", service="$service", status=~"5.."}[$__rate_interval]))
```

Color overrides: A = green, B = yellow, C = red.

**Step 5: Add the latency heatmap**

```promql
sum by (le) (increase(http_request_duration_seconds_bucket{
  namespace="$namespace", service="$service"
}[$__rate_interval]))
```

Settings: Format = Heatmap, Color scheme = Spectral.

**Step 6: Add the resource usage panels**

CPU Usage:
```promql
sum(rate(container_cpu_usage_seconds_total{
  namespace="$namespace", container="$service"
}[$__rate_interval]))
```

Memory Usage:
```promql
sum(container_memory_working_set_bytes{
  namespace="$namespace", container="$service"
})
```

**Step 7: Add variables**

Create three variables:
- `namespace`: `label_values(kube_namespace_labels, namespace)`
- `service`: `label_values(http_requests_total{namespace="$namespace"}, service)`
- `interval`: Interval type, auto-enabled

**Step 8: Save and provision**

```bash
# Export the dashboard JSON
curl -s -H "Authorization: Bearer <api-key>" \
  http://localhost:3000/api/dashboards/uid/<dashboard-uid> | \
  jq '.dashboard | del(.id) | del(.uid)' > \
  /var/lib/grafana/dashboards/service-overview.json
```

The final dashboard should look like:

```
+------------------------------------------------------------------+
| Namespace: [production v]   Service: [payment-service v]          |
+------------------------------------------------------------------+
| Request Rate  | Error Rate   | P99 Latency  | Uptime (30d)       |
| 1,234/s       | 0.02%        | 145ms        | 99.971%            |
+------------------------------------------------------------------+
| [Request Rate by Status Code - Time Series]                       |
|                                                                    |
+------------------------------------------------------------------+
| [Latency Heatmap]          | [CPU Usage]   | [Memory Usage]      |
|                            |               |                      |
+------------------------------------------------------------------+
```

---

## Exercises

### Exercise 1: First Dashboard
Create a Grafana dashboard with four Stat panels showing the Golden Signals for any
service running in your cluster. Use the `$__rate_interval` variable for all rate
queries.

### Exercise 2: Template Variables
Add namespace and service variables to your dashboard so it works for any service
in any namespace. Verify that changing the namespace dropdown updates the service
dropdown (cascading variables).

### Exercise 3: Heatmap Panel
Create a heatmap panel showing request latency distribution over time. Use histogram
bucket data and configure appropriate bucket boundaries and color schemes.

### Exercise 4: Dashboard Export and Import
Export your dashboard as JSON, commit it to a Git repository, and configure Grafana
provisioning to load it automatically. Verify that deleting and restarting Grafana
restores the dashboard.

### Exercise 5: Multi-Data-Source Dashboard
Create a dashboard that shows Prometheus metrics in the top row and Loki log results
in the bottom row. Configure a click-through from a time series panel to a Loki
logs panel filtered by the same time range.

---

## Knowledge Check

### Question 1
What is the difference between `proxy` and `direct` access modes for data sources?

<details>
<summary>Answer</summary>

**Proxy (Server)**: Grafana's backend server makes the request to the data source.
The browser never communicates directly with Prometheus/Loki. This is preferred
because it keeps data source URLs and credentials on the server side.

**Direct (Browser)**: The browser makes requests directly to the data source. The
data source URL must be accessible from the user's browser. This is rarely used
and has been deprecated in newer Grafana versions.

</details>

### Question 2
What is `$__rate_interval` and why should you use it instead of a hardcoded interval?

<details>
<summary>Answer</summary>

`$__rate_interval` is a Grafana variable that calculates the optimal `rate()`
window based on the scrape interval and the dashboard time range. It ensures that
the rate window always contains at least four data points (4 * scrape_interval),
which is the minimum for accurate `rate()` calculations.

Using a hardcoded interval like `[5m]` can produce incorrect results if the scrape
interval changes or if the dashboard time range is very short. `$__rate_interval`
adapts automatically.

</details>

### Question 3
How does dashboard provisioning work?

<details>
<summary>Answer</summary>

Dashboard provisioning loads dashboards from files (JSON or YAML) on disk when
Grafana starts. You configure a provider in
`/etc/grafana/provisioning/dashboards/` that specifies a directory path. Grafana
watches that directory and loads any dashboard files it finds. This enables
dashboards-as-code: export a dashboard as JSON, commit it to Git, and deploy it
via ConfigMap or volume mount. Provisioned dashboards can be set to read-only
(`disableDeletion: true`) to prevent UI edits from diverging from the code.

</details>

### Question 4
What are cascading variables and how do you set them up?

<details>
<summary>Answer</summary>

Cascading variables are template variables where one variable's values depend on
another variable's selection. For example:

- Variable `namespace`: `label_values(kube_namespace_labels, namespace)`
- Variable `service`: `label_values(http_requests_total{namespace="$namespace"}, service)`

When the user selects a namespace, the service dropdown updates to show only
services in that namespace. The key is referencing the parent variable
(`$namespace`) in the child variable's query.

</details>
