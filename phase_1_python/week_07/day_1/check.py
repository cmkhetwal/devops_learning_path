#!/usr/bin/env python3
"""
Week 7, Day 1: HTTP Basics - Auto-Checker
Validates exercise.py solutions.
"""

import subprocess
import sys

def run_test(test_name, test_func):
    """Run a single test and return pass/fail."""
    try:
        result = test_func()
        if result:
            print(f"  PASS: {test_name}")
            return True
        else:
            print(f"  FAIL: {test_name}")
            return False
    except Exception as e:
        print(f"  FAIL: {test_name} - {e}")
        return False

def main():
    # Import the exercise module
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_07/day_1")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 7, Day 1: HTTP Basics - Checking Solutions")
    print("=" * 50)

    # TASK 1: classify_status
    print("\nTask 1: Status Code Classifier")
    t1_pass = True
    tests_1 = [
        (200, "2xx Success: OK"),
        (201, "2xx Success: Created"),
        (301, "3xx Redirection: Moved Permanently"),
        (400, "4xx Client Error: Bad Request"),
        (401, "4xx Client Error: Unauthorized"),
        (403, "4xx Client Error: Forbidden"),
        (404, "4xx Client Error: Not Found"),
        (500, "5xx Server Error: Internal Server Error"),
        (502, "5xx Server Error: Bad Gateway"),
        (503, "5xx Server Error: Service Unavailable"),
        (999, "Unknown Status Code"),
    ]
    for code, expected in tests_1:
        result = exercise.classify_status(code)
        if result != expected:
            print(f"  FAIL: classify_status({code}) returned {repr(result)}, expected {repr(expected)}")
            t1_pass = False
    if t1_pass:
        print("  PASS: All status codes classified correctly")
        score += 1

    # TASK 2: get_method
    print("\nTask 2: Method Matcher")
    t2_pass = True
    tests_2 = [
        ("read", "GET"), ("create", "POST"), ("update", "PUT"),
        ("delete", "DELETE"), ("list", "GET"), ("fetch", "GET"),
        ("remove", "DELETE"), ("add", "POST"), ("modify", "PUT"),
        ("READ", "GET"), ("Create", "POST"), ("unknown_action", "UNKNOWN"),
    ]
    for action, expected in tests_2:
        result = exercise.get_method(action)
        if result != expected:
            print(f"  FAIL: get_method({repr(action)}) returned {repr(result)}, expected {repr(expected)}")
            t2_pass = False
    if t2_pass:
        print("  PASS: All methods matched correctly")
        score += 1

    # TASK 3: build_request
    print("\nTask 3: Build a Request Dictionary")
    t3_pass = True

    r1 = exercise.build_request("GET", "https://api.example.com/servers")
    if r1 is None:
        print("  FAIL: build_request returned None")
        t3_pass = False
    else:
        if r1.get("method") != "GET":
            print(f"  FAIL: method should be 'GET', got {repr(r1.get('method'))}")
            t3_pass = False
        if r1.get("url") != "https://api.example.com/servers":
            print(f"  FAIL: url mismatch")
            t3_pass = False
        if r1.get("headers", {}).get("Content-Type") != "application/json":
            print(f"  FAIL: Content-Type header missing")
            t3_pass = False
        if r1.get("body") is not None:
            print(f"  FAIL: body should be None for basic GET")
            t3_pass = False

    r2 = exercise.build_request("POST", "https://api.example.com/servers",
                                 headers={"Authorization": "Bearer token123"},
                                 body={"name": "web-01"})
    if r2 is not None:
        if r2.get("headers", {}).get("Authorization") != "Bearer token123":
            print(f"  FAIL: Authorization header not merged")
            t3_pass = False
        if r2.get("headers", {}).get("Content-Type") != "application/json":
            print(f"  FAIL: Content-Type missing after merge")
            t3_pass = False
        if r2.get("body") != {"name": "web-01"}:
            print(f"  FAIL: body mismatch")
            t3_pass = False

    if t3_pass:
        print("  PASS: Request dictionaries built correctly")
        score += 1

    # TASK 4: parse_response
    print("\nTask 4: Parse a Response")
    t4_pass = True

    resp1 = exercise.parse_response({
        "status_code": 200,
        "headers": {"Content-Type": "application/json"},
        "body": {"id": 1}
    })
    expected1 = "Status: 200 | Content-Type: application/json | Has Body: yes"
    if resp1 != expected1:
        print(f"  FAIL: Got {repr(resp1)}, expected {repr(expected1)}")
        t4_pass = False

    resp2 = exercise.parse_response({
        "status_code": 404,
        "headers": {},
        "body": None
    })
    expected2 = "Status: 404 | Content-Type: unknown | Has Body: no"
    if resp2 != expected2:
        print(f"  FAIL: Got {repr(resp2)}, expected {repr(expected2)}")
        t4_pass = False

    if t4_pass:
        print("  PASS: Response parsing correct")
        score += 1

    # TASK 5: build_endpoint
    print("\nTask 5: Endpoint Builder")
    t5_pass = True
    tests_5 = [
        (("https://api.example.com", "servers"), {},
         "https://api.example.com/servers"),
        (("https://api.example.com/", "servers", 42), {},
         "https://api.example.com/servers/42"),
        (("https://api.example.com", "servers"), {"resource_id": 42, "action": "restart"},
         "https://api.example.com/servers/42/restart"),
    ]
    for args, kwargs, expected in tests_5:
        result = exercise.build_endpoint(*args, **kwargs)
        if result != expected:
            print(f"  FAIL: build_endpoint{args} returned {repr(result)}, expected {repr(expected)}")
            t5_pass = False
    if t5_pass:
        print("  PASS: Endpoints built correctly")
        score += 1

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You understand HTTP fundamentals!")
    elif score >= 3:
        print("Good progress! Review the tasks you missed.")
    else:
        print("Keep practicing! Re-read the lesson and try again.")
    print("=" * 50)

if __name__ == "__main__":
    main()
