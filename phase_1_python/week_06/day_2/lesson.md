# Week 6, Day 2: The subprocess Module

## What You'll Learn

- Run external shell commands from Python
- Capture command output (stdout and stderr)
- Check if commands succeeded or failed
- Understand `shell=True` vs `shell=False` (and the security implications)
- Parse command output for automation

## Why This Matters for DevOps

DevOps automation often means orchestrating existing command-line tools. You might need to
check disk space with `df`, restart a service with `systemctl`, pull code with `git`, or
verify connectivity with `ping`. The `subprocess` module lets you run any command you would
type in a terminal and process the results in Python.

---

## 1. Basic Command Execution: subprocess.run()

```python
import subprocess

# Run a simple command
result = subprocess.run(["echo", "Hello from Python"])
# Output: Hello from Python
```

`subprocess.run()` takes a **list** where the first item is the command and the rest
are arguments. This is the safe, recommended way.

---

## 2. Capturing Output

By default, command output goes directly to the terminal. To capture it in Python:

```python
import subprocess

result = subprocess.run(
    ["whoami"],
    capture_output=True,
    text=True
)

print(f"Username: {result.stdout.strip()}")
print(f"Errors: {result.stderr}")
print(f"Return code: {result.returncode}")
```

Key parameters:
- **capture_output=True** -- capture stdout and stderr instead of printing them
- **text=True** -- return strings instead of bytes (also called `universal_newlines=True`)

Key attributes of the result:
- **result.stdout** -- the standard output
- **result.stderr** -- the standard error
- **result.returncode** -- 0 means success, non-zero means failure

---

## 3. Checking Return Codes

```python
import subprocess

result = subprocess.run(
    ["ls", "/nonexistent"],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Command succeeded")
    print(result.stdout)
else:
    print(f"Command failed with code {result.returncode}")
    print(f"Error: {result.stderr}")
```

You can also use `check=True` to automatically raise an exception on failure:

```python
import subprocess

try:
    result = subprocess.run(
        ["ls", "/nonexistent"],
        capture_output=True,
        text=True,
        check=True          # Raises CalledProcessError if returncode != 0
    )
except subprocess.CalledProcessError as e:
    print(f"Command failed: {e}")
    print(f"stderr: {e.stderr}")
```

---

## 4. shell=True vs shell=False

```python
import subprocess

# shell=False (DEFAULT) -- safer, pass command as a list
result = subprocess.run(
    ["df", "-h", "/"],
    capture_output=True, text=True
)

# shell=True -- pass command as a single string
result = subprocess.run(
    "df -h /",
    shell=True,
    capture_output=True, text=True
)
```

**When to use each:**

| Mode | Syntax | Use When |
|---|---|---|
| `shell=False` (default) | `["cmd", "arg1", "arg2"]` | Always prefer this. Safer. |
| `shell=True` | `"cmd arg1 arg2"` | Need pipes, redirects, or shell features |

**Security Warning:** Never use `shell=True` with user-provided input!

```python
# DANGEROUS -- user could inject commands
user_input = "file.txt; rm -rf /"
subprocess.run(f"cat {user_input}", shell=True)  # DO NOT DO THIS

# SAFE -- arguments are escaped automatically
subprocess.run(["cat", user_input])  # This is fine
```

---

## 5. Using Pipes with shell=True

Sometimes you need shell features like pipes:

```python
import subprocess

# Count Python processes
result = subprocess.run(
    "ps aux | grep python | wc -l",
    shell=True,
    capture_output=True, text=True
)
print(f"Python processes: {result.stdout.strip()}")
```

---

## 6. Setting Timeouts

Prevent commands from running forever:

```python
import subprocess

try:
    result = subprocess.run(
        ["ping", "-c", "4", "8.8.8.8"],
        capture_output=True, text=True,
        timeout=10  # seconds
    )
except subprocess.TimeoutExpired:
    print("Command timed out!")
```

---

## 7. Passing Environment Variables

```python
import subprocess
import os

# Modify environment for the subprocess
my_env = os.environ.copy()
my_env["APP_ENV"] = "production"
my_env["LOG_LEVEL"] = "debug"

result = subprocess.run(
    ["printenv", "APP_ENV"],
    capture_output=True, text=True,
    env=my_env
)
print(result.stdout.strip())  # production
```

---

## 8. Real-World Example: System Health Report

```python
import subprocess

def get_command_output(command):
    """Run a command and return its output, or an error message."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"ERROR: {result.stderr.strip()}"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out"
    except FileNotFoundError:
        return "ERROR: Command not found"

# Gather system info
print("=== System Health Report ===")
print(f"Hostname: {get_command_output(['hostname'])}")
print(f"User: {get_command_output(['whoami'])}")
print(f"Uptime: {get_command_output(['uptime', '-p'])}")
print(f"\n--- Disk Usage ---")
print(get_command_output(["df", "-h", "/"]))
print(f"\n--- Memory ---")
print(get_command_output(["free", "-h"]))
```

---

## 9. Parsing Command Output

The real power comes from parsing output:

```python
import subprocess

# Get disk usage and parse it
result = subprocess.run(
    ["df", "-h", "/"],
    capture_output=True, text=True
)

lines = result.stdout.strip().split("\n")
# lines[0] is the header, lines[1] is the data
parts = lines[1].split()
filesystem = parts[0]
total = parts[1]
used = parts[2]
available = parts[3]
percent = parts[4]

print(f"Disk: {percent} used ({used} of {total})")
```

---

## Key Takeaways

1. **subprocess.run()** is the modern way to run commands
2. Always use **capture_output=True, text=True** to get string output
3. Check **result.returncode** (0 = success)
4. Prefer **shell=False** (list syntax) for security
5. Use **shell=True** only when you need pipes or shell features
6. Set **timeout** to prevent hangs
7. Use **check=True** when failure should raise an exception

---

## DevOps Connection

| Task | Command |
|---|---|
| Check disk space | `subprocess.run(["df", "-h"])` |
| Check running services | `subprocess.run(["systemctl", "is-active", "nginx"])` |
| Get Git status | `subprocess.run(["git", "status"])` |
| Test connectivity | `subprocess.run(["ping", "-c", "1", "host"])` |
| Check open ports | `subprocess.run(["ss", "-tlnp"])` |

Tomorrow you will learn `shutil` and `pathlib` -- higher-level tools for file
operations like copying, moving, and finding files.
