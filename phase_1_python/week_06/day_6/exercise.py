"""
Week 6, Day 6: Practice Day - 5 Mini-Projects

THEME: Real-World DevOps Automation

Combine os, subprocess, shutil, pathlib, re, and argparse into
5 practical mini-projects. Each builds on what you learned this week.

Complete all 5 projects below.
"""

import os
import subprocess
import shutil
import re
from pathlib import Path


# =====================================================================
# PROJECT 1: System Info Gatherer
# =====================================================================
# Write a function that collects system information and returns it
# as a dictionary with these keys:
#
#   "hostname"       -> system hostname (use subprocess: ["hostname"])
#   "username"       -> current user (use os.getenv or subprocess: ["whoami"])
#   "cwd"            -> current working directory (use os.getcwd())
#   "python_version" -> Python version string (use subprocess: ["python3", "--version"])
#                       extract just the version number, e.g., "3.10.12"
#   "home_dir"       -> user home directory (use os.path.expanduser("~"))
#   "os_type"        -> os.name (e.g., "posix" on Linux)
#   "cpu_count"      -> number of CPUs (use os.cpu_count())
#
# If any command fails, use "unknown" as the value for that key.

def gather_system_info():
    # YOUR CODE HERE
    pass


# =====================================================================
# PROJECT 2: File Organizer
# =====================================================================
# Write a function that takes a directory path and organizes all files
# in it into subdirectories based on their file extension.
#
# Rules:
#   - ".py" files go into a "py" subdirectory
#   - ".log" files go into a "log" subdirectory
#   - ".txt" files go into a "txt" subdirectory
#   - Files with no extension go into an "other" subdirectory
#   - Any other extension: use the extension without the dot as the folder name
#   - Only move files, not directories
#   - Subdirectories for organization are created as needed
#
# Return a dictionary:
#   "files_moved"  -> total number of files moved (int)
#   "categories"   -> dict mapping folder name to list of filenames moved there
#
# Example return:
#   {"files_moved": 4, "categories": {"py": ["app.py"], "txt": ["notes.txt"], ...}}
#
# Use pathlib for path operations and shutil.move() for moving files.

def organize_directory(directory):
    # YOUR CODE HERE
    pass


# =====================================================================
# PROJECT 3: Log Parser with Regex
# =====================================================================
# Write a function that takes a multi-line log string and returns
# a detailed analysis dictionary.
#
# Log format (each line):
#   "2024-01-15 10:30:45 LEVEL [module] Message text"
#   or
#   "192.168.1.10 - - [15/Jan/2024:10:30:45] \"GET /path HTTP/1.1\" 200 1234"
#
# The log may contain BOTH formats mixed together.
#
# Return a dictionary with:
#   "total_lines"     -> number of non-empty lines (int)
#   "error_count"     -> number of lines containing "ERROR" (int)
#   "warning_count"   -> number of lines containing "WARNING" (int)
#   "unique_ips"      -> sorted list of unique IPv4 addresses found
#   "error_messages"  -> list of message text from ERROR lines
#                        (the part after "ERROR [module] ")
#   "status_codes"    -> dict mapping HTTP status codes to counts
#                        e.g., {"200": 5, "404": 2}
#
# Hints:
#   - IP pattern: r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
#   - Error message: r"ERROR \[\w+\] (.+)"
#   - HTTP status code: r'" (\d{3}) \d+'

def parse_log(log_text):
    # YOUR CODE HERE
    pass


# =====================================================================
# PROJECT 4: Disk Space Monitor
# =====================================================================
# Write a function that checks disk space for a given path and returns
# a status report.
#
# Parameters:
#   - path: filesystem path to check (default "/")
#   - warning_threshold: percent used that triggers WARNING (default 75)
#   - critical_threshold: percent used that triggers CRITICAL (default 90)
#
# Return a dictionary with:
#   "path"          -> the path checked (string)
#   "total_gb"      -> total space in GB (float, rounded to 1 decimal)
#   "used_gb"       -> used space in GB (float, rounded to 1 decimal)
#   "free_gb"       -> free space in GB (float, rounded to 1 decimal)
#   "percent_used"  -> percentage used (float, rounded to 1 decimal)
#   "status"        -> "OK", "WARNING", or "CRITICAL"
#
# Logic:
#   - If percent_used >= critical_threshold -> "CRITICAL"
#   - Elif percent_used >= warning_threshold -> "WARNING"
#   - Else -> "OK"
#
# Use shutil.disk_usage() to get the raw bytes.
# 1 GB = 1024 ** 3 bytes

def check_disk_space(path="/", warning_threshold=75, critical_threshold=90):
    # YOUR CODE HERE
    pass


# =====================================================================
# PROJECT 5: CLI System Health Checker
# =====================================================================
# Write a function that takes a list of check names and a threshold,
# and runs the corresponding checks, returning results.
#
# Available checks:
#   "disk"     -> use check_disk_space() from Project 4
#   "hostname" -> run ["hostname"], return the hostname string
#   "uptime"   -> run ["uptime", "-p"], return the output string
#   "memory"   -> run ["free", "-m"], parse total/used from the "Mem:" line
#   "load"     -> read /proc/loadavg (first value), or run ["uptime"]
#
# Parameters:
#   - checks: list of check names (e.g., ["disk", "hostname"])
#   - threshold: disk warning threshold (int, default 80)
#   - verbose: if True, include extra detail (default False)
#
# Return a dictionary:
#   "checks_run"    -> number of checks that were run (int)
#   "checks_passed" -> number of checks that passed (int)
#   "results"       -> dict mapping check name to its result dict:
#                      {"status": "OK"/"WARNING"/"FAIL", "detail": "info string"}
#
# Check pass/fail rules:
#   "disk"     -> PASS if status is "OK" or "WARNING", FAIL if "CRITICAL"
#   "hostname" -> PASS if hostname is a non-empty string
#   "uptime"   -> PASS if command succeeds
#   "memory"   -> PASS if command succeeds and used < total
#   "load"     -> PASS if load average < number of CPUs
#
# If a check is not recognized, skip it (don't count it).
# If a command fails, mark it as FAIL with detail "Command failed".

def run_health_checks(checks, threshold=80, verbose=False):
    # YOUR CODE HERE
    pass


# === Do not modify below this line ===
if __name__ == "__main__":
    print("=" * 50)
    print("  PROJECT 1: System Info Gatherer")
    print("=" * 50)
    info = gather_system_info()
    if info:
        for k, v in info.items():
            print(f"  {k}: {v}")

    print(f"\n{'=' * 50}")
    print("  PROJECT 2: File Organizer")
    print("=" * 50)
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["app.py", "test.py", "data.csv", "report.pdf", "notes.txt", "Makefile"]:
            (Path(tmp) / name).touch()
        result = organize_directory(tmp)
        if result:
            print(f"  Files moved: {result.get('files_moved')}")
            for cat, files in result.get("categories", {}).items():
                print(f"    {cat}/: {files}")

    print(f"\n{'=' * 50}")
    print("  PROJECT 3: Log Parser")
    print("=" * 50)
    sample_log = """2024-01-15 10:30:45 INFO [app] Server started on port 8080
2024-01-15 10:31:00 ERROR [auth] Invalid token for user admin
192.168.1.10 - - [15/Jan/2024:10:31:05] "GET /api/users HTTP/1.1" 200 1234
192.168.1.10 - - [15/Jan/2024:10:31:06] "GET /api/data HTTP/1.1" 200 5678
10.0.0.5 - - [15/Jan/2024:10:31:07] "POST /api/login HTTP/1.1" 401 52
2024-01-15 10:31:10 ERROR [db] Connection timeout after 30s
2024-01-15 10:31:15 WARNING [disk] Space below 20%
10.0.0.5 - - [15/Jan/2024:10:31:20] "GET /missing HTTP/1.1" 404 0"""
    parsed = parse_log(sample_log)
    if parsed:
        print(f"  Total lines: {parsed.get('total_lines')}")
        print(f"  Errors: {parsed.get('error_count')}")
        print(f"  Warnings: {parsed.get('warning_count')}")
        print(f"  Unique IPs: {parsed.get('unique_ips')}")
        print(f"  Error messages: {parsed.get('error_messages')}")
        print(f"  Status codes: {parsed.get('status_codes')}")

    print(f"\n{'=' * 50}")
    print("  PROJECT 4: Disk Space Monitor")
    print("=" * 50)
    disk = check_disk_space("/")
    if disk:
        for k, v in disk.items():
            print(f"  {k}: {v}")

    print(f"\n{'=' * 50}")
    print("  PROJECT 5: CLI System Health Checker")
    print("=" * 50)
    health = run_health_checks(["disk", "hostname", "uptime"], threshold=80, verbose=True)
    if health:
        print(f"  Checks run: {health.get('checks_run')}")
        print(f"  Checks passed: {health.get('checks_passed')}")
        for name, result in health.get("results", {}).items():
            print(f"    [{name}] {result.get('status')}: {result.get('detail')}")
