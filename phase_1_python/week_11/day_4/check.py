"""
Week 11, Day 4: Check - Config Generation with Templates
Verifies all 6 tasks from exercise.py
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
    total = 6

    # Task 1: generate_nginx_config
    print("Task 1: generate_nginx_config()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_nginx_config

r = generate_nginx_config({
    "server_name": "api.example.com",
    "port": 443,
    "upstream_host": "127.0.0.1",
    "upstream_port": 8080,
    "ssl_enabled": True,
    "ssl_cert": "/etc/ssl/cert.crt",
    "ssl_key": "/etc/ssl/cert.key",
    "locations": [{"path": "/static", "directive": "alias /var/www/static"}],
})
assert isinstance(r, str), "Must return a string"
assert "server {" in r or "server{" in r, "Must contain server block"
assert "listen 443" in r, "Must have listen 443"
assert "api.example.com" in r
assert "proxy_pass http://127.0.0.1:8080" in r
assert "ssl_certificate" in r, "SSL should be present"
assert "/etc/ssl/cert.crt" in r
assert "/static" in r, "Extra location should be present"

# Test without SSL
r2 = generate_nginx_config({
    "server_name": "test.com",
    "upstream_host": "localhost",
    "upstream_port": 3000,
})
assert "ssl_certificate" not in r2, "No SSL when not enabled"
assert "listen 80" in r2 or "listen" in r2
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 2: generate_dockerfile
    print("Task 2: generate_dockerfile()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_dockerfile

r = generate_dockerfile({
    "base_image": "python",
    "tag": "3.11-slim",
    "maintainer": "devops@company.com",
    "system_packages": ["curl", "git"],
    "pip_packages": ["flask", "gunicorn"],
    "expose_port": 8080,
    "cmd": "gunicorn app:app",
    "env_vars": {"APP_ENV": "production"},
})
assert isinstance(r, str), "Must return a string"
assert "FROM python:3.11-slim" in r
assert "devops@company.com" in r
assert "WORKDIR" in r
assert "curl" in r and "git" in r
assert "flask" in r and "gunicorn" in r
assert "EXPOSE 8080" in r
assert "CMD" in r
assert "APP_ENV" in r

# Test without optional fields
r2 = generate_dockerfile({"base_image": "node", "cmd": "node server.js"})
assert "FROM node" in r2
assert "EXPOSE" not in r2, "No EXPOSE when port is None"
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 3: generate_k8s_deployment
    print("Task 3: generate_k8s_deployment()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_k8s_deployment

r = generate_k8s_deployment({
    "app_name": "web-api",
    "namespace": "production",
    "image": "myorg/web-api",
    "version": "1.2.3",
    "replicas": 3,
    "port": 8080,
    "env_vars": {"APP_ENV": "production", "LOG_LEVEL": "info"},
})
assert isinstance(r, str)
assert "apiVersion: apps/v1" in r
assert "kind: Deployment" in r
assert "name: web-api" in r
assert "namespace: production" in r
assert "replicas: 3" in r
assert "myorg/web-api:1.2.3" in r
assert "containerPort: 8080" in r
assert "500m" in r  # default cpu
assert "256Mi" in r  # default memory
assert "APP_ENV" in r
assert "LOG_LEVEL" in r

# Defaults
r2 = generate_k8s_deployment({"app_name": "test", "image": "test:latest"})
assert "namespace: default" in r2
assert "replicas: 3" in r2
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 4: generate_docker_compose
    print("Task 4: generate_docker_compose()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_docker_compose

r = generate_docker_compose([
    {"name": "web", "image": "myapp:latest", "ports": ["8080:80"],
     "environment": {"APP_ENV": "prod"}, "depends_on": ["db"]},
    {"name": "db", "image": "postgres:15", "ports": ["5432:5432"],
     "environment": {"POSTGRES_PASSWORD": "secret"}},
])
assert isinstance(r, str)
assert 'version: "3.8"' in r or "version:" in r
assert "services:" in r
assert "web:" in r
assert "db:" in r
assert "myapp:latest" in r
assert "8080:80" in r
assert "APP_ENV" in r
assert "depends_on" in r
assert "postgres:15" in r
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 5: generate_env_file
    print("Task 5: generate_env_file()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_env_file

r = generate_env_file("production", {
    "DEBUG": "false",
    "APP_ENV": "production",
    "DATABASE_URL": "postgres://db:5432/myapp",
    "SECRET_KEY": "my secret key",
})
assert isinstance(r, str)
assert "# Environment: production" in r
assert "Generated" in r or "generated" in r
lines = [l for l in r.strip().split("\\n") if l and not l.startswith("#")]
# Check alphabetical ordering
keys = [l.split("=")[0] for l in lines]
assert keys == sorted(keys), f"Keys must be sorted: {keys}"
assert "APP_ENV=production" in r
assert "DEBUG=false" in r
# Values with spaces should be quoted
assert '"my secret key"' in r or "'my secret key'" in r
print("PASS")
'''
    ok, out, err = run_test(code)
    if ok and "PASS" in out:
        print("  PASS"); score += 1
    else:
        print(f"  FAIL");
        if err: print(f"  Error: {err[:200]}")

    # Task 6: generate_all_configs
    print("Task 6: generate_all_configs()")
    code = '''
import sys; sys.path.insert(0, ".")
from exercise import generate_all_configs

r = generate_all_configs({
    "app_name": "my-api",
    "domain": "api.example.com",
    "port": 8080,
    "image": "myorg/my-api",
    "version": "2.0.0",
    "environment": "production",
    "env_vars": {"APP_ENV": "production", "DEBUG": "false"},
})
assert isinstance(r, dict)
assert "nginx" in r, f"Keys: {list(r.keys())}"
assert "dockerfile" in r
assert "kubernetes" in r
assert "env_file" in r

# Check nginx is for production (SSL)
assert "ssl" in r["nginx"].lower() or "443" in r["nginx"]
# Check dockerfile has FROM
assert "FROM" in r["dockerfile"]
# Check k8s has app name
assert "my-api" in r["kubernetes"]
assert "replicas: 3" in r["kubernetes"]
# Check env file
assert "production" in r["env_file"]

# Test staging
r2 = generate_all_configs({
    "app_name": "test",
    "domain": "staging.test.com",
    "port": 3000,
    "image": "test",
    "version": "1.0",
    "environment": "staging",
    "env_vars": {"APP_ENV": "staging"},
})
assert "replicas: 1" in r2["kubernetes"]
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
        print("  PERFECT! Template master!")
    elif score >= 4:
        print("  Great work! Review failed tasks.")
    else:
        print("  Keep practicing with the lesson.")
    print(f"{'='*40}")

if __name__ == "__main__":
    main()
