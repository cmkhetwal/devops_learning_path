#!/usr/bin/env python3
"""
Week 7, Day 6: Practice Day - Auto-Checker
Validates the 5 mini-project solutions.
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_07/day_6")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 7, Day 6: Practice Day - Checking Solutions")
    print("=" * 50)
    print()

    # PROJECT 1: API Health Checker
    print("Project 1: API Health Checker")
    try:
        endpoints = [
            {"name": "Posts", "url": "https://jsonplaceholder.typicode.com/posts/1"},
            {"name": "Bad", "url": "https://httpbin.org/status/500"},
        ]
        result = exercise.check_api_health(endpoints, timeout=10)
        if result is None:
            print("  FAIL: Returned None")
        else:
            t_pass = True
            if result.get("total") != 2:
                print(f"  FAIL: total should be 2")
                t_pass = False
            if result.get("healthy") != 1:
                print(f"  FAIL: healthy should be 1, got {result.get('healthy')}")
                t_pass = False
            if result.get("unhealthy") != 1:
                print(f"  FAIL: unhealthy should be 1, got {result.get('unhealthy')}")
                t_pass = False
            if not isinstance(result.get("results"), list) or len(result.get("results", [])) != 2:
                print(f"  FAIL: results should be list of 2")
                t_pass = False
            else:
                r0 = result["results"][0]
                if r0.get("healthy") is not True:
                    print(f"  FAIL: Posts endpoint should be healthy")
                    t_pass = False
                if not isinstance(r0.get("response_time_ms"), float):
                    print(f"  FAIL: response_time_ms should be float")
                    t_pass = False
            if t_pass:
                print("  PASS: API health checker works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 2: Port Scanner
    print("\nProject 2: Port Scanner")
    try:
        result = exercise.port_scanner("google.com", [80, 443, 12345], timeout=3)
        if result is None:
            print("  FAIL: Returned None")
        else:
            t_pass = True
            if result.get("host") != "google.com":
                print(f"  FAIL: host mismatch")
                t_pass = False
            if not isinstance(result.get("open_services"), list):
                print(f"  FAIL: open_services should be a list")
                t_pass = False
            if not isinstance(result.get("all_results"), dict):
                print(f"  FAIL: all_results should be a dict")
                t_pass = False
            if "scan_summary" not in result:
                print(f"  FAIL: missing scan_summary")
                t_pass = False
            # Check default ports work
            result2 = exercise.port_scanner("google.com", timeout=3)
            if result2 and len(result2.get("all_results", {})) != 9:
                print(f"  FAIL: default scan should check 9 ports")
                t_pass = False
            if t_pass:
                print("  PASS: Port scanner works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 3: REST API Client
    print("\nProject 3: REST API Client Library")
    try:
        client = exercise.DevOpsAPIClient("https://jsonplaceholder.typicode.com")
        t_pass = True

        posts = client.list("posts")
        if not isinstance(posts, list) or len(posts) != 100:
            print(f"  FAIL: list('posts') should return 100 items")
            t_pass = False

        post = client.get("posts", 1)
        if not isinstance(post, dict) or post.get("id") != 1:
            print(f"  FAIL: get('posts', 1) should return post with id=1")
            t_pass = False

        created = client.create("posts", {"title": "T", "body": "B", "userId": 1})
        if not isinstance(created, dict) or created.get("success") is not True:
            print(f"  FAIL: create should return success=True")
            t_pass = False

        updated = client.update("posts", 1, {"title": "U"})
        if not isinstance(updated, dict) or updated.get("success") is not True:
            print(f"  FAIL: update should return success=True")
            t_pass = False

        deleted = client.delete("posts", 1)
        if not isinstance(deleted, dict) or deleted.get("success") is not True:
            print(f"  FAIL: delete should return success=True")
            t_pass = False

        if t_pass:
            print("  PASS: REST API client works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 4: URL Status Checker
    print("\nProject 4: URL Status Checker")
    try:
        result = exercise.check_urls([
            "https://httpbin.org/status/200",
            "https://httpbin.org/status/404",
        ], timeout=10)
        if result is None:
            print("  FAIL: Returned None")
        else:
            t_pass = True
            if result.get("checked") != 2:
                print(f"  FAIL: checked should be 2")
                t_pass = False
            cats = result.get("categories", {})
            if not isinstance(cats, dict):
                print(f"  FAIL: categories should be a dict")
                t_pass = False
            else:
                for cat in ["success", "redirect", "client_error", "server_error", "unreachable"]:
                    if cat not in cats:
                        print(f"  FAIL: missing category '{cat}'")
                        t_pass = False
                if "https://httpbin.org/status/200" not in cats.get("success", []):
                    print(f"  FAIL: 200 URL should be in 'success'")
                    t_pass = False
                if "https://httpbin.org/status/404" not in cats.get("client_error", []):
                    print(f"  FAIL: 404 URL should be in 'client_error'")
                    t_pass = False
            if not isinstance(result.get("details"), list) or len(result.get("details", [])) != 2:
                print(f"  FAIL: details should have 2 items")
                t_pass = False
            if t_pass:
                print("  PASS: URL status checker works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 5: Server Dashboard
    print("\nProject 5: Multi-Server Status Dashboard")
    try:
        mock_servers = [
            exercise.MockServer("web-01", "running", 35.0, 4096),
            exercise.MockServer("web-02", "running", 85.0, 4096),
            exercise.MockServer("db-01", "stopped", 0.0, 0),
            exercise.MockServer("cache-01", "running", 20.0, 7500),
        ]
        result = exercise.server_dashboard(mock_servers)
        if result is None:
            print("  FAIL: Returned None")
        else:
            t_pass = True
            if result.get("total_servers") != 4:
                print(f"  FAIL: total_servers should be 4")
                t_pass = False
            if result.get("servers_up") != 3:
                print(f"  FAIL: servers_up should be 3, got {result.get('servers_up')}")
                t_pass = False
            if result.get("servers_down") != 1:
                print(f"  FAIL: servers_down should be 1")
                t_pass = False
            expected_cpu = 35.0 + 85.0 + 0.0 + 20.0
            if result.get("total_cpu_percent") != expected_cpu:
                print(f"  FAIL: total_cpu should be {expected_cpu}")
                t_pass = False
            if result.get("avg_cpu_percent") != round(expected_cpu / 4, 1):
                print(f"  FAIL: avg_cpu should be {round(expected_cpu/4, 1)}")
                t_pass = False
            expected_mem = 4096 + 4096 + 0 + 7500
            if result.get("total_memory_mb") != expected_mem:
                print(f"  FAIL: total_memory should be {expected_mem}")
                t_pass = False
            alerts = result.get("alerts", [])
            if not any("db-01" in a and "DOWN" in a for a in alerts):
                print(f"  FAIL: Missing DOWN alert for db-01")
                t_pass = False
            if not any("web-02" in a and "CPU" in a for a in alerts):
                print(f"  FAIL: Missing CPU alert for web-02")
                t_pass = False
            if not any("cache-01" in a and "memory" in a for a in alerts):
                print(f"  FAIL: Missing memory alert for cache-01")
                t_pass = False
            if t_pass:
                print("  PASS: Server dashboard works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} projects passed")
    if score == total:
        print("PERFECT! All networking projects complete!")
    elif score >= 3:
        print("Good progress! Review the failed projects.")
    else:
        print("Keep at it! Practice makes perfect.")
    print("=" * 50)

if __name__ == "__main__":
    main()
