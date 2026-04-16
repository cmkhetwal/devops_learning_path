"""
Week 5, Day 5: Exercise - Logging
==================================

Today you will practice using the Python logging module.
Complete all 5 tasks. Run check.py when finished to verify your work.
"""

import logging
import os

# === Cleanup from previous runs ===
for f in ["deploy.log", "health.log", "app_debug.log", "app_info.log"]:
    if os.path.exists(f):
        os.remove(f)

# Reset logging (needed if running multiple times)
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


# ============================================
# TASK 1: Basic logging setup
# ============================================
# Configure basicConfig with:
# - level: DEBUG
# - format: "%(asctime)s [%(levelname)s] %(message)s"
# - datefmt: "%Y-%m-%d %H:%M:%S"
# - filename: "deploy.log"
# - filemode: "w"
#
# Then log these messages at the correct levels:
# 1. "Deployment script started" (INFO)
# 2. "Checking prerequisites" (DEBUG)
# 3. "All prerequisites met" (INFO)
# 4. "Slow network detected, deployment may take longer" (WARNING)
# 5. "Deployment to web-01 complete" (INFO)
# 6. "Failed to deploy to web-02: connection refused" (ERROR)
# 7. "Deployment finished with errors" (WARNING)

# YOUR CODE HERE


# ============================================
# TASK 2: Custom logger with file handler
# ============================================
# Create a logger called "healthcheck" (use logging.getLogger)
# - Set the logger level to DEBUG
# - Create a FileHandler that writes to "health.log"
# - Set the handler level to INFO
# - Set the format to: "%(asctime)s | %(name)s | %(levelname)-8s | %(message)s"
# - Set datefmt to "%Y-%m-%d %H:%M:%S"
# - Add the handler to the logger
#
# Then log these messages using the logger:
# 1. "Health check started" (INFO)
# 2. "Checking web-01" (DEBUG)  <-- this should NOT appear in file (below INFO)
# 3. "web-01: CPU at 45% - OK" (INFO)
# 4. "web-02: CPU at 87% - High" (WARNING)
# 5. "db-01: Disk at 95% - CRITICAL" (CRITICAL)
# 6. "Health check complete" (INFO)

# YOUR CODE HERE


# ============================================
# TASK 3: Logger with multiple handlers
# ============================================
# Create a logger called "app" (use logging.getLogger)
# - Set the logger level to DEBUG
#
# Add TWO FileHandlers:
# 1. "app_debug.log" - level DEBUG, captures everything
#    format: "%(asctime)s [%(levelname)s] %(message)s"
# 2. "app_info.log" - level INFO, captures INFO and above
#    format: "%(asctime)s [%(levelname)s] %(message)s"
#
# Use datefmt "%Y-%m-%d %H:%M:%S" for both handlers.
#
# Then log these messages using the logger:
# 1. "Application starting" (INFO)
# 2. "Loading config from /etc/app/config.json" (DEBUG)
# 3. "Config loaded successfully" (INFO)
# 4. "Cache miss for key: user_123" (DEBUG)
# 5. "Request processed in 250ms" (INFO)
# 6. "Database query slow: 5.2 seconds" (WARNING)
# 7. "Failed to send notification email" (ERROR)

# YOUR CODE HERE


# ============================================
# TASK 4: Deployment simulation with logging
# ============================================
# Write a function called deploy_server(logger, server, version) that:
# - Logs "Deploying v{version} to {server}..." at INFO level
# - If server is "web-03", log "Connection refused to {server}" at ERROR
#   level and return False
# - Otherwise log "Successfully deployed v{version} to {server}" at INFO
#   level and return True
#
# Then:
# - Create a logger called "deployer" with level INFO
# - Add a FileHandler for "deploy_results.log" with level INFO
#   and format "%(asctime)s [%(levelname)s] %(message)s"
#   with datefmt "%Y-%m-%d %H:%M:%S"
# - Call deploy_server for each server: "web-01", "web-02", "web-03", "db-01"
# - Collect the return values in a list called deploy_outcomes

# YOUR CODE HERE
deploy_outcomes = None


# ============================================
# TASK 5: Log level counter
# ============================================
# Write a function called count_log_levels(log_filepath) that:
# - Reads a log file
# - Counts how many lines contain each log level
# - Returns a dictionary like: {"DEBUG": 2, "INFO": 5, "WARNING": 1, "ERROR": 1, "CRITICAL": 0}
#
# Hint: Check if "[DEBUG]" or "[INFO]" etc. appears in each line.
#       Also check for "| DEBUG" patterns (from Task 2 format).
#       A simple approach: check if the level name is anywhere in the line.

# YOUR CODE HERE


# Count levels in the deploy.log from Task 1
deploy_log_counts = None
if os.path.exists("deploy.log"):
    deploy_log_counts = count_log_levels("deploy.log")


# === Display Results ===
print("=" * 50)
print("RESULTS")
print("=" * 50)
print(f"Task 1 - deploy.log exists: {os.path.exists('deploy.log')}")
print(f"Task 2 - health.log exists: {os.path.exists('health.log')}")
print(f"Task 3 - app_debug.log exists: {os.path.exists('app_debug.log')}")
print(f"Task 3 - app_info.log exists: {os.path.exists('app_info.log')}")
print(f"Task 4 - deploy_outcomes: {deploy_outcomes}")
print(f"Task 5 - deploy.log counts: {deploy_log_counts}")
