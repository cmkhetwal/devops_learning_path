"""
Week 4, Day 1: Functions Basics - Auto-Checker
===============================================
Run this script to check your exercise solutions.
Usage: python check.py
"""

import subprocess
import sys
import os

EXERCISE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

tests = {
    "Task 1 - is_port_valid(80) returns True": {
        "code": "from exercise import is_port_valid; print(is_port_valid(80))",
        "expected": "True"
    },
    "Task 1 - is_port_valid(0) returns False": {
        "code": "from exercise import is_port_valid; print(is_port_valid(0))",
        "expected": "False"
    },
    "Task 1 - is_port_valid(65535) returns True": {
        "code": "from exercise import is_port_valid; print(is_port_valid(65535))",
        "expected": "True"
    },
    "Task 1 - is_port_valid(70000) returns False": {
        "code": "from exercise import is_port_valid; print(is_port_valid(70000))",
        "expected": "False"
    },
    "Task 1 - is_port_valid('80') returns False": {
        "code": "from exercise import is_port_valid; print(is_port_valid('80'))",
        "expected": "False"
    },
    "Task 2 - format_hostname('  Web Server 01  ')": {
        "code": "from exercise import format_hostname; print(format_hostname('  Web Server 01  '))",
        "expected": "web-server-01"
    },
    "Task 2 - format_hostname('DB SERVER')": {
        "code": "from exercise import format_hostname; print(format_hostname('DB SERVER'))",
        "expected": "db-server"
    },
    "Task 2 - format_hostname('cache-01')": {
        "code": "from exercise import format_hostname; print(format_hostname('cache-01'))",
        "expected": "cache-01"
    },
    "Task 3 - calculate_uptime(720, 2) returns 99.72": {
        "code": "from exercise import calculate_uptime; print(calculate_uptime(720, 2))",
        "expected": "99.72"
    },
    "Task 3 - calculate_uptime(100, 0) returns 100.0": {
        "code": "from exercise import calculate_uptime; print(calculate_uptime(100, 0))",
        "expected": "100.0"
    },
    "Task 3 - calculate_uptime(0, 5) returns 0.0": {
        "code": "from exercise import calculate_uptime; print(calculate_uptime(0, 5))",
        "expected": "0.0"
    },
    "Task 3 - calculate_uptime(100, -1) returns 100.0": {
        "code": "from exercise import calculate_uptime; print(calculate_uptime(100, -1))",
        "expected": "100.0"
    },
    "Task 4 - create_server_summary('Web01', '10.0.0.1', 'running')": {
        "code": "from exercise import create_server_summary; print(create_server_summary('Web01', '10.0.0.1', 'running'))",
        "expected": "Server: web01 | IP: 10.0.0.1 | Status: RUNNING"
    },
    "Task 5 - get_service_port('http') returns 80": {
        "code": "from exercise import get_service_port; print(get_service_port('http'))",
        "expected": "80"
    },
    "Task 5 - get_service_port('SSH') returns 22": {
        "code": "from exercise import get_service_port; print(get_service_port('SSH'))",
        "expected": "22"
    },
    "Task 5 - get_service_port('redis') returns -1": {
        "code": "from exercise import get_service_port; print(get_service_port('redis'))",
        "expected": "-1"
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
    print("  Week 4, Day 1: Functions Basics - Checking Solutions")
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
        print("  PERFECT! You've mastered function basics!")
    elif passed >= total * 0.7:
        print("  Good progress! Review the failing tests and try again.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 60)


if __name__ == "__main__":
    main()
