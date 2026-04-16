"""
Week 3, Day 6: Practice Day - 5 Mini-Projects

Apply everything from Week 3: lists, tuples, sets, dicts, nested structures.
Each mini-project is a real DevOps scenario.

Run `python3 check.py` when you're done to check your answers.
"""

# ==================================================
# MINI-PROJECT 1: Contact Book (Dict Operations)
# ==================================================
# 1. Create a dictionary called `contacts` with these entries:
#      "Alice"   -> "alice@devops.com"
#      "Bob"     -> "bob@devops.com"
#      "Charlie" -> "charlie@devops.com"
#
# 2. Add a new contact: "Diana" -> "diana@devops.com"
#
# 3. Delete "Bob" from the contacts (use del)
#
# 4. Create a variable `alice_email` by looking up "Alice" with .get()
#
# 5. Create a variable `unknown_email` by looking up "Zara" with .get()
#    and a default of "not found"
#
# After all steps, contacts should have: Alice, Charlie, Diana

# YOUR CODE HERE


# ==================================================
# MINI-PROJECT 2: Server Inventory Manager (CRUD)
# ==================================================
# Start with this inventory:
server_inventory = []

# CREATE: Add these 3 servers (append each as a dict):
#   {"name": "web-01", "ip": "10.0.0.1", "status": "running"}
#   {"name": "db-01",  "ip": "10.0.0.2", "status": "running"}
#   {"name": "cache-01", "ip": "10.0.0.3", "status": "stopped"}

# UPDATE: Change the status of "cache-01" to "running"
#   (Loop through server_inventory, find the server with name "cache-01",
#    and set its "status" to "running")

# DELETE: Remove "db-01" from the inventory
#   Create a NEW list called `server_inventory` that includes only
#   servers whose name is NOT "db-01" (use a list comprehension).

# After all steps, server_inventory should be:
# [
#   {"name": "web-01", "ip": "10.0.0.1", "status": "running"},
#   {"name": "cache-01", "ip": "10.0.0.3", "status": "running"}
# ]

# Create `inventory_count` = number of servers remaining (should be 2)

# YOUR CODE HERE


# ==================================================
# MINI-PROJECT 3: Log Categorizer
# ==================================================
# Given these log entries:
log_entries = [
    "ERROR: Disk space critical on web-01",
    "INFO: Deployment started",
    "WARNING: High memory usage on db-01",
    "ERROR: Connection timeout to cache-01",
    "INFO: Health check passed",
    "INFO: Backup completed",
    "WARNING: SSL certificate expires in 7 days",
    "ERROR: Service unreachable on web-02",
]

# Categorize them into a dictionary called `categorized_logs` with:
#   "ERROR"   -> list of all ERROR log entries
#   "WARNING" -> list of all WARNING log entries
#   "INFO"    -> list of all INFO log entries
#
# Hint: loop through log_entries and check what each starts with
#       using .startswith()

# Then create:
#   `error_count`   = number of ERROR entries (should be 3)
#   `warning_count` = number of WARNING entries (should be 2)
#   `info_count`    = number of INFO entries (should be 3)

# YOUR CODE HERE


# ==================================================
# MINI-PROJECT 4: Unique IP Finder
# ==================================================
# Two access logs from different servers:
web_server_log = [
    "192.168.1.1", "10.0.0.5", "192.168.1.2", "10.0.0.5",
    "172.16.0.1", "192.168.1.1", "10.0.0.5", "192.168.1.3"
]
api_server_log = [
    "10.0.0.5", "192.168.1.4", "172.16.0.1", "192.168.1.1",
    "10.0.0.8", "192.168.1.4", "172.16.0.1", "10.0.0.5"
]

# 1. Create `web_unique` -- a set of unique IPs from web_server_log
# 2. Create `api_unique` -- a set of unique IPs from api_server_log
# 3. Create `all_unique` -- union of both sets (all unique IPs across both)
# 4. Create `common_ips` -- intersection (IPs that appear in BOTH logs)
# 5. Create `web_only` -- IPs that appear in web log but NOT api log

# YOUR CODE HERE


# ==================================================
# MINI-PROJECT 5: Infrastructure Report
# ==================================================
# Here is a multi-region infrastructure dataset:
infrastructure = {
    "us-east-1": [
        {"id": "i-001", "type": "t3.micro", "state": "running"},
        {"id": "i-002", "type": "t3.large", "state": "running"},
        {"id": "i-003", "type": "t3.micro", "state": "stopped"},
    ],
    "us-west-2": [
        {"id": "i-004", "type": "t3.medium", "state": "running"},
        {"id": "i-005", "type": "t3.micro", "state": "stopped"},
    ],
    "eu-west-1": [
        {"id": "i-006", "type": "t3.large", "state": "running"},
        {"id": "i-007", "type": "t3.large", "state": "running"},
        {"id": "i-008", "type": "t3.micro", "state": "stopped"},
    ]
}

# Build a report dictionary called `report` with:
#   "total_instances" -> total number of instances across all regions (8)
#   "running"         -> total number of running instances (5)
#   "stopped"         -> total number of stopped instances (3)
#   "by_region"       -> a dict mapping each region to its instance count
#                        {"us-east-1": 3, "us-west-2": 2, "eu-west-1": 3}
#
# Hint: Loop through infrastructure.items() to get (region, instances) pairs.
#       Then loop through instances to count states.

# YOUR CODE HERE
