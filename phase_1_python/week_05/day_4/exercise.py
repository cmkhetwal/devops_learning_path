"""
Week 5, Day 4: Exercise - Error Handling
=========================================

Today you will practice error handling with try/except.
Complete all 5 tasks. Run check.py when finished to verify your work.
"""

import json

# === Setup: Create sample data files ===
# (Do NOT modify this section)

good_config = {"app_name": "web-service", "version": "1.0.0", "port": 8080}
with open("good_config.json", "w") as f:
    json.dump(good_config, f, indent=4)

with open("bad_config.json", "w") as f:
    f.write('{"app_name": "broken", port: INVALID}')  # Invalid JSON

# ============================================
# TASK 1: Safe file reader
# ============================================
# Write a function called safe_read_file(filepath) that:
# - Tries to open and read the file, returning its content as a string
# - If the file is not found, return the string "FILE_NOT_FOUND"
# - If any other error occurs, return the string "READ_ERROR"
#
# Test it with the calls below (do NOT modify the test calls).

# YOUR CODE HERE


result_good = safe_read_file("good_config.json")
result_missing = safe_read_file("nonexistent_file.txt")


# ============================================
# TASK 2: Safe JSON loader
# ============================================
# Write a function called safe_load_json(filepath) that:
# - Tries to open the file and parse it as JSON
# - If successful, return the parsed data (dict)
# - If the file is not found, return {"error": "file_not_found"}
# - If the JSON is invalid, return {"error": "invalid_json"}

# YOUR CODE HERE


json_good = safe_load_json("good_config.json")
json_missing = safe_load_json("no_such_file.json")
json_bad = safe_load_json("bad_config.json")


# ============================================
# TASK 3: Config validator
# ============================================
# Write a custom exception class called ConfigError that
# inherits from Exception.
#
# Then write a function called validate_config(config) that:
# - Takes a dictionary as input
# - Checks that it has the keys: "app_name", "version", "port"
# - Checks that "port" is an integer between 1 and 65535
# - If any check fails, RAISE ConfigError with a descriptive message
# - If all checks pass, return True

# YOUR CODE HERE


# Test the validator (do NOT modify these test calls)
validation_results = {}

try:
    validate_config({"app_name": "test", "version": "1.0", "port": 8080})
    validation_results["valid"] = "passed"
except ConfigError:
    validation_results["valid"] = "failed"

try:
    validate_config({"app_name": "test", "version": "1.0"})
    validation_results["missing_port"] = "passed"
except ConfigError as e:
    validation_results["missing_port"] = str(e)

try:
    validate_config({"app_name": "test", "version": "1.0", "port": 99999})
    validation_results["bad_port"] = "passed"
except ConfigError as e:
    validation_results["bad_port"] = str(e)

try:
    validate_config({"version": "1.0", "port": 8080})
    validation_results["missing_name"] = "passed"
except ConfigError as e:
    validation_results["missing_name"] = str(e)


# ============================================
# TASK 4: Error-collecting processor
# ============================================
# Write a function called process_server_list(servers) that:
# - Takes a list of server dictionaries
# - For each server, tries to access "hostname" and "port" keys
# - Returns a tuple: (successes, errors)
#   - successes: list of strings like "web-01:8080"
#   - errors: list of strings describing what went wrong
#
# Each server dict might be:
# - A valid dict with "hostname" and "port" keys
# - A dict missing one or both keys (KeyError)
# - Not a dict at all (TypeError/AttributeError)

# YOUR CODE HERE


test_servers = [
    {"hostname": "web-01", "port": 8080},
    {"hostname": "web-02", "port": 443},
    {"hostname": "web-03"},               # Missing port
    "not-a-dict",                          # Not a dictionary
    {"hostname": "db-01", "port": 5432},
]

successes, errors = process_server_list(test_servers)


# ============================================
# TASK 5: try/except/else/finally
# ============================================
# Write a function called load_and_validate(filepath) that:
# - Uses try to open and parse a JSON file
# - In the except block: if any error occurs, set result to
#   {"status": "error", "message": str(e)} where e is the exception
# - In the else block (no error): set result to
#   {"status": "ok", "data": <the parsed data>}
# - In the finally block: set result["attempted_file"] = filepath
# - Return result

# YOUR CODE HERE


load_result_good = load_and_validate("good_config.json")
load_result_bad = load_and_validate("bad_config.json")
load_result_missing = load_and_validate("no_file.json")


# === Display Results ===
print("=" * 50)
print("RESULTS")
print("=" * 50)
print(f"Task 1 - good file: {result_good[:50] if result_good else None}...")
print(f"Task 1 - missing file: {result_missing}")
print(f"Task 2 - good json: {json_good}")
print(f"Task 2 - missing json: {json_missing}")
print(f"Task 2 - bad json: {json_bad}")
print(f"Task 3 - validations: {validation_results}")
print(f"Task 4 - successes: {successes}")
print(f"Task 4 - errors: {errors}")
print(f"Task 5 - good: {load_result_good}")
print(f"Task 5 - bad: {load_result_bad}")
print(f"Task 5 - missing: {load_result_missing}")
