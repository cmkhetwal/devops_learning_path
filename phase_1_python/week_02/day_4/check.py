"""
Week 2, Day 4: For Loops - Auto-Checker
=========================================
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
    print("  WEEK 2, DAY 4 - For Loops Checker")
    print("=" * 50)
    print()

    try:
        output = run_exercise()
    except subprocess.TimeoutExpired:
        print("[FAIL] Your code took too long to run (possible infinite loop).")
        print(f"\n  Score: 0/{total} tasks passed")
        return
    except Exception as e:
        print(f"[FAIL] Error running exercise.py: {e}")
        print(f"\n  Score: 0/{total} tasks passed")
        return

    # ---- TASK 1: Ping All Servers ----
    try:
        expected = [
            "Pinging web-01...",
            "Pinging web-02...",
            "Pinging db-01...",
            "Pinging cache-01..."
        ]
        if all(line in output for line in expected):
            print("[PASS] Task 1: Ping All Servers")
            passed += 1
        else:
            print("[FAIL] Task 1: Expected ping messages for all 4 servers")
    except Exception as e:
        print(f"[FAIL] Task 1: Error - {e}")

    # ---- TASK 2: Print Port Range ----
    try:
        expected_ports = ["8080", "8081", "8082", "8083", "8084"]
        if all(p in output for p in expected_ports):
            print("[PASS] Task 2: Print Port Range")
            passed += 1
        else:
            print("[FAIL] Task 2: Expected ports 8080 through 8084")
    except Exception as e:
        print(f"[FAIL] Task 2: Error - {e}")

    # ---- TASK 3: Count Production Servers ----
    try:
        if "Production servers: 3" in output:
            print("[PASS] Task 3: Count Production Servers")
            passed += 1
        else:
            print("[FAIL] Task 3: Expected 'Production servers: 3'")
    except Exception as e:
        print(f"[FAIL] Task 3: Error - {e}")

    # ---- TASK 4: Numbered Server List ----
    try:
        expected = [
            "1. app-server",
            "2. db-server",
            "3. cache-server",
            "4. log-server"
        ]
        if all(line in output for line in expected):
            print("[PASS] Task 4: Numbered Server List")
            passed += 1
        else:
            print("[FAIL] Task 4: Expected numbered list (1. app-server, 2. db-server, ...)")
    except Exception as e:
        print(f"[FAIL] Task 4: Error - {e}")

    # ---- TASK 5: Generate IP Addresses ----
    try:
        expected_ips = [
            "192.168.1.1",
            "192.168.1.2",
            "192.168.1.3",
            "192.168.1.4",
            "192.168.1.5"
        ]
        if all(ip in output for ip in expected_ips):
            print("[PASS] Task 5: Generate IP Addresses")
            passed += 1
        else:
            print("[FAIL] Task 5: Expected IPs from 192.168.1.1 to 192.168.1.5")
    except Exception as e:
        print(f"[FAIL] Task 5: Error - {e}")

    # ---- Summary ----
    print()
    print("-" * 50)
    print(f"  Score: {passed}/{total} tasks passed")
    if passed == total:
        print("  PERFECT! For loops mastered!")
    elif passed >= 3:
        print("  Good progress! Review the ones you missed.")
    else:
        print("  Keep trying! Re-read lesson.md for help.")
    print("-" * 50)


if __name__ == "__main__":
    main()
