"""
Week 3, Day 1: Auto-checker for Lists exercise.
Run: python3 check.py
"""

import subprocess
import sys

def run_check():
    code = open("exercise.py").read()

    # We'll exec the student code and inspect variables
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
    print("TASK 1: Create a list of server hostnames")
    expected_servers = ["web-01", "web-02", "db-01", "cache-01", "monitor-01"]
    if "servers" not in student_vars:
        print("  FAIL - Variable 'servers' not found.")
    elif not isinstance(student_vars["servers"], list):
        print("  FAIL - 'servers' is not a list.")
    elif student_vars["servers"][:] != expected_servers and student_vars["servers"][:] != ["web-01", "web-02-upgraded", "db-01", "cache-01", "monitor-01"]:
        # Allow for Task 5 modification
        # Check original before task 5 by checking first element and length
        if len(student_vars["servers"]) == 5 and student_vars["servers"][0] == "web-01":
            print("  PASS")
            score += 1
        else:
            print(f"  FAIL - Expected {expected_servers}")
            print(f"         Got      {student_vars['servers']}")
    else:
        print("  PASS")
        score += 1

    # TASK 2
    print("\nTASK 2: Access specific servers by index")
    if "first_server" not in student_vars:
        print("  FAIL - Variable 'first_server' not found.")
    elif "last_server" not in student_vars:
        print("  FAIL - Variable 'last_server' not found.")
    elif student_vars["first_server"] == "web-01" and student_vars["last_server"] == "monitor-01":
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL - first_server should be 'web-01', got '{student_vars.get('first_server')}'")
        print(f"         last_server should be 'monitor-01', got '{student_vars.get('last_server')}'")

    # TASK 3
    print("\nTASK 3: Find the fleet size")
    if "fleet_size" not in student_vars:
        print("  FAIL - Variable 'fleet_size' not found.")
    elif student_vars["fleet_size"] == 5:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL - Expected 5, got {student_vars['fleet_size']}")

    # TASK 4
    print("\nTASK 4: Create a list of open ports")
    expected_ports = [22, 80, 443, 8080, 3306]
    t4_pass = True
    if "open_ports" not in student_vars:
        print("  FAIL - Variable 'open_ports' not found.")
        t4_pass = False
    elif student_vars["open_ports"] != expected_ports:
        print(f"  FAIL - open_ports expected {expected_ports}, got {student_vars['open_ports']}")
        t4_pass = False
    if "ssh_port" not in student_vars:
        print("  FAIL - Variable 'ssh_port' not found.")
        t4_pass = False
    elif student_vars["ssh_port"] != 22:
        print(f"  FAIL - ssh_port should be 22, got {student_vars['ssh_port']}")
        t4_pass = False
    if "db_port" not in student_vars:
        print("  FAIL - Variable 'db_port' not found.")
        t4_pass = False
    elif student_vars["db_port"] != 3306:
        print(f"  FAIL - db_port should be 3306, got {student_vars['db_port']}")
        t4_pass = False
    if t4_pass:
        print("  PASS")
        score += 1

    # TASK 5
    print("\nTASK 5: Update a server in the list")
    if "updated_server" not in student_vars:
        print("  FAIL - Variable 'updated_server' not found.")
    elif student_vars["updated_server"] != "web-02-upgraded":
        print(f"  FAIL - updated_server should be 'web-02-upgraded', got '{student_vars['updated_server']}'")
    elif isinstance(student_vars.get("servers"), list) and len(student_vars["servers"]) >= 2 and student_vars["servers"][1] == "web-02-upgraded":
        print("  PASS")
        score += 1
    else:
        print("  FAIL - servers[1] should be 'web-02-upgraded'")

    # Summary
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You've mastered Python lists!")
    elif score >= 3:
        print("Good progress! Review the tasks you missed.")
    else:
        print("Keep practicing! Re-read lesson.md and try again.")
    print("=" * 50)

if __name__ == "__main__":
    run_check()
