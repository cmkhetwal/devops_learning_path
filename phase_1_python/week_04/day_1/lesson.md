# Week 4, Day 1: Functions Basics

## What You'll Learn
- What functions are and why they matter
- How to define functions with the `def` keyword
- How to use parameters and arguments
- How to return values from functions
- How to call functions you've created

---

## Why Functions Matter

Imagine you're a DevOps engineer and you need to check if a port number is valid.
You write the same 5 lines of code in 20 different scripts. Then the rules change
and you have to update all 20 scripts. That's a nightmare.

**Functions** let you write code once and reuse it everywhere.

```
Without functions (bad):
    port = 8080
    if port > 0 and port <= 65535:
        print("Valid port")
    else:
        print("Invalid port")

    # ... 200 lines later, same check again ...
    port = 443
    if port > 0 and port <= 65535:
        print("Valid port")
    else:
        print("Invalid port")
```

```
With functions (good):
    def is_port_valid(port):
        return port > 0 and port <= 65535

    print(is_port_valid(8080))   # True
    print(is_port_valid(443))    # True
    print(is_port_valid(-1))     # False
```

---

## Defining a Function

Use the `def` keyword followed by a name, parentheses, and a colon:

```python
def greet():
    print("Hello, DevOps engineer!")
```

Key pieces:
- `def` - tells Python "I'm creating a function"
- `greet` - the function name (use lowercase_with_underscores)
- `()` - parentheses hold parameters (empty here)
- `:` - starts the function body
- The indented block below is the function body

**Important:** Defining a function does NOT run it. You must **call** it:

```python
def greet():
    print("Hello, DevOps engineer!")

# Nothing happens until you call it:
greet()   # Output: Hello, DevOps engineer!
```

---

## Parameters and Arguments

**Parameters** are placeholders in the function definition.
**Arguments** are actual values you pass when calling the function.

```python
def check_server(hostname):        # hostname is a PARAMETER
    print(f"Checking {hostname}...")

check_server("web-server-01")      # "web-server-01" is an ARGUMENT
check_server("db-server-01")       # "db-server-01" is an ARGUMENT
```

You can have multiple parameters:

```python
def check_server(hostname, port):
    print(f"Checking {hostname} on port {port}...")

check_server("web-server-01", 8080)
check_server("db-server-01", 5432)
```

---

## The return Statement

Functions can **return** a value back to the caller:

```python
def add_numbers(a, b):
    return a + b

result = add_numbers(3, 5)
print(result)   # 8
```

Without `return`, a function returns `None`:

```python
def greet(name):
    print(f"Hello, {name}")

result = greet("Alice")
print(result)   # None (the function printed, but returned nothing)
```

You can return any type -- strings, numbers, lists, booleans, dictionaries:

```python
def is_port_valid(port):
    return port > 0 and port <= 65535

def get_server_info(hostname):
    return {
        "hostname": hostname,
        "status": "running",
        "port": 8080
    }

print(is_port_valid(443))           # True
info = get_server_info("web-01")
print(info["status"])               # running
```

---

## A Complete Example: DevOps Style

```python
def format_hostname(name, domain="example.com"):
    """Format a server name into a full hostname."""
    clean_name = name.strip().lower()
    return f"{clean_name}.{domain}"

def is_port_valid(port):
    """Check if a port number is in the valid range."""
    return isinstance(port, int) and 0 < port <= 65535

def calculate_uptime_percentage(total_hours, downtime_hours):
    """Calculate server uptime as a percentage."""
    if total_hours <= 0:
        return 0.0
    uptime = total_hours - downtime_hours
    return round((uptime / total_hours) * 100, 2)

# Using the functions:
host = format_hostname("  Web-Server-01  ")
print(host)   # web-server-01.example.com

print(is_port_valid(8080))    # True
print(is_port_valid(99999))   # False

uptime = calculate_uptime_percentage(720, 2)
print(f"Uptime: {uptime}%")  # Uptime: 99.72%
```

Notice the triple-quoted strings right after `def`. Those are **docstrings** --
they describe what the function does. It's a best practice to include them.

---

## Common Mistakes

**1. Forgetting to call the function:**
```python
def deploy():
    print("Deploying...")

deploy    # WRONG - this doesn't call it
deploy()  # RIGHT - parentheses call it
```

**2. Forgetting to return a value:**
```python
def double(x):
    x * 2      # Calculates but throws away the result!

def double(x):
    return x * 2   # Correct - returns the result
```

**3. Code after return never runs:**
```python
def check(port):
    return port > 0
    print("This never prints!")   # Dead code!
```

---

## DevOps Connection

Functions are the backbone of every DevOps tool you'll build:
- **Health check scripts** - functions to check different services
- **Deployment scripts** - functions for each deployment step
- **Monitoring tools** - functions to collect and format metrics
- **Automation** - reusable functions you call from multiple scripts

In real DevOps work, a deployment script might look like:
```python
def validate_config():
    ...

def backup_current():
    ...

def deploy_new_version():
    ...

def run_health_checks():
    ...

# Deployment pipeline:
validate_config()
backup_current()
deploy_new_version()
run_health_checks()
```

---

## Today's Exercise

Open `exercise.py` and complete the tasks. You'll create three DevOps-themed
functions:
1. `is_port_valid(port)` - validate port numbers
2. `format_hostname(name)` - clean and format hostnames
3. `calculate_uptime(total_hours, downtime_hours)` - calculate uptime percentage

Run `python check.py` to verify your solutions!
