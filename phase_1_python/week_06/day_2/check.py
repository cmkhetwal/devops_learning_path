"""
Week 6, Day 2: Auto-Checker for subprocess exercises.
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


# --- TASK 1: get_current_user ---
print("Task 1: get_current_user()")
code = """
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import get_current_user
user = get_current_user()
expected = subprocess.run(["whoami"], capture_output=True, text=True).stdout.strip()
assert isinstance(user, str), "Must return a string"
assert user == expected, f"Expected '{{expected}}', got '{{user}}'"
assert "\\n" not in user, "Username should not contain newlines"
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


# --- TASK 2: run_command ---
print("Task 2: run_command()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import run_command

# Test successful command
result = run_command(["echo", "test123"])
assert isinstance(result, dict), "Must return a dict"
assert "test123" in result["stdout"], f"stdout should contain 'test123': {{result['stdout']}}"
assert result["returncode"] == 0, f"returncode should be 0: {{result['returncode']}}"
assert result["success"] == True, "success should be True"

# Test failing command
result2 = run_command(["ls", "/nonexistent_path_xyz"])
assert result2["returncode"] != 0, "returncode should be non-zero for failure"
assert result2["success"] == False, "success should be False"

# Test command not found
result3 = run_command(["totally_fake_command_xyz"])
assert result3["success"] == False, "success should be False for missing command"
assert result3["stderr"] == "Command not found", f"stderr wrong: {{result3['stderr']}}"
assert result3["returncode"] == -1, f"returncode should be -1: {{result3['returncode']}}"

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


# --- TASK 3: get_disk_usage ---
print("Task 3: get_disk_usage()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import get_disk_usage

result = get_disk_usage()
assert isinstance(result, dict), "Must return a dict"
assert len(result) > 0, "Dict should not be empty"
required_keys = ["filesystem", "total", "used", "available", "percent"]
for key in required_keys:
    assert key in result, f"Missing key: {{key}}"
    assert isinstance(result[key], str), f"{{key}} should be a string"
    assert len(result[key]) > 0, f"{{key}} should not be empty"
assert "%" in result["percent"], f"percent should contain '%': {{result['percent']}}"
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


# --- TASK 4: ping_host ---
print("Task 4: ping_host()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import ping_host

# Test with localhost (should always work)
result = ping_host("127.0.0.1")
assert isinstance(result, dict), "Must return a dict"
assert result["host"] == "127.0.0.1", f"host wrong: {{result['host']}}"
assert result["reachable"] == True, "127.0.0.1 should be reachable"
assert isinstance(result["output"], str), "output should be a string"
assert len(result["output"]) > 0, "output should not be empty"

# Test with unreachable host
result2 = ping_host("192.0.2.1")  # RFC 5737 TEST-NET, should be unreachable
assert result2["host"] == "192.0.2.1", f"host wrong: {{result2['host']}}"
assert result2["reachable"] == False, "192.0.2.1 should be unreachable"
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


# --- TASK 5: run_shell_pipeline ---
print("Task 5: run_shell_pipeline()")
code = r"""
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import run_shell_pipeline

# Test basic echo
result = run_shell_pipeline("echo -e 'alpha\nbeta\ngamma'")
assert isinstance(result, list), "Must return a list"
assert len(result) == 3, f"Expected 3 lines, got {{len(result)}}: {{result}}"
assert result[0] == "alpha", f"First line wrong: {{result[0]}}"
assert result[2] == "gamma", f"Third line wrong: {{result[2]}}"

# Test failed command returns empty list
result2 = run_shell_pipeline("ls /totally_nonexistent_xyz_123 2>/dev/null; exit 1")
assert result2 == [], f"Failed command should return []: {{result2}}"

# Test pipeline
result3 = run_shell_pipeline("echo -e 'dog\ncat\nbird' | sort")
assert isinstance(result3, list), "Pipeline should return a list"
assert len(result3) == 3, f"Expected 3 lines from sort: {{result3}}"
assert result3[0] == "bird", f"First sorted line wrong: {{result3[0]}}"
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
print(f"  Week 6, Day 2 Score: {score}/{total}")
print(f"{'='*40}")
if score == total:
    print("  Outstanding! You've mastered subprocess.")
elif score >= 3:
    print("  Good progress. Review the tasks you missed.")
else:
    print("  Keep practicing. Re-read lesson.md and try again.")
