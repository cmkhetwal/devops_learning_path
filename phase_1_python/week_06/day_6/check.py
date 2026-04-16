"""
Week 6, Day 6: Auto-Checker for Practice Day mini-projects.
Run: python3 check.py
"""

import subprocess
import sys
import os

EXERCISE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
score = 0
total = 5


def run_python(code):
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=15,
        cwd=os.path.dirname(EXERCISE)
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# --- PROJECT 1: gather_system_info ---
print("Project 1: gather_system_info()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import gather_system_info

result = gather_system_info()
assert isinstance(result, dict), "Must return a dict"

required_keys = ["hostname", "username", "cwd", "python_version", "home_dir", "os_type", "cpu_count"]
for key in required_keys:
    assert key in result, f"Missing key: {{key}}"

assert isinstance(result["hostname"], str) and len(result["hostname"]) > 0, "hostname empty"
assert isinstance(result["username"], str) and len(result["username"]) > 0, "username empty"
assert result["cwd"] == os.getcwd(), f"cwd wrong: {{result['cwd']}}"
assert result["os_type"] == os.name, f"os_type wrong: {{result['os_type']}}"
assert isinstance(result["cpu_count"], int) and result["cpu_count"] > 0, f"cpu_count wrong: {{result['cpu_count']}}"
# python_version should look like a version string (digits and dots)
import re
assert re.search(r"\\d+\\.\\d+", result["python_version"]), f"python_version wrong: {{result['python_version']}}"
print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        print(f"  Error: {stderr.splitlines()[-1]}")


# --- PROJECT 2: organize_directory ---
print("Project 2: organize_directory()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import organize_directory

with tempfile.TemporaryDirectory() as tmp:
    # Create test files
    for name in ["app.py", "test.py", "data.csv", "report.pdf", "notes.txt", "Makefile"]:
        (Path(tmp) / name).touch()
    # Create a directory (should be skipped)
    (Path(tmp) / "subdir").mkdir()

    result = organize_directory(tmp)
    assert isinstance(result, dict), "Must return a dict"
    assert result["files_moved"] == 6, f"files_moved wrong: {{result['files_moved']}}"
    assert isinstance(result["categories"], dict), "categories must be a dict"

    # Check files were actually moved
    assert (Path(tmp) / "py" / "app.py").exists(), "app.py not in py/"
    assert (Path(tmp) / "py" / "test.py").exists(), "test.py not in py/"
    assert (Path(tmp) / "csv" / "data.csv").exists(), "data.csv not in csv/"
    assert (Path(tmp) / "pdf" / "report.pdf").exists(), "report.pdf not in pdf/"
    assert (Path(tmp) / "txt" / "notes.txt").exists(), "notes.txt not in txt/"
    assert (Path(tmp) / "other" / "Makefile").exists(), "Makefile not in other/"

    # Check categories dict
    assert "py" in result["categories"], "py not in categories"
    assert len(result["categories"]["py"]) == 2, f"py should have 2 files"
print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        print(f"  Error: {stderr.splitlines()[-1]}")


# --- PROJECT 3: parse_log ---
print("Project 3: parse_log()")
code = '''
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import parse_log

log = """2024-01-15 10:30:45 INFO [app] Server started on port 8080
2024-01-15 10:31:00 ERROR [auth] Invalid token for user admin
192.168.1.10 - - [15/Jan/2024:10:31:05] "GET /api/users HTTP/1.1" 200 1234
192.168.1.10 - - [15/Jan/2024:10:31:06] "GET /api/data HTTP/1.1" 200 5678
10.0.0.5 - - [15/Jan/2024:10:31:07] "POST /api/login HTTP/1.1" 401 52
2024-01-15 10:31:10 ERROR [db] Connection timeout after 30s
2024-01-15 10:31:15 WARNING [disk] Space below 20%
10.0.0.5 - - [15/Jan/2024:10:31:20] "GET /missing HTTP/1.1" 404 0"""

result = parse_log(log)
assert isinstance(result, dict), "Must return a dict"
assert result["total_lines"] == 8, f"total_lines wrong: {{result['total_lines']}}"
assert result["error_count"] == 2, f"error_count wrong: {{result['error_count']}}"
assert result["warning_count"] == 1, f"warning_count wrong: {{result['warning_count']}}"
assert sorted(result["unique_ips"]) == ["10.0.0.5", "192.168.1.10"], f"unique_ips wrong: {{result['unique_ips']}}"
assert len(result["error_messages"]) == 2, f"error_messages count wrong: {{result['error_messages']}}"
assert "Invalid token for user admin" in result["error_messages"], f"Missing error msg: {{result['error_messages']}}"
assert isinstance(result["status_codes"], dict), "status_codes must be dict"
assert result["status_codes"].get("200") == 2, f"200 count wrong: {{result['status_codes']}}"
assert result["status_codes"].get("401") == 1, f"401 count wrong: {{result['status_codes']}}"
assert result["status_codes"].get("404") == 1, f"404 count wrong: {{result['status_codes']}}"

# Test empty log
empty_result = parse_log("")
assert empty_result["total_lines"] == 0, "Empty log should have 0 lines"
assert empty_result["error_count"] == 0, "Empty log should have 0 errors"
print("OK")
'''.format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        print(f"  Error: {stderr.splitlines()[-1]}")


# --- PROJECT 4: check_disk_space ---
print("Project 4: check_disk_space()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import check_disk_space

result = check_disk_space("/")
assert isinstance(result, dict), "Must return a dict"

required_keys = ["path", "total_gb", "used_gb", "free_gb", "percent_used", "status"]
for key in required_keys:
    assert key in result, f"Missing key: {{key}}"

assert result["path"] == "/", f"path wrong: {{result['path']}}"
assert isinstance(result["total_gb"], float), "total_gb must be float"
assert isinstance(result["used_gb"], float), "used_gb must be float"
assert isinstance(result["free_gb"], float), "free_gb must be float"
assert isinstance(result["percent_used"], float), "percent_used must be float"
assert result["total_gb"] > 0, "total_gb should be > 0"
assert result["used_gb"] >= 0, "used_gb should be >= 0"
assert result["free_gb"] >= 0, "free_gb should be >= 0"
assert 0 <= result["percent_used"] <= 100, f"percent_used out of range: {{result['percent_used']}}"
assert result["status"] in ["OK", "WARNING", "CRITICAL"], f"status wrong: {{result['status']}}"

# Test threshold logic
result2 = check_disk_space("/", warning_threshold=0, critical_threshold=0)
assert result2["status"] == "CRITICAL", "Should be CRITICAL with 0% threshold"

result3 = check_disk_space("/", warning_threshold=100, critical_threshold=100)
assert result3["status"] == "OK", "Should be OK with 100% threshold"
print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        print(f"  Error: {stderr.splitlines()[-1]}")


# --- PROJECT 5: run_health_checks ---
print("Project 5: run_health_checks()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import run_health_checks

# Test with basic checks
result = run_health_checks(["disk", "hostname"])
assert isinstance(result, dict), "Must return a dict"
assert "checks_run" in result, "Missing key: checks_run"
assert "checks_passed" in result, "Missing key: checks_passed"
assert "results" in result, "Missing key: results"
assert result["checks_run"] == 2, f"checks_run wrong: {{result['checks_run']}}"
assert isinstance(result["results"], dict), "results must be a dict"
assert "disk" in result["results"], "disk check missing from results"
assert "hostname" in result["results"], "hostname check missing from results"

# Check result structure
for name, check_result in result["results"].items():
    assert "status" in check_result, f"{{name}} missing status"
    assert "detail" in check_result, f"{{name}} missing detail"
    assert check_result["status"] in ["OK", "WARNING", "FAIL"], f"{{name}} invalid status: {{check_result['status']}}"

# Hostname should pass
assert result["results"]["hostname"]["status"] in ["OK", "WARNING"], f"hostname should pass: {{result['results']['hostname']}}"

# Test with unknown check (should be skipped)
result2 = run_health_checks(["hostname", "nonexistent_check"])
assert result2["checks_run"] == 1, f"Unknown check should be skipped: {{result2['checks_run']}}"

# Test with empty list
result3 = run_health_checks([])
assert result3["checks_run"] == 0, f"Empty checks should give 0: {{result3['checks_run']}}"
print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        print(f"  Error: {stderr.splitlines()[-1]}")


# --- SUMMARY ---
print(f"\n{'='*40}")
print(f"  Week 6, Day 6 Score: {score}/{total}")
print(f"{'='*40}")
if score == total:
    print("  Outstanding! All 5 mini-projects complete.")
    print("  You are ready for the Week 6 quiz tomorrow.")
elif score >= 3:
    print("  Good progress. Review the projects you missed.")
else:
    print("  Keep working at it. These projects combine all")
    print("  the skills from this week -- review earlier days.")
