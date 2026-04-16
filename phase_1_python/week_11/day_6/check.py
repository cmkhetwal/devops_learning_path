"""
Week 11, Day 6: Check - Practice Day Mini-Projects
Verifies all 5 projects from exercise.py
"""

import subprocess
import sys

def run_test(test_code):
    result = subprocess.run(
        [sys.executable, "-c", test_code],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0, result.stdout.strip(), result.stderr.strip()

def main():
    score = 0
    total = 5

    # Project 1: git_repo_analyzer
    print("Project 1: git_repo_analyzer()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import git_repo_analyzer, SAMPLE_REPO

r = git_repo_analyzer(SAMPLE_REPO)
assert isinstance(r, dict), "Must return a dict"
assert r["repo_name"] == "payment-service"
assert r["total_branches"] == 6
assert isinstance(r["active_branches"], int)
assert isinstance(r["stale_branches"], int)
assert r["active_branches"] + r["stale_branches"] == 6
assert r["active_branches"] == 4, f"Active (>= 2025-01-13): main, develop, refund-api, timeout-fix = 4, got {r['active_branches']}"
assert r["top_contributor"] == "Alice"
assert r["total_commits"] == 338, f"Total commits: 120+95+78+45=338, got {r['total_commits']}"
assert isinstance(r["commit_types"], dict)
assert r["commit_types"].get("feat", 0) == 2
assert r["commit_types"].get("fix", 0) == 1
assert r["commit_types"].get("docs", 0) == 1
assert r["commit_types"].get("chore", 0) == 1
assert isinstance(r["health_score"], int)
assert 0 <= r["health_score"] <= 100
# active(4) > stale(2) -> +20
# Alice 120/338=35.5% < 40% -> +20
# 4 contributors >= 3 -> +20
# 4 types >= 3 -> +20
# has feat and fix -> +20
# total = 100
assert r["health_score"] == 100, f"Health should be 100, got {r['health_score']}"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Project 2: cicd_pipeline_generator
    print("Project 2: cicd_pipeline_generator()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import cicd_pipeline_generator, SAMPLE_APP

r = cicd_pipeline_generator(SAMPLE_APP)
assert isinstance(r, dict)
assert r["name"] == "CI/CD - payment-service"
stages = r["stages"]
assert isinstance(stages, list)
stage_names = [s["name"] for s in stages]
assert "lint" in stage_names
assert "test" in stage_names
assert "build" in stage_names
assert "push" in stage_names
assert "deploy-staging" in stage_names
assert "deploy-production" in stage_names

# Check build stage
build = [s for s in stages if s["name"] == "build"][0]
assert any("docker build" in step for step in build["steps"])
assert any("payment-service" in step for step in build["steps"])
assert any("2.1.0" in step for step in build["steps"])

# Check trigger
assert "trigger" in r
assert "main" in r["trigger"]["branches"]
assert "environment_variables" in r
assert r["environment_variables"]["APP_ENV"] == "production"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Project 3: config_template_engine
    print("Project 3: config_template_engine()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import config_template_engine, SAMPLE_APP

r = config_template_engine(SAMPLE_APP)
assert isinstance(r, dict)
assert "dockerfile" in r
assert "docker_compose" in r
assert "nginx_config" in r
assert "env_files" in r

# Dockerfile checks
df = r["dockerfile"]
assert "FROM python:3.11-slim" in df
assert "EXPOSE 8080" in df
assert "curl" in df and "libpq-dev" in df
assert "gunicorn" in df

# Docker compose checks
dc = r["docker_compose"]
assert "web" in dc or "payment" in dc
assert "postgres" in dc
assert "redis" in dc

# Nginx checks
ng = r["nginx_config"]
assert "payments.example.com" in ng
assert "8080" in ng

# Env files
ef = r["env_files"]
assert isinstance(ef, dict)
assert len(ef) >= 2, f"Should have env files for each environment, got {len(ef)}"
for env_name, content in ef.items():
    assert "APP_ENV" in content
    assert "2.1.0" in content, f"Should include APP_VERSION"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Project 4: deployment_automation
    print("Project 4: deployment_automation()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import deployment_automation, SAMPLE_APP

r = deployment_automation(SAMPLE_APP, "production")
assert isinstance(r, dict)
assert r["target"] == "production"
assert r["version"] == "2.1.0"
assert r["total_steps"] == 7
assert "rollback_command" in r
assert "undo" in r["rollback_command"]
assert "production" in r["rollback_command"]

plan = r["plan"]
assert len(plan) == 7
assert plan[0]["step"] == 1
assert plan[0]["status"] == "READY"
assert "health" in plan[0]["name"].lower() or "check" in plan[0]["name"].lower() or "pre" in plan[0]["name"].lower()
assert "backup" in plan[1]["name"].lower()
assert any("pull" in s["name"].lower() for s in plan)
assert any("deploy" in s["name"].lower() for s in plan)
assert "payments.example.com" in plan[5]["command"] or "example.com" in plan[5]["command"]
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Project 5: infra_manifest_generator
    print("Project 5: infra_manifest_generator()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import infra_manifest_generator, SAMPLE_APP

r = infra_manifest_generator(SAMPLE_APP)
assert isinstance(r, dict)
assert "namespace" in r
assert "deployment" in r
assert "service" in r
assert "configmap" in r
assert "ingress" in r

# Namespace
assert "kind: Namespace" in r["namespace"]
assert "payment-service" in r["namespace"]

# Deployment
assert "kind: Deployment" in r["deployment"]
assert "payment-service" in r["deployment"]
assert "myorg/payment-service" in r["deployment"]
assert "8080" in r["deployment"]

# Service
assert "kind: Service" in r["service"]
assert "ClusterIP" in r["service"]
assert "8080" in r["service"]

# ConfigMap
assert "kind: ConfigMap" in r["configmap"]
assert "APP_ENV" in r["configmap"]
assert "DATABASE_URL" in r["configmap"]

# Ingress
assert "kind: Ingress" in r["ingress"]
assert "payments.example.com" in r["ingress"]
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    print(f"\n{'='*40}")
    print(f"  Score: {score}/{total}")
    if score == total:
        print("  PERFECT! All mini-projects complete!")
    elif score >= 3:
        print("  Great progress! Review the failed ones.")
    else:
        print("  Review Days 1-5 and try again.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
