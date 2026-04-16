"""
Week 12, Day 2: Exercise - DevOps Dashboard API (Simulated)

Build a simulated REST API using classes and functions. No Flask
installation needed -- you'll build the request/response handling
logic that mirrors how a Flask app works.

TASKS:
    1. Request class          - Simulates an HTTP request
    2. Response class         - Simulates an HTTP response
    3. Router class           - Routes requests to handlers
    4. DevOpsAPI class        - Complete API with DevOps endpoints
    5. Health check endpoints - /health and /ready
    6. Run simulation         - Process a list of requests
"""

import json
import time


# ============================================================
# TASK 1: Request class
#
# Simulates an HTTP request.
#
# __init__(self, method, path, body=None, headers=None, query_params=None):
#   - method: "GET", "POST", "PUT", "DELETE" (store as uppercase)
#   - path: URL path string like "/api/servers"
#   - body: dict (for POST/PUT data), default None
#   - headers: dict of header key-value pairs, default {}
#   - query_params: dict of query parameters, default {}
#
# get_json(self):
#   - Return the body dict (or {} if None)
#
# args: property that returns query_params dict
#
# __repr__: "Request(GET /api/servers)"
# ============================================================

class Request:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: Response class
#
# Simulates an HTTP response.
#
# __init__(self, data=None, status_code=200, headers=None):
#   - data: any data (usually dict for JSON APIs)
#   - status_code: HTTP status code (int), default 200
#   - headers: dict, default {"Content-Type": "application/json"}
#
# get_json(self):
#   - Return the data as a dict
#
# to_json_string(self):
#   - Return data serialized as a JSON string (indent=2)
#   - If data is None, return "{}"
#
# is_success(self):
#   - Return True if status_code is 2xx (200-299)
#
# __repr__: "Response(200, {'key': 'value'})" (truncate data repr to 50 chars)
# ============================================================

class Response:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: Router class
#
# Routes requests to handler functions.
#
# __init__(self):
#   - Initialize empty routes dict:
#     {("/path", "METHOD"): handler_function}
#
# route(self, path, methods=None):
#   - A decorator factory that registers a handler.
#   - methods: list of HTTP methods, default ["GET"]
#   - Usage:
#       @router.route("/api/servers", methods=["GET"])
#       def list_servers(request):
#           return Response({"servers": []})
#
# handle(self, request):
#   - Find the matching handler for request.path and request.method
#   - If found, call it with the request and return the Response
#   - If path exists but method not allowed: return Response
#     with status 405 and {"error": "Method not allowed"}
#   - If path not found: return Response with status 404 and
#     {"error": "Not found"}
#
# Note: handle simple path matching (exact match).
#       For paths with parameters like /api/servers/<name>,
#       just do exact match -- we won't parse path params.
# ============================================================

class Router:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: DevOpsAPI class
#
# A complete API with DevOps endpoints.
#
# __init__(self):
#   - Create a Router
#   - Initialize in-memory data stores:
#     self.servers = [
#       {"name": "web-01", "ip": "10.0.1.1", "status": "healthy", "cpu": 45.2},
#       {"name": "web-02", "ip": "10.0.1.2", "status": "healthy", "cpu": 62.8},
#       {"name": "db-01", "ip": "10.0.2.1", "status": "healthy", "cpu": 30.1},
#       {"name": "cache-01", "ip": "10.0.3.1", "status": "degraded", "cpu": 88.5},
#     ]
#     self.deployments = [
#       {"app": "web-api", "version": "2.1.0", "env": "production",
#        "status": "success", "timestamp": "2025-01-15T14:30:00"},
#       {"app": "worker", "version": "1.5.2", "env": "production",
#        "status": "success", "timestamp": "2025-01-15T10:00:00"},
#       {"app": "web-api", "version": "2.1.1", "env": "staging",
#        "status": "failed", "timestamp": "2025-01-15T16:00:00"},
#     ]
#     self.start_time = time.time()
#   - Register these routes:
#
#   GET /api/servers -> list all servers
#     Response: {"servers": self.servers, "count": len}
#
#   GET /api/deployments -> list all deployments
#     Response: {"deployments": self.deployments, "count": len}
#
#   POST /api/deployments -> add a deployment
#     Body should have: app, version, env
#     Add to self.deployments with status="pending" and current timestamp
#     Response(201): {"message": "Deployment queued", "deployment": new_entry}
#     If missing fields: Response(400): {"error": "Missing required fields: app, version, env"}
#
#   GET /api/status -> overall system status
#     Response: {
#       "total_servers": count,
#       "healthy_servers": count of status=="healthy",
#       "total_deployments": count,
#       "successful_deployments": count of status=="success",
#       "failed_deployments": count of status=="failed"
#     }
#
# process(self, request):
#   - Route the request through self.router and return Response
# ============================================================

class DevOpsAPI:
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: Add health check methods to DevOpsAPI
#
# Register two additional routes in __init__:
#
# GET /health -> health check
#   Response: {
#     "status": "healthy",
#     "uptime_seconds": round(time.time() - self.start_time, 2),
#     "version": "1.0.0"
#   }
#
# GET /ready -> readiness check
#   Check if any server is not "healthy".
#   If all healthy:
#     Response(200): {"ready": True, "checks": {"servers": True, "deployments": True}}
#   If any NOT healthy:
#     Response(503): {"ready": False, "checks": {"servers": False, "deployments": True},
#                     "unhealthy_servers": [list of unhealthy server names]}
#
# NOTE: Integrate this into the DevOpsAPI.__init__ method above.
#       This is listed separately for clarity, but should be part
#       of the same class.
# ============================================================


# ============================================================
# TASK 6: run_simulation(api, requests_list)
#
# Process a list of Request objects through the API and return
# a list of result dicts:
#
# [
#   {
#     "request": "GET /api/servers",
#     "status_code": 200,
#     "success": True,
#     "response_data": {response data dict}
#   },
#   ...
# ]
#
# Also print a summary at the end:
#   "Processed X requests: Y successful, Z failed"
#
# Return the results list.
# ============================================================

def run_simulation(api, requests_list):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    api = DevOpsAPI()

    requests_to_test = [
        Request("GET", "/health"),
        Request("GET", "/ready"),
        Request("GET", "/api/servers"),
        Request("GET", "/api/deployments"),
        Request("GET", "/api/status"),
        Request("POST", "/api/deployments",
                body={"app": "new-service", "version": "1.0.0", "env": "staging"}),
        Request("POST", "/api/deployments", body={"app": "incomplete"}),
        Request("GET", "/api/nonexistent"),
        Request("DELETE", "/api/servers"),
    ]

    results = run_simulation(api, requests_to_test)
    if results:
        print("\n=== Results ===")
        for r in results:
            print(f"  {r['request']}: {r['status_code']} ({'OK' if r['success'] else 'FAIL'})")
