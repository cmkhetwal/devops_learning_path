"""
Week 5, Day 6: Practice Day - 5 Mini-Projects
===============================================

Combine everything from this week: file reading, writing, CSV,
JSON, error handling, and logging.

Complete all 5 mini-projects. Run check.py when finished.
"""

import json
import csv
import logging
import os

# === Cleanup from previous runs ===
for f in ["sample_app.log", "log_summary.txt", "managed_config.json",
          "server_report.csv", "processing_results.json",
          "deployment.log", "deploy_summary.txt",
          "good_data.json", "corrupt_data.json"]:
    if os.path.exists(f):
        os.remove(f)

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# === Setup: Create sample data files ===
# (Do NOT modify this section)

sample_log_content = """2024-03-15 09:00:01 INFO Application started on port 8080
2024-03-15 09:00:05 INFO Connected to database db-01
2024-03-15 09:01:12 WARNING Slow query detected: 3.2 seconds
2024-03-15 09:02:30 INFO User login: admin from 10.0.1.50
2024-03-15 09:03:45 ERROR Failed to process request: timeout
2024-03-15 09:04:00 INFO Retry successful for request #1042
2024-03-15 09:05:22 WARNING Memory usage at 82%
2024-03-15 09:06:10 ERROR Database connection lost to db-01
2024-03-15 09:06:15 CRITICAL Service unavailable - no database connection
2024-03-15 09:06:20 INFO Attempting database failover to db-02
2024-03-15 09:06:25 INFO Database failover successful
2024-03-15 09:07:00 WARNING CPU usage at 78%
2024-03-15 09:10:00 INFO Health check passed
2024-03-15 09:15:00 ERROR Disk write failed: /var/log partition full
2024-03-15 09:15:05 CRITICAL Unable to write logs - disk full
2024-03-15 09:15:30 INFO Emergency log rotation triggered
2024-03-15 09:16:00 INFO Disk space recovered, normal operation resumed
2024-03-15 09:20:00 INFO Scheduled backup started
2024-03-15 09:25:00 INFO Backup completed successfully
2024-03-15 09:30:00 INFO Application running normally
"""

with open("sample_app.log", "w") as f:
    f.write(sample_log_content.strip())

with open("good_data.json", "w") as f:
    json.dump({"servers": [{"name": "web-01", "cpu": 45}, {"name": "db-01", "cpu": 72}]}, f)

with open("corrupt_data.json", "w") as f:
    f.write("{invalid json content here!!!")


# ============================================================
# MINI-PROJECT 1: Log File Analyzer
# ============================================================
# Read "sample_app.log" and analyze its contents. Then write
# a summary report to "log_summary.txt".
#
# The summary file must contain EXACTLY this format:
#
# LOG ANALYSIS SUMMARY
# ====================
# Total lines: 20
# INFO: 12
# WARNING: 3
# ERROR: 3
# CRITICAL: 2
# ====================
# ERRORS AND CRITICALS:
# 2024-03-15 09:03:45 ERROR Failed to process request: timeout
# 2024-03-15 09:06:10 ERROR Database connection lost to db-01
# 2024-03-15 09:06:15 CRITICAL Service unavailable - no database connection
# 2024-03-15 09:15:00 ERROR Disk write failed: /var/log partition full
# 2024-03-15 09:15:05 CRITICAL Unable to write logs - disk full
#
# Store the counts in a dict called analyzer_counts with keys:
# "total", "INFO", "WARNING", "ERROR", "CRITICAL"

# YOUR CODE HERE
analyzer_counts = None


# ============================================================
# MINI-PROJECT 2: Config File Manager
# ============================================================
# Write a function called manage_config(filepath, updates=None)
# that:
# - Tries to read a JSON config file
# - If file not found, starts with this default:
#   {"app_name": "default-app", "version": "0.0.0", "port": 8080, "debug": False}
# - If JSON is invalid, starts with the same default
# - If updates is a dictionary, merge it into the config
#   (updates override existing keys)
# - Write the (possibly updated) config to the filepath
# - Return the final config dictionary
#
# Then call it:
# config_result = manage_config("managed_config.json", {"app_name": "my-service", "version": "2.0.0"})

# YOUR CODE HERE
config_result = None


# ============================================================
# MINI-PROJECT 3: CSV Report Generator
# ============================================================
# Given the server data below, generate a CSV file called
# "server_report.csv" with columns:
#   hostname, ip, cpu, memory, status
#
# The "status" column should be computed:
# - If cpu > 90 OR memory > 90: status = "critical"
# - If cpu > 70 OR memory > 70: status = "warning"
# - Otherwise: status = "healthy"
#
# Use csv.DictWriter. Include a header row.
# Store the count of each status in a dict called status_counts
# e.g., {"healthy": 3, "warning": 2, "critical": 1}

server_data = [
    {"hostname": "web-01", "ip": "10.0.1.10", "cpu": 45, "memory": 60},
    {"hostname": "web-02", "ip": "10.0.1.11", "cpu": 72, "memory": 68},
    {"hostname": "web-03", "ip": "10.0.1.12", "cpu": 55, "memory": 50},
    {"hostname": "db-01", "ip": "10.0.2.10", "cpu": 88, "memory": 75},
    {"hostname": "db-02", "ip": "10.0.2.11", "cpu": 92, "memory": 95},
    {"hostname": "cache-01", "ip": "10.0.3.10", "cpu": 30, "memory": 45},
]

# YOUR CODE HERE
status_counts = None


# ============================================================
# MINI-PROJECT 4: Error-Resilient File Processor
# ============================================================
# Write a function called process_files(file_list) that:
# - Takes a list of filenames
# - For each file, tries to open it and parse it as JSON
# - Returns a dict with:
#   "processed": list of dicts with {"file": filename, "data": parsed_data}
#   "errors": list of dicts with {"file": filename, "error": error_message}
#
# Test it with these files:
# file_list = ["good_data.json", "missing_file.json", "corrupt_data.json"]
#
# Store the result in processing_result.
# Also write processing_result to "processing_results.json" with indent=2.

# YOUR CODE HERE
processing_result = None


# ============================================================
# MINI-PROJECT 5: Deployment Logger
# ============================================================
# Simulate a deployment with proper logging:
#
# 1. Create a logger called "deployment" with level DEBUG
# 2. Add a FileHandler for "deployment.log" with level DEBUG
#    format: "%(asctime)s [%(levelname)s] %(message)s"
#    datefmt: "%Y-%m-%d %H:%M:%S"
#
# 3. Define a function called run_deployment(logger, servers, version):
#    - Log "Starting deployment of v{version}" at INFO
#    - For each server:
#      - Log "Deploying to {server}..." at INFO
#      - If server == "web-03": log "FAILED: {server} unreachable" at ERROR
#      - Else: log "SUCCESS: {server} deployed v{version}" at INFO
#    - Count successes and failures
#    - If any failures: log "Deployment completed with {n} failure(s)" at WARNING
#    - If all succeed: log "Deployment completed successfully" at INFO
#    - Return a dict: {"successes": count, "failures": count}
#
# 4. Call it:
#    deploy_result = run_deployment(deploy_logger, ["web-01", "web-02", "web-03", "db-01"], "3.0.0")
#
# 5. Write "deploy_summary.txt" containing:
#    Deployment v3.0.0
#    Successes: {n}
#    Failures: {n}

# YOUR CODE HERE
deploy_result = None


# === Display Results ===
print("=" * 50)
print("RESULTS")
print("=" * 50)
print(f"MP1 - analyzer_counts: {analyzer_counts}")
print(f"MP2 - config_result: {config_result}")
print(f"MP3 - status_counts: {status_counts}")
print(f"MP4 - processing_result files: {len(processing_result['processed']) if processing_result else 0} ok, {len(processing_result['errors']) if processing_result else 0} errors")
print(f"MP5 - deploy_result: {deploy_result}")
