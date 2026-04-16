"""
Week 5, Day 6: Auto-checker
============================
Run this file to verify your exercise.py solutions (5 mini-projects).
"""

import subprocess
import sys
import os
import json
import csv

def main():
    print("=" * 50)
    print("WEEK 5, DAY 6 - EXERCISE CHECKER")
    print("=" * 50)
    print()

    # Clean up first
    for f in ["log_summary.txt", "managed_config.json", "server_report.csv",
              "processing_results.json", "deployment.log", "deploy_summary.txt"]:
        if os.path.exists(f):
            os.remove(f)

    # Run exercise.py
    result = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, ".")
exec(open("exercise.py").read())

print("---RESULTS---")
print(f"analyzer_counts={analyzer_counts!r}")
print(f"config_result={config_result!r}")
print(f"status_counts={status_counts!r}")
print(f"processing_result={processing_result!r}")
print(f"deploy_result={deploy_result!r}")
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

    # Mini-Project 1: Log File Analyzer
    print("Mini-Project 1 - Log File Analyzer")
    mp1_pass = True
    ac = results.get("analyzer_counts", {})
    expected_counts = {"total": 20, "INFO": 12, "WARNING": 3, "ERROR": 3, "CRITICAL": 2}
    if ac != expected_counts:
        print(f"  FAIL: analyzer_counts expected {expected_counts}, got {ac}")
        mp1_pass = False

    if os.path.exists("log_summary.txt"):
        with open("log_summary.txt", "r") as f:
            summary = f.read()
        if "Total lines: 20" not in summary:
            print("  FAIL: log_summary.txt missing 'Total lines: 20'")
            mp1_pass = False
        if "ERROR: 3" not in summary:
            print("  FAIL: log_summary.txt missing 'ERROR: 3'")
            mp1_pass = False
        if "CRITICAL: 2" not in summary:
            print("  FAIL: log_summary.txt missing 'CRITICAL: 2'")
            mp1_pass = False
        if "ERRORS AND CRITICALS:" not in summary:
            print("  FAIL: log_summary.txt missing 'ERRORS AND CRITICALS:' section")
            mp1_pass = False
    else:
        print("  FAIL: log_summary.txt not found")
        mp1_pass = False

    if mp1_pass:
        print("  PASS: Log analysis and summary correct")
        score += 1

    # Mini-Project 2: Config File Manager
    print("\nMini-Project 2 - Config File Manager")
    mp2_pass = True
    cr = results.get("config_result", {})
    if not isinstance(cr, dict):
        print(f"  FAIL: config_result should be a dict, got {type(cr)}")
        mp2_pass = False
    else:
        if cr.get("app_name") != "my-service":
            print(f"  FAIL: app_name should be 'my-service', got {cr.get('app_name')!r}")
            mp2_pass = False
        if cr.get("version") != "2.0.0":
            print(f"  FAIL: version should be '2.0.0', got {cr.get('version')!r}")
            mp2_pass = False
        if cr.get("port") != 8080:
            print(f"  FAIL: port should be 8080 (from default), got {cr.get('port')!r}")
            mp2_pass = False

    if os.path.exists("managed_config.json"):
        with open("managed_config.json", "r") as f:
            try:
                saved = json.load(f)
                if saved.get("app_name") != "my-service":
                    print("  FAIL: managed_config.json not written correctly")
                    mp2_pass = False
            except json.JSONDecodeError:
                print("  FAIL: managed_config.json is not valid JSON")
                mp2_pass = False
    else:
        print("  FAIL: managed_config.json not found")
        mp2_pass = False

    if mp2_pass:
        print("  PASS: Config manager works correctly")
        score += 1

    # Mini-Project 3: CSV Report Generator
    print("\nMini-Project 3 - CSV Report Generator")
    mp3_pass = True
    sc = results.get("status_counts", {})
    expected_status = {"healthy": 2, "warning": 2, "critical": 2}
    # web-01: 45/60 -> healthy, web-02: 72/68 -> warning (cpu>70)
    # web-03: 55/50 -> healthy, db-01: 88/75 -> warning (cpu>70, mem>70)
    # db-02: 92/95 -> critical, cache-01: 30/45 -> healthy
    # Recalculate: web-01=healthy, web-02=warning(cpu72), web-03=healthy,
    # db-01=warning(cpu88,mem75), db-02=critical(cpu92,mem95), cache-01=healthy
    expected_status = {"healthy": 3, "warning": 2, "critical": 1}

    if sc != expected_status:
        print(f"  FAIL: status_counts expected {expected_status}, got {sc}")
        mp3_pass = False

    if os.path.exists("server_report.csv"):
        with open("server_report.csv", "r", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        if len(rows) != 6:
            print(f"  FAIL: CSV should have 6 data rows, got {len(rows)}")
            mp3_pass = False
        elif "status" not in rows[0]:
            print("  FAIL: CSV missing 'status' column")
            mp3_pass = False
    else:
        print("  FAIL: server_report.csv not found")
        mp3_pass = False

    if mp3_pass:
        print("  PASS: CSV report with computed status correct")
        score += 1

    # Mini-Project 4: Error-Resilient File Processor
    print("\nMini-Project 4 - Error-Resilient File Processor")
    mp4_pass = True
    pr = results.get("processing_result", {})
    if not isinstance(pr, dict):
        print(f"  FAIL: processing_result should be a dict")
        mp4_pass = False
    else:
        processed = pr.get("processed", [])
        errors = pr.get("errors", [])
        if len(processed) != 1:
            print(f"  FAIL: Should have 1 processed file, got {len(processed)}")
            mp4_pass = False
        if len(errors) != 2:
            print(f"  FAIL: Should have 2 errors, got {len(errors)}")
            mp4_pass = False

    if os.path.exists("processing_results.json"):
        with open("processing_results.json", "r") as f:
            try:
                saved = json.load(f)
                if "processed" not in saved or "errors" not in saved:
                    print("  FAIL: processing_results.json missing keys")
                    mp4_pass = False
            except json.JSONDecodeError:
                print("  FAIL: processing_results.json is not valid JSON")
                mp4_pass = False
    else:
        print("  FAIL: processing_results.json not found")
        mp4_pass = False

    if mp4_pass:
        print("  PASS: File processor handles all cases correctly")
        score += 1

    # Mini-Project 5: Deployment Logger
    print("\nMini-Project 5 - Deployment Logger")
    mp5_pass = True
    dr = results.get("deploy_result", {})
    if not isinstance(dr, dict):
        print(f"  FAIL: deploy_result should be a dict")
        mp5_pass = False
    else:
        if dr.get("successes") != 3:
            print(f"  FAIL: Expected 3 successes, got {dr.get('successes')}")
            mp5_pass = False
        if dr.get("failures") != 1:
            print(f"  FAIL: Expected 1 failure, got {dr.get('failures')}")
            mp5_pass = False

    if os.path.exists("deployment.log"):
        with open("deployment.log", "r") as f:
            log_content = f.read()
        if "ERROR" not in log_content:
            print("  FAIL: deployment.log should contain ERROR for web-03")
            mp5_pass = False
        if "web-03" not in log_content:
            print("  FAIL: deployment.log should mention web-03")
            mp5_pass = False
    else:
        print("  FAIL: deployment.log not found")
        mp5_pass = False

    if os.path.exists("deploy_summary.txt"):
        with open("deploy_summary.txt", "r") as f:
            summary = f.read()
        if "Successes: 3" not in summary:
            print("  FAIL: deploy_summary.txt should contain 'Successes: 3'")
            mp5_pass = False
        if "Failures: 1" not in summary:
            print("  FAIL: deploy_summary.txt should contain 'Failures: 1'")
            mp5_pass = False
    else:
        print("  FAIL: deploy_summary.txt not found")
        mp5_pass = False

    if mp5_pass:
        print("  PASS: Deployment logger works correctly")
        score += 1

    # Final score
    print()
    print("=" * 50)
    print(f"SCORE: {score}/{total} mini-projects passed")
    print("=" * 50)
    if score == total:
        print("Outstanding! All 5 mini-projects complete. Move on to Day 7!")
    elif score >= 3:
        print("Good progress! Review the failed projects and try again.")
    else:
        print("Keep practicing! Review the week's lessons and try again.")

    # Cleanup
    for f in ["sample_app.log", "log_summary.txt", "managed_config.json",
              "server_report.csv", "processing_results.json",
              "deployment.log", "deploy_summary.txt",
              "good_data.json", "corrupt_data.json"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
