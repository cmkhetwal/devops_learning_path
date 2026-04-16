"""
Week 8, Day 3: Inheritance - Exercise

Build class hierarchies for DevOps infrastructure components.

DevOps Context: Real infrastructure has natural hierarchies -
servers have specializations, deployments have strategies,
and monitors have different protocols.
"""

# ===========================================================
# TASK 1: Server Hierarchy
# ===========================================================
# Create a base Server class and two child classes.
#
# Server (base class):
#   __init__(self, name, ip_address):
#     - self.name, self.ip_address
#     - self.status = "stopped"
#   start(): set status to "running", return "{name} started"
#   stop(): set status to "stopped", return "{name} stopped"
#   get_type(): return "generic"
#   get_info(): return dict with "name", "ip_address", "status", "type"
#     (type comes from get_type())
#   __str__(): return "{type}:{name} ({status})"
#
# WebServer(Server):
#   __init__(self, name, ip_address, port=80):
#     - call super().__init__
#     - self.port = port
#     - self.sites = []
#   add_site(site_name): append to sites, return "Site {site_name} added"
#   get_type(): return "web"
#   get_info(): call super, add "port" and "sites" keys, return dict
#
# DatabaseServer(Server):
#   __init__(self, name, ip_address, engine="postgresql", port=5432):
#     - call super().__init__
#     - self.engine, self.port
#     - self.databases = []
#   create_db(db_name): append to databases, return "Database {db_name} created"
#   get_type(): return "database"
#   get_info(): call super, add "engine", "port", "databases" keys

class Server:
    # YOUR CODE HERE
    pass

class WebServer(Server):
    # YOUR CODE HERE
    pass

class DatabaseServer(Server):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: Deployment Strategies
# ===========================================================
# Create a Deployment base and specialized deployment classes.
#
# Deployment (base):
#   __init__(self, app_name, version):
#     - self.app_name, self.version
#     - self.status = "pending"
#     - self.steps = []
#   start(): set status "in_progress", add "started" to steps.
#     Return "Starting deployment of {app_name} v{version}"
#   complete(): set status "completed", add "completed" to steps.
#     Return "Deployment complete"
#   get_strategy(): return "basic"
#   get_status(): return dict with "app_name", "version", "status",
#     "strategy" (from get_strategy()), "steps"
#
# RollingDeployment(Deployment):
#   __init__(self, app_name, version, batch_size=2):
#     - call super().__init__, self.batch_size, self.batches_completed = 0
#   execute_batch(): increment batches_completed, add "batch_{n}" to steps.
#     Return "Batch {n} deployed"
#   get_strategy(): return "rolling"
#
# BlueGreenDeployment(Deployment):
#   __init__(self, app_name, version):
#     - call super().__init__, self.active_env = "blue"
#   switch(): swap active_env between "blue" and "green",
#     add "switched to {env}" to steps.
#     Return "Switched to {env} environment"
#   get_strategy(): return "blue-green"

class Deployment:
    # YOUR CODE HERE
    pass

class RollingDeployment(Deployment):
    # YOUR CODE HERE
    pass

class BlueGreenDeployment(Deployment):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: Monitor Hierarchy
# ===========================================================
# Create monitors with different check methods.
#
# Monitor (base):
#   __init__(self, name, target):
#     - self.name, self.target
#     - self._checks = []
#   record_check(success, message=""): append dict
#     {"success": bool, "message": str} to _checks.
#     Return "Check recorded for {name}"
#   get_last_status(): return "up" if last check success, "down" if not,
#     "unknown" if no checks
#   get_uptime(self): return percentage of successful checks (float,
#     rounded to 1 decimal). Return 0.0 if no checks.
#   get_type(): return "base"
#   get_summary(): return dict with "name", "target", "type" (from get_type()),
#     "total_checks" (len of _checks), "uptime" (from get_uptime()),
#     "last_status" (from get_last_status())
#
# HTTPMonitor(Monitor):
#   __init__(self, name, url, expected_status=200):
#     - call super().__init__(name, url)
#     - self.url = url (same as target)
#     - self.expected_status = expected_status
#   simulate_check(status_code): record_check with
#     success = (status_code == expected_status)
#     message = "HTTP {status_code}"
#     Return "HTTP check: {status_code}"
#   get_type(): return "http"
#
# TCPMonitor(Monitor):
#   __init__(self, name, host, port):
#     - call super().__init__(name, f"{host}:{port}")
#     - self.host, self.port
#   simulate_check(is_open): record_check with
#     success = is_open
#     message = "port {'open' if is_open else 'closed'}"
#     Return "TCP check: port {'open' if is_open else 'closed'}"
#   get_type(): return "tcp"

class Monitor:
    # YOUR CODE HERE
    pass

class HTTPMonitor(Monitor):
    # YOUR CODE HERE
    pass

class TCPMonitor(Monitor):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: isinstance Checks
# ===========================================================
# Create a function that takes a list of mixed objects (Server,
# WebServer, DatabaseServer, etc.) and categorizes them.
#
# Parameters:
#   - objects: list of objects
#
# Return:
#   {
#       "servers": [names of all Server instances (including children)],
#       "web_servers": [names of WebServer instances only],
#       "database_servers": [names of DatabaseServer instances only],
#       "deployments": [app_names of all Deployment instances (including children)],
#       "monitors": [names of all Monitor instances (including children)],
#       "total": total number of objects
#   }
#
# Use isinstance() to check types.

def categorize_objects(objects):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: Infrastructure Manager
# ===========================================================
# Create an InfrastructureManager class that manages all types of
# servers using polymorphism.
#
# Constructor:
#   - self.servers = []
#
# Methods:
#   - add_server(server): append server to list.
#     Return "Added {server.name} ({server.get_type()})"
#   - start_all(): call start() on each server.
#     Return list of result strings from each start()
#   - stop_all(): call stop() on each server.
#     Return list of result strings.
#   - get_by_type(server_type): return list of servers where
#     get_type() matches server_type.
#   - get_status_report(): return dict:
#     {
#         "total": total count,
#         "running": count of servers with status=="running",
#         "stopped": count with status=="stopped",
#         "by_type": {type: count} e.g., {"web": 2, "database": 1}
#     }
#   - find_server(name): return server with matching name, or None

class InfrastructureManager:
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Task 1
    web = WebServer("web-01", "10.0.1.10")
    db = DatabaseServer("db-01", "10.0.2.10")
    web.start()
    web.add_site("example.com")
    db.create_db("mydb")
    print("Task 1:", web.get_info())
    print("Task 1:", db.get_info())
    print("Task 1:", str(web))
    print()

    # Task 2
    rolling = RollingDeployment("myapp", "2.0", batch_size=3)
    rolling.start()
    rolling.execute_batch()
    rolling.execute_batch()
    print("Task 2:", rolling.get_status())
    bg = BlueGreenDeployment("myapp", "2.0")
    bg.start()
    bg.switch()
    print("Task 2:", bg.get_status())
    print()

    # Task 3
    http_mon = HTTPMonitor("web-check", "https://example.com")
    http_mon.simulate_check(200)
    http_mon.simulate_check(200)
    http_mon.simulate_check(500)
    print("Task 3:", http_mon.get_summary())
    tcp_mon = TCPMonitor("db-check", "10.0.2.10", 5432)
    tcp_mon.simulate_check(True)
    print("Task 3:", tcp_mon.get_summary())
    print()

    # Task 4
    objects = [web, db, rolling, bg, http_mon, tcp_mon]
    print("Task 4:", categorize_objects(objects))
    print()

    # Task 5
    mgr = InfrastructureManager()
    mgr.add_server(WebServer("web-01", "10.0.1.10"))
    mgr.add_server(WebServer("web-02", "10.0.1.11"))
    mgr.add_server(DatabaseServer("db-01", "10.0.2.10"))
    mgr.start_all()
    print("Task 5:", mgr.get_status_report())
