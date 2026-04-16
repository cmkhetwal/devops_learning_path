"""
Week 7, Day 6: Practice Day - Networking Mini-Projects

Build 5 mini-projects that combine HTTP, sockets, and API skills.

DevOps Context: These are real tools that DevOps engineers build
and use daily for monitoring, automation, and troubleshooting.
"""

import socket

# ===========================================================
# PROJECT 1: API Health Checker
# ===========================================================
# Create a function that checks the health of multiple API endpoints.
#
# Parameters:
#   - endpoints (list of dicts): each has "name" (str) and "url" (str)
#   - timeout (int): request timeout, default 5
#
# For each endpoint, make a GET request and collect:
#   - name, url, status_code, response_time_ms (rounded to 2 places),
#     healthy (True if status < 400 and request succeeded)
#
# Return a dictionary:
#   {
#       "total": number of endpoints checked,
#       "healthy": number of healthy endpoints,
#       "unhealthy": number of unhealthy endpoints,
#       "results": [list of result dicts per endpoint]
#   }
#
# On request failure, set status_code to None, response_time_ms to 0.0,
# healthy to False.
#
# Example:
#   check_api_health([
#       {"name": "JSONPlaceholder", "url": "https://jsonplaceholder.typicode.com/posts/1"},
#       {"name": "Bad URL", "url": "https://httpbin.org/status/500"},
#   ])

def check_api_health(endpoints, timeout=5):
    # YOUR CODE HERE
    pass


# ===========================================================
# PROJECT 2: Port Scanner
# ===========================================================
# Create a function that scans common service ports on a host.
#
# Parameters:
#   - host (str): hostname or IP to scan
#   - port_list (list of int, optional): specific ports to scan.
#     If None, scan these defaults: [22, 80, 443, 3306, 5432, 6379, 8080, 8443, 27017]
#   - timeout (int): timeout per port, default 2
#
# Return a dictionary:
#   {
#       "host": the host,
#       "scan_summary": "X open, Y closed out of Z scanned",
#       "open_services": [{"port": int, "service": str}, ...],
#       "all_results": {port: {"open": bool, "service": str}, ...}
#   }
#
# Use these service names:
SERVICE_NAMES = {
    22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL",
    5432: "PostgreSQL", 6379: "Redis", 8080: "HTTP-Alt",
    8443: "HTTPS-Alt", 27017: "MongoDB", 9090: "Prometheus",
    3000: "Grafana", 9200: "Elasticsearch",
}
# For unknown ports, use "unknown".
#
# Example:
#   port_scanner("google.com")
#   -> {"host": "google.com", "scan_summary": "2 open, 7 closed out of 9 scanned", ...}

def port_scanner(host, port_list=None, timeout=2):
    # YOUR CODE HERE
    pass


# ===========================================================
# PROJECT 3: REST API Client Library
# ===========================================================
# Create a class called DevOpsAPIClient that provides a clean
# interface for REST API interactions.
#
# Constructor:
#   - base_url (str): the API base URL
#   - auth_token (str, optional): Bearer token for auth
#   - timeout (int): default 10
#
# Methods:
#   - list(resource): GET /{resource}, return list or []
#   - get(resource, id): GET /{resource}/{id}, return dict or None
#   - create(resource, data): POST /{resource} with json=data,
#       return {"success": True, "data": response_json} or
#       {"success": False, "error": error_message}
#   - update(resource, id, data): PUT /{resource}/{id} with json=data,
#       return {"success": True, "data": response_json} or
#       {"success": False, "error": error_message}
#   - delete(resource, id): DELETE /{resource}/{id},
#       return {"success": True, "status_code": int} or
#       {"success": False, "error": error_message}
#
# All methods should handle exceptions gracefully.
# If auth_token is set, include "Authorization": "Bearer {token}" header.
#
# Example:
#   client = DevOpsAPIClient("https://jsonplaceholder.typicode.com")
#   posts = client.list("posts")          # list of 100 posts
#   post = client.get("posts", 1)         # single post
#   new = client.create("posts", {...})   # create post
#   client.delete("posts", 1)             # delete post

class DevOpsAPIClient:
    # YOUR CODE HERE
    pass


# ===========================================================
# PROJECT 4: URL Status Checker
# ===========================================================
# Create a function that checks the status of multiple URLs
# and categorizes them.
#
# Parameters:
#   - urls (list of str): URLs to check
#   - timeout (int): default 5
#
# Return a dictionary:
#   {
#       "checked": total number of URLs,
#       "categories": {
#           "success": [urls with 2xx status],
#           "redirect": [urls with 3xx status],
#           "client_error": [urls with 4xx status],
#           "server_error": [urls with 5xx status],
#           "unreachable": [urls that failed to connect/timeout]
#       },
#       "details": [
#           {"url": str, "status_code": int or None, "category": str}
#       ]
#   }
#
# NOTE: Use allow_redirects=False in requests.get() so you can
# detect 3xx redirects instead of following them.
#
# Example:
#   check_urls([
#       "https://httpbin.org/status/200",
#       "https://httpbin.org/status/301",
#       "https://httpbin.org/status/404",
#   ])

def check_urls(urls, timeout=5):
    # YOUR CODE HERE
    pass


# ===========================================================
# PROJECT 5: Multi-Server Status Dashboard
# ===========================================================
# Create a function that simulates a server monitoring dashboard.
# Uses the MockServer class below (do not modify it).
#
# Parameters:
#   - servers (list of MockServer instances)
#
# For each server, call its .get_status() method and compile results.
#
# Return a dictionary:
#   {
#       "total_servers": int,
#       "servers_up": int,
#       "servers_down": int,
#       "total_cpu_percent": float (sum of all cpu_percent values),
#       "avg_cpu_percent": float (average, rounded to 1 decimal),
#       "total_memory_mb": int (sum of memory_used_mb),
#       "alerts": [list of alert strings for servers that are down
#                  or have cpu > 80 or memory_used > 7000],
#       "server_details": [list of status dicts from each server]
#   }
#
# Alert format:
#   "ALERT: {name} is DOWN" for servers that are down
#   "ALERT: {name} CPU at {cpu}%" for cpu > 80
#   "ALERT: {name} memory at {mem}MB" for memory_used_mb > 7000

class MockServer:
    """Simulated server for dashboard project. Do not modify."""
    def __init__(self, name, status="running", cpu=25.0, memory=2048):
        self.name = name
        self._status = status
        self._cpu = cpu
        self._memory = memory

    def get_status(self):
        return {
            "name": self.name,
            "status": self._status,
            "cpu_percent": self._cpu,
            "memory_used_mb": self._memory,
            "disk_percent": 45.0,
        }

def server_dashboard(servers):
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Project 1
    print("=== Project 1: API Health Checker ===")
    endpoints = [
        {"name": "Posts API", "url": "https://jsonplaceholder.typicode.com/posts/1"},
        {"name": "Users API", "url": "https://jsonplaceholder.typicode.com/users/1"},
    ]
    print(check_api_health(endpoints))
    print()

    # Project 2
    print("=== Project 2: Port Scanner ===")
    print(port_scanner("google.com", [80, 443, 8080]))
    print()

    # Project 3
    print("=== Project 3: REST API Client ===")
    client = DevOpsAPIClient("https://jsonplaceholder.typicode.com")
    print("List:", len(client.list("posts")), "posts")
    print("Get:", client.get("posts", 1))
    print()

    # Project 4
    print("=== Project 4: URL Status Checker ===")
    print(check_urls(["https://httpbin.org/status/200", "https://httpbin.org/status/404"]))
    print()

    # Project 5
    print("=== Project 5: Server Dashboard ===")
    mock_servers = [
        MockServer("web-01", "running", 35.0, 4096),
        MockServer("web-02", "running", 85.0, 4096),
        MockServer("db-01", "stopped", 0.0, 0),
        MockServer("cache-01", "running", 20.0, 7500),
    ]
    print(server_dashboard(mock_servers))
