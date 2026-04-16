#!/usr/bin/env python3
"""
Week 1, Day 7 - Auto-checker
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
    print("\n  Checking your quiz answers...\n")

    stdout, stderr = run_exercise()

    if stderr:
        print(f"  ERROR in your code:\n  {stderr}")
        print(f"\n  Fix the error and try again!")
        return

    output = stdout
    lines = output.strip().split("\n") if output.strip() else []
    passed = 0
    total = 10

    # Build a dict of answers from the output: {"Q1": "...", "Q2": "...", ...}
    answers = {}
    for line in lines:
        line = line.strip()
        for i in range(1, 11):
            prefix = f"Q{i}: "
            if line.startswith(prefix):
                answers[f"Q{i}"] = line[len(prefix):]

    # ── Question 1: print() function ──
    if answers.get("Q1") == "Server is online":
        print("  Q1  (print function):      PASS")
        passed += 1
    elif "Q1" in answers:
        print("  Q1  (print function):      FAIL - Output should be 'Server is online'")
    else:
        print("  Q1  (print function):      SKIP - Uncomment the line and fill in the blank")

    # ── Question 2: variable assignment ──
    if answers.get("Q2") == "443":
        print("  Q2  (variable assignment): PASS")
        passed += 1
    elif "Q2" in answers:
        print("  Q2  (variable assignment): FAIL - port should be the integer 443")
    else:
        print("  Q2  (variable assignment): SKIP - Uncomment the lines and fill in the blank")

    # ── Question 3: boolean type ──
    if answers.get("Q3") == "bool":
        print("  Q3  (data type of True):   PASS")
        passed += 1
    elif "Q3" in answers:
        print(f"  Q3  (data type of True):   FAIL - True is a '{answers['Q3']}'? Think again!")
    else:
        print("  Q3  (data type of True):   SKIP - Uncomment the lines and fill in the blank")

    # ── Question 4: int() conversion ──
    if answers.get("Q4") == "8081":
        print("  Q4  (str to int):          PASS")
        passed += 1
    elif "Q4" in answers:
        print(f"  Q4  (str to int):          FAIL - Expected 8081 (int('8080') + 1), got {answers['Q4']}")
    else:
        print("  Q4  (str to int):          SKIP - Uncomment the lines and fill in the blank")

    # ── Question 5: modulo ──
    if answers.get("Q5") == "2":
        print("  Q5  (modulo 17 % 5):       PASS")
        passed += 1
    elif "Q5" in answers:
        print(f"  Q5  (modulo 17 % 5):       FAIL - 17 % 5 = 2, not {answers['Q5']}")
    else:
        print("  Q5  (modulo 17 % 5):       SKIP - Uncomment the lines and fill in the blank")

    # ── Question 6: len() function ──
    if answers.get("Q6") == "6":
        print("  Q6  (string length):       PASS")
        passed += 1
    elif "Q6" in answers:
        print(f"  Q6  (string length):       FAIL - len('devops') = 6, not {answers['Q6']}")
    else:
        print("  Q6  (string length):       SKIP - Uncomment the lines and fill in the blank")

    # ── Question 7: strip and lower ──
    if answers.get("Q7") == "prod-db-01":
        print("  Q7  (strip + lower):       PASS")
        passed += 1
    elif "Q7" in answers:
        print(f"  Q7  (strip + lower):       FAIL - Expected 'prod-db-01', got '{answers['Q7']}'")
    else:
        print("  Q7  (strip + lower):       SKIP - Uncomment the lines and fill in the blank")

    # ── Question 8: floor division ──
    if answers.get("Q8") == "3":
        print("  Q8  (floor division):      PASS")
        passed += 1
    elif "Q8" in answers:
        print(f"  Q8  (floor division):      FAIL - 15 // 4 = 3, not {answers['Q8']}")
    else:
        print("  Q8  (floor division):      SKIP - Uncomment the lines and fill in the blank")

    # ── Question 9: replace method ──
    if answers.get("Q9") == "web_app_01":
        print("  Q9  (string replace):      PASS")
        passed += 1
    elif "Q9" in answers:
        print(f"  Q9  (string replace):      FAIL - Expected 'web_app_01', got '{answers['Q9']}'")
    else:
        print("  Q9  (string replace):      SKIP - Uncomment the lines and fill in the blank")

    # ── Question 10: f-string building ──
    if answers.get("Q10") == "Server web-07 has 4 CPUs":
        print("  Q10 (f-string):            PASS")
        passed += 1
    elif "Q10" in answers:
        print(f"  Q10 (f-string):            FAIL - Expected 'Server web-07 has 4 CPUs', got '{answers['Q10']}'")
    else:
        print("  Q10 (f-string):            SKIP - Uncomment the lines and fill in the blank")

    # ── Results ──
    answered = len(answers)
    skipped = total - answered

    print(f"\n  {'─' * 40}")
    print(f"  Score: {passed}/{total} correct")

    if skipped > 0:
        print(f"  ({skipped} question{'s' if skipped != 1 else ''} still commented out)")

    if passed == total:
        print(f"\n  PERFECT SCORE! You aced the Week 1 quiz!")
        print(f"  You have a solid foundation in Python basics.")
        print(f"  You're ready for Week 2!")
        print(f"\n  Mark your progress: python3 ../../tracker.py")
    elif passed >= 8:
        print(f"\n  Great job! Review the ones you missed and try again.")
    elif passed >= 5:
        print(f"\n  Good start! Check the cheat sheet in lesson.md for help.")
    else:
        print(f"\n  Keep studying! Re-read the lesson.md cheat sheet and try again.")

    if answered == total and passed < total:
        print(f"  Tip: Review the Week 1 Cheat Sheet in lesson.md")


if __name__ == "__main__":
    check()
