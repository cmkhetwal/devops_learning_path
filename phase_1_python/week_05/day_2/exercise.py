"""
Week 5, Day 2: Exercise - Writing Files
========================================

Today you will practice writing files and working with CSV.
Complete all 5 tasks. Run check.py when finished to verify your work.
"""

import csv

# ============================================
# TASK 1: Write a server status report
# ============================================
# Write a text file called "server_report.txt" with the following
# EXACT content (use write mode "w"):
#
# SERVER STATUS REPORT
# ====================
# web-01: ONLINE
# web-02: ONLINE
# web-03: OFFLINE
# db-01: ONLINE
# db-02: MAINTENANCE
#
# Hint: Remember to include \n at the end of each line.

# YOUR CODE HERE


# ============================================
# TASK 2: Append to the report
# ============================================
# Using APPEND mode ("a"), add these two lines to "server_report.txt":
#
# --------------------
# Total: 3 online, 1 offline, 1 maintenance
#
# After this task, the file should have the original content from
# Task 1 PLUS these two new lines.

# YOUR CODE HERE


# ============================================
# TASK 3: Write a CSV inventory file
# ============================================
# Create a CSV file called "inventory.csv" using the csv module.
# Use csv.writer to write the following data (including the header row):
#
# hostname,ip,role,status
# web-01,10.0.1.10,webserver,online
# web-02,10.0.1.11,webserver,online
# web-03,10.0.1.12,webserver,offline
# db-01,10.0.2.10,database,online
# db-02,10.0.2.11,database,maintenance
#
# Remember to open the file with newline=""

# YOUR CODE HERE


# ============================================
# TASK 4: Write CSV from dictionaries
# ============================================
# Create a CSV file called "disk_usage.csv" using csv.DictWriter.
# Use the data below. Write the header row and all data rows.
#
# Remember: open with newline="", use writeheader(), then writerows()

disk_data = [
    {"server": "web-01", "disk": "/dev/sda1", "size_gb": 100, "used_pct": 45},
    {"server": "web-02", "disk": "/dev/sda1", "size_gb": 100, "used_pct": 62},
    {"server": "db-01", "disk": "/dev/sda1", "size_gb": 500, "used_pct": 78},
    {"server": "db-01", "disk": "/dev/sdb1", "size_gb": 1000, "used_pct": 55},
    {"server": "db-02", "disk": "/dev/sda1", "size_gb": 500, "used_pct": 91},
]

# YOUR CODE HERE


# ============================================
# TASK 5: Build a file from a list of servers
# ============================================
# Given the list below, write a file called "deploy_targets.txt"
# with one server per line. Only include servers whose status is "online".
# Write just the hostname, one per line, no extra spaces.
#
# Expected file content:
# web-01
# web-02
# db-01

all_servers = [
    {"hostname": "web-01", "status": "online"},
    {"hostname": "web-02", "status": "online"},
    {"hostname": "web-03", "status": "offline"},
    {"hostname": "db-01", "status": "online"},
    {"hostname": "db-02", "status": "maintenance"},
]

# YOUR CODE HERE


# === Display Results ===
print("=" * 50)
print("FILES CREATED")
print("=" * 50)

import os
for filename in ["server_report.txt", "inventory.csv", "disk_usage.csv", "deploy_targets.txt"]:
    if os.path.exists(filename):
        print(f"\n--- {filename} ---")
        with open(filename, "r") as f:
            print(f.read())
    else:
        print(f"\n--- {filename} --- NOT FOUND")
