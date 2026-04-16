#!/usr/bin/env python3
"""
Week 8, Day 3: Inheritance - Auto-Checker
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_08/day_3")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 8, Day 3: Inheritance - Checking Solutions")
    print("=" * 50)
    print()

    # TASK 1: Server Hierarchy
    print("Task 1: Server Hierarchy")
    try:
        t_pass = True
        s = exercise.Server("generic-01", "10.0.0.1")
        web = exercise.WebServer("web-01", "10.0.1.10", port=8080)
        db = exercise.DatabaseServer("db-01", "10.0.2.10", engine="mysql", port=3306)

        # Inheritance check
        if not isinstance(web, exercise.Server):
            print("  FAIL: WebServer should be a Server")
            t_pass = False
        if not isinstance(db, exercise.Server):
            print("  FAIL: DatabaseServer should be a Server")
            t_pass = False

        # Base class
        if s.get_type() != "generic":
            print(f"  FAIL: Server get_type should be 'generic'")
            t_pass = False
        s.start()
        if s.status != "running":
            print(f"  FAIL: start() should set status to running")
            t_pass = False

        # WebServer
        web.start()
        web.add_site("example.com")
        info = web.get_info()
        if info.get("type") != "web":
            print(f"  FAIL: WebServer type should be 'web'")
            t_pass = False
        if info.get("port") != 8080:
            print(f"  FAIL: WebServer info missing port")
            t_pass = False
        if info.get("sites") != ["example.com"]:
            print(f"  FAIL: WebServer info missing sites")
            t_pass = False

        # DatabaseServer
        db.create_db("mydb")
        info = db.get_info()
        if info.get("type") != "database":
            print(f"  FAIL: DatabaseServer type should be 'database'")
            t_pass = False
        if info.get("engine") != "mysql":
            print(f"  FAIL: DatabaseServer info missing engine")
            t_pass = False
        if info.get("databases") != ["mydb"]:
            print(f"  FAIL: DatabaseServer info missing databases")
            t_pass = False

        # __str__
        web_str = str(web)
        if "web" not in web_str.lower() or "web-01" not in web_str:
            print(f"  FAIL: WebServer __str__ should include type and name")
            t_pass = False

        if t_pass:
            print("  PASS: Server hierarchy works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: Deployment Strategies
    print("\nTask 2: Deployment Strategies")
    try:
        t_pass = True

        d = exercise.Deployment("app", "1.0")
        if d.get_strategy() != "basic":
            print(f"  FAIL: Deployment strategy should be 'basic'")
            t_pass = False
        d.start()
        if d.status != "in_progress" or "started" not in d.steps:
            print(f"  FAIL: start() didn't work")
            t_pass = False

        r = exercise.RollingDeployment("app", "2.0", batch_size=3)
        if not isinstance(r, exercise.Deployment):
            print(f"  FAIL: RollingDeployment should inherit Deployment")
            t_pass = False
        r.start()
        r.execute_batch()
        r.execute_batch()
        if r.batches_completed != 2:
            print(f"  FAIL: batches_completed should be 2")
            t_pass = False
        if r.get_strategy() != "rolling":
            print(f"  FAIL: Strategy should be 'rolling'")
            t_pass = False
        status = r.get_status()
        if status.get("strategy") != "rolling":
            print(f"  FAIL: get_status strategy wrong")
            t_pass = False

        bg = exercise.BlueGreenDeployment("app", "2.0")
        bg.start()
        if bg.active_env != "blue":
            print(f"  FAIL: Initial env should be 'blue'")
            t_pass = False
        bg.switch()
        if bg.active_env != "green":
            print(f"  FAIL: After switch should be 'green'")
            t_pass = False
        bg.switch()
        if bg.active_env != "blue":
            print(f"  FAIL: After second switch should be 'blue'")
            t_pass = False
        if bg.get_strategy() != "blue-green":
            print(f"  FAIL: Strategy should be 'blue-green'")
            t_pass = False

        if t_pass:
            print("  PASS: Deployment strategies work correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: Monitor Hierarchy
    print("\nTask 3: Monitor Hierarchy")
    try:
        t_pass = True

        http = exercise.HTTPMonitor("web-check", "https://example.com")
        if not isinstance(http, exercise.Monitor):
            print(f"  FAIL: HTTPMonitor should inherit Monitor")
            t_pass = False
        http.simulate_check(200)
        http.simulate_check(200)
        http.simulate_check(500)
        if http.get_last_status() != "down":
            print(f"  FAIL: Last check (500) should be 'down'")
            t_pass = False
        if http.get_uptime() != round(2/3*100, 1):
            print(f"  FAIL: Uptime should be {round(2/3*100, 1)}")
            t_pass = False
        if http.get_type() != "http":
            print(f"  FAIL: HTTPMonitor type should be 'http'")
            t_pass = False
        summary = http.get_summary()
        if summary.get("total_checks") != 3:
            print(f"  FAIL: total_checks should be 3")
            t_pass = False

        tcp = exercise.TCPMonitor("db-check", "10.0.2.10", 5432)
        tcp.simulate_check(True)
        tcp.simulate_check(False)
        if tcp.get_type() != "tcp":
            print(f"  FAIL: TCPMonitor type should be 'tcp'")
            t_pass = False
        if tcp.get_last_status() != "down":
            print(f"  FAIL: Last tcp check (False) should be 'down'")
            t_pass = False

        # Base monitor
        m = exercise.Monitor("test", "target")
        if m.get_last_status() != "unknown":
            print(f"  FAIL: No checks should be 'unknown'")
            t_pass = False
        if m.get_uptime() != 0.0:
            print(f"  FAIL: No checks uptime should be 0.0")
            t_pass = False

        if t_pass:
            print("  PASS: Monitor hierarchy works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: isinstance checks
    print("\nTask 4: categorize_objects")
    try:
        t_pass = True
        web = exercise.WebServer("web-01", "10.0.1.10")
        db = exercise.DatabaseServer("db-01", "10.0.2.10")
        dep = exercise.RollingDeployment("app", "1.0")
        mon = exercise.HTTPMonitor("check", "https://ex.com")

        result = exercise.categorize_objects([web, db, dep, mon])
        if result is None:
            print("  FAIL: Returned None")
            t_pass = False
        else:
            if sorted(result.get("servers", [])) != sorted(["web-01", "db-01"]):
                print(f"  FAIL: servers should be ['web-01', 'db-01'], got {result.get('servers')}")
                t_pass = False
            if result.get("web_servers") != ["web-01"]:
                print(f"  FAIL: web_servers should be ['web-01']")
                t_pass = False
            if result.get("database_servers") != ["db-01"]:
                print(f"  FAIL: database_servers should be ['db-01']")
                t_pass = False
            if result.get("deployments") != ["app"]:
                print(f"  FAIL: deployments should be ['app']")
                t_pass = False
            if result.get("monitors") != ["check"]:
                print(f"  FAIL: monitors should be ['check']")
                t_pass = False
            if result.get("total") != 4:
                print(f"  FAIL: total should be 4")
                t_pass = False
        if t_pass:
            print("  PASS: categorize_objects works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: InfrastructureManager
    print("\nTask 5: Infrastructure Manager")
    try:
        t_pass = True
        mgr = exercise.InfrastructureManager()
        w1 = exercise.WebServer("web-01", "10.0.1.10")
        w2 = exercise.WebServer("web-02", "10.0.1.11")
        d1 = exercise.DatabaseServer("db-01", "10.0.2.10")

        mgr.add_server(w1)
        mgr.add_server(w2)
        r = mgr.add_server(d1)
        if "db-01" not in r or "database" not in r:
            print(f"  FAIL: add_server should return name and type")
            t_pass = False

        results = mgr.start_all()
        if len(results) != 3:
            print(f"  FAIL: start_all should return 3 results")
            t_pass = False
        if w1.status != "running":
            print(f"  FAIL: start_all should set all to running")
            t_pass = False

        web_servers = mgr.get_by_type("web")
        if len(web_servers) != 2:
            print(f"  FAIL: get_by_type('web') should return 2")
            t_pass = False

        report = mgr.get_status_report()
        if report.get("total") != 3:
            print(f"  FAIL: total should be 3")
            t_pass = False
        if report.get("running") != 3:
            print(f"  FAIL: running should be 3")
            t_pass = False
        by_type = report.get("by_type", {})
        if by_type.get("web") != 2 or by_type.get("database") != 1:
            print(f"  FAIL: by_type wrong: {by_type}")
            t_pass = False

        found = mgr.find_server("web-01")
        if found is None or found.name != "web-01":
            print(f"  FAIL: find_server should find web-01")
            t_pass = False
        if mgr.find_server("nonexistent") is not None:
            print(f"  FAIL: find_server should return None for unknown")
            t_pass = False

        mgr.stop_all()
        if w1.status != "stopped":
            print(f"  FAIL: stop_all should stop all servers")
            t_pass = False

        if t_pass:
            print("  PASS: InfrastructureManager works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You've mastered inheritance!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Focus on super() and method overriding.")
    print("=" * 50)

if __name__ == "__main__":
    main()
