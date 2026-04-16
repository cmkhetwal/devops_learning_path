"""
Week 5, Day 1: Exercise - Reading Files
========================================

Today you will practice reading files in Python.
All sample data files are created for you automatically below.

Complete all 5 tasks. Run check.py when finished to verify your work.
"""

# === Setup: Create sample data files ===
# (Do NOT modify this section)

sample_log = """2024-01-15 08:01:23 INFO Server web-01 started successfully
2024-01-15 08:01:45 INFO Server web-02 started successfully
2024-01-15 08:02:10 WARNING High memory usage on db-01 (85%)
2024-01-15 08:05:33 ERROR Connection timeout on web-03
2024-01-15 08:06:01 INFO Retry attempt 1 for web-03
2024-01-15 08:06:15 ERROR Connection timeout on web-03
2024-01-15 08:06:30 INFO Retry attempt 2 for web-03
2024-01-15 08:06:45 INFO Server web-03 reconnected
2024-01-15 08:10:00 WARNING Disk usage above 90% on db-02
2024-01-15 08:12:22 INFO Backup completed for db-01
2024-01-15 08:15:00 ERROR Disk full on db-02
2024-01-15 08:15:05 CRITICAL Service crash on db-02
2024-01-15 08:15:30 INFO Emergency failover initiated for db-02
2024-01-15 08:16:00 INFO Failover complete, db-03 now primary
2024-01-15 08:20:00 INFO All systems operational
"""

with open("sample.log", "w") as f:
    f.write(sample_log.strip())

inventory_data = """web-01
web-02
web-03
db-01
db-02
db-03
cache-01
lb-01
"""

with open("inventory.txt", "w") as f:
    f.write(inventory_data.strip())

# ============================================
# TASK 1: Count the lines in sample.log
# ============================================
# Read sample.log and store the total number of lines
# in a variable called total_lines.
# Hint: You can iterate over the file and count, or use readlines().

# YOUR CODE HERE
total_lines = None


# ============================================
# TASK 2: Find all ERROR lines
# ============================================
# Read sample.log and collect all lines that contain "ERROR"
# into a list called error_lines.
# Each line should have whitespace stripped (use .strip()).

# YOUR CODE HERE
error_lines = None


# ============================================
# TASK 3: Count each log level
# ============================================
# Read sample.log and count how many lines are INFO, WARNING,
# ERROR, and CRITICAL. Store results in a dictionary called
# log_counts with keys: "INFO", "WARNING", "ERROR", "CRITICAL"
# Example: {"INFO": 8, "WARNING": 2, "ERROR": 3, "CRITICAL": 1}

# YOUR CODE HERE
log_counts = None


# ============================================
# TASK 4: Read server inventory
# ============================================
# Read inventory.txt and create a list called servers
# containing each server name (stripped of whitespace).
# Skip any empty lines.

# YOUR CODE HERE
servers = None


# ============================================
# TASK 5: Extract the first and last log entries
# ============================================
# Read sample.log. Store the first line (stripped) in a variable
# called first_entry and the last line (stripped) in last_entry.

# YOUR CODE HERE
first_entry = None
last_entry = None


# === Display Results ===
print("=" * 50)
print("RESULTS")
print("=" * 50)
print(f"Task 1 - Total lines: {total_lines}")
print(f"Task 2 - Error lines: {error_lines}")
print(f"Task 3 - Log counts: {log_counts}")
print(f"Task 4 - Servers: {servers}")
print(f"Task 5 - First entry: {first_entry}")
print(f"Task 5 - Last entry: {last_entry}")
