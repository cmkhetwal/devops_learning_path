#!/usr/bin/env python3
"""
Auto-checker for Week 10, Day 4: IAM & Security
"""
import subprocess
import sys
import os

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_10/day_4",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Created user: testuser" in output,
        "Created group: testgroup" in output,
        "Added testuser to testgroup" in output,
        "Attached ReadOnlyAccess to testuser" in output,
        "Users: 1" in output,
        "Deleted user: testuser" in output,
        "After delete: 0" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "Team setup complete: 5 users, 3 groups" in output,
        "alice" in output,
        "bob" in output,
        "diana" in output,
    ]
    return all(checks)

def check_task_3(output):
    output_dir = "/home/cmk/python/devops-python-path/week_10/day_4/output"
    checks = [
        "Generated policy: S3ReadOnly" in output,
        "Generated policy: EC2Manage" in output,
        "Generated policy: DenyDelete" in output and "Deny" in output,
        "Policy has Statement: True" in output,
        os.path.exists(os.path.join(output_dir, "policy_S3ReadOnly.json")),
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "Security Audit Report" in output,
        "=====================" in output,
        "HIGH" in output and "MFA" in output,
        "Total findings:" in output,
    ]
    return all(checks)

def check_task_5(output):
    checks = [
        "IAM Inventory Report" in output,
        "====================" in output,
        "USERS:" in output,
        "GROUPS:" in output,
        "Summary:" in output and "users" in output and "groups" in output,
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 10, Day 4 - IAM & Security")
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
        ("Task 1 - MockIAM class", check_task_1),
        ("Task 2 - Team setup", check_task_2),
        ("Task 3 - Policy generator", check_task_3),
        ("Task 4 - Security audit", check_task_4),
        ("Task 5 - IAM report", check_task_5),
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
        print("PERFECT! IAM security skills complete!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
