#!/usr/bin/env python3
"""
Auto-checker for Week 9, Day 6: Practice Day
"""
import subprocess
import sys
import os

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_09/day_6",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_project_1(output):
    checks = [
        "web-frontend" in output,
        "nginx:latest" in output,
        "running" in output,
        "Available commands:" in output,
        "Unknown command: invalid" in output,
    ]
    return all(checks)

def check_project_2(output):
    checks = [
        "Health Dashboard" in output,
        "================" in output,
        "healthy" in output,
        "critical" in output,
        "Summary:" in output,
    ]
    return all(checks)

def check_project_3(output):
    output_dir = "/home/cmk/python/devops-python-path/week_09/day_6/output"
    checks = [
        "Generated compose for 'webapp': 3 services" in output,
        os.path.exists(os.path.join(output_dir, "compose_webapp.json")),
    ]
    return all(checks)

def check_project_4(output):
    checks = [
        "Image Cleanup Report" in output,
        "KEEP:" in output,
        "REMOVE:" in output,
        "Space saved:" in output,
        "Cleanup result:" in output,
    ]
    return all(checks)

def check_project_5(output):
    checks = [
        "Deploying web version v2.0" in output,
        "Stopping" in output,
        "Starting" in output,
        "Deployment complete!" in output,
        "status" in output and "success" in output,
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 9, Day 6 - Practice Day")
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
        ("Project 1 - Docker CLI Tool", check_project_1),
        ("Project 2 - Health Dashboard", check_project_2),
        ("Project 3 - Compose Generator", check_project_3),
        ("Project 4 - Image Cleanup", check_project_4),
        ("Project 5 - Deployment Manager", check_project_5),
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
        print("PERFECT! All 5 mini-projects complete!")
    elif score >= 3:
        print("Good progress! Review the failing projects.")
    else:
        print("Keep going! Review each project's requirements.")

if __name__ == "__main__":
    main()
