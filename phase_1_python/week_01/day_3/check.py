#!/usr/bin/env python3
"""Week 1, Day 3 - Auto-checker

Since Day 3 exercises use input(), this checker works in two ways:
1. Reads your code to verify you used the right functions
2. Feeds test input via stdin to check the output
"""
import subprocess
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
exercise_path = os.path.join(script_dir, "exercise.py")


def read_source():
    """Read the exercise.py source code."""
    with open(exercise_path, "r") as f:
        return f.read()


def run_with_input(test_input):
    """Run exercise.py with simulated user input."""
    try:
        result = subprocess.run(
            [sys.executable, exercise_path],
            input=test_input, capture_output=True, text=True, timeout=10
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "ERROR: Script took too long (did you forget an input() call?)"
    except Exception as e:
        return "", str(e)


def check():
    print("\n  Checking your exercise...\n")

    source = read_source()
    passed = 0
    total = 5

    # Provide test input for all 5 tasks:
    # Task 1: name = "Alice"
    # Task 2: first = "10", second = "20"
    # Task 3: server = "web-01", port = "8080"
    # Task 4: cpu = "78.5678"
    # Task 5: hostname = "prod-db-01", port = "3306", region = "us-east-1"
    test_input = "Alice\n10\n20\nweb-01\n8080\n78.5678\nprod-db-01\n3306\nus-east-1\n"

    stdout, stderr = run_with_input(test_input)

    if stderr:
        print(f"  ERROR in your code:\n  {stderr}")
        print(f"\n  Fix the error and try again!")
        return

    output = stdout

    # --- Task 1: Greet the user ---
    has_input_call = "input(" in source
    if "Hello, Alice! Welcome to DevOps." in output and has_input_call:
        print("  Task 1: PASS - Greeting with input works")
        passed += 1
    elif not has_input_call:
        print("  Task 1: FAIL - You need to use input() to ask for the name")
    elif "Hello" in output and "Alice" in output:
        print("  Task 1: FAIL - Close! Make sure it says exactly: Hello, Alice! Welcome to DevOps.")
    else:
        print('  Task 1: FAIL - Use input("Enter your name: ") and print with f-string')

    # --- Task 2: Add two numbers ---
    if "Sum: 30" in output and "int(" in source:
        print("  Task 2: PASS - Number addition works")
        passed += 1
    elif "Sum: 1020" in output:
        print("  Task 2: FAIL - You got string concatenation! Use int() to convert inputs")
    elif "Sum:" in output:
        print("  Task 2: FAIL - Expected 'Sum: 30' (10 + 20)")
    else:
        print('  Task 2: FAIL - Ask for two numbers, convert with int(), print "Sum: <result>"')

    # --- Task 3: Build a URL ---
    if "URL: http://web-01:8080" in output:
        print("  Task 3: PASS - URL built correctly")
        passed += 1
    elif "http://web-01:8080" in output:
        print("  Task 3: FAIL - Close! Print it as: URL: http://web-01:8080")
    elif "web-01" in output and "8080" in output:
        print("  Task 3: FAIL - Build the URL using f-string: http://<server>:<port>")
    else:
        print('  Task 3: FAIL - Ask for server and port, print "URL: http://<server>:<port>"')

    # --- Task 4: Format CPU usage ---
    if "CPU Usage: 78.6%" in output and "float(" in source:
        print("  Task 4: PASS - CPU formatted to 1 decimal place")
        passed += 1
    elif "78.5678" in output:
        print("  Task 4: FAIL - Use :.1f in your f-string to format to 1 decimal place")
    elif "CPU Usage:" in output:
        print("  Task 4: FAIL - Expected 'CPU Usage: 78.6%' (use :.1f formatting)")
    else:
        print('  Task 4: FAIL - Convert to float, then use f"{cpu:.1f}" to format')

    # --- Task 5: Server config prompt ---
    config_checks = [
        "=== Server Config ===",
        "Hostname: prod-db-01",
        "Port: 3306",
        "Region: us-east-1",
        "Connection: prod-db-01:3306",
    ]
    config_pass = all(check_str in output for check_str in config_checks)

    if config_pass:
        print("  Task 5: PASS - Server config prompt works perfectly")
        passed += 1
    else:
        missing = [c for c in config_checks if c not in output]
        print(f"  Task 5: FAIL - Missing or wrong lines:")
        for m in missing:
            print(f"           Expected: {m}")

    # --- Results ---
    print(f"\n  {'─' * 40}")
    print(f"  Score: {passed}/{total} tasks passed")

    if passed == total:
        print(f"  PERFECT! All tasks completed!")
        print(f"  You're ready to move on to Day 4!")
        print(f"\n  Mark your progress: python3 ../../tracker.py")
    elif passed >= 3:
        print(f"  Good job! Fix the remaining tasks and try again.")
    else:
        print(f"  Keep trying! Re-read the lesson.md for help.")


if __name__ == "__main__":
    check()
