"""
Week 12, Day 4: Capstone Part 2 - File I/O, Error Handling, Logging

Add persistence, error handling, and logging to the DevOps Platform.

TASKS:
    1. Custom exception classes
    2. PlatformLogger        - Configurable logging
    3. DataStore             - JSON file persistence
    4. HealthChecker         - Simulated health checks
    5. PlatformManager       - Orchestrate all components
"""

import json
import os
import logging
from datetime import datetime


# ============================================================
# TASK 1: Custom Exception Classes
#
# Create these exception classes:
#
# PlatformError(Exception)
#   Base exception. __init__(self, message, details=None):
#   - Store message and details (dict, default {})
#   - __str__ returns message
#
# ServerNotFoundError(PlatformError)
#   Raised when a server is not found.
#   __init__(self, server_name):
#   - message: "Server not found: {server_name}"
#   - details: {"server_name": server_name}
#
# DuplicateServerError(PlatformError)
#   Raised when adding a server that already exists.
#   __init__(self, server_name):
#   - message: "Server already exists: {server_name}"
#
# DeploymentError(PlatformError)
#   Raised for deployment-related errors.
#   __init__(self, message, app=None, environment=None):
#   - Store app and environment in details
#
# DataStoreError(PlatformError)
#   Raised for file I/O errors.
#   __init__(self, message, filepath=None):
#   - Store filepath in details
# ============================================================

class PlatformError(Exception):
    # YOUR CODE HERE
    pass


class ServerNotFoundError(PlatformError):
    # YOUR CODE HERE
    pass


class DuplicateServerError(PlatformError):
    # YOUR CODE HERE
    pass


class DeploymentError(PlatformError):
    # YOUR CODE HERE
    pass


class DataStoreError(PlatformError):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: PlatformLogger class
#
# __init__(self, name="devops_platform", level="INFO", log_file=None):
#   - Create a logging.Logger with the given name
#   - Set level from string (INFO, DEBUG, WARNING, ERROR)
#   - Always add a StreamHandler (console output)
#   - If log_file is provided, also add a FileHandler
#   - Use format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
#   - Store logger as self.logger
#
# info(self, message):    - Log at INFO level
# debug(self, message):   - Log at DEBUG level
# warning(self, message): - Log at WARNING level
# error(self, message):   - Log at ERROR level
#
# get_logger(self):
#   - Return the underlying logging.Logger object
# ============================================================

class PlatformLogger:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: DataStore class
#
# Handles saving and loading data to/from JSON files.
#
# __init__(self, base_dir="data"):
#   - Store base_dir path
#   - Create the directory if it doesn't exist (os.makedirs)
#
# save(self, filename, data):
#   - Save data (dict or list) to base_dir/filename as JSON
#   - Use indent=2 for readability
#   - Return the full filepath
#   - Raise DataStoreError on any I/O error
#
# load(self, filename, default=None):
#   - Load and return JSON data from base_dir/filename
#   - If file doesn't exist, return default (or {} if None)
#   - Raise DataStoreError on JSON decode errors
#
# exists(self, filename):
#   - Return True if the file exists in base_dir
#
# delete(self, filename):
#   - Delete the file. Return True if deleted, False if not found.
#
# list_files(self):
#   - Return sorted list of .json filenames in base_dir
# ============================================================

class DataStore:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: HealthChecker class
#
# Simulates health checks on servers using predefined rules.
#
# __init__(self):
#   - self.check_history = []  (list of check result dicts)
#
# check_server(self, server_dict):
#   - server_dict has: name, ip, role, status
#   - Run simulated checks based on role:
#     "web": ["ping", "http"]
#     "database": ["ping", "tcp"]
#     "cache": ["ping", "tcp"]
#     "worker": ["ping"]
#     "monitoring": ["ping", "http"]
#     "loadbalancer": ["ping", "http", "tcp"]
#     default: ["ping"]
#
#   - Simulation rules for each check:
#     If server status is "offline" -> all checks "fail"
#     If server status is "unhealthy" -> "http" and "tcp" fail, "ping" passes
#     If server status is "degraded" -> "http" fails, others pass
#     If server status is "healthy" -> all checks "pass"
#
#   - For each check, create a result dict:
#     {"server_name": name, "check_type": type, "result": "pass"/"fail",
#      "timestamp": ISO datetime string,
#      "message": "OK" for pass, "{check_type} check failed" for fail}
#
#   - Add all results to self.check_history
#   - Return list of result dicts for this check run
#
# get_server_health(self, server_name):
#   - Look at check_history for this server
#   - Return dict:
#     {"server_name": name,
#      "total_checks": count,
#      "passed": count of "pass",
#      "failed": count of "fail",
#      "health_percentage": float (passed/total * 100, 0 if no checks),
#      "last_check": most recent timestamp or None}
#
# get_history(self, server_name=None, limit=10):
#   - Return check_history, optionally filtered by server_name
#   - Most recent first
#   - Limited to 'limit' entries
# ============================================================

class HealthChecker:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: PlatformManager class
#
# Ties everything together.
#
# __init__(self, data_dir="platform_data"):
#   - Create a DataStore with data_dir
#   - Create a PlatformLogger named "devops_platform"
#   - Create a HealthChecker
#   - self.servers = {}  (name -> server dict)
#   - self.deployments = []  (list of deployment dicts)
#   - Try to load existing data: call self.load_data()
#
# add_server(self, name, ip, role, status="healthy"):
#   - Validate role is in VALID_ROLES = ["web", "database", "cache",
#     "worker", "monitoring", "loadbalancer"]
#   - Raise DuplicateServerError if name exists
#   - Add server dict to self.servers
#   - Log info: "Server added: {name}"
#   - Auto-save: call self.save_data()
#   - Return the server dict
#
# remove_server(self, name):
#   - Raise ServerNotFoundError if not found
#   - Remove from self.servers
#   - Log info: "Server removed: {name}"
#   - Auto-save
#   - Return the removed server dict
#
# record_deployment(self, app, version, environment):
#   - Create deployment dict with: app, version, environment,
#     status="pending", timestamp=ISO datetime,
#     deploy_id="{app}-{environment}-{timestamp with colons replaced by dashes}"
#   - Add to self.deployments
#   - Log info: "Deployment recorded: {app} v{version} -> {environment}"
#   - Auto-save
#   - Return deployment dict
#
# check_all_servers(self):
#   - Run health check on each server in self.servers
#   - Return list of all check results
#
# save_data(self):
#   - Save self.servers to "servers.json"
#   - Save self.deployments to "deployments.json"
#   - Log debug: "Data saved"
#
# load_data(self):
#   - Load servers from "servers.json" (default {})
#   - Load deployments from "deployments.json" (default [])
#   - Log debug: "Data loaded"
#
# get_dashboard(self):
#   - Return a summary dict:
#     {"total_servers": count,
#      "healthy_servers": count with status "healthy",
#      "total_deployments": count,
#      "recent_deployments": last 5 deployments (newest first),
#      "server_health": results from check_all_servers}
# ============================================================

VALID_ROLES = ["web", "database", "cache", "worker", "monitoring", "loadbalancer"]


class PlatformManager:
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    # Clean up any previous test data
    import shutil
    test_dir = "test_platform_data"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)

    print("=== Testing Platform Manager ===")
    pm = PlatformManager(data_dir=test_dir)

    pm.add_server("web-01", "10.0.1.1", "web")
    pm.add_server("web-02", "10.0.1.2", "web")
    pm.add_server("db-01", "10.0.2.1", "database")
    pm.add_server("cache-01", "10.0.3.1", "cache", "degraded")

    pm.record_deployment("web-api", "2.1.0", "production")
    pm.record_deployment("worker", "1.0.0", "staging")

    dashboard = pm.get_dashboard()
    print(f"\n  Total servers: {dashboard['total_servers']}")
    print(f"  Healthy: {dashboard['healthy_servers']}")
    print(f"  Deployments: {dashboard['total_deployments']}")

    # Test persistence
    pm2 = PlatformManager(data_dir=test_dir)
    print(f"\n  Loaded servers: {len(pm2.servers)}")
    print(f"  Loaded deployments: {len(pm2.deployments)}")

    # Cleanup
    shutil.rmtree(test_dir)
    print("\n  Test cleanup complete.")
