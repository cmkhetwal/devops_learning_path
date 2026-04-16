"""
Week 2, Day 1: If/Else Statements - Exercise
=============================================
Complete each task below. Replace '# YOUR CODE HERE' with your solution.
Run 'python check.py' when you are done to see your score!
"""

# ---------------------------------------------------------------------------
# TASK 1: HTTP Status Code Checker
# ---------------------------------------------------------------------------
# The variable 'status_code' holds an HTTP response code.
# Print the EXACT message based on the code:
#   200 -> "OK"
#   301 -> "Moved Permanently"
#   404 -> "Not Found"
#   500 -> "Internal Server Error"
#   Anything else -> "Unknown Status"
#
# Example: if status_code is 404, print "Not Found"

status_code = 404

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 2: Port Range Validator
# ---------------------------------------------------------------------------
# The variable 'port' holds a port number.
# Valid ports are between 1 and 65535 (inclusive).
#
# If the port is valid, print "Valid port"
# If the port is NOT valid, print "Invalid port"

port = 8080

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 3: Server Health Check
# ---------------------------------------------------------------------------
# The variable 'response_time' holds how long a server took to respond (in ms).
#
# If response_time is less than 200, print "HEALTHY"
# If response_time is between 200 and 500 (inclusive on both ends), print "SLOW"
# If response_time is greater than 500, print "CRITICAL"

response_time = 350

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 4: Environment Config
# ---------------------------------------------------------------------------
# The variable 'env' holds the environment name (a string).
#
# If env is "production", set the variable 'debug' to False
# If env is "development", set the variable 'debug' to True
# For any other value, set 'debug' to False
#
# After your if/elif/else, print the value of debug (just: print(debug))

env = "development"

# YOUR CODE HERE


# ---------------------------------------------------------------------------
# TASK 5: Disk Space Alert
# ---------------------------------------------------------------------------
# The variable 'disk_usage_percent' holds disk usage as a percentage (0-100).
#
# If usage is below 60, print "OK"
# If usage is 60 or above but below 80, print "WARNING"
# If usage is 80 or above but below 95, print "CRITICAL"
# If usage is 95 or above, print "EMERGENCY"

disk_usage_percent = 87

# YOUR CODE HERE
