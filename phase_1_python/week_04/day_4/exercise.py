"""
Week 4, Day 4: Built-in Functions - Exercise
=============================================

Process server data using Python's powerful built-in functions.

Instructions:
- Complete each function below.
- Do NOT rename the functions or change their parameters.
- Run 'python check.py' to test your solutions.
"""


# TASK 1: get_unhealthy_servers(servers)
# --------------------------------------
# Given a list of server dicts, return a list of server NAMES
# where status is NOT "running".
# Use filter() and map() (or a combination).
#
# Input format: [{"name": "web-01", "status": "running"}, ...]
#
# Examples:
#   get_unhealthy_servers([
#       {"name": "web-01", "status": "running"},
#       {"name": "db-01", "status": "stopped"},
#       {"name": "cache-01", "status": "error"},
#   ])
#   -> ["db-01", "cache-01"]
#
#   get_unhealthy_servers([
#       {"name": "web-01", "status": "running"},
#   ])
#   -> []

# YOUR CODE HERE


# TASK 2: sort_by_cpu(servers)
# ----------------------------
# Sort servers by CPU usage, highest first.
# Return the sorted list of server dicts.
# Use sorted() with a key.
#
# Input format: [{"name": "web-01", "cpu": 85}, ...]
#
# Examples:
#   sort_by_cpu([
#       {"name": "web-01", "cpu": 45},
#       {"name": "db-01", "cpu": 92},
#       {"name": "cache-01", "cpu": 67},
#   ])
#   -> [
#       {"name": "db-01", "cpu": 92},
#       {"name": "cache-01", "cpu": 67},
#       {"name": "web-01", "cpu": 45},
#   ]

# YOUR CODE HERE


# TASK 3: all_servers_healthy(servers)
# ------------------------------------
# Return True if ALL servers have status "running", False otherwise.
# Use the all() function.
#
# Input format: [{"name": "web-01", "status": "running"}, ...]
#
# Examples:
#   all_servers_healthy([
#       {"name": "web-01", "status": "running"},
#       {"name": "db-01", "status": "running"},
#   ])  -> True
#
#   all_servers_healthy([
#       {"name": "web-01", "status": "running"},
#       {"name": "db-01", "status": "stopped"},
#   ])  -> False
#
#   all_servers_healthy([])  -> True  (no unhealthy servers!)

# YOUR CODE HERE


# TASK 4: create_server_report(names, cpu_values, memory_values)
# --------------------------------------------------------------
# Combine three parallel lists into a list of dictionaries using zip().
# Each dict should have keys: "name", "cpu", "memory"
#
# Examples:
#   create_server_report(
#       ["web-01", "db-01"],
#       [85, 45],
#       [70, 60]
#   )
#   -> [
#       {"name": "web-01", "cpu": 85, "memory": 70},
#       {"name": "db-01", "cpu": 45, "memory": 60},
#   ]

# YOUR CODE HERE


# TASK 5: get_server_rankings(servers)
# ------------------------------------
# Return a list of strings showing server rankings by CPU usage.
# Rank from highest CPU to lowest.
# Format: "1. server_name (CPU: XX%)"
# Use sorted(), enumerate(), and any other built-ins you need.
#
# Input format: [{"name": "web-01", "cpu": 85}, ...]
#
# Examples:
#   get_server_rankings([
#       {"name": "web-01", "cpu": 45},
#       {"name": "db-01", "cpu": 92},
#       {"name": "cache-01", "cpu": 67},
#   ])
#   -> [
#       "1. db-01 (CPU: 92%)",
#       "2. cache-01 (CPU: 67%)",
#       "3. web-01 (CPU: 45%)",
#   ]

# YOUR CODE HERE


# TASK 6: any_critical_alerts(servers, cpu_threshold=90, memory_threshold=85)
# ---------------------------------------------------------------------------
# Return True if ANY server exceeds either the CPU or memory threshold.
# Use the any() function.
#
# Input format: [{"name": "web-01", "cpu": 85, "memory": 70}, ...]
#
# Examples:
#   any_critical_alerts([
#       {"name": "web-01", "cpu": 85, "memory": 70},
#       {"name": "db-01", "cpu": 45, "memory": 60},
#   ])  -> False
#
#   any_critical_alerts([
#       {"name": "web-01", "cpu": 95, "memory": 70},
#       {"name": "db-01", "cpu": 45, "memory": 60},
#   ])  -> True
#
#   any_critical_alerts([
#       {"name": "web-01", "cpu": 50, "memory": 90},
#   ])  -> True

# YOUR CODE HERE


# TASK 7: extract_ports(config_strings)
# --------------------------------------
# Given a list of "host:port" strings, extract just the port numbers
# as integers. Use map().
#
# Examples:
#   extract_ports(["web-01:8080", "db-01:5432", "cache-01:6379"])
#       -> [8080, 5432, 6379]
#
#   extract_ports(["localhost:80"])
#       -> [80]

# YOUR CODE HERE
