"""
Week 9, Day 5: Container Monitoring

BUILD A CONTAINER MONITORING SYSTEM
====================================

In this exercise you will build a complete container monitoring system
using simulated data.  The patterns here map directly to real Docker
monitoring with the Docker SDK.

TASKS
-----
1. Create a ContainerMetrics class
2. Build a log analyzer
3. Write a threshold alert system
4. Create a monitoring dashboard
5. Generate a monitoring report
"""

import random

# Seed for reproducible results in testing
random.seed(42)


# ============================================================
# TASK 1: ContainerMetrics class
# ============================================================
# Create a class called `ContainerMetrics` with:
#   __init__(self, name, cpu_percent, memory_mb, memory_limit_mb, net_rx, net_tx):
#       - Store all six values as instance attributes with the same names
#       - self.memory_percent = round((memory_mb / memory_limit_mb) * 100, 1)
#
#   Methods:
#       is_healthy():
#           Returns True if cpu_percent < 90 AND memory_percent < 90
#
#       severity():
#           Returns "critical" if cpu > 90 OR mem% > 90
#           Returns "warning"  if cpu > 70 OR mem% > 70
#           Returns "normal"   otherwise
#
#       __repr__():
#           Returns "Metrics(<name>: CPU=<cpu>%, MEM=<mem%>%)"

# YOUR CODE HERE


# ============================================================
# TASK 2: Log analyzer
# ============================================================
# Write a function called `analyze_logs` that:
#   - Takes one argument: log_lines (list of strings)
#   - Each line may contain "INFO", "WARNING", "ERROR", or "DEBUG"
#   - Returns a dictionary:
#       "total"    -> total number of lines
#       "info"     -> count of lines containing "INFO"
#       "warning"  -> count of lines containing "WARNING"
#       "error"    -> count of lines containing "ERROR"
#       "debug"    -> count of lines containing "DEBUG"
#       "other"    -> lines that match none of the above
#       "error_rate" -> errors / total * 100, rounded to 1 decimal (0.0 if total is 0)
#   - Prints "Log Analysis: X lines, Y errors (Z%)"

# YOUR CODE HERE


# ============================================================
# TASK 3: Alert system
# ============================================================
# Write a function called `check_alerts` that:
#   - Takes two arguments: metrics_list (list of ContainerMetrics),
#     thresholds (dict with keys "cpu_warning", "cpu_critical",
#                 "mem_warning", "mem_critical")
#   - Default thresholds if not provided: cpu_warning=70, cpu_critical=90,
#     mem_warning=70, mem_critical=90
#   - Returns a list of alert dicts, each with:
#       "container": container name
#       "type": "cpu" or "memory"
#       "level": "warning" or "critical"
#       "value": the actual value
#   - Prints each alert as "[LEVEL] <container>: <type> at <value>%"
#   - If no alerts, prints "All containers healthy"

# YOUR CODE HERE


# ============================================================
# TASK 4: Monitoring dashboard
# ============================================================
# Write a function called `print_dashboard` that:
#   - Takes one argument: metrics_list (list of ContainerMetrics)
#   - Prints a formatted dashboard:
#
#     Container Monitoring Dashboard
#     ==============================
#     NAME                 CPU%     MEM(MB)  MEM%     STATUS
#     <name>               <cpu>    <mem>    <mem%>   <severity>
#     ...
#     ------------------------------
#     Containers: X total, Y healthy, Z unhealthy
#
#   - NAME: 20 chars left-aligned
#   - CPU%: 6 chars right-aligned, 1 decimal
#   - MEM(MB): 8 chars right-aligned, 1 decimal
#   - MEM%: 6 chars right-aligned, 1 decimal
#   - STATUS: severity() value
#   - Returns a dict: {"total": X, "healthy": Y, "unhealthy": Z}

# YOUR CODE HERE


# ============================================================
# TASK 5: Monitoring report
# ============================================================
# Write a function called `generate_monitoring_report` that:
#   - Takes two arguments: metrics_list (list of ContainerMetrics),
#     log_lines (list of strings)
#   - Calls print_dashboard(metrics_list) and analyze_logs(log_lines)
#   - Calls check_alerts(metrics_list, None) using default thresholds
#   - Returns a dict summarizing everything:
#       "containers_total": number of containers
#       "containers_healthy": number healthy
#       "total_alerts": number of alerts
#       "log_errors": number of error log lines
#       "overall_status": "OK" if 0 alerts and error_rate < 5,
#                         "WARNING" if alerts exist but all are "warning" level,
#                         "CRITICAL" if any alert is "critical" level or error_rate >= 10
#   - Prints "Overall Status: <overall_status>"

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  WEEK 9, DAY 5 - Container Monitoring")
    print("=" * 55)

    # Task 1 test
    print("\n--- Task 1: ContainerMetrics ---")
    m1 = ContainerMetrics("web-1", 45.2, 256, 512, 10000, 5000)
    m2 = ContainerMetrics("api-1", 85.0, 480, 512, 30000, 15000)
    m3 = ContainerMetrics("db-1", 92.5, 450, 512, 5000, 2000)
    print(repr(m1))
    print(repr(m2))
    print(repr(m3))
    print(f"web-1 healthy: {m1.is_healthy()}, severity: {m1.severity()}")
    print(f"api-1 healthy: {m2.is_healthy()}, severity: {m2.severity()}")
    print(f"db-1 healthy: {m3.is_healthy()}, severity: {m3.severity()}")

    # Task 2 test
    print("\n--- Task 2: Log Analysis ---")
    sample_logs = [
        "INFO: Request processed in 45ms",
        "INFO: Connection from 10.0.0.5",
        "WARNING: Slow query: 1200ms",
        "ERROR: Connection refused to database",
        "INFO: Cache hit for key user_123",
        "ERROR: Timeout waiting for response",
        "DEBUG: Checking health endpoint",
        "INFO: Request processed in 12ms",
        "WARNING: Memory usage above 70%",
        "INFO: Scheduled task completed",
    ]
    log_result = analyze_logs(sample_logs)
    for k, v in log_result.items():
        print(f"  {k}: {v}")

    # Task 3 test
    print("\n--- Task 3: Alert System ---")
    metrics = [m1, m2, m3]
    alerts = check_alerts(metrics, None)
    print(f"Total alerts: {len(alerts)}")

    # Task 4 test
    print("\n--- Task 4: Dashboard ---")
    m4 = ContainerMetrics("cache-1", 12.3, 64, 256, 8000, 4000)
    m5 = ContainerMetrics("worker-1", 55.8, 200, 512, 2000, 1000)
    all_metrics = [m1, m2, m3, m4, m5]
    summary = print_dashboard(all_metrics)
    print(f"Dashboard summary: {summary}")

    # Task 5 test
    print("\n--- Task 5: Full Report ---")
    report = generate_monitoring_report(all_metrics, sample_logs)
    print(f"Report: {report}")
