# Week 8, Day 7: Phase 2 Final Test - Comprehensive Cheat Sheet

## Phase 2 Summary (Weeks 5-8)

Congratulations on reaching the end of Phase 2! Here is a comprehensive
cheat sheet covering everything from Weeks 5 through 8.

---

## Week 5: File Handling & Data Formats

### File I/O
```python
# Read a file
with open("file.txt", "r") as f:
    content = f.read()       # Entire file as string
    # or
    lines = f.readlines()   # List of lines

# Write a file
with open("file.txt", "w") as f:
    f.write("Hello\n")

# Append to a file
with open("file.txt", "a") as f:
    f.write("New line\n")

# Read line by line (memory efficient)
with open("file.txt") as f:
    for line in f:
        print(line.strip())
```

### JSON
```python
import json

# Read JSON
with open("data.json") as f:
    data = json.load(f)

# Write JSON
with open("data.json", "w") as f:
    json.dump(data, f, indent=2)

# String conversion
json_str = json.dumps(data)
data = json.loads(json_str)
```

### YAML
```python
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

with open("config.yaml", "w") as f:
    yaml.dump(config, f, default_flow_style=False)
```

### CSV
```python
import csv

# Read CSV
with open("data.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["column_name"])

# Write CSV
with open("data.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "value"])
    writer.writeheader()
    writer.writerow({"name": "test", "value": 42})
```

---

## Week 6: Error Handling & OS Operations

### Exception Handling
```python
try:
    result = risky_operation()
except ValueError as e:
    print(f"Value error: {e}")
except FileNotFoundError:
    print("File not found")
except Exception as e:
    print(f"Unexpected: {e}")
else:
    print("Success!")
finally:
    cleanup()

# Raise exceptions
raise ValueError("Invalid input")

# Custom exceptions
class DeploymentError(Exception):
    pass
```

### OS Operations
```python
import os
import shutil
from pathlib import Path

# Path operations
os.path.exists("file.txt")
os.path.join("dir", "file.txt")
os.makedirs("dir/subdir", exist_ok=True)
os.listdir(".")
os.remove("file.txt")
shutil.rmtree("directory")
shutil.copy("src", "dst")

# pathlib (modern)
p = Path("dir/file.txt")
p.exists()
p.read_text()
p.write_text("content")
p.parent.mkdir(parents=True, exist_ok=True)
list(Path(".").glob("*.py"))
```

### Subprocess
```python
import subprocess

result = subprocess.run(
    ["ls", "-la"],
    capture_output=True,
    text=True,
    timeout=30
)
print(result.stdout)
print(result.returncode)  # 0 = success
```

---

## Week 7: Networking & APIs

### HTTP with requests
```python
import requests

# GET
response = requests.get(url, params={}, headers={}, timeout=5)
response.status_code   # 200
response.json()        # parsed JSON
response.ok            # True if < 400

# POST
response = requests.post(url, json=data, timeout=5)

# PUT / DELETE
response = requests.put(url, json=data, timeout=5)
response = requests.delete(url, timeout=5)

# Error handling
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.Timeout:
    pass
except requests.exceptions.HTTPError:
    pass
```

### Status Codes
```
200 OK          201 Created       204 No Content
301 Moved       400 Bad Request   401 Unauthorized
403 Forbidden   404 Not Found     500 Server Error
502 Bad Gateway 503 Unavailable
```

### Sockets
```python
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
result = sock.connect_ex((host, port))  # 0 = open
sock.close()

ip = socket.gethostbyname("google.com")
```

---

## Week 8: OOP & Project Structure

### Classes
```python
class Server:
    count = 0  # Class attribute

    def __init__(self, name, ip):
        self.name = name       # Instance attribute
        self.ip = ip
        Server.count += 1

    def start(self):           # Instance method
        return f"{self.name} started"

    @classmethod
    def from_config(cls, cfg): # Alternative constructor
        return cls(cfg["name"], cfg["ip"])

    @staticmethod
    def validate_ip(ip):       # Utility function
        parts = ip.split(".")
        return len(parts) == 4

    @property
    def info(self):            # Computed property
        return f"{self.name} ({self.ip})"
```

### Inheritance
```python
class WebServer(Server):
    def __init__(self, name, ip, port=80):
        super().__init__(name, ip)
        self.port = port

    def start(self):           # Override parent
        result = super().start()
        return f"{result} on port {self.port}"

isinstance(web, Server)     # True
isinstance(web, WebServer)  # True
```

### Project Structure
```
project/
├── package/
│   ├── __init__.py
│   ├── core.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── requirements.txt
├── setup.py
└── README.md
```

### Testing with pytest
```python
import pytest

def test_something():
    assert result == expected

def test_raises():
    with pytest.raises(ValueError):
        bad_function()

@pytest.fixture
def server():
    return Server("test", "10.0.1.1")

def test_with_fixture(server):
    assert server.name == "test"
```

---

## Key Takeaways from Phase 2

1. **Always use `with` for files** - ensures proper cleanup
2. **Handle exceptions** - never let scripts crash silently
3. **Set timeouts** on all network operations
4. **Use classes** to model infrastructure components
5. **Write tests** before deploying to production
6. **Structure projects** properly from the start
7. **Use virtual environments** for dependency isolation

Good luck on the final test!
