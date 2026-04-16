"""
Week 4, Day 2: Function Arguments - Auto-Checker
=================================================
Run this script to check your exercise solutions.
Usage: python check.py
"""

import subprocess
import sys
import os

EXERCISE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

tests = {
    "Task 1 - create_instance('web-01') with defaults": {
        "code": "from exercise import create_instance; print(create_instance('web-01'))",
        "expected": "{'name': 'web-01', 'region': 'us-east-1', 'size': 't2.micro', 'count': 1}"
    },
    "Task 1 - create_instance with overrides": {
        "code": "from exercise import create_instance; print(create_instance('db-01', region='eu-west-1', size='r5.large', count=2))",
        "expected": "{'name': 'db-01', 'region': 'eu-west-1', 'size': 'r5.large', 'count': 2}"
    },
    "Task 2 - log_message('Server started') default level": {
        "code": "from exercise import log_message; print(log_message('Server started'))",
        "expected": "[INFO] Server started"
    },
    "Task 2 - log_message with ERROR and tags": {
        "code": "from exercise import log_message; print(log_message('Deploy failed', 'ERROR', 'deploy', 'critical'))",
        "expected": "[ERROR] Deploy failed #deploy #critical"
    },
    "Task 2 - log_message with lowercase level": {
        "code": "from exercise import log_message; print(log_message('Test', 'warning'))",
        "expected": "[WARNING] Test"
    },
    "Task 3 - build_connection_string no options": {
        "code": "from exercise import build_connection_string; print(build_connection_string('localhost', 5432))",
        "expected": "localhost:5432"
    },
    "Task 3 - build_connection_string with options": {
        "code": "from exercise import build_connection_string; print(build_connection_string('db.example.com', 3306, user='admin', db='myapp'))",
        "expected": "db.example.com:3306?db=myapp&user=admin"
    },
    "Task 4 - apply_config with multiple settings": {
        "code": "from exercise import apply_config; print(apply_config('web-01', {'port': 8080, 'debug': True}))",
        "expected": "['web-01: debug=True', 'web-01: port=8080']"
    },
    "Task 4 - apply_config with single setting": {
        "code": "from exercise import apply_config; print(apply_config('db-01', {'max_connections': 100}))",
        "expected": "['db-01: max_connections=100']"
    },
    "Task 5 - merge_server_tags two lists": {
        "code": "from exercise import merge_server_tags; print(merge_server_tags(['web', 'prod'], ['web', 'us-east']))",
        "expected": "['prod', 'us-east', 'web']"
    },
    "Task 5 - merge_server_tags three lists": {
        "code": "from exercise import merge_server_tags; print(merge_server_tags(['db'], ['cache'], ['db', 'cache', 'prod']))",
        "expected": "['cache', 'db', 'prod']"
    },
    "Task 5 - merge_server_tags empty": {
        "code": "from exercise import merge_server_tags; print(merge_server_tags())",
        "expected": "[]"
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
    print("  Week 4, Day 2: Function Arguments - Checking Solutions")
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
        print("  PERFECT! You've mastered function arguments!")
    elif passed >= total * 0.7:
        print("  Good progress! Review the failing tests and try again.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 60)


if __name__ == "__main__":
    main()
