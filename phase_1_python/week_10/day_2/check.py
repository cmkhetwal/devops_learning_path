#!/usr/bin/env python3
"""
Auto-checker for Week 10, Day 2: EC2 Management
"""
import subprocess
import sys

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_10/day_2",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Parsed: web-server-01" in output,
        "name: web-server-01" in output,
        "state: running" in output,
        "environment: production" in output,
        "team: frontend" in output,
        "public_ip: 54.123.45.67" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "Filter matched 3 of 5 instances" in output,  # running
        "Filter matched 3 of 5 instances" in output,  # production (same count)
        "Filter matched 1 of 5 instances" in output,  # backend+running
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        "Stopping web-server-01" in output,
        "Starting dev-server-01" in output,
        "Terminating test-server-01" in output,
        "already stopped" in output,
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "CostCenter" in output,
        "eng-123" in output,
        "Final tag count:" in output,
    ]
    return all(checks)

def check_task_5(output):
    checks = [
        "EC2 Instance Inventory" in output,
        "======================" in output,
        "NAME" in output and "ID" in output and "TYPE" in output and "STATE" in output,
        "Total:" in output and "running" in output and "stopped" in output,
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 10, Day 2 - EC2 Management")
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
        ("Task 1 - Parse instance data", check_task_1),
        ("Task 2 - Filter instances", check_task_2),
        ("Task 3 - Instance management", check_task_3),
        ("Task 4 - Tag manager", check_task_4),
        ("Task 5 - EC2 inventory report", check_task_5),
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
        print("PERFECT! EC2 management skills complete!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
