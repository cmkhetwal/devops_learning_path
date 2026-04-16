#!/usr/bin/env python3
"""
Auto-checker for Week 9, Day 2: Container Management
"""
import subprocess
import sys

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_09/day_2",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Container(web-server, running)" in output,
        "web-server stopped" in output,
        "Container(web-server, exited)" in output,
        "web-server started" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "All containers: 5" in output,
        "Running: 3" in output,
        "Found db-1: Container(db-1, running)" in output,
        "Found nonexistent: None" in output,
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        "Found 3 containers with status: running" in output,
        "Found 2 containers with status: exited" in output,
        "Found 5 containers with status: all" in output,
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "Cleaned up 2 exited containers" in output,
        "Remaining containers: 3" in output,
    ]
    return all(checks)

def check_task_5(output):
    checks = [
        "Container Status Report" in output,
        "=======================" in output,
        "Total:" in output,
        "Running:" in output,
        "Exited:" in output,
        "NAME" in output and "STATUS" in output and "IMAGE" in output,
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 9, Day 2 - Container Management")
    print("=" * 55)

    try:
        output, returncode = run_exercise()
    except subprocess.TimeoutExpired:
        print("\nFAILED: Exercise timed out")
        return
    except FileNotFoundError:
        print("\nFAILED: exercise.py not found")
        return

    if returncode != 0 and not output.strip():
        print(f"\nFAILED: Exercise crashed (rc={returncode})")
        print(output)
        return

    tasks = [
        ("Task 1 - MockContainer class", check_task_1),
        ("Task 2 - ContainerManager class", check_task_2),
        ("Task 3 - Filter containers", check_task_3),
        ("Task 4 - Container cleanup", check_task_4),
        ("Task 5 - Status report", check_task_5),
    ]

    score = 0
    for name, checker in tasks:
        try:
            passed = checker(output)
        except Exception:
            passed = False
        status = "PASS" if passed else "FAIL"
        if passed:
            score += 1
        print(f"  {status} - {name}")

    print(f"\nScore: {score}/{len(tasks)}")
    if score == len(tasks):
        print("PERFECT! Container management skills locked in!")
    elif score >= 3:
        print("Good work! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
