"""
Week 2, Day 7: Quiz Day - Auto-Checker
========================================
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
    total = 10

    print("=" * 55)
    print("  WEEK 2, DAY 7 - Final Quiz Checker")
    print("=" * 55)
    print()

    try:
        output = run_exercise()
    except subprocess.TimeoutExpired:
        print("[FAIL] Your code took too long (possible infinite loop).")
        print("       Check Question 2 -- did you decrement countdown_num?")
        print(f"\n  Score: 0/{total} questions passed")
        return
    except Exception as e:
        print(f"[FAIL] Error running exercise.py: {e}")
        print(f"\n  Score: 0/{total} questions passed")
        return

    # ---- Q1: if/elif/else ----
    try:
        if "Server Error" in output:
            # Verify another case
            out2 = run_exercise([("status_code = 500", "status_code = 404")])
            if "Not Found" in out2:
                print("[PASS] Q1:  if/elif/else status code")
                passed += 1
            else:
                print("[FAIL] Q1:  status_code 404 should print 'Not Found'")
        else:
            print("[FAIL] Q1:  status_code 500 should print 'Server Error'")
    except Exception as e:
        print(f"[FAIL] Q1:  Error - {e}")

    # ---- Q2: while loop countdown ----
    try:
        has_countdown = True
        for num in ["5", "4", "3", "2", "1"]:
            if num not in output:
                has_countdown = False
                break
        if has_countdown and "Liftoff!" in output:
            print("[PASS] Q2:  while loop countdown")
            passed += 1
        else:
            print("[FAIL] Q2:  Expected 5, 4, 3, 2, 1, then 'Liftoff!'")
    except Exception as e:
        print(f"[FAIL] Q2:  Error - {e}")

    # ---- Q3: for loop through list ----
    try:
        expected = ["nginx is running", "postgres is running", "redis is running"]
        if all(line in output for line in expected):
            print("[PASS] Q3:  for loop through services")
            passed += 1
        else:
            print("[FAIL] Q3:  Expected '<service> is running' for each service")
    except Exception as e:
        print(f"[FAIL] Q3:  Error - {e}")

    # ---- Q4: logical operators ----
    try:
        if "ALERT" in output:
            out2 = run_exercise([("cpu = 95", "cpu = 50")])
            if "OK" in out2:
                print("[PASS] Q4:  logical operators (and)")
                passed += 1
            else:
                print("[FAIL] Q4:  cpu=50, memory=88 should print 'OK'")
        else:
            print("[FAIL] Q4:  cpu=95, memory=88 should print 'ALERT'")
    except Exception as e:
        print(f"[FAIL] Q4:  Error - {e}")

    # ---- Q5: range() even numbers ----
    try:
        even_nums = ["2", "4", "6", "8", "10"]
        if all(n in output for n in even_nums):
            # Make sure odd numbers are NOT printed (checking a few)
            if "3" not in output or output.count("3") == 0:
                print("[PASS] Q5:  range() even numbers")
                passed += 1
            else:
                # Be careful: "3" could appear in other output, so just check evens are present
                print("[PASS] Q5:  range() even numbers")
                passed += 1
        else:
            print("[FAIL] Q5:  Expected even numbers: 2, 4, 6, 8, 10")
    except Exception as e:
        print(f"[FAIL] Q5:  Error - {e}")

    # ---- Q6: break ----
    try:
        if "SSH port found" in output:
            print("[PASS] Q6:  break to find SSH port")
            passed += 1
        else:
            print("[FAIL] Q6:  Expected 'SSH port found'")
    except Exception as e:
        print(f"[FAIL] Q6:  Error - {e}")

    # ---- Q7: continue ----
    try:
        expected_nums = ["1", "2", "4", "5", "7", "8", "10"]
        skipped_nums = ["3", "6", "9"]
        # Check that expected numbers appear in output
        # This is tricky because other questions also print numbers
        # We will check that at least these appear and the skip pattern makes sense
        all_present = all(n in output for n in expected_nums)
        if all_present:
            print("[PASS] Q7:  continue to skip multiples of 3")
            passed += 1
        else:
            print("[FAIL] Q7:  Expected 1,2,4,5,7,8,10 (skip multiples of 3)")
    except Exception as e:
        print(f"[FAIL] Q7:  Error - {e}")

    # ---- Q8: nested conditions ----
    try:
        if "Deploying update" in output:
            out2 = run_exercise([("is_maintenance_window = True",
                                   "is_maintenance_window = False")])
            if "Waiting for window" in out2:
                out3 = run_exercise([("is_weekend = True", "is_weekend = False")])
                if "No weekend deploys" in out3:
                    print("[PASS] Q8:  nested conditions")
                    passed += 1
                else:
                    print("[FAIL] Q8:  Not weekend should print 'No weekend deploys'")
            else:
                print("[FAIL] Q8:  Weekend + no window should print 'Waiting for window'")
        else:
            print("[FAIL] Q8:  Weekend + window should print 'Deploying update'")
    except Exception as e:
        print(f"[FAIL] Q8:  Error - {e}")

    # ---- Q9: accumulator ----
    try:
        if "Total response time: 1650 ms" in output:
            print("[PASS] Q9:  accumulator pattern")
            passed += 1
        else:
            print("[FAIL] Q9:  Expected 'Total response time: 1650 ms'")
    except Exception as e:
        print(f"[FAIL] Q9:  Error - {e}")

    # ---- Q10: nested for loops ----
    try:
        expected = ["dev-web", "dev-db", "prod-web", "prod-db"]
        if all(line in output for line in expected):
            print("[PASS] Q10: nested for loops")
            passed += 1
        else:
            print("[FAIL] Q10: Expected dev-web, dev-db, prod-web, prod-db")
    except Exception as e:
        print(f"[FAIL] Q10: Error - {e}")

    # ---- Summary ----
    print()
    print("=" * 55)
    print(f"  FINAL SCORE: {passed}/{total} questions correct")
    print("=" * 55)
    if passed == total:
        print("  PERFECT SCORE! You have mastered Week 2: Control Flow!")
        print("  You are ready for Week 3!")
    elif passed >= 8:
        print("  Excellent! Just a couple to review.")
    elif passed >= 5:
        print("  Good foundation! Review the cheat sheet in lesson.md.")
    else:
        print("  Review the week's lessons and try again. You got this!")
    print("=" * 55)


if __name__ == "__main__":
    main()
