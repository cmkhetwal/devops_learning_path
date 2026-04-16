# Week 5, Day 2: Writing Files

## What You'll Learn
- How to write and create files with Python
- The `write()` and `writelines()` methods
- Write mode vs. append mode
- Working with CSV files using the `csv` module
- Practical DevOps file writing patterns

---

## Why File Writing Matters in DevOps

Writing files is how your scripts produce output:
- **Reports** - Generate status reports and summaries
- **Configurations** - Create or update config files for servers
- **Logs** - Record what your automation scripts do
- **Exports** - Write data in formats other tools can read (CSV, etc.)
- **Inventory files** - Maintain lists of servers and resources

---

## Writing Files with `open()`

### File Modes for Writing

| Mode | Description |
|------|-------------|
| `"w"` | Write - creates new file or **overwrites** existing |
| `"a"` | Append - creates new file or **adds to end** of existing |
| `"x"` | Exclusive create - fails if file already exists |

**Warning:** Using `"w"` mode on an existing file will erase all its contents!

---

## The `write()` Method

Writes a string to the file. Does **not** add a newline automatically.

```python
# Create a new file and write to it
with open("status.txt", "w") as file:
    file.write("Server Status Report\n")
    file.write("====================\n")
    file.write("web-01: ONLINE\n")
    file.write("web-02: ONLINE\n")
    file.write("db-01: ONLINE\n")
```

You must include `\n` yourself for new lines.

### Using f-strings with write()

```python
server = "web-01"
status = "ONLINE"
cpu = 45.2

with open("report.txt", "w") as file:
    file.write(f"Server: {server}\n")
    file.write(f"Status: {status}\n")
    file.write(f"CPU Usage: {cpu}%\n")
```

---

## The `writelines()` Method

Writes a list of strings. Like `write()`, it does **not** add newlines.

```python
lines = [
    "web-01\n",
    "web-02\n",
    "web-03\n",
    "db-01\n",
]

with open("servers.txt", "w") as file:
    file.writelines(lines)
```

A common pattern is to add newlines with a list comprehension:

```python
servers = ["web-01", "web-02", "web-03", "db-01"]

with open("servers.txt", "w") as file:
    file.writelines(f"{server}\n" for server in servers)
```

---

## Append Mode: Adding to Files

Append mode adds new content to the end of an existing file.

```python
# First, create the file
with open("deploy.log", "w") as file:
    file.write("Deployment started\n")

# Later, add more entries
with open("deploy.log", "a") as file:
    file.write("Step 1: Downloaded package\n")
    file.write("Step 2: Installed dependencies\n")

# Add even more
with open("deploy.log", "a") as file:
    file.write("Step 3: Deployment complete\n")
```

Reading the file now shows all four lines.

---

## Write Mode vs. Append Mode

```python
# WRITE mode - overwrites everything!
with open("test.txt", "w") as f:
    f.write("First write\n")

with open("test.txt", "w") as f:
    f.write("Second write\n")

# test.txt contains ONLY "Second write\n"

# APPEND mode - keeps everything!
with open("test.txt", "a") as f:
    f.write("First append\n")

with open("test.txt", "a") as f:
    f.write("Second append\n")

# test.txt now has "Second write\n", "First append\n", "Second append\n"
```

---

## Working with CSV Files

CSV (Comma-Separated Values) is one of the most common formats for data exchange. Python has a built-in `csv` module.

### Writing CSV Files

```python
import csv

servers = [
    ["hostname", "ip", "status", "cpu"],
    ["web-01", "10.0.1.10", "online", "45%"],
    ["web-02", "10.0.1.11", "online", "62%"],
    ["db-01", "10.0.2.10", "online", "78%"],
    ["db-02", "10.0.2.11", "offline", "0%"],
]

with open("inventory.csv", "w", newline="") as file:
    writer = csv.writer(file)
    for row in servers:
        writer.writerow(row)
```

**Important:** Always use `newline=""` when opening CSV files. This prevents extra blank lines on some systems.

### Writing CSV with `writerows()`

```python
import csv

# Write all rows at once
with open("inventory.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerows(servers)  # Write the entire list
```

### Writing CSV from Dictionaries

```python
import csv

servers = [
    {"hostname": "web-01", "ip": "10.0.1.10", "status": "online"},
    {"hostname": "web-02", "ip": "10.0.1.11", "status": "online"},
    {"hostname": "db-01", "ip": "10.0.2.10", "status": "offline"},
]

with open("inventory.csv", "w", newline="") as file:
    fieldnames = ["hostname", "ip", "status"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()    # Writes the header row
    writer.writerows(servers)  # Writes all data rows
```

### Reading CSV Files

```python
import csv

with open("inventory.csv", "r") as file:
    reader = csv.reader(file)
    header = next(reader)  # Get the first row (header)
    print(f"Columns: {header}")
    for row in reader:
        print(f"Server: {row[0]}, IP: {row[1]}, Status: {row[2]}")
```

### Reading CSV into Dictionaries

```python
import csv

with open("inventory.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        print(f"{row['hostname']} ({row['ip']}) - {row['status']}")
```

---

## Practical Examples

### Example 1: Generate a Server Status Report

```python
import datetime

servers = {
    "web-01": {"status": "online", "cpu": 45, "memory": 62},
    "web-02": {"status": "online", "cpu": 71, "memory": 80},
    "db-01": {"status": "offline", "cpu": 0, "memory": 0},
}

with open("status_report.txt", "w") as report:
    report.write("SERVER STATUS REPORT\n")
    report.write(f"Generated: {datetime.datetime.now()}\n")
    report.write("=" * 40 + "\n\n")

    for name, info in servers.items():
        report.write(f"Server: {name}\n")
        report.write(f"  Status: {info['status']}\n")
        report.write(f"  CPU:    {info['cpu']}%\n")
        report.write(f"  Memory: {info['memory']}%\n")
        report.write("\n")

    online = sum(1 for s in servers.values() if s["status"] == "online")
    report.write(f"Summary: {online}/{len(servers)} servers online\n")
```

### Example 2: Build an Inventory CSV

```python
import csv

inventory = [
    {"name": "web-01", "role": "webserver", "os": "Ubuntu 22.04", "ram_gb": 16},
    {"name": "web-02", "role": "webserver", "os": "Ubuntu 22.04", "ram_gb": 16},
    {"name": "db-01", "role": "database", "os": "Ubuntu 22.04", "ram_gb": 64},
    {"name": "lb-01", "role": "loadbalancer", "os": "Ubuntu 22.04", "ram_gb": 8},
]

with open("full_inventory.csv", "w", newline="") as file:
    fields = ["name", "role", "os", "ram_gb"]
    writer = csv.DictWriter(file, fieldnames=fields)
    writer.writeheader()
    writer.writerows(inventory)

print("Inventory written to full_inventory.csv")
```

---

## DevOps Connection

Writing files powers many DevOps tasks:
- **Report generation** - Automated daily/weekly status reports
- **Configuration creation** - Generate configs from templates
- **Data export** - Export metrics and logs to CSV for analysis
- **Audit trails** - Record changes made by automation scripts
- **Infrastructure as Code** - Generate config files programmatically

---

## Key Takeaways

1. `"w"` mode creates or **overwrites**; `"a"` mode creates or **appends**
2. `write()` does not add newlines - you must include `\n` yourself
3. `writelines()` writes a list of strings (also no automatic newlines)
4. Always use `newline=""` when opening CSV files
5. The `csv` module handles commas, quotes, and special characters properly
6. Use `csv.DictWriter` when working with dictionaries for cleaner code
