# Week 3, Day 3: Tuples & Sets

## What You'll Learn Today
- Tuples: immutable sequences that can't be changed
- Sets: collections of unique items (no duplicates)
- When to use a tuple vs. a list vs. a set
- Frozensets: immutable sets

---

## Tuples -- Immutable Lists

A tuple looks like a list, but uses parentheses `()` instead of square brackets `[]`. The key difference: **you cannot change a tuple after creating it**. This makes tuples perfect for data that should never be modified.

```python
# Creating a tuple
server_config = ("web-01", "192.168.1.10", 8080)

# Access items the same way as lists
hostname = server_config[0]    # "web-01"
ip = server_config[1]          # "192.168.1.10"
port = server_config[2]        # 8080

print(f"Server: {hostname} at {ip}:{port}")
# Output: Server: web-01 at 192.168.1.10:8080

# Negative indexing works too
last = server_config[-1]       # 8080

# Length works the same
print(len(server_config))      # 3
```

### Why Can't You Change Tuples?

```python
server_config = ("web-01", "192.168.1.10", 8080)

# This will cause an error!
# server_config[0] = "web-02"    # TypeError: 'tuple' object does not support item assignment

# You also can't append, remove, or sort
# server_config.append("new")    # AttributeError: 'tuple' object has no attribute 'append'
```

### When to Use Tuples

```python
# Database connection settings (should not change at runtime)
db_config = ("db-prod.example.com", 5432, "myapp_db")

# Geographic coordinates of a data center
datacenter_location = (39.0438, -77.4874)

# Return multiple values from a calculation
def get_server_stats():
    cpu = 72.5
    memory = 85.3
    disk = 45.0
    return (cpu, memory, disk)   # Return as a tuple

stats = get_server_stats()
print(f"CPU: {stats[0]}%, Memory: {stats[1]}%, Disk: {stats[2]}%")

# Tuple unpacking -- assign each element to a variable
cpu, memory, disk = get_server_stats()
print(f"CPU: {cpu}%")
```

---

## Sets -- Unique Collections

A set is a collection where **every item is unique** -- no duplicates allowed. Sets use curly braces `{}`.

```python
# Creating a set
allowed_ports = {22, 80, 443, 8080}
print(allowed_ports)
# Output: {8080, 443, 80, 22}  (order may vary -- sets are unordered!)

# Duplicates are automatically removed
ports = {22, 80, 443, 22, 80}
print(ports)
# Output: {80, 443, 22}  (duplicates gone!)
```

### Adding and Removing from Sets

```python
allowed_ips = {"10.0.0.1", "10.0.0.2", "10.0.0.3"}

# Add a new IP
allowed_ips.add("10.0.0.4")
print(allowed_ips)
# Output: {'10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4'}

# Adding a duplicate does nothing (no error, just ignored)
allowed_ips.add("10.0.0.1")
print(len(allowed_ips))   # Still 4

# Remove an IP
allowed_ips.discard("10.0.0.3")   # Safe: no error if not found
print(allowed_ips)

# remove() also works but raises an error if not found
# allowed_ips.remove("10.0.0.99")  # KeyError!
```

### Set Operations -- The Real Power

Sets support mathematical operations that are incredibly useful for comparing groups.

```python
# Servers in two different data centers
dc_east = {"web-01", "web-02", "db-01", "cache-01"}
dc_west = {"web-03", "web-04", "db-01", "cache-01"}

# UNION -- all servers across both data centers (no duplicates)
all_servers = dc_east | dc_west    # or dc_east.union(dc_west)
print(all_servers)
# Output: {'web-01', 'web-02', 'web-03', 'web-04', 'db-01', 'cache-01'}

# INTERSECTION -- servers that exist in BOTH data centers
shared = dc_east & dc_west         # or dc_east.intersection(dc_west)
print(shared)
# Output: {'db-01', 'cache-01'}

# DIFFERENCE -- servers ONLY in east (not in west)
east_only = dc_east - dc_west      # or dc_east.difference(dc_west)
print(east_only)
# Output: {'web-01', 'web-02'}

# SYMMETRIC DIFFERENCE -- servers in one but NOT both
unique_to_each = dc_east ^ dc_west  # or dc_east.symmetric_difference(dc_west)
print(unique_to_each)
# Output: {'web-01', 'web-02', 'web-03', 'web-04'}
```

### Creating a Set from a List (Removing Duplicates)

```python
# Log of IPs that connected today (lots of duplicates)
connection_log = ["10.0.0.1", "10.0.0.2", "10.0.0.1", "10.0.0.3",
                  "10.0.0.1", "10.0.0.2", "10.0.0.4", "10.0.0.1"]

# Convert to a set to get unique IPs
unique_ips = set(connection_log)
print(unique_ips)
# Output: {'10.0.0.1', '10.0.0.2', '10.0.0.3', '10.0.0.4'}

print(f"Total connections: {len(connection_log)}")
print(f"Unique visitors: {len(unique_ips)}")
# Output: Total connections: 8
# Output: Unique visitors: 4
```

### Checking Membership

```python
# Sets are FAST for checking if something is "in" the collection
allowed_ips = {"10.0.0.1", "10.0.0.2", "10.0.0.3"}

incoming_ip = "10.0.0.2"
if incoming_ip in allowed_ips:
    print(f"{incoming_ip} is allowed")
else:
    print(f"{incoming_ip} is BLOCKED")
# Output: 10.0.0.2 is allowed
```

---

## Frozenset -- An Immutable Set

A `frozenset` is a set that cannot be modified after creation. It is to a set what a tuple is to a list.

```python
# Create a frozenset -- these ports can never change
critical_ports = frozenset({22, 80, 443})

# You can still check membership and do set operations
print(22 in critical_ports)       # True
print(critical_ports | {8080})    # frozenset({8080, 80, 443, 22})

# But you CANNOT modify it
# critical_ports.add(8080)        # AttributeError!
# critical_ports.discard(22)      # AttributeError!
```

---

## Quick Comparison

| Feature | List | Tuple | Set |
|---|---|---|---|
| Syntax | `[1, 2, 3]` | `(1, 2, 3)` | `{1, 2, 3}` |
| Ordered? | Yes | Yes | No |
| Mutable? | Yes | No | Yes |
| Duplicates? | Allowed | Allowed | Not allowed |
| Indexing? | Yes | Yes | No |
| Best for | General collections | Fixed data | Unique items, membership |

---

## DevOps Connection

| Data Structure | DevOps Use Case |
|---|---|
| Tuple | Immutable configs: `("db-host", 5432)` |
| Tuple | Function return values: `(cpu, mem, disk)` |
| Set | IP allowlists and blocklists |
| Set | Finding unique users/IPs from logs |
| Set operations | Comparing inventories across environments |
| Frozenset | Security-critical lists that must not change |

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks. Then run `python3 check.py` to see how you did!
