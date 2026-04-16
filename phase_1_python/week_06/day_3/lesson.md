# Week 6, Day 3: shutil & pathlib

## What You'll Learn

- Copy, move, and delete files and directories with `shutil`
- Use `pathlib.Path` for modern, object-oriented path handling
- Find files using glob patterns
- Build a file backup script

## Why This Matters for DevOps

File management is at the heart of DevOps. You deploy by copying files. You rotate logs
by moving them. You clean up old builds by deleting directories. You find configuration
files across complex directory trees. `shutil` and `pathlib` are the high-level tools
that make these operations clean and reliable.

---

## 1. shutil.copy() -- Copying Files

```python
import shutil

# Copy a file (preserves content, not metadata)
shutil.copy("config.yml", "config.yml.bak")

# Copy a file preserving metadata (timestamps, permissions)
shutil.copy2("config.yml", "config.yml.bak")

# Copy into a directory (keeps the original filename)
shutil.copy2("config.yml", "/tmp/backups/")
# Result: /tmp/backups/config.yml
```

| Function | Preserves Permissions | Preserves Timestamps |
|---|---|---|
| `shutil.copy()` | Yes | No |
| `shutil.copy2()` | Yes | Yes |

---

## 2. shutil.copytree() -- Copying Directories

```python
import shutil

# Copy an entire directory tree
shutil.copytree("project/", "project_backup/")

# Copy but ignore certain patterns
shutil.copytree(
    "project/",
    "project_clean/",
    ignore=shutil.ignore_patterns("*.pyc", "__pycache__", ".git")
)
```

Note: The destination directory must NOT already exist (unless you use `dirs_exist_ok=True`
in Python 3.8+).

```python
# Overwrite existing destination (Python 3.8+)
shutil.copytree("project/", "project_backup/", dirs_exist_ok=True)
```

---

## 3. shutil.move() -- Moving/Renaming Files

```python
import shutil

# Move a file
shutil.move("app.log", "logs/app.log")

# Rename a file (same directory, different name)
shutil.move("config.yml", "config.yml.old")

# Move a directory
shutil.move("old_deploy/", "archive/old_deploy/")
```

`shutil.move()` works like the `mv` command -- it handles both moves and renames.

---

## 4. shutil.rmtree() -- Deleting Directories

```python
import shutil
import os

# Delete an entire directory tree (like rm -rf)
if os.path.isdir("build/"):
    shutil.rmtree("build/")

# Ignore errors during deletion
shutil.rmtree("temp/", ignore_errors=True)
```

**WARNING:** `shutil.rmtree()` is the Python equivalent of `rm -rf`. There is no undo.
Always double-check your path before calling it.

---

## 5. shutil.disk_usage() -- Check Disk Space

```python
import shutil

usage = shutil.disk_usage("/")
print(f"Total: {usage.total // (1024**3)} GB")
print(f"Used:  {usage.used // (1024**3)} GB")
print(f"Free:  {usage.free // (1024**3)} GB")
```

---

## 6. pathlib.Path -- Modern Path Handling

`pathlib` was added in Python 3.4 and is the modern way to work with filesystem paths.
Instead of string manipulation, you work with `Path` objects.

```python
from pathlib import Path

# Create a Path object
p = Path("/var/log/nginx/access.log")

# Get parts of the path
print(p.name)       # access.log
print(p.stem)       # access
print(p.suffix)     # .log
print(p.parent)     # /var/log/nginx
print(p.parts)      # ('/', 'var', 'log', 'nginx', 'access.log')
```

---

## 7. Building Paths with the / Operator

```python
from pathlib import Path

# Build paths using / (much cleaner than os.path.join)
base = Path("/var/log")
log_file = base / "nginx" / "access.log"
print(log_file)  # /var/log/nginx/access.log

# Works with strings too
config = Path.home() / ".config" / "myapp" / "settings.yml"
print(config)  # /home/user/.config/myapp/settings.yml
```

---

## 8. Checking Paths with pathlib

```python
from pathlib import Path

p = Path("/etc/hosts")
print(p.exists())      # True
print(p.is_file())     # True
print(p.is_dir())      # False

d = Path("/var/log")
print(d.exists())      # True
print(d.is_dir())      # True
```

---

## 9. Creating Directories with pathlib

```python
from pathlib import Path

# Create a directory (like os.makedirs with exist_ok)
Path("deploy/staging/configs").mkdir(parents=True, exist_ok=True)
```

`parents=True` is like `mkdir -p` -- it creates all intermediate directories.

---

## 10. Reading and Writing Files with pathlib

```python
from pathlib import Path

# Write text to a file
Path("status.txt").write_text("deployment: success\n")

# Read text from a file
content = Path("status.txt").read_text()
print(content)

# Read lines
lines = Path("/etc/hosts").read_text().splitlines()
for line in lines:
    print(line)
```

---

## 11. Glob Patterns -- Finding Files

Glob patterns let you search for files using wildcards:

```python
from pathlib import Path

# Find all .log files in a directory
for log in Path("/var/log").glob("*.log"):
    print(log)

# Find all .conf files recursively (any depth)
for conf in Path("/etc").rglob("*.conf"):
    print(conf)

# Find all Python files in a project
py_files = list(Path("project/").rglob("*.py"))
print(f"Found {len(py_files)} Python files")
```

Common glob patterns:
| Pattern | Matches |
|---|---|
| `*.log` | All .log files in that directory |
| `**/*.log` | All .log files recursively |
| `*.py` | All Python files |
| `config*` | Files starting with "config" |
| `*.{yml,yaml}` | .yml and .yaml files (use two globs for pathlib) |

---

## 12. Real-World Example: File Backup Script

```python
import shutil
from pathlib import Path
from datetime import datetime

def backup_directory(source, backup_root):
    """Create a timestamped backup of a directory."""
    source = Path(source)
    backup_root = Path(backup_root)

    if not source.is_dir():
        print(f"Error: {source} is not a directory")
        return None

    # Create backup directory name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source.name}_backup_{timestamp}"
    backup_path = backup_root / backup_name

    # Create backup root if needed
    backup_root.mkdir(parents=True, exist_ok=True)

    # Copy the directory
    shutil.copytree(source, backup_path)
    print(f"Backed up {source} -> {backup_path}")
    return backup_path

# Usage
backup_directory("/etc/nginx", "/tmp/backups")
```

---

## 13. Real-World Example: File Organizer

```python
from pathlib import Path
import shutil

def organize_by_extension(source_dir):
    """Move files into subdirectories based on their extension."""
    source = Path(source_dir)

    for filepath in source.iterdir():
        if filepath.is_file():
            ext = filepath.suffix.lower()
            if ext == "":
                ext_dir = source / "no_extension"
            else:
                ext_dir = source / ext.lstrip(".")
            ext_dir.mkdir(exist_ok=True)
            shutil.move(str(filepath), str(ext_dir / filepath.name))
            print(f"Moved {filepath.name} -> {ext_dir.name}/")
```

---

## Key Takeaways

1. **shutil.copy2()** -- copy files preserving metadata
2. **shutil.copytree()** -- copy entire directory trees
3. **shutil.move()** -- move or rename files and directories
4. **shutil.rmtree()** -- delete directory trees (be careful!)
5. **Path()** -- modern, object-oriented paths
6. **Path / "subdir"** -- build paths with the `/` operator
7. **Path.glob() / Path.rglob()** -- find files with patterns

---

## DevOps Connection

| Task | Tool |
|---|---|
| Backup config files | `shutil.copy2()` |
| Deploy a release | `shutil.copytree()` |
| Rotate log files | `shutil.move()` |
| Clean up old builds | `shutil.rmtree()` |
| Find all YAML configs | `Path("/etc").rglob("*.yml")` |
| Create deployment dirs | `Path("deploy").mkdir(parents=True)` |

Tomorrow you will learn regular expressions -- the power tool for parsing text like
log files, IP addresses, and error codes.
