# Week 3, Day 2: List Methods

## What You'll Learn Today
- How to add items to a list (`append`, `insert`)
- How to remove items from a list (`remove`, `pop`)
- How to sort and reverse a list
- How to search a list with `index` and `count`
- How to slice lists to get sub-lists
- A first look at list comprehensions

---

## Adding Items to a List

### append() -- Add to the End

```python
# Start with two servers
servers = ["web-01", "web-02"]

# A new server comes online -- add it to the end
servers.append("web-03")
print(servers)
# Output: ['web-01', 'web-02', 'web-03']

# Add another
servers.append("db-01")
print(servers)
# Output: ['web-01', 'web-02', 'web-03', 'db-01']
```

### insert() -- Add at a Specific Position

```python
servers = ["web-01", "web-03", "db-01"]

# Oops, we need web-02 between web-01 and web-03
# insert(index, item) -- puts the item BEFORE that index
servers.insert(1, "web-02")
print(servers)
# Output: ['web-01', 'web-02', 'web-03', 'db-01']

# Insert at the very beginning (index 0)
servers.insert(0, "load-balancer")
print(servers)
# Output: ['load-balancer', 'web-01', 'web-02', 'web-03', 'db-01']
```

---

## Removing Items from a List

### remove() -- Remove by Value

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]

# Decommission the cache server
servers.remove("cache-01")
print(servers)
# Output: ['web-01', 'web-02', 'db-01']

# WARNING: remove() only removes the FIRST occurrence
# If the item isn't found, you get an error (ValueError)
```

### pop() -- Remove by Index (and Get the Value Back)

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]

# Remove the last server and see what it was
removed = servers.pop()
print(f"Removed: {removed}")   # Output: Removed: cache-01
print(servers)                  # Output: ['web-01', 'web-02', 'db-01']

# Remove a specific index
removed = servers.pop(0)
print(f"Removed: {removed}")   # Output: Removed: web-01
print(servers)                  # Output: ['web-02', 'db-01']
```

---

## Sorting and Reversing

### sort() -- Sort in Place

```python
servers = ["db-01", "web-02", "cache-01", "web-01"]

# Sort alphabetically (modifies the list directly)
servers.sort()
print(servers)
# Output: ['cache-01', 'db-01', 'web-01', 'web-02']

# Sort in reverse order
servers.sort(reverse=True)
print(servers)
# Output: ['web-02', 'web-01', 'db-01', 'cache-01']

# Sorting numbers
response_times = [230, 45, 120, 89, 310]
response_times.sort()
print(response_times)
# Output: [45, 89, 120, 230, 310]
```

### reverse() -- Flip the Order

```python
deploy_order = ["database", "backend", "frontend"]

# Reverse for rollback order
deploy_order.reverse()
print(deploy_order)
# Output: ['frontend', 'backend', 'database']
```

---

## Searching a List

### index() -- Find the Position of an Item

```python
servers = ["web-01", "web-02", "db-01", "cache-01"]

# Where is db-01?
position = servers.index("db-01")
print(position)    # Output: 2

# WARNING: Raises ValueError if not found
```

### count() -- Count Occurrences

```python
status_codes = [200, 200, 404, 200, 500, 404, 200]

# How many 200 responses?
ok_count = status_codes.count(200)
print(f"Successful responses: {ok_count}")
# Output: Successful responses: 4

# How many errors?
not_found = status_codes.count(404)
errors = status_codes.count(500)
print(f"404 errors: {not_found}, 500 errors: {errors}")
# Output: 404 errors: 2, 500 errors: 1
```

---

## Slicing -- Getting a Sub-list

Slicing lets you grab a portion of a list using `list[start:stop]`. The `start` index is included, but the `stop` index is NOT.

```python
servers = ["web-01", "web-02", "db-01", "cache-01", "monitor-01"]

# Get the first two servers (index 0 and 1)
first_two = servers[0:2]
print(first_two)
# Output: ['web-01', 'web-02']

# Get servers from index 2 to end
rest = servers[2:]
print(rest)
# Output: ['db-01', 'cache-01', 'monitor-01']

# Get the first three
first_three = servers[:3]
print(first_three)
# Output: ['web-01', 'web-02', 'db-01']

# Get every other server (step of 2)
every_other = servers[::2]
print(every_other)
# Output: ['web-01', 'db-01', 'monitor-01']

# Reverse a list with slicing
backwards = servers[::-1]
print(backwards)
# Output: ['monitor-01', 'cache-01', 'db-01', 'web-02', 'web-01']
```

---

## List Comprehensions -- A First Look

A list comprehension is a compact way to create a new list by transforming each item from an existing list. Don't worry if this feels advanced -- you'll use it more as you go.

```python
# Regular way: add "-prod" to each server name
servers = ["web-01", "web-02", "db-01"]
prod_servers = []
for s in servers:
    prod_servers.append(s + "-prod")
print(prod_servers)
# Output: ['web-01-prod', 'web-02-prod', 'db-01-prod']

# List comprehension way (same result, one line)
prod_servers = [s + "-prod" for s in servers]
print(prod_servers)
# Output: ['web-01-prod', 'web-02-prod', 'db-01-prod']

# Another example: extract just the port numbers that are above 1000
ports = [22, 80, 443, 3306, 8080, 5432]
high_ports = [p for p in ports if p > 1000]
print(high_ports)
# Output: [3306, 8080, 5432]
```

---

## DevOps Connection

| Method | DevOps Use Case |
|---|---|
| `append()` | Add a new server to the fleet |
| `remove()` | Decommission a server |
| `sort()` | Prioritize deployment targets |
| `pop()` | Process a queue (take next item) |
| `count()` | Count error occurrences in logs |
| Slicing | Get a batch of servers for rolling deploy |
| Comprehensions | Transform hostnames, filter results |

These methods are the building blocks of any automation script that manages lists of resources.

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks. Then run `python3 check.py` to see how you did!
