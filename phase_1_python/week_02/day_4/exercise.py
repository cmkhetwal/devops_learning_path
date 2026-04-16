"""
Week 2, Day 4: For Loops - Exercise
=====================================
Complete each task below. Replace '# YOUR CODE HERE' with your solution.
Run 'python check.py' when you are done to see your score!
"""

# ---------------------------------------------------------------------------
# TASK 1: Ping All Servers
# ---------------------------------------------------------------------------
# Loop through the list of servers and print a ping message for each one.
# For each server, print: "Pinging <server>..."
#
# Expected output:
#   Pinging web-01...
#   Pinging web-02...
#   Pinging db-01...
#   Pinging cache-01...

servers = ["web-01", "web-02", "db-01", "cache-01"]

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 2: Print Port Range
# ---------------------------------------------------------------------------
# Use a for loop with range() to print ports from 8080 to 8084 (inclusive).
# For each port, print just the number.
#
# Expected output:
#   8080
#   8081
#   8082
#   8083
#   8084

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 3: Count Production Servers
# ---------------------------------------------------------------------------
# Loop through the list of environments and count how many are "production".
# After the loop, print: "Production servers: X"
#
# Expected output:
#   Production servers: 3

environments = ["production", "staging", "production", "development", "production"]
prod_count = 0

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 4: Numbered Server List
# ---------------------------------------------------------------------------
# Loop through the server list and print each server with its number.
# Use enumerate() or a counter variable.
# Print: "X. <server>"  where X starts at 1.
#
# Expected output:
#   1. app-server
#   2. db-server
#   3. cache-server
#   4. log-server

server_list = ["app-server", "db-server", "cache-server", "log-server"]

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 5: Generate IP Addresses
# ---------------------------------------------------------------------------
# Use a for loop to generate IP addresses from 192.168.1.1 to 192.168.1.5
# (use range(1, 6) for the last octet).
# Print each IP address on its own line.
#
# Expected output:
#   192.168.1.1
#   192.168.1.2
#   192.168.1.3
#   192.168.1.4
#   192.168.1.5

# YOUR CODE HERE
