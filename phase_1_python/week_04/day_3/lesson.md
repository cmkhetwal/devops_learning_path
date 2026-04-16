# Week 4, Day 3: Scope & Variables

## What You'll Learn
- What "scope" means in Python
- Local vs global variables
- The LEGB rule (simplified)
- The `global` keyword (and why to avoid it)
- Best practices for clean, bug-free code

---

## What Is Scope?

**Scope** is where a variable can be seen and used. Think of it like rooms in
a building -- a variable created inside a room (function) can only be used in
that room.

```python
def check_server():
    status = "running"        # This variable lives INSIDE the function
    print(status)             # Works fine

check_server()
print(status)                 # ERROR! 'status' doesn't exist out here
```

---

## Local Variables

Variables created inside a function are **local** to that function:

```python
def deploy():
    version = "2.1.0"         # Local variable
    print(f"Deploying v{version}")

deploy()
# print(version)              # NameError! version only exists inside deploy()
```

Each function call creates **fresh** local variables:

```python
def count_requests():
    count = 0                  # Fresh start every time!
    count += 1
    return count

print(count_requests())       # 1
print(count_requests())       # 1  (NOT 2 -- count resets each call)
```

---

## Global Variables

Variables created outside any function are **global** -- they can be read
from anywhere:

```python
MAX_RETRIES = 3               # Global variable

def attempt_deploy():
    print(f"Max retries: {MAX_RETRIES}")   # Can READ global variables

attempt_deploy()              # Output: Max retries: 3
```

But you **cannot modify** a global variable inside a function without the
`global` keyword:

```python
counter = 0

def increment():
    counter += 1     # ERROR! Python thinks you're creating a local variable

increment()          # UnboundLocalError!
```

---

## The LEGB Rule (Simplified)

When Python encounters a variable name, it searches in this order:

1. **L**ocal -- inside the current function
2. **E**nclosing -- inside any outer functions (nested functions)
3. **G**lobal -- at the top level of the file
4. **B**uilt-in -- Python's built-in names (like `print`, `len`, `True`)

```python
# BUILT-IN: print, len, True, etc. (always available)

server_name = "global-server"          # GLOBAL scope

def outer_function():
    server_name = "enclosing-server"   # ENCLOSING scope

    def inner_function():
        server_name = "local-server"   # LOCAL scope
        print(server_name)             # Finds LOCAL first

    inner_function()

outer_function()   # Output: local-server
```

If we remove the local variable:

```python
server_name = "global-server"

def outer_function():
    server_name = "enclosing-server"

    def inner_function():
        # No local server_name, so Python checks ENCLOSING
        print(server_name)

    inner_function()

outer_function()   # Output: enclosing-server
```

---

## The global Keyword

The `global` keyword lets you modify a global variable inside a function:

```python
deploy_count = 0

def deploy():
    global deploy_count
    deploy_count += 1
    print(f"Deploy #{deploy_count}")

deploy()   # Deploy #1
deploy()   # Deploy #2
deploy()   # Deploy #3
print(deploy_count)   # 3
```

### Why You Should Avoid global

Using `global` is considered **bad practice** because:

1. **Hard to debug** -- any function could change the value
2. **Hard to test** -- functions depend on external state
3. **Hard to reason about** -- you can't tell what a function does by looking at it alone

```python
# BAD -- uses global state
error_count = 0

def process_log(line):
    global error_count
    if "ERROR" in line:
        error_count += 1    # Who changed this? When? Hard to track.

# GOOD -- uses parameters and return values
def process_log(line, current_count):
    if "ERROR" in line:
        return current_count + 1
    return current_count

count = 0
count = process_log("ERROR: disk full", count)   # Clear data flow
```

---

## Best Practices

### 1. Pass data through parameters, return results

```python
# BAD
server_list = []

def add_server(name):
    global server_list
    server_list.append(name)

# GOOD
def add_server(server_list, name):
    server_list.append(name)
    return server_list

servers = []
servers = add_server(servers, "web-01")
```

### 2. Use UPPER_CASE for constants (read-only globals)

```python
MAX_RETRIES = 3
DEFAULT_PORT = 8080
DEFAULT_REGION = "us-east-1"

def create_server(port=DEFAULT_PORT, region=DEFAULT_REGION):
    print(f"Creating server on port {port} in {region}")
```

### 3. Keep functions self-contained

A function should work correctly using only its parameters:

```python
# BAD -- depends on global state
config = {"port": 8080}

def get_port():
    return config["port"]

# GOOD -- self-contained
def get_port(config):
    return config["port"]
```

---

## Common Scope Bugs

### Bug 1: Accidental shadowing

```python
servers = ["web-01", "web-02"]     # Global list

def process_servers():
    servers = []                    # Oops! Created a NEW local variable
    servers.append("web-03")       # Only modifies local list
    return servers

result = process_servers()
print(result)     # ["web-03"]
print(servers)    # ["web-01", "web-02"] -- unchanged!
```

### Bug 2: Reading before assignment

```python
count = 10

def update_count():
    count = count + 1   # ERROR! Python sees assignment, treats as local
    return count         # But local 'count' hasn't been defined yet

# Fix: pass as parameter
def update_count(count):
    return count + 1
```

### Bug 3: Mutable default arguments

```python
# DANGEROUS -- the default list is shared between calls!
def add_server(name, server_list=[]):
    server_list.append(name)
    return server_list

print(add_server("web-01"))   # ["web-01"]
print(add_server("web-02"))   # ["web-01", "web-02"]  -- SURPRISE!

# FIX: Use None as default
def add_server(name, server_list=None):
    if server_list is None:
        server_list = []
    server_list.append(name)
    return server_list
```

---

## DevOps Connection

Understanding scope prevents bugs in:
- **Configuration management** -- accidentally overwriting shared config
- **Monitoring scripts** -- counters that don't reset properly
- **Deployment pipelines** -- state leaking between deployment steps
- **Log processing** -- variables from one log entry affecting another

---

## Today's Exercise

Open `exercise.py` and complete the tasks. You'll:
1. Fix scope bugs in broken functions
2. Refactor functions that use `global` to use parameters instead
3. Practice writing clean, self-contained functions

Run `python check.py` to verify your solutions!
