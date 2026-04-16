"""
Week 3, Day 4: Auto-checker for Dictionaries exercise.
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
    print("TASK 1: Create a server config dictionary")
    if "server" not in student_vars:
        print("  FAIL - Variable 'server' not found.")
    elif not isinstance(student_vars["server"], dict):
        print("  FAIL - 'server' should be a dictionary.")
    else:
        s = student_vars["server"]
        # After task 2, server is modified, so check what matters
        if s.get("hostname") == "web-01" and s.get("port") == 80:
            print("  PASS")
            score += 1
        else:
            print("  FAIL - server should have hostname='web-01' and port=80")
            print(f"         Got: {s}")

    # TASK 2
    print("\nTASK 2: Access and update values")
    t2_pass = True
    if "server_ip" not in student_vars or student_vars["server_ip"] != "10.0.0.5":
        print("  FAIL - server_ip should be '10.0.0.5'")
        t2_pass = False
    s = student_vars.get("server", {})
    if s.get("status") != "maintenance":
        print("  FAIL - server['status'] should be 'maintenance'")
        t2_pass = False
    if s.get("region") != "us-east-1":
        print("  FAIL - server['region'] should be 'us-east-1'")
        t2_pass = False
    if "server_region" not in student_vars or student_vars["server_region"] != "us-east-1":
        print("  FAIL - server_region should be 'us-east-1'")
        t2_pass = False
    if t2_pass:
        print("  PASS")
        score += 1

    # TASK 3
    print("\nTASK 3: Use dictionary methods")
    t3_pass = True
    expected_keys = ["id", "type", "state", "az"]
    expected_values = ["i-0abc123", "t3.medium", "running", "us-east-1a"]
    if "instance_keys" not in student_vars:
        print("  FAIL - Variable 'instance_keys' not found.")
        t3_pass = False
    elif not isinstance(student_vars["instance_keys"], list):
        print("  FAIL - instance_keys should be a list.")
        t3_pass = False
    elif sorted(student_vars["instance_keys"]) != sorted(expected_keys):
        print(f"  FAIL - instance_keys expected {expected_keys}")
        print(f"         Got: {student_vars['instance_keys']}")
        t3_pass = False
    if "instance_values" not in student_vars:
        print("  FAIL - Variable 'instance_values' not found.")
        t3_pass = False
    elif not isinstance(student_vars["instance_values"], list):
        print("  FAIL - instance_values should be a list.")
        t3_pass = False
    elif sorted(str(v) for v in student_vars["instance_values"]) != sorted(str(v) for v in expected_values):
        print(f"  FAIL - instance_values expected {expected_values}")
        print(f"         Got: {student_vars['instance_values']}")
        t3_pass = False
    if "key_count" not in student_vars or student_vars["key_count"] != 4:
        print("  FAIL - key_count should be 4")
        t3_pass = False
    if t3_pass:
        print("  PASS")
        score += 1

    # TASK 4
    print("\nTASK 4: Build a dictionary and look up values")
    t4_pass = True
    if "port_names" not in student_vars:
        print("  FAIL - Variable 'port_names' not found.")
        t4_pass = False
    elif not isinstance(student_vars["port_names"], dict):
        print("  FAIL - port_names should be a dict.")
        t4_pass = False
    else:
        pn = student_vars["port_names"]
        expected_pn = {22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 5432: "PostgreSQL"}
        if pn != expected_pn:
            print(f"  FAIL - port_names expected {expected_pn}")
            print(f"         Got: {pn}")
            t4_pass = False
    if "ssh_service" not in student_vars or student_vars["ssh_service"] != "SSH":
        print("  FAIL - ssh_service should be 'SSH'")
        t4_pass = False
    if "unknown_service" not in student_vars or student_vars["unknown_service"] != "Unknown":
        print("  FAIL - unknown_service should be 'Unknown'")
        t4_pass = False
    if t4_pass:
        print("  PASS")
        score += 1

    # TASK 5
    print("\nTASK 5: Nested dictionary")
    t5_pass = True
    if "cloud_instance" not in student_vars:
        print("  FAIL - Variable 'cloud_instance' not found.")
        t5_pass = False
    elif not isinstance(student_vars["cloud_instance"], dict):
        print("  FAIL - cloud_instance should be a dict.")
        t5_pass = False
    else:
        ci = student_vars["cloud_instance"]
        if ci.get("id") != "i-0abc123def":
            print("  FAIL - cloud_instance['id'] should be 'i-0abc123def'")
            t5_pass = False
        if not isinstance(ci.get("network"), dict):
            print("  FAIL - cloud_instance['network'] should be a dict")
            t5_pass = False
        elif ci["network"].get("public_ip") != "54.210.100.5":
            print("  FAIL - network.public_ip should be '54.210.100.5'")
            t5_pass = False
        if not isinstance(ci.get("tags"), dict):
            print("  FAIL - cloud_instance['tags'] should be a dict")
            t5_pass = False
        elif ci["tags"].get("Name") != "prod-api-01":
            print("  FAIL - tags.Name should be 'prod-api-01'")
            t5_pass = False
    if "public_ip" not in student_vars or student_vars["public_ip"] != "54.210.100.5":
        print("  FAIL - public_ip should be '54.210.100.5'")
        t5_pass = False
    if "instance_name" not in student_vars or student_vars["instance_name"] != "prod-api-01":
        print("  FAIL - instance_name should be 'prod-api-01'")
        t5_pass = False
    if t5_pass:
        print("  PASS")
        score += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! Dictionaries are now your superpower!")
    elif score >= 3:
        print("Good progress! Review the tasks you missed.")
    else:
        print("Keep practicing! Re-read lesson.md and try again.")
    print("=" * 50)

if __name__ == "__main__":
    run_check()
