# Lesson 02: Prometheus Fundamentals

## Why This Matters in DevOps

Prometheus is the de facto standard for metrics collection in cloud-native
environments. It is a CNCF graduated project (the second ever, after Kubernetes),
used by virtually every company running Kubernetes. Understanding Prometheus is not
optional for DevOps engineers — it is as fundamental as knowing Linux or Git.

Prometheus introduced a pull-based model that was radical at the time: instead of
applications pushing metrics to a central server, Prometheus scrapes HTTP endpoints
at regular intervals. This architecture is simple, reliable, and works naturally
with service discovery in dynamic environments like Kubernetes where containers
start and stop constantly.

---

## Core Concepts

### What Is Prometheus?

Prometheus is an open-source time-series database and monitoring system originally
built at SoundCloud in 2012, inspired by Google's internal Borgmon system. It
stores metrics as time series — sequences of timestamped values identified by a
metric name and a set of key-value labels.

Key characteristics:
- **Pull-based**: Prometheus scrapes targets; targets do not push.
- **Multi-dimensional**: Labels enable slicing and dicing metrics.
- **PromQL**: A powerful functional query language built for time series.
- **Standalone**: No external dependencies (no Kafka, no database cluster).
- **Alerting**: Built-in rule evaluation with Alertmanager integration.

### Pull-Based Architecture

```
+------------------+        scrape /metrics          +------------------+
|                  |  --------------------------->   |  Target (app)    |
|   Prometheus     |        HTTP GET every 15s       |  :8080/metrics   |
|   Server         |  <---------------------------   |                  |
|                  |        metric data (text)       +------------------+
|  +-----------+   |
|  | TSDB      |   |        scrape /metrics          +------------------+
|  | (storage) |   |  --------------------------->   |  Target (node)   |
|  +-----------+   |        HTTP GET every 15s       |  :9100/metrics   |
|                  |  <---------------------------   +------------------+
|  +-----------+   |
|  | Rule      |   |        push alerts              +------------------+
|  | Engine    |---+  --------------------------->   |  Alertmanager    |
|  +-----------+   |                                 |  :9093           |
+------------------+                                 +------------------+
```

Why pull instead of push?
- **Simpler targets**: Applications just expose an HTTP endpoint — no client
  library for sending metrics, no connection management.
- **Centralized control**: Prometheus decides what to scrape, how often, and which
  labels to add. No need to configure each target individually.
- **Health as a signal**: If a scrape fails, Prometheus knows the target is down.
  With push, silence is ambiguous.
- **Easy debugging**: You can `curl http://target:8080/metrics` and see exactly
  what Prometheus sees.

### Metric Types

#### Counter

A monotonically increasing value. Only goes up (or resets to zero on restart).

```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET", endpoint="/api/users", status="200"} 142857
http_requests_total{method="POST", endpoint="/api/orders", status="201"} 8923
http_requests_total{method="GET", endpoint="/api/users", status="500"} 42
```

Use counters for: request counts, error counts, bytes sent, tasks completed.
Always apply `rate()` or `increase()` to counters — the raw value is meaningless.

#### Gauge

A value that can go up or down.

```
# HELP node_memory_available_bytes Available memory in bytes
# TYPE node_memory_available_bytes gauge
node_memory_available_bytes 2147483648

# HELP http_active_connections Current number of active connections
# TYPE http_active_connections gauge
http_active_connections{service="api"} 234
```

Use gauges for: temperature, memory usage, active connections, queue depth.

#### Histogram

Samples observations and counts them in configurable buckets.

```
# HELP http_request_duration_seconds Request latency distribution
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.01"} 24054
http_request_duration_seconds_bucket{le="0.025"} 56312
http_request_duration_seconds_bucket{le="0.05"} 78901
http_request_duration_seconds_bucket{le="0.1"} 92345
http_request_duration_seconds_bucket{le="0.25"} 98765
http_request_duration_seconds_bucket{le="0.5"} 99876
http_request_duration_seconds_bucket{le="1.0"} 99987
http_request_duration_seconds_bucket{le="+Inf"} 100000
http_request_duration_seconds_sum 4523.45
http_request_duration_seconds_count 100000
```

Histograms are the most important metric type for latency monitoring. Buckets
enable calculating arbitrary percentiles with `histogram_quantile()`.

#### Summary

Similar to histogram but calculates quantiles on the client side.

```
# TYPE rpc_duration_seconds summary
rpc_duration_seconds{quantile="0.5"} 0.045
rpc_duration_seconds{quantile="0.9"} 0.12
rpc_duration_seconds{quantile="0.99"} 0.48
rpc_duration_seconds_sum 1234.56
rpc_duration_seconds_count 100000
```

**Histograms vs Summaries**: Prefer histograms. They can be aggregated across
instances (summaries cannot), and bucket boundaries can be adjusted retroactively
via queries.

### Data Model

Every time series is uniquely identified by its metric name and label set:

```
metric_name{label1="value1", label2="value2"} value timestamp

# Example:
http_requests_total{method="GET", handler="/api/v1/users", status="200"} 1027 1705312245
```

Labels create dimensions. The metric `http_requests_total` with labels for method,
handler, and status can answer:
- Total requests: `sum(http_requests_total)`
- Requests per endpoint: `sum by (handler) (http_requests_total)`
- Error rate: `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`

**Cardinality warning**: Every unique label combination creates a new time series.
A label with 1000 possible values on a metric with 5 other labels can create
millions of time series. High cardinality kills Prometheus performance.

### PromQL Basics

```promql
# Instant vector: current value of all matching time series
http_requests_total{method="GET"}

# Range vector: values over the last 5 minutes
http_requests_total{method="GET"}[5m]

# Rate: per-second rate of change over 5 minutes (for counters)
rate(http_requests_total[5m])

# Sum by label: aggregate across instances
sum by (handler) (rate(http_requests_total[5m]))

# 99th percentile latency from histogram
histogram_quantile(0.99, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))
```

### Instrumentation

Applications expose metrics via client libraries:

```python
# Python example using prometheus_client
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

ACTIVE_REQUESTS = Gauge(
    'http_active_requests',
    'Number of active HTTP requests'
)

# Use in request handler
@app.route('/api/users')
def get_users():
    ACTIVE_REQUESTS.inc()
    with REQUEST_DURATION.labels(method='GET', endpoint='/api/users').time():
        try:
            result = fetch_users()
            REQUEST_COUNT.labels(method='GET', endpoint='/api/users', status='200').inc()
            return result
        except Exception:
            REQUEST_COUNT.labels(method='GET', endpoint='/api/users', status='500').inc()
            raise
        finally:
            ACTIVE_REQUESTS.dec()

# Start metrics server on port 8000
start_http_server(8000)
```

### Service Discovery

In Kubernetes, Prometheus discovers targets automatically:

```yaml
# prometheus.yml — Kubernetes service discovery
scrape_configs:
  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Only scrape pods with annotation prometheus.io/scrape: "true"
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      # Use annotation for custom metrics port
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        target_label: __address__
        regex: (.+)
        replacement: ${1}:$1
      # Use annotation for custom metrics path
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

Pods opt in to scraping with annotations:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

---

## Step-by-Step Practical

### Install Prometheus and Scrape a Target

**Step 1: Install Prometheus using Helm**

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.retention=15d \
  --set prometheus.prometheusSpec.resources.requests.cpu=500m \
  --set prometheus.prometheusSpec.resources.requests.memory=1Gi
```

**Step 2: Deploy a sample application with metrics**

```yaml
# sample-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sample-app
  namespace: monitoring
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sample-app
  template:
    metadata:
      labels:
        app: sample-app
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
        prometheus.io/path: "/metrics"
    spec:
      containers:
        - name: app
          image: prom/prometheus:latest    # Self-monitoring example
          ports:
            - containerPort: 8080
```

**Step 3: Create a ServiceMonitor (for kube-prometheus-stack)**

```yaml
# servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sample-app
  namespace: monitoring
  labels:
    release: prometheus     # Must match Helm release label
spec:
  selector:
    matchLabels:
      app: sample-app
  endpoints:
    - port: http
      interval: 15s
      path: /metrics
```

**Step 4: Access Prometheus UI**

```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
# Open http://localhost:9090
```

**Step 5: Run PromQL queries**

```promql
# Total scrape targets
up

# Scrape duration
scrape_duration_seconds

# Memory usage of Prometheus itself
process_resident_memory_bytes{job="prometheus"}

# Per-second request rate
rate(prometheus_http_requests_total[5m])
```

Expected output for `up`:

```
up{instance="10.244.0.5:8080", job="sample-app"} 1
up{instance="10.244.0.6:8080", job="sample-app"} 1
up{instance="10.244.0.7:9090", job="prometheus"} 1
```

**Step 6: Verify the Targets page**

Navigate to Status > Targets in the Prometheus UI. You should see your sample-app
endpoints listed with state "UP" and the last scrape timestamp.

---

## Exercises

### Exercise 1: Install and Explore
Install Prometheus on a local cluster and explore the built-in metrics. Find three
metrics that tell you about Prometheus's own performance (hint: look for metrics
starting with `prometheus_` and `process_`).

### Exercise 2: Instrument a Python App
Create a simple Python Flask or FastAPI application with three metrics: a Counter
for requests, a Histogram for latency, and a Gauge for active connections. Deploy it
and verify Prometheus scrapes it.

### Exercise 3: PromQL Practice
Write PromQL queries for:
- The total number of HTTP requests per second across all instances
- The 95th percentile latency for a specific endpoint
- The top 5 endpoints by error rate

### Exercise 4: Cardinality Investigation
Run `prometheus_tsdb_head_series` to see how many time series Prometheus is tracking.
Then look at `topk(10, count by (__name__)({__name__=~".+"}))` to find the metrics
with the most time series. Investigate whether any have excessive cardinality.

---

## Knowledge Check

### Question 1
Why does Prometheus use a pull-based model instead of push?

<details>
<summary>Answer</summary>

Pull-based scraping provides several advantages:
1. **Simpler targets** — Apps just expose an HTTP endpoint; no push client needed.
2. **Centralized control** — Prometheus decides what to scrape and how often.
3. **Health detection** — A failed scrape means the target is down; push silence is
   ambiguous.
4. **Debuggability** — You can `curl` the metrics endpoint to see exactly what
   Prometheus sees.
5. **Service discovery** — Prometheus integrates with Kubernetes SD to find targets
   automatically.

</details>

### Question 2
What are the four Prometheus metric types and when do you use each?

<details>
<summary>Answer</summary>

1. **Counter** — Monotonically increasing. Use for: request counts, error counts,
   bytes sent. Always apply `rate()` to get meaningful values.
2. **Gauge** — Can go up or down. Use for: current memory usage, active connections,
   temperature, queue depth.
3. **Histogram** — Counts observations in buckets. Use for: request latency, response
   sizes. Enables `histogram_quantile()` for percentiles.
4. **Summary** — Calculates quantiles client-side. Similar to histogram but cannot
   be aggregated across instances. Generally, prefer histograms.

</details>

### Question 3
What is cardinality, and why is it dangerous in Prometheus?

<details>
<summary>Answer</summary>

Cardinality is the number of unique time series in Prometheus. Each unique
combination of metric name and label values creates a separate time series. High
cardinality occurs when labels have many possible values (e.g., user_id,
request_id, IP address). A metric with two labels each having 1,000 values creates
up to 1,000,000 time series. This causes: excessive memory usage, slow queries,
increased disk I/O, and can crash Prometheus. Avoid high-cardinality labels —
use logs or traces for per-request data.

</details>

### Question 4
What is the difference between `rate()` and `increase()` in PromQL?

<details>
<summary>Answer</summary>

Both operate on counters over a time range:
- **`rate(counter[5m])`** returns the per-second average rate of increase over the
  last 5 minutes. Result is always per-second.
- **`increase(counter[5m])`** returns the total increase over the last 5 minutes.
  It is equivalent to `rate() * seconds_in_range`.

Use `rate()` for dashboards (shows requests/second). Use `increase()` for totals
("how many errors in the last hour?"). Both handle counter resets automatically.

</details>
