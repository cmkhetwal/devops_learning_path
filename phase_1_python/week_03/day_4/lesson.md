# Week 3, Day 4: Dictionaries

## What You'll Learn Today
- What dictionaries are: key-value pairs
- Creating dictionaries and accessing values
- Adding, updating, and deleting entries
- Essential methods: `.get()`, `.keys()`, `.values()`, `.items()`
- Nested dictionaries for complex data

---

## What Is a Dictionary?

A dictionary stores data as **key-value pairs**. Think of it like a real dictionary: you look up a word (the key) to find its definition (the value). In DevOps, dictionaries are everywhere -- server configs, cloud metadata, API responses.

```python
# Create a dictionary with curly braces and colons
server = {
    "hostname": "web-01",
    "ip": "10.0.0.5",
    "port": 80,
    "status": "running"
}

print(server)
# Output: {'hostname': 'web-01', 'ip': '10.0.0.5', 'port': 80, 'status': 'running'}
```

---

## Accessing Values

Use square brackets with the **key** (not an index number) to get a value.

```python
server = {
    "hostname": "web-01",
    "ip": "10.0.0.5",
    "port": 80,
    "status": "running"
}

# Access values by key
print(server["hostname"])    # Output: web-01
print(server["ip"])          # Output: 10.0.0.5
print(server["port"])        # Output: 80

# Use in f-strings
print(f"Server {server['hostname']} is {server['status']}")
# Output: Server web-01 is running
```

### The Problem with Square Brackets

```python
# If the key doesn't exist, you get a KeyError!
# print(server["region"])    # KeyError: 'region'
```

### The .get() Method -- Safe Access

```python
server = {"hostname": "web-01", "ip": "10.0.0.5"}

# .get() returns None if the key doesn't exist (no error!)
region = server.get("region")
print(region)                # Output: None

# You can provide a default value
region = server.get("region", "unknown")
print(region)                # Output: unknown

# If the key exists, .get() works just like square brackets
hostname = server.get("hostname")
print(hostname)              # Output: web-01
```

---

## Adding and Updating Entries

```python
server = {"hostname": "web-01", "status": "running"}

# Add a new key-value pair
server["ip"] = "10.0.0.5"
server["port"] = 80
print(server)
# Output: {'hostname': 'web-01', 'status': 'running', 'ip': '10.0.0.5', 'port': 80}

# Update an existing value
server["status"] = "maintenance"
print(server["status"])      # Output: maintenance

# Add multiple entries at once with .update()
server.update({
    "region": "us-east-1",
    "tier": "production"
})
print(server)
# Now includes region and tier
```

---

## Deleting Entries

```python
server = {"hostname": "web-01", "ip": "10.0.0.5", "temp_key": "delete_me"}

# Remove a specific key
del server["temp_key"]
print(server)
# Output: {'hostname': 'web-01', 'ip': '10.0.0.5'}

# pop() removes and returns the value
ip = server.pop("ip")
print(f"Removed IP: {ip}")   # Output: Removed IP: 10.0.0.5
print(server)                 # Output: {'hostname': 'web-01'}
```

---

## Essential Methods

### .keys() -- Get All Keys

```python
server = {"hostname": "web-01", "ip": "10.0.0.5", "port": 80}

keys = server.keys()
print(keys)
# Output: dict_keys(['hostname', 'ip', 'port'])

# Convert to a list if needed
key_list = list(server.keys())
print(key_list)
# Output: ['hostname', 'ip', 'port']
```

### .values() -- Get All Values

```python
server = {"hostname": "web-01", "ip": "10.0.0.5", "port": 80}

values = server.values()
print(values)
# Output: dict_values(['web-01', '10.0.0.5', 80])
```

### .items() -- Get All Key-Value Pairs

```python
server = {"hostname": "web-01", "ip": "10.0.0.5", "port": 80}

# .items() returns pairs you can loop through
for key, value in server.items():
    print(f"  {key}: {value}")
# Output:
#   hostname: web-01
#   ip: 10.0.0.5
#   port: 80
```

---

## Checking If a Key Exists

```python
server = {"hostname": "web-01", "ip": "10.0.0.5"}

# Check with `in`
if "hostname" in server:
    print("Hostname is set")

if "region" not in server:
    print("No region configured")

# This is safer than just using server["region"]
```

---

## Nested Dictionaries

Dictionaries can contain other dictionaries. This is exactly how JSON data works (and JSON is everywhere in DevOps).

```python
# A server with nested configuration
server = {
    "hostname": "web-01",
    "network": {
        "ip": "10.0.0.5",
        "subnet": "10.0.0.0/24",
        "gateway": "10.0.0.1"
    },
    "resources": {
        "cpu_cores": 4,
        "memory_gb": 16,
        "disk_gb": 100
    }
}

# Access nested values with chained brackets
print(server["network"]["ip"])          # Output: 10.0.0.5
print(server["resources"]["cpu_cores"]) # Output: 4

# Safe nested access with .get()
dns = server.get("network", {}).get("dns", "not set")
print(dns)                               # Output: not set
```

---

## Building a Dictionary Step by Step

```python
# Start empty and build up
instance = {}

# Add basic info
instance["id"] = "i-0abc123def"
instance["type"] = "t3.medium"
instance["state"] = "running"

# Add tags as a nested dict
instance["tags"] = {
    "Name": "prod-web-01",
    "Environment": "production",
    "Team": "platform"
}

print(f"Instance {instance['id']} ({instance['type']})")
print(f"  Name: {instance['tags']['Name']}")
print(f"  Env:  {instance['tags']['Environment']}")
# Output:
# Instance i-0abc123def (t3.medium)
#   Name: prod-web-01
#   Env:  production
```

---

## DevOps Connection

| Use Case | Example |
|---|---|
| Server config | `{"hostname": "web-01", "ip": "10.0.0.5"}` |
| API responses | JSON from AWS, Azure, GCP APIs |
| Environment variables | `{"PATH": "/usr/bin", "HOME": "/root"}` |
| Terraform state | Resource attributes as key-value pairs |
| Docker labels | `{"app": "nginx", "version": "1.21"}` |
| Ansible variables | Host vars and group vars |

Dictionaries are the most important data structure for working with cloud APIs, configuration management, and infrastructure-as-code tools.

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks. Then run `python3 check.py` to see how you did!
