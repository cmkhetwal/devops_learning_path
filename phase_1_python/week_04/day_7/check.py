"""
Week 4, Day 7: Phase 1 Final Test - Auto-Checker
=================================================
Run this script to grade your Phase 1 final test.
Usage: python check.py
"""

import subprocess
import sys
import os

EXERCISE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exercise.py")

tests = {
    # Q1
    "Q1 - format_server_label('Web-01', 'production', 8080)": {
        "code": "from exercise import format_server_label; print(format_server_label('Web-01', 'production', 8080))",
        "expected": "[PRODUCTION] web-01:8080"
    },
    "Q1 - format_server_label('DB-Master', 'staging', 5432)": {
        "code": "from exercise import format_server_label; print(format_server_label('DB-Master', 'staging', 5432))",
        "expected": "[STAGING] db-master:5432"
    },

    # Q2
    "Q2 - parse_log_entry('ERROR:2024-01-15:Disk full')": {
        "code": "from exercise import parse_log_entry; print(parse_log_entry('ERROR:2024-01-15:Disk full'))",
        "expected": "{'level': 'ERROR', 'timestamp': '2024-01-15', 'message': 'Disk full'}"
    },

    # Q3
    "Q3 - categorize_response_time(50)": {
        "code": "from exercise import categorize_response_time; print(categorize_response_time(50))",
        "expected": "fast"
    },
    "Q3 - categorize_response_time(500)": {
        "code": "from exercise import categorize_response_time; print(categorize_response_time(500))",
        "expected": "normal"
    },
    "Q3 - categorize_response_time(501)": {
        "code": "from exercise import categorize_response_time; print(categorize_response_time(501))",
        "expected": "slow"
    },
    "Q3 - categorize_response_time(1500)": {
        "code": "from exercise import categorize_response_time; print(categorize_response_time(1500))",
        "expected": "critical"
    },

    # Q4
    "Q4 - count_status_codes([200, 200, 404, 500, 301, 200, 503])": {
        "code": "from exercise import count_status_codes; print(count_status_codes([200, 200, 404, 500, 301, 200, 503]))",
        "expected": "{'2xx': 3, '3xx': 1, '4xx': 1, '5xx': 2}"
    },
    "Q4 - count_status_codes([])": {
        "code": "from exercise import count_status_codes; print(count_status_codes([]))",
        "expected": "{'2xx': 0, '3xx': 0, '4xx': 0, '5xx': 0}"
    },

    # Q5
    "Q5 - retry_operation(3, ['fail', 'fail', 'success'])": {
        "code": "from exercise import retry_operation; print(retry_operation(3, ['fail', 'fail', 'success']))",
        "expected": "3"
    },
    "Q5 - retry_operation(2, ['fail', 'fail', 'success'])": {
        "code": "from exercise import retry_operation; print(retry_operation(2, ['fail', 'fail', 'success']))",
        "expected": "-1"
    },
    "Q5 - retry_operation(5, ['success'])": {
        "code": "from exercise import retry_operation; print(retry_operation(5, ['success']))",
        "expected": "1"
    },

    # Q6
    "Q6 - deduplicate_servers": {
        "code": "from exercise import deduplicate_servers; print(deduplicate_servers(['web-01', 'db-01', 'web-01', 'cache-01', 'db-01']))",
        "expected": "['web-01', 'db-01', 'cache-01']"
    },
    "Q6 - deduplicate_servers empty": {
        "code": "from exercise import deduplicate_servers; print(deduplicate_servers([]))",
        "expected": "[]"
    },

    # Q7
    "Q7 - merge_configs": {
        "code": "from exercise import merge_configs; print(merge_configs({'port': 8080, 'host': 'localhost', 'debug': False}, {'port': 9090, 'debug': True}))",
        "expected": "{'port': 9090, 'host': 'localhost', 'debug': True}"
    },
    "Q7 - merge_configs doesn't modify originals": {
        "code": "from exercise import merge_configs; d = {'a': 1}; merge_configs(d, {'b': 2}); print(d)",
        "expected": "{'a': 1}"
    },

    # Q8
    "Q8 - find_common_tags one common": {
        "code": """from exercise import find_common_tags
result = find_common_tags({
    "web-01": ["prod", "us-east", "web"],
    "web-02": ["prod", "us-west", "web"],
    "db-01": ["prod", "us-east", "database"],
})
print(result)""",
        "expected": "['prod']"
    },
    "Q8 - find_common_tags multiple common": {
        "code": """from exercise import find_common_tags
print(find_common_tags({"a": ["prod", "web"], "b": ["prod", "web"]}))""",
        "expected": "['prod', 'web']"
    },
    "Q8 - find_common_tags empty": {
        "code": "from exercise import find_common_tags; print(find_common_tags({}))",
        "expected": "[]"
    },

    # Q9
    "Q9 - create_server_factory default": {
        "code": "from exercise import create_server_factory; make = create_server_factory(); print(make('web-01'))",
        "expected": "{'name': 'web-01', 'region': 'us-east-1', 'size': 't2.micro'}"
    },
    "Q9 - create_server_factory custom": {
        "code": "from exercise import create_server_factory; make = create_server_factory(default_region='eu-west-1'); print(make('db-01'))",
        "expected": "{'name': 'db-01', 'region': 'eu-west-1', 'size': 't2.micro'}"
    },

    # Q10
    "Q10 - apply_to_all str.upper": {
        "code": "from exercise import apply_to_all; print(apply_to_all(str.upper, ['hello', 'world']))",
        "expected": "['HELLO', 'WORLD']"
    },
    "Q10 - apply_to_all lambda": {
        "code": "from exercise import apply_to_all; print(apply_to_all(lambda x: x * 2, [1, 2, 3]))",
        "expected": "[2, 4, 6]"
    },

    # Q11
    "Q11 - filter_and_sort_servers": {
        "code": """from exercise import filter_and_sort_servers
servers = [
    {"name": "web-01", "cpu": 85, "memory": 70},
    {"name": "db-01", "cpu": 45, "memory": 90},
    {"name": "cache-01", "cpu": 92, "memory": 40},
]
result = filter_and_sort_servers(servers, min_cpu=50, sort_by="cpu")
print([s["name"] for s in result])""",
        "expected": "['web-01', 'cache-01']"
    },
    "Q11 - filter_and_sort_servers by name": {
        "code": """from exercise import filter_and_sort_servers
servers = [
    {"name": "web-01", "cpu": 85, "memory": 70},
    {"name": "db-01", "cpu": 45, "memory": 90},
    {"name": "cache-01", "cpu": 92, "memory": 40},
]
result = filter_and_sort_servers(servers, sort_by="name")
print([s["name"] for s in result])""",
        "expected": "['cache-01', 'db-01', 'web-01']"
    },

    # Q12
    "Q12 - generate_inventory": {
        "code": """from exercise import generate_inventory
result = generate_inventory({
    "webservers": ["web-02", "web-01"],
    "databases": ["db-01"],
})
print(result)""",
        "expected": "[databases]\ndb-01\n\n[webservers]\nweb-01\nweb-02"
    },

    # Q13
    "Q13 - analyze_logs": {
        "code": """from exercise import analyze_logs
result = analyze_logs([
    "INFO: Server started",
    "INFO: Listening on port 8080",
    "ERROR: Connection refused",
    "WARNING: High memory usage",
    "ERROR: Disk full",
])
print(result['total'], result['info'], result['warning'], result['error'])
print(result['most_common'])
print(result['error_messages'])""",
        "expected": "5 2 1 2\nerror\n['Connection refused', 'Disk full']"
    },
    "Q13 - analyze_logs tie-breaking": {
        "code": """from exercise import analyze_logs
result = analyze_logs(["INFO: a", "ERROR: b"])
print(result['most_common'])""",
        "expected": "error"
    },

    # Q14
    "Q14 - build_pipeline all success": {
        "code": """from exercise import build_pipeline
result = build_pipeline(
    ("validate", lambda: "OK"),
    ("build", lambda: "OK"),
    ("deploy", lambda: "OK"),
)
print(len(result))
print(result[-1])""",
        "expected": "4\n{'step': 'PIPELINE', 'result': 'SUCCESS'}"
    },
    "Q14 - build_pipeline with failure": {
        "code": """from exercise import build_pipeline
result = build_pipeline(
    ("validate", lambda: "OK"),
    ("build", lambda: "FAIL"),
    ("deploy", lambda: "OK"),
)
print(len(result))
print(result[-1])""",
        "expected": "3\n{'step': 'PIPELINE', 'result': 'FAILED at build'}"
    },

    # Q15
    "Q15 - create_monitoring_report": {
        "code": """from exercise import create_monitoring_report
result = create_monitoring_report(
    [
        {"name": "web-01", "cpu": 95, "memory": 70, "disk": 60},
        {"name": "db-01", "cpu": 50, "memory": 88, "disk": 75},
        {"name": "cache-01", "cpu": 40, "memory": 30, "disk": 20},
    ],
    {"cpu": 90, "memory": 85, "disk": 80}
)
print(result['total_servers'], result['healthy_count'], result['unhealthy_count'])
print(result['alerts'])
print(result['summary'])""",
        "expected": "3 1 2\n[{'server': 'db-01', 'metric': 'memory', 'value': 88, 'threshold': 85}, {'server': 'web-01', 'metric': 'cpu', 'value': 95, 'threshold': 90}]\n2 alerts on 2 servers"
    },
    "Q15 - create_monitoring_report all healthy": {
        "code": """from exercise import create_monitoring_report
result = create_monitoring_report(
    [{"name": "web-01", "cpu": 10, "memory": 20, "disk": 30}],
    {"cpu": 90, "memory": 85, "disk": 80}
)
print(result['summary'])""",
        "expected": "All servers healthy"
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
    print("=" * 65)
    print("  PHASE 1 FINAL TEST - Python for DevOps")
    print("  Week 4, Day 7: Comprehensive Review")
    print("=" * 65)
    print()

    passed = 0
    total = len(tests)
    question_results = {}

    for name, test in tests.items():
        q_num = name.split(" - ")[0]
        result = run_test(name, test["code"], test["expected"])
        if result:
            passed += 1
        if q_num not in question_results:
            question_results[q_num] = True
        if not result:
            question_results[q_num] = False

    questions_passed = sum(1 for v in question_results.values() if v)
    total_questions = len(question_results)

    print()
    print("=" * 65)
    print(f"  Test Score: {passed}/{total} checks passed")
    print(f"  Questions:  {questions_passed}/{total_questions} fully correct")
    print()

    if passed == total:
        print("  *** PERFECT SCORE! ***")
        print()
        print("  Congratulations! You have completed Phase 1 of the")
        print("  Python for DevOps learning path!")
        print()
        print("  You've mastered:")
        print("    - Variables, strings, and data types")
        print("    - Control flow (if/else, loops)")
        print("    - Data structures (lists, dicts, sets, tuples)")
        print("    - Functions and modules")
        print()
        print("  You're ready for Phase 2: Real-World DevOps Automation!")
    elif passed >= total * 0.8:
        print("  GREAT JOB! You're almost there!")
        print("  Review the failing questions and try again.")
        print("  You need a perfect score to officially complete Phase 1.")
    elif passed >= total * 0.6:
        print("  Good progress! You have solid fundamentals.")
        print("  Review the weeks where you struggled and retry.")
    else:
        print("  Keep studying! Review the lesson.md files from each week.")
        print("  Practice makes perfect -- you'll get there!")

    print("=" * 65)


if __name__ == "__main__":
    main()
