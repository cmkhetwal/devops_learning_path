# Week 7, Day 6: Practice Day - Networking Mini-Projects

## What You'll Build Today
Five mini-projects that combine everything from this week:
1. API Health Checker - monitor multiple endpoints
2. Port Scanner - scan a range of ports on hosts
3. REST API Client Library - reusable API wrapper
4. URL Status Checker - batch URL validation
5. Multi-Server Status Dashboard - simulated server monitoring

## Tips for Today
- Read each task carefully before coding
- Reuse patterns from Days 1-5
- Focus on error handling - real DevOps tools must handle failures
- Test your functions with the provided examples

## Quick Reference

```python
# HTTP requests
import requests
response = requests.get(url, timeout=5)
response.status_code  # 200
response.json()       # parsed JSON
response.ok           # True if status < 400

# Sockets
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
result = sock.connect_ex((host, port))  # 0 = open
sock.close()

# Error handling
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.Timeout:
    print("Timed out")
except requests.exceptions.ConnectionError:
    print("Connection failed")
except requests.exceptions.HTTPError as e:
    print(f"HTTP error: {e}")
```

Good luck! These projects are practical tools you can use in real DevOps work.
