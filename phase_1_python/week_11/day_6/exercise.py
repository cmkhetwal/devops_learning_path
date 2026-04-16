"""
Week 11, Day 6: Practice Day - 5 Mini-Projects

Combine all Week 11 skills: Git analysis, CI/CD, templates, Ansible.

PROJECTS:
    1. git_repo_analyzer()          - Analyze repository health
    2. cicd_pipeline_generator()    - Generate CI/CD pipeline config
    3. config_template_engine()     - Generate configs from metadata
    4. deployment_automation()      - Coordinate a deployment
    5. infra_manifest_generator()   - Generate infrastructure manifests
"""

# ============================================================
# SHARED DATA
# ============================================================

SAMPLE_REPO = {
    "name": "payment-service",
    "branches": [
        {"name": "main", "commits": 342, "last_activity": "2025-01-15"},
        {"name": "develop", "commits": 458, "last_activity": "2025-01-15"},
        {"name": "feature/refund-api", "commits": 12, "last_activity": "2025-01-14"},
        {"name": "feature/payment-v2", "commits": 45, "last_activity": "2025-01-10"},
        {"name": "bugfix/timeout-fix", "commits": 3, "last_activity": "2025-01-13"},
        {"name": "release/v2.1.0", "commits": 350, "last_activity": "2025-01-12"},
    ],
    "contributors": [
        {"name": "Alice", "commits": 120, "additions": 15000, "deletions": 8000},
        {"name": "Bob", "commits": 95, "additions": 12000, "deletions": 6000},
        {"name": "Carol", "commits": 78, "additions": 9000, "deletions": 4500},
        {"name": "Dave", "commits": 45, "additions": 5000, "deletions": 2000},
    ],
    "recent_commits": [
        {"sha": "abc1234", "author": "Alice", "message": "feat: add refund endpoint",
         "date": "2025-01-15", "files_changed": 5},
        {"sha": "def5678", "author": "Bob", "message": "fix: payment timeout issue",
         "date": "2025-01-14", "files_changed": 2},
        {"sha": "ghi9012", "author": "Carol", "message": "docs: update API docs",
         "date": "2025-01-14", "files_changed": 3},
        {"sha": "jkl3456", "author": "Alice", "message": "feat: payment v2 schema",
         "date": "2025-01-13", "files_changed": 8},
        {"sha": "mno7890", "author": "Dave", "message": "chore: update deps",
         "date": "2025-01-12", "files_changed": 1},
    ],
}

SAMPLE_APP = {
    "name": "payment-service",
    "language": "python",
    "version": "2.1.0",
    "port": 8080,
    "domain": "payments.example.com",
    "image": "myorg/payment-service",
    "packages": ["flask", "gunicorn", "sqlalchemy", "redis"],
    "system_deps": ["curl", "libpq-dev"],
    "test_command": "pytest tests/ -v",
    "lint_command": "flake8 .",
    "environments": [
        {"name": "staging", "replicas": 1, "url": "https://staging-payments.example.com"},
        {"name": "production", "replicas": 3, "url": "https://payments.example.com"},
    ],
    "env_vars": {
        "APP_ENV": "production",
        "DATABASE_URL": "postgres://db:5432/payments",
        "REDIS_URL": "redis://cache:6379",
        "LOG_LEVEL": "info",
    },
    "services": [
        {"name": "web", "image": "myorg/payment-service:2.1.0", "port": "8080:8080"},
        {"name": "db", "image": "postgres:15", "port": "5432:5432"},
        {"name": "cache", "image": "redis:7-alpine", "port": "6379:6379"},
    ],
}


# ============================================================
# PROJECT 1: git_repo_analyzer(repo_data)
#
# Analyze the repository and return a dict with:
#   - "repo_name": repo name
#   - "total_branches": count of branches
#   - "active_branches": branches with last_activity in last 3 days
#                        from "2025-01-15" (>= "2025-01-13")
#   - "stale_branches": branches with last_activity before that
#   - "top_contributor": name of person with most commits
#   - "total_commits": sum of all contributor commits
#   - "commit_types": dict counting commit types from messages
#                     ("feat", "fix", "docs", "chore", "other")
#   - "health_score": int 0-100 calculated as:
#       +20 if active_branches > stale_branches
#       +20 if top contributor has < 40% of total commits
#       +20 if at least 3 contributors
#       +20 if recent commits have variety (>= 3 types)
#       +20 if at least 1 feature and 1 fix in recent commits
# ============================================================

def git_repo_analyzer(repo_data):
    # YOUR CODE HERE
    pass


# ============================================================
# PROJECT 2: cicd_pipeline_generator(app_data)
#
# Generate a CI/CD pipeline configuration as a dict with:
#   - "name": "CI/CD - {app_name}"
#   - "stages": list of stage dicts, each with:
#       - "name": stage name
#       - "steps": list of step strings
#
# Stages to generate:
# 1. "lint" stage: [lint_command]
# 2. "test" stage: ["pip install -r requirements.txt", test_command]
# 3. "build" stage: ["docker build -t {image}:{version} ."]
# 4. "push" stage: ["docker push {image}:{version}"]
# 5. For each environment:
#    "deploy-{env_name}" stage:
#       ["kubectl set image deployment/{app_name} {app_name}={image}:{version} -n {env_name}",
#        "kubectl rollout status deployment/{app_name} -n {env_name}"]
#
# Also include:
#   - "trigger": {"branches": ["main"], "events": ["push", "pull_request"]}
#   - "environment_variables": dict from app env_vars
# ============================================================

def cicd_pipeline_generator(app_data):
    # YOUR CODE HERE
    pass


# ============================================================
# PROJECT 3: config_template_engine(app_data)
#
# Generate configuration files. Return a dict with:
#   - "dockerfile": Dockerfile string with:
#       FROM python:3.11-slim
#       WORKDIR /app
#       RUN apt-get update && apt-get install -y {system_deps}
#       COPY requirements.txt .
#       RUN pip install --no-cache-dir -r requirements.txt
#       COPY . .
#       EXPOSE {port}
#       CMD ["gunicorn", "-b", "0.0.0.0:{port}", "app:app"]
#
#   - "docker_compose": docker-compose.yml string with all services
#
#   - "nginx_config": nginx server block string proxying to app port
#
#   - "env_files": dict mapping env name to .env file string
#     for each environment (from app_data["environments"]),
#     including all env_vars plus APP_VERSION={version}
#
# ============================================================

def config_template_engine(app_data):
    # YOUR CODE HERE
    pass


# ============================================================
# PROJECT 4: deployment_automation(app_data, target_env)
#
# Simulate a deployment workflow. Return a dict with:
#   - "plan": list of step dicts, each with:
#       - "step": step number (1-based)
#       - "name": step name
#       - "command": the command that would be run
#       - "status": "READY" for all steps
#
# Steps to include:
# 1. "Pre-deploy checks" - "python health_check.py --env {target_env}"
# 2. "Backup current version" - "kubectl get deployment/{app_name} -n {target_env} -o yaml > backup.yaml"
# 3. "Pull latest image" - "docker pull {image}:{version}"
# 4. "Deploy to {target_env}" - "kubectl set image deployment/{app_name} {app_name}={image}:{version} -n {target_env}"
# 5. "Wait for rollout" - "kubectl rollout status deployment/{app_name} -n {target_env} --timeout=300s"
# 6. "Post-deploy health check" - "curl -f {env_url}/health"
# 7. "Update deployment log" - "echo '{app_name} v{version} deployed to {target_env}' >> deploy.log"
#
# Also include:
#   - "rollback_command": "kubectl rollout undo deployment/{app_name} -n {target_env}"
#   - "target": target_env
#   - "version": app version
#   - "total_steps": 7
#
# target_env should match one of the environment names in app_data.
# Use the matching environment's URL for health check.
# If target_env not found, use "http://localhost:{port}/health"
# ============================================================

def deployment_automation(app_data, target_env):
    # YOUR CODE HERE
    pass


# ============================================================
# PROJECT 5: infra_manifest_generator(app_data)
#
# Generate Kubernetes manifests for the entire application.
# Return a dict with:
#
#   - "namespace": YAML string for a Namespace resource
#       kind: Namespace, metadata.name = app_name
#
#   - "deployment": YAML string for a Deployment
#       (app_name, image, version, replicas from first env,
#        port, env_vars)
#
#   - "service": YAML string for a Service
#       kind: Service, spec.type: ClusterIP
#       ports: [{port: port, targetPort: port}]
#       selector: app: app_name
#
#   - "configmap": YAML string for a ConfigMap
#       kind: ConfigMap, data = env_vars
#
#   - "ingress": YAML string for an Ingress
#       kind: Ingress, host = domain
#       path: /, backend service name = app_name, port = port
#
# Each manifest should be a properly-structured YAML string.
# Use basic string building -- no yaml library needed.
# ============================================================

def infra_manifest_generator(app_data):
    # YOUR CODE HERE
    pass


# ============================================================
# Manual testing
# ============================================================
if __name__ == "__main__":
    print("=== Project 1: Git Analyzer ===")
    analysis = git_repo_analyzer(SAMPLE_REPO)
    if analysis:
        for k, v in analysis.items():
            print(f"  {k}: {v}")

    print("\n=== Project 2: CI/CD Pipeline ===")
    pipeline = cicd_pipeline_generator(SAMPLE_APP)
    if pipeline:
        print(f"  Name: {pipeline.get('name')}")
        for stage in pipeline.get("stages", []):
            print(f"  Stage: {stage['name']} -> {len(stage['steps'])} steps")

    print("\n=== Project 3: Config Templates ===")
    configs = config_template_engine(SAMPLE_APP)
    if configs:
        for name in configs:
            val = configs[name]
            size = len(val) if isinstance(val, str) else f"{len(val)} items"
            print(f"  {name}: {size}")

    print("\n=== Project 4: Deployment ===")
    deploy = deployment_automation(SAMPLE_APP, "production")
    if deploy:
        for step in deploy.get("plan", []):
            print(f"  Step {step['step']}: {step['name']} [{step['status']}]")

    print("\n=== Project 5: K8s Manifests ===")
    manifests = infra_manifest_generator(SAMPLE_APP)
    if manifests:
        for name, content in manifests.items():
            print(f"  {name}: {len(content)} chars")
