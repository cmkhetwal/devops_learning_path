"""
Week 12, Day 3: Capstone Part 1 - Data Models & Core Functions

Build the foundation of the DevOps Automation Platform.

TASKS:
    1. Server class            - Server data model
    2. Deployment class        - Deployment record model
    3. HealthCheck class       - Health check result model
    4. ServerInventory class   - Manage server collection
    5. DeploymentTracker class - Track deployment history
"""

from datetime import datetime


# ============================================================
# TASK 1: Server class
#
# __init__(self, name, ip, role, status="healthy", metadata=None):
#   - name: unique server name (string, e.g., "web-01")
#   - ip: IP address (string, e.g., "10.0.1.1")
#   - role: server role (string, one of: "web", "database",
#           "cache", "worker", "monitoring", "loadbalancer")
#   - status: "healthy", "degraded", "unhealthy", "offline"
#             (default "healthy")
#   - metadata: dict of additional info (default {})
#   - created_at: current datetime string (ISO format, YYYY-MM-DDTHH:MM:SS)
#   - updated_at: same as created_at initially
#
# VALID_ROLES = ["web", "database", "cache", "worker", "monitoring", "loadbalancer"]
# VALID_STATUSES = ["healthy", "degraded", "unhealthy", "offline"]
#
# Validate role and status in __init__. Raise ValueError if invalid.
#
# to_dict(self):
#   - Return all fields as a dict
#
# update_status(self, new_status):
#   - Update status (validate), update updated_at
#   - Raise ValueError if invalid status
#
# __repr__: "Server(web-01, 10.0.1.1, role=web, status=healthy)"
#
# __eq__: Two servers are equal if they have the same name
# ============================================================

VALID_ROLES = ["web", "database", "cache", "worker", "monitoring", "loadbalancer"]
VALID_STATUSES = ["healthy", "degraded", "unhealthy", "offline"]


class Server:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: Deployment class
#
# __init__(self, app, version, environment, status="pending"):
#   - app: application name (string)
#   - version: version string (e.g., "2.1.0")
#   - environment: "production", "staging", "development"
#   - status: "pending", "in_progress", "success", "failed", "rolled_back"
#             (default "pending")
#   - timestamp: current datetime ISO format string
#   - completed_at: None initially
#   - duration: None initially (set when completed)
#   - deploy_id: auto-generated "{app}-{environment}-{timestamp}"
#                (replace colons with dashes in timestamp)
#
# VALID_ENVIRONMENTS = ["production", "staging", "development"]
# VALID_DEPLOY_STATUSES = ["pending", "in_progress", "success", "failed", "rolled_back"]
#
# Validate environment and status. Raise ValueError if invalid.
#
# complete(self, result_status):
#   - Set status to result_status (validate it)
#   - Set completed_at to current ISO datetime
#   - Calculate duration as string: completed_at minus timestamp
#     (just store the completed_at string; for simplicity, duration
#      can be "completed" as a string marker)
#
# to_dict(self):
#   - Return all fields as a dict
#
# __repr__: "Deployment(web-api v2.1.0 -> production [pending])"
# ============================================================

VALID_ENVIRONMENTS = ["production", "staging", "development"]
VALID_DEPLOY_STATUSES = ["pending", "in_progress", "success", "failed", "rolled_back"]


class Deployment:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: HealthCheck class
#
# __init__(self, server_name, check_type, result, message=""):
#   - server_name: name of the server checked
#   - check_type: one of "ping", "http", "tcp", "disk", "cpu", "memory"
#   - result: "pass" or "fail"
#   - message: optional detail message (default "")
#   - timestamp: current ISO datetime
#
# VALID_CHECK_TYPES = ["ping", "http", "tcp", "disk", "cpu", "memory"]
# VALID_RESULTS = ["pass", "fail"]
#
# Validate check_type and result. Raise ValueError if invalid.
#
# to_dict(self):
#   - Return all fields as a dict
#
# __repr__: "HealthCheck(web-01, ping, pass)"
# ============================================================

VALID_CHECK_TYPES = ["ping", "http", "tcp", "disk", "cpu", "memory"]
VALID_RESULTS = ["pass", "fail"]


class HealthCheck:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: ServerInventory class
#
# __init__(self):
#   - Initialize empty dict: self.servers = {} (name -> Server)
#
# add_server(self, server):
#   - Add a Server object. Raise ValueError if name already exists.
#   - Return the server.
#
# remove_server(self, name):
#   - Remove by name. Raise KeyError if not found.
#   - Return the removed server.
#
# get_server(self, name):
#   - Return Server by name, or None if not found.
#
# list_servers(self, role=None, status=None):
#   - Return list of Server objects, optionally filtered by role and/or status.
#   - Sort by name.
#
# update_server_status(self, name, new_status):
#   - Update the status of a server by name.
#   - Raise KeyError if not found.
#   - Return the updated server.
#
# get_statistics(self):
#   - Return dict with:
#     "total": total count
#     "by_role": {role: count} for each role present
#     "by_status": {status: count} for each status present
#     "healthy_percentage": float (healthy / total * 100, 0 if empty)
#
# find_servers(self, query):
#   - Search servers where name or ip contains query (case-insensitive)
#   - Return list of matching Server objects, sorted by name
# ============================================================

class ServerInventory:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: DeploymentTracker class
#
# __init__(self):
#   - Initialize empty list: self.deployments = []
#
# record_deployment(self, app, version, environment):
#   - Create a Deployment and add to list.
#   - Return the new Deployment.
#
# complete_deployment(self, deploy_id, result_status):
#   - Find deployment by deploy_id and complete it.
#   - Raise KeyError if deploy_id not found.
#   - Return the updated Deployment.
#
# get_deployments(self, app=None, environment=None, status=None):
#   - Return filtered list of Deployment objects.
#   - Filters are optional; apply all that are given.
#   - Return in reverse chronological order (newest first).
#
# get_latest_deployment(self, app, environment):
#   - Return the most recent deployment for app+environment.
#   - Return None if not found.
#
# get_statistics(self):
#   - Return dict with:
#     "total": total count
#     "by_status": {status: count}
#     "by_environment": {env: count}
#     "by_app": {app: count}
#     "success_rate": float percentage (success / total * 100, 0 if empty)
#
# rollback(self, app, environment):
#   - Find the latest successful deployment for the app+env.
#   - If found, create a new deployment with that version
#     and immediately complete it with "rolled_back" status.
#   - Return the new Deployment, or None if no successful
#     deployment found to roll back to.
# ============================================================

class DeploymentTracker:
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    print("=== Server ===")
    s = Server("web-01", "10.0.1.1", "web")
    print(f"  {s}")
    print(f"  Dict: {s.to_dict()}")

    print("\n=== Deployment ===")
    d = Deployment("web-api", "2.1.0", "production")
    print(f"  {d}")
    d.complete("success")
    print(f"  After complete: {d}")

    print("\n=== HealthCheck ===")
    hc = HealthCheck("web-01", "ping", "pass", "Response time: 2ms")
    print(f"  {hc}")

    print("\n=== ServerInventory ===")
    inv = ServerInventory()
    inv.add_server(Server("web-01", "10.0.1.1", "web"))
    inv.add_server(Server("web-02", "10.0.1.2", "web"))
    inv.add_server(Server("db-01", "10.0.2.1", "database"))
    inv.add_server(Server("cache-01", "10.0.3.1", "cache", "degraded"))
    print(f"  All: {[s.name for s in inv.list_servers()]}")
    print(f"  Web: {[s.name for s in inv.list_servers(role='web')]}")
    print(f"  Stats: {inv.get_statistics()}")

    print("\n=== DeploymentTracker ===")
    tracker = DeploymentTracker()
    d1 = tracker.record_deployment("web-api", "2.0.0", "production")
    tracker.complete_deployment(d1.deploy_id, "success")
    d2 = tracker.record_deployment("web-api", "2.1.0", "production")
    tracker.complete_deployment(d2.deploy_id, "failed")
    d3 = tracker.record_deployment("worker", "1.0.0", "staging")
    print(f"  Total: {len(tracker.deployments)}")
    print(f"  Stats: {tracker.get_statistics()}")
    rb = tracker.rollback("web-api", "production")
    if rb:
        print(f"  Rollback: {rb}")
