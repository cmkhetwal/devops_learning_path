"""
Week 7, Day 7: Quiz Day - Networking & APIs

Answer 10 questions about networking, HTTP, APIs, sockets, and SSH.
Each function should return the correct answer.

DevOps Context: These questions test the networking knowledge
every DevOps engineer needs for daily work.
"""

# ===========================================================
# QUESTION 1: HTTP Status Codes
# ===========================================================
# A deployment script gets a 503 response from a health check.
# What does this mean and what category is it?
#
# Return a dictionary:
#   {
#       "status_code": 503,
#       "meaning": <one of: "OK", "Created", "Bad Request", "Unauthorized",
#                   "Forbidden", "Not Found", "Service Unavailable",
#                   "Internal Server Error", "Bad Gateway">,
#       "category": <one of: "success", "redirect", "client_error", "server_error">,
#       "action": <one of: "retry later", "fix client request", "check credentials",
#                  "check URL", "check server logs", "no action needed">
#   }

def question_1():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 2: HTTP Methods
# ===========================================================
# Match each operation to the correct HTTP method.
# Return a dictionary mapping operation to method.
#
# Operations: "list_servers", "create_server", "update_server",
#             "delete_server", "get_server_details"
#
# Methods: "GET", "POST", "PUT", "DELETE"

def question_2():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 3: requests Library
# ===========================================================
# What is the correct way to make a POST request with JSON data
# and a timeout using the requests library?
#
# Return the letter of the correct answer (str):
# "A": requests.post(url, body=data, time=5)
# "B": requests.post(url, json=data, timeout=5)
# "C": requests.post(url, data=json.dumps(data), timeout=5)
# "D": requests.send("POST", url, json=data)

def question_3():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 4: Response Handling
# ===========================================================
# Given this code, what will 'result' contain?
#
#   response = requests.get("https://api.example.com/users")
#   result = response.json()
#
# Return the letter of the correct answer (str):
# "A": A JSON string
# "B": A Python dictionary or list (parsed JSON)
# "C": A Response object
# "D": The raw bytes of the response

def question_4():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 5: REST API Design
# ===========================================================
# You need to design REST endpoints for managing Docker containers.
# Return a dictionary with the correct HTTP method and URL path
# for each action.
#
# Actions:
#   "list_containers"  -> method and path
#   "create_container" -> method and path
#   "get_container"    -> method and path (for container id "abc123")
#   "delete_container" -> method and path (for container id "abc123")
#   "restart_container"-> method and path (for container id "abc123")
#
# Use these URL patterns:
#   /api/v1/containers
#   /api/v1/containers/{id}
#   /api/v1/containers/{id}/restart
#
# Return format: {"action_name": {"method": "...", "path": "..."}}

def question_5():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 6: Socket Programming
# ===========================================================
# What does socket.connect_ex() return when a port is OPEN?
#
# Return the letter of the correct answer (str):
# "A": True
# "B": False
# "C": 0
# "D": 1
# "E": The port number

def question_6():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 7: Common Ports
# ===========================================================
# Match each port number to its service.
# Return a dictionary: {port_number: "service_name"}
#
# Ports: 22, 80, 443, 3306, 5432, 6379
# Services: "SSH", "HTTP", "HTTPS", "MySQL", "PostgreSQL", "Redis"

def question_7():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 8: Error Handling
# ===========================================================
# Put these exception types in order from MOST specific to
# LEAST specific for requests error handling.
#
# Return a list of strings in order (most specific first):
#   "Timeout", "ConnectionError", "HTTPError", "RequestException"
#
# Hint: RequestException is the base class. The others inherit from it.

def question_8():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 9: SSH Concepts
# ===========================================================
# Which SSH authentication method is MORE SECURE for production?
#
# Return the letter of the correct answer (str):
# "A": Password authentication
# "B": SSH key-based authentication
# "C": Both are equally secure
# "D": Neither is secure

def question_9():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 10: API Best Practices
# ===========================================================
# Which of these are best practices for production API calls?
# Return a list of the letters that are TRUE (list of str):
#
# "A": Always set a timeout on requests
# "B": Never handle exceptions - let them crash the program
# "C": Use sessions when making multiple requests to the same API
# "D": Hardcode API keys directly in your source code
# "E": Implement retry logic for transient failures
# "F": Check response status codes before using the data

def question_10():
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    for i in range(1, 11):
        func = globals()[f"question_{i}"]
        print(f"Question {i}: {func()}")
