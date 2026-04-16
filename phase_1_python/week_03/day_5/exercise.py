"""
Week 3, Day 5: Exercise - Nested Structures

Practice working with lists of dicts, dicts of lists, and deeply
nested data -- the kind you see in every cloud API response.

Run `python3 check.py` when you're done to check your answers.
"""

# --------------------------------------------------
# TASK 1: Access data in a list of dicts
# --------------------------------------------------
# Here is a server inventory (list of dictionaries):
inventory = [
    {"hostname": "web-01", "ip": "10.0.0.1", "status": "running", "cpu": 45},
    {"hostname": "web-02", "ip": "10.0.0.2", "status": "running", "cpu": 72},
    {"hostname": "db-01",  "ip": "10.0.0.3", "status": "stopped", "cpu": 0},
    {"hostname": "cache-01", "ip": "10.0.0.4", "status": "running", "cpu": 30},
    {"hostname": "monitor-01", "ip": "10.0.0.5", "status": "running", "cpu": 55},
]

# 1. Create `first_hostname` -- the hostname of the FIRST server
# 2. Create `db_ip` -- the IP address of the server at index 2
# 3. Create `total_servers` -- the total number of servers (len of inventory)

# YOUR CODE HERE


# --------------------------------------------------
# TASK 2: Filter the inventory
# --------------------------------------------------
# Using the `inventory` list above:
# 1. Create `running_servers` -- a list of dicts containing ONLY
#    servers where status is "running"
# 2. Create `running_count` -- the number of running servers (should be 4)

# YOUR CODE HERE


# --------------------------------------------------
# TASK 3: Extract data from nested structures
# --------------------------------------------------
# Using the `inventory` list above:
# 1. Create `all_hostnames` -- a list of just the hostname strings
#    Example: ["web-01", "web-02", "db-01", "cache-01", "monitor-01"]
# 2. Create `high_cpu_servers` -- a list of hostnames where cpu > 50
#    Example: ["web-02", "monitor-01"]

# YOUR CODE HERE


# --------------------------------------------------
# TASK 4: Work with a dict of lists
# --------------------------------------------------
# Create a dictionary called `server_groups` with these key-value pairs:
#   "web"      -> ["web-01", "web-02"]
#   "database" -> ["db-01"]
#   "cache"    -> ["cache-01"]
#   "monitor"  -> ["monitor-01"]
#
# Then create:
# 1. `web_servers` -- the list of web servers from server_groups
# 2. `first_web` -- the first web server name (index into the list)
# 3. `group_names` -- a list of all the keys in server_groups

# YOUR CODE HERE


# --------------------------------------------------
# TASK 5: Navigate deeply nested data
# --------------------------------------------------
# Here is a simulated cloud API response:
cloud_data = {
    "region": "us-east-1",
    "instances": [
        {
            "id": "i-001",
            "type": "t3.micro",
            "state": "running",
            "tags": {"Name": "prod-web", "Env": "production"}
        },
        {
            "id": "i-002",
            "type": "t3.large",
            "state": "stopped",
            "tags": {"Name": "dev-api", "Env": "development"}
        },
        {
            "id": "i-003",
            "type": "t3.medium",
            "state": "running",
            "tags": {"Name": "prod-db", "Env": "production"}
        }
    ]
}

# 1. Create `cloud_region` -- the value of "region"
# 2. Create `first_instance_id` -- the id of the first instance ("i-001")
# 3. Create `second_instance_name` -- the Name tag of the second instance ("dev-api")
# 4. Create `prod_instances` -- a list of dicts containing ONLY instances
#    where tags["Env"] is "production"
#    (Should contain 2 dicts: the i-001 and i-003 instances)

# YOUR CODE HERE
