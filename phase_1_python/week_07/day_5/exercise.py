"""
Week 7, Day 5: SSH with Paramiko - Exercise

Practice SSH automation patterns using a mock/simulation approach.
No actual SSH server is needed - we simulate SSH behavior.

DevOps Context: SSH automation is used for server management,
deployments, and configuration management across server fleets.
"""

# ===========================================================
# MOCK SSH CLIENT (provided - do not modify)
# ===========================================================
# This simulates SSH behavior so you can practice without a server.

class MockSSHClient:
    """Simulates SSH client for practice."""

    def __init__(self):
        self.connected = False
        self.hostname = None
        self.username = None
        self._command_log = []

    def connect(self, hostname, username, password=None, key_filename=None):
        if not hostname or not username:
            raise ValueError("hostname and username are required")
        if password == "wrong_password":
            raise ConnectionError("Authentication failed")
        self.hostname = hostname
        self.username = username
        self.connected = True

    def exec_command(self, command):
        if not self.connected:
            raise RuntimeError("Not connected to any server")
        self._command_log.append(command)

        responses = {
            "hostname": (self.hostname, "", 0),
            "whoami": (self.username, "", 0),
            "uptime": (" 14:30  up 45 days, 3:22, load averages: 0.15 0.10 0.05", "", 0),
            "df -h": ("Filesystem  Size  Used Avail Use%\n/dev/sda1   50G   23G   25G  48%", "", 0),
            "free -m": ("       total  used  free\nMem:    8192  4096  4096\nSwap:   2048   128  1920", "", 0),
            "cat /etc/os-release": ('NAME="Ubuntu"\nVERSION="22.04 LTS"', "", 0),
            "docker ps": ("CONTAINER ID  IMAGE         STATUS       NAMES\nabc123        nginx:latest  Up 2 hours   web-01\ndef456        redis:7       Up 2 hours   cache-01", "", 0),
            "systemctl status nginx": ("nginx.service - nginx\n   Active: active (running)", "", 0),
            "systemctl status redis": ("redis.service - redis\n   Active: active (running)", "", 0),
            "systemctl restart nginx": ("", "", 0),
            "ls /var/log": ("syslog\nnginx\nauth.log\nkern.log", "", 0),
            "cat /proc/cpuinfo | grep processor | wc -l": ("4", "", 0),
            "invalid_command": ("", "command not found: invalid_command", 127),
        }

        stdout, stderr, exit_code = responses.get(
            command, (f"executed: {command}", "", 0)
        )
        return {"stdout": stdout, "stderr": stderr, "exit_code": exit_code}

    def close(self):
        self.connected = False

    def get_command_log(self):
        return list(self._command_log)


# ===========================================================
# TASK 1: SSH Connection Manager
# ===========================================================
# Create a class called SSHManager that wraps the MockSSHClient.
#
# Constructor parameters:
#   - hostname (str)
#   - username (str)
#   - password (str, optional, default None)
#
# Methods:
#   - connect(): create a MockSSHClient, connect it, store as self.client
#       Return True on success, False on failure.
#   - disconnect(): close the client, set self.client to None
#       Return True.
#   - is_connected(): return True if client exists and is connected
#   - run(command): execute a command via self.client.exec_command()
#       Return the result dict {"stdout":..., "stderr":..., "exit_code":...}
#       If not connected, return {"stdout":"", "stderr":"Not connected", "exit_code": 1}
#
# Example:
#   mgr = SSHManager("web-01.example.com", "admin", "secret")
#   mgr.connect()         # True
#   mgr.is_connected()    # True
#   mgr.run("hostname")   # {"stdout": "web-01.example.com", ...}
#   mgr.disconnect()      # True

class SSHManager:
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 2: Remote Command Runner
# ===========================================================
# Create a function that connects to a server, runs a list of
# commands, and returns the results.
#
# Parameters:
#   - hostname (str)
#   - username (str)
#   - password (str)
#   - commands (list of str)
#
# Return a list of dictionaries, one per command:
#   {
#       "command": the command string,
#       "stdout": stdout output,
#       "stderr": stderr output,
#       "exit_code": exit code,
#       "success": True if exit_code == 0, else False
#   }
#
# If connection fails, return an empty list.
# Always disconnect when done (use try/finally).
#
# Example:
#   run_remote_commands("web-01", "admin", "pass", ["hostname", "uptime"])
#   -> [
#       {"command": "hostname", "stdout": "web-01", ..., "success": True},
#       {"command": "uptime", "stdout": "...", ..., "success": True}
#   ]

def run_remote_commands(hostname, username, password, commands):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 3: System Info Gatherer
# ===========================================================
# Create a function that gathers system information from a server.
#
# Parameters:
#   - hostname (str)
#   - username (str)
#   - password (str)
#
# Connect, then run these commands and collect output:
#   - "hostname" -> store as "hostname"
#   - "uptime" -> store as "uptime"
#   - "df -h" -> store as "disk_usage"
#   - "free -m" -> store as "memory"
#   - "cat /etc/os-release" -> store as "os_info"
#   - "cat /proc/cpuinfo | grep processor | wc -l" -> store as "cpu_count"
#
# Return a dictionary with those keys and the stdout values.
# On connection failure, return None.
#
# Example:
#   get_system_info("web-01", "admin", "pass")
#   -> {
#       "hostname": "web-01",
#       "uptime": "...",
#       "disk_usage": "...",
#       "memory": "...",
#       "os_info": "...",
#       "cpu_count": "4"
#   }

def get_system_info(hostname, username, password):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 4: Multi-Server Health Check
# ===========================================================
# Create a function that checks the health of multiple servers.
#
# Parameters:
#   - servers (list of dicts): each dict has "hostname", "username", "password"
#
# For each server:
#   1. Try to connect
#   2. Run "hostname" and "uptime" commands
#   3. Report status
#
# Return a list of dictionaries:
#   {
#       "hostname": the hostname,
#       "reachable": True/False (could we connect?),
#       "uptime": uptime string or "N/A",
#       "status": "healthy" if reachable, "unreachable" if not
#   }
#
# Example:
#   servers = [
#       {"hostname": "web-01", "username": "admin", "password": "pass"},
#       {"hostname": "db-01", "username": "admin", "password": "wrong_password"},
#   ]
#   check_server_health(servers)
#   -> [
#       {"hostname": "web-01", "reachable": True, "uptime": "...", "status": "healthy"},
#       {"hostname": "db-01", "reachable": False, "uptime": "N/A", "status": "unreachable"},
#   ]

def check_server_health(servers):
    # YOUR CODE HERE
    pass


# ===========================================================
# TASK 5: Deployment Simulator
# ===========================================================
# Create a function that simulates deploying to multiple servers.
#
# Parameters:
#   - servers (list of dicts): each has "hostname", "username", "password"
#   - deploy_commands (list of str): commands to run on each server
#
# For each server:
#   1. Connect
#   2. Run all deploy_commands in order
#   3. Track results
#
# Return a dictionary:
#   {
#       "total_servers": number of servers,
#       "successful": number of servers where ALL commands succeeded,
#       "failed": number of servers where connection failed or any command failed,
#       "results": [
#           {
#               "hostname": str,
#               "deployed": True/False,
#               "commands_run": int (number of commands executed),
#               "errors": [list of error strings, if any]
#           }
#       ]
#   }
#
# A command "fails" if its exit_code is not 0.
# If connection fails, deployed=False, commands_run=0, errors=["Connection failed"]
#
# Example:
#   deploy(
#       [{"hostname": "web-01", "username": "admin", "password": "pass"}],
#       ["systemctl restart nginx", "systemctl status nginx"]
#   )

def deploy(servers, deploy_commands):
    # YOUR CODE HERE
    pass


# ===========================================================
# Don't modify below - used for testing
# ===========================================================
if __name__ == "__main__":
    # Task 1
    mgr = SSHManager("web-01.example.com", "admin", "secret")
    print("Task 1 connect:", mgr.connect())
    print("Task 1 connected:", mgr.is_connected())
    print("Task 1 run:", mgr.run("hostname"))
    print("Task 1 disconnect:", mgr.disconnect())
    print()

    # Task 2
    print("Task 2:", run_remote_commands("web-01", "admin", "pass", ["hostname", "uptime"]))
    print()

    # Task 3
    print("Task 3:", get_system_info("web-01", "admin", "pass"))
    print()

    # Task 4
    servers = [
        {"hostname": "web-01", "username": "admin", "password": "pass"},
        {"hostname": "db-01", "username": "admin", "password": "wrong_password"},
    ]
    print("Task 4:", check_server_health(servers))
    print()

    # Task 5
    print("Task 5:", deploy(
        [{"hostname": "web-01", "username": "admin", "password": "pass"},
         {"hostname": "web-02", "username": "admin", "password": "wrong_password"}],
        ["systemctl restart nginx", "systemctl status nginx"]
    ))
