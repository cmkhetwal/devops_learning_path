"""
Week 4, Day 7: Phase 1 Final Test
===================================

15 comprehensive questions covering ALL topics from Weeks 1-4.
This is your final exam for Phase 1 of the Python for DevOps learning path.

Instructions:
- Complete each function below.
- Do NOT rename the functions or change their parameters.
- Run 'python check.py' to grade your test.
- Aim for 15/15!
"""


# =====================================================================
# WEEK 1 REVIEW: Variables, Strings, Types
# =====================================================================

# Q1: format_server_label(name, env, port)
# -----------------------------------------
# Return a formatted string: "[ENV] name:port"
# Rules:
#   - env should be UPPERCASE
#   - name should be lowercase
#   - port should be an integer in the string
#
# Examples:
#   format_server_label("Web-01", "production", 8080)
#       -> "[PRODUCTION] web-01:8080"
#   format_server_label("DB-Master", "staging", 5432)
#       -> "[STAGING] db-master:5432"

# YOUR CODE HERE


# Q2: parse_log_entry(log_string)
# --------------------------------
# Parse a log string in the format "LEVEL:TIMESTAMP:MESSAGE"
# Return a dictionary with keys: "level", "timestamp", "message"
#
# Examples:
#   parse_log_entry("ERROR:2024-01-15:Disk full")
#       -> {"level": "ERROR", "timestamp": "2024-01-15", "message": "Disk full"}
#   parse_log_entry("INFO:2024-01-15:Server started")
#       -> {"level": "INFO", "timestamp": "2024-01-15", "message": "Server started"}

# YOUR CODE HERE


# =====================================================================
# WEEK 2 REVIEW: Control Flow
# =====================================================================

# Q3: categorize_response_time(ms)
# ---------------------------------
# Categorize a server response time in milliseconds:
#   - Less than 100: "fast"
#   - 100 to 500 (inclusive): "normal"
#   - 501 to 1000 (inclusive): "slow"
#   - Above 1000: "critical"
#
# Examples:
#   categorize_response_time(50)    -> "fast"
#   categorize_response_time(100)   -> "normal"
#   categorize_response_time(500)   -> "normal"
#   categorize_response_time(501)   -> "slow"
#   categorize_response_time(1500)  -> "critical"

# YOUR CODE HERE


# Q4: count_status_codes(status_codes)
# -------------------------------------
# Given a list of HTTP status codes, count how many are in each category:
#   - "2xx": codes 200-299
#   - "3xx": codes 300-399
#   - "4xx": codes 400-499
#   - "5xx": codes 500-599
# Return a dictionary with the counts.
#
# Examples:
#   count_status_codes([200, 200, 404, 500, 301, 200, 503])
#       -> {"2xx": 3, "3xx": 1, "4xx": 1, "5xx": 2}
#   count_status_codes([])
#       -> {"2xx": 0, "3xx": 0, "4xx": 0, "5xx": 0}

# YOUR CODE HERE


# Q5: retry_operation(max_retries, results)
# ------------------------------------------
# Simulate retrying an operation. Given a list of results ("success" or "fail"),
# iterate through them and return the attempt number (1-based) of the first
# success, or -1 if all attempts up to max_retries fail.
#
# Rules:
#   - Only try up to max_retries times
#   - Return the 1-based attempt number on first success
#   - Return -1 if no success within max_retries
#
# Examples:
#   retry_operation(3, ["fail", "fail", "success"])          -> 3
#   retry_operation(3, ["fail", "success", "fail"])          -> 2
#   retry_operation(2, ["fail", "fail", "success"])          -> -1
#   retry_operation(5, ["success"])                          -> 1
#   retry_operation(3, ["fail", "fail", "fail"])             -> -1

# YOUR CODE HERE


# =====================================================================
# WEEK 3 REVIEW: Data Structures
# =====================================================================

# Q6: deduplicate_servers(server_list)
# -------------------------------------
# Remove duplicate server names from a list while preserving order.
# Return a new list with duplicates removed (keep first occurrence).
#
# Examples:
#   deduplicate_servers(["web-01", "db-01", "web-01", "cache-01", "db-01"])
#       -> ["web-01", "db-01", "cache-01"]
#   deduplicate_servers(["web-01"])
#       -> ["web-01"]
#   deduplicate_servers([])
#       -> []

# YOUR CODE HERE


# Q7: merge_configs(default_config, override_config)
# ---------------------------------------------------
# Merge two configuration dictionaries. Values in override_config should
# replace values in default_config. Include all keys from both dicts.
# Do NOT modify either input dictionary.
#
# Examples:
#   merge_configs(
#       {"port": 8080, "host": "localhost", "debug": False},
#       {"port": 9090, "debug": True}
#   )
#   -> {"port": 9090, "host": "localhost", "debug": True}
#
#   merge_configs({"a": 1}, {"b": 2})
#   -> {"a": 1, "b": 2}

# YOUR CODE HERE


# Q8: find_common_tags(server_tags)
# ----------------------------------
# Given a dictionary where keys are server names and values are lists of tags,
# find tags that appear on ALL servers.
# Return a sorted list of common tags.
#
# Examples:
#   find_common_tags({
#       "web-01": ["prod", "us-east", "web"],
#       "web-02": ["prod", "us-west", "web"],
#       "db-01": ["prod", "us-east", "database"],
#   })
#   -> ["prod"]
#
#   find_common_tags({
#       "web-01": ["prod", "web"],
#       "web-02": ["prod", "web"],
#   })
#   -> ["prod", "web"]
#
#   find_common_tags({})
#   -> []

# YOUR CODE HERE


# =====================================================================
# WEEK 4 REVIEW: Functions & Modules
# =====================================================================

# Q9: create_server_factory(default_region="us-east-1", default_size="t2.micro")
# -------------------------------------------------------------------------------
# Return a function that creates server dictionaries.
# The returned function should accept (name) and return a dict with:
#   "name", "region", "size"
# The region and size come from the factory's defaults.
#
# Examples:
#   make_server = create_server_factory()
#   make_server("web-01")
#       -> {"name": "web-01", "region": "us-east-1", "size": "t2.micro"}
#
#   make_eu_server = create_server_factory(default_region="eu-west-1")
#   make_eu_server("db-01")
#       -> {"name": "db-01", "region": "eu-west-1", "size": "t2.micro"}

# YOUR CODE HERE


# Q10: apply_to_all(func, items)
# --------------------------------
# Apply a function to all items and return the results as a list.
# (This is like writing your own version of map().)
#
# Examples:
#   apply_to_all(str.upper, ["hello", "world"])
#       -> ["HELLO", "WORLD"]
#   apply_to_all(lambda x: x * 2, [1, 2, 3])
#       -> [2, 4, 6]
#   apply_to_all(len, ["hi", "hello", "hey"])
#       -> [2, 5, 3]

# YOUR CODE HERE


# Q11: filter_and_sort_servers(servers, min_cpu=0, sort_by="name")
# ----------------------------------------------------------------
# Filter servers where CPU >= min_cpu, then sort by the given key.
# Return the filtered and sorted list.
#
# Input: list of dicts with keys "name", "cpu", "memory"
# sort_by can be "name", "cpu", or "memory"
#
# Examples:
#   servers = [
#       {"name": "web-01", "cpu": 85, "memory": 70},
#       {"name": "db-01", "cpu": 45, "memory": 90},
#       {"name": "cache-01", "cpu": 92, "memory": 40},
#   ]
#   filter_and_sort_servers(servers, min_cpu=50, sort_by="cpu")
#   -> [
#       {"name": "web-01", "cpu": 85, "memory": 70},
#       {"name": "cache-01", "cpu": 92, "memory": 40},
#   ]

# YOUR CODE HERE


# =====================================================================
# COMBINED SKILLS
# =====================================================================

# Q12: generate_inventory(server_groups)
# ----------------------------------------
# Given a dictionary of groups (key=group_name, value=list of server names),
# generate an inventory string in this format:
#
# [group_name]
# server1
# server2
#
# [group_name2]
# server3
#
# Rules:
#   - Groups should be in alphabetical order
#   - Servers within each group should be in alphabetical order
#   - One blank line between groups
#   - No trailing blank line
#
# Examples:
#   generate_inventory({
#       "webservers": ["web-02", "web-01"],
#       "databases": ["db-01"],
#   })
#   -> "[databases]\ndb-01\n\n[webservers]\nweb-01\nweb-02"

# YOUR CODE HERE


# Q13: analyze_logs(log_lines)
# -----------------------------
# Analyze a list of log lines and return a summary dictionary.
# Each log line is in the format: "LEVEL: message"
# (LEVEL is one of: INFO, WARNING, ERROR)
#
# Return:
#   {
#       "total": total number of lines,
#       "info": count of INFO lines,
#       "warning": count of WARNING lines,
#       "error": count of ERROR lines,
#       "most_common": the level with the highest count (lowercase),
#       "error_messages": list of messages from ERROR lines (in order)
#   }
#
# If there's a tie for most_common, pick the first one alphabetically
# (e.g., "error" before "info").
#
# Examples:
#   analyze_logs([
#       "INFO: Server started",
#       "INFO: Listening on port 8080",
#       "ERROR: Connection refused",
#       "WARNING: High memory usage",
#       "ERROR: Disk full",
#   ])
#   -> {
#       "total": 5,
#       "info": 2,
#       "warning": 1,
#       "error": 2,
#       "most_common": "error",
#       "error_messages": ["Connection refused", "Disk full"]
#   }

# YOUR CODE HERE


# Q14: build_pipeline(*steps)
# ----------------------------
# Create a deployment pipeline from step functions.
# Each step is a tuple: (step_name, function)
# Run each function in order and collect results.
# Return a list of dicts:
#   [{"step": name, "result": function_return_value}, ...]
#
# If a function returns "FAIL", stop the pipeline and add
#   {"step": "PIPELINE", "result": "FAILED at <step_name>"}
# as the last entry.
#
# If all succeed, add:
#   {"step": "PIPELINE", "result": "SUCCESS"}
# as the last entry.
#
# Examples:
#   build_pipeline(
#       ("validate", lambda: "OK"),
#       ("build", lambda: "OK"),
#       ("deploy", lambda: "OK"),
#   )
#   -> [
#       {"step": "validate", "result": "OK"},
#       {"step": "build", "result": "OK"},
#       {"step": "deploy", "result": "OK"},
#       {"step": "PIPELINE", "result": "SUCCESS"},
#   ]
#
#   build_pipeline(
#       ("validate", lambda: "OK"),
#       ("build", lambda: "FAIL"),
#       ("deploy", lambda: "OK"),
#   )
#   -> [
#       {"step": "validate", "result": "OK"},
#       {"step": "build", "result": "FAIL"},
#       {"step": "PIPELINE", "result": "FAILED at build"},
#   ]

# YOUR CODE HERE


# Q15: create_monitoring_report(servers, alert_rules)
# ----------------------------------------------------
# Generate a monitoring report for a list of servers.
#
# servers: list of dicts with keys "name", "cpu", "memory", "disk"
# alert_rules: dict with keys "cpu", "memory", "disk" and threshold values
#
# Return a dictionary:
#   {
#       "total_servers": int,
#       "healthy_count": int,
#       "unhealthy_count": int,
#       "alerts": [
#           {"server": name, "metric": metric_name, "value": value, "threshold": threshold},
#           ...
#       ],
#       "summary": "All servers healthy" or "X alerts on Y servers"
#   }
#
# Rules:
#   - A server is "unhealthy" if ANY metric exceeds its threshold
#   - Sort alerts by server name, then by metric name
#   - In the summary, X = total number of alerts, Y = number of unhealthy servers
#
# Examples:
#   create_monitoring_report(
#       [
#           {"name": "web-01", "cpu": 95, "memory": 70, "disk": 60},
#           {"name": "db-01", "cpu": 50, "memory": 88, "disk": 75},
#           {"name": "cache-01", "cpu": 40, "memory": 30, "disk": 20},
#       ],
#       {"cpu": 90, "memory": 85, "disk": 80}
#   )
#   -> {
#       "total_servers": 3,
#       "healthy_count": 1,
#       "unhealthy_count": 2,
#       "alerts": [
#           {"server": "db-01", "metric": "memory", "value": 88, "threshold": 85},
#           {"server": "web-01", "metric": "cpu", "value": 95, "threshold": 90},
#       ],
#       "summary": "2 alerts on 2 servers"
#   }

# YOUR CODE HERE
