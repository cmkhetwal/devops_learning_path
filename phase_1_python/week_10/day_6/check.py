#!/usr/bin/env python3
"""
Auto-checker for Week 10, Day 6: Practice Day
"""
import subprocess
import sys
import os

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_10/day_6",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_project_1(output):
    checks = [
        "AWS Resource Inventory" in output,
        "EC2 INSTANCES" in output,
        "S3 BUCKETS" in output,
        "IAM USERS" in output,
        "ec2_count" in output,
        "s3_count" in output,
        "iam_count" in output,
    ]
    return all(checks)

def check_project_2(output):
    checks = [
        "AWS Cost Analysis" in output or "Cost Analysis" in output,
        "EC2 COSTS:" in output,
        "S3 COSTS:" in output,
        "TOTAL ESTIMATED MONTHLY COST" in output or "total" in output,
        "ec2_cost" in output,
        "s3_cost" in output,
    ]
    return all(checks)

def check_project_3(output):
    output_dir = "/home/cmk/python/devops-python-path/week_10/day_6/output"
    checks = [
        "Backup Plan" in output,
        "Total objects:" in output,
        "Total size:" in output,
        "Estimated time:" in output,
        "Plan buckets: 3" in output,
        os.path.exists(os.path.join(output_dir, "backup_plan.json")),
    ]
    return all(checks)

def check_project_4(output):
    checks = [
        "Fleet Manager:" in output,
        "Matched:" in output,
        "Starting" in output or "Stopping" in output,
        "Fleet result:" in output,
    ]
    return all(checks)

def check_project_5(output):
    output_dir = "/home/cmk/python/devops-python-path/week_10/day_6/output"
    checks = [
        "Infrastructure report generated:" in output,
        "EC2 total: 6" in output,
        "S3 buckets: 5" in output,
        "IAM users: 6" in output,
        "Monthly cost: $" in output,
        os.path.exists(os.path.join(output_dir, "infra_report.json")),
    ]
    return all(checks)

def main():
    print("=" * 60)
    print("  CHECKING: Week 10, Day 6 - Practice Day")
    print("=" * 60)

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
        ("Project 1 - Resource Inventory", check_project_1),
        ("Project 2 - Cost Analyzer", check_project_2),
        ("Project 3 - S3 Backup Tool", check_project_3),
        ("Project 4 - EC2 Fleet Manager", check_project_4),
        ("Project 5 - Infrastructure Report", check_project_5),
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
        print("PERFECT! All 5 AWS mini-projects complete!")
    elif score >= 3:
        print("Good progress! Review the failing projects.")
    else:
        print("Keep going! Review each project's requirements.")

if __name__ == "__main__":
    main()
