#!/usr/bin/env python3
"""
Auto-checker for Week 9, Day 1: Docker SDK Basics
"""
import subprocess
import sys

def run_exercise():
    """Run the exercise and capture output."""
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True, cwd="/home/cmk/python/devops-python-path/week_09/day_1",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    """Check MockDockerClient class."""
    checks = [
        "Ping: True" in output,
        "Architecture" in output,
        "Version: 24.0.7" in output,
    ]
    return all(checks)

def check_task_2(output):
    """Check safe connection function."""
    checks = [
        "Client type:" in output,
        ("Connected to Docker daemon" in output or "Docker not available" in output),
    ]
    return all(checks)

def check_task_3(output):
    """Check Docker info extraction."""
    checks = [
        "os:" in output or "os: " in output,
        "arch:" in output or "arch: " in output,
        "cpus:" in output or "cpus: " in output,
        "memory_gb:" in output or "memory_gb: " in output,
        "containers:" in output or "containers: " in output,
    ]
    return all(checks)

def check_task_4(output):
    """Check version report."""
    checks = [
        "Docker Version Report" in output,
        "====================" in output,
        "Docker Version" in output,
        "API Version" in output,
        "OS/Arch" in output,
        "Total Containers" in output,
        "Total Images" in output,
    ]
    return all(checks)

def check_task_5(output):
    """Check health-check utility."""
    checks = [
        "PING: OK" in output or "PING: FAILED" in output,
        "CONTAINERS:" in output and "running" in output and "stopped" in output,
        "IMAGES:" in output,
        "MEMORY:" in output,
        "Total checks:" in output,
    ]
    return all(checks)

def main():
    print("=" * 50)
    print("  CHECKING: Week 9, Day 1 - Docker SDK Basics")
    print("=" * 50)

    try:
        output, returncode = run_exercise()
    except subprocess.TimeoutExpired:
        print("\nFAILED: Exercise timed out after 30 seconds")
        return
    except FileNotFoundError:
        print("\nFAILED: exercise.py not found")
        return

    if returncode != 0 and not output.strip():
        print(f"\nFAILED: Exercise crashed with return code {returncode}")
        print(f"Error output: {output}")
        return

    tasks = [
        ("Task 1 - MockDockerClient class", check_task_1),
        ("Task 2 - Safe connection function", check_task_2),
        ("Task 3 - Docker info extraction", check_task_3),
        ("Task 4 - Version report", check_task_4),
        ("Task 5 - Health-check utility", check_task_5),
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
        print("PERFECT! You understand Docker SDK connection patterns!")
    elif score >= 3:
        print("Good progress! Review the failing tasks and try again.")
    else:
        print("Keep going! Re-read the lesson and check your code carefully.")

if __name__ == "__main__":
    main()
