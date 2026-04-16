"""
Week 7, Day 1: HTTP Basics - Exercise

Practice identifying HTTP methods, status codes, and understanding
the building blocks of web communication.

DevOps Context: Every API call, health check, and webhook you work
with uses HTTP. Master the fundamentals here.
"""

# ===========================================================
# TASK 1: Status Code Classifier
# ===========================================================
# Create a function that takes a status code (int) and returns
# a string describing its category and meaning.
#
# Rules:
#   200 -> "2xx Success: OK"
#   201 -> "2xx Success: Created"
#   301 -> "3xx Redirection: Moved Permanently"
#   400 -> "4xx Client Error: Bad Request"
#   401 -> "4xx Client Error: Unauthorized"
#   403 -> "4xx Client Error: Forbidden"
#   404 -> "4xx Client Error: Not Found"
#   500 -> "5xx Server Error: Internal Server Error"
#   502 -> "5xx Server Error: Bad Gateway"
#   503 -> "5xx Server Error: Service Unavailable"
#   For any other code, return "Unknown Status Code"
#
# Example:
#   classify_status(200) -> "2xx Success: OK"
#   classify_status(404) -> "4xx Client Error: Not Found"
#   classify_status(999) -> "Unknown Status Code"

def classify_status(code):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: Method Matcher
# ===========================================================
# Create a function that takes an action description (string)
# and returns the correct HTTP method.
#
# Mappings:
#   "read"   -> "GET"
#   "create" -> "POST"
#   "update" -> "PUT"
#   "delete" -> "DELETE"
#   "list"   -> "GET"
#   "fetch"  -> "GET"
#   "remove" -> "DELETE"
#   "add"    -> "POST"
#   "modify" -> "PUT"
#
# The action should be case-insensitive.
# Return "UNKNOWN" for any unrecognized action.
#
# Example:
#   get_method("create") -> "POST"
#   get_method("READ")   -> "GET"

def get_method(action):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: Build a Request Dictionary
# ===========================================================
# Create a function that builds a complete HTTP request as a
# dictionary. It should accept:
#   - method (str): HTTP method
#   - url (str): The endpoint URL
#   - headers (dict, optional): defaults to empty dict
#   - body (dict, optional): defaults to None
#
# Return a dictionary with keys: "method", "url", "headers", "body"
# The headers should ALWAYS include "Content-Type": "application/json"
# (merged with any headers passed in).
#
# Example:
#   build_request("GET", "https://api.example.com/servers")
#   Returns:
#   {
#       "method": "GET",
#       "url": "https://api.example.com/servers",
#       "headers": {"Content-Type": "application/json"},
#       "body": None
#   }
#
#   build_request("POST", "https://api.example.com/servers",
#                 headers={"Authorization": "Bearer token123"},
#                 body={"name": "web-01"})
#   Returns:
#   {
#       "method": "POST",
#       "url": "https://api.example.com/servers",
#       "headers": {"Content-Type": "application/json",
#                   "Authorization": "Bearer token123"},
#       "body": {"name": "web-01"}
#   }

def build_request(method, url, headers=None, body=None):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: Parse a Response
# ===========================================================
# Create a function that takes a response dictionary and returns
# a summary string.
#
# The response dict has keys:
#   "status_code" (int), "headers" (dict), "body" (dict or None)
#
# Return format:
#   "Status: {code} | Content-Type: {content_type} | Has Body: {yes/no}"
#
# Get content_type from headers["Content-Type"], default to "unknown"
# if the header is missing.
# "Has Body" should be "yes" if body is not None, "no" if it is None.
#
# Example:
#   parse_response({
#       "status_code": 200,
#       "headers": {"Content-Type": "application/json"},
#       "body": {"id": 1}
#   })
#   Returns: "Status: 200 | Content-Type: application/json | Has Body: yes"

def parse_response(response):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: Endpoint Builder
# ===========================================================
# Create a function that builds REST API endpoint URLs.
#
# Parameters:
#   - base_url (str): e.g., "https://api.example.com"
#   - resource (str): e.g., "servers"
#   - resource_id (int or str, optional): e.g., 42
#   - action (str, optional): e.g., "restart"
#
# Rules:
#   - base_url + "/" + resource                         (list all)
#   - base_url + "/" + resource + "/" + str(resource_id) (single item)
#   - base_url + "/" + resource + "/" + str(resource_id) + "/" + action
#     (action on item)
#   - Remove any trailing slash from base_url before building
#
# Examples:
#   build_endpoint("https://api.example.com", "servers")
#       -> "https://api.example.com/servers"
#   build_endpoint("https://api.example.com/", "servers", 42)
#       -> "https://api.example.com/servers/42"
#   build_endpoint("https://api.example.com", "servers", 42, "restart")
#       -> "https://api.example.com/servers/42/restart"

def build_endpoint(base_url, resource, resource_id=None, action=None):
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Task 1 quick test
    print("Task 1:", classify_status(200))
    print("Task 1:", classify_status(404))
    print("Task 1:", classify_status(500))

    # Task 2 quick test
    print("Task 2:", get_method("create"))
    print("Task 2:", get_method("READ"))

    # Task 3 quick test
    print("Task 3:", build_request("GET", "https://api.example.com/servers"))

    # Task 4 quick test
    print("Task 4:", parse_response({
        "status_code": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {"id": 1}
    }))

    # Task 5 quick test
    print("Task 5:", build_endpoint("https://api.example.com", "servers", 42, "restart"))
