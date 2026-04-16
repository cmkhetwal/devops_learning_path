# Week 4, Day 4: Built-in Functions

## What You'll Learn
- `map()` and `filter()` for transforming and filtering data
- `sorted()` with custom keys
- `lambda` -- small anonymous functions
- `enumerate()` and `zip()` for looping
- `any()`, `all()`, `min()`, `max()` for quick checks

---

## Why Built-in Functions Matter

Python has dozens of powerful built-in functions that save you from writing
loops. In DevOps, you constantly process lists of servers, metrics, and logs.
These tools make that work fast and clean.

---

## lambda -- Small Anonymous Functions

A `lambda` is a one-line function without a name:

```python
# Regular function:
def double(x):
    return x * 2

# Same thing as a lambda:
double = lambda x: x * 2

print(double(5))   # 10
```

Lambdas are most useful when passed directly to other functions:

```python
# Sort servers by their number
servers = ["web-10", "web-2", "web-1", "web-5"]
sorted_servers = sorted(servers, key=lambda s: int(s.split("-")[1]))
print(sorted_servers)   # ['web-1', 'web-2', 'web-5', 'web-10']
```

---

## sorted() with key

`sorted()` returns a new sorted list. The `key` parameter tells it HOW to sort:

```python
servers = [
    {"name": "web-01", "cpu": 85},
    {"name": "db-01", "cpu": 45},
    {"name": "cache-01", "cpu": 92},
]

# Sort by CPU usage
by_cpu = sorted(servers, key=lambda s: s["cpu"])
print(by_cpu[0]["name"])    # db-01 (lowest CPU)

# Sort by CPU usage, highest first
by_cpu_desc = sorted(servers, key=lambda s: s["cpu"], reverse=True)
print(by_cpu_desc[0]["name"])   # cache-01 (highest CPU)

# Sort strings by length
names = ["web-server-01", "db", "cache-01"]
by_length = sorted(names, key=lambda n: len(n))
print(by_length)   # ['db', 'cache-01', 'web-server-01']
```

---

## map() -- Transform Every Item

`map()` applies a function to every item in a list:

```python
# Get all hostnames in uppercase
servers = ["web-01", "db-01", "cache-01"]
upper_servers = list(map(str.upper, servers))
print(upper_servers)   # ['WEB-01', 'DB-01', 'CACHE-01']

# Extract CPU values from server dicts
server_data = [
    {"name": "web-01", "cpu": 85},
    {"name": "db-01", "cpu": 45},
]
cpu_values = list(map(lambda s: s["cpu"], server_data))
print(cpu_values)   # [85, 45]

# Convert string ports to integers
ports = ["80", "443", "8080"]
int_ports = list(map(int, ports))
print(int_ports)   # [80, 443, 8080]
```

Note: `map()` returns a map object, so wrap it in `list()` to see the results.

---

## filter() -- Keep Only Matching Items

`filter()` keeps items where the function returns `True`:

```python
# Keep only high CPU servers
servers = [
    {"name": "web-01", "cpu": 85},
    {"name": "db-01", "cpu": 45},
    {"name": "cache-01", "cpu": 92},
]

high_cpu = list(filter(lambda s: s["cpu"] > 80, servers))
print(high_cpu)
# [{'name': 'web-01', 'cpu': 85}, {'name': 'cache-01', 'cpu': 92}]

# Filter out empty strings
logs = ["ERROR: disk full", "", "INFO: started", "", "WARNING: low memory"]
non_empty = list(filter(None, logs))   # None removes falsy values
print(non_empty)
# ['ERROR: disk full', 'INFO: started', 'WARNING: low memory']

# Keep only error lines
errors = list(filter(lambda line: "ERROR" in line, logs))
print(errors)   # ['ERROR: disk full']
```

---

## enumerate() -- Loop with Index

`enumerate()` gives you both the index and the item:

```python
servers = ["web-01", "db-01", "cache-01"]

# Without enumerate (ugly):
i = 0
for server in servers:
    print(f"{i}: {server}")
    i += 1

# With enumerate (clean):
for i, server in enumerate(servers):
    print(f"{i}: {server}")

# Start counting from 1:
for i, server in enumerate(servers, start=1):
    print(f"Server {i}: {server}")
# Server 1: web-01
# Server 2: db-01
# Server 3: cache-01
```

---

## zip() -- Combine Multiple Lists

`zip()` pairs up items from multiple lists:

```python
servers = ["web-01", "db-01", "cache-01"]
cpu_usage = [85, 45, 92]
memory_usage = [70, 60, 55]

# Pair servers with their CPU
for server, cpu in zip(servers, cpu_usage):
    print(f"{server}: CPU {cpu}%")
# web-01: CPU 85%
# db-01: CPU 45%
# cache-01: CPU 92%

# Combine three lists
for server, cpu, mem in zip(servers, cpu_usage, memory_usage):
    print(f"{server}: CPU {cpu}%, Memory {mem}%")

# Create a dictionary from two lists
server_cpu = dict(zip(servers, cpu_usage))
print(server_cpu)   # {'web-01': 85, 'db-01': 45, 'cache-01': 92}
```

---

## any() and all() -- Quick Checks

`any()` returns `True` if ANY item is truthy.
`all()` returns `True` if ALL items are truthy.

```python
cpu_values = [45, 62, 95, 30]

# Is ANY server above 90% CPU?
print(any(cpu > 90 for cpu in cpu_values))    # True

# Are ALL servers below 80% CPU?
print(all(cpu < 80 for cpu in cpu_values))    # False

# Are ALL servers responding?
statuses = ["running", "running", "running"]
print(all(s == "running" for s in statuses))  # True

statuses = ["running", "stopped", "running"]
print(all(s == "running" for s in statuses))  # False
print(any(s == "stopped" for s in statuses))  # True
```

---

## min() and max() -- Find Extremes

```python
cpu_values = [85, 45, 92, 15, 67]
print(min(cpu_values))   # 15
print(max(cpu_values))   # 92

# With key parameter -- find the server with highest CPU
servers = [
    {"name": "web-01", "cpu": 85},
    {"name": "db-01", "cpu": 45},
    {"name": "cache-01", "cpu": 92},
]

busiest = max(servers, key=lambda s: s["cpu"])
print(busiest["name"])   # cache-01

quietest = min(servers, key=lambda s: s["cpu"])
print(quietest["name"])  # db-01
```

---

## Combining Built-in Functions

The real power comes from combining these functions:

```python
servers = [
    {"name": "web-01", "cpu": 85, "status": "running"},
    {"name": "web-02", "cpu": 45, "status": "running"},
    {"name": "db-01", "cpu": 92, "status": "running"},
    {"name": "cache-01", "cpu": 15, "status": "stopped"},
]

# Get names of running servers sorted by CPU (highest first)
result = sorted(
    filter(lambda s: s["status"] == "running", servers),
    key=lambda s: s["cpu"],
    reverse=True
)
names = list(map(lambda s: s["name"], result))
print(names)   # ['db-01', 'web-01', 'web-02']

# Are all running servers below 95% CPU?
running = filter(lambda s: s["status"] == "running", servers)
print(all(s["cpu"] < 95 for s in running))   # True
```

---

## DevOps Connection

These functions are essential for:
- **Monitoring dashboards** -- filter unhealthy servers, sort by load
- **Alert systems** -- `any()` to check if any threshold is breached
- **Log processing** -- `filter()` and `map()` to extract relevant data
- **Inventory management** -- `sorted()` and `zip()` to organize server lists
- **Health checks** -- `all()` to verify all services are running

---

## Today's Exercise

Open `exercise.py` and complete the tasks. You'll process server data using
built-in functions:
1. Filter unhealthy servers
2. Sort servers by CPU usage
3. Check if all servers are healthy
4. Combine multiple data sources with zip
5. Transform server data with map

Run `python check.py` to verify your solutions!
