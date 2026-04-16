"""
Week 6, Day 7: Auto-Checker for Quiz Day.
Run: python3 check.py
"""

import subprocess
import sys
import os

EXERCISE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
score = 0
total = 10


def run_python(code):
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10,
        cwd=os.path.dirname(EXERCISE)
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# --- Q1: is_valid_nonempty_dir ---
print("Q1:  is_valid_nonempty_dir()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import is_valid_nonempty_dir

# /tmp should be valid and non-empty
assert is_valid_nonempty_dir("/tmp") == True, "/tmp should be True"

# Non-existent path
assert is_valid_nonempty_dir("/nonexistent_xyz_123") == False, "nonexistent should be False"

# Empty directory
with tempfile.TemporaryDirectory() as tmp:
    assert is_valid_nonempty_dir(tmp) == False, "empty dir should be False"
    Path(tmp, "file.txt").touch()
    assert is_valid_nonempty_dir(tmp) == True, "non-empty dir should be True"

# File, not directory
with tempfile.NamedTemporaryFile() as f:
    assert is_valid_nonempty_dir(f.name) == False, "file should be False"
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


# --- Q2: safe_run ---
print("Q2:  safe_run()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import safe_run

# Successful command
success, output = safe_run(["echo", "hello world"])
assert success == True, f"echo should succeed: {{success}}"
assert output == "hello world", f"output wrong: '{{output}}'"

# Failed command
success2, output2 = safe_run(["ls", "/nonexistent_xyz_123"])
assert success2 == False, "ls nonexistent should fail"
assert isinstance(output2, str), "output should be string"

# Command not found
success3, output3 = safe_run(["totally_fake_command_xyz"])
assert success3 == False, "fake command should fail"
assert output3 == "not found", f"should say 'not found': '{{output3}}'"
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


# --- Q3: dir_total_size ---
print("Q3:  dir_total_size()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import dir_total_size

with tempfile.TemporaryDirectory() as tmp:
    Path(tmp, "a.txt").write_text("hello")       # 5 bytes
    Path(tmp, "b.txt").write_text("world!!")      # 7 bytes
    sub = Path(tmp) / "subdir"
    sub.mkdir()
    Path(sub, "c.txt").write_text("inside sub")   # Should NOT be counted

    result = dir_total_size(tmp)
    assert isinstance(result, int), f"Must return int, got {{type(result)}}"
    assert result == 12, f"Expected 12 bytes, got {{result}}"

# Empty directory
with tempfile.TemporaryDirectory() as tmp:
    assert dir_total_size(tmp) == 0, "Empty dir should be 0 bytes"
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


# --- Q4: find_capitalized_words ---
print("Q4:  find_capitalized_words()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import find_capitalized_words

result = find_capitalized_words("The Quick brown Fox jumps Over")
assert isinstance(result, list), "Must return a list"
assert result == ["The", "Quick", "Fox", "Over"], f"Wrong: {{result}}"

assert find_capitalized_words("no caps here") == [], "Should return [] for no caps"
assert find_capitalized_words("ALL CAPS Test") == ["ALL", "CAPS", "Test"] or find_capitalized_words("ALL CAPS Test") == ["Test"], "Tricky case"

# Just check a simpler case to be more flexible with the pattern
result2 = find_capitalized_words("Hello World")
assert "Hello" in result2 and "World" in result2, f"Should find Hello World: {{result2}}"
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


# --- Q5: copy_conf_files ---
print("Q5:  copy_conf_files()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import copy_conf_files

with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "src"
    dst = Path(tmp) / "dst"
    src.mkdir()

    (src / "nginx.conf").write_text("server {{}}")
    (src / "app.conf").write_text("key=val")
    (src / "readme.txt").write_text("not a conf")
    (src / "data.csv").write_text("a,b,c")

    count = copy_conf_files(str(src), str(dst))
    assert isinstance(count, int), "Must return int"
    assert count == 2, f"Expected 2 conf files, got {{count}}"
    assert (dst / "nginx.conf").exists(), "nginx.conf not copied"
    assert (dst / "app.conf").exists(), "app.conf not copied"
    assert not (dst / "readme.txt").exists(), "txt file should not be copied"
    assert (dst / "nginx.conf").read_text() == "server {{}}", "Content mismatch"
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


# --- Q6: detect_severity ---
print("Q6:  detect_severity()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import detect_severity

assert detect_severity("ERROR: disk full") == "ERROR", "Should detect ERROR"
assert detect_severity("error connection refused") == "ERROR", "Should detect lowercase error"
assert detect_severity("WARNING: high cpu") == "WARNING", "Should detect WARNING"
assert detect_severity("warn: something") == "WARNING", "Should detect warn"
assert detect_severity("INFO server started") == "INFO", "Should detect INFO"
assert detect_severity("info: all good") == "INFO", "Should detect lowercase info"
assert detect_severity("something happened") == "UNKNOWN", "Should be UNKNOWN"
assert detect_severity("") == "UNKNOWN", "Empty should be UNKNOWN"

# ERROR takes priority over others
assert detect_severity("ERROR and WARNING in same line") == "ERROR", "ERROR should take priority"
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


# --- Q7: check_env_vars ---
print("Q7:  check_env_vars()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import check_env_vars

os.environ["TEST_A"] = "yes"
os.environ["TEST_B"] = "yes"
# Make sure TEST_C is not set
os.environ.pop("TEST_C", None)

result = check_env_vars(["TEST_A", "TEST_C", "TEST_B"])
assert isinstance(result, dict), "Must return a dict"
assert "set" in result, "Missing key: set"
assert "missing" in result, "Missing key: missing"
assert result["set"] == ["TEST_A", "TEST_B"], f"set wrong: {{result['set']}}"
assert result["missing"] == ["TEST_C"], f"missing wrong: {{result['missing']}}"

# Test empty list
result2 = check_env_vars([])
assert result2["set"] == [], "Empty input set should be []"
assert result2["missing"] == [], "Empty input missing should be []"
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


# --- Q8: parse_env_file ---
print("Q8:  parse_env_file()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import parse_env_file

text = "HOST=localhost\\nPORT=8080\\nDEBUG=true\\n\\nINVALID LINE\\n"
result = parse_env_file(text)
assert isinstance(result, dict), "Must return a dict"
assert result == {{"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}}, f"Wrong: {{result}}"

# Test with spaces
text2 = " KEY = value \\n"
result2 = parse_env_file(text2)
assert result2.get("KEY") == "value", f"Should strip whitespace: {{result2}}"

# Test with value containing =
text3 = "URL=https://host.com/path?a=1\\n"
result3 = parse_env_file(text3)
assert result3.get("URL") == "https://host.com/path?a=1", f"Should handle = in value: {{result3}}"

# Test empty
assert parse_env_file("") == {{}}, "Empty string should give empty dict"
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


# --- Q9: path_breadcrumb ---
print("Q9:  path_breadcrumb()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import path_breadcrumb

result = path_breadcrumb("/var/log/nginx/access.log")
assert isinstance(result, str), "Must return a string"
assert result == "var > log > nginx > access.log", f"Wrong: '{{result}}'"

assert path_breadcrumb("/etc/hosts") == "etc > hosts", f"Simple path wrong"
assert path_breadcrumb("/single") == "single", f"Single component wrong"
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


# --- Q10: get_full_filesystems ---
print("Q10: get_full_filesystems()")
code = '''
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import get_full_filesystems

df_output = """Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/sda1   50G   45G   5G     90%   /
tmpfs       4G    100M  3.9G   3%    /tmp
/dev/sdb1   100G  82G   18G    82%   /data"""

result = get_full_filesystems(df_output, 80)
assert isinstance(result, list), "Must return a list"
assert len(result) == 2, f"Expected 2 results, got {{len(result)}}"

# Check first result (90%)
r1 = [r for r in result if r["filesystem"] == "/dev/sda1"]
assert len(r1) == 1, "/dev/sda1 should be in results"
assert r1[0]["percent"] == 90, f"percent wrong: {{r1[0]['percent']}}"
assert r1[0]["mount"] == "/", f"mount wrong: {{r1[0]['mount']}}"

# Check second result (82%)
r2 = [r for r in result if r["filesystem"] == "/dev/sdb1"]
assert len(r2) == 1, "/dev/sdb1 should be in results"
assert r2[0]["percent"] == 82, f"percent wrong: {{r2[0]['percent']}}"

# tmpfs (3%) should NOT be in results
r3 = [r for r in result if r["filesystem"] == "tmpfs"]
assert len(r3) == 0, "tmpfs should not be in results"

# Test with high threshold (no results)
result2 = get_full_filesystems(df_output, 95)
assert result2 == [], f"No filesystems at 95%: {{result2}}"
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


# --- SUMMARY ---
print(f"\n{'='*40}")
print(f"  Week 6 Quiz Score: {score}/{total}")
print(f"{'='*40}")

if score == total:
    print("  PERFECT SCORE! Week 6 complete.")
    print("  You have mastered OS & System Automation.")
    print("  You are ready for Week 7!")
elif score >= 8:
    print("  Excellent! Strong understanding of the material.")
elif score >= 6:
    print("  Good work. Review the topics you missed.")
elif score >= 4:
    print("  Decent start. Go back and review Days 1-5.")
else:
    print("  Needs more practice. Re-read the lessons and")
    print("  complete the exercises before moving on.")
