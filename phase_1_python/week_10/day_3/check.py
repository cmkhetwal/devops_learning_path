#!/usr/bin/env python3
"""
Auto-checker for Week 10, Day 3: S3 Operations
"""
import subprocess
import sys
import os

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_10/day_3",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Created bucket: test-bucket" in output,
        "Uploaded hello.txt to test-bucket" in output,
        "Objects in test-bucket: 1" in output,
        "Bucket size: 100 bytes" in output,
        "Deleted hello.txt from test-bucket" in output,
        "Deleted bucket: test-bucket" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "Created bucket: app-logs-prod" in output,
        "Created bucket: app-data-prod" in output,
        "Created bucket: app-backups" in output,
        "Created bucket: dev-artifacts" in output,
        "Total buckets: 4" in output,
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        "Uploaded 6 objects to app-logs-prod" in output,
        "All objects: 6" in output,
        "Log objects: 3" in output,
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "Storage Analysis" in output,
        "================" in output,
        "BUCKET" in output and "OBJECTS" in output and "SIZE" in output,
        "Total:" in output and "objects across" in output and "buckets" in output,
    ]
    return all(checks)

def check_task_5(output):
    manifest_path = "/home/cmk/python/devops-python-path/week_10/day_3/output/backup_manifest.json"
    checks = [
        "Backup manifest:" in output,
        "Manifest objects: 6" in output,
        "Manifest file exists: True" in output,
        os.path.exists(manifest_path),
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 10, Day 3 - S3 Operations")
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
        ("Task 1 - MockS3 class", check_task_1),
        ("Task 2 - Bucket management", check_task_2),
        ("Task 3 - Object operations", check_task_3),
        ("Task 4 - Storage analyzer", check_task_4),
        ("Task 5 - Backup manifest", check_task_5),
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
        print("PERFECT! S3 operations mastered!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
