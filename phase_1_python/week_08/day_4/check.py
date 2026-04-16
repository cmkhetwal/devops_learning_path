#!/usr/bin/env python3
"""
Week 8, Day 4: Project Structure - Auto-Checker
"""

import sys

def main():
    try:
        sys.path.insert(0, "/home/cmk/python/devops-python-path/week_08/day_4")
        import exercise
    except ImportError as e:
        print(f"Could not import exercise.py: {e}")
        sys.exit(1)

    score = 0
    total = 5

    print("=" * 50)
    print("Week 8, Day 4: Project Structure - Checking")
    print("=" * 50)
    print()

    # TASK 1: Utility functions
    print("Task 1: Utility Functions")
    try:
        t_pass = True
        # validate_ip
        if exercise.validate_ip("10.0.1.10") is not True:
            print("  FAIL: validate_ip('10.0.1.10') should be True")
            t_pass = False
        if exercise.validate_ip("192.168.1.1") is not True:
            print("  FAIL: validate_ip('192.168.1.1') should be True")
            t_pass = False
        if exercise.validate_ip("999.0.1.1") is not False:
            print("  FAIL: validate_ip('999.0.1.1') should be False")
            t_pass = False
        if exercise.validate_ip("10.0.1") is not False:
            print("  FAIL: validate_ip('10.0.1') should be False")
            t_pass = False
        if exercise.validate_ip("abc.def.ghi.jkl") is not False:
            print("  FAIL: validate_ip('abc.def.ghi.jkl') should be False")
            t_pass = False

        # format_bytes
        if exercise.format_bytes(500) != "500.0 B":
            print(f"  FAIL: format_bytes(500) should be '500.0 B', got {repr(exercise.format_bytes(500))}")
            t_pass = False
        if exercise.format_bytes(1536) != "1.5 KB":
            print(f"  FAIL: format_bytes(1536) should be '1.5 KB', got {repr(exercise.format_bytes(1536))}")
            t_pass = False
        if exercise.format_bytes(1048576) != "1.0 MB":
            print(f"  FAIL: format_bytes(1048576) should be '1.0 MB'")
            t_pass = False

        # sanitize_name
        if exercise.sanitize_name("My Server 01") != "my-server-01":
            print(f"  FAIL: sanitize_name wrong: {repr(exercise.sanitize_name('My Server 01'))}")
            t_pass = False
        if exercise.sanitize_name("Web@Server#1") != "webserver1":
            print(f"  FAIL: sanitize_name('Web@Server#1') should be 'webserver1'")
            t_pass = False

        # generate_id
        if exercise.generate_id("srv", 42) != "srv-0042":
            print(f"  FAIL: generate_id wrong: {repr(exercise.generate_id('srv', 42))}")
            t_pass = False

        if t_pass:
            print("  PASS: All utility functions work correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 2: Project structure
    print("\nTask 2: Package Structure Knowledge")
    try:
        result = exercise.get_project_structure("server_manager")
        t_pass = True
        if result is None:
            print("  FAIL: Returned None")
            t_pass = False
        else:
            if result.get("root") != "server_manager/":
                print(f"  FAIL: root wrong")
                t_pass = False
            if result.get("package_dir") != "server_manager/server_manager/":
                print(f"  FAIL: package_dir wrong")
                t_pass = False
            req_files = result.get("required_files", [])
            if "server_manager/server_manager/__init__.py" not in req_files:
                print(f"  FAIL: Missing __init__.py in required_files")
                t_pass = False
            if "server_manager/requirements.txt" not in req_files:
                print(f"  FAIL: Missing requirements.txt")
                t_pass = False
            if "server_manager/setup.py" not in req_files:
                print(f"  FAIL: Missing setup.py")
                t_pass = False
            if result.get("test_dir") != "server_manager/tests/":
                print(f"  FAIL: test_dir wrong")
                t_pass = False
            if result.get("test_init") != "server_manager/tests/__init__.py":
                print(f"  FAIL: test_init wrong")
                t_pass = False
        if t_pass:
            print("  PASS: Project structure correct")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 3: Requirements parser
    print("\nTask 3: Requirements Parser")
    try:
        reqs_text = "requests>=2.28.0\nparamiko==3.0.0\n# A comment\n\nclick\npyyaml~=6.0"
        result = exercise.parse_requirements(reqs_text)
        t_pass = True
        if not isinstance(result, list):
            print(f"  FAIL: Should return a list")
            t_pass = False
        elif len(result) != 4:
            print(f"  FAIL: Should have 4 entries (skip comment and blank), got {len(result)}")
            t_pass = False
        else:
            if result[0] != {"name": "requests", "version": "2.28.0", "operator": ">="}:
                print(f"  FAIL: First entry wrong: {result[0]}")
                t_pass = False
            if result[1] != {"name": "paramiko", "version": "3.0.0", "operator": "=="}:
                print(f"  FAIL: Second entry wrong: {result[1]}")
                t_pass = False
            if result[2] != {"name": "click", "version": None, "operator": None}:
                print(f"  FAIL: Third entry wrong: {result[2]}")
                t_pass = False
            if result[3] != {"name": "pyyaml", "version": "6.0", "operator": "~="}:
                print(f"  FAIL: Fourth entry wrong: {result[3]}")
                t_pass = False
        if t_pass:
            print("  PASS: Requirements parser works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 4: Setup.py generator
    print("\nTask 4: Config File Generator")
    try:
        result = exercise.generate_setup_py(
            "my-tool", "1.0.0", "My tool", "Dev", ["requests", "click"]
        )
        t_pass = True
        if not isinstance(result, str):
            print(f"  FAIL: Should return a string")
            t_pass = False
        else:
            if "from setuptools import setup" not in result:
                print(f"  FAIL: Missing setuptools import")
                t_pass = False
            if "find_packages" not in result:
                print(f"  FAIL: Missing find_packages")
                t_pass = False
            if 'name="my-tool"' not in result and "name='my-tool'" not in result:
                print(f"  FAIL: Missing name")
                t_pass = False
            if 'version="1.0.0"' not in result and "version='1.0.0'" not in result:
                print(f"  FAIL: Missing version")
                t_pass = False
            if "requests" not in result or "click" not in result:
                print(f"  FAIL: Missing dependencies")
                t_pass = False
            # Try to compile it
            try:
                compile(result, "<setup.py>", "exec")
            except SyntaxError as se:
                print(f"  FAIL: Generated code has syntax error: {se}")
                t_pass = False
        if t_pass:
            print("  PASS: Setup.py generator works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    # TASK 5: Import resolver
    print("\nTask 5: Import Path Resolver")
    try:
        t_pass = True
        r1 = exercise.resolve_import("server_manager",
                                      "server_manager/models/server.py", "Server")
        if r1 is None:
            print("  FAIL: Returned None")
            t_pass = False
        else:
            if r1.get("module_path") != "server_manager.models.server":
                print(f"  FAIL: module_path wrong: {r1.get('module_path')}")
                t_pass = False
            if r1.get("absolute_import") != "from server_manager.models.server import Server":
                print(f"  FAIL: absolute_import wrong: {r1.get('absolute_import')}")
                t_pass = False

        r2 = exercise.resolve_import("server_manager",
                                      "server_manager/utils.py", "validate_ip")
        if r2 is not None:
            if r2.get("module_path") != "server_manager.utils":
                print(f"  FAIL: utils module_path wrong")
                t_pass = False
            if r2.get("absolute_import") != "from server_manager.utils import validate_ip":
                print(f"  FAIL: utils import wrong")
                t_pass = False

        if t_pass:
            print("  PASS: Import resolver works correctly")
            score += 1
    except Exception as e:
        print(f"  FAIL: Exception - {e}")

    print("\n" + "=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    if score == total:
        print("PERFECT! You understand project structure!")
    elif score >= 3:
        print("Good progress! Review the failed tasks.")
    else:
        print("Keep practicing! Re-read the lesson.")
    print("=" * 50)

if __name__ == "__main__":
    main()
