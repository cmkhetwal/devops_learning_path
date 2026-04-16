"""
Week 6, Day 3: Auto-Checker for shutil & pathlib exercises.
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


# --- TASK 1: backup_file ---
print("Task 1: backup_file()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import backup_file

with tempfile.TemporaryDirectory() as tmp:
    src = Path(tmp) / "myconfig.yml"
    src.write_text("server: nginx\\nport: 80\\n")
    backup_dir = os.path.join(tmp, "backups", "nested")
    result = backup_file(str(src), backup_dir)

    assert result is not None, "Must return a value"
    result_path = Path(result)
    assert result_path.exists(), f"Backup file does not exist: {{result}}"
    assert result_path.name == "myconfig.yml", f"Wrong filename: {{result_path.name}}"
    assert result_path.read_text() == "server: nginx\\nport: 80\\n", "Content mismatch"
    assert result_path.parent == Path(backup_dir), f"Wrong directory: {{result_path.parent}}"
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


# --- TASK 2: group_files_by_extension ---
print("Task 2: group_files_by_extension()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import group_files_by_extension

with tempfile.TemporaryDirectory() as tmp:
    for name in ["app.py", "utils.py", "config.yml", "data.csv", "readme.CSV", "Makefile"]:
        (Path(tmp) / name).touch()
    # Create a subdirectory (should be ignored)
    (Path(tmp) / "subdir").mkdir()

    result = group_files_by_extension(tmp)
    assert isinstance(result, dict), "Must return a dict"
    assert sorted(result.get(".py", [])) == ["app.py", "utils.py"], f".py wrong: {{result.get('.py')}}"
    assert result.get(".yml") == ["config.yml"], f".yml wrong: {{result.get('.yml')}}"
    # .csv should include both data.csv and readme.CSV (lowercased extension)
    csv_files = sorted(result.get(".csv", []))
    assert len(csv_files) == 2, f".csv should have 2 files: {{csv_files}}"
    assert result.get("") == ["Makefile"], f"no-ext wrong: {{result.get('')}}"
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


# --- TASK 3: organize_files ---
print("Task 3: organize_files()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import organize_files

with tempfile.TemporaryDirectory() as tmp:
    for name in ["report.pdf", "data.csv", "script.py", "notes.txt", "Makefile"]:
        (Path(tmp) / name).touch()
    count = organize_files(tmp)
    assert isinstance(count, int), "Must return an int"
    assert count == 5, f"Expected 5 files moved, got {{count}}"
    assert (Path(tmp) / "pdf" / "report.pdf").exists(), "report.pdf not in pdf/"
    assert (Path(tmp) / "csv" / "data.csv").exists(), "data.csv not in csv/"
    assert (Path(tmp) / "py" / "script.py").exists(), "script.py not in py/"
    assert (Path(tmp) / "txt" / "notes.txt").exists(), "notes.txt not in txt/"
    assert (Path(tmp) / "other" / "Makefile").exists(), "Makefile not in other/"
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


# --- TASK 4: find_files ---
print("Task 4: find_files()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import find_files

with tempfile.TemporaryDirectory() as tmp:
    (Path(tmp) / "small.log").write_text("x" * 10)
    (Path(tmp) / "big.log").write_text("x" * 1000)
    sub = Path(tmp) / "sub"
    sub.mkdir()
    (sub / "medium.log").write_text("x" * 500)
    (Path(tmp) / "ignore.txt").write_text("not a log")

    result = find_files(tmp, "*.log")
    assert isinstance(result, list), "Must return a list"
    assert len(result) == 3, f"Expected 3 log files, got {{len(result)}}"

    # Check structure
    for item in result:
        assert "name" in item, "Missing key: name"
        assert "path" in item, "Missing key: path"
        assert "size" in item, "Missing key: size"
        assert isinstance(item["size"], int), "size must be int"

    # Check sorted by size (largest first)
    assert result[0]["name"] == "big.log", f"First should be big.log: {{result[0]['name']}}"
    assert result[0]["size"] == 1000, f"big.log size wrong: {{result[0]['size']}}"
    assert result[-1]["name"] == "small.log", f"Last should be small.log: {{result[-1]['name']}}"

    # Check path is absolute
    assert os.path.isabs(result[0]["path"]), "path should be absolute"
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


# --- TASK 5: create_project_scaffold ---
print("Task 5: create_project_scaffold()")
code = """
import sys, os, tempfile
from pathlib import Path
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import create_project_scaffold

with tempfile.TemporaryDirectory() as tmp:
    result = create_project_scaffold(tmp, "my_api")
    assert result is not None, "Must return a value"
    root = Path(result)
    assert root.exists(), f"Project root does not exist: {{root}}"
    assert root.name == "my_api", f"Wrong project name: {{root.name}}"

    # Check directories
    assert (root / "app").is_dir(), "app/ directory missing"
    assert (root / "config").is_dir(), "config/ directory missing"
    assert (root / "tests").is_dir(), "tests/ directory missing"
    assert (root / "logs").is_dir(), "logs/ directory missing"

    # Check files exist and have content
    assert (root / "app" / "__init__.py").is_file(), "app/__init__.py missing"
    assert (root / "app" / "main.py").is_file(), "app/main.py missing"
    assert "Main application" in (root / "app" / "main.py").read_text(), "main.py wrong content"
    assert (root / "config" / "settings.yml").is_file(), "config/settings.yml missing"
    assert "development" in (root / "config" / "settings.yml").read_text(), "settings.yml wrong"
    assert (root / "tests" / "__init__.py").is_file(), "tests/__init__.py missing"
    assert (root / "tests" / "test_main.py").is_file(), "tests/test_main.py missing"
    assert (root / "README.md").is_file(), "README.md missing"
    assert "my_api" in (root / "README.md").read_text(), "README.md should contain project name"
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
print(f"  Week 6, Day 3 Score: {score}/{total}")
print(f"{'='*40}")
if score == total:
    print("  Outstanding! You've mastered shutil & pathlib.")
elif score >= 3:
    print("  Good progress. Review the tasks you missed.")
else:
    print("  Keep practicing. Re-read lesson.md and try again.")
