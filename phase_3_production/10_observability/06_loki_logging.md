# Lesson 06: Loki Logging

## Why This Matters in DevOps

Logs are the most familiar observability signal — developers have been writing
`print()` statements since the dawn of computing. But in a distributed system with
hundreds of containers producing gigabytes of logs per hour, the challenge is not
generating logs but *aggregating, indexing, querying, and retaining them
cost-effectively*.

Traditional log systems like Elasticsearch (ELK stack) index the full content of
every log line, which is powerful but extremely expensive at scale. Grafana Loki
takes a radically different approach: it indexes only the labels (metadata) and
stores log content as compressed chunks, much like Prometheus indexes labels but
not metric values. This makes Loki 10-100x cheaper to operate than Elasticsearch
for many workloads.

If you run Kubernetes in production, you will need centralized logging. Loki is
the cloud-native answer.

---

## Core Concepts

### What Is Loki?

Loki is a horizontally scalable, multi-tenant log aggregation system designed by
Grafana Labs. Its tagline: "like Prometheus, but for logs."

Key design decisions:
- **Label-based indexing only**: Loki does not index log content. It indexes labels
  (like `{namespace="production", pod="api-abc123"}`). Searching within log content
  is done via grep-style filters at query time.
- **Chunks**: Log lines with the same label set are batched into compressed chunks
  stored in object storage (S3, GCS, MinIO).
- **Cost efficiency**: By not indexing content, Loki uses far less CPU and memory
  than full-text search engines.

### Architecture

```
+------------------------------------------------------------------+
|                         Loki Architecture                         |
+------------------------------------------------------------------+
|                                                                    |
|  +------------------+          +-------------------+               |
|  | Promtail/Agents  |  push   |    Distributor     |              |
|  | (log collectors) | ------> | (validates, routes) |             |
|  +------------------+          +-------------------+               |
|                                        |                           |
|                                        v                           |
|                               +-------------------+                |
|                               |     Ingester      |                |
|                               | (builds chunks,   |                |
|                               |  writes to WAL)   |                |
|                               +-------------------+                |
|                                   |          |                     |
|                              flush|          |query                |
|                                   v          v                     |
|                         +-----------+  +-----------+               |
|                         |  Object   |  |  Querier  |               |
|                         |  Storage  |  | (executes |               |
|                         | (S3/GCS)  |  |  LogQL)   |               |
|                         +-----------+  +-----------+               |
|                                             |                      |
|                                             v                      |
|                                       +-----------+                |
|                                       |  Grafana  |                |
|                                       +-----------+                |
+------------------------------------------------------------------+
```

**Distributor**: Receives log entries from agents, validates them, and distributes
to ingesters based on consistent hashing of the label set.

**Ingester**: Accumulates log entries in memory, builds compressed chunks, and
periodically flushes them to object storage. Uses a Write-Ahead Log (WAL) for
durability.

**Querier**: Executes LogQL queries against both ingesters (recent data) and object
storage (historical data).

**Query Frontend** (not shown): Optional caching and query-splitting layer for
performance.

### LogQL Query Language

LogQL has two types of queries:

#### Log Queries (return log lines)

```logql
# Stream selector (required — selects by labels)
{namespace="production", app="payment-service"}

# Pipeline stages (filter, parse, format)
{namespace="production", app="payment-service"}
  |= "error"                           # Contains "error"
  != "health check"                    # Does not contain "health check"
  |~ "timeout|connection refused"      # Regex match
  !~ "DEBUG|TRACE"                     # Regex exclude

# JSON parsing
{app="payment-service"} | json
  | level="error"
  | amount > 100

# Logfmt parsing
{app="api-gateway"} | logfmt
  | status >= 500
  | duration > 1s

# Pattern matching
{app="nginx"} | pattern `<ip> - - [<_>] "<method> <uri> <_>" <status> <size>`
  | status >= 500

# Line formatting
{app="payment-service"} | json
  | line_format "{{.level}} | {{.message}} | customer={{.customer_id}}"
```

#### Metric Queries (return numeric values from logs)

```logql
# Count error logs per second
rate({app="payment-service"} |= "error" [5m])

# Count log lines per level
sum by (level) (count_over_time({app="payment-service"} | json [5m]))

# Average extracted value from logs
avg_over_time({app="payment-service"} | json | unwrap response_time [5m])

# Bytes rate (data volume)
bytes_rate({namespace="production"}[5m])

# Quantile of extracted values
quantile_over_time(0.99, {app="api"} | json | unwrap duration [5m])
```

### Labels vs Content

```
HIGH-CARDINALITY LABELS (AVOID):
  {user_id="12345"}              # Millions of unique values
  {request_id="abc-def-123"}     # Unique per request
  {ip="192.168.1.1"}             # Thousands of values

GOOD LABELS:
  {namespace="production"}       # ~5 values
  {app="payment-service"}        # ~50 values
  {level="error"}                # 4-5 values
  {cluster="us-east-1"}          # ~10 values
```

**Rule of thumb**: If a label has more than a few hundred unique values, it should
be log content, not a label. Loki creates a new stream for each unique label set,
and too many streams kills performance.

### Promtail Agent

Promtail is the default log collector for Loki. It runs as a DaemonSet on each
Kubernetes node, discovers pod logs via the Kubernetes API, and ships them to Loki.

```yaml
# promtail-config.yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: kubernetes-pods
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      # Use pod labels as Loki labels
      - source_labels: [__meta_kubernetes_pod_label_app]
        target_label: app
      - source_labels: [__meta_kubernetes_namespace]
        target_label: namespace
      - source_labels: [__meta_kubernetes_pod_name]
        target_label: pod
      - source_labels: [__meta_kubernetes_pod_container_name]
        target_label: container
    pipeline_stages:
      # Parse JSON logs
      - json:
          expressions:
            level: level
            message: message
            trace_id: trace_id
      # Set level as a label
      - labels:
          level:
      # Add trace_id for correlation
      - labels:
          trace_id:
      # Drop debug logs in production (reduce volume)
      - match:
          selector: '{level="debug"}'
          action: drop
```

### Installing Loki + Promtail

```bash
# Add Grafana Helm repo
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install Loki (single binary mode for dev/small prod)
helm install loki grafana/loki \
  --namespace monitoring \
  --set loki.auth_enabled=false \
  --set loki.storage.type=filesystem \
  --set singleBinary.replicas=1 \
  --set monitoring.selfMonitoring.enabled=false

# Install Promtail
helm install promtail grafana/promtail \
  --namespace monitoring \
  --set config.clients[0].url=http://loki:3100/loki/api/v1/push

# For production with object storage:
helm install loki grafana/loki \
  --namespace monitoring \
  --values - <<EOF
loki:
  auth_enabled: true
  storage:
    type: s3
    s3:
      endpoint: s3.amazonaws.com
      region: us-east-1
      bucketnames: loki-chunks
      access_key_id: ${AWS_ACCESS_KEY_ID}
      secret_access_key: ${AWS_SECRET_ACCESS_KEY}
  limits_config:
    retention_period: 30d
    max_query_series: 500
    max_entries_limit_per_query: 5000
EOF
```

---

## Step-by-Step Practical

### Set Up Centralized Logging for a Kubernetes Cluster

**Step 1: Install the Loki stack**

```bash
helm install loki-stack grafana/loki-stack \
  --namespace monitoring \
  --create-namespace \
  --set loki.isDefault=true \
  --set promtail.enabled=true \
  --set grafana.enabled=false    # Use existing Grafana
```

**Step 2: Configure Grafana data source**

```yaml
# Add Loki data source to Grafana
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-loki-datasource
  namespace: monitoring
  labels:
    grafana_datasource: "1"
data:
  loki-datasource.yaml: |
    apiVersion: 1
    datasources:
      - name: Loki
        type: loki
        url: http://loki:3100
        access: proxy
        isDefault: false
        jsonData:
          maxLines: 1000
```

**Step 3: Deploy a sample application that generates logs**

```yaml
# sample-logger.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: log-generator
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: log-generator
  template:
    metadata:
      labels:
        app: log-generator
    spec:
      containers:
        - name: logger
          image: mingrammer/flog:0.4.3
          args:
            - --format=json
            - --loop
            - --delay=100ms
            - --number=1
          resources:
            requests:
              cpu: 10m
              memory: 16Mi
```

```bash
kubectl apply -f sample-logger.yaml
```

**Step 4: Query logs in Grafana**

Open Grafana > Explore > Select Loki data source.

```logql
# All logs from the log generator
{app="log-generator"}

# Filter for specific status codes
{app="log-generator"} | json | status >= 400

# Count requests per status code over time
sum by (status) (count_over_time({app="log-generator"} | json [1m]))

# Show only error-level logs from all apps
{namespace="monitoring"} | json | level="error"

# Search for a specific trace ID
{namespace="production"} |= "trace_id=abc123def456"
```

**Step 5: Query and filter logs via LogCLI (command-line)**

```bash
# Install LogCLI
curl -O -L "https://github.com/grafana/loki/releases/latest/download/logcli-linux-amd64.zip"
unzip logcli-linux-amd64.zip
chmod +x logcli-linux-amd64
sudo mv logcli-linux-amd64 /usr/local/bin/logcli

# Set the Loki URL
export LOKI_ADDR=http://localhost:3100

# Query logs
logcli query '{app="log-generator"}' --limit=10

# Tail logs in real-time
logcli query '{app="log-generator"}' --tail

# Query with time range
logcli query '{app="payment-service"} |= "error"' \
  --from="2024-01-15T00:00:00Z" \
  --to="2024-01-15T12:00:00Z"

# Get label values
logcli labels app
```

**Step 6: Verify log volume and storage**

```logql
# Log volume per app (bytes per second)
sum by (app) (bytes_rate({namespace="monitoring"}[5m]))

# Log line rate per namespace
sum by (namespace) (rate({namespace=~".+"}[5m]))
```

---

## Exercises

### Exercise 1: Install and Query
Install Loki and Promtail on a local Kubernetes cluster. Deploy a sample application
and write LogQL queries to find: (a) all error logs, (b) logs containing a specific
keyword, (c) the rate of error logs over time.

### Exercise 2: Structured Logging
Deploy an application that outputs JSON-formatted logs. Use LogQL's JSON parser to
filter by structured fields (e.g., `| json | status >= 500 | duration > 1s`).

### Exercise 3: Log-Based Metrics
Create a Grafana dashboard panel that shows metrics derived from logs: error rate
from log lines, p99 response time extracted from log fields, and log volume per
service.

### Exercise 4: Label Design
Audit the labels on your Loki streams. Identify any high-cardinality labels that
are creating too many streams. Redesign the labeling strategy to keep cardinality
under control.

### Exercise 5: Log Retention Policy
Configure Loki with a 30-day retention policy. Calculate the expected storage cost
based on your current log volume rate. Compare this with your current logging
solution's cost.

---

## Knowledge Check

### Question 1
How does Loki's indexing strategy differ from Elasticsearch?

<details>
<summary>Answer</summary>

**Elasticsearch** indexes the full content of every log line, creating an inverted
index that enables fast full-text search. This is powerful but expensive in CPU,
memory, and storage.

**Loki** indexes only the labels (metadata like namespace, pod, app) and stores log
content as compressed chunks. Searching within log content is done via brute-force
filtering (like grep) at query time. This makes Loki much cheaper to operate but
slower for full-text searches across large time ranges.

The trade-off: Loki is 10-100x cheaper but requires you to narrow results by labels
first, then filter content.

</details>

### Question 2
What is the danger of high-cardinality labels in Loki?

<details>
<summary>Answer</summary>

Each unique combination of labels creates a separate "stream" in Loki. High-
cardinality labels (like user_id, request_id, or IP address) can create millions of
streams. This causes: excessive memory usage in ingesters, slow index lookups,
increased storage overhead, and potentially crashing the Loki cluster. Keep label
cardinality low (tens to hundreds of unique values per label). Use log content (not
labels) for high-cardinality data.

</details>

### Question 3
What is the difference between log queries and metric queries in LogQL?

<details>
<summary>Answer</summary>

**Log queries** return log lines. They start with a stream selector and optionally
include pipeline stages (filters, parsers, formatters):
`{app="api"} |= "error" | json | status >= 500`

**Metric queries** return numeric values computed from logs. They wrap log queries
in aggregation functions:
`rate({app="api"} |= "error" [5m])` — returns errors per second.
`count_over_time({app="api"} | json | status >= 500 [1h])` — counts matching lines.

Metric queries are used in dashboards and alerts. Log queries are used for
investigation and debugging.

</details>

### Question 4
What role does Promtail play in the Loki ecosystem?

<details>
<summary>Answer</summary>

Promtail is the log collection agent that runs on each Kubernetes node (as a
DaemonSet). It:
1. **Discovers** pod logs via the Kubernetes API.
2. **Reads** log files from the node filesystem (`/var/log/pods/`).
3. **Labels** log streams with metadata (namespace, pod name, container name).
4. **Processes** log lines through pipeline stages (parsing, filtering, relabeling).
5. **Pushes** batched, compressed log entries to the Loki distributor.

Alternatives to Promtail include Grafana Alloy (the successor agent), Fluentd, and
Fluent Bit with Loki output plugins.

</details>
