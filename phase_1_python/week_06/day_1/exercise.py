"""
Week 6, Day 1: Exercise - os Module

THEME: System Exploration and Environment Setup

You are writing utility functions that a DevOps engineer would use
to inspect and prepare a system before deploying an application.

Complete all 5 tasks below.
"""

import os


# TASK 1: Write a function that returns a dictionary with information
#         about the current working directory.
#
# The dictionary should have these keys:
#   "cwd"   -> the current working directory (string)
#   "files" -> list of ONLY files in cwd (not directories)
#   "dirs"  -> list of ONLY directories in cwd (not files)
#   "total" -> total number of items (files + dirs)
#
# Hint: Use os.getcwd(), os.listdir(), os.path.isfile(), os.path.isdir()
# Hint: os.listdir gives names only -- join with cwd to get full paths for checking

def explore_cwd():
    # YOUR CODE HERE
    pass


# TASK 2: Write a function that takes a base directory path and a list
#         of subdirectory names, and creates all of them.
#
# Example: setup_directories("/tmp/myapp", ["logs", "config", "data", "backups"])
#   Should create: /tmp/myapp/logs, /tmp/myapp/config, /tmp/myapp/data, /tmp/myapp/backups
#
# Requirements:
#   - Use os.path.join() to build paths
#   - Use os.makedirs() with exist_ok=True
#   - Return a list of the full paths that were created
#
# Hint: The base directory itself may not exist yet -- makedirs handles that.

def setup_directories(base_dir, subdirs):
    # YOUR CODE HERE
    pass


# TASK 3: Write a function that takes a directory path and returns a
#         dictionary mapping file extensions to the count of files
#         with that extension.
#
# Example: count_extensions("/var/log")
#   Returns: {".log": 5, ".gz": 3, ".conf": 1, "": 2}
#
# Requirements:
#   - Only count files, not directories
#   - Files with no extension should use "" as the key
#   - Use os.path.splitext() to get extensions
#   - Extensions should be lowercase (e.g., ".LOG" becomes ".log")

def count_extensions(directory):
    # YOUR CODE HERE
    pass


# TASK 4: Write a function that reads specific environment variables
#         and returns a "config" dictionary for a web application.
#
# Read these environment variables (with defaults):
#   "APP_HOST"  -> default "0.0.0.0"
#   "APP_PORT"  -> default "8080"
#   "APP_ENV"   -> default "development"
#   "DB_HOST"   -> default "localhost"
#   "DB_PORT"   -> default "5432"
#   "DEBUG"     -> default "false"
#
# Return a dictionary with these exact keys and the values from the
# environment (or defaults if not set).
#
# Hint: Use os.getenv() with two arguments.

def get_app_config():
    # YOUR CODE HERE
    pass


# TASK 5: Write a function that takes a file path and returns a
#         dictionary of information about that path.
#
# The dictionary should have:
#   "exists"    -> True/False
#   "is_file"   -> True/False
#   "is_dir"    -> True/False
#   "basename"  -> filename or directory name (e.g., "app.log")
#   "dirname"   -> parent directory (e.g., "/var/log")
#   "extension" -> file extension (e.g., ".log") or "" if none
#   "size"      -> file size in bytes (0 if path doesn't exist)
#
# Hint: Use os.path.exists(), isfile(), isdir(), basename(),
#       dirname(), splitext(), getsize()

def path_info(filepath):
    # YOUR CODE HERE
    pass


# === Do not modify below this line ===
if __name__ == "__main__":
    print("=== Task 1: Explore CWD ===")
    result = explore_cwd()
    if result:
        print(f"  CWD: {result.get('cwd')}")
        print(f"  Files: {len(result.get('files', []))}")
        print(f"  Dirs: {len(result.get('dirs', []))}")

    print("\n=== Task 2: Setup Directories ===")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        paths = setup_directories(
            os.path.join(tmp, "myapp"),
            ["logs", "config", "data"]
        )
        if paths:
            for p in paths:
                print(f"  Created: {p} (exists: {os.path.isdir(p)})")

    print("\n=== Task 3: Count Extensions ===")
    ext_counts = count_extensions(os.getcwd())
    if ext_counts:
        for ext, count in sorted(ext_counts.items()):
            label = ext if ext else "(no extension)"
            print(f"  {label}: {count}")

    print("\n=== Task 4: App Config ===")
    config = get_app_config()
    if config:
        for k, v in config.items():
            print(f"  {k} = {v}")

    print("\n=== Task 5: Path Info ===")
    info = path_info(__file__)
    if info:
        for k, v in info.items():
            print(f"  {k}: {v}")
