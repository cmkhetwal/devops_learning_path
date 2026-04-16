"""
Week 12, Day 5: Check - Capstone Part 3
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

    # Task 1: CommandParser
    print("Task 1: CommandParser")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import CommandParser

cp = CommandParser()

# Simple command
r = cp.parse("add-server web-03 10.0.1.3 web")
assert r["command"] == "add-server"
assert r["args"] == ["web-03", "10.0.1.3", "web"]
assert r["options"] == {}
assert r["valid"] == True

# Command with options
r2 = cp.parse("list-servers --role web --status healthy")
assert r2["command"] == "list-servers"
assert r2["args"] == []
assert r2["options"]["role"] == "web"
assert r2["options"]["status"] == "healthy"
assert r2["valid"] == True

# Unknown command
r3 = cp.parse("bad-command stuff")
assert r3["valid"] == False

# Empty/help
r4 = cp.parse("help")
assert r4["command"] == "help"
assert r4["valid"] == True

# Deploy
r5 = cp.parse("deploy web-api 2.0.0 production")
assert r5["command"] == "deploy"
assert r5["args"] == ["web-api", "2.0.0", "production"]

# Health check no args
r6 = cp.parse("health-check")
assert r6["command"] == "health-check"
assert r6["args"] == []

# Raw preserved
assert r["raw"] == "add-server web-03 10.0.1.3 web"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: ReportGenerator
    print("Task 2: ReportGenerator")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import ReportGenerator, SAMPLE_SERVERS, SAMPLE_DEPLOYMENTS

rg = ReportGenerator(SAMPLE_SERVERS, SAMPLE_DEPLOYMENTS)

sr = rg.server_report()
assert isinstance(sr, str)
assert "SERVER INVENTORY REPORT" in sr
assert "Total Servers: 6" in sr
assert "Healthy: 5" in sr or "Healthy:  5" in sr
assert "Degraded: 1" in sr or "Degraded:  1" in sr
assert "web-01" in sr
assert "10.0.1.1" in sr
assert "database" in sr

dr = rg.deployment_report()
assert isinstance(dr, str)
assert "DEPLOYMENT REPORT" in dr
assert "Total Deployments: 5" in dr
assert "Success: 3" in dr or "Success:  3" in sr or "success" in dr.lower()
assert "Failed: 1" in dr or "Failed:  1" in dr or "failed" in dr.lower()
assert "web-api" in dr
assert "worker" in dr
assert "60" in dr  # 60% success rate

fr = rg.full_report()
assert "SERVER INVENTORY" in fr
assert "DEPLOYMENT REPORT" in fr
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: ConfigGenerator
    print("Task 3: ConfigGenerator")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import ConfigGenerator, SAMPLE_SERVERS

cg = ConfigGenerator(SAMPLE_SERVERS)

# Nginx upstream
nginx = cg.generate_nginx_upstream()
assert isinstance(nginx, str)
assert "upstream" in nginx
assert "10.0.1.1" in nginx  # web-01
assert "10.0.1.2" in nginx  # web-02
assert "10.0.2.1" not in nginx  # db-01 should NOT be in upstream

# Prometheus targets
prom = cg.generate_prometheus_targets()
assert isinstance(prom, str)
assert "web" in prom
assert "database" in prom
assert "10.0.1.1" in prom
assert "9090" in prom

# Ansible inventory
ansible = cg.generate_ansible_inventory()
assert isinstance(ansible, str)
assert "[web]" in ansible
assert "[database]" in ansible
assert "[cache]" in ansible
assert "web-01" in ansible
assert "ansible_host=10.0.1.1" in ansible

# All configs
all_configs = cg.generate_all()
assert isinstance(all_configs, dict)
assert "nginx" in all_configs
assert "prometheus" in all_configs
assert "ansible_inventory" in all_configs
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: DevOpsCLI
    print("Task 4: DevOpsCLI")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import DevOpsCLI

cli = DevOpsCLI()

# Help
r = cli.execute("help")
assert isinstance(r, str)
assert "add-server" in r
assert "deploy" in r

# List servers
r2 = cli.execute("list-servers")
assert "web-01" in r2
assert "6" in r2 or "Servers" in r2

# List servers with filter
r3 = cli.execute("list-servers --role web")
assert "web-01" in r3
assert "web-02" in r3

# Server status
r4 = cli.execute("server-status web-01")
assert "web-01" in r4
assert "10.0.1.1" in r4

# Add server
r5 = cli.execute("add-server lb-01 10.0.5.1 loadbalancer")
assert "lb-01" in r5
assert "added" in r5.lower() or "Added" in r5

# Duplicate add
r6 = cli.execute("add-server lb-01 10.0.5.2 web")
assert "Error" in r6 or "error" in r6 or "already" in r6.lower()

# Remove server
r7 = cli.execute("remove-server lb-01")
assert "removed" in r7.lower() or "Removed" in r7

# Remove nonexistent
r8 = cli.execute("remove-server nonexistent")
assert "Error" in r8 or "error" in r8 or "not found" in r8.lower()

# Deploy
r9 = cli.execute("deploy my-app 1.0.0 staging")
assert "my-app" in r9 and "staging" in r9

# Generate config
r10 = cli.execute("generate-config nginx")
assert "upstream" in r10 or "server" in r10

r11 = cli.execute("generate-config invalid")
assert "Error" in r11 or "error" in r11 or "Unknown" in r11

# Unknown command
r12 = cli.execute("bad-command")
assert "Unknown" in r12 or "unknown" in r12

# Check output history
assert len(cli.output_history) >= 10
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: run_platform
    print("Task 5: run_platform()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import run_platform

commands = [
    "list-servers",
    "add-server test-01 10.0.9.1 web",
    "deploy test-app 1.0.0 staging",
    "server-status test-01",
    "bad-command",
    "remove-server nonexistent-server",
]

results = run_platform(commands)
assert isinstance(results, list)
assert len(results) == 6

# list-servers should succeed
assert results[0]["success"] == True
assert results[0]["command"] == "list-servers"

# add-server should succeed
assert results[1]["success"] == True
assert "test-01" in results[1]["output"]

# deploy should succeed
assert results[2]["success"] == True

# server-status should succeed
assert results[3]["success"] == True

# bad-command should fail
assert results[4]["success"] == False

# remove nonexistent should fail
assert results[5]["success"] == False
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    print(f"\n{'='*40}")
    print(f"  Capstone Part 3 Score: {score}/{total}")
    if score == total:
        print("  PERFECT! Capstone complete!")
        print("  Your DevOps Platform is fully functional!")
    elif score >= 3:
        print("  Almost there! Fix remaining issues.")
    else:
        print("  Review CLI patterns and integration.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
