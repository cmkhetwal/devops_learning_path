"""
Week 5, Day 5: Auto-checker
============================
Run this file to verify your exercise.py solutions.
"""

import subprocess
import sys
import os

def count_level_in_file(filepath, level):
    """Count how many lines contain a log level keyword."""
    count = 0
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            for line in f:
                if level in line:
                    count += 1
    return count

def count_lines(filepath):
    """Count total non-empty lines in a file."""
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r") as f:
        return sum(1 for line in f if line.strip())

def main():
    print("=" * 50)
    print("WEEK 5, DAY 5 - EXERCISE CHECKER")
    print("=" * 50)
    print()

    # Clean up first
    for f in ["deploy.log", "health.log", "app_debug.log", "app_info.log", "deploy_results.log"]:
        if os.path.exists(f):
            os.remove(f)

    # Run exercise.py
    result = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, ".")
exec(open("exercise.py").read())

print("---RESULTS---")
print(f"deploy_outcomes={deploy_outcomes!r}")
print(f"deploy_log_counts={deploy_log_counts!r}")
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
    total = 5

    # Task 1: Basic logging to file
    print("Task 1 - Basic logging to deploy.log")
    if os.path.exists("deploy.log"):
        info_count = count_level_in_file("deploy.log", "INFO")
        warn_count = count_level_in_file("deploy.log", "WARNING")
        error_count = count_level_in_file("deploy.log", "ERROR")
        debug_count = count_level_in_file("deploy.log", "DEBUG")
        total_lines = count_lines("deploy.log")

        if total_lines >= 7 and info_count >= 3 and warn_count >= 1 and error_count >= 1 and debug_count >= 1:
            print(f"  PASS: deploy.log has {total_lines} lines with correct levels")
            score += 1
        else:
            print(f"  FAIL: Expected 7+ lines with DEBUG(1+), INFO(3+), WARNING(1+), ERROR(1+)")
            print(f"        Got {total_lines} lines: DEBUG={debug_count}, INFO={info_count}, WARNING={warn_count}, ERROR={error_count}")
    else:
        print("  FAIL: deploy.log not found")

    # Task 2: Custom logger with file handler
    print("\nTask 2 - Health check logger")
    if os.path.exists("health.log"):
        total_lines = count_lines("health.log")
        debug_count = count_level_in_file("health.log", "DEBUG")
        info_count = count_level_in_file("health.log", "INFO")
        warn_count = count_level_in_file("health.log", "WARNING")
        crit_count = count_level_in_file("health.log", "CRITICAL")

        # DEBUG messages should NOT be in file (handler level is INFO)
        if total_lines >= 4 and debug_count == 0 and info_count >= 2 and crit_count >= 1:
            print(f"  PASS: health.log has {total_lines} lines, DEBUG correctly filtered")
            score += 1
        else:
            print(f"  FAIL: Expected 4+ lines with no DEBUG lines (handler level=INFO)")
            print(f"        Got {total_lines} lines: DEBUG={debug_count}, INFO={info_count}, WARNING={warn_count}, CRITICAL={crit_count}")
    else:
        print("  FAIL: health.log not found")

    # Task 3: Multiple handlers
    print("\nTask 3 - Multiple handlers (debug + info logs)")
    t3_pass = True
    if os.path.exists("app_debug.log") and os.path.exists("app_info.log"):
        debug_total = count_lines("app_debug.log")
        info_total = count_lines("app_info.log")
        debug_debugs = count_level_in_file("app_debug.log", "DEBUG")
        info_debugs = count_level_in_file("app_info.log", "DEBUG")

        if debug_total < 7:
            print(f"  FAIL: app_debug.log should have 7+ lines (all levels), got {debug_total}")
            t3_pass = False
        if info_total >= debug_total:
            print(f"  FAIL: app_info.log ({info_total} lines) should have fewer lines than app_debug.log ({debug_total} lines)")
            t3_pass = False
        if debug_debugs == 0:
            print(f"  FAIL: app_debug.log should contain DEBUG messages")
            t3_pass = False
        if info_debugs > 0:
            print(f"  FAIL: app_info.log should NOT contain DEBUG messages (handler level=INFO)")
            t3_pass = False
        if t3_pass:
            print(f"  PASS: app_debug.log has {debug_total} lines, app_info.log has {info_total} lines")
            score += 1
    else:
        print(f"  FAIL: app_debug.log exists={os.path.exists('app_debug.log')}, app_info.log exists={os.path.exists('app_info.log')}")

    # Task 4: Deployment simulation
    print("\nTask 4 - Deployment simulation")
    outcomes = results.get("deploy_outcomes")
    expected_outcomes = [True, True, False, True]
    if outcomes == expected_outcomes:
        if os.path.exists("deploy_results.log"):
            error_count = count_level_in_file("deploy_results.log", "ERROR")
            if error_count >= 1:
                print("  PASS: Deploy outcomes correct and error logged for web-03")
                score += 1
            else:
                print("  FAIL: deploy_results.log should contain at least one ERROR")
        else:
            print("  FAIL: deploy_results.log not found")
    else:
        print(f"  FAIL: Expected outcomes {expected_outcomes}, got {outcomes}")

    # Task 5: Log level counter
    print("\nTask 5 - Count log levels")
    dlc = results.get("deploy_log_counts")
    if isinstance(dlc, dict):
        expected_keys = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if set(dlc.keys()) == expected_keys:
            if dlc["DEBUG"] >= 1 and dlc["INFO"] >= 3 and dlc["WARNING"] >= 1 and dlc["ERROR"] >= 1:
                print(f"  PASS: Log counts: {dlc}")
                score += 1
            else:
                print(f"  FAIL: Counts seem off: {dlc}")
                print(f"        Expected at least DEBUG=1, INFO=3, WARNING=1, ERROR=1")
        else:
            print(f"  FAIL: Expected keys {expected_keys}, got {set(dlc.keys())}")
    else:
        print(f"  FAIL: Expected a dict, got {type(dlc)}: {dlc}")

    # Final score
    print()
    print("=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    print("=" * 50)
    if score == total:
        print("Excellent! All tasks complete. Move on to Day 6!")
    elif score >= 3:
        print("Good progress! Review the failed tasks and try again.")
    else:
        print("Keep practicing! Review the lesson and try again.")

    # Cleanup
    for f in ["deploy.log", "health.log", "app_debug.log", "app_info.log", "deploy_results.log"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
