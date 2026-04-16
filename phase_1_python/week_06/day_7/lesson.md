# Week 6, Day 7: Quiz Day -- Cheat Sheet & Review

## Week 6 Cheat Sheet: OS & System Automation

Keep this as a quick reference for everything you learned this week.

---

### os Module (Day 1)

```python
import os

# Navigation
os.getcwd()                          # Current working directory
os.listdir("/var/log")               # List directory contents
os.chdir("/tmp")                     # Change directory

# Paths
os.path.join("/var", "log", "app.log")   # Build paths safely
os.path.exists("/etc/hosts")             # Does it exist?
os.path.isfile("/etc/hosts")             # Is it a file?
os.path.isdir("/var/log")                # Is it a directory?
os.path.basename("/var/log/app.log")     # "app.log"
os.path.dirname("/var/log/app.log")      # "/var/log"
os.path.splitext("app.log")             # ("app", ".log")
os.path.getsize("/etc/hosts")           # Size in bytes
os.path.abspath("relative/path")        # Full absolute path

# Directories
os.mkdir("new_dir")                      # Create one directory
os.makedirs("a/b/c", exist_ok=True)     # Create nested dirs

# Environment Variables
os.getenv("DB_HOST")                     # Returns None if not set
os.getenv("DB_HOST", "localhost")        # Returns "localhost" if not set
os.environ["DB_HOST"]                    # Raises KeyError if not set
os.environ["APP_ENV"] = "production"     # Set an env var
```

---

### subprocess Module (Day 2)

```python
import subprocess

# Run a command and capture output
result = subprocess.run(
    ["command", "arg1", "arg2"],
    capture_output=True,     # Capture stdout/stderr
    text=True,               # Return strings, not bytes
    timeout=10,              # Timeout in seconds
    check=True               # Raise exception on failure
)

result.stdout                # Standard output (string)
result.stderr                # Standard error (string)
result.returncode            # 0 = success, non-zero = failure

# Shell mode (for pipes, redirects)
result = subprocess.run("ps aux | grep python", shell=True, capture_output=True, text=True)

# Pass environment variables
import os
my_env = os.environ.copy()
my_env["KEY"] = "value"
subprocess.run(["cmd"], env=my_env)

# Handle errors
try:
    subprocess.run(["cmd"], check=True, capture_output=True, text=True)
except subprocess.CalledProcessError as e:
    print(f"Failed: {e.stderr}")
except subprocess.TimeoutExpired:
    print("Command timed out")
except FileNotFoundError:
    print("Command not found")
```

---

### shutil Module (Day 3)

```python
import shutil

# Copy
shutil.copy("src.txt", "dst.txt")              # Copy file
shutil.copy2("src.txt", "dst.txt")             # Copy with metadata
shutil.copytree("src_dir/", "dst_dir/")        # Copy entire directory

# Move / Rename
shutil.move("old.txt", "new.txt")              # Move or rename

# Delete
shutil.rmtree("directory/")                     # Delete directory tree
shutil.rmtree("dir/", ignore_errors=True)       # Ignore errors

# Disk Usage
usage = shutil.disk_usage("/")
usage.total    # Total bytes
usage.used     # Used bytes
usage.free     # Free bytes
```

---

### pathlib Module (Day 3)

```python
from pathlib import Path

# Create paths
p = Path("/var/log/app.log")
p = Path.home() / ".config" / "myapp"     # Build with /

# Path properties
p.name           # "app.log"
p.stem           # "app"
p.suffix         # ".log"
p.parent         # Path("/var/log")
p.parts          # ("/", "var", "log", "app.log")

# Check paths
p.exists()       # Does it exist?
p.is_file()      # Is it a file?
p.is_dir()       # Is it a directory?

# Create directories
Path("a/b/c").mkdir(parents=True, exist_ok=True)

# Read/Write files
Path("f.txt").write_text("content")
content = Path("f.txt").read_text()

# Find files (glob)
list(Path("/var/log").glob("*.log"))       # .log files in directory
list(Path("/etc").rglob("*.conf"))         # .conf files recursively

# Iterate directory
for item in Path("/var/log").iterdir():
    print(item.name, item.is_file())
```

---

### Regular Expressions (Day 4)

```python
import re

# Search (first match)
match = re.search(r"\d+", "port 8080")
if match:
    print(match.group())         # "8080"

# Find all
re.findall(r"\d+", "ports 80 443 8080")   # ["80", "443", "8080"]

# Groups
match = re.search(r"(\w+):(\d+)", "host:8080")
match.group(1)    # "host"
match.group(2)    # "8080"

# Replace
re.sub(r"\d+\.\d+\.\d+\.\d+", "X.X.X.X", text)

# Common Patterns
r"\d"              # Digit
r"\w"              # Word character (letter, digit, underscore)
r"\s"              # Whitespace
r"."               # Any character
r"\d+"             # One or more digits
r"\d*"             # Zero or more digits
r"\d?"             # Zero or one digit
r"\d{3}"           # Exactly 3 digits
r"\d{1,3}"         # 1 to 3 digits
r"[aeiou]"         # Any vowel
r"[^0-9]"          # Any non-digit
r"^start"          # Start of line
r"end$"            # End of line
r"\b"              # Word boundary
r"(a|b)"           # a or b

# Flags
re.IGNORECASE      # Case-insensitive
re.MULTILINE       # ^ and $ match line boundaries

# Common DevOps Patterns
r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"    # IPv4 address
r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"  # Email
r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"       # Timestamp
r"\b[1-5]\d{2}\b"                              # HTTP status code
```

---

### argparse Module (Day 5)

```python
import argparse

parser = argparse.ArgumentParser(description="My tool")

# Positional argument (required)
parser.add_argument("target", help="Target host")

# Optional arguments
parser.add_argument("--port", "-p", type=int, default=22, help="Port number")
parser.add_argument("--env", choices=["dev", "staging", "prod"], default="dev")
parser.add_argument("--verbose", "-v", action="store_true", help="Verbose mode")
parser.add_argument("--hosts", nargs="+", help="Multiple hosts")
parser.add_argument("--key", required=True, help="Required flag")

# Parse
args = parser.parse_args()          # From sys.argv
args = parser.parse_args(["web01", "--port", "443"])  # From list

# Access
args.target     # Positional value
args.port       # Optional value (int)
args.verbose    # Boolean flag
vars(args)      # Convert to dictionary
```

---

## Quick Reference: When to Use What

| I need to... | Use |
|---|---|
| Check if a file exists | `os.path.exists()` or `Path.exists()` |
| List files in a directory | `os.listdir()` or `Path.iterdir()` |
| Build a file path | `os.path.join()` or `Path / "name"` |
| Read an environment variable | `os.getenv()` |
| Run a shell command | `subprocess.run()` |
| Copy a file | `shutil.copy2()` |
| Delete a directory | `shutil.rmtree()` |
| Find files by pattern | `Path.rglob("*.ext")` |
| Parse text patterns | `re.findall()` or `re.search()` |
| Build a CLI | `argparse.ArgumentParser()` |

---

Now complete the quiz in `exercise.py` to test your knowledge!
