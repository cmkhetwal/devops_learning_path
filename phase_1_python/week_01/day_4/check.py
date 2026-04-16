#!/usr/bin/env python3
"""Week 1, Day 4 - Auto-checker"""
import subprocess
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
exercise_path = os.path.join(script_dir, "exercise.py")


def run_exercise():
    try:
        result = subprocess.run(
            [sys.executable, exercise_path],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "ERROR: Script took too long to run"
    except Exception as e:
        return "", str(e)


def check():
    print("\n  Checking your exercise...\n")

    stdout, stderr = run_exercise()

    if stderr:
        print(f"  ERROR in your code:\n  {stderr}")
        print(f"\n  Fix the error and try again!")
        return

    output = stdout
    lines = output.strip().split("\n") if output.strip() else []
    passed = 0
    total = 5

    # --- Task 1: Server capacity ---
    task1_checks = [
        "Total capacity: 24",
        "Containers needed: 50",
        "Full servers needed: 6",
        "Leftover containers: 2",
    ]
    if all(c in output for c in task1_checks):
        print("  Task 1: PASS - Server capacity calculated correctly")
        passed += 1
    else:
        missing = [c for c in task1_checks if c not in output]
        print(f"  Task 1: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Task 2: Disk usage ---
    task2_checks = [
        "Disk total: 500 GB",
        "Disk used: 347 GB",
        "Disk free: 153 GB",
        "Usage: 69.4%",
    ]
    if all(c in output for c in task2_checks):
        print("  Task 2: PASS - Disk usage calculated correctly")
        passed += 1
    else:
        missing = [c for c in task2_checks if c not in output]
        print(f"  Task 2: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Task 3: Network bandwidth ---
    task3_checks = [
        "Speed: 1000 Mbps",
        "Speed: 125.0 MBps",
        "Speed: 0.122 GBps",
    ]
    if all(c in output for c in task3_checks):
        print("  Task 3: PASS - Network bandwidth converted correctly")
        passed += 1
    else:
        missing = [c for c in task3_checks if c not in output]
        print(f"  Task 3: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Task 4: Uptime calculation ---
    task4_checks = [
        "Total minutes: 43200",
        "Uptime minutes: 43185",
        "Downtime minutes: 15",
        "Uptime: 99.965%",
    ]
    if all(c in output for c in task4_checks):
        print("  Task 4: PASS - Uptime calculated correctly")
        passed += 1
    else:
        missing = [c for c in task4_checks if c not in output]
        print(f"  Task 4: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Task 5: Comparisons ---
    task5_checks = [
        "CPU critical (>90): False",
        "Memory critical (>90): True",
        "Disk warning (>80): False",
        "Errors OK (<5): True",
        "All healthy: False",
    ]
    if all(c in output for c in task5_checks):
        print("  Task 5: PASS - All comparisons correct")
        passed += 1
    else:
        missing = [c for c in task5_checks if c not in output]
        print(f"  Task 5: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Results ---
    print(f"\n  {'─' * 40}")
    print(f"  Score: {passed}/{total} tasks passed")

    if passed == total:
        print(f"  PERFECT! All tasks completed!")
        print(f"  You're ready to move on to Day 5!")
        print(f"\n  Mark your progress: python3 ../../tracker.py")
    elif passed >= 3:
        print(f"  Good job! Fix the remaining tasks and try again.")
    else:
        print(f"  Keep trying! Re-read the lesson.md for help.")


if __name__ == "__main__":
    check()
