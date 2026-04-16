"""
Week 9, Day 1: Docker SDK - Getting Connected

DOCKER SDK FUNDAMENTALS
=======================

In this exercise you will write functions that demonstrate the patterns used
when connecting to Docker from Python.  Since Docker may not be installed on
your machine, the exercises use a MockDockerClient so that every task can be
completed and verified without a running Docker daemon.

TASKS
-----
1. Create a MockDockerClient class
2. Write a safe connection function
3. Extract Docker environment info
4. Build a Docker version report
5. Create a Docker health-check utility
"""


# ============================================================
# TASK 1: Create a MockDockerClient class
# ============================================================
# Create a class called `MockDockerClient` that simulates a Docker client.
#
# It must have these methods:
#   - ping()    -> returns True
#   - info()    -> returns a dict with these exact keys and values:
#       "ServerVersion": "24.0.7"
#       "Containers": 5
#       "ContainersRunning": 2
#       "ContainersStopped": 3
#       "Images": 12
#       "OperatingSystem": "Linux"
#       "Architecture": "x86_64"
#       "NCPU": 4
#       "MemTotal": 8589934592        (8 GB in bytes)
#   - version() -> returns a dict with these exact keys and values:
#       "Version": "24.0.7"
#       "ApiVersion": "1.43"
#       "Os": "linux"
#       "Arch": "amd64"

# YOUR CODE HERE


# ============================================================
# TASK 2: Write a safe connection function
# ============================================================
# Write a function called `get_docker_client` that:
#   - Takes no arguments
#   - Tries to import docker and call docker.from_env()
#   - If that succeeds, returns the real client
#   - If ANY exception occurs, returns a MockDockerClient() instead
#   - Prints "Connected to Docker daemon" when real Docker works
#   - Prints "Docker not available - using mock client" when falling back
#
# Hint: Wrap the import + connection in a try/except block.

# YOUR CODE HERE


# ============================================================
# TASK 3: Extract Docker environment info
# ============================================================
# Write a function called `get_docker_info` that:
#   - Takes one argument: client (a docker client or MockDockerClient)
#   - Calls client.info() and returns a NEW dictionary with exactly:
#       "os"            -> value of "OperatingSystem"
#       "arch"          -> value of "Architecture"
#       "cpus"          -> value of "NCPU"
#       "memory_gb"     -> value of "MemTotal" converted to GB (divide by 1024**3), rounded to 1 decimal
#       "containers"    -> value of "Containers"
#       "running"       -> value of "ContainersRunning"
#       "stopped"       -> value of "ContainersStopped"
#       "images"        -> value of "Images"

# YOUR CODE HERE


# ============================================================
# TASK 4: Build a Docker version report
# ============================================================
# Write a function called `docker_version_report` that:
#   - Takes one argument: client
#   - Calls client.version() and client.info()
#   - Returns a multi-line STRING formatted exactly as:
#
#     Docker Version Report
#     ====================
#     Docker Version : 24.0.7
#     API Version    : 1.43
#     OS/Arch        : linux/amd64
#     Total Containers: 5
#     Total Images   : 12
#
#   (Use the values from client.version() and client.info())
#   NOTE: The first line has no leading spaces.  Each data line has no
#         leading spaces.  Use the exact label widths shown above
#         (pad with spaces so the colons align is NOT required --
#          just match the labels exactly as written).

# YOUR CODE HERE


# ============================================================
# TASK 5: Docker health-check utility
# ============================================================
# Write a function called `docker_health_check` that:
#   - Takes one argument: client
#   - Performs these checks and returns a list of strings (messages):
#     1. Call client.ping(). If True, append "PING: OK"
#        If it raises an exception, append "PING: FAILED"
#     2. Call client.info() to get container counts.
#        Append "CONTAINERS: X running, Y stopped" using real numbers.
#     3. Call client.info() to get image count.
#        If images > 0, append "IMAGES: X available"
#        If images == 0, append "IMAGES: No images found"
#     4. Check memory: info["MemTotal"] / (1024**3)
#        If >= 4, append "MEMORY: OK (X.X GB)"
#        If < 4, append "MEMORY: LOW (X.X GB)"
#        (X.X = 1 decimal place)
#   - Also PRINTS each message on its own line (before returning the list).

# YOUR CODE HERE


# ============================================================
# MAIN - Test your solutions
# ============================================================
if __name__ == "__main__":
    print("=" * 50)
    print("  WEEK 9, DAY 1 - Docker SDK Basics")
    print("=" * 50)

    # Task 1 test
    print("\n--- Task 1: MockDockerClient ---")
    mock = MockDockerClient()
    print(f"Ping: {mock.ping()}")
    print(f"Info keys: {sorted(mock.info().keys())}")
    print(f"Version: {mock.version()['Version']}")

    # Task 2 test
    print("\n--- Task 2: Safe Connection ---")
    client = get_docker_client()
    print(f"Client type: {type(client).__name__}")

    # Task 3 test
    print("\n--- Task 3: Docker Info ---")
    info = get_docker_info(client)
    for key, value in info.items():
        print(f"  {key}: {value}")

    # Task 4 test
    print("\n--- Task 4: Version Report ---")
    report = docker_version_report(client)
    print(report)

    # Task 5 test
    print("\n--- Task 5: Health Check ---")
    messages = docker_health_check(client)
    print(f"Total checks: {len(messages)}")
