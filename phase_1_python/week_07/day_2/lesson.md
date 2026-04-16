# Week 7, Day 2: The requests Library

## What You'll Learn
- Installing and importing the `requests` library
- Making GET and POST requests
- Handling responses: status codes, JSON, text
- Setting headers, timeouts, and query parameters
- Real-world API interaction patterns

## Installing requests

```bash
pip install requests
```

The `requests` library is the most popular HTTP library in Python. It makes
HTTP calls simple and readable.

## Making GET Requests

```python
import requests

# Simple GET request
response = requests.get("https://httpbin.org/get")

# Check status code
print(response.status_code)  # 200

# Get response body as text
print(response.text)  # Raw text

# Get response body as JSON (parsed into a Python dict)
data = response.json()
print(data)

# Get response headers
print(response.headers)
print(response.headers["Content-Type"])  # application/json
```

## Making POST Requests

```python
import requests

# POST with JSON body
payload = {
    "name": "web-server-01",
    "region": "us-east-1"
}

response = requests.post(
    "https://httpbin.org/post",
    json=payload  # Automatically sets Content-Type to application/json
)

print(response.status_code)  # 200
data = response.json()
print(data["json"])  # Shows the data we sent
```

## All HTTP Methods

```python
import requests

# GET - Read
response = requests.get("https://httpbin.org/get")

# POST - Create
response = requests.post("https://httpbin.org/post", json={"key": "value"})

# PUT - Update
response = requests.put("https://httpbin.org/put", json={"key": "new_value"})

# DELETE - Delete
response = requests.delete("https://httpbin.org/delete")

# PATCH - Partial update
response = requests.patch("https://httpbin.org/patch", json={"key": "partial"})
```

## Setting Headers

```python
import requests

headers = {
    "Authorization": "Bearer my-api-token",
    "Accept": "application/json",
    "User-Agent": "DevOpsBot/1.0"
}

response = requests.get(
    "https://httpbin.org/headers",
    headers=headers
)

print(response.json())
```

## Query Parameters

```python
import requests

# Instead of building URL strings manually:
# requests.get("https://api.example.com/search?q=python&page=1")

# Use params - cleaner and handles encoding
params = {
    "q": "python",
    "page": 1,
    "limit": 10
}

response = requests.get(
    "https://httpbin.org/get",
    params=params
)

# The URL becomes: https://httpbin.org/get?q=python&page=1&limit=10
print(response.url)
```

## Timeouts (Critical for DevOps!)

```python
import requests

# ALWAYS set a timeout in production code!
# Without a timeout, your script can hang forever

try:
    response = requests.get(
        "https://httpbin.org/delay/5",
        timeout=3  # Wait max 3 seconds
    )
except requests.exceptions.Timeout:
    print("Request timed out!")
except requests.exceptions.ConnectionError:
    print("Could not connect to server!")
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
```

## The Response Object

```python
import requests

response = requests.get("https://httpbin.org/get")

# Key attributes:
print(response.status_code)    # 200 (int)
print(response.text)           # Raw response body (str)
print(response.json())         # Parsed JSON (dict/list)
print(response.headers)        # Response headers (dict-like)
print(response.url)            # Final URL (after redirects)
print(response.elapsed)        # Time the request took
print(response.ok)             # True if status_code < 400

# Check if request was successful
if response.ok:
    data = response.json()
    print("Success!", data)
else:
    print(f"Error: {response.status_code}")

# Or raise an exception on bad status codes
response.raise_for_status()  # Raises HTTPError if status >= 400
```

## Sessions (Reuse Connections)

```python
import requests

# A Session reuses connections and persists settings
session = requests.Session()
session.headers.update({
    "Authorization": "Bearer my-token",
    "User-Agent": "DevOpsBot/1.0"
})

# All requests through this session include those headers
response1 = session.get("https://httpbin.org/get")
response2 = session.get("https://httpbin.org/headers")

session.close()
```

## Practical Example: Health Check

```python
import requests

def check_service_health(url, timeout=5):
    """Check if a service is healthy."""
    try:
        response = requests.get(url, timeout=timeout)
        return {
            "url": url,
            "status": response.status_code,
            "healthy": response.ok,
            "response_time_ms": response.elapsed.total_seconds() * 1000
        }
    except requests.exceptions.Timeout:
        return {"url": url, "status": None, "healthy": False, "error": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"url": url, "status": None, "healthy": False, "error": "connection_failed"}

# Check multiple services
services = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/10",
]

for service in services:
    result = check_service_health(service, timeout=3)
    status = "HEALTHY" if result["healthy"] else "UNHEALTHY"
    print(f"[{status}] {result['url']} - {result.get('status', 'N/A')}")
```

## DevOps Connection

The `requests` library is your primary tool for:
- **Health checks**: Monitor if services are responding
- **API automation**: Create/manage cloud resources programmatically
- **Webhook handlers**: Send notifications to Slack, PagerDuty, etc.
- **CI/CD integration**: Trigger builds, check pipeline status
- **Monitoring**: Collect metrics from HTTP endpoints
- **Configuration**: Pull configs from remote services

Always remember: **set timeouts** and **handle exceptions** in production code!
