# Week 7, Day 1: HTTP Basics

## What You'll Learn
- How the HTTP protocol works
- HTTP methods: GET, POST, PUT, DELETE
- Common status codes and what they mean
- Headers and JSON request/response bodies
- Why DevOps engineers must understand HTTP

## How HTTP Works

HTTP (HyperText Transfer Protocol) is the foundation of web communication. Every time
you deploy an app, check a health endpoint, or call an API, you're using HTTP.

### The Request-Response Cycle

```
Client (you)  --->  REQUEST  --->  Server
Client (you)  <---  RESPONSE <---  Server
```

A request has:
1. **Method** - What action you want (GET, POST, etc.)
2. **URL** - Where to send it (https://api.example.com/servers)
3. **Headers** - Metadata (content type, auth tokens)
4. **Body** - Data you're sending (for POST/PUT)

A response has:
1. **Status Code** - Did it work? (200, 404, 500, etc.)
2. **Headers** - Metadata about the response
3. **Body** - The data returned (often JSON)

## HTTP Methods

```python
# The 4 main HTTP methods map to CRUD operations:

# GET    = Read    - Fetch data, no body sent
# POST   = Create  - Send data to create something
# PUT    = Update  - Send data to replace/update something
# DELETE = Delete  - Remove something

# DevOps examples:
# GET    /api/servers          -> List all servers
# GET    /api/servers/42       -> Get server #42 details
# POST   /api/servers          -> Create a new server
# PUT    /api/servers/42       -> Update server #42
# DELETE /api/servers/42       -> Delete server #42
```

### Less Common Methods
```python
# PATCH  = Partial update (change one field, not the whole resource)
# HEAD   = Like GET but only returns headers (good for checking if something exists)
# OPTIONS = Ask what methods are allowed
```

## Status Codes

Status codes tell you what happened. They fall into 5 categories:

```python
# 1xx - Informational (rare, you won't see these often)
# 2xx - Success!
# 3xx - Redirection (resource moved)
# 4xx - Client Error (YOU did something wrong)
# 5xx - Server Error (SERVER did something wrong)

# === SUCCESS (2xx) ===
# 200 OK              - Request succeeded
# 201 Created         - New resource was created (after POST)
# 204 No Content      - Success but nothing to return (after DELETE)

# === REDIRECTION (3xx) ===
# 301 Moved Permanently - Resource has a new URL forever
# 302 Found             - Resource temporarily at different URL
# 304 Not Modified      - Cached version is still good

# === CLIENT ERRORS (4xx) ===
# 400 Bad Request      - Your request was malformed
# 401 Unauthorized     - You need to authenticate (log in)
# 403 Forbidden        - You're authenticated but not allowed
# 404 Not Found        - Resource doesn't exist
# 405 Method Not Allowed - Wrong HTTP method for this endpoint
# 429 Too Many Requests  - Rate limited, slow down

# === SERVER ERRORS (5xx) ===
# 500 Internal Server Error - Server crashed
# 502 Bad Gateway          - Upstream server failed
# 503 Service Unavailable  - Server is overloaded or in maintenance
# 504 Gateway Timeout      - Upstream server took too long
```

### DevOps Status Code Quick Reference
```python
status_meanings = {
    200: "Everything is fine",
    201: "Resource created successfully",
    301: "Update your bookmarks/configs - URL changed",
    400: "Check your request format/data",
    401: "Check your API key or token",
    403: "You don't have permission - check IAM/roles",
    404: "Wrong URL or resource was deleted",
    500: "Application bug - check server logs",
    502: "Backend server is down - check upstream",
    503: "Server overloaded - scale up or wait",
}
```

## Headers

Headers carry metadata about the request/response:

```python
# Common Request Headers
request_headers = {
    "Content-Type": "application/json",      # What format the body is in
    "Accept": "application/json",            # What format you want back
    "Authorization": "Bearer your-token",    # Authentication
    "User-Agent": "MyApp/1.0",              # Who is making the request
}

# Common Response Headers
# Content-Type: application/json     -> Body is JSON
# Content-Length: 1234               -> Size of body in bytes
# X-RateLimit-Remaining: 58         -> API calls left
# Retry-After: 30                   -> Wait 30 seconds (when rate limited)
```

## JSON Body

Most modern APIs use JSON (JavaScript Object Notation) for data:

```python
import json

# A JSON request body (creating a server)
request_body = {
    "name": "web-server-01",
    "type": "t3.medium",
    "region": "us-east-1",
    "tags": ["production", "web"]
}

# Convert Python dict to JSON string
json_string = json.dumps(request_body, indent=2)
print(json_string)
# {
#   "name": "web-server-01",
#   "type": "t3.medium",
#   "region": "us-east-1",
#   "tags": ["production", "web"]
# }

# Convert JSON string back to Python dict
data = json.loads(json_string)
print(data["name"])  # web-server-01

# JSON data types map to Python:
# JSON string  -> Python str
# JSON number  -> Python int or float
# JSON object  -> Python dict
# JSON array   -> Python list
# JSON true    -> Python True
# JSON false   -> Python False
# JSON null    -> Python None
```

## Putting It All Together

```python
# A complete HTTP interaction looks like this:

# 1. Client sends request:
# POST /api/v1/servers HTTP/1.1
# Host: api.example.com
# Content-Type: application/json
# Authorization: Bearer abc123
#
# {"name": "web-01", "type": "small"}

# 2. Server sends response:
# HTTP/1.1 201 Created
# Content-Type: application/json
#
# {"id": 42, "name": "web-01", "type": "small", "status": "creating"}
```

## DevOps Connection

HTTP knowledge is critical for DevOps because:
- **Health Checks**: Load balancers use HTTP GET to check if servers are alive
- **APIs**: Cloud providers (AWS, GCP, Azure) are controlled via REST APIs
- **Monitoring**: Tools like Prometheus expose metrics via HTTP endpoints
- **CI/CD**: Jenkins, GitHub Actions, GitLab CI all have HTTP APIs
- **Troubleshooting**: Understanding status codes helps debug deployment issues
- **Webhooks**: Events trigger HTTP POST requests to notify other services

Understanding HTTP is the foundation for everything in the next few days.
