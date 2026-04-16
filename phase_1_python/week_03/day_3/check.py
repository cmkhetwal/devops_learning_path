"""
Week 3, Day 3: Auto-checker for Tuples & Sets exercise.
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
    print("TASK 1: Create an immutable server config (tuple)")
    t1_pass = True
    expected_config = ("db-prod.example.com", 5432, "app_database")
    if "db_config" not in student_vars:
        print("  FAIL - Variable 'db_config' not found.")
        t1_pass = False
    elif not isinstance(student_vars["db_config"], tuple):
        print("  FAIL - 'db_config' should be a tuple.")
        t1_pass = False
    elif student_vars["db_config"] != expected_config:
        print(f"  FAIL - db_config expected {expected_config}")
        print(f"         Got: {student_vars['db_config']}")
        t1_pass = False
    if "db_host" not in student_vars or student_vars["db_host"] != "db-prod.example.com":
        print("  FAIL - db_host should be 'db-prod.example.com'")
        t1_pass = False
    if "db_port" not in student_vars or student_vars["db_port"] != 5432:
        print("  FAIL - db_port should be 5432")
        t1_pass = False
    if "db_name" not in student_vars or student_vars["db_name"] != "app_database":
        print("  FAIL - db_name should be 'app_database'")
        t1_pass = False
    if t1_pass:
        print("  PASS")
        score += 1

    # TASK 2
    print("\nTASK 2: Build an IP allowlist (set)")
    t2_pass = True
    expected_allowlist = {"10.0.0.1", "10.0.0.2", "10.0.0.4"}
    if "allowlist" not in student_vars:
        print("  FAIL - Variable 'allowlist' not found.")
        t2_pass = False
    elif not isinstance(student_vars["allowlist"], set):
        print("  FAIL - 'allowlist' should be a set.")
        t2_pass = False
    elif student_vars["allowlist"] != expected_allowlist:
        print(f"  FAIL - allowlist expected {expected_allowlist}")
        print(f"         Got: {student_vars['allowlist']}")
        t2_pass = False
    if "allowlist_size" not in student_vars or student_vars["allowlist_size"] != 3:
        print("  FAIL - allowlist_size should be 3")
        t2_pass = False
    if t2_pass:
        print("  PASS")
        score += 1

    # TASK 3
    print("\nTASK 3: Find unique IPs from a connection log")
    t3_pass = True
    expected_unique = {"192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5"}
    if "unique_ips" not in student_vars:
        print("  FAIL - Variable 'unique_ips' not found.")
        t3_pass = False
    elif not isinstance(student_vars["unique_ips"], set):
        print("  FAIL - 'unique_ips' should be a set.")
        t3_pass = False
    elif student_vars["unique_ips"] != expected_unique:
        print(f"  FAIL - unique_ips expected {expected_unique}")
        print(f"         Got: {student_vars['unique_ips']}")
        t3_pass = False
    if "total_connections" not in student_vars or student_vars["total_connections"] != 12:
        print("  FAIL - total_connections should be 12")
        t3_pass = False
    if "unique_count" not in student_vars or student_vars["unique_count"] != 5:
        print("  FAIL - unique_count should be 5")
        t3_pass = False
    if t3_pass:
        print("  PASS")
        score += 1

    # TASK 4
    print("\nTASK 4: Compare server inventories using set operations")
    t4_pass = True
    stg = {"web-01", "web-02", "api-01", "db-01"}
    prod = {"web-01", "api-01", "api-02", "db-01", "cache-01"}
    if "all_servers" not in student_vars or student_vars["all_servers"] != stg | prod:
        print(f"  FAIL - all_servers expected {stg | prod}")
        print(f"         Got: {student_vars.get('all_servers', 'NOT FOUND')}")
        t4_pass = False
    if "shared_servers" not in student_vars or student_vars["shared_servers"] != stg & prod:
        print(f"  FAIL - shared_servers expected {stg & prod}")
        print(f"         Got: {student_vars.get('shared_servers', 'NOT FOUND')}")
        t4_pass = False
    if "staging_only" not in student_vars or student_vars["staging_only"] != stg - prod:
        print(f"  FAIL - staging_only expected {stg - prod}")
        print(f"         Got: {student_vars.get('staging_only', 'NOT FOUND')}")
        t4_pass = False
    if "prod_only" not in student_vars or student_vars["prod_only"] != prod - stg:
        print(f"  FAIL - prod_only expected {prod - stg}")
        print(f"         Got: {student_vars.get('prod_only', 'NOT FOUND')}")
        t4_pass = False
    if t4_pass:
        print("  PASS")
        score += 1

    # TASK 5
    print("\nTASK 5: Create a frozenset for critical ports")
    t5_pass = True
    if "critical_ports" not in student_vars:
        print("  FAIL - Variable 'critical_ports' not found.")
        t5_pass = False
    elif not isinstance(student_vars["critical_ports"], frozenset):
        print("  FAIL - 'critical_ports' should be a frozenset.")
        t5_pass = False
    elif student_vars["critical_ports"] != frozenset({22, 443, 5432}):
        print(f"  FAIL - critical_ports expected frozenset({{22, 443, 5432}})")
        print(f"         Got: {student_vars['critical_ports']}")
        t5_pass = False
    if "is_ssh_critical" not in student_vars or student_vars["is_ssh_critical"] is not True:
        print("  FAIL - is_ssh_critical should be True")
        t5_pass = False
    if "is_http_critical" not in student_vars or student_vars["is_http_critical"] is not False:
        print("  FAIL - is_http_critical should be False")
        t5_pass = False
    if t5_pass:
        print("  PASS")
        score += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! Tuples and sets are now in your toolkit!")
    elif score >= 3:
        print("Good progress! Review the tasks you missed.")
    else:
        print("Keep practicing! Re-read lesson.md and try again.")
    print("=" * 50)

if __name__ == "__main__":
    run_check()
