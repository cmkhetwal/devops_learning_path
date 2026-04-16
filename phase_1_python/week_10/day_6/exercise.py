"""
Week 10, Day 6: Practice Day - AWS with Python

FIVE MINI-PROJECTS
==================

Complete all five projects.  Each combines patterns from Week 10.
All use simulated data -- no AWS account needed.

PROJECTS
--------
1. AWS Resource Inventory
2. Cost Analyzer
3. S3 Backup Tool
4. EC2 Fleet Manager
5. Infrastructure Report Generator
"""

import json
import os

OUTPUT_DIR = "/home/cmk/python/devops-python-path/week_10/day_6/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Shared mock data ──

MOCK_EC2_INSTANCES = [
    {"InstanceId": "i-001", "InstanceType": "t3.micro", "State": "running",
     "Name": "web-prod-01", "Environment": "production", "Team": "frontend"},
    {"InstanceId": "i-002", "InstanceType": "t3.small", "State": "running",
     "Name": "api-prod-01", "Environment": "production", "Team": "backend"},
    {"InstanceId": "i-003", "InstanceType": "t3.medium", "State": "running",
     "Name": "db-prod-01", "Environment": "production", "Team": "database"},
    {"InstanceId": "i-004", "InstanceType": "t3.micro", "State": "stopped",
     "Name": "web-dev-01", "Environment": "development", "Team": "frontend"},
    {"InstanceId": "i-005", "InstanceType": "t3.micro", "State": "stopped",
     "Name": "api-dev-01", "Environment": "development", "Team": "backend"},
    {"InstanceId": "i-006", "InstanceType": "t3.large", "State": "running",
     "Name": "ml-prod-01", "Environment": "production", "Team": "data"},
]

MOCK_S3_BUCKETS = [
    {"Name": "app-logs-prod", "Objects": 1500, "SizeGB": 25.5},
    {"Name": "app-data-prod", "Objects": 300, "SizeGB": 10.2},
    {"Name": "backups-weekly", "Objects": 52, "SizeGB": 150.0},
    {"Name": "dev-artifacts", "Objects": 800, "SizeGB": 5.8},
    {"Name": "static-assets", "Objects": 2000, "SizeGB": 3.1},
]

MOCK_IAM_USERS = [
    {"UserName": "alice", "Groups": ["developers"], "MFA": True, "LastActive": "2024-03-14"},
    {"UserName": "bob", "Groups": ["developers"], "MFA": True, "LastActive": "2024-03-15"},
    {"UserName": "charlie", "Groups": ["developers", "admins"], "MFA": True, "LastActive": "2024-03-15"},
    {"UserName": "diana", "Groups": ["admins"], "MFA": True, "LastActive": "2024-03-10"},
    {"UserName": "eve", "Groups": ["readonly"], "MFA": False, "LastActive": "2024-01-05"},
    {"UserName": "deploy-bot", "Groups": ["ci-cd"], "MFA": False, "LastActive": "2024-03-15"},
]

# Pricing data (simplified monthly costs)
INSTANCE_PRICING = {
    "t3.micro": 8.50,
    "t3.small": 17.00,
    "t3.medium": 34.00,
    "t3.large": 68.00,
    "t3.xlarge": 136.00,
    "m5.large": 77.00,
}

S3_PRICE_PER_GB = 0.023  # per month


# ============================================================
# PROJECT 1: AWS Resource Inventory
# ============================================================
# Write a function called `resource_inventory` that:
#   - Takes no arguments (uses the global MOCK data)
#   - Prints a formatted inventory:
#       AWS Resource Inventory
#       ======================
#
#       EC2 INSTANCES (X total)
#       NAME                 TYPE         STATE      ENV            TEAM
#       <name>               <type>       <state>    <env>          <team>
#       ...
#
#       S3 BUCKETS (X total)
#       BUCKET                    OBJECTS   SIZE(GB)
#       <name>                    <count>   <size>
#       ...
#
#       IAM USERS (X total)
#       USER          GROUPS                MFA     LAST ACTIVE
#       <user>        <groups>              <mfa>   <date>
#       ...
#
#   - Returns dict: {"ec2_count": X, "s3_count": X, "iam_count": X}

# YOUR CODE HERE


# ============================================================
# PROJECT 2: Cost Analyzer
# ============================================================
# Write a function called `analyze_costs` that:
#   - Takes no arguments (uses MOCK data + INSTANCE_PRICING + S3_PRICE_PER_GB)
#   - Calculates:
#       EC2 costs: only RUNNING instances, lookup price by type
#       S3 costs: SizeGB * S3_PRICE_PER_GB for each bucket
#   - Prints:
#       AWS Cost Analysis (Monthly Estimate)
#       =====================================
#       EC2 COSTS:
#         <name> (<type>): $<price>/mo
#         ...
#         Subtotal: $<total>
#
#       S3 COSTS:
#         <bucket> (<size>GB): $<cost>/mo
#         ...
#         Subtotal: $<total>
#
#       TOTAL ESTIMATED MONTHLY COST: $<grand_total>
#
#   - Returns dict: {"ec2_cost": float, "s3_cost": float, "total": float}
#     All rounded to 2 decimals.

# YOUR CODE HERE


# ============================================================
# PROJECT 3: S3 Backup Tool
# ============================================================
# Write a function called `backup_planner` that:
#   - Takes one argument: buckets_to_backup (list of bucket name strings)
#   - For each bucket name, find matching bucket in MOCK_S3_BUCKETS
#   - Create a backup plan dict:
#       "timestamp": "2024-03-15T10:00:00Z"
#       "buckets": list of {"name": str, "objects": int, "size_gb": float,
#                           "backup_name": "<name>-backup-20240315"}
#       "total_objects": sum of objects
#       "total_size_gb": sum of sizes
#       "estimated_time_min": total_size_gb * 2 (2 min per GB, round to 1 decimal)
#   - Writes plan to OUTPUT_DIR/backup_plan.json
#   - Prints:
#       Backup Plan
#       ===========
#       Buckets: X
#       Total objects: X
#       Total size: X GB
#       Estimated time: X min
#   - Returns the plan dict

# YOUR CODE HERE


# ============================================================
# PROJECT 4: EC2 Fleet Manager
# ============================================================
# Write a function called `fleet_manager` that:
#   - Takes two arguments: action (str), filters (dict)
#   - filters can have keys: "environment", "team", "state"
#   - First, find matching instances from MOCK_EC2_INSTANCES
#   - Actions:
#       "status"  -> print each matching instance's name, type, state
#       "start"   -> for stopped instances, print "Starting <name>..."
#       "stop"    -> for running instances, print "Stopping <name>..."
#       "report"  -> generate a summary
#   - Prints:
#       Fleet Manager: <action>
#       ========================
#       <action-specific output>
#       ========================
#       Matched: X instances
#   - Returns dict: {"action": str, "matched": int, "affected": int}
#     (affected = actually started/stopped; for status/report, affected = matched)

# YOUR CODE HERE


# ============================================================
# PROJECT 5: Infrastructure Report Generator
# ============================================================
# Write a function called `generate_infra_report` that:
#   - Takes no arguments
#   - Builds a comprehensive report dict:
#       {
#           "report_name": "Infrastructure Report",
#           "generated_at": "2024-03-15T10:00:00Z",
#           "ec2": {
#               "total": X, "running": X, "stopped": X,
#               "by_type": {"t3.micro": X, ...},
#               "by_environment": {"production": X, ...}
#           },
#           "s3": {
#               "total_buckets": X, "total_objects": X,
#               "total_size_gb": X
#           },
#           "iam": {
#               "total_users": X, "mfa_enabled": X,
#               "mfa_disabled": X
#           },
#           "cost_estimate": {
#               "ec2_monthly": X, "s3_monthly": X, "total_monthly": X
#           }
#       }
#   - Writes to OUTPUT_DIR/infra_report.json
#   - Prints "Infrastructure report generated: <filepath>"
#   - Returns the report dict

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  WEEK 10, DAY 6 - Practice Day")
    print("=" * 60)

    # Project 1
    print("\n--- Project 1: Resource Inventory ---")
    inv = resource_inventory()
    print(f"Inventory: {inv}")

    # Project 2
    print("\n--- Project 2: Cost Analysis ---")
    costs = analyze_costs()
    print(f"Costs: {costs}")

    # Project 3
    print("\n--- Project 3: Backup Planner ---")
    plan = backup_planner(["app-logs-prod", "app-data-prod", "backups-weekly"])
    print(f"Plan buckets: {len(plan['buckets'])}")

    # Project 4
    print("\n--- Project 4: Fleet Manager ---")
    fleet_manager("status", {"environment": "production"})
    print()
    fleet_manager("stop", {"team": "frontend"})
    print()
    result = fleet_manager("start", {"environment": "development"})
    print(f"Fleet result: {result}")

    # Project 5
    print("\n--- Project 5: Infrastructure Report ---")
    report = generate_infra_report()
    print(f"EC2 total: {report['ec2']['total']}")
    print(f"S3 buckets: {report['s3']['total_buckets']}")
    print(f"IAM users: {report['iam']['total_users']}")
    print(f"Monthly cost: ${report['cost_estimate']['total_monthly']}")
