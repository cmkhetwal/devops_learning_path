"""
Week 2, Day 3: While Loops - Auto-Checker
==========================================
Run this file to check your exercise.py answers!
Usage: python check.py
"""

import subprocess
import sys
import os

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

def run_exercise(replacements=None):
    """Run exercise.py with optional variable replacements and return stdout lines."""
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


def main():
    passed = 0
    total = 5

    print("=" * 50)
    print("  WEEK 2, DAY 3 - While Loops Checker")
    print("=" * 50)
    print()

    try:
        output = run_exercise()
    except subprocess.TimeoutExpired:
        print("[FAIL] Your code took too long to run (possible infinite loop).")
        print("       Check that your while loops have proper exit conditions.")
        print(f"\n  Score: 0/{total} tasks passed")
        return
    except Exception as e:
        print(f"[FAIL] Error running exercise.py: {e}")
        print(f"\n  Score: 0/{total} tasks passed")
        return

    # ---- TASK 1: Retry Connection ----
    try:
        expected = [
            "Attempt 1: Connecting...",
            "Attempt 2: Connecting...",
            "Attempt 3: Connecting...",
            "Attempt 4: Connecting...",
            "Attempt 5: Connecting...",
            "Finished: 5 attempts made"
        ]
        if all(line in output for line in expected):
            print("[PASS] Task 1: Retry Connection")
            passed += 1
        else:
            print("[FAIL] Task 1: Expected 5 attempts and a finished message")
    except Exception as e:
        print(f"[FAIL] Task 1: Error - {e}")

    # ---- TASK 2: Countdown Timer ----
    try:
        has_countdown = True
        for i in range(10, 0, -1):
            if str(i) not in output:
                has_countdown = False
                break
        if has_countdown and "System shutdown complete" in output:
            print("[PASS] Task 2: Countdown Timer")
            passed += 1
        else:
            print("[FAIL] Task 2: Expected countdown from 10 to 1, then 'System shutdown complete'")
    except Exception as e:
        print(f"[FAIL] Task 2: Error - {e}")

    # ---- TASK 3: Monitoring Loop with Break ----
    try:
        expected = [
            "Check 1: Server OK",
            "Check 2: Server OK",
            "Check 3: Server OK",
            "Check 4: Server OK",
            "Monitoring stopped after 4 checks"
        ]
        if all(line in output for line in expected):
            # Make sure there is no Check 5
            if "Check 5: Server OK" not in output:
                print("[PASS] Task 3: Monitoring Loop with Break")
                passed += 1
            else:
                print("[FAIL] Task 3: Should stop at Check 4 (use break)")
        else:
            print("[FAIL] Task 3: Expected 4 checks and a stop message")
    except Exception as e:
        print(f"[FAIL] Task 3: Error - {e}")

    # ---- TASK 4: Sum Until Threshold ----
    try:
        expected_lines = [
            "Transferred so far: 15 GB",
            "Transferred so far: 30 GB",
            "Transferred so far: 45 GB",
            "Transferred so far: 60 GB",
            "Transferred so far: 75 GB",
            "Transferred so far: 90 GB",
            "Transferred so far: 105 GB",
            "Limit reached: 105 GB total"
        ]
        if all(line in output for line in expected_lines):
            print("[PASS] Task 4: Sum Until Threshold")
            passed += 1
        else:
            print("[FAIL] Task 4: Expected transfers up to 105 GB and a limit message")
    except Exception as e:
        print(f"[FAIL] Task 4: Error - {e}")

    # ---- TASK 5: Password Attempt Limiter ----
    try:
        expected = [
            "Attempt 1: Incorrect password",
            "Attempt 2: Incorrect password",
            "Attempt 3: Access granted"
        ]
        if all(line in output for line in expected):
            if "Attempt 4" not in output:
                print("[PASS] Task 5: Password Attempt Limiter")
                passed += 1
            else:
                print("[FAIL] Task 5: Should stop after access is granted (use break)")
        else:
            print("[FAIL] Task 5: Expected 2 incorrect attempts then 'Access granted'")
    except Exception as e:
        print(f"[FAIL] Task 5: Error - {e}")

    # ---- Summary ----
    print()
    print("-" * 50)
    print(f"  Score: {passed}/{total} tasks passed")
    if passed == total:
        print("  PERFECT! While loops mastered!")
    elif passed >= 3:
        print("  Good progress! Review the ones you missed.")
    else:
        print("  Keep trying! Re-read lesson.md for help.")
    print("-" * 50)


if __name__ == "__main__":
    main()
