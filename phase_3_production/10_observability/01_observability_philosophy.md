# Lesson 01: Observability Philosophy

## Why This Matters in DevOps

In a monolith, debugging is hard but contained: one process, one log file, one
server. In distributed systems, a single user request may traverse ten services
across three clusters, pass through message queues, hit caches, query databases,
and return through an API gateway. When that request fails, you cannot simply SSH
into "the server" and tail a log file.

Observability is the discipline of understanding *what your system is doing* and
*why it is behaving that way*, based solely on the signals it emits. It is not
monitoring with a fancier name — it represents a fundamental shift from "did the
thing I anticipated happen?" (monitoring) to "what is happening, including things
I did not anticipate?" (observability).

For DevOps engineers and SREs, observability is the difference between spending 20
minutes resolving an incident and spending 4 hours blindly restarting services.

---

## Core Concepts

### Monitoring vs Observability

**Monitoring** answers known questions: "Is the server up?" "Is CPU above 80%?"
"Did the batch job complete?" You define dashboards for things you *expect* to go
wrong.

**Observability** answers unknown questions: "Why is the P99 latency elevated for
users in the EU accessing the checkout endpoint via mobile?" You instrument your
system to emit rich signals so you can ask arbitrary questions *after* a problem
occurs.

```
MONITORING                          OBSERVABILITY
==========                          =============
- Predefined dashboards             - Ad-hoc querying
- Known failure modes               - Unknown failure modes
- Thresholds and alerts              - Exploration and correlation
- "Is it broken?"                   - "Why is it broken?"
- Necessary but not sufficient       - Includes monitoring + more
```

Observability does not replace monitoring — it encompasses it. You still need alerts
for known failure modes. But observability gives you the tools to diagnose novel
failures that no dashboard anticipated.

### The Three Pillars (Plus Profiling)

#### Pillar 1: Metrics

Numeric measurements over time. Compact, efficient, excellent for alerting.

```
http_requests_total{method="GET", endpoint="/api/v1/users", status="200"} 142857
http_request_duration_seconds{quantile="0.99"} 0.245
system_cpu_utilization{host="web-01"} 0.73
```

Characteristics:
- Fixed cost per metric (regardless of request volume)
- Easy to aggregate, downsample, and alert on
- Lose individual request context

#### Pillar 2: Logs

Timestamped textual records of events.

```json
{
  "timestamp": "2024-01-15T10:23:45.123Z",
  "level": "ERROR",
  "service": "payment-service",
  "trace_id": "abc123def456",
  "message": "Payment processing failed",
  "error": "timeout connecting to payment gateway",
  "customer_id": "cust_789",
  "amount": 99.99
}
```

Characteristics:
- Rich context for individual events
- Cost scales with event volume
- Harder to aggregate and query at scale

#### Pillar 3: Traces

Records of a request's journey across services.

```
Trace: abc123def456
├── [api-gateway] GET /checkout (45ms)
│   ├── [auth-service] validateToken (3ms)
│   ├── [cart-service] getCart (12ms)
│   │   └── [redis] GET cart:user:789 (1ms)
│   ├── [payment-service] processPayment (28ms)  ← SLOW
│   │   └── [payment-gateway] charge (25ms)       ← ROOT CAUSE
│   └── [notification-service] sendConfirmation (2ms)
```

Characteristics:
- Shows causality and timing across services
- Expensive to store (sampled in production)
- Essential for debugging distributed systems

#### Bonus Pillar: Profiling (Continuous Profiling)

Captures CPU, memory, and goroutine profiles over time. Tools like Pyroscope or
Parca allow you to ask "what code paths were consuming CPU during the latency
spike at 3am?"

### Google's Four Golden Signals

From the Google SRE book, these four signals are sufficient to monitor any
user-facing service:

```
1. LATENCY
   How long requests take.
   Track both successful and failed request latency separately.
   Example: p50 = 45ms, p95 = 120ms, p99 = 450ms

2. TRAFFIC
   How much demand is placed on the system.
   Example: 1,200 requests/second, 45 active WebSocket connections

3. ERRORS
   The rate of failed requests.
   Track explicit errors (HTTP 5xx) AND implicit errors (HTTP 200 but wrong data).
   Example: 0.3% error rate (target: < 0.1%)

4. SATURATION
   How "full" the system is.
   The resource most constrained (CPU, memory, disk I/O, network).
   Example: CPU at 78%, connection pool at 90% capacity
```

### The RED Method (for request-driven services)

Coined by Tom Wilkie (Grafana Labs), RED focuses on the request:

```
R - Rate:      requests per second
E - Errors:    number of failed requests per second
D - Duration:  distribution of request latency (histograms, not averages)
```

RED is ideal for microservices and APIs. "If I know the rate, error rate, and
latency distribution, I know if this service is healthy."

### The USE Method (for infrastructure resources)

Coined by Brendan Gregg, USE focuses on the resource:

```
U - Utilization:  percentage of resource capacity being used
S - Saturation:   degree of queued work (excess demand)
E - Errors:       count of error events
```

Apply USE to every resource: CPU, memory, disk, network, file descriptors,
connection pools. A service may have low RED metrics but high USE metrics (e.g.,
disk is 95% full — no errors yet, but failure is imminent).

### SRE Principles

#### SLIs (Service Level Indicators)
Quantitative measures of service behavior. Examples:
- Request latency (p99 < 200ms)
- Availability (successful requests / total requests)
- Throughput (requests processed per second)

#### SLOs (Service Level Objectives)
Target values for SLIs over a time window. Examples:
- "99.9% of requests complete within 200ms over a 30-day window"
- "99.95% availability per calendar month"

#### SLAs (Service Level Agreements)
Contractual commitments with consequences for missing SLOs. Example:
- "If availability drops below 99.9% in a month, customer receives 10% credit"

SLAs are tighter than SLOs, which are tighter than what engineering targets. The
buffer between SLO and SLA is your safety margin.

#### Error Budgets

```
Error Budget = 1 - SLO

Example:
  SLO: 99.9% availability
  Error Budget: 0.1% (43.2 minutes of downtime per 30 days)

  If 30 minutes of downtime have occurred this month:
  Remaining budget: 13.2 minutes
  Action: Slow down feature releases, focus on reliability
```

Error budgets create an objective framework for balancing feature velocity and
reliability. If the budget is healthy, ship fast. If the budget is depleted, freeze
features and fix reliability.

### Why Observability Matters More in Distributed Systems

```
Monolith:
  1 process, 1 log file, 1 host
  Failure modes: N
  Debugging: grep the log

Microservices (10 services):
  10 processes, 10 log streams, N hosts
  Failure modes: N * 10 (plus network between them)
  Debugging: correlate across 10 log streams using trace IDs

Microservices (100 services):
  100 processes, 100 log streams, M hosts
  Failure modes: combinatorial explosion
  Debugging: impossible without observability tooling
```

The number of potential failure modes grows combinatorially with the number of
services. Without correlated metrics, logs, and traces, debugging a 100-service
architecture is effectively impossible.

---

## Step-by-Step Practical

### Scenario: Designing an Observability Strategy

**Step 1: Classify your signals by the Golden Signals**

For a hypothetical e-commerce checkout service:

```yaml
# Golden Signals for checkout-service
signals:
  latency:
    metrics:
      - checkout_request_duration_seconds (histogram)
    slo: "99% of requests < 500ms"

  traffic:
    metrics:
      - checkout_requests_total (counter)
      - checkout_active_sessions (gauge)

  errors:
    metrics:
      - checkout_requests_total{status=~"5.."} (counter)
      - checkout_payment_failures_total (counter)
    slo: "Error rate < 0.1%"

  saturation:
    metrics:
      - checkout_db_connection_pool_usage (gauge)
      - container_cpu_usage_seconds_total (counter)
      - container_memory_working_set_bytes (gauge)
```

**Step 2: Define SLIs and SLOs**

```yaml
# SLI: Availability
definition: >
  The proportion of valid requests served successfully.
calculation: >
  sum(rate(http_requests_total{service="checkout",status!~"5.."}[30d])) /
  sum(rate(http_requests_total{service="checkout"}[30d]))
slo: 99.95%
error_budget_30d: 21.6 minutes

# SLI: Latency
definition: >
  The proportion of requests faster than the threshold.
calculation: >
  sum(rate(http_request_duration_seconds_bucket{service="checkout",le="0.5"}[30d])) /
  sum(rate(http_request_duration_seconds_count{service="checkout"}[30d]))
slo: 99.0%
```

**Step 3: Map the three pillars to your services**

```
Service          Metrics              Logs                  Traces
--------------------------------------------------------------------------
API Gateway      Rate, latency,       Access logs           Entry span
                 error rate           Error logs            (trace starts)

Auth Service     Token validation     Auth failures         Auth span
                 rate, latency        Audit events

Payment Service  Payment success      Transaction details   Payment span
                 rate, amount         Gateway errors        (critical path)

Notification     Delivery rate        Delivery attempts     Notification
Service          Queue depth          Template rendering    span (async)
```

**Step 4: Establish correlation**

The key that ties all three pillars together is the **trace ID**:

```json
// In metrics (via exemplars):
http_request_duration_seconds{service="checkout"} 0.45 # trace_id=abc123

// In logs:
{"trace_id": "abc123", "service": "checkout", "message": "Payment processed"}

// In traces:
Trace abc123: api-gateway -> auth -> cart -> payment -> notification
```

With a trace ID, you can jump from a slow metric to the exact trace to the
specific log line that explains the failure.

---

## Exercises

### Exercise 1: Golden Signals Audit
Pick a service your team owns. Identify what metrics exist today for each of the
four Golden Signals. Document gaps — which signals have no metric coverage?

### Exercise 2: SLO Design
Write SLOs for a service you operate. Define the SLI calculation (as a PromQL query
or pseudocode), the target percentage, and the implied error budget per 30-day
window.

### Exercise 3: RED vs USE
For one of your services, create a table with two rows: one for RED metrics
(rate, errors, duration) and one for USE metrics (utilization, saturation, errors)
applied to each infrastructure resource (CPU, memory, disk, network, database
connections).

### Exercise 4: Failure Mode Brainstorm
List 10 failure modes for a microservices architecture. For each, identify which
pillar (metrics, logs, or traces) would be most useful for detection and which for
diagnosis.

### Exercise 5: Observability Maturity Assessment
Rate your organization on a 1-5 scale for each area: metrics coverage, log
aggregation, distributed tracing, SLO adoption, alert quality, and incident
response tooling. Identify the weakest area and draft a 30-day improvement plan.

---

## Knowledge Check

### Question 1
What is the fundamental difference between monitoring and observability?

<details>
<summary>Answer</summary>

**Monitoring** answers predefined questions about known failure modes ("Is CPU above
80%?" "Is the service up?"). It relies on dashboards and alerts configured in
advance.

**Observability** enables answering arbitrary, unforeseen questions about system
behavior ("Why are EU mobile users experiencing slow checkout?"). It requires rich,
correlated signals (metrics, logs, traces) that can be queried ad hoc. Observability
includes monitoring but extends beyond it.

</details>

### Question 2
What are Google's Four Golden Signals?

<details>
<summary>Answer</summary>

1. **Latency** — How long requests take (both successful and failed).
2. **Traffic** — Volume of demand (requests per second, active connections).
3. **Errors** — Rate of failed requests (explicit 5xx and implicit failures).
4. **Saturation** — How full the system's resources are (CPU, memory, connections).

From the Google SRE book: "If you can only measure four metrics of your user-facing
system, focus on these four."

</details>

### Question 3
What is an error budget, and how does it influence engineering decisions?

<details>
<summary>Answer</summary>

An error budget is `1 - SLO`. For a 99.9% availability SLO, the error budget is
0.1%, which equals approximately 43 minutes of allowed downtime per 30-day window.

It influences decisions by providing an objective framework: when the budget is
healthy, teams can prioritize features and ship fast. When the budget is consumed
or at risk, teams must freeze feature work and focus on reliability improvements.
This prevents the subjective argument of "we need to move faster" vs "we need to be
more reliable" — the error budget provides the data-driven answer.

</details>

### Question 4
How does the RED method differ from the USE method?

<details>
<summary>Answer</summary>

**RED** (Rate, Errors, Duration) focuses on **requests** and is ideal for
user-facing services. It answers: "How is the service performing from the user's
perspective?"

**USE** (Utilization, Saturation, Errors) focuses on **resources** (CPU, memory,
disk, network) and is ideal for infrastructure monitoring. It answers: "How
stressed are the underlying resources?"

RED tells you *what* is broken from the user's perspective. USE tells you *why* it
might be broken from the resource perspective. Both are complementary.

</details>

### Question 5
Why is the trace ID the most important piece of observability correlation?

<details>
<summary>Answer</summary>

The trace ID is a unique identifier that follows a request across all services,
appearing in metrics (via exemplars), logs (as a structured field), and traces
(as the trace identifier). It enables three critical correlations:

1. **Metric to trace** — A slow p99 metric links to the exact trace showing which
   service was slow.
2. **Trace to log** — A span in a trace links to the detailed log entries for that
   request in that service.
3. **Log to trace** — An error log entry links to the full distributed trace
   showing the broader context.

Without trace IDs, the three pillars are isolated silos. With them, you can navigate
seamlessly between metrics, logs, and traces.

</details>
