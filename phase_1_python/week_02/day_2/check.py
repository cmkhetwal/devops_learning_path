"""
Week 2, Day 2: Nested Conditions & Logical Operators - Auto-Checker
====================================================================
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
    print("  WEEK 2, DAY 2 - Nested Conditions & Logic Checker")
    print("=" * 55)
    print()

    # ---- TASK 1: Dual Resource Alert ----
    try:
        out = run_exercise()
        if "CRITICAL: Both resources maxed" in out:
            out2 = run_exercise([("cpu_usage = 95", "cpu_usage = 95"),
                                  ("mem_usage = 92", "mem_usage = 50")])
            if "WARNING: High CPU" in out2:
                out3 = run_exercise([("cpu_usage = 95", "cpu_usage = 50"),
                                      ("mem_usage = 92", "mem_usage = 95")])
                if "WARNING: High Memory" in out3:
                    out4 = run_exercise([("cpu_usage = 95", "cpu_usage = 50"),
                                          ("mem_usage = 92", "mem_usage = 50")])
                    if "OK" in out4:
                        print("[PASS] Task 1: Dual Resource Alert")
                        passed += 1
                    else:
                        print("[FAIL] Task 1: Both below 90 should print 'OK'")
                else:
                    print("[FAIL] Task 1: Only high memory should print 'WARNING: High Memory'")
            else:
                print("[FAIL] Task 1: Only high CPU should print 'WARNING: High CPU'")
        else:
            print("[FAIL] Task 1: Both > 90 should print 'CRITICAL: Both resources maxed'")
    except Exception as e:
        print(f"[FAIL] Task 1: Error - {e}")

    # ---- TASK 2: Access Control ----
    try:
        out = run_exercise()
        if "Full access" in out:
            out2 = run_exercise([("is_authenticated = True", "is_authenticated = False")])
            if "Login required" in out2:
                out3 = run_exercise([('role = "admin"', 'role = "viewer"')])
                if "Read-only access" in out3:
                    out4 = run_exercise([('role = "admin"', 'role = "guest"')])
                    if "Access denied" in out4:
                        print("[PASS] Task 2: Access Control")
                        passed += 1
                    else:
                        print("[FAIL] Task 2: role 'guest' should print 'Access denied'")
                else:
                    print("[FAIL] Task 2: authenticated viewer should print 'Read-only access'")
            else:
                print("[FAIL] Task 2: unauthenticated admin should print 'Login required'")
        else:
            print("[FAIL] Task 2: authenticated admin should print 'Full access'")
    except Exception as e:
        print(f"[FAIL] Task 2: Error - {e}")

    # ---- TASK 3: Deploy Gate Check ----
    try:
        out = run_exercise()
        if "Deploy approved" in out:
            out2 = run_exercise([("is_deploy_freeze = False", "is_deploy_freeze = True")])
            if "Deploy blocked" in out2:
                out3 = run_exercise([("tests_passing = True", "tests_passing = False")])
                if "Deploy blocked" in out3:
                    print("[PASS] Task 3: Deploy Gate Check")
                    passed += 1
                else:
                    print("[FAIL] Task 3: Failing tests should print 'Deploy blocked'")
            else:
                print("[FAIL] Task 3: Deploy freeze should print 'Deploy blocked'")
        else:
            print("[FAIL] Task 3: tests passing + no freeze should print 'Deploy approved'")
    except Exception as e:
        print(f"[FAIL] Task 3: Error - {e}")

    # ---- TASK 4: Server Tier Classification ----
    try:
        out = run_exercise()
        if "Tier 2: Staging" in out:
            out2 = run_exercise([("cpu_cores = 8", "cpu_cores = 32"),
                                  ("ram_gb = 32", "ram_gb = 128")])
            if "Tier 1: Production" in out2:
                out3 = run_exercise([("cpu_cores = 8", "cpu_cores = 4"),
                                      ("ram_gb = 32", "ram_gb = 16")])
                if "Tier 3: Development" in out3:
                    out4 = run_exercise([("cpu_cores = 8", "cpu_cores = 2"),
                                          ("ram_gb = 32", "ram_gb = 8")])
                    if "Tier 4: Testing" in out4:
                        print("[PASS] Task 4: Server Tier Classification")
                        passed += 1
                    else:
                        print("[FAIL] Task 4: 2 cores, 8GB should be 'Tier 4: Testing'")
                else:
                    print("[FAIL] Task 4: 4 cores, 16GB should be 'Tier 3: Development'")
            else:
                print("[FAIL] Task 4: 32 cores, 128GB should be 'Tier 1: Production'")
        else:
            print("[FAIL] Task 4: 8 cores, 32GB should be 'Tier 2: Staging'")
    except Exception as e:
        print(f"[FAIL] Task 4: Error - {e}")

    # ---- TASK 5: Nested Incident Response ----
    try:
        out = run_exercise()
        if "Critical production incident: paging on-call" in out:
            out2 = run_exercise([("is_acknowledged = False", "is_acknowledged = True")])
            if "Critical production incident: team notified" in out2:
                out3 = run_exercise([("is_production = True", "is_production = False")])
                if "Critical non-production incident: logged" in out3:
                    out4 = run_exercise([("is_critical = True", "is_critical = False")])
                    if "Minor incident: monitoring" in out4:
                        print("[PASS] Task 5: Nested Incident Response")
                        passed += 1
                    else:
                        print("[FAIL] Task 5: Non-critical should print 'Minor incident: monitoring'")
                else:
                    print("[FAIL] Task 5: Critical + non-prod should print 'Critical non-production incident: logged'")
            else:
                print("[FAIL] Task 5: Acknowledged should print 'Critical production incident: team notified'")
        else:
            print("[FAIL] Task 5: Default should print 'Critical production incident: paging on-call'")
    except Exception as e:
        print(f"[FAIL] Task 5: Error - {e}")

    # ---- Summary ----
    print()
    print("-" * 55)
    print(f"  Score: {passed}/{total} tasks passed")
    if passed == total:
        print("  PERFECT! You mastered logical operators and nesting!")
    elif passed >= 3:
        print("  Good work! Review the failed tasks and try again.")
    else:
        print("  Keep at it! Re-read lesson.md for help.")
    print("-" * 55)


if __name__ == "__main__":
    main()
