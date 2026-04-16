#!/usr/bin/env python3
"""
Auto-checker for Week 9, Day 5: Container Monitoring
"""
import subprocess
import sys

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_09/day_5",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Metrics(web-1: CPU=45.2%, MEM=50.0%)" in output,
        "Metrics(api-1: CPU=85.0%, MEM=93.8%)" in output,
        "Metrics(db-1: CPU=92.5%, MEM=87.9%)" in output,
        "web-1 healthy: True" in output,
        "severity: normal" in output,
        "severity: critical" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "Log Analysis:" in output and "10 lines" in output,
        "total: 10" in output,
        "error: 2" in output,
        "warning: 2" in output,
        "error_rate: 20.0" in output,
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        "Total alerts:" in output,
        ("CRITICAL" in output or "WARNING" in output or "critical" in output.lower() or "warning" in output.lower()),
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "Container Monitoring Dashboard" in output,
        "==============================" in output,
        "NAME" in output and "CPU%" in output and "STATUS" in output,
        "healthy" in output,
        "Dashboard summary:" in output,
    ]
    return all(checks)

def check_task_5(output):
    checks = [
        "Overall Status:" in output,
        "Report:" in output,
        "containers_total" in output,
        "containers_healthy" in output,
        "total_alerts" in output,
        "log_errors" in output,
        "overall_status" in output,
    ]
    return all(checks)

def main():
    print("=" * 55)
    print("  CHECKING: Week 9, Day 5 - Container Monitoring")
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
        ("Task 1 - ContainerMetrics class", check_task_1),
        ("Task 2 - Log analyzer", check_task_2),
        ("Task 3 - Alert system", check_task_3),
        ("Task 4 - Monitoring dashboard", check_task_4),
        ("Task 5 - Full monitoring report", check_task_5),
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
        print("PERFECT! Container monitoring skills complete!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
