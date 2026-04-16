#!/usr/bin/env python3
"""
Auto-checker for Week 9, Day 4: Docker Compose + Python
"""
import subprocess
import sys
import os

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_09/day_4",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Compose config: 3 services" in output,
        "web" in output and "api" in output and "db" in output,
    ]
    return all(checks)

def check_task_2(output):
    output_dir = "/home/cmk/python/devops-python-path/week_09/day_4/output"
    checks = [
        "Wrote compose file:" in output,
        os.path.exists(os.path.join(output_dir, "docker-compose.yml")),
        "File exists: True" in output,
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        "Valid config errors: []" in output,
        "Missing 'version'" in output,
        "missing image or build" in output,
        "not defined" in output,
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "Generated dev config" in output,
        "Generated prod config" in output,
        "Dev restart: no" in output,
        "Prod restart: always" in output,
        "Prod deploy: True" in output,
    ]
    return all(checks)

def check_task_5(output):
    output_dir = "/home/cmk/python/devops-python-path/week_09/day_4/output"
    checks = [
        "Generated stack for 'myapp': 3 services" in output,
        "myapp-web" in output,
        "myapp-api" in output,
        "myapp-db" in output,
        "Has volumes: True" in output,
        os.path.exists(os.path.join(output_dir, "myapp-compose.yml")),
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 9, Day 4 - Docker Compose + Python")
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
        ("Task 1 - Build compose config", check_task_1),
        ("Task 2 - Write compose file", check_task_2),
        ("Task 3 - Validate config", check_task_3),
        ("Task 4 - Environment configs", check_task_4),
        ("Task 5 - App stack generator", check_task_5),
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
        print("PERFECT! Compose generation mastered!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
