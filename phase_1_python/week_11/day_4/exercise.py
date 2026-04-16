"""
Week 11, Day 4: Exercise - Config Generation with Jinja2-style Templates

Generate DevOps configuration files using Python string templates.
We use Python's built-in string formatting (no Jinja2 install needed)
to simulate template rendering.

TASKS:
    1. generate_nginx_config()       - Nginx server block config
    2. generate_dockerfile()         - Dockerfile from parameters
    3. generate_k8s_deployment()     - Kubernetes deployment YAML
    4. generate_docker_compose()     - docker-compose.yml
    5. generate_env_file()           - .env file for different environments
    6. generate_all_configs()        - Generate complete config set for an app
"""


# ============================================================
# TASK 1: generate_nginx_config(config)
#
# config is a dict with:
#   - "server_name": domain name (e.g., "api.example.com")
#   - "port": listen port (default 80)
#   - "upstream_host": backend host (e.g., "127.0.0.1")
#   - "upstream_port": backend port (e.g., 8080)
#   - "ssl_enabled": bool (default False)
#   - "ssl_cert": path to cert (only if ssl_enabled)
#   - "ssl_key": path to key (only if ssl_enabled)
#   - "locations": list of dicts with "path" and "directive"
#                  (optional, default [])
#
# Return a string that looks like a valid nginx config:
#
# server {
#     listen 80;
#     server_name api.example.com;
#
#     # SSL Configuration       <-- only if ssl_enabled
#     ssl_certificate /path;    <-- only if ssl_enabled
#     ssl_certificate_key /path;<-- only if ssl_enabled
#
#     location / {
#         proxy_pass http://127.0.0.1:8080;
#         proxy_set_header Host $host;
#         proxy_set_header X-Real-IP $remote_addr;
#     }
#
#     location /static {       <-- for each extra location
#         alias /var/www/static;
#     }
# }
# ============================================================

def generate_nginx_config(config):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 2: generate_dockerfile(config)
#
# config is a dict with:
#   - "base_image": e.g., "python" (required)
#   - "tag": e.g., "3.11-slim" (default "latest")
#   - "maintainer": e.g., "team@example.com" (default "devops")
#   - "workdir": e.g., "/app" (default "/app")
#   - "system_packages": list of apt packages (default [])
#   - "pip_packages": list of pip packages (default [])
#   - "copy_files": list of files/dirs to COPY (default ["."])
#   - "expose_port": port number (default None, skip EXPOSE if None)
#   - "cmd": command string (e.g., "python app.py")
#   - "env_vars": dict of environment variables (default {})
#
# Return a string that looks like a valid Dockerfile:
#
# FROM python:3.11-slim
# LABEL maintainer="team@example.com"
# WORKDIR /app
# ENV APP_ENV=production
# ENV DEBUG=false
# RUN apt-get update && apt-get install -y curl git && rm -rf /var/lib/apt/lists/*
# RUN pip install --no-cache-dir flask gunicorn
# COPY . .
# EXPOSE 8080
# CMD ["python", "app.py"]
#
# Note: CMD should be in exec form (JSON array).
#       Split the cmd string by spaces for the array.
# ============================================================

def generate_dockerfile(config):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 3: generate_k8s_deployment(config)
#
# config is a dict with:
#   - "app_name": e.g., "web-api" (required)
#   - "namespace": e.g., "production" (default "default")
#   - "image": e.g., "myorg/web-api" (required)
#   - "version": e.g., "1.2.3" (default "latest")
#   - "replicas": int (default 3)
#   - "port": container port (default 8080)
#   - "cpu_limit": e.g., "500m" (default "500m")
#   - "memory_limit": e.g., "256Mi" (default "256Mi")
#   - "env_vars": dict of env vars (default {})
#
# Return a YAML-like string for a k8s Deployment:
#
# apiVersion: apps/v1
# kind: Deployment
# metadata:
#   name: web-api
#   namespace: production
#   labels:
#     app: web-api
#     version: "1.2.3"
# spec:
#   replicas: 3
#   selector:
#     matchLabels:
#       app: web-api
#   template:
#     metadata:
#       labels:
#         app: web-api
#         version: "1.2.3"
#     spec:
#       containers:
#       - name: web-api
#         image: myorg/web-api:1.2.3
#         ports:
#         - containerPort: 8080
#         resources:
#           limits:
#             cpu: "500m"
#             memory: "256Mi"
#         env:
#         - name: APP_ENV
#           value: "production"
# ============================================================

def generate_k8s_deployment(config):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 4: generate_docker_compose(services)
#
# services is a list of dicts, each with:
#   - "name": service name (e.g., "web")
#   - "image": Docker image (e.g., "myapp:latest")
#   - "ports": list of "host:container" strings (e.g., ["8080:80"])
#   - "environment": dict of env vars (default {})
#   - "depends_on": list of service names (default [])
#   - "volumes": list of volume mounts (default [])
#
# Return a docker-compose.yml string:
#
# version: "3.8"
# services:
#   web:
#     image: myapp:latest
#     ports:
#       - "8080:80"
#     environment:
#       - APP_ENV=production
#     depends_on:
#       - db
#     volumes:
#       - ./data:/app/data
#   db:
#     image: postgres:15
#     ports:
#       - "5432:5432"
#     environment:
#       - POSTGRES_PASSWORD=secret
# ============================================================

def generate_docker_compose(services):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 5: generate_env_file(env_name, variables)
#
# env_name: string like "production", "staging", "development"
# variables: dict of key-value pairs
#
# Return a .env file string with:
# - A header comment: # Environment: production
# - A generated timestamp comment: # Generated by DevOps Config Tool
# - Each variable as KEY=value
# - Values with spaces should be quoted
# - Variables sorted alphabetically by key
#
# Example:
# # Environment: production
# # Generated by DevOps Config Tool
# APP_ENV=production
# DATABASE_URL="postgres://db:5432/myapp"
# DEBUG=false
# SECRET_KEY="my-secret-key-here"
# ============================================================

def generate_env_file(env_name, variables):
    # YOUR CODE HERE
    pass


# ============================================================
# TASK 6: generate_all_configs(app_config)
#
# app_config is a dict with:
#   - "app_name": string
#   - "domain": string
#   - "port": int
#   - "image": string
#   - "version": string
#   - "environment": "production" or "staging" or "development"
#   - "env_vars": dict
#
# Return a dict with keys:
#   - "nginx": generated nginx config string
#   - "dockerfile": generated Dockerfile string
#   - "kubernetes": generated k8s deployment string
#   - "env_file": generated .env file string
#
# Use the other functions you built! Map app_config fields
# to the appropriate parameters for each generator.
#
# Mappings:
#   nginx: server_name=domain, port=80 (or 443 if production),
#          upstream_host="127.0.0.1", upstream_port=port,
#          ssl_enabled=(environment=="production")
#   dockerfile: base_image="python", tag="3.11-slim",
#               expose_port=port, cmd=f"python app.py"
#   kubernetes: all fields map naturally,
#               namespace=environment, replicas=3 for prod else 1
#   env_file: env_name=environment, variables=env_vars
# ============================================================

def generate_all_configs(app_config):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    print("=== Task 1: Nginx Config ===")
    nginx = generate_nginx_config({
        "server_name": "api.example.com",
        "port": 443,
        "upstream_host": "127.0.0.1",
        "upstream_port": 8080,
        "ssl_enabled": True,
        "ssl_cert": "/etc/ssl/api.example.com.crt",
        "ssl_key": "/etc/ssl/api.example.com.key",
        "locations": [{"path": "/static", "directive": "alias /var/www/static"}],
    })
    if nginx:
        print(nginx[:300])

    print("\n=== Task 2: Dockerfile ===")
    df = generate_dockerfile({
        "base_image": "python",
        "tag": "3.11-slim",
        "system_packages": ["curl", "git"],
        "pip_packages": ["flask", "gunicorn"],
        "expose_port": 8080,
        "cmd": "gunicorn app:app",
        "env_vars": {"APP_ENV": "production"},
    })
    if df:
        print(df[:300])

    print("\n=== Task 3: K8s Deployment ===")
    k8s = generate_k8s_deployment({
        "app_name": "web-api",
        "namespace": "production",
        "image": "myorg/web-api",
        "version": "1.2.3",
        "replicas": 3,
        "port": 8080,
        "env_vars": {"APP_ENV": "production"},
    })
    if k8s:
        print(k8s[:400])

    print("\n=== Task 4: Docker Compose ===")
    dc = generate_docker_compose([
        {"name": "web", "image": "myapp:latest", "ports": ["8080:80"],
         "environment": {"APP_ENV": "production"}, "depends_on": ["db"]},
        {"name": "db", "image": "postgres:15", "ports": ["5432:5432"],
         "environment": {"POSTGRES_PASSWORD": "secret"}},
    ])
    if dc:
        print(dc[:300])

    print("\n=== Task 6: All Configs ===")
    all_cfg = generate_all_configs({
        "app_name": "my-api",
        "domain": "api.example.com",
        "port": 8080,
        "image": "myorg/my-api",
        "version": "2.0.0",
        "environment": "production",
        "env_vars": {"APP_ENV": "production", "DEBUG": "false"},
    })
    if all_cfg:
        print(f"  Generated configs: {list(all_cfg.keys())}")
