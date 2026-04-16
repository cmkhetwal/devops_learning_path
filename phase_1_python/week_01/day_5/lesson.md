# Week 1, Day 5: Strings Deep Dive

## What You'll Learn Today
- How to access individual characters in a string (indexing)
- How to grab parts of a string (slicing)
- Powerful built-in string methods
- Advanced f-string formatting tricks

## String Indexing
Every character in a string has a position number (index), starting at 0.

```python
hostname = "web-server-01"
#           0123456789...

# Access individual characters with square brackets
print(hostname[0])     # w   (first character)
print(hostname[1])     # e   (second character)
print(hostname[4])     # s

# Negative indexing counts from the end
print(hostname[-1])    # 1   (last character)
print(hostname[-2])    # 0   (second to last)

# Get the length of a string
print(len(hostname))   # 13
```

## String Slicing
Slicing lets you grab a portion of a string: `string[start:end]`

The `start` is included, the `end` is NOT included.

```python
log_line = "ERROR: Disk full on server-05"

# Basic slicing: [start:end]
print(log_line[0:5])      # ERROR  (characters 0,1,2,3,4)
print(log_line[7:16])     # Disk full

# Omit start = start from beginning
print(log_line[:5])       # ERROR

# Omit end = go to the end
print(log_line[7:])       # Disk full on server-05

# Negative slicing
print(log_line[-9:])      # server-05  (last 9 characters)

# Step (every Nth character)
text = "abcdefgh"
print(text[::2])          # aceg  (every 2nd character)

# Reverse a string
print(text[::-1])         # hgfedcba
```

### Slicing Cheat Sheet
```python
s = "Hello"
# s[start:end:step]
# s[0:3]   -> "Hel"     characters 0, 1, 2
# s[:3]    -> "Hel"     same (start defaults to 0)
# s[2:]    -> "llo"     from index 2 to end
# s[-2:]   -> "lo"      last 2 characters
# s[:]     -> "Hello"   full copy
# s[::-1]  -> "olleH"   reversed
```

## String Methods
Methods are actions you can perform on a string. Call them with a dot: `string.method()`

### Case Methods
```python
status = "Server Running"

print(status.upper())     # SERVER RUNNING
print(status.lower())     # server running
print(status.title())     # Server Running
print(status.swapcase())  # sERVER rUNNING
```

### Whitespace Methods
```python
# strip() removes whitespace from both ends
messy = "   web-server-01   "
print(messy.strip())        # "web-server-01"
print(messy.lstrip())       # "web-server-01   "  (left only)
print(messy.rstrip())       # "   web-server-01"  (right only)

# Also strips newlines and tabs
log = "\n  ERROR: timeout  \n"
print(log.strip())          # "ERROR: timeout"
```

### Search Methods
```python
log = "ERROR: Connection timeout on server-05 at port 8080"

# find() returns the position of a substring (-1 if not found)
print(log.find("timeout"))      # 19
print(log.find("missing"))      # -1

# count() counts how many times a substring appears
text = "error error warning error info"
print(text.count("error"))      # 3
print(text.count("warning"))    # 1

# startswith() and endswith() return True/False
filename = "deploy-log-2024.txt"
print(filename.startswith("deploy"))    # True
print(filename.endswith(".txt"))        # True
print(filename.endswith(".log"))        # False
```

### Split and Join
```python
# split() breaks a string into a list of parts
log_line = "2024-01-15 ERROR Server timeout"
parts = log_line.split(" ")
print(parts)    # ['2024-01-15', 'ERROR', 'Server', 'timeout']
print(parts[0]) # 2024-01-15  (the date)
print(parts[1]) # ERROR       (the level)

# Split on different characters
path = "/var/log/nginx/error.log"
folders = path.split("/")
print(folders)  # ['', 'var', 'log', 'nginx', 'error.log']

csv_line = "web-01,8080,us-east-1,running"
fields = csv_line.split(",")
print(fields)   # ['web-01', '8080', 'us-east-1', 'running']

# join() combines a list into a string (opposite of split)
servers = ["web-01", "web-02", "web-03"]
result = ", ".join(servers)
print(result)   # web-01, web-02, web-03

result2 = " | ".join(servers)
print(result2)  # web-01 | web-02 | web-03
```

### Replace
```python
# replace(old, new) swaps text
config = "host=localhost port=3000"
prod_config = config.replace("localhost", "prod-server-01")
print(prod_config)  # host=prod-server-01 port=3000

# Replace multiple occurrences
log = "ERROR: disk full. ERROR: memory low."
clean = log.replace("ERROR", "WARN")
print(clean)  # WARN: disk full. WARN: memory low.
```

## f-string Formatting (Advanced)
Building on what you learned in Day 3, here are more tricks.

```python
# Align text in columns
name = "web-01"
status = "running"
cpu = 45.7

# Left-align (<), right-align (>), center (^)
print(f"{'Server':<15} {'Status':<10} {'CPU':>6}")
print(f"{name:<15} {status:<10} {cpu:>5.1f}%")
# Output:
# Server          Status     CPU
# web-01          running    45.7%

# Repeat a character
print(f"{'─' * 35}")    # ───────────────────────────────────

# Combine everything for a table
print(f"{'=' * 35}")
print(f"{'Server':<15} {'Status':<10} {'CPU':>6}")
print(f"{'─' * 35}")
print(f"{'web-01':<15} {'running':<10} {'45.7':>5}%")
print(f"{'web-02':<15} {'stopped':<10} {'0.0':>5}%")
print(f"{'web-03':<15} {'running':<10} {'82.3':>5}%")
print(f"{'=' * 35}")
```

## Key Concepts
| Method | Example | Result |
|--------|---------|--------|
| `s[0]` | `"hello"[0]` | `"h"` |
| `s[1:4]` | `"hello"[1:4]` | `"ell"` |
| `.upper()` | `"hello".upper()` | `"HELLO"` |
| `.lower()` | `"HELLO".lower()` | `"hello"` |
| `.strip()` | `" hi ".strip()` | `"hi"` |
| `.split(",")` | `"a,b,c".split(",")` | `["a","b","c"]` |
| `",".join(list)` | `",".join(["a","b"])` | `"a,b"` |
| `.replace(a,b)` | `"hi".replace("hi","bye")` | `"bye"` |
| `.find(x)` | `"hello".find("ll")` | `2` |
| `.startswith(x)` | `"log.txt".startswith("log")` | `True` |
| `.endswith(x)` | `"log.txt".endswith(".txt")` | `True` |
| `.count(x)` | `"abab".count("ab")` | `2` |

## DevOps Connection
String manipulation is essential for DevOps scripting:
```python
# Parse a log entry
log = "2024-01-15 14:30:22 ERROR [nginx] Connection refused to 10.0.1.5:443"
date = log[:10]
time = log[11:19]
level = log[20:25]
message = log[34:]
print(f"Date: {date}, Level: {level}, Message: {message}")

# Extract hostname from URL
url = "https://api.example.com:8443/health"
# Remove protocol
without_proto = url.split("://")[1]  # "api.example.com:8443/health"
# Get hostname
hostname = without_proto.split(":")[0]  # "api.example.com"
print(f"Hostname: {hostname}")

# Check log files for errors
filename = "app-error-2024.log"
if filename.endswith(".log") and "error" in filename:
    print("This is an error log file")
```

## Now Do The Exercise!
Open `exercise.py` and complete the tasks.
Then run `python3 check.py` to verify your answers.
