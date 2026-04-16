"""
Week 12, Day 1: Exercise - Prometheus-style Metrics for DevOps

Build a metrics system that simulates Prometheus metric types.
No prometheus_client library needed -- you'll implement the
metric types yourself to understand how they work.

TASKS:
    1. Counter class        - A monotonically increasing counter
    2. Gauge class          - A value that goes up and down
    3. Histogram class      - Observe values in buckets
    4. MetricsRegistry      - Register and collect all metrics
    5. DevOpsDashboard      - Create DevOps-specific metrics
    6. format_metrics()     - Format metrics in Prometheus text format
"""


# ============================================================
# TASK 1: Counter class
#
# Implement a Counter metric that only increases.
#
# __init__(self, name, description, labels=None):
#   - name: metric name (string)
#   - description: help text (string)
#   - labels: list of label names (optional)
#   - Internal storage for values (float, starts at 0)
#   - If labels provided, store values per label combination
#
# inc(self, amount=1, **label_values):
#   - Increase counter by amount (must be >= 0)
#   - If amount < 0, raise ValueError
#   - If labels defined, label_values must match label names
#
# get(self, **label_values):
#   - Return current value (float)
#   - If labels, return value for given label combination
#   - Return 0.0 if label combination hasn't been used
#
# values(self):
#   - Return dict of all {label_tuple: value} pairs
#   - If no labels, return {(): value}
# ============================================================

class Counter:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: Gauge class
#
# Implement a Gauge metric that can increase or decrease.
#
# __init__(self, name, description, labels=None):
#   - Same as Counter
#
# set(self, value, **label_values):
#   - Set gauge to specific value
#
# inc(self, amount=1, **label_values):
#   - Increase by amount (can be negative)
#
# dec(self, amount=1, **label_values):
#   - Decrease by amount
#
# get(self, **label_values):
#   - Return current value (float), default 0.0
#
# values(self):
#   - Same as Counter
# ============================================================

class Gauge:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: Histogram class
#
# Implement a Histogram that sorts observations into buckets.
#
# __init__(self, name, description, buckets=None):
#   - buckets: sorted list of upper bounds
#     Default: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10]
#   - Track: count of observations, sum of observations,
#     and count per bucket
#
# observe(self, value):
#   - Record an observed value
#   - Increment count, add to sum
#   - Increment bucket counts for all buckets where value <= bound
#
# get_count(self):
#   - Return total number of observations
#
# get_sum(self):
#   - Return sum of all observed values
#
# get_buckets(self):
#   - Return list of (upper_bound, cumulative_count) tuples
#   - Include a "+Inf" bucket at the end with total count
#
# get_average(self):
#   - Return average of observed values (sum/count)
#   - Return 0.0 if no observations
# ============================================================

class Histogram:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: MetricsRegistry
#
# A registry that holds all metrics and can collect them.
#
# __init__(self):
#   - Initialize empty dict of metrics
#
# register(self, metric):
#   - Add a metric (Counter, Gauge, or Histogram) by its name
#   - If name already registered, raise ValueError
#
# get_metric(self, name):
#   - Return the metric object by name, or None
#
# collect(self):
#   - Return a list of dicts, one per metric:
#     {"name": name, "type": "counter"/"gauge"/"histogram",
#      "description": description, "values": metric.values()
#                                   or bucket data for histograms}
#   - For histograms, "values" should be:
#     {"count": count, "sum": sum, "buckets": get_buckets()}
# ============================================================

class MetricsRegistry:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: DevOpsDashboard
#
# Create a pre-configured dashboard with common DevOps metrics.
#
# __init__(self):
#   - Create a MetricsRegistry
#   - Register these metrics:
#     Counter("deployments_total", "Total deployments",
#             labels=["environment", "app", "result"])
#     Counter("http_requests_total", "Total HTTP requests",
#             labels=["method", "status"])
#     Gauge("active_servers", "Number of active servers",
#           labels=["environment"])
#     Gauge("cpu_usage_percent", "CPU usage percentage",
#           labels=["server"])
#     Histogram("request_duration_seconds",
#               "Request duration", buckets=[0.01, 0.05, 0.1, 0.5, 1, 5])
#
# record_deployment(self, environment, app, result):
#   - Increment the deployments_total counter
#
# record_request(self, method, status, duration):
#   - Increment http_requests_total counter
#   - Observe duration in histogram
#
# set_server_count(self, environment, count):
#   - Set active_servers gauge
#
# set_cpu_usage(self, server, percent):
#   - Set cpu_usage_percent gauge
#
# get_summary(self):
#   - Return a dict with:
#     "total_deployments": total across all labels
#     "total_requests": total across all labels
#     "avg_request_duration": from histogram
#     "environments": dict of env -> server count from gauge
# ============================================================

class DevOpsDashboard:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 6: format_metrics(registry)
#
# Format all metrics in Prometheus text exposition format.
#
# Format for each metric:
#
# # HELP metric_name description
# # TYPE metric_name counter|gauge|histogram
# metric_name{label1="val1",label2="val2"} value
#
# For counters/gauges with no labels:
# metric_name value
#
# For histograms:
# # HELP name description
# # TYPE name histogram
# name_bucket{le="0.01"} count
# name_bucket{le="0.05"} count
# ...
# name_bucket{le="+Inf"} count
# name_count total_count
# name_sum total_sum
#
# Return as a single string.
# ============================================================

def format_metrics(registry):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    print("=== Task 1: Counter ===")
    c = Counter("requests_total", "Total requests", labels=["method"])
    c.inc(method="GET")
    c.inc(method="GET")
    c.inc(method="POST")
    print(f"  GET: {c.get(method='GET')}")
    print(f"  POST: {c.get(method='POST')}")

    print("\n=== Task 2: Gauge ===")
    g = Gauge("temperature", "Current temp")
    g.set(22.5)
    g.inc(2)
    g.dec(0.5)
    print(f"  Value: {g.get()}")

    print("\n=== Task 3: Histogram ===")
    h = Histogram("duration", "Duration", buckets=[0.1, 0.5, 1.0, 5.0])
    for v in [0.05, 0.15, 0.3, 0.8, 1.5, 3.0]:
        h.observe(v)
    print(f"  Count: {h.get_count()}")
    print(f"  Sum: {h.get_sum()}")
    print(f"  Avg: {h.get_average():.3f}")
    print(f"  Buckets: {h.get_buckets()}")

    print("\n=== Task 5: Dashboard ===")
    dash = DevOpsDashboard()
    dash.record_deployment("production", "web-api", "success")
    dash.record_deployment("staging", "web-api", "success")
    dash.record_deployment("production", "web-api", "failure")
    dash.record_request("GET", "200", 0.15)
    dash.record_request("POST", "201", 0.45)
    dash.set_server_count("production", 5)
    dash.set_server_count("staging", 2)
    dash.set_cpu_usage("web-01", 45.2)
    summary = dash.get_summary()
    if summary:
        for k, v in summary.items():
            print(f"  {k}: {v}")

    print("\n=== Task 6: Prometheus Format ===")
    reg = MetricsRegistry()
    c2 = Counter("test_counter", "A test counter")
    c2.inc(5)
    reg.register(c2)
    output = format_metrics(reg)
    if output:
        print(output)
