#!/usr/bin/env python3
"""
Auto-checker for Week 9, Day 3: Image Management
"""
import subprocess
import sys

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_09/day_3",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Image(nginx:latest, 150MB)" in output,
        "myregistry.com/nginx:v1.0" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "Pulled nginx:latest (150MB)" in output,
        "Pulled python:3.11 (350MB)" in output,
        "Total images: 5" in output,
        "Total size: 985 MB" in output,
        "Found redis: Image(redis:7, 80MB)" in output,
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        "Image Analysis: 5 images, total 985 MB" in output,
        "total_mb: 985" in output,
        "average_mb: 197.0" in output,
        "largest: postgres:15" in output,
        "smallest: alpine:3.18" in output,
        "count: 5" in output,
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "Keeping:" in output,
        "Removing:" in output,
        "Removed 3 images, 2 remaining" in output,
    ]
    return all(checks)

def check_task_5(output):
    checks = [
        "Docker Image Inventory" in output,
        "======================" in output,
        "IMAGE" in output and "SIZE" in output and "ID" in output,
        "Total:" in output and "images" in output and "MB" in output,
        "----------------------" in output,
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 9, Day 3 - Image Management")
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
        ("Task 1 - MockImage class", check_task_1),
        ("Task 2 - ImageRegistry", check_task_2),
        ("Task 3 - Size analyzer", check_task_3),
        ("Task 4 - Image cleanup", check_task_4),
        ("Task 5 - Inventory report", check_task_5),
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
        print("PERFECT! Docker image management mastered!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
