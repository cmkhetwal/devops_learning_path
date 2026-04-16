#!/usr/bin/env python3
"""
Auto-checker for Week 10, Day 7: Quiz Day
"""
import subprocess
import sys

CORRECT = {
    "Q1": "b",
    "Q2": "c",
    "Q3": "b",
    "Q4": "c",
    "Q5": "b",
    "Q6": "b",
    "Q7": "b",
    "Q8": "b",
    "Q9": "b",
    "Q10": "b",
}

def run_exercise():
    result = subprocess.run(
        [sys.executable, "exercise.py"],
        capture_output=True, text=True,
        cwd="/home/cmk/python/devops-python-path/week_10/day_7",
        timeout=30
    )
    return result.stdout + result.stderr, result.returncode

def extract_answers(output):
    """Extract answers from output."""
    answers = {}
    for line in output.splitlines():
        line = line.strip()
        for q_num in CORRECT:
            if line.startswith(f"{q_num}:"):
                parts = line.split(":")
                if len(parts) >= 2:
                    ans = parts[1].strip().split()[0].strip()
                    if ans != "---":
                        answers[q_num] = ans
    return answers

def main():
    print("=" * 55)
    print("  CHECKING: Week 10 Quiz - AWS with Python")
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

    student_answers = extract_answers(output)

    score = 0
    for q_num in sorted(CORRECT.keys(), key=lambda x: int(x[1:])):
        student = student_answers.get(q_num, "")
        correct = CORRECT[q_num]
        if student.lower() == correct.lower():
            score += 1
            print(f"  PASS - {q_num}: {student}")
        elif student:
            print(f"  FAIL - {q_num}: you said '{student}', correct is '{correct}'")
        else:
            print(f"  FAIL - {q_num}: unanswered (correct: '{correct}')")

    print(f"\nScore: {score}/{len(CORRECT)}")
    if score == len(CORRECT):
        print("PERFECT! Week 10 AWS mastery confirmed!")
    elif score >= 7:
        print("Great job! Review the missed questions.")
    elif score >= 5:
        print("Good effort! Re-read the cheat sheet for missed topics.")
    else:
        print("Review the Week 10 lessons and try again.")

if __name__ == "__main__":
    main()
