"""
Week 12, Day 6: Exercise - Code Review & Refactoring

You are given "bad" code examples with multiple issues.
Your job is to refactor each one into clean, proper Python.

TASKS:
    1. refactor_server_checker()  - Fix a messy health check function
    2. refactor_deploy_function() - Fix a deploy function with issues
    3. refactor_config_loader()   - Fix a config loader with bad practices
    4. RefactoredInventory class  - Rewrite a bad class properly
    5. refactor_log_parser()      - Fix a messy log parser
    6. RefactoredPipeline class   - Rewrite a deployment pipeline
"""

import json
import os
import logging
from datetime import datetime


# ============================================================
# TASK 1: refactor_server_checker(servers)
#
# THE BAD CODE (do NOT use this -- rewrite it properly):
# -------------------------------------------------------
# def check_servers(s):
#     r = []
#     for x in s:
#         try:
#             if x['status'] == 'healthy':
#                 r.append({'name': x['name'], 'ok': True, 'msg': 'good'})
#             elif x['status'] == 'degraded':
#                 r.append({'name': x['name'], 'ok': False, 'msg': 'bad'})
#             elif x['status'] == 'unhealthy':
#                 r.append({'name': x['name'], 'ok': False, 'msg': 'bad'})
#             elif x['status'] == 'offline':
#                 r.append({'name': x['name'], 'ok': False, 'msg': 'bad'})
#             else:
#                 r.append({'name': x['name'], 'ok': False, 'msg': 'bad'})
#         except:
#             pass
#     return r
#
# YOUR REFACTORED VERSION:
# - Use descriptive variable names
# - Simplify the conditionals (healthy = ok, everything else = not ok)
# - Use specific exception handling
# - Include proper docstring
# - Validate input
# - Return more informative messages
#
# Expected behavior:
# - Takes list of server dicts (each has "name" and "status" keys)
# - Returns list of dicts with:
#   "name": server name
#   "is_healthy": True only if status is "healthy"
#   "status": the original status string
#   "message": "Server is operating normally" if healthy,
#              "Server is {status}" if not healthy,
#              "Missing server data" if dict is missing keys
# - Skip invalid entries (not dicts), don't crash
# ============================================================

def refactor_server_checker(servers):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: refactor_deploy_function(app_name, version, environment, servers)
#
# THE BAD CODE:
# -------------------------------------------------------
# def deploy(a, v, e, s):
#     if e == 'production' or e == 'staging' or e == 'development':
#         pass
#     else:
#         return 'bad env'
#     d = []
#     for x in s:
#         d.append(x + ' deployed')
#     result = {'app': a, 'v': v, 'env': e, 'servers': d, 'time': str(datetime.now())}
#     print('deployed ' + a)
#     return result
#
# YOUR REFACTORED VERSION:
# - Descriptive parameter names and variable names
# - Proper validation with exceptions or error dicts
# - Return a structured result dict:
#   "app": app_name
#   "version": version
#   "environment": environment
#   "deployed_to": list of "{server}: deployed" strings
#   "timestamp": ISO format datetime string
#   "status": "success"
#   "server_count": number of servers
#
# - If environment not in ["production", "staging", "development"],
#   return dict with "status": "error", "message": "Invalid environment: {env}"
# - If servers list is empty, return dict with "status": "error",
#   "message": "No servers specified"
# - If app_name or version is empty/None, return dict with
#   "status": "error", "message": "App name and version are required"
# ============================================================

def refactor_deploy_function(app_name, version, environment, servers):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: refactor_config_loader(config_string)
#
# THE BAD CODE:
# -------------------------------------------------------
# def load(s):
#     d = {}
#     for line in s.split('\n'):
#         if '=' in line:
#             k = line.split('=')[0]
#             v = line.split('=')[1]
#             d[k] = v
#     return d
#
# YOUR REFACTORED VERSION:
# - Handle comments (lines starting with #)
# - Handle empty lines
# - Strip whitespace from keys and values
# - Handle values that contain '=' (only split on first '=')
# - Handle quoted values (remove surrounding quotes)
# - Handle inline comments (# after value, but not inside quotes)
# - Return dict of key-value pairs
# - Ignore malformed lines (no '=' sign, after removing comments)
#
# Example input:
#   "# Database config\nDB_HOST=localhost\nDB_PORT=5432\n\n# Connection\nDB_URL=postgres://user:pass@host:5432/db\nDEBUG=false # Set to true for dev"
#
# Expected output:
#   {"DB_HOST": "localhost", "DB_PORT": "5432",
#    "DB_URL": "postgres://user:pass@host:5432/db",
#    "DEBUG": "false"}
# ============================================================

def refactor_config_loader(config_string):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: RefactoredInventory class
#
# THE BAD CODE:
# -------------------------------------------------------
# class Inv:
#     def __init__(self):
#         self.s = {}
#     def add(self, n, i, r):
#         self.s[n] = {'n': n, 'i': i, 'r': r, 's': 'up'}
#     def rm(self, n):
#         del self.s[n]
#     def get(self, n):
#         return self.s[n]
#     def all(self):
#         return self.s
#
# YOUR REFACTORED VERSION:
#
# class RefactoredInventory:
#   - Use descriptive attribute names
#   - Proper docstrings on class and all methods
#   - Input validation on all methods
#   - Proper error handling (ValueError for bad input, KeyError for not found)
#   - __init__: self.servers = {}
#   - add_server(name, ip, role): validate name (non-empty string),
#     ip (non-empty string), role (in ["web", "database", "cache", "worker"]).
#     Raise ValueError for invalid inputs.
#     Raise ValueError if name already exists.
#     Store as dict with name, ip, role, status="healthy",
#     added_at=ISO datetime string. Return the server dict.
#   - remove_server(name): Raise KeyError if not found.
#     Return removed server dict.
#   - get_server(name): Raise KeyError if not found. Return server dict.
#   - list_servers(role=None): Return sorted list of server dicts,
#     optionally filtered by role. Sort by name.
#   - server_count(): Return total count
#   - __repr__: "RefactoredInventory(X servers)"
# ============================================================

class RefactoredInventory:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: refactor_log_parser(log_text)
#
# THE BAD CODE:
# -------------------------------------------------------
# def parse(t):
#     l = []
#     for x in t.split('\n'):
#         if x == '':
#             continue
#         try:
#             p = x.split(' ')
#             l.append({'time': p[0] + ' ' + p[1], 'level': p[2],
#                       'msg': ' '.join(p[3:])})
#         except:
#             pass
#     return l
#
# YOUR REFACTORED VERSION:
# Parse log lines in format: "2025-01-15 14:30:00 INFO Server started"
#
# - Handle empty lines (skip them)
# - Handle malformed lines (add to results with level="UNKNOWN"
#   and the full line as message)
# - Strip whitespace
# - Return list of dicts with:
#   "timestamp": the datetime string (first two space-separated parts)
#   "level": the log level (third part, uppercased)
#   "message": the rest of the line (everything after level)
#   "is_error": True if level is "ERROR" or "CRITICAL"
#
# Also include a summary dict at the end of the list:
#   {"_summary": True, "total": N, "errors": count,
#    "warnings": count, "info": count}
# ============================================================

def refactor_log_parser(log_text):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 6: RefactoredPipeline class
#
# THE BAD CODE:
# -------------------------------------------------------
# class P:
#     def __init__(self):
#         self.s = []
#     def add(self, n, f):
#         self.s.append((n, f))
#     def run(self):
#         for n, f in self.s:
#             try:
#                 f()
#                 print(n + ' ok')
#             except:
#                 print(n + ' fail')
#
# YOUR REFACTORED VERSION:
#
# class RefactoredPipeline:
#   """A deployment pipeline that runs stages in order."""
#
#   __init__(self):
#     - self.stages = []
#     - self.results = []
#
#   add_stage(self, name, function, continue_on_failure=False):
#     - name: stage name (string)
#     - function: callable that takes no args and returns a value
#     - continue_on_failure: if True, pipeline continues even if
#       this stage fails
#     - Validate: name must be non-empty, function must be callable
#     - Raise ValueError otherwise
#
#   run(self):
#     - Run each stage in order
#     - For each stage, capture the result and any exceptions
#     - Store result dict:
#       {"stage": name, "status": "success"/"failed"/"skipped",
#        "result": return value or None,
#        "error": error message or None,
#        "duration": "completed" (string marker)}
#     - If a stage fails and continue_on_failure is False,
#       mark all remaining stages as "skipped" and stop
#     - Return the list of result dicts
#
#   get_summary(self):
#     - Return dict:
#       {"total": N, "passed": N, "failed": N, "skipped": N,
#        "success": True if all non-skipped stages passed}
#
#   __repr__: "RefactoredPipeline(N stages)"
# ============================================================

class RefactoredPipeline:
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    print("=== Task 1: Server Checker ===")
    servers = [
        {"name": "web-01", "status": "healthy"},
        {"name": "web-02", "status": "degraded"},
        {"name": "db-01", "status": "offline"},
        "not a dict",
        {"name": "bad-server"},
    ]
    results = refactor_server_checker(servers)
    if results:
        for r in results:
            print(f"  {r}")

    print("\n=== Task 2: Deploy Function ===")
    result = refactor_deploy_function("web-api", "2.0", "production", ["web-01", "web-02"])
    if result:
        print(f"  {result}")

    print("\n=== Task 3: Config Loader ===")
    config = "# DB Config\nDB_HOST=localhost\nDB_PORT=5432\nDEBUG=false # dev only"
    parsed = refactor_config_loader(config)
    if parsed:
        for k, v in parsed.items():
            print(f"  {k}={v}")

    print("\n=== Task 4: Inventory ===")
    inv = RefactoredInventory()
    inv.add_server("web-01", "10.0.1.1", "web")
    inv.add_server("db-01", "10.0.2.1", "database")
    print(f"  {inv}")
    print(f"  Count: {inv.server_count()}")

    print("\n=== Task 5: Log Parser ===")
    logs = "2025-01-15 14:30:00 INFO Server started\n2025-01-15 14:31:00 ERROR Connection failed\n"
    parsed = refactor_log_parser(logs)
    if parsed:
        for entry in parsed:
            print(f"  {entry}")

    print("\n=== Task 6: Pipeline ===")
    pipeline = RefactoredPipeline()
    pipeline.add_stage("build", lambda: "built")
    pipeline.add_stage("test", lambda: "tested")
    pipeline.add_stage("deploy", lambda: "deployed")
    results = pipeline.run()
    if results:
        for r in results:
            print(f"  {r['stage']}: {r['status']}")
        print(f"  Summary: {pipeline.get_summary()}")
