# Week 3, Day 5: Nested Structures

## What You'll Learn Today
- Lists of dictionaries (the most common real-world pattern)
- Dictionaries of lists
- How to iterate over nested structures
- How to access deeply nested data
- Working with JSON-like data from APIs

---

## Lists of Dictionaries

This is the single most important data pattern in DevOps. Every API you talk to -- AWS, Azure, Kubernetes, Docker -- returns data in this format: a list where each item is a dictionary.

```python
# A list of server dictionaries -- like an API response
servers = [
    {"hostname": "web-01", "ip": "10.0.0.1", "status": "running"},
    {"hostname": "web-02", "ip": "10.0.0.2", "status": "running"},
    {"hostname": "db-01",  "ip": "10.0.0.3", "status": "stopped"},
    {"hostname": "cache-01", "ip": "10.0.0.4", "status": "running"}
]

# Access the first server (it's a dict)
print(servers[0])
# Output: {'hostname': 'web-01', 'ip': '10.0.0.1', 'status': 'running'}

# Access a specific field of the first server
print(servers[0]["hostname"])     # Output: web-01

# Access the IP of the third server
print(servers[2]["ip"])           # Output: 10.0.0.3
```

---

## Iterating Over a List of Dicts

```python
servers = [
    {"hostname": "web-01", "ip": "10.0.0.1", "status": "running"},
    {"hostname": "web-02", "ip": "10.0.0.2", "status": "running"},
    {"hostname": "db-01",  "ip": "10.0.0.3", "status": "stopped"},
]

# Loop through each server and print its info
for server in servers:
    name = server["hostname"]
    status = server["status"]
    print(f"  {name}: {status}")
# Output:
#   web-01: running
#   web-02: running
#   db-01: stopped

# Count servers by status
running = 0
stopped = 0
for server in servers:
    if server["status"] == "running":
        running += 1
    elif server["status"] == "stopped":
        stopped += 1

print(f"Running: {running}, Stopped: {stopped}")
# Output: Running: 2, Stopped: 1
```

---

## Filtering a List of Dicts

```python
servers = [
    {"hostname": "web-01", "ip": "10.0.0.1", "status": "running"},
    {"hostname": "web-02", "ip": "10.0.0.2", "status": "stopped"},
    {"hostname": "db-01",  "ip": "10.0.0.3", "status": "running"},
    {"hostname": "cache-01", "ip": "10.0.0.4", "status": "stopped"},
]

# Find all running servers
running_servers = []
for server in servers:
    if server["status"] == "running":
        running_servers.append(server)

print(f"Running servers: {len(running_servers)}")
for s in running_servers:
    print(f"  {s['hostname']}")
# Output:
# Running servers: 2
#   web-01
#   db-01

# Same thing with a list comprehension
running_servers = [s for s in servers if s["status"] == "running"]

# Get just the hostnames of running servers
running_names = [s["hostname"] for s in servers if s["status"] == "running"]
print(running_names)
# Output: ['web-01', 'db-01']
```

---

## Searching a List of Dicts

```python
servers = [
    {"hostname": "web-01", "ip": "10.0.0.1", "status": "running"},
    {"hostname": "web-02", "ip": "10.0.0.2", "status": "running"},
    {"hostname": "db-01",  "ip": "10.0.0.3", "status": "stopped"},
]

# Find a specific server by hostname
target = "db-01"
found = None
for server in servers:
    if server["hostname"] == target:
        found = server
        break   # Stop looking once found

if found:
    print(f"Found {found['hostname']} at {found['ip']}")
else:
    print(f"{target} not found in inventory")
# Output: Found db-01 at 10.0.0.3
```

---

## Dictionaries of Lists

Sometimes a dictionary's values are lists. This is common for grouping items.

```python
# Servers grouped by role
server_groups = {
    "web": ["web-01", "web-02", "web-03"],
    "database": ["db-01", "db-02"],
    "cache": ["cache-01"]
}

# Access the web servers list
print(server_groups["web"])
# Output: ['web-01', 'web-02', 'web-03']

# Get the first database server
print(server_groups["database"][0])
# Output: db-01

# How many web servers?
print(len(server_groups["web"]))
# Output: 3

# Loop through all groups
for role, hosts in server_groups.items():
    print(f"{role} ({len(hosts)} servers): {', '.join(hosts)}")
# Output:
# web (3 servers): web-01, web-02, web-03
# database (2 servers): db-01, db-02
# cache (1 servers): cache-01
```

---

## Deeply Nested Structures (JSON-like)

Real API responses can be nested several levels deep.

```python
# Simulated AWS-style API response
ec2_response = {
    "Reservations": [
        {
            "Instances": [
                {
                    "InstanceId": "i-0abc123",
                    "State": {"Name": "running"},
                    "Tags": [
                        {"Key": "Name", "Value": "prod-web-01"},
                        {"Key": "Environment", "Value": "production"}
                    ]
                }
            ]
        },
        {
            "Instances": [
                {
                    "InstanceId": "i-0def456",
                    "State": {"Name": "stopped"},
                    "Tags": [
                        {"Key": "Name", "Value": "dev-web-01"},
                        {"Key": "Environment", "Value": "development"}
                    ]
                }
            ]
        }
    ]
}

# Navigate the structure step by step
reservations = ec2_response["Reservations"]

for res in reservations:
    for instance in res["Instances"]:
        inst_id = instance["InstanceId"]
        state = instance["State"]["Name"]
        # Find the "Name" tag
        name = "unknown"
        for tag in instance["Tags"]:
            if tag["Key"] == "Name":
                name = tag["Value"]
        print(f"  {inst_id} ({name}): {state}")
# Output:
#   i-0abc123 (prod-web-01): running
#   i-0def456 (dev-web-01): stopped
```

---

## Building Nested Structures

```python
# Build an inventory from scratch
inventory = []

# Add servers one at a time
inventory.append({
    "hostname": "web-01",
    "ip": "10.0.0.1",
    "tags": {"role": "web", "env": "prod"}
})

inventory.append({
    "hostname": "db-01",
    "ip": "10.0.0.2",
    "tags": {"role": "database", "env": "prod"}
})

# Now you can work with it
for server in inventory:
    role = server["tags"]["role"]
    print(f"{server['hostname']} -> role: {role}")
# Output:
# web-01 -> role: web
# db-01 -> role: database
```

---

## DevOps Connection

| Pattern | Real-World Example |
|---|---|
| List of dicts | AWS `describe_instances()` response |
| List of dicts | Kubernetes pod listing from API |
| Dict of lists | Ansible inventory groups |
| Nested dicts | Docker inspect output |
| Nested dicts | Terraform state file |

Every time you parse a JSON API response, read a config file, or process cloud metadata, you are working with nested structures. This is the most practical skill in DevOps Python programming.

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks. Then run `python3 check.py` to see how you did!
