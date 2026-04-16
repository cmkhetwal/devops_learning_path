# Week 7, Day 4: Socket Basics

## What You'll Learn
- What sockets are and how they work
- The `socket` module in Python
- TCP connections and port checking
- Using `socket.connect_ex()` for non-blocking checks
- Building a port checker tool
- Common ports every DevOps engineer should know

## What Are Sockets?

A socket is a low-level networking endpoint. When your browser connects to
a web server, it creates a socket connection. Every network service (HTTP,
SSH, DNS, database) uses sockets underneath.

```
Client                          Server
[Socket] ---TCP connection---> [Socket listening on port 80]
```

## The socket Module

```python
import socket

# Create a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# AF_INET    = IPv4
# SOCK_STREAM = TCP (reliable, ordered)

# Set a timeout (important!)
sock.settimeout(3)  # 3 seconds

# Connect to a server
try:
    sock.connect(("google.com", 80))  # (host, port)
    print("Connected!")
except socket.timeout:
    print("Connection timed out")
except socket.error as e:
    print(f"Connection failed: {e}")
finally:
    sock.close()  # Always close the socket
```

## Checking if a Port is Open

### Method 1: connect_ex() (Best for port checking)

```python
import socket

def is_port_open(host, port, timeout=3):
    """Check if a port is open on a host.

    connect_ex() returns 0 if connection succeeds, error code otherwise.
    This is better than connect() because it doesn't raise exceptions.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()
    return result == 0  # 0 means success

# Test it
print(is_port_open("google.com", 80))    # True (HTTP)
print(is_port_open("google.com", 443))   # True (HTTPS)
print(is_port_open("google.com", 12345)) # False (not open)
```

### Method 2: connect() with exception handling

```python
import socket

def check_port(host, port, timeout=3):
    """Check port using connect() with exception handling."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False
```

## Common Ports for DevOps

```python
COMMON_PORTS = {
    22:    "SSH",
    25:    "SMTP (Email)",
    53:    "DNS",
    80:    "HTTP",
    443:   "HTTPS",
    3306:  "MySQL",
    5432:  "PostgreSQL",
    6379:  "Redis",
    8080:  "HTTP Alternate / Jenkins",
    8443:  "HTTPS Alternate",
    9090:  "Prometheus",
    27017: "MongoDB",
}
```

## Building a Port Scanner

```python
import socket

def scan_ports(host, ports, timeout=2):
    """Scan multiple ports on a host."""
    results = {}
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        results[port] = result == 0
        sock.close()
    return results

# Scan common ports
ports_to_check = [22, 80, 443, 3306, 5432, 8080]
results = scan_ports("google.com", ports_to_check)

for port, is_open in results.items():
    status = "OPEN" if is_open else "CLOSED"
    print(f"  Port {port}: {status}")
```

## Getting Host Information

```python
import socket

# Resolve hostname to IP
ip = socket.gethostbyname("google.com")
print(f"google.com -> {ip}")  # e.g., 142.250.80.46

# Get your own hostname
hostname = socket.gethostname()
print(f"My hostname: {hostname}")

# Get full hostname info
try:
    host_info = socket.getaddrinfo("google.com", 80)
    for info in host_info[:3]:
        print(f"  Family: {info[0]}, Address: {info[4]}")
except socket.gaierror:
    print("DNS lookup failed")
```

## Simple TCP Client

```python
import socket

def send_http_request(host, port=80, path="/"):
    """Send a raw HTTP GET request using sockets."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        sock.connect((host, port))

        # Send HTTP request
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        sock.sendall(request.encode())

        # Receive response
        response = b""
        while True:
            data = sock.recv(4096)
            if not data:
                break
            response += data

        return response.decode("utf-8", errors="ignore")

    except (socket.timeout, socket.error) as e:
        return f"Error: {e}"
    finally:
        sock.close()

# Get the first line of response
response = send_http_request("httpbin.org", 80, "/get")
first_line = response.split("\r\n")[0]
print(first_line)  # HTTP/1.1 200 OK
```

## Service Checker Pattern

```python
import socket

def check_service(host, port, service_name, timeout=3):
    """Check if a specific service is running."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    result = sock.connect_ex((host, port))
    sock.close()

    return {
        "service": service_name,
        "host": host,
        "port": port,
        "status": "running" if result == 0 else "down",
        "reachable": result == 0
    }

# Check if services are running
services = [
    ("google.com", 80, "Google HTTP"),
    ("google.com", 443, "Google HTTPS"),
    ("localhost", 5432, "Local PostgreSQL"),
    ("localhost", 6379, "Local Redis"),
]

for host, port, name in services:
    result = check_service(host, port, name)
    status_icon = "UP" if result["reachable"] else "DOWN"
    print(f"  [{status_icon}] {result['service']} ({host}:{port})")
```

## DevOps Connection

Socket programming is essential for DevOps because:
- **Health Checks**: Verify services are listening on expected ports
- **Monitoring**: Check if databases, caches, and services are reachable
- **Troubleshooting**: Diagnose network connectivity issues
- **Security**: Audit which ports are open (port scanning)
- **Load Balancers**: Health checks often use TCP port checks
- **Alerting**: Detect when a service goes down by checking its port

The port checker is one of the most practical tools in a DevOps engineer's toolkit.
