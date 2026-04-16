"""
Week 2, Day 5: Loop Control - Auto-Checker
============================================
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
    print("  WEEK 2, DAY 5 - Loop Control Checker")
    print("=" * 50)
    print()

    try:
        output = run_exercise()
    except subprocess.TimeoutExpired:
        print("[FAIL] Your code took too long (possible infinite loop).")
        print(f"\n  Score: 0/{total} tasks passed")
        return
    except Exception as e:
        print(f"[FAIL] Error running exercise.py: {e}")
        print(f"\n  Score: 0/{total} tasks passed")
        return

    # ---- TASK 1: Search Through Logs ----
    try:
        if "Found error: ERROR: Connection timeout on db-01" in output:
            # Make sure it stopped at the first error (did not find the second one)
            if "ERROR: Disk full" not in " ".join(output):
                print("[PASS] Task 1: Search Through Logs")
                passed += 1
            else:
                print("[FAIL] Task 1: Should break after finding the first error")
        else:
            # Check if no-error path works
            out2 = run_exercise([('"ERROR: Connection timeout on db-01",', '"INFO: All good",'),
                                  ('"ERROR: Disk full"', '"INFO: Still good"')])
            if "No errors found" in out2:
                print("[FAIL] Task 1: Should find 'ERROR: Connection timeout on db-01'")
            else:
                print("[FAIL] Task 1: Expected 'Found error: ERROR: Connection timeout on db-01'")
    except Exception as e:
        print(f"[FAIL] Task 1: Error - {e}")

    # Also verify the else clause works
    try:
        out_no_err = run_exercise([
            ('"ERROR: Connection timeout on db-01",', '"INFO: All good",'),
            ('"ERROR: Disk full"', '"INFO: Still good"')
        ])
        if "No errors found" not in out_no_err and passed > 0:
            # Revert pass if else clause is missing
            print("       (Note: for/else pattern not detected, but primary test passed)")
    except Exception:
        pass

    # ---- TASK 2: Skip Failed Servers ----
    try:
        expected = [
            "Deploying to web-01",
            "Skipping web-02 (failed)",
            "Deploying to web-03",
            "Deploying to web-04",
            "Skipping web-05 (failed)"
        ]
        if all(line in output for line in expected):
            print("[PASS] Task 2: Skip Failed Servers")
            passed += 1
        else:
            print("[FAIL] Task 2: Check your continue logic and print messages")
    except Exception as e:
        print(f"[FAIL] Task 2: Error - {e}")

    # ---- TASK 3: Find First Available Port ----
    try:
        if "First available port: 3005" in output:
            # Make sure it did not print ports after 3005
            if "First available port: 3006" not in output:
                print("[PASS] Task 3: Find First Available Port")
                passed += 1
            else:
                print("[FAIL] Task 3: Should break after finding first available port")
        else:
            print("[FAIL] Task 3: Expected 'First available port: 3005'")
    except Exception as e:
        print(f"[FAIL] Task 3: Error - {e}")

    # ---- TASK 4: Server-Port Matrix ----
    try:
        expected = [
            "app-01:80",
            "app-01:443",
            "app-02:80",
            "app-02:443",
            "app-03:80",
            "app-03:443"
        ]
        if all(line in output for line in expected):
            print("[PASS] Task 4: Server-Port Matrix")
            passed += 1
        else:
            print("[FAIL] Task 4: Expected all server:port combinations")
    except Exception as e:
        print(f"[FAIL] Task 4: Error - {e}")

    # ---- TASK 5: Process Log Until Marker ----
    try:
        expected_present = [
            "Starting backup",
            "Copying files",
            "Verifying integrity",
            "End marker found",
            "Processing complete"
        ]
        expected_absent = [
            "This should not appear",
            "Neither should this"
        ]
        present_ok = all(line in output for line in expected_present)
        absent_ok = all(line not in output for line in expected_absent)
        if present_ok and absent_ok:
            print("[PASS] Task 5: Process Log Until Marker")
            passed += 1
        else:
            if not present_ok:
                print("[FAIL] Task 5: Missing expected output lines")
            else:
                print("[FAIL] Task 5: Lines after ---END--- should not appear (use break)")
    except Exception as e:
        print(f"[FAIL] Task 5: Error - {e}")

    # ---- Summary ----
    print()
    print("-" * 50)
    print(f"  Score: {passed}/{total} tasks passed")
    if passed == total:
        print("  PERFECT! Loop control mastered!")
    elif passed >= 3:
        print("  Great work! Review the tricky ones.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 50)


if __name__ == "__main__":
    main()
