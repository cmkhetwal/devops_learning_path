"""
Week 11, Day 7: Check - Quiz Day
Verifies all 10 quiz answers from exercise.py
"""

import subprocess
import sys

def run_test(test_code):
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    score = 0
    total = 10

    answers = {
        "q1": "b",   # True
        "q2": "c",   # repo.active_branch
        "q3": "b",   # POST
        "q4": "c",   # Last succeeded, currently running
        "q5": "c",   # on: schedule
        "q6": "b",   # Continue other combinations
        "q7": "b",   # {% for %}...{% endfor %}
        "q8": "b",   # Output port or 8080 if undefined
        "q9": "c",   # Tasks triggered by notification
        "q10": "b",  # Same result multiple times
    }

    topics = {
        "q1": "GitPython - is_dirty()",
        "q2": "GitPython - active branch",
        "q3": "Jenkins API - trigger build method",
        "q4": "Jenkins API - blue_anime color",
        "q5": "GitHub Actions - schedule trigger",
        "q6": "GitHub Actions - fail-fast",
        "q7": "Jinja2 - for-loop syntax",
        "q8": "Jinja2 - default filter",
        "q9": "Ansible - handlers",
        "q10": "Ansible - idempotent",
    }

    for qnum, correct in answers.items():
        topic = topics[qnum]
        code = f'''
import sys; sys.path.insert(0, ".")
from exercise import {qnum}
print({qnum})
'''
        ok, out, err = run_test(code)
        student_answer = out.strip().lower() if ok else ""

        if student_answer == correct:
            print(f"  {qnum}: PASS - {topic}")
            score += 1
        elif student_answer == "":
            print(f"  {qnum}: SKIP - {topic} (no answer)")
        else:
            print(f"  {qnum}: FAIL - {topic} (your answer: {student_answer}, correct: {correct})")

    print(f"\n{'='*40}")
    print(f"  Week 11 Quiz Score: {score}/{total}")
    if score == total:
        print("  PERFECT! CI/CD & IaC mastered!")
    elif score >= 8:
        print("  Excellent! Almost there!")
    elif score >= 6:
        print("  Good job! Review missed topics.")
    else:
        print("  Review the Week 11 material.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
