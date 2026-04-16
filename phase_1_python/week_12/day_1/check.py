"""
Week 12, Day 1: Check - Prometheus-style Metrics
Verifies all 6 tasks from exercise.py
"""

import subprocess
import sys

def run_test(test_code):
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    score = 0
    total = 6

    # Task 1: Counter
    print("Task 1: Counter")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import Counter

# Without labels
c = Counter("test_total", "Test counter")
assert c.get() == 0.0
c.inc()
assert c.get() == 1.0
c.inc(5)
assert c.get() == 6.0

# Negative increment should raise
try:
    c.inc(-1)
    assert False, "Should raise ValueError for negative"
except ValueError:
    pass

# With labels
c2 = Counter("req_total", "Requests", labels=["method", "status"])
c2.inc(method="GET", status="200")
c2.inc(method="GET", status="200")
c2.inc(method="POST", status="201")
assert c2.get(method="GET", status="200") == 2.0
assert c2.get(method="POST", status="201") == 1.0
assert c2.get(method="DELETE", status="404") == 0.0

vals = c2.values()
assert isinstance(vals, dict)
assert len(vals) == 2
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: Gauge
    print("Task 2: Gauge")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import Gauge

g = Gauge("temp", "Temperature")
assert g.get() == 0.0
g.set(25.5)
assert g.get() == 25.5
g.inc(2)
assert g.get() == 27.5
g.dec(5)
assert g.get() == 22.5

# With labels
g2 = Gauge("cpu", "CPU", labels=["server"])
g2.set(45.0, server="web-01")
g2.set(62.0, server="web-02")
assert g2.get(server="web-01") == 45.0
assert g2.get(server="web-02") == 62.0
g2.inc(5, server="web-01")
assert g2.get(server="web-01") == 50.0
assert g2.get(server="unknown") == 0.0

vals = g2.values()
assert len(vals) == 2
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: Histogram
    print("Task 3: Histogram")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import Histogram

h = Histogram("dur", "Duration", buckets=[0.1, 0.5, 1.0, 5.0])
assert h.get_count() == 0
assert h.get_sum() == 0.0
assert h.get_average() == 0.0

h.observe(0.05)  # fits in 0.1, 0.5, 1.0, 5.0
h.observe(0.3)   # fits in 0.5, 1.0, 5.0
h.observe(0.8)   # fits in 1.0, 5.0
h.observe(3.0)   # fits in 5.0
h.observe(10.0)  # fits in none (only +Inf)

assert h.get_count() == 5
assert abs(h.get_sum() - 14.15) < 0.001, f"Sum: {h.get_sum()}"
assert abs(h.get_average() - 2.83) < 0.01, f"Avg: {h.get_average()}"

buckets = h.get_buckets()
assert isinstance(buckets, list)
# Buckets should be cumulative
bucket_dict = {str(b[0]): b[1] for b in buckets}
assert bucket_dict["0.1"] == 1, f"0.1 bucket: {bucket_dict['0.1']}"
assert bucket_dict["0.5"] == 2, f"0.5 bucket: {bucket_dict['0.5']}"
assert bucket_dict["1.0"] == 3, f"1.0 bucket: {bucket_dict['1.0']}"
assert bucket_dict["5.0"] == 4, f"5.0 bucket: {bucket_dict['5.0']}"
assert bucket_dict["+Inf"] == 5, f"+Inf bucket: {bucket_dict['+Inf']}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: MetricsRegistry
    print("Task 4: MetricsRegistry")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import MetricsRegistry, Counter, Gauge, Histogram

reg = MetricsRegistry()
c = Counter("requests", "Total requests")
g = Gauge("connections", "Active conns")
h = Histogram("latency", "Latency", buckets=[0.1, 1.0])

reg.register(c)
reg.register(g)
reg.register(h)

# Duplicate should raise
try:
    reg.register(Counter("requests", "duplicate"))
    assert False, "Should raise ValueError"
except ValueError:
    pass

assert reg.get_metric("requests") is c
assert reg.get_metric("connections") is g
assert reg.get_metric("nonexistent") is None

c.inc(10)
g.set(5)
h.observe(0.5)

collected = reg.collect()
assert isinstance(collected, list)
assert len(collected) == 3

names = {m["name"] for m in collected}
assert "requests" in names
assert "connections" in names
assert "latency" in names

for m in collected:
    if m["name"] == "requests":
        assert m["type"] == "counter"
    elif m["name"] == "connections":
        assert m["type"] == "gauge"
    elif m["name"] == "latency":
        assert m["type"] == "histogram"
        assert "count" in m["values"]
        assert "sum" in m["values"]
        assert "buckets" in m["values"]
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: DevOpsDashboard
    print("Task 5: DevOpsDashboard")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import DevOpsDashboard

dash = DevOpsDashboard()
dash.record_deployment("production", "web-api", "success")
dash.record_deployment("production", "web-api", "success")
dash.record_deployment("staging", "worker", "failure")
dash.record_request("GET", "200", 0.1)
dash.record_request("GET", "200", 0.2)
dash.record_request("POST", "201", 0.5)
dash.set_server_count("production", 5)
dash.set_server_count("staging", 2)
dash.set_cpu_usage("web-01", 45.0)

summary = dash.get_summary()
assert isinstance(summary, dict)
assert summary["total_deployments"] == 3, f"Deployments: {summary['total_deployments']}"
assert summary["total_requests"] == 3, f"Requests: {summary['total_requests']}"
assert abs(summary["avg_request_duration"] - 0.2667) < 0.01, f"Avg duration: {summary['avg_request_duration']}"
assert summary["environments"]["production"] == 5
assert summary["environments"]["staging"] == 2
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 6: format_metrics
    print("Task 6: format_metrics()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import format_metrics, MetricsRegistry, Counter, Gauge, Histogram

reg = MetricsRegistry()
c = Counter("http_requests_total", "Total HTTP requests", labels=["method"])
c.inc(method="GET")
c.inc(method="GET")
c.inc(method="POST")
reg.register(c)

g = Gauge("active_connections", "Active connections")
g.set(42)
reg.register(g)

h = Histogram("request_duration_seconds", "Request duration", buckets=[0.1, 0.5, 1.0])
h.observe(0.05)
h.observe(0.3)
reg.register(h)

output = format_metrics(reg)
assert isinstance(output, str)
assert "# HELP http_requests_total" in output
assert "# TYPE http_requests_total counter" in output
assert 'http_requests_total{method="GET"}' in output or "http_requests_total" in output
assert "# HELP active_connections" in output
assert "# TYPE active_connections gauge" in output
assert "active_connections 42" in output or "active_connections 42.0" in output
assert "# TYPE request_duration_seconds histogram" in output
assert "request_duration_seconds_bucket" in output
assert "request_duration_seconds_count" in output
assert "request_duration_seconds_sum" in output
assert '+Inf' in output
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    print(f"\n{'='*40}")
    print(f"  Score: {score}/{total}")
    if score == total:
        print("  PERFECT! Prometheus metrics mastered!")
    elif score >= 4:
        print("  Great work! Review failed tasks.")
    else:
        print("  Keep practicing with the lesson.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
