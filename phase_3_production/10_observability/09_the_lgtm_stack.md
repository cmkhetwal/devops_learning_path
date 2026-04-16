# Lesson 09: The LGTM Stack

## Why This Matters in DevOps

Individual observability tools are powerful. Prometheus collects metrics. Loki
aggregates logs. Tempo stores traces. Grafana visualizes them. But the real value
emerges when these tools work together as an integrated stack — when clicking a spike
on a metric graph takes you to the relevant traces, and clicking a trace takes you
to the exact log lines for that request.

The LGTM stack (Loki, Grafana, Tempo, Mimir) is Grafana Labs' answer to the
"full-stack observability" challenge. It is fully open source, scales horizontally,
and provides the correlations between metrics, logs, and traces that make debugging
distributed systems tractable.

Understanding how to deploy and integrate the LGTM stack is a critical skill for
any DevOps engineer building a modern observability platform. It competes directly
with commercial solutions like Datadog and New Relic, at a fraction of the cost.

---

## Core Concepts

### What Is the LGTM Stack?

```
L - Loki     (Logs)      - Index-free log aggregation
G - Grafana  (Viz)       - Unified visualization and exploration
T - Tempo    (Traces)    - Distributed tracing backend
M - Mimir    (Metrics)   - Horizontally scalable Prometheus
```

Each component handles one signal type, and Grafana ties them together:

```
+------------------------------------------------------------------+
|                        The LGTM Stack                             |
+------------------------------------------------------------------+
|                                                                    |
|  Applications (instrumented with OpenTelemetry)                   |
|       |                |                |                          |
|    metrics          traces            logs                        |
|       |                |                |                          |
|       v                v                v                          |
|  +---------+     +---------+     +---------+                      |
|  |  Mimir  |     |  Tempo  |     |  Loki   |                      |
|  | (metrics)|    | (traces)|     | (logs)  |                      |
|  +---------+     +---------+     +---------+                      |
|       |                |                |                          |
|       +--------+-------+-------+--------+                         |
|                |                                                   |
|           +---------+                                              |
|           | Grafana |                                              |
|           +---------+                                              |
|                                                                    |
+------------------------------------------------------------------+
```

### How They Fit Together

#### Mimir: Prometheus at Scale

Grafana Mimir is a horizontally scalable, multi-tenant, long-term storage for
Prometheus metrics. It is wire-compatible with Prometheus: you can use PromQL,
Prometheus remote write, and Prometheus recording/alerting rules.

Why Mimir over standalone Prometheus?
- **Horizontal scaling**: Prometheus is single-node; Mimir distributes across many
  nodes.
- **Long-term storage**: Object storage (S3/GCS) instead of local disk.
- **Multi-tenancy**: Isolate teams or environments with tenant headers.
- **Global view**: Query metrics across all Prometheus instances.

```yaml
# Prometheus remote write to Mimir
remote_write:
  - url: http://mimir:9009/api/v1/push
    headers:
      X-Scope-OrgID: production
```

#### Tempo: Trace Storage

Tempo stores traces in object storage with no indexing — it only needs the Trace
ID to retrieve a trace. This makes it extremely cost-effective.

Integration with Grafana enables:
- **TraceQL**: A query language for finding traces by attributes.
- **Service graph**: Auto-generated service dependency map from traces.
- **Span metrics**: Automatic generation of RED metrics from trace data.

```
TraceQL examples:
  { resource.service.name = "payment-service" && status = error }
  { span.http.status_code >= 500 }
  { duration > 2s && resource.service.name = "api-gateway" }
```

#### Loki: Log Aggregation

Loki stores logs indexed only by labels. It integrates with Grafana for log
exploration with LogQL.

#### Grafana: The Glue

Grafana provides the unified interface and the correlations:

```
Metric spike detected
    │
    ├── Click exemplar on metric panel
    │       │
    │       └── Opens trace in Tempo
    │               │
    │               └── See slow span in payment-service
    │                       │
    │                       └── Click "Logs for this span"
    │                               │
    │                               └── Opens Loki logs filtered by
    │                                   trace_id and time range
    │
    └── Click "Show logs" on metric panel
            │
            └── Opens Loki logs for same service and time range
```

### Deploying the LGTM Stack on Kubernetes

#### Option 1: Grafana Helm Charts (Production)

```bash
# Add Grafana Helm repo
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Mimir (distributed mode)
helm install mimir grafana/mimir-distributed \
  --namespace monitoring \
  --create-namespace \
  --values - <<EOF
mimir:
  structuredConfig:
    common:
      storage:
        backend: s3
        s3:
          endpoint: s3.amazonaws.com
          region: us-east-1
          bucket_name: mimir-data
    limits:
      max_global_series_per_user: 1000000
minio:
  enabled: false
EOF

# Install Tempo (distributed mode)
helm install tempo grafana/tempo-distributed \
  --namespace monitoring \
  --values - <<EOF
storage:
  trace:
    backend: s3
    s3:
      bucket: tempo-traces
      endpoint: s3.amazonaws.com
      region: us-east-1
global_overrides:
  max_traces_per_user: 100000
EOF

# Install Loki (simple scalable mode)
helm install loki grafana/loki \
  --namespace monitoring \
  --values - <<EOF
loki:
  storage:
    type: s3
    s3:
      endpoint: s3.amazonaws.com
      region: us-east-1
      bucketnames: loki-data
  limits_config:
    retention_period: 30d
deploymentMode: SimpleScalable
EOF

# Install Grafana
helm install grafana grafana/grafana \
  --namespace monitoring \
  --values - <<EOF
datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
      - name: Mimir
        type: prometheus
        url: http://mimir-query-frontend:8080/prometheus
        isDefault: true
        jsonData:
          exemplarTraceIdDestinations:
            - name: traceID
              datasourceUid: tempo
      - name: Tempo
        type: tempo
        uid: tempo
        url: http://tempo-query-frontend:3200
        jsonData:
          tracesToLogs:
            datasourceUid: loki
            tags: ['service.name']
            mappedTags: [{ key: 'service.name', value: 'app' }]
            filterByTraceID: true
          tracesToMetrics:
            datasourceUid: mimir
            tags: ['service.name']
          serviceMap:
            datasourceUid: mimir
      - name: Loki
        type: loki
        uid: loki
        url: http://loki-read:3100
        jsonData:
          derivedFields:
            - name: TraceID
              matcherRegex: '"trace_id":"(\w+)"'
              url: '$${__value.raw}'
              datasourceUid: tempo
EOF
```

#### Option 2: Docker Compose (Development / Learning)

```yaml
# docker-compose.yaml
version: "3.8"

services:
  mimir:
    image: grafana/mimir:latest
    command: ["-config.file=/etc/mimir/config.yaml"]
    ports: ["9009:9009"]
    volumes:
      - ./mimir-config.yaml:/etc/mimir/config.yaml
      - mimir-data:/data

  tempo:
    image: grafana/tempo:latest
    command: ["-config.file=/etc/tempo/config.yaml"]
    ports: ["3200:3200", "4317:4317"]
    volumes:
      - ./tempo-config.yaml:/etc/tempo/config.yaml
      - tempo-data:/var/tempo

  loki:
    image: grafana/loki:latest
    command: ["-config.file=/etc/loki/config.yaml"]
    ports: ["3100:3100"]
    volumes:
      - ./loki-config.yaml:/etc/loki/config.yaml
      - loki-data:/loki

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    volumes:
      - ./grafana-datasources.yaml:/etc/grafana/provisioning/datasources/ds.yaml
      - grafana-data:/var/lib/grafana

  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    command: ["--config=/etc/otel/config.yaml"]
    ports: ["4317:4317", "4318:4318"]
    volumes:
      - ./otel-config.yaml:/etc/otel/config.yaml

volumes:
  mimir-data:
  tempo-data:
  loki-data:
  grafana-data:
```

### Correlating Metrics, Logs, and Traces in Grafana

The correlation workflow in practice:

**Scenario**: Users report slow checkout.

**Step 1**: Open the SRE dashboard. The P99 latency for `checkout-service` has
spiked from 200ms to 2s.

**Step 2**: Click the exemplar dot at the spike. Grafana opens the trace in Tempo:

```
Trace: 9f2e1d3c4b5a6789 (2,134ms)
├── api-gateway: /checkout (2,134ms)
│   ├── auth-service: validateToken (15ms)
│   ├── cart-service: getCart (45ms)
│   └── payment-service: processPayment (2,050ms)  <-- BOTTLENECK
│       ├── payment-service: validateCard (12ms)
│       └── payment-service: chargeGateway (2,030ms) <-- ROOT CAUSE
│           └── attribute: gateway.retry_count = 3
```

**Step 3**: Click "Logs for this span" on the `chargeGateway` span. Grafana opens
Loki filtered by trace_id and time range:

```
2024-01-15 10:23:45.123 WARN  payment-service trace_id=9f2e1d3c4b5a6789
  Gateway connection timeout, retrying (attempt 1/3)
2024-01-15 10:23:46.234 WARN  payment-service trace_id=9f2e1d3c4b5a6789
  Gateway connection timeout, retrying (attempt 2/3)
2024-01-15 10:23:47.345 WARN  payment-service trace_id=9f2e1d3c4b5a6789
  Gateway connection timeout, retrying (attempt 3/3)
2024-01-15 10:23:47.456 INFO  payment-service trace_id=9f2e1d3c4b5a6789
  Gateway responded after 3 retries, latency=2030ms
```

**Root cause identified**: The payment gateway had intermittent connection timeouts
causing retries.

---

## Step-by-Step Practical

### Unified Observability for a Sample Microservices App

**Step 1: Deploy the LGTM stack (using Docker Compose)**

```bash
mkdir lgtm-demo && cd lgtm-demo

# Create minimal configs (see Docker Compose section above)
# Then start the stack:
docker compose up -d
```

**Step 2: Configure the OTel Collector to fan out signals**

```yaml
# otel-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:
    timeout: 5s
    send_batch_size: 500

exporters:
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true
  prometheusremotewrite:
    endpoint: http://mimir:9009/api/v1/push
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [loki]
```

**Step 3: Deploy a sample multi-service application**

Use the three services from Lesson 08 (api-gateway, order-service, payment-service),
all configured to send telemetry to the OTel Collector.

**Step 4: Generate load and verify all signals**

```bash
# Generate traffic
for i in $(seq 1 200); do
  curl -s http://localhost:8081/checkout > /dev/null
  sleep 0.1
done
```

**Step 5: Verify in Grafana (http://localhost:3000)**

Check each data source:

```
Explore > Mimir:
  Query: rate(http_server_duration_count[5m])
  Expected: Metrics from all three services

Explore > Tempo:
  Search: service.name = "api-gateway"
  Expected: Traces showing the full checkout flow

Explore > Loki:
  Query: {service_name="payment-service"}
  Expected: Log lines from the payment service
```

**Step 6: Test correlation**

1. In a Mimir time series panel, enable exemplars.
2. Click an exemplar dot to jump to Tempo.
3. In the trace view, click "Logs for this span" to jump to Loki.
4. Verify the round-trip: metric -> trace -> log -> back to metric.

**Step 7: Build a unified dashboard**

Create a dashboard with three rows:

```
Row 1: Metrics (Mimir)
  - Request rate per service
  - Error rate per service
  - P99 latency per service

Row 2: Traces (Tempo)
  - Service graph (auto-generated)
  - Recent traces table

Row 3: Logs (Loki)
  - Recent error logs
  - Log volume per service
```

---

## Exercises

### Exercise 1: Deploy the LGTM Stack
Deploy all four components (Loki, Grafana, Tempo, Mimir) on either Docker Compose
or Kubernetes. Configure the OTel Collector to route all three signals to the
correct backends. Verify by querying each data source in Grafana.

### Exercise 2: End-to-End Correlation
Instrument an application with OpenTelemetry (traces, metrics, and structured logs
with trace IDs). In Grafana, configure all three data sources with correlation
links. Demonstrate navigating from a metric anomaly to a specific trace to the
relevant log lines.

### Exercise 3: Service Graph
Deploy at least three interconnected services. Generate traffic and use Tempo's
service graph feature to visualize the dependency map. Compare the auto-generated
graph with your actual architecture.

### Exercise 4: Unified Alert
Create an alert that fires based on metrics (high error rate) and includes a link
to the relevant Loki log query and Tempo trace search in the alert annotation.
Verify the links work when the alert fires.

### Exercise 5: Cost Estimation
Calculate the expected monthly storage cost for your LGTM stack based on: metrics
ingestion rate, log volume, trace volume, and retention periods. Compare with a
commercial alternative (Datadog or New Relic) for the same data volume.

---

## Knowledge Check

### Question 1
What does each letter in LGTM stand for, and what signal type does each handle?

<details>
<summary>Answer</summary>

- **L** — **Loki**: Handles **logs**. Index-free log aggregation with LogQL.
- **G** — **Grafana**: Handles **visualization**. Unified UI for all signals.
- **T** — **Tempo**: Handles **traces**. Distributed tracing backend with TraceQL.
- **M** — **Mimir**: Handles **metrics**. Horizontally scalable, Prometheus-
  compatible time series database.

</details>

### Question 2
How does Grafana enable correlation between metrics, logs, and traces?

<details>
<summary>Answer</summary>

Grafana uses data source configuration to link signals:

1. **Metrics to traces** (exemplars): The Prometheus/Mimir data source is configured
   with `exemplarTraceIdDestinations` pointing to Tempo. Exemplar dots on metric
   panels link to specific traces.

2. **Traces to logs**: The Tempo data source is configured with `tracesToLogs`
   pointing to Loki. Clicking a span shows related log lines filtered by trace ID.

3. **Logs to traces**: The Loki data source is configured with `derivedFields`
   that extract trace IDs from log content and link to Tempo.

4. **Traces to metrics**: The Tempo data source is configured with
   `tracesToMetrics` pointing to Mimir, showing related metrics for a traced
   service.

</details>

### Question 3
Why use Mimir instead of standalone Prometheus?

<details>
<summary>Answer</summary>

Standalone Prometheus has limitations that Mimir solves:
1. **Single-node**: Prometheus cannot scale horizontally. Mimir distributes across
   many nodes.
2. **Local storage**: Prometheus stores data on local disk with limited retention.
   Mimir uses object storage (S3/GCS) for long-term, durable storage.
3. **No multi-tenancy**: Prometheus serves one tenant. Mimir supports multiple
   tenants with isolation.
4. **No global view**: With multiple Prometheus instances, you cannot query across
   all of them natively. Mimir provides a unified query endpoint.

Mimir is wire-compatible with Prometheus — same PromQL, same remote write, same
alerting rules — so migration is straightforward.

</details>

### Question 4
What is the typical debugging workflow using the LGTM stack?

<details>
<summary>Answer</summary>

1. **Alert fires** based on a metric threshold (e.g., high error rate).
2. **View the dashboard** in Grafana showing the metric anomaly over time.
3. **Click an exemplar** on the metric panel to open the specific trace in Tempo.
4. **Analyze the trace** to identify which service/span is slow or erroring.
5. **Click "Logs for this span"** to open Loki filtered by trace ID and time range.
6. **Read the logs** to understand the root cause (error messages, stack traces).
7. **Fix the issue** and verify metrics return to normal.

This workflow reduces mean time to resolution (MTTR) by providing a clear path from
symptom (metric) to cause (log line) through context (trace).

</details>
