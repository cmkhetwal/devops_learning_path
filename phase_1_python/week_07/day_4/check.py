#!/usr/bin/env python3
"""
Week 7, Day 4: Socket Basics - Auto-Checker
Validates exercise.py solutions.
NOTE: Requires network access. Some tests use google.com.
"""

import sys
import socket

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_07/day_4")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 7, Day 4: Socket Basics - Checking Solutions")
    print("=" * 50)
    print("(Requires network access)\n")

    # Check network availability first
    test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    test_sock.settimeout(5)
    network_ok = test_sock.connect_ex(("google.com", 80)) == 0
    test_sock.close()
    if not network_ok:
        print("WARNING: Cannot reach google.com. Some tests may fail.\n")

    # TASK 1: check_port
    print("Task 1: Port Checker Function")
    try:
        result = exercise.check_port("google.com", 80)
        if result is None:
            print("  FAIL: Returned None")
        else:
            t1_pass = True
            if result.get("host") != "google.com":
                print(f"  FAIL: host should be 'google.com', got {repr(result.get('host'))}")
                t1_pass = False
            if result.get("port") != 80:
                print(f"  FAIL: port should be 80")
                t1_pass = False
            if result.get("open") is not True and network_ok:
                print(f"  FAIL: port 80 should be open")
                t1_pass = False
            if result.get("service") != "HTTP":
                print(f"  FAIL: service should be 'HTTP', got {repr(result.get('service'))}")
                t1_pass = False

            # Test unknown port
            result2 = exercise.check_port("google.com", 99)
            if result2 and result2.get("service") != "unknown":
                print(f"  FAIL: port 99 service should be 'unknown'")
                t1_pass = False

            if t1_pass:
                print("  PASS: Port checker works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: scan_ports
    print("\nTask 2: Multi-Port Scanner")
    try:
        result = exercise.scan_ports("google.com", [80, 443, 12345], timeout=3)
        if result is None:
            print("  FAIL: Returned None")
        else:
            t2_pass = True
            if result.get("host") != "google.com":
                print(f"  FAIL: host mismatch")
                t2_pass = False
            if not isinstance(result.get("open_ports"), list):
                print(f"  FAIL: open_ports should be a list")
                t2_pass = False
            if not isinstance(result.get("closed_ports"), list):
                print(f"  FAIL: closed_ports should be a list")
                t2_pass = False
            if not isinstance(result.get("results"), dict):
                print(f"  FAIL: results should be a dict")
                t2_pass = False
            if network_ok:
                if 80 not in result.get("open_ports", []):
                    print(f"  FAIL: port 80 should be in open_ports")
                    t2_pass = False
                if 12345 not in result.get("closed_ports", []):
                    print(f"  FAIL: port 12345 should be in closed_ports")
                    t2_pass = False
            if t2_pass:
                print("  PASS: Port scanner works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: resolve_host
    print("\nTask 3: DNS Resolver")
    try:
        result = exercise.resolve_host("google.com")
        bad = exercise.resolve_host("nonexistent.invalid")
        t3_pass = True

        if result is None:
            print("  FAIL: Returned None for google.com")
            t3_pass = False
        else:
            if result.get("hostname") != "google.com":
                print(f"  FAIL: hostname mismatch")
                t3_pass = False
            if not result.get("resolved") and network_ok:
                print(f"  FAIL: google.com should resolve")
                t3_pass = False
            if result.get("ip_address") is None and network_ok:
                print(f"  FAIL: ip_address should not be None")
                t3_pass = False

        if bad is None:
            print("  FAIL: Returned None instead of error dict for bad host")
            t3_pass = False
        else:
            if bad.get("resolved") is not False:
                print(f"  FAIL: nonexistent.invalid should not resolve")
                t3_pass = False
            if bad.get("ip_address") is not None:
                print(f"  FAIL: ip_address should be None for bad host")
                t3_pass = False

        if t3_pass:
            print("  PASS: DNS resolver works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: check_services
    print("\nTask 4: Service Status Checker")
    try:
        services = [
            ("Google HTTP", "google.com", 80),
            ("Fake Service", "google.com", 12345),
        ]
        results = exercise.check_services(services)
        if results is None:
            print("  FAIL: Returned None")
        elif not isinstance(results, list) or len(results) != 2:
            print(f"  FAIL: Expected list of 2 results")
        else:
            t4_pass = True
            r1, r2 = results[0], results[1]
            if r1.get("name") != "Google HTTP":
                print(f"  FAIL: First service name mismatch")
                t4_pass = False
            if r1.get("status") != "running" and network_ok:
                print(f"  FAIL: Google HTTP should be 'running'")
                t4_pass = False
            if r2.get("status") != "down":
                print(f"  FAIL: Fake Service should be 'down'")
                t4_pass = False
            if t4_pass:
                print("  PASS: Service checker works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: scan_port_range
    print("\nTask 5: Port Range Scanner with Summary")
    try:
        result = exercise.scan_port_range("google.com", 79, 81, timeout=3)
        if result is None:
            print("  FAIL: Returned None")
        else:
            t5_pass = True
            if result.get("host") != "google.com":
                print(f"  FAIL: host mismatch")
                t5_pass = False
            if result.get("range") != "79-81":
                print(f"  FAIL: range should be '79-81', got {repr(result.get('range'))}")
                t5_pass = False
            if result.get("total_scanned") != 3:
                print(f"  FAIL: total_scanned should be 3")
                t5_pass = False
            if not isinstance(result.get("open_ports"), list):
                print(f"  FAIL: open_ports should be a list")
                t5_pass = False
            if network_ok:
                open_port_nums = [p.get("port") for p in result.get("open_ports", [])]
                if 80 not in open_port_nums:
                    print(f"  FAIL: port 80 should be in open_ports")
                    t5_pass = False
            total = result.get("open_count", 0) + result.get("closed_count", 0)
            if total != 3:
                print(f"  FAIL: open_count + closed_count should equal 3")
                t5_pass = False
            if t5_pass:
                print("  PASS: Port range scanner works correctly")
                score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # Final score
    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You can work with sockets!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Make sure you have network access.")
    print("=" * 50)

if __name__ == "__main__":
    main()
