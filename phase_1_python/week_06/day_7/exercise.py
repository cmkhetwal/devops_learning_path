"""
Week 6, Day 7: Quiz - OS & System Automation

THEME: Test Your Week 6 Knowledge

Complete each function. Each one tests a specific concept from this week.
There are 10 questions total.

Refer to lesson.md (the cheat sheet) if you need a refresher.
"""

import os
import re
import subprocess
import shutil
from pathlib import Path


# Q1: Write a function that takes a directory path and returns True
#     if ALL of these conditions are met:
#       - The path exists
#       - The path is a directory (not a file)
#       - The directory is not empty (has at least one item)
#     Return False otherwise.
#
# Use: os.path.exists(), os.path.isdir(), os.listdir()

def is_valid_nonempty_dir(path):
    # YOUR CODE HERE
    pass


# Q2: Write a function that takes a command as a list of strings,
#     runs it, and returns a tuple: (success, output)
#       - success: True if returncode == 0, False otherwise
#       - output: stdout if success, stderr if failure (stripped)
#     If the command is not found, return (False, "not found").
#     Use timeout=5.

def safe_run(cmd_list):
    # YOUR CODE HERE
    pass


# Q3: Write a function that takes a directory path and returns the
#     total size of all files in it (NON-recursively) in bytes.
#     Only count files, not subdirectories.
#
# Use: pathlib.Path, .iterdir(), .is_file(), .stat().st_size

def dir_total_size(directory):
    # YOUR CODE HERE
    pass


# Q4: Write a function that takes a text string and returns a list
#     of all words that start with a capital letter.
#
# Example: "The Quick brown Fox jumps" -> ["The", "Quick", "Fox"]
#
# Use: re.findall() with pattern r"\b[A-Z][a-z]*\b"

def find_capitalized_words(text):
    # YOUR CODE HERE
    pass


# Q5: Write a function that takes two directory paths (source, dest)
#     and copies ONLY .conf files from source to dest.
#     Create dest if it does not exist.
#     Return the number of files copied.
#
# Use: pathlib.Path.glob(), shutil.copy2(), Path.mkdir()

def copy_conf_files(source, dest):
    # YOUR CODE HERE
    pass


# Q6: Write a function that takes a log line string and determines
#     its severity level. Return one of: "ERROR", "WARNING", "INFO",
#     or "UNKNOWN".
#
# Rules:
#   - If the line contains "ERROR" (case-insensitive) -> "ERROR"
#   - If the line contains "WARNING" or "WARN" (case-insensitive) -> "WARNING"
#   - If the line contains "INFO" (case-insensitive) -> "INFO"
#   - Otherwise -> "UNKNOWN"
#
# Check in order: ERROR first, then WARNING/WARN, then INFO.
# Use: re.search() with re.IGNORECASE

def detect_severity(log_line):
    # YOUR CODE HERE
    pass


# Q7: Write a function that takes a list of environment variable
#     names and returns a dictionary of which ones are set and which
#     are not.
#
# Return: {"set": ["VAR1", "VAR3"], "missing": ["VAR2", "VAR4"]}
#
# Both lists should be sorted alphabetically.
# Use: os.getenv()

def check_env_vars(var_names):
    # YOUR CODE HERE
    pass


# Q8: Write a function that takes a text string containing key=value
#     pairs (one per line) and returns them as a dictionary.
#
# Example input:
#   "HOST=localhost\nPORT=8080\nDEBUG=true\n"
#
# Returns: {"HOST": "localhost", "PORT": "8080", "DEBUG": "true"}
#
# Rules:
#   - Skip empty lines
#   - Skip lines that don't contain "="
#   - Strip whitespace from keys and values
#   - Use re.match() or simple string splitting
#
# Use: re or str.split("=", 1)

def parse_env_file(text):
    # YOUR CODE HERE
    pass


# Q9: Write a function that takes a path string and returns a
#     "breadcrumb" string showing the path hierarchy.
#
# Example: "/var/log/nginx/access.log"
#   Returns: "var > log > nginx > access.log"
#
# Rules:
#   - Remove leading "/"
#   - Join parts with " > "
#   - Works with both file and directory paths
#
# Use: pathlib.Path.parts or os.path.split techniques

def path_breadcrumb(filepath):
    # YOUR CODE HERE
    pass


# Q10: Write a function that takes a multi-line string of output
#      from "df -h" and returns a list of filesystems that are
#      over a given usage percentage threshold.
#
# Example df -h output:
#   "Filesystem  Size  Used  Avail  Use%  Mounted on\n"
#   "/dev/sda1   50G   45G   5G     90%   /\n"
#   "tmpfs       4G    100M  3.9G   3%    /tmp\n"
#
# Call: get_full_filesystems(df_output, 80)
#   Returns: [{"filesystem": "/dev/sda1", "percent": 90, "mount": "/"}]
#
# Return list of dicts with: "filesystem", "percent" (int), "mount" (string)
# Only include entries where percent >= threshold.
#
# Use: str.split(), int(), string parsing (skip the header line)

def get_full_filesystems(df_output, threshold=80):
    # YOUR CODE HERE
    pass


# === Do not modify below this line ===
if __name__ == "__main__":
    import tempfile

    print("=== Q1: Valid Non-Empty Dir ===")
    print(f"  /tmp: {is_valid_nonempty_dir('/tmp')}")
    print(f"  /nonexistent: {is_valid_nonempty_dir('/nonexistent')}")

    print("\n=== Q2: Safe Run ===")
    success, output = safe_run(["echo", "hello"])
    print(f"  echo hello: success={success}, output='{output}'")
    success2, output2 = safe_run(["fake_command_xyz"])
    print(f"  fake_cmd: success={success2}, output='{output2}'")

    print("\n=== Q3: Dir Total Size ===")
    with tempfile.TemporaryDirectory() as tmp:
        Path(tmp, "a.txt").write_text("hello")
        Path(tmp, "b.txt").write_text("world!!")
        print(f"  Size: {dir_total_size(tmp)} bytes")

    print("\n=== Q4: Capitalized Words ===")
    print(f"  {find_capitalized_words('The Quick brown Fox jumps Over')}")

    print("\n=== Q5: Copy Conf Files ===")
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "src"
        dst = Path(tmp) / "dst"
        src.mkdir()
        (src / "nginx.conf").write_text("server {}")
        (src / "app.conf").write_text("key=val")
        (src / "readme.txt").write_text("ignore me")
        count = copy_conf_files(str(src), str(dst))
        print(f"  Copied: {count} conf files")

    print("\n=== Q6: Detect Severity ===")
    print(f"  'ERROR disk full': {detect_severity('ERROR disk full')}")
    print(f"  'warn: high cpu': {detect_severity('warn: high cpu')}")
    print(f"  'info started': {detect_severity('info started')}")
    print(f"  'something else': {detect_severity('something else')}")

    print("\n=== Q7: Check Env Vars ===")
    os.environ["TEST_SET_VAR"] = "yes"
    result = check_env_vars(["TEST_SET_VAR", "NONEXISTENT_XYZ_123", "HOME"])
    print(f"  {result}")

    print("\n=== Q8: Parse Env File ===")
    text = "HOST=localhost\nPORT=8080\nDEBUG=true\n\nINVALID LINE\n"
    print(f"  {parse_env_file(text)}")

    print("\n=== Q9: Path Breadcrumb ===")
    print(f"  {path_breadcrumb('/var/log/nginx/access.log')}")

    print("\n=== Q10: Full Filesystems ===")
    df = """Filesystem  Size  Used  Avail  Use%  Mounted on
/dev/sda1   50G   45G   5G     90%   /
tmpfs       4G    100M  3.9G   3%    /tmp
/dev/sdb1   100G  82G   18G    82%   /data"""
    print(f"  {get_full_filesystems(df, 80)}")
