# Week 3, Day 7: Quiz Day -- Data Structures Cheat Sheet

## Week 3 Cheat Sheet

Use this as a quick reference while completing the quiz and in your future DevOps work.

---

## Lists

```python
# Create
servers = ["web-01", "web-02", "db-01"]
empty = []

# Access
first = servers[0]           # "web-01"
last = servers[-1]           # "db-01"
length = len(servers)        # 3

# Modify
servers[0] = "web-01-new"   # Replace
servers.append("cache-01")  # Add to end
servers.insert(0, "lb-01")  # Insert at position
servers.remove("db-01")     # Remove by value
removed = servers.pop()     # Remove & return last
removed = servers.pop(0)    # Remove & return at index

# Search
pos = servers.index("web-02")     # Find position
n = servers.count("web-01")       # Count occurrences
exists = "web-01" in servers      # True/False

# Sort & Reverse
servers.sort()                    # Sort ascending (in place)
servers.sort(reverse=True)        # Sort descending (in place)
servers.reverse()                 # Reverse order (in place)

# Slice
first_two = servers[0:2]         # First two items
last_two = servers[-2:]          # Last two items
every_other = servers[::2]       # Every other item
backwards = servers[::-1]        # Reversed copy

# List Comprehension
upper = [s.upper() for s in servers]                    # Transform each
web = [s for s in servers if s.startswith("web")]       # Filter
```

---

## Tuples

```python
# Create (immutable -- cannot change after creation)
config = ("db-host.example.com", 5432, "mydb")

# Access (same as lists)
host = config[0]
port = config[1]

# Unpack
host, port, db = config

# Length
length = len(config)       # 3

# Cannot modify!
# config[0] = "new"        # TypeError!
# config.append("x")       # AttributeError!
```

---

## Sets

```python
# Create (unique items only, unordered)
ips = {"10.0.0.1", "10.0.0.2", "10.0.0.3"}
from_list = set(["a", "b", "a"])    # {"a", "b"}

# Add & Remove
ips.add("10.0.0.4")                 # Add one item
ips.discard("10.0.0.2")             # Remove (no error if missing)
ips.remove("10.0.0.1")              # Remove (error if missing)

# Membership (very fast)
exists = "10.0.0.1" in ips          # True/False

# Set Operations
a = {"web-01", "web-02", "db-01"}
b = {"web-02", "db-01", "cache-01"}

union = a | b              # All unique: {'web-01','web-02','db-01','cache-01'}
intersection = a & b       # In both: {'web-02', 'db-01'}
difference = a - b         # In a not b: {'web-01'}
sym_diff = a ^ b           # In one but not both: {'web-01', 'cache-01'}

# Frozenset (immutable set)
locked = frozenset({22, 80, 443})
# locked.add(8080)          # AttributeError!
```

---

## Dictionaries

```python
# Create
server = {"hostname": "web-01", "ip": "10.0.0.5", "port": 80}
empty = {}

# Access
name = server["hostname"]                 # "web-01" (KeyError if missing)
name = server.get("hostname")             # "web-01" (None if missing)
name = server.get("region", "unknown")    # "unknown" (custom default)

# Add / Update
server["region"] = "us-east-1"            # Add new key
server["port"] = 443                      # Update existing
server.update({"tier": "prod", "port": 8080})  # Add/update multiple

# Delete
del server["region"]                      # Delete key (KeyError if missing)
val = server.pop("tier")                  # Delete & return value

# Keys, Values, Items
keys = list(server.keys())               # ["hostname", "ip", "port"]
vals = list(server.values())             # ["web-01", "10.0.0.5", 8080]
pairs = list(server.items())             # [("hostname","web-01"), ...]

# Check key existence
if "hostname" in server:
    print("Found it")

# Loop through items
for key, value in server.items():
    print(f"{key}: {value}")

# Nested dicts
server = {
    "hostname": "web-01",
    "network": {"ip": "10.0.0.5", "subnet": "/24"}
}
ip = server["network"]["ip"]             # "10.0.0.5"
```

---

## Nested Structures

```python
# List of dicts (most common pattern in APIs)
servers = [
    {"name": "web-01", "status": "running"},
    {"name": "db-01", "status": "stopped"}
]
first_name = servers[0]["name"]                          # "web-01"
running = [s for s in servers if s["status"] == "running"]

# Dict of lists (grouping pattern)
groups = {"web": ["web-01", "web-02"], "db": ["db-01"]}
web_list = groups["web"]                                 # ["web-01", "web-02"]
first_web = groups["web"][0]                             # "web-01"
```

---

## When to Use What

| Need | Use |
|---|---|
| Ordered collection, may change | **List** |
| Fixed data, should not change | **Tuple** |
| Unique items, fast membership checks | **Set** |
| Unique items that must never change | **Frozenset** |
| Key-value lookup | **Dictionary** |
| API response / structured data | **List of dicts** or **Nested dicts** |

---

## Now Do The Exercise!

Open `exercise.py` and complete all 10 code-completion challenges. Then run `python3 check.py` to see your score!
