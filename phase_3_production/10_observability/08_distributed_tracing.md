# Lesson 08: Distributed Tracing

## Why This Matters in DevOps

When a user clicks "Place Order" and sees a timeout, the request may have traveled
through an API gateway, authentication service, inventory service, payment service,
notification service, and a message queue — all running on different containers
across multiple nodes. Without distributed tracing, debugging means reading log
files from six different services and trying to mentally reconstruct the request
flow.

Distributed tracing solves this by stitching together a complete picture of a
request's journey across services. It shows exactly which service was slow, which
call failed, and where time was spent. It transforms "something is slow" into "the
payment gateway took 4 seconds on the third retry because the connection pool was
exhausted."

---

## Core Concepts

### Tracing Terminology

#### Trace

A trace represents the entire journey of a request through a distributed system.
It is identified by a unique **Trace ID** (typically a 128-bit hex string).

```
Trace ID: 4bf92f3577b34da6a3ce929d0e0e4736

api-gateway ──── auth-service
     │
     └── cart-service ──── redis
              │
              └── payment-service ──── payment-gateway
                        │
                        └── notification-service ──── email-provider
```

#### Span

A span represents a single unit of work within a trace. Each span has:
- **Span ID**: Unique identifier
- **Parent Span ID**: Links to the calling span (forms the tree)
- **Operation name**: What this span represents
- **Start time** and **Duration**
- **Attributes**: Key-value metadata
- **Events**: Timestamped annotations within the span
- **Status**: OK, ERROR, or UNSET

```
Span: api-gateway / HTTP GET /checkout
├── Span ID: 00f067aa0ba902b7
├── Parent: none (root span)
├── Duration: 1,245ms
├── Attributes:
│   ├── http.method: GET
│   ├── http.url: /checkout
│   ├── http.status_code: 200
│   └── user.id: cust_789
├── Events:
│   └── [10ms] "Authentication validated"
└── Status: OK
```

#### Context Propagation

For traces to span across services, the trace context (Trace ID + Span ID) must be
propagated through the network. The W3C Trace Context standard defines HTTP headers:

```http
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
             │  │                                  │                 │
             │  │                                  │                 └── flags (sampled)
             │  │                                  └── parent span ID
             │  └── trace ID
             └── version
```

When Service A calls Service B, the OTel SDK automatically:
1. Injects the `traceparent` header into the outgoing HTTP request.
2. Service B's SDK extracts the header and creates a child span with the same
   Trace ID.

```python
# This happens automatically with OTel instrumentation:
# Service A (caller)
import requests
response = requests.get("http://service-b/api/data")
# OTel automatically adds: traceparent: 00-<trace-id>-<span-id>-01

# Service B (receiver)
# OTel automatically reads traceparent header
# Creates a new span with parent = Service A's span ID
```

### Tracing Backends

#### Grafana Tempo

The Grafana-native tracing backend. Designed for cost efficiency:

```bash
# Install Tempo via Helm
helm install tempo grafana/tempo \
  --namespace monitoring \
  --set tempo.storage.trace.backend=s3 \
  --set tempo.storage.trace.s3.bucket=tempo-traces \
  --set tempo.storage.trace.s3.endpoint=s3.amazonaws.com
```

Tempo stores traces in object storage (S3, GCS) without any indexing, relying on
Trace ID for lookups. It integrates natively with Grafana for visualization.

#### Jaeger

The CNCF graduated tracing backend (originally from Uber):

```bash
# Simple deployment for development
kubectl create namespace tracing
kubectl apply -f https://raw.githubusercontent.com/jaegertracing/jaeger-operator/main/examples/simplest.yaml
```

Jaeger provides its own UI and supports both in-memory and persistent storage
(Elasticsearch, Cassandra, Kafka).

### Trace-to-Log Correlation

Link traces to the exact log lines for that request:

```python
import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)

def process_order(order_id):
    span = trace.get_current_span()
    trace_id = span.get_span_context().trace_id
    span_id = span.get_span_context().span_id

    # Include trace context in log messages
    logger.info(
        "Processing order",
        extra={
            "order_id": order_id,
            "trace_id": format(trace_id, '032x'),
            "span_id": format(span_id, '016x'),
        }
    )
```

In Grafana, configure Loki to extract trace IDs from logs:

```yaml
# Loki data source configuration in Grafana
jsonData:
  derivedFields:
    - name: TraceID
      matcherRegex: '"trace_id":"(\w+)"'
      url: '$${__value.raw}'
      datasourceUid: tempo
```

Now clicking a trace ID in a log line opens the full trace in Tempo.

### Trace-to-Metric Correlation (Exemplars)

Exemplars are references from metrics to specific trace IDs:

```python
from opentelemetry import trace, metrics

meter = metrics.get_meter(__name__)
histogram = meter.create_histogram("http.request.duration")

def handle_request():
    start = time.time()
    # ... handle request ...
    duration = time.time() - start

    # The SDK automatically attaches the current trace ID as an exemplar
    histogram.record(duration * 1000, {"endpoint": "/api/orders"})
```

In Grafana, enable exemplars on Prometheus data source. Clicking an exemplar data
point on a time series panel opens the corresponding trace.

### Span Attributes

Standard semantic conventions for span attributes:

```python
# HTTP attributes
span.set_attribute("http.method", "POST")
span.set_attribute("http.url", "https://api.example.com/orders")
span.set_attribute("http.status_code", 201)
span.set_attribute("http.request.body.size", 1024)

# Database attributes
span.set_attribute("db.system", "postgresql")
span.set_attribute("db.name", "orders_db")
span.set_attribute("db.operation", "INSERT")
span.set_attribute("db.statement", "INSERT INTO orders (id, ...) VALUES (...)")

# Message queue attributes
span.set_attribute("messaging.system", "rabbitmq")
span.set_attribute("messaging.destination.name", "order.created")
span.set_attribute("messaging.operation", "publish")

# Custom business attributes
span.set_attribute("order.id", "ord_123")
span.set_attribute("order.total", 99.99)
span.set_attribute("customer.tier", "premium")
```

### Sampling Strategies

Storing every trace at scale is expensive. Sampling reduces volume:

#### Head-Based Sampling

Decision made at the start of the trace (in the SDK):

```python
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

# Sample 10% of traces
sampler = TraceIdRatioBased(0.1)
provider = TracerProvider(sampler=sampler, resource=resource)
```

Pros: Simple, low overhead. Cons: Might miss error traces.

#### Tail-Based Sampling

Decision made at the end of the trace (in the Collector):

```yaml
# OTel Collector tail sampling
processors:
  tail_sampling:
    decision_wait: 10s
    policies:
      # Always keep error traces
      - name: errors
        type: status_code
        status_code: { status_codes: [ERROR] }
      # Always keep slow traces
      - name: slow
        type: latency
        latency: { threshold_ms: 2000 }
      # Sample 5% of everything else
      - name: probabilistic
        type: probabilistic
        probabilistic: { sampling_percentage: 5 }
```

Pros: Keeps all interesting traces. Cons: Requires buffering complete traces in
the Collector (memory-intensive).

---

## Step-by-Step Practical

### Trace a Request Across 3 Services

**Step 1: Create three microservices**

```python
# service_a.py (API Gateway - port 8081)
from flask import Flask, jsonify
import requests
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

resource = Resource.create({"service.name": "api-gateway"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/checkout")
def checkout():
    with tracer.start_as_current_span("checkout_flow") as span:
        span.set_attribute("user.id", "cust_789")

        # Call order service
        order_resp = requests.get("http://localhost:8082/create-order")
        order = order_resp.json()

        # Call payment service
        payment_resp = requests.post(
            "http://localhost:8083/process-payment",
            json={"order_id": order["id"], "amount": 99.99}
        )

        return jsonify({
            "status": "complete",
            "order": order,
            "payment": payment_resp.json()
        })

if __name__ == "__main__":
    app.run(port=8081)
```

```python
# service_b.py (Order Service - port 8082)
import time
import random
from flask import Flask, jsonify
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

resource = Resource.create({"service.name": "order-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/create-order")
def create_order():
    with tracer.start_as_current_span("create_order") as span:
        # Simulate database insert
        with tracer.start_as_current_span("db_insert") as db_span:
            db_span.set_attribute("db.system", "postgresql")
            db_span.set_attribute("db.operation", "INSERT")
            time.sleep(random.uniform(0.01, 0.05))

        order_id = f"ord_{random.randint(1000, 9999)}"
        span.set_attribute("order.id", order_id)
        return jsonify({"id": order_id, "status": "created"})

if __name__ == "__main__":
    app.run(port=8082)
```

```python
# service_c.py (Payment Service - port 8083)
import time
import random
from flask import Flask, request, jsonify
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

resource = Resource.create({"service.name": "payment-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(BatchSpanProcessor(
    OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/process-payment", methods=["POST"])
def process_payment():
    data = request.json
    with tracer.start_as_current_span("process_payment") as span:
        span.set_attribute("payment.order_id", data["order_id"])
        span.set_attribute("payment.amount", data["amount"])

        # Simulate payment gateway call
        with tracer.start_as_current_span("gateway_charge") as gw_span:
            gw_span.set_attribute("gateway.name", "stripe")
            latency = random.uniform(0.05, 0.3)
            time.sleep(latency)

            if random.random() < 0.03:  # 3% failure rate
                gw_span.set_status(trace.StatusCode.ERROR, "Gateway timeout")
                span.set_status(trace.StatusCode.ERROR, "Payment failed")
                return jsonify({"status": "failed", "error": "gateway_timeout"}), 500

            gw_span.set_attribute("gateway.transaction_id", f"txn_{random.randint(100000, 999999)}")

        return jsonify({"status": "charged", "transaction_id": f"txn_{random.randint(100000, 999999)}"})

if __name__ == "__main__":
    app.run(port=8083)
```

**Step 2: Run the OTel Collector and all services**

```bash
# Terminal 1: OTel Collector (Docker)
docker run -p 4317:4317 -p 4318:4318 \
  -v $(pwd)/otel-config.yaml:/etc/otel/config.yaml \
  otel/opentelemetry-collector-contrib:latest \
  --config /etc/otel/config.yaml

# Terminals 2-4: Run each service
python service_a.py
python service_b.py
python service_c.py
```

**Step 3: Generate traffic and observe traces**

```bash
# Send requests
for i in $(seq 1 20); do
  curl http://localhost:8081/checkout
  sleep 0.5
done
```

**Step 4: View traces in Grafana (Tempo)**

Open Grafana > Explore > Tempo. Search for traces:

```
Expected trace visualization:

Trace: 4bf92f3577b34da6a3ce929d0e0e4736 (345ms)
├── api-gateway: HTTP GET /checkout (345ms)
│   ├── api-gateway: checkout_flow (340ms)
│   │   ├── order-service: HTTP GET /create-order (35ms)
│   │   │   └── order-service: create_order (32ms)
│   │   │       └── order-service: db_insert (23ms)
│   │   └── payment-service: HTTP POST /process-payment (280ms)
│   │       └── payment-service: process_payment (275ms)
│   │           └── payment-service: gateway_charge (250ms)  <- BOTTLENECK
```

The trace clearly shows that the payment gateway call dominates the total latency.

---

## Exercises

### Exercise 1: Three-Service Trace
Deploy the three services from the practical section. Generate traffic and find a
trace that shows the complete request flow. Identify the slowest span.

### Exercise 2: Error Trace Investigation
Find a trace with an ERROR status. Follow the trace to identify which service failed
and what the error message was. Check if the error was propagated correctly to the
root span.

### Exercise 3: Trace-to-Log Correlation
Add trace ID to your application's log output. In Grafana, configure Loki's derived
fields to link trace IDs to Tempo. Navigate from a log line to its full trace.

### Exercise 4: Sampling Strategy
Configure tail-based sampling in the OTel Collector. Generate 1000 requests, then
verify that all error traces are kept but only ~10% of successful traces are stored.
Calculate the storage savings.

### Exercise 5: Service Dependency Map
Use Tempo's service graph feature (or Jaeger's) to generate a service dependency
map from trace data. Compare it with your actual architecture diagram.

---

## Knowledge Check

### Question 1
What is the difference between a trace and a span?

<details>
<summary>Answer</summary>

A **trace** represents the complete journey of a single request through a
distributed system. It is identified by a unique Trace ID and is composed of
multiple spans.

A **span** represents a single unit of work within a trace (e.g., an HTTP request,
a database query, a function call). It has its own Span ID, a parent Span ID
(linking it to the calling span), a start time, duration, and attributes. Spans
form a tree structure that visualizes the request flow.

</details>

### Question 2
How does context propagation work across services?

<details>
<summary>Answer</summary>

Context propagation passes the Trace ID and Span ID from one service to the next
through HTTP headers. The W3C Trace Context standard uses the `traceparent` header:
`00-<trace-id>-<parent-span-id>-<flags>`.

When Service A calls Service B:
1. Service A's OTel SDK injects the `traceparent` header into the outgoing request.
2. Service B's OTel SDK extracts the header from the incoming request.
3. Service B creates a new span with the same Trace ID and sets the parent to
   Service A's Span ID.

This creates a connected tree of spans across all services.

</details>

### Question 3
What is the difference between head-based and tail-based sampling?

<details>
<summary>Answer</summary>

**Head-based sampling** makes the sampling decision at the start of a trace (in the
SDK). It is simple and low-overhead, but it cannot consider the trace outcome —
it might drop an error trace because the error had not happened yet when the
decision was made.

**Tail-based sampling** makes the decision after the trace is complete (in the
Collector). It can keep all error traces, all slow traces, and sample normal traces.
However, it requires the Collector to buffer complete traces in memory, which is
resource-intensive.

For production, tail-based sampling is preferred because it guarantees important
traces are always retained.

</details>

### Question 4
What are exemplars and how do they connect metrics to traces?

<details>
<summary>Answer</summary>

Exemplars are sample data points attached to metrics that include a reference to a
specific trace ID. When Prometheus records a histogram observation, it can store the
trace ID of the request that generated that data point.

In Grafana, exemplars appear as dots on time series panels. Clicking an exemplar
opens the corresponding trace in Tempo, allowing you to jump from "the p99 latency
spiked at 3pm" directly to "here is the exact trace of the slowest request at that
time." This bridges the gap between aggregate metrics and individual request details.

</details>
