#!/usr/bin/env python3
"""
Week 8, Day 6: Practice Day - Auto-Checker
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_08/day_6")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 8, Day 6: Practice Day - Checking Solutions")
    print("=" * 50)
    print()

    # PROJECT 1: ServerManager
    print("Project 1: ServerManager")
    try:
        mgr = exercise.ServerManager()
        t_pass = True

        r = mgr.add_server("web-01", "10.0.1.10")
        if "Added" not in str(r):
            print(f"  FAIL: add_server should return 'Added ...'")
            t_pass = False
        r = mgr.add_server("web-01", "10.0.1.10")
        if "already exists" not in str(r):
            print(f"  FAIL: Duplicate add should say 'already exists'")
            t_pass = False
        mgr.add_server("web-02", "10.0.1.11")
        mgr.add_server("db-01", "10.0.2.10", role="database")

        count = mgr.start_all()
        if count != 3:
            print(f"  FAIL: start_all should return 3, got {count}")
            t_pass = False

        status = mgr.get_status()
        if status.get("total") != 3 or status.get("running") != 3:
            print(f"  FAIL: get_status wrong: {status}")
            t_pass = False

        db_servers = mgr.get_servers_by_role("database")
        if db_servers != ["db-01"]:
            print(f"  FAIL: get_servers_by_role wrong: {db_servers}")
            t_pass = False

        mgr.stop_server("web-01")
        status = mgr.get_status()
        if status.get("running") != 2:
            print(f"  FAIL: After stop, running should be 2")
            t_pass = False

        r = mgr.remove_server("web-01")
        if "Removed" not in str(r):
            print(f"  FAIL: remove_server should return 'Removed ...'")
            t_pass = False
        r = mgr.remove_server("nonexistent")
        if "not found" not in str(r).lower():
            print(f"  FAIL: Removing nonexistent should say 'not found'")
            t_pass = False

        if t_pass:
            print("  PASS: ServerManager works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 2: DeploymentPipeline
    print("\nProject 2: DeploymentPipeline")
    try:
        t_pass = True

        # Test passing pipeline
        pipe = exercise.DeploymentPipeline("deploy-v2")
        pipe.add_stage("build", lambda: True)
        pipe.add_stage("test", lambda: True)
        pipe.add_stage("deploy", lambda: True)
        result = pipe.run()

        if result.get("status") != "completed":
            print(f"  FAIL: All-pass pipeline should be 'completed', got {result.get('status')}")
            t_pass = False
        if result.get("stages_run") != 3:
            print(f"  FAIL: Should run 3 stages")
            t_pass = False
        if result.get("failed_stage") is not None:
            print(f"  FAIL: No failed stage expected")
            t_pass = False

        # Test failing pipeline
        pipe2 = exercise.DeploymentPipeline("deploy-v3")
        pipe2.add_stage("build", lambda: True)
        pipe2.add_stage("test", lambda: False)
        pipe2.add_stage("deploy", lambda: True)
        result2 = pipe2.run()

        if result2.get("status") != "failed":
            print(f"  FAIL: Pipeline with failing test should be 'failed'")
            t_pass = False
        if result2.get("stages_run") != 2:
            print(f"  FAIL: Should stop after 2 stages (build + failed test)")
            t_pass = False
        if result2.get("failed_stage") != "test":
            print(f"  FAIL: failed_stage should be 'test', got {result2.get('failed_stage')}")
            t_pass = False

        report = pipe2.get_report()
        if len(report) != 3:
            print(f"  FAIL: Report should have 3 entries")
            t_pass = False
        if report[2].get("status") != "pending":
            print(f"  FAIL: Unrun stage should be 'pending'")
            t_pass = False

        if t_pass:
            print("  PASS: DeploymentPipeline works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 3: ConfigManager
    print("\nProject 3: ConfigManager with Inheritance")
    try:
        t_pass = True

        # Base ConfigManager
        cfg = exercise.ConfigManager()
        cfg.set("key1", "value1")
        if cfg.get("key1") != "value1":
            print(f"  FAIL: get('key1') should return 'value1'")
            t_pass = False
        if cfg.count() != 1:
            print(f"  FAIL: count should be 1")
            t_pass = False
        if not cfg.has("key1"):
            print(f"  FAIL: has('key1') should be True")
            t_pass = False
        cfg.delete("key1")
        if cfg.has("key1"):
            print(f"  FAIL: key1 should be deleted")
            t_pass = False

        # EnvironmentConfig
        env = exercise.EnvironmentConfig("prod")
        env.set("port", 8080)
        env.set("host", "0.0.0.0")
        if env.get("port") != 8080:
            print(f"  FAIL: EnvironmentConfig get('port') should return 8080")
            t_pass = False
        all_cfg = env.get_all()
        if "prod.port" not in all_cfg:
            print(f"  FAIL: Keys should be prefixed with 'prod.': {all_cfg}")
            t_pass = False
        env_keys = env.get_env_keys()
        if not isinstance(env_keys, list) or len(env_keys) != 2:
            print(f"  FAIL: get_env_keys should return 2 keys")
            t_pass = False

        # SecureConfig
        sec = exercise.SecureConfig()
        sec.set("app_name", "myapp")
        sec.set_secret("db_password", "secret123")
        if sec.get("app_name") != "myapp":
            print(f"  FAIL: Normal key should return value")
            t_pass = False
        if sec.get("db_password") != "***REDACTED***":
            print(f"  FAIL: Secret should be redacted, got {repr(sec.get('db_password'))}")
            t_pass = False
        if sec.get_real("db_password") != "secret123":
            print(f"  FAIL: get_real should return actual secret")
            t_pass = False
        if sec.list_secrets() != ["db_password"]:
            print(f"  FAIL: list_secrets should return ['db_password']")
            t_pass = False

        if t_pass:
            print("  PASS: ConfigManager hierarchy works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 4: Test Suite
    print("\nProject 4: Test Suite")
    try:
        t_pass = True
        r1 = exercise.test_server_manager()
        if r1 != "all tests passed":
            print(f"  FAIL: test_server_manager should return 'all tests passed', got {repr(r1)}")
            t_pass = False
        r2 = exercise.test_deployment_pipeline()
        if r2 != "all tests passed":
            print(f"  FAIL: test_deployment_pipeline should return 'all tests passed', got {repr(r2)}")
            t_pass = False
        r3 = exercise.test_config_manager()
        if r3 != "all tests passed":
            print(f"  FAIL: test_config_manager should return 'all tests passed', got {repr(r3)}")
            t_pass = False
        if t_pass:
            print("  PASS: All test functions pass")
            score += 1
    except AssertionError as e:
        print(f"  FAIL: Test assertion failed - {e}")
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # PROJECT 5: ProjectRegistry
    print("\nProject 5: ProjectRegistry")
    try:
        reg = exercise.ProjectRegistry("infra-tool")
        t_pass = True

        r = reg.register("server", "web-01")
        if "Registered" not in str(r):
            print(f"  FAIL: register should return 'Registered ...'")
            t_pass = False
        reg.register("server", "db-01")
        reg.register("pipeline", "deploy-v2")
        reg.register("config", "prod-config")

        servers = reg.list_components("server")
        if servers != ["web-01", "db-01"]:
            print(f"  FAIL: list_components('server') wrong: {servers}")
            t_pass = False

        all_comp = reg.list_components()
        if not isinstance(all_comp, dict) or len(all_comp) != 3:
            print(f"  FAIL: list_components() should return dict with 3 types")
            t_pass = False

        summary = reg.get_summary()
        if summary.get("project") != "infra-tool":
            print(f"  FAIL: project name wrong")
            t_pass = False
        if summary.get("total_components") != 4:
            print(f"  FAIL: total should be 4, got {summary.get('total_components')}")
            t_pass = False
        if sorted(summary.get("component_types", [])) != ["config", "pipeline", "server"]:
            print(f"  FAIL: component_types wrong")
            t_pass = False

        r = reg.unregister("server", "web-01")
        if "Unregistered" not in str(r):
            print(f"  FAIL: unregister should return 'Unregistered ...'")
            t_pass = False
        r = reg.unregister("server", "nonexistent")
        if "not found" not in str(r).lower():
            print(f"  FAIL: Unregister nonexistent should say 'not found'")
            t_pass = False

        s = str(reg)
        if "infra-tool" not in s or "3" not in s:
            print(f"  FAIL: __str__ should include project name and count")
            t_pass = False

        if t_pass:
            print("  PASS: ProjectRegistry works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} projects passed")
    if score == total:
        print("PERFECT! All OOP projects complete!")
    elif score >= 3:
        print("Good progress! Review the failed projects.")
    else:
        print("Keep at it! Practice makes perfect.")
    print("=" * 50)

if __name__ == "__main__":
    main()
