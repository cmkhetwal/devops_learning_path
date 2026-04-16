# Week 3, Day 6: Practice Day -- 5 Mini-Projects

## What You'll Practice Today
Today is all about applying what you learned this week. You have 5 mini-projects that combine lists, tuples, sets, dictionaries, and nested structures. Each one is a realistic DevOps scenario.

---

## Mini-Project 1: Contact Book (Dict Operations)

A contact book is a dictionary where each key is a person's name and the value is their email. You'll practice creating, adding, looking up, and deleting entries.

```python
# Example of what a contact book looks like:
contacts = {
    "Alice": "alice@example.com",
    "Bob": "bob@example.com"
}

# Look up a contact
print(contacts.get("Alice", "Not found"))
# Output: alice@example.com

# Add a contact
contacts["Charlie"] = "charlie@example.com"

# Delete a contact
del contacts["Bob"]
```

---

## Mini-Project 2: Server Inventory Manager (List of Dicts with CRUD)

CRUD stands for Create, Read, Update, Delete -- the four basic operations. You'll manage a list of server dictionaries.

```python
# Example inventory
servers = [
    {"name": "web-01", "ip": "10.0.0.1", "status": "running"}
]

# CREATE: Add a new server
servers.append({"name": "db-01", "ip": "10.0.0.2", "status": "running"})

# READ: Find a server
for s in servers:
    if s["name"] == "web-01":
        print(s)

# UPDATE: Change a server's status
for s in servers:
    if s["name"] == "web-01":
        s["status"] = "maintenance"

# DELETE: Remove a server
servers = [s for s in servers if s["name"] != "db-01"]
```

---

## Mini-Project 3: Log Categorizer (Sort Entries into Categories)

Log lines often start with a level like INFO, WARNING, or ERROR. You'll sort them into a dictionary of lists.

```python
# Example:
logs = ["INFO: started", "ERROR: disk full", "INFO: request ok"]

categorized = {"INFO": [], "ERROR": [], "WARNING": []}
for line in logs:
    if line.startswith("INFO"):
        categorized["INFO"].append(line)
    elif line.startswith("ERROR"):
        categorized["ERROR"].append(line)
```

---

## Mini-Project 4: Unique IP Finder (Sets from Log Data)

Logs often contain repeated IP addresses. Sets make it trivial to find unique values and compare groups.

```python
# Example:
log_ips = ["10.0.0.1", "10.0.0.2", "10.0.0.1"]
unique = set(log_ips)   # {"10.0.0.1", "10.0.0.2"}
```

---

## Mini-Project 5: Infrastructure Report (Nested Structures)

Combine everything to build a summary report from a nested data structure -- just like processing a real API response.

```python
# Example: Count instances by state
instances = [
    {"id": "i-001", "state": "running"},
    {"id": "i-002", "state": "stopped"},
    {"id": "i-003", "state": "running"}
]

report = {}
for inst in instances:
    state = inst["state"]
    if state not in report:
        report[state] = 0
    report[state] += 1
# report = {"running": 2, "stopped": 1}
```

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 mini-projects. Then run `python3 check.py` to see how you did!
