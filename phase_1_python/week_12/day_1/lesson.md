# Week 12, Day 1: Prometheus Client for Python

## What You'll Learn

- Prometheus metrics types: Counter, Gauge, Histogram, Summary
- Using the `prometheus_client` Python library
- Exposing metrics endpoints for monitoring
- Building custom DevOps metrics

## Why This Matters for DevOps

Monitoring is the eyes and ears of DevOps. Prometheus is the industry
standard for metrics collection, and its Python client library lets
you instrument any application with custom metrics. Understanding
metrics is essential for SRE, on-call, and capacity planning.

---

## 1. Installing prometheus_client

```bash
pip install prometheus_client
```

## 2. Metric Types

### Counter
A value that only goes up (e.g., total requests, errors):

```python
from prometheus_client import Counter

request_count = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

# Increment
request_count.labels(method="GET", endpoint="/api/users", status="200").inc()
request_count.labels(method="POST", endpoint="/api/users", status="201").inc()
request_count.labels(method="GET", endpoint="/api/users", status="500").inc()
```

### Gauge
A value that can go up or down (e.g., CPU usage, active connections):

```python
from prometheus_client import Gauge

active_connections = Gauge(
    "active_connections",
    "Number of active connections"
)

active_connections.set(42)
active_connections.inc()    # +1
active_connections.dec(5)   # -5
```

### Histogram
Observes values and counts them in configurable buckets:

```python
from prometheus_client import Histogram

request_duration = Histogram(
    "http_request_duration_seconds",
    "Request duration in seconds",
    ["endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# Observe a value
request_duration.labels(endpoint="/api/users").observe(0.15)

# Or use as a timer
with request_duration.labels(endpoint="/api/data").time():
    # ... do work ...
    pass
```

### Summary
Similar to Histogram but calculates quantiles client-side:

```python
from prometheus_client import Summary

request_latency = Summary(
    "request_processing_seconds",
    "Time spent processing request"
)

request_latency.observe(0.5)
```

## 3. Exposing Metrics via HTTP

```python
from prometheus_client import start_http_server, Counter, Gauge
import time

# Define metrics
requests = Counter("app_requests_total", "Total app requests")
temperature = Gauge("app_temperature_celsius", "Current temperature")

# Start metrics server on port 8000
start_http_server(8000)

# Your application logic
while True:
    requests.inc()
    temperature.set(22.5)
    time.sleep(1)
```

Visit `http://localhost:8000/metrics` to see Prometheus text format.

## 4. Custom Collectors

```python
from prometheus_client import Gauge
import psutil

cpu_usage = Gauge("system_cpu_percent", "System CPU usage percentage")
memory_usage = Gauge("system_memory_percent", "System memory usage percentage")
disk_usage = Gauge("system_disk_percent", "System disk usage percentage")

def collect_system_metrics():
    cpu_usage.set(psutil.cpu_percent())
    memory_usage.set(psutil.virtual_memory().percent)
    disk_usage.set(psutil.disk_usage("/").percent)
```

## 5. Labels for Dimensional Data

```python
deployment_status = Counter(
    "deployments_total",
    "Total deployments",
    ["environment", "app", "result"]
)

# Track deployments
deployment_status.labels(
    environment="production",
    app="web-api",
    result="success"
).inc()

deployment_status.labels(
    environment="staging",
    app="web-api",
    result="failure"
).inc()
```

## 6. Metric Naming Conventions

| Convention | Example |
|------------|---------|
| Use snake_case | `http_requests_total` |
| Include unit as suffix | `_seconds`, `_bytes`, `_total` |
| Counters end in `_total` | `errors_total` |
| Use base units | seconds (not ms), bytes (not KB) |

## 7. Prometheus Query Language (PromQL) Basics

```
# Rate of requests per second over 5 minutes
rate(http_requests_total[5m])

# 95th percentile latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Current gauge value
system_cpu_percent
```

## DevOps Connection

Prometheus monitoring enables:
- **SLO/SLA tracking**: Measure uptime, latency, error rates
- **Alerting**: Alert on threshold breaches via AlertManager
- **Capacity planning**: Track resource trends over time
- **Incident response**: Dashboards for debugging production issues
- **Auto-scaling**: Scale based on custom metrics

---

## Key Takeaways

| Type | Use Case | Operations |
|------|----------|------------|
| Counter | Requests, errors | `inc()` only |
| Gauge | CPU, connections | `set()`, `inc()`, `dec()` |
| Histogram | Latency, sizes | `observe()`, buckets |
| Summary | Latency quantiles | `observe()` |
