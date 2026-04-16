#!/usr/bin/env python3
"""Week 1, Day 2 - Auto-checker"""
import subprocess, sys, os

script_dir = os.path.dirname(os.path.abspath(__file__))
exercise_path = os.path.join(script_dir, "exercise.py")


def check():
    print("\n  Checking your exercise...\n")
    try:
        result = subprocess.run(
            [sys.executable, exercise_path],
            capture_output=True, text=True, timeout=10
        )
    except subprocess.TimeoutExpired:
        print("  ERROR: Script timed out"); return

    if result.stderr:
        print(f"  ERROR in your code:\n  {result.stderr}")
        return

    output = result.stdout
    lines = output.strip().split("\n") if output.strip() else []
    passed = 0
    total = 5

    # Task 1
    if "app-server-01" in output and "8" in output and "32" in output and "True" in output:
        print("  Task 1: PASS"); passed += 1
    else:
        print("  Task 1: FAIL - Print all 4 variables (server_name, cpu_cores, memory_gb, is_active)")

    # Task 2
    if "3001" in output:
        print("  Task 2: PASS"); passed += 1
    else:
        print("  Task 2: FAIL - Expected 3001 (convert string '3000' to int, then add 1)")

    # Task 3
    type_checks = ["<class 'str'>", "<class 'int'>", "<class 'float'>", "<class 'bool'>"]
    if all(t in output for t in type_checks):
        print("  Task 3: PASS"); passed += 1
    else:
        print("  Task 3: FAIL - Use type() to print each variable's type")

    # Task 4
    if "server_count" not in result.stderr and "Servers:" in output and "5" in output:
        print("  Task 4: PASS"); passed += 1
    else:
        print("  Task 4: FAIL - Fix: no spaces in names, strings need quotes, True is capitalized, use str()")

    # Task 5
    if "=== Server Report ===" in output and "prod-db-01" in output and "16.0" in output:
        print("  Task 5: PASS"); passed += 1
    else:
        print("  Task 5: FAIL - Print the server report matching the exact format")

    print(f"\n  Score: {passed}/{total}")
    if passed == total:
        print("  PERFECT! Ready for Day 3!")


if __name__ == "__main__":
    check()
