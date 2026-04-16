"""
Week 5, Day 7: Quiz Auto-checker
=================================
Run this file to verify your quiz answers.
"""

import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("WEEK 5, DAY 7 - QUIZ CHECKER")
    print("=" * 50)
    print()

    # Clean up
    for f in ["quiz_output.txt", "quiz_data.csv", "quiz_config.json",
              "quiz_append.txt", "quiz.log"]:
        if os.path.exists(f):
            os.remove(f)

    # Run exercise.py
    result = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, ".")
exec(open("exercise.py").read())

print("---RESULTS---")
print(f"q1_answer={q1_answer!r}")
print(f"q2_answer={q2_answer!r}")
print(f"q3_answer={q3_answer!r}")
print(f"q4_answer={q4_answer!r}")
print(f"q5_answer={q5_answer!r}")
print(f"q6_answer={q6_answer!r}")
print(f"q7_answer={q7_answer!r}")
print(f"q8_answer={q8_answer!r}")
print(f"q9_answer={q9_answer!r}")
print(f"q10_answer={q10_answer!r}")
"""],
        capture_output=True, text=True, timeout=10
    )

    if result.returncode != 0:
        print("ERROR: exercise.py failed to run!")
        print(result.stderr)
        return

    output = result.stdout
    if "---RESULTS---" not in output:
        print("ERROR: Could not find results in output.")
        print(output)
        return

    results_section = output.split("---RESULTS---")[1]
    results = {}
    for line in results_section.strip().split("\n"):
        if "=" in line:
            key, value = line.split("=", 1)
            try:
                results[key] = eval(value)
            except:
                results[key] = None

    score = 0
    total = 10

    # Q1: Count lines
    print("Q1  - Read file and count lines")
    if results.get("q1_answer") == 5:
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: Expected 5, got {results.get('q1_answer')}")

    # Q2: Write to file
    print("Q2  - Write to a file")
    if results.get("q2_answer") == "Hello DevOps\n":
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: Expected 'Hello DevOps\\n', got {results.get('q2_answer')!r}")

    # Q3: Append to file
    print("Q3  - Append to a file")
    if results.get("q3_answer") == "Hello DevOps\nWelcome to Python\n":
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: Expected 'Hello DevOps\\nWelcome to Python\\n', got {results.get('q3_answer')!r}")

    # Q4: Parse JSON string
    print("Q4  - Parse a JSON string")
    if results.get("q4_answer") == "web-01":
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: Expected 'web-01', got {results.get('q4_answer')!r}")

    # Q5: Write JSON file
    print("Q5  - Write JSON to a file")
    if results.get("q5_answer") is True:
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: JSON file not written correctly")

    # Q6: Write CSV
    print("Q6  - Write a CSV file")
    if results.get("q6_answer") is True:
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: CSV file not written correctly")

    # Q7: Handle missing file
    print("Q7  - Handle a missing file")
    if results.get("q7_answer") == "not_found":
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: Expected 'not_found', got {results.get('q7_answer')!r}")

    # Q8: Custom exception
    print("Q8  - Custom exception")
    if results.get("q8_answer") == "Invalid port: 99999":
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: Expected 'Invalid port: 99999', got {results.get('q8_answer')!r}")

    # Q9: try/except/else/finally
    print("Q9  - try/except/else/finally")
    q9 = results.get("q9_answer")
    if q9 == (42, -1, True):
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: Expected (42, -1, True), got {q9!r}")

    # Q10: Logging to file
    print("Q10 - Logging to a file")
    if results.get("q10_answer") is True:
        print("     PASS")
        score += 1
    else:
        print(f"     FAIL: quiz.log should contain INFO and ERROR messages")

    # Final score
    print()
    print("=" * 50)
    print(f"QUIZ SCORE: {score}/{total}")
    print("=" * 50)
    if score == total:
        print("PERFECT SCORE! You have mastered Week 5!")
        print("You are ready to move on to Week 6!")
    elif score >= 8:
        print("Great work! Review the questions you missed.")
    elif score >= 5:
        print("Decent effort. Review the cheat sheet and try again.")
    else:
        print("Review this week's lessons before moving on.")

    # Cleanup
    for f in ["quiz_output.txt", "quiz_data.csv", "quiz_config.json",
              "quiz_append.txt", "quiz.log"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
