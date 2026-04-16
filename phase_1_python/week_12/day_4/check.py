"""
Week 12, Day 4: Check - Capstone Part 2
Verifies all 5 tasks from exercise.py
"""

import subprocess
import sys
import os
import shutil

def run_test(test_code):
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    score = 0
    total = 5

    # Task 1: Custom Exceptions
    print("Task 1: Custom Exceptions")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import (PlatformError, ServerNotFoundError, DuplicateServerError,
                       DeploymentError, DataStoreError)

# PlatformError
e = PlatformError("test error", {"key": "val"})
assert str(e) == "test error"
assert e.details == {"key": "val"}

# ServerNotFoundError
e2 = ServerNotFoundError("web-01")
assert "web-01" in str(e2)
assert isinstance(e2, PlatformError)
assert e2.details.get("server_name") == "web-01"

# DuplicateServerError
e3 = DuplicateServerError("web-01")
assert "web-01" in str(e3)
assert isinstance(e3, PlatformError)

# DeploymentError
e4 = DeploymentError("failed", app="web", environment="prod")
assert isinstance(e4, PlatformError)
assert e4.details.get("app") == "web"

# DataStoreError
e5 = DataStoreError("io error", filepath="/tmp/test")
assert isinstance(e5, PlatformError)
assert e5.details.get("filepath") == "/tmp/test"

# All inherit from PlatformError and Exception
for cls in [ServerNotFoundError, DuplicateServerError, DeploymentError, DataStoreError]:
    assert issubclass(cls, PlatformError)
    assert issubclass(cls, Exception)
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: PlatformLogger
    print("Task 2: PlatformLogger")
    code = '''
import sys; sys.path.insert(0, ".")
import logging
from exercise import PlatformLogger

pl = PlatformLogger("test_logger", level="DEBUG")
logger = pl.get_logger()
assert isinstance(logger, logging.Logger)
assert logger.name == "test_logger"
assert logger.level == logging.DEBUG

# Methods should work without error
pl.info("test info")
pl.debug("test debug")
pl.warning("test warning")
pl.error("test error")

# Test with INFO level
pl2 = PlatformLogger("test2", level="INFO")
assert pl2.get_logger().level == logging.INFO

# Logger should have at least one handler
assert len(logger.handlers) >= 1
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: DataStore
    print("Task 3: DataStore")
    test_dir = "check_test_datastore"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    code = f'''
import sys; sys.path.insert(0, ".")
import os, shutil
from exercise import DataStore, DataStoreError

ds = DataStore("{test_dir}")
assert os.path.isdir("{test_dir}")

# Save
path = ds.save("test.json", {{"servers": ["web-01", "web-02"]}})
assert os.path.exists(path)

# Load
data = ds.load("test.json")
assert data["servers"] == ["web-01", "web-02"]

# Load nonexistent - returns default
data2 = ds.load("nonexistent.json")
assert data2 == {{}}

data3 = ds.load("nonexistent.json", default=[])
assert data3 == []

# Exists
assert ds.exists("test.json") == True
assert ds.exists("nope.json") == False

# List files
ds.save("another.json", {{"x": 1}})
files = ds.list_files()
assert "test.json" in files
assert "another.json" in files

# Delete
assert ds.delete("test.json") == True
assert ds.delete("test.json") == False
assert not ds.exists("test.json")

shutil.rmtree("{test_dir}")
print("PASS")
'''
    ok, out, err = run_test(code)
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: HealthChecker
    print("Task 4: HealthChecker")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import HealthChecker

hc = HealthChecker()

# Healthy web server -> ping pass, http pass
results = hc.check_server({"name": "web-01", "ip": "10.0.1.1", "role": "web", "status": "healthy"})
assert len(results) == 2, f"Web should have 2 checks: {len(results)}"
assert all(r["result"] == "pass" for r in results)

# Degraded server -> http fails, ping passes
results2 = hc.check_server({"name": "web-02", "ip": "10.0.1.2", "role": "web", "status": "degraded"})
ping_result = [r for r in results2 if r["check_type"] == "ping"][0]
http_result = [r for r in results2 if r["check_type"] == "http"][0]
assert ping_result["result"] == "pass"
assert http_result["result"] == "fail"

# Offline server -> all fail
results3 = hc.check_server({"name": "db-01", "ip": "10.0.2.1", "role": "database", "status": "offline"})
assert all(r["result"] == "fail" for r in results3)

# Check history
health = hc.get_server_health("web-01")
assert health["server_name"] == "web-01"
assert health["total_checks"] == 2
assert health["passed"] == 2
assert health["failed"] == 0
assert health["health_percentage"] == 100.0

health2 = hc.get_server_health("db-01")
assert health2["failed"] > 0

# Get history
history = hc.get_history(limit=3)
assert len(history) <= 3
assert history[0]["timestamp"] >= history[-1]["timestamp"]  # newest first

history2 = hc.get_history(server_name="web-01")
assert all(h["server_name"] == "web-01" for h in history2)
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: PlatformManager
    print("Task 5: PlatformManager")
    test_dir2 = "check_test_platform"
    if os.path.exists(test_dir2):
        shutil.rmtree(test_dir2)
    code = f'''
import sys; sys.path.insert(0, ".")
import os, shutil
from exercise import PlatformManager, DuplicateServerError, ServerNotFoundError

pm = PlatformManager(data_dir="{test_dir2}")

# Add servers
s = pm.add_server("web-01", "10.0.1.1", "web")
assert s["name"] == "web-01"
pm.add_server("db-01", "10.0.2.1", "database")
pm.add_server("cache-01", "10.0.3.1", "cache", "degraded")

# Duplicate
try:
    pm.add_server("web-01", "10.0.1.2", "web")
    assert False, "Should raise DuplicateServerError"
except DuplicateServerError:
    pass

# Remove
removed = pm.remove_server("cache-01")
assert removed["name"] == "cache-01"

try:
    pm.remove_server("nonexistent")
    assert False, "Should raise ServerNotFoundError"
except ServerNotFoundError:
    pass

# Deploy
d = pm.record_deployment("web-api", "2.1.0", "production")
assert d["app"] == "web-api"
assert d["status"] == "pending"
assert "deploy_id" in d

# Dashboard
dashboard = pm.get_dashboard()
assert dashboard["total_servers"] == 2
assert dashboard["healthy_servers"] == 2
assert dashboard["total_deployments"] == 1

# Persistence test
pm.save_data()
pm2 = PlatformManager(data_dir="{test_dir2}")
assert len(pm2.servers) == 2, f"Should persist 2 servers, got {{len(pm2.servers)}}"
assert len(pm2.deployments) == 1

# Health checks
health = pm.check_all_servers()
assert len(health) > 0

shutil.rmtree("{test_dir2}")
print("PASS")
'''
    ok, out, err = run_test(code)
    if os.path.exists(test_dir2):
        shutil.rmtree(test_dir2)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    print(f"\n{'='*40}")
    print(f"  Capstone Part 2 Score: {score}/{total}")
    if score == total:
        print("  PERFECT! Production-ready code!")
    elif score >= 3:
        print("  Good progress! Fix remaining issues.")
    else:
        print("  Review error handling and I/O patterns.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
