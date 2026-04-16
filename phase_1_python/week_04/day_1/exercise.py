"""
Week 4, Day 1: Functions Basics - Exercise
===========================================

Your first functions! Create reusable tools for server management.

Instructions:
- Complete each function below.
- Do NOT rename the functions or change their parameters.
- Run 'python check.py' to test your solutions.
"""


# TASK 1: is_port_valid(port)
# ---------------------------
# Write a function that checks if a port number is valid.
# Rules:
#   - port must be an integer
#   - port must be between 1 and 65535 (inclusive)
#   - Return True if valid, False otherwise
#
# Examples:
#   is_port_valid(80)     -> True
#   is_port_valid(0)      -> False
#   is_port_valid(70000)  -> False
#   is_port_valid("80")   -> False

# YOUR CODE HERE


# TASK 2: format_hostname(name)
# -----------------------------
# Write a function that cleans up a server hostname.
# Rules:
#   - Remove leading and trailing whitespace
#   - Convert to lowercase
#   - Replace spaces with hyphens
#   - Return the cleaned hostname
#
# Examples:
#   format_hostname("  Web Server 01  ")  -> "web-server-01"
#   format_hostname("DB SERVER")          -> "db-server"
#   format_hostname("cache-01")           -> "cache-01"

# YOUR CODE HERE


# TASK 3: calculate_uptime(total_hours, downtime_hours)
# -----------------------------------------------------
# Write a function that calculates uptime percentage.
# Rules:
#   - uptime = total_hours - downtime_hours
#   - percentage = (uptime / total_hours) * 100
#   - Round to 2 decimal places
#   - If total_hours is 0 or negative, return 0.0
#   - If downtime_hours is negative, treat it as 0
#
# Examples:
#   calculate_uptime(720, 2)    -> 99.72
#   calculate_uptime(100, 0)    -> 100.0
#   calculate_uptime(0, 5)      -> 0.0
#   calculate_uptime(100, -1)   -> 100.0

# YOUR CODE HERE


# TASK 4: create_server_summary(hostname, ip, status)
# ---------------------------------------------------
# Write a function that returns a formatted string summarizing a server.
# Format: "Server: <hostname> | IP: <ip> | Status: <STATUS>"
# Rules:
#   - hostname should be lowercase
#   - status should be UPPERCASE
#
# Examples:
#   create_server_summary("Web01", "10.0.0.1", "running")
#       -> "Server: web01 | IP: 10.0.0.1 | Status: RUNNING"

# YOUR CODE HERE


# TASK 5: get_service_port(service_name)
# --------------------------------------
# Write a function that returns the default port for common services.
# Use a dictionary inside the function to map service names to ports:
#   "http"  -> 80
#   "https" -> 443
#   "ssh"   -> 22
#   "dns"   -> 53
#   "mysql" -> 3306
# Rules:
#   - Convert service_name to lowercase before looking it up
#   - If the service is not found, return -1
#
# Examples:
#   get_service_port("http")   -> 80
#   get_service_port("SSH")    -> 22
#   get_service_port("redis")  -> -1

# YOUR CODE HERE
