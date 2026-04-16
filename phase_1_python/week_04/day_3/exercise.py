"""
Week 4, Day 3: Scope & Variables - Exercise
============================================

Fix scope bugs and refactor global variables into proper function parameters.

Instructions:
- Complete each function below.
- Do NOT rename the functions or change their parameters.
- Run 'python check.py' to test your solutions.
"""


# TASK 1: fix_counter(items)
# --------------------------
# The function below has a scope bug. Rewrite it correctly.
# It should count how many items in the list contain "ERROR".
# Return the count as an integer.
#
# BROKEN VERSION (for reference):
#   count = 0
#   def fix_counter(items):
#       for item in items:
#           if "ERROR" in item:
#               count += 1      # BUG: can't modify global without 'global'
#       return count
#
# Your version should NOT use the 'global' keyword.
# Instead, use a local variable inside the function.
#
# Examples:
#   fix_counter(["ERROR: disk full", "INFO: started", "ERROR: timeout"])  -> 2
#   fix_counter(["INFO: all good"])                                       -> 0
#   fix_counter([])                                                       -> 0

# YOUR CODE HERE


# TASK 2: build_server_list(new_servers, existing=None)
# -----------------------------------------------------
# Write a function that safely adds new servers to an existing list.
# This avoids the mutable default argument bug.
#
# Rules:
#   - If existing is None, start with an empty list
#   - Add each server from new_servers to the list
#   - Return the final list
#   - Do NOT modify the original existing list (make a copy!)
#
# Examples:
#   build_server_list(["web-01", "web-02"])
#       -> ["web-01", "web-02"]
#
#   build_server_list(["web-03"], existing=["web-01", "web-02"])
#       -> ["web-01", "web-02", "web-03"]
#
#   # Calling twice with no existing should NOT accumulate:
#   build_server_list(["a"])   -> ["a"]
#   build_server_list(["b"])   -> ["b"]   (NOT ["a", "b"])

# YOUR CODE HERE


# TASK 3: process_metrics(metrics_list)
# -------------------------------------
# The original version used global variables. Rewrite it using only
# local variables and return values.
#
# BROKEN VERSION (for reference):
#   total = 0
#   highest = 0
#   lowest = float('inf')
#
#   def process_metrics(metrics_list):
#       global total, highest, lowest
#       for m in metrics_list:
#           total += m
#           if m > highest:
#               highest = m
#           if m < lowest:
#               lowest = m
#       return {"total": total, "highest": highest, "lowest": lowest}
#
# Your version should:
#   - Use only local variables (no 'global' keyword)
#   - Handle empty lists by returning {"total": 0, "highest": 0, "lowest": 0}
#   - Return a dict: {"total": sum, "highest": max_value, "lowest": min_value}
#
# Examples:
#   process_metrics([80, 45, 92, 15, 67])
#       -> {"total": 299, "highest": 92, "lowest": 15}
#
#   process_metrics([])
#       -> {"total": 0, "highest": 0, "lowest": 0}

# YOUR CODE HERE


# TASK 4: create_alert_checker(threshold)
# ----------------------------------------
# Write a function that RETURNS another function.
# The returned function takes a value and returns True if it exceeds
# the threshold, False otherwise.
#
# This demonstrates how enclosing scope works (the 'E' in LEGB).
#
# Examples:
#   check_cpu = create_alert_checker(90)
#   check_cpu(95)   -> True
#   check_cpu(80)   -> False
#
#   check_memory = create_alert_checker(75)
#   check_memory(80)   -> True
#   check_memory(50)   -> False

# YOUR CODE HERE


# TASK 5: safe_config_update(config, key, value)
# -----------------------------------------------
# Write a function that updates a config dictionary WITHOUT modifying
# the original. Return a NEW dictionary with the update applied.
#
# Rules:
#   - Do NOT modify the original config dictionary
#   - Return a new dictionary with all original keys plus the update
#
# Examples:
#   original = {"port": 8080, "host": "localhost"}
#   updated = safe_config_update(original, "port", 9090)
#   # updated -> {"port": 9090, "host": "localhost"}
#   # original -> {"port": 8080, "host": "localhost"}  (unchanged!)
#
#   safe_config_update({}, "debug", True)
#       -> {"debug": True}

# YOUR CODE HERE
