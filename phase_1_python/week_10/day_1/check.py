#!/usr/bin/env python3
"""
Auto-checker for Week 10, Day 1: boto3 Setup
"""
import subprocess
import sys

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_10/day_1",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Region: us-west-2" in output,
        "Profile: dev" in output,
        "Services: 10" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "AWSClient(ec2, us-east-1)" in output,
        "Account: 123456789012" in output,
        "Regions: 5" in output,
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        ("Connected to AWS" in output or "AWS not available" in output),
        "Session type:" in output,
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "REGION" in output and "ENDPOINT" in output,
        "us-east-1" in output,
        "Total regions:" in output,
    ]
    return all(checks)

def check_task_5(output):
    checks = [
        "AWS Environment Report" in output,
        "======================" in output,
        "Profile" in output,
        "Region" in output,
        "Account" in output,
        "User ARN" in output or "Arn" in output,
        "Available Services" in output,
        "Available Regions" in output,
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 10, Day 1 - boto3 Setup")
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
        ("Task 1 - MockAWSSession class", check_task_1),
        ("Task 2 - MockAWSClient class", check_task_2),
        ("Task 3 - Safe connection", check_task_3),
        ("Task 4 - Region explorer", check_task_4),
        ("Task 5 - Environment report", check_task_5),
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
        print("PERFECT! boto3 fundamentals understood!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
