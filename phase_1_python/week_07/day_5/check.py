#!/usr/bin/env python3
"""
Week 7, Day 5: SSH with Paramiko - Auto-Checker
Validates exercise.py solutions using the MockSSHClient.
No actual SSH server needed.
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_07/day_5")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 7, Day 5: SSH with Paramiko - Checking Solutions")
    print("=" * 50)
    print()

    # TASK 1: SSHManager
    print("Task 1: SSH Connection Manager")
    try:
        mgr = exercise.SSHManager("web-01.example.com", "admin", "secret")
        t1_pass = True

        if mgr.is_connected():
            print("  FAIL: Should not be connected before connect()")
            t1_pass = False

        result = mgr.connect()
        if result is not True:
            print(f"  FAIL: connect() should return True, got {result}")
            t1_pass = False

        if not mgr.is_connected():
            print("  FAIL: Should be connected after connect()")
            t1_pass = False

        cmd_result = mgr.run("hostname")
        if cmd_result is None or cmd_result.get("stdout") != "web-01.example.com":
            print(f"  FAIL: run('hostname') returned {cmd_result}")
            t1_pass = False

        mgr.disconnect()
        if mgr.is_connected():
            print("  FAIL: Should not be connected after disconnect()")
            t1_pass = False

        # Test not connected
        cmd_result = mgr.run("hostname")
        if cmd_result.get("stderr") != "Not connected" or cmd_result.get("exit_code") != 1:
            print(f"  FAIL: run() when disconnected should return error")
            t1_pass = False

        if t1_pass:
            print("  PASS: SSHManager works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: run_remote_commands
    print("\nTask 2: Remote Command Runner")
    try:
        results = exercise.run_remote_commands("web-01", "admin", "pass",
                                                ["hostname", "uptime", "invalid_command"])
        if not isinstance(results, list):
            print(f"  FAIL: Should return a list, got {type(results)}")
        elif len(results) != 3:
            print(f"  FAIL: Should return 3 results, got {len(results)}")
        else:
            t2_pass = True
            if results[0].get("command") != "hostname":
                print(f"  FAIL: First result should be for 'hostname'")
                t2_pass = False
            if results[0].get("success") is not True:
                print(f"  FAIL: 'hostname' should succeed")
                t2_pass = False
            if results[2].get("success") is not False:
                print(f"  FAIL: 'invalid_command' should fail")
                t2_pass = False

            # Test connection failure
            fail_results = exercise.run_remote_commands("web-01", "admin",
                                                         "wrong_password", ["hostname"])
            if fail_results != []:
                print(f"  FAIL: Should return empty list on connection failure")
                t2_pass = False

            if t2_pass:
                print("  PASS: Remote command runner works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: get_system_info
    print("\nTask 3: System Info Gatherer")
    try:
        info = exercise.get_system_info("web-01.example.com", "admin", "pass")
        if info is None:
            print("  FAIL: Returned None")
        else:
            t3_pass = True
            expected_keys = ["hostname", "uptime", "disk_usage", "memory", "os_info", "cpu_count"]
            for key in expected_keys:
                if key not in info:
                    print(f"  FAIL: Missing key '{key}'")
                    t3_pass = False
            if info.get("hostname") != "web-01.example.com":
                print(f"  FAIL: hostname should be 'web-01.example.com'")
                t3_pass = False
            if info.get("cpu_count") != "4":
                print(f"  FAIL: cpu_count should be '4'")
                t3_pass = False

            # Test connection failure
            fail_info = exercise.get_system_info("web-01", "admin", "wrong_password")
            if fail_info is not None:
                print(f"  FAIL: Should return None on connection failure")
                t3_pass = False

            if t3_pass:
                print("  PASS: System info gatherer works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: check_server_health
    print("\nTask 4: Multi-Server Health Check")
    try:
        servers = [
            {"hostname": "web-01", "username": "admin", "password": "pass"},
            {"hostname": "db-01", "username": "admin", "password": "wrong_password"},
        ]
        results = exercise.check_server_health(servers)
        if not isinstance(results, list) or len(results) != 2:
            print(f"  FAIL: Should return list of 2 results")
        else:
            t4_pass = True
            r1, r2 = results[0], results[1]
            if r1.get("hostname") != "web-01":
                print(f"  FAIL: First hostname mismatch")
                t4_pass = False
            if r1.get("reachable") is not True:
                print(f"  FAIL: web-01 should be reachable")
                t4_pass = False
            if r1.get("status") != "healthy":
                print(f"  FAIL: web-01 status should be 'healthy'")
                t4_pass = False
            if r2.get("reachable") is not False:
                print(f"  FAIL: db-01 should not be reachable (wrong password)")
                t4_pass = False
            if r2.get("status") != "unreachable":
                print(f"  FAIL: db-01 status should be 'unreachable'")
                t4_pass = False
            if r2.get("uptime") != "N/A":
                print(f"  FAIL: db-01 uptime should be 'N/A'")
                t4_pass = False
            if t4_pass:
                print("  PASS: Server health check works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: deploy
    print("\nTask 5: Deployment Simulator")
    try:
        result = exercise.deploy(
            [
                {"hostname": "web-01", "username": "admin", "password": "pass"},
                {"hostname": "web-02", "username": "admin", "password": "wrong_password"},
                {"hostname": "web-03", "username": "admin", "password": "pass"},
            ],
            ["systemctl restart nginx", "systemctl status nginx"]
        )
        if result is None:
            print("  FAIL: Returned None")
        else:
            t5_pass = True
            if result.get("total_servers") != 3:
                print(f"  FAIL: total_servers should be 3")
                t5_pass = False
            if result.get("successful") != 2:
                print(f"  FAIL: successful should be 2, got {result.get('successful')}")
                t5_pass = False
            if result.get("failed") != 1:
                print(f"  FAIL: failed should be 1, got {result.get('failed')}")
                t5_pass = False
            results_list = result.get("results", [])
            if len(results_list) != 3:
                print(f"  FAIL: results should have 3 entries")
                t5_pass = False
            else:
                if results_list[0].get("deployed") is not True:
                    print(f"  FAIL: web-01 should be deployed")
                    t5_pass = False
                if results_list[0].get("commands_run") != 2:
                    print(f"  FAIL: web-01 should have 2 commands run")
                    t5_pass = False
                if results_list[1].get("deployed") is not False:
                    print(f"  FAIL: web-02 should not be deployed")
                    t5_pass = False
                if results_list[1].get("commands_run") != 0:
                    print(f"  FAIL: web-02 should have 0 commands run")
                    t5_pass = False
            if t5_pass:
                print("  PASS: Deployment simulator works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You understand SSH automation patterns!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Re-read the lesson on SSH.")
    print("=" * 50)

if __name__ == "__main__":
    main()
