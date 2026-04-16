# Week 2, Day 4: For Loops

## What You'll Learn Today

- How to use `for` loops to iterate over sequences
- How to use `range()` to generate number sequences
- How to loop through strings, lists, and more
- The difference between `for` loops and `while` loops

---

## 1. What Is a For Loop?

A `for` loop goes through each item in a sequence, one at a time.

```python
# Loop through a list of servers
servers = ["web-01", "web-02", "db-01", "cache-01"]

for server in servers:
    print(f"Pinging {server}...")

# Output:
# Pinging web-01...
# Pinging web-02...
# Pinging db-01...
# Pinging cache-01...
```

**How it works:**
1. Take the first item from the list, put it in `server`
2. Run the indented code
3. Take the next item, put it in `server`
4. Repeat until there are no more items

---

## 2. The `range()` Function

`range()` generates a sequence of numbers. It is the most common way to loop a specific number of times.

```python
# range(5) gives you: 0, 1, 2, 3, 4  (starts at 0, stops BEFORE 5)
for i in range(5):
    print(f"Iteration {i}")

# Output:
# Iteration 0
# Iteration 1
# Iteration 2
# Iteration 3
# Iteration 4
```

### Three Ways to Use `range()`

```python
# range(stop) -- starts at 0, goes up to stop-1
for i in range(3):
    print(i)          # 0, 1, 2

# range(start, stop) -- starts at start, goes up to stop-1
for i in range(1, 4):
    print(i)          # 1, 2, 3

# range(start, stop, step) -- starts at start, goes up by step
for i in range(0, 10, 2):
    print(i)          # 0, 2, 4, 6, 8

# Counting backwards
for i in range(5, 0, -1):
    print(i)          # 5, 4, 3, 2, 1
```

---

## 3. Looping Through Strings

Strings are sequences of characters, so you can loop through them:

```python
# Loop through each character in a string
hostname = "web-01"

for char in hostname:
    print(char)

# Output:
# w
# e
# b
# -
# 0
# 1
```

---

## 4. Looping Through a List of Servers

```python
# A very common DevOps pattern: do something to each server
servers = ["192.168.1.1", "192.168.1.2", "192.168.1.3"]

for ip in servers:
    print(f"Checking server at {ip}...")
    print(f"  Server {ip} is reachable")

print("All servers checked!")
```

---

## 5. Using `range()` for Port Scanning

```python
# Print a range of ports
print("Common web ports:")
for port in range(8080, 8086):
    print(f"  Port {port}")

# Output:
# Common web ports:
#   Port 8080
#   Port 8081
#   Port 8082
#   Port 8083
#   Port 8084
#   Port 8085
```

---

## 6. Building Strings and Totals in Loops

You can accumulate values as you loop:

```python
# Count total servers
environments = ["prod", "staging", "dev", "prod", "prod"]
prod_count = 0

for env in environments:
    if env == "prod":
        prod_count += 1

print(f"Production servers: {prod_count}")   # Production servers: 3
```

```python
# Build a string
server_names = ["web", "api", "db"]
report = ""

for name in server_names:
    report = report + name + ", "

print(f"Servers: {report}")   # Servers: web, api, db,
```

---

## 7. Enumerate -- Getting Index AND Value

Sometimes you need both the position and the value:

```python
# enumerate() gives you the index and the item
servers = ["web-01", "web-02", "db-01"]

for index, server in enumerate(servers):
    print(f"Server #{index + 1}: {server}")

# Output:
# Server #1: web-01
# Server #2: web-02
# Server #3: db-01
```

---

## 8. For Loop vs. While Loop

```python
# FOR loop: Use when you know how many times to loop
#           or when you are going through a collection
for i in range(5):
    print(i)

# WHILE loop: Use when you do NOT know when to stop
#             (loop until a condition changes)
count = 0
while count < 5:
    print(count)
    count += 1

# Both produce the same output, but for loops are cleaner
# when you know the number of iterations
```

**Rule of thumb:**
- Know how many times? Use `for`
- Don't know, waiting for something? Use `while`

---

## DevOps Connection

For loops are used constantly in DevOps:

- **Iterating over server lists**: Apply a config to each server
- **Port scanning**: Check a range of ports
- **Log processing**: Go through each line in a log file
- **IP address generation**: Generate IPs in a subnet
- **Batch operations**: Restart multiple services, deploy to multiple environments

```python
# Real-world pattern: Check multiple servers
servers = [
    {"name": "web-01", "port": 80},
    {"name": "web-02", "port": 80},
    {"name": "api-01", "port": 443},
]

for server in servers:
    print(f"Checking {server['name']} on port {server['port']}...")
```

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks.
When you are done, run `python check.py` to see your score.
