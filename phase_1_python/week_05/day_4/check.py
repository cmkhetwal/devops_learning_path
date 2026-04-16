"""
Week 5, Day 4: Auto-checker
============================
Run this file to verify your exercise.py solutions.
"""

import subprocess
import sys
import os

def main():
    print("=" * 50)
    print("WEEK 5, DAY 4 - EXERCISE CHECKER")
    print("=" * 50)
    print()

    result = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, ".")
exec(open("exercise.py").read())

print("---RESULTS---")
print(f"result_good={result_good!r}")
print(f"result_missing={result_missing!r}")
print(f"json_good={json_good!r}")
print(f"json_missing={json_missing!r}")
print(f"json_bad={json_bad!r}")
print(f"validation_results={validation_results!r}")
print(f"successes={successes!r}")
print(f"errors_len={len(errors)!r}")
print(f"load_result_good={load_result_good!r}")
print(f"load_result_bad={load_result_bad!r}")
print(f"load_result_missing={load_result_missing!r}")

# Check if ConfigError exists and is an Exception subclass
print(f"config_error_exists={issubclass(ConfigError, Exception)!r}")
"""],
        capture_output=True, text=True, timeout=10
    )

    if result.returncode != 0:
        print("ERROR: exercise.py failed to run!")
        print(result.stderr)
        return

    output = result.stdout
    if "---RESULTS---" not in output:
        print("ERROR: Could not find results in output.")
        print(output)
        return

    results_section = output.split("---RESULTS---")[1]
    results = {}
    for line in results_section.strip().split("\n"):
        if "=" in line:
            key, value = line.split("=", 1)
            try:
                results[key] = eval(value)
            except:
                results[key] = None

    score = 0
    total = 5

    # Task 1: Safe file reader
    print("Task 1 - Safe file reader")
    t1_pass = True
    good = results.get("result_good", "")
    if good and "app_name" in str(good):
        pass  # Content looks right
    else:
        print(f"  FAIL: Reading good_config.json returned unexpected: {str(good)[:80]}")
        t1_pass = False

    if results.get("result_missing") != "FILE_NOT_FOUND":
        print(f"  FAIL: Missing file should return 'FILE_NOT_FOUND', got {results.get('result_missing')!r}")
        t1_pass = False

    if t1_pass:
        print("  PASS: safe_read_file handles both cases correctly")
        score += 1

    # Task 2: Safe JSON loader
    print("\nTask 2 - Safe JSON loader")
    t2_pass = True
    jg = results.get("json_good")
    if not isinstance(jg, dict) or jg.get("app_name") != "web-service":
        print(f"  FAIL: Good JSON should parse correctly, got {jg!r}")
        t2_pass = False
    jm = results.get("json_missing")
    if jm != {"error": "file_not_found"}:
        print(f"  FAIL: Missing file should return {{'error': 'file_not_found'}}, got {jm!r}")
        t2_pass = False
    jb = results.get("json_bad")
    if jb != {"error": "invalid_json"}:
        print(f"  FAIL: Bad JSON should return {{'error': 'invalid_json'}}, got {jb!r}")
        t2_pass = False
    if t2_pass:
        print("  PASS: safe_load_json handles all three cases")
        score += 1

    # Task 3: Config validator with custom exception
    print("\nTask 3 - Config validator")
    t3_pass = True
    vr = results.get("validation_results", {})
    if not results.get("config_error_exists"):
        print("  FAIL: ConfigError class not found or not an Exception subclass")
        t3_pass = False
    if vr.get("valid") != "passed":
        print(f"  FAIL: Valid config should pass validation")
        t3_pass = False
    if vr.get("missing_port") == "passed":
        print(f"  FAIL: Config missing 'port' should raise ConfigError")
        t3_pass = False
    if vr.get("bad_port") == "passed":
        print(f"  FAIL: Config with port=99999 should raise ConfigError")
        t3_pass = False
    if vr.get("missing_name") == "passed":
        print(f"  FAIL: Config missing 'app_name' should raise ConfigError")
        t3_pass = False
    if t3_pass:
        print("  PASS: ConfigError and validate_config work correctly")
        score += 1

    # Task 4: Error-collecting processor
    print("\nTask 4 - Error-collecting processor")
    t4_pass = True
    succ = results.get("successes", [])
    err_len = results.get("errors_len", 0)
    expected_successes = ["web-01:8080", "web-02:443", "db-01:5432"]
    if succ != expected_successes:
        print(f"  FAIL: successes expected {expected_successes}, got {succ}")
        t4_pass = False
    if err_len != 2:
        print(f"  FAIL: Should have 2 errors (missing port + not a dict), got {err_len}")
        t4_pass = False
    if t4_pass:
        print("  PASS: process_server_list collects successes and errors")
        score += 1

    # Task 5: try/except/else/finally
    print("\nTask 5 - try/except/else/finally")
    t5_pass = True
    lg = results.get("load_result_good", {})
    lb = results.get("load_result_bad", {})
    lm = results.get("load_result_missing", {})

    if not isinstance(lg, dict) or lg.get("status") != "ok":
        print(f"  FAIL: Good file should have status='ok', got {lg}")
        t5_pass = False
    elif "data" not in lg:
        print(f"  FAIL: Good file should have 'data' key in result")
        t5_pass = False
    elif lg.get("attempted_file") != "good_config.json":
        print(f"  FAIL: attempted_file should be 'good_config.json', got {lg.get('attempted_file')!r}")
        t5_pass = False

    if not isinstance(lb, dict) or lb.get("status") != "error":
        print(f"  FAIL: Bad JSON should have status='error', got {lb}")
        t5_pass = False
    elif lb.get("attempted_file") != "bad_config.json":
        print(f"  FAIL: attempted_file should be 'bad_config.json'")
        t5_pass = False

    if not isinstance(lm, dict) or lm.get("status") != "error":
        print(f"  FAIL: Missing file should have status='error', got {lm}")
        t5_pass = False
    elif lm.get("attempted_file") != "no_file.json":
        print(f"  FAIL: attempted_file should be 'no_file.json'")
        t5_pass = False

    if t5_pass:
        print("  PASS: try/except/else/finally used correctly")
        score += 1

    # Final score
    print()
    print("=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    print("=" * 50)
    if score == total:
        print("Excellent! All tasks complete. Move on to Day 5!")
    elif score >= 3:
        print("Good progress! Review the failed tasks and try again.")
    else:
        print("Keep practicing! Review the lesson and try again.")

    # Cleanup
    for f in ["good_config.json", "bad_config.json"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
