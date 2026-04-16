"""
Week 5, Day 2: Auto-checker
============================
Run this file to verify your exercise.py solutions.
"""

import subprocess
import sys
import os
import csv

def main():
    print("=" * 50)
    print("WEEK 5, DAY 2 - EXERCISE CHECKER")
    print("=" * 50)
    print()

    # Run exercise.py first
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True, timeout=10
    )

    if result.returncode != 0:
        print("ERROR: exercise.py failed to run!")
        print(result.stderr)
        return

    score = 0
    total = 5

    # Task 1: Server report exists with correct initial content
    print("Task 1 - Write server status report")
    expected_report_start = (
        "SERVER STATUS REPORT\n"
        "====================\n"
        "web-01: ONLINE\n"
        "web-02: ONLINE\n"
        "web-03: OFFLINE\n"
        "db-01: ONLINE\n"
        "db-02: MAINTENANCE\n"
    )
    if os.path.exists("server_report.txt"):
        with open("server_report.txt", "r") as f:
            content = f.read()
        if content.startswith(expected_report_start):
            print("  PASS: server_report.txt has correct initial content")
            score += 1
        else:
            print("  FAIL: Content does not match expected format")
            print(f"  Expected to start with:\n{expected_report_start}")
            print(f"  Got:\n{content[:300]}")
    else:
        print("  FAIL: server_report.txt not found")

    # Task 2: Appended lines
    print("\nTask 2 - Append to report")
    expected_full = (
        "SERVER STATUS REPORT\n"
        "====================\n"
        "web-01: ONLINE\n"
        "web-02: ONLINE\n"
        "web-03: OFFLINE\n"
        "db-01: ONLINE\n"
        "db-02: MAINTENANCE\n"
        "--------------------\n"
        "Total: 3 online, 1 offline, 1 maintenance\n"
    )
    if os.path.exists("server_report.txt"):
        with open("server_report.txt", "r") as f:
            content = f.read()
        if content == expected_full:
            print("  PASS: Appended lines are correct")
            score += 1
        else:
            print("  FAIL: File content does not match after append")
            print(f"  Expected:\n{expected_full}")
            print(f"  Got:\n{content}")
    else:
        print("  FAIL: server_report.txt not found")

    # Task 3: CSV inventory
    print("\nTask 3 - CSV inventory file")
    expected_csv = [
        ["hostname", "ip", "role", "status"],
        ["web-01", "10.0.1.10", "webserver", "online"],
        ["web-02", "10.0.1.11", "webserver", "online"],
        ["web-03", "10.0.1.12", "webserver", "offline"],
        ["db-01", "10.0.2.10", "database", "online"],
        ["db-02", "10.0.2.11", "database", "maintenance"],
    ]
    if os.path.exists("inventory.csv"):
        with open("inventory.csv", "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if rows == expected_csv:
            print("  PASS: inventory.csv is correct")
            score += 1
        else:
            print(f"  FAIL: Expected {len(expected_csv)} rows, got {len(rows)}")
            if rows:
                print(f"  First row: {rows[0]}")
    else:
        print("  FAIL: inventory.csv not found")

    # Task 4: Disk usage CSV from dicts
    print("\nTask 4 - Disk usage CSV from dictionaries")
    expected_header = ["server", "disk", "size_gb", "used_pct"]
    expected_rows = [
        ["web-01", "/dev/sda1", "100", "45"],
        ["web-02", "/dev/sda1", "100", "62"],
        ["db-01", "/dev/sda1", "500", "78"],
        ["db-01", "/dev/sdb1", "1000", "55"],
        ["db-02", "/dev/sda1", "500", "91"],
    ]
    if os.path.exists("disk_usage.csv"):
        with open("disk_usage.csv", "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if len(rows) >= 6 and rows[0] == expected_header and rows[1:] == expected_rows:
            print("  PASS: disk_usage.csv is correct")
            score += 1
        else:
            print("  FAIL: Content does not match expected data")
            if rows:
                print(f"  Header: {rows[0]}")
                print(f"  Expected header: {expected_header}")
                print(f"  Row count: {len(rows)} (expected 6)")
    else:
        print("  FAIL: disk_usage.csv not found")

    # Task 5: Deploy targets
    print("\nTask 5 - Deploy targets file")
    expected_targets = "web-01\nweb-02\ndb-01\n"
    if os.path.exists("deploy_targets.txt"):
        with open("deploy_targets.txt", "r") as f:
            content = f.read()
        if content == expected_targets:
            print("  PASS: deploy_targets.txt is correct")
            score += 1
        else:
            print(f"  FAIL: Expected:\n{expected_targets!r}")
            print(f"  Got:\n{content!r}")
    else:
        print("  FAIL: deploy_targets.txt not found")

    # Final score
    print()
    print("=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    print("=" * 50)
    if score == total:
        print("Excellent! All tasks complete. Move on to Day 3!")
    elif score >= 3:
        print("Good progress! Review the failed tasks and try again.")
    else:
        print("Keep practicing! Review the lesson and try again.")

    # Cleanup
    for f in ["server_report.txt", "inventory.csv", "disk_usage.csv", "deploy_targets.txt"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
