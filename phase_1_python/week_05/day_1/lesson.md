# Week 5, Day 1: Reading Files

## What You'll Learn
- How to open and read files in Python
- The `open()` function and file modes
- Reading methods: `read()`, `readline()`, `readlines()`
- The `with` statement for safe file handling
- Practical DevOps file reading patterns

---

## Why File Reading Matters in DevOps

As a DevOps engineer, you will constantly read files:
- **Log files** to troubleshoot problems
- **Configuration files** to understand system settings
- **Inventory files** to know what servers you manage
- **Reports** from monitoring tools

Python makes reading files simple and powerful.

---

## Opening a File with `open()`

The `open()` function is how Python accesses files on disk.

```python
# Basic syntax
file = open("filename.txt", "mode")

# Always close when done
file.close()
```

### File Modes for Reading

| Mode | Description |
|------|-------------|
| `"r"` | Read (default) - file must exist |
| `"rb"` | Read binary - for non-text files |

```python
# These two lines do the same thing
file = open("server.log")
file = open("server.log", "r")
```

If the file does not exist, Python raises a `FileNotFoundError`.

---

## The `with` Statement (Best Practice)

The `with` statement automatically closes the file when done, even if an error occurs. **Always use this approach.**

```python
# GOOD - file closes automatically
with open("server.log", "r") as file:
    content = file.read()
    print(content)
# File is closed here, no need to call file.close()

# BAD - you might forget to close
file = open("server.log", "r")
content = file.read()
file.close()  # Easy to forget!
```

---

## Reading Methods

### `read()` - Read the Entire File

Returns the whole file as one big string.

```python
with open("server.log", "r") as file:
    content = file.read()
    print(content)
    print(type(content))  # <class 'str'>
```

Best for: Small files where you need all the content at once.

### `readline()` - Read One Line at a Time

Returns a single line including the newline character `\n`.

```python
with open("server.log", "r") as file:
    first_line = file.readline()
    second_line = file.readline()
    print("Line 1:", first_line)
    print("Line 2:", second_line)
```

Each call to `readline()` advances to the next line.

### `readlines()` - Read All Lines into a List

Returns a list where each element is one line.

```python
with open("server.log", "r") as file:
    lines = file.readlines()
    print(type(lines))       # <class 'list'>
    print(len(lines))        # Number of lines
    print(lines[0])          # First line
    print(lines[-1])         # Last line
```

### Iterating Over Lines (Most Common)

The most memory-efficient way to process a file line by line:

```python
with open("server.log", "r") as file:
    for line in file:
        print(line.strip())  # strip() removes the trailing \n
```

This reads one line at a time, so it works even with very large files.

---

## Practical Examples

### Example 1: Count Lines in a Log File

```python
with open("server.log", "r") as file:
    line_count = 0
    for line in file:
        line_count += 1
    print(f"Total lines: {line_count}")
```

### Example 2: Search for Errors in a Log

```python
with open("server.log", "r") as file:
    error_count = 0
    for line in file:
        if "ERROR" in line:
            error_count += 1
            print(f"Found error: {line.strip()}")
    print(f"\nTotal errors: {error_count}")
```

### Example 3: Read a Server Inventory

```python
# inventory.txt contains one server per line:
# web-server-01
# web-server-02
# db-server-01

with open("inventory.txt", "r") as file:
    servers = []
    for line in file:
        server = line.strip()  # Remove whitespace and \n
        if server:             # Skip empty lines
            servers.append(server)

print(f"Managing {len(servers)} servers:")
for server in servers:
    print(f"  - {server}")
```

### Example 4: Read Specific Parts of a File

```python
with open("server.log", "r") as file:
    content = file.read()

# Split into lines
lines = content.split("\n")

# Get the first 5 lines
first_five = lines[:5]
print("First 5 lines:")
for line in first_five:
    print(f"  {line}")

# Get the last 3 lines
last_three = lines[-3:]
print("\nLast 3 lines:")
for line in last_three:
    print(f"  {line}")
```

---

## Useful String Methods for File Processing

When reading files, these string methods are essential:

```python
line = "  2024-01-15 ERROR: Disk full on web-server-01  \n"

line.strip()       # Remove whitespace from both ends
line.lstrip()      # Remove whitespace from left
line.rstrip()      # Remove whitespace from right
line.upper()       # Convert to uppercase
line.lower()       # Convert to lowercase
line.startswith("2024")  # Check if line starts with text
line.endswith("\n")      # Check if line ends with text
"ERROR" in line          # Check if text appears in line
line.split()             # Split by whitespace into a list
line.split(":")          # Split by a specific character
line.replace("ERROR", "WARN")  # Replace text
```

---

## DevOps Connection

Reading files is the foundation for:
- **Log analysis** - Parse application and system logs
- **Configuration management** - Read server configs
- **Monitoring** - Check status files and health reports
- **Automation** - Read input files for scripts
- **Auditing** - Review access logs and change records

In the next lesson, you will learn how to write files, completing the read/write cycle that powers most DevOps scripts.

---

## Key Takeaways

1. Use `open("filename", "r")` to open files for reading
2. **Always** use the `with` statement - it closes files automatically
3. `read()` gets everything, `readline()` gets one line, `readlines()` gets a list
4. Iterating with `for line in file:` is the most memory-efficient approach
5. Use `strip()` to remove trailing newlines from each line
