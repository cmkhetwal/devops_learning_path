#!/usr/bin/env python3
"""
Auto-checker for Week 10, Day 5: CloudWatch & Lambda
"""
import subprocess
import sys

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_10/day_5",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def check_task_1(output):
    checks = [
        "Metric: AWS/EC2/CPUUtilization = 75.5" in output,
        "Data points: 6" in output,
        "Created alarm: TestAlarm" in output,
        "ALARM" in output,
        "Triggered: 1" in output,
    ]
    return all(checks)

def check_task_2(output):
    checks = [
        "Metric: AWS/EC2/CPUUtilization" in output,
        "points:" in output,
        "avg_of_averages:" in output,
        "peak:" in output,
        "trend: rising" in output,
        "TIME" in output and "AVG" in output and "MAX" in output,
    ]
    return all(checks)

def check_task_3(output):
    checks = [
        "Created alarm: HighCPU" in output,
        "Created alarm: HighMemory" in output,
        "Created alarm: HighDisk" in output,
        "Alarms triggered: 2 of 4" in output,
    ]
    return all(checks)

def check_task_4(output):
    checks = [
        "Created Lambda: hello" in output,
        "Invoked hello" in output,
        "StatusCode" in output and "200" in output,
        "Hello DevOps" in output or "Hello, DevOps" in output,
        "Functions:" in output,
    ]
    return all(checks)

def check_task_5(output):
    checks = [
        "Pipeline complete:" in output and "alerts processed" in output,
        "alarms_total" in output,
        "alarms_triggered" in output,
        "alerts_processed" in output,
    ]
    return all(checks)

def main():
    print("=" * 60)
    print("  CHECKING: Week 10, Day 5 - CloudWatch & Lambda")
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
        ("Task 1 - MockCloudWatch class", check_task_1),
        ("Task 2 - Metric analyzer", check_task_2),
        ("Task 3 - Alarm manager", check_task_3),
        ("Task 4 - MockLambda class", check_task_4),
        ("Task 5 - Monitoring pipeline", check_task_5),
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
        print("PERFECT! CloudWatch and Lambda mastered!")
    elif score >= 3:
        print("Good progress! Review the failing tasks.")
    else:
        print("Review the lesson and try again.")

if __name__ == "__main__":
    main()
