"""
Week 6, Day 5: Auto-Checker for argparse exercises.
Run: python3 check.py
"""

import subprocess
import sys
import os

EXERCISE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
score = 0
total = 5


def run_python(code):
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True, text=True, timeout=10,
        cwd=os.path.dirname(EXERCISE)
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# --- TASK 1: create_basic_parser ---
print("Task 1: create_basic_parser()")
code = """
import sys, os, argparse
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import create_basic_parser

parser = create_basic_parser()
assert isinstance(parser, argparse.ArgumentParser), "Must return an ArgumentParser"

# Test with all args
args = parser.parse_args(["status", "--host", "web01", "--port", "2222", "-v"])
assert args.action == "status", f"action wrong: {{args.action}}"
assert args.host == "web01", f"host wrong: {{args.host}}"
assert args.port == 2222, f"port wrong (should be int): {{args.port}}"
assert args.verbose == True, f"verbose wrong: {{args.verbose}}"

# Test defaults
args2 = parser.parse_args(["deploy"])
assert args2.host == "localhost", f"default host wrong: {{args2.host}}"
assert args2.port == 22, f"default port wrong: {{args2.port}}"
assert args2.verbose == False, f"default verbose wrong: {{args2.verbose}}"

# Test choices validation
try:
    parser.parse_args(["invalid_action"])
    assert False, "Should reject invalid action"
except SystemExit:
    pass  # Expected

print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        # Filter out argparse error messages to show our assertion error
        lines = [l for l in stderr.splitlines() if "assert" in l.lower() or "Error" in l]
        if lines:
            print(f"  Error: {lines[-1]}")


# --- TASK 2: parse_deploy_args ---
print("Task 2: parse_deploy_args()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import parse_deploy_args

# Test full args
args = parse_deploy_args(["myapp", "--env", "prod", "--version", "2.0.0", "--replicas", "3", "--dry-run"])
assert args.service == "myapp", f"service wrong: {{args.service}}"
assert args.env == "prod", f"env wrong: {{args.env}}"
assert args.version == "2.0.0", f"version wrong: {{args.version}}"
assert args.replicas == 3, f"replicas wrong: {{args.replicas}}"
assert args.dry_run == True, f"dry_run wrong: {{args.dry_run}}"

# Test defaults
args2 = parse_deploy_args(["web", "-e", "dev", "--version", "1.0"])
assert args2.service == "web", f"service wrong: {{args2.service}}"
assert args2.replicas == 1, f"default replicas wrong: {{args2.replicas}}"
assert args2.dry_run == False, f"default dry_run wrong: {{args2.dry_run}}"

# Test short flag -e
args3 = parse_deploy_args(["svc", "-e", "staging", "--version", "0.1"])
assert args3.env == "staging", f"short -e flag wrong: {{args3.env}}"

# Test short flag -r
args4 = parse_deploy_args(["svc", "-e", "dev", "--version", "0.1", "-r", "5"])
assert args4.replicas == 5, f"short -r flag wrong: {{args4.replicas}}"

print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        lines = [l for l in stderr.splitlines() if "assert" in l.lower() or "Error" in l]
        if lines:
            print(f"  Error: {lines[-1]}")


# --- TASK 3: parse_monitor_args ---
print("Task 3: parse_monitor_args()")
code = """
import sys, os
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import parse_monitor_args

# Test with multiple hosts and checks
args = parse_monitor_args(["--hosts", "web01", "web02", "db01",
                           "--checks", "ping", "disk", "cpu",
                           "--interval", "30",
                           "--alert-email", "ops@company.com", "-q"])
assert args.hosts == ["web01", "web02", "db01"], f"hosts wrong: {{args.hosts}}"
assert args.checks == ["ping", "disk", "cpu"], f"checks wrong: {{args.checks}}"
assert args.interval == 30, f"interval wrong: {{args.interval}}"
assert args.alert_email == "ops@company.com", f"alert_email wrong: {{args.alert_email}}"
assert args.quiet == True, f"quiet wrong: {{args.quiet}}"

# Test defaults
args2 = parse_monitor_args(["--hosts", "server1"])
assert args2.checks == ["ping"], f"default checks wrong: {{args2.checks}}"
assert args2.interval == 60, f"default interval wrong: {{args2.interval}}"
assert args2.alert_email is None, f"default alert_email wrong: {{args2.alert_email}}"
assert args2.quiet == False, f"default quiet wrong: {{args2.quiet}}"

print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        lines = [l for l in stderr.splitlines() if "assert" in l.lower() or "Error" in l]
        if lines:
            print(f"  Error: {lines[-1]}")


# --- TASK 4: format_deploy_summary ---
print("Task 4: format_deploy_summary()")
code = """
import sys, os, argparse
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import format_deploy_summary

# Test normal deployment
args = argparse.Namespace(service="api", version="1.0.0", env="prod", replicas=3, dry_run=False)
result = format_deploy_summary(args)
assert isinstance(result, str), "Must return a string"
assert result == "Deploying api v1.0.0 to prod (3 replica(s))", f"Wrong: {{result}}"

# Test dry run
args2 = argparse.Namespace(service="web", version="2.1", env="staging", replicas=1, dry_run=True)
result2 = format_deploy_summary(args2)
assert result2 == "[DRY RUN] Deploying web v2.1 to staging (1 replica(s))", f"Wrong: {{result2}}"

# Test single replica
args3 = argparse.Namespace(service="db", version="0.5", env="dev", replicas=1, dry_run=False)
result3 = format_deploy_summary(args3)
assert "1 replica(s)" in result3, f"Single replica wrong: {{result3}}"

print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        print(f"  Error: {stderr.splitlines()[-1]}")


# --- TASK 5: build_monitor_config ---
print("Task 5: build_monitor_config()")
code = """
import sys, os, argparse
sys.path.insert(0, os.path.dirname(r'{}'))
from exercise import build_monitor_config

# Test with alert email
args = argparse.Namespace(
    hosts=["web01", "web02"],
    checks=["ping", "disk"],
    interval=30,
    alert_email="ops@co.com",
    quiet=False
)
result = build_monitor_config(args)
assert isinstance(result, dict), "Must return a dict"
assert result["hosts"] == ["web01", "web02"], f"hosts wrong: {{result['hosts']}}"
assert result["checks"] == ["ping", "disk"], f"checks wrong: {{result['checks']}}"
assert result["interval"] == 30, f"interval wrong: {{result['interval']}}"
assert result["alert"] == "ops@co.com", f"alert wrong: {{result['alert']}}"
assert result["quiet"] == False, f"quiet wrong: {{result['quiet']}}"
assert result["total_checks"] == 4, f"total_checks wrong: {{result['total_checks']}}"

# Test without alert email
args2 = argparse.Namespace(
    hosts=["db01"],
    checks=["ping", "cpu", "memory"],
    interval=60,
    alert_email=None,
    quiet=True
)
result2 = build_monitor_config(args2)
assert result2["alert"] == "none", f"alert should be 'none': {{result2['alert']}}"
assert result2["quiet"] == True, f"quiet wrong: {{result2['quiet']}}"
assert result2["total_checks"] == 3, f"total_checks wrong: {{result2['total_checks']}}"

print("OK")
""".format(EXERCISE)
stdout, stderr, rc = run_python(code)
if rc == 0 and "OK" in stdout:
    print(f"  {PASS}")
    score += 1
else:
    print(f"  {FAIL}")
    if stderr:
        print(f"  Error: {stderr.splitlines()[-1]}")


# --- SUMMARY ---
print(f"\n{'='*40}")
print(f"  Week 6, Day 5 Score: {score}/{total}")
print(f"{'='*40}")
if score == total:
    print("  Outstanding! You've mastered argparse.")
elif score >= 3:
    print("  Good progress. Review the tasks you missed.")
else:
    print("  Keep practicing. Re-read lesson.md and try again.")
