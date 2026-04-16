# Week 2, Day 5: Loop Control

## What You'll Learn Today

- How to use `break` to exit a loop early
- How to use `continue` to skip an iteration
- How nested loops work (a loop inside a loop)
- How the `else` clause on loops works

---

## 1. The `break` Statement

`break` immediately stops the loop and jumps to the code after it.

```python
# Search for a specific server and stop when found
servers = ["web-01", "web-02", "db-01", "web-03"]

for server in servers:
    print(f"Checking {server}...")
    if server == "db-01":
        print(f"Found database server: {server}")
        break    # Stop the loop right here!

# Output:
# Checking web-01...
# Checking web-02...
# Checking db-01...
# Found database server: db-01
# (web-03 is never checked!)
```

**When to use `break`:** When you found what you are looking for and do not need to keep searching.

---

## 2. The `continue` Statement

`continue` skips the rest of the current iteration and moves to the next one.

```python
# Skip servers that are in maintenance
servers = ["web-01", "web-02", "web-03", "web-04"]
maintenance = ["web-02", "web-04"]

for server in servers:
    if server in maintenance:
        print(f"Skipping {server} (in maintenance)")
        continue    # Skip to next server, do NOT run the lines below

    print(f"Deploying to {server}...")

# Output:
# Deploying to web-01...
# Skipping web-02 (in maintenance)
# Deploying to web-03...
# Skipping web-04 (in maintenance)
```

**When to use `continue`:** When you want to skip certain items but keep going through the rest.

---

## 3. Break vs. Continue

```python
# BREAK = "Stop the entire loop"
# CONTINUE = "Skip this one, keep going"

numbers = [1, 2, 3, 4, 5]

# break example: stops at 3
print("Break example:")
for n in numbers:
    if n == 3:
        break
    print(n)
# Output: 1, 2

# continue example: skips 3
print("Continue example:")
for n in numbers:
    if n == 3:
        continue
    print(n)
# Output: 1, 2, 4, 5
```

---

## 4. Nested Loops

A loop inside another loop. The inner loop runs completely for each iteration of the outer loop.

```python
# Check each server on each port
servers = ["web-01", "web-02"]
ports = [80, 443, 8080]

for server in servers:
    for port in ports:
        print(f"Checking {server}:{port}")

# Output:
# Checking web-01:80
# Checking web-01:443
# Checking web-01:8080
# Checking web-02:80
# Checking web-02:443
# Checking web-02:8080
```

**How nested loops work:**
1. Outer loop picks "web-01"
2. Inner loop runs ALL its iterations (80, 443, 8080)
3. Outer loop picks "web-02"
4. Inner loop runs ALL its iterations again

---

## 5. Break in Nested Loops

`break` only breaks out of the **innermost** loop:

```python
# Find the first open port for each server
servers = ["web-01", "web-02"]
ports = [22, 80, 443, 8080]

for server in servers:
    print(f"Scanning {server}...")
    for port in ports:
        print(f"  Checking port {port}...")
        if port == 80:
            print(f"  Found open port {port}!")
            break    # Breaks inner loop only, outer loop continues
    # After breaking, we continue with the next server

# Output:
# Scanning web-01...
#   Checking port 22...
#   Checking port 80...
#   Found open port 80!
# Scanning web-02...
#   Checking port 22...
#   Checking port 80...
#   Found open port 80!
```

---

## 6. The `else` Clause on Loops

Python has a unique feature: you can put `else` on a `for` or `while` loop.
The `else` block runs ONLY if the loop finished normally (without hitting `break`).

```python
# Search for a critical error in logs
log_entries = ["INFO: Started", "WARNING: Slow query", "INFO: Request OK"]

for entry in log_entries:
    if "CRITICAL" in entry:
        print(f"Found critical error: {entry}")
        break
else:
    # This runs because the loop finished without break
    print("No critical errors found!")

# Output: No critical errors found!
```

```python
# Now with a critical error present
log_entries = ["INFO: Started", "CRITICAL: Disk full", "INFO: Request OK"]

for entry in log_entries:
    if "CRITICAL" in entry:
        print(f"Found critical error: {entry}")
        break
else:
    print("No critical errors found!")

# Output: Found critical error: CRITICAL: Disk full
# (The else block does NOT run because we hit break)
```

---

## 7. Combining Everything

```python
# Real-world example: Find the first available port
used_ports = [80, 443, 3000, 5000, 8080]
port_range = range(80, 8090)

for port in port_range:
    if port in used_ports:
        continue          # Skip used ports
    print(f"First available port: {port}")
    break                 # Found one, stop looking
else:
    print("No available ports in range!")

# Output: First available port: 81
```

---

## 8. While Loop with Break and Continue

These work in `while` loops too:

```python
# Process log lines, skip blanks, stop at END marker
log_lines = ["Server started", "", "Request received", "END", "This is ignored"]
index = 0

while index < len(log_lines):
    line = log_lines[index]
    index += 1

    if line == "":
        continue       # Skip empty lines

    if line == "END":
        print("Reached end of log")
        break          # Stop processing

    print(f"Processing: {line}")

# Output:
# Processing: Server started
# Processing: Request received
# Reached end of log
```

---

## DevOps Connection

Loop control is critical in DevOps automation:

- **`break` in searching**: Stop scanning once you find the issue in logs
- **`continue` for filtering**: Skip healthy servers, only process the failing ones
- **Nested loops for matrix operations**: Test all combinations of servers and ports
- **`else` on loops**: Know whether a search was successful or not
- **Port scanning**: Find the first available port in a range

---

## Now Do The Exercise!

Open `exercise.py` and complete all 5 tasks.
When you are done, run `python check.py` to see your score.
