"""
Week 6, Day 3: Exercise - shutil & pathlib

THEME: File Management for Deployments

You are building file management utilities for a deployment pipeline.
These functions handle backups, file organization, and directory cleanup.

Complete all 5 tasks below.
"""

import shutil
from pathlib import Path


# TASK 1: Write a function that takes a source file path and a backup
#         directory path. It should:
#         1. Create the backup directory if it doesn't exist
#         2. Copy the source file into the backup directory (preserving metadata)
#         3. Return the Path to the copied file
#
# Requirements:
#   - Use pathlib.Path for path handling
#   - Use shutil.copy2() to preserve metadata
#   - Create parent directories with parents=True, exist_ok=True
#   - Return a Path object pointing to the backup copy
#
# Example: backup_file("/etc/hosts", "/tmp/backups")
#   -> Creates /tmp/backups/hosts and returns Path("/tmp/backups/hosts")

def backup_file(source, backup_dir):
    # YOUR CODE HERE
    pass


# TASK 2: Write a function that takes a directory path and returns a
#         dictionary mapping file extensions to lists of filenames.
#
# Example: group_files_by_extension("/some/dir")
#   Returns: {
#       ".py":   ["app.py", "utils.py"],
#       ".log":  ["error.log"],
#       ".conf": ["nginx.conf"],
#       "":      ["Makefile", "Dockerfile"]
#   }
#
# Requirements:
#   - Use pathlib.Path for iteration
#   - Only include files (not subdirectories)
#   - Files with no extension should use "" as the key
#   - Extensions should be lowercase
#   - Each value is a sorted list of filenames

def group_files_by_extension(directory):
    # YOUR CODE HERE
    pass


# TASK 3: Write a function that takes a directory path and organizes
#         files into subdirectories based on their extension.
#
# Example: If /tmp/messy/ contains: report.pdf, data.csv, script.py, notes.txt
#   After organize_files("/tmp/messy"):
#     /tmp/messy/pdf/report.pdf
#     /tmp/messy/csv/data.csv
#     /tmp/messy/py/script.py
#     /tmp/messy/txt/notes.txt
#
# Requirements:
#   - Use pathlib and shutil.move()
#   - Create subdirectories named after the extension (without the dot)
#   - Files with no extension go into a folder called "other"
#   - Skip files that are already in a subdirectory
#   - Return the number of files moved (int)
#
# Hint: iterate over files in the directory, get suffix, create subdir, move file

def organize_files(directory):
    # YOUR CODE HERE
    pass


# TASK 4: Write a function that uses glob to find files matching a
#         pattern in a directory (recursively) and returns information
#         about them.
#
# Parameters:
#   - directory: the root directory to search
#   - pattern: a glob pattern like "*.log" or "*.py"
#
# Returns a list of dictionaries, one per matching file:
#   {"name": "access.log", "path": "/var/log/access.log", "size": 1024}
#
# Requirements:
#   - Use Path.rglob() for recursive search
#   - Only include files (not directories)
#   - "path" should be the full absolute path as a string
#   - "size" should be in bytes (use .stat().st_size)
#   - Sort the list by file size (largest first)

def find_files(directory, pattern):
    # YOUR CODE HERE
    pass


# TASK 5: Write a function that creates a complete project directory
#         structure and populates it with template files.
#
# Given a base path and project name, create this structure:
#   <base>/<project_name>/
#       app/
#           __init__.py       (empty file)
#           main.py           (contains: # Main application entry point)
#       config/
#           settings.yml      (contains: environment: development)
#       tests/
#           __init__.py       (empty file)
#           test_main.py      (contains: # Tests for main module)
#       logs/                 (empty directory)
#       README.md             (contains: # <project_name>)
#
# Requirements:
#   - Use pathlib for all path operations
#   - Use Path.mkdir() to create directories
#   - Use Path.write_text() to create files
#   - Return the Path to the project root directory
#
# Example: create_project_scaffold("/tmp", "my_api")
#   Creates /tmp/my_api/ with the above structure

def create_project_scaffold(base_path, project_name):
    # YOUR CODE HERE
    pass


# === Do not modify below this line ===
if __name__ == "__main__":
    import tempfile
    import os

    print("=== Task 1: Backup File ===")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "config.yml"
        src.write_text("server: nginx\nport: 80\n")
        backup = backup_file(str(src), os.path.join(tmp, "backups"))
        if backup:
            print(f"  Backed up to: {backup}")
            print(f"  Exists: {Path(backup).exists()}")

    print("\n=== Task 2: Group Files by Extension ===")
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["app.py", "utils.py", "config.yml", "data.csv", "Makefile"]:
            (Path(tmp) / name).touch()
        groups = group_files_by_extension(tmp)
        if groups:
            for ext, files in sorted(groups.items()):
                label = ext if ext else "(none)"
                print(f"  {label}: {files}")

    print("\n=== Task 3: Organize Files ===")
    with tempfile.TemporaryDirectory() as tmp:
        for name in ["report.pdf", "data.csv", "script.py", "notes.txt"]:
            (Path(tmp) / name).touch()
        count = organize_files(tmp)
        print(f"  Moved {count} files")
        for d in sorted(Path(tmp).iterdir()):
            if d.is_dir():
                contents = list(d.iterdir())
                print(f"  {d.name}/: {[f.name for f in contents]}")

    print("\n=== Task 4: Find Files ===")
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "a.log").write_text("x" * 100)
        (Path(tmp) / "b.log").write_text("x" * 500)
        sub = Path(tmp) / "sub"
        sub.mkdir()
        (sub / "c.log").write_text("x" * 200)
        results = find_files(tmp, "*.log")
        if results:
            for r in results:
                print(f"  {r['name']}: {r['size']} bytes")

    print("\n=== Task 5: Project Scaffold ===")
    with tempfile.TemporaryDirectory() as tmp:
        project = create_project_scaffold(tmp, "devops_tool")
        if project:
            for p in sorted(Path(project).rglob("*")):
                rel = p.relative_to(project)
                kind = "DIR" if p.is_dir() else "FILE"
                print(f"  [{kind}] {rel}")
