"""
Week 6, Day 1: Auto-Checker for os Module exercises.
Run: python3 check.py
"""

import subprocess
import sys
import os
import tempfile
import json

EXERCISE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
score = 0
total = 5


def run_python(code):
    """Run a Python code snippet that imports exercise and returns output."""
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10,
        cwd=os.path.dirname(EXERCISE)
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# --- TASK 1: explore_cwd ---
print("Task 1: explore_cwd()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import explore_cwd
result = explore_cwd()
assert isinstance(result, dict), "Must return a dict"
assert "cwd" in result, "Missing key: cwd"
assert "files" in result, "Missing key: files"
assert "dirs" in result, "Missing key: dirs"
assert "total" in result, "Missing key: total"
assert isinstance(result["cwd"], str), "cwd must be a string"
assert isinstance(result["files"], list), "files must be a list"
assert isinstance(result["dirs"], list), "dirs must be a list"
assert isinstance(result["total"], int), "total must be an int"
assert result["total"] == len(result["files"]) + len(result["dirs"]), "total must equal files + dirs"
assert result["cwd"] == os.getcwd(), "cwd should match os.getcwd()"
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


# --- TASK 2: setup_directories ---
print("Task 2: setup_directories()")
code = """
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import setup_directories
with tempfile.TemporaryDirectory() as tmp:
    base = os.path.join(tmp, "testapp")
    subdirs = ["logs", "config", "data", "backups"]
    result = setup_directories(base, subdirs)
    assert isinstance(result, list), "Must return a list"
    assert len(result) == 4, f"Expected 4 paths, got {{len(result)}}"
    for name in subdirs:
        expected = os.path.join(base, name)
        assert os.path.isdir(expected), f"Directory not created: {{expected}}"
        assert expected in result, f"{{expected}} not in returned list"
    # Test idempotency (exist_ok=True)
    result2 = setup_directories(base, subdirs)
    assert len(result2) == 4, "Should work on second run (exist_ok)"
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


# --- TASK 3: count_extensions ---
print("Task 3: count_extensions()")
code = """
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import count_extensions
with tempfile.TemporaryDirectory() as tmp:
    # Create test files
    for name in ["a.log", "b.log", "c.txt", "d.txt", "e.txt", "f.conf", "noext", "Makefile"]:
        open(os.path.join(tmp, name), "w").close()
    # Create a subdirectory (should NOT be counted)
    os.mkdir(os.path.join(tmp, "subdir"))

    result = count_extensions(tmp)
    assert isinstance(result, dict), "Must return a dict"
    assert result.get(".log") == 2, f".log count: expected 2, got {{result.get('.log')}}"
    assert result.get(".txt") == 3, f".txt count: expected 3, got {{result.get('.txt')}}"
    assert result.get(".conf") == 1, f".conf count: expected 1, got {{result.get('.conf')}}"
    assert result.get("") == 2, f"no-extension count: expected 2, got {{result.get('')}}"
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


# --- TASK 4: get_app_config ---
print("Task 4: get_app_config()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))

# Test with defaults (clear any that might be set)
for var in ["APP_HOST", "APP_PORT", "APP_ENV", "DB_HOST", "DB_PORT", "DEBUG"]:
    os.environ.pop(var, None)

from exercise import get_app_config
result = get_app_config()
assert isinstance(result, dict), "Must return a dict"
assert result.get("APP_HOST") == "0.0.0.0", f"APP_HOST default wrong: {{result.get('APP_HOST')}}"
assert result.get("APP_PORT") == "8080", f"APP_PORT default wrong: {{result.get('APP_PORT')}}"
assert result.get("APP_ENV") == "development", f"APP_ENV default wrong: {{result.get('APP_ENV')}}"
assert result.get("DB_HOST") == "localhost", f"DB_HOST default wrong: {{result.get('DB_HOST')}}"
assert result.get("DB_PORT") == "5432", f"DB_PORT default wrong: {{result.get('DB_PORT')}}"
assert result.get("DEBUG") == "false", f"DEBUG default wrong: {{result.get('DEBUG')}}"

# Test with environment variables set
os.environ["APP_HOST"] = "192.168.1.10"
os.environ["APP_PORT"] = "3000"
os.environ["APP_ENV"] = "production"
result2 = get_app_config()
assert result2["APP_HOST"] == "192.168.1.10", "Should read APP_HOST from env"
assert result2["APP_PORT"] == "3000", "Should read APP_PORT from env"
assert result2["APP_ENV"] == "production", "Should read APP_ENV from env"
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


# --- TASK 5: path_info ---
print("Task 5: path_info()")
code = """
import sys, os, tempfile
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import path_info

# Test with a real file
with tempfile.NamedTemporaryFile(suffix=".log", delete=False) as f:
    f.write(b"hello world")
    tmp_path = f.name

result = path_info(tmp_path)
assert isinstance(result, dict), "Must return a dict"
assert result["exists"] == True, "exists should be True"
assert result["is_file"] == True, "is_file should be True"
assert result["is_dir"] == False, "is_dir should be False"
assert result["basename"] == os.path.basename(tmp_path), f"basename wrong: {{result['basename']}}"
assert result["dirname"] == os.path.dirname(tmp_path), f"dirname wrong: {{result['dirname']}}"
assert result["extension"] == ".log", f"extension wrong: {{result['extension']}}"
assert result["size"] == 11, f"size wrong: {{result['size']}}"
os.unlink(tmp_path)

# Test with a non-existent path
result2 = path_info("/nonexistent/fake/path.txt")
assert result2["exists"] == False, "exists should be False for missing path"
assert result2["size"] == 0, "size should be 0 for missing path"
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
print(f"  Week 6, Day 1 Score: {score}/{total}")
print(f"{'='*40}")
if score == total:
    print("  Outstanding! You've mastered the os module.")
elif score >= 3:
    print("  Good progress. Review the tasks you missed.")
else:
    print("  Keep practicing. Re-read lesson.md and try again.")
