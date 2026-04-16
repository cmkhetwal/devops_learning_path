"""
Week 2, Day 5: Loop Control - Exercise
========================================
Complete each task below. Replace '# YOUR CODE HERE' with your solution.
Run 'python check.py' when you are done to see your score!
"""

# ---------------------------------------------------------------------------
# TASK 1: Search Through Logs
# ---------------------------------------------------------------------------
# Loop through log_entries. When you find an entry that contains "ERROR",
# print: "Found error: <the entry>"
# Then break out of the loop.
# If no error is found (loop finishes without break), print:
#   "No errors found"
# Use the for/else pattern!
#
# Expected output (with the given data):
#   Found error: ERROR: Connection timeout on db-01

log_entries = [
    "INFO: Server started",
    "INFO: Listening on port 8080",
    "WARNING: High memory usage",
    "ERROR: Connection timeout on db-01",
    "INFO: Request processed",
    "ERROR: Disk full"
]

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 2: Skip Failed Servers
# ---------------------------------------------------------------------------
# Loop through all_servers. If a server is in the failed_servers list,
# print: "Skipping <server> (failed)"
# and use continue to skip it.
# For all other servers, print: "Deploying to <server>"
#
# Expected output:
#   Deploying to web-01
#   Skipping web-02 (failed)
#   Deploying to web-03
#   Deploying to web-04
#   Skipping web-05 (failed)

all_servers = ["web-01", "web-02", "web-03", "web-04", "web-05"]
failed_servers = ["web-02", "web-05"]

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 3: Find First Available Port
# ---------------------------------------------------------------------------
# The list used_ports contains ports that are already in use.
# Loop through range(3000, 3011) and find the FIRST port that is NOT in
# used_ports.
# Skip used ports with continue.
# When you find an available one, print: "First available port: <port>"
# and break.
# If all ports are used (no break), print: "No available ports"
#
# Expected output:
#   First available port: 3005

used_ports = [3000, 3001, 3002, 3003, 3004]

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 4: Server-Port Matrix
# ---------------------------------------------------------------------------
# Use nested loops to print every combination of server and port.
# Format: "<server>:<port>"
#
# Expected output:
#   app-01:80
#   app-01:443
#   app-02:80
#   app-02:443
#   app-03:80
#   app-03:443

matrix_servers = ["app-01", "app-02", "app-03"]
matrix_ports = [80, 443]

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 5: Process Log Until Marker
# ---------------------------------------------------------------------------
# Loop through log_data. For each line:
#   - If the line is empty (an empty string ""), use continue to skip it
#   - If the line is "---END---", print "End marker found" and break
#   - Otherwise, print the line
#
# After the loop, print: "Processing complete"
#
# Expected output:
#   Starting backup
#   Copying files
#   Verifying integrity
#   End marker found
#   Processing complete

log_data = [
    "Starting backup",
    "",
    "Copying files",
    "",
    "Verifying integrity",
    "---END---",
    "This should not appear",
    "Neither should this"
]

# YOUR CODE HERE
