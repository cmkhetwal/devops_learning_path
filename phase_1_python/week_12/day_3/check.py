"""
Week 12, Day 3: Check - Capstone Part 1
Verifies all 5 tasks from exercise.py
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
    total = 5

    # Task 1: Server
    print("Task 1: Server class")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import Server

s = Server("web-01", "10.0.1.1", "web")
assert s.name == "web-01"
assert s.ip == "10.0.1.1"
assert s.role == "web"
assert s.status == "healthy"
assert s.metadata == {}
assert s.created_at is not None
assert s.updated_at is not None

d = s.to_dict()
assert d["name"] == "web-01"
assert d["ip"] == "10.0.1.1"
assert d["role"] == "web"
assert d["status"] == "healthy"

s.update_status("degraded")
assert s.status == "degraded"

# Test invalid role
try:
    Server("bad", "1.1.1.1", "invalid_role")
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Test invalid status
try:
    s.update_status("invalid")
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Test equality
s2 = Server("web-01", "10.0.1.2", "database")
assert s == s2, "Servers with same name should be equal"

assert "web-01" in repr(s)
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: Deployment
    print("Task 2: Deployment class")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import Deployment

d = Deployment("web-api", "2.1.0", "production")
assert d.app == "web-api"
assert d.version == "2.1.0"
assert d.environment == "production"
assert d.status == "pending"
assert d.completed_at is None
assert d.deploy_id is not None
assert "web-api" in d.deploy_id
assert "production" in d.deploy_id

dd = d.to_dict()
assert dd["app"] == "web-api"
assert dd["version"] == "2.1.0"

d.complete("success")
assert d.status == "success"
assert d.completed_at is not None

# Invalid environment
try:
    Deployment("app", "1.0", "invalid_env")
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Invalid status
try:
    d2 = Deployment("app", "1.0", "staging")
    d2.complete("invalid")
    assert False, "Should raise ValueError"
except ValueError:
    pass

assert "web-api" in repr(d)
assert "production" in repr(d)
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: HealthCheck
    print("Task 3: HealthCheck class")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import HealthCheck

hc = HealthCheck("web-01", "ping", "pass", "2ms response")
assert hc.server_name == "web-01"
assert hc.check_type == "ping"
assert hc.result == "pass"
assert hc.message == "2ms response"
assert hc.timestamp is not None

d = hc.to_dict()
assert d["server_name"] == "web-01"
assert d["check_type"] == "ping"
assert d["result"] == "pass"
assert d["message"] == "2ms response"

# Invalid check type
try:
    HealthCheck("s1", "invalid_type", "pass")
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Invalid result
try:
    HealthCheck("s1", "ping", "maybe")
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Default message
hc2 = HealthCheck("s1", "http", "fail")
assert hc2.message == ""

assert "web-01" in repr(hc)
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: ServerInventory
    print("Task 4: ServerInventory class")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import ServerInventory, Server

inv = ServerInventory()
inv.add_server(Server("web-01", "10.0.1.1", "web"))
inv.add_server(Server("web-02", "10.0.1.2", "web"))
inv.add_server(Server("db-01", "10.0.2.1", "database"))
inv.add_server(Server("cache-01", "10.0.3.1", "cache", "degraded"))

# Duplicate
try:
    inv.add_server(Server("web-01", "10.0.1.3", "web"))
    assert False, "Should raise ValueError"
except ValueError:
    pass

# Get
s = inv.get_server("web-01")
assert s is not None and s.name == "web-01"
assert inv.get_server("nonexistent") is None

# List all
all_s = inv.list_servers()
assert len(all_s) == 4
assert all_s[0].name == "cache-01"  # sorted alphabetically

# List by role
webs = inv.list_servers(role="web")
assert len(webs) == 2

# List by status
healthy = inv.list_servers(status="healthy")
assert len(healthy) == 3

# List by both
web_healthy = inv.list_servers(role="web", status="healthy")
assert len(web_healthy) == 2

# Update status
inv.update_server_status("web-01", "unhealthy")
assert inv.get_server("web-01").status == "unhealthy"

try:
    inv.update_server_status("nonexistent", "healthy")
    assert False, "Should raise KeyError"
except KeyError:
    pass

# Remove
removed = inv.remove_server("cache-01")
assert removed.name == "cache-01"
assert len(inv.list_servers()) == 3

try:
    inv.remove_server("nonexistent")
    assert False, "Should raise KeyError"
except KeyError:
    pass

# Statistics
stats = inv.get_statistics()
assert stats["total"] == 3
assert stats["by_role"]["web"] == 2
assert stats["by_role"]["database"] == 1
assert isinstance(stats["healthy_percentage"], float)

# Find
found = inv.find_servers("web")
assert len(found) == 2
found2 = inv.find_servers("10.0.2")
assert len(found2) == 1
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: DeploymentTracker
    print("Task 5: DeploymentTracker class")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import DeploymentTracker

tracker = DeploymentTracker()

d1 = tracker.record_deployment("web-api", "2.0.0", "production")
assert d1.status == "pending"
tracker.complete_deployment(d1.deploy_id, "success")
assert d1.status == "success"

d2 = tracker.record_deployment("web-api", "2.1.0", "production")
tracker.complete_deployment(d2.deploy_id, "failed")

d3 = tracker.record_deployment("worker", "1.0.0", "staging")
tracker.complete_deployment(d3.deploy_id, "success")

d4 = tracker.record_deployment("web-api", "2.0.5", "staging")

# Not found
try:
    tracker.complete_deployment("nonexistent-id", "success")
    assert False, "Should raise KeyError"
except KeyError:
    pass

# Filtered list
web_deploys = tracker.get_deployments(app="web-api")
assert len(web_deploys) == 3

prod_deploys = tracker.get_deployments(environment="production")
assert len(prod_deploys) == 2

success_deploys = tracker.get_deployments(status="success")
assert len(success_deploys) == 2

# Latest
latest = tracker.get_latest_deployment("web-api", "production")
assert latest.version == "2.1.0"

assert tracker.get_latest_deployment("nonexistent", "production") is None

# Statistics
stats = tracker.get_statistics()
assert stats["total"] == 4
assert stats["by_app"]["web-api"] == 3
assert stats["by_app"]["worker"] == 1
assert isinstance(stats["success_rate"], float)

# Rollback
rb = tracker.rollback("web-api", "production")
assert rb is not None, "Should find v2.0.0 to roll back to"
assert rb.version == "2.0.0"
assert rb.status == "rolled_back"

# No successful deploy to roll back to
rb2 = tracker.rollback("nonexistent-app", "production")
assert rb2 is None
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    print(f"\n{'='*40}")
    print(f"  Capstone Part 1 Score: {score}/{total}")
    if score == total:
        print("  PERFECT! Foundation is solid!")
    elif score >= 3:
        print("  Good progress! Fix remaining issues.")
    else:
        print("  Review your data models carefully.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
