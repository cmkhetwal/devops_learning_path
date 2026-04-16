"""
Week 9, Day 6: Practice Day - Docker & Containers

FIVE MINI-PROJECTS
==================

Complete all five mini-projects below.  Each builds on what you learned
this week.  All projects use simulated data so Docker is NOT required.

PROJECTS
--------
1. Docker CLI Tool
2. Container Health Dashboard
3. Compose File Generator
4. Image Cleanup Script
5. Deployment Manager
"""

import os
import json

OUTPUT_DIR = "/home/cmk/python/devops-python-path/week_09/day_6/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# PROJECT 1: Docker CLI Tool
# ============================================================
# Build a function called `docker_cli` that:
#   - Takes one argument: command (str)
#   - Supports these commands:
#       "ps"     -> prints a table of containers (use SAMPLE_CONTAINERS below)
#                    Format: NAME(20) STATUS(12) IMAGE(25)
#                    Print header + separator + rows
#       "images" -> prints a table of images (use SAMPLE_IMAGES below)
#                    Format: REPOSITORY:TAG(30) SIZE(10) ID(15)
#                    Print header + separator + rows
#       "stats"  -> prints stats for running containers only
#                    Format: NAME(20) CPU%(8) MEM%(8) STATUS(10)
#       "help"   -> prints "Available commands: ps, images, stats, help"
#       anything else -> prints "Unknown command: <command>"
#   - Returns the command that was executed (the input string)

SAMPLE_CONTAINERS = [
    {"name": "web-frontend", "status": "running", "image": "nginx:latest", "cpu": 12.5, "mem": 35.2},
    {"name": "api-server", "status": "running", "image": "python:3.11-slim", "cpu": 45.0, "mem": 62.1},
    {"name": "database", "status": "running", "image": "postgres:15", "cpu": 8.3, "mem": 41.0},
    {"name": "cache", "status": "exited", "image": "redis:7", "cpu": 0.0, "mem": 0.0},
    {"name": "old-worker", "status": "exited", "image": "python:3.9", "cpu": 0.0, "mem": 0.0},
]

SAMPLE_IMAGES = [
    {"repo": "nginx", "tag": "latest", "size_mb": 150, "id": "sha256:abc123def"},
    {"repo": "python", "tag": "3.11-slim", "size_mb": 350, "id": "sha256:def456ghi"},
    {"repo": "postgres", "tag": "15", "size_mb": 400, "id": "sha256:ghi789jkl"},
    {"repo": "redis", "tag": "7", "size_mb": 80, "id": "sha256:jkl012mno"},
    {"repo": "python", "tag": "3.9", "size_mb": 900, "id": "sha256:mno345pqr"},
]

# YOUR CODE HERE


# ============================================================
# PROJECT 2: Container Health Dashboard
# ============================================================
# Build a function called `health_dashboard` that:
#   - Takes one argument: containers (list of dicts like SAMPLE_CONTAINERS)
#   - For each container, determine health:
#       "healthy"   if status == "running" and cpu < 80 and mem < 80
#       "warning"   if status == "running" and (cpu >= 80 or mem >= 80)
#       "critical"  if status != "running"
#   - Prints a dashboard:
#       Health Dashboard
#       ================
#       NAME                 HEALTH      CPU%     MEM%
#       <name>               <health>    <cpu>    <mem>
#       ...
#       ----------------
#       Summary: X healthy, Y warning, Z critical
#   - Returns dict: {"healthy": X, "warning": Y, "critical": Z}

# YOUR CODE HERE


# ============================================================
# PROJECT 3: Compose File Generator
# ============================================================
# Build a function called `generate_compose` that:
#   - Takes one argument: app_config (dict) with structure:
#       {
#           "app_name": "myapp",
#           "services": [
#               {"name": "web", "image": "nginx", "port": 80},
#               {"name": "api", "image": "python:3.11", "port": 5000},
#               {"name": "db", "image": "postgres:15", "port": 5432},
#           ]
#       }
#   - Generates a compose config dict with version "3.8"
#   - Each service gets:
#       image: from config
#       ports: ["<port>:<port>"]
#       container_name: "<app_name>-<service_name>"
#   - Writes the config as JSON to OUTPUT_DIR/compose_<app_name>.json
#   - Prints "Generated compose for '<app_name>': X services"
#   - Returns the config dict

# YOUR CODE HERE


# ============================================================
# PROJECT 4: Image Cleanup Script
# ============================================================
# Build a function called `cleanup_images` that:
#   - Takes two arguments: images (list of dicts like SAMPLE_IMAGES),
#     max_size_mb (int, default 500)
#   - Identifies images that should be cleaned:
#       - Size > max_size_mb
#   - Prints:
#       Image Cleanup Report
#       ====================
#       KEEP:
#         <repo>:<tag> (X MB)
#       ...
#       REMOVE:
#         <repo>:<tag> (X MB) - exceeds limit
#       ...
#       Space saved: X MB
#   - Returns dict: {"kept": X, "removed": Y, "saved_mb": Z}

# YOUR CODE HERE


# ============================================================
# PROJECT 5: Deployment Manager
# ============================================================
# Build a function called `deploy_application` that:
#   - Takes three arguments: app_name (str), version (str),
#     containers (list of dicts like SAMPLE_CONTAINERS)
#   - Simulates a deployment:
#     1. Print "Deploying <app_name> version <version>..."
#     2. For each container whose name starts with app_name (or any prefix
#        match is fine -- just use the first 3 characters of app_name):
#        Print "  Stopping <name>..."
#     3. Print "  Starting <app_name>-<version>..."
#     4. Print "Deployment complete!"
#   - Returns dict:
#       "app": app_name
#       "version": version
#       "stopped": number of containers stopped
#       "started": 1
#       "status": "success"

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  WEEK 9, DAY 6 - Practice Day")
    print("=" * 55)

    # Project 1
    print("\n--- Project 1: Docker CLI ---")
    docker_cli("ps")
    print()
    docker_cli("images")
    print()
    docker_cli("stats")
    print()
    docker_cli("help")
    docker_cli("invalid")

    # Project 2
    print("\n--- Project 2: Health Dashboard ---")
    health = health_dashboard(SAMPLE_CONTAINERS)
    print(f"Result: {health}")

    # Project 3
    print("\n--- Project 3: Compose Generator ---")
    app_config = {
        "app_name": "webapp",
        "services": [
            {"name": "web", "image": "nginx:latest", "port": 80},
            {"name": "api", "image": "fastapi:latest", "port": 8000},
            {"name": "db", "image": "postgres:15", "port": 5432},
        ]
    }
    compose = generate_compose(app_config)
    print(f"Services: {list(compose.get('services', {}).keys())}")

    # Project 4
    print("\n--- Project 4: Image Cleanup ---")
    result = cleanup_images(SAMPLE_IMAGES, max_size_mb=300)
    print(f"Cleanup result: {result}")

    # Project 5
    print("\n--- Project 5: Deployment ---")
    dep = deploy_application("web", "v2.0", SAMPLE_CONTAINERS)
    print(f"Deploy result: {dep}")
