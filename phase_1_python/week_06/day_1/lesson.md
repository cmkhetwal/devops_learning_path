# Week 6, Day 1: The os Module

## What You'll Learn

- Navigate the filesystem with Python
- List directory contents and check paths
- Create directories programmatically
- Build cross-platform paths with `os.path.join()`
- Read and set environment variables

## Why This Matters for DevOps

Every automation script you write will interact with the operating system. Deployment scripts
check if directories exist before creating them. Configuration tools read environment variables.
Monitoring scripts scan directories for log files. The `os` module is your Python gateway to
the underlying system.

---

## 1. Getting the Current Working Directory

```python
import os

cwd = os.getcwd()
print(f"Current directory: {cwd}")
# Output: Current directory: /home/devops/projects
```

This is the Python equivalent of running `pwd` in a terminal. You will use this constantly
to understand where your script is executing from.

---

## 2. Listing Directory Contents

```python
import os

# List everything in the current directory
contents = os.listdir(".")
print(contents)
# Output: ['app.py', 'config', 'logs', 'README.md']

# List a specific directory
log_files = os.listdir("/var/log")
for f in log_files:
    print(f)
```

`os.listdir()` returns a plain list of filenames (no full paths). It does NOT include
`.` or `..` entries. It does NOT recurse into subdirectories.

---

## 3. Creating Directories

```python
import os

# Create a single directory
os.mkdir("backups")

# Create nested directories (like mkdir -p)
os.makedirs("deploy/staging/configs", exist_ok=True)
```

The `exist_ok=True` parameter prevents an error if the directory already exists. This is
critical in automation -- your script might run multiple times, and you don't want it to
crash on the second run.

---

## 4. Building Paths with os.path.join()

```python
import os

# WRONG way (breaks on Windows)
path = "/var/log" + "/" + "app.log"

# RIGHT way (cross-platform)
path = os.path.join("/var", "log", "app.log")
print(path)
# Output on Linux: /var/log/app.log
# Output on Windows: /var\log\app.log
```

Always use `os.path.join()` instead of string concatenation. Your scripts may need to run
on different operating systems, and path separators differ between them.

---

## 5. Checking If Paths Exist

```python
import os

# Check if a file exists
if os.path.exists("/etc/nginx/nginx.conf"):
    print("Nginx config found")

# Check specifically for a file (not directory)
if os.path.isfile("/etc/hosts"):
    print("Hosts file found")

# Check specifically for a directory
if os.path.isdir("/var/log"):
    print("Log directory exists")
```

In DevOps scripts, you almost always check before you act:
- Check if a config file exists before reading it
- Check if a directory exists before creating it
- Check if a lock file exists before proceeding

---

## 6. Other Useful os.path Functions

```python
import os

path = "/var/log/nginx/access.log"

# Get just the filename
print(os.path.basename(path))   # access.log

# Get just the directory
print(os.path.dirname(path))    # /var/log/nginx

# Split into directory and filename
print(os.path.split(path))      # ('/var/log/nginx', 'access.log')

# Get file extension
print(os.path.splitext(path))   # ('/var/log/nginx/access', '.log')

# Get absolute path from a relative one
print(os.path.abspath("logs"))  # /home/user/projects/logs

# Get file size in bytes
print(os.path.getsize("/etc/hosts"))  # 221
```

---

## 7. Environment Variables

Environment variables are the standard way to pass configuration to applications in DevOps.
Docker containers, CI/CD pipelines, and cloud platforms all use them heavily.

```python
import os

# Read an environment variable (returns None if not set)
db_host = os.getenv("DB_HOST")
print(db_host)  # None (if not set)

# Read with a default value
db_host = os.getenv("DB_HOST", "localhost")
print(db_host)  # localhost

# Read using os.environ (raises KeyError if not set)
try:
    secret = os.environ["API_KEY"]
except KeyError:
    print("API_KEY not set!")

# See ALL environment variables
for key, value in os.environ.items():
    print(f"{key}={value}")

# Set an environment variable (for this process only)
os.environ["APP_ENV"] = "staging"
print(os.getenv("APP_ENV"))  # staging
```

**os.getenv() vs os.environ[]:**
| Method | Missing Key | Use When |
|---|---|---|
| `os.getenv("KEY")` | Returns `None` | Variable is optional |
| `os.getenv("KEY", "default")` | Returns `"default"` | You have a fallback |
| `os.environ["KEY"]` | Raises `KeyError` | Variable is required |

---

## 8. Real-World Example: Pre-Deployment Check

```python
import os

def pre_deploy_check(app_dir):
    """Verify everything is in place before deploying."""
    checks_passed = True

    # Check the app directory exists
    if not os.path.isdir(app_dir):
        print(f"FAIL: App directory {app_dir} not found")
        checks_passed = False

    # Check required config file
    config_path = os.path.join(app_dir, "config.yml")
    if not os.path.isfile(config_path):
        print(f"FAIL: Config file missing at {config_path}")
        checks_passed = False

    # Check required environment variables
    required_vars = ["DB_HOST", "DB_USER", "APP_SECRET"]
    for var in required_vars:
        if os.getenv(var) is None:
            print(f"FAIL: Environment variable {var} not set")
            checks_passed = False

    # Check log directory is writable
    log_dir = os.path.join(app_dir, "logs")
    if not os.path.isdir(log_dir):
        os.makedirs(log_dir, exist_ok=True)
        print(f"INFO: Created log directory {log_dir}")

    return checks_passed
```

---

## Key Takeaways

1. **os.getcwd()** -- know where you are
2. **os.listdir()** -- see what is in a directory
3. **os.mkdir() / os.makedirs()** -- create directories (use `exist_ok=True`)
4. **os.path.join()** -- always build paths this way
5. **os.path.exists() / isfile() / isdir()** -- check before you act
6. **os.getenv()** -- read environment variables safely
7. **os.environ** -- access the full environment dictionary

---

## DevOps Connection

| Concept | Real-World Use |
|---|---|
| `os.listdir()` | Scan for config files, find log files |
| `os.makedirs()` | Create deployment directories |
| `os.path.exists()` | Pre-flight checks before deployments |
| `os.getenv()` | Read DB_HOST, API_KEY, APP_ENV from the environment |
| `os.environ` | Inject config into child processes |

Tomorrow you will learn the `subprocess` module -- running actual shell commands from Python.
Combined with `os`, you will be able to fully automate system tasks.
