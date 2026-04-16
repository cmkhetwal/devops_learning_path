#!/usr/bin/env python3
"""
Week 8, Day 7: Phase 2 Final Test - Auto-Checker
Grades all 15 questions covering Weeks 5-8.
"""

import subprocess
import sys
import os

EXERCISE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

ANSWERS = {
    1: "B",
    2: {
        "json.load": "read JSON from file",
        "json.dump": "write JSON to file",
        "json.loads": "parse JSON string to Python",
        "json.dumps": "convert Python to JSON string",
    },
    3: "caught done",
    4: "B",
    5: {"return_type": "CompletedProcess", "success_returncode": 0, "capture_flag": "capture_output"},
    6: {200: "success", 301: "redirect", 403: "client_error", 404: "client_error", 500: "server_error", 502: "server_error", 201: "success"},
    7: "B",
    8: {
        "list_pods": {"method": "GET", "path": "/api/v1/pods"},
        "create_pod": {"method": "POST", "path": "/api/v1/pods"},
        "get_pod": {"method": "GET", "path": "/api/v1/pods/web-01"},
        "delete_pod": {"method": "DELETE", "path": "/api/v1/pods/web-01"},
        "list_pod_logs": {"method": "GET", "path": "/api/v1/pods/web-01/logs"},
    },
    9: "B",
    10: "B",
    11: [True, True, False],
    12: {
        "@property": "attribute-like access with getter/setter logic",
        "@classmethod": "alternative constructor or class-level operation",
        "@staticmethod": "utility function that doesn't need self or cls",
    },
    13: "C",
    14: ["A", "B", "C", "E"],
    15: [
        "set up virtual environment",
        "create project structure with __init__.py",
        "define classes for infrastructure (Server, Deployment)",
        "add error handling and logging",
        "write unit tests",
        "create requirements.txt and setup.py",
    ],
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


def check_answer(q_num, student, expected):
    if student is None:
        return False
    if isinstance(expected, list) and isinstance(student, list):
        return student == expected
    if isinstance(expected, dict) and isinstance(student, dict):
        return student == expected
    return student == expected


def main():
    print("=" * 60)
    print("  PHASE 2 FINAL TEST - Weeks 5-8")
    print("=" * 60)
    print()

    passed = 0
    total = 15

    topics = {
        1: "File Handling", 2: "JSON Operations", 3: "Exception Handling",
        4: "OS Operations", 5: "subprocess", 6: "HTTP Status Codes",
        7: "requests Library", 8: "REST API Design", 9: "Socket Programming",
        10: "OOP - Classes", 11: "OOP - Inheritance", 12: "Properties & Methods",
        13: "Project Structure", 14: "Testing", 15: "DevOps Scenario",
    }

    for q in range(1, 16):
        student_answer, error = run_question(q)
        if error:
            print(f"  Q{q:>2} [{topics[q]:<22}]: FAIL (error: {error[:60]})")
        elif student_answer is None:
            print(f"  Q{q:>2} [{topics[q]:<22}]: SKIP (returned None)")
        elif check_answer(q, student_answer, ANSWERS[q]):
            print(f"  Q{q:>2} [{topics[q]:<22}]: PASS")
            passed += 1
        else:
            print(f"  Q{q:>2} [{topics[q]:<22}]: FAIL")
            print(f"       Expected: {ANSWERS[q]}")
            print(f"       Got:      {student_answer}")

    pct = (passed / total) * 100
    print()
    print("-" * 60)
    print(f"  Score: {passed}/{total} ({pct:.0f}%)")
    print("-" * 60)

    if passed == total:
        print("  PERFECT SCORE! Phase 2 COMPLETE!")
        print("  You're ready for Phase 3: Cloud & DevOps!")
    elif pct >= 70:
        print("  PASSED! Good job. Review missed topics before Phase 3.")
    elif pct >= 50:
        print("  Almost there. Review the lessons and retake the test.")
    else:
        print("  More study needed. Go back and review Weeks 5-8.")

    print()
    print("  Run 'python3 ../../quiz.py 8' for the interactive quiz too!")


if __name__ == "__main__":
    main()
