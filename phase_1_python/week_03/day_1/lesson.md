# Week 3, Day 1: Lists

## What You'll Learn Today
- What lists are and why they matter in DevOps
- Creating lists of servers, IPs, and other resources
- Accessing items by index (positive and negative)
- Finding how many items are in a list with `len()`

---

## What Is a List?

A list is a collection of items stored in a specific order. Think of it as a roster, a queue, or an inventory. In DevOps, you deal with lists constantly: lists of servers, lists of ports, lists of IP addresses, lists of log entries.

```python
# Creating a list is simple: use square brackets []
servers = ["web-01", "web-02", "db-01", "cache-01"]

# A list can hold any type of data
ports = [22, 80, 443, 8080]

# A list can even mix types (though this is less common)
server_info = ["web-01", "192.168.1.10", 22, True]

# An empty list - you'll fill it later
failed_hosts = []
```

---

## Accessing Items by Index

Every item in a list has a position number called an **index**. Python starts counting at 0, not 1.

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]
#           index 0    index 1    index 2    index 3

# Get the first server
first = servers[0]       # "web-01"

# Get the second server
second = servers[1]      # "web-02"

# Get the third server
third = servers[2]       # "db-01"

print(first)             # Output: web-01
print(second)            # Output: web-02
```

---

## Negative Indexing

You can count backwards from the end using negative numbers. This is super useful when you want the last item and don't know the list length.

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]

# Get the LAST server
last = servers[-1]       # "cache-01"

# Get the second-to-last server
second_last = servers[-2]  # "db-01"

print(last)              # Output: cache-01
print(second_last)       # Output: db-01
```

---

## Finding the Length of a List

The `len()` function tells you how many items are in a list.

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]

# How many servers do we have?
count = len(servers)
print(count)             # Output: 4

# This is useful for reporting
print(f"Total servers in fleet: {len(servers)}")
# Output: Total servers in fleet: 4

# An empty list has length 0
empty = []
print(len(empty))        # Output: 0
```

---

## Creating Different Kinds of Lists

```python
# List of server hostnames
hostnames = ["app-server-1", "app-server-2", "app-server-3"]

# List of IP addresses (as strings)
ip_addresses = ["10.0.0.1", "10.0.0.2", "10.0.0.3"]

# List of open ports (as integers)
open_ports = [22, 80, 443, 3306, 5432]

# List of True/False health check results
health_status = [True, True, False, True]

# List of environment names
environments = ["dev", "staging", "production"]

# You can check if a list is empty
if len(health_status) > 0:
    print("We have health check results to review.")
```

---

## Printing Lists and Items

```python
servers = ["web-01", "web-02", "db-01"]

# Print the whole list
print(servers)
# Output: ['web-01', 'web-02', 'db-01']

# Print individual items
print(f"Primary server: {servers[0]}")
# Output: Primary server: web-01

print(f"Backup server: {servers[-1]}")
# Output: Backup server: db-01

# Print with a loop (you'll learn more about loops in Week 4)
for server in servers:
    print(f"  - {server}")
# Output:
#   - web-01
#   - web-02
#   - db-01
```

---

## Changing Items in a List

Lists are **mutable** -- you can change their contents after creating them.

```python
servers = ["web-01", "web-02", "db-01"]

# Replace the second server
servers[1] = "web-02-new"
print(servers)
# Output: ['web-01', 'web-02-new', 'db-01']

# Replace the last server
servers[-1] = "db-01-upgraded"
print(servers)
# Output: ['web-01', 'web-02-new', 'db-01-upgraded']
```

---

## DevOps Connection

Lists are the backbone of infrastructure management:

| Use Case | Example |
|---|---|
| Server inventory | `["web-01", "web-02", "db-01"]` |
| Port scanning results | `[22, 80, 443, 8080]` |
| Log file lines | `["ERROR: timeout", "INFO: started", ...]` |
| Deployment targets | `["us-east-1", "eu-west-1"]` |
| Health check results | `[True, True, False, True]` |

In real-world tools like Ansible, your host inventories are essentially lists. In Terraform, many resource arguments accept lists. Understanding lists is the first step to working with structured data in automation.

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks. Then run `python3 check.py` to see how you did!
