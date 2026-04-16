# Week 7, Day 3: REST APIs

## What You'll Learn
- What REST is and why it matters
- CRUD operations mapped to HTTP methods
- API endpoints and URL structure
- Authentication: API keys, Bearer tokens
- Pagination: handling large datasets
- Building a proper API client

## What is REST?

REST (Representational State Transfer) is an architectural style for APIs.
Almost every cloud service, DevOps tool, and modern application uses REST APIs.

### REST Principles
```
1. Resources have URLs    -> /api/servers, /api/users/42
2. Use HTTP methods       -> GET, POST, PUT, DELETE
3. Stateless              -> Each request is independent
4. JSON format            -> Standard data exchange format
5. Status codes matter    -> 200 OK, 404 Not Found, etc.
```

## CRUD Operations

CRUD maps directly to HTTP methods:

```python
# CRUD = Create, Read, Update, Delete
#
# Create -> POST   /api/servers         (create new server)
# Read   -> GET    /api/servers         (list all servers)
# Read   -> GET    /api/servers/42      (get one server)
# Update -> PUT    /api/servers/42      (update a server)
# Delete -> DELETE /api/servers/42      (delete a server)
```

## API Endpoint Patterns

```python
# Standard REST URL patterns:
# /api/v1/resources              -> Collection (list/create)
# /api/v1/resources/:id          -> Single resource (read/update/delete)
# /api/v1/resources/:id/action   -> Action on a resource
# /api/v1/resources/:id/children -> Nested resources

# Real-world examples:
# GET    /api/v1/servers                 -> List servers
# POST   /api/v1/servers                 -> Create server
# GET    /api/v1/servers/42              -> Get server 42
# PUT    /api/v1/servers/42              -> Update server 42
# DELETE /api/v1/servers/42              -> Delete server 42
# POST   /api/v1/servers/42/restart      -> Restart server 42
# GET    /api/v1/servers/42/logs         -> Get server 42 logs
```

## Working with jsonplaceholder API

jsonplaceholder.typicode.com is a free fake REST API for testing:

```python
import requests

BASE_URL = "https://jsonplaceholder.typicode.com"

# === CREATE (POST) ===
new_post = {
    "title": "Deploy Update",
    "body": "Deployed version 2.1 to production",
    "userId": 1
}
response = requests.post(f"{BASE_URL}/posts", json=new_post, timeout=10)
print(response.status_code)  # 201
print(response.json())       # {"id": 101, "title": "Deploy Update", ...}

# === READ (GET) ===
# List all
response = requests.get(f"{BASE_URL}/posts", timeout=10)
posts = response.json()
print(f"Total posts: {len(posts)}")  # 100

# Get one
response = requests.get(f"{BASE_URL}/posts/1", timeout=10)
post = response.json()
print(post["title"])

# === UPDATE (PUT) ===
updated = {"title": "Updated Title", "body": "Updated body", "userId": 1}
response = requests.put(f"{BASE_URL}/posts/1", json=updated, timeout=10)
print(response.json())

# === DELETE ===
response = requests.delete(f"{BASE_URL}/posts/1", timeout=10)
print(response.status_code)  # 200
```

## Authentication

Most real APIs require authentication:

### API Key (in headers or query params)
```python
import requests

# API key in header
headers = {"X-API-Key": "your-api-key-here"}
response = requests.get("https://api.example.com/data",
                        headers=headers, timeout=10)

# API key in query parameter
params = {"api_key": "your-api-key-here"}
response = requests.get("https://api.example.com/data",
                        params=params, timeout=10)
```

### Bearer Token (OAuth, JWT)
```python
import requests

token = "your-jwt-token-here"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("https://api.example.com/data",
                        headers=headers, timeout=10)
```

### Using a Session for Auth
```python
import requests

session = requests.Session()
session.headers.update({
    "Authorization": "Bearer my-token",
    "Content-Type": "application/json"
})

# All requests now include auth
users = session.get("https://api.example.com/users", timeout=10)
servers = session.get("https://api.example.com/servers", timeout=10)
```

## Pagination

APIs return data in pages when there are many results:

```python
import requests

def get_all_items(base_url, per_page=20):
    """Fetch all items using pagination."""
    all_items = []
    page = 1

    while True:
        response = requests.get(
            base_url,
            params={"_page": page, "_limit": per_page},
            timeout=10
        )

        items = response.json()
        if not items:  # Empty page means we're done
            break

        all_items.extend(items)
        page += 1

    return all_items

# Fetch all posts in pages of 10
posts = get_all_items("https://jsonplaceholder.typicode.com/posts", per_page=10)
print(f"Fetched {len(posts)} posts")
```

## Building an API Client Class

```python
import requests

class APIClient:
    """A reusable REST API client."""

    def __init__(self, base_url, api_key=None, timeout=10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if api_key:
            self.session.headers["Authorization"] = f"Bearer {api_key}"
        self.session.headers["Content-Type"] = "application/json"

    def _url(self, endpoint):
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None):
        response = self.session.get(
            self._url(endpoint), params=params, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data):
        response = self.session.post(
            self._url(endpoint), json=data, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def put(self, endpoint, data):
        response = self.session.put(
            self._url(endpoint), json=data, timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def delete(self, endpoint):
        response = self.session.delete(
            self._url(endpoint), timeout=self.timeout
        )
        response.raise_for_status()
        return response.status_code

# Usage:
client = APIClient("https://jsonplaceholder.typicode.com")
posts = client.get("/posts", params={"userId": 1})
new_post = client.post("/posts", {"title": "New", "body": "Content", "userId": 1})
```

## Error Handling Pattern

```python
import requests

def safe_api_call(method, url, **kwargs):
    """Make an API call with proper error handling."""
    try:
        response = method(url, timeout=10, **kwargs)
        response.raise_for_status()
        return {"success": True, "data": response.json(), "status": response.status_code}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out", "status": None}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection failed", "status": None}
    except requests.exceptions.HTTPError as e:
        return {"success": False, "error": str(e), "status": e.response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e), "status": None}
```

## DevOps Connection

REST APIs are everywhere in DevOps:
- **AWS/GCP/Azure**: All cloud providers are controlled via REST APIs
- **Kubernetes**: The API server is a REST API
- **GitHub/GitLab**: Manage repos, PRs, issues via REST
- **Jenkins**: Trigger builds, check status via REST
- **Terraform**: Providers translate config to REST API calls
- **Monitoring**: Grafana, Datadog, Prometheus all have REST APIs

Mastering REST API interaction is essential for DevOps automation.
