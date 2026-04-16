"""
Week 12, Day 5: Capstone Part 3 - CLI, Reporting, Final Integration

Bring the DevOps Automation Platform to life with a CLI interface,
reporting, and config generation.

TASKS:
    1. CommandParser        - Parse CLI-style commands
    2. ReportGenerator      - Generate formatted reports
    3. ConfigGenerator      - Generate configs from inventory
    4. DevOpsCLI            - Full CLI interface
    5. run_platform()       - Process a script of commands
"""

from datetime import datetime
import json


# ============================================================
# SAMPLE DATA (used by tests -- simulates persisted state)
# ============================================================

SAMPLE_SERVERS = {
    "web-01": {"name": "web-01", "ip": "10.0.1.1", "role": "web", "status": "healthy"},
    "web-02": {"name": "web-02", "ip": "10.0.1.2", "role": "web", "status": "healthy"},
    "db-01": {"name": "db-01", "ip": "10.0.2.1", "role": "database", "status": "healthy"},
    "db-02": {"name": "db-02", "ip": "10.0.2.2", "role": "database", "status": "degraded"},
    "cache-01": {"name": "cache-01", "ip": "10.0.3.1", "role": "cache", "status": "healthy"},
    "mon-01": {"name": "mon-01", "ip": "10.0.4.1", "role": "monitoring", "status": "healthy"},
}

SAMPLE_DEPLOYMENTS = [
    {"app": "web-api", "version": "2.1.0", "environment": "production",
     "status": "success", "timestamp": "2025-01-15T14:30:00"},
    {"app": "web-api", "version": "2.0.9", "environment": "staging",
     "status": "success", "timestamp": "2025-01-15T10:00:00"},
    {"app": "worker", "version": "1.5.0", "environment": "production",
     "status": "success", "timestamp": "2025-01-14T16:00:00"},
    {"app": "web-api", "version": "2.2.0", "environment": "staging",
     "status": "failed", "timestamp": "2025-01-15T18:00:00"},
    {"app": "worker", "version": "1.6.0", "environment": "staging",
     "status": "pending", "timestamp": "2025-01-15T20:00:00"},
]


# ============================================================
# TASK 1: CommandParser class
#
# Parses text commands into structured objects.
#
# SUPPORTED COMMANDS:
#   "add-server <name> <ip> <role>"
#   "remove-server <name>"
#   "list-servers [--role <role>] [--status <status>]"
#   "server-status <name>"
#   "deploy <app> <version> <environment>"
#   "list-deployments [--app <app>] [--env <env>]"
#   "health-check [<server_name>]"
#   "report"
#   "generate-config <type>"  (type: nginx, dockerfile, k8s)
#   "help"
#
# parse(self, input_string):
#   - Return a dict with:
#     "command": the command name (string)
#     "args": list of positional arguments
#     "options": dict of --flag values
#     "valid": True if command is recognized, False otherwise
#     "raw": the original input string
#
# Examples:
#   parse("add-server web-03 10.0.1.3 web")
#   -> {"command": "add-server", "args": ["web-03", "10.0.1.3", "web"],
#       "options": {}, "valid": True, "raw": "add-server web-03 10.0.1.3 web"}
#
#   parse("list-servers --role web --status healthy")
#   -> {"command": "list-servers", "args": [],
#       "options": {"role": "web", "status": "healthy"},
#       "valid": True, "raw": "..."}
#
#   parse("unknown-cmd")
#   -> {"command": "unknown-cmd", "args": [], "options": {},
#       "valid": False, "raw": "unknown-cmd"}
# ============================================================

VALID_COMMANDS = [
    "add-server", "remove-server", "list-servers", "server-status",
    "deploy", "list-deployments", "health-check", "report",
    "generate-config", "help",
]


class CommandParser:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: ReportGenerator class
#
# Generates formatted text reports from platform data.
#
# __init__(self, servers, deployments):
#   - servers: dict of name -> server dict (like SAMPLE_SERVERS)
#   - deployments: list of deployment dicts (like SAMPLE_DEPLOYMENTS)
#
# server_report(self):
#   - Return a formatted string report:
#
#   ============================================
#   SERVER INVENTORY REPORT
#   Generated: 2025-01-15 14:30:00
#   ============================================
#
#   Total Servers: 6
#   Healthy: 5 | Degraded: 1 | Unhealthy: 0 | Offline: 0
#
#   By Role:
#     web:        2 servers
#     database:   2 servers
#     cache:      1 servers
#     monitoring: 1 servers
#
#   Server Details:
#     cache-01    10.0.3.1    cache        [healthy]
#     db-01       10.0.2.1    database     [healthy]
#     db-02       10.0.2.2    database     [degraded]
#     mon-01      10.0.4.1    monitoring   [healthy]
#     web-01      10.0.1.1    web          [healthy]
#     web-02      10.0.1.2    web          [healthy]
#
#   ============================================
#
# deployment_report(self):
#   - Return a formatted string report:
#
#   ============================================
#   DEPLOYMENT REPORT
#   Generated: 2025-01-15 14:30:00
#   ============================================
#
#   Total Deployments: 5
#   Success: 3 | Failed: 1 | Pending: 1
#   Success Rate: 60.0%
#
#   Recent Deployments:
#     [2025-01-15T18:00:00] web-api v2.2.0 -> staging     [failed]
#     [2025-01-15T14:30:00] web-api v2.1.0 -> production  [success]
#     ...
#
#   By Application:
#     web-api: 3 deployments
#     worker:  2 deployments
#
#   ============================================
#
# full_report(self):
#   - Combine server_report() and deployment_report()
#   - With a blank line between them
# ============================================================

class ReportGenerator:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: ConfigGenerator class
#
# Generates configuration files from server inventory.
#
# __init__(self, servers):
#   - servers: dict of name -> server dict
#
# generate_nginx_upstream(self):
#   - Generate nginx upstream config for all "web" role servers
#   - Return string:
#     upstream backend {
#         server 10.0.1.1:8080;
#         server 10.0.1.2:8080;
#     }
#   - Only include servers with status "healthy"
#
# generate_prometheus_targets(self):
#   - Generate Prometheus scrape targets config (YAML-like string)
#   - Return string:
#     scrape_configs:
#       - job_name: "web"
#         static_configs:
#           - targets:
#             - "10.0.1.1:9090"
#             - "10.0.1.2:9090"
#       - job_name: "database"
#         static_configs:
#           - targets:
#             - "10.0.2.1:9090"
#     ...
#   - Group by role
#   - Use port 9090 for monitoring endpoint
#   - Only include healthy or degraded servers
#
# generate_ansible_inventory(self):
#   - Generate Ansible INI-format inventory
#   - Return string:
#     [web]
#     web-01 ansible_host=10.0.1.1
#     web-02 ansible_host=10.0.1.2
#
#     [database]
#     db-01 ansible_host=10.0.2.1
#     ...
#   - Group by role
#   - Groups sorted alphabetically
#   - Only include non-offline servers
#
# generate_all(self):
#   - Return dict with all generated configs:
#     {"nginx": nginx string,
#      "prometheus": prometheus string,
#      "ansible_inventory": ansible string}
# ============================================================

class ConfigGenerator:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: DevOpsCLI class
#
# Full CLI interface that processes commands.
#
# __init__(self, servers=None, deployments=None):
#   - Use provided data or default to SAMPLE_SERVERS/SAMPLE_DEPLOYMENTS
#   - Create CommandParser, ReportGenerator, ConfigGenerator
#   - self.output_history = []  (stores all output strings)
#
# execute(self, command_string):
#   - Parse the command using CommandParser
#   - Execute the appropriate action
#   - Return a response string
#   - Store the response in output_history
#
# Implement these command handlers:
#
# "add-server": Add server to self.servers
#   - Validate 3 args: name, ip, role
#   - Return "Server added: {name} ({ip}, {role})"
#   - On error: "Error: Server '{name}' already exists" or
#               "Error: Invalid role '{role}'"
#
# "remove-server": Remove server
#   - Validate 1 arg: name
#   - Return "Server removed: {name}"
#   - On error: "Error: Server '{name}' not found"
#
# "list-servers": List servers with optional filters
#   - Apply --role and --status filters
#   - Return formatted list:
#     "Servers (X total):\n  name    ip    role    [status]\n  ..."
#   - If none found: "No servers found matching filters"
#
# "server-status": Show single server details
#   - Return "Server: {name}\n  IP: {ip}\n  Role: {role}\n  Status: {status}"
#   - On error: "Error: Server '{name}' not found"
#
# "deploy": Record a deployment
#   - Validate 3 args: app, version, environment
#   - Return "Deployment queued: {app} v{version} -> {environment}"
#
# "list-deployments": List with optional filters
#   - Apply --app and --env filters
#   - Return formatted list of deployments (newest first)
#
# "health-check": Run health check
#   - If server_name given, check just that server
#   - Otherwise check all
#   - Return summary of results
#
# "report": Generate full report
#   - Return full_report()
#
# "generate-config": Generate config
#   - Arg: type (nginx, prometheus, ansible)
#   - Return the generated config string
#   - On invalid type: "Error: Unknown config type '{type}'. Use: nginx, prometheus, ansible"
#
# "help": Return help text listing all commands
#
# Invalid command: "Unknown command: '{cmd}'. Type 'help' for available commands."
# ============================================================

class DevOpsCLI:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: run_platform(commands)
#
# Process a list of command strings through a DevOpsCLI instance.
#
# commands: list of command strings
#
# Return a list of result dicts:
# [
#   {"command": "add-server web-03 10.0.1.3 web",
#    "output": "Server added: web-03 (10.0.1.3, web)",
#    "success": True},
#   ...
# ]
#
# "success" is True if the output does NOT start with "Error:"
# and is NOT "Unknown command"
# ============================================================

def run_platform(commands):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    commands = [
        "help",
        "list-servers",
        "list-servers --role web",
        "server-status web-01",
        "add-server lb-01 10.0.5.1 loadbalancer",
        "deploy auth-service 1.0.0 staging",
        "list-deployments --app web-api",
        "report",
        "generate-config nginx",
        "generate-config prometheus",
        "generate-config ansible",
        "health-check web-01",
        "remove-server lb-01",
        "unknown-command",
    ]

    results = run_platform(commands)
    if results:
        for r in results:
            print(f"\n>>> {r['command']}")
            print(f"{'[OK]' if r['success'] else '[FAIL]'}")
            output = r['output']
            if len(output) > 200:
                print(f"{output[:200]}...")
            else:
                print(output)
