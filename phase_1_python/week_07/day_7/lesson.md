# Week 7, Day 7: Quiz Day - Networking & APIs Cheat Sheet

## Week 7 Cheat Sheet

### HTTP Basics
```python
# HTTP Methods
# GET    = Read data        POST   = Create data
# PUT    = Update data      DELETE = Remove data
# PATCH  = Partial update   HEAD   = Headers only

# Status Code Ranges
# 2xx = Success     3xx = Redirect     4xx = Client Error     5xx = Server Error

# Key Status Codes
# 200 OK              201 Created         204 No Content
# 301 Moved Perm      302 Found           304 Not Modified
# 400 Bad Request     401 Unauthorized    403 Forbidden
# 404 Not Found       429 Rate Limited
# 500 Internal Error  502 Bad Gateway     503 Unavailable
```

### requests Library
```python
import requests

# GET request
response = requests.get(url, params={}, headers={}, timeout=5)

# POST request
response = requests.post(url, json={}, headers={}, timeout=5)

# PUT request
response = requests.put(url, json={}, headers={}, timeout=5)

# DELETE request
response = requests.delete(url, timeout=5)

# Response attributes
response.status_code   # 200 (int)
response.json()        # parsed JSON (dict/list)
response.text          # raw text (str)
response.headers       # response headers
response.ok            # True if status < 400
response.elapsed       # time delta

# Error handling
try:
    response = requests.get(url, timeout=5)
    response.raise_for_status()
except requests.exceptions.Timeout:
    pass  # timed out
except requests.exceptions.ConnectionError:
    pass  # can't connect
except requests.exceptions.HTTPError:
    pass  # bad status code
```

### REST APIs
```python
# REST URL patterns
# GET    /resource          -> List all
# POST   /resource          -> Create new
# GET    /resource/{id}     -> Read one
# PUT    /resource/{id}     -> Update one
# DELETE /resource/{id}     -> Delete one

# Authentication
headers = {"Authorization": "Bearer YOUR_TOKEN"}
headers = {"X-API-Key": "YOUR_KEY"}

# Pagination
params = {"page": 1, "per_page": 20}

# Sessions (reuse connections + auth)
session = requests.Session()
session.headers.update({"Authorization": "Bearer token"})
```

### Sockets
```python
import socket

# Check if port is open
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
result = sock.connect_ex((host, port))  # 0 = open
sock.close()

# DNS lookup
ip = socket.gethostbyname("google.com")
hostname = socket.gethostname()

# Common ports: 22=SSH, 80=HTTP, 443=HTTPS, 3306=MySQL,
# 5432=PostgreSQL, 6379=Redis, 8080=HTTP-Alt
```

### SSH with Paramiko
```python
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname="server", username="user", password="pass")

stdin, stdout, stderr = client.exec_command("uptime")
output = stdout.read().decode()
exit_code = stdout.channel.recv_exit_status()

client.close()

# SFTP
sftp = client.open_sftp()
sftp.put(local_path, remote_path)    # upload
sftp.get(remote_path, local_path)    # download
sftp.close()
```

## Key Concepts
- Always set **timeouts** on network requests
- Always **handle exceptions** for network code
- Use **sessions** when making multiple requests to the same API
- **REST** maps CRUD to HTTP methods
- **Sockets** are the low-level foundation of all network communication
- **SSH** is the standard for remote server management

Good luck on the quiz!
