"""
Week 3, Day 2: Exercise - List Methods

Practice adding, removing, sorting, slicing, and transforming lists.
You're managing a server fleet!

Run `python3 check.py` when you're done to check your answers.
"""

# --------------------------------------------------
# TASK 1: Build a server fleet with append and insert
# --------------------------------------------------
# Start with an empty list called `fleet`.
# Then:
#   1. Append "web-01"
#   2. Append "web-02"
#   3. Append "db-01"
#   4. Insert "load-balancer" at the BEGINNING (index 0)
#   5. Append "cache-01"
#
# After these steps, fleet should be:
# ["load-balancer", "web-01", "web-02", "db-01", "cache-01"]

# YOUR CODE HERE


# --------------------------------------------------
# TASK 2: Remove servers from the fleet
# --------------------------------------------------
# Starting from your `fleet` list above:
#   1. Remove "cache-01" using the remove() method
#   2. Use pop() to remove the LAST item and store it
#      in a variable called `decommissioned`
#
# After these steps:
#   fleet should be: ["load-balancer", "web-01", "web-02"]
#   decommissioned should be: "db-01"

# YOUR CODE HERE


# --------------------------------------------------
# TASK 3: Sort a priority list
# --------------------------------------------------
# Given this list of server priorities (lower number = higher priority):
priorities = [5, 1, 3, 2, 4]
# 1. Sort the list in ascending order (lowest first) -- sort in place
# 2. Create a variable called `top_priority` that holds the FIRST
#    element of the sorted list

# YOUR CODE HERE


# --------------------------------------------------
# TASK 4: Slice a deployment list
# --------------------------------------------------
# Here is a list of servers in deployment order:
deploy_targets = ["app-01", "app-02", "app-03", "app-04", "app-05", "app-06"]
# 1. Create `first_batch` containing the first 3 servers (use slicing)
# 2. Create `second_batch` containing the last 3 servers (use slicing)
# 3. Create `rollback_order` that is deploy_targets reversed (use slicing, not .reverse())

# YOUR CODE HERE


# --------------------------------------------------
# TASK 5: List comprehension
# --------------------------------------------------
# Given this list of server names:
base_servers = ["web-01", "web-02", "api-01", "api-02", "db-01"]
# 1. Create `tagged_servers` -- a list where each name has "-prod" appended
#    Example: ["web-01-prod", "web-02-prod", ...]
#    Use a list comprehension.
#
# 2. Create `api_servers` -- a list containing ONLY the servers that
#    start with "api" (use a list comprehension with an if condition).
#    Hint: use the string method .startswith("api")

# YOUR CODE HERE
