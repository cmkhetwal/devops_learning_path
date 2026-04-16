"""
Week 3, Day 7: Quiz Day - 10 Code Completion Exercises

Complete each snippet to prove your data structures knowledge.
Each question tests a specific skill from this week.

Run `python3 check.py` when you're done to check your answers.
"""

# --------------------------------------------------
# Q1: Create a list and access elements
# --------------------------------------------------
# Create a list called `regions` with: "us-east-1", "us-west-2", "eu-west-1"
# Then create `first_region` (first item) and `last_region` (last item, use negative index).

# YOUR CODE HERE


# --------------------------------------------------
# Q2: List methods -- append, remove, sort
# --------------------------------------------------
# Start with this list:
ports = [443, 22, 8080, 80]
# 1. Append 3306 to the list
# 2. Remove 8080 from the list
# 3. Sort the list in ascending order (in place)
# After: ports should be [22, 80, 443, 3306]

# YOUR CODE HERE


# --------------------------------------------------
# Q3: Slicing
# --------------------------------------------------
# Given:
deploy_queue = ["srv-01", "srv-02", "srv-03", "srv-04", "srv-05"]
# Create `batch` containing the first 3 items using slicing.
# Create `remaining` containing the last 2 items using slicing.

# YOUR CODE HERE


# --------------------------------------------------
# Q4: Tuple unpacking
# --------------------------------------------------
# Create a tuple called `connection` with values: "db.example.com", 5432, "appdb"
# Then unpack it into three variables: `host`, `port`, `database`

# YOUR CODE HERE


# --------------------------------------------------
# Q5: Set -- unique values and operations
# --------------------------------------------------
# Given two lists:
morning_ips = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.1"]
evening_ips = ["10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.3"]
# 1. Create `morning_set` (set from morning_ips)
# 2. Create `evening_set` (set from evening_ips)
# 3. Create `all_day_ips` (union of both sets)
# 4. Create `always_on` (intersection -- IPs present in both)

# YOUR CODE HERE


# --------------------------------------------------
# Q6: Dictionary -- create and access
# --------------------------------------------------
# Create a dict called `container` with:
#   "image"  -> "nginx:latest"
#   "port"   -> 80
#   "status" -> "running"
# Then create `image_name` using .get() to access "image".
# Create `restart_policy` using .get() with default "always".

# YOUR CODE HERE


# --------------------------------------------------
# Q7: Dictionary -- keys, values, loop
# --------------------------------------------------
# Given:
service_ports = {"ssh": 22, "http": 80, "https": 443, "mysql": 3306}
# 1. Create `service_names` -- a list of all keys
# 2. Create `port_numbers` -- a list of all values
# 3. Create `formatted` -- a list of strings like "ssh:22", "http:80", etc.
#    Use a list comprehension over .items()

# YOUR CODE HERE


# --------------------------------------------------
# Q8: Nested dict access
# --------------------------------------------------
# Given:
pod = {
    "metadata": {
        "name": "nginx-pod",
        "namespace": "production",
        "labels": {"app": "nginx", "tier": "frontend"}
    },
    "status": {
        "phase": "Running",
        "pod_ip": "172.17.0.5"
    }
}
# Create:
# `pod_name` -- the name from metadata ("nginx-pod")
# `pod_namespace` -- the namespace from metadata ("production")
# `pod_app_label` -- the "app" label from metadata.labels ("nginx")
# `pod_phase` -- the phase from status ("Running")

# YOUR CODE HERE


# --------------------------------------------------
# Q9: List of dicts -- filter
# --------------------------------------------------
# Given:
instances = [
    {"id": "i-001", "state": "running", "type": "t3.micro"},
    {"id": "i-002", "state": "stopped", "type": "t3.large"},
    {"id": "i-003", "state": "running", "type": "t3.medium"},
    {"id": "i-004", "state": "terminated", "type": "t3.micro"},
    {"id": "i-005", "state": "running", "type": "t3.micro"},
]
# 1. Create `running_ids` -- a list of "id" values for instances
#    where state is "running". Use a list comprehension.
#    Expected: ["i-001", "i-003", "i-005"]
#
# 2. Create `micro_count` -- the number of instances where type is "t3.micro"
#    (should be 3)

# YOUR CODE HERE


# --------------------------------------------------
# Q10: Build a summary from nested data
# --------------------------------------------------
# Given:
deployments = [
    {"app": "frontend", "version": "2.1.0", "status": "success"},
    {"app": "backend",  "version": "3.4.1", "status": "failed"},
    {"app": "worker",   "version": "1.0.5", "status": "success"},
    {"app": "frontend", "version": "2.1.1", "status": "success"},
    {"app": "backend",  "version": "3.4.2", "status": "success"},
]
# Create a dict called `deploy_summary` with:
#   "total"     -> total number of deployments (5)
#   "success"   -> number of successful deployments (4)
#   "failed"    -> number of failed deployments (1)
#   "apps"      -> a SET of unique app names ({"frontend", "backend", "worker"})

# YOUR CODE HERE
