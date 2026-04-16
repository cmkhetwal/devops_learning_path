# Lesson 07: OpenTelemetry

## Why This Matters in DevOps

For years, the observability ecosystem was fragmented. You instrumented your code
with Prometheus client libraries for metrics, a Jaeger SDK for traces, and a
separate logging framework for logs. Switching vendors meant re-instrumenting
everything. Each signal was a silo with its own API, SDK, and wire format.

OpenTelemetry (OTel) ended this fragmentation. Born from the merger of OpenTracing
and OpenCensus in 2019, OTel is now the second-most-active CNCF project after
Kubernetes. It provides a single, vendor-neutral standard for generating, collecting,
and exporting telemetry data — metrics, logs, and traces — from any application.

Over 95% of organizations adopting new observability tooling choose OTel-compatible
solutions. It is the standard. Not learning it means being locked into vendor-
specific instrumentation that will eventually be replaced.

---

## Core Concepts

### What Is OpenTelemetry?

OpenTelemetry is a collection of APIs, SDKs, and tools for instrumenting,
generating, collecting, and exporting telemetry data. It is NOT a backend — it does
not store or visualize data. It is the plumbing that connects your applications to
your observability backends.

```
Your Application                  OTel Collector              Backends
+---------------+                +---------------+         +-----------+
| OTel API      | -- traces -->  | Receivers     | ------> | Tempo     |
| OTel SDK      | -- metrics --> | Processors    | ------> | Mimir     |
| Auto-instrumentation           | Exporters     | ------> | Loki      |
+---------------+                +---------------+         +-----------+
                                                           | Jaeger    |
                                                           | Datadog   |
                                                           | New Relic |
                                                           +-----------+
```

### The Merger: OpenTracing + OpenCensus

- **OpenTracing** (2016): A vendor-neutral API for distributed tracing.
  Problem: API-only, no implementation, no metrics.
- **OpenCensus** (2018): Google's project providing both traces and metrics with
  implementations. Problem: Competing standard with OpenTracing.
- **OpenTelemetry** (2019): Merged both projects into one unified standard covering
  traces, metrics, and logs with both API and SDK.

### OTel Architecture

```
+------------------------------------------------------------------+
|                    OpenTelemetry Architecture                      |
+------------------------------------------------------------------+
|                                                                    |
|  APPLICATION SIDE                                                  |
|  +-----------+  +-----------+  +-------------------+               |
|  | OTel API  |  | OTel SDK  |  | Auto-Instrument.  |              |
|  | (stable   |  | (implements| | (zero-code        |              |
|  |  interfaces| |  the API)  | |  instrumentation)  |             |
|  +-----------+  +-----------+  +-------------------+               |
|                       |                                            |
|                       v                                            |
|              +------------------+                                  |
|              | OTLP Exporter    |                                  |
|              | (sends to        |                                  |
|              |  collector/backend)                                 |
|              +------------------+                                  |
|                       |                                            |
|  INFRASTRUCTURE SIDE  |                                            |
|                       v                                            |
|              +------------------+                                  |
|              | OTel Collector   |                                  |
|              | +- Receivers -+  |                                  |
|              | +- Processors +  |                                  |
|              | +- Exporters -+  |                                  |
|              +------------------+                                  |
|                    |   |   |                                       |
|                    v   v   v                                       |
|              [Tempo] [Mimir] [Loki]                                |
+------------------------------------------------------------------+
```

#### API

The API defines the interfaces for creating traces, metrics, and logs. It is stable,
safe to depend on, and never contains implementation logic. Libraries use the API
to instrument their code without importing any specific SDK.

#### SDK

The SDK implements the API. It handles sampling, batching, exporting, and context
propagation. Application developers configure the SDK at startup:

```python
# Python SDK configuration
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Configure the resource (identifies your service)
resource = Resource.create({
    "service.name": "payment-service",
    "service.version": "3.2.1",
    "deployment.environment": "production",
})

# Configure trace provider
provider = TracerProvider(resource=resource)
processor = BatchSpanProcessor(OTLPSpanExporter(
    endpoint="http://otel-collector:4317",
    insecure=True,
))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
```

#### Collector

The Collector is a vendor-agnostic proxy that receives, processes, and exports
telemetry data. It is the recommended deployment pattern because it decouples
applications from backends.

### Instrumentation Approaches

#### Automatic Instrumentation (Zero-Code)

OTel provides auto-instrumentation agents that patch common libraries at runtime:

```bash
# Python: install the auto-instrumentation package
pip install opentelemetry-distro opentelemetry-exporter-otlp
opentelemetry-bootstrap -a install

# Run your app with auto-instrumentation
opentelemetry-instrument \
  --service_name payment-service \
  --exporter_otlp_endpoint http://otel-collector:4317 \
  --exporter_otlp_protocol grpc \
  python app.py
```

Auto-instrumentation automatically traces:
- HTTP requests (requests, urllib3, aiohttp)
- Database queries (psycopg2, SQLAlchemy, pymongo)
- gRPC calls
- Redis commands
- Message queue operations (Celery, Kafka)
- Flask/Django/FastAPI endpoints

#### Manual Instrumentation

For custom business logic that auto-instrumentation cannot capture:

```python
from opentelemetry import trace

tracer = trace.get_tracer("payment.processor")

def process_payment(order_id: str, amount: float):
    with tracer.start_as_current_span("process_payment") as span:
        # Add attributes (key-value metadata)
        span.set_attribute("order.id", order_id)
        span.set_attribute("payment.amount", amount)
        span.set_attribute("payment.currency", "USD")

        try:
            # Validate payment
            with tracer.start_as_current_span("validate_payment"):
                validate(order_id, amount)

            # Charge customer
            with tracer.start_as_current_span("charge_customer") as charge_span:
                result = gateway.charge(amount)
                charge_span.set_attribute("gateway.transaction_id", result.txn_id)

            span.set_attribute("payment.status", "success")
            return result

        except PaymentError as e:
            span.set_status(trace.StatusCode.ERROR, str(e))
            span.record_exception(e)
            raise
```

### Exporters

Exporters send telemetry to backends. The most common wire protocol is OTLP
(OpenTelemetry Protocol):

| Exporter              | Protocol | Backend           |
|----------------------|----------|-------------------|
| OTLP (gRPC)          | gRPC     | Collector, Tempo  |
| OTLP (HTTP)          | HTTP/1.1 | Collector, Tempo  |
| Prometheus            | HTTP     | Prometheus        |
| Jaeger                | gRPC     | Jaeger            |
| Zipkin                | HTTP     | Zipkin            |
| Console               | stdout   | Development       |

### The OTel Collector

The Collector is a pipeline of receivers, processors, and exporters:

```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  # Scrape Prometheus metrics
  prometheus:
    config:
      scrape_configs:
        - job_name: 'otel-collector'
          static_configs:
            - targets: ['localhost:8888']

processors:
  # Batch telemetry for efficient export
  batch:
    timeout: 5s
    send_batch_size: 1000

  # Add resource attributes
  resource:
    attributes:
      - key: environment
        value: production
        action: upsert

  # Memory limiter (prevents OOM)
  memory_limiter:
    check_interval: 1s
    limit_mib: 2048
    spike_limit_mib: 512

  # Tail-based sampling (keep only interesting traces)
  tail_sampling:
    policies:
      - name: error-policy
        type: status_code
        status_code: { status_codes: [ERROR] }
      - name: slow-policy
        type: latency
        latency: { threshold_ms: 1000 }
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: { sampling_percentage: 10 }

exporters:
  # Send traces to Tempo
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

  # Send metrics to Mimir/Prometheus
  prometheusremotewrite:
    endpoint: http://mimir:9009/api/v1/push

  # Send logs to Loki
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

  # Debug output
  debug:
    verbosity: detailed

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch, tail_sampling]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch, resource]
      exporters: [prometheusremotewrite]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [loki]
```

---

## Step-by-Step Practical

### Instrument a Python Application with OpenTelemetry

**Step 1: Install dependencies**

```bash
pip install flask \
  opentelemetry-api \
  opentelemetry-sdk \
  opentelemetry-exporter-otlp \
  opentelemetry-instrumentation-flask \
  opentelemetry-instrumentation-requests
```

**Step 2: Create the instrumented application**

```python
# app.py
import time
import random
from flask import Flask, jsonify
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

# Resource definition
resource = Resource.create({
    "service.name": "demo-api",
    "service.version": "1.0.0",
    "deployment.environment": "development",
})

# Traces setup
trace_provider = TracerProvider(resource=resource)
trace_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
)
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# Metrics setup
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint="localhost:4317", insecure=True),
    export_interval_millis=15000,
)
metric_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)
meter = metrics.get_meter(__name__)

# Custom metrics
request_counter = meter.create_counter(
    "app.requests.total",
    description="Total requests processed",
)
request_duration = meter.create_histogram(
    "app.request.duration",
    description="Request duration in milliseconds",
    unit="ms",
)

# Flask app
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/api/users")
def get_users():
    with tracer.start_as_current_span("fetch_users") as span:
        # Simulate database query
        duration = random.uniform(5, 50)
        time.sleep(duration / 1000)

        span.set_attribute("db.system", "postgresql")
        span.set_attribute("db.operation", "SELECT")
        span.set_attribute("users.count", 42)

        request_counter.add(1, {"endpoint": "/api/users", "method": "GET"})
        request_duration.record(duration, {"endpoint": "/api/users"})

        return jsonify({"users": [{"id": 1, "name": "Alice"}]})

@app.route("/api/orders")
def get_orders():
    with tracer.start_as_current_span("fetch_orders") as span:
        duration = random.uniform(10, 200)
        time.sleep(duration / 1000)

        if random.random() < 0.05:  # 5% error rate
            span.set_status(trace.StatusCode.ERROR, "Database timeout")
            request_counter.add(1, {"endpoint": "/api/orders", "status": "error"})
            return jsonify({"error": "timeout"}), 500

        request_counter.add(1, {"endpoint": "/api/orders", "status": "ok"})
        request_duration.record(duration, {"endpoint": "/api/orders"})
        return jsonify({"orders": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
```

**Step 3: Deploy the OTel Collector**

```bash
# Install the OTel Collector via Helm
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm install otel-collector open-telemetry/opentelemetry-collector \
  --namespace monitoring \
  --set mode=deployment \
  --set config.receivers.otlp.protocols.grpc.endpoint="0.0.0.0:4317" \
  --set config.exporters.debug.verbosity=detailed
```

**Step 4: Run and verify**

```bash
# Run the app
python app.py

# Generate traffic
for i in $(seq 1 100); do
  curl http://localhost:8080/api/users
  curl http://localhost:8080/api/orders
done

# Check collector logs for received spans and metrics
kubectl logs -n monitoring deployment/otel-collector
```

Expected collector output:

```
Span #0
    Trace ID       : 4bf92f3577b34da6a3ce929d0e0e4736
    Span ID        : 00f067aa0ba902b7
    Name           : fetch_users
    Kind           : Internal
    Start time     : 2024-01-15T10:23:45.123Z
    End time       : 2024-01-15T10:23:45.158Z
    Status code    : Unset
    Attributes:
        -> db.system: postgresql
        -> db.operation: SELECT
        -> users.count: 42
```

---

## Exercises

### Exercise 1: Auto-Instrumentation
Use OpenTelemetry auto-instrumentation to instrument an existing Python application
without modifying any code. Compare the traces generated by auto-instrumentation with
manual instrumentation.

### Exercise 2: Collector Pipeline
Deploy an OTel Collector with three exporters: OTLP to Tempo (traces), Prometheus
Remote Write to Mimir (metrics), and Loki (logs). Verify that all three signal types
flow through the same Collector.

### Exercise 3: Custom Spans
Add manual instrumentation to a multi-step business process (e.g., checkout flow).
Create spans for each step, add relevant attributes, and record errors as span
events.

### Exercise 4: Sampling Configuration
Configure tail-based sampling in the OTel Collector to: (a) keep 100% of error
traces, (b) keep 100% of traces slower than 1 second, (c) sample 10% of all other
traces. Verify the sampling is working by checking the trace count.

---

## Knowledge Check

### Question 1
What is the difference between the OTel API and the OTel SDK?

<details>
<summary>Answer</summary>

The **API** defines the interfaces (abstract classes, function signatures) for
creating spans, metrics, and log records. It is lightweight, stable, and safe for
library authors to depend on. It contains no implementation logic.

The **SDK** implements the API. It handles sampling decisions, batching, context
propagation, and exporting. Application developers configure the SDK at startup to
control how telemetry is collected and where it is sent.

This separation allows libraries to instrument themselves with the API without
forcing users into a specific SDK implementation or backend.

</details>

### Question 2
What is the OTel Collector and why should you use it?

<details>
<summary>Answer</summary>

The OTel Collector is a vendor-agnostic proxy that receives, processes, and exports
telemetry data. Benefits:

1. **Decoupling** — Applications send to the Collector; the Collector sends to
   backends. Changing backends requires only Collector config changes, not code.
2. **Processing** — The Collector can batch, filter, sample, enrich, and transform
   data before export.
3. **Reliability** — The Collector handles retries, buffering, and backpressure,
   reducing the burden on applications.
4. **Multi-backend** — One Collector can send traces to Tempo, metrics to
   Prometheus, and logs to Loki simultaneously.

</details>

### Question 3
What are the three types of Collector pipeline components?

<details>
<summary>Answer</summary>

1. **Receivers** — Ingest telemetry data in various formats (OTLP, Prometheus,
   Jaeger, Zipkin, syslog). They listen on network ports or scrape endpoints.
2. **Processors** — Transform, filter, batch, or enrich data in the pipeline.
   Examples: batch, memory_limiter, resource (add attributes), tail_sampling.
3. **Exporters** — Send processed data to backends (OTLP, Prometheus Remote Write,
   Loki, Jaeger, vendor-specific exporters).

Pipelines are defined per signal type (traces, metrics, logs) and can have multiple
receivers, processors, and exporters.

</details>

### Question 4
Why did OpenTracing and OpenCensus merge into OpenTelemetry?

<details>
<summary>Answer</summary>

Having two competing standards fragmented the ecosystem. Library authors had to
choose which standard to support, and users had to pick one and hope their
libraries supported it. OpenTracing provided only an API (no implementation),
while OpenCensus provided both API and implementation but only for traces and
metrics (no logs). The merger combined the best of both: OpenTracing's broad vendor
support with OpenCensus's implementation quality, and extended coverage to all three
signals (traces, metrics, logs) under a single unified project.

</details>
