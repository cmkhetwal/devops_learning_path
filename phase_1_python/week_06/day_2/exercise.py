"""
Week 6, Day 2: Exercise - subprocess Module

THEME: Running System Commands from Python

You are building helper functions that wrap common system commands
for a DevOps automation toolkit. Each function should run a command,
capture its output, and return structured data.

Complete all 5 tasks below.
"""

import subprocess


# TASK 1: Write a function that runs the "whoami" command and returns
#         the current username as a string (stripped of whitespace).
#
# Requirements:
#   - Use subprocess.run() with capture_output=True and text=True
#   - Return the username as a clean string (no newlines)
#   - If the command fails, return the string "unknown"
#
# Hint: result.stdout.strip() removes whitespace/newlines

def get_current_user():
    # YOUR CODE HERE
    pass


# TASK 2: Write a function that takes a command as a LIST of strings
#         (e.g., ["ls", "-la", "/tmp"]) and returns a dictionary with:
#
#   "stdout"      -> the command's standard output (string)
#   "stderr"      -> the command's standard error (string)
#   "returncode"  -> the exit code (int)
#   "success"     -> True if returncode is 0, else False
#
# Requirements:
#   - Use capture_output=True and text=True
#   - Set timeout=10 to prevent hangs
#   - If the command times out, return:
#     {"stdout": "", "stderr": "Command timed out", "returncode": -1, "success": False}
#   - If the command is not found, return:
#     {"stdout": "", "stderr": "Command not found", "returncode": -1, "success": False}

def run_command(cmd_list):
    # YOUR CODE HERE
    pass


# TASK 3: Write a function that returns disk usage info for the root
#         filesystem "/" as a dictionary.
#
# Run: ["df", "-h", "/"]
#
# Parse the output to return:
#   "filesystem"  -> the device name (first column, e.g., "/dev/sda1")
#   "total"       -> total size (second column, e.g., "50G")
#   "used"        -> used space (third column, e.g., "23G")
#   "available"   -> available space (fourth column, e.g., "25G")
#   "percent"     -> usage percentage (fifth column, e.g., "48%")
#
# Hint: The output has a header line and a data line.
#       Split the output into lines, take the second line, split by whitespace.
#       df output columns: Filesystem  Size  Used  Avail  Use%  Mounted_on
#
# If the command fails, return an empty dictionary {}.

def get_disk_usage():
    # YOUR CODE HERE
    pass


# TASK 4: Write a function that takes a hostname or IP address and
#         pings it once, returning a dictionary with:
#
#   "host"        -> the host that was pinged (string)
#   "reachable"   -> True if ping succeeded (returncode 0), else False
#   "output"      -> the full stdout from the ping command
#
# Run: ["ping", "-c", "1", "-W", "2", host]
#   -c 1   = send 1 ping
#   -W 2   = timeout after 2 seconds
#
# Requirements:
#   - Set timeout=5 on subprocess.run() as a safety net
#   - Handle TimeoutExpired by returning reachable=False and output="Timed out"

def ping_host(host):
    # YOUR CODE HERE
    pass


# TASK 5: Write a function that takes a shell command as a SINGLE STRING
#         (using shell=True) and returns the output lines as a list.
#
# Example: run_shell_pipeline("echo -e 'one\ntwo\nthree'")
#   Returns: ["one", "two", "three"]
#
# Requirements:
#   - Use shell=True (since this is a pipeline/shell command)
#   - Use capture_output=True and text=True
#   - Split stdout into lines and remove empty trailing lines
#   - If the command fails (non-zero returncode), return an empty list []
#   - Set timeout=10
#
# Hint: "output".strip().split("\n") gives you clean lines.

def run_shell_pipeline(command_string):
    # YOUR CODE HERE
    pass


# === Do not modify below this line ===
if __name__ == "__main__":
    print("=== Task 1: Get Current User ===")
    user = get_current_user()
    print(f"  Current user: {user}")

    print("\n=== Task 2: Run Command ===")
    result = run_command(["echo", "Hello from subprocess"])
    if result:
        print(f"  stdout: {result.get('stdout', '').strip()}")
        print(f"  success: {result.get('success')}")

    print("\n=== Task 3: Disk Usage ===")
    disk = get_disk_usage()
    if disk:
        print(f"  Filesystem: {disk.get('filesystem')}")
        print(f"  Used: {disk.get('used')} of {disk.get('total')} ({disk.get('percent')})")

    print("\n=== Task 4: Ping Host ===")
    ping = ping_host("127.0.0.1")
    if ping:
        print(f"  Host: {ping.get('host')}")
        print(f"  Reachable: {ping.get('reachable')}")

    print("\n=== Task 5: Shell Pipeline ===")
    lines = run_shell_pipeline("echo -e 'line1\nline2\nline3'")
    if lines:
        for line in lines:
            print(f"  {line}")
