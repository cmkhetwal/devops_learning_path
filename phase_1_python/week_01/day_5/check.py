#!/usr/bin/env python3
"""Week 1, Day 5 - Auto-checker"""
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

    # --- Task 1: Parse a log line ---
    task1_checks = [
        "Date: 2024-03-15",
        "Time: 08:45:30",
        "Level: ERROR",
        "Message: Disk usage critical on server-12",
    ]
    if all(c in output for c in task1_checks):
        print("  Task 1: PASS - Log line parsed correctly")
        passed += 1
    else:
        missing = [c for c in task1_checks if c not in output]
        print(f"  Task 1: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Task 2: Formatted table ---
    task2_checks = [
        "=" * 40,
        "-" * 40,
        "Server",
        "Status",
        "CPU",
        "web-01",
        "web-02",
        "db-01",
        "running",
        "stopped",
        "45.2%",
        "0.0%",
        "78.9%",
    ]
    if all(c in output for c in task2_checks):
        print("  Task 2: PASS - Server table formatted correctly")
        passed += 1
    else:
        missing = [c for c in task2_checks if c not in output]
        print(f"  Task 2: FAIL - Missing or wrong:")
        for m in missing[:5]:
            print(f"           Expected to contain: {m}")
        if len(missing) > 5:
            print(f"           ...and {len(missing) - 5} more")

    # --- Task 3: Extract hostnames ---
    task3_checks = [
        "Host 1: api.example.com",
        "Host 2: monitoring.internal.net",
    ]
    if all(c in output for c in task3_checks):
        print("  Task 3: PASS - Hostnames extracted correctly")
        passed += 1
    else:
        missing = [c for c in task3_checks if c not in output]
        print(f"  Task 3: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")
        if "api.example.com:8443" in output:
            print("           Hint: You still have the port number. Split on ':' to remove it.")

    # --- Task 4: Config analysis ---
    task4_checks = [
        "Total lines: 7",
        "Contains 'production': True",
        "Contains 'staging': False",
        "Lines with '=': 7",
    ]
    has_upper = False
    for line in lines:
        if "HOST=WEB-SERVER-01" in line or "PORT=8080" in line:
            has_upper = True
            break

    if all(c in output for c in task4_checks) and has_upper:
        print("  Task 4: PASS - Config analyzed correctly")
        passed += 1
    else:
        missing = [c for c in task4_checks if c not in output]
        if not has_upper:
            missing.append("Uppercase config (should contain HOST=WEB-SERVER-01)")
        print(f"  Task 4: FAIL - Missing or wrong:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Task 5: Log line processor ---
    task5_checks = [
        "Log 1: WARNING: HIGH MEMORY USAGE ON PRODUCTION-WEB-03",
        "Log 1 is error: False",
        "Log 2: ERROR: CONNECTION TIMEOUT TO DB-REPLICA-02",
        "Log 2 is error: True",
        "Log 3: INFO: DEPLOYMENT SUCCESSFUL FOR APP-V2.1.0",
        "Log 3 is error: False",
    ]
    if all(c in output for c in task5_checks):
        print("  Task 5: PASS - Log lines processed correctly")
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
        print(f"  You've finished Week 1! Amazing progress!")
        print(f"\n  Mark your progress: python3 ../../tracker.py")
    elif passed >= 3:
        print(f"  Good job! Fix the remaining tasks and try again.")
    else:
        print(f"  Keep trying! Re-read the lesson.md for help.")


if __name__ == "__main__":
    check()
