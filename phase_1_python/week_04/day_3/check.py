"""
Week 4, Day 3: Scope & Variables - Auto-Checker
================================================
Run this script to check your exercise solutions.
Usage: python check.py
"""

import subprocess
import sys
import os

EXERCISE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

tests = {
    "Task 1 - fix_counter with 2 errors": {
        "code": "from exercise import fix_counter; print(fix_counter(['ERROR: disk full', 'INFO: started', 'ERROR: timeout']))",
        "expected": "2"
    },
    "Task 1 - fix_counter with no errors": {
        "code": "from exercise import fix_counter; print(fix_counter(['INFO: all good']))",
        "expected": "0"
    },
    "Task 1 - fix_counter with empty list": {
        "code": "from exercise import fix_counter; print(fix_counter([]))",
        "expected": "0"
    },
    "Task 1 - fix_counter called twice gives independent results": {
        "code": "from exercise import fix_counter; fix_counter(['ERROR: one']); print(fix_counter(['ERROR: a', 'ERROR: b']))",
        "expected": "2"
    },
    "Task 2 - build_server_list with no existing": {
        "code": "from exercise import build_server_list; print(build_server_list(['web-01', 'web-02']))",
        "expected": "['web-01', 'web-02']"
    },
    "Task 2 - build_server_list with existing": {
        "code": "from exercise import build_server_list; print(build_server_list(['web-03'], existing=['web-01', 'web-02']))",
        "expected": "['web-01', 'web-02', 'web-03']"
    },
    "Task 2 - build_server_list doesn't accumulate": {
        "code": "from exercise import build_server_list; build_server_list(['a']); print(build_server_list(['b']))",
        "expected": "['b']"
    },
    "Task 2 - build_server_list doesn't modify original": {
        "code": "from exercise import build_server_list; orig = ['web-01']; build_server_list(['web-02'], existing=orig); print(orig)",
        "expected": "['web-01']"
    },
    "Task 3 - process_metrics normal list": {
        "code": "from exercise import process_metrics; print(process_metrics([80, 45, 92, 15, 67]))",
        "expected": "{'total': 299, 'highest': 92, 'lowest': 15}"
    },
    "Task 3 - process_metrics empty list": {
        "code": "from exercise import process_metrics; print(process_metrics([]))",
        "expected": "{'total': 0, 'highest': 0, 'lowest': 0}"
    },
    "Task 3 - process_metrics called twice gives independent results": {
        "code": "from exercise import process_metrics; process_metrics([10, 20]); print(process_metrics([5, 15]))",
        "expected": "{'total': 20, 'highest': 15, 'lowest': 5}"
    },
    "Task 4 - create_alert_checker(90) with 95": {
        "code": "from exercise import create_alert_checker; check = create_alert_checker(90); print(check(95))",
        "expected": "True"
    },
    "Task 4 - create_alert_checker(90) with 80": {
        "code": "from exercise import create_alert_checker; check = create_alert_checker(90); print(check(80))",
        "expected": "False"
    },
    "Task 4 - create_alert_checker(75) with 80": {
        "code": "from exercise import create_alert_checker; check = create_alert_checker(75); print(check(80))",
        "expected": "True"
    },
    "Task 5 - safe_config_update changes value": {
        "code": "from exercise import safe_config_update; print(safe_config_update({'port': 8080, 'host': 'localhost'}, 'port', 9090))",
        "expected": "{'port': 9090, 'host': 'localhost'}"
    },
    "Task 5 - safe_config_update doesn't modify original": {
        "code": "from exercise import safe_config_update; orig = {'port': 8080}; safe_config_update(orig, 'port', 9090); print(orig)",
        "expected": "{'port': 8080}"
    },
    "Task 5 - safe_config_update adds new key": {
        "code": "from exercise import safe_config_update; print(safe_config_update({}, 'debug', True))",
        "expected": "{'debug': True}"
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
    print("  Week 4, Day 3: Scope & Variables - Checking Solutions")
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
        print("  PERFECT! You understand scope and variable management!")
    elif passed >= total * 0.7:
        print("  Good progress! Review the failing tests and try again.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 60)


if __name__ == "__main__":
    main()
