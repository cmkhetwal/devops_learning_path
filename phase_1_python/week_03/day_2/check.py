"""
Week 3, Day 2: Auto-checker for List Methods exercise.
Run: python3 check.py
"""

import subprocess
import sys

def run_check():
    code = open("exercise.py").read()

    student_vars = {}
    try:
        exec(code, student_vars)
    except Exception as e:
        print(f"ERROR: Your code raised an exception: {e}")
        print("Fix the error and try again.\n")
        return

    score = 0
    total = 5

    # TASK 1
    print("=" * 50)
    print("TASK 1: Build a server fleet with append and insert")
    # After tasks 1 and 2, fleet is modified. Check after task 2.
    if "fleet" not in student_vars:
        print("  FAIL - Variable 'fleet' not found.")
    elif not isinstance(student_vars["fleet"], list):
        print("  FAIL - 'fleet' is not a list.")
    else:
        # After task 2, fleet should be ["load-balancer", "web-01", "web-02"]
        # But task 1 alone should produce ["load-balancer", "web-01", "web-02", "db-01", "cache-01"]
        # Since task 2 modifies it, we check that load-balancer is first and web-01 is second
        f = student_vars["fleet"]
        if len(f) >= 2 and f[0] == "load-balancer" and f[1] == "web-01":
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL - fleet should start with ['load-balancer', 'web-01', ...]")
            print(f"         Got: {f}")

    # TASK 2
    print("\nTASK 2: Remove servers from the fleet")
    t2_pass = True
    expected_fleet = ["load-balancer", "web-01", "web-02"]
    if "fleet" not in student_vars:
        print("  FAIL - Variable 'fleet' not found.")
        t2_pass = False
    elif student_vars["fleet"] != expected_fleet:
        print(f"  FAIL - fleet should be {expected_fleet}")
        print(f"         Got: {student_vars['fleet']}")
        t2_pass = False
    if "decommissioned" not in student_vars:
        print("  FAIL - Variable 'decommissioned' not found.")
        t2_pass = False
    elif student_vars["decommissioned"] != "db-01":
        print(f"  FAIL - decommissioned should be 'db-01', got '{student_vars['decommissioned']}'")
        t2_pass = False
    if t2_pass:
        print("  PASS")
        score += 1

    # TASK 3
    print("\nTASK 3: Sort a priority list")
    t3_pass = True
    if "priorities" not in student_vars:
        print("  FAIL - Variable 'priorities' not found.")
        t3_pass = False
    elif student_vars["priorities"] != [1, 2, 3, 4, 5]:
        print(f"  FAIL - priorities should be [1, 2, 3, 4, 5] after sorting")
        print(f"         Got: {student_vars['priorities']}")
        t3_pass = False
    if "top_priority" not in student_vars:
        print("  FAIL - Variable 'top_priority' not found.")
        t3_pass = False
    elif student_vars["top_priority"] != 1:
        print(f"  FAIL - top_priority should be 1, got {student_vars['top_priority']}")
        t3_pass = False
    if t3_pass:
        print("  PASS")
        score += 1

    # TASK 4
    print("\nTASK 4: Slice a deployment list")
    t4_pass = True
    if "first_batch" not in student_vars:
        print("  FAIL - Variable 'first_batch' not found.")
        t4_pass = False
    elif student_vars["first_batch"] != ["app-01", "app-02", "app-03"]:
        print(f"  FAIL - first_batch should be ['app-01', 'app-02', 'app-03']")
        print(f"         Got: {student_vars['first_batch']}")
        t4_pass = False
    if "second_batch" not in student_vars:
        print("  FAIL - Variable 'second_batch' not found.")
        t4_pass = False
    elif student_vars["second_batch"] != ["app-04", "app-05", "app-06"]:
        print(f"  FAIL - second_batch should be ['app-04', 'app-05', 'app-06']")
        print(f"         Got: {student_vars['second_batch']}")
        t4_pass = False
    if "rollback_order" not in student_vars:
        print("  FAIL - Variable 'rollback_order' not found.")
        t4_pass = False
    elif student_vars["rollback_order"] != ["app-06", "app-05", "app-04", "app-03", "app-02", "app-01"]:
        print(f"  FAIL - rollback_order should be deploy_targets reversed")
        print(f"         Got: {student_vars['rollback_order']}")
        t4_pass = False
    if t4_pass:
        print("  PASS")
        score += 1

    # TASK 5
    print("\nTASK 5: List comprehension")
    t5_pass = True
    expected_tagged = ["web-01-prod", "web-02-prod", "api-01-prod", "api-02-prod", "db-01-prod"]
    expected_api = ["api-01", "api-02"]
    if "tagged_servers" not in student_vars:
        print("  FAIL - Variable 'tagged_servers' not found.")
        t5_pass = False
    elif student_vars["tagged_servers"] != expected_tagged:
        print(f"  FAIL - tagged_servers expected {expected_tagged}")
        print(f"         Got: {student_vars['tagged_servers']}")
        t5_pass = False
    if "api_servers" not in student_vars:
        print("  FAIL - Variable 'api_servers' not found.")
        t5_pass = False
    elif student_vars["api_servers"] != expected_api:
        print(f"  FAIL - api_servers expected {expected_api}")
        print(f"         Got: {student_vars['api_servers']}")
        t5_pass = False
    if t5_pass:
        print("  PASS")
        score += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You're a list methods master!")
    elif score >= 3:
        print("Good progress! Review the tasks you missed.")
    else:
        print("Keep practicing! Re-read lesson.md and try again.")
    print("=" * 50)

if __name__ == "__main__":
    run_check()
