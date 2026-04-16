#!/usr/bin/env python3
"""
Week 12, Day 6: Code Review & Refactoring - Auto-Checker
"""

import subprocess
import sys
import os

EXERCISE_DIR = os.path.dirname(os.path.abspath(__file__))


def run_test(test_code):
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10,
        cwd=EXERCISE_DIR,
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()


def main():
    score = 0
    total = 6

    print("=" * 50)
    print("  WEEK 12, DAY 6 - Code Review Checker")
    print("=" * 50)
    print()

    # Task 1: refactor_server_checker
    print("Task 1: refactor_server_checker()")
    ok, out, err = run_test('''
import sys; sys.path.insert(0, ".")
from exercise import refactor_server_checker
servers = [
    {"name": "web-01", "status": "healthy"},
    {"name": "web-02", "status": "degraded"},
    {"name": "db-01", "status": "offline"},
    {"name": "bad"},
    "not_a_dict",
]
results = refactor_server_checker(servers)
assert isinstance(results, list), "Must return list"
valid = [r for r in results if r.get("name") in ("web-01", "web-02", "db-01")]
assert len(valid) == 3, f"Expected 3 valid results, got {len(valid)}"
web01 = [r for r in results if r.get("name") == "web-01"][0]
assert web01["is_healthy"] == True
web02 = [r for r in results if r.get("name") == "web-02"][0]
assert web02["is_healthy"] == False
print("PASS")
''')
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  {err.splitlines()[-1][:100]}")

    # Task 2: refactor_deploy_function
    print("Task 2: refactor_deploy_function()")
    ok, out, err = run_test('''
import sys; sys.path.insert(0, ".")
from exercise import refactor_deploy_function
r = refactor_deploy_function("web-api", "2.0", "production", ["web-01", "web-02"])
assert r["status"] == "success"
assert r["app"] == "web-api"
assert r["server_count"] == 2
r2 = refactor_deploy_function("app", "1.0", "invalid_env", ["s1"])
assert r2["status"] == "error"
r3 = refactor_deploy_function("app", "1.0", "staging", [])
assert r3["status"] == "error"
print("PASS")
''')
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  {err.splitlines()[-1][:100]}")

    # Task 3: refactor_config_loader
    print("Task 3: refactor_config_loader()")
    ok, out, err = run_test('''
import sys; sys.path.insert(0, ".")
from exercise import refactor_config_loader
config = """# Database config
DB_HOST=localhost
DB_PORT=5432
DB_URL=postgres://user:pass@host:5432/db
DEBUG=false
EMPTY_VAL=
"""
r = refactor_config_loader(config)
assert isinstance(r, dict)
assert r["DB_HOST"] == "localhost"
assert r["DB_PORT"] == "5432"
assert r["DB_URL"] == "postgres://user:pass@host:5432/db"
assert "#" not in str(list(r.keys()))
print("PASS")
''')
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  {err.splitlines()[-1][:100]}")

    # Task 4: RefactoredInventory
    print("Task 4: RefactoredInventory class")
    ok, out, err = run_test('''
import sys; sys.path.insert(0, ".")
from exercise import RefactoredInventory
inv = RefactoredInventory()
inv.add_server("web-01", "10.0.1.1", "web")
inv.add_server("db-01", "10.0.2.1", "database")
assert inv.server_count() == 2
g = inv.get_server("web-01")
assert g["name"] == "web-01"
try:
    inv.add_server("web-01", "10.0.1.2", "web")
    assert False, "Should raise ValueError"
except ValueError:
    pass
all_s = inv.list_servers()
assert len(all_s) == 2
web_only = inv.list_servers(role="web")
assert len(web_only) == 1
inv.remove_server("db-01")
assert inv.server_count() == 1
print("PASS")
''')
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  {err.splitlines()[-1][:100]}")

    # Task 5: refactor_log_parser
    print("Task 5: refactor_log_parser()")
    ok, out, err = run_test('''
import sys; sys.path.insert(0, ".")
from exercise import refactor_log_parser
logs = """2025-01-15 14:30:00 INFO Server started successfully
2025-01-15 14:31:00 WARNING High memory usage detected
2025-01-15 14:32:00 ERROR Connection to database failed
malformed line here
2025-01-15 14:34:00 CRITICAL System shutdown
"""
results = refactor_log_parser(logs)
assert isinstance(results, list)
entries = [r for r in results if not r.get("_summary")]
summary = [r for r in results if r.get("_summary")]
assert len(entries) >= 4
assert len(summary) == 1
error_entry = [e for e in entries if e.get("level") == "ERROR"][0]
assert error_entry["is_error"] == True
print("PASS")
''')
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  {err.splitlines()[-1][:100]}")

    # Task 6: RefactoredPipeline
    print("Task 6: RefactoredPipeline class")
    ok, out, err = run_test('''
import sys; sys.path.insert(0, ".")
from exercise import RefactoredPipeline
p = RefactoredPipeline()
p.add_stage("build", lambda: "artifact.zip")
p.add_stage("test", lambda: "all passed")
p.add_stage("deploy", lambda: "deployed")
results = p.run()
assert len(results) == 3
assert all(r["status"] == "success" for r in results)
s = p.get_summary()
assert s["success"] == True
assert s["total"] == 3
p2 = RefactoredPipeline()
p2.add_stage("build", lambda: "ok")
p2.add_stage("test", lambda: 1/0)
p2.add_stage("deploy", lambda: "deployed")
r2 = p2.run()
assert r2[1]["status"] == "failed"
assert r2[2]["status"] == "skipped"
s2 = p2.get_summary()
assert s2["success"] == False
print("PASS")
''')
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL")
        if err: print(f"  {err.splitlines()[-1][:100]}")

    print(f"\n{'=' * 50}")
    print(f"  Score: {score}/{total}")
    if score == total:
        print("  PERFECT! Your refactoring skills are professional-grade!")
    elif score >= 4:
        print("  Great work! Fix the remaining items.")
    else:
        print("  Review clean code principles and try again.")
    print("=" * 50)


if __name__ == "__main__":
    main()
