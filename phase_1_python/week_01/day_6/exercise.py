"""
Week 1, Day 6 - Exercise: Practice Day - Mini-Projects

Combine everything from Week 1: print, variables, input, math, strings.

Instructions:
- Complete each mini-project below
- Run this file: python3 exercise.py
- Check your work: python3 check.py
"""

# ============================================================
# MINI-PROJECT 1: Server Info Card
# ============================================================
# Create these variables for a server:
#   hostname     -> "prod-web-07"
#   ip_address   -> "10.0.5.27"
#   os_type      -> "Ubuntu 22.04"
#   cpu_cores    -> 4
#   memory_gb    -> 16.0
#   disk_gb      -> 500
#   is_active    -> True
#
# Then print a formatted info card that looks EXACTLY like this:
#
#   ╔══════════════════════════════╗
#   ║       SERVER INFO CARD       ║
#   ╠══════════════════════════════╣
#   ║ Hostname : prod-web-07       ║
#   ║ IP       : 10.0.5.27         ║
#   ║ OS       : Ubuntu 22.04      ║
#   ║ CPU      : 4 cores            ║
#   ║ Memory   : 16.0 GB            ║
#   ║ Disk     : 500 GB             ║
#   ║ Active   : True               ║
#   ╚══════════════════════════════╝
#
# IMPORTANT: Use f-strings with your variables for the data lines.
# The border lines can be plain print statements.
# Don't worry about perfect spacing on the right border -- the
# checker only looks for the data values, not exact box alignment.
# ============================================================
# YOUR CODE HERE


# ============================================================
# MINI-PROJECT 2: Simple Calculator
# ============================================================
# This calculator takes two numbers and shows all operations.
#
# The two numbers are given to you (do NOT use input()):
num1 = 120
num2 = 7
#
# Using num1 and num2, print EXACTLY these lines:
#   === Simple Calculator ===
#   Number 1: 120
#   Number 2: 7
#   Addition:       120 + 7 = 127
#   Subtraction:    120 - 7 = 113
#   Multiplication: 120 * 7 = 840
#   Division:       120 / 7 = 17.14
#   Floor Division: 120 // 7 = 17
#   Modulo:         120 % 7 = 1
#   Power:          120 ** 7 = 358318080000000
#
# RULES:
#   - Calculate each result using Python (don't hardcode answers)
#   - For Division, round to 2 decimal places using round()
# ============================================================
# YOUR CODE HERE


# ============================================================
# MINI-PROJECT 3: Log Line Builder
# ============================================================
# Build formatted log messages from these variables:
log_date = "2024-01-15"
log_time = "10:30:00"
log_level = "INFO"
log_message = "Server started on port 8080"
#
# Using the variables above, print EXACTLY:
#   [2024-01-15 10:30:00] [INFO] Server started on port 8080
#
# Then create a second log line with these variables:
error_date = "2024-01-15"
error_time = "10:35:22"
error_level = "ERROR"
error_message = "Connection refused to database on port 5432"
#
# Print EXACTLY:
#   [2024-01-15 10:35:22] [ERROR] Connection refused to database on port 5432
#
# Then create a third log line with these variables:
warn_date = "2024-01-15"
warn_time = "10:40:05"
warn_level = "WARNING"
warn_message = "Disk usage at 85%"
#
# Print EXACTLY:
#   [2024-01-15 10:40:05] [WARNING] Disk usage at 85%
#
# RULES:
#   - Use f-strings to build each log line
#   - Use the variables, do not hardcode the values
# ============================================================
# YOUR CODE HERE


# ============================================================
# MINI-PROJECT 4: String Processor
# ============================================================
# You received a messy hostname from a monitoring system.
# Clean it up step by step.
messy_hostname = "  WEB-Server-01.Example.COM  "
#
# Step 1: Strip the whitespace and print:
#   Step 1 - Stripped: WEB-Server-01.Example.COM
#
# Step 2: Convert to lowercase and print:
#   Step 2 - Lowercase: web-server-01.example.com
#
# Step 3: Replace all hyphens with underscores and print:
#   Step 3 - Underscores: web_server_01.example.com
#
# Step 4: Extract just the server name (everything before the
#         first dot). Print:
#   Step 4 - Server name: web_server_01
#
#   HINT: Use .find(".") to get the position of the first dot,
#         then use slicing [:position] to get everything before it.
#
# Step 5: Print the length of the final server name:
#   Step 5 - Name length: 15
#
# RULES:
#   - Start from messy_hostname and chain the steps
#   - Print each step exactly as shown above
# ============================================================
# YOUR CODE HERE


# ============================================================
# MINI-PROJECT 5: Deployment Summary
# ============================================================
# You are writing a script that prints a deployment report.
# Here is the data:
app_name = "payment-service"
version = "3.2.1"
total_servers = 12
successful = 11
failed = 1
deploy_time_seconds = 185
#
# Calculate:
#   success_rate   -> percentage of successful deployments (successful/total * 100)
#                     round to 1 decimal place
#   fail_rate      -> percentage of failed deployments (failed/total * 100)
#                     round to 1 decimal place
#   deploy_minutes -> deploy_time_seconds converted to minutes (use floor division)
#   deploy_remaining_secs -> the leftover seconds (use modulo)
#
# Then print EXACTLY this report:
#
#   ========== DEPLOYMENT SUMMARY ==========
#   Application: payment-service v3.2.1
#   Servers:     12 total
#   Successful:  11 (91.7%)
#   Failed:      1 (8.3%)
#   Duration:    3 min 5 sec
#   ========================================
#   Status: ISSUES DETECTED
#
# NOTES:
#   - "Status" is "ALL CLEAR" if failed == 0, otherwise "ISSUES DETECTED"
#   - Use f-strings for all data lines
#   - Calculate everything with Python, do not hardcode numbers
# ============================================================
# YOUR CODE HERE
