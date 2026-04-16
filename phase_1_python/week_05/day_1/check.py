"""
Week 5, Day 1: Auto-checker
============================
Run this file to verify your exercise.py solutions.
"""

import subprocess
import sys

def run_exercise():
    """Run exercise.py and capture its namespace."""
    # We run the exercise in a subprocess to catch syntax errors cleanly
    result = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, ".")
exec(open("exercise.py").read())

# Output results for parsing
print("---RESULTS---")
print(f"total_lines={total_lines!r}")
print(f"error_lines={error_lines!r}")
print(f"log_counts={log_counts!r}")
print(f"servers={servers!r}")
print(f"first_entry={first_entry!r}")
print(f"last_entry={last_entry!r}")
"""],
        capture_output=True, text=True, timeout=10
    )
    return result

def parse_results(output):
    """Parse the results from exercise output."""
    results = {}
    for line in output.strip().split("\n"):
        if "=" in line and "---RESULTS---" not in line:
            key, value = line.split("=", 1)
            try:
                results[key] = eval(value)
            except:
                results[key] = None
    return results

def main():
    print("=" * 50)
    print("WEEK 5, DAY 1 - EXERCISE CHECKER")
    print("=" * 50)
    print()

    result = run_exercise()

    if result.returncode != 0:
        print("ERROR: exercise.py failed to run!")
        print(result.stderr)
        return

    # Find the results section
    output = result.stdout
    if "---RESULTS---" not in output:
        print("ERROR: Could not find results in output.")
        print(output)
        return

    results_section = output.split("---RESULTS---")[1]
    results = parse_results(results_section)

    score = 0
    total = 5

    # Task 1: Count lines
    print("Task 1 - Count lines in sample.log")
    if results.get("total_lines") == 15:
        print("  PASS: total_lines = 15")
        score += 1
    else:
        print(f"  FAIL: Expected 15, got {results.get('total_lines')}")

    # Task 2: Error lines
    print("\nTask 2 - Find ERROR lines")
    expected_errors = [
        "2024-01-15 08:05:33 ERROR Connection timeout on web-03",
        "2024-01-15 08:06:15 ERROR Connection timeout on web-03",
        "2024-01-15 08:15:00 ERROR Disk full on db-02",
    ]
    if results.get("error_lines") == expected_errors:
        print("  PASS: Found all 3 ERROR lines")
        score += 1
    else:
        print(f"  FAIL: Expected {expected_errors}")
        print(f"        Got {results.get('error_lines')}")

    # Task 3: Log counts
    print("\nTask 3 - Count each log level")
    expected_counts = {"INFO": 9, "WARNING": 2, "ERROR": 3, "CRITICAL": 1}
    if results.get("log_counts") == expected_counts:
        print(f"  PASS: {expected_counts}")
        score += 1
    else:
        print(f"  FAIL: Expected {expected_counts}")
        print(f"        Got {results.get('log_counts')}")

    # Task 4: Server inventory
    print("\nTask 4 - Read server inventory")
    expected_servers = ["web-01", "web-02", "web-03", "db-01", "db-02", "db-03", "cache-01", "lb-01"]
    if results.get("servers") == expected_servers:
        print(f"  PASS: Found all {len(expected_servers)} servers")
        score += 1
    else:
        print(f"  FAIL: Expected {expected_servers}")
        print(f"        Got {results.get('servers')}")

    # Task 5: First and last entries
    print("\nTask 5 - First and last log entries")
    expected_first = "2024-01-15 08:01:23 INFO Server web-01 started successfully"
    expected_last = "2024-01-15 08:20:00 INFO All systems operational"
    first_ok = results.get("first_entry") == expected_first
    last_ok = results.get("last_entry") == expected_last
    if first_ok and last_ok:
        print("  PASS: First and last entries correct")
        score += 1
    else:
        if not first_ok:
            print(f"  FAIL: first_entry expected: {expected_first!r}")
            print(f"        Got: {results.get('first_entry')!r}")
        if not last_ok:
            print(f"  FAIL: last_entry expected: {expected_last!r}")
            print(f"        Got: {results.get('last_entry')!r}")

    # Final score
    print()
    print("=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    print("=" * 50)
    if score == total:
        print("Excellent! All tasks complete. Move on to Day 2!")
    elif score >= 3:
        print("Good progress! Review the failed tasks and try again.")
    else:
        print("Keep practicing! Review the lesson and try again.")

if __name__ == "__main__":
    main()
