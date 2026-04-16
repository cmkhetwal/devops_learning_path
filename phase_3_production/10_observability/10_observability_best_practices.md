# Lesson 10: Observability Best Practices

## Why This Matters in DevOps

You can deploy Prometheus, Loki, Tempo, and Grafana — and still have terrible
observability. Tools are necessary but not sufficient. What matters is *how* you use
them: what you measure, how you alert, how you respond to incidents, and how you
build a culture where observability is everyone's responsibility.

This lesson covers the practices that separate organizations with mature
observability from those drowning in dashboards nobody looks at, alerts nobody
responds to, and traces nobody knows how to read. These are the human and
organizational patterns that make the technical investment worthwhile.

---

## Core Concepts

### Instrumentation Strategy: What to Measure

Not everything that can be measured should be measured. Over-instrumentation wastes
resources (storage, CPU, cardinality) and creates noise.

#### The Instrumentation Hierarchy

```
Level 1: INFRASTRUCTURE (provided by platform)
  - Node CPU, memory, disk, network (node_exporter)
  - Container resource usage (cAdvisor / kubelet)
  - Kubernetes state (kube-state-metrics)
  Status: Usually provided out of the box with kube-prometheus-stack

Level 2: SERVICE-LEVEL (RED metrics for every service)
  - Request rate
  - Error rate
  - Latency distribution (histogram)
  Status: Auto-instrumented via OTel or service mesh

Level 3: DEPENDENCY (health of external dependencies)
  - Database query latency and error rate
  - Cache hit/miss ratio
  - External API latency and availability
  - Message queue depth and consumer lag
  Status: Auto-instrumented via OTel client libraries

Level 4: BUSINESS (domain-specific metrics)
  - Orders processed per minute
  - Payment success rate
  - User signups
  - Revenue per hour
  Status: Manual instrumentation required — MOST VALUABLE for stakeholders
```

**Guideline**: Levels 1-2 should be fully automated (zero developer effort). Level 3
should be mostly automated via OTel. Level 4 requires intentional design and is
where observability delivers the most business value.

#### What NOT to Instrument

- Individual user IDs as metric labels (cardinality explosion)
- Request bodies or PII in traces (security/compliance risk)
- Extremely high-frequency internal loops (performance overhead)
- Metrics that nobody ever queries (measure quarterly, prune unused metrics)

### Alert Design: Symptoms Not Causes

The most common alerting mistake is alerting on causes instead of symptoms:

```
BAD ALERTS (cause-based):
  "CPU above 80%" — So what? If latency is fine, this is informational.
  "Memory above 90%" — Same. Might be normal for a JVM.
  "Disk read IOPS above 1000" — Is the service affected? Maybe not.
  "Pod restarted" — If the service is healthy, this is noise.

GOOD ALERTS (symptom-based):
  "P99 latency above SLO threshold for 5 minutes"
  "Error rate above 1% for 5 minutes"
  "Error budget burned 5% in the last hour"
  "Service returning 5xx for more than 2 minutes"
```

```
Cause-based alert:     "CPU is high" -> Maybe the service is fine
Symptom-based alert:   "Users are experiencing errors" -> Definitely a problem

Cause-based alerts generate noise.
Symptom-based alerts generate action.
```

Every alert should pass the "so what?" test: if this alert fires at 3am, will the
on-call engineer need to take immediate action? If the answer is "probably not,"
it should be a dashboard metric or a warning, not a page.

### Runbooks

Every alert must have a runbook. A runbook is a documented procedure for responding
to a specific alert:

```markdown
# Runbook: HighErrorRate

## Alert Description
Error rate for the payment service has exceeded 1% for more than 5 minutes.

## Severity
Critical

## Impact
Users may be unable to complete purchases.

## Diagnosis Steps
1. Check the error rate dashboard:
   https://grafana.example.com/d/payment-svc
2. Look at recent traces with errors:
   https://grafana.example.com/explore?datasource=tempo&query=...
3. Check recent deployments:
   `argocd app history payment-service`
4. Check dependency health:
   - Payment gateway status: https://status.stripe.com
   - Database: check connection pool and query latency

## Common Causes
- Payment gateway timeout (check status page)
- Database connection exhaustion (check pool metrics)
- Bad deployment (check ArgoCD sync history)
- Rate limiting by payment provider

## Remediation
1. If caused by a recent deployment:
   `argocd app rollback payment-service`
2. If caused by gateway timeout:
   - Check if gateway is experiencing an incident
   - Consider enabling circuit breaker
3. If caused by database:
   - Check slow query log
   - Consider scaling read replicas

## Escalation
- Team: #payments-team
- On-call: PagerDuty payments rotation
- Manager: @payments-lead
```

### On-Call Practices

```
HEALTHY ON-CALL:
  - Average 1-2 pages per shift (not per hour)
  - 95% of alerts are actionable
  - Runbooks exist for all alerts
  - Post-incident reviews happen for every significant incident
  - On-call load is distributed fairly across the team
  - On-call engineers have time to improve reliability (not just fight fires)

UNHEALTHY ON-CALL:
  - 10+ pages per shift
  - Most alerts are noise or duplicates
  - No runbooks ("ask John, he knows")
  - Post-mortems are blame-oriented
  - The same 2 people always take on-call
  - On-call is 100% reactive, 0% proactive
```

### SLO-Based Alerting

Instead of alerting on raw metrics, alert on SLO burn rate:

```yaml
# Multi-window, multi-burn-rate alerting (Google SRE approach)

# 2% of monthly budget consumed in 1 hour -> Critical
- alert: ErrorBudgetBurn_High
  expr: |
    (
      http_errors_ratio:rate1h > (14.4 * 0.001)
      and
      http_errors_ratio:rate5m > (14.4 * 0.001)
    )
  for: 2m
  labels:
    severity: critical
    window: 1h
  annotations:
    summary: "High error budget burn rate"
    description: "At this rate, the monthly error budget will be exhausted in ~2 days"

# 5% of monthly budget consumed in 6 hours -> Critical
- alert: ErrorBudgetBurn_Medium
  expr: |
    (
      http_errors_ratio:rate6h > (6 * 0.001)
      and
      http_errors_ratio:rate30m > (6 * 0.001)
    )
  for: 5m
  labels:
    severity: critical
    window: 6h

# 10% of monthly budget consumed in 3 days -> Warning
- alert: ErrorBudgetBurn_Low
  expr: |
    (
      http_errors_ratio:rate3d > (1 * 0.001)
      and
      http_errors_ratio:rate6h > (1 * 0.001)
    )
  for: 30m
  labels:
    severity: warning
    window: 3d
```

The multi-window approach prevents both false positives (short spikes that heal
quickly) and false negatives (slow burns that individually seem fine).

### Cost of Observability

Observability data volume can grow faster than your infrastructure:

```
Data Volume Estimation:

METRICS:
  - 1,000 time series * 15s scrape interval * 8 bytes/sample
  - = ~46 MB/day per 1,000 series
  - 100,000 series = ~4.6 GB/day
  - With 30-day retention = ~138 GB

LOGS:
  - 100 pods * 100 log lines/second * 200 bytes/line
  - = ~1.7 GB/hour = ~41 GB/day
  - With 30-day retention = ~1.2 TB
  - THIS IS USUALLY THE BIGGEST COST

TRACES:
  - 10,000 req/s * 10% sampling * 5 spans/trace * 1 KB/span
  - = ~50 MB/minute = ~72 GB/day
  - With 14-day retention = ~1 TB
```

Cost reduction strategies:

```
METRICS:
  - Review and remove unused metrics (query Prometheus for unused metrics)
  - Use recording rules to pre-aggregate and drop raw high-cardinality data
  - Implement tiered retention (full resolution for 7 days, downsampled for 1 year)

LOGS:
  - Drop debug/trace logs in production at the agent level
  - Use structured logging to reduce line size
  - Implement log levels and only ship WARN+ to long-term storage
  - Use sampling for high-volume services

TRACES:
  - Implement tail-based sampling (keep errors, sample normal traces)
  - Set aggressive retention (7-14 days for most environments)
  - Use span filtering to drop health-check and readiness probe spans
```

### Commercial vs Open-Source

| Feature            | LGTM Stack (Open Source)  | Datadog          | New Relic         | Dynatrace        |
|--------------------|--------------------------|------------------|-------------------|------------------|
| Cost               | Infrastructure only      | Per host + volume| Per GB ingested   | Per host          |
| Metrics            | Mimir (PromQL)           | Proprietary      | NRQL              | Proprietary      |
| Logs               | Loki (LogQL)             | Included         | Included          | Included         |
| Traces             | Tempo (TraceQL)          | Included         | Included          | Included (auto)  |
| Setup complexity   | High                     | Low              | Low               | Medium           |
| Customization      | Unlimited                | Limited          | Limited           | Limited          |
| Vendor lock-in     | None                     | High             | High              | High             |
| OTel support       | Native                   | Good             | Good              | Good             |
| Support            | Community / paid         | 24/7 enterprise  | 24/7 enterprise   | 24/7 enterprise  |

**When to choose open source**: You have platform engineering capacity, want to
avoid vendor lock-in, have cost sensitivity at scale, or need deep customization.

**When to choose commercial**: Your team is small, you need to move fast, you value
ease of setup over flexibility, or you need enterprise support and compliance
certifications.

**Typical cost comparison at scale (100 hosts, 50 services)**:

```
LGTM Stack:
  AWS infrastructure: ~$2,000-5,000/month
  Engineering time: 1-2 FTEs for maintenance
  Total effective: ~$20,000-40,000/month

Datadog:
  Licensing: ~$30,000-80,000/month (depends on features)
  Engineering time: 0.25 FTE
  Total effective: ~$35,000-85,000/month

Break-even: ~50-100 hosts (below this, commercial is often cheaper)
```

### Building an Observability Culture

Technical tools are only half the equation. Culture determines whether observability
is actually used:

```
PRACTICES THAT BUILD CULTURE:

1. Observability is part of the definition of done
   - No feature ships without metrics, logs, and traces
   - PR review includes instrumentation review

2. Dashboards are part of daily standups
   - "Here is what our service looked like yesterday"
   - Teams own their dashboards

3. Post-incident reviews focus on observability gaps
   - "How could we have detected this faster?"
   - "What signal was missing?"
   - Action items include adding missing instrumentation

4. On-call handoff includes dashboard review
   - Outgoing on-call walks through any anomalies
   - Incoming on-call knows what "normal" looks like

5. Regular alert hygiene
   - Quarterly review: delete alerts nobody acts on
   - Track alert-to-action ratio as a team metric
   - If an alert fires and is ignored 3 times, delete or fix it

6. Game days and chaos engineering
   - Inject failures and verify detection time
   - Practice using observability tools under pressure
   - Build muscle memory for incident response workflows
```

---

## Step-by-Step Practical

### Building an Observability Review Process

**Step 1: Create an observability checklist for new services**

```markdown
## Observability Checklist for New Service Deployment

### Metrics (Level 2: Service-Level)
- [ ] HTTP request rate (counter)
- [ ] HTTP error rate (counter by status code)
- [ ] HTTP request latency (histogram)
- [ ] Active connections (gauge)

### Metrics (Level 3: Dependencies)
- [ ] Database query latency (histogram)
- [ ] Database error rate (counter)
- [ ] Cache hit/miss ratio (counters)
- [ ] External API latency (histogram per dependency)

### Metrics (Level 4: Business)
- [ ] Key business events (counters)
- [ ] Business-specific latency metrics

### Logging
- [ ] Structured JSON logging
- [ ] Trace ID in all log entries
- [ ] Request ID in all log entries
- [ ] Log level is configurable at runtime
- [ ] No PII in logs

### Tracing
- [ ] OTel auto-instrumentation enabled
- [ ] Custom spans for key business logic
- [ ] Span attributes follow semantic conventions
- [ ] Error spans include exception details

### Dashboards
- [ ] Service-level RED dashboard
- [ ] Dependency health dashboard
- [ ] SLO tracking dashboard (if SLOs are defined)

### Alerting
- [ ] SLO-based alert for availability
- [ ] SLO-based alert for latency
- [ ] Runbook for each alert
- [ ] Alerts tested (verified they fire)
```

**Step 2: Define SLOs for the service**

```yaml
service: payment-service
slos:
  availability:
    description: "Proportion of non-5xx responses"
    target: 99.95%
    window: 30 days
    error_budget: 21.6 minutes

  latency:
    description: "Proportion of requests faster than 500ms"
    target: 99.0%
    window: 30 days

burn_rate_alerts:
  - severity: critical
    short_window: 5m
    long_window: 1h
    burn_rate: 14.4x

  - severity: warning
    short_window: 30m
    long_window: 6h
    burn_rate: 6x
```

**Step 3: Create a quarterly observability review template**

```markdown
## Q1 Observability Review — Payment Service

### Alert Quality
- Total alerts fired: 47
- Actionable alerts: 38 (81%)
- False positives: 9 (19%)
- Target: > 90% actionable

### Actions:
- Remove alert: "PaymentDBSlowQuery" — fired 12 times, never actioned
- Tune threshold: "HighLatency" — threshold too aggressive, increase to 800ms

### SLO Performance
- Availability: 99.97% (target: 99.95%) — PASS
- Latency: 98.8% (target: 99.0%) — FAIL
- Error budget consumed: 120%

### Actions:
- Investigate latency regression introduced in v3.2.0
- Consider adding read replicas for database

### Instrumentation Gaps
- Missing: Circuit breaker state metric
- Missing: Connection pool utilization for payment gateway
- Missing: Business metric for refund processing rate

### Cost
- Metrics: 45,000 series (within budget)
- Logs: 28 GB/day (over budget — need to reduce debug logs)
- Traces: 12 GB/day (within budget with 10% sampling)
```

**Step 4: Set up metric usage tracking**

```promql
# Find metrics that are never queried (unused)
# Run this against Prometheus itself:
prometheus_tsdb_head_series

# Check which metrics have the most time series (potential cardinality issues)
topk(20, count by (__name__) ({__name__=~".+"}))

# Check which metrics are costing the most storage
topk(20, sum by (__name__) (
  scrape_series_added
))
```

---

## Exercises

### Exercise 1: Alert Audit
Review all alerts currently configured in your environment. For each alert, answer:
(a) Is it symptom-based or cause-based? (b) Does it have a runbook? (c) How many
times did it fire last month? (d) How many times was it actioned? Remove or
restructure alerts that fail this review.

### Exercise 2: SLO Implementation
Define SLOs for a service you own. Implement them as Prometheus recording rules,
create a Grafana dashboard with SLI gauges and error budget tracking, and set up
multi-window burn rate alerts.

### Exercise 3: Cost Analysis
Calculate the monthly observability cost for your environment. Break it down by
signal type (metrics, logs, traces) and by service. Identify the top three cost
drivers and propose specific reduction strategies.

### Exercise 4: Instrumentation Review
Pick a service and audit its observability coverage using the checklist from the
practical section. Identify three gaps and file tickets to address them.

### Exercise 5: Observability Culture Assessment
Interview three engineers on your team. Ask: (a) Do they check dashboards daily?
(b) Can they explain how to trace a request through the system? (c) Do they know
the SLOs for their services? Use the answers to identify cultural gaps and propose
one specific improvement.

---

## Knowledge Check

### Question 1
Why should alerts be based on symptoms rather than causes?

<details>
<summary>Answer</summary>

Symptom-based alerts (high error rate, SLO violation) indicate user-visible impact
and always require action. Cause-based alerts (high CPU, disk usage) may or may not
affect users — a JVM running at 90% memory is normal; high CPU during a batch job
is expected.

Alerting on causes generates noise: on-call engineers learn to ignore alerts that do
not correlate with problems. Alerting on symptoms ensures every page represents real
user impact, maintaining trust in the alerting system and reducing alert fatigue.

Causes should be monitored (via dashboards) but not paged. Symptoms should be paged.

</details>

### Question 2
What is multi-window, multi-burn-rate alerting?

<details>
<summary>Answer</summary>

It is a sophisticated SLO-based alerting technique from Google's SRE practices. It
uses multiple time windows to detect both fast and slow burns of the error budget:

- **Fast burn** (14.4x rate, 1h window): Detects rapid degradation that will
  exhaust the monthly budget in ~2 days. Triggers critical alert quickly.
- **Medium burn** (6x rate, 6h window): Detects moderate degradation. Triggers
  critical alert after sustained issues.
- **Slow burn** (1x rate, 3d window): Detects gradual degradation. Triggers
  warning for slow-building problems.

Each burn rate check uses two windows (short for freshness, long to avoid false
positives from brief spikes). This prevents both false positives (momentary spikes)
and false negatives (slow cumulative degradation).

</details>

### Question 3
When should you choose commercial observability (Datadog, New Relic) over open-source
(LGTM stack)?

<details>
<summary>Answer</summary>

Choose commercial when:
- Your team is small (under ~5 engineers) and cannot dedicate time to operating
  observability infrastructure.
- You value fast time-to-value — commercial tools work out of the box.
- You need enterprise features (SSO, compliance certifications, enterprise support).
- Your scale is small enough (under ~50-100 hosts) that the licensing cost is less
  than the engineering time to run open-source.

Choose open-source when:
- You have platform engineering capacity to operate the stack.
- You are at scale where commercial licensing becomes prohibitively expensive.
- You need deep customization or specific integrations.
- Vendor lock-in is a strategic concern.

The break-even point is typically around 50-100 hosts — below that, commercial is
often cheaper in total cost; above that, open-source becomes increasingly
cost-effective.

</details>

### Question 4
What are the four levels of the instrumentation hierarchy?

<details>
<summary>Answer</summary>

1. **Infrastructure** — Node and container metrics (CPU, memory, disk, network).
   Provided by platform tooling (node_exporter, cAdvisor). Zero developer effort.

2. **Service-level** — RED metrics for every service (request rate, error rate,
   latency). Auto-instrumented via OTel or service mesh.

3. **Dependency** — Health of external dependencies (database latency, cache
   hit/miss, external API health). Mostly auto-instrumented via OTel client
   libraries.

4. **Business** — Domain-specific metrics (orders/minute, revenue, conversion rate).
   Requires manual instrumentation. Most valuable for stakeholders and most often
   missing.

</details>

### Question 5
What should a well-written runbook contain?

<details>
<summary>Answer</summary>

A complete runbook contains:
1. **Alert description** — What the alert means in plain language.
2. **Severity** — How urgent the response should be.
3. **Impact** — What users or systems are affected.
4. **Diagnosis steps** — Specific dashboards, queries, and commands to determine
   the root cause.
5. **Common causes** — The most likely reasons for this alert, based on past
   incidents.
6. **Remediation** — Step-by-step instructions for each common cause, including
   rollback procedures.
7. **Escalation** — Who to contact if the on-call engineer cannot resolve it.

Every alert without a runbook is a training failure — the next on-call engineer
should not have to reverse-engineer the response at 3am.

</details>
