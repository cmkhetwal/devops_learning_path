"""
Week 3, Day 6: Auto-checker for Practice Day mini-projects.
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

    # MINI-PROJECT 1: Contact Book
    print("=" * 50)
    print("MINI-PROJECT 1: Contact Book")
    t1_pass = True
    if "contacts" not in student_vars:
        print("  FAIL - Variable 'contacts' not found.")
        t1_pass = False
    elif not isinstance(student_vars["contacts"], dict):
        print("  FAIL - 'contacts' should be a dictionary.")
        t1_pass = False
    else:
        c = student_vars["contacts"]
        expected = {"Alice": "alice@devops.com", "Charlie": "charlie@devops.com", "Diana": "diana@devops.com"}
        if c != expected:
            print(f"  FAIL - contacts expected {expected}")
            print(f"         Got: {c}")
            t1_pass = False
    if "alice_email" not in student_vars or student_vars["alice_email"] != "alice@devops.com":
        print("  FAIL - alice_email should be 'alice@devops.com'")
        t1_pass = False
    if "unknown_email" not in student_vars or student_vars["unknown_email"] != "not found":
        print("  FAIL - unknown_email should be 'not found'")
        t1_pass = False
    if t1_pass:
        print("  PASS")
        score += 1

    # MINI-PROJECT 2: Server Inventory Manager
    print("\nMINI-PROJECT 2: Server Inventory Manager")
    t2_pass = True
    if "server_inventory" not in student_vars:
        print("  FAIL - Variable 'server_inventory' not found.")
        t2_pass = False
    elif not isinstance(student_vars["server_inventory"], list):
        print("  FAIL - server_inventory should be a list.")
        t2_pass = False
    else:
        si = student_vars["server_inventory"]
        expected_si = [
            {"name": "web-01", "ip": "10.0.0.1", "status": "running"},
            {"name": "cache-01", "ip": "10.0.0.3", "status": "running"}
        ]
        if len(si) != 2:
            print(f"  FAIL - server_inventory should have 2 servers, got {len(si)}")
            t2_pass = False
        else:
            names = [s["name"] for s in si]
            if "web-01" not in names or "cache-01" not in names:
                print("  FAIL - server_inventory should contain web-01 and cache-01")
                t2_pass = False
            for s in si:
                if s.get("status") != "running":
                    print(f"  FAIL - All servers should have status 'running'")
                    t2_pass = False
                    break
    if "inventory_count" not in student_vars or student_vars["inventory_count"] != 2:
        print("  FAIL - inventory_count should be 2")
        t2_pass = False
    if t2_pass:
        print("  PASS")
        score += 1

    # MINI-PROJECT 3: Log Categorizer
    print("\nMINI-PROJECT 3: Log Categorizer")
    t3_pass = True
    if "categorized_logs" not in student_vars:
        print("  FAIL - Variable 'categorized_logs' not found.")
        t3_pass = False
    elif not isinstance(student_vars["categorized_logs"], dict):
        print("  FAIL - categorized_logs should be a dict.")
        t3_pass = False
    else:
        cl = student_vars["categorized_logs"]
        if len(cl.get("ERROR", [])) != 3:
            print(f"  FAIL - ERROR should have 3 entries, got {len(cl.get('ERROR', []))}")
            t3_pass = False
        if len(cl.get("WARNING", [])) != 2:
            print(f"  FAIL - WARNING should have 2 entries, got {len(cl.get('WARNING', []))}")
            t3_pass = False
        if len(cl.get("INFO", [])) != 3:
            print(f"  FAIL - INFO should have 3 entries, got {len(cl.get('INFO', []))}")
            t3_pass = False
    if "error_count" not in student_vars or student_vars["error_count"] != 3:
        print("  FAIL - error_count should be 3")
        t3_pass = False
    if "warning_count" not in student_vars or student_vars["warning_count"] != 2:
        print("  FAIL - warning_count should be 2")
        t3_pass = False
    if "info_count" not in student_vars or student_vars["info_count"] != 3:
        print("  FAIL - info_count should be 3")
        t3_pass = False
    if t3_pass:
        print("  PASS")
        score += 1

    # MINI-PROJECT 4: Unique IP Finder
    print("\nMINI-PROJECT 4: Unique IP Finder")
    t4_pass = True
    web_expected = {"192.168.1.1", "10.0.0.5", "192.168.1.2", "172.16.0.1", "192.168.1.3"}
    api_expected = {"10.0.0.5", "192.168.1.4", "172.16.0.1", "192.168.1.1", "10.0.0.8"}

    if "web_unique" not in student_vars or student_vars["web_unique"] != web_expected:
        print(f"  FAIL - web_unique expected {web_expected}")
        print(f"         Got: {student_vars.get('web_unique', 'NOT FOUND')}")
        t4_pass = False
    if "api_unique" not in student_vars or student_vars["api_unique"] != api_expected:
        print(f"  FAIL - api_unique expected {api_expected}")
        print(f"         Got: {student_vars.get('api_unique', 'NOT FOUND')}")
        t4_pass = False
    if "all_unique" not in student_vars or student_vars["all_unique"] != web_expected | api_expected:
        print("  FAIL - all_unique should be the union of web_unique and api_unique")
        t4_pass = False
    if "common_ips" not in student_vars or student_vars["common_ips"] != web_expected & api_expected:
        print("  FAIL - common_ips should be the intersection of web_unique and api_unique")
        t4_pass = False
    if "web_only" not in student_vars or student_vars["web_only"] != web_expected - api_expected:
        print("  FAIL - web_only should be web_unique - api_unique")
        t4_pass = False
    if t4_pass:
        print("  PASS")
        score += 1

    # MINI-PROJECT 5: Infrastructure Report
    print("\nMINI-PROJECT 5: Infrastructure Report")
    t5_pass = True
    if "report" not in student_vars:
        print("  FAIL - Variable 'report' not found.")
        t5_pass = False
    elif not isinstance(student_vars["report"], dict):
        print("  FAIL - report should be a dict.")
        t5_pass = False
    else:
        r = student_vars["report"]
        if r.get("total_instances") != 8:
            print(f"  FAIL - report['total_instances'] should be 8, got {r.get('total_instances')}")
            t5_pass = False
        if r.get("running") != 5:
            print(f"  FAIL - report['running'] should be 5, got {r.get('running')}")
            t5_pass = False
        if r.get("stopped") != 3:
            print(f"  FAIL - report['stopped'] should be 3, got {r.get('stopped')}")
            t5_pass = False
        expected_by_region = {"us-east-1": 3, "us-west-2": 2, "eu-west-1": 3}
        if r.get("by_region") != expected_by_region:
            print(f"  FAIL - report['by_region'] should be {expected_by_region}")
            print(f"         Got: {r.get('by_region')}")
            t5_pass = False
    if t5_pass:
        print("  PASS")
        score += 1

    # Summary
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} mini-projects passed")
    if score == total:
        print("PERFECT! You crushed all 5 mini-projects!")
    elif score >= 3:
        print("Good progress! Review the projects you missed.")
    else:
        print("Keep practicing! Re-read lesson.md for hints.")
    print("=" * 50)

if __name__ == "__main__":
    run_check()
