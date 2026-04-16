"""
Week 4, Day 2: Function Arguments - Exercise
=============================================

Build flexible, reusable DevOps functions using different argument types.

Instructions:
- Complete each function below.
- Do NOT rename the functions or change their parameters.
- Run 'python check.py' to test your solutions.
"""


# TASK 1: create_instance(name, region="us-east-1", size="t2.micro", count=1)
# ---------------------------------------------------------------------------
# Write a function that returns a dictionary describing a cloud instance order.
# Return format:
#   {"name": name, "region": region, "size": size, "count": count}
#
# Examples:
#   create_instance("web-01")
#       -> {"name": "web-01", "region": "us-east-1", "size": "t2.micro", "count": 1}
#
#   create_instance("db-01", region="eu-west-1", size="r5.large", count=2)
#       -> {"name": "db-01", "region": "eu-west-1", "size": "r5.large", "count": 2}

# YOUR CODE HERE


# TASK 2: log_message(message, level="INFO", *tags)
# --------------------------------------------------
# Write a function that formats a log message.
# Return format: "[LEVEL] message #tag1 #tag2 #tag3"
# If no tags are provided, just return "[LEVEL] message"
#
# Rules:
#   - level should be uppercase in the output
#   - Each tag should be prefixed with '#' and separated by spaces
#
# Examples:
#   log_message("Server started")
#       -> "[INFO] Server started"
#
#   log_message("Deploy failed", "ERROR", "deploy", "critical")
#       -> "[ERROR] Deploy failed #deploy #critical"

# YOUR CODE HERE


# TASK 3: build_connection_string(host, port, **options)
# ------------------------------------------------------
# Write a function that builds a connection string from parts.
# Return format: "host:port?key1=value1&key2=value2"
# If no options are provided, return "host:port"
#
# Rules:
#   - port should be converted to a string
#   - Options are joined with '&' and appended after '?'
#   - Sort options alphabetically by key for consistent output
#
# Examples:
#   build_connection_string("localhost", 5432)
#       -> "localhost:5432"
#
#   build_connection_string("db.example.com", 3306, user="admin", db="myapp")
#       -> "db.example.com:3306?db=myapp&user=admin"

# YOUR CODE HERE


# TASK 4: apply_config(server_name, config_dict)
# -----------------------------------------------
# Write a function that takes a server name and a dictionary of settings.
# Return a list of strings, one per setting, in this format:
#   "server_name: key=value"
#
# Rules:
#   - Sort the settings alphabetically by key
#   - Each line: "server_name: key=value"
#
# Examples:
#   apply_config("web-01", {"port": 8080, "debug": True})
#       -> ["web-01: debug=True", "web-01: port=8080"]
#
#   apply_config("db-01", {"max_connections": 100})
#       -> ["db-01: max_connections=100"]

# YOUR CODE HERE


# TASK 5: merge_server_tags(*tag_lists)
# --------------------------------------
# Write a function that takes multiple lists of tags and merges them.
# Return a single sorted list with no duplicates.
#
# Examples:
#   merge_server_tags(["web", "prod"], ["web", "us-east"])
#       -> ["prod", "us-east", "web"]
#
#   merge_server_tags(["db"], ["cache"], ["db", "cache", "prod"])
#       -> ["cache", "db", "prod"]
#
#   merge_server_tags()
#       -> []

# YOUR CODE HERE
