#!/usr/bin/env python3
"""
Week 8, Day 1: Classes & Objects - Auto-Checker
Validates exercise.py solutions.
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_08/day_1")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 8, Day 1: Classes & Objects - Checking Solutions")
    print("=" * 50)
    print()

    # TASK 1: Server
    print("Task 1: Server Class")
    try:
        s = exercise.Server("web-01", "10.0.1.10")
        t_pass = True
        if s.name != "web-01" or s.ip_address != "10.0.1.10":
            print("  FAIL: Attributes not set correctly")
            t_pass = False
        if s.role != "web":
            print(f"  FAIL: Default role should be 'web', got {repr(s.role)}")
            t_pass = False
        if s.status != "stopped":
            print(f"  FAIL: Initial status should be 'stopped'")
            t_pass = False
        start_msg = s.start()
        if s.status != "running" or "running" not in start_msg:
            print(f"  FAIL: start() didn't work correctly")
            t_pass = False
        info = s.get_info()
        if not isinstance(info, dict) or info.get("name") != "web-01":
            print(f"  FAIL: get_info() wrong")
            t_pass = False
        s_str = str(s)
        if "web-01" not in s_str or "10.0.1.10" not in s_str:
            print(f"  FAIL: __str__ wrong: {s_str}")
            t_pass = False
        s.stop()
        if s.status != "stopped":
            print(f"  FAIL: stop() didn't set status to 'stopped'")
            t_pass = False
        if t_pass:
            print("  PASS: Server class works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: Container
    print("\nTask 2: Container Class")
    try:
        exercise.Container.total_created = 0  # Reset counter
        c1 = exercise.Container("web", "nginx:latest", [80, 443])
        c2 = exercise.Container("api", "python:3.11")
        t_pass = True

        if c1.container_id != "cnt-0":
            print(f"  FAIL: First container id should be 'cnt-0', got {repr(c1.container_id)}")
            t_pass = False
        if c2.container_id != "cnt-1":
            print(f"  FAIL: Second container id should be 'cnt-1', got {repr(c2.container_id)}")
            t_pass = False
        if exercise.Container.total_created != 2:
            print(f"  FAIL: total_created should be 2")
            t_pass = False
        r = c1.start()
        if c1.status != "running" or "started" not in r:
            print(f"  FAIL: start() didn't work")
            t_pass = False
        r2 = c1.start()
        if "already running" not in r2:
            print(f"  FAIL: Second start() should say already running")
            t_pass = False
        c1.stop()
        if c1.status != "stopped":
            print(f"  FAIL: stop() didn't work")
            t_pass = False
        r3 = c1.stop()
        if "not running" not in r3:
            print(f"  FAIL: stop() when stopped should say not running")
            t_pass = False
        info = c1.get_info()
        if not isinstance(info, dict) or "container_id" not in info:
            print(f"  FAIL: get_info() missing keys")
            t_pass = False
        if c2.ports != []:
            print(f"  FAIL: Default ports should be empty list")
            t_pass = False
        if t_pass:
            print("  PASS: Container class works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: Deployment
    print("\nTask 3: Deployment Class")
    try:
        d = exercise.Deployment("myapp", "2.1.0", "production")
        t_pass = True

        if d.status != "pending":
            print(f"  FAIL: Initial status should be 'pending'")
            t_pass = False
        r = d.start()
        if d.status != "in_progress" or "Deploying" not in r or "myapp" not in r:
            print(f"  FAIL: start() wrong")
            t_pass = False
        if "started" not in d.steps_completed:
            print(f"  FAIL: 'started' should be in steps_completed")
            t_pass = False
        r = d.complete()
        if d.status != "completed" or "complete" not in r:
            print(f"  FAIL: complete() wrong")
            t_pass = False

        # Test fail
        d2 = exercise.Deployment("otherapp", "1.0", "staging")
        d2.start()
        r = d2.fail("tests failed")
        if d2.status != "failed" or "tests failed" not in r:
            print(f"  FAIL: fail() wrong")
            t_pass = False
        if not any("failed" in step for step in d2.steps_completed):
            print(f"  FAIL: fail step not recorded")
            t_pass = False

        status = d2.get_status()
        if not isinstance(status, dict) or status.get("app_name") != "otherapp":
            print(f"  FAIL: get_status() wrong")
            t_pass = False

        if t_pass:
            print("  PASS: Deployment class works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: NetworkInterface
    print("\nTask 4: NetworkInterface Class")
    try:
        nic = exercise.NetworkInterface("eth0", "10.0.1.10")
        t_pass = True

        if nic.name != "eth0" or nic.ip_address != "10.0.1.10":
            print(f"  FAIL: Attributes wrong")
            t_pass = False
        if nic.is_up is not True:
            print(f"  FAIL: Default is_up should be True")
            t_pass = False

        if nic.send_data(1024) is not True:
            print(f"  FAIL: send_data should return True when up")
            t_pass = False
        if nic.receive_data(2048) is not True:
            print(f"  FAIL: receive_data should return True when up")
            t_pass = False

        stats = nic.get_stats()
        if stats.get("bytes_sent") != 1024 or stats.get("bytes_received") != 2048:
            print(f"  FAIL: Stats wrong: {stats}")
            t_pass = False
        if stats.get("total_traffic") != 3072:
            print(f"  FAIL: total_traffic should be 3072")
            t_pass = False

        r = nic.toggle()
        if nic.is_up is not False or "down" not in r.lower():
            print(f"  FAIL: toggle() should set is_up=False")
            t_pass = False
        if nic.send_data(100) is not False:
            print(f"  FAIL: send_data should return False when down")
            t_pass = False

        s = str(nic)
        if "eth0" not in s or "DOWN" not in s:
            print(f"  FAIL: __str__ wrong: {s}")
            t_pass = False

        if t_pass:
            print("  PASS: NetworkInterface class works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: ServerRack
    print("\nTask 5: ServerRack Class")
    try:
        rack = exercise.ServerRack("RACK-A1", capacity=2)
        s1 = exercise.Server("web-01", "10.0.1.10")
        s2 = exercise.Server("web-02", "10.0.1.11")
        s3 = exercise.Server("web-03", "10.0.1.12")
        t_pass = True

        r = rack.add_server(s1)
        if "Added" not in r or "web-01" not in r:
            print(f"  FAIL: add_server wrong: {r}")
            t_pass = False
        rack.add_server(s2)

        r = rack.add_server(s3)
        if "full" not in r.lower():
            print(f"  FAIL: Should say rack is full: {r}")
            t_pass = False

        names = rack.list_servers()
        if names != ["web-01", "web-02"]:
            print(f"  FAIL: list_servers should be ['web-01', 'web-02'], got {names}")
            t_pass = False

        found = rack.get_server("web-01")
        if found is None or found.name != "web-01":
            print(f"  FAIL: get_server('web-01') should return server")
            t_pass = False

        not_found = rack.get_server("web-99")
        if not_found is not None:
            print(f"  FAIL: get_server('web-99') should return None")
            t_pass = False

        r = rack.remove_server("web-01")
        if "Removed" not in r:
            print(f"  FAIL: remove_server wrong: {r}")
            t_pass = False
        if len(rack.servers) != 1:
            print(f"  FAIL: Should have 1 server after removal")
            t_pass = False

        r = rack.remove_server("web-99")
        if "not found" not in r.lower():
            print(f"  FAIL: Should say not found: {r}")
            t_pass = False

        status = rack.rack_status()
        if status.get("used") != 1 or status.get("available") != 1:
            print(f"  FAIL: rack_status wrong: {status}")
            t_pass = False

        if t_pass:
            print("  PASS: ServerRack class works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You understand classes and objects!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Re-read the lesson on classes.")
    print("=" * 50)

if __name__ == "__main__":
    main()
