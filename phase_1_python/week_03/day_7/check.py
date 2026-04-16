"""
Week 3, Day 7: Auto-checker for Quiz Day.
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
    total = 10

    # Q1
    print("=" * 50)
    print("Q1: Create a list and access elements")
    q1 = True
    if "regions" not in student_vars or student_vars["regions"] != ["us-east-1", "us-west-2", "eu-west-1"]:
        print("  FAIL - regions should be ['us-east-1', 'us-west-2', 'eu-west-1']")
        q1 = False
    if "first_region" not in student_vars or student_vars["first_region"] != "us-east-1":
        print("  FAIL - first_region should be 'us-east-1'")
        q1 = False
    if "last_region" not in student_vars or student_vars["last_region"] != "eu-west-1":
        print("  FAIL - last_region should be 'eu-west-1'")
        q1 = False
    if q1:
        print("  PASS")
        score += 1

    # Q2
    print("\nQ2: List methods -- append, remove, sort")
    if "ports" not in student_vars:
        print("  FAIL - Variable 'ports' not found.")
    elif student_vars["ports"] == [22, 80, 443, 3306]:
        print("  PASS")
        score += 1
    else:
        print(f"  FAIL - ports should be [22, 80, 443, 3306], got {student_vars['ports']}")

    # Q3
    print("\nQ3: Slicing")
    q3 = True
    if "batch" not in student_vars or student_vars["batch"] != ["srv-01", "srv-02", "srv-03"]:
        print(f"  FAIL - batch should be ['srv-01', 'srv-02', 'srv-03'], got {student_vars.get('batch')}")
        q3 = False
    if "remaining" not in student_vars or student_vars["remaining"] != ["srv-04", "srv-05"]:
        print(f"  FAIL - remaining should be ['srv-04', 'srv-05'], got {student_vars.get('remaining')}")
        q3 = False
    if q3:
        print("  PASS")
        score += 1

    # Q4
    print("\nQ4: Tuple unpacking")
    q4 = True
    if "connection" not in student_vars or not isinstance(student_vars["connection"], tuple):
        print("  FAIL - 'connection' should be a tuple.")
        q4 = False
    elif student_vars["connection"] != ("db.example.com", 5432, "appdb"):
        print(f"  FAIL - connection expected ('db.example.com', 5432, 'appdb')")
        q4 = False
    if "host" not in student_vars or student_vars["host"] != "db.example.com":
        print("  FAIL - host should be 'db.example.com'")
        q4 = False
    if "port" not in student_vars or student_vars["port"] != 5432:
        print("  FAIL - port should be 5432")
        q4 = False
    if "database" not in student_vars or student_vars["database"] != "appdb":
        print("  FAIL - database should be 'appdb'")
        q4 = False
    if q4:
        print("  PASS")
        score += 1

    # Q5
    print("\nQ5: Set -- unique values and operations")
    q5 = True
    exp_morning = {"10.0.0.1", "10.0.0.2", "10.0.0.3"}
    exp_evening = {"10.0.0.2", "10.0.0.3", "10.0.0.4"}
    if "morning_set" not in student_vars or student_vars["morning_set"] != exp_morning:
        print(f"  FAIL - morning_set expected {exp_morning}")
        q5 = False
    if "evening_set" not in student_vars or student_vars["evening_set"] != exp_evening:
        print(f"  FAIL - evening_set expected {exp_evening}")
        q5 = False
    if "all_day_ips" not in student_vars or student_vars["all_day_ips"] != exp_morning | exp_evening:
        print("  FAIL - all_day_ips should be the union of morning and evening sets")
        q5 = False
    if "always_on" not in student_vars or student_vars["always_on"] != exp_morning & exp_evening:
        print("  FAIL - always_on should be the intersection of morning and evening sets")
        q5 = False
    if q5:
        print("  PASS")
        score += 1

    # Q6
    print("\nQ6: Dictionary -- create and access")
    q6 = True
    if "container" not in student_vars or not isinstance(student_vars["container"], dict):
        print("  FAIL - 'container' should be a dict.")
        q6 = False
    else:
        c = student_vars["container"]
        if c.get("image") != "nginx:latest" or c.get("port") != 80 or c.get("status") != "running":
            print("  FAIL - container should have image='nginx:latest', port=80, status='running'")
            q6 = False
    if "image_name" not in student_vars or student_vars["image_name"] != "nginx:latest":
        print("  FAIL - image_name should be 'nginx:latest'")
        q6 = False
    if "restart_policy" not in student_vars or student_vars["restart_policy"] != "always":
        print("  FAIL - restart_policy should be 'always'")
        q6 = False
    if q6:
        print("  PASS")
        score += 1

    # Q7
    print("\nQ7: Dictionary -- keys, values, loop")
    q7 = True
    exp_names = ["ssh", "http", "https", "mysql"]
    exp_ports = [22, 80, 443, 3306]
    if "service_names" not in student_vars or sorted(student_vars["service_names"]) != sorted(exp_names):
        print(f"  FAIL - service_names expected {exp_names}")
        q7 = False
    if "port_numbers" not in student_vars or sorted(student_vars["port_numbers"]) != sorted(exp_ports):
        print(f"  FAIL - port_numbers expected {exp_ports}")
        q7 = False
    if "formatted" not in student_vars:
        print("  FAIL - Variable 'formatted' not found.")
        q7 = False
    elif not isinstance(student_vars["formatted"], list):
        print("  FAIL - formatted should be a list.")
        q7 = False
    else:
        exp_formatted = sorted(["ssh:22", "http:80", "https:443", "mysql:3306"])
        got_formatted = sorted(student_vars["formatted"])
        if got_formatted != exp_formatted:
            print(f"  FAIL - formatted expected items like 'ssh:22', got {student_vars['formatted']}")
            q7 = False
    if q7:
        print("  PASS")
        score += 1

    # Q8
    print("\nQ8: Nested dict access")
    q8 = True
    if "pod_name" not in student_vars or student_vars["pod_name"] != "nginx-pod":
        print("  FAIL - pod_name should be 'nginx-pod'")
        q8 = False
    if "pod_namespace" not in student_vars or student_vars["pod_namespace"] != "production":
        print("  FAIL - pod_namespace should be 'production'")
        q8 = False
    if "pod_app_label" not in student_vars or student_vars["pod_app_label"] != "nginx":
        print("  FAIL - pod_app_label should be 'nginx'")
        q8 = False
    if "pod_phase" not in student_vars or student_vars["pod_phase"] != "Running":
        print("  FAIL - pod_phase should be 'Running'")
        q8 = False
    if q8:
        print("  PASS")
        score += 1

    # Q9
    print("\nQ9: List of dicts -- filter")
    q9 = True
    if "running_ids" not in student_vars or student_vars["running_ids"] != ["i-001", "i-003", "i-005"]:
        print(f"  FAIL - running_ids should be ['i-001', 'i-003', 'i-005']")
        print(f"         Got: {student_vars.get('running_ids')}")
        q9 = False
    if "micro_count" not in student_vars or student_vars["micro_count"] != 3:
        print(f"  FAIL - micro_count should be 3, got {student_vars.get('micro_count')}")
        q9 = False
    if q9:
        print("  PASS")
        score += 1

    # Q10
    print("\nQ10: Build a summary from nested data")
    q10 = True
    if "deploy_summary" not in student_vars:
        print("  FAIL - Variable 'deploy_summary' not found.")
        q10 = False
    elif not isinstance(student_vars["deploy_summary"], dict):
        print("  FAIL - deploy_summary should be a dict.")
        q10 = False
    else:
        ds = student_vars["deploy_summary"]
        if ds.get("total") != 5:
            print(f"  FAIL - deploy_summary['total'] should be 5, got {ds.get('total')}")
            q10 = False
        if ds.get("success") != 4:
            print(f"  FAIL - deploy_summary['success'] should be 4, got {ds.get('success')}")
            q10 = False
        if ds.get("failed") != 1:
            print(f"  FAIL - deploy_summary['failed'] should be 1, got {ds.get('failed')}")
            q10 = False
        expected_apps = {"frontend", "backend", "worker"}
        if ds.get("apps") != expected_apps:
            print(f"  FAIL - deploy_summary['apps'] should be {expected_apps}")
            print(f"         Got: {ds.get('apps')}")
            q10 = False
    if q10:
        print("  PASS")
        score += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"QUIZ SCORE: {score}/{total}")
    if score == total:
        print("PERFECT SCORE! You've mastered Week 3: Data Structures!")
        print("You're ready for Week 4!")
    elif score >= 8:
        print("Excellent! Just a couple to review.")
    elif score >= 6:
        print("Good work! Review the ones you missed before moving on.")
    elif score >= 4:
        print("Decent start. Re-read the cheat sheet and try again.")
    else:
        print("Keep studying! Review the lessons from this week.")
    print("=" * 50)

if __name__ == "__main__":
    run_check()
