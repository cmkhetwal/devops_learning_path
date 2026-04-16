# Lesson 03: Prometheus Advanced

## Why This Matters in DevOps

Knowing how to install Prometheus and write basic PromQL is just the starting point.
In production, you need deep PromQL skills to build meaningful SLO dashboards,
recording rules to pre-compute expensive queries, alerting rules to detect problems
before users notice, and Alertmanager to route those alerts to the right people
without drowning them in noise.

The gap between a junior engineer who can query `up` and a senior SRE who can write
multi-metric join queries with histogram quantiles and error budget calculations is
enormous. This lesson bridges that gap.

---

## Core Concepts

### PromQL Deep Dive

#### rate() and irate()

```promql
# rate(): average per-second rate over the window (smoothed)
rate(http_requests_total[5m])
# Result: 23.4 (average 23.4 req/s over last 5 minutes)

# irate(): instantaneous rate using the last two data points (spiky)
irate(http_requests_total[5m])
# Result: 45.2 (rate between the last two scrapes)
```

Use `rate()` for alerts and dashboards (stable). Use `irate()` for high-resolution
graphs where you want to see spikes.

#### histogram_quantile()

```promql
# 99th percentile latency across all instances
histogram_quantile(0.99,
  sum by (le) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# 99th percentile latency per endpoint
histogram_quantile(0.99,
  sum by (le, endpoint) (
    rate(http_request_duration_seconds_bucket[5m])
  )
)

# Multiple percentiles in one query (for Grafana variables)
histogram_quantile(0.50, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

**Important**: `le` (less-than-or-equal) must always be in the `by` clause.

#### Aggregation Operators

```promql
# Sum across all instances
sum(rate(http_requests_total[5m]))

# Sum grouped by method
sum by (method) (rate(http_requests_total[5m]))

# Average CPU usage per node
avg by (node) (node_cpu_seconds_total{mode="idle"})

# Top 5 endpoints by request rate
topk(5, sum by (endpoint) (rate(http_requests_total[5m])))

# Count unique label values
count(count by (endpoint) (http_requests_total))

# Min/Max memory usage across pods
min(container_memory_working_set_bytes{container!=""})
max(container_memory_working_set_bytes{container!=""})

# Standard deviation of latency across instances
stddev(rate(http_request_duration_seconds_sum[5m]) / rate(http_request_duration_seconds_count[5m]))
```

#### Vector Matching (Joins)

```promql
# Divide two metrics with matching labels (one-to-one)
rate(http_requests_total{status=~"5.."}[5m])
  /
rate(http_requests_total[5m])

# Join on specific labels (ignoring others)
rate(http_requests_total{status=~"5.."}[5m])
  / ignoring(status)
sum without(status) (rate(http_requests_total[5m]))

# Many-to-one matching with group_left
# Example: add deployment name to pod metrics
container_memory_working_set_bytes{container!=""}
  * on(pod) group_left(deployment)
kube_pod_owner{owner_kind="ReplicaSet"}
```

#### Subqueries

```promql
# Average of 5-minute rates, computed over the last hour, sampled every minute
avg_over_time(rate(http_requests_total[5m])[1h:1m])

# Max latency over the last 24 hours
max_over_time(
  histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))[24h:5m]
)
```

#### Useful Functions

```promql
# Predict disk full in 4 hours based on 24h trend
predict_linear(node_filesystem_avail_bytes[24h], 4*3600) < 0

# Changes in gauge value over time
changes(process_start_time_seconds[1h])

# Time since last change (detect stale metrics)
time() - process_start_time_seconds

# Absent metric detection (for dead targets)
absent(up{job="payment-service"})

# Clamping values
clamp_min(disk_usage_percent, 0)
clamp_max(disk_usage_percent, 100)

# Label manipulation
label_replace(up, "short_instance", "$1", "instance", "(.+):.+")
```

### Recording Rules

Recording rules pre-compute expensive queries and store results as new time series.
This speeds up dashboard loading and makes complex queries reusable.

```yaml
# /etc/prometheus/rules/recording_rules.yaml
groups:
  - name: http_metrics
    interval: 30s      # Evaluate every 30 seconds
    rules:
      # Pre-compute request rate by endpoint
      - record: job:http_requests:rate5m
        expr: sum by (job, endpoint) (rate(http_requests_total[5m]))

      # Pre-compute error ratio
      - record: job:http_errors:ratio5m
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum by (job) (rate(http_requests_total[5m]))

      # Pre-compute latency percentiles
      - record: job:http_latency:p99_5m
        expr: |
          histogram_quantile(0.99,
            sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
          )

      - record: job:http_latency:p95_5m
        expr: |
          histogram_quantile(0.95,
            sum by (job, le) (rate(http_request_duration_seconds_bucket[5m]))
          )

  - name: slo_metrics
    interval: 60s
    rules:
      # 30-day availability SLI
      - record: slo:availability:ratio30d
        expr: |
          sum(increase(http_requests_total{status!~"5.."}[30d]))
          /
          sum(increase(http_requests_total[30d]))

      # Error budget remaining
      - record: slo:error_budget:remaining
        expr: |
          1 - (
            (1 - slo:availability:ratio30d)
            /
            (1 - 0.999)
          )
```

### Alerting Rules

```yaml
# /etc/prometheus/rules/alerting_rules.yaml
groups:
  - name: service_alerts
    rules:
      # High error rate
      - alert: HighErrorRate
        expr: job:http_errors:ratio5m > 0.01
        for: 5m
        labels:
          severity: critical
          team: backend
        annotations:
          summary: "High error rate on {{ $labels.job }}"
          description: >
            Error rate is {{ $value | humanizePercentage }} (threshold: 1%).
            This has been firing for more than 5 minutes.
          runbook_url: "https://wiki.example.com/runbooks/high-error-rate"

      # High latency
      - alert: HighLatencyP99
        expr: job:http_latency:p99_5m > 0.5
        for: 10m
        labels:
          severity: warning
          team: backend
        annotations:
          summary: "P99 latency above 500ms on {{ $labels.job }}"
          description: "P99 latency is {{ $value }}s"

      # Target down
      - alert: TargetDown
        expr: up == 0
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "Target {{ $labels.instance }} is down"

      # Disk filling up (predictive)
      - alert: DiskWillFillIn4Hours
        expr: predict_linear(node_filesystem_avail_bytes[6h], 4*3600) < 0
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Disk on {{ $labels.instance }} will be full in ~4 hours"

      # Error budget burn rate (multi-window)
      - alert: ErrorBudgetBurnHigh
        expr: |
          (
            job:http_errors:ratio5m > (14.4 * 0.001)    # 1h burn rate
            and
            job:http_errors:ratio30m > (14.4 * 0.001)   # 6h burn rate
          )
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error budget burning too fast on {{ $labels.job }}"
```

### Alertmanager

Alertmanager handles deduplication, grouping, routing, silencing, and inhibition
of alerts.

```yaml
# alertmanager.yml
global:
  resolve_timeout: 5m
  slack_api_url: 'https://hooks.slack.com/services/xxx/yyy/zzz'

route:
  receiver: 'default-slack'
  group_by: ['alertname', 'job']
  group_wait: 30s           # Wait before sending first notification
  group_interval: 5m        # Wait before sending updates
  repeat_interval: 4h       # Repeat if not resolved
  routes:
    # Critical alerts go to PagerDuty
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
      continue: true         # Also send to Slack

    # Team-specific routing
    - match:
        team: payments
      receiver: 'payments-slack'

    - match:
        team: frontend
      receiver: 'frontend-slack'

receivers:
  - name: 'default-slack'
    slack_configs:
      - channel: '#alerts'
        title: '{{ .GroupLabels.alertname }}'
        text: >
          {{ range .Alerts }}
          *{{ .Annotations.summary }}*
          {{ .Annotations.description }}
          {{ end }}

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: 'your-pagerduty-service-key'
        description: '{{ .GroupLabels.alertname }}: {{ .CommonAnnotations.summary }}'

  - name: 'payments-slack'
    slack_configs:
      - channel: '#payments-alerts'

  - name: 'frontend-slack'
    slack_configs:
      - channel: '#frontend-alerts'

inhibit_rules:
  # If a critical alert is firing, suppress warnings for the same job
  - source_match:
      severity: critical
    target_match:
      severity: warning
    equal: ['alertname', 'job']
```

### Alert Fatigue Prevention

```
Signs of alert fatigue:
- Alerts are routinely ignored or silenced
- On-call engineers do not look at pages within 5 minutes
- More than 50% of alerts do not require human action
- Alerts fire and resolve repeatedly (flapping)

Prevention strategies:
1. Alert on SYMPTOMS, not causes (alert on "high error rate", not "CPU at 80%")
2. Set appropriate `for` durations (do not alert on momentary spikes)
3. Use inhibit_rules to suppress lower-severity duplicates
4. Every alert must have a runbook_url
5. Review alerts quarterly — delete alerts nobody acts on
6. Track alert-to-action ratio as a team metric
```

### Long-Term Storage: Thanos and Mimir

Prometheus stores data locally for days or weeks. For months or years, use:

**Thanos** — Sidecar uploads Prometheus data to object storage (S3, GCS):

```yaml
# Thanos sidecar as a Prometheus container
containers:
  - name: thanos-sidecar
    image: thanosio/thanos:v0.34.0
    args:
      - sidecar
      - --prometheus.url=http://localhost:9090
      - --objstore.config-file=/etc/thanos/bucket.yaml
```

**Grafana Mimir** — Horizontally scalable, multi-tenant Prometheus-compatible TSDB:

```bash
helm install mimir grafana/mimir-distributed \
  --namespace monitoring \
  --set minio.enabled=true
```

Both provide global query view across multiple Prometheus instances and long-term
storage with downsampling.

---

## Step-by-Step Practical

### Set Up Alerting for a Web Service

**Step 1: Create alerting rules**

```yaml
# web-service-alerts.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: web-service-alerts
  namespace: monitoring
  labels:
    release: prometheus
spec:
  groups:
    - name: web-service
      rules:
        - alert: WebServiceHighErrorRate
          expr: |
            sum(rate(http_requests_total{job="web-service",status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{job="web-service"}[5m]))
            > 0.01
          for: 5m
          labels:
            severity: critical
          annotations:
            summary: "Web service error rate above 1%"
            description: "Error rate: {{ $value | humanizePercentage }}"

        - alert: WebServiceHighLatency
          expr: |
            histogram_quantile(0.99,
              sum by (le) (rate(http_request_duration_seconds_bucket{job="web-service"}[5m]))
            ) > 1.0
          for: 10m
          labels:
            severity: warning
          annotations:
            summary: "Web service P99 latency above 1s"

        - alert: WebServiceDown
          expr: up{job="web-service"} == 0
          for: 1m
          labels:
            severity: critical
          annotations:
            summary: "Web service instance {{ $labels.instance }} is down"
```

```bash
kubectl apply -f web-service-alerts.yaml
```

**Step 2: Verify rules are loaded**

```bash
# Port-forward and check
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
# Navigate to http://localhost:9090/alerts
```

**Step 3: Configure Alertmanager routing**

```yaml
# alertmanager-config.yaml
apiVersion: monitoring.coreos.com/v1alpha1
kind: AlertmanagerConfig
metadata:
  name: web-service-routing
  namespace: monitoring
  labels:
    release: prometheus
spec:
  route:
    groupBy: ['alertname']
    groupWait: 30s
    groupInterval: 5m
    repeatInterval: 4h
    receiver: slack-notifications
  receivers:
    - name: slack-notifications
      slackConfigs:
        - channel: '#web-alerts'
          apiURL:
            name: slack-webhook-url
            key: url
          title: '{{ .GroupLabels.alertname }}'
          text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
```

**Step 4: Test the alert pipeline**

```bash
# Simulate high error rate by deploying a broken version
# Or use amtool to create a test alert:
amtool alert add WebServiceHighErrorRate \
  severity=critical \
  job=web-service \
  --annotation.summary="Test alert" \
  --alertmanager.url=http://localhost:9093
```

---

## Exercises

### Exercise 1: PromQL Challenge
Write PromQL queries for:
- Error rate per endpoint for the last hour
- P95 latency broken down by HTTP method
- Percentage of request time spent in the top 3 slowest endpoints
- Prediction of when memory will be exhausted

### Exercise 2: Recording Rules
Create recording rules that pre-compute your team's SLIs. The recorded metrics
should be usable in both dashboards and alert rules.

### Exercise 3: Alertmanager Routing
Configure Alertmanager with three receivers (Slack, PagerDuty, email) and routing
rules that send critical alerts to PagerDuty, warnings to Slack, and daily
summaries to email.

### Exercise 4: Silence and Inhibition
Create a maintenance silence for planned downtime. Then set up an inhibition rule
so that a "ClusterDown" alert suppresses all other alerts for that cluster.

---

## Knowledge Check

### Question 1
What is the difference between `rate()` and `irate()` in PromQL?

<details>
<summary>Answer</summary>

`rate()` calculates the average per-second rate of increase over the entire time
window. It produces a smoothed result that is good for alerting and dashboards.

`irate()` calculates the instantaneous rate using only the last two data points
within the window. It produces a spiky result that captures short-lived bursts.

Use `rate()` for alerting rules (stable, not noisy). Use `irate()` for
high-resolution dashboard graphs where you want to see transient spikes.

</details>

### Question 2
Why must `le` always appear in the `by` clause when using `histogram_quantile()`?

<details>
<summary>Answer</summary>

`histogram_quantile()` requires the bucket boundaries (`le` labels) to calculate
percentiles. It interpolates between bucket counts to estimate the value at the
requested quantile. If `le` is aggregated away, the bucket structure is destroyed
and the function cannot work. The correct pattern is:

```promql
histogram_quantile(0.99, sum by (le, ...) (rate(my_histogram_bucket[5m])))
```

</details>

### Question 3
What is the purpose of recording rules?

<details>
<summary>Answer</summary>

Recording rules pre-compute frequently used or expensive PromQL expressions and
store the results as new time series. Benefits:
1. **Performance** — Dashboards load faster because they query pre-computed results
   instead of re-evaluating complex expressions.
2. **Reusability** — The same pre-computed metric can be used in dashboards, alerts,
   and SLO calculations.
3. **Consistency** — All consumers use the same computation, avoiding subtle
   differences in how a metric is calculated across different dashboards.

</details>

### Question 4
What is alert inhibition in Alertmanager?

<details>
<summary>Answer</summary>

Inhibition automatically suppresses certain alerts when other alerts are already
firing. For example, if a "ClusterDown" alert is active, all individual service
alerts for that cluster are inhibited because they add no new information. This
reduces alert noise during large-scale outages. Inhibition rules match on label
values — when a source alert matches, target alerts with the same specified labels
are silenced.

</details>
