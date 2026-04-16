"""
Week 1, Day 4 - Exercise: Math Operations

Complete each task below. Run check.py when done.
"""

# ============================================
# TASK 1: Calculate server capacity
#   You have 3 servers. Each server can run 8 containers.
#   You need to deploy 50 containers total.
#
#   Calculate and print:
#     Total capacity: <number>            (3 * 8)
#     Containers needed: 50
#     Full servers needed: <number>       (use floor division: 50 // 8)
#     Leftover containers: <number>       (use modulo: 50 % 8)
#
#   Hint: create variables and use //, %, and *
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 2: Calculate disk usage percentage
#   total_disk = 500    (GB total)
#   used_disk = 347     (GB used)
#
#   Calculate:
#     free_disk = total minus used
#     usage_percent = (used / total) * 100
#
#   Print exactly:
#     Disk total: 500 GB
#     Disk used: 347 GB
#     Disk free: 153 GB
#     Usage: 69.4%
#
#   (Hint: format usage_percent to 1 decimal with :.1f)
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 3: Network bandwidth conversion
#   You have a network speed of 1000 megabits per second (Mbps).
#
#   Convert and print:
#     Speed: 1000 Mbps
#     Speed: 125.0 MBps
#     Speed: 0.122 GBps
#
#   Formulas:
#     MBps = Mbps / 8           (bits to bytes)
#     GBps = MBps / 1024        (megabytes to gigabytes)
#
#   (Hint: format MBps to 1 decimal, GBps to 3 decimals)
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 4: Uptime calculation
#   A server was up for 29 days, 23 hours, and 45 minutes
#   out of 30 full days.
#
#   Step 1: Calculate total_minutes for 30 days (30 * 24 * 60)
#   Step 2: Calculate uptime_minutes (29*24*60 + 23*60 + 45)
#   Step 3: Calculate downtime_minutes (total minus uptime)
#   Step 4: Calculate uptime_percent ((uptime / total) * 100)
#
#   Print exactly:
#     Total minutes: 43200
#     Uptime minutes: 43185
#     Downtime minutes: 15
#     Uptime: 99.965%
#
#   (Hint: format uptime_percent to 3 decimal places)
# ============================================
# YOUR CODE HERE


# ============================================
# TASK 5: Resource monitoring with comparison operators
#   Given these values:
#     cpu_usage = 78
#     memory_usage = 92
#     disk_usage = 45
#     error_count = 3
#     max_errors = 5
#
#   Print these comparisons (True or False):
#     CPU critical (>90): False
#     Memory critical (>90): True
#     Disk warning (>80): False
#     Errors OK (<5): True
#     All healthy: False
#
#   For "All healthy", it should be True only when:
#     cpu_usage < 90 AND memory_usage < 90 AND
#     disk_usage < 90 AND error_count < max_errors
#   (Hint: use "and" to combine comparisons)
#   Since memory_usage is 92, "All healthy" should be False.
# ============================================
# YOUR CODE HERE
