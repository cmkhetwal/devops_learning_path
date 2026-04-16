"""
Week 3, Day 3: Exercise - Tuples & Sets

Practice using tuples for immutable configs and sets for unique collections.
DevOps themed: IP allowlists, server configs, and log analysis.

Run `python3 check.py` when you're done to check your answers.
"""

# --------------------------------------------------
# TASK 1: Create an immutable server config (tuple)
# --------------------------------------------------
# Create a tuple called `db_config` with these 3 values (in order):
#   "db-prod.example.com", 5432, "app_database"
#
# Then create three variables by unpacking the tuple:
#   db_host  -> first element
#   db_port  -> second element
#   db_name  -> third element

# YOUR CODE HERE


# --------------------------------------------------
# TASK 2: Build an IP allowlist (set)
# --------------------------------------------------
# Create a set called `allowlist` containing these IPs:
#   "10.0.0.1", "10.0.0.2", "10.0.0.3"
#
# Then:
#   1. Add "10.0.0.4" to the allowlist
#   2. Add "10.0.0.2" again (it should have no effect)
#   3. Remove "10.0.0.3" using discard()
#
# After these steps, allowlist should contain:
#   {"10.0.0.1", "10.0.0.2", "10.0.0.4"}
#
# Create a variable `allowlist_size` that holds len(allowlist).

# YOUR CODE HERE


# --------------------------------------------------
# TASK 3: Find unique IPs from a connection log
# --------------------------------------------------
# Here's a raw connection log with duplicate IPs:
raw_log = [
    "192.168.1.1", "192.168.1.2", "192.168.1.1",
    "192.168.1.3", "192.168.1.2", "192.168.1.4",
    "192.168.1.1", "192.168.1.5", "192.168.1.3",
    "192.168.1.1", "192.168.1.2", "192.168.1.5"
]
# 1. Create a set called `unique_ips` from the raw_log list
# 2. Create a variable `total_connections` = length of raw_log
# 3. Create a variable `unique_count` = length of unique_ips

# YOUR CODE HERE


# --------------------------------------------------
# TASK 4: Compare server inventories using set operations
# --------------------------------------------------
# Two environments:
staging_servers = {"web-01", "web-02", "api-01", "db-01"}
production_servers = {"web-01", "api-01", "api-02", "db-01", "cache-01"}

# Using set operations, create:
# 1. `all_servers` -- union of both sets (every unique server)
# 2. `shared_servers` -- intersection (servers in BOTH environments)
# 3. `staging_only` -- servers ONLY in staging (not in production)
# 4. `prod_only` -- servers ONLY in production (not in staging)

# YOUR CODE HERE


# --------------------------------------------------
# TASK 5: Create a frozenset for critical ports
# --------------------------------------------------
# Create a frozenset called `critical_ports` containing: 22, 443, 5432
#
# Then create a variable called `is_ssh_critical` that is True if
# 22 is in critical_ports, False otherwise (use the `in` operator).
#
# Create a variable called `is_http_critical` that is True if
# 80 is in critical_ports, False otherwise.

# YOUR CODE HERE
