"""
Week 7, Day 4: Socket Basics - Exercise

Practice socket programming to build network checking tools.

DevOps Context: Port checking and service monitoring are daily
tasks for DevOps engineers. These tools help verify deployments
and troubleshoot connectivity issues.

NOTE: Some tests check localhost ports that may or may not be open
on your system. The checker accounts for this.
"""

import socket

# ===========================================================
# TASK 1: Port Checker Function
# ===========================================================
# Create a function that checks if a single port is open on a host.
#
# Parameters:
#   - host (str): hostname or IP address
#   - port (int): port number to check
#   - timeout (int): connection timeout in seconds, default 3
#
# Return a dictionary:
#   {
#       "host": the host,
#       "port": the port,
#       "open": True/False,
#       "service": service name from KNOWN_PORTS or "unknown"
#   }
#
# Use socket.connect_ex() for the check.
# Use the KNOWN_PORTS dict below for service names.
#
# Example:
#   check_port("google.com", 80)
#   -> {"host": "google.com", "port": 80, "open": True, "service": "HTTP"}

KNOWN_PORTS = {
    22: "SSH", 25: "SMTP", 53: "DNS", 80: "HTTP", 443: "HTTPS",
    3306: "MySQL", 5432: "PostgreSQL", 6379: "Redis",
    8080: "HTTP-Alt", 8443: "HTTPS-Alt", 27017: "MongoDB",
}

def check_port(host, port, timeout=3):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: Multi-Port Scanner
# ===========================================================
# Create a function that scans multiple ports on a host.
#
# Parameters:
#   - host (str): hostname or IP
#   - ports (list of int): ports to scan
#   - timeout (int): timeout per port, default 2
#
# Return a dictionary:
#   {
#       "host": the host,
#       "open_ports": [list of open port numbers],
#       "closed_ports": [list of closed port numbers],
#       "results": {port: True/False for each port}
#   }
#
# Example:
#   scan_ports("google.com", [80, 443, 8080])
#   -> {
#       "host": "google.com",
#       "open_ports": [80, 443],
#       "closed_ports": [8080],
#       "results": {80: True, 443: True, 8080: False}
#   }

def scan_ports(host, ports, timeout=2):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: DNS Resolver
# ===========================================================
# Create a function that resolves a hostname to its IP address(es).
#
# Parameters:
#   - hostname (str): the hostname to resolve
#
# Return a dictionary:
#   {
#       "hostname": the hostname,
#       "ip_address": primary IP (from gethostbyname),
#       "resolved": True/False
#   }
#
# If DNS resolution fails, set ip_address to None and resolved to False.
#
# Example:
#   resolve_host("google.com")
#   -> {"hostname": "google.com", "ip_address": "142.250.80.46", "resolved": True}
#   resolve_host("nonexistent.invalid")
#   -> {"hostname": "nonexistent.invalid", "ip_address": None, "resolved": False}

def resolve_host(hostname):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: Service Status Checker
# ===========================================================
# Create a function that checks if a list of services are running.
#
# Parameters:
#   - services (list of tuples): each tuple is (name, host, port)
#   - timeout (int): timeout per check, default 3
#
# Return a list of dictionaries:
#   {
#       "name": service name,
#       "host": host,
#       "port": port,
#       "status": "running" or "down"
#   }
#
# Example:
#   check_services([
#       ("Google HTTP", "google.com", 80),
#       ("Local Redis", "localhost", 6379),
#   ])
#   -> [
#       {"name": "Google HTTP", "host": "google.com", "port": 80, "status": "running"},
#       {"name": "Local Redis", "host": "localhost", "port": 6379, "status": "down"},
#   ]

def check_services(services, timeout=3):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: Port Range Scanner with Summary
# ===========================================================
# Create a function that scans a range of ports and provides
# a summary report.
#
# Parameters:
#   - host (str): hostname or IP
#   - start_port (int): beginning of range (inclusive)
#   - end_port (int): end of range (inclusive)
#   - timeout (int): timeout per port, default 1
#
# Return a dictionary:
#   {
#       "host": the host,
#       "range": "start_port-end_port" (string),
#       "total_scanned": number of ports scanned,
#       "open_ports": [list of dicts with "port" and "service" keys],
#       "open_count": number of open ports,
#       "closed_count": number of closed ports
#   }
#
# For the service name, use KNOWN_PORTS dict or "unknown".
#
# Example:
#   scan_port_range("google.com", 79, 81)
#   -> {
#       "host": "google.com",
#       "range": "79-81",
#       "total_scanned": 3,
#       "open_ports": [{"port": 80, "service": "HTTP"}],
#       "open_count": 1,
#       "closed_count": 2
#   }

def scan_port_range(host, start_port, end_port, timeout=1):
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    print("Task 1:", check_port("google.com", 80))
    print()
    print("Task 2:", scan_ports("google.com", [80, 443, 8080]))
    print()
    print("Task 3:", resolve_host("google.com"))
    print("Task 3:", resolve_host("nonexistent.invalid"))
    print()
    print("Task 4:", check_services([
        ("Google HTTP", "google.com", 80),
        ("Local Redis", "localhost", 6379),
    ]))
    print()
    print("Task 5:", scan_port_range("google.com", 79, 81))
