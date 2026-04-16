"""
Week 4, Day 4: Built-in Functions - Auto-Checker
=================================================
Run this script to check your exercise solutions.
Usage: python check.py
"""

import subprocess
import sys
import os

EXERCISE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

tests = {
    "Task 1 - get_unhealthy_servers with mixed statuses": {
        "code": """from exercise import get_unhealthy_servers
result = get_unhealthy_servers([
    {"name": "web-01", "status": "running"},
    {"name": "db-01", "status": "stopped"},
    {"name": "cache-01", "status": "error"},
])
print(result)""",
        "expected": "['db-01', 'cache-01']"
    },
    "Task 1 - get_unhealthy_servers all healthy": {
        "code": """from exercise import get_unhealthy_servers
result = get_unhealthy_servers([{"name": "web-01", "status": "running"}])
print(result)""",
        "expected": "[]"
    },
    "Task 2 - sort_by_cpu highest first": {
        "code": """from exercise import sort_by_cpu
result = sort_by_cpu([
    {"name": "web-01", "cpu": 45},
    {"name": "db-01", "cpu": 92},
    {"name": "cache-01", "cpu": 67},
])
print([s["name"] for s in result])""",
        "expected": "['db-01', 'cache-01', 'web-01']"
    },
    "Task 2 - sort_by_cpu preserves dict structure": {
        "code": """from exercise import sort_by_cpu
result = sort_by_cpu([{"name": "a", "cpu": 10}, {"name": "b", "cpu": 20}])
print(result[0])""",
        "expected": "{'name': 'b', 'cpu': 20}"
    },
    "Task 3 - all_servers_healthy all running": {
        "code": """from exercise import all_servers_healthy
print(all_servers_healthy([
    {"name": "web-01", "status": "running"},
    {"name": "db-01", "status": "running"},
]))""",
        "expected": "True"
    },
    "Task 3 - all_servers_healthy one stopped": {
        "code": """from exercise import all_servers_healthy
print(all_servers_healthy([
    {"name": "web-01", "status": "running"},
    {"name": "db-01", "status": "stopped"},
]))""",
        "expected": "False"
    },
    "Task 3 - all_servers_healthy empty list": {
        "code": "from exercise import all_servers_healthy; print(all_servers_healthy([]))",
        "expected": "True"
    },
    "Task 4 - create_server_report combines lists": {
        "code": """from exercise import create_server_report
result = create_server_report(["web-01", "db-01"], [85, 45], [70, 60])
print(result)""",
        "expected": "[{'name': 'web-01', 'cpu': 85, 'memory': 70}, {'name': 'db-01', 'cpu': 45, 'memory': 60}]"
    },
    "Task 4 - create_server_report single server": {
        "code": """from exercise import create_server_report
result = create_server_report(["web-01"], [85], [70])
print(result)""",
        "expected": "[{'name': 'web-01', 'cpu': 85, 'memory': 70}]"
    },
    "Task 5 - get_server_rankings": {
        "code": """from exercise import get_server_rankings
result = get_server_rankings([
    {"name": "web-01", "cpu": 45},
    {"name": "db-01", "cpu": 92},
    {"name": "cache-01", "cpu": 67},
])
print(result)""",
        "expected": "['1. db-01 (CPU: 92%)', '2. cache-01 (CPU: 67%)', '3. web-01 (CPU: 45%)']"
    },
    "Task 6 - any_critical_alerts no alerts": {
        "code": """from exercise import any_critical_alerts
print(any_critical_alerts([
    {"name": "web-01", "cpu": 85, "memory": 70},
    {"name": "db-01", "cpu": 45, "memory": 60},
]))""",
        "expected": "False"
    },
    "Task 6 - any_critical_alerts CPU alert": {
        "code": """from exercise import any_critical_alerts
print(any_critical_alerts([
    {"name": "web-01", "cpu": 95, "memory": 70},
    {"name": "db-01", "cpu": 45, "memory": 60},
]))""",
        "expected": "True"
    },
    "Task 6 - any_critical_alerts memory alert": {
        "code": """from exercise import any_critical_alerts
print(any_critical_alerts([
    {"name": "web-01", "cpu": 50, "memory": 90},
]))""",
        "expected": "True"
    },
    "Task 7 - extract_ports multiple": {
        "code": """from exercise import extract_ports
print(extract_ports(["web-01:8080", "db-01:5432", "cache-01:6379"]))""",
        "expected": "[8080, 5432, 6379]"
    },
    "Task 7 - extract_ports single": {
        "code": "from exercise import extract_ports; print(extract_ports(['localhost:80']))",
        "expected": "[80]"
    },
}


def run_test(name, code, expected):
    """Run a single test and return True/False."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        actual = result.stdout.strip()
        if result.returncode != 0:
            print(f"  FAIL: {name}")
            print(f"        Error: {result.stderr.strip()[:120]}")
            return False
        if actual == expected:
            print(f"  PASS: {name}")
            return True
        else:
            print(f"  FAIL: {name}")
            print(f"        Expected: {expected}")
            print(f"        Got:      {actual}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  FAIL: {name} (timed out)")
        return False
    except Exception as e:
        print(f"  FAIL: {name} ({e})")
        return False


def main():
    print("=" * 60)
    print("  Week 4, Day 4: Built-in Functions - Checking Solutions")
    print("=" * 60)
    print()

    passed = 0
    total = len(tests)

    for name, test in tests.items():
        if run_test(name, test["code"], test["expected"]):
            passed += 1

    print()
    print("-" * 60)
    print(f"  Score: {passed}/{total} tests passed")
    if passed == total:
        print("  PERFECT! You've mastered Python's built-in functions!")
    elif passed >= total * 0.7:
        print("  Good progress! Review the failing tests and try again.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 60)


if __name__ == "__main__":
    main()
