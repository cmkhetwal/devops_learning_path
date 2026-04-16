"""
Week 8, Day 5: Unit Testing - Exercise

Write test functions for a Server class and utility functions.
This file IS the test file - it can be run with pytest.

DevOps Context: Writing tests is a fundamental DevOps skill.
Every CI/CD pipeline should run tests before deployment.

Run with: pytest exercise.py -v
"""

import pytest

# ============================================================
# CODE TO TEST (provided - do not modify this section)
# ============================================================

class Server:
    """Server class to test."""
    def __init__(self, name, ip_address, role="web"):
        if not name:
            raise ValueError("Server name cannot be empty")
        if not validate_ip(ip_address):
            raise ValueError(f"Invalid IP address: {ip_address}")
        self.name = name
        self.ip_address = ip_address
        self.role = role
        self.status = "stopped"
        self.cpu_usage = 0.0

    def start(self):
        if self.status == "running":
            return f"{self.name} is already running"
        self.status = "running"
        return f"{self.name} started"

    def stop(self):
        if self.status == "stopped":
            return f"{self.name} is already stopped"
        self.status = "stopped"
        self.cpu_usage = 0.0
        return f"{self.name} stopped"

    def set_cpu(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("CPU usage must be a number")
        if value < 0 or value > 100:
            raise ValueError("CPU usage must be between 0 and 100")
        self.cpu_usage = float(value)

    def is_healthy(self):
        return self.status == "running" and self.cpu_usage < 90

    def get_info(self):
        return {
            "name": self.name,
            "ip_address": self.ip_address,
            "role": self.role,
            "status": self.status,
            "cpu_usage": self.cpu_usage,
            "healthy": self.is_healthy()
        }


def validate_ip(ip_str):
    """Validate IPv4 address."""
    try:
        parts = ip_str.split(".")
        if len(parts) != 4:
            return False
        return all(0 <= int(p) <= 255 for p in parts)
    except (ValueError, AttributeError):
        return False


def format_status(server):
    """Format server status as a string."""
    status = "UP" if server.status == "running" else "DOWN"
    health = "HEALTHY" if server.is_healthy() else "UNHEALTHY"
    return f"[{status}] {server.name} ({server.ip_address}) - {health}"


# ============================================================
# TASK 1: Test Server Creation
# ============================================================
# Write 3 test functions for Server.__init__:
#
# test_server_creation: Create a server with name="web-01",
#   ip_address="10.0.1.10". Assert name, ip_address, role (default),
#   and status (stopped) are correct.
#
# test_server_custom_role: Create a server with role="database".
#   Assert role is "database".
#
# test_server_invalid_name: Test that creating a Server with
#   empty name raises ValueError. Use pytest.raises().

def test_server_creation():
    # YOUR CODE HERE
    pass

def test_server_custom_role():
    # YOUR CODE HERE
    pass

def test_server_invalid_name():
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: Test Server Methods
# ============================================================
# Write 4 test functions for start/stop:
#
# test_server_start: Start a server, check status is "running"
#   and return value contains "started".
#
# test_server_start_already_running: Start twice, check second
#   call returns "already running".
#
# test_server_stop: Start then stop, check status is "stopped".
#
# test_server_stop_resets_cpu: Start, set cpu to 50.0, stop.
#   Check cpu_usage is 0.0 after stop.

def test_server_start():
    # YOUR CODE HERE
    pass

def test_server_start_already_running():
    # YOUR CODE HERE
    pass

def test_server_stop():
    # YOUR CODE HERE
    pass

def test_server_stop_resets_cpu():
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: Test CPU and Health
# ============================================================
# Write 4 test functions:
#
# test_set_cpu_valid: Set cpu to 45.0, assert cpu_usage == 45.0
#
# test_set_cpu_invalid_high: Setting cpu to 150 should raise ValueError.
#
# test_set_cpu_invalid_type: Setting cpu to "high" should raise TypeError.
#
# test_is_healthy: A running server with cpu < 90 is healthy.
#   A running server with cpu >= 90 is NOT healthy.
#   A stopped server is NOT healthy.

def test_set_cpu_valid():
    # YOUR CODE HERE
    pass

def test_set_cpu_invalid_high():
    # YOUR CODE HERE
    pass

def test_set_cpu_invalid_type():
    # YOUR CODE HERE
    pass

def test_is_healthy():
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: Test Utility Functions
# ============================================================
# Write 3 test functions:
#
# test_validate_ip_valid: Test that valid IPs return True.
#   Test at least: "10.0.1.10", "192.168.1.1", "0.0.0.0"
#
# test_validate_ip_invalid: Test that invalid IPs return False.
#   Test at least: "999.0.1.1", "10.0.1", "abc.def.ghi.jkl", ""
#
# test_format_status: Create a server, start it. Call format_status().
#   Assert the result contains "UP", the server name, and "HEALTHY".
#   Stop the server. Assert result contains "DOWN" and "UNHEALTHY".

def test_validate_ip_valid():
    # YOUR CODE HERE
    pass

def test_validate_ip_invalid():
    # YOUR CODE HERE
    pass

def test_format_status():
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: Test with Fixtures and get_info
# ============================================================
# Create a pytest fixture called 'web_server' that returns a
# Server with name="web-01", ip_address="10.0.1.10".
#
# Create a fixture called 'running_server' that returns a started
# Server (name="app-01", ip_address="10.0.1.20") with cpu at 45.0.
#
# Write 3 test functions using these fixtures:
#
# test_fixture_server(web_server): assert web_server.name is "web-01"
#
# test_fixture_running(running_server): assert status is "running"
#   and cpu_usage is 45.0
#
# test_get_info(running_server): call get_info(), assert it returns
#   a dict with correct name, status, cpu_usage, and healthy values.

@pytest.fixture
def web_server():
    # YOUR CODE HERE
    pass

@pytest.fixture
def running_server():
    # YOUR CODE HERE
    pass

def test_fixture_server(web_server):
    # YOUR CODE HERE
    pass

def test_fixture_running(running_server):
    # YOUR CODE HERE
    pass

def test_get_info(running_server):
    # YOUR CODE HERE
    pass


# ============================================================
# Don't modify below - used for manual testing
# ============================================================
if __name__ == "__main__":
    print("Run this file with: pytest exercise.py -v")
    print("Or use: python check.py")
