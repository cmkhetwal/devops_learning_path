"""
Week 4, Day 5: Modules & Imports - Auto-Checker
================================================
Run this script to check your exercise solutions.
Usage: python check.py
"""

import subprocess
import sys
import os

EXERCISE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

tests = {
    "Task 1 - get_system_info returns dict with correct keys": {
        "code": """from exercise import get_system_info
info = get_system_info()
keys = sorted(info.keys())
print(keys)
print(type(info['python_version']).__name__)
print(type(info['os_name']).__name__)
print(type(info['current_dir']).__name__)""",
        "expected": "['current_dir', 'os_name', 'python_version']\nstr\nstr\nstr"
    },
    "Task 1 - get_system_info has valid python_version": {
        "code": """from exercise import get_system_info
info = get_system_info()
parts = info['python_version'].split('.')
print(len(parts) >= 2)""",
        "expected": "True"
    },
    "Task 2 - dict_to_json_string basic": {
        "code": """from exercise import dict_to_json_string
result = dict_to_json_string({"name": "web-01", "port": 8080})
print(result)""",
        "expected": '{\n  "name": "web-01",\n  "port": 8080\n}'
    },
    "Task 2 - dict_to_json_string sorts keys": {
        "code": """from exercise import dict_to_json_string
result = dict_to_json_string({"z_key": 1, "a_key": 2})
print(result)""",
        "expected": '{\n  "a_key": 2,\n  "z_key": 1\n}'
    },
    "Task 3 - json_string_to_dict basic": {
        "code": """from exercise import json_string_to_dict
result = json_string_to_dict('{"name": "web-01", "port": 8080}')
print(result)""",
        "expected": "{'name': 'web-01', 'port': 8080}"
    },
    "Task 3 - json_string_to_dict preserves types": {
        "code": """from exercise import json_string_to_dict
result = json_string_to_dict('{"count": 5, "active": true}')
print(type(result['count']).__name__, type(result['active']).__name__)""",
        "expected": "int bool"
    },
    "Task 4 - use_server_utils('web-01', 8080)": {
        "code": """from exercise import use_server_utils
result = use_server_utils('web-01', 8080)
print(result)""",
        "expected": "{'hostname': 'web-01.example.com', 'port_valid': True, 'status': 'healthy'}"
    },
    "Task 4 - use_server_utils('db 01', 99999)": {
        "code": """from exercise import use_server_utils
result = use_server_utils('db 01', 99999)
print(result)""",
        "expected": "{'hostname': 'db-01.example.com', 'port_valid': False, 'status': 'healthy'}"
    },
    "Task 5 - get_default_config returns correct dict": {
        "code": "from exercise import get_default_config; print(get_default_config())",
        "expected": "{'port': 8080, 'region': 'us-east-1', 'max_retries': 3, 'timeout': 30}"
    },
    "Task 5 - get_default_config returns a copy": {
        "code": """from exercise import get_default_config
from server_utils import DEFAULT_CONFIG
copy = get_default_config()
copy['port'] = 9999
print(DEFAULT_CONFIG['port'])""",
        "expected": "8080"
    },
    "Task 6 - generate_random_hostname default prefix": {
        "code": """import random; random.seed(42)
from exercise import generate_random_hostname
result = generate_random_hostname()
parts = result.split('-')
print(parts[0])
print(1000 <= int(parts[1]) <= 9999)""",
        "expected": "server\nTrue"
    },
    "Task 6 - generate_random_hostname custom prefix": {
        "code": """import random; random.seed(100)
from exercise import generate_random_hostname
result = generate_random_hostname('web')
print(result.startswith('web-'))
parts = result.split('-')
print(1000 <= int(parts[1]) <= 9999)""",
        "expected": "True\nTrue"
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
    print("  Week 4, Day 5: Modules & Imports - Checking Solutions")
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
        print("  PERFECT! You've mastered modules and imports!")
    elif passed >= total * 0.7:
        print("  Good progress! Review the failing tests and try again.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 60)


if __name__ == "__main__":
    main()
