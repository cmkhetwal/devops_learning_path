"""
Week 2, Day 6: Practice Day - Auto-Checker
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

    print("=" * 55)
    print("  WEEK 2, DAY 6 - Practice Day Checker")
    print("=" * 55)
    print()

    try:
        output = run_exercise()
    except subprocess.TimeoutExpired:
        print("[FAIL] Your code took too long (possible infinite loop).")
        print(f"\n  Score: 0/{total} projects passed")
        return
    except Exception as e:
        print(f"[FAIL] Error running exercise.py: {e}")
        print(f"\n  Score: 0/{total} projects passed")
        return

    # ---- PROJECT 1: Number Guessing Game ----
    try:
        expected = [
            "Guess 1: Too low!",
            "Guess 2: Too high!",
            "Guess 3: Too low!",
            "Guess 4: Correct! You win!"
        ]
        if all(line in output for line in expected):
            # Should NOT have Guess 5 since we broke at 4
            if "Guess 5" not in " ".join(output):
                # Should NOT print "Game over" since they guessed correctly
                if "Game over" not in " ".join(output):
                    print("[PASS] Project 1: Number Guessing Game")
                    passed += 1
                else:
                    print("[FAIL] Project 1: Should not print 'Game over' when guess is correct")
            else:
                print("[FAIL] Project 1: Should break after correct guess (no Guess 5)")
        else:
            print("[FAIL] Project 1: Check your too low/too high/correct messages")
    except Exception as e:
        print(f"[FAIL] Project 1: Error - {e}")

    # ---- PROJECT 2: Server Health Monitor ----
    try:
        expected = [
            "web-01: HEALTHY",
            "web-02: WARNING",
            "db-01: CRITICAL",
            "cache-01: HEALTHY",
            "api-01: WARNING",
            "Summary: 2 healthy, 2 warning, 1 critical"
        ]
        if all(line in output for line in expected):
            print("[PASS] Project 2: Server Health Monitor")
            passed += 1
        else:
            missing = [line for line in expected if line not in output]
            print(f"[FAIL] Project 2: Missing output: {missing[0]}")
    except Exception as e:
        print(f"[FAIL] Project 2: Error - {e}")

    # ---- PROJECT 3: Simple Menu System ----
    try:
        expected = [
            "Status: All systems operational",
            "Servers: web-01, web-02, db-01",
            "Invalid choice",
            "Goodbye!"
        ]
        if all(line in output for line in expected):
            print("[PASS] Project 3: Simple Menu System")
            passed += 1
        else:
            missing = [line for line in expected if line not in output]
            print(f"[FAIL] Project 3: Missing output: {missing[0]}")
    except Exception as e:
        print(f"[FAIL] Project 3: Error - {e}")

    # ---- PROJECT 4: Password Validator ----
    try:
        expected = [
            "Length check: PASS",
            "Uppercase check: PASS",
            "Digit check: PASS",
            "Special char check: PASS",
            "Password is STRONG"
        ]
        if all(line in output for line in expected):
            # Also test with a weak password
            out2 = run_exercise([('password = "DevOps2024!"', 'password = "weak"')])
            if "Password is WEAK" in out2:
                print("[PASS] Project 4: Password Validator")
                passed += 1
            else:
                print("[FAIL] Project 4: 'weak' password should result in 'Password is WEAK'")
        else:
            missing = [line for line in expected if line not in output]
            print(f"[FAIL] Project 4: Missing output: {missing[0]}")
    except Exception as e:
        print(f"[FAIL] Project 4: Error - {e}")

    # ---- PROJECT 5: Port Scanner Simulator ----
    try:
        expected = [
            "web-01:80 OPEN",
            "web-01:443 OPEN",
            "web-01: Scan complete",
            "db-01:3306 OPEN",
            "db-01:5432 OPEN",
            "db-01: Scan complete",
            "api-01:443 OPEN",
            "api-01:8080 OPEN",
            "api-01: Scan complete"
        ]
        # Should NOT print closed ports
        closed_markers = ["web-01:3306", "web-01:5432", "web-01:8080",
                          "db-01:80", "db-01:443", "db-01:8080",
                          "api-01:80", "api-01:3306", "api-01:5432"]

        if all(line in output for line in expected):
            has_closed = any(marker in " ".join(output) for marker in closed_markers)
            if not has_closed:
                print("[PASS] Project 5: Port Scanner Simulator")
                passed += 1
            else:
                print("[FAIL] Project 5: Should not print closed ports (use continue)")
        else:
            missing = [line for line in expected if line not in output]
            print(f"[FAIL] Project 5: Missing output: {missing[0]}")
    except Exception as e:
        print(f"[FAIL] Project 5: Error - {e}")

    # ---- Summary ----
    print()
    print("-" * 55)
    print(f"  Score: {passed}/{total} projects passed")
    if passed == total:
        print("  AMAZING! You completed all 5 mini-projects!")
        print("  You are ready for the Week 2 quiz tomorrow!")
    elif passed >= 3:
        print("  Great effort! Try to fix the remaining ones.")
    else:
        print("  Keep working at it! Review earlier lessons for help.")
    print("-" * 55)


if __name__ == "__main__":
    main()
