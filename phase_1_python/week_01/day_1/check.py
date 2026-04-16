#!/usr/bin/env python3
"""
Week 1, Day 1 - Auto-checker
Run: python3 check.py
"""

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

    lines = stdout.strip().split("\n") if stdout.strip() else []
    passed = 0
    total = 5

    # Task 1: Hello, World!
    if any("Hello, World!" in line for line in lines):
        print("  Task 1: PASS - Hello, World! printed correctly")
        passed += 1
    else:
        print("  Task 1: FAIL - Expected 'Hello, World!' (check capitalization and comma)")

    # Task 2: My name is ...
    if any("My name is" in line or "my name is" in line.lower() for line in lines):
        print("  Task 2: PASS - Name printed correctly")
        passed += 1
    else:
        print('  Task 2: FAIL - Expected something like "My name is <your name>"')

    # Task 3: Three server names
    servers = ["web-server-01", "db-server-01", "cache-server-01"]
    if all(any(s in line for line in lines) for s in servers):
        print("  Task 3: PASS - All server names printed")
        passed += 1
    else:
        print("  Task 3: FAIL - Expected web-server-01, db-server-01, cache-server-01 on separate lines")

    # Task 4: Deployment messages
    deploy_msgs = ["[DEPLOY] Starting deployment...", "[DEPLOY] Version: 2.1.0", "[DEPLOY] Status: SUCCESS"]
    if all(any(msg in line for line in lines) for msg in deploy_msgs):
        print("  Task 4: PASS - Deployment messages correct")
        passed += 1
    else:
        print("  Task 4: FAIL - Check your deployment messages match exactly")

    # Task 5: Servers running: 5
    if any("Servers running:" in line and "5" in line for line in lines):
        print("  Task 5: PASS - Server count printed correctly")
        passed += 1
    else:
        print('  Task 5: FAIL - Expected "Servers running: 5"')

    # Results
    print(f"\n  {'─' * 40}")
    print(f"  Score: {passed}/{total} tasks passed")

    if passed == total:
        print(f"  PERFECT! All tasks completed!")
        print(f"  You're ready to move on to Day 2!")
        print(f"\n  Mark your progress: python3 ../../tracker.py")
    elif passed >= 3:
        print(f"  Good job! Fix the remaining tasks and try again.")
    else:
        print(f"  Keep trying! Re-read the lesson.md for help.")


if __name__ == "__main__":
    check()
