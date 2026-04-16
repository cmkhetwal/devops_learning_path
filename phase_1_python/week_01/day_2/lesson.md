# Week 1, Day 2: Variables & Data Types

## What You'll Learn Today
- How to store data in variables
- The 4 basic data types in Python
- How to check and convert types

## Variables = Named Containers
A variable stores a value so you can use it later.

```python
# Creating variables (no special keyword needed!)
server_name = "web-01"
cpu_count = 4
memory_gb = 16.5
is_running = True

# Using variables
print(server_name)          # Output: web-01
print("CPUs:", cpu_count)   # Output: CPUs: 4
```

## Naming Rules
```python
# GOOD variable names (use snake_case)
server_name = "web-01"
max_retries = 3
is_healthy = True

# BAD variable names
# 2server = "no"      # Can't start with number
# server-name = "no"  # No hyphens (use underscore)
# class = "no"        # Can't use Python keywords
```

## The 4 Basic Data Types

### 1. Strings (str) - Text
```python
hostname = "web-server-01"
ip_address = '192.168.1.100'    # Single or double quotes both work
empty = ""                       # Empty string

# String length
print(len(hostname))  # Output: 13
```

### 2. Integers (int) - Whole Numbers
```python
port = 8080
max_connections = 1000
error_count = 0
negative = -1
```

### 3. Floats (float) - Decimal Numbers
```python
cpu_usage = 75.5
uptime_hours = 99.99
temperature = 45.0
```

### 4. Booleans (bool) - True/False
```python
is_running = True
has_errors = False
# Note: True and False are capitalized!
```

## Checking Types
```python
port = 8080
print(type(port))        # <class 'int'>

hostname = "web-01"
print(type(hostname))    # <class 'str'>

cpu = 75.5
print(type(cpu))         # <class 'float'>

active = True
print(type(active))      # <class 'bool'>
```

## Converting Types
```python
# String to Integer
port_str = "8080"
port_num = int(port_str)
print(port_num + 1)      # 8081

# Integer to String
count = 42
message = "Errors: " + str(count)
print(message)           # Errors: 42

# String to Float
cpu = float("75.5")
print(cpu)               # 75.5

# Any value to Boolean
print(bool(0))           # False
print(bool(1))           # True
print(bool(""))          # False (empty string)
print(bool("hello"))     # True (non-empty string)
```

## Variable Reassignment
```python
status = "starting"
print(status)        # starting

status = "running"   # Same variable, new value
print(status)        # running

# Variables can even change type (but avoid this!)
x = 10
x = "ten"           # Now it's a string (not recommended)
```

## DevOps Connection
```python
# Server configuration using variables
server_name = "prod-web-01"
region = "us-east-1"
instance_type = "t3.medium"
cpu_cores = 2
memory_gb = 4.0
is_production = True

print(f"Server: {server_name}")
print(f"Region: {region}")
print(f"Type: {instance_type}")
print(f"Production: {is_production}")
```

## Now Do The Exercise!
Open `exercise.py` and complete the tasks.
