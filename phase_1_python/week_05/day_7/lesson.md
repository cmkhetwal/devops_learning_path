# Week 5, Day 7: Cheat Sheet & Quiz

## Week 5 Cheat Sheet: File Handling & Error Management

Use this as a quick reference for everything covered this week.

---

## Reading Files

```python
# Read entire file as one string
with open("file.txt", "r") as f:
    content = f.read()

# Read all lines into a list
with open("file.txt", "r") as f:
    lines = f.readlines()

# Read one line at a time (most memory-efficient)
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())

# Read single line
with open("file.txt", "r") as f:
    first_line = f.readline()
```

---

## Writing Files

```python
# Write (creates or overwrites)
with open("file.txt", "w") as f:
    f.write("Hello\n")
    f.write("World\n")

# Append (creates or adds to end)
with open("file.txt", "a") as f:
    f.write("New line at the end\n")

# Write a list of strings
lines = ["line 1\n", "line 2\n", "line 3\n"]
with open("file.txt", "w") as f:
    f.writelines(lines)
```

---

## File Modes

| Mode | Description |
|------|-------------|
| `"r"` | Read (default, file must exist) |
| `"w"` | Write (creates or overwrites) |
| `"a"` | Append (creates or adds to end) |
| `"x"` | Exclusive create (fails if exists) |
| `"rb"` | Read binary |
| `"wb"` | Write binary |

---

## CSV Files

```python
import csv

# Write CSV
with open("data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "age"])     # Header
    writer.writerow(["Alice", 30])       # Data row
    writer.writerows([["Bob", 25], ["Charlie", 35]])  # Multiple rows

# Write CSV from dictionaries
with open("data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "age"])
    writer.writeheader()
    writer.writerow({"name": "Alice", "age": 30})

# Read CSV
with open("data.csv", "r") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        print(row)

# Read CSV as dictionaries
with open("data.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["name"], row["age"])
```

---

## JSON

```python
import json

# Read JSON file
with open("config.json", "r") as f:
    data = json.load(f)

# Write JSON file
with open("config.json", "w") as f:
    json.dump(data, f, indent=4)

# Parse JSON string
data = json.loads('{"key": "value"}')

# Convert to JSON string
text = json.dumps(data, indent=2)
```

---

## YAML

```python
import yaml  # pip install pyyaml

# Read YAML file
with open("config.yaml", "r") as f:
    data = yaml.safe_load(f)

# Write YAML file
with open("config.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False)

# Parse YAML string
data = yaml.safe_load(yaml_string)
```

---

## Error Handling

```python
# Basic try/except
try:
    risky_operation()
except SpecificError as e:
    print(f"Error: {e}")

# Multiple except blocks
try:
    data = json.load(open("config.json"))
except FileNotFoundError:
    print("File not found")
except json.JSONDecodeError:
    print("Invalid JSON")

# Full structure
try:
    result = operation()
except SomeError as e:
    print(f"Failed: {e}")
else:
    print(f"Success: {result}")  # Only if no error
finally:
    cleanup()  # Always runs

# Raise your own
raise ValueError("Port must be between 1 and 65535")

# Custom exceptions
class ConfigError(Exception):
    pass

raise ConfigError("Missing required field: hostname")
```

### Common Exception Types

| Exception | Cause |
|-----------|-------|
| `FileNotFoundError` | File does not exist |
| `PermissionError` | No permission |
| `json.JSONDecodeError` | Invalid JSON |
| `KeyError` | Missing dict key |
| `ValueError` | Invalid value |
| `TypeError` | Wrong type |
| `IndexError` | List index out of range |
| `IOError` / `OSError` | I/O failure |

---

## Logging

```python
import logging

# Quick setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("Message here")

# Log to file
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Custom logger with handlers
logger = logging.getLogger("myapp")
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler("myapp.log")
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(handler)

logger.debug("Detail")     # Level 10
logger.info("Progress")    # Level 20
logger.warning("Concern")  # Level 30
logger.error("Failure")    # Level 40
logger.critical("Crash")   # Level 50

# Log rotation
from logging.handlers import RotatingFileHandler
handler = RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=5)
```

---

## Common Patterns

### Safe File Reader
```python
def safe_read(filepath, default=""):
    try:
        with open(filepath, "r") as f:
            return f.read()
    except (FileNotFoundError, PermissionError):
        return default
```

### Safe JSON Loader
```python
def safe_load_json(filepath, default=None):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}
```

### Process Multiple Files
```python
for filename in file_list:
    try:
        with open(filename, "r") as f:
            data = f.read()
        process(data)
    except FileNotFoundError:
        logging.warning(f"Skipping {filename}: not found")
    except Exception as e:
        logging.error(f"Error processing {filename}: {e}")
```

---

## Quick Tips

1. **Always use `with`** for file operations (auto-closes files)
2. **Always use `newline=""`** when opening CSV files
3. **Always use `yaml.safe_load()`** not `yaml.load()`
4. **Always catch specific exceptions** not bare `except:`
5. **Use `indent=4`** for readable JSON output
6. **Use `strip()`** to remove trailing newlines from file lines
7. **Use `logging`** instead of `print()` in production scripts
