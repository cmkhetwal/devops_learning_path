"""
Week 11, Day 2: Check - Jenkins API Client
Verifies all 6 tasks from exercise.py
"""

import subprocess
import sys

def run_test(test_code):
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    score = 0
    total = 6

    # Task 1: __init__ and __repr__
    print("Task 1: JenkinsClient.__init__() and __repr__()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import JenkinsClient

c = JenkinsClient("http://jenkins:8080/", "admin", "secret-token")
assert c.url == "http://jenkins:8080", f"URL should strip trailing slash: {c.url}"
assert c.username == "admin"
assert c.token == "secret-token"
assert c.auth == ("admin", "secret-token"), f"auth wrong: {c.auth}"
r = repr(c)
assert "JenkinsClient" in r and "admin" in r and "8080" in r, f"repr wrong: {r}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: list_jobs
    print("Task 2: list_jobs()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import JenkinsClient

c = JenkinsClient("http://jenkins:8080", "admin", "token")
jobs = c.list_jobs()
assert isinstance(jobs, list), "Must return a list"
assert len(jobs) == 5, f"Should have 5 jobs, got {len(jobs)}"

names = {j["name"]: j for j in jobs}
assert names["webapp-build"]["status"] == "SUCCESS"
assert names["api-tests"]["status"] == "FAILURE"
assert names["deploy-production"]["status"] == "RUNNING"
assert names["nightly-backup"]["status"] == "DISABLED"
assert names["webapp-build"]["last_build"] == 142
assert names["nightly-backup"]["buildable"] == False
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: get_job_details
    print("Task 3: get_job_details()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import JenkinsClient

c = JenkinsClient("http://jenkins:8080", "admin", "token")

d = c.get_job_details("webapp-build")
assert d is not None, "Should find webapp-build"
assert d["name"] == "webapp-build"
assert d["status"] == "SUCCESS"
assert d["last_build"] == 142
assert d["last_success"] == 142
assert d["last_failure"] == 139
assert d["health"] == "GOOD", f"Health should be GOOD: {d['health']}"

d2 = c.get_job_details("api-tests")
assert d2["health"] == "BAD", f"api-tests health should be BAD: {d2['health']}"

d3 = c.get_job_details("deploy-production")
assert d3["health"] == "BUILDING", f"deploy-production should be BUILDING: {d3['health']}"

d4 = c.get_job_details("nonexistent")
assert d4 is None, "Nonexistent job should return None"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: trigger_build
    print("Task 4: trigger_build()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import JenkinsClient

c = JenkinsClient("http://jenkins:8080", "admin", "token")

r = c.trigger_build("webapp-build", {"BRANCH": "main"})
assert r["status"] == "TRIGGERED", f"Should be TRIGGERED: {r['status']}"
assert r["job"] == "webapp-build"
assert r["next_build"] == 143, f"Next build should be 143: {r['next_build']}"
assert r["parameters"] == {"BRANCH": "main"}

r2 = c.trigger_build("nightly-backup")
assert r2["status"] == "FAILED", f"Disabled job should fail: {r2['status']}"

r3 = c.trigger_build("nonexistent-job")
assert r3["status"] == "FAILED", f"Nonexistent should fail: {r3['status']}"

r4 = c.trigger_build("api-tests")
assert r4["parameters"] == {}, "No params should be empty dict"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: get_build_status
    print("Task 5: get_build_status()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import JenkinsClient

c = JenkinsClient("http://jenkins:8080", "admin", "token")

s = c.get_build_status("webapp-build", 142)
assert s is not None
assert s["job"] == "webapp-build"
assert s["number"] == 142
assert s["result"] == "SUCCESS"
assert s["duration_seconds"] == 45, f"Duration should be 45s: {s['duration_seconds']}"
assert s["building"] == False

s2 = c.get_build_status("deploy-production", 23)
assert s2["result"] == "IN_PROGRESS", f"Building job should be IN_PROGRESS: {s2['result']}"
assert s2["building"] == True

s3 = c.get_build_status("webapp-build", 142)
assert s3["parameters"] == {"BRANCH": "main"}, f"Params wrong: {s3['parameters']}"

s4 = c.get_build_status("nonexistent", 1)
assert s4 is None

s5 = c.get_build_status("webapp-build", 9999)
assert s5 is None
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 6: generate_build_report
    print("Task 6: generate_build_report()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import JenkinsClient

c = JenkinsClient("http://jenkins:8080", "admin", "token")
report = c.generate_build_report()
assert isinstance(report, str), "Must return a string"
assert "Jenkins Build Report" in report
assert "webapp-build" in report
assert "api-tests" in report
assert "Summary" in report or "summary" in report.lower()
assert "Total Jobs: 5" in report or "Total Jobs:  5" in report
assert "Healthy: 2" in report or "Healthy:  2" in report
assert "Failing: 1" in report or "Failing:  1" in report
assert "Running: 1" in report or "Running:  1" in report
assert "Disabled: 1" in report or "Disabled:  1" in report
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    print(f"\n{'='*40}")
    print(f"  Score: {score}/{total}")
    if score == total:
        print("  PERFECT! Jenkins API mastered!")
    elif score >= 4:
        print("  Great work! Review failed tasks.")
    else:
        print("  Keep practicing with the lesson.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
