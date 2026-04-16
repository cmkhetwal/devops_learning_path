"""
Week 4, Day 6: Practice Day - Auto-Checker
===========================================
Run this script to check your exercise solutions.
Usage: python check.py
"""

import subprocess
import sys
import os

EXERCISE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

tests = {
    # Mini-Project 1: Password Generator
    "Task 1 - generate_password returns correct length": {
        "code": """import random; random.seed(42)
from exercise import generate_password
p = generate_password(20)
print(len(p))""",
        "expected": "20"
    },
    "Task 1 - generate_password with no special chars": {
        "code": """import random; random.seed(42)
from exercise import generate_password
p = generate_password(100, use_special=False)
special = set('!@#$%^&*')
print(any(c in special for c in p))""",
        "expected": "False"
    },
    "Task 1 - generate_password with no digits": {
        "code": """import random; random.seed(42)
from exercise import generate_password
p = generate_password(100, use_digits=False)
print(any(c.isdigit() for c in p))""",
        "expected": "False"
    },
    "Task 1 - generate_password lowercase only": {
        "code": """import random; random.seed(42)
from exercise import generate_password
p = generate_password(100, use_uppercase=False, use_digits=False, use_special=False)
print(p == p.lower() and p.isalpha())""",
        "expected": "True"
    },
    "Task 2 - check_password_strength strong": {
        "code": "from exercise import check_password_strength; print(check_password_strength('Abc123!@#xyz'))",
        "expected": "strong"
    },
    "Task 2 - check_password_strength medium": {
        "code": "from exercise import check_password_strength; print(check_password_strength('Abc12345'))",
        "expected": "medium"
    },
    "Task 2 - check_password_strength weak": {
        "code": "from exercise import check_password_strength; print(check_password_strength('abc'))",
        "expected": "weak"
    },

    # Mini-Project 2: File Size Converter
    "Task 3 - bytes_to_human bytes": {
        "code": "from exercise import bytes_to_human; print(bytes_to_human(500))",
        "expected": "500 bytes"
    },
    "Task 3 - bytes_to_human KB": {
        "code": "from exercise import bytes_to_human; print(bytes_to_human(1536))",
        "expected": "1.50 KB"
    },
    "Task 3 - bytes_to_human MB": {
        "code": "from exercise import bytes_to_human; print(bytes_to_human(2621440))",
        "expected": "2.50 MB"
    },
    "Task 3 - bytes_to_human GB": {
        "code": "from exercise import bytes_to_human; print(bytes_to_human(5368709120))",
        "expected": "5.00 GB"
    },
    "Task 4 - human_to_bytes bytes": {
        "code": "from exercise import human_to_bytes; print(human_to_bytes('500 bytes'))",
        "expected": "500"
    },
    "Task 4 - human_to_bytes KB": {
        "code": "from exercise import human_to_bytes; print(human_to_bytes('1.50 KB'))",
        "expected": "1536"
    },
    "Task 4 - human_to_bytes MB": {
        "code": "from exercise import human_to_bytes; print(human_to_bytes('2.50 MB'))",
        "expected": "2621440"
    },
    "Task 4 - human_to_bytes GB": {
        "code": "from exercise import human_to_bytes; print(human_to_bytes('5.00 GB'))",
        "expected": "5368709120"
    },

    # Mini-Project 3: Server Health Check
    "Task 5 - check_cpu healthy": {
        "code": "from exercise import check_cpu; print(check_cpu(85))",
        "expected": "{'metric': 'cpu', 'value': 85, 'ok': True}"
    },
    "Task 5 - check_cpu unhealthy": {
        "code": "from exercise import check_cpu; print(check_cpu(95))",
        "expected": "{'metric': 'cpu', 'value': 95, 'ok': False}"
    },
    "Task 6 - check_memory healthy": {
        "code": "from exercise import check_memory; print(check_memory(60))",
        "expected": "{'metric': 'memory', 'value': 60, 'ok': True}"
    },
    "Task 7 - check_disk unhealthy": {
        "code": "from exercise import check_disk; print(check_disk(85))",
        "expected": "{'metric': 'disk', 'value': 85, 'ok': False}"
    },
    "Task 8 - full_health_check all healthy": {
        "code": """from exercise import full_health_check
r = full_health_check(50, 60, 40)
print(r['status'])
print(r['failed'])""",
        "expected": "healthy\n[]"
    },
    "Task 8 - full_health_check some unhealthy": {
        "code": """from exercise import full_health_check
r = full_health_check(95, 60, 85)
print(r['status'])
print(sorted(r['failed']))""",
        "expected": "unhealthy\n['cpu', 'disk']"
    },

    # Mini-Project 4: Encryption
    "Task 9 - encrypt basic": {
        "code": "from exercise import encrypt; print(encrypt('abc', 1))",
        "expected": "bcd"
    },
    "Task 9 - encrypt wrap around": {
        "code": "from exercise import encrypt; print(encrypt('xyz', 3))",
        "expected": "abc"
    },
    "Task 9 - encrypt preserves case and symbols": {
        "code": "from exercise import encrypt; print(encrypt('Hello World!', 5))",
        "expected": "Mjqqt Btwqi!"
    },
    "Task 10 - decrypt basic": {
        "code": "from exercise import decrypt; print(decrypt('def', 3))",
        "expected": "abc"
    },
    "Task 10 - decrypt round-trip": {
        "code": "from exercise import encrypt, decrypt; print(decrypt(encrypt('DevOps rocks!', 7), 7))",
        "expected": "DevOps rocks!"
    },

    # Mini-Project 5: CLI Tool
    "Task 11 - process_command filesize": {
        "code": "from exercise import process_command; print(process_command('filesize', '2621440'))",
        "expected": "2.50 MB"
    },
    "Task 11 - process_command encrypt": {
        "code": "from exercise import process_command; print(process_command('encrypt', 'hello'))",
        "expected": "khoor"
    },
    "Task 11 - process_command decrypt": {
        "code": "from exercise import process_command; print(process_command('decrypt', 'khoor'))",
        "expected": "hello"
    },
    "Task 11 - process_command unknown": {
        "code": "from exercise import process_command; print(process_command('unknown'))",
        "expected": "Unknown command: unknown"
    },
    "Task 11 - process_command health": {
        "code": """from exercise import process_command
r = process_command('health', '50', '60', '40')
print(r['status'])""",
        "expected": "healthy"
    },
}


def run_test(name, code, expected):
    """Run a single test and return True/False."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        actual = result.stdout.strip()
        if result.returncode != 0:
            print(f"  FAIL: {name}")
            print(f"        Error: {result.stderr.strip()[:120]}")
            return False
        if actual == expected:
            print(f"  PASS: {name}")
            return True
        else:
            print(f"  FAIL: {name}")
            print(f"        Expected: {expected}")
            print(f"        Got:      {actual}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  FAIL: {name} (timed out)")
        return False
    except Exception as e:
        print(f"  FAIL: {name} ({e})")
        return False


def main():
    print("=" * 60)
    print("  Week 4, Day 6: Practice Day - Checking Solutions")
    print("=" * 60)
    print()

    passed = 0
    total = len(tests)

    for name, test in tests.items():
        if run_test(name, test["code"], test["expected"]):
            passed += 1

    print()
    print("-" * 60)
    print(f"  Score: {passed}/{total} tests passed")
    if passed == total:
        print("  PERFECT! All 5 mini-projects complete!")
        print("  You're ready for tomorrow's final test!")
    elif passed >= total * 0.7:
        print("  Good progress! Review the failing tests and try again.")
    else:
        print("  Keep practicing! Re-read lesson.md for help.")
    print("-" * 60)


if __name__ == "__main__":
    main()
