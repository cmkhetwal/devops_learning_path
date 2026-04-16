#!/usr/bin/env python3
"""
Week 12, Day 7: Final Graduation Assessment - Auto-Checker
Grades all 20 questions covering the entire 12-week program.
"""

import subprocess
import sys
import os

EXERCISE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

ANSWERS = {
    1: "int",
    2: ["web", "server", "01"],
    3: 2,
    4: "web-02",
    5: 8080,
    6: "B",
    7: "B",
    8: "C",
    9: "B",
    10: "C",
    11: "C",
    12: ["4", "16"],
    13: {
        "GET": "retrieve a resource",
        "POST": "create a new resource",
        "PUT": "update an existing resource",
        "DELETE": "remove a resource",
    },
    14: "web-01 started | running=True",
    15: "B",
    16: "B",
    17: {
        "EC2": "virtual servers",
        "S3": "object storage",
        "IAM": "access management",
        "CloudWatch": "monitoring and logging",
    },
    18: ["lint", "build", "test", "deploy"],
    19: ["errors", "latency", "saturation", "traffic"],
    20: {
        "http_check": "requests",
        "logging": "logging",
        "alerting": "smtplib",
        "scheduling": "schedule",
    },
}

TOPICS = {
    1: "Variables & Types",
    2: "Strings",
    3: "Control Flow",
    4: "Lists",
    5: "Dictionaries",
    6: "Functions",
    7: "Virtual Envs",
    8: "File Handling",
    9: "JSON/YAML",
    10: "Error Handling",
    11: "OS/Subprocess",
    12: "Regex",
    13: "HTTP & APIs",
    14: "OOP Basics",
    15: "Inheritance",
    16: "Docker",
    17: "AWS",
    18: "CI/CD",
    19: "Monitoring",
    20: "DevOps Scenario",
}


def run_question(q_num):
    code = f"""
import sys, os
sys.path.insert(0, os.path.dirname(r'{EXERCISE}'))
from exercise import question_{q_num}
result = question_{q_num}()
print(repr(result))
"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True, text=True, timeout=10,
            cwd=os.path.dirname(EXERCISE),
        )
        if result.returncode != 0:
            return None, result.stderr.strip()[:100]
        return eval(result.stdout.strip()), None
    except Exception as e:
        return None, str(e)


def check_answer(student, expected):
    if student is None:
        return False
    if isinstance(expected, list) and isinstance(student, list):
        return student == expected
    if isinstance(expected, dict) and isinstance(student, dict):
        return student == expected
    return student == expected


def main():
    print()
    print("=" * 60)
    print("  FINAL GRADUATION ASSESSMENT")
    print("  DevOps Python Path - All 12 Weeks")
    print("=" * 60)
    print()

    passed = 0
    total = 20

    for q in range(1, 21):
        student_answer, error = run_question(q)
        if error:
            print(f"  Q{q:>2} [{TOPICS[q]:<18}]: FAIL (error)")
        elif student_answer is None:
            print(f"  Q{q:>2} [{TOPICS[q]:<18}]: SKIP (returned None)")
        elif check_answer(student_answer, ANSWERS[q]):
            print(f"  Q{q:>2} [{TOPICS[q]:<18}]: PASS")
            passed += 1
        else:
            print(f"  Q{q:>2} [{TOPICS[q]:<18}]: FAIL")
            print(f"       Expected: {ANSWERS[q]}")
            print(f"       Got:      {student_answer}")

    pct = (passed / total) * 100
    print()
    print("-" * 60)
    print(f"  Score: {passed}/{total} ({pct:.0f}%)")
    print("-" * 60)

    if passed == total:
        print()
        print("  *" * 30)
        print()
        print("     CONGRATULATIONS! PERFECT SCORE!")
        print()
        print("     =============================")
        print("     GRADUATION CERTIFICATE")
        print("     =============================")
        print("     DevOps Python Path - COMPLETE")
        print("     90 Days of Learning")
        print("     Score: 20/20 (100%)")
        print("     =============================")
        print()
        print("     You are ready for a DevOps career!")
        print()
        print("  *" * 30)
    elif pct >= 80:
        print(f"  PASSED! Excellent work! Review the {total - passed} missed topic(s).")
    elif pct >= 60:
        print("  Almost there! Review weak areas and retake.")
    else:
        print("  More study needed. Review the weekly lessons and try again.")

    print()
    print("  Next steps:")
    print("  - Run 'python3 ../../tracker.py' to see your full progress")
    print("  - Run 'python3 ../../quiz.py <week>' for any week's quiz")
    print("  - See lesson.md for career guidance and next steps")
    print()


if __name__ == "__main__":
    main()
