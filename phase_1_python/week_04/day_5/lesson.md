# Week 4, Day 5: Modules & Imports

## What You'll Learn
- What modules are and why they exist
- `import` and `from...import` syntax
- Creating your own module
- The `__name__ == "__main__"` pattern
- Installing packages with `pip`
- Virtual environments with `venv`

---

## What Is a Module?

A **module** is simply a Python file (`.py`) that contains code you can reuse.
When you write `import os`, you're importing Python's built-in `os` module.

You've already used modules without knowing it:

```python
import random          # Module for random numbers
import os              # Module for operating system operations
import sys             # Module for system-specific info
```

---

## import Statement

The basic way to use a module:

```python
import os

# Use with module_name.function_name
current_dir = os.getcwd()
print(current_dir)

# List files in a directory
files = os.listdir(".")
print(files)
```

Import multiple modules:

```python
import os
import sys
import json
```

---

## from...import Statement

Import specific items from a module:

```python
from os import getcwd, listdir

# Now use directly (no os. prefix needed)
current_dir = getcwd()
files = listdir(".")
```

Import with an alias:

```python
import json as j

data = j.dumps({"name": "web-01"})

from os.path import join as path_join

full_path = path_join("/var", "log", "app.log")
print(full_path)   # /var/log/app.log
```

### Import Everything (avoid this)

```python
from os import *    # Imports EVERYTHING -- bad practice!
```

This pollutes your namespace and makes it hard to know where things came from.

---

## Useful Standard Library Modules

Python comes with many modules you don't need to install:

```python
# os - Operating system interaction
import os
os.getcwd()                    # Current directory
os.listdir("/var/log")         # List files
os.path.exists("/etc/hosts")   # Check if file exists
os.environ.get("HOME")        # Get environment variable

# json - Read and write JSON
import json
data = {"server": "web-01", "port": 8080}
json_string = json.dumps(data)            # Dict to JSON string
parsed = json.loads(json_string)          # JSON string to dict

# datetime - Work with dates and times
from datetime import datetime
now = datetime.now()
print(now.strftime("%Y-%m-%d %H:%M:%S"))  # 2024-01-15 14:30:00

# platform - System information
import platform
print(platform.system())        # Linux, Windows, or Darwin
print(platform.python_version())  # 3.11.5

# random - Random number generation
import random
port = random.randint(8000, 9000)
server = random.choice(["web-01", "web-02", "web-03"])
```

---

## Creating Your Own Module

Any Python file can be a module. Create a file called `server_utils.py`:

```python
# server_utils.py

DEFAULT_PORT = 8080

def is_port_valid(port):
    """Check if a port number is valid."""
    return isinstance(port, int) and 0 < port <= 65535

def format_hostname(name, domain="example.com"):
    """Format a server name into a full hostname."""
    return f"{name.strip().lower()}.{domain}"

def get_server_status(cpu_percent):
    """Return status based on CPU percentage."""
    if cpu_percent > 90:
        return "critical"
    elif cpu_percent > 70:
        return "warning"
    return "healthy"
```

Now use it in another file in the same directory:

```python
# main.py

import server_utils

print(server_utils.is_port_valid(8080))          # True
print(server_utils.format_hostname("web-01"))     # web-01.example.com
print(server_utils.DEFAULT_PORT)                  # 8080

# Or import specific functions:
from server_utils import is_port_valid, format_hostname

print(is_port_valid(443))               # True
print(format_hostname("db-01"))         # db-01.example.com
```

---

## The __name__ == "__main__" Pattern

When Python runs a file directly, it sets `__name__` to `"__main__"`.
When a file is imported as a module, `__name__` is set to the module name.

This lets you have code that runs ONLY when the file is executed directly:

```python
# server_utils.py

def is_port_valid(port):
    return isinstance(port, int) and 0 < port <= 65535

def format_hostname(name):
    return name.strip().lower()

# This block only runs when you do: python server_utils.py
# It does NOT run when someone does: import server_utils
if __name__ == "__main__":
    # Test our functions
    print("Testing is_port_valid:")
    print(f"  80: {is_port_valid(80)}")         # True
    print(f"  0: {is_port_valid(0)}")           # False

    print("Testing format_hostname:")
    print(f"  '  WEB-01  ': {format_hostname('  WEB-01  ')}")   # web-01
```

This is extremely useful:
- **As a module:** Other files can `import server_utils` without triggering tests
- **As a script:** Running `python server_utils.py` directly runs the tests

---

## pip -- Installing Packages

`pip` is Python's package installer. It downloads packages from PyPI
(Python Package Index -- the largest repository of Python packages).

```bash
# Install a package
pip install requests

# Install a specific version
pip install requests==2.31.0

# Install multiple packages
pip install requests flask boto3

# See what's installed
pip list

# Uninstall
pip uninstall requests

# Save your project's dependencies
pip freeze > requirements.txt

# Install from a requirements file
pip install -r requirements.txt
```

Common DevOps packages:
- `requests` -- HTTP requests (API calls)
- `boto3` -- AWS SDK
- `paramiko` -- SSH connections
- `pyyaml` -- YAML parsing
- `python-dotenv` -- Load .env files
- `flask` -- Simple web servers

---

## Virtual Environments (venv)

A **virtual environment** is an isolated Python environment for your project.
Each project gets its own packages, avoiding version conflicts.

```bash
# Create a virtual environment
python -m venv myenv

# Activate it (Linux/Mac)
source myenv/bin/activate

# Activate it (Windows)
myenv\Scripts\activate

# Your prompt changes to show the active environment:
# (myenv) $

# Now pip installs go only to this environment
pip install requests

# Deactivate when done
deactivate
```

**Why use virtual environments?**
- Project A needs `requests 2.28` but Project B needs `requests 2.31`
- Without venv, they'd conflict
- With venv, each project has its own isolated packages

Best practice workflow:

```bash
# 1. Create project directory
mkdir my-devops-tool
cd my-devops-tool

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Install packages
pip install requests pyyaml

# 5. Save dependencies
pip freeze > requirements.txt

# 6. Add venv/ to .gitignore (never commit the venv folder!)
echo "venv/" >> .gitignore
```

---

## DevOps Connection

Modules and imports are how real DevOps tools are structured:
- **Ansible** -- uses Python modules for each task type
- **Docker SDK** -- `import docker` to manage containers from Python
- **AWS Boto3** -- `import boto3` to manage AWS resources
- **Custom tools** -- you'll create reusable module libraries

Virtual environments prevent "it works on my machine" problems -- each
project has exactly the dependencies it needs.

---

## Today's Exercise

Open `exercise.py` and complete the tasks. You'll:
1. Create a utility module with reusable functions
2. Use standard library modules (os, json, platform)
3. Practice the `__name__ == "__main__"` pattern

Run `python check.py` to verify your solutions!
