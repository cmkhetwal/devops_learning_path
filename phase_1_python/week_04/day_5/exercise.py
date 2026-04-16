"""
Week 4, Day 5: Modules & Imports - Exercise
============================================

Practice using imports, the standard library, and your own custom module.

Instructions:
- Complete each function below.
- Do NOT rename the functions or change their parameters.
- Run 'python check.py' to test your solutions.
"""


# TASK 1: get_system_info()
# -------------------------
# Use the 'platform' and 'os' modules to return a dictionary with:
#   "python_version" - Python version string (e.g., "3.11.5")
#   "os_name"        - Operating system name (e.g., "Linux", "Windows", "Darwin")
#   "current_dir"    - Current working directory path
#
# Hints:
#   - platform.python_version() returns the Python version
#   - platform.system() returns the OS name
#   - os.getcwd() returns the current directory
#
# Example return (values will vary):
#   {"python_version": "3.11.5", "os_name": "Linux", "current_dir": "/home/user"}

# YOUR CODE HERE


# TASK 2: dict_to_json_string(data)
# ----------------------------------
# Use the 'json' module to convert a dictionary to a JSON string.
# The JSON should be sorted by keys and indented with 2 spaces.
#
# Hints:
#   - json.dumps(data, sort_keys=True, indent=2)
#
# Examples:
#   dict_to_json_string({"name": "web-01", "port": 8080})
#   -> '{\n  "name": "web-01",\n  "port": 8080\n}'

# YOUR CODE HERE


# TASK 3: json_string_to_dict(json_str)
# --------------------------------------
# Use the 'json' module to convert a JSON string back to a dictionary.
#
# Hints:
#   - json.loads(json_str)
#
# Examples:
#   json_string_to_dict('{"name": "web-01", "port": 8080}')
#   -> {"name": "web-01", "port": 8080}

# YOUR CODE HERE


# TASK 4: use_server_utils(server_name, port)
# --------------------------------------------
# Import from the server_utils module (in this same directory) and use its
# functions to return a dictionary with:
#   "hostname"  - result of format_hostname(server_name)
#   "port_valid" - result of is_port_valid(port)
#   "status"    - result of get_server_status(50)  (hardcoded 50 for testing)
#
# Hints:
#   - from server_utils import format_hostname, is_port_valid, get_server_status
#
# Examples:
#   use_server_utils("web-01", 8080)
#   -> {"hostname": "web-01.example.com", "port_valid": True, "status": "healthy"}
#
#   use_server_utils("db 01", 99999)
#   -> {"hostname": "db-01.example.com", "port_valid": False, "status": "healthy"}

# YOUR CODE HERE


# TASK 5: get_default_config()
# ----------------------------
# Import DEFAULT_CONFIG from server_utils and return a COPY of it.
# (Return a copy so the original can't be accidentally modified.)
#
# Hints:
#   - from server_utils import DEFAULT_CONFIG
#   - Use .copy() on the dictionary
#
# Expected return:
#   {"port": 8080, "region": "us-east-1", "max_retries": 3, "timeout": 30}

# YOUR CODE HERE


# TASK 6: generate_random_hostname(prefix="server")
# --------------------------------------------------
# Use the 'random' module to generate a hostname like "server-4827".
# The number should be a random integer between 1000 and 9999.
# Return the hostname as a string.
#
# Hints:
#   - random.randint(1000, 9999)
#   - Use random.seed(42) at the start for consistent test results
#
# Note: The check.py will set the seed before calling, so just use
#       random.randint() in your function. Do NOT set the seed yourself.
#
# Format: "{prefix}-{random_number}"
# Example: generate_random_hostname("web")  -> "web-1234" (number varies)

# YOUR CODE HERE
