#!/usr/bin/env python3
"""
Week 8, Day 5: Unit Testing - Auto-Checker
Validates that tests in exercise.py are properly written.
"""

import sys
import importlib

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_08/day_5")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 8, Day 5: Unit Testing - Checking Solutions")
    print("=" * 50)
    print()

    # Helper: run a test function and check it passes (no assertion errors)
    def run_test(func_name, module):
        func = getattr(module, func_name, None)
        if func is None:
            return False, f"Function {func_name} not found"
        try:
            # Check if it needs fixtures
            import inspect
            sig = inspect.signature(func)
            params = list(sig.parameters.keys())

            if "web_server" in params:
                fixture_func = getattr(module, "web_server", None)
                if fixture_func is None:
                    return False, "web_server fixture not found"
                # Call the fixture function directly (skip pytest decorator)
                ws = fixture_func.__wrapped__() if hasattr(fixture_func, '__wrapped__') else fixture_func()
                if ws is None:
                    return False, "web_server fixture returned None"
                func(ws)
            elif "running_server" in params:
                fixture_func = getattr(module, "running_server", None)
                if fixture_func is None:
                    return False, "running_server fixture not found"
                rs = fixture_func.__wrapped__() if hasattr(fixture_func, '__wrapped__') else fixture_func()
                if rs is None:
                    return False, "running_server fixture returned None"
                func(rs)
            else:
                func()
            return True, "passed"
        except AssertionError as e:
            return False, f"Assertion failed: {e}"
        except Exception as e:
            return False, f"Exception: {e}"

    # TASK 1: Server Creation Tests
    print("Task 1: Test Server Creation")
    t1_tests = ["test_server_creation", "test_server_custom_role", "test_server_invalid_name"]
    t1_pass = True
    for test_name in t1_tests:
        passed, msg = run_test(test_name, exercise)
        if not passed:
            print(f"  FAIL: {test_name} - {msg}")
            t1_pass = False
    if t1_pass:
        print("  PASS: All creation tests pass")
        score += 1

    # TASK 2: Server Method Tests
    print("\nTask 2: Test Server Methods")
    t2_tests = ["test_server_start", "test_server_start_already_running",
                 "test_server_stop", "test_server_stop_resets_cpu"]
    t2_pass = True
    for test_name in t2_tests:
        passed, msg = run_test(test_name, exercise)
        if not passed:
            print(f"  FAIL: {test_name} - {msg}")
            t2_pass = False
    if t2_pass:
        print("  PASS: All method tests pass")
        score += 1

    # TASK 3: CPU and Health Tests
    print("\nTask 3: Test CPU and Health")
    t3_tests = ["test_set_cpu_valid", "test_set_cpu_invalid_high",
                 "test_set_cpu_invalid_type", "test_is_healthy"]
    t3_pass = True
    for test_name in t3_tests:
        passed, msg = run_test(test_name, exercise)
        if not passed:
            print(f"  FAIL: {test_name} - {msg}")
            t3_pass = False
    if t3_pass:
        print("  PASS: All CPU and health tests pass")
        score += 1

    # TASK 4: Utility Function Tests
    print("\nTask 4: Test Utility Functions")
    t4_tests = ["test_validate_ip_valid", "test_validate_ip_invalid", "test_format_status"]
    t4_pass = True
    for test_name in t4_tests:
        passed, msg = run_test(test_name, exercise)
        if not passed:
            print(f"  FAIL: {test_name} - {msg}")
            t4_pass = False
    if t4_pass:
        print("  PASS: All utility tests pass")
        score += 1

    # TASK 5: Fixtures and get_info
    print("\nTask 5: Tests with Fixtures")
    t5_tests = ["test_fixture_server", "test_fixture_running", "test_get_info"]
    t5_pass = True

    # Check fixtures exist and return correct types
    ws_fixture = getattr(exercise, "web_server", None)
    rs_fixture = getattr(exercise, "running_server", None)
    if ws_fixture is None:
        print("  FAIL: web_server fixture not defined")
        t5_pass = False
    if rs_fixture is None:
        print("  FAIL: running_server fixture not defined")
        t5_pass = False

    if t5_pass:
        for test_name in t5_tests:
            passed, msg = run_test(test_name, exercise)
            if not passed:
                print(f"  FAIL: {test_name} - {msg}")
                t5_pass = False
    if t5_pass:
        print("  PASS: All fixture tests pass")
        score += 1

    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You can write proper unit tests!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Testing is a critical skill.")
    print("=" * 50)

if __name__ == "__main__":
    main()
