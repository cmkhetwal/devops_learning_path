"""
Week 10, Day 2: EC2 Management with boto3

EC2 INSTANCE MANAGEMENT
========================

In this exercise you will write functions to manage EC2 instances using
mock data.  These patterns map directly to real boto3 EC2 operations.

TASKS
-----
1. Parse EC2 instance data
2. Filter instances by criteria
3. Write instance management functions (start/stop)
4. Build a tag manager
5. Create an EC2 inventory report
"""


# Mock EC2 instance data (simulates describe_instances response)
MOCK_INSTANCES = [
    {
        "InstanceId": "i-0abc123def456789a",
        "InstanceType": "t3.micro",
        "State": {"Name": "running", "Code": 16},
        "LaunchTime": "2024-01-10T08:00:00Z",
        "Tags": [
            {"Key": "Name", "Value": "web-server-01"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Team", "Value": "frontend"},
        ],
        "PublicIpAddress": "54.123.45.67",
        "PrivateIpAddress": "10.0.1.10",
    },
    {
        "InstanceId": "i-0def456ghi789012b",
        "InstanceType": "t3.small",
        "State": {"Name": "running", "Code": 16},
        "LaunchTime": "2024-01-15T10:30:00Z",
        "Tags": [
            {"Key": "Name", "Value": "api-server-01"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Team", "Value": "backend"},
        ],
        "PublicIpAddress": "54.123.45.68",
        "PrivateIpAddress": "10.0.1.11",
    },
    {
        "InstanceId": "i-0ghi789jkl012345c",
        "InstanceType": "t3.medium",
        "State": {"Name": "stopped", "Code": 80},
        "LaunchTime": "2024-02-01T14:00:00Z",
        "Tags": [
            {"Key": "Name", "Value": "dev-server-01"},
            {"Key": "Environment", "Value": "development"},
            {"Key": "Team", "Value": "backend"},
        ],
        "PublicIpAddress": None,
        "PrivateIpAddress": "10.0.2.10",
    },
    {
        "InstanceId": "i-0jkl012mno345678d",
        "InstanceType": "t3.large",
        "State": {"Name": "running", "Code": 16},
        "LaunchTime": "2024-01-20T09:15:00Z",
        "Tags": [
            {"Key": "Name", "Value": "db-server-01"},
            {"Key": "Environment", "Value": "production"},
            {"Key": "Team", "Value": "database"},
        ],
        "PublicIpAddress": None,
        "PrivateIpAddress": "10.0.1.20",
    },
    {
        "InstanceId": "i-0mno345pqr678901e",
        "InstanceType": "t3.micro",
        "State": {"Name": "stopped", "Code": 80},
        "LaunchTime": "2023-12-01T12:00:00Z",
        "Tags": [
            {"Key": "Name", "Value": "test-server-01"},
            {"Key": "Environment", "Value": "testing"},
            {"Key": "Team", "Value": "qa"},
        ],
        "PublicIpAddress": None,
        "PrivateIpAddress": "10.0.3.10",
    },
]


# ============================================================
# TASK 1: Parse EC2 instance data
# ============================================================
# Write a function called `parse_instance` that:
#   - Takes one argument: instance (dict, one item from MOCK_INSTANCES)
#   - Returns a simplified dict:
#       "id"          -> InstanceId
#       "name"        -> Value of the "Name" tag (or "unnamed" if no Name tag)
#       "type"        -> InstanceType
#       "state"       -> State["Name"]
#       "environment" -> Value of the "Environment" tag (or "unknown")
#       "team"        -> Value of the "Team" tag (or "unknown")
#       "public_ip"   -> PublicIpAddress (or "N/A" if None)
#       "private_ip"  -> PrivateIpAddress
#   - Prints "Parsed: <name> (<id>) - <state>"

# YOUR CODE HERE


# ============================================================
# TASK 2: Filter instances
# ============================================================
# Write a function called `filter_instances` that:
#   - Takes two arguments: instances (list of raw instance dicts),
#     filters (dict of filter criteria)
#   - Supported filter keys:
#       "state"       -> match State["Name"]
#       "environment" -> match Environment tag value
#       "team"        -> match Team tag value
#       "type"        -> match InstanceType
#   - All filters must match (AND logic)
#   - Returns the list of matching raw instance dicts
#   - Prints "Filter matched X of Y instances"
#
# Hint: Write a helper to extract tag values from an instance dict.

# YOUR CODE HERE


# ============================================================
# TASK 3: Instance management (start/stop)
# ============================================================
# Write a function called `manage_instance` that:
#   - Takes two arguments: instance (raw dict), action (str)
#   - Actions:
#       "stop"  -> if state is "running", change to "stopped" and print
#                  "Stopping <name> (<id>)..."
#                  If already stopped, print "Instance <name> is already stopped"
#       "start" -> if state is "stopped", change to "running" and print
#                  "Starting <name> (<id>)..."
#                  If already running, print "Instance <name> is already running"
#       "terminate" -> change state to "terminated" and print
#                      "Terminating <name> (<id>)..."
#   - Returns the new state string
#
# Note: This modifies the instance dict in place (simulating the API).

# YOUR CODE HERE


# ============================================================
# TASK 4: Tag manager
# ============================================================
# Write a function called `manage_tags` that:
#   - Takes three arguments: instance (raw dict), action (str), tags (dict)
#   - actions:
#       "add"    -> add each key/value from tags dict to the instance's Tags
#                   (if a key already exists, update its value)
#       "remove" -> remove tags whose Key is in the tags dict keys
#       "list"   -> just list current tags (ignore the tags argument)
#   - Prints the action taken for each tag
#   - Returns the current list of tags after the operation
#
# Example: manage_tags(instance, "add", {"CostCenter": "eng-123"})

# YOUR CODE HERE


# ============================================================
# TASK 5: EC2 inventory report
# ============================================================
# Write a function called `ec2_inventory_report` that:
#   - Takes one argument: instances (list of raw instance dicts)
#   - Parses each instance using parse_instance()
#   - Returns a multi-line string:
#
#     EC2 Instance Inventory
#     ======================
#     NAME                 ID                      TYPE         STATE      ENV
#     <name>               <id>                    <type>       <state>    <env>
#     ...
#     ----------------------
#     Total: X instances (Y running, Z stopped)
#
#   - NAME: 20 chars, ID: 23 chars, TYPE: 12 chars, STATE: 10 chars, ENV: remainder
#   - Also prints the report

# YOUR CODE HERE


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 75)
    print("  WEEK 10, DAY 2 - EC2 Management")
    print("=" * 75)

    # Task 1 test
    print("\n--- Task 1: Parse Instance ---")
    parsed = parse_instance(MOCK_INSTANCES[0])
    for k, v in parsed.items():
        print(f"  {k}: {v}")

    # Task 2 test
    print("\n--- Task 2: Filter Instances ---")
    running = filter_instances(MOCK_INSTANCES, {"state": "running"})
    prod = filter_instances(MOCK_INSTANCES, {"environment": "production"})
    backend_running = filter_instances(MOCK_INSTANCES, {"state": "running", "team": "backend"})

    # Task 3 test
    print("\n--- Task 3: Instance Management ---")
    import copy
    test_instances = copy.deepcopy(MOCK_INSTANCES)
    manage_instance(test_instances[0], "stop")
    manage_instance(test_instances[2], "start")
    manage_instance(test_instances[4], "terminate")
    manage_instance(test_instances[0], "stop")  # already stopped

    # Task 4 test
    print("\n--- Task 4: Tag Manager ---")
    test_inst = copy.deepcopy(MOCK_INSTANCES[0])
    manage_tags(test_inst, "list", {})
    manage_tags(test_inst, "add", {"CostCenter": "eng-123", "Owner": "devops"})
    manage_tags(test_inst, "remove", {"Owner": ""})
    current_tags = manage_tags(test_inst, "list", {})
    print(f"Final tag count: {len(current_tags)}")

    # Task 5 test
    print("\n--- Task 5: EC2 Inventory Report ---")
    report = ec2_inventory_report(MOCK_INSTANCES)
    print(report)
