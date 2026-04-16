#!/usr/bin/env python3
"""
Week 1, Day 6 - Auto-checker
Run: python3 check.py
"""

import subprocess
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
exercise_path = os.path.join(script_dir, "exercise.py")


def run_exercise():
    try:
        result = subprocess.run(
            [sys.executable, exercise_path],
            capture_output=True, text=True, timeout=10
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "ERROR: Script took too long to run"
    except Exception as e:
        return "", str(e)


def check():
    print("\n  Checking your exercise...\n")

    stdout, stderr = run_exercise()

    if stderr:
        print(f"  ERROR in your code:\n  {stderr}")
        print(f"\n  Fix the error and try again!")
        return

    output = stdout
    lines = output.strip().split("\n") if output.strip() else []
    passed = 0
    total = 5

    # ── Mini-Project 1: Server Info Card ──
    mp1_checks = [
        "prod-web-07" in output,
        "10.0.5.27" in output,
        "Ubuntu 22.04" in output,
        "4" in output and "core" in output.lower(),
        "16.0" in output,
        "500" in output,
        "True" in output,
        "SERVER INFO CARD" in output.upper(),
    ]
    if all(mp1_checks):
        print("  Mini-Project 1 (Server Info Card): PASS")
        passed += 1
    else:
        missing = []
        labels = [
            "hostname prod-web-07",
            "IP 10.0.5.27",
            "OS Ubuntu 22.04",
            "CPU 4 cores",
            "Memory 16.0",
            "Disk 500",
            "Active True",
            "Title SERVER INFO CARD",
        ]
        for i, ok in enumerate(mp1_checks):
            if not ok:
                missing.append(labels[i])
        print(f"  Mini-Project 1 (Server Info Card): FAIL - Missing: {', '.join(missing)}")

    # ── Mini-Project 2: Simple Calculator ──
    mp2_checks = [
        "Simple Calculator" in output,
        "120 + 7 = 127" in output,
        "120 - 7 = 113" in output,
        "120 * 7 = 840" in output,
        "120 / 7 = 17.14" in output,
        "120 // 7 = 17" in output,
        "120 % 7 = 1" in output,
        "120 ** 7 = 358318080000000" in output,
    ]
    if all(mp2_checks):
        print("  Mini-Project 2 (Simple Calculator): PASS")
        passed += 1
    else:
        missing = []
        labels = [
            "title line",
            "addition (127)",
            "subtraction (113)",
            "multiplication (840)",
            "division (17.14)",
            "floor division (17)",
            "modulo (1)",
            "power (358318080000000)",
        ]
        for i, ok in enumerate(mp2_checks):
            if not ok:
                missing.append(labels[i])
        print(f"  Mini-Project 2 (Simple Calculator): FAIL - Missing: {', '.join(missing)}")

    # ── Mini-Project 3: Log Line Builder ──
    mp3_checks = [
        "[2024-01-15 10:30:00] [INFO] Server started on port 8080" in output,
        "[2024-01-15 10:35:22] [ERROR] Connection refused to database on port 5432" in output,
        "[2024-01-15 10:40:05] [WARNING] Disk usage at 85%" in output,
    ]
    if all(mp3_checks):
        print("  Mini-Project 3 (Log Line Builder): PASS")
        passed += 1
    else:
        missing = []
        labels = ["INFO log line", "ERROR log line", "WARNING log line"]
        for i, ok in enumerate(mp3_checks):
            if not ok:
                missing.append(labels[i])
        print(f"  Mini-Project 3 (Log Line Builder): FAIL - Missing: {', '.join(missing)}")

    # ── Mini-Project 4: String Processor ──
    mp4_checks = [
        "Step 1 - Stripped: WEB-Server-01.Example.COM" in output,
        "Step 2 - Lowercase: web-server-01.example.com" in output,
        "Step 3 - Underscores: web_server_01.example.com" in output,
        "Step 4 - Server name: web_server_01" in output,
        "Step 5 - Name length: 15" in output,
    ]
    if all(mp4_checks):
        print("  Mini-Project 4 (String Processor): PASS")
        passed += 1
    else:
        missing = []
        labels = ["Step 1 strip", "Step 2 lowercase", "Step 3 replace", "Step 4 slice", "Step 5 length"]
        for i, ok in enumerate(mp4_checks):
            if not ok:
                missing.append(labels[i])
        print(f"  Mini-Project 4 (String Processor): FAIL - Missing: {', '.join(missing)}")

    # ── Mini-Project 5: Deployment Summary ──
    mp5_checks = [
        "DEPLOYMENT SUMMARY" in output,
        "payment-service" in output and "3.2.1" in output,
        "12 total" in output,
        "11" in output and "91.7%" in output,
        "1" in output and "8.3%" in output,
        "3 min 5 sec" in output,
        "ISSUES DETECTED" in output,
    ]
    if all(mp5_checks):
        print("  Mini-Project 5 (Deployment Summary): PASS")
        passed += 1
    else:
        missing = []
        labels = [
            "title DEPLOYMENT SUMMARY",
            "app name and version",
            "12 total servers",
            "success 91.7%",
            "failed 8.3%",
            "duration 3 min 5 sec",
            "status ISSUES DETECTED",
        ]
        for i, ok in enumerate(mp5_checks):
            if not ok:
                missing.append(labels[i])
        print(f"  Mini-Project 5 (Deployment Summary): FAIL - Missing: {', '.join(missing)}")

    # ── Results ──
    print(f"\n  {'─' * 40}")
    print(f"  Score: {passed}/{total} mini-projects passed")

    if passed == total:
        print(f"  PERFECT! You crushed the practice day!")
        print(f"  You're ready for the Week 1 Quiz on Day 7!")
        print(f"\n  Mark your progress: python3 ../../tracker.py")
    elif passed >= 3:
        print(f"  Good job! Fix the remaining projects and try again.")
    else:
        print(f"  Keep going! Re-read lesson.md for the quick reference table.")


if __name__ == "__main__":
    check()
