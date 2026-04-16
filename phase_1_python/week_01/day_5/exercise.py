"""
Week 1, Day 5 - Exercise: Strings Deep Dive

Complete each task below. Run check.py when done.
"""

# ============================================
# TASK 1: Parse a log line
#   Given this log line:
log_line = "2024-03-15 08:45:30 ERROR Disk usage critical on server-12"
#
#   Use string slicing and methods to extract and print:
#     Date: 2024-03-15
#     Time: 08:45:30
#     Level: ERROR
#     Message: Disk usage critical on server-12
#
#   Hints:
#     - Date is characters 0 to 10 (use slicing)
#     - Time is characters 11 to 19
#     - Split the line by spaces, level is the 3rd item (index 2)
#     - Message is everything from character 26 onward
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 2: Build a formatted server status table
#   Given these values:
servers = [
    ("web-01", "running", 45.2),
    ("web-02", "stopped", 0.0),
    ("db-01", "running", 78.9),
]
#
#   Print this EXACT table (use f-strings with alignment):
#   ========================================
#   Server          Status        CPU
#   ----------------------------------------
#   web-01          running      45.2%
#   web-02          stopped       0.0%
#   db-01           running      78.9%
#   ========================================
#
#   Hints:
#     - Use "=" * 40 and "-" * 40 for the lines
#     - Server is left-aligned, 16 chars wide  (:<16)
#     - Status is left-aligned, 10 chars wide  (:<10)
#     - CPU number is right-aligned, 5 chars wide, 1 decimal (:>5.1f)
#     - Don't forget the % after the CPU number
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 3: Extract hostname from URLs
#   Given these URLs:
url1 = "https://api.example.com:8443/v1/health"
url2 = "http://monitoring.internal.net/dashboard"
#
#   Extract and print JUST the hostname from each URL.
#
#   Expected output:
#     Host 1: api.example.com
#     Host 2: monitoring.internal.net
#
#   Hints for url1 (has port):
#     Step 1: Split on "://" and take index [1]  -> "api.example.com:8443/v1/health"
#     Step 2: Split on "/" and take index [0]     -> "api.example.com:8443"
#     Step 3: Split on ":" and take index [0]     -> "api.example.com"
#
#   Hints for url2 (no port):
#     Step 1: Split on "://" and take index [1]  -> "monitoring.internal.net/dashboard"
#     Step 2: Split on "/" and take index [0]     -> "monitoring.internal.net"
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 4: String analysis of a config file
#   Given this multi-line config string:
config = """host=web-server-01
port=8080
environment=production
debug=false
max_retries=3
log_level=ERROR
region=us-east-1"""
#
#   Analyze the config and print:
#     Total lines: 7
#     Contains 'production': True
#     Contains 'staging': False
#     Lines with '=': 7
#     Uppercase config: <the whole config in uppercase>
#
#   Hints:
#     - Use config.count("\n") + 1 for total lines (or split and len)
#     - Use "production" in config for True/False check
#     - Use config.count("=") for counting = signs
#     - Use config.upper() for uppercase version
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 5: Log line processor
#   Given these log lines:
log1 = "  WARNING: High memory usage on prod-web-03  "
log2 = "  error: Connection timeout to db-replica-02  "
log3 = "  INFO: Deployment successful for app-v2.1.0  "
#
#   For EACH log line, clean it up and print:
#     1. Strip whitespace from both ends
#     2. Convert to uppercase
#     3. Check if it starts with "ERROR" (after uppercase)
#     4. Replace "PROD-" with "PRODUCTION-" (after uppercase)
#
#   Expected output:
#     Log 1: WARNING: HIGH MEMORY USAGE ON PRODUCTION-WEB-03
#     Log 1 is error: False
#     Log 2: ERROR: CONNECTION TIMEOUT TO DB-REPLICA-02
#     Log 2 is error: True
#     Log 3: INFO: DEPLOYMENT SUCCESSFUL FOR APP-V2.1.0
#     Log 3 is error: False
#
#   Hints:
#     - Chain methods: log1.strip().upper().replace(...)
#     - Use .startswith("ERROR") to check for errors
# ============================================
# YOUR CODE HERE
