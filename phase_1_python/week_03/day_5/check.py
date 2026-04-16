"""
Week 3, Day 5: Auto-checker for Nested Structures exercise.
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
    print("TASK 1: Access data in a list of dicts")
    t1_pass = True
    if "first_hostname" not in student_vars or student_vars["first_hostname"] != "web-01":
        print("  FAIL - first_hostname should be 'web-01'")
        t1_pass = False
    if "db_ip" not in student_vars or student_vars["db_ip"] != "10.0.0.3":
        print("  FAIL - db_ip should be '10.0.0.3'")
        t1_pass = False
    if "total_servers" not in student_vars or student_vars["total_servers"] != 5:
        print("  FAIL - total_servers should be 5")
        t1_pass = False
    if t1_pass:
        print("  PASS")
        score += 1

    # TASK 2
    print("\nTASK 2: Filter the inventory")
    t2_pass = True
    if "running_servers" not in student_vars:
        print("  FAIL - Variable 'running_servers' not found.")
        t2_pass = False
    elif not isinstance(student_vars["running_servers"], list):
        print("  FAIL - running_servers should be a list.")
        t2_pass = False
    else:
        rs = student_vars["running_servers"]
        if len(rs) != 4:
            print(f"  FAIL - running_servers should have 4 items, got {len(rs)}")
            t2_pass = False
        else:
            for s in rs:
                if not isinstance(s, dict) or s.get("status") != "running":
                    print("  FAIL - running_servers should only contain dicts with status='running'")
                    t2_pass = False
                    break
    if "running_count" not in student_vars or student_vars["running_count"] != 4:
        print("  FAIL - running_count should be 4")
        t2_pass = False
    if t2_pass:
        print("  PASS")
        score += 1

    # TASK 3
    print("\nTASK 3: Extract data from nested structures")
    t3_pass = True
    expected_hostnames = ["web-01", "web-02", "db-01", "cache-01", "monitor-01"]
    expected_high_cpu = ["web-02", "monitor-01"]
    if "all_hostnames" not in student_vars:
        print("  FAIL - Variable 'all_hostnames' not found.")
        t3_pass = False
    elif student_vars["all_hostnames"] != expected_hostnames:
        print(f"  FAIL - all_hostnames expected {expected_hostnames}")
        print(f"         Got: {student_vars['all_hostnames']}")
        t3_pass = False
    if "high_cpu_servers" not in student_vars:
        print("  FAIL - Variable 'high_cpu_servers' not found.")
        t3_pass = False
    elif student_vars["high_cpu_servers"] != expected_high_cpu:
        print(f"  FAIL - high_cpu_servers expected {expected_high_cpu}")
        print(f"         Got: {student_vars['high_cpu_servers']}")
        t3_pass = False
    if t3_pass:
        print("  PASS")
        score += 1

    # TASK 4
    print("\nTASK 4: Work with a dict of lists")
    t4_pass = True
    if "server_groups" not in student_vars:
        print("  FAIL - Variable 'server_groups' not found.")
        t4_pass = False
    elif not isinstance(student_vars["server_groups"], dict):
        print("  FAIL - server_groups should be a dict.")
        t4_pass = False
    else:
        sg = student_vars["server_groups"]
        expected_sg = {
            "web": ["web-01", "web-02"],
            "database": ["db-01"],
            "cache": ["cache-01"],
            "monitor": ["monitor-01"]
        }
        if sg != expected_sg:
            print(f"  FAIL - server_groups does not match expected structure")
            print(f"         Got: {sg}")
            t4_pass = False
    if "web_servers" not in student_vars or student_vars["web_servers"] != ["web-01", "web-02"]:
        print("  FAIL - web_servers should be ['web-01', 'web-02']")
        t4_pass = False
    if "first_web" not in student_vars or student_vars["first_web"] != "web-01":
        print("  FAIL - first_web should be 'web-01'")
        t4_pass = False
    if "group_names" not in student_vars:
        print("  FAIL - Variable 'group_names' not found.")
        t4_pass = False
    elif not isinstance(student_vars["group_names"], list):
        print("  FAIL - group_names should be a list.")
        t4_pass = False
    elif sorted(student_vars["group_names"]) != sorted(["web", "database", "cache", "monitor"]):
        print(f"  FAIL - group_names should contain ['web', 'database', 'cache', 'monitor']")
        print(f"         Got: {student_vars['group_names']}")
        t4_pass = False
    if t4_pass:
        print("  PASS")
        score += 1

    # TASK 5
    print("\nTASK 5: Navigate deeply nested data")
    t5_pass = True
    if "cloud_region" not in student_vars or student_vars["cloud_region"] != "us-east-1":
        print("  FAIL - cloud_region should be 'us-east-1'")
        t5_pass = False
    if "first_instance_id" not in student_vars or student_vars["first_instance_id"] != "i-001":
        print("  FAIL - first_instance_id should be 'i-001'")
        t5_pass = False
    if "second_instance_name" not in student_vars or student_vars["second_instance_name"] != "dev-api":
        print("  FAIL - second_instance_name should be 'dev-api'")
        t5_pass = False
    if "prod_instances" not in student_vars:
        print("  FAIL - Variable 'prod_instances' not found.")
        t5_pass = False
    elif not isinstance(student_vars["prod_instances"], list):
        print("  FAIL - prod_instances should be a list.")
        t5_pass = False
    elif len(student_vars["prod_instances"]) != 2:
        print(f"  FAIL - prod_instances should have 2 items, got {len(student_vars['prod_instances'])}")
        t5_pass = False
    else:
        ids = [inst["id"] for inst in student_vars["prod_instances"]]
        if sorted(ids) != ["i-001", "i-003"]:
            print(f"  FAIL - prod_instances should contain i-001 and i-003")
            print(f"         Got ids: {ids}")
            t5_pass = False
    if t5_pass:
        print("  PASS")
        score += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You can navigate any nested data structure!")
    elif score >= 3:
        print("Good progress! Review the tasks you missed.")
    else:
        print("Keep practicing! Re-read lesson.md and try again.")
    print("=" * 50)

if __name__ == "__main__":
    run_check()
