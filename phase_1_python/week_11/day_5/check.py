"""
Week 11, Day 5: Check - Ansible Playbook & Inventory Generator
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

    # Task 1: generate_inventory_ini
    print("Task 1: generate_inventory_ini()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_inventory_ini, SERVERS

r = generate_inventory_ini(SERVERS)
assert isinstance(r, str), "Must return a string"
assert "[databases]" in r, "Must have databases group"
assert "[webservers]" in r, "Must have webservers group"
assert "[monitoring]" in r, "Must have monitoring group"
assert "web1.example.com" in r
assert "ansible_host=10.0.1.10" in r
assert "ansible_user=deploy" in r
assert "[webservers:vars]" in r
assert "http_port=80" in r
assert "[databases:vars]" in r
assert "db_port=5432" in r

# Check alphabetical group ordering
db_pos = r.index("[databases]")
mon_pos = r.index("[monitoring]")
web_pos = r.index("[webservers]")
assert db_pos < mon_pos < web_pos, "Groups should be alphabetical"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: generate_inventory_yaml
    print("Task 2: generate_inventory_yaml()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_inventory_yaml, SERVERS

r = generate_inventory_yaml(SERVERS)
assert isinstance(r, str)
assert "all:" in r
assert "children:" in r
assert "databases:" in r
assert "webservers:" in r
assert "hosts:" in r
assert "web1.example.com:" in r
assert "ansible_host: 10.0.1.10" in r
assert "vars:" in r
assert "http_port: 80" in r or "http_port: 80" in r
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: generate_playbook
    print("Task 3: generate_playbook()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_playbook

r = generate_playbook("Setup Web", "webservers", True, [
    {"name": "Install nginx", "module": "apt",
     "args": {"name": "nginx", "state": "present"}},
    {"name": "Start nginx", "module": "service",
     "args": {"name": "nginx", "state": "started"}},
])
assert isinstance(r, str)
assert "---" in r
assert "name: Setup Web" in r
assert "hosts: webservers" in r
assert "become: yes" in r or "become: true" in r or "become: True" in r
assert "tasks:" in r
assert "Install nginx" in r
assert "apt:" in r
assert "state: present" in r
assert "Start nginx" in r
assert "service:" in r
assert "state: started" in r
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: generate_role_playbook
    print("Task 4: generate_role_playbook()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_role_playbook

r = generate_role_playbook(
    "nginx",
    ["nginx", "python3"],
    [{"name": "nginx", "state": "started", "enabled": True}],
    [{"src": "nginx.conf", "dest": "/etc/nginx/nginx.conf", "notify": "Restart nginx"}],
    [{"name": "Restart nginx", "module": "service", "args": {"name": "nginx", "state": "restarted"}}],
)
assert isinstance(r, str)
assert "---" in r
assert "nginx" in r.lower()
assert "tasks:" in r
assert "handlers:" in r
assert "Install packages" in r or "install" in r.lower()
assert "nginx" in r and "python3" in r
assert "notify: Restart nginx" in r or "notify:" in r
assert "Restart nginx" in r
assert "restarted" in r
assert "/etc/nginx/nginx.conf" in r
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: generate_full_stack
    print("Task 5: generate_full_stack()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_full_stack

r = generate_full_stack("my-app", [
    {"name": "web", "hosts": "webservers", "packages": ["nginx"],
     "services": ["nginx"], "env_vars": {"APP_ENV": "prod"}, "port": 80},
    {"name": "database", "hosts": "databases", "packages": ["postgresql"],
     "services": ["postgresql"], "env_vars": {"DB_PORT": "5432"}, "port": 5432},
])
assert isinstance(r, str)
assert "---" in r
assert "my-app" in r
assert "webservers" in r
assert "databases" in r
assert "nginx" in r
assert "postgresql" in r
assert "APP_ENV" in r
assert "80" in r
assert "5432" in r
assert "wait_for" in r or "verify" in r.lower() or "port" in r.lower()

# Should have two plays (one per component)
assert r.count("hosts:") >= 2, "Should have at least 2 plays"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 6: generate_deployment_plan
    print("Task 6: generate_deployment_plan()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_deployment_plan

r = generate_deployment_plan("my-app", "2.0.0", [
    {"name": "staging", "hosts": "staging", "verify_url": "https://staging.example.com/health"},
    {"name": "production", "hosts": "production", "verify_url": "https://example.com/health"},
], rollback=True)
assert isinstance(r, str)
assert "---" in r
assert "my-app" in r
assert "2.0.0" in r
assert "staging" in r
assert "production" in r
assert "backup" in r.lower() or "Backup" in r
assert "git" in r.lower() or "Pull" in r or "pull" in r
assert "health" in r.lower() or "Health" in r
assert "rollback" in r.lower() or "Rollback" in r
assert "staging.example.com" in r
assert "example.com/health" in r

# Test without rollback
r2 = generate_deployment_plan("app", "1.0", [
    {"name": "staging", "hosts": "staging", "verify_url": "http://staging/health"},
], rollback=False)
assert "rollback" not in r2.lower() and "Rollback" not in r2
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
        print("  PERFECT! Ansible automation mastered!")
    elif score >= 4:
        print("  Great work! Review failed tasks.")
    else:
        print("  Keep practicing with the lesson.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
