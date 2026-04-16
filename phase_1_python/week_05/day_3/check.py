"""
Week 5, Day 3: Auto-checker
============================
Run this file to verify your exercise.py solutions.
"""

import subprocess
import sys
import os
import json

def main():
    print("=" * 50)
    print("WEEK 5, DAY 3 - EXERCISE CHECKER")
    print("=" * 50)
    print()

    # Run exercise.py first
    result = subprocess.run(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, ".")
exec(open("exercise.py").read())

print("---RESULTS---")
print(f"app_name={app_name!r}")
print(f"db_host={db_host!r}")
print(f"db_port={db_port!r}")
print(f"server_count={server_count!r}")
print(f"monitoring_enabled={monitoring_enabled!r}")
print(f"server_hostnames={server_hostnames!r}")
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

    # Task 1: Parse JSON config
    print("Task 1 - Parse JSON config")
    t1_pass = True
    checks = {
        "app_name": "inventory-service",
        "db_host": "db-01.example.com",
        "db_port": 5432,
        "server_count": 3,
        "monitoring_enabled": True,
    }
    for key, expected in checks.items():
        got = results.get(key)
        if got != expected:
            print(f"  FAIL: {key} expected {expected!r}, got {got!r}")
            t1_pass = False
    if t1_pass:
        print("  PASS: All config values extracted correctly")
        score += 1

    # Task 2: Server hostnames
    print("\nTask 2 - Extract server hostnames")
    expected_hostnames = ["web-01", "web-02", "web-03"]
    if results.get("server_hostnames") == expected_hostnames:
        print(f"  PASS: {expected_hostnames}")
        score += 1
    else:
        print(f"  FAIL: Expected {expected_hostnames}")
        print(f"        Got {results.get('server_hostnames')}")

    # Task 3: Create deploy config JSON
    print("\nTask 3 - Create deploy_config.json")
    if os.path.exists("deploy_config.json"):
        with open("deploy_config.json", "r") as f:
            try:
                deploy_data = json.load(f)
                expected_keys = {"project", "deploy_to", "version", "rollback_enabled",
                                 "max_retries", "targets", "notifications"}
                if set(deploy_data.keys()) == expected_keys:
                    if (deploy_data["project"] == "inventory-service" and
                            deploy_data["version"] == "1.4.0" and
                            deploy_data["targets"] == ["web-01", "web-02", "web-03"]):
                        print("  PASS: deploy_config.json created with correct content")
                        score += 1
                    else:
                        print("  FAIL: Some values in deploy_config.json are incorrect")
                else:
                    print(f"  FAIL: Expected keys {expected_keys}, got {set(deploy_data.keys())}")
            except json.JSONDecodeError:
                print("  FAIL: deploy_config.json is not valid JSON")
    else:
        print("  FAIL: deploy_config.json not found")

    # Task 4: Update config
    print("\nTask 4 - Update and save config")
    if os.path.exists("updated_config.json"):
        with open("updated_config.json", "r") as f:
            try:
                updated = json.load(f)
                t4_pass = True
                if updated.get("version") != "1.4.0":
                    print(f"  FAIL: version should be '1.4.0', got {updated.get('version')!r}")
                    t4_pass = False
                if updated.get("debug") is not True:
                    print(f"  FAIL: debug should be True, got {updated.get('debug')!r}")
                    t4_pass = False
                if updated.get("environment") != "staging":
                    print(f"  FAIL: environment should be 'staging', got {updated.get('environment')!r}")
                    t4_pass = False
                if updated.get("database", {}).get("max_connections") != 100:
                    print(f"  FAIL: max_connections should be 100, got {updated.get('database', {}).get('max_connections')!r}")
                    t4_pass = False
                # Verify original is unchanged
                if updated.get("app_name") != "inventory-service":
                    print(f"  FAIL: app_name should still be 'inventory-service'")
                    t4_pass = False
                if t4_pass:
                    print("  PASS: updated_config.json has all correct changes")
                    score += 1
            except json.JSONDecodeError:
                print("  FAIL: updated_config.json is not valid JSON")
    else:
        print("  FAIL: updated_config.json not found")

    # Task 5: JSON to YAML
    print("\nTask 5 - Convert JSON to YAML")
    try:
        import yaml
        if os.path.exists("app_config.yaml"):
            with open("app_config.yaml", "r") as f:
                yaml_data = yaml.safe_load(f)
            # Compare with original JSON
            with open("app_config.json", "r") as f:
                json_data = json.load(f)
            if yaml_data == json_data:
                print("  PASS: YAML file matches JSON content")
                score += 1
            else:
                print("  FAIL: YAML content does not match JSON content")
        else:
            print("  FAIL: app_config.yaml not found")
    except ImportError:
        print("  SKIP: pyyaml not installed (pip install pyyaml)")
        print("  (This task is worth 1 point but will be skipped)")
        total -= 1

    # Final score
    print()
    print("=" * 50)
    print(f"SCORE: {score}/{total} tasks passed")
    print("=" * 50)
    if score == total:
        print("Excellent! All tasks complete. Move on to Day 4!")
    elif score >= 3:
        print("Good progress! Review the failed tasks and try again.")
    else:
        print("Keep practicing! Review the lesson and try again.")

    # Cleanup
    for f in ["app_config.json", "deploy_config.json", "updated_config.json", "app_config.yaml"]:
        if os.path.exists(f):
            os.remove(f)

if __name__ == "__main__":
    main()
