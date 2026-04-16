"""
Week 4, Day 5: Modules & Imports - Your Custom Module
======================================================

This is the module you'll import in exercise.py.
Complete the functions below, then import them in your exercise.

IMPORTANT: Do NOT rename this file or the functions.
"""


# CONSTANT: Default configuration values
DEFAULT_CONFIG = {
    "port": 8080,
    "region": "us-east-1",
    "max_retries": 3,
    "timeout": 30,
}


def is_port_valid(port):
    """Check if a port number is valid (1-65535, must be int)."""
    return isinstance(port, int) and 0 < port <= 65535


def format_hostname(name, domain="example.com"):
    """
    Format a server name into a full hostname.
    - Strip whitespace
    - Convert to lowercase
    - Replace spaces with hyphens
    - Append domain
    """
    clean = name.strip().lower().replace(" ", "-")
    return f"{clean}.{domain}"


def get_server_status(cpu_percent):
    """
    Return status string based on CPU percentage.
    - Above 90: "critical"
    - Above 70: "warning"
    - 70 or below: "healthy"
    """
    if cpu_percent > 90:
        return "critical"
    elif cpu_percent > 70:
        return "warning"
    return "healthy"


def parse_server_string(server_string):
    """
    Parse a 'hostname:port' string into a dictionary.
    Returns {"hostname": str, "port": int}
    If no port provided, use DEFAULT_CONFIG["port"].

    Examples:
        parse_server_string("web-01:8080")  -> {"hostname": "web-01", "port": 8080}
        parse_server_string("db-01")        -> {"hostname": "db-01", "port": 8080}
    """
    if ":" in server_string:
        parts = server_string.split(":")
        return {"hostname": parts[0], "port": int(parts[1])}
    return {"hostname": server_string, "port": DEFAULT_CONFIG["port"]}


if __name__ == "__main__":
    print("server_utils module - self test")
    print(f"  is_port_valid(80): {is_port_valid(80)}")
    print(f"  is_port_valid(0): {is_port_valid(0)}")
    print(f"  format_hostname('Web 01'): {format_hostname('Web 01')}")
    print(f"  get_server_status(95): {get_server_status(95)}")
    print(f"  parse_server_string('web-01:8080'): {parse_server_string('web-01:8080')}")
    print("All self-tests complete.")
