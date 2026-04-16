#!/usr/bin/env python3
"""
DevOps Python Learning Path - Weekly Quiz System
Usage: python3 quiz.py <week_number>
Example: python3 quiz.py 1
"""

import json
import os
import sys
import random

PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress", "progress.json")

# ================================================================
# QUIZ BANK - 10 questions per week
# Each question: (question_text, options_list, correct_index, explanation)
# ================================================================

QUIZZES = {
    1: {
        "title": "Week 1: Python Basics - Variables, Types, Strings",
        "questions": [
            (
                'What does print("Hello") do?',
                ["A) Saves Hello to a file", "B) Displays Hello on screen", "C) Creates a variable called Hello", "D) Nothing"],
                1,
                "print() displays output to the screen/terminal."
            ),
            (
                "Which is a valid variable name?",
                ["A) 2server", "B) server-name", "C) server_name", "D) class"],
                2,
                "Variable names use underscores, not hyphens, can't start with numbers, can't be keywords."
            ),
            (
                'What is the type of: x = 3.14?',
                ["A) str", "B) int", "C) float", "D) bool"],
                2,
                "Numbers with decimals are floats."
            ),
            (
                'What does int("42") return?',
                ["A) The string '42'", "B) The integer 42", "C) An error", "D) True"],
                1,
                "int() converts a string containing a number to an integer."
            ),
            (
                'What is the output of: print("CPU" + ":" + "80%")?',
                ["A) CPU : 80%", "B) CPU:80%", "C) CPU + : + 80%", "D) Error"],
                1,
                "String concatenation with + joins strings with no spaces."
            ),
            (
                'What does input("Enter name: ") do?',
                ["A) Prints 'Enter name: '", "B) Waits for user to type something", "C) Both A and B", "D) Creates a variable"],
                2,
                "input() displays the prompt AND waits for user input."
            ),
            (
                "What is 17 % 5?",
                ["A) 3.4", "B) 3", "C) 2", "D) 12"],
                2,
                "% is modulo (remainder). 17 / 5 = 3 remainder 2."
            ),
            (
                "What is 2 ** 3?",
                ["A) 6", "B) 8", "C) 5", "D) 23"],
                1,
                "** is exponentiation. 2 ** 3 = 2 * 2 * 2 = 8."
            ),
            (
                'What does "hello".upper() return?',
                ["A) Hello", "B) HELLO", "C) hello", "D) hELLO"],
                1,
                ".upper() converts all characters to uppercase."
            ),
            (
                'What does f"Port: {8080}" produce?',
                ["A) Port: {8080}", "B) Port: 8080", "C) Error", "D) f'Port: 8080'"],
                1,
                "f-strings replace {expression} with the value of the expression."
            ),
        ]
    },
    2: {
        "title": "Week 2: Control Flow - Conditions & Loops",
        "questions": [
            (
                "What keyword starts a conditional check?",
                ["A) check", "B) when", "C) if", "D) condition"],
                2,
                "if is the keyword for conditional statements in Python."
            ),
            (
                "What does 'elif' mean?",
                ["A) else if", "B) else loop", "C) end if", "D) evaluate if"],
                0,
                "elif is short for 'else if' - another condition to check."
            ),
            (
                'What is the output?\nx = 10\nif x > 5:\n    print("A")\nelse:\n    print("B")',
                ["A) A", "B) B", "C) AB", "D) Error"],
                0,
                "10 > 5 is True, so the if block runs, printing 'A'."
            ),
            (
                "Which operator means 'AND both must be true'?",
                ["A) or", "B) and", "C) not", "D) &&"],
                1,
                "Python uses 'and' (not && like other languages)."
            ),
            (
                "What does 'break' do in a loop?",
                ["A) Pauses the loop", "B) Skips to next iteration", "C) Exits the loop completely", "D) Restarts the loop"],
                2,
                "break immediately exits the loop."
            ),
            (
                "What does 'continue' do in a loop?",
                ["A) Exits the loop", "B) Skips to the next iteration", "C) Pauses", "D) Restarts from beginning"],
                1,
                "continue skips the rest of the current iteration and goes to the next."
            ),
            (
                "How many times does this loop run?\nfor i in range(5):\n    print(i)",
                ["A) 4", "B) 5", "C) 6", "D) Infinite"],
                1,
                "range(5) gives 0,1,2,3,4 - that's 5 iterations."
            ),
            (
                "What does range(2, 10, 3) produce?",
                ["A) 2, 5, 8", "B) 2, 5, 8, 11", "C) 3, 6, 9", "D) 2, 4, 6, 8"],
                0,
                "range(start, stop, step): starts at 2, increments by 3, stops before 10."
            ),
            (
                "When does a while loop stop?",
                ["A) After 10 iterations", "B) When its condition becomes False", "C) When it hits return", "D) Never"],
                1,
                "A while loop keeps running as long as its condition is True."
            ),
            (
                "What is wrong with: while True: print('hi')?",
                ["A) Syntax error", "B) It runs forever (infinite loop)", "C) It prints nothing", "D) Nothing, it's fine"],
                1,
                "while True with no break creates an infinite loop."
            ),
        ]
    },
    3: {
        "title": "Week 3: Data Structures - Lists, Dicts, Sets",
        "questions": [
            (
                "How do you create an empty list?",
                ["A) list = {}", "B) list = []", "C) list = ()", "D) list = empty"],
                1,
                "Square brackets [] create a list. {} is a dict, () is a tuple."
            ),
            (
                'What does servers = ["a","b","c"]; print(servers[1]) show?',
                ["A) a", "B) b", "C) c", "D) Error"],
                1,
                "List indexing starts at 0. Index 1 is the second element."
            ),
            (
                "Which method adds an item to the END of a list?",
                ["A) .add()", "B) .insert()", "C) .append()", "D) .push()"],
                2,
                ".append() adds to the end. .insert() adds at a specific position."
            ),
            (
                "What makes a tuple different from a list?",
                ["A) Tuples are faster", "B) Tuples can't be changed (immutable)", "C) Tuples are sorted", "D) Tuples can't hold strings"],
                1,
                "Tuples are immutable - once created, you can't add/remove/change elements."
            ),
            (
                "What is special about a set?",
                ["A) It's sorted", "B) It only holds numbers", "C) It has no duplicate values", "D) It's immutable"],
                2,
                "Sets automatically remove duplicates. {1,2,2,3} becomes {1,2,3}."
            ),
            (
                'How do you access a dictionary value?\nserver = {"name": "web-01", "port": 80}',
                ['A) server[0]', 'B) server["name"]', 'C) server.name', 'D) server(name)'],
                1,
                "Dictionary values are accessed by their key in square brackets."
            ),
            (
                "What does .get('key', 'default') do that ['key'] doesn't?",
                ["A) It's faster", "B) Returns a default value instead of error if key missing", "C) It searches nested dicts", "D) No difference"],
                1,
                ".get() returns the default value if the key doesn't exist, avoiding KeyError."
            ),
            (
                'What does {"a":1, "b":2}.keys() return?',
                ["A) [1, 2]", "B) ['a', 'b']", "C) [('a',1), ('b',2)]", "D) {'a', 'b'}"],
                1,
                ".keys() returns the dictionary's keys."
            ),
            (
                "How do you loop through a dict's keys AND values?",
                ["A) for k,v in d.items()", "B) for k,v in d.values()", "C) for k,v in d", "D) for k,v in d.keys()"],
                0,
                ".items() returns key-value pairs as tuples for iteration."
            ),
            (
                'What is servers[-1] if servers = ["a", "b", "c"]?',
                ["A) a", "B) b", "C) c", "D) Error"],
                2,
                "Negative indexing: -1 is the last element."
            ),
        ]
    },
    4: {
        "title": "Week 4: Functions & Modules (Phase 1 Finale)",
        "questions": [
            (
                "What keyword defines a function?",
                ["A) function", "B) func", "C) def", "D) define"],
                2,
                "Python uses 'def' to define functions."
            ),
            (
                "What does 'return' do in a function?",
                ["A) Prints a value", "B) Sends a value back to the caller", "C) Stops the program", "D) Creates a variable"],
                1,
                "return sends a value back to wherever the function was called."
            ),
            (
                "What is a default parameter?\ndef connect(host, port=22):",
                ["A) A parameter that must be provided", "B) A parameter with a pre-set value if not given", "C) The first parameter", "D) A global variable"],
                1,
                "port=22 means if no port is specified, it defaults to 22."
            ),
            (
                "What does *args allow?",
                ["A) Only keyword arguments", "B) Any number of positional arguments", "C) Only one argument", "D) No arguments"],
                1,
                "*args collects extra positional arguments into a tuple."
            ),
            (
                "What is variable scope?",
                ["A) The size of a variable", "B) Where a variable can be accessed", "C) The type of a variable", "D) How long a variable exists"],
                1,
                "Scope determines where in the code a variable is accessible."
            ),
            (
                "What does lambda x: x * 2 create?",
                ["A) A loop", "B) A small anonymous function", "C) A variable", "D) A class"],
                1,
                "lambda creates a small inline function without using def."
            ),
            (
                "What does filter() do?",
                ["A) Sorts items", "B) Keeps items that pass a test", "C) Transforms items", "D) Counts items"],
                1,
                "filter() keeps only items for which the function returns True."
            ),
            (
                "What does 'import os' do?",
                ["A) Creates an operating system", "B) Loads the os module for use", "C) Installs the os package", "D) Runs an OS command"],
                1,
                "import loads a module so you can use its functions."
            ),
            (
                "What does if __name__ == '__main__': check?",
                ["A) If the file exists", "B) If it's being run directly (not imported)", "C) If the function is named main", "D) Nothing useful"],
                1,
                "This check runs code only when the file is executed directly, not when imported."
            ),
            (
                "What command creates a virtual environment?",
                ["A) pip install venv", "B) python3 -m venv myenv", "C) virtualenv --create", "D) pip venv create"],
                1,
                "python3 -m venv creates an isolated Python environment."
            ),
        ]
    },
    5: {
        "title": "Week 5: File Handling & Error Management",
        "questions": [
            (
                "What mode opens a file for reading?",
                ['A) "w"', 'B) "r"', 'C) "a"', 'D) "x"'],
                1,
                '"r" is read mode (the default).'
            ),
            (
                "Why use 'with open()' instead of just 'open()'?",
                ["A) It's faster", "B) It automatically closes the file", "C) It creates the file", "D) No difference"],
                1,
                "'with' ensures the file is properly closed even if an error occurs."
            ),
            (
                "What Python module parses JSON?",
                ["A) yaml", "B) csv", "C) json", "D) parse"],
                2,
                "The built-in json module handles JSON parsing and writing."
            ),
            (
                "What does json.loads(string) do?",
                ["A) Loads a JSON file", "B) Converts JSON string to Python dict/list", "C) Saves to JSON", "D) Validates JSON"],
                1,
                "json.loads() parses a JSON string into Python objects."
            ),
            (
                "What does 'try/except' do?",
                ["A) Tries to optimize code", "B) Catches and handles errors gracefully", "C) Tests code speed", "D) Tries different approaches"],
                1,
                "try/except catches errors so your program doesn't crash."
            ),
            (
                "What exception occurs when a file doesn't exist?",
                ["A) ValueError", "B) TypeError", "C) FileNotFoundError", "D) IOError"],
                2,
                "FileNotFoundError is raised when trying to open a non-existent file."
            ),
            (
                "What does the 'finally' block do?",
                ["A) Runs only if no error", "B) Runs only on error", "C) Always runs, error or not", "D) Runs after the program ends"],
                2,
                "'finally' always executes, making it useful for cleanup tasks."
            ),
            (
                "What logging level is most severe?",
                ["A) DEBUG", "B) INFO", "C) WARNING", "D) CRITICAL"],
                3,
                "Levels: DEBUG < INFO < WARNING < ERROR < CRITICAL."
            ),
            (
                'What does "a" mode do when opening a file?',
                ["A) Creates a new file", "B) Reads a file", "C) Appends to the end of a file", "D) Archives a file"],
                2,
                '"a" mode appends - adds new data to the end without deleting existing content.'
            ),
            (
                "What format is most commonly used for DevOps config files?",
                ["A) CSV", "B) XML", "C) YAML", "D) HTML"],
                2,
                "YAML is the standard for Kubernetes, Docker Compose, Ansible, etc."
            ),
        ]
    },
    6: {
        "title": "Week 6: OS & System Automation",
        "questions": [
            (
                "What module lets you interact with the operating system?",
                ["A) sys", "B) os", "C) platform", "D) shell"],
                1,
                "The 'os' module provides OS-level functions (files, env vars, paths)."
            ),
            (
                "How do you get an environment variable in Python?",
                ['A) os.getenv("VAR")', 'B) env.get("VAR")', 'C) os.env["VAR"]', 'D) getenv("VAR")'],
                0,
                "os.getenv() safely retrieves environment variables."
            ),
            (
                "What module runs shell commands from Python?",
                ["A) shell", "B) os.system", "C) subprocess", "D) commands"],
                2,
                "subprocess is the recommended way to run shell commands."
            ),
            (
                "What does subprocess.run() return?",
                ["A) A string", "B) A CompletedProcess object", "C) An integer", "D) Nothing"],
                1,
                "It returns a CompletedProcess with returncode, stdout, stderr."
            ),
            (
                "What module provides modern file path handling?",
                ["A) os.path", "B) pathlib", "C) filepath", "D) fs"],
                1,
                "pathlib provides an object-oriented approach to file paths."
            ),
            (
                "What does a regex pattern r'\\d+' match?",
                ["A) Any letters", "B) One or more digits", "C) Whitespace", "D) Special characters"],
                1,
                "\\d matches digits, + means one or more."
            ),
            (
                "What module handles command-line arguments?",
                ["A) sys.argv only", "B) argparse", "C) getopt", "D) cli"],
                1,
                "argparse is the standard library for building CLI argument parsers."
            ),
            (
                "What does shutil.copy() do?",
                ["A) Copies a directory", "B) Copies a single file", "C) Moves a file", "D) Deletes and recreates"],
                1,
                "shutil.copy() copies a file to a new location."
            ),
            (
                "How do you list all files in a directory?",
                ["A) os.listdir(path)", "B) os.files(path)", "C) dir.list(path)", "D) list(path)"],
                0,
                "os.listdir() returns a list of entries in the directory."
            ),
            (
                "What does os.path.exists(path) check?",
                ["A) If path is a file", "B) If path is a directory", "C) If path exists (file or dir)", "D) If path is readable"],
                2,
                "os.path.exists() returns True if the path exists, regardless of type."
            ),
        ]
    },
    7: {
        "title": "Week 7: Networking & APIs",
        "questions": [
            (
                "What HTTP status code means 'success'?",
                ["A) 404", "B) 500", "C) 200", "D) 301"],
                2,
                "200 OK means the request was successful."
            ),
            (
                "What Python library is used for HTTP requests?",
                ["A) http", "B) urllib", "C) requests", "D) wget"],
                2,
                "The 'requests' library is the most popular for HTTP calls."
            ),
            (
                "What does requests.get(url) do?",
                ["A) Downloads a file", "B) Sends an HTTP GET request", "C) Opens a browser", "D) Pings the server"],
                1,
                "requests.get() sends an HTTP GET request to retrieve data."
            ),
            (
                "What does response.json() return?",
                ["A) A JSON string", "B) A Python dict/list", "C) A file path", "D) An HTTP status"],
                1,
                ".json() parses the JSON response body into Python objects."
            ),
            (
                "What HTTP method is used to send/create data?",
                ["A) GET", "B) POST", "C) DELETE", "D) HEAD"],
                1,
                "POST is used to send data to create or update resources."
            ),
            (
                "What does REST stand for?",
                ["A) Remote Execution Standard Transfer", "B) Representational State Transfer", "C) Reliable Server Technology", "D) Request-Send-Transfer"],
                1,
                "REST = Representational State Transfer, an API design style."
            ),
            (
                "What status code means 'not found'?",
                ["A) 403", "B) 404", "C) 500", "D) 302"],
                1,
                "404 means the requested resource was not found."
            ),
            (
                "What library enables SSH connections from Python?",
                ["A) ssh", "B) openssh", "C) paramiko", "D) pyssh"],
                2,
                "Paramiko is the standard Python library for SSH connections."
            ),
            (
                "What does a socket do?",
                ["A) Manages files", "B) Provides network communication endpoint", "C) Runs commands", "D) Monitors CPU"],
                1,
                "Sockets are endpoints for sending/receiving data over a network."
            ),
            (
                "What header is used for API authentication?",
                ["A) Content-Type", "B) Authorization", "C) Accept", "D) User-Agent"],
                1,
                "The Authorization header carries authentication credentials."
            ),
        ]
    },
    8: {
        "title": "Week 8: OOP & Project Structure (Phase 2 Finale)",
        "questions": [
            (
                "What keyword creates a class?",
                ["A) def", "B) class", "C) new", "D) object"],
                1,
                "The 'class' keyword defines a new class."
            ),
            (
                "What is __init__()?",
                ["A) A destructor", "B) A constructor (initializer)", "C) A static method", "D) A module function"],
                1,
                "__init__ runs automatically when creating a new object."
            ),
            (
                "What does 'self' refer to?",
                ["A) The class itself", "B) The current instance/object", "C) The parent class", "D) The module"],
                1,
                "'self' refers to the specific instance of the class."
            ),
            (
                "What is inheritance?",
                ["A) Copying a class", "B) A class getting features from a parent class", "C) Deleting a class", "D) Renaming a class"],
                1,
                "Inheritance lets a child class reuse and extend parent class code."
            ),
            (
                "What does super().__init__() do?",
                ["A) Creates a new class", "B) Calls the parent class constructor", "C) Deletes the parent", "D) Imports a module"],
                1,
                "super().__init__() runs the parent class's __init__ method."
            ),
            (
                "What file makes a directory a Python package?",
                ["A) setup.py", "B) __init__.py", "C) main.py", "D) package.json"],
                1,
                "__init__.py marks a directory as a Python package."
            ),
            (
                "What is pytest used for?",
                ["A) Formatting code", "B) Running automated tests", "C) Deploying apps", "D) Installing packages"],
                1,
                "pytest is a framework for writing and running tests."
            ),
            (
                "What naming convention do test functions use in pytest?",
                ["A) test_()", "B) check_()", "C) verify_()", "D) assert_()"],
                0,
                "pytest discovers functions starting with 'test_'."
            ),
            (
                "What does 'pip install -r requirements.txt' do?",
                ["A) Creates requirements.txt", "B) Installs all packages listed in the file", "C) Removes packages", "D) Updates pip"],
                1,
                "It reads the file and installs every package listed."
            ),
            (
                "What is a virtual environment for?",
                ["A) Running virtual machines", "B) Isolating project dependencies", "C) Testing in production", "D) Docker replacement"],
                1,
                "Virtual environments keep project dependencies separate."
            ),
        ]
    },
    9: {
        "title": "Week 9: Docker & Containers with Python",
        "questions": [
            (
                "What Python library controls Docker?",
                ["A) pydocker", "B) docker", "C) container", "D) dockerpy"],
                1,
                "The 'docker' package (pip install docker) provides the Docker SDK."
            ),
            (
                "How do you connect to Docker from Python?",
                ["A) docker.connect()", "B) docker.from_env()", "C) Docker()", "D) docker.client()"],
                1,
                "docker.from_env() connects using your environment's Docker config."
            ),
            (
                "What does client.containers.list() return?",
                ["A) All containers ever created", "B) Running containers", "C) Docker images", "D) Container IDs only"],
                1,
                "By default it lists running containers. Use all=True for all."
            ),
            (
                "How do you stop a container in Python?",
                ["A) container.kill()", "B) container.stop()", "C) docker.stop(id)", "D) container.end()"],
                1,
                "container.stop() gracefully stops a running container."
            ),
            (
                "What does client.images.pull('nginx') do?",
                ["A) Deletes nginx image", "B) Downloads nginx image from Docker Hub", "C) Runs nginx", "D) Builds nginx image"],
                1,
                "images.pull() downloads an image from a registry."
            ),
            (
                "How do you get container logs?",
                ["A) container.output()", "B) container.logs()", "C) docker.logs(id)", "D) container.stdout()"],
                1,
                "container.logs() returns the container's log output."
            ),
            (
                "What method gets container resource stats?",
                ["A) container.stats()", "B) container.resources()", "C) container.usage()", "D) container.metrics()"],
                0,
                "container.stats() returns CPU, memory, network usage stats."
            ),
            (
                "How do you run a container from Python?",
                ["A) docker.run(image)", "B) client.containers.run(image)", "C) container.start(image)", "D) docker.create(image)"],
                1,
                "client.containers.run() creates and starts a container."
            ),
            (
                "What is Docker Compose used for?",
                ["A) Building images", "B) Managing multi-container applications", "C) Docker networking only", "D) Container monitoring"],
                1,
                "Docker Compose defines and runs multi-container applications."
            ),
            (
                "What format is docker-compose.yml?",
                ["A) JSON", "B) YAML", "C) TOML", "D) INI"],
                1,
                "Docker Compose files use YAML format."
            ),
        ]
    },
    10: {
        "title": "Week 10: AWS with Python (boto3)",
        "questions": [
            (
                "What is boto3?",
                ["A) A web framework", "B) AWS SDK for Python", "C) A database library", "D) A testing tool"],
                1,
                "boto3 is the official AWS SDK for Python."
            ),
            (
                "What are the two main interfaces in boto3?",
                ["A) Client and Resource", "B) Session and Connection", "C) API and SDK", "D) High and Low"],
                0,
                "Client (low-level) and Resource (high-level, object-oriented)."
            ),
            (
                "What AWS service manages virtual servers?",
                ["A) S3", "B) EC2", "C) RDS", "D) Lambda"],
                1,
                "EC2 (Elastic Compute Cloud) manages virtual server instances."
            ),
            (
                "How do you list S3 buckets with boto3?",
                ["A) s3.list_buckets()", "B) s3.get_buckets()", "C) s3.buckets.all()", "D) Both A and C"],
                3,
                "Client uses list_buckets(), Resource uses s3.buckets.all()."
            ),
            (
                "What does ec2.describe_instances() return?",
                ["A) A list of instance names", "B) Detailed info about EC2 instances", "C) Only running instances", "D) Instance costs"],
                1,
                "describe_instances() returns comprehensive instance details."
            ),
            (
                "What AWS service stores objects/files?",
                ["A) EBS", "B) S3", "C) EFS", "D) Glacier"],
                1,
                "S3 (Simple Storage Service) is AWS's object storage service."
            ),
            (
                "What does IAM stand for?",
                ["A) Internet Access Management", "B) Identity and Access Management", "C) Instance and Application Manager", "D) Integrated Auth Module"],
                1,
                "IAM manages users, roles, and permissions in AWS."
            ),
            (
                "What is AWS Lambda?",
                ["A) A database", "B) Serverless compute (run code without servers)", "C) A load balancer", "D) A VPN service"],
                1,
                "Lambda runs code without provisioning servers (serverless)."
            ),
            (
                "What service monitors AWS resources?",
                ["A) CloudTrail", "B) CloudWatch", "C) CloudFront", "D) CloudFormation"],
                1,
                "CloudWatch monitors resources and applications on AWS."
            ),
            (
                "How do you upload a file to S3?",
                ["A) s3.put_file()", "B) s3.upload_file(file, bucket, key)", "C) s3.send(file)", "D) s3.copy_to(bucket)"],
                1,
                "upload_file() uploads a local file to an S3 bucket."
            ),
        ]
    },
    11: {
        "title": "Week 11: CI/CD & Infrastructure as Code",
        "questions": [
            (
                "What does CI/CD stand for?",
                ["A) Code Integration / Code Deployment", "B) Continuous Integration / Continuous Delivery", "C) Cloud Infrastructure / Cloud Deployment", "D) Container Integration / Container Delivery"],
                1,
                "CI/CD = Continuous Integration / Continuous Delivery (or Deployment)."
            ),
            (
                "What Python library interacts with Git repositories?",
                ["A) pygit", "B) gitpython", "C) git", "D) vcs"],
                1,
                "GitPython provides Python access to Git repositories."
            ),
            (
                "What is Jinja2 used for?",
                ["A) Database queries", "B) Template rendering (generating configs)", "C) API calls", "D) Testing"],
                1,
                "Jinja2 generates dynamic content from templates (configs, HTML, etc)."
            ),
            (
                "What does {{ variable }} mean in Jinja2?",
                ["A) A comment", "B) A loop", "C) Output the variable's value", "D) Define a variable"],
                2,
                "{{ }} outputs the value of an expression in Jinja2 templates."
            ),
            (
                "What is Ansible primarily used for?",
                ["A) Monitoring", "B) Configuration management & automation", "C) Container orchestration", "D) Code compilation"],
                1,
                "Ansible automates configuration management, deployment, and orchestration."
            ),
            (
                "What format are Ansible playbooks written in?",
                ["A) JSON", "B) YAML", "C) Python", "D) XML"],
                1,
                "Ansible playbooks use YAML format."
            ),
            (
                "What is a GitHub Actions workflow?",
                ["A) A Python script", "B) An automated CI/CD pipeline", "C) A Git branch", "D) A testing framework"],
                1,
                "GitHub Actions workflows automate build, test, and deploy pipelines."
            ),
            (
                "Where do GitHub Actions workflow files live?",
                ["A) /actions/", "B) /.github/workflows/", "C) /ci/", "D) /pipelines/"],
                1,
                "Workflow YAML files go in the .github/workflows/ directory."
            ),
            (
                "What does 'Infrastructure as Code' mean?",
                ["A) Writing code on servers", "B) Managing infrastructure through code/config files", "C) Coding infrastructure hardware", "D) Using code editors on servers"],
                1,
                "IaC means defining and managing infrastructure using code files."
            ),
            (
                "What is a webhook?",
                ["A) A web server", "B) An HTTP callback triggered by an event", "C) A web framework", "D) A cron job"],
                1,
                "Webhooks are HTTP callbacks that notify your app when events happen."
            ),
        ]
    },
    12: {
        "title": "Week 12: Monitoring, Flask & Final Assessment",
        "questions": [
            (
                "What is Prometheus?",
                ["A) A web framework", "B) A monitoring and alerting system", "C) A database", "D) A CI/CD tool"],
                1,
                "Prometheus is an open-source monitoring and alerting toolkit."
            ),
            (
                "What Python library exposes Prometheus metrics?",
                ["A) prometheus_client", "B) prom_python", "C) metrics", "D) monitoring"],
                0,
                "prometheus_client is the official Python client for Prometheus."
            ),
            (
                "What is Flask?",
                ["A) A database", "B) A lightweight Python web framework", "C) A monitoring tool", "D) A testing library"],
                1,
                "Flask is a minimal Python web framework for building web apps and APIs."
            ),
            (
                "What decorator defines a Flask route?",
                ["A) @route", "B) @app.route", "C) @flask.path", "D) @url"],
                1,
                "@app.route('/path') maps a URL to a Python function."
            ),
            (
                "What are the 4 common metric types in Prometheus?",
                ["A) Counter, Gauge, Histogram, Summary", "B) Count, Average, Max, Min", "C) Int, Float, String, Bool", "D) Request, Response, Error, Latency"],
                0,
                "Counter, Gauge, Histogram, and Summary are the 4 metric types."
            ),
            (
                "What does a Counter metric do?",
                ["A) Goes up and down", "B) Only goes up (counts events)", "C) Measures time", "D) Stores strings"],
                1,
                "Counters only increase - used for counting requests, errors, etc."
            ),
            (
                "What does a Gauge metric do?",
                ["A) Only goes up", "B) Goes up and down (current value)", "C) Counts events", "D) Measures percentiles"],
                1,
                "Gauges go up and down - used for temperature, memory usage, etc."
            ),
            (
                "What HTTP method does a REST API use to delete a resource?",
                ["A) POST", "B) PUT", "C) REMOVE", "D) DELETE"],
                3,
                "DELETE is the HTTP method for removing resources."
            ),
            (
                "What is the purpose of a health check endpoint?",
                ["A) To serve web pages", "B) To verify a service is running and healthy", "C) To authenticate users", "D) To log errors"],
                1,
                "Health checks let monitoring systems verify service availability."
            ),
            (
                "What makes a good DevOps Python script?",
                ["A) It's as short as possible", "B) It has error handling, logging, and is well-structured", "C) It uses the most advanced features", "D) It avoids using libraries"],
                1,
                "Good DevOps scripts are reliable (error handling), observable (logging), and maintainable."
            ),
        ]
    },
}


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {
        "start_date": None,
        "days_completed": {},
        "quiz_scores": {},
        "streaks": {"current": 0, "longest": 0, "last_date": None},
        "notes": {},
    }


def save_progress(data):
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def run_quiz(week_num):
    if week_num not in QUIZZES:
        print(f"\n  No quiz available for week {week_num}.")
        print(f"  Available weeks: {', '.join(str(w) for w in sorted(QUIZZES.keys()))}")
        return

    quiz = QUIZZES[week_num]
    questions = quiz["questions"][:]
    random.shuffle(questions)

    print(f"\n{'=' * 60}")
    print(f"  WEEKLY QUIZ: {quiz['title']}")
    print(f"  10 Questions | 10 points each | 70% to pass")
    print(f"{'=' * 60}\n")

    score = 0
    wrong = []

    for i, (question, options, correct, explanation) in enumerate(questions, 1):
        print(f"  Question {i}/10:")
        print(f"  {question}\n")
        for opt in options:
            print(f"    {opt}")

        while True:
            try:
                answer = input(f"\n  Your answer (A/B/C/D): ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("\n\n  Quiz cancelled.")
                return
            if answer in ["A", "B", "C", "D"]:
                break
            print("  Please enter A, B, C, or D")

        answer_idx = {"A": 0, "B": 1, "C": 2, "D": 3}[answer]

        if answer_idx == correct:
            print(f"  CORRECT! +10 points")
            score += 10
        else:
            correct_letter = ["A", "B", "C", "D"][correct]
            print(f"  WRONG. Correct answer: {correct_letter}")
            print(f"  Explanation: {explanation}")
            wrong.append((question, explanation))

        print()

    # Results
    print(f"{'=' * 60}")
    print(f"  QUIZ RESULTS - Week {week_num}")
    print(f"{'=' * 60}")
    print(f"\n  Score: {score}/100")

    if score >= 90:
        grade = "A - Excellent!"
        msg = "Outstanding! You've mastered this week's material."
    elif score >= 70:
        grade = "B - Good"
        msg = "Solid understanding! Review the topics you missed."
    elif score >= 50:
        grade = "C - Needs Improvement"
        msg = "You should review the lesson materials before moving on."
    else:
        grade = "D - Retry Recommended"
        msg = "Go back and re-read the lessons for this week, then retake the quiz."

    print(f"  Grade: {grade}")
    print(f"  {msg}")

    if wrong:
        print(f"\n  Topics to Review:")
        for q, exp in wrong:
            print(f"  - {exp}")

    # Save score
    progress = load_progress()
    # Keep the best score
    prev = progress["quiz_scores"].get(str(week_num), 0)
    if score > prev:
        progress["quiz_scores"][str(week_num)] = score
        save_progress(progress)
        if prev > 0:
            print(f"\n  New high score! (Previous: {prev}%)")

    print(f"\n  Run 'python3 tracker.py' to see your updated dashboard.")
    print(f"{'=' * 60}\n")


def main():
    if len(sys.argv) != 2:
        print("\n  Usage: python3 quiz.py <week_number>")
        print("  Example: python3 quiz.py 1")
        print(f"\n  Available quizzes: Weeks 1-{max(QUIZZES.keys())}")
        return

    try:
        week = int(sys.argv[1])
    except ValueError:
        print("  Please provide a week number (1-12)")
        return

    run_quiz(week)


if __name__ == "__main__":
    main()
