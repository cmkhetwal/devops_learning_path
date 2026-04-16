"""
Week 11, Day 3: Check - GitHub Actions Workflow Generator
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

    # Task 1: generate_basic_ci
    print("Task 1: generate_basic_ci()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_basic_ci

r = generate_basic_ci("my-webapp", "3.12")
assert isinstance(r, dict), "Must return a dict"
assert r["name"] == "CI - my-webapp", f"Name wrong: {r['name']}"
assert r["on"]["push"]["branches"] == ["main", "develop"]
assert r["on"]["pull_request"]["branches"] == ["main"]
job = r["jobs"]["test"]
assert job["runs-on"] == "ubuntu-latest"
steps = job["steps"]
assert len(steps) == 5, f"Should have 5 steps, got {len(steps)}"
assert steps[0]["uses"] == "actions/checkout@v4"
assert steps[1]["with"]["python-version"] == "3.12"
assert "flake8" in steps[3]["run"]
assert "pytest" in steps[4]["run"]

# Default python version
r2 = generate_basic_ci("app2")
assert r2["jobs"]["test"]["steps"][1]["with"]["python-version"] == "3.11"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: generate_python_test
    print("Task 2: generate_python_test()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_python_test

r = generate_python_test("api", ["3.10", "3.11"], ["ubuntu-latest", "macos-latest"])
assert r["name"] == "Tests - api"
job = r["jobs"]["test"]
assert job["runs-on"] == "${{ matrix.os }}"
m = job["strategy"]["matrix"]
assert m["python-version"] == ["3.10", "3.11"]
assert m["os"] == ["ubuntu-latest", "macos-latest"]
assert job["strategy"]["fail-fast"] == False

# Default os_list
r2 = generate_python_test("app", ["3.11"])
m2 = r2["jobs"]["test"]["strategy"]["matrix"]
assert m2["os"] == ["ubuntu-latest"], f"Default os wrong: {m2['os']}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: generate_docker_build
    print("Task 3: generate_docker_build()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_docker_build

r = generate_docker_build("myorg/myapp", "Dockerfile.prod", "docker.io")
assert r["name"] == "Docker Build - myorg/myapp"
assert r["env"]["REGISTRY"] == "docker.io"
assert r["env"]["IMAGE_NAME"] == "myorg/myapp"
assert r["on"]["push"]["tags"] == ["v*"]
job = r["jobs"]["build-and-push"]
assert job["permissions"]["packages"] == "write"
steps = job["steps"]
assert any("login" in s.get("name", "").lower() for s in steps)
assert any("build" in s.get("name", "").lower() for s in steps)

# Find the build step and check dockerfile
build_step = [s for s in steps if "build" in s.get("name", "").lower() and "push" in s.get("name", "").lower()][0]
assert build_step["with"]["file"] == "Dockerfile.prod"
assert build_step["with"]["push"] == True

# Defaults
r2 = generate_docker_build("app")
assert r2["env"]["REGISTRY"] == "ghcr.io"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: generate_deploy_workflow
    print("Task 4: generate_deploy_workflow()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_deploy_workflow

envs = [
    {"name": "staging", "url": "https://staging.example.com", "auto": True},
    {"name": "production", "url": "https://example.com", "auto": False},
]
r = generate_deploy_workflow("my-app", envs)
assert r["name"] == "Deploy - my-app"
jobs = r["jobs"]
assert "build" in jobs
assert "deploy-staging" in jobs, f"Jobs: {list(jobs.keys())}"
assert "deploy-production" in jobs, f"Jobs: {list(jobs.keys())}"

# Check chaining
staging = jobs["deploy-staging"]
assert "build" in str(staging.get("needs", "")), f"Staging should need build: {staging.get('needs')}"
prod = jobs["deploy-production"]
assert "staging" in str(prod.get("needs", "")), f"Prod should need staging: {prod.get('needs')}"

# Check environment
assert staging["environment"]["name"] == "staging"
assert staging["environment"]["url"] == "https://staging.example.com"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: generate_scheduled_job
    print("Task 5: generate_scheduled_job()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_scheduled_job

r = generate_scheduled_job("cleanup", "0 2 * * *", "cleanup.py", "3.12")
assert r["name"] == "Scheduled - cleanup"
assert r["on"]["schedule"] == [{"cron": "0 2 * * *"}]
assert "workflow_dispatch" in r["on"]
job = r["jobs"]["run"]
steps = job["steps"]
assert steps[1]["with"]["python-version"] == "3.12"
assert "cleanup.py" in steps[-1]["run"]
assert "cleanup" in steps[-1]["name"].lower() or "Run" in steps[-1]["name"]
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 6: workflow_to_yaml
    print("Task 6: workflow_to_yaml()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_basic_ci, workflow_to_yaml

ci = generate_basic_ci("test-app")
result = workflow_to_yaml(ci)
assert isinstance(result, str), "Must return a string"
assert len(result) > 50, "Output too short"
assert "name" in result, "Should contain 'name'"
assert "CI - test-app" in result, "Should contain workflow name"
assert "jobs" in result, "Should contain 'jobs'"
assert "test" in result, "Should contain job name 'test'"
assert "checkout" in result, "Should contain checkout step"
assert "pytest" in result, "Should contain pytest"
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
        print("  PERFECT! GitHub Actions mastered!")
    elif score >= 4:
        print("  Great work! Review failed tasks.")
    else:
        print("  Keep practicing with the lesson.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
