"""
Week 6, Day 5: Exercise - argparse

THEME: Building a DevOps CLI Tool

You are building a command-line server management tool called "srvctl".
The tool should accept various flags and arguments to control its behavior.

Complete all 5 tasks below.

Note: For testing purposes, each function creates its own parser and
accepts an optional list of arguments (instead of reading sys.argv).
"""

import argparse


# TASK 1: Write a function that creates and returns an ArgumentParser
#         with the following arguments:
#
#   Positional:
#     "action"  -> choices: ["status", "restart", "deploy", "logs"]
#                  help: "Action to perform"
#
#   Optional:
#     "--host" / "-H"  -> default: "localhost", help: "Target hostname"
#     "--port" / "-p"  -> type: int, default: 22, help: "SSH port"
#     "--verbose" / "-v" -> action: "store_true", help: "Enable verbose output"
#
#   Parser description: "Server management CLI tool"
#
# The function should return the parser object (not the parsed args).

def create_basic_parser():
    # YOUR CODE HERE
    pass


# TASK 2: Write a function that creates a parser for a deployment tool
#         and parses the given arguments.
#
#   Arguments to define:
#     "service"        -> positional, help: "Service name to deploy"
#     "--env" / "-e"   -> required=True, choices: ["dev", "staging", "prod"]
#                         help: "Target environment"
#     "--version"      -> required=True, help: "Version to deploy (e.g., 1.2.3)"
#     "--dry-run"      -> action: "store_true", help: "Show what would be done"
#     "--replicas" / "-r" -> type: int, default: 1, help: "Number of replicas"
#
#   Parser description: "Deploy a service to an environment"
#
# The function should accept a list of argument strings and return
# the parsed args namespace.
#
# Example: parse_deploy_args(["myapp", "--env", "prod", "--version", "2.0.0"])
#   Returns: Namespace(service='myapp', env='prod', version='2.0.0',
#                      dry_run=False, replicas=1)

def parse_deploy_args(arg_list):
    # YOUR CODE HERE
    pass


# TASK 3: Write a function that creates a parser for a monitoring tool
#         that accepts multiple hosts and check types.
#
#   Arguments to define:
#     "--hosts"       -> nargs="+", required=True, help: "Hosts to monitor"
#     "--checks"      -> nargs="+", default=["ping"],
#                        choices: ["ping", "disk", "cpu", "memory", "ports"]
#                        help: "Checks to perform"
#     "--interval"    -> type=int, default=60, help: "Check interval in seconds"
#     "--alert-email" -> default=None, help: "Email for alerts"
#     "--quiet" / "-q" -> action="store_true", help: "Suppress normal output"
#
#   Parser description: "Monitor server health"
#
# The function should accept a list of argument strings and return
# the parsed args namespace.

def parse_monitor_args(arg_list):
    # YOUR CODE HERE
    pass


# TASK 4: Write a function that takes a parsed args namespace (from Task 2)
#         and returns a formatted deployment summary string.
#
# Format:
#   "Deploying <service> v<version> to <env> (<replicas> replica(s))"
#
# If dry_run is True, prepend "[DRY RUN] " to the string.
#
# Examples:
#   format_deploy_summary(Namespace(service="api", version="1.0", env="prod",
#                                   replicas=3, dry_run=False))
#   -> "Deploying api v1.0 to prod (3 replica(s))"
#
#   format_deploy_summary(Namespace(service="web", version="2.1", env="staging",
#                                   replicas=1, dry_run=True))
#   -> "[DRY RUN] Deploying web v2.1 to staging (1 replica(s))"

def format_deploy_summary(args):
    # YOUR CODE HERE
    pass


# TASK 5: Write a function that takes a parsed args namespace (from Task 3)
#         and returns a dictionary representing the monitoring configuration.
#
# The dictionary should have:
#   "hosts"     -> list of hosts
#   "checks"    -> list of checks
#   "interval"  -> interval value (int)
#   "alert"     -> the alert email, or "none" if not set (None)
#   "quiet"     -> boolean
#   "total_checks" -> len(hosts) * len(checks)  (total check operations)
#
# Example:
#   args = Namespace(hosts=["web01", "web02"], checks=["ping", "disk"],
#                    interval=30, alert_email="ops@co.com", quiet=False)
#   -> {
#       "hosts": ["web01", "web02"],
#       "checks": ["ping", "disk"],
#       "interval": 30,
#       "alert": "ops@co.com",
#       "quiet": False,
#       "total_checks": 4
#   }

def build_monitor_config(args):
    # YOUR CODE HERE
    pass


# === Do not modify below this line ===
if __name__ == "__main__":
    print("=== Task 1: Basic Parser ===")
    parser = create_basic_parser()
    if parser:
        args = parser.parse_args(["status", "--host", "web01", "-v"])
        print(f"  Action: {args.action}")
        print(f"  Host: {args.host}")
        print(f"  Port: {args.port}")
        print(f"  Verbose: {args.verbose}")

    print("\n=== Task 2: Deploy Parser ===")
    args = parse_deploy_args(["myapp", "--env", "prod", "--version", "2.0.0", "--replicas", "3"])
    if args:
        print(f"  Service: {args.service}")
        print(f"  Env: {args.env}")
        print(f"  Version: {args.version}")
        print(f"  Replicas: {args.replicas}")
        print(f"  Dry run: {args.dry_run}")

    print("\n=== Task 3: Monitor Parser ===")
    args = parse_monitor_args(["--hosts", "web01", "web02", "--checks", "ping", "disk"])
    if args:
        print(f"  Hosts: {args.hosts}")
        print(f"  Checks: {args.checks}")
        print(f"  Interval: {args.interval}")

    print("\n=== Task 4: Deploy Summary ===")
    args = parse_deploy_args(["api", "-e", "staging", "--version", "1.5.0", "--dry-run"])
    if args:
        summary = format_deploy_summary(args)
        print(f"  {summary}")

    print("\n=== Task 5: Monitor Config ===")
    args = parse_monitor_args(["--hosts", "db01", "db02", "--checks", "ping", "memory", "--interval", "30"])
    if args:
        config = build_monitor_config(args)
        if config:
            for k, v in config.items():
                print(f"  {k}: {v}")
