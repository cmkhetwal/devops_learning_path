"""
Week 10, Day 4: IAM & Security with boto3

IAM MANAGEMENT AND SECURITY
=============================

In this exercise you will build IAM management functions using mock data.
These patterns teach the real boto3 IAM API structure.

TASKS
-----
1. Create a MockIAM class
2. Write user management functions
3. Build a policy generator
4. Create a security audit function
5. Generate an IAM report
"""

import json
import os

OUTPUT_DIR = "/home/cmk/python/devops-python-path/week_10/day_4/output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# TASK 1: MockIAM class
# ============================================================
# Create a class called `MockIAM` with:
#   __init__(self):
#       - self.users = {}    # username -> {"arn": str, "policies": [], "groups": [], "mfa": bool}
#       - self.policies = {} # policy_name -> {"arn": str, "document": dict}
#       - self.groups = {}   # group_name -> {"arn": str, "members": [], "policies": []}
#
#   Methods:
#       create_user(username):
#           - Create user with arn="arn:aws:iam::123456789012:user/<username>"
#           - policies=[], groups=[], mfa=False
#           - Print "Created user: <username>"
#           - Return True if created, False if exists
#
#       delete_user(username):
#           - Remove from self.users
#           - Print "Deleted user: <username>" or "User not found: <username>"
#           - Return True/False
#
#       list_users():
#           - Return list of dicts: [{"UserName": name, "Arn": arn, "MFA": mfa}, ...]
#
#       attach_user_policy(username, policy_name):
#           - Add policy_name to user's policies list (if not already there)
#           - Print "Attached <policy_name> to <username>"
#           - Return True/False
#
#       create_group(group_name):
#           - Create group with arn, empty members and policies
#           - Print "Created group: <group_name>"
#           - Return True/False
#
#       add_user_to_group(username, group_name):
#           - Add username to group's members (if both exist)
#           - Also add group_name to user's groups
#           - Print "Added <username> to <group_name>"
#           - Return True/False

# YOUR CODE HERE


# ============================================================
# TASK 2: User management functions
# ============================================================
# Write a function called `setup_team` that:
#   - Takes one argument: iam (MockIAM instance)
#   - Creates these users: "alice", "bob", "charlie", "diana", "eve"
#   - Creates these groups: "developers", "admins", "readonly"
#   - Adds users to groups:
#       developers: alice, bob, charlie
#       admins: diana
#       readonly: eve
#   - Returns the result of iam.list_users()
#   - Prints "Team setup complete: X users, Y groups"

# YOUR CODE HERE


# ============================================================
# TASK 3: Policy generator
# ============================================================
# Write a function called `generate_policy` that:
#   - Takes three arguments:
#       name (str), actions (list of str), resources (list of str)
#   - Optional keyword: effect (str, default "Allow")
#   - Returns a dict in AWS policy format:
#       {
#           "Version": "2012-10-17",
#           "Statement": [
#               {
#                   "Effect": <effect>,
#                   "Action": <actions>,
#                   "Resource": <resources>
#               }
#           ]
#       }
#   - Also writes the policy JSON to OUTPUT_DIR/policy_<name>.json
#   - Prints "Generated policy: <name> (<effect>, X actions, Y resources)"
#   - Returns the policy dict

# YOUR CODE HERE


# ============================================================
# TASK 4: Security audit
# ============================================================
# Write a function called `security_audit` that:
#   - Takes one argument: iam (MockIAM instance)
#   - Checks each user and returns a list of finding dicts:
#       {"user": username, "issue": description, "severity": "high"/"medium"/"low"}
#   - Check rules:
#       1. User has no MFA enabled -> severity: "high",
#          issue: "MFA not enabled"
#       2. User has no group membership -> severity: "medium",
#          issue: "No group membership"
#       3. User has no policies attached (directly) -> severity: "low",
#          issue: "No direct policies"  (this is actually OK if using groups)
#   - Prints a formatted audit report:
#       Security Audit Report
#       =====================
#       [HIGH] <username>: <issue>
#       [MEDIUM] <username>: <issue>
#       ...
#       ---------------------
#       Total findings: X (Y high, Z medium, W low)
#   - Returns the list of findings

# YOUR CODE HERE


# ============================================================
# TASK 5: IAM inventory report
# ============================================================
# Write a function called `iam_report` that:
#   - Takes one argument: iam (MockIAM instance)
#   - Returns a multi-line string:
#
#     IAM Inventory Report
#     ====================
#     USERS:
#       <username>  Groups: [<groups>]  Policies: [<policies>]  MFA: <yes/no>
#       ...
#     GROUPS:
#       <group_name>  Members: X  Policies: [<policies>]
#       ...
#     --------------------
#     Summary: X users, Y groups
#
#   - Also prints the report

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  WEEK 10, DAY 4 - IAM & Security")
    print("=" * 60)

    # Task 1 test
    print("\n--- Task 1: MockIAM ---")
    iam = MockIAM()
    iam.create_user("testuser")
    iam.create_group("testgroup")
    iam.add_user_to_group("testuser", "testgroup")
    iam.attach_user_policy("testuser", "ReadOnlyAccess")
    users = iam.list_users()
    print(f"Users: {len(users)}")
    iam.delete_user("testuser")
    print(f"After delete: {len(iam.list_users())}")

    # Task 2 test
    print("\n--- Task 2: Team Setup ---")
    iam = MockIAM()
    team = setup_team(iam)
    print(f"Team members: {[u['UserName'] for u in team]}")

    # Task 3 test
    print("\n--- Task 3: Policy Generator ---")
    s3_read = generate_policy(
        "S3ReadOnly",
        ["s3:GetObject", "s3:ListBucket"],
        ["arn:aws:s3:::my-bucket", "arn:aws:s3:::my-bucket/*"]
    )
    ec2_manage = generate_policy(
        "EC2Manage",
        ["ec2:DescribeInstances", "ec2:StartInstances", "ec2:StopInstances"],
        ["*"]
    )
    deny_delete = generate_policy(
        "DenyDelete",
        ["s3:DeleteBucket", "ec2:TerminateInstances"],
        ["*"],
        effect="Deny"
    )
    print(f"Policy has Statement: {'Statement' in s3_read}")

    # Task 4 test
    print("\n--- Task 4: Security Audit ---")
    findings = security_audit(iam)
    print(f"Total findings: {len(findings)}")

    # Task 5 test
    print("\n--- Task 5: IAM Report ---")
    # Attach some policies for a richer report
    iam.attach_user_policy("alice", "S3ReadOnly")
    iam.attach_user_policy("diana", "AdministratorAccess")
    report = iam_report(iam)
    print(report)
