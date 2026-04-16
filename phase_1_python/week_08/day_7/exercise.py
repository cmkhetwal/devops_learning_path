"""
Week 8, Day 7: Phase 2 Final Test

15 questions covering Weeks 5-8:
  - File Handling & Data Formats (Week 5)
  - Error Handling & OS Operations (Week 6)
  - Networking & APIs (Week 7)
  - OOP & Project Structure (Week 8)

Each function should return the correct answer.
"""

# ===========================================================
# QUESTION 1: File Handling
# ===========================================================
# What is the correct way to read a file safely in Python?
#
# Return the letter of the correct answer (str):
# "A": f = open("file.txt"); data = f.read()
# "B": with open("file.txt") as f: data = f.read()
# "C": data = read("file.txt")
# "D": data = file.read("file.txt")

def question_1():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 2: JSON Operations
# ===========================================================
# Match each json function to its purpose.
# Return a dict mapping function name to description.
#
# Functions: "json.load", "json.dump", "json.loads", "json.dumps"
# Descriptions (use these exact strings):
#   "read JSON from file"
#   "write JSON to file"
#   "parse JSON string to Python"
#   "convert Python to JSON string"

def question_2():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 3: Exception Handling
# ===========================================================
# What is the output of this code?
#
# try:
#     x = int("hello")
# except ValueError:
#     result = "caught"
# except TypeError:
#     result = "type error"
# else:
#     result = "success"
# finally:
#     result = result + " done"
#
# Return the value of result (str):

def question_3():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 4: OS Operations
# ===========================================================
# Which module and function creates directories including
# all parent directories that don't exist?
#
# Return the letter of the correct answer (str):
# "A": os.mkdir("a/b/c")
# "B": os.makedirs("a/b/c", exist_ok=True)
# "C": os.create_directory("a/b/c")
# "D": shutil.mkdir("a/b/c")

def question_4():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 5: subprocess
# ===========================================================
# What does subprocess.run() return when a command succeeds?
#
# Return a dict:
# {
#     "return_type": <"CompletedProcess", "string", "int", "bool">,
#     "success_returncode": <the returncode value for success (int)>,
#     "capture_flag": <the parameter name to capture output (str)>
# }

def question_5():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 6: HTTP Status Codes
# ===========================================================
# Categorize each status code.
# Return a dict mapping status code (int) to category (str).
# Categories: "success", "redirect", "client_error", "server_error"
#
# Status codes: 200, 301, 403, 404, 500, 502, 201

def question_6():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 7: requests Library
# ===========================================================
# You need to make a POST request with JSON data, custom headers,
# and a 5-second timeout. Which call is correct?
#
# Return the letter (str):
# "A": requests.post(url, data=payload, timeout=5)
# "B": requests.post(url, json=payload, headers=headers, timeout=5)
# "C": requests.send("POST", url, body=payload)
# "D": requests.post(url, json=payload, headers=headers)

def question_7():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 8: REST API Design
# ===========================================================
# Design REST endpoints for a container orchestration API.
# Return a dict mapping action to {"method": ..., "path": ...}
#
# Actions:
#   "list_pods"      -> List all pods
#   "create_pod"     -> Create a new pod
#   "get_pod"        -> Get pod named "web-01"
#   "delete_pod"     -> Delete pod named "web-01"
#   "list_pod_logs"  -> Get logs for pod "web-01"
#
# Use base path: /api/v1/pods

def question_8():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 9: Socket Programming
# ===========================================================
# You need to check if port 5432 is open on a database server.
# Which approach is correct?
#
# Return the letter (str):
# "A": socket.ping("db-server", 5432)
# "B": socket.connect_ex(("db-server", 5432)) returns 0 if open
# "C": socket.is_open("db-server", 5432)
# "D": socket.test_port("db-server", 5432)

def question_9():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 10: OOP - Classes
# ===========================================================
# What is the purpose of __init__ in a Python class?
#
# Return the letter (str):
# "A": It imports the class module
# "B": It initializes instance attributes when an object is created
# "C": It defines the class name
# "D": It creates a copy of the class

def question_10():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 11: OOP - Inheritance
# ===========================================================
# Given:
#   class Animal:
#       def speak(self): return "..."
#   class Dog(Animal):
#       def speak(self): return "Woof"
#   class Cat(Animal):
#       def speak(self): return "Meow"
#
#   d = Dog()
#   isinstance(d, Animal) -> ???
#   isinstance(d, Dog) -> ???
#   isinstance(d, Cat) -> ???
#
# Return a list of 3 booleans: [result1, result2, result3]

def question_11():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 12: Properties and Methods
# ===========================================================
# Match each decorator to its use case.
# Return a dict mapping decorator to description.
#
# Decorators: "@property", "@classmethod", "@staticmethod"
# Descriptions (use these exact strings):
#   "attribute-like access with getter/setter logic"
#   "alternative constructor or class-level operation"
#   "utility function that doesn't need self or cls"

def question_12():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 13: Project Structure
# ===========================================================
# Which file makes a directory a Python package?
#
# Return the letter (str):
# "A": setup.py
# "B": requirements.txt
# "C": __init__.py
# "D": __main__.py

def question_13():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 14: Testing
# ===========================================================
# Which of these are valid pytest practices?
# Return a list of letters that are TRUE:
#
# "A": Test functions must start with "test_"
# "B": Use assert statements for checks
# "C": Fixtures provide reusable test setup
# "D": Tests should modify production data
# "E": pytest.raises() tests for expected exceptions
# "F": Each test should test multiple unrelated features

def question_14():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 15: Complete DevOps Scenario
# ===========================================================
# You're building a deployment tool. Arrange these steps in the
# correct order for building a production-ready Python tool.
#
# Return a list of strings in the correct order:
# Steps (unordered):
#   "write unit tests"
#   "create project structure with __init__.py"
#   "define classes for infrastructure (Server, Deployment)"
#   "add error handling and logging"
#   "create requirements.txt and setup.py"
#   "set up virtual environment"
#
# Correct order (return this list):
#   1. Set up virtual environment
#   2. Create project structure
#   3. Define classes
#   4. Add error handling
#   5. Write unit tests
#   6. Create requirements.txt and setup.py

def question_15():
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below
# ===========================================================
if __name__ == "__main__":
    for i in range(1, 16):
        func = globals()[f"question_{i}"]
        print(f"Question {i}: {func()}")
