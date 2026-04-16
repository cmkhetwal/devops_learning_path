"""
Week 9, Day 2: Container Management

MANAGING DOCKER CONTAINERS WITH PYTHON
=======================================

In this exercise you will build functions to manage containers using mock
objects.  This teaches you the exact patterns used with the real Docker SDK
without requiring a running Docker daemon.

TASKS
-----
1. Create a MockContainer class
2. Build a container manager class
3. Filter containers by status
4. Write a container cleanup function
5. Create a container status report
"""


# ============================================================
# TASK 1: Create a MockContainer class
# ============================================================
# Create a class called `MockContainer` with:
#   __init__(self, name, image, status="running"):
#       - self.name   = name
#       - self.image  = image
#       - self.status = status
#       - self.id     = "sha_" + name  (simple fake ID)
#       - self.short_id = self.id[:10]
#
#   Methods:
#       stop()    -> sets self.status to "exited", prints "<name> stopped"
#       start()   -> sets self.status to "running", prints "<name> started"
#       remove()  -> sets self.status to "removed", prints "<name> removed"
#       __repr__  -> returns "Container(<name>, <status>)"

# YOUR CODE HERE


# ============================================================
# TASK 2: Build a ContainerManager class
# ============================================================
# Create a class called `ContainerManager` with:
#   __init__(self):
#       - self.containers = []   (empty list)
#
#   Methods:
#       add_container(name, image, status="running"):
#           - Creates a MockContainer and appends it to self.containers
#           - Returns the new container
#
#       list_all():
#           - Returns a list of ALL containers
#
#       list_running():
#           - Returns a list of containers where status == "running"
#
#       get_container(name):
#           - Returns the container with matching name
#           - Returns None if not found
#
#       remove_container(name):
#           - Finds the container by name
#           - Calls its .remove() method
#           - Removes it from self.containers list
#           - Returns True if found and removed, False if not found

# YOUR CODE HERE


# ============================================================
# TASK 3: Filter containers by status
# ============================================================
# Write a function called `filter_containers` that:
#   - Takes two arguments: containers (list of MockContainer), status (str)
#   - Returns a list of containers whose .status matches the given status
#   - If status is "all", return the entire list unchanged
#   - Print "Found X containers with status: <status>" where X is the count

# YOUR CODE HERE


# ============================================================
# TASK 4: Container cleanup function
# ============================================================
# Write a function called `cleanup_containers` that:
#   - Takes one argument: manager (a ContainerManager)
#   - Finds all containers with status "exited"
#   - Calls .remove() on each one
#   - Removes them from the manager's containers list
#   - Returns the number of containers cleaned up
#   - Prints "Cleaned up X exited containers"

# YOUR CODE HERE


# ============================================================
# TASK 5: Container status report
# ============================================================
# Write a function called `container_status_report` that:
#   - Takes one argument: manager (a ContainerManager)
#   - Returns a multi-line string formatted as:
#
#     Container Status Report
#     =======================
#     Total: X
#     Running: X
#     Exited: X
#     Other: X
#     ---
#     NAME                 STATUS     IMAGE
#     <name>               <status>   <image>
#     ...
#
#   Rules:
#   - NAME column is 20 chars wide (left-aligned)
#   - STATUS column is 10 chars wide (left-aligned)
#   - IMAGE column is the remainder
#   - List ALL containers from manager.containers
#   - "Other" = total - running - exited

# YOUR CODE HERE


# ============================================================
# MAIN - Test your solutions
# ============================================================
if __name__ == "__main__":
    print("=" * 55)
    print("  WEEK 9, DAY 2 - Container Management")
    print("=" * 55)

    # Task 1 test
    print("\n--- Task 1: MockContainer ---")
    c = MockContainer("web-server", "nginx:latest")
    print(repr(c))
    c.stop()
    print(repr(c))
    c.start()
    print(repr(c))

    # Task 2 test
    print("\n--- Task 2: ContainerManager ---")
    mgr = ContainerManager()
    mgr.add_container("web-1", "nginx:latest")
    mgr.add_container("db-1", "postgres:15", status="running")
    mgr.add_container("cache-1", "redis:7", status="exited")
    mgr.add_container("worker-1", "python:3.11", status="running")
    mgr.add_container("old-app", "myapp:v1", status="exited")

    print(f"All containers: {len(mgr.list_all())}")
    print(f"Running: {len(mgr.list_running())}")
    found = mgr.get_container("db-1")
    print(f"Found db-1: {repr(found)}")
    not_found = mgr.get_container("nonexistent")
    print(f"Found nonexistent: {not_found}")

    # Task 3 test
    print("\n--- Task 3: Filter Containers ---")
    running = filter_containers(mgr.containers, "running")
    exited = filter_containers(mgr.containers, "exited")
    all_c = filter_containers(mgr.containers, "all")

    # Task 4 test
    print("\n--- Task 4: Cleanup ---")
    cleaned = cleanup_containers(mgr)
    print(f"Remaining containers: {len(mgr.list_all())}")

    # Task 5 test - re-add some for the report
    mgr.add_container("api-1", "fastapi:latest")
    mgr.add_container("proxy", "traefik:v2", status="exited")
    print("\n--- Task 5: Status Report ---")
    report = container_status_report(mgr)
    print(report)
