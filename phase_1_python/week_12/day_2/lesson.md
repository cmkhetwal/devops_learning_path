# Week 12, Day 2: Flask Basics for DevOps

## What You'll Learn

- Flask web framework fundamentals
- Creating routes and handling HTTP methods
- Returning JSON responses for APIs
- Building health check and status endpoints
- Creating a simple DevOps dashboard API

## Why This Matters for DevOps

Flask is a lightweight Python web framework perfect for building:
- Health check endpoints for load balancers
- Internal DevOps dashboards and tools
- Webhook receivers for CI/CD pipelines
- API wrappers around scripts and automation tools

---

## 1. Installing Flask

```bash
pip install flask
```

## 2. Minimal Flask Application

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, DevOps!"

if __name__ == "__main__":
    app.run(debug=True, port=5000)
```

## 3. Routes and Methods

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/api/servers", methods=["GET"])
def list_servers():
    servers = [
        {"name": "web-01", "status": "healthy"},
        {"name": "web-02", "status": "healthy"},
    ]
    return jsonify({"servers": servers})

@app.route("/api/servers/<name>", methods=["GET"])
def get_server(name):
    return jsonify({"name": name, "status": "healthy"})

@app.route("/api/servers", methods=["POST"])
def add_server():
    data = request.get_json()
    return jsonify({"message": f"Server {data['name']} added"}), 201
```

## 4. Health Check Endpoint

Every production service needs a health check:

```python
import time

start_time = time.time()

@app.route("/health")
def health():
    uptime = time.time() - start_time
    return jsonify({
        "status": "healthy",
        "uptime_seconds": round(uptime, 2),
        "version": "1.0.0",
    })

@app.route("/ready")
def readiness():
    """Kubernetes readiness probe."""
    # Check database connection, etc.
    checks = {
        "database": True,
        "cache": True,
    }
    all_ok = all(checks.values())
    status_code = 200 if all_ok else 503
    return jsonify({
        "ready": all_ok,
        "checks": checks
    }), status_code
```

## 5. JSON Request/Response

```python
from flask import Flask, request, jsonify

@app.route("/api/deploy", methods=["POST"])
def deploy():
    data = request.get_json()

    app_name = data.get("app")
    version = data.get("version")
    environment = data.get("environment")

    if not all([app_name, version, environment]):
        return jsonify({"error": "Missing required fields"}), 400

    # Simulate deployment
    result = {
        "status": "deployed",
        "app": app_name,
        "version": version,
        "environment": environment,
    }
    return jsonify(result), 200
```

## 6. Error Handling

```python
from flask import Flask, jsonify

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500
```

## 7. Request Object

```python
@app.route("/api/search")
def search():
    # Query parameters: /api/search?q=web&limit=10
    query = request.args.get("q", "")
    limit = request.args.get("limit", 10, type=int)

    # Headers
    auth_token = request.headers.get("Authorization")

    # Method
    method = request.method

    return jsonify({"query": query, "limit": limit})
```

## 8. Blueprint for Organizing Routes

```python
from flask import Blueprint, jsonify

# Create a blueprint
api = Blueprint("api", __name__, url_prefix="/api")

@api.route("/servers")
def list_servers():
    return jsonify({"servers": []})

@api.route("/deployments")
def list_deployments():
    return jsonify({"deployments": []})

# Register blueprint in main app
app = Flask(__name__)
app.register_blueprint(api)
```

## 9. Testing Flask Applications

```python
import pytest

def test_health_endpoint():
    app.config["TESTING"] = True
    client = app.test_client()

    response = client.get("/health")
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "healthy"

def test_deploy_endpoint():
    client = app.test_client()

    response = client.post("/api/deploy",
        json={"app": "web", "version": "1.0", "environment": "staging"})
    assert response.status_code == 200
    assert response.get_json()["status"] == "deployed"
```

## DevOps Connection

Flask in DevOps is used for:
- **Service health checks**: `/health` and `/ready` endpoints for k8s probes
- **Internal tools**: Build dashboards for deployment status, logs, metrics
- **Webhook receivers**: Listen for GitHub/GitLab webhooks
- **API gateways**: Lightweight proxies and routers
- **ChatOps backends**: Receive Slack/Teams commands and trigger automation

---

## Key Takeaways

| Concept | Code |
|---------|------|
| Create app | `app = Flask(__name__)` |
| Define route | `@app.route("/path")` |
| JSON response | `return jsonify(data)` |
| Get JSON body | `request.get_json()` |
| Query params | `request.args.get("key")` |
| Status code | `return jsonify(data), 201` |
| Test client | `app.test_client()` |
| Run | `app.run(port=5000)` |
