#!/usr/bin/env python3
"""
Week 8, Day 2: Methods & Properties - Auto-Checker
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_08/day_2")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 8, Day 2: Methods & Properties - Checking")
    print("=" * 50)
    print()

    # TASK 1: Server
    print("Task 1: Enhanced Server Class")
    try:
        exercise.Server._fleet = {}
        exercise.Server.total_created = 0
        t_pass = True

        s = exercise.Server("web-01", "10.0.1.10")
        if s.status != "stopped":
            print(f"  FAIL: Initial status should be 'stopped'")
            t_pass = False
        s.start()
        if s.status != "running":
            print(f"  FAIL: Status should be 'running' after start()")
            t_pass = False
        s.cpu_usage = 45.0
        s.memory_usage = 30.0
        hc = s.health_check()
        if hc.get("healthy") is not True:
            print(f"  FAIL: Should be healthy (cpu=45, mem=30)")
            t_pass = False
        s.cpu_usage = 95.0
        hc = s.health_check()
        if hc.get("healthy") is not False:
            print(f"  FAIL: Should NOT be healthy (cpu=95)")
            t_pass = False
        # Property validation
        try:
            s.cpu_usage = 150
            print(f"  FAIL: Should raise ValueError for cpu=150")
            t_pass = False
        except ValueError:
            pass
        # Class methods
        s2 = exercise.Server.from_config({"name": "db-01", "ip": "10.0.2.10", "role": "database"})
        if s2.role != "database":
            print(f"  FAIL: from_config role wrong")
            t_pass = False
        if exercise.Server.fleet_size() != 2:
            print(f"  FAIL: fleet_size should be 2")
            t_pass = False
        found = exercise.Server.find("web-01")
        if found is None or found.name != "web-01":
            print(f"  FAIL: find('web-01') should return server")
            t_pass = False
        # Static methods
        if not exercise.Server.validate_ip("10.0.1.10"):
            print(f"  FAIL: validate_ip('10.0.1.10') should be True")
            t_pass = False
        if exercise.Server.validate_ip("999.0.1"):
            print(f"  FAIL: validate_ip('999.0.1') should be False")
            t_pass = False
        if exercise.Server.generate_name("web", 3) != "web-03":
            print(f"  FAIL: generate_name wrong")
            t_pass = False
        s.stop()
        if s.cpu_usage != 0.0:
            print(f"  FAIL: stop() should reset cpu to 0")
            t_pass = False
        if t_pass:
            print("  PASS: Enhanced Server class works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: Container
    print("\nTask 2: Container with Factory Methods")
    try:
        exercise.Container._all_containers = []
        t_pass = True

        c = exercise.Container("web", "nginx", "1.25")
        if c.full_image != "nginx:1.25":
            print(f"  FAIL: full_image should be 'nginx:1.25', got {repr(c.full_image)}")
            t_pass = False
        c.start()
        if c.status != "running":
            print(f"  FAIL: status should be 'running'")
            t_pass = False
        c.add_port(80)
        if c.ports != [80]:
            print(f"  FAIL: ports should be [80]")
            t_pass = False

        c2 = exercise.Container.from_image_string("redis:7")
        if c2.full_image != "redis:7":
            print(f"  FAIL: from_image_string full_image wrong: {c2.full_image}")
            t_pass = False
        if "redis" not in c2.name:
            print(f"  FAIL: from_image_string name should contain 'redis'")
            t_pass = False

        c.start()
        if exercise.Container.running_count() != 1:
            print(f"  FAIL: running_count should be 1")
            t_pass = False

        if not exercise.Container.validate_image("nginx:latest"):
            print(f"  FAIL: validate_image('nginx:latest') should be True")
            t_pass = False
        if exercise.Container.validate_image("nginx"):
            print(f"  FAIL: validate_image('nginx') should be False")
            t_pass = False
        if exercise.Container.validate_image(":latest"):
            print(f"  FAIL: validate_image(':latest') should be False")
            t_pass = False

        if t_pass:
            print("  PASS: Container class works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: MetricsCollector
    print("\nTask 3: Metrics Collector")
    try:
        m = exercise.MetricsCollector("web-01")
        t_pass = True

        for v in [45.0, 62.0, 85.0, 91.0, 30.0]:
            m.add_metric(v)
        if m.count != 5:
            print(f"  FAIL: count should be 5")
            t_pass = False
        if m.average != 62.6:
            print(f"  FAIL: average should be 62.6, got {m.average}")
            t_pass = False
        if m.maximum != 91.0:
            print(f"  FAIL: max should be 91.0")
            t_pass = False
        if m.minimum != 30.0:
            print(f"  FAIL: min should be 30.0")
            t_pass = False
        above = m.above_threshold
        if sorted(above) != [85.0, 91.0]:
            print(f"  FAIL: above_threshold should be [85.0, 91.0], got {above}")
            t_pass = False
        if m.alert_status != "warning":
            print(f"  FAIL: alert_status should be 'warning' (avg<threshold but some above)")
            t_pass = False

        # Test critical
        m2 = exercise.MetricsCollector("db-01")
        m2.threshold = 50.0
        for v in [80.0, 90.0, 85.0]:
            m2.add_metric(v)
        if m2.alert_status != "critical":
            print(f"  FAIL: Should be 'critical' when avg > threshold")
            t_pass = False

        # Test ok
        m3 = exercise.MetricsCollector("cache-01")
        for v in [10.0, 20.0, 30.0]:
            m3.add_metric(v)
        if m3.alert_status != "ok":
            print(f"  FAIL: Should be 'ok' when all below threshold")
            t_pass = False

        # Empty
        m4 = exercise.MetricsCollector("empty")
        if m4.average != 0.0 or m4.maximum != 0.0:
            print(f"  FAIL: Empty metrics should return 0.0")
            t_pass = False

        try:
            m.threshold = 0
            print(f"  FAIL: threshold=0 should raise ValueError")
            t_pass = False
        except ValueError:
            pass

        if t_pass:
            print("  PASS: MetricsCollector works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: ConfigEntry
    print("\nTask 4: ConfigEntry with Validation")
    try:
        t_pass = True

        cfg_str = exercise.ConfigEntry("app_name", "myapp", "string")
        if cfg_str.key != "app_name" or cfg_str.value != "myapp":
            print(f"  FAIL: String config wrong")
            t_pass = False
        if cfg_str.as_string != "myapp":
            print(f"  FAIL: as_string for string should be 'myapp'")
            t_pass = False

        cfg_int = exercise.ConfigEntry("max_workers", 4, "integer")
        if cfg_int.as_string != "4":
            print(f"  FAIL: as_string for integer should be '4'")
            t_pass = False

        cfg_bool = exercise.ConfigEntry("debug", True, "boolean")
        if cfg_bool.as_string != "true":
            print(f"  FAIL: as_string for True should be 'true'")
            t_pass = False
        cfg_bool.value = False
        if cfg_bool.as_string != "false":
            print(f"  FAIL: as_string for False should be 'false'")
            t_pass = False

        cfg_list = exercise.ConfigEntry("hosts", ["a", "b", "c"], "list")
        if cfg_list.as_string != "a,b,c":
            print(f"  FAIL: as_string for list should be 'a,b,c', got {repr(cfg_list.as_string)}")
            t_pass = False

        # Validation
        try:
            cfg_int.value = "not_an_int"
            print(f"  FAIL: Should raise TypeError for string in integer config")
            t_pass = False
        except TypeError:
            pass

        d = cfg_int.to_dict()
        if d != {"key": "max_workers", "value": 4, "type": "integer"}:
            print(f"  FAIL: to_dict wrong: {d}")
            t_pass = False

        if str(cfg_int) != "max_workers=4":
            print(f"  FAIL: __str__ should be 'max_workers=4', got {repr(str(cfg_int))}")
            t_pass = False

        if t_pass:
            print("  PASS: ConfigEntry works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: ServiceMonitor
    print("\nTask 5: ServiceMonitor")
    try:
        exercise.ServiceMonitor._monitors = {}
        t_pass = True

        mon = exercise.ServiceMonitor("nginx", 80)
        mon.record_check(True)
        mon.record_check(True)
        mon.record_check(False)

        if mon.total_checks != 3:
            print(f"  FAIL: total_checks should be 3")
            t_pass = False
        if mon.uptime_percent != round(2/3 * 100, 1):
            print(f"  FAIL: uptime should be {round(2/3*100, 1)}, got {mon.uptime_percent}")
            t_pass = False
        if mon.is_up is not False:
            print(f"  FAIL: is_up should be False (last check was False)")
            t_pass = False

        report = mon.get_report()
        if report.get("service_name") != "nginx" or report.get("port") != 80:
            print(f"  FAIL: Report missing basic info")
            t_pass = False
        if report.get("last_status") != "down":
            print(f"  FAIL: last_status should be 'down'")
            t_pass = False

        found = exercise.ServiceMonitor.get_monitor("nginx")
        if found is None or found is not mon:
            print(f"  FAIL: get_monitor should find nginx")
            t_pass = False

        if not exercise.ServiceMonitor.is_valid_port(80):
            print(f"  FAIL: port 80 should be valid")
            t_pass = False
        if exercise.ServiceMonitor.is_valid_port(0):
            print(f"  FAIL: port 0 should be invalid")
            t_pass = False
        if exercise.ServiceMonitor.is_valid_port(70000):
            print(f"  FAIL: port 70000 should be invalid")
            t_pass = False

        # Test empty checks
        mon2 = exercise.ServiceMonitor("redis", 6379)
        if mon2.is_up is not False:
            print(f"  FAIL: is_up should be False with no checks")
            t_pass = False
        report2 = mon2.get_report()
        if report2.get("last_status") != "unknown":
            print(f"  FAIL: last_status should be 'unknown' with no checks")
            t_pass = False

        if t_pass:
            print("  PASS: ServiceMonitor works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You've mastered methods and properties!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Focus on @property and @classmethod.")
    print("=" * 50)

if __name__ == "__main__":
    main()
