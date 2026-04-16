"""
Week 10, Day 5: CloudWatch & Lambda with boto3

MONITORING AND SERVERLESS FUNCTIONS
=====================================

In this exercise you will build CloudWatch monitoring and Lambda invocation
patterns using mock data.  These are the exact patterns used in production
AWS environments.

TASKS
-----
1. Create a MockCloudWatch class
2. Build a metric analyzer
3. Implement an alarm manager
4. Create a MockLambda class
5. Build a monitoring + alerting pipeline
"""

import json
import os
from datetime import datetime, timedelta

OUTPUT_DIR = "/home/cmk/python/devops-python-path/week_10/day_5/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# TASK 1: MockCloudWatch class
# ============================================================
# Create a class called `MockCloudWatch` with:
#   __init__(self):
#       - self.alarms = {}     # alarm_name -> alarm config dict
#       - self.metrics = []    # list of metric data points
#
#   Methods:
#       put_metric_data(namespace, metric_name, value, instance_id="i-000"):
#           - Appends a dict to self.metrics:
#               {"Namespace": namespace, "MetricName": metric_name,
#                "Value": value, "InstanceId": instance_id,
#                "Timestamp": "2024-03-15T10:00:00Z"}
#           - Print "Metric: <namespace>/<metric_name> = <value>"
#
#       get_metric_statistics(namespace, metric_name, points=6):
#           - Returns a list of <points> dicts simulating metric data.
#             For each point i (0 to points-1):
#               {"Timestamp": f"2024-03-15T{10+i:02d}:00:00Z",
#                "Average": 30.0 + i * 5.0,
#                "Maximum": 35.0 + i * 5.0,
#                "Minimum": 25.0 + i * 5.0}
#           (This creates a rising metric pattern for testing.)
#
#       put_alarm(name, metric_name, threshold, comparison="GreaterThanThreshold"):
#           - Stores alarm in self.alarms:
#               {"AlarmName": name, "MetricName": metric_name,
#                "Threshold": threshold, "Comparison": comparison,
#                "State": "OK"}
#           - Print "Created alarm: <name> (<metric> > <threshold>)"
#
#       check_alarms(current_values):
#           - current_values is a dict: {metric_name: current_value}
#           - For each alarm, check if the current value triggers it:
#               "GreaterThanThreshold": value > threshold -> State = "ALARM"
#               Otherwise: State = "OK"
#           - Returns list of alarm dicts that are in "ALARM" state
#           - Print "[ALARM] <name>: <metric> = <value> (threshold: <threshold>)"
#             for each triggered alarm

# YOUR CODE HERE


# ============================================================
# TASK 2: Metric analyzer
# ============================================================
# Write a function called `analyze_metrics` that:
#   - Takes two arguments: cw (MockCloudWatch), namespace (str), metric_name (str)
#   - Gets metric statistics (6 points) using cw.get_metric_statistics()
#   - Returns a dict:
#       "metric": "<namespace>/<metric_name>"
#       "points": number of data points
#       "avg_of_averages": mean of all Average values, rounded to 1 decimal
#       "peak": highest Maximum value
#       "trend": "rising" if last Average > first Average,
#                "falling" if last < first, "stable" otherwise
#   - Prints formatted table:
#       Metric: <namespace>/<metric_name>
#       TIME         AVG      MAX      MIN
#       <timestamp>  <avg>    <max>    <min>
#       ...
#       Trend: <trend>

# YOUR CODE HERE


# ============================================================
# TASK 3: Alarm manager
# ============================================================
# Write a function called `setup_monitoring_alarms` that:
#   - Takes one argument: cw (MockCloudWatch)
#   - Creates these alarms:
#       Name: "HighCPU"      metric: "CPUUtilization"     threshold: 80.0
#       Name: "HighMemory"   metric: "MemoryUtilization"  threshold: 85.0
#       Name: "HighDisk"     metric: "DiskUtilization"    threshold: 90.0
#       Name: "HighNetwork"  metric: "NetworkIn"          threshold: 1000000.0
#   - Then checks alarms against these current values:
#       {"CPUUtilization": 82.5, "MemoryUtilization": 60.0,
#        "DiskUtilization": 95.0, "NetworkIn": 500000.0}
#   - Returns the list of triggered alarms
#   - Prints "Alarms triggered: X of Y"

# YOUR CODE HERE


# ============================================================
# TASK 4: MockLambda class
# ============================================================
# Create a class called `MockLambda` with:
#   __init__(self):
#       - self.functions = {}  # name -> {"handler": callable, "invocations": int}
#
#   Methods:
#       create_function(name, handler):
#           - handler is a Python callable (function)
#           - Store it in self.functions
#           - Print "Created Lambda: <name>"
#
#       invoke(name, payload):
#           - payload is a dict
#           - Call the handler function: result = handler(payload)
#           - Increment invocations count
#           - Print "Invoked <name> (invocation #X)"
#           - Return {"StatusCode": 200, "Payload": result}
#           - If function not found, return {"StatusCode": 404, "Payload": "Function not found"}
#
#       list_functions():
#           - Return list of dicts: [{"Name": name, "Invocations": count}, ...]

# YOUR CODE HERE


# ============================================================
# TASK 5: Monitoring + alerting pipeline
# ============================================================
# Write a function called `monitoring_pipeline` that:
#   - Takes two arguments: cw (MockCloudWatch), lmb (MockLambda)
#   - Creates a Lambda function called "alert-handler" with this handler:
#       def alert_handler(event):
#           return {"status": "alert_processed", "alarm": event.get("alarm", "unknown"),
#                   "message": f"Alert for {event.get('alarm', 'unknown')} processed"}
#   - Sets up the 4 monitoring alarms using setup_monitoring_alarms(cw)
#   - For each triggered alarm, invokes the "alert-handler" Lambda with:
#       {"alarm": alarm["AlarmName"], "value": <current_value>, "threshold": alarm["Threshold"]}
#   - Returns dict:
#       "alarms_total": number of alarms created
#       "alarms_triggered": number triggered
#       "alerts_processed": number of Lambda invocations made
#       "functions": result of lmb.list_functions()
#   - Prints "Pipeline complete: X alerts processed"

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  WEEK 10, DAY 5 - CloudWatch & Lambda")
    print("=" * 60)

    # Task 1 test
    print("\n--- Task 1: MockCloudWatch ---")
    cw = MockCloudWatch()
    cw.put_metric_data("AWS/EC2", "CPUUtilization", 75.5, "i-abc123")
    stats = cw.get_metric_statistics("AWS/EC2", "CPUUtilization")
    print(f"Data points: {len(stats)}")
    cw.put_alarm("TestAlarm", "CPUUtilization", 80.0)
    triggered = cw.check_alarms({"CPUUtilization": 85.0})
    print(f"Triggered: {len(triggered)}")

    # Task 2 test
    print("\n--- Task 2: Metric Analyzer ---")
    analysis = analyze_metrics(cw, "AWS/EC2", "CPUUtilization")
    for k, v in analysis.items():
        print(f"  {k}: {v}")

    # Task 3 test
    print("\n--- Task 3: Alarm Manager ---")
    cw2 = MockCloudWatch()
    triggered_alarms = setup_monitoring_alarms(cw2)
    for a in triggered_alarms:
        print(f"  Triggered: {a['AlarmName']}")

    # Task 4 test
    print("\n--- Task 4: MockLambda ---")
    lmb = MockLambda()
    lmb.create_function("hello", lambda event: {"message": f"Hello {event.get('name', 'World')}"})
    result = lmb.invoke("hello", {"name": "DevOps"})
    print(f"Lambda result: {result}")
    funcs = lmb.list_functions()
    print(f"Functions: {funcs}")

    # Task 5 test
    print("\n--- Task 5: Monitoring Pipeline ---")
    cw3 = MockCloudWatch()
    lmb2 = MockLambda()
    pipeline_result = monitoring_pipeline(cw3, lmb2)
    print(f"Pipeline result: {pipeline_result}")
