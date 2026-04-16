"""
Week 2, Day 1: If/Else Statements - Auto-Checker
==================================================
Run this file to check your exercise.py answers!
Usage: python check.py
"""

import subprocess
import sys
import os

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

def run_exercise(replacements=None):
    """Run exercise.py with optional variable replacements and return stdout."""
    with open(SCRIPT, "r") as f:
        code = f.read()
    if replacements:
        for old, new in replacements:
            code = code.replace(old, new)
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout.strip().split("\n")


def check_task(task_num, description, test_cases):
    """Run multiple test cases for a task. Returns True if all pass."""
    all_passed = True
    for replacements, expected_output, hint in test_cases:
        try:
            output = run_exercise(replacements)
            # Find the relevant output line(s) for this task
            if expected_output in output:
                pass  # good
            else:
                all_passed = False
        except Exception as e:
            all_passed = False
    return all_passed


def main():
    passed = 0
    total = 5

    print("=" * 50)
    print("  WEEK 2, DAY 1 - If/Else Statements Checker")
    print("=" * 50)
    print()

    # ---- TASK 1: HTTP Status Code Checker ----
    try:
        # Test with 404 (default)
        output = run_exercise()
        if "Not Found" in output:
            # Test with 200
            out2 = run_exercise([("status_code = 404", "status_code = 200")])
            if "OK" in out2:
                # Test with 500
                out3 = run_exercise([("status_code = 404", "status_code = 500")])
                if "Internal Server Error" in out3:
                    # Test with 999
                    out4 = run_exercise([("status_code = 404", "status_code = 999")])
                    if "Unknown Status" in out4:
                        print("[PASS] Task 1: HTTP Status Code Checker")
                        passed += 1
                    else:
                        print("[FAIL] Task 1: Unknown code should print 'Unknown Status'")
                else:
                    print("[FAIL] Task 1: Status 500 should print 'Internal Server Error'")
            else:
                print("[FAIL] Task 1: Status 200 should print 'OK'")
        else:
            print("[FAIL] Task 1: Status 404 should print 'Not Found'")
    except Exception as e:
        print(f"[FAIL] Task 1: Error - {e}")

    # ---- TASK 2: Port Range Validator ----
    try:
        output = run_exercise()
        if "Valid port" in output:
            out2 = run_exercise([("port = 8080", "port = 0")])
            if "Invalid port" in out2:
                out3 = run_exercise([("port = 8080", "port = 70000")])
                if "Invalid port" in out3:
                    print("[PASS] Task 2: Port Range Validator")
                    passed += 1
                else:
                    print("[FAIL] Task 2: Port 70000 should print 'Invalid port'")
            else:
                print("[FAIL] Task 2: Port 0 should print 'Invalid port'")
        else:
            print("[FAIL] Task 2: Port 8080 should print 'Valid port'")
    except Exception as e:
        print(f"[FAIL] Task 2: Error - {e}")

    # ---- TASK 3: Server Health Check ----
    try:
        output = run_exercise()
        if "SLOW" in output:
            out2 = run_exercise([("response_time = 350", "response_time = 100")])
            if "HEALTHY" in out2:
                out3 = run_exercise([("response_time = 350", "response_time = 600")])
                if "CRITICAL" in out3:
                    print("[PASS] Task 3: Server Health Check")
                    passed += 1
                else:
                    print("[FAIL] Task 3: response_time 600 should print 'CRITICAL'")
            else:
                print("[FAIL] Task 3: response_time 100 should print 'HEALTHY'")
        else:
            print("[FAIL] Task 3: response_time 350 should print 'SLOW'")
    except Exception as e:
        print(f"[FAIL] Task 3: Error - {e}")

    # ---- TASK 4: Environment Config ----
    try:
        output = run_exercise()
        if "True" in output:
            out2 = run_exercise([('env = "development"', 'env = "production"')])
            if "False" in out2:
                out3 = run_exercise([('env = "development"', 'env = "staging"')])
                if "False" in out3:
                    print("[PASS] Task 4: Environment Config")
                    passed += 1
                else:
                    print("[FAIL] Task 4: env 'staging' should set debug to False")
            else:
                print("[FAIL] Task 4: env 'production' should set debug to False")
        else:
            print("[FAIL] Task 4: env 'development' should print True")
    except Exception as e:
        print(f"[FAIL] Task 4: Error - {e}")

    # ---- TASK 5: Disk Space Alert ----
    try:
        output = run_exercise()
        if "CRITICAL" in output:
            out2 = run_exercise([("disk_usage_percent = 87", "disk_usage_percent = 40")])
            if "OK" in out2:
                out3 = run_exercise([("disk_usage_percent = 87", "disk_usage_percent = 70")])
                if "WARNING" in out3:
                    out4 = run_exercise([("disk_usage_percent = 87", "disk_usage_percent = 98")])
                    if "EMERGENCY" in out4:
                        print("[PASS] Task 5: Disk Space Alert")
                        passed += 1
                    else:
                        print("[FAIL] Task 5: 98% should print 'EMERGENCY'")
                else:
                    print("[FAIL] Task 5: 70% should print 'WARNING'")
            else:
                print("[FAIL] Task 5: 40% should print 'OK'")
        else:
            print("[FAIL] Task 5: 87% should print 'CRITICAL'")
    except Exception as e:
        print(f"[FAIL] Task 5: Error - {e}")

    # ---- Summary ----
    print()
    print("-" * 50)
    print(f"  Score: {passed}/{total} tasks passed")
    if passed == total:
        print("  PERFECT SCORE! You nailed if/else statements!")
    elif passed >= 3:
        print("  Good progress! Review the ones you missed.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 50)


if __name__ == "__main__":
    main()
