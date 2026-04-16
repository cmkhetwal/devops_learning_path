# Week 4, Day 7: Phase 1 Final Test - Complete Cheat Sheet

## Congratulations! You've Completed Phase 1!

You've gone from zero Python knowledge to being able to write real, functional
DevOps scripts. That's a huge accomplishment. Before your final test, here's
a complete cheat sheet of everything you've learned.

---

## WEEK 1: Python Foundations

### Variables & Data Types
```python
# Strings
name = "web-server-01"
greeting = f"Hello, {name}"          # f-string
multiline = """line 1
line 2"""

# Numbers
port = 8080                          # int
cpu_percent = 87.5                   # float
count = int("42")                    # string to int
price = float("19.99")              # string to float

# Booleans
is_running = True
is_stopped = False

# None
result = None
```

### String Methods
```python
name = "  Web Server 01  "
name.strip()            # "Web Server 01"
name.lower()            # "  web server 01  "
name.upper()            # "  WEB SERVER 01  "
name.replace(" ", "-")  # "--Web-Server-01--"
name.split()            # ["Web", "Server", "01"]
"-".join(["a", "b"])    # "a-b"
name.startswith("  W")  # True
name.endswith("  ")     # True
len(name)               # 18
"Server" in name        # True
```

### Type Checking & Conversion
```python
type(42)          # <class 'int'>
isinstance(42, int)  # True
str(42)           # "42"
int("42")         # 42
float("3.14")     # 3.14
bool(0)           # False
bool(1)           # True
```

---

## WEEK 2: Control Flow

### Comparisons & Logic
```python
# Comparison operators
x == y    # equal
x != y    # not equal
x > y     # greater than
x < y     # less than
x >= y    # greater or equal
x <= y    # less or equal

# Logical operators
x and y   # both must be True
x or y    # at least one True
not x     # flip True/False
```

### If/Elif/Else
```python
cpu = 85
if cpu > 90:
    status = "critical"
elif cpu > 70:
    status = "warning"
else:
    status = "healthy"
```

### For Loops
```python
# Loop through a list
servers = ["web-01", "db-01", "cache-01"]
for server in servers:
    print(server)

# Loop with range
for i in range(5):          # 0, 1, 2, 3, 4
    print(i)

for i in range(1, 6):       # 1, 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2):   # 0, 2, 4, 6, 8
    print(i)

# Loop through a dictionary
config = {"port": 8080, "host": "localhost"}
for key, value in config.items():
    print(f"{key}: {value}")

# break and continue
for server in servers:
    if server == "db-01":
        continue            # Skip this one
    if server == "cache-01":
        break               # Stop the loop
    print(server)
```

### While Loops
```python
retries = 0
while retries < 3:
    print(f"Attempt {retries + 1}")
    retries += 1
```

---

## WEEK 3: Data Structures

### Lists
```python
servers = ["web-01", "db-01", "cache-01"]
servers.append("api-01")          # Add to end
servers.insert(0, "lb-01")        # Insert at index
servers.remove("db-01")           # Remove by value
popped = servers.pop()            # Remove & return last
servers.sort()                    # Sort in place
servers.reverse()                 # Reverse in place
length = len(servers)             # Length
first = servers[0]                # First item
last = servers[-1]                # Last item
subset = servers[1:3]             # Slice

# List comprehension
upper = [s.upper() for s in servers]
running = [s for s in servers if "web" in s]
```

### Dictionaries
```python
server = {
    "name": "web-01",
    "port": 8080,
    "status": "running"
}
server["name"]                    # "web-01"
server.get("ip", "unknown")      # "unknown" (default)
server["ip"] = "10.0.0.1"        # Add/update key
del server["status"]              # Delete key
"name" in server                  # True
server.keys()                     # dict_keys
server.values()                   # dict_values
server.items()                    # key-value pairs

# Dictionary comprehension
ports = {s: 8080 + i for i, s in enumerate(["web", "api"])}
```

### Tuples
```python
point = (10, 20)                  # Immutable
x, y = point                     # Unpacking
```

### Sets
```python
tags = {"web", "prod", "us-east"}
tags.add("v2")                    # Add item
tags.discard("v2")                # Remove (no error if missing)
"web" in tags                     # True

# Set operations
a = {"web", "prod"}
b = {"prod", "staging"}
a | b                             # Union: {"web", "prod", "staging"}
a & b                             # Intersection: {"prod"}
a - b                             # Difference: {"web"}
```

---

## WEEK 4: Functions & Modules

### Defining Functions
```python
def greet(name):
    """Docstring: describe the function."""
    return f"Hello, {name}!"

result = greet("Alice")
```

### Arguments
```python
# Default values
def deploy(app, version="latest", env="staging"):
    return f"Deploying {app} v{version} to {env}"

# *args - variable positional
def restart(*servers):
    for s in servers:
        print(f"Restarting {s}")

# **kwargs - variable keyword
def configure(host, **settings):
    for k, v in settings.items():
        print(f"{host}: {k}={v}")

# Unpacking
args = ["my-app", "2.0"]
deploy(*args)

config = {"app": "my-app", "env": "prod"}
deploy(**config)
```

### Scope
```python
# Local vs Global
MAX_RETRIES = 3                   # Global (read anywhere)

def process():
    count = 0                     # Local (only in this function)
    return count

# AVOID global keyword -- use parameters instead
# BAD:  global counter; counter += 1
# GOOD: def increment(counter): return counter + 1
```

### Built-in Functions
```python
# sorted with key
sorted(servers, key=lambda s: s["cpu"], reverse=True)

# map -- transform items
list(map(str.upper, ["a", "b"]))           # ["A", "B"]

# filter -- keep matching items
list(filter(lambda x: x > 50, [30, 60, 90]))  # [60, 90]

# enumerate -- index + item
for i, item in enumerate(my_list):
    print(f"{i}: {item}")

# zip -- combine lists
for name, cpu in zip(names, cpus):
    print(f"{name}: {cpu}%")

# any/all -- quick checks
any(cpu > 90 for cpu in cpus)     # True if any above 90
all(cpu < 90 for cpu in cpus)     # True if all below 90

# min/max with key
max(servers, key=lambda s: s["cpu"])

# lambda -- anonymous function
double = lambda x: x * 2
```

### Modules & Imports
```python
import os                         # Full import
from os import getcwd             # Specific import
import json as j                  # Alias

# Common standard library modules:
# os, sys, json, random, datetime, platform, string

# Your own modules:
# from my_module import my_function

# __name__ == "__main__" pattern:
if __name__ == "__main__":
    # Only runs when file is executed directly
    main()

# pip
# pip install requests
# pip freeze > requirements.txt
# pip install -r requirements.txt

# Virtual environments
# python -m venv venv
# source venv/bin/activate
# deactivate
```

---

## What's Coming in Phase 2

Phase 2 takes your skills to the next level with real-world DevOps automation:

- **Week 5:** File handling -- read/write configs, parse logs, work with CSV/JSON/YAML
- **Week 6:** Error handling -- try/except, custom exceptions, robust scripts
- **Week 7:** Working with APIs -- HTTP requests, REST APIs, cloud provider SDKs
- **Week 8:** Process automation -- subprocess, running shell commands from Python

You now have the foundation to build real DevOps tools. Phase 2 will teach you
to interact with the outside world -- files, networks, APIs, and system commands.

---

## Today's Final Test

Open `exercise.py` for 15 comprehensive questions covering ALL Phase 1 topics.
This is your chance to prove you've mastered the fundamentals.

Run `python check.py` to grade your test. Aim for 100%!

Good luck!
