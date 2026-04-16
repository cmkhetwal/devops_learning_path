"""
Week 6, Day 4: Auto-Checker for regex exercises.
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
        capture_output=True, text=True, timeout=10,
        cwd=os.path.dirname(EXERCISE)
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# --- TASK 1: extract_ips ---
print("Task 1: extract_ips()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import extract_ips

# Test basic extraction
text = "From 192.168.1.10 to 10.0.0.5 and back to 192.168.1.10"
result = extract_ips(text)
assert isinstance(result, list), "Must return a list"
assert result == ["10.0.0.5", "192.168.1.10"], f"Wrong: {{result}}"

# Test with no IPs
assert extract_ips("no ips here") == [], "Should return empty list"

# Test multiple unique IPs
text2 = "172.16.0.1 10.0.0.1 192.168.0.1"
result2 = extract_ips(text2)
assert len(result2) == 3, f"Expected 3 unique IPs: {{result2}}"
assert result2 == sorted(result2), "Should be sorted"

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


# --- TASK 2: is_valid_email ---
print("Task 2: is_valid_email()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import is_valid_email

# Valid emails
assert is_valid_email("admin@server.com") == True, "admin@server.com should be valid"
assert is_valid_email("dev.ops@company.io") == True, "dev.ops@company.io should be valid"
assert is_valid_email("user+tag@mail.co.uk") == True, "user+tag@mail.co.uk should be valid"
assert is_valid_email("test123@example.org") == True, "test123@example.org should be valid"

# Invalid emails
assert is_valid_email("no-at-sign.com") == False, "no-at-sign.com should be invalid"
assert is_valid_email("@missing.com") == False, "@missing.com should be invalid"
assert is_valid_email("user@") == False, "user@ should be invalid"
assert is_valid_email("user @space.com") == False, "space in email should be invalid"
assert is_valid_email("") == False, "empty string should be invalid"
assert is_valid_email("user@host.x") == False, "single char TLD should be invalid"

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


# --- TASK 3: parse_error_logs ---
print("Task 3: parse_error_logs()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import parse_error_logs

logs = \"\"\"2024-01-15 10:30:45 INFO [app] Started successfully
2024-01-15 10:31:00 ERROR [auth] Invalid token for user admin
2024-01-15 10:31:05 WARNING [disk] Space below 20%
2024-01-15 10:31:10 ERROR [db] Connection timeout after 30s
2024-01-15 10:31:15 INFO [app] Request processed\"\"\"

result = parse_error_logs(logs)
assert isinstance(result, list), "Must return a list"
assert len(result) == 2, f"Expected 2 errors, got {{len(result)}}"

assert result[0]["timestamp"] == "2024-01-15 10:31:00", f"Wrong timestamp: {{result[0]}}"
assert result[0]["module"] == "auth", f"Wrong module: {{result[0]}}"
assert result[0]["message"] == "Invalid token for user admin", f"Wrong message: {{result[0]}}"

assert result[1]["module"] == "db", f"Second error module wrong: {{result[1]}}"
assert "timeout" in result[1]["message"].lower(), f"Second error message wrong: {{result[1]}}"

# Test with no errors
assert parse_error_logs("INFO [app] All good") == [], "No errors should return []"

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


# --- TASK 4: mask_sensitive_data ---
print("Task 4: mask_sensitive_data()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import mask_sensitive_data

# Test email masking
result = mask_sensitive_data("Contact admin@server.com for help")
assert "***@***.***" in result, f"Email not masked: {{result}}"
assert "admin@server.com" not in result, f"Email still visible: {{result}}"

# Test IP masking
result2 = mask_sensitive_data("Server at 192.168.1.1 is down")
assert "X.X.X.X" in result2, f"IP not masked: {{result2}}"
assert "192.168.1.1" not in result2, f"IP still visible: {{result2}}"

# Test long number masking
result3 = mask_sensitive_data("Account number 1234567890 is active")
assert "**REDACTED**" in result3, f"Number not masked: {{result3}}"
assert "1234567890" not in result3, f"Number still visible: {{result3}}"

# Test all together
result4 = mask_sensitive_data("User admin@co.com from 10.0.0.1 ref 9876543210")
assert "***@***.***" in result4, f"Email not masked in combined: {{result4}}"
assert "X.X.X.X" in result4, f"IP not masked in combined: {{result4}}"
assert "**REDACTED**" in result4, f"Number not masked in combined: {{result4}}"

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


# --- TASK 5: parse_access_log ---
print("Task 5: parse_access_log()")
code = r"""
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import parse_access_log

line = '172.16.0.1 - - [15/Jan/2024:10:30:45 +0000] "POST /api/login HTTP/1.1" 401 52'
result = parse_access_log(line)
assert isinstance(result, dict), "Must return a dict"
assert result["ip"] == "172.16.0.1", f"ip wrong: {{result.get('ip')}}"
assert result["date"] == "15/Jan/2024:10:30:45 +0000", f"date wrong: {{result.get('date')}}"
assert result["method"] == "POST", f"method wrong: {{result.get('method')}}"
assert result["path"] == "/api/login", f"path wrong: {{result.get('path')}}"
assert result["status"] == "401", f"status wrong: {{result.get('status')}}"
assert result["size"] == "52", f"size wrong: {{result.get('size')}}"

# Test GET request
line2 = '10.0.0.5 - - [16/Jan/2024:08:00:00 +0000] "GET /health HTTP/1.1" 200 15'
result2 = parse_access_log(line2)
assert result2["ip"] == "10.0.0.5", f"ip wrong: {{result2.get('ip')}}"
assert result2["method"] == "GET", f"method wrong: {{result2.get('method')}}"
assert result2["status"] == "200", f"status wrong: {{result2.get('status')}}"

# Test invalid line
result3 = parse_access_log("this is not a log line")
assert result3 == {{}}, f"Invalid line should return empty dict: {{result3}}"

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
print(f"  Week 6, Day 4 Score: {score}/{total}")
print(f"{'='*40}")
if score == total:
    print("  Outstanding! You've mastered regular expressions.")
elif score >= 3:
    print("  Good progress. Review the tasks you missed.")
else:
    print("  Keep practicing. Re-read lesson.md and try again.")
