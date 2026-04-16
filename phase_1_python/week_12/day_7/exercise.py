"""
Week 12, Day 7: Final Graduation Assessment

20 questions covering ALL 12 weeks of the DevOps Python Path.
Each function should return the correct answer.

Run: python3 check.py   to see your graduation score!
"""

# ===========================================================
# QUESTION 1: Variables & Data Types (Week 1)
# ===========================================================
# What is the output of: type(42).__name__
#
# Return the answer as a string.

def question_1():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 2: Strings (Week 1)
# ===========================================================
# Given server_name = "web-server-01", what does
# server_name.split("-") return?
#
# Return the result as a list.

def question_2():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 3: Control Flow (Week 2)
# ===========================================================
# What is the output of this code?
#
# status_codes = [200, 404, 200, 500, 200, 404]
# count = 0
# for code in status_codes:
#     if code != 200:
#         count += 1
#
# Return the value of count (int).

def question_3():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 4: Lists (Week 3)
# ===========================================================
# Given: servers = ["web-01", "db-01", "web-02", "cache-01"]
# What does servers[-2] return?
#
# Return the answer (str).

def question_4():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 5: Dictionaries (Week 3)
# ===========================================================
# Given:
# server = {"name": "web-01", "ip": "10.0.1.1", "status": "running"}
# What does server.get("port", 8080) return?
#
# Return the answer (int).

def question_5():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 6: Functions (Week 4)
# ===========================================================
# What does **kwargs do in a function definition?
#
# Return the letter (str):
# "A": Collects extra positional arguments as a tuple
# "B": Collects extra keyword arguments as a dictionary
# "C": Makes all arguments optional
# "D": Creates a new variable scope

def question_6():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 7: Virtual Environments (Week 4)
# ===========================================================
# What is the correct command to create a virtual environment
# named "venv" and activate it on Linux?
#
# Return the letter (str):
# "A": pip install venv && source venv/activate
# "B": python3 -m venv venv && source venv/bin/activate
# "C": virtualenv --create venv && venv/activate.sh
# "D": python3 venv create && ./venv/activate

def question_7():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 8: File Handling (Week 5)
# ===========================================================
# What mode should you use to APPEND text to an existing file
# without overwriting it?
#
# Return the letter (str):
# "A": "r"
# "B": "w"
# "C": "a"
# "D": "x"

def question_8():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 9: JSON & YAML (Week 5)
# ===========================================================
# What does json.dumps({"name": "web-01", "port": 8080}) return?
#
# Return the letter (str):
# "A": A Python dictionary
# "B": A JSON-formatted string
# "C": A file object
# "D": A bytes object

def question_9():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 10: Error Handling (Week 5)
# ===========================================================
# In a try/except/else/finally block, when does the "else"
# block execute?
#
# Return the letter (str):
# "A": Always, after except
# "B": Only when an exception occurs
# "C": Only when NO exception occurs
# "D": Before the try block

def question_10():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 11: OS & Subprocess (Week 6)
# ===========================================================
# What does subprocess.run() return?
#
# Return the letter (str):
# "A": A string with stdout
# "B": An integer return code
# "C": A CompletedProcess object
# "D": A boolean (True/False)

def question_11():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 12: Regex (Week 6)
# ===========================================================
# What does re.findall(r"\d+", "Server has 4 CPUs and 16GB RAM")
# return?
#
# Return the result as a list of strings.

def question_12():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 13: HTTP & APIs (Week 7)
# ===========================================================
# Match the HTTP methods to their purpose.
# Return a dict mapping method to purpose.
#
# Methods: "GET", "POST", "PUT", "DELETE"
# Purposes (use exact strings):
#   "retrieve a resource"
#   "create a new resource"
#   "update an existing resource"
#   "remove a resource"

def question_13():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 14: OOP Basics (Week 8)
# ===========================================================
# What is the output of this code?
#
# class Server:
#     def __init__(self, name):
#         self.name = name
#         self.running = False
#     def start(self):
#         self.running = True
#         return f"{self.name} started"
#
# s = Server("web-01")
# msg = s.start()
# result = f"{msg} | running={s.running}"
#
# Return the value of result (str).

def question_14():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 15: Inheritance (Week 8)
# ===========================================================
# What keyword is used to call a parent class method from
# a child class in Python?
#
# Return the letter (str):
# "A": parent()
# "B": super()
# "C": base()
# "D": this()

def question_15():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 16: Docker (Week 9)
# ===========================================================
# In Docker, what is the difference between an image and
# a container?
#
# Return the letter (str):
# "A": They are the same thing
# "B": An image is a template; a container is a running instance of an image
# "C": A container is a template; an image is a running instance
# "D": Images are for Linux only; containers are cross-platform

def question_16():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 17: AWS (Week 10)
# ===========================================================
# Match the AWS service to its purpose.
# Return a dict mapping service to purpose.
#
# Services: "EC2", "S3", "IAM", "CloudWatch"
# Purposes (use exact strings):
#   "virtual servers"
#   "object storage"
#   "access management"
#   "monitoring and logging"

def question_17():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 18: CI/CD (Week 11)
# ===========================================================
# What is the correct order for a basic CI/CD pipeline?
#
# Return a list of strings in order:
# Steps (unordered):
#   "deploy"
#   "build"
#   "test"
#   "lint"
#
# Hint: lint -> build -> test -> deploy

def question_18():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 19: Monitoring (Week 12)
# ===========================================================
# What are the four golden signals of monitoring as defined
# by Google SRE?
#
# Return a list of 4 strings (lowercase, alphabetical order):
# The signals are: latency, traffic, errors, saturation

def question_19():
    # YOUR CODE HERE
    pass


# ===========================================================
# QUESTION 20: DevOps Scenario (Capstone)
# ===========================================================
# You need to build a Python tool that:
# - Checks server health via HTTP
# - Logs results to a file
# - Sends alerts if a server is down
# - Runs every 5 minutes
#
# Which modules/libraries would you use?
# Return a dict mapping task to module/library name.
#
# Tasks: "http_check", "logging", "alerting", "scheduling"
# Modules (use exact strings):
#   "requests"
#   "logging"
#   "smtplib"
#   "schedule"

def question_20():
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below
# ===========================================================
if __name__ == "__main__":
    for i in range(1, 21):
        func = globals()[f"question_{i}"]
        print(f"Question {i}: {func()}")
