"""
Week 8, Day 1: Classes & Objects - Exercise

Practice creating classes and objects for DevOps concepts.

DevOps Context: Model real infrastructure components as Python
objects - this is how tools like Ansible, Terraform, and
Kubernetes SDKs work internally.
"""

# ===========================================================
# TASK 1: Server Class
# ===========================================================
# Create a class called Server with:
#
# Constructor (__init__) parameters:
#   - name (str): server name
#   - ip_address (str): IP address
#   - role (str): default "web"
#
# Instance attributes (set in __init__):
#   - name, ip_address, role (from parameters)
#   - status: always starts as "stopped"
#   - cpu_usage: starts at 0.0
#   - memory_usage: starts at 0.0
#
# Methods:
#   - start(): set status to "running", return "{name} is now running"
#   - stop(): set status to "stopped", return "{name} is now stopped"
#   - get_info(): return a dict with keys: name, ip_address, role, status
#   - __str__(): return "Server({name}, {ip_address}, {role}, {status})"
#
# Example:
#   s = Server("web-01", "10.0.1.10")
#   s.start()       # "web-01 is now running"
#   s.get_info()    # {"name":"web-01", "ip_address":"10.0.1.10", "role":"web", "status":"running"}
#   str(s)          # "Server(web-01, 10.0.1.10, web, running)"

class Server:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: Container Class
# ===========================================================
# Create a class called Container with:
#
# Class attribute:
#   - total_created: starts at 0, incremented each time a Container is made
#
# Constructor parameters:
#   - name (str): container name
#   - image (str): Docker image (e.g., "nginx:latest")
#   - ports (list, optional): default empty list
#
# Instance attributes:
#   - name, image, ports (from parameters; copy ports list to avoid mutation)
#   - status: starts as "created"
#   - container_id: auto-generated as "cnt-{total_created}" (BEFORE incrementing)
#     e.g., first container is "cnt-0", second is "cnt-1"
#
# Methods:
#   - start(): if status is "running", return "{name} already running".
#     Otherwise set status to "running", return "{name} started"
#   - stop(): if status is not "running", return "{name} not running".
#     Otherwise set status to "stopped", return "{name} stopped"
#   - get_info(): return dict with keys: container_id, name, image, status, ports
#   - __str__(): return "Container({container_id}: {name} [{image}] - {status})"
#
# Example:
#   c = Container("web", "nginx:latest", [80, 443])
#   c.start()  # "web started"
#   c.start()  # "web already running"

class Container:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: Deployment Class
# ===========================================================
# Create a class called Deployment with:
#
# Constructor parameters:
#   - app_name (str): name of the application
#   - version (str): version being deployed
#   - environment (str): default "staging"
#
# Instance attributes:
#   - app_name, version, environment (from parameters)
#   - status: starts as "pending"
#   - steps_completed: starts as empty list
#
# Methods:
#   - start(): set status to "in_progress", add "started" to steps_completed.
#     Return "Deploying {app_name} v{version} to {environment}"
#   - complete(): set status to "completed", add "completed" to steps_completed.
#     Return "Deployment of {app_name} v{version} complete"
#   - fail(reason): set status to "failed", add "failed: {reason}" to steps.
#     Return "Deployment failed: {reason}"
#   - get_status(): return dict with keys: app_name, version, environment,
#     status, steps_completed
#   - __str__(): return "Deployment({app_name} v{version} -> {environment}: {status})"

class Deployment:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: NetworkInterface Class
# ===========================================================
# Create a class called NetworkInterface with:
#
# Constructor parameters:
#   - name (str): interface name (e.g., "eth0")
#   - ip_address (str): IP address
#   - subnet_mask (str): default "255.255.255.0"
#   - is_up (bool): default True
#
# Instance attributes: all constructor params stored as-is
#   - bytes_sent: starts at 0
#   - bytes_received: starts at 0
#
# Methods:
#   - send_data(num_bytes): add num_bytes to bytes_sent if is_up.
#     Return True if sent, False if interface is down.
#   - receive_data(num_bytes): add num_bytes to bytes_received if is_up.
#     Return True if received, False if interface is down.
#   - get_stats(): return dict with keys: name, ip_address, is_up,
#     bytes_sent, bytes_received, total_traffic (sent + received)
#   - toggle(): flip is_up (True->False, False->True).
#     Return "eth0 is now up" or "eth0 is now down"
#   - __str__(): return "{name}: {ip_address} ({'UP' if is_up else 'DOWN'})"

class NetworkInterface:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: ServerRack Class
# ===========================================================
# Create a class called ServerRack that holds multiple Server objects.
#
# Constructor parameters:
#   - rack_id (str): rack identifier (e.g., "RACK-A1")
#   - capacity (int): max number of servers, default 10
#
# Instance attributes:
#   - rack_id, capacity (from parameters)
#   - servers: starts as empty list
#
# Methods:
#   - add_server(server): add a Server object to servers list.
#     If at capacity, return "Rack {rack_id} is full".
#     Otherwise add and return "Added {server.name} to {rack_id}"
#   - remove_server(server_name): remove server with matching name.
#     Return "Removed {name} from {rack_id}" or
#     "Server {name} not found in {rack_id}"
#   - get_server(server_name): return the Server object with matching name,
#     or None if not found.
#   - list_servers(): return list of server names (strings).
#   - rack_status(): return dict with keys:
#     rack_id, capacity, used (number of servers), available (capacity - used),
#     servers (list of server name strings)
#   - __str__(): return "ServerRack({rack_id}: {used}/{capacity} servers)"
#
# Example:
#   rack = ServerRack("RACK-A1", capacity=3)
#   s1 = Server("web-01", "10.0.1.10")
#   rack.add_server(s1)   # "Added web-01 to RACK-A1"
#   rack.list_servers()    # ["web-01"]

class ServerRack:
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Task 1
    s = Server("web-01", "10.0.1.10")
    print("Task 1:", s.start())
    print("Task 1:", s.get_info())
    print("Task 1:", s)
    print()

    # Task 2
    c = Container("web", "nginx:latest", [80, 443])
    print("Task 2:", c.start())
    print("Task 2:", c.start())
    print("Task 2:", c.get_info())
    print()

    # Task 3
    d = Deployment("myapp", "2.1.0", "production")
    print("Task 3:", d.start())
    print("Task 3:", d.complete())
    print("Task 3:", d.get_status())
    print()

    # Task 4
    nic = NetworkInterface("eth0", "10.0.1.10")
    nic.send_data(1024)
    nic.receive_data(2048)
    print("Task 4:", nic.get_stats())
    print("Task 4:", nic)
    print()

    # Task 5
    rack = ServerRack("RACK-A1", capacity=2)
    rack.add_server(Server("web-01", "10.0.1.10"))
    rack.add_server(Server("web-02", "10.0.1.11"))
    print("Task 5:", rack.add_server(Server("web-03", "10.0.1.12")))  # Full
    print("Task 5:", rack.list_servers())
    print("Task 5:", rack.rack_status())
    print("Task 5:", rack)
