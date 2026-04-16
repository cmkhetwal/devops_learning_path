"""
Week 3, Day 4: Exercise - Dictionaries

Practice creating, accessing, and modifying dictionaries.
You'll work with server configs, cloud instances, and more.

Run `python3 check.py` when you're done to check your answers.
"""

# --------------------------------------------------
# TASK 1: Create a server config dictionary
# --------------------------------------------------
# Create a dictionary called `server` with these key-value pairs:
#   "hostname" -> "web-01"
#   "ip"       -> "10.0.0.5"
#   "port"     -> 80
#   "status"   -> "running"

# YOUR CODE HERE


# --------------------------------------------------
# TASK 2: Access and update values
# --------------------------------------------------
# Using the `server` dict from Task 1:
# 1. Create a variable `server_ip` that holds the value of the "ip" key
# 2. Change the "status" to "maintenance"
# 3. Add a NEW key "region" with value "us-east-1"
# 4. Create a variable `server_region` using .get() to access "region"

# YOUR CODE HERE


# --------------------------------------------------
# TASK 3: Use dictionary methods
# --------------------------------------------------
# Given this cloud instance:
instance = {
    "id": "i-0abc123",
    "type": "t3.medium",
    "state": "running",
    "az": "us-east-1a"
}
# 1. Create `instance_keys` -- a LIST of all keys (convert .keys() to list)
# 2. Create `instance_values` -- a LIST of all values (convert .values() to list)
# 3. Create `key_count` -- the number of keys in the instance dict (use len)

# YOUR CODE HERE


# --------------------------------------------------
# TASK 4: Build a dictionary and look up values
# --------------------------------------------------
# Create a dictionary called `port_names` that maps port numbers to
# their service names:
#   22   -> "SSH"
#   80   -> "HTTP"
#   443  -> "HTTPS"
#   3306 -> "MySQL"
#   5432 -> "PostgreSQL"
#
# Then:
# 1. Create `ssh_service` by looking up port 22
# 2. Create `unknown_service` by using .get() to look up port 9999
#    with a default value of "Unknown"

# YOUR CODE HERE


# --------------------------------------------------
# TASK 5: Nested dictionary
# --------------------------------------------------
# Create a dictionary called `cloud_instance` with this structure:
# {
#     "id": "i-0abc123def",
#     "type": "t3.large",
#     "network": {
#         "public_ip": "54.210.100.5",
#         "private_ip": "10.0.1.50",
#         "vpc_id": "vpc-abc123"
#     },
#     "tags": {
#         "Name": "prod-api-01",
#         "Environment": "production"
#     }
# }
#
# Then create:
# 1. `public_ip` -- the value of cloud_instance -> network -> public_ip
# 2. `instance_name` -- the value of cloud_instance -> tags -> Name

# YOUR CODE HERE
