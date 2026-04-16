"""
Week 12, Day 2: Check - DevOps Dashboard API
Verifies all 6 tasks from exercise.py
"""

import subprocess
import sys

def run_test(test_code):
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    score = 0
    total = 6

    # Task 1: Request
    print("Task 1: Request class")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import Request

r = Request("get", "/api/servers", body={"key": "val"}, headers={"Auth": "token"}, query_params={"limit": "10"})
assert r.method == "GET", f"Method should be uppercase: {r.method}"
assert r.path == "/api/servers"
assert r.get_json() == {"key": "val"}
assert r.headers == {"Auth": "token"}
assert r.args == {"limit": "10"} or r.query_params == {"limit": "10"}
assert "GET" in repr(r) and "/api/servers" in repr(r)

r2 = Request("POST", "/test")
assert r2.get_json() == {}
assert r2.headers == {} or r2.headers is not None
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: Response
    print("Task 2: Response class")
    code = '''
import sys; sys.path.insert(0, ".")
import json
from exercise import Response

r = Response({"status": "ok"}, 200)
assert r.status_code == 200
assert r.get_json() == {"status": "ok"}
assert r.is_success() == True
j = r.to_json_string()
assert json.loads(j) == {"status": "ok"}

r2 = Response({"error": "bad"}, 400)
assert r2.is_success() == False

r3 = Response(None, 204)
assert r3.to_json_string() == "{}"
assert r3.is_success() == True

r4 = Response({"x": "y"}, 201)
assert r4.is_success() == True
assert "Content-Type" in r4.headers or "content-type" in str(r4.headers).lower()
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: Router
    print("Task 3: Router class")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import Router, Request, Response

router = Router()

@router.route("/api/test", methods=["GET"])
def test_get(req):
    return Response({"method": "GET"})

@router.route("/api/test", methods=["POST"])
def test_post(req):
    return Response({"method": "POST"}, 201)

@router.route("/api/other")
def other(req):
    return Response({"other": True})

# GET match
resp = router.handle(Request("GET", "/api/test"))
assert resp.status_code == 200
assert resp.get_json()["method"] == "GET"

# POST match
resp2 = router.handle(Request("POST", "/api/test"))
assert resp2.status_code == 201

# Default method is GET
resp3 = router.handle(Request("GET", "/api/other"))
assert resp3.status_code == 200

# 404 - not found
resp4 = router.handle(Request("GET", "/api/nonexistent"))
assert resp4.status_code == 404

# 405 - method not allowed
resp5 = router.handle(Request("DELETE", "/api/test"))
assert resp5.status_code == 405
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: DevOpsAPI
    print("Task 4: DevOpsAPI - core endpoints")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import DevOpsAPI, Request

api = DevOpsAPI()

# GET /api/servers
resp = api.process(Request("GET", "/api/servers"))
assert resp.status_code == 200
data = resp.get_json()
assert "servers" in data
assert data["count"] == 4

# GET /api/deployments
resp2 = api.process(Request("GET", "/api/deployments"))
data2 = resp2.get_json()
assert "deployments" in data2
assert data2["count"] == 3

# POST /api/deployments - success
resp3 = api.process(Request("POST", "/api/deployments",
    body={"app": "test", "version": "1.0", "env": "staging"}))
assert resp3.status_code == 201
data3 = resp3.get_json()
assert "deployment" in data3 or "message" in data3

# POST /api/deployments - missing fields
resp4 = api.process(Request("POST", "/api/deployments", body={"app": "test"}))
assert resp4.status_code == 400

# GET /api/status
resp5 = api.process(Request("GET", "/api/status"))
data5 = resp5.get_json()
assert data5["total_servers"] == 4
assert data5["healthy_servers"] == 3  # cache-01 is degraded
assert data5["successful_deployments"] == 2
assert data5["failed_deployments"] == 1
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: Health checks
    print("Task 5: Health and readiness endpoints")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import DevOpsAPI, Request

api = DevOpsAPI()

# GET /health
resp = api.process(Request("GET", "/health"))
assert resp.status_code == 200
data = resp.get_json()
assert data["status"] == "healthy"
assert "uptime_seconds" in data
assert data["version"] == "1.0.0"

# GET /ready - should be not ready (cache-01 is degraded)
resp2 = api.process(Request("GET", "/ready"))
data2 = resp2.get_json()
assert data2["ready"] == False, f"Should not be ready: {data2}"
assert resp2.status_code == 503, f"Should be 503: {resp2.status_code}"
assert "cache-01" in data2.get("unhealthy_servers", []), f"Should list cache-01: {data2}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 6: run_simulation
    print("Task 6: run_simulation()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import DevOpsAPI, Request, run_simulation

api = DevOpsAPI()
reqs = [
    Request("GET", "/health"),
    Request("GET", "/api/servers"),
    Request("GET", "/api/nonexistent"),
    Request("POST", "/api/deployments", body={"app": "x", "version": "1", "env": "s"}),
]
results = run_simulation(api, reqs)
assert isinstance(results, list)
assert len(results) == 4

assert results[0]["status_code"] == 200
assert results[0]["success"] == True
assert results[0]["request"] == "GET /health"

assert results[2]["status_code"] == 404
assert results[2]["success"] == False

assert results[3]["status_code"] == 201
assert results[3]["success"] == True
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    print(f"\n{'='*40}")
    print(f"  Score: {score}/{total}")
    if score == total:
        print("  PERFECT! Flask API concepts mastered!")
    elif score >= 4:
        print("  Great work! Review failed tasks.")
    else:
        print("  Keep practicing with the lesson.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
