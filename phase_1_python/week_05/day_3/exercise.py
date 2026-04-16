"""
Week 5, Day 3: Exercise - JSON & YAML
======================================

Today you will practice working with JSON and YAML config files.
Sample data files are created for you below.

Complete all 5 tasks. Run check.py when finished to verify your work.

NOTE: Task 5 requires pyyaml. Install with: pip install pyyaml
      Tasks 1-4 use only the built-in json module.
"""

import json
import os

# === Setup: Create sample data files ===
# (Do NOT modify this section)

sample_json_config = {
    "app_name": "inventory-service",
    "version": "1.3.2",
    "environment": "production",
    "debug": False,
    "database": {
        "host": "db-01.example.com",
        "port": 5432,
        "name": "inventory_db",
        "max_connections": 50
    },
    "servers": [
        {"hostname": "web-01", "ip": "10.0.1.10", "role": "primary"},
        {"hostname": "web-02", "ip": "10.0.1.11", "role": "secondary"},
        {"hostname": "web-03", "ip": "10.0.1.12", "role": "secondary"}
    ],
    "monitoring": {
        "enabled": True,
        "interval_seconds": 30,
        "alert_email": "ops@example.com"
    }
}

with open("app_config.json", "w") as f:
    json.dump(sample_json_config, f, indent=4)

# ============================================
# TASK 1: Parse the JSON config
# ============================================
# Read "app_config.json" and extract the following values:
# - app_name: the app name (string)
# - db_host: the database host (string)
# - db_port: the database port (integer)
# - server_count: how many servers are in the list (integer)
# - monitoring_enabled: whether monitoring is enabled (boolean)

# YOUR CODE HERE
app_name = None
db_host = None
db_port = None
server_count = None
monitoring_enabled = None


# ============================================
# TASK 2: Extract server hostnames
# ============================================
# Read "app_config.json" and create a list called server_hostnames
# that contains just the hostname of each server.
# Expected: ["web-01", "web-02", "web-03"]

# YOUR CODE HERE
server_hostnames = None


# ============================================
# TASK 3: Create a new JSON config
# ============================================
# Create a file called "deploy_config.json" with the following
# Python dictionary, written as pretty JSON (indent=4):

deploy_settings = {
    "project": "inventory-service",
    "deploy_to": "production",
    "version": "1.4.0",
    "rollback_enabled": True,
    "max_retries": 3,
    "targets": ["web-01", "web-02", "web-03"],
    "notifications": {
        "slack_channel": "#deployments",
        "email": "ops@example.com"
    }
}

# YOUR CODE HERE


# ============================================
# TASK 4: Update a JSON config
# ============================================
# Read "app_config.json", make these changes, then write it
# to a NEW file called "updated_config.json" (with indent=4):
#
# 1. Change "version" to "1.4.0"
# 2. Change "debug" to True
# 3. Change "environment" to "staging"
# 4. Change database "max_connections" to 100
#
# Do NOT modify the original app_config.json.

# YOUR CODE HERE


# ============================================
# TASK 5: Convert JSON to YAML
# ============================================
# Read "app_config.json" and write its contents as a YAML file
# called "app_config.yaml".
#
# Use yaml.dump() with default_flow_style=False.
#
# NOTE: You need pyyaml installed: pip install pyyaml
# If pyyaml is not installed, this task will be skipped by the checker.

# YOUR CODE HERE


# === Display Results ===
print("=" * 50)
print("RESULTS")
print("=" * 50)
print(f"Task 1 - app_name: {app_name}")
print(f"Task 1 - db_host: {db_host}")
print(f"Task 1 - db_port: {db_port}")
print(f"Task 1 - server_count: {server_count}")
print(f"Task 1 - monitoring_enabled: {monitoring_enabled}")
print(f"Task 2 - server_hostnames: {server_hostnames}")
print(f"Task 3 - deploy_config.json exists: {os.path.exists('deploy_config.json')}")
print(f"Task 4 - updated_config.json exists: {os.path.exists('updated_config.json')}")
print(f"Task 5 - app_config.yaml exists: {os.path.exists('app_config.yaml')}")
